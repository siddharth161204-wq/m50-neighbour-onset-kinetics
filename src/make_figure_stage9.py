#!/usr/bin/env python3
"""Figure 8 (Stage 9): the delivered fraction read from each test's time and peak.

a  With Stage 8's delivery (21.39 s): each propagated test's crossing time t_c against the delivered fraction above
   the lower end of its Stage 8 bracket, f - f*_lo (a square-root scale), for the hot spot (C1, circles) and the
   lumped neighbour (C2, squares), one line per test and criterion, every run of Part A drawn (A1's grid and A2's
   bisection). Each test's measured time to propagation is a short horizontal mark, placed where its C2 line meets
   it if A2 found f_t(C2) there, at the start of its C2 line otherwise. The band is the range of the nine measured
   times.
b  For each of the sixteen tests, against its trigger energy: f_t(C2) (squares) and f_t(C1) (circles, where A2
   found any) for the propagated tests, and f_max at the thermocouple node (diamonds) for the not propagated. A
   fraction whose run came within the search's tolerance (10 s, 5 K) is a point; one interpolated within a bracket
   has the bracket as a bar. A propagated test whose search ended at the threshold, with no run reproducing its time,
   is drawn hollow at its bracket (D101). The two tests with maxima of 626 and 808 C are drawn hollow (exploratory). The dashed
   lines mark the largest registered f_max and the smallest f_t(C2), the separation of Part C1. The vertical axis
   is on a square-root scale.
Usage: python3 make_figure_stage9.py [--res ../results] [--out DIR]
"""
import argparse, csv, json, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage9_inputs as IN               # noqa: E402

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
COL = {"C1": ORANGE, "C2": BLUE}
MARK = {"C1": "o", "C2": "s"}


def num(s):
    return None if s in ("", None) else float(s)


def rows(name):
    with open(os.path.join(a.res, name)) as fh:
        return list(csv.DictReader(fh))


ind = rows("stage9_induction.csv")
frac = {r["test"]: r for r in rows("stage9_fractions.csv")}
card = json.load(open(os.path.join(a.res, "stage9_scorecard.json")))
f8 = IN.stage8_fstar()
tests = {t["test"]: t for t in IN.tests()}
prop = [x for x, t in tests.items() if t["propagated"]]
fwd = lambda y: np.sqrt(np.clip(y, 0, None))
inv = lambda y: np.square(y)

fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.6), gridspec_kw={"wspace": 0.28, "width_ratios": [1.0, 1.1]})

# a
ax = axs[0]
ax.set_xscale("function", functions=(fwd, inv))
tm_all = [tests[x]["time_s"] for x in prop]
xr = 0.26
ax.axhspan(min(tm_all), max(tm_all), color=BAND, lw=0, zorder=0)
for crit in IN.CRITERIA:
    for x in prop:
        pts = sorted((num(r["f"]), num(r["t_c_s"])) for r in ind
                     if r["chain"] == f"A1_{crit}_{x}" and r["t_c_s"] not in ("", None))
        if not pts:
            continue
        lo = f8[x][crit]["lo"] or 0.0
        xs = [f - lo for f, _ in pts]
        ys = [t for _, t in pts]
        ax.plot(xs, ys, color=COL[crit], lw=0.8, alpha=0.75, zorder=2)
        ax.scatter(xs, ys, s=7, marker=MARK[crit], color=COL[crit], zorder=3, lw=0)
for x in prop:
    tm = tests[x]["time_s"]
    lo = f8[x]["C2"]["lo"] or 0.0
    ft = num(frac[x].get("ft_C2"))
    if ft is not None:
        xm = ft - lo
    else:
        pts = sorted(num(r["f"]) for r in ind if r["chain"] == f"A1_C2_{x}" and r["t_c_s"] not in ("", None))
        xm = (pts[0] - lo) if pts else 0.0
    q = fwd(max(xm, 0.0))
    ax.plot([inv(max(q - 0.012, 0.0)), inv(q + 0.012)], [tm, tm], color=INK, lw=1.4, solid_capstyle="butt", zorder=4)
ax.set_xlim(0, xr)
tmax = max([num(r["t_c_s"]) for r in ind if r["chain"].startswith("A1_") and r["t_c_s"] not in ("", None)] + [0.0])
ytop = min(900.0, max(420.0, 1.05 * tmax))
ax.set_ylim(0, ytop)
ticks = [0, 0.0125, 0.05, 0.1, 0.2]
ax.set_xticks(ticks)
ax.set_xticklabels(["0", "0.0125", "0.05", "0.1", "0.2"])
ax.set_xlabel("f − f*_lo, above the Stage 8 bracket's lower end (square-root scale)")
ax.set_ylabel("Crossing time t_c (s), 21.39 s delivery")
ax.grid(True, color=GRID, lw=0.7)
ax.set_axisbelow(True)
for sp_ in ("top", "right"):
    ax.spines[sp_].set_visible(False)
ax.text(xr * 0.98, min(tm_all) + 4, "range of the measured times", ha="right", va="bottom", fontsize=5.6,
        color=INK2)
