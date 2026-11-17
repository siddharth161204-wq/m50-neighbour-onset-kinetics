"""Stage 14 figure: each path's upper bound on a logarithmic energy axis, with the tests' needs marked.

Reads results/stage14_bounds.json, results/stage14_corrections.json (the bounds after the independent read,
D162) and results/stage14_needs.csv; writes results/stage14_figure.png and .pdf. The bars are the corrected
bounds; the registered A1 and A2 within 21.39 s are marked beside them.
Every lower bound is 0, which a logarithmic axis cannot show; the bars start at the axis's left edge.
Colours: the reference palette's first two categorical slots (blue for the bound within 21.39 s, orange
for the total), text in ink colours, the needs in dark grey.
"""
import csv
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df"
SURFACE = "#fcfcfb"


def main():
    bj = json.load(open(os.path.join(ROOT, "results", "stage14_bounds.json")))
    cj = json.load(open(os.path.join(ROOT, "results", "stage14_corrections.json")))
    corrected = {"A1": {k: x["corrected"] for k, x in cj["A1"]["by_window"].items()},
                 "A2": {k: x["corrected"] for k, x in cj["A2"]["by_window"].items()}}
    with open(os.path.join(ROOT, "results", "stage14_needs.csv"), newline="") as fh:
        needs = list(csv.DictReader(fh))

    labels = {
        "A1": "A1 radiation from a cap-end vent",
        "A2": "A2 vented gas beside the neighbour",
        "A3": "A3 a breach's jet facing it",
        "A4": "A4 solids and melt",
        "A5": "A5 the holder",
        "A6": "A6 the neighbour's own discharge\n(parallel tests; heat in the roll)",
    }
    order = ["A1", "A2", "A3", "A4", "A5", "A6"]
    xmin, xmax = 1e2, 1e6
    fig, ax = plt.subplots(figsize=(9.0, 5.6), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    ax.set_xscale("log")
    ax.set_xlim(xmin, xmax)
    ypos = {p: i for i, p in enumerate(order)}
    h = 0.32
    for p in order:
        y = ypos[p]
        if p == "A5":
            cap = bj["A5"]["cap_J"]
            ax.barh(y, cap - xmin, left=xmin, height=2 * h, color="none", edgecolor=MUTED, hatch="//", linewidth=0.8)
            ax.text(xmin * 1.15, y, "not determinable; energy conservation alone caps it at the hatched bar's end", va="center", ha="left",
                    fontsize=7.5, color=INK2, bbox=dict(facecolor=SURFACE, edgecolor="none", pad=1.5))
            continue
        b = corrected.get(p, bj[p]["bounds_J"])
        u21, ut = b["21.39"], b["total"]
        if p in corrected:
            reg = bj[p]["bounds_J"]["21.39"]
            ax.plot([reg], [y - h / 2 - 0.01], marker="D", markersize=5, linestyle="none", markerfacecolor=SURFACE,
                    markeredgecolor=INK, markeredgewidth=1.0)
            ax.text(reg * 0.92, y - h / 2 - 0.01, f"registered {reg / 1000:.1f} kJ", ha="right", va="center", fontsize=6.5, color=SURFACE)
        ax.barh(y - h / 2 - 0.01, u21 - xmin, left=xmin, height=h, color=BLUE, linewidth=0)
        ax.barh(y + h / 2 + 0.01, ut - xmin, left=xmin, height=h, color=ORANGE, linewidth=0)
        ax.text(u21 * 1.08, y - h / 2, f"{u21 / 1000:.1f} kJ", va="center", fontsize=7, color=INK2)
        ax.text(ut * 1.08, y + h / 2, f"{ut / 1000:.1f} kJ", va="center", fontsize=7, color=INK2)
        if p == "A1":
            # beside the bound, not part of it: a flame held on the vent's axis, and P1's line (2 % of 76.74 kJ)
            xa = 849.0   # D162 (5): the largest on the vent's axis, about 843 to 849 J
            ax.plot([xa, xa], [y - h - 0.08, y + h + 0.08], color=INK, linewidth=1.2)
            ax.text(xa * 0.93, y + h + 0.2, "flame held on the vent's axis: about 0.85 kJ", ha="right", va="center", fontsize=6.5, color=INK2)
            xp = 0.02 * bj["inputs"]["E_fix_J"]
            ax.plot([xp, xp], [y - h - 0.08, y + h + 0.08], color=INK, linewidth=0.9, linestyle=(0, (2, 2)))
            ax.text(xp * 1.07, y - h - 0.2, f"P1's line, {xp / 1000:.2f} kJ", ha="left", va="center", fontsize=6.5, color=INK2)
        if p == "A6":
            xc = bj["A6"]["conditional_25C_J"]["21.39"]
            ax.plot([xc, xc], [y - h - 0.08, y + 0.02], color=INK, linewidth=1.2)
            ax.text(xc * 0.93, y - h - 0.2, f"at 25 C, within 21.39 s: {xc / 1000:.1f} kJ", ha="right", va="center", fontsize=6.5, color=INK2)

    # The needs at 21.39 s, along the top: propagated tests filled, non-propagated open; thresholds as spans.
    ytop = len(order) - 0.1
    zero = []
    for t in needs:
        lo, hi = float(t["need_21s_lo_J"]), float(t["need_21s_hi_J"])
        if hi == 0.0:
            zero.append(t["test"].replace("M50_", ""))
            continue
        prop = t["propagated"] == "yes"
        if hi > lo:
            ax.plot([lo, hi], [ytop, ytop], color=INK2, linewidth=2.0, solid_capstyle="round")
        ax.plot([hi], [ytop], marker="o", markersize=6, linestyle="none",
                markerfacecolor=INK2 if prop else SURFACE, markeredgecolor=INK2, markeredgewidth=1.2)
        ax.axvline(hi, color=GRID, linewidth=0.8, zorder=0)
    ax.text(xmin * 1.15, ytop + 0.42, "needs at 21.39 s (filled: propagated; open: did not propagate; bar: a threshold's range)",
            fontsize=7.5, color=INK2, va="center")
    ax.text(xmin * 1.15, ytop - 0.36, "need nothing: " + ", ".join(zero), fontsize=7, color=MUTED, va="center")

    ax.set_yticks([ypos[p] for p in order] + [ytop])
    ax.set_yticklabels([labels[p] for p in order] + ["the sixteen tests"], fontsize=8, color=INK)
    ax.set_ylim(-0.7, len(order) + 0.6)
    ax.invert_yaxis()
    ax.set_xlabel("energy delivered to the facing half, J (upper bounds; every lower bound is 0)", fontsize=8.5, color=INK)
    ax.tick_params(axis="x", labelsize=8, colors=INK2)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(MUTED)
    ax.grid(axis="x", which="major", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=BLUE, label="within 21.39 s"), Patch(color=ORANGE, label="in total")],
              loc="lower right", fontsize=8, frameon=False)
    ax.set_title("Stage 14: what published inputs allow each path to deliver to the neighbour's facing half\n(the bounds after the independent read, D162)",
                 fontsize=9.5, color=INK, loc="left")
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(ROOT, "results", f"stage14_figure.{ext}"), facecolor=SURFACE)
    print("wrote results/stage14_figure.png and .pdf")


if __name__ == "__main__":
    main()
