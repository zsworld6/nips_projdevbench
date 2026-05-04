#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OJBench execution-score analysis — registry-consistent maxN version.

Same multi-subproblem weighted scoring formula as analyze_exec_score.py, but
caps per-problem submissions according to ``max_submissions`` in
``config/problem_registry.json``. Submission verdicts are read from a local
OJ submission cache (``$OJ_CACHE_PATH``); cache misses fall back to the
OJ HTTP API using ``$OJ_TOKEN``.

Usage:
  OJ_TOKEN=oj-xxxxx python3 scripts/analyze/analyze_exec_score_registry.py
Output:
  results/maxN_exec_scores_registry.json
"""

import os
import pathlib
import re
import json
import sys
import time
import threading
import requests
from typing import Dict, Any, Optional, Tuple, List, Set
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============================================================================
# Configuration (override via environment variables)
# ============================================================================

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
ROOT = os.environ.get('OJBENCH_ROOT', str(REPO_ROOT))
LOGS_DIR = os.environ.get('OJBENCH_LOGS', os.path.join(ROOT, 'logs'))
REGISTRY_FILE = os.path.join(REPO_ROOT, 'config', 'problem_registry.json')
API_BASE_URL = os.environ.get('OJ_API_BASE', 'https://acm.sjtu.edu.cn')
OJ_TOKEN = os.environ.get('OJ_TOKEN', '')

CACHE_PATH = os.environ.get('OJ_CACHE_PATH', '/tmp/oj_sub_cache.json')
OUT_PATH = os.environ.get(
    'EXEC_SCORE_OUT',
    str(REPO_ROOT / 'results' / 'maxN_exec_scores_registry.json'),
)

MAX_WORKERS = 8
REQUEST_DELAY = 0.0  # cache misses are rare; rely on retries
MAX_RETRIES = 4
RETRY_BASE_DELAY = 2

REPO_URL_PATTERN = re.compile(r'✅\s*Repository created:\s*(https://github\.com/[^\s]+)')

# ============================================================================
# Combo (paper name) → list of (agent_dir, model_dir_glob)
# Maps multi-round directories under logs/<agent>/<dir>/ to one combo.
# Glob applied via fnmatch; trailing '*' to allow round suffixes.
# ============================================================================

COMBO_DIRS: Dict[str, List[Tuple[str, str]]] = {
    "Codex+GPT-5":         [("codex", "gpt-5*"), ("codex", "openai-gpt-5*"), ("codex", "gzy-gpt-5-responses*")],
    "Codex+Gemini-3-Flash":[("codex", "google-gemini-3-flash*")],
    "Codex+Sonnet-4.5":    [("codex", "claude-sonnet-4-5-20250929*"), ("codex", "anthropic-claude-sonnet-4.5*")],
    "Codex+qwen3-235b":    [("codex", "qwen3-235b*")],
    "Codex+GLM-4.6":       [("codex", "GLM-4.6*")],
    "Codex+gpt-oss":       [("codex", "gpt-oss-120b*")],
    "CC+Sonnet-4.5":       [("claude-code-login-in-with-pro", "claude-sonnet-4-5-20250929*"),
                            ("claude-code-login-in-with-pro", "sonnet-4.5*"),
                            ("claude-code", "claude-sonnet-4-5-20250929*"),
                            ("claude-code", "sonnet-4.5*")],
    "CC+Gemini-3-Flash":   [("claude-code", "google-gemini-3-flash*"),
                            ("claude-code", "gemini-3-flash-preview*"),
                            ("claude-code", "gzy-gemini-3-flash*")],
    "CC+GPT-5":            [("claude-code", "gpt-5*")],
    "OpenHands+GPT-5":     [("openhands", "gpt-5*")],
    "OpenHands+Gemini-Flash":[("openhands", "google-gemini-3-flash*")],
    "OpenHands+Sonnet-4.5":[("openhands", "claude-sonnet-4-5-20250929*"), ("openhands", "anthropic-claude-sonnet-4.5*")],
    "OpenHands+GLM-4.6":   [("openhands", "GLM-4.6*")],
    "OpenHands+qwen3-235b":[("openhands", "qwen3-235b*")],
    "Gemini CLI+Flash":    [("gemini-cli", "gemini-3-flash*")],
}

# ============================================================================
# Special scoring (006 Minesweeper Advanced 2877)
# ============================================================================

MINESWEEPER_ADVANCED_BASELINES = {'rubbish': 39625, 'baseline1': 100449, 'baseline2': 136481}

def calculate_minesweeper_advanced_score(raw_score: float) -> float:
    rubbish = MINESWEEPER_ADVANCED_BASELINES['rubbish']
    baseline1 = MINESWEEPER_ADVANCED_BASELINES['baseline1']
    baseline2 = MINESWEEPER_ADVANCED_BASELINES['baseline2']
    pct_baseline1 = 10 / 35 * 100
    pct_baseline2 = 30 / 35 * 100
    if raw_score < rubbish:
        return 0
    elif raw_score < baseline1:
        ratio = (raw_score - rubbish) / (baseline1 - rubbish)
        return ratio * pct_baseline1
    elif raw_score < baseline2:
        ratio = (raw_score - baseline1) / (baseline2 - baseline1)
        return pct_baseline1 + ratio * (pct_baseline2 - pct_baseline1)
    else:
        return 100.0

# ============================================================================
# Registry
# ============================================================================

def load_registry() -> Dict:
    with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_problem_api_ids(registry: Dict) -> Dict[str, List[str]]:
    out = {}
    for prob, info in registry.get('problems', {}).items():
        out[prob] = [x.strip() for x in info.get('oj_id', '').split(',') if x.strip()]
    return out

def get_scoring_config(registry: Dict) -> Dict[str, Dict]:
    out = {}
    for prob, info in registry.get('problems', {}).items():
        out[prob] = {
            'score_weight': info.get('score_weight', {}),
            'score_full': info.get('score_full', {}),
        }
    return out

# ============================================================================
# Cache (shared with /tmp/oj_sub_cache.json)
# ============================================================================

cache_lock = threading.Lock()

def load_cache() -> Dict[str, Dict]:
    if os.path.isfile(CACHE_PATH):
        try:
            with open(CACHE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] Cache load failed: {e}", flush=True)
            return {}
    return {}

def save_cache(cache: Dict[str, Dict]):
    with cache_lock:
        tmp = CACHE_PATH + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(cache, f)
        os.replace(tmp, CACHE_PATH)

# ============================================================================
# API client
# ============================================================================

session = requests.Session()
session.headers.update({
    "Authorization": f"Bearer {OJ_TOKEN}",
    "User-Agent": "OJ-Python-Client-max1/1.0",
})

def fetch_submission(sid: int) -> Optional[Dict]:
    """Returns cache record {result, score, problem_id, full_score} or None."""
    url = f"{API_BASE_URL}/OnlineJudge/api/v1/submission/{sid}"
    for attempt in range(MAX_RETRIES):
        try:
            if attempt > 0:
                time.sleep(RETRY_BASE_DELAY * (2 ** (attempt - 1)))
            r = session.get(url, timeout=15)
            if r.status_code == 200:
                d = r.json()
                rec = {
                    "result": d.get("status") or d.get("details", {}).get("result"),
                    "score": d.get("score", d.get("details", {}).get("score", 0.0)) or 0.0,
                    "problem_id": d.get("problem", {}).get("id") if d.get("problem") else None,
                    "full_score": None,
                }
                return rec
            elif r.status_code == 429:
                continue
            else:
                return None
        except Exception:
            continue
    return None

# ============================================================================
# Walk logs/<agent>/<model>/<prob>/submission_ids_*.log
# ============================================================================

import fnmatch

def discover_submissions() -> Dict[str, Dict[str, List[Tuple[int, str]]]]:
    """
    Returns: combo_paper_name -> { problem -> [(sid_int, source_path), ...] }
    Submissions are deduplicated across rounds, sorted by sid_int.
    """
    out: Dict[str, Dict[str, List[Tuple[int, str]]]] = {c: defaultdict(list) for c in COMBO_DIRS}
    seen_per_combo_prob: Dict[Tuple[str, str], Set[int]] = defaultdict(set)

    for combo, mappings in COMBO_DIRS.items():
        for agent_name, model_glob in mappings:
            agent_root = os.path.join(LOGS_DIR, agent_name)
            if not os.path.isdir(agent_root):
                continue
            for model_dir in os.listdir(agent_root):
                if not fnmatch.fnmatch(model_dir, model_glob):
                    continue
                model_root = os.path.join(agent_root, model_dir)
                if not os.path.isdir(model_root):
                    continue
                for prob in os.listdir(model_root):
                    prob_root = os.path.join(model_root, prob)
                    if not os.path.isdir(prob_root):
                        continue
                    if not re.fullmatch(r'\d{3}', prob):
                        continue
                    for f in os.listdir(prob_root):
                        if f.startswith('submission_ids_') and f.endswith('.log'):
                            log_path = os.path.join(prob_root, f)
                            try:
                                with open(log_path, 'r', encoding='utf-8') as fh:
                                    for line in fh:
                                        line = line.strip()
                                        if not line:
                                            continue
                                        try:
                                            rec = json.loads(line)
                                            sid = int(rec.get('submission_id', 0))
                                            if sid <= 0:
                                                continue
                                            if sid in seen_per_combo_prob[(combo, prob)]:
                                                continue
                                            seen_per_combo_prob[(combo, prob)].add(sid)
                                            out[combo][prob].append((sid, log_path))
                                        except Exception:
                                            continue
                            except Exception:
                                continue

    # sort
    for combo in out:
        for prob in out[combo]:
            out[combo][prob].sort(key=lambda x: x[0])
    return out

# ============================================================================
# Scoring (max=1)
# ============================================================================

def score_problem_max1(prob: str, sids: List[int], cache: Dict[str, Dict],
                        problem_to_api_ids: Dict[str, List[str]],
                        scoring_config: Dict[str, Dict],
                        max_subs_total: int = 999) -> Optional[float]:
    """
    Replicates analyze_exec_score.py weighted scoring with registry-style
    per-problem total submission cap (matching original `non_abort_records[:max_subs]`).

    - Walk submissions chronologically.
    - Skip aborted submissions (they don't consume the budget).
    - Take first `max_subs_total` non-aborted submissions across all sub-problems.
    - For each api_id, take MAX score among the captured submissions to it.
    - Apply weighted formula:
        final_score = Σ(min(raw/full, 1.0) * weight) / total_weight * 100
        (006 special piecewise handling for api_id 2877.)
    """
    config = scoring_config.get(prob, {})
    score_weight = config.get('score_weight', {})
    score_full = config.get('score_full', {})
    expected_api_ids = problem_to_api_ids.get(prob, [])

    if not sids:
        return None

    # Walk chronologically; skip aborted; collect first `max_subs_total` non-aborts.
    api_scores_list: Dict[str, List[float]] = {}
    consumed = 0
    for sid in sids:
        if consumed >= max_subs_total:
            break
        rec = cache.get(str(sid))
        if rec is None:
            continue
        result = (rec.get('result') or '').lower()
        if result in ('abort', 'aborted'):
            continue  # abort doesn't consume budget
        api_id = str(rec.get('problem_id', 'N/A'))
        try:
            sc = float(rec.get('score', 0) or 0)
        except Exception:
            sc = 0.0
        api_scores_list.setdefault(api_id, []).append(sc)
        consumed += 1

    api_max_score = {a: max(v) for a, v in api_scores_list.items() if v}

    if not api_max_score and not expected_api_ids:
        return None

    total_weight = sum(float(score_weight.get(a, 1)) for a in expected_api_ids)
    if total_weight == 0:
        total_weight = len(expected_api_ids) or 1

    weighted_sum = 0.0
    for api_id, raw in api_max_score.items():
        full = float(score_full.get(api_id, 100))
        weight = float(score_weight.get(api_id, 1))
        if prob == '006' and api_id == '2877':
            normalized = calculate_minesweeper_advanced_score(raw)
            weighted_sum += (normalized / 100.0) * weight
        else:
            if full > 0:
                ratio = min(raw / full, 1.0)
                weighted_sum += ratio * weight

    final = (weighted_sum / total_weight) * 100 if total_weight > 0 else 0.0
    return round(final, 2)

# ============================================================================
# Main
# ============================================================================

def main():
    t0 = time.time()
    print(f"[*] Loading registry from {REGISTRY_FILE}")
    registry = load_registry()
    problem_to_api_ids = get_problem_api_ids(registry)
    scoring_config = get_scoring_config(registry)
    all_problems = sorted(problem_to_api_ids.keys())
    # registry-based per-problem max_submissions
    default_max = registry.get('default', {}).get('max_submissions', 3)
    max_subs_map: Dict[str, int] = {}
    for pid, info in registry.get('problems', {}).items():
        max_subs_map[pid] = int(info.get('max_submissions', default_max))
    print(f"[*] {len(all_problems)} problems registered (default max_submissions={default_max})")

    print(f"[*] Loading cache from {CACHE_PATH}")
    cache = load_cache()
    print(f"[*] Cache pre-populated: {len(cache)} entries")
    pre_count = len(cache)

    print(f"[*] Discovering submission_ids_*.log under {LOGS_DIR}")
    combo_subs = discover_submissions()
    total_unique_sids: Set[int] = set()
    for combo, probs in combo_subs.items():
        for prob, items in probs.items():
            for sid, _ in items:
                total_unique_sids.add(sid)
    print(f"[*] Discovered {len(total_unique_sids)} unique submission IDs across "
          f"{sum(1 for c in combo_subs if combo_subs[c])} combos")

    # Identify which sids are NOT in cache
    missing = [sid for sid in total_unique_sids if str(sid) not in cache]
    print(f"[*] Cache misses: {len(missing)}; Hits: {len(total_unique_sids) - len(missing)}")

    # Fetch missing
    fetch_count = 0
    fail_count = 0
    if missing:
        print(f"[*] Fetching {len(missing)} missing submissions ({MAX_WORKERS} workers)...")
        last_save = time.time()
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
            futs = {ex.submit(fetch_submission, sid): sid for sid in missing}
            for i, fut in enumerate(as_completed(futs), 1):
                sid = futs[fut]
                rec = fut.result()
                if rec is not None:
                    cache[str(sid)] = rec
                    fetch_count += 1
                else:
                    fail_count += 1
                if i % 50 == 0:
                    print(f"  [+] {i}/{len(missing)} fetched (ok={fetch_count} fail={fail_count})", flush=True)
                # periodic save
                if time.time() - last_save > 20:
                    save_cache(cache)
                    last_save = time.time()
        save_cache(cache)
        print(f"[*] Fetch complete: ok={fetch_count} fail={fail_count}")

    save_cache(cache)
    print(f"[*] Cache size now: {len(cache)} (added {len(cache) - pre_count})")

    # Compute scores
    print(f"\n[*] Scoring...")
    output: Dict[str, Dict] = {}
    for combo in COMBO_DIRS:
        per_problem_score: Dict[str, Optional[float]] = {}
        classifications: Dict[str, str] = {}
        prob_data = combo_subs.get(combo, {})
        for prob in all_problems:
            sids = [sid for sid, _ in prob_data.get(prob, [])]
            if not sids:
                continue  # not attempted at all – do not include in this combo
            score = score_problem_max1(prob, sids, cache,
                                       problem_to_api_ids, scoring_config,
                                       max_subs_total=max_subs_map.get(prob, default_max))
            if score is None:
                # all sids missing from cache → treat as no-data; skip
                continue
            per_problem_score[prob] = score
            # classification: if any non-aborted submission existed → submitted, else tried_no_submit
            had_non_abort = False
            for sid in sids:
                rec = cache.get(str(sid))
                if rec is None:
                    continue
                if (rec.get('result') or '').lower() not in ('abort', 'aborted'):
                    had_non_abort = True
                    break
            classifications[prob] = 'submitted' if had_non_abort else 'tried_no_submit'

        valid_count = len(per_problem_score)
        submitted = sum(1 for v in classifications.values() if v == 'submitted')
        tried_no_submit = sum(1 for v in classifications.values() if v == 'tried_no_submit')

        # avg_exec_filtered: average over problems where classification == 'submitted'
        submitted_scores = [per_problem_score[p] for p in classifications
                            if classifications[p] == 'submitted']
        avg_filtered = round(sum(submitted_scores) / len(submitted_scores), 2) \
            if submitted_scores else 0.0

        # avg_exec_full128: average over all 128 problems in this combo's attempted
        # set (treating tried-no-submit as 0). To match the published "full128" sense
        # exactly we average over per_problem_score values (no padding to 128 since
        # the published values do the same — see: filtered file Codex+GPT-5 shows 122).
        all_scores = list(per_problem_score.values())
        avg_full128 = round(sum(all_scores) / len(all_scores), 2) if all_scores else 0.0

        output[combo] = {
            "avg_exec_full128": avg_full128,
            "avg_exec_filtered": avg_filtered,
            "valid_count": valid_count,
            "submitted": submitted,
            "tried_no_submit": tried_no_submit,
            "excluded_read_only": 0,
            "excluded_quota": 0,
            "excluded_no_run": 0,
            "per_problem": {p: per_problem_score[p] for p in sorted(per_problem_score)},
            "classifications": {p: classifications[p] for p in sorted(classifications)},
        }
        print(f"  {combo:28s}  avg_full={avg_full128:6.2f}  avg_filt={avg_filtered:6.2f}  "
              f"valid={valid_count:3d}  submitted={submitted:3d}  tried_no_submit={tried_no_submit:3d}")

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n[*] Saved → {OUT_PATH}")

    elapsed = time.time() - t0
    print(f"[*] Done. Wall time: {elapsed:.1f}s.  "
          f"API calls: {fetch_count} ok / {fail_count} fail.  "
          f"Cache hits: {len(total_unique_sids) - len(missing)}.")


if __name__ == "__main__":
    main()
