#!/usr/bin/env python3
"""
合并 Code Review 结果：将 cr_evaluation.json 和 result.json 合并为 all_result.json

最终分数计算逻辑：
- Python 规则检查：每个通过的 check 得 1 分
- LLM 评审：每个评分项按 10 分制转换为 0-1 分
- 最终分数 = (总得分 / 总可得分) × 100
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge cr_evaluation.json and result.json into all_result.json"
    )
    parser.add_argument(
        "cr_result_dir",
        nargs="?",
        default=None,
        help="Path to the CR result directory, e.g. cr_result/augment/GPT-5",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Merge results for all agent/model combinations under cr_result/",
    )
    parser.add_argument(
        "--cr-result-root",
        default="cr_result",
        help="Root directory containing CR results (default: cr_result). Used with --all.",
    )
    return parser.parse_args()


def load_json_file(path: Path) -> Optional[Dict[str, Any]]:
    """Load a JSON file, return None if not found or invalid."""
    if not path.is_file():
        return None
    try:
        with path.open(encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        sys.stderr.write(f"[WARN] Failed to load {path}: {e}\n")
        return None


def map_llm_scores(llm_review: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Map LLM scores from 0-10 scale to 0-1 scale.
    Identify readability/organization criteria for special handling.
    """
    criteria_scores = llm_review.get("criteria_scores", [])
    mapped = []
    
    readability_keywords = [
        "readability", "organization", "structure", "clarity", 
        "clean", "format", "style", "maintainability"
    ]
    
    for item in criteria_scores:
        name = item.get("name", "")
        original_score = item.get("result", 0)
        
        # Check if this is a readability/organization criterion
        name_lower = name.lower()
        is_readability = any(kw in name_lower for kw in readability_keywords)
        
        mapped.append({
            "name": name,
            "original_score": original_score,
            "mapped_score": original_score / 10.0,
            "is_readability_or_organization": is_readability,
        })
    
    return mapped


