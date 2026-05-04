#!/usr/bin/env python3
"""Recompute per-problem interaction stats (turns + tokens) over the 128-problem
benchmark using the 10 combos with parseable token/turn data:
  - 3 CC combos (CC_Sonnet-4.5, CC_Gemini-3-Flash, CC_GPT-5)
  - 6 Codex combos (Codex_GPT-5, Codex_Gemini-3-Flash, Codex_Sonnet-4.5,
                    Codex_qwen3-235b, Codex_GLM-4.6, Codex_gpt-oss)
  - 1 Gemini CLI combo (Gemini_CLI_Flash)

OpenHands stdout lacks token info -> skipped (documented).
"""
from __future__ import annotations

import json
import os
import re
import sys
from glob import glob
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = REPO_ROOT / "results"
LOGS_ROOT = Path(os.environ.get(
    "OJBENCH_FINAL_LOGS", str(REPO_ROOT / "data" / "final-logs")))
EXEC_SCORES = Path(os.environ.get(
    "EXEC_SCORES_JSON", str(RESULTS_DIR / "maxN_exec_finallogs.json")))
OUT_JSON = RESULTS_DIR / "per_problem_interaction_v2.json"

CC_COMBOS = ["CC_Sonnet-4.5", "CC_Gemini-3-Flash", "CC_GPT-5"]
CODEX_COMBOS = [
    "Codex_GPT-5",
    "Codex_Gemini-3-Flash",
    "Codex_Sonnet-4.5",
    "Codex_qwen3-235b",
    "Codex_GLM-4.6",
    "Codex_gpt-oss",
]
GEMINI_COMBOS = ["Gemini_CLI_Flash"]
ALL_COMBOS = CC_COMBOS + CODEX_COMBOS + GEMINI_COMBOS

# combo_safe -> combo_key in maxN_exec_finallogs.json
COMBO_SAFE_TO_KEY = {
    "CC_Sonnet-4.5": "CC+Sonnet-4.5",
    "CC_Gemini-3-Flash": "CC+Gemini-3-Flash",
    "CC_GPT-5": "CC+GPT-5",
    "Codex_GPT-5": "Codex+GPT-5",
    "Codex_Gemini-3-Flash": "Codex+Gemini-3-Flash",
    "Codex_Sonnet-4.5": "Codex+Sonnet-4.5",
    "Codex_qwen3-235b": "Codex+qwen3-235b",
    "Codex_GLM-4.6": "Codex+GLM-4.6",
    "Codex_gpt-oss": "Codex+gpt-oss",
    "Gemini_CLI_Flash": "Gemini CLI+Flash",
}


def find_log_file(combo_safe: str, prob: str) -> Optional[Path]:
    """Find oj_eval_*.log for combo/prob."""
    d = LOGS_ROOT / combo_safe / prob
    if not d.is_dir():
        return None
    candidates = sorted(d.glob("oj_eval_*.log"))
    return candidates[-1] if candidates else None


