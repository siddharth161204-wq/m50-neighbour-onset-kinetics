#!/usr/bin/env python3
"""Figure 7 (Stage 8): how much of the ejected energy the outcomes require.

a  For each of the sixteen tests, against its trigger energy, f*(C1) (circles: the fraction of the ejected energy at
   which the hot spot reaches 255.7 C) and f*(C2) (squares: the lumped neighbour), each as its bracket (a bar from the
   largest fraction tried that does not meet the criterion to the smallest that does, the marker at the latter; a
   test met at f = 0 sits at 0). Filled: propagated; hollow: not propagated. The shaded bands mark, for each
   criterion, where the range of f* over the propagated tests and the range over the non-propagated tests overlap.
   The vertical axis is on a square-root scale.
b  At f = 0.2: each criterion's predicted time against the measured time to propagation, for the propagated tests
   it predicts (on the left of the divider; a propagated test it misses is drawn hollow below the axis, at its
   measured time), and the predicted times of its false alarms (on the right, with their number). The line is
   equality, the band 60 s either side. Model times run from the start of cell 1's release, the paper's from the
   trigger's runaway (D34), with no shift.
Usage: python3 make_figure_stage8.py [--res ../results]
"""
import argparse, json, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

ap = argparse.ArgumentParser()
ap.add_argument("--res", default=os.path.join(HERE, "..", "results"))
ap.add_argument("--out", default=None)
a = ap.parse_args()
OUT = a.out or a.res

INK, INK2, MUTED, GRID, AXIS, SURF, BAND = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#ffffff", "#f0efec"
BLUE, ORANGE, GREEN = "#2a78d6", "#eb6834", "#1f9d6b"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.5, "axes.edgecolor": AXIS, "axes.labelcolor": INK2,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.linewidth": 0.8, "xtick.major.width": 0.8,
                     "ytick.major.width": 0.8, "figure.facecolor": SURF, "axes.facecolor": SURF,
                     "xtick.labelsize": 6.6, "ytick.labelsize": 6.6})
COL = {"C1": ORANGE, "C2": BLUE, "C3": GREEN}
MARK = {"C1": "o", "C2": "s", "C3": "^"}

v = json.load(open(os.path.join(a.res, "stage8_verdicts.json")))
card = json.load(open(os.path.join(a.res, "stage8_scorecard.json")))
rows = v["thresholds"]
fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.6), gridspec_kw={"wspace": 0.28, "width_ratios": [1.15, 1.0]})

# a
ax = axs[0]
fwd = lambda y: np.sqrt(np.clip(y, 0, None))
inv = lambda y: np.square(y)
ax.set_yscale("function", functions=(fwd, inv))
top = 1.05
X_OV = {"C1": 57.6, "C2": 59.0}
for crit, key, dx in (("C1", "fC1", -0.32), ("C2", "fC2", 0.32)):
    rng = {}
    for grp in (True, False):
        g = [r for r in rows if r["propagated"] == grp]
        los = [0.0 if r[key]["status"] == "zero" else r[key]["lo"] for r in g if r[key]["status"] in ("zero", "bracket")]
        his = [top if r[key]["status"] == "above" else (0.0 if r[key]["status"] == "zero" else r[key]["hi"]) for r in g]
        rng[grp] = (min(los) if los else 0.0, max(his) if his else 0.0)
    ov = (max(rng[True][0], rng[False][0]), min(rng[True][1], rng[False][1]))
    if ov[1] >= ov[0]:
        ax.plot([X_OV[crit]] * 2, [ov[0], ov[1]], color=COL[crit], lw=3.2, alpha=0.55, solid_capstyle="butt", zorder=1,
                clip_on=False)
    for r in rows:
        x = r["E_b_J"] / 1e3 + dx
        fs = r[key]
        if fs["status"] == "zero":
            y0, y1 = 0.0, 0.0
        elif fs["status"] == "above":
            y0, y1 = fs["lo"], top
        else:
            y0, y1 = fs["lo"], fs["hi"]
        ax.plot([x, x], [y0, y1], color=COL[crit], lw=0.8, alpha=0.7, zorder=2)
        ax.scatter([x], [y1], s=15, marker=MARK[crit], zorder=3, facecolor=COL[crit] if r["propagated"] else SURF,
                   edgecolor=COL[crit], lw=0.9, clip_on=False)
