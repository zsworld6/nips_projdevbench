from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, Sequence


class CheckFailed(Exception):
    """Raised when a code review check fails."""


def normalize_gitignore_lines(lines: Iterable[str]) -> set[str]:
    entries: set[str] = set()
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            entries.add(stripped)
    return entries


def ensure_gitignore_contains(repo_path: Path, entries: Sequence[str]) -> None:
    gitignore_path = repo_path / ".gitignore"
    if not gitignore_path.is_file():
        raise CheckFailed(
            "未找到 .gitignore 文件，请在仓库根目录创建并添加必需条目："
            + "、".join(entries)
        )

    with gitignore_path.open(encoding="utf-8") as fh:
        existing = normalize_gitignore_lines(fh)

    missing = [entry for entry in entries if entry not in existing]
    if missing:
        raise CheckFailed(
            " .gitignore 缺少以下必需条目：{}".format("、".join(missing))
        )


def forbid_pattern_in_files(
    repo_path: Path,
    pattern: str,
    paths: Sequence[str],
    *,
    case_sensitive: bool = True,
) -> None:
    offending_files: list[str] = []
    for rel in paths:
        file_path = repo_path / rel
        if not file_path.is_file():
            continue
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        haystack = content if case_sensitive else content.lower()
        needle = pattern if case_sensitive else pattern.lower()
        if needle in haystack:
            offending_files.append(rel)

    if offending_files:
        raise CheckFailed(
            f"禁止在以下文件中出现模式 `{pattern}`：{', '.join(offending_files)}"
        )


def forbid_pattern_recursive(
    repo_path: Path,
    pattern: str,
    *,
    include_suffixes: Sequence[str] | None = None,
    case_sensitive: bool = True,
    strip_comments: bool = False,
) -> None:
    offending_files: list[str] = []
    needle = pattern if case_sensitive else pattern.lower()
    suffix_set = {s.lower() for s in include_suffixes} if include_suffixes else None

    for file_path in repo_path.rglob("*"):
        if not file_path.is_file():
            continue
        if suffix_set:
            if file_path.suffix.lower() not in suffix_set:
                continue
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        if strip_comments and file_path.suffix.lower() in {".c", ".cc", ".cpp", ".cxx", ".h", ".hpp"}:
            content = re.sub(r"//.*?$|/\*.*?\*/", "", content, flags=re.DOTALL | re.MULTILINE)
        haystack = content if case_sensitive else content.lower()
        if needle in haystack:
            offending_files.append(str(file_path.relative_to(repo_path)))

    if offending_files:
        raise CheckFailed(
            f"禁止在仓库中出现模式 `{pattern}`，违规文件：{', '.join(offending_files)}"
        )


def ensure_allowed_includes(
    repo_path: Path,
    *,
    files: Sequence[str],
    allowed: Sequence[str],
    reference_root: Path | None = None,
) -> None:
    allowed_set = {inc.strip() for inc in allowed}
    violations: list[str] = []

    # Extract includes from reference/template files if provided
    baseline_includes: dict[str, set[str]] = {}
    if reference_root is not None:
        for rel in files:
            ref_file = reference_root / rel
            if ref_file.is_file():
                baseline_includes[rel] = set()
                for line in ref_file.read_text(encoding="utf-8", errors="ignore").splitlines():
                    stripped = line.strip()
                    if stripped.startswith("#include"):
                        if stripped.startswith("#include <") and stripped.endswith(">"):
                            include_name = stripped[len("#include <") : -1].strip()
                            baseline_includes[rel].add(include_name)

    for rel in files:
        file_path = repo_path / rel
        if not file_path.is_file():
            continue
        
        # Get baseline includes for this file
        baseline = baseline_includes.get(rel, set())
        
        for line in file_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            stripped = line.strip()
            if stripped.startswith("#include"):
                if stripped.startswith("#include <") and stripped.endswith(">"):
                    include_name = stripped[len("#include <") : -1].strip()
                    # Allow if in allowed set OR in baseline (template already had it)
                    if include_name not in allowed_set and include_name not in baseline:
                        violations.append(f"{rel}: {include_name}")

    if violations:
        raise CheckFailed(
            "检测到使用未允许的标准库头文件：" + "；".join(violations)
        )


def ensure_files_exist(repo_path: Path, files: Sequence[str]) -> None:
    missing = [path for path in files if not (repo_path / path).is_file()]
    if missing:
        raise CheckFailed("缺少必需文件：" + "、".join(missing))


def ensure_cmake_outputs_code(repo_path: Path, cmake_path: str) -> None:
    file_path = repo_path / cmake_path
    if not file_path.is_file():
        raise CheckFailed(f"缺少必需文件：{cmake_path}")

    content = file_path.read_text(encoding="utf-8", errors="ignore")
    normalized = content.lower()

    if "add_executable" not in normalized:
        raise CheckFailed(f"{cmake_path} 中未找到 add_executable 定义")

    if "add_executable(code" not in normalized.replace(" ", ""):
        raise CheckFailed(f"{cmake_path} 中的可执行目标应命名为 code")


def ensure_files_unchanged(
    repo_path: Path,
    files: Sequence[str],
    reference_root: Path,
    *,
    diffs_dir: str | None = None,
) -> None:
    import filecmp
    import difflib

    differing: list[str] = []
    for rel in files:
        repo_file = repo_path / rel
        ref_file = reference_root / rel
        if not ref_file.is_file():
            differing.append(rel)
            continue
        if not repo_file.exists():
            differing.append(f"{rel}（提交缺失）")
            continue
        if repo_file.is_dir() or ref_file.is_dir():
            continue
        if not filecmp.cmp(ref_file, repo_file, shallow=False):
            differing.append(rel)

    if differing:
        messages = ["检测到被禁止修改的文件发生变动："]
        for rel in differing:
            if diffs_dir:
                diff_root = repo_path / diffs_dir
                diff_root.mkdir(parents=True, exist_ok=True)
                diff_file = diff_root / f"{rel.replace('/', '_')}.diff"
                ref_lines = ref_file.read_text(encoding="utf-8", errors="ignore").splitlines()
                repo_lines = repo_file.read_text(encoding="utf-8", errors="ignore").splitlines()
                diff = difflib.unified_diff(
                    ref_lines,
                    repo_lines,
                    fromfile=f"template/{rel}",
                    tofile=f"submission/{rel}",
                    lineterm="",
                )
                diff_file.write_text("\n".join(diff), encoding="utf-8")
                messages.append(f"- {rel}（见 {diff_file} ）")
            else:
                messages.append(f"- {rel}")
        raise CheckFailed("\n".join(messages))

