#!/usr/bin/env python3
"""Regenerate Figure 4 (category_pie_chart.pdf) for the 128-problem benchmark."""
import json
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parents[2]
CATS_JSON = REPO_ROOT / "config" / "problem_categories.json"
OUT_PDF = REPO_ROOT / "results" / "category_pie_chart.pdf"
OUT_PDF.parent.mkdir(parents=True, exist_ok=True)

cats = json.loads(CATS_JSON.read_text())
counter = Counter(v["category"] for v in cats.values())

# Sort by count desc for stable display
ordered = counter.most_common()
labels = [f"{name} ({n})" for name, n in ordered]
sizes = [n for _, n in ordered]

# A muted but distinguishable palette
colors = [
    "#5B8FF9", "#5AD8A6", "#F6BD16", "#E86452",
    "#6DC8EC", "#945FB9", "#FF9845", "#1E9493",
]

fig, ax = plt.subplots(figsize=(7.0, 5.0))
wedges, texts, autotexts = ax.pie(
    sizes,
    labels=None,
    colors=colors[: len(ordered)],
    autopct=lambda p: f"{p:.1f}%",
    pctdistance=0.78,
    startangle=90,
    counterclock=False,
    wedgeprops={"linewidth": 1.2, "edgecolor": "white"},
    textprops={"fontsize": 11},
)
for at in autotexts:
    at.set_color("white")
    at.set_fontweight("bold")
ax.legend(
    wedges, labels, title="Category", loc="center left",
    bbox_to_anchor=(1.02, 0.5), frameon=False, fontsize=10,
    title_fontsize=11,
)
ax.set_aspect("equal")
plt.tight_layout()
fig.savefig(str(OUT_PDF), bbox_inches="tight")
print(f"wrote {OUT_PDF}")
print(f"total problems: {sum(sizes)}")
for n, c in zip(labels, sizes):
    print(f"  {n:35s}  {c:3d}")
