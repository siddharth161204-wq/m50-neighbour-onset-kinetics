#!/usr/bin/env python3
"""Figure 4 (Stage 5, version 1.2.0): the resolved and the lumped neighbour against the measured two-cell tests of
Fransson et al. (2024).

a  Time to propagation by connection. Black: the measured tests that propagated (Tables 3 and 4), with the share of
   the eight that did. Orange (resolved) and blue (lumped): the central case at the 30 s release (filled) and the
   10 s release (hollow), and over the factorial set (200 kinetic draws x 3 contacts x tab bracket x 2 releases) the
   2.5 to 97.5 % range (thin bar) and the quartiles (thick bar) of the runs that propagate, with the share that does.
   A marker in the band at the top did not propagate within 900 s. The grey band is the measured range, 147 to 342 s.
b  The central case, series, 30 s release: cell 1 (grey), the resolved hottest node (orange), the mid-surface
   temperature toward the trigger (violet; the line of contact) and away from it (magenta), the lumped neighbour
   (blue); the 150 C line of the paper, the 255.7 C propagation level, and a 0.4 C/s slope over the 60 s before the
   resolved propagation (or, without it, ending at 150 C at the measured mean time). Ticks on the time axis: the nine
   measured times.
Colours keep Figures 1 to 3's meanings: blue lumped, orange the resolved hottest node; violet and magenta, the probes,
are slots the earlier figures use only in Figure 3 for other quantities.
Usage: python3 make_figure_v12.py --out ../results
"""
import argparse, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ap = argparse.ArgumentParser()
ap.add_argument("--out", default="../results")
a = ap.parse_args()

INK, INK2, MUTED, GRID, AXIS, SURF, BAND = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#ffffff", "#f0efec"
BLUE, ORANGE, VIOLET, MAGENTA, GREY = "#2a78d6", "#eb6834", "#6250d6", "#e87ba4", "#898781"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.5, "axes.edgecolor": AXIS, "axes.labelcolor": INK2,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.linewidth": 0.8, "xtick.major.width": 0.8,
                     "ytick.major.width": 0.8, "figure.facecolor": SURF, "axes.facecolor": SURF,
                     "xtick.labelsize": 6.6, "ytick.labelsize": 6.6})
R = json.load(open(os.path.join(a.out, "v12_results.json")))
M = R["measured"]
NONE_Y = 985.0


def tidy(ax):
    ax.grid(True, which="major", color=GRID, lw=0.7); ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)


rows = []
import csv
with open(os.path.join(a.out, "v12_runs.csv")) as f:
    rows = list(csv.DictReader(f))


def fact_times(conn, which):
    rs = [r for r in rows if r["set"] == "fact" and r["connection"] == conn]
    key_p, key_t = (("res_propagated", "res_t_prop_s") if which == "res" else ("lum_propagated", "lum_t_prop_s"))
    t = [float(r[key_t]) for r in rs if r[key_p] == "True"]
    return np.array(t), len(rs)


fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.0), gridspec_kw={"wspace": 0.24, "width_ratios": [1.0, 1.15]})
ax = axs[0]
ax.axhspan(147, 342, color=BAND, zorder=0)
ax.axhspan(930, 1040, color="#f7f6f3", zorder=0)
ax.text(1.23, NONE_Y, "none within\n900 s", ha="center", va="center", fontsize=5.9, color=MUTED)
xt, xl = [], []
for i, conn in enumerate(("series", "parallel")):
    x0 = i * 1.45
    mt = M[conn]["times_s"]
    jit = np.linspace(-0.08, 0.08, len(mt))
    ax.scatter(x0 + jit, mt, s=14, color=INK, zorder=4, lw=0)
    ax.text(x0, 60, f"{M[conn]['n_propagated']} of {M[conn]['n_tests']}", ha="center", fontsize=6.3, color=INK2)
    for j, (which, col) in enumerate((("res", ORANGE), ("lum", BLUE))):
        x = x0 + 0.42 * (j + 1)
        t, n = fact_times(conn, which)
        if t.size:
            q = np.percentile(t, [2.5, 25, 50, 75, 97.5])
            ax.plot([x, x], [q[0], q[4]], color=col, lw=1.0, alpha=0.55, solid_capstyle="butt", zorder=2)
            ax.plot([x, x], [q[1], q[3]], color=col, lw=3.6, alpha=0.55, solid_capstyle="butt", zorder=2)
            ax.plot([x - 0.05, x + 0.05], [q[2], q[2]], color=col, lw=1.2, zorder=3)
        if n:
            ax.text(x, 60, f"{100 * t.size / n:.0f} %", ha="center", fontsize=6.3, color=INK2)
        for tau, fill in ((30, True), (10, False)):
            c = R["central_case"].get(f"{conn}_tau{tau}")
            if not c:
                continue
            prop = c["res_propagated"] if which == "res" else c["lum_propagated"]
            tt = (c["res_t_prop_s"] if which == "res" else c["lum_t_prop_s"]) if prop else NONE_Y
            dx = -0.09 if tau == 30 else 0.09
            ax.scatter([x + dx], [tt], s=26, marker="D" if which == "res" else "s", zorder=5,
                       facecolor=col if fill else SURF, edgecolor=col, lw=1.1)
    xt += [x0, x0 + 0.42, x0 + 0.84]
    xl += ["measured", "resolved", "lumped"]
    ax.text(x0 + 0.42, -95, conn.capitalize(), ha="center", va="top", fontsize=7.2, color=INK)
