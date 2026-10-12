#!/usr/bin/env python3
"""Figure 2 (Stage 3, brief): kinetic and thermophysical uncertainty in the onset.

a  The lead (lumped onset minus hottest-node onset at 0.15 K/min) at 33.2 kJ, 30 s, 500 mW/K: its distribution over
   the 200 kinetic draws at the nominal thermal inputs, over the 30 thermal draws with the posterior-mean kinetics, and
   over the 210 combined pairs (share of each set per 2 s bin), with zero marked and the posterior-mean value.
b  The hottest-node and lumped onset times against busbar conductance at 33.2 kJ (30 s release): median and the band
   from the 2.5 to the 97.5 percentile over the 200 kinetic draws, with the posterior-mean onsets of Stage 1. A band
   that reaches the dashed line at 900 s holds draws in which that node does not start within the run.
Colours follow Figure 1: lumped node blue, resolved hottest node orange; the factors in (a) are told apart by line style.
Usage: python3 make_figure_stage3.py --out ../results
"""
import argparse, csv, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator

ap = argparse.ArgumentParser()
ap.add_argument("--out", default="../results")
a = ap.parse_args()

INK, INK2, MUTED, GRID, AXIS, SURF, BAND = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#ffffff", "#f0efec"
BLUE, ORANGE = "#2a78d6", "#eb6834"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.5, "axes.edgecolor": AXIS, "axes.labelcolor": INK2,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.linewidth": 0.8, "xtick.major.width": 0.8,
                     "ytick.major.width": 0.8, "figure.facecolor": SURF, "axes.facecolor": SURF,
                     "xtick.labelsize": 6.6, "ytick.labelsize": 6.6})
LV = "0.15Kpm"
HEADLINE = "two_E33223_tau30_G0.5"
GS = [0.05, 0.1, 0.2, 0.5]


def num(v):
    return None if v in ("", "None", None) else float(v)


def tidy(ax):
    ax.grid(True, which="major", color=GRID, lw=0.7); ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)


on = {}
for r in csv.DictReader(open(os.path.join(a.out, "stage3a_onsets.csv"))):
    on[(int(r["draw"]), r["case"], r["history"])] = num(r[f"t_{LV}_s"])
draws = sorted({k[0] for k in on})
bc = list(csv.DictReader(open(os.path.join(a.out, "stage3bc_onsets.csv"))))
s1 = {r["case"]: r for r in json.load(open(os.path.join(a.out, "onset_results.json")))["cases"]}


def leads_kinetic():
    out = []
    for d in draws:
        h, l = on[(d, HEADLINE, "hottest_node")], on[(d, HEADLINE, "lumped")]
        if h is not None and l is not None:
            out.append(l - h)
    return np.array(out)


def leads_bc(kind):
    out = []
    for r in bc:
        if (kind == "thermal") != (int(r["kinetic_draw"]) == 0):
            continue
        h, l = num(r[f"hottest_node_t_{LV}_s"]), num(r[f"lumped_t_{LV}_s"])
        if h is not None and l is not None:
            out.append(l - h)
    return np.array(out)


LK, LT, LC = leads_kinetic(), leads_bc("thermal"), leads_bc("combined")
mean_lead = s1[HEADLINE][f"lumped_t_{LV}_s"] - s1[HEADLINE][f"hottest_node_t_{LV}_s"]

fig, axs = plt.subplots(1, 2, figsize=(7.6, 2.35), gridspec_kw={"wspace": 0.32, "width_ratios": [1.15, 1.0]})

