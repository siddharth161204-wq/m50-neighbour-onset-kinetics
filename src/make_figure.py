#!/usr/bin/env python3
"""The figure of the note (brief step 6).

a  Time at which each history first self-heats at 0.15 K/min against busbar conductance, 33.2 kJ, 30 s release:
   lumped node, resolved mean and resolved hottest node; cases where only the hottest node gets there are ringed.
b  Kinetic self-heating rate against time for the headline case (33.2 kJ, 30 s, 500 mW/K), the three histories on one
   axis, with the 0.15, 1 and 10 K/min levels (Stage 1, passive).
c  Stage 2, headline case: the hottest node with and without the reaction source, and the lumped node with and
   without it, against the internal-short band of Koenig, Zhao and Deng (2025).
Colours follow the published two-cell figure: lumped blue, resolved mean aqua, resolved hottest orange.
Usage: python3 make_figure.py --out ../results
"""
import argparse, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import NullLocator
import onset_kinetics as OK

ap = argparse.ArgumentParser()
ap.add_argument("--out", default="../results")
ap.add_argument("--series", default="../external/m50-two-cell-pilot/results/resolved_series")
a = ap.parse_args()

INK, INK2, MUTED, GRID, AXIS, SURF, BAND = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#ffffff", "#f0efec"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.5, "axes.edgecolor": AXIS, "axes.labelcolor": INK2,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.linewidth": 0.8, "xtick.major.width": 0.8,
                     "ytick.major.width": 0.8, "figure.facecolor": SURF, "axes.facecolor": SURF,
                     "xtick.labelsize": 6.6, "ytick.labelsize": 6.6})
G = [0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5]
GL = ["5", "10", "20", "50", "100", "200", "500"]
HIST = (("lumped", BLUE, "o", "Lumped node"), ("resolved_mean", AQUA, "s", "Resolved mean"),
        ("hottest_node", ORANGE, "^", "Resolved hottest node"))
rows = {r["case"]: r for r in json.load(open(os.path.join(a.out, "onset_results.json")))["cases"]}


def tidy(ax):
    ax.grid(True, which="major", color=GRID, lw=0.7); ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)


fig, axs = plt.subplots(1, 3, figsize=(7.6, 2.45), gridspec_kw={"wspace": 0.55})

# a: time to 0.15 K/min against conductance, 30 s release, maximum (filled) and median (hollow) energy
ax = axs[0]
for e, ls, fill in (("33223", "-", True), ("21495", "--", False)):
    for key, col, mk, _ in HIST:
        pts = [(g, rows[f"two_E{e}_tau30_G{g:g}"][f"{key}_t_0.15Kpm_s"]) for g in G]
        pts = [(g, y) for g, y in pts if y is not None]
        if pts:
            xs, ys = zip(*pts)
            if len(xs) > 1:
                ax.plot(xs, ys, color=col, lw=1.6, ls=ls, zorder=2)
            ax.scatter(xs, ys, marker=mk, s=24, facecolor=col if fill else SURF, edgecolor=col, linewidth=1.2, zorder=3)
    for g in G:
        r = rows[f"two_E{e}_tau30_G{g:g}"]
        got = [k for k, *_ in HIST if r[f"{k}_t_0.15Kpm_s"] is not None]
        if got == ["hottest_node"]:
            ax.scatter([g], [r["hottest_node_t_0.15Kpm_s"]], marker="o", s=120, facecolor="none", edgecolor=INK2, lw=0.8, zorder=4)
ax.set_xscale("log"); ax.set_xlim(0.0036, 0.68); ax.set_xticks(G); ax.set_xticklabels(GL); ax.xaxis.set_minor_locator(NullLocator())
ax.set_yscale("log"); ax.set_ylim(3, 1000)
ax.set_yticks([3, 10, 30, 100, 300, 1000]); ax.set_yticklabels(["3", "10", "30", "100", "300", "1000"]); ax.yaxis.set_minor_locator(NullLocator())
r = rows["two_E33223_tau30_G0.5"]
ax.annotate(f"{r['hottest_node_t_0.15Kpm_s']:.1f} s", (0.5, r["hottest_node_t_0.15Kpm_s"]), xytext=(0, -10),
            textcoords="offset points", fontsize=6.6, color=INK, ha="center", va="center")
ax.annotate(f"{r['lumped_t_0.15Kpm_s']:.1f} s", (0.5, r["lumped_t_0.15Kpm_s"]), xytext=(-7, 0), textcoords="offset points",
            fontsize=6.6, color=INK, ha="right", va="center")
