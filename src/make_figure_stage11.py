#!/usr/bin/env python3
"""Figure 10 (Stage 11): the bands the manuscript states.

a  For each of the four tests (in order of the trigger's energy), the thresholds f*(C1) (orange) and f*(C2) (blue)
   under the posterior mean (a black bar at the bracket's midpoint), the four kinetic draws (filled circles, by rank 5,
   50, 151 and 196 of the hottest node's onset, left to right) and the four thermal draws (hollow diamonds: the
   smallest and the largest radial conductivity, the smallest and the largest heat capacity, left to right). Each
   draw's threshold is its bracket from the search (a bar from the largest fraction that does not meet the criterion
   to the smallest that does), the marker at the midpoint, D113 (2); a test met with no delivery sits at 0. Square-root
   scale.
b  For each of the five tests whose neighbour stayed below the measured maximum with no delivery in Stage 9's reading
   (f_max = 0 in four of them), the far face's peak at f = 0 less the measured maximum: the central case (black bar),
   the four thermal draws at the central contact (hollow diamonds, in the order of a) and the low and high contacts at
   the central properties (triangles down and up). Above zero the far face overheats with no delivery.
c  (The manuscript's Figure 8 only.) For the nine propagated tests at their f_t(C2), the lumped neighbour's crossing
   under the posterior mean (blue bar) and under the four kinetic draws (circles; a triangle at the top where it does
   not cross within 900 s), beside the measured time (black bar).
Usage: python3 make_figure_stage11.py [--res ../results] [--out DIR]
"""
import argparse, csv, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage11_inputs as IN              # noqa: E402

INK, INK2, MUTED, GRID, AXIS, SURF, BAND = "#0b0b0b", "#52514e", "#77756f", "#e1e0d9", "#b9b8ad", "#ffffff", "#ecebe6"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
SQ = (lambda y: np.sqrt(np.clip(y, 0, None)), lambda y: np.square(y))
KIN = [f"d{IN.KIN_DRAWS[r]}" for r in IN.KIN_RANKS]
THERM = list(IN.THERMAL_DRAWS)
SHORT = {"M50_PT_Exp1": "PT_Exp1", "M50_PP_Exp3": "PP_Exp3", "M50_ST_Exp2": "ST_Exp2", "M50_SP_Exp3": "SP_Exp3",
         "M50_PT_Exp3": "PT_Exp3", "M50_ST_Exp1": "ST_Exp1"}


def rows(res, name):
    with open(os.path.join(res, name)) as fh:
        return list(csv.DictReader(fh))


def num(s):
    return None if s in ("", None, "None") else float(s)


def _tidy(ax, axis="y"):
    ax.grid(True, axis=axis, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)


def panel_fstar(ax, res, fs=7.0):
    th = {(r["criterion"], r["test"], r["draw"]): r for r in rows(res, "stage11_thresholds.csv")}
    ax.set_yscale("function", functions=SQ)
    tests = list(IN.A_TESTS)
    top = 1.0
    for i, test in enumerate(tests):
        for crit, dx, col in (("C1", -0.22, ORANGE), ("C2", 0.22, BLUE)):
            x0 = i + dx
            m = th[(crit, test, "mean")]
            fm = num(m["f_star"])
            ax.plot([x0 - 0.13, x0 + 0.13], [fm, fm], color=INK, lw=1.6, solid_capstyle="butt", zorder=4)
            for k, (d, filled) in enumerate([(d, True) for d in KIN] + [(d, False) for d in THERM]):
                r = th.get((crit, test, d))
                if r is None or r["status"] not in ("zero", "bracket", "above"):
                    continue
                x = x0 - 0.16 + 0.04 * k if k < 4 else x0 + 0.04 + 0.04 * (k - 4)
                if r["status"] == "zero":
                    lo = hi = mid = 0.0
                elif r["status"] == "above":
                    lo, hi, mid = num(r["lo"]), top, top
                else:
                    lo, hi, mid = num(r["lo"]), num(r["hi"]), num(r["f_star"])
                ax.plot([x, x], [lo, hi], color=col, lw=0.8, alpha=0.75, zorder=2)
                ax.scatter([x], [mid], s=13 if filled else 15, marker="o" if filled else "D", zorder=3,
                           facecolor=col if filled else SURF, edgecolor=col, lw=0.8, clip_on=False)
    ticks = [0, 0.005, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5]
    ax.set_yticks(ticks)
    ax.set_yticklabels(["0", "0.005", "0.02", "0.05", "0.1", "0.2", "0.3", "0.5"])
    ax.set_ylim(0, 0.56)
    ax.set_xticks(range(len(tests)))
    ax.set_xticklabels([SHORT[t] for t in tests])
    ax.set_xlim(-0.5, len(tests) - 0.5)
    ax.set_ylabel("Threshold $f^*$ (square-root scale)")
    _tidy(ax)
    hs = [Line2D([], [], ls="", marker="o", mfc=ORANGE, mec=ORANGE, ms=3.6, label="$f^*$(C1)"),
          Line2D([], [], ls="", marker="o", mfc=BLUE, mec=BLUE, ms=3.6, label="$f^*$(C2)"),
          Line2D([], [], color=INK, lw=1.6, label="posterior mean"),
          Line2D([], [], ls="", marker="o", mfc=INK2, mec=INK2, ms=3.6, label="kinetic draws"),
          Line2D([], [], ls="", marker="D", mfc=SURF, mec=INK2, ms=3.6, label="thermal draws")]
    ax.legend(handles=hs, loc="upper right", frameon=False, fontsize=fs, handletextpad=0.3, borderaxespad=0.1,
              labelspacing=0.3)


