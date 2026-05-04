from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Optional

from .checks import (
    CheckFailed,
    ensure_allowed_includes,
    ensure_cmake_outputs_code,
    ensure_files_exist,
    ensure_gitignore_contains,
    ensure_files_unchanged,
    forbid_pattern_in_files,
    forbid_pattern_recursive,
)


CheckFunc = Callable[[Path, Dict[str, Any]], None]


@dataclass
class ReviewItem:
    name: str
    description: str
    script: str
    args: Dict[str, Any]
    handler: Optional[CheckFunc]


CHECK_REGISTRY: dict[str, CheckFunc] = {
    "gitignore_entries": lambda repo_path, kwargs: ensure_gitignore_contains(
        repo_path, kwargs.get("entries", [])
    ),
    "forbid_pattern": lambda repo_path, kwargs: forbid_pattern_in_files(
        repo_path,
        pattern=kwargs["pattern"],
        paths=kwargs["paths"],
        case_sensitive=kwargs.get("case_sensitive", True),
    ),
    "forbid_pattern_recursive": lambda repo_path, kwargs: forbid_pattern_recursive(
        repo_path,
        pattern=kwargs["pattern"],
        include_suffixes=kwargs.get("include_suffixes"),
        case_sensitive=kwargs.get("case_sensitive", True),
        strip_comments=kwargs.get("strip_comments", False),
    ),
    "allowed_includes": lambda repo_path, kwargs: ensure_allowed_includes(
        repo_path,
        files=kwargs["files"],
        allowed=kwargs["allowed"],
        reference_root=kwargs.get("reference_root") if isinstance(kwargs.get("reference_root"), Path) else (Path(kwargs["reference_root"]).resolve() if kwargs.get("reference_root") else None),
    ),
    "require_files": lambda repo_path, kwargs: ensure_files_exist(
        repo_path,
        files=kwargs["files"],
    ),
    "require_unmodified": lambda repo_path, kwargs: ensure_files_unchanged(
        repo_path,
        files=kwargs["files"],
        reference_root=Path(kwargs["reference_root"]).resolve(),
        diffs_dir=kwargs.get("diffs_dir"),
    ),
    "cmakelists_outputs_code": lambda repo_path, kwargs: ensure_cmake_outputs_code(
        repo_path,
        cmake_path=kwargs.get("path", "CMakeLists.txt"),
    ),
}


def parse_args(problem_id: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"Run code review checks for problem {problem_id}"
    )
    parser.add_argument(
        "repo_url",
        help="Git repository URL to clone for review (e.g. https://github.com/user/repo.git)",
    )
    parser.add_argument(
        "--branch",
        default=None,
        help="Optional branch or tag name to checkout after cloning.",
    )
    return parser.parse_args()


def load_cr_list(problem_dir: Path, script_name: str) -> Iterable[ReviewItem]:
    cr_list_path = problem_dir / "cr_list.json"
    entries = json.loads(cr_list_path.read_text(encoding="utf-8"))
    for entry in entries:
        entry_script = entry.get("script")
        if entry_script and entry_script != script_name:
            continue
        name = entry.get("name")
        description = entry.get("description", "")
        args = entry.get("args", {})
        if not name:
            raise ValueError("cr_list.json 中存在缺少 name 的条目")

        handler = None
        if entry_script and entry_script.startswith("llm_as_a_judge"):
            handler = None
        else:
            if args.get("entries") is not None:
                handler = CHECK_REGISTRY.get("gitignore_entries")
            elif args.get("pattern") is not None and args.get("paths") is not None:
                handler = CHECK_REGISTRY.get("forbid_pattern")
            elif args.get("pattern") is not None:
                handler = CHECK_REGISTRY.get("forbid_pattern_recursive")
            elif args.get("files") is not None and args.get("allowed") is not None:
                handler = CHECK_REGISTRY.get("allowed_includes")
            elif args.get("files") is not None and args.get("reference_root") is not None:
                handler = CHECK_REGISTRY.get("require_unmodified")
            elif args.get("files") is not None:
                handler = CHECK_REGISTRY.get("require_files")
            elif args.get("path") is not None:
                handler = CHECK_REGISTRY.get("cmakelists_outputs_code")

        yield ReviewItem(
            name=name,
            description=description,
            script=entry_script or script_name,
            args=args,
            handler=handler,
        )


def run_git_clone(repo_url: str, target_dir: Path, branch: str | None) -> None:
    clone_cmd = ["git", "clone", "--depth", "1"]
    if branch:
        clone_cmd += ["--branch", branch]
    clone_cmd += [repo_url, str(target_dir)]

    subprocess.run(clone_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def execute_checks(problem_id: str) -> int:
    script_path = Path(__file__).resolve()
    problem_dir = script_path.parent / ".." / problem_id
    problem_dir = problem_dir.resolve()
    project_root = script_path.parents[3]

    args = parse_args(problem_id)
    script_name = Path(sys.argv[0]).name

    try:
        review_items = list(load_cr_list(problem_dir, script_name))
    except Exception as exc:  # noqa: BLE001
        print(f"❌ 加载 cr_list.json 失败：{exc}")
        return 1

    if not review_items:
        print("⚠️ 当前脚本在 cr_list.json 中没有匹配的检查条目，自动跳过。")
        return 0

    with tempfile.TemporaryDirectory(prefix=f"ojbench_cr_{problem_id}_") as tmpdir:
        repo_path = Path(tmpdir) / "repo"
        try:
            run_git_clone(args.repo_url, repo_path, args.branch)
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.decode(errors="ignore") if exc.stderr else str(exc)
            print("❌ git clone 失败：")
            print(stderr)
            return 1

        all_passed = True
        for item in review_items:
            print(f"▶️ 检查：{item.name}")
            if item.description:
                print(f"   说明：{item.description}")
            check_func = item.handler
            if check_func is None:
                print("⚠️ 当前检查需要人工或 LLM 审查，自动跳过。")
                continue
            kwargs = dict(item.args)
            # Handle reference_root for both require_unmodified and allowed_includes
            if "reference_root" in kwargs and isinstance(kwargs["reference_root"], str):
                ref_str = kwargs["reference_root"]
                if ref_str.startswith("${PROJECT_ROOT}"):
                    ref_str = ref_str.replace("${PROJECT_ROOT}", str(project_root))
                    kwargs["reference_root"] = Path(ref_str).resolve()
                else:
                    ref_path = Path(ref_str)
                    if not ref_path.is_absolute():
                        kwargs["reference_root"] = (project_root / ref_path).resolve()
                    else:
                        kwargs["reference_root"] = ref_path
            try:
                check_func(repo_path, kwargs)
            except CheckFailed as exc:
                print(f"❌ {exc}")
                all_passed = False
            except Exception as exc:  # noqa: BLE001
                print(f"❌ 检查过程中出现异常：{exc}")
                all_passed = False
            else:
                print("✅ 检查通过")

    return 0 if all_passed else 1

