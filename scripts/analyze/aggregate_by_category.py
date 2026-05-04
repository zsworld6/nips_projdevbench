#!/usr/bin/env python3
"""Aggregate Exec + CR scores per combo, split by Easy/Hard (Category 1 vs 2)."""
import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = REPO_ROOT / "results"
CATS = json.loads((REPO_ROOT / "config" / "problem_categories.json").read_text())
EXEC = json.loads(Path(os.environ.get(
    "EXEC_SCORES_JSON", str(RESULTS_DIR / "maxN_exec_finallogs.json"))).read_text())
CR_BASE = Path(os.environ.get(
    "CR_RESULT_DIR", str(REPO_ROOT / "data" / "cr_result")))

EASY = {pid for pid, v in CATS.items() if v["difficulty"] == "easy"}
HARD = {pid for pid, v in CATS.items() if v["difficulty"] == "hard"}
print(f"Easy: {len(EASY)} probs   Hard: {len(HARD)} probs")

# Combos that appear in Table 2 (paper-form name -> CR dir name)
ROWS = [
    ("Codex+GPT-5",            "Codex_GPT-5"),
    ("Codex+Gemini-3-Flash",   "Codex_Gemini-3-Flash"),
    ("Codex+Sonnet-4.5",       "Codex_Sonnet-4.5"),
    ("Codex+qwen3-235b",       "Codex_qwen3-235b"),
    ("Codex+GLM-4.6",          "Codex_GLM-4.6"),
    ("Codex+gpt-oss",          "Codex_gpt-oss"),
    ("CC+Sonnet-4.5",          "CC_Sonnet-4.5"),
    ("CC+Gemini-3-Flash",      "CC_Gemini-3-Flash"),
    ("CC+GPT-5",               "CC_GPT-5"),
    ("OpenHands+GPT-5",        "OpenHands_GPT-5"),
    ("OpenHands+Gemini-Flash", "OpenHands_Gemini-Flash"),
    ("OpenHands+Sonnet-4.5",   "OpenHands_Sonnet-4.5"),
    ("OpenHands+GLM-4.6",      "OpenHands_GLM-4.6"),
    ("OpenHands+qwen3-235b",   "OpenHands_qwen3-235b"),
    ("Gemini CLI+Flash",       "Gemini_CLI_Flash"),
]

# Load CR per-problem map per combo from cr_result_v2/<safe>/<prob>/all_result.json
def load_cr_per_combo(safe):
    out = {}
    d = CR_BASE / safe
    if not d.exists():
        return out
    for f in d.rglob("all_result.json"):
        prob = f.parent.name
        data = json.loads(f.read_text())
        sc = data["score_calculation"]
        if sc.get("error") in ("clone_failed", "no_repo_url"):
            continue
        out[prob] = sc["final_score_0_100"]
    return out

print()
print(f"{'Combo':28s}  {'EZ-Exec':>7s} {'EZ-CR':>7s}({'n':>3s})  {'HD-Exec':>7s} {'HD-CR':>7s}({'n':>3s})")
print("-" * 80)

results = {}
for paper_name, safe in ROWS:
    combo_exec = EXEC.get(paper_name, {})
    pp_exec = combo_exec.get("per_problem", {})
    cls = combo_exec.get("classifications", {})
    pp_cr   = load_cr_per_combo(safe)

    def avg_exec(probs):
        # Only include problems classified as "submitted" (filtered semantics).
        vals = [pp_exec[p] for p in probs
                if p in pp_exec and cls.get(p) == "submitted"]
        return (sum(vals) / len(vals), len(vals)) if vals else (0.0, 0)

    def avg_cr(probs):
        vals = [pp_cr[p] for p in probs if p in pp_cr]
        return (sum(vals) / len(vals), len(vals)) if vals else (0.0, 0)

    ez_exec, ez_exec_n = avg_exec(EASY)
    hd_exec, hd_exec_n = avg_exec(HARD)
    ez_cr,   ez_cr_n   = avg_cr(EASY)
    hd_cr,   hd_cr_n   = avg_cr(HARD)

    results[paper_name] = {
        "easy": {"exec": round(ez_exec, 2), "exec_n": ez_exec_n,
                  "cr":   round(ez_cr, 2),   "cr_n": ez_cr_n},
        "hard": {"exec": round(hd_exec, 2), "exec_n": hd_exec_n,
                  "cr":   round(hd_cr, 2),   "cr_n": hd_cr_n},
    }
    print(f"{paper_name:28s}  {ez_exec:7.2f}({ez_exec_n:3d}) {ez_cr:7.2f}({ez_cr_n:3d})  "
          f"{hd_exec:7.2f}({hd_exec_n:3d}) {hd_cr:7.2f}({hd_cr_n:3d})")

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
(RESULTS_DIR / "per_category_table2.json").write_text(
    json.dumps(results, indent=2, ensure_ascii=False))
print(f"\nSaved → {RESULTS_DIR / 'per_category_table2.json'}")
