#!/usr/bin/env python3
"""Figure 5 (Stage 6): the paper's 150 C criterion on the Stage 5 runs, and the trigger matched to the tests.

a  Part A. The first crossing of 150 C by four model clocks in the 36 grid runs of Stage 5 (posterior-mean
   kinetics; 3 contacts x 3 tabs x 2 releases x 2 connections): the hot spot (the hottest node), the resolved mean,
   the face away from the trigger at mid-height (the thermocouple's position) and the lumped neighbour, each row
   split by contact (low, central, high from the bottom), beside the nine measured times to propagation (black).
   The grey band is the measured window, 147 to 342 s. At the right of each row: crossings inside the window, of the
   runs that cross, and the runs that never reach 150 C.
b  Part B. The neighbour's peak against cell 1's (the trigger's) peak: the sixteen tests of Tables 3 and 4 (black;
   filled, propagated), and the model at the face away (circles) and at the hot spot (diamonds), joined per run, for
   Stage 5's trigger (the reference, grey), the matched trigger (33.2 kJ over the measured durations), the
   Databank's total energy (107.0 kJ, upper bracket) and the exploratory peak-matched energy. A run whose hot spot
   reaches 255.7 C ends there, so its markers stop at that line. The grey band is the measured trigger range.
Colours: orange the hot spot, blue the lumped neighbour, magenta the face away, as in Figure 4; in b the sets.
Usage: python3 make_figure_stage6.py --res ../results
"""
import argparse, csv, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage6_inputs as IN

ap = argparse.ArgumentParser()
ap.add_argument("--res", default=os.path.join(HERE, "..", "results"))
a = ap.parse_args()

INK, INK2, MUTED, GRID, AXIS, SURF, BAND = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#ffffff", "#f0efec"
BLUE, ORANGE, VIOLET, MAGENTA, GREY, TEAL, RED = "#2a78d6", "#eb6834", "#6250d6", "#e87ba4", "#898781", "#1f9e89", "#b8312f"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.5, "axes.edgecolor": AXIS, "axes.labelcolor": INK2,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.linewidth": 0.8, "xtick.major.width": 0.8,
                     "ytick.major.width": 0.8, "figure.facecolor": SURF, "axes.facecolor": SURF,
                     "xtick.labelsize": 6.6, "ytick.labelsize": 6.6})
LO, HI = IN.WINDOW_S
M = IN.measured()


def tidy(ax):
    ax.grid(True, which="major", color=GRID, lw=0.7)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)


def rows_of(name):
    out = []
    for r in csv.DictReader(open(os.path.join(a.res, name))):
        for k, v in list(r.items()):
            if v in ("", "None"):
                r[k] = None
            elif v in ("True", "False"):
                r[k] = v == "True"
            else:
                try:
                    r[k] = float(v)
                except ValueError:
                    pass
        out.append(r)
    return out


A = [r for r in rows_of("stage6_crossings.csv") if r["set"] == "grid"]
B = rows_of("stage6_matched.csv") if os.path.exists(os.path.join(a.res, "stage6_matched.csv")) else []
fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.2), gridspec_kw={"wspace": 0.36, "width_ratios": [1.1, 1.0]})

# a: crossings of 150 C
ax = axs[0]
ax.axvspan(LO, HI, color=BAND, zorder=0)
clocks = [("lumped", "lumped", BLUE), ("away", "face away", MAGENTA),
          ("mean", "resolved mean", VIOLET), ("hot", "hot spot", ORANGE)]
dy = {"low": -0.22, "central": 0.0, "high": 0.22}
for k, (c, label, col) in enumerate(clocks):
    y0 = k
    n_cross = n_in = n_none = 0
    for r in A:
        t = r[f"{c}_t_cross_s"]
        if t is None:
            n_none += 1
            continue
        n_cross += 1
        n_in += LO <= t <= HI
        ax.scatter([t], [y0 + dy[r["h"]]], s=12, marker="o" if r["connection"] == "series" else "s",
                   facecolor=col if r["tau"] == 30.0 else SURF, edgecolor=col, lw=0.8, zorder=3)
    ax.text(405, y0 + 0.30, f"{n_in} of {n_cross} inside" + (f"; {n_none} never" if n_none else ""), ha="right",
            va="bottom", fontsize=5.8, color=INK2)
