#!/usr/bin/env python3
"""Figure 3 (Stage 4, version 1.1.0): which submodel of the kinetic posterior carries each output's spread.

a  Main-effect shares (predictions_v11.md): for each output and conductance (33.2 kJ, 30 s), the variance over each
   submodel's 200 grouped runs (the other two at their posterior mean) divided by the variance over the 200 joint draws
   of Stage 3a, stacked; the bar's length is the sum of the three shares (printed at its end), the whisker the paired
   bootstrap 95 % interval of that sum, and the dashed line at 1 is where the shares add up to the joint variance.
b  The lead at 33.2 kJ, 30 s, 500 mW/K over the 200 joint draws (Stage 3a), over the joint draws whose particle of
   the dominant submodel lies in that file's central half (the restricted set of P4), and over those whose particle lies
   in the central half chosen on its SEI-decomposition rows alone (secondary), as shares per 2 s bin; the bars above
   give each set's 2.5 to 97.5 % interval and its width.
Colours: the submodels take categorical slots that Figures 1 and 2 do not use (violet, magenta, yellow; Figure 1 draws
the resolved mean in aqua), checked for colour-blind separation, so blue, orange and aqua keep their meanings.
Usage: python3 make_figure_v11.py --out ../results
"""
import argparse, csv, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ap = argparse.ArgumentParser()
ap.add_argument("--out", default="../results")
a = ap.parse_args()

INK, INK2, MUTED, GRID, AXIS, SURF = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#ffffff"
COL = {"an_ele": "#6250d6", "ncm811": "#e87ba4", "separator": "#eda100"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.5, "axes.edgecolor": AXIS, "axes.labelcolor": INK2,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.linewidth": 0.8, "xtick.major.width": 0.8,
                     "ytick.major.width": 0.8, "figure.facecolor": SURF, "axes.facecolor": SURF,
                     "xtick.labelsize": 6.6, "ytick.labelsize": 6.6})
R = json.load(open(os.path.join(a.out, "v11_sensitivity.json")))
HEAD = "two_E33223_tau30_G0.5"
OUTS = [("lead_s", "Lead"), ("hottest_onset_s", "Hottest-node onset"), ("lumped_onset_s", "Lumped onset"),
        ("hottest_onset_T_C", "Hottest-node onset temperature")]
CL = ["500 mW/K", "100 mW/K"]


def tidy(ax):
    ax.grid(True, which="major", color=GRID, lw=0.7); ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)


def share_range(g):
    v = [R["shares"][cl][k]["by_group"][g]["share"] for k, _ in OUTS for cl in CL]
    return min(v), max(v)


fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.05), gridspec_kw={"wspace": 0.22, "width_ratios": [1.12, 1.0]})

# a: stacked main-effect shares
ax = axs[0]
ticks, ticklabels, y = [], [], 0.0
H = 0.62
for y_key, y_name in OUTS:
    ax.text(0.0, y - 0.05, y_name, ha="left", va="bottom", fontsize=6.7, color=INK)
    for cl in CL:
        yy = y + 0.62 + (0.0 if cl == CL[0] else 0.86)
        e = R["shares"][cl][y_key]
        left = 0.0
        for g in ("an_ele", "ncm811", "separator"):
            s = e["by_group"][g]["share"]
            ax.barh(yy, s, left=left, height=H, color=COL[g], edgecolor=SURF, linewidth=1.0, zorder=2)
            left += s
        lo, hi = e["sum_95_bootstrap"]
        ax.plot([lo, hi], [yy, yy], color=INK, lw=0.8, zorder=3)
        ax.plot([lo, lo], [yy - 0.13, yy + 0.13], color=INK, lw=0.8, zorder=3)
        ax.plot([hi, hi], [yy - 0.13, yy + 0.13], color=INK, lw=0.8, zorder=3)
        ax.text(hi + 0.025, yy, f"{e['sum']:.2f}", va="center", ha="left", fontsize=6.3, color=INK2)
        ticks.append(yy); ticklabels.append(cl)
    y += 2.75
