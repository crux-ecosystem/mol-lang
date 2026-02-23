#!/usr/bin/env python3
"""
MOL Research — Chart Generator
================================
Reads benchmark JSON data and generates publication-quality charts
as PNG and SVG files in research/figures/.

Requirements: matplotlib, numpy (pip install matplotlib numpy)
"""

import json
import os
import sys

# ── Paths ─────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "data")
FIG_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "figures")

os.makedirs(FIG_DIR, exist_ok=True)

try:
    import matplotlib
    matplotlib.use("Agg")  # Non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
except ImportError:
    print("ERROR: matplotlib and numpy required.")
    print("  pip install matplotlib numpy")
    sys.exit(1)

# ── Style ─────────────────────────────────────────────────────────────────
MOL_BLUE = "#2962FF"
MOL_GREEN = "#00C853"
COLORS = {
    "mol": "#2962FF",
    "python": "#3776AB",
    "javascript": "#F7DF1E",
    "elixir": "#6E4A7E",
    "rust": "#DEA584",
    "fsharp": "#378BBA",
}
COLOR_LIST = [COLORS["mol"], COLORS["python"], COLORS["javascript"],
              COLORS["elixir"], COLORS["rust"], COLORS.get("fsharp", "#378BBA")]

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 150,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.2,
})


def load_json(name):
    path = os.path.join(DATA_DIR, name)
    with open(path) as f:
        return json.load(f)


def save_fig(fig, name):
    for ext in ("png", "svg"):
        path = os.path.join(FIG_DIR, f"{name}.{ext}")
        fig.savefig(path, format=ext)
    plt.close(fig)
    print(f"  ✓ {name}.png / .svg")


# ══════════════════════════════════════════════════════════════════════════
# Figure 1: Average LOC Comparison (Bar Chart)
# ══════════════════════════════════════════════════════════════════════════
def fig_01_loc():
    data = load_json("bench_01_loc.json")
    summary = data["summary"]
    langs = list(summary.keys())
    avg_loc = [summary[l]["avg_loc"] for l in langs]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(langs, avg_loc, color=[COLORS.get(l.lower(), "#888") for l in langs],
                  edgecolor="white", linewidth=1.5, width=0.6)

    # Highlight MOL bar
    bars[0].set_edgecolor(MOL_BLUE)
    bars[0].set_linewidth(2.5)

    # Value labels
    for bar, val in zip(bars, avg_loc):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f"{val:.1f}", ha="center", va="bottom", fontweight="bold", fontsize=12)

    ax.set_ylabel("Average Lines of Code", fontsize=13)
    ax.set_title("Lines of Code — 6 Equivalent AI/Data Tasks", fontsize=14, fontweight="bold")
    ax.set_ylim(0, max(avg_loc) * 1.2)
    ax.tick_params(axis="x", labelsize=12)

    # Annotation
    reduction_vs_rust = (1 - avg_loc[0] / avg_loc[-1]) * 100
    ax.annotate(f"MOL: {reduction_vs_rust:.0f}% fewer lines\nthan Rust",
                xy=(0, avg_loc[0]), xytext=(2.5, avg_loc[0] + 3),
                fontsize=10, color=MOL_BLUE, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=MOL_BLUE, lw=1.5))

    save_fig(fig, "fig_01_avg_loc")