y_m = len(clocks)
mt = M["times_to_propagation_s"]
ax.scatter(mt, [y_m] * len(mt), s=14, color=INK, zorder=4, lw=0)
ax.text(405, y_m + 0.30, f"{len(mt)} of 16 tests propagated", ha="right", va="bottom", fontsize=5.8, color=INK2)
ax.set_yticks(list(range(len(clocks) + 1)))
ax.set_yticklabels([c[1] for c in clocks] + ["measured"], fontsize=6.4)
ax.set_xlim(0, 410)
ax.set_ylim(-0.65, y_m + 0.75)
ax.set_xlabel("First crossing of 150 C, from the start of cell 1's release (s)")
tidy(ax)
ax.legend(handles=[Line2D([], [], ls="", marker="o", mfc=INK2, mec=INK2, ms=3.6, label="series, 30 s"),
                   Line2D([], [], ls="", marker="s", mfc=SURF, mec=INK2, ms=3.6, label="parallel; hollow, 10 s")],
          loc="upper left", bbox_to_anchor=(0.0, 1.0), fontsize=5.6, frameon=False, handletextpad=0.3)
ax.text(2, -0.6, "within a row: contact low, central, high from the bottom", fontsize=5.4, color=MUTED, va="bottom")
ax.set_title("a", loc="left", fontsize=8.5, fontweight="bold", color=INK)

# b: neighbour peak against the trigger's
ax = axs[1]
ax.axvspan(*M["trigger_max_range_C"], color=BAND, zorder=0)
by = M["by_test"]
for t, r in by.items():
    prop = r["propagated"] == "Yes"
    ax.scatter([float(r["trigger_max_C"])], [float(r["neighbour_max_C"])], s=16, marker="o", zorder=4,
               facecolor=INK if prop else SURF, edgecolor=INK, lw=0.9)
ref = [r for r in rows_of("stage6_crossings.csv") if r["set"] == "grid"]
import json
recs5 = {r["id"]: r for r in ref}
t1_5 = {}
for rid in recs5:
    rec = json.load(open(os.path.join(a.res, "v12_runs", rid + ".json")))
    t1_5[rid] = rec["T1max_C"]
sets = [("reference (Stage 5)", GREY, [(t1_5[r["id"]], r["away_peak_C"], r["hot_peak_C"], False) for r in ref])]
for name, label, col in (("body", "matched, 33.2 kJ", ORANGE), ("total", "Databank total, 107.0 kJ", RED),
                         ("peak", "peak-matched (exploratory)", VIOLET)):
    rs = [r for r in B if r["set"] == name]
    if rs:
        sets.append((label, col, [(r["T1max_C"], r["away_peak_C"], r["hot_peak_C"], r["hot_t_255_7_s"] is not None)
                                  for r in rs]))
for label, col, pts in sets:
    for x, y_away, y_hot, reached in pts:
        ax.plot([x, x], [y_away, y_hot], color=col, lw=0.6, alpha=0.6, zorder=2)
        ax.scatter([x], [y_away], s=10, marker="o", facecolor=SURF, edgecolor=col, lw=0.8, zorder=3)
        ax.scatter([x], [y_hot], s=12, marker="D", facecolor=col, edgecolor=col, lw=0.6, zorder=3)
ax.axhline(150, color=INK2, lw=0.8, ls=(0, (4, 3)))
ax.axhline(255.7, color=INK2, lw=0.8, ls=(0, (1, 2)))
xmax = max([1000.0] + [p[0] + 60 for _, _, pts in sets for p in pts])
ax.text(xmax * 0.995, 152, "150 C", ha="right", va="bottom", fontsize=6.0, color=INK2)
ax.text(xmax * 0.995, 258, "255.7 C", ha="right", va="bottom", fontsize=6.0, color=INK2)
ax.set_xlim(100, xmax)
ax.set_ylim(0, 860)
ax.set_xlabel("Cell 1 (trigger) peak (C)")
ax.set_ylabel("Neighbour peak (C)")
tidy(ax)
hs = [Line2D([], [], ls="", marker="o", mfc=INK, mec=INK, ms=3.8, label="tests, propagated"),
      Line2D([], [], ls="", marker="o", mfc=SURF, mec=INK, ms=3.8, label="tests, not propagated")]
hs += [Line2D([], [], ls="-", lw=0.8, color=col, marker="D", ms=3.2, label=label) for label, col, _ in sets]
hs += [Line2D([], [], ls="", marker="o", mfc=SURF, mec=INK2, ms=3.4, label="model: face away"),
       Line2D([], [], ls="", marker="D", mfc=INK2, mec=INK2, ms=3.2, label="model: hot spot")]
ax.legend(handles=hs, loc="upper right", fontsize=5.3, frameon=False, handlelength=1.4, ncol=1)
ax.set_title("b", loc="left", fontsize=8.5, fontweight="bold", color=INK)
fig.subplots_adjust(left=0.105, right=0.99, top=0.93, bottom=0.15)
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(a.res, f"stage6_figure.{ext}"), dpi=300)
print("wrote stage6_figure.png and .pdf")