ax.axvline(1.0, color=INK, lw=0.8, ls=(0, (3, 2)), zorder=1)
ax.set_yticks(ticks); ax.set_yticklabels(ticklabels)
ax.set_ylim(y - 0.7, -0.45)
ax.set_xlim(0, 1.42)
ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4])
ax.set_xlabel("Share of the joint draws' variance (bar: sum of the three)")
c_lo, c_hi = share_range("ncm811"); s_lo, s_hi = share_range("separator")
ax.legend(handles=[Patch(facecolor=COL["an_ele"], edgecolor="none", label="Anode-electrolyte (holds the SEI)"),
                   Patch(facecolor=COL["ncm811"], edgecolor="none", label=f"NCM811 cathode: {c_hi:.3f} in every row"),
                   Patch(facecolor=COL["separator"], edgecolor="none", label=f"Separator: {s_lo:.3f} to {s_hi:.3f}")],
          loc="lower left", bbox_to_anchor=(-0.01, 1.0), ncol=3, frameon=False, fontsize=6.0, handlelength=1.1,
          columnspacing=0.9, handletextpad=0.4, borderaxespad=0.1)
ax.set_title("a  Which submodel carries each output's spread", loc="left", fontsize=7.8, color=INK, fontweight="bold", pad=15)
tidy(ax); ax.grid(False, axis="y")
ax.tick_params(axis="y", length=0)

# b: the lead, full joint posterior against the restricted sets
ax = axs[1]
dom = R["dominant_submodel"]
rest = R["restriction"][dom]["by_case"]["500 mW/K"]
rows_csv = [r for r in csv.DictReader(open(os.path.join(a.out, "v11_sensitivity.csv"))) if r["case"] == HEAD and r["run"] == "joint"]
lead = np.array([float(r["lead_s"]) for r in rows_csv])
inside = np.array([r[f"{dom}_in_central_half"] == "True" for r in rows_csv])
sets = [("All 200 joint draws", lead, INK, "-", rest["full"]),
        (f"Central half ({inside.sum()})", lead[inside], COL[dom], "-", rest["restricted"])]
sei = rest.get("per_reaction_restriction", {}).get("sei_decomp")
col_sei = f"{dom}_sei_decomp_rows_in_central_half"
if sei is not None and col_sei in rows_csv[0]:
    in_sei = np.array([r[col_sei] == "True" for r in rows_csv])
    sets.append((f"Half on SEI rows ({in_sei.sum()})", lead[in_sei], COL[dom], (0, (2.6, 1.4)), sei["restricted"]))
bins = np.arange(np.floor(lead.min() / 2) * 2, np.ceil(lead.max() / 2) * 2 + 2, 2.0)
peak = 0.0
for lab, v, c, ls, w in sets:
    n, _, _ = ax.hist(v, bins=bins, weights=np.full(v.size, 100.0 / v.size), histtype="step", color=c, lw=1.4, ls=ls, zorder=3)
    peak = max(peak, n.max())
ymax = peak * 1.72
ax.set_ylim(0, ymax)
for i, (lab, v, c, ls, w) in enumerate(sets):
    yy = ymax * (0.89 - 0.07 * i)
    ax.plot([w["p2.5"], w["p97.5"]], [yy, yy], color=c, lw=1.8, ls=ls, solid_capstyle="butt", zorder=4)
    ax.text(w["p97.5"] + 0.8, yy, f"{w['width_s']:.1f} s", va="center", fontsize=6.3, color=INK2)
ax.text(sets[0][4]["p2.5"], ymax * 0.965, "2.5 to 97.5 % of each set, and its width", va="center", ha="left",
        fontsize=6.0, color=INK2)
ax.legend(handles=[Line2D([], [], color=c, lw=1.4, ls=ls, label=lab) for lab, v, c, ls, w in sets],
          loc="center", bbox_to_anchor=(0.585, 0.40), frameon=False, fontsize=6.1, handlelength=1.6)
ax.set_xlabel("Lumped onset minus hottest-node onset (s)")
ax.set_ylabel("Share of draws per 2 s (%)")
ax.set_title("b  The lead at 33.2 kJ, 30 s, 500 mW/K", loc="left", fontsize=7.8, color=INK, fontweight="bold", pad=15)
tidy(ax)

for ext in ("png", "pdf"):
    fig.savefig(os.path.join(a.out, f"v11_figure.{ext}"), dpi=300, bbox_inches="tight")
print("figure written; dominant", dom, "restricted draws", int(inside.sum()))