# ══════════════════════════════════════════════════════════════════════════
# Figure 2: LOC per Task (Grouped Bar)
# ══════════════════════════════════════════════════════════════════════════
def fig_02_loc_per_task():
    data = load_json("bench_01_loc.json")
    tasks_data = data["tasks"]  # dict of task_name -> {lang -> metrics}

    task_names = list(tasks_data.keys())
    task_labels = [t.replace("_", " ").title()[:25] for t in task_names]
    # Get langs from first task
    first_task = tasks_data[task_names[0]]
    langs = list(first_task.keys())
    x = np.arange(len(task_names))
    width = 0.15

    fig, ax = plt.subplots(figsize=(14, 6))

    for i, lang in enumerate(langs):
        locs = [tasks_data[t][lang]["loc"] for t in task_names]
        offset = (i - len(langs)/2 + 0.5) * width
        bars = ax.bar(x + offset, locs, width, label=lang.upper(),
                      color=COLORS.get(lang.lower(), "#888"), edgecolor="white")

    ax.set_ylabel("Lines of Code", fontsize=13)
    ax.set_title("Lines of Code per Task by Language", fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(task_labels, rotation=25, ha="right", fontsize=9)
    ax.legend(loc="upper left", fontsize=10)
    ax.set_ylim(0, 30)

    save_fig(fig, "fig_02_loc_per_task")


# ══════════════════════════════════════════════════════════════════════════
# Figure 3: Stdlib Coverage Heatmap
# ══════════════════════════════════════════════════════════════════════════
def fig_03_stdlib_heatmap():
    data = load_json("bench_02_stdlib.json")
    matrix = data["categories"]

    categories = list(matrix.keys())
    langs = list(matrix[categories[0]].keys())

    values = np.array([[matrix[cat][lang]["count"] for lang in langs] for cat in categories])

    fig, ax = plt.subplots(figsize=(10, 10))
    im = ax.imshow(values, cmap="YlGnBu", aspect="auto")

    ax.set_xticks(range(len(langs)))
    ax.set_xticklabels([l.upper() for l in langs], fontsize=11)
    ax.set_yticks(range(len(categories)))
    ax.set_yticklabels(categories, fontsize=9)

    # Cell values
    for i in range(len(categories)):
        for j in range(len(langs)):
            val = values[i, j]
            color = "white" if val > 10 else "black"
            ax.text(j, i, str(val), ha="center", va="center",
                    fontsize=9, color=color, fontweight="bold")

    ax.set_title("Standard Library Coverage — Zero-Import Functions",
                 fontsize=14, fontweight="bold", pad=15)
    fig.colorbar(im, ax=ax, shrink=0.6, label="Function Count")

    save_fig(fig, "fig_03_stdlib_heatmap")


# ══════════════════════════════════════════════════════════════════════════
# Figure 4: Stdlib Totals (Horizontal Bar)
# ══════════════════════════════════════════════════════════════════════════
def fig_04_stdlib_totals():
    data = load_json("bench_02_stdlib.json")
    totals = data["totals"]
    langs = list(totals.keys())
    funcs = [totals[l]["total_funcs"] for l in langs]
    cats = [totals[l]["categories_covered"] for l in langs]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Total functions
    bars1 = ax1.barh(langs, funcs, color=[COLORS.get(l.lower(), "#888") for l in langs],
                     edgecolor="white")
    for bar, val in zip(bars1, funcs):
        ax1.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
                 str(val), va="center", fontweight="bold", fontsize=12)
    ax1.set_xlabel("Functions", fontsize=12)
    ax1.set_title("Total Built-in Functions", fontsize=13, fontweight="bold")
    ax1.set_xlim(0, max(funcs) * 1.2)
    ax1.invert_yaxis()

    # Categories covered
    bars2 = ax2.barh(langs, cats, color=[COLORS.get(l.lower(), "#888") for l in langs],
                     edgecolor="white")
    for bar, val in zip(bars2, cats):
        ax2.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                 f"{val}/16", va="center", fontweight="bold", fontsize=12)
    ax2.set_xlabel("Categories", fontsize=12)
    ax2.set_title("Categories Covered (of 16)", fontsize=13, fontweight="bold")
    ax2.set_xlim(0, 20)
    ax2.invert_yaxis()

    fig.suptitle("Standard Library Coverage Comparison", fontsize=15, fontweight="bold", y=1.02)
    fig.tight_layout()
    save_fig(fig, "fig_04_stdlib_totals")


# ══════════════════════════════════════════════════════════════════════════
# Figure 5: Security Radar Chart
# ══════════════════════════════════════════════════════════════════════════
def fig_05_security_radar():
    data = load_json("bench_04_security.json")
    features = list(data["features"].keys())
    langs = list(data["scores"].keys())

    # Build values: built-in=2, external=1, none=0
    values = {}
    for lang in langs:
        vals = []
        for feat in features:
            status = data["features"][feat][lang]
            if status == "built-in":
                vals.append(2)
            elif status == "external":
                vals.append(1)
            else:
                vals.append(0)
        values[lang] = vals

    # Radar chart
    N = len(features)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]  # Complete the circle

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

    for lang in langs[:3]:  # MOL, Python, Rust for clarity
        vals = values[lang] + values[lang][:1]
        color = COLORS.get(lang.lower(), "#888")
        ax.plot(angles, vals, 'o-', linewidth=2, label=lang.upper(), color=color)
        ax.fill(angles, vals, alpha=0.1, color=color)

    ax.set_xticks(angles[:-1])
    short_labels = [f.replace("_", "\n")[:18] for f in features]
    ax.set_xticklabels(short_labels, fontsize=8)
    ax.set_ylim(0, 2.5)
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(["None", "External", "Built-in"], fontsize=8)
    ax.set_title("Security Feature Coverage", fontsize=14, fontweight="bold", pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=11)

    save_fig(fig, "fig_05_security_radar")