def calculate_combined_score(
    cr_evaluation: Optional[Dict[str, Any]],
    llm_review: Optional[Dict[str, Any]],
    mapped_scores: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Calculate combined score from CR evaluation and LLM review.
    
    Scoring:
    - CR evaluation: 1 point per approved check
    - LLM review: score/10 per criterion (0-1 scale)
    - Final score = (total_achieved / total_possible) × 100
    """
    # CR evaluation scores
    cr_approved = 0
    cr_total = 0
    commit_count = 0
    
    if cr_evaluation:
        cr_approved = cr_evaluation.get("approved", 0)
        cr_total = cr_evaluation.get("total", 0)
        commit_count = cr_evaluation.get("commit_count", 0)
    
    # LLM review scores
    llm_achieved = sum(item["mapped_score"] for item in mapped_scores)
    llm_possible = len(mapped_scores) * 1.0 if mapped_scores else 0.0
    
    # Combined calculation
    total_achieved = cr_approved + llm_achieved
    total_possible = cr_total + llm_possible
    
    ratio = total_achieved / total_possible if total_possible > 0 else 0.0
    final_score = ratio * 100.0
    
    # Check if commit count is suspicious (<=1 usually means copied/forked)
    commit_count_check = commit_count <= 1
    
    return {
        "cr_evaluation": {
            "approved": cr_approved,
            "total": cr_total,
            "commit_count": commit_count,
        },
        "llm_review": {
            "total_achieved_score": round(llm_achieved, 2),
            "total_possible_score": round(llm_possible, 2),
        },
        "combined": {
            "total_achieved_score": round(total_achieved, 2),
            "total_possible_score": round(total_possible, 2),
            "ratio": round(ratio, 4),
        },
        "final_score_0_100": round(final_score, 1),
        "commit_count_check": commit_count_check,
    }


def merge_results_for_problem(problem_dir: Path) -> bool:
    """
    Merge cr_evaluation.json and result.json into all_result.json for a single problem.
    Returns True if successful.
    """
    cr_eval_path = problem_dir / "cr_evaluation.json"
    llm_result_path = problem_dir / "result.json"
    output_path = problem_dir / "all_result.json"
    
    # Load existing results
    cr_evaluation = load_json_file(cr_eval_path)
    llm_review = load_json_file(llm_result_path)
    
    # Need at least one of them to proceed
    if cr_evaluation is None and llm_review is None:
        sys.stderr.write(f"[WARN] No CR results found in {problem_dir}\n")
        return False
    
    # Get repo URL from either source
    repo_url = None
    if cr_evaluation:
        repo_url = cr_evaluation.get("repo_url")
    if not repo_url and llm_review:
        repo_url = llm_review.get("repo_url")
    
    # Map LLM scores
    mapped_scores = []
    if llm_review:
        mapped_scores = map_llm_scores(llm_review)
    
    # Calculate combined score
    score_calculation = calculate_combined_score(cr_evaluation, llm_review, mapped_scores)
    
    # Build the merged result
    all_result: Dict[str, Any] = {}
    
    if repo_url:
        all_result["repo_url"] = repo_url
    
    if cr_evaluation:
        all_result["cr_evaluation"] = cr_evaluation
    
    if llm_review:
        all_result["llm_review"] = llm_review
    
    if mapped_scores:
        all_result["mapped_scores"] = mapped_scores
    
    all_result["score_calculation"] = score_calculation
    
    # Write the merged result
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(all_result, fh, ensure_ascii=False, indent=2)
    
    return True


def process_agent_model_dir(agent_model_dir: Path) -> int:
    """
    Process all problem directories under an agent/model directory.
    Returns number of problems processed.
    """
    if not agent_model_dir.is_dir():
        sys.stderr.write(f"[ERROR] Directory not found: {agent_model_dir}\n")
        return 0
    
    processed = 0
    for problem_dir in sorted(agent_model_dir.iterdir()):
        if not problem_dir.is_dir():
            continue
        
        problem_id = problem_dir.name
        if merge_results_for_problem(problem_dir):
            print(f"  ✅ Merged results for problem {problem_id}")
            processed += 1
    
    return processed


def find_all_agent_model_dirs(cr_result_root: Path) -> List[Path]:
    """Find all agent/model directories under cr_result_root."""
    dirs = []
    if not cr_result_root.is_dir():
        return dirs
    
    for agent_dir in sorted(cr_result_root.iterdir()):
        if not agent_dir.is_dir():
            continue
        for model_dir in sorted(agent_dir.iterdir()):
            if model_dir.is_dir():
                dirs.append(model_dir)
    
    return dirs


def main() -> None:
    args = parse_args()
    
    if args.all:
        # Process all agent/model combinations
        cr_result_root = Path(args.cr_result_root).resolve()
        if not cr_result_root.is_dir():
            sys.stderr.write(f"[ERROR] CR result root not found: {cr_result_root}\n")
            sys.exit(1)
        
        all_dirs = find_all_agent_model_dirs(cr_result_root)
        if not all_dirs:
            sys.stderr.write(f"[WARN] No agent/model directories found under {cr_result_root}\n")
            sys.exit(0)
        
        print(f"Found {len(all_dirs)} agent/model combinations to process:")
        for d in all_dirs:
            print(f"  - {d.relative_to(cr_result_root.parent)}")
        print()
        
        total_processed = 0
        for agent_model_dir in all_dirs:
            agent_model = f"{agent_model_dir.parent.name}/{agent_model_dir.name}"
            print(f"Processing: {agent_model}")
            count = process_agent_model_dir(agent_model_dir)
            total_processed += count
            print(f"  Merged {count} problems\n")
        
        print(f"{'=' * 50}")
        print(f"All done! Total problems merged: {total_processed}")
        
    else:
        # Process a single agent/model directory
        if not args.cr_result_dir:
            sys.stderr.write("[ERROR] Please provide cr_result_dir or use --all flag.\n")
            sys.stderr.write("Usage:\n")
            sys.stderr.write("  python merge_cr_results.py cr_result/augment/GPT-5\n")
            sys.stderr.write("  python merge_cr_results.py --all\n")
            sys.exit(1)
        
        cr_result_dir = Path(args.cr_result_dir).resolve()
        print(f"Processing: {cr_result_dir}")
        count = process_agent_model_dir(cr_result_dir)
        print(f"Merged {count} problems.")


if __name__ == "__main__":
    main()
