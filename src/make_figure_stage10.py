#!/usr/bin/env python3
"""Figure 9 (Stage 10): what the one published history decides, and what the sixteen tests can tell a model.

a  M50_PT_Exp4's measured thermocouple history (Fransson et al. 2024, supplementary Figure 10(a), as read in D102,
   with the band of its 2.47 K uncertainty) and the model's history at the Stage 9 node (the face away from the
   trigger, at mid-length) and the central contact: with no delivery, under the short delivery (21.39 s) at both
   ends of its C2 threshold bracket, and under the long deliveries at their f_t (C2 over 240 and 360 s, C1 over
   360 s). The vertical line is the onset the figure marks, 271.50 s; the shaded strip is the last 60 s before it.
b  Held out (C1 of Part C): for each predictor and each direction of the split, the mean log score of the logistic
   on the eight held-out tests less that of one probability for every test (points), with the 2.5 to 97.5 % band of
   the same difference over 10,000 relabellings of the outcomes (bars). Zero is the constant; the dashed line at
   0.1 is P6's margin.
Usage: python3 make_figure_stage10.py [--res ../results] [--out DIR]
"""
import argparse, json, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage10_inputs as IN              # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--res", default=os.path.join(HERE, "..", "results"))
ap.add_argument("--out", default=None)
a = ap.parse_args()
OUT = a.out or a.res

INK, INK2, MUTED, GRID, AXIS, SURF, BAND = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#ffffff", "#e9e8e3"
BLUE, ORANGE, GREEN = "#2a78d6", "#eb6834", "#1f9d6b"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.5, "axes.edgecolor": AXIS, "axes.labelcolor": INK2,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.linewidth": 0.8, "xtick.major.width": 0.8,
                     "ytick.major.width": 0.8, "figure.facecolor": SURF, "axes.facecolor": SURF,
                     "xtick.labelsize": 6.6, "ytick.labelsize": 6.6})

hs = json.load(open(os.path.join(a.res, "stage10_history_scores.json")))["part_a"]
held = json.load(open(os.path.join(a.res, "stage10_heldout.json")))

fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.5), gridspec_kw={"wspace": 0.24, "width_ratios": [1.35, 1.0]})

# a
ax = axs[0]
tm, Tm, _ = IN.history("a")
tm, Tm = np.array(tm), np.array(Tm)
keep = tm <= 290.0
ax.axvspan(IN.T_PROP_S - IN.LAST_S, IN.T_PROP_S, color="#f4f3ef", lw=0, zorder=0)
ax.fill_between(tm[keep], Tm[keep] - IN.UNC_K, Tm[keep] + IN.UNC_K, color=BAND, lw=0, zorder=1)
ax.plot(tm[keep], Tm[keep], color=INK, lw=1.3, zorder=5)
lines = [("none_hcentral", MUTED, (0, (3, 2)), 1.0, "no delivery"),
         ("tri21_C2_lo_hcentral", BLUE, "-", 1.2, "21.39 s, f = 0.0375 (C2 bracket, lower end)"),
         ("tri21_C2_hi_hcentral", BLUE, (0, (4, 1.5)), 1.2, "21.39 s, f = 0.040625 (upper end)"),
         ("con240_C2_hcentral", ORANGE, (0, (5, 1.5, 1, 1.5)), 1.1, "240 s, f_t(C2) = 0.028125"),
         ("con360_C2_hcentral", ORANGE, "-", 1.1, "360 s, f_t(C2) = 0.040625"),
         ("con360_C1_hcentral", GREEN, "-", 1.1, "360 s, f_t(C1) = 0.071875")]
handles = [Line2D([], [], color=INK, lw=1.3, label="measured (band: 2.47 K)")]
for key, col, ls, lw, lab in lines:
    z = np.load(os.path.join(a.res, "stage10_series", hs[key]["id"] + ".npz"))
    ax.plot(z["probe_t"], z["probe_away"] - 273.15, color=col, ls=ls, lw=lw, zorder=3)      # the series are in K
    rms = hs[key]["nodes"]["away"]["window"]["rms_K"]
    handles.append(Line2D([], [], color=col, ls=ls, lw=lw, label=f"{lab}; rms {rms:.1f} K"))