def parse_cc_log(path: Path) -> Optional[dict]:
    """Parse a Claude Code stream-json log.

    Strategy: prefer the final 'type':'result' line which carries `num_turns`
    plus a fully-cumulative final `usage` block. If absent, fall back to
    summing per-turn tool_use counts and per-message usage entries.
    """
    if not path.is_file():
        return None
    last_result = None
    tool_use_count = 0
    sum_input = sum_cache_create = sum_cache_read = sum_output = 0
    n_assistant_msgs_with_usage = 0
    # We de-dup by uuid (per-emission unique id) to avoid double-counting the
    # same call when content fields are emitted across multiple lines that
    # share the same message id+usage. CC_GPT-5 logs frequently lack `msg.id`
    # entirely AND have zero-valued usage (proxy stripped both), so the
    # result block is the only signal there.
    seen_uuids = set()
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line.startswith("{"):
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                t = obj.get("type")
                if t == "result":
                    last_result = obj
                elif t == "assistant":
                    msg = obj.get("message", {})
                    msg_id = msg.get("id")
                    uuid = obj.get("uuid")
                    content = msg.get("content", []) or []
                    for c in content:
                        if isinstance(c, dict) and c.get("type") == "tool_use":
                            tool_use_count += 1
                    usage = msg.get("usage")
                    # The same usage block is repeated per emitted content
                    # item under a single API response. Use msg_id when
                    # available; otherwise fall back to summing every uuid
                    # (we'll only get over-count for splits, not for shared).
                    dedupe_key = msg_id if msg_id else None
                    if usage and dedupe_key:
                        if dedupe_key in seen_uuids:
                            continue
                        seen_uuids.add(dedupe_key)
                        sum_input += int(usage.get("input_tokens", 0) or 0)
                        sum_cache_create += int(usage.get("cache_creation_input_tokens", 0) or 0)
                        sum_cache_read += int(usage.get("cache_read_input_tokens", 0) or 0)
                        sum_output += int(usage.get("output_tokens", 0) or 0)
                        n_assistant_msgs_with_usage += 1
                    elif usage and not dedupe_key:
                        # No msg id; use uuid to dedupe within this emission.
                        if uuid in seen_uuids:
                            continue
                        seen_uuids.add(uuid)
                        sum_input += int(usage.get("input_tokens", 0) or 0)
                        sum_cache_create += int(usage.get("cache_creation_input_tokens", 0) or 0)
                        sum_cache_read += int(usage.get("cache_read_input_tokens", 0) or 0)
                        sum_output += int(usage.get("output_tokens", 0) or 0)
                        n_assistant_msgs_with_usage += 1
    except OSError:
        return None

    if last_result is not None:
        usage = last_result.get("usage", {}) or {}
        # The result block reports the cumulative session totals.
        result_total = (
            int(usage.get("input_tokens", 0) or 0)
            + int(usage.get("cache_creation_input_tokens", 0) or 0)
            + int(usage.get("cache_read_input_tokens", 0) or 0)
            + int(usage.get("output_tokens", 0) or 0)
        )
        # Use tool_use count for "interaction turns"; fall back to num_turns.
        turns = tool_use_count if tool_use_count > 0 else int(last_result.get("num_turns", 0) or 0)
        # Pick whichever total is larger -- handles the cases where either the
        # result.usage or the per-message stream might be partially missing.
        summed_total = sum_input + sum_cache_create + sum_cache_read + sum_output
        total = max(result_total, summed_total)
        return {
            "turns": turns,
            "tokens": total,
            "result_usage": usage,
            "summed_input": sum_input,
            "summed_cache_create": sum_cache_create,
            "summed_cache_read": sum_cache_read,
            "summed_output": sum_output,
            "source": "cc_result_block",
        }

    # Fallback: rely on summed assistant usage + tool_use count.
    # If both turns and summed tokens are zero, treat as unparseable.
    summed_total = sum_input + sum_cache_create + sum_cache_read + sum_output
    if tool_use_count == 0 and summed_total == 0:
        return None
    # If we have turns but zero tokens (CC_GPT-5 with stripped usage and no
    # result block), skip token aggregation -- caller treats this as missing.
    if summed_total == 0:
        return None
    return {
        "turns": tool_use_count,
        "tokens": summed_total,
        "summed_input": sum_input,
        "summed_cache_create": sum_cache_create,
        "summed_cache_read": sum_cache_read,
        "summed_output": sum_output,
        "source": "cc_summed",
    }


_CODEX_TURN_RE = re.compile(r'\{"type":"turn\.completed","usage":\{[^}]*\}\}')


def parse_codex_log(path: Path) -> Optional[dict]:
    """Parse a Codex CLI stdout log: count `command_execution` items as turns,
    sum `turn.completed.usage` JSON blobs for tokens.
    """
    if not path.is_file():
        return None
    cmd_exec = 0
    sum_input = sum_cached = sum_output = 0
    found_any = False
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            for line in f:
                # We want each *started* command execution counted exactly once.
                # Use item.completed for command_execution to count successful turns.
                if '"type":"item.completed"' in line and '"type":"command_execution"' in line:
                    cmd_exec += 1
                    found_any = True
                if '"type":"turn.completed"' in line and '"usage"' in line:
                    found_any = True
                    # Extract usage object
                    try:
                        # Find first { ... } JSON object on the line
                        start = line.find("{")
                        if start >= 0:
                            obj = json.loads(line[start:])
                            usage = obj.get("usage", {}) or {}
                            sum_input += int(usage.get("input_tokens", 0) or 0)
                            sum_cached += int(usage.get("cached_input_tokens", 0) or 0)
                            sum_output += int(usage.get("output_tokens", 0) or 0)
                    except (json.JSONDecodeError, ValueError):
                        pass
    except OSError:
        return None
    if not found_any:
        return None
    # Codex `input_tokens` already INCLUDES `cached_input_tokens` (per OpenAI conv).
    # To match CC accounting (input + cache + output), add cached separately so
    # the aggregate comparison is consistent across providers.
    total = sum_input + sum_cached + sum_output
    # Some Codex runs have turn.completed blocks with all-zero token fields
    # (proxy stripped them). Treat these as token-data-missing.
    if total == 0:
        return None
    return {
        "turns": cmd_exec,
        "tokens": total,
        "input_tokens": sum_input,
        "cached_input_tokens": sum_cached,
        "output_tokens": sum_output,
        "source": "codex_stdout",
    }