hs = [Line2D([], [], color=ORANGE, marker="o", ms=3.0, lw=0.8, label="C1 hot spot at 255.7 C"),
      Line2D([], [], color=BLUE, marker="s", ms=3.0, lw=0.8, label="C2 lumped neighbour at 255.7 C"),
      Line2D([], [], color=INK, lw=1.4, label="measured time (on its C2 line)")]
ax.legend(handles=hs, loc="upper right", fontsize=5.4, frameon=False, handletextpad=0.4)
ax.set_title("a", loc="left", fontsize=8.5, fontweight="bold", color=INK)

# b
ax = axs[1]
ax.set_yscale("function", functions=(fwd, inv))
top = 1.05
found_c1 = found_thr = False
for x, t in tests.items():
    r = frac[x]
    E = t["E_b_J"] / 1e3
    if t["propagated"]:
        for crit, dx in (("C2", 0.0), ("C1", -0.45)):
            st = r.get(f"ft_{crit}_status")
            if crit == "C2" and st == "threshold":          # D101 (8): no run of the search reproduces the time; its bracket shown
                lo, hi = num(r["ft_C2_lo"]), num(r["ft_C2_hi"])
                ax.plot([E + dx] * 2, [lo, hi], color=BLUE, lw=0.9, alpha=0.8, zorder=2)
                ax.scatter([E + dx], [hi], s=16, marker="s", facecolor=SURF, edgecolor=BLUE, lw=0.9, zorder=3)
                found_thr = True
                continue
            if st not in ("matched", "bracketed") or r.get(f"ft_{crit}_across_jump") == "True":
                continue
            lo, hi, ft = num(r[f"ft_{crit}_lo"]), num(r[f"ft_{crit}_hi"]), num(r[f"ft_{crit}"])
            found_c1 = found_c1 or crit == "C1"
            if st == "bracketed":
                ax.plot([E + dx] * 2, [lo, hi], color=COL[crit], lw=0.9, alpha=0.8, zorder=2)
            ax.scatter([E + dx], [ft], s=16, marker=MARK[crit], color=COL[crit], zorder=3, lw=0)
    else:
        st = r.get("fmax_status")
        if st not in ("zero", "matched", "bracketed"):
            continue
        expl = x in IN.EXPLORATORY_FMAX
        lo, hi, fm = num(r["fmax_lo"]) or 0.0, num(r["fmax_hi"]) or 0.0, num(r["fmax"])
        if st == "bracketed":
            ax.plot([E, E], [lo, hi], color=GREEN, lw=0.9, alpha=0.8, zorder=2, ls=(0, (2, 1.5)) if expl else "-")
        ax.scatter([E], [fm], s=18, marker="D", zorder=3, facecolor=SURF if expl else GREEN, edgecolor=GREEN,
                   lw=0.9, clip_on=False)
sep = card["separation"]["C2"]
if sep.get("separate") is not None:
    big, small = sep["largest_f_max"]["f"], sep["smallest_f_t"]["f"]
    ax.axhline(big, color=GREEN, lw=0.7, ls=(0, (3, 2)), zorder=1)
    ax.axhline(small, color=BLUE, lw=0.7, ls=(0, (3, 2)), zorder=1)
ticks = [0, 0.005, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
ax.set_yticks(ticks)
ax.set_yticklabels(["0", "0.005", "0.02", "0.05", "0.1", "0.2", "0.5", "1"])
ax.set_ylim(0, top)
ax.set_xlim(5, 56.5)
ax.set_xlabel("Trigger energy E_b (kJ)")
ax.set_ylabel("Delivered fraction of the ejected energy (square-root scale)")
ax.grid(True, axis="y", color=GRID, lw=0.7)
ax.set_axisbelow(True)
for sp_ in ("top", "right"):
    ax.spines[sp_].set_visible(False)
hs = [Line2D([], [], ls="", marker="s", color=BLUE, ms=3.6, label="f_t(C2), propagated")]
if found_thr:
    hs.append(Line2D([], [], ls="", marker="s", mfc=SURF, mec=BLUE, ms=3.6, label="no f_t(C2): its threshold's bracket"))
if found_c1:
    hs.append(Line2D([], [], ls="", marker="o", color=ORANGE, ms=3.6, label="f_t(C1), propagated"))
hs += [Line2D([], [], ls="", marker="D", mfc=GREEN, mec=GREEN, ms=3.4, label="f_max, not propagated"),
      Line2D([], [], ls="", marker="D", mfc=SURF, mec=GREEN, ms=3.4, label="f_max, 626 and 808 C (exploratory)"),
      Line2D([], [], color=GREEN, lw=0.7, ls=(0, (3, 2)), label="largest registered f_max"),
      Line2D([], [], color=BLUE, lw=0.7, ls=(0, (3, 2)), label="smallest f_t(C2)")]
ax.legend(handles=hs, loc="upper left", fontsize=5.2, frameon=False, handletextpad=0.3, ncol=2, columnspacing=0.8)
ax.set_title("b", loc="left", fontsize=8.5, fontweight="bold", color=INK)
fig.subplots_adjust(left=0.08, right=0.99, top=0.95, bottom=0.13)
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(OUT, f"stage9_figure.{ext}"), dpi=300)
print("wrote stage9_figure.png and .pdf")
