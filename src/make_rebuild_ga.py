"""Graphical abstract of the rebuilt manuscript (Brief 29), drawn from the results files only.

Left: the two cells and where the delivered heat enters, with conduction's shortfall. Right: the estimate (Brief 30),
the heat the propagated tests with strong triggers need by their measured times under each reading of the neighbour,
each delivery shape (results/stage15_table.csv), against the ejecta's measured energy; below, its model dependence
(the threshold ratios, results/stage15_paper_numbers.json B1 against the lumped brackets) and the measurement. Every label it draws is also
written, one per line, to manuscript/rebuild/ga_text.txt, which the numbers check reads.

The guides ask for at least 1,328 pixels across, the longest side horizontal, readable at 13 cm: the figure is drawn
13.3 cm wide (7.4 cm high) with no text below 7 points and saved at 300 dpi (1,571 pixels) as TIFF and PDF.

Usage: python3 src/make_rebuild_ga.py
"""
import json
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge, FancyArrowPatch

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUT = os.path.join(ROOT, "manuscript", "rebuild")
INK, MUTED, GRID = "#222222", "#6b6b6b", "#e6e6e6"
C_LUMP, C_RES, C_TRIG, C_HEAT = "#0072B2", "#009E73", "#D55E00", "#E69F00"
CM = 1 / 2.54



def half_up(x, nd=2):
    """x to nd decimals, halves rounded up, as the manuscript writes a midpoint such as 3.975 kJ (3.98)."""
    from decimal import Decimal, ROUND_HALF_UP
    return str(Decimal(repr(float(x))).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))