def parse_gemini_log(path: Path) -> Optional[dict]:
    """Parse a Gemini CLI stdout log. Final line:
    {"type":"result", ..., "stats":{"total_tokens":N, "input_tokens":I,
                                    "output_tokens":O, "tool_calls":T, ...}}
    """
    if not path.is_file():
        return None
    last_stats = None
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not (line.startswith("{") and '"stats"' in line):
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if obj.get("type") == "result" and "stats" in obj:
                    last_stats = obj["stats"]
    except OSError:
        return None
    if not last_stats:
        return None
    total = int(last_stats.get("total_tokens", 0) or 0)
    if total == 0:
        total = (
            int(last_stats.get("input_tokens", 0) or 0)
            + int(last_stats.get("output_tokens", 0) or 0)
        )
    return {
        "turns": int(last_stats.get("tool_calls", 0) or 0),
        "tokens": total,
        "input_tokens": int(last_stats.get("input_tokens", 0) or 0),
        "output_tokens": int(last_stats.get("output_tokens", 0) or 0),
        "source": "gemini_stats",
    }


def parse_combo_problem(combo_safe: str, prob: str) -> Optional[dict]:
    log = find_log_file(combo_safe, prob)
    if log is None:
        return None
    if combo_safe.startswith("CC_"):
        return parse_cc_log(log)
    if combo_safe.startswith("Codex_"):
        return parse_codex_log(log)
    if combo_safe.startswith("Gemini_CLI"):
        return parse_gemini_log(log)
    return None


