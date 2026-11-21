"""Graphical abstract of the rebuilt manuscript (Brief 29), drawn from the results files only.

Left: the two cells and where the delivered heat enters. Right: the heat over 21.4 s that makes each neighbour run
away in the two tests where both thresholds are bracketed with a strong trigger (results/stage15_paper_numbers.json,
B1), with the measured record's place and the bound on every path in words below. Every label it draws is also
written, one per line, to manuscript/rebuild/ga_text.txt, which the numbers check reads.

The guides ask for at least 1,328 pixels across, the longest side horizontal, readable at 13 cm: the figure is drawn
13.3 cm wide with no text below 7 points and saved at 300 dpi (1,571 pixels) as TIFF and PDF.

Usage: python3 src/make_rebuild_ga.py
"""
import json
import os

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


def main():
    p = json.load(open(os.path.join(ROOT, "results", "stage15_paper_numbers.json")))
    b1 = p["B1"]
    rows = []
    for t in ("M50_PT_Exp4", "M50_PP_Exp2"):
        b = b1[t]
        rows.append(dict(test=t.replace("M50_", "").replace("_", "-"), lumped=b["E_C2_J"] / 1000,
                         lo=b["bracket"]["lo_J"] / 1000, hi=b["bracket"]["hi_J"] / 1000,
                         mid=b["bracket"]["mid_J"] / 1000, ratio=b["ratio_to_C2"]))
    sc = json.load(open(os.path.join(ROOT, "results", "stage15_scorecard.json")))
    above = sc["scorecard"]["predictions"]["P5"]["above_197.3_K"]
    short = json.load(open(os.path.join(ROOT, "results", "stage12_paper_numbers.json")))["part_a"]["high"]["shortfall_hot_spot_K"][0]
    import csv
    bound = [float(r["upper_J"]) for r in csv.DictReader(open(os.path.join(ROOT, "results", "stage14_bounds_corrected.csv")))
             if r["path"] == "A1" and r["window_s"] == "21.39"][0] / 1000

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                         "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK, "axes.spines.top": False,
                         "axes.spines.right": False, "pdf.fonttype": 42})
    fig = plt.figure(figsize=(13.3 * CM, 6.6 * CM))
    texts = []

    def T(ax, x, y, s, what="", **kw):
        texts.append(s.replace("\n", " ") + (f" | {what}" if what else ""))
        return ax.text(x, y, s, **kw)

    # ---------------------------------------------------------------- left: the cells
    ax = fig.add_axes([0.0, 0.15, 0.45, 0.82])
    ax.set_xlim(0, 10); ax.set_ylim(0, 8); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Circle((2.6, 4.4), 2.0, fc="#fbe3d4", ec=C_TRIG, lw=1.4))
    ax.add_patch(Circle((6.6, 4.4), 2.0, fc="#f2f2f2", ec=INK, lw=1.2))
    ax.add_patch(Wedge((6.6, 4.4), 2.0, 90, 270, width=0.28, fc=C_HEAT, ec="none"))
    T(ax, 2.6, 4.4, "failing\ncell", ha="center", va="center", fontsize=8, color=C_TRIG, fontweight="bold")
    T(ax, 6.6, 4.4, "neighbour", ha="center", va="center", fontsize=8)
    for dy in (-1.1, 0.0, 1.1):
        ax.add_patch(FancyArrowPatch((3.9, 4.4 + dy * 1.25), (4.95, 4.4 + dy * 1.05), arrowstyle="-|>", mutation_scale=9,
                                     color=C_HEAT, lw=1.3))
    T(ax, 6.6, 7.0, "heat delivered to the facing half", ha="center", va="center", fontsize=7.5, color="#9a5b00")
    T(ax, 4.6, 0.9, f"with calorimetry's energy, conduction\nand radiation alone leave the neighbour\nat least {short:.0f} K short of runaway", ha="center", va="center",
      fontsize=7.5, color=MUTED, linespacing=1.3)

    # ---------------------------------------------------------------- right: what each neighbour needs
    ax2 = fig.add_axes([0.56, 0.24, 0.42, 0.60])
    x = [0, 1]
    w = 0.34
    for i, r in enumerate(rows):
        ax2.bar(i - w / 2 - 0.02, r["lumped"], w, color=C_LUMP, zorder=3)
        ax2.bar(i + w / 2 + 0.02, r["mid"], w, color=C_RES, zorder=3)
        ax2.plot([i + w / 2 + 0.02] * 2, [r["lo"], r["hi"]], color=INK, lw=1.0, zorder=4)
        T(ax2, i - w / 2 - 0.02, r["lumped"] + 0.25, f"{r['lumped']:.2f}", f"{r['test']}, the lumped neighbour's threshold, kJ",
          ha="center", va="bottom", fontsize=7.5, color=C_LUMP)
        T(ax2, i + w / 2 + 0.02, r["hi"] + 0.25, f"{r['mid']:.2f}", f"{r['test']}, the resolved neighbour's threshold, kJ",
          ha="center", va="bottom", fontsize=7.5, color=C_RES)
        T(ax2, i, 9.3, f"{r['ratio']:.1f} times", f"{r['test']}, the resolved threshold over the lumped one",
          ha="center", va="top", fontsize=7.5, color=INK)
    ax2.set_xticks(x); ax2.set_xticklabels([r["test"] for r in rows], fontsize=8)
    texts += [r["test"] for r in rows]
    ax2.set_ylim(0, 9.6); ax2.set_yticks([0, 2, 4, 6, 8]); ax2.tick_params(labelsize=7.5)
    ax2.grid(True, axis="y", color=GRID, lw=0.6, zorder=0)
    lab = "heat in 21.4 s for runaway (kJ)"
    ax2.set_ylabel(lab, fontsize=7.5); texts.append(lab)
    from matplotlib.patches import Patch
    leg = ["lumped neighbour", "resolved neighbour"]
    ax2.legend(handles=[Patch(color=C_LUMP, label=leg[0]), Patch(color=C_RES, label=leg[1])], fontsize=7.2,
               frameon=False, loc="upper left", bbox_to_anchor=(-0.24, 1.19), ncol=2, handlelength=1.0, columnspacing=1.0)
    texts += leg
    foot = (f"In the one published record of a propagating neighbour, the final rise starts\n{above:.0f} K cooler than "
            f"on the resolved neighbour's far side. No path through the facing half\nis bounded below {bound:.1f} kJ "
            f"within 21.4 s by published inputs.")
    T(fig, 0.5, 0.02, foot, ha="center", va="bottom", fontsize=7.2, color=MUTED, linespacing=1.3)

    for ext, kw in (("pdf", {}), ("png", {"dpi": 300}), ("tif", {"dpi": 300, "pil_kwargs": {"compression": "tiff_lzw"}})):
        fig.savefig(os.path.join(OUT, "figures", f"graphical_abstract.{ext}"), **kw)
    plt.close(fig)
    open(os.path.join(OUT, "ga_text.txt"), "w").write("\n".join(texts) + "\n")
    print("graphical abstract written;", len(texts), "labels")


if __name__ == "__main__":
    main()