# a: lead histograms
ax = axs[0]
lo = min(0.0, np.floor(min(LK.min(), LT.min(), LC.min()) / 2) * 2)
hi = np.ceil(max(LK.max(), LT.max(), LC.max()) / 2) * 2
bins = np.arange(lo, hi + 2, 2.0)
ax.hist(LC, bins=bins, weights=np.full(LC.size, 100.0 / LC.size), histtype="stepfilled", color=BAND, ec="none", zorder=1)
ax.hist(LC, bins=bins, weights=np.full(LC.size, 100.0 / LC.size), histtype="step", color=INK2, lw=0.9, zorder=2)
ax.hist(LK, bins=bins, weights=np.full(LK.size, 100.0 / LK.size), histtype="step", color=INK, lw=1.6, zorder=3)
ax.hist(LT, bins=bins, weights=np.full(LT.size, 100.0 / LT.size), histtype="step", color=MUTED, lw=1.4, ls=(0, (3, 2)), zorder=4)
ax.axvline(0, color=INK, lw=0.9, zorder=5)
ax.axvline(mean_lead, color=ORANGE, lw=1.0, ls=(0, (1, 1.5)), zorder=5)
ymax = ax.get_ylim()[1]
ax.text(0.8, ymax * 0.95, "zero lead", color=INK2, fontsize=6.3, va="top")
ax.text(mean_lead + 4.5, ymax * 0.66, f"dotted: posterior mean,\nnominal inputs, {mean_lead:.1f} s", color=INK2, fontsize=6.3, va="top", ha="left")
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
ax.legend(handles=[Line2D([], [], color=INK, lw=1.6, label=f"kinetic draws ({LK.size})"),
                   Line2D([], [], color=MUTED, lw=1.4, ls=(0, (3, 2)), label=f"thermophysical draws ({LT.size})"),
                   Patch(facecolor=BAND, edgecolor=INK2, lw=0.9, label=f"both ({LC.size} pairs)")],
          loc="upper right", frameon=False, fontsize=6.3, handlelength=2.2)
ax.set_xlabel("Lumped onset minus hottest-node onset (s)")
ax.set_ylabel("Share of draws per 2 s (%)")
ax.set_title("a  The lead at 33.2 kJ, 30 s, 500 mW/K", loc="left", fontsize=7.8, color=INK, fontweight="bold")
tidy(ax)

# b: onset against conductance, 2.5 to 97.5 percentile bands over the kinetic draws
ax = axs[1]
for hist, col, mk, lab in (("lumped", BLUE, "o", "Lumped node"), ("hottest_node", ORANGE, "^", "Resolved hottest node")):
    med, p_lo, p_hi, ref = [], [], [], []
    for g in GS:
        case = f"two_E33223_tau30_G{g:g}"
        # a node that does not start within the run ranks after every onset; a percentile among those draws is
        # drawn at the run's end, 900 s (the band then reaches the dashed line)
        v = np.array([1e9 if on[(d, case, hist)] is None else on[(d, case, hist)] for d in draws])
        q = np.percentile(v, [2.5, 50, 97.5])
        p_lo.append(min(q[0], 900.0)); med.append(min(q[1], 900.0)); p_hi.append(min(q[2], 900.0))
        ref.append(s1[case][f"{hist}_t_{LV}_s"])
    ax.fill_between(GS, p_lo, p_hi, color=col, alpha=0.18, lw=0, zorder=1)
    ax.plot(GS, med, color=col, lw=1.6, zorder=2, label=f"{lab}, median")
    ax.scatter(GS, [np.nan if r is None else r for r in ref], marker=mk, s=22, facecolor=SURF, edgecolor=col, lw=1.2, zorder=3)
ax.axhline(900.0, color=MUTED, lw=0.8, ls=(0, (3, 2)), zorder=0)
ax.text(GS[0], 900.0 * 1.06, "end of the run, 900 s", color=INK2, fontsize=6.3, va="bottom")
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xticks(GS); ax.set_xticklabels([f"{int(g * 1000)}" for g in GS]); ax.xaxis.set_minor_locator(NullLocator())
ax.set_ylim(0.5, 1500)
ax.set_xlabel("Busbar conductance (mW/K)")
ax.set_ylabel("First time at 0.15 K/min (s)")
ax.legend(handles=[Line2D([], [], color=BLUE, lw=1.6, label="Lumped node, median"),
                   Line2D([], [], color=ORANGE, lw=1.6, label="Resolved hottest node, median"),
                   Patch(facecolor=MUTED, alpha=0.3, label="2.5 to 97.5 % of kinetic draws"),
                   Line2D([], [], marker="o", color=MUTED, mfc=SURF, lw=0, label="Posterior mean (Stage 1)")],
          loc="lower left", frameon=False, fontsize=6.3)
ax.set_title("b  Onset against conductance, 33.2 kJ, 30 s", loc="left", fontsize=7.8, color=INK, fontweight="bold")
tidy(ax)

for ext in ("png", "pdf"):
    fig.savefig(os.path.join(a.out, f"stage3_figure.{ext}"), dpi=300, bbox_inches="tight")
print("leads (kinetic, thermal, both):", LK.size, LT.size, LC.size, "posterior-mean lead", round(mean_lead, 2))