# ══════════════════════════════════════════════════════════════════════════
# Figure 6: Security Scores (Bar)
# ══════════════════════════════════════════════════════════════════════════
def fig_06_security_scores():
    data = load_json("bench_04_security.json")
    scores = data["scores"]
    langs = list(scores.keys())
    supported = [scores[l]["supported"] for l in langs]
    builtin = [scores[l]["built_in"] for l in langs]

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(langs))
    w = 0.35

    bars1 = ax.bar(x - w/2, supported, w, label="Supported (any)",
                   color="#90CAF9", edgecolor="white")
    bars2 = ax.bar(x + w/2, builtin, w, label="Built-in (zero config)",
                   color=MOL_BLUE, edgecolor="white")

    for bar, val in zip(bars2, builtin):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                str(val), ha="center", fontweight="bold", fontsize=11)

    ax.set_ylabel("Features (out of 10)", fontsize=12)
    ax.set_title("Security Feature Scores", fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([l.upper() for l in langs], fontsize=11)
    ax.set_ylim(0, 12)
    ax.legend(fontsize=11)

    save_fig(fig, "fig_06_security_scores")


# ══════════════════════════════════════════════════════════════════════════
# Figure 7: Innovation Scores (Horizontal Bar)
# ══════════════════════════════════════════════════════════════════════════
def fig_07_innovation():
    data = load_json("bench_05_innovation.json")
    scores = data["scores"]  # {lang: int_score}
    # Sort by score ascending (for horizontal bar, bottom to top)
    sorted_langs = sorted(scores.keys(), key=lambda l: scores[l] if isinstance(scores[l], (int, float)) else scores[l].get("weighted_score", 0))
    vals = [scores[l] if isinstance(scores[l], (int, float)) else scores[l]["weighted_score"] for l in sorted_langs]
    pcts = [int(v) for v in vals]  # scores are already percentages

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = [COLORS.get(l.lower(), "#888") for l in sorted_langs]
    bars = ax.barh(sorted_langs, vals, color=colors, edgecolor="white", height=0.6)

    for bar, val, pct in zip(bars, vals, pcts):
        ax.text(bar.get_width() + 1.5, bar.get_y() + bar.get_height()/2,
                f"{val}/100 ({pct}%)", va="center", fontweight="bold", fontsize=11)


    ax.set_xlabel("Weighted Innovation Score", fontsize=13)
    ax.set_title("Innovation & Language Design Score", fontsize=15, fontweight="bold")
    ax.set_xlim(0, 120)
    ax.tick_params(axis="y", labelsize=12)

    save_fig(fig, "fig_07_innovation_scores")


# ══════════════════════════════════════════════════════════════════════════
# Figure 8: Performance Overhead (Log Scale)
# ══════════════════════════════════════════════════════════════════════════
def fig_08_performance():
    data = load_json("bench_03_performance.json")
    results = data["results"]  # dict of test_name -> {description, mol, python, overhead}
    names = [k.replace("_", " ").title() for k in results.keys()]
    overheads = []
    for k, v in results.items():
        mol_ms = v["mol"]["mean_ms"]
        py_ms = v["python"]["mean_ms"]
        overheads.append(round(mol_ms / py_ms, 1) if py_ms > 0 else 1)

    fig, ax = plt.subplots(figsize=(10, 6))
    colors_perf = [MOL_BLUE if o < 50 else "#FF6B6B" if o > 200 else "#FFB74D" for o in overheads]
    bars = ax.barh(names, overheads, color=colors_perf, edgecolor="white", height=0.6)

    for bar, val in zip(bars, overheads):
        ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
                f"{val:.1f}x", va="center", fontsize=10, fontweight="bold")

    ax.set_xlabel("Overhead Factor (MOL / Python)", fontsize=12)
    ax.set_title("Execution Overhead — MOL vs Native Python\n(Interpreted DSL trade-off)",
                 fontsize=13, fontweight="bold")
    ax.set_xscale("log")
    ax.axvline(x=data["summary"]["avg_overhead"], color="gray",
               linestyle="--", alpha=0.7, label=f'Average: {data["summary"]["avg_overhead"]:.1f}x')
    ax.legend(fontsize=10)

    save_fig(fig, "fig_08_performance_overhead")


