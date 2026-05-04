#!/usr/bin/env python3
"""Compute max=N and max=1 exec scores from FINAL-LOGS only (winning runs).

Reuses the scoring function from analyze_exec_score_registry.py but reads
submission_ids_*.log from final-logs/<safe_combo>/<prob>/ instead of logs/.
"""
from __future__ import annotations
import json
import os
import importlib.util
from collections import defaultdict
from pathlib import Path
from typing import Dict

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = REPO_ROOT / 'results'

# Load helpers from the registry-based script (avoid running its main())
_spec = importlib.util.spec_from_file_location(
    "regbase",
    str(Path(__file__).with_name("analyze_exec_score_registry.py")),
)
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)

CACHE_PATH = os.environ.get('OJ_CACHE_PATH', '/tmp/oj_sub_cache.json')
FINAL_LOGS = Path(os.environ.get(
    'OJBENCH_FINAL_LOGS', str(REPO_ROOT / 'data' / 'final-logs')))

COMBO_TO_SAFE = {
    "Codex+GPT-5":            "Codex_GPT-5",
    "Codex+Gemini-3-Flash":   "Codex_Gemini-3-Flash",
    "Codex+Sonnet-4.5":       "Codex_Sonnet-4.5",
    "Codex+qwen3-235b":       "Codex_qwen3-235b",
    "Codex+GLM-4.6":          "Codex_GLM-4.6",
    "Codex+gpt-oss":          "Codex_gpt-oss",
    "CC+Sonnet-4.5":          "CC_Sonnet-4.5",
    "CC+Gemini-3-Flash":      "CC_Gemini-3-Flash",
    "CC+GPT-5":               "CC_GPT-5",
    "OpenHands+GPT-5":        "OpenHands_GPT-5",
    "OpenHands+Gemini-Flash": "OpenHands_Gemini-Flash",
    "OpenHands+Sonnet-4.5":   "OpenHands_Sonnet-4.5",
    "OpenHands+GLM-4.6":      "OpenHands_GLM-4.6",
    "OpenHands+qwen3-235b":   "OpenHands_qwen3-235b",
    "Gemini CLI+Flash":       "Gemini_CLI_Flash",
}


def discover_finallogs_subs():
    """combo -> {prob -> [(sid, timestamp), ...]} chronological."""
    out: Dict[str, Dict[str, list]] = {}
    for combo, safe in COMBO_TO_SAFE.items():
        out[combo] = defaultdict(list)
        d = FINAL_LOGS / safe
        if not d.exists():
            continue
        for prob_dir in sorted(d.iterdir()):
            if not prob_dir.is_dir():
                continue
            prob = prob_dir.name
            for log in sorted(prob_dir.glob('submission_ids_*.log')):
                for line in log.read_text(errors='ignore').splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        d2 = json.loads(line)
                        out[combo][prob].append(
                            (int(d2['submission_id']), d2.get('timestamp', ''))
                        )
                    except Exception:
                        continue
            out[combo][prob].sort(key=lambda x: x[1])
    return out


def main():
    cache = json.loads(Path(CACHE_PATH).read_text()) if Path(CACHE_PATH).exists() else {}
    print(f"Cache size: {len(cache)}")
    registry = mod.load_registry()
    problem_to_api_ids = mod.get_problem_api_ids(registry)
    scoring_config = mod.get_scoring_config(registry)
    default_max = registry.get('default', {}).get('max_submissions', 3)
    max_subs_map = {pid: int(info.get('max_submissions', default_max))
                    for pid, info in registry.get('problems', {}).items()}

    combo_subs = discover_finallogs_subs()
    all_problems = sorted(problem_to_api_ids.keys())

    out_maxN: Dict[str, Dict] = {}
    out_max1: Dict[str, Dict] = {}

    for combo in COMBO_TO_SAFE:
        prob_data = combo_subs.get(combo, {})
        per_prob_N: Dict[str, float] = {}
        per_prob_1: Dict[str, float] = {}
        cls: Dict[str, str] = {}
        for prob in all_problems:
            sids = [sid for sid, _ in prob_data.get(prob, [])]
            if not sids:
                continue
            scN = mod.score_problem_max1(
                prob, sids, cache, problem_to_api_ids, scoring_config,
                max_subs_total=max_subs_map.get(prob, default_max))
            sc1 = mod.score_problem_max1(
                prob, sids, cache, problem_to_api_ids, scoring_config,
                max_subs_total=1)
            if scN is None and sc1 is None:
                continue
            per_prob_N[prob] = scN if scN is not None else 0.0
            per_prob_1[prob] = sc1 if sc1 is not None else 0.0
            had_non_abort = any(
                (cache.get(str(sid), {}).get('result') or '').lower()
                not in ('abort', 'aborted')
                for sid in sids if cache.get(str(sid)))
            cls[prob] = 'submitted' if had_non_abort else 'tried_no_submit'

        def stats(d):
            scores = list(d.values())
            full = round(sum(scores) / len(scores), 2) if scores else 0.0
            sub_scores = [d[p] for p in cls if cls[p] == 'submitted' and p in d]
            filt = round(sum(sub_scores) / len(sub_scores), 2) if sub_scores else 0.0
            return full, filt, len(scores), sum(1 for v in cls.values() if v == 'submitted')

        fN, ffN, nN, sN = stats(per_prob_N)
        f1, ff1, _, _ = stats(per_prob_1)
        out_maxN[combo] = {
            "avg_exec_full128": fN, "avg_exec_filtered": ffN,
            "valid_count": nN, "submitted": sN,
            "per_problem": per_prob_N, "classifications": cls,
        }
        out_max1[combo] = {
            "avg_exec_full128": f1, "avg_exec_filtered": ff1,
            "valid_count": nN, "submitted": sN,
            "per_problem": per_prob_1, "classifications": cls,
        }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / 'maxN_exec_finallogs.json').write_text(
        json.dumps(out_maxN, indent=2, ensure_ascii=False))
    (RESULTS_DIR / 'max1_exec_finallogs.json').write_text(
        json.dumps(out_max1, indent=2, ensure_ascii=False))

    print(f"\n{'combo':28s} {'maxN_full':>9s} {'maxN_filt':>9s} {'max1_full':>9s} {'max1_filt':>9s}  {'n':>3s}")
    for c in sorted(out_maxN.keys(), key=lambda x: -out_maxN[x]['avg_exec_full128']):
        v = out_maxN[c]; v1 = out_max1[c]
        print(f"{c:28s} {v['avg_exec_full128']:9.2f} {v['avg_exec_filtered']:9.2f} "
              f"{v1['avg_exec_full128']:9.2f} {v1['avg_exec_filtered']:9.2f}  {v['valid_count']:3d}")


if __name__ == "__main__":
    main()