tidy(ax)
ax.set_xlabel("Busbar conductance (mW/K)")
ax.set_ylabel("Time to 0.15 K/min (s)")
ax.set_title("a  When the chemistry starts", loc="left", fontsize=8, color=INK, fontweight="bold")

# b: self-heating rate against time, headline case
ax = axs[1]
_, ser = OK.run_case(os.path.join(a.series, "two_E33223_tau30_G0.5.npz"), keep_series=True)
for lv in (0.15, 1.0, 10.0):
    ax.axhline(lv, color=AXIS, lw=0.8, ls=(0, (3, 2)), zorder=1)
    ax.text(304, lv, f"{lv:g}", fontsize=6.0, color=INK2, ha="left", va="center", clip_on=False)
for key, col, mk, lab in HIST:
    tt, sh, Tg = ser[key]
    m = tt <= 300
    ax.plot(tt[m], np.where(sh[m] > 1e-3, sh[m], np.nan), color=col, lw=1.4, zorder=2)
ax.set_yscale("log"); ax.set_ylim(1e-3, 1e4); ax.set_xlim(0, 300)
ax.set_yticks([1e-3, 1e-1, 1e1, 1e3]); ax.yaxis.set_minor_locator(NullLocator())
tidy(ax)
ax.set_xlabel("Time (s)")
ax.set_ylabel("Kinetic self-heating rate (K/min)")
ax.set_title("b  How fast it would self-heat", loc="left", fontsize=8, color=INK, fontweight="bold")

# c: Stage 2, headline case
ax = axs[2]
s2 = os.path.join(a.out, "stage2", "two_E33223_tau30_G0.5.npz")
arch = np.load(os.path.join(a.series, "two_E33223_tau30_G0.5.npz"))
ax.axhspan(255.7, 302.1, color=BAND, lw=0, zorder=0)
ax.text(296, 278.9, "internal-short band", fontsize=6.3, color=INK2, va="center", ha="right")
ax.plot(arch["t"], arch["Tmax"] - 273.15, color=ORANGE, lw=1.2, ls=(0, (3, 2)), zorder=2)
ax.plot(arch["t_be"], arch["T2_be"] - 273.15, color=BLUE, lw=1.2, ls=(0, (3, 2)), zorder=2)
if os.path.exists(s2):
    d = np.load(s2)
    ax.plot(d["t"], d["Tmax"] - 273.15, color=ORANGE, lw=1.6, zorder=3)
    ax.plot(d["t_lumped"], d["T_lumped"] - 273.15, color=BLUE, lw=1.6, zorder=3)
ax.set_xlim(0, 300)
tidy(ax)
ax.set_xlabel("Time (s)")
ax.set_ylabel("Temperature (C)")
ax.set_title("c  With the reaction heat (Stage 2)", loc="left", fontsize=8, color=INK, fontweight="bold")

legend = [Line2D([], [], color=BLUE, marker="o", lw=1.6, markersize=4.5, label="Lumped node"),
          Line2D([], [], color=AQUA, marker="s", lw=1.6, markersize=4.5, label="Resolved mean"),
          Line2D([], [], color=ORANGE, marker="^", lw=1.6, markersize=5, label="Resolved hottest node"),
          Line2D([], [], color=INK2, marker="o", ls="none", markerfacecolor="none", markersize=8.5, label="a: only the hottest node starts"),
          Line2D([], [], color=INK2, marker="o", lw=1.3, markersize=4.5, label="a: 33.2 kJ"),
          Line2D([], [], color=INK2, marker="o", lw=1.3, ls=(0, (3, 2)), markersize=4.5, markerfacecolor=SURF, label="a: 21.5 kJ"),
          Line2D([], [], color=INK2, lw=1.6, label="c: with the reaction heat"),
          Line2D([], [], color=INK2, lw=1.2, ls=(0, (3, 2)), label="c: without (archived)")]
fig.legend(handles=legend, loc="upper center", ncol=4, fontsize=6.6, frameon=False, bbox_to_anchor=(0.5, -0.02),
           columnspacing=1.8, handlelength=2.2)
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(a.out, f"neighbour_onset_figure.{ext}"), dpi=240, bbox_inches="tight", pad_inches=0.03)
print("wrote", os.path.join(a.out, "neighbour_onset_figure.png"))