# ══════════════════════════════════════════════════════════════════════════
# Figure 9: Import Comparison (Bar)
# ══════════════════════════════════════════════════════════════════════════
def fig_09_imports():
    data = load_json("bench_01_loc.json")
    summary = data["summary"]
    langs = list(summary.keys())
    imports = [summary[l]["avg_imports"] for l in langs]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(langs, imports, color=[COLORS.get(l.lower(), "#888") for l in langs],
                  edgecolor="white", width=0.6)

    for bar, val in zip(bars, imports):
        label = "ZERO" if val == 0 else f"{val:.1f}"
        color = MOL_GREEN if val == 0 else "black"
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                label, ha="center", va="bottom", fontweight="bold", fontsize=13, color=color)

    ax.set_ylabel("Average Import Statements", fontsize=13)
    ax.set_title("Import Requirements — Zero-Import Advantage",
                 fontsize=14, fontweight="bold")
    ax.set_ylim(0, max(imports) * 1.4 + 0.5)

    save_fig(fig, "fig_09_imports")


# ══════════════════════════════════════════════════════════════════════════
# Figure 10: Comprehensive Summary Dashboard
# ══════════════════════════════════════════════════════════════════════════
def fig_10_dashboard():
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle("MOL Language — Research Benchmark Summary Dashboard",
                 fontsize=18, fontweight="bold", y=0.98)

    # Panel 1: LOC
    data1 = load_json("bench_01_loc.json")
    s = data1["summary"]
    langs1 = list(s.keys())
    ax = axes[0, 0]
    ax.bar(langs1, [s[l]["avg_loc"] for l in langs1],
           color=[COLORS.get(l.lower(), "#888") for l in langs1], edgecolor="white")
    ax.set_title("Avg Lines of Code (lower = better)", fontweight="bold")
    ax.set_ylabel("LOC")

    # Panel 2: Stdlib
    data2 = load_json("bench_02_stdlib.json")
    t = data2["totals"]
    langs2 = list(t.keys())
    ax = axes[0, 1]
    ax.bar(langs2, [t[l]["total_funcs"] for l in langs2],
           color=[COLORS.get(l.lower(), "#888") for l in langs2], edgecolor="white")
    ax.set_title("Built-in Functions (higher = better)", fontweight="bold")
    ax.set_ylabel("Functions")

    # Panel 3: Security
    data4 = load_json("bench_04_security.json")
    sc = data4["scores"]
    langs4 = list(sc.keys())
    ax = axes[1, 0]
    ax.bar(langs4, [sc[l]["built_in"] for l in langs4],
           color=[COLORS.get(l.lower(), "#888") for l in langs4], edgecolor="white")
    ax.set_title("Built-in Security Features /10 (higher = better)", fontweight="bold")
    ax.set_ylabel("Features")

    # Panel 4: Innovation
    data5 = load_json("bench_05_innovation.json")
    iv = data5["scores"]
    langs5 = sorted(iv.keys(), key=lambda l: iv[l] if isinstance(iv[l], (int, float)) else 0, reverse=True)
    ax = axes[1, 1]
    ax.bar(langs5, [iv[l] if isinstance(iv[l], (int, float)) else 0 for l in langs5],
           color=[COLORS.get(l.lower(), "#888") for l in langs5], edgecolor="white")
    ax.set_title("Innovation Score /100 (higher = better)", fontweight="bold")
    ax.set_ylabel("Score")

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    save_fig(fig, "fig_10_dashboard")


# ══════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════
def main():
    print("=" * 70)
    print("  MOL Research — Generating Publication Charts")
    print("=" * 70)

    generators = [
        ("Fig 1: Average LOC", fig_01_loc),
        ("Fig 2: LOC per Task", fig_02_loc_per_task),
        ("Fig 3: Stdlib Heatmap", fig_03_stdlib_heatmap),
        ("Fig 4: Stdlib Totals", fig_04_stdlib_totals),
        ("Fig 5: Security Radar", fig_05_security_radar),
        ("Fig 6: Security Scores", fig_06_security_scores),
        ("Fig 7: Innovation Scores", fig_07_innovation),
        ("Fig 8: Performance Overhead", fig_08_performance),
        ("Fig 9: Import Comparison", fig_09_imports),
        ("Fig 10: Summary Dashboard", fig_10_dashboard),
    ]

    for name, func in generators:
        print(f"\n  Generating {name}...")
        try:
            func()
        except Exception as e:
            print(f"  ✗ Error: {e}")

    print("\n" + "=" * 70)
    print(f"  Done! {len(generators)} figures saved to: {FIG_DIR}")
    print("  Formats: PNG (150 DPI) + SVG (vector)")
    print("=" * 70)


if __name__ == "__main__":
    main()