def main() -> None:
    # Discover all 128 problem IDs from the 'problems' canonical set: take the
    # union of problem dirs across all combos.
    all_problems = set()
    for combo_safe in ALL_COMBOS:
        d = LOGS_ROOT / combo_safe
        if not d.is_dir():
            continue
        for p in d.iterdir():
            if p.is_dir() and p.name.isdigit() and len(p.name) == 3:
                all_problems.add(p.name)
    problems_sorted = sorted(all_problems)

    # Load exec scores for "Final Score" column.
    try:
        with EXEC_SCORES.open("r") as f:
            exec_data = json.load(f)
    except (OSError, json.JSONDecodeError):
        exec_data = {}

    # Per (combo, prob) parse
    raw_per_pair: dict[str, dict[str, dict]] = {}
    skipped: list[tuple[str, str]] = []
    for combo_safe in ALL_COMBOS:
        raw_per_pair[combo_safe] = {}
        for prob in problems_sorted:
            r = parse_combo_problem(combo_safe, prob)
            if r is None:
                skipped.append((combo_safe, prob))
                continue
            raw_per_pair[combo_safe][prob] = r

    # Aggregate per problem
    per_problem: dict[str, dict] = {}
    for prob in problems_sorted:
        per_combo_turns = []
        per_combo_tokens = []
        per_combo_scores = []
        contributing_combos = []
        for combo_safe in ALL_COMBOS:
            entry = raw_per_pair[combo_safe].get(prob)
            if entry is None:
                continue
            per_combo_turns.append(entry["turns"])
            per_combo_tokens.append(entry["tokens"])
            contributing_combos.append(combo_safe)
            ckey = COMBO_SAFE_TO_KEY[combo_safe]
            sc = (exec_data.get(ckey, {}) or {}).get("per_problem", {}).get(prob)
            if sc is not None:
                per_combo_scores.append(float(sc))
        if not per_combo_turns:
            continue
        n = len(per_combo_turns)
        avg_turns = sum(per_combo_turns) / n
        avg_tokens = sum(per_combo_tokens) / n
        per_problem[prob] = {
            "avg_turns": round(avg_turns, 2),
            "avg_tokens_M": round(avg_tokens / 1_000_000, 3),
            "n_combos": n,
            "min_turns": int(min(per_combo_turns)),
            "max_turns": int(max(per_combo_turns)),
            "min_tokens_M": round(min(per_combo_tokens) / 1_000_000, 3),
            "max_tokens_M": round(max(per_combo_tokens) / 1_000_000, 3),
            "avg_score": (round(sum(per_combo_scores) / len(per_combo_scores), 2)
                          if per_combo_scores else None),
            "n_scored": len(per_combo_scores),
            "combos": contributing_combos,
        }

    # Save full JSON.
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with OUT_JSON.open("w") as f:
        json.dump(per_problem, f, indent=2)

    # Headline averages.
    n_problems = len(per_problem)
    overall_mean_turns = (sum(d["avg_turns"] for d in per_problem.values()) / n_problems
                          if n_problems else 0.0)
    overall_mean_tokens_M = (sum(d["avg_tokens_M"] for d in per_problem.values()) / n_problems
                             if n_problems else 0.0)

    print("=" * 72)
    print("Per-problem interaction recomputation (v2)")
    print("=" * 72)
    print(f"Combos used: {len(ALL_COMBOS)}  ({', '.join(ALL_COMBOS)})")
    print(f"Problems with >=1 combo of data: {n_problems}")
    print(f"Overall mean turns (mean of per-problem averages):  {overall_mean_turns:.2f}")
    print(f"Overall mean tokens (M) (mean of per-problem avgs): {overall_mean_tokens_M:.3f}M")
    print(f"Skipped (combo, prob) pairs (missing/unparseable): {len(skipped)}")
    print()

    # 20-row LaTeX-ready subset (problems 001-020, matching old appendix layout)
    subset = [f"{i:03d}" for i in range(1, 21)]
    print("LaTeX appendix subset (problems 001-020):")
    print(r"% Problem ID  & avg_turns  & avg_tokens(M)  & n_combos  & avg_score  \\")
    for prob in subset:
        d = per_problem.get(prob)
        if d is None:
            print(f"%   {prob}  --  no data")
            continue
        sc = "n/a" if d["avg_score"] is None else f"{d['avg_score']:.2f}"
        print(f"  {prob}  &  {d['avg_turns']:>6.1f}  &  "
              f"{d['avg_tokens_M']:>6.2f}  &  {d['n_combos']:>2d}  &  {sc}  \\\\")
    print()

    # Top-5 / bottom-5 by avg turns (only problems with full or near-full coverage)
    rich = [(p, d) for p, d in per_problem.items() if d["n_combos"] >= 5]
    rich.sort(key=lambda kv: kv[1]["avg_turns"])
    bottom5 = rich[:5]
    top5 = rich[-5:][::-1]

    print("Bottom-5 (lowest avg turns, n_combos>=5):")
    print(f"{'Prob':<6}{'avg_turns':<12}{'avg_tok_M':<12}{'n':<4}{'score':<8}")
    for p, d in bottom5:
        sc = "n/a" if d["avg_score"] is None else f"{d['avg_score']:.1f}"
        print(f"{p:<6}{d['avg_turns']:<12.1f}{d['avg_tokens_M']:<12.2f}"
              f"{d['n_combos']:<4d}{sc:<8}")
    print()
    print("Top-5 (highest avg turns, n_combos>=5):")
    print(f"{'Prob':<6}{'avg_turns':<12}{'avg_tok_M':<12}{'n':<4}{'score':<8}")
    for p, d in top5:
        sc = "n/a" if d["avg_score"] is None else f"{d['avg_score']:.1f}"
        print(f"{p:<6}{d['avg_turns']:<12.1f}{d['avg_tokens_M']:<12.2f}"
              f"{d['n_combos']:<4d}{sc:<8}")
    print()

    # Per-combo coverage and per-combo mean turn/token (for context).
    print("Per-combo coverage and mean stats (over combo's own parseable problems):")
    print(f"{'combo':<25}{'parseable':>10}{'on_disk':>9}{'mean_turns':>12}{'mean_tokens_M':>15}")
    for combo_safe in ALL_COMBOS:
        entries = [v for v in raw_per_pair[combo_safe].values()]
        n_have = len(entries)
        n_dir = len(list((LOGS_ROOT / combo_safe).iterdir())) if (LOGS_ROOT / combo_safe).is_dir() else 0
        if n_have:
            mt = sum(e["turns"] for e in entries) / n_have
            mtok = sum(e["tokens"] for e in entries) / n_have / 1_000_000
        else:
            mt, mtok = 0.0, 0.0
        print(f"  {combo_safe:<23}{n_have:>10}{n_dir:>9}{mt:>12.1f}{mtok:>15.3f}")
    print()
    print(f"Wrote: {OUT_JSON}")


if __name__ == "__main__":
    main()
