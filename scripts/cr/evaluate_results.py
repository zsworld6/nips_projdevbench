#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List


REPO_URL_PATTERN = re.compile(r"https://github\.com/[^\s)]+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clone evaluation repositories and run Python-based code review checks."
    )
    parser.add_argument(
        "results_dir",
        nargs="?",
        default=None,
        help="Path to the evaluation results directory, e.g. logs/augment/GPT-5",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run code review for all agent/model combinations under logs/",
    )
    parser.add_argument(
        "--logs-root",
        default="logs",
        help="Root directory containing evaluation logs (default: logs). Used with --all.",
    )
    # Default to the directory where this script is located
    script_dir = Path(__file__).resolve().parent
    parser.add_argument(
        "--scripts-root",
        default=str(script_dir),
        help="Path to the directory that stores per-problem code review definitions (default: scripts/cr)",
    )
    return parser.parse_args()


def find_log_file(problem_dir: Path) -> Path | None:
    logs = sorted(problem_dir.glob("*.log"))
    return logs[0] if logs else None


def extract_repo_url(log_path: Path) -> str | None:
    with log_path.open(encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            match = REPO_URL_PATTERN.search(line)
            if match:
                url = match.group(0).rstrip(".,)")
                return url
    return None


def clone_repository(repo_url: str, destination_dir: Path) -> Path | None:
    repo_name = repo_url.rstrip("/").split("/")[-1]
    target_path = destination_dir / repo_name

    if (target_path / ".git").is_dir():
        return target_path

    try:
        subprocess.run(
            ["git", "clone", repo_url, str(target_path)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as exc:
        sys.stderr.write(
            f"[ERROR] Failed to clone {repo_url} into {target_path}: {exc.stderr.decode(errors='ignore')}\n"
        )
        return None

    return target_path


def load_cr_list(scripts_root: Path, problem_id: str) -> List[Dict]:
    cr_path = scripts_root / problem_id / "cr_list.json"
    if not cr_path.is_file():
        return []
    with cr_path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _parse_check_output(output: str) -> Dict[str, Dict[str, str]]:
    """Return mapping of rule name -> {'message': str, 'status': 'approved'/'未通过'}."""
    segments: Dict[str, List[str]] = {}
    current_rule = None
    for line in output.splitlines():
        if line.startswith("▶️ 检查："):
            rule = line[len("▶️ 检查：") :].strip()
            current_rule = rule
            segments[current_rule] = [line]
        elif current_rule is not None:
            segments[current_rule].append(line)

    results: Dict[str, Dict[str, str]] = {}
    for rule, lines in segments.items():
        segment_text = "\n".join(lines).strip()
        if "❌" in segment_text:
            status = "未通过"
        else:
            status = "approved"
        results[rule] = {"message": segment_text, "status": status}
    return results


def run_python_checks(
    repo_url: str,
    problem_id: str,
    python_entries: List[Dict],
    scripts_root: Path,
) -> List[Dict[str, str]]:
    # Group entries by script so we only run each script once
    grouped: Dict[str, List[Dict]] = {}
    for entry in python_entries:
        script_name = entry.get("script")
        grouped.setdefault(script_name, []).append(entry)

    results: List[Dict[str, str]] = []
    for script_name, entries in grouped.items():
        script_path = scripts_root / problem_id / script_name
        if not script_path.is_file():
            for entry in entries:
                results.append(
                    {
                        "rule": entry.get("name", "Unnamed Rule"),
                        "status": "未通过",
                        "message": f"脚本缺失: {script_path}",
                    }
                )
            continue

        cmd = ["python3", str(script_path), repo_url]
        try:
            completed = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            parsed = _parse_check_output(completed.stdout)
            for entry in entries:
                rule_name = entry.get("name", "Unnamed Rule")
                rule_result = parsed.get(rule_name)
                if rule_result is None:
                    status = "未通过" if completed.returncode != 0 else "approved"
                    message = completed.stdout.strip() or completed.stderr.strip()
                    results.append(
                        {
                            "rule": rule_name,
                            "status": status,
                            "message": message,
                        }
                    )
                else:
                    results.append(
                        {
                            "rule": rule_name,
                            "status": rule_result["status"],
                            "message": rule_result["message"],
                        }
                    )
        except Exception as exc:  # noqa: BLE001
            for entry in entries:
                results.append(
                    {
                        "rule": entry.get("name", "Unnamed Rule"),
                        "status": "未通过",
                        "message": f"运行脚本失败: {exc}",
                    }
                )

    return results


def get_commit_count(repo_path: Path) -> int:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo_path), "rev-list", "--count", "HEAD"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return int(completed.stdout.strip() or "0")
    except Exception:
        return 0


def write_results(
    output_dir: Path,
    repo_url: str,
    results: List[Dict[str, str]],
    *,
    commit_count: int | None = None,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "cr_evaluation.json"
    total = len(results)
    approved = sum(1 for item in results if item.get("status") == "approved")
    score = approved / total if total > 0 else None
    payload = {
        "repo_url": repo_url,
        "checks": results,
        "approved": approved,
        "total": total,
        "score": score,
    }
    if commit_count is not None:
        payload["commit_count"] = commit_count
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)


def find_all_agent_model_dirs(logs_root: Path) -> List[Path]:
    """Find all agent/model directories under logs_root."""
    dirs = []
    if not logs_root.is_dir():
        return dirs
    for agent_dir in sorted(logs_root.iterdir()):
        if not agent_dir.is_dir():
            continue
        for model_dir in sorted(agent_dir.iterdir()):
            if model_dir.is_dir():
                dirs.append(model_dir)
    return dirs


def process_results_dir(
    results_root: Path,
    scripts_root: Path,
    project_root: Path,
) -> int:
    """Process a single agent/model results directory. Returns number of problems processed."""
    if not results_root.is_dir():
        sys.stderr.write(f"[ERROR] Results directory not found: {results_root}\n")
        return 0

    # Extract agent and model from results_dir path (e.g., logs/augment/GPT-5 -> augment, GPT-5)
    parts = results_root.parts
    try:
        # Find 'logs' in the path and get agent/model after it
        logs_idx = parts.index('logs')
        if logs_idx + 2 < len(parts):
            agent_name = parts[logs_idx + 1]
            model_name = parts[logs_idx + 2]
        else:
            sys.stderr.write(f"[ERROR] Cannot extract agent/model from path: {results_root}\n")
            sys.stderr.write(f"Expected format: logs/<agent>/<model>\n")
            return 0
    except ValueError:
        # If 'logs' not found, try to infer from path structure
        # Assume format: .../logs/agent/model or similar
        if len(parts) >= 3:
            agent_name = parts[-2]
            model_name = parts[-1]
        else:
            sys.stderr.write(f"[ERROR] Cannot extract agent/model from path: {results_root}\n")
            sys.stderr.write(f"Expected format: logs/<agent>/<model>\n")
            return 0

    # Build output directory: cr_result/<agent>/<model>
    output_root = project_root / "cr_result" / agent_name / model_name

    processed_count = 0
    for problem_dir in sorted(results_root.iterdir()):
        if not problem_dir.is_dir():
            continue

        problem_id = problem_dir.name
        log_file = find_log_file(problem_dir)
        if not log_file:
            continue

        repo_url = extract_repo_url(log_file)
        if not repo_url:
            sys.stderr.write(f"[WARN] 未在日志 {log_file} 中找到仓库链接\n")
            continue

        cloned_path = clone_repository(repo_url, problem_dir)
        if cloned_path is None:
            continue

        cr_entries = load_cr_list(scripts_root, problem_id)
        python_entries = [
            entry
            for entry in cr_entries
            if entry.get("script", "").startswith("run") and entry.get("script", "").endswith(".py")
        ]

        # Output directory for this problem
        output_dir = output_root / problem_id

        commit_count = get_commit_count(cloned_path)
        if commit_count <= 1:
            if python_entries:
                results = [
                    {
                        "rule": entry.get("name", "Unnamed Rule"),
                        "status": "未通过",
                        "message": "仓库提交记录不足（commit_count <= 1），评测直接判定为未通过。",
                    }
                    for entry in python_entries
                ]
            else:
                results = [
                    {
                        "rule": "仓库提交检查",
                        "status": "未通过",
                        "message": "仓库提交记录不足（commit_count <= 1），评测直接判定为未通过。",
                    }
                ]
            write_results(output_dir, repo_url, results, commit_count=commit_count)
            processed_count += 1
            continue

        results = run_python_checks(repo_url, problem_id, python_entries, scripts_root)
        write_results(output_dir, repo_url, results, commit_count=commit_count)
        processed_count += 1

    return processed_count


def main() -> None:
    args = parse_args()
    scripts_root = Path(args.scripts_root).resolve()

    # Determine project root
    if args.results_dir:
        project_root = Path(args.results_dir).resolve().parents[2]
    else:
        project_root = Path.cwd()

    # Handle --all mode
    if args.all:
        logs_root = Path(args.logs_root).resolve()
        if not logs_root.is_dir():
            sys.stderr.write(f"[ERROR] Logs root directory not found: {logs_root}\n")
            sys.exit(1)

        all_dirs = find_all_agent_model_dirs(logs_root)
        if not all_dirs:
            sys.stderr.write(f"[WARN] No agent/model directories found under {logs_root}\n")
            sys.exit(0)

        print(f"Found {len(all_dirs)} agent/model combinations to process:")
        for d in all_dirs:
            print(f"  - {d.relative_to(logs_root.parent)}")
        print()

        total_processed = 0
        for results_dir in all_dirs:
            agent_model = f"{results_dir.parent.name}/{results_dir.name}"
            print(f"{'=' * 60}")
            print(f"Processing: {agent_model}")
            print(f"{'=' * 60}")
            count = process_results_dir(results_dir, scripts_root, logs_root.parent)
            total_processed += count
            print(f"Processed {count} problems for {agent_model}\n")

        print(f"{'=' * 60}")
        print(f"All done! Total problems processed: {total_processed}")
        return

    # Single directory mode (original behavior)
    if not args.results_dir:
        sys.stderr.write("[ERROR] Please provide results_dir or use --all flag.\n")
        sys.stderr.write("Usage:\n")
        sys.stderr.write("  python evaluate_results.py logs/augment/GPT-5\n")
        sys.stderr.write("  python evaluate_results.py --all\n")
        sys.exit(1)

    results_root = Path(args.results_dir).resolve()
    count = process_results_dir(results_root, scripts_root, project_root)
    print(f"Processed {count} problems.")


if __name__ == "__main__":
    main()

