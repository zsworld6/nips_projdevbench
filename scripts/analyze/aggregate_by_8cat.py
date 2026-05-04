#!/usr/bin/env python3
"""Aggregate Exec + CR per combo, broken down by the 8 task categories."""
import json
import os
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = REPO_ROOT / "results"
CATS = json.loads((REPO_ROOT / "config" / "problem_categories.json").read_text())
EXEC = json.loads(Path(os.environ.get(
    "EXEC_SCORES_JSON", str(RESULTS_DIR / "maxN_exec_finallogs.json"))).read_text())
CR_BASE = Path(os.environ.get(
    "CR_RESULT_DIR", str(REPO_ROOT / "data" / "cr_result")))

# Group problem IDs by category
CAT_TO_PROBS = defaultdict(set)
for pid, v in CATS.items():
    CAT_TO_PROBS[v["category"]].add(pid)

# Display order: largest to smallest
CAT_ORDER = [
    "Data Structures", "Algorithm", "Game/Simulation", "Optimization",
    "Interpreters", "Management Systems", "Storage Systems", "Assembly",
]
print(f"{'Category':22s} {'#probs':>7s}")
for c in CAT_ORDER:
    print(f"  {c:20s} {len(CAT_TO_PROBS[c]):3d}")

ROWS = [
    ("Codex CLI", "GPT-5",          "Codex+GPT-5",            "Codex_GPT-5"),
    ("Codex CLI", "Gemini-3-Flash", "Codex+Gemini-3-Flash",   "Codex_Gemini-3-Flash"),
    ("Codex CLI", "Sonnet-4.5",     "Codex+Sonnet-4.5",       "Codex_Sonnet-4.5"),
    ("Codex CLI", "qwen3-235b",     "Codex+qwen3-235b",       "Codex_qwen3-235b"),
    ("Codex CLI", "GLM-4.6",        "Codex+GLM-4.6",          "Codex_GLM-4.6"),
    ("Codex CLI", "gpt-oss-120b",   "Codex+gpt-oss",          "Codex_gpt-oss"),
    ("Claude Code", "Sonnet-4.5",   "CC+Sonnet-4.5",          "CC_Sonnet-4.5"),
    ("Claude Code", "Gemini-3-Flash","CC+Gemini-3-Flash",     "CC_Gemini-3-Flash"),
    ("Claude Code", "GPT-5",        "CC+GPT-5",               "CC_GPT-5"),
    ("OpenHands",   "GPT-5",        "OpenHands+GPT-5",        "OpenHands_GPT-5"),
    ("OpenHands",   "Gemini-3-Flash","OpenHands+Gemini-Flash","OpenHands_Gemini-Flash"),
    ("OpenHands",   "Sonnet-4.5",   "OpenHands+Sonnet-4.5",   "OpenHands_Sonnet-4.5"),
    ("OpenHands",   "GLM-4.6",      "OpenHands+GLM-4.6",      "OpenHands_GLM-4.6"),
    ("OpenHands",   "qwen3-235b",   "OpenHands+qwen3-235b",   "OpenHands_qwen3-235b"),
    ("Gemini CLI",  "Gemini-3-Flash","Gemini CLI+Flash",      "Gemini_CLI_Flash"),
]

def load_cr_per_combo(safe):
    out = {}
    d = CR_BASE / safe
    if not d.exists(): return out
    for f in d.rglob("all_result.json"):
        prob = f.parent.name
        data = json.loads(f.read_text())
        sc = data["score_calculation"]
        if sc.get("error") in ("clone_failed", "no_repo_url"):
            continue
        out[prob] = sc["final_score_0_100"]
    return out

results = {}
for agent, model, paper_name, safe in ROWS:
    combo_exec = EXEC.get(paper_name, {})
    pp_exec = combo_exec.get("per_problem", {})
    cls = combo_exec.get("classifications", {})
    pp_cr = load_cr_per_combo(safe)
    per_cat = {}
    for cat in CAT_ORDER:
        probs = CAT_TO_PROBS[cat]
        e_vals = [pp_exec[p] for p in probs if p in pp_exec and cls.get(p) == "submitted"]
        c_vals = [pp_cr[p] for p in probs if p in pp_cr]
        per_cat[cat] = {
            "exec": round(sum(e_vals)/len(e_vals), 2) if e_vals else None,
            "exec_n": len(e_vals),
            "cr":   round(sum(c_vals)/len(c_vals), 2) if c_vals else None,
            "cr_n": len(c_vals),
        }
    results[paper_name] = {"agent": agent, "model": model, "per_cat": per_cat}

print()
print("Exec by category:")
header = f"{'combo':28s} " + " ".join(f"{c[:10]:>11s}" for c in CAT_ORDER)
print(header)
for paper_name, _, _, _ in [(r[2], r[0], r[1], r[3]) for r in ROWS]:
    pass  # placeholder
for agent, model, paper_name, safe in ROWS:
    cells = []
    for cat in CAT_ORDER:
        v = results[paper_name]["per_cat"][cat]
        cells.append(f"{v['exec']:5.1f}({v['exec_n']:2d})" if v['exec'] is not None else f"{'—':>9s}")
    print(f"{paper_name:28s} " + " ".join(f"{c:>11s}" for c in cells))

print()
print("CR by category:")
print(header)
for agent, model, paper_name, safe in ROWS:
    cells = []
    for cat in CAT_ORDER:
        v = results[paper_name]["per_cat"][cat]
        cells.append(f"{v['cr']:5.1f}({v['cr_n']:2d})" if v['cr'] is not None else f"{'—':>9s}")
    print(f"{paper_name:28s} " + " ".join(f"{c:>11s}" for c in cells))

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
out_path = RESULTS_DIR / "per_8cat_table2.json"
out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
print(f"\nSaved → {out_path}")