ax.text(58.3, 0.30, "overlap of\nthe two\ngroups", ha="center", va="bottom", fontsize=5.2, color=INK2, linespacing=1.0)
ticks = [0, 0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 1.0]
ax.set_yticks(ticks)
ax.set_yticklabels(["0", "0.01", "0.05", "0.1", "0.2", "0.3", "0.5", "1"])
ax.set_ylim(0, top)
ax.set_xlim(5, 56.5)
ax.set_xlabel("Trigger energy E_b (kJ)")
ax.set_ylabel("Delivered fraction f* of the ejected energy (square-root scale)")
ax.grid(True, axis="y", color=GRID, lw=0.7)
ax.set_axisbelow(True)
for sp_ in ("top", "right"):
    ax.spines[sp_].set_visible(False)
hs = [Line2D([], [], ls="", marker="o", mfc=ORANGE, mec=ORANGE, ms=3.8, label="f*(C1), propagated"),
      Line2D([], [], ls="", marker="o", mfc=SURF, mec=ORANGE, ms=3.8, label="f*(C1), not propagated"),
      Line2D([], [], ls="", marker="s", mfc=BLUE, mec=BLUE, ms=3.6, label="f*(C2), propagated"),
      Line2D([], [], ls="", marker="s", mfc=SURF, mec=BLUE, ms=3.6, label="f*(C2), not propagated")]
ax.legend(handles=hs, loc="upper center", fontsize=5.4, frameon=False, handletextpad=0.3, ncol=2, columnspacing=0.8)
ax.set_title("a", loc="left", fontsize=8.5, fontweight="bold", color=INK)

# b
ax = axs[1]
c02 = card["by_fraction"]["0.2"]
xmax = 380.0
ax.fill_between([0, xmax], [-60, xmax - 60], [60, xmax + 60], color=BAND, lw=0, zorder=0)
ax.plot([0, xmax], [0, xmax], color=INK2, lw=0.8, zorder=1)
fa_x = {"C1": xmax + 25, "C2": xmax + 50, "C3": xmax + 75}
ymax = 400.0
off = {"C1": -4.0, "C2": 0.0, "C3": 4.0}
for crit in ("C1", "C2", "C3"):
    k = 0
    for test, d in sorted(c02[crit]["per_test"].items()):
        if d.get("missing") or not d["predicted"]:
            continue
        if d["class"] == "hit":
            ax.scatter([d["measured_s"] + off[crit]], [d["t_s"]], s=15, marker=MARK[crit], color=COL[crit], zorder=3)
        else:
            ax.scatter([fa_x[crit] + 3.0 * (k % 3 - 1)], [d["t_s"]], s=15, marker=MARK[crit], facecolor=SURF,
                       edgecolor=COL[crit], lw=0.9, zorder=3)
            k += 1
    if k:
        ax.text(fa_x[crit], 36.0, f"{k}", ha="center", va="bottom", fontsize=5.6, color=COL[crit])
    miss = [t for t, d in c02[crit]["per_test"].items() if not d.get("missing") and d["class"] == "miss"]
    for j, t in enumerate(sorted(miss)):
        ax.scatter([c02[crit]["per_test"][t]["measured_s"] + off[crit]], [-12.0], s=15, marker=MARK[crit],
                   facecolor=SURF, edgecolor=COL[crit], lw=0.9, zorder=3, clip_on=False)
ax.axvline(xmax + 10, color=INK2, lw=0.7, ls=(0, (2, 2)))
ax.text(xmax + 50, ymax * 0.98, "false\nalarms", ha="center", va="top", fontsize=5.6, color=INK2)
ax.set_xlim(100, xmax + 90)
ax.set_ylim(-22, ymax)
ax.axhline(0, color=AXIS, lw=0.8)
ax.text(105, -12.0, "missed", ha="left", va="center", fontsize=5.4, color=INK2)
ax.set_xticks([150, 200, 250, 300, 350])
ax.set_xlabel("Measured time to propagation (s)")
ax.set_ylabel("Predicted time at f = 0.2 (s)")
ax.grid(True, color=GRID, lw=0.7)
ax.set_axisbelow(True)
for sp_ in ("top", "right"):
    ax.spines[sp_].set_visible(False)
hs = [Line2D([], [], ls="", marker=MARK[c], color=COL[c], ms=3.8,
             label={"C1": "C1 hot spot 255.7 C", "C2": "C2 lumped 255.7 C", "C3": "C3 lumped 150 C"}[c])
      for c in ("C1", "C2", "C3")]
ax.legend(handles=hs, loc="upper left", fontsize=5.4, frameon=False, handletextpad=0.3)
ax.set_title("b", loc="left", fontsize=8.5, fontweight="bold", color=INK)
fig.subplots_adjust(left=0.08, right=0.99, top=0.95, bottom=0.13)
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(OUT, f"stage8_figure.{ext}"), dpi=300)
print("wrote stage8_figure.png and .pdf")