def panel_overshoot(ax, res, fs=7.0):
    ov = rows(res, "stage11_overshoot.csv")
    tests = list(IN.C_TESTS)
    by = {(r["test"], r["thermal"], r["contact"]): r for r in ov}
    ax.axhline(0.0, color=INK2, lw=0.8, zorder=1)
    for i, test in enumerate(tests):
        r = by.get((test, "central", "central"))
        v = num(r["overshoot_K"]) if r else None
        if v is not None:
            ax.plot([i - 0.3, i + 0.3], [v, v], color=INK, lw=1.6, solid_capstyle="butt", zorder=4)
        for k, lab in enumerate(THERM):
            r = by.get((test, lab, "central"))
            v = num(r["overshoot_K"]) if r else None
            if v is not None:
                ax.scatter([i - 0.24 + 0.08 * k], [v], s=15, marker="D", facecolor=SURF, edgecolor=AQUA, lw=0.9,
                           zorder=3)
        for h, mk, x in (("low", "v", 0.16), ("high", "^", 0.24)):
            r = by.get((test, "central", h))
            v = num(r["overshoot_K"]) if r else None
            if v is not None:
                ax.scatter([i + x], [v], s=18, marker=mk, color=AQUA, zorder=3, lw=0)
    vals = [num(r["overshoot_K"]) for r in ov if num(r["overshoot_K"]) is not None]
    ax.set_ylim(min(vals) - 6.0, max(vals) + 30.0)
    ax.set_xticks(range(len(tests)))
    ax.set_xticklabels([SHORT[t] for t in tests])
    ax.set_xlim(-0.5, len(tests) - 0.5)
    ax.set_ylabel("Far face's peak at $f$ = 0\nless the measured maximum (K)")
    _tidy(ax)
    hs = [Line2D([], [], color=INK, lw=1.6, label="central"),
          Line2D([], [], ls="", marker="D", mfc=SURF, mec=AQUA, ms=3.6, label="thermal draws"),
          Line2D([], [], ls="", marker="v", color=AQUA, ms=4, label="low contact"),
          Line2D([], [], ls="", marker="^", color=AQUA, ms=4, label="high contact")]
    ax.legend(handles=hs, loc="upper right", frameon=False, fontsize=fs, handletextpad=0.3, borderaxespad=0.1,
              labelspacing=0.3, ncol=2, columnspacing=0.8)


def panel_times(ax, res, fs=7.0):
    tr = rows(res, "stage11_times.csv")
    tests = sorted({r["test"] for r in tr}, key=lambda t: num(next(r for r in tr if r["test"] == t)["t_measured_s"]))
    for i, test in enumerate(tests):
        rs = [r for r in tr if r["test"] == test]
        tm, t0 = num(rs[0]["t_measured_s"]), num(rs[0]["t_mean_s"])
        ax.plot([i - 0.32, i + 0.32], [tm, tm], color=INK, lw=1.6, solid_capstyle="butt", zorder=4)
        if t0 is not None:
            ax.plot([i - 0.32, i + 0.32], [t0, t0], color=BLUE, lw=1.6, solid_capstyle="butt", zorder=4)
        for k, r in enumerate(sorted(rs, key=lambda r: int(r["rank"]))):
            x = i - 0.15 + 0.1 * k
            if r["recorded"] != "True":
                continue
            t = num(r["t_draw_s"])
            if t is None:
                ax.scatter([x], [945], s=18, marker="^", facecolor=SURF, edgecolor=BLUE, lw=0.9, zorder=3,
                           clip_on=False)
            else:
                ax.scatter([x], [t], s=13, marker="o", color=BLUE, zorder=3, lw=0)
    ax.set_xticks(range(len(tests)))
    ax.set_xticklabels([SHORT.get(t, t.replace("M50_", "")) for t in tests], rotation=45, ha="right",
                       rotation_mode="anchor")
    ax.set_xlim(-0.5, len(tests) - 0.5)
    ax.set_ylim(0, 990)
    ax.axhline(900.0, color=MUTED, lw=0.7, ls=(0, (3, 2)), zorder=1)
    ax.text(-0.4, 905, "900 s", fontsize=fs, color=INK2, va="bottom", ha="left")
    ax.set_ylabel("Crossing of C2 (s)")
    _tidy(ax)
    hs = [Line2D([], [], color=INK, lw=1.6, label="measured"),
          Line2D([], [], color=BLUE, lw=1.6, label="posterior mean"),
          Line2D([], [], ls="", marker="o", color=BLUE, ms=3.6, label="kinetic draws"),
          Line2D([], [], ls="", marker="^", mfc=SURF, mec=BLUE, ms=4, label="none by 900 s")]
    ax.legend(handles=hs, loc="upper left", frameon=False, fontsize=fs, handletextpad=0.3, borderaxespad=0.1,
              labelspacing=0.3, ncol=2, columnspacing=0.8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", default=os.path.join(HERE, "..", "results"))
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or a.res
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.5, "axes.edgecolor": AXIS,
                         "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.linewidth": 0.8,
                         "xtick.labelsize": 7.0, "ytick.labelsize": 7.0, "figure.facecolor": SURF,
                         "axes.facecolor": SURF})
    fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.1), gridspec_kw={"wspace": 0.3, "width_ratios": [1.0, 1.0]})
    panel_fstar(axs[0], a.res)
    axs[0].set_title("a", loc="left", fontsize=8.5, fontweight="bold", color=INK)
    panel_overshoot(axs[1], a.res)
    axs[1].set_title("b", loc="left", fontsize=8.5, fontweight="bold", color=INK)
    fig.subplots_adjust(left=0.08, right=0.99, top=0.93, bottom=0.1)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(out, f"stage11_figure.{ext}"), dpi=300)
    print("wrote stage11_figure.png and .pdf")


if __name__ == "__main__":
    main()