ax.set_xticks(xt); ax.set_xticklabels(xl, fontsize=5.9)
ax.set_xlim(-0.3, 2.65); ax.set_ylim(0, 1040)
ax.set_ylabel("Time to propagation (s)")
ax.set_yticks([0, 200, 400, 600, 800])
tidy(ax)
ax.set_title("a", loc="left", fontsize=8.5, fontweight="bold", color=INK)

# b: histories of the central case, series, 30 s
ax = axs[1]
sid = "grid_mean_series_hcentral_gcentral_tau30"
S = np.load(os.path.join(a.out, "v12_series", sid + ".npz"))
cc = R["central_case"]["series_tau30"]
t_end = float(S["probe_t"][-1])
tmax = max(400.0, min(900.0, t_end + 40.0))
ax.plot(S["t1_t"], S["t1_T1_C"], color=GREY, lw=1.0, label="cell 1")
ax.plot(S["probe_t"], S["probe_toward"] - 273.15, color=VIOLET, lw=2.4, zorder=2,
        label="mid-surface, toward (contact line)")
ax.plot(S["t"], S["Tmax"] - 273.15, color=ORANGE, lw=1.0, zorder=3, label="resolved, hottest node")
ax.plot(S["probe_t"], S["probe_away"] - 273.15, color=MAGENTA, lw=1.1, label="mid-surface, away")
ax.plot(S["t_lumped"], S["T_lumped"] - 273.15, color=BLUE, lw=1.3, label="lumped")
ax.axhline(150, color=INK2, lw=0.8, ls=(0, (4, 3)))
ax.axhline(255.7, color=INK2, lw=0.8, ls=(0, (1, 2)))
ax.text(tmax * 0.995, 152, "150 C", ha="right", va="bottom", fontsize=6.2, color=INK2)
ax.text(tmax * 0.995, 258, "255.7 C", ha="right", va="bottom", fontsize=6.2, color=INK2)
if cc["res_propagated"]:
    tp, Tp = cc["res_t_prop_s"], cc["res_T_mid_away_C"]
    ax.axvline(tp, color=ORANGE, lw=0.7, ls=(0, (2, 2)))
else:
    tp, Tp = M["all"]["mean_s"], 150.0
ax.plot([tp - 60, tp], [Tp - 24.0, Tp], color=INK, lw=1.4, solid_capstyle="round")
ax.text(tp - 62, Tp - 24.0, "0.4 C/s ", ha="right", va="center", fontsize=6.2, color=INK)
for tm in M["parallel"]["times_s"] + M["series"]["times_s"]:
    ax.plot([tm, tm], [0, 14], color=INK, lw=0.9)
ax.set_xlim(0, tmax); ax.set_ylim(0, 560)
ax.set_xlabel("Time from the start of cell 1's release (s)"); ax.set_ylabel("Temperature (C)")
tidy(ax)
ax.legend(loc="upper right", fontsize=6.0, frameon=False, handlelength=1.6)
ax.set_title("b", loc="left", fontsize=8.5, fontweight="bold", color=INK)
fig.subplots_adjust(left=0.07, right=0.99, top=0.93, bottom=0.17)
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(a.out, f"v12_figure.{ext}"), dpi=300)
print("wrote v12_figure.png and .pdf")