def main():
    import csv
    rows = list(csv.DictReader(open(os.path.join(ROOT, "results", "stage15_table.csv"))))
    # the needs of the eight propagated tests with strong triggers, each delivery shape, counted to the run's runaway
    strong = [r for r in rows if r["test"] != "M50_ST_Exp3" and r["C8_xs_status"] in ("matched", "threshold")]
    res = [float(r["C8_xs_E_by_t_J"]) / 1000 for r in strong]
    lum = [float(r["C2_E_by_t_J"]) / 1000 for r in strong]
    e_fix = [float(r["value"]) for r in csv.DictReader(open(os.path.join(ROOT, "results", "stage14_inputs.csv")))
             if r["key"] == "db_Eej_median"][0] / 1000
    short = json.load(open(os.path.join(ROOT, "results", "stage12_paper_numbers.json")))["part_a"]["high"]["shortfall_hot_spot_K"][0]
    bound = [float(r["upper_J"]) for r in csv.DictReader(open(os.path.join(ROOT, "results", "stage14_bounds_corrected.csv")))
             if r["path"] == "A1" and r["window_s"] == "21.39"][0] / 1000
    sys.path.insert(0, os.path.join(ROOT, "manuscript", "rebuild"))
    import number_sources as NS
    r_lo = min(math.floor(100 * NS.ratio_span(t)[0]) / 100 for t in ("PT_Exp4", "PP_Exp2"))   # rounded outward
    r_hi = math.ceil(NS.ratio_span("PP_Exp2")[1] * 100) / 100
    w_lo = math.floor(NS.ratio_span("ST_Exp3")[0] * 100) / 100
    w_hi = math.ceil(NS.ratio_span("ST_Exp3")[1] * 100) / 100

    def rng(v, nd=1):
        return f"{min(v):.{nd}f} to {max(v):.{nd}f}"

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                         "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK, "axes.spines.top": False,
                         "axes.spines.right": False, "axes.spines.left": False, "pdf.fonttype": 42})
    fig = plt.figure(figsize=(13.3 * CM, 7.4 * CM))
    texts = []

    def T(ax, x, y, s, what="", **kw):
        texts.append(s.replace("\n", " ") + (f" | {what}" if what else ""))
        return ax.text(x, y, s, **kw)

    # ---------------------------------------------------------------- left: the cells and conduction's shortfall
    ax = fig.add_axes([0.01, 0.30, 0.37, 0.69])
    ax.set_xlim(0, 10); ax.set_ylim(0, 9.3); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Circle((2.7, 5.4), 2.2, fc="#fbe3d4", ec=C_TRIG, lw=1.4))
    ax.add_patch(Circle((7.1, 5.4), 2.2, fc="#f2f2f2", ec=INK, lw=1.2))
    ax.add_patch(Wedge((7.1, 5.4), 2.2, 90, 270, width=0.3, fc=C_HEAT, ec="none"))
    T(ax, 2.7, 5.4, "failing\ncell", ha="center", va="center", fontsize=8, color=C_TRIG, fontweight="bold")
    T(ax, 7.3, 5.4, "neighbour", ha="center", va="center", fontsize=7.5)
    for dy in (-1.2, 0.0, 1.2):
        ax.add_patch(FancyArrowPatch((4.1, 5.4 + dy * 1.25), (5.25, 5.4 + dy * 1.05), arrowstyle="-|>", mutation_scale=9,
                                     color=C_HEAT, lw=1.3))
    T(ax, 5.0, 8.6, "heat delivered to the facing half", ha="center", va="center", fontsize=7.5, color="#9a5b00")
    T(ax, 5.0, 1.45, f"with calorimetry's energy, conduction\nand radiation alone leave the\nneighbour at least {short:.0f} K short of runaway",
      ha="center", va="center", fontsize=7.0, color=MUTED, linespacing=1.25)

    # ---------------------------------------------------------------- right: what the tests need
    ax2 = fig.add_axes([0.45, 0.34, 0.52, 0.48])
    T(fig, 0.45, 0.975, "heat the tests need by their measured times,\nafter strong triggers (kJ)", ha="left", va="top",
      fontsize=7.8, color=INK, linespacing=1.2)
    for y, vals, col, face, name in ((1.25, res, C_RES, "white", "resolved neighbour"),
                                     (0.0, lum, C_LUMP, C_LUMP, "lumped neighbour")):
        ax2.plot([min(vals), max(vals)], [y, y], color=col, lw=5, alpha=0.25, solid_capstyle="round", zorder=2)
        jit = [((i % 4) - 1.5) * 0.06 for i in range(len(vals))]
        ax2.scatter(vals, [y + j for j in jit], s=12, facecolors=face, edgecolors=col, linewidths=0.9, zorder=3)
        pct = f"{100 * min(vals) / e_fix:.1f} to {100 * max(vals) / e_fix:.1f} %"
        T(ax2, 0.0, y + 0.22, f"{name}: {rng(vals)} kJ,\n{pct} of the {e_fix:.2f} kJ in this cell's ejecta",
          ha="left", va="bottom", fontsize=7.0, color=INK, linespacing=1.15)
    ax2.set_ylim(-0.3, 2.25); ax2.set_yticks([])
    ax2.set_xlim(0, 8.5); ax2.set_xticks([0, 2, 4, 6, 8]); ax2.tick_params(labelsize=7.5)
    ax2.grid(True, axis="x", color=GRID, lw=0.6, zorder=0)
    foot = (f"With a 21.4 s pulse the resolved neighbour's least energy for runaway is {r_lo:.2f} to {r_hi:.2f} times\n"
            f"the lumped one's after two strong triggers and {w_lo:.2f} to {w_hi:.2f} times after a weak one.\n"
            f"Published inputs bound no path to the facing half below {bound:.1f} kJ within 21.4 s;\n"
            f"a heat flux measured there would remove the dependence.")
    T(fig, 0.5, 0.015, foot, ha="center", va="bottom", fontsize=7.0, color=MUTED, linespacing=1.25)

    for ext, kw in (("pdf", {}), ("png", {"dpi": 300}), ("tif", {"dpi": 300, "pil_kwargs": {"compression": "tiff_lzw"}})):
        fig.savefig(os.path.join(OUT, "figures", f"graphical_abstract.{ext}"), **kw)
    plt.close(fig)
    open(os.path.join(OUT, "ga_text.txt"), "w").write("\n".join(texts) + "\n")
    print("graphical abstract written;", len(texts), "labels")


if __name__ == "__main__":
    main()