ax.axvline(IN.T_PROP_S, color=INK2, lw=0.7, zorder=2)
ax.text(IN.T_PROP_S - 3, 33, "onset 271.5 s", rotation=90, ha="right", va="bottom", fontsize=6.0, color=INK2)
ax.text(IN.T_PROP_S - IN.LAST_S + 2, 33, "last 60 s", ha="left", va="bottom", fontsize=6.0, color=MUTED)
ax.set_xlim(0, 300)
ax.set_ylim(20, 300)
ax.set_xlabel("Time from the trigger's runaway (s)")
ax.set_ylabel("Neighbour's face away from the trigger (C)")
ax.grid(True, color=GRID, lw=0.6)
ax.set_axisbelow(True)
for sp_ in ("top", "right"):
    ax.spines[sp_].set_visible(False)
ax.legend(handles=handles, loc="upper left", fontsize=5.3, frameon=False, handlelength=2.6, handletextpad=0.4)
ax.set_title("a", loc="left", fontsize=8.5, fontweight="bold", color=INK)

# b
ax = axs[1]
names = {"fC1": "f*(C1)\n(Stage 8)", "fC2": "f*(C2)\n(Stage 8)", "f9": "Stage 9's\nfraction"}
dirs = [("series_to_parallel", "o", "fit on series, scored on parallel", -0.12),
        ("parallel_to_series", "s", "fit on parallel, scored on series", 0.12)]
for i, name in enumerate(("fC1", "fC2", "f9")):
    for d, mk, _, dx in dirs:
        v = held["predictors"][name][d]
        lo, hi = v["band_log_2.5_97.5"]
        x = i + dx
        ax.plot([x, x], [lo, hi], color=AXIS, lw=3.2, solid_capstyle="round", zorder=2)
        ax.scatter([x], [v["observed"]["d_log"]], marker=mk, s=22, color=BLUE, zorder=4, edgecolor=SURF, lw=0.6)
        ax.text(x + 0.05, v["observed"]["d_log"], f"p = {v['p_log']:.2f}", fontsize=5.4, color=INK2, va="center",
                ha="left")
ax.axhline(0.0, color=INK2, lw=0.8, zorder=1)
ax.axhline(IN.LOG_MARGIN, color=MUTED, lw=0.7, ls=(0, (3, 2)), zorder=1)
ax.set_xticks([0, 1, 2])
ax.set_xticklabels([names[n] for n in ("fC1", "fC2", "f9")])
ax.set_xlim(-0.45, 2.5)
ax.set_ylim(-0.72, 0.26)
ax.set_ylabel("Held-out mean log score, logistic less constant")
ax.grid(True, axis="y", color=GRID, lw=0.6)
ax.set_axisbelow(True)
for sp_ in ("top", "right"):
    ax.spines[sp_].set_visible(False)
hb = [Line2D([], [], ls="", marker=mk, color=BLUE, ms=4, label=lab) for _, mk, lab, _ in dirs]
hb.append(Line2D([], [], color=AXIS, lw=3.2, label="2.5 to 97.5 % over 10,000 relabellings"))
hb.append(Line2D([], [], color=INK2, lw=0.8, label="0: one probability for every test"))
hb.append(Line2D([], [], color=MUTED, lw=0.7, ls=(0, (3, 2)), label="0.1: P6's margin"))
ax.legend(handles=hb, loc="lower left", fontsize=5.4, frameon=False, handletextpad=0.4)
ax.set_title("b", loc="left", fontsize=8.5, fontweight="bold", color=INK)

fig.subplots_adjust(left=0.07, right=0.99, top=0.94, bottom=0.15)
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(OUT, f"stage10_figure.{ext}"), dpi=300)
print("wrote stage10_figure.png and .pdf")
