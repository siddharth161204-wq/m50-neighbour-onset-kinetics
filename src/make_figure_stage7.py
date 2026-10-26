#!/usr/bin/env python3
"""Figure 6 (Stage 7): the ignition condition scored test by test.

a  The sixteen tests of Tables 3 and 4 (rows; parallel above, series below, each in order of the trigger's maximum),
   the measured outcome and time to propagation beside the prediction of each criterion at the central contact
   (columns C1 to C7): the time at which the criterion's clock reaches its level, or "no". The cell's shade gives the
   class against the measured outcome: a hit or a correct rejection (blue tints), a false alarm (orange), a miss
   (magenta). Model times run from the start of cell 1's release; the paper's from the trigger's runaway (D34), with
   no shift. The bottom rows count hits, misses, false alarms and correct rejections.
b  Part C at the central contact: the neighbour's peak after the event (65.52 kJ released from its separator's
   melting at 138.5 C, at the hot spot for C4 and in the lumped neighbour for C5), at the hot spot (diamonds) and in
   the lumped neighbour (circles), beside the measured neighbour maximum of each test (black; filled, propagated).
   The grey band is the measured range of the propagating neighbours' maxima.
Usage: python3 make_figure_stage7.py --res ../results
"""
import argparse, csv, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage7_inputs as IN

ap = argparse.ArgumentParser()
ap.add_argument("--res", default=os.path.join(HERE, "..", "results"))
ap.add_argument("--out", default=None)
a = ap.parse_args()
OUT = a.out or a.res

INK, INK2, MUTED, GRID, AXIS, SURF, BAND = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#ffffff", "#f0efec"
BLUE, ORANGE, MAGENTA = "#2a78d6", "#eb6834", "#e87ba4"
FILL = {"hit": "#cfe0f6", "correct rejection": "#eef4fc", "false alarm": "#fbd9c9", "miss": "#f9d7e4"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.5, "axes.edgecolor": AXIS, "axes.labelcolor": INK2,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.linewidth": 0.8, "xtick.major.width": 0.8,
                     "ytick.major.width": 0.8, "figure.facecolor": SURF, "axes.facecolor": SURF,
                     "xtick.labelsize": 6.6, "ytick.labelsize": 6.6})
CRIT = ("C1", "C2", "C3", "C4", "C5", "C6", "C7")
HEAD = {"C1": "C1\nhot spot\n255.7 C", "C2": "C2\nlumped\n255.7 C", "C3": "C3\nlumped\n150 C",
        "C4": "C4\nhot spot\n138.5 C", "C5": "C5\nlumped\n138.5 C", "C6": "C6\nhot spot\n255.7 C\naged",
        "C7": "C7\nhot spot\n138.5 C\naged"}


def rows_of(name):
    out = []
    p = os.path.join(a.res, name)
    if not os.path.exists(p):
        return out
    for r in csv.DictReader(open(p)):
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


tests = IN.tests()
order = sorted([t for t in tests if t["connection"] == "parallel"], key=lambda t: t["trigger_max_C"]) + \
    sorted([t for t in tests if t["connection"] == "series"], key=lambda t: t["trigger_max_C"])
P = {(r["test"], r["criterion"]): r for r in rows_of("stage7_pertest.csv") if r["contact"] == "central"}
E = [r for r in rows_of("stage7_events.csv") if r["set"] == "event" and r["contact"] == "central"]
fig, axs = plt.subplots(1, 2, figsize=(7.6, 4.3), gridspec_kw={"wspace": 0.17, "width_ratios": [1.35, 1.0]})

# a: the matrix
ax = axs[0]
ncol = 1 + len(CRIT)
nrow = len(order)
for i, t in enumerate(order):
    y = nrow - 1 - i
    txt = f"{t['time_s']:.0f} s" if t["propagated"] else "no"
    ax.add_patch(Rectangle((0, y), 1, 1, facecolor="#d9d8d3" if t["propagated"] else SURF, edgecolor=GRID, lw=0.6))
    ax.text(0.5, y + 0.5, txt, ha="center", va="center", fontsize=5.9, color=INK, fontweight="bold" if t["propagated"] else None)
    for j, c in enumerate(CRIT):
        r = P.get((t["test"], c))
        x = 1 + j
        if r is None:
            ax.add_patch(Rectangle((x, y), 1, 1, facecolor=SURF, edgecolor=GRID, lw=0.6))
            ax.text(x + 0.5, y + 0.5, "", ha="center", va="center")
            continue
        ax.add_patch(Rectangle((x, y), 1, 1, facecolor=FILL[r["class"]], edgecolor=GRID, lw=0.6))
        s = (f"{r['predicted_time_s']:.0f}" if r["predicted_time_s"] >= 9.5 else f"{r['predicted_time_s']:.1f}") \
            if r["predicted"] == "Yes" else "no"
        ax.text(x + 0.5, y + 0.5, s, ha="center", va="center", fontsize=5.9, color=INK if r["predicted"] == "Yes" else INK2)
    ax.text(-0.08, y + 0.5, f"{t['test'][4:]}  {t['trigger_max_C']:.0f} C", ha="right", va="center", fontsize=5.8,
            color=INK2)
ax.axhline(8, color=INK2, lw=0.9)
ax.text(-3.35, 12, "parallel", rotation=90, ha="center", va="center", fontsize=6.2, color=INK2)
ax.text(-3.35, 4, "series", rotation=90, ha="center", va="center", fontsize=6.2, color=INK2)
ax.text(0.5, nrow + 0.15, "Tables\n3 and 4", ha="center", va="bottom", fontsize=5.2, color=INK2, linespacing=1.05)
for j, c in enumerate(CRIT):
    ax.text(1 + j + 0.5, nrow + 0.15, HEAD[c], ha="center", va="bottom", fontsize=5.2, color=INK2, linespacing=1.05)
# counts below
labels = (("hits", "hit"), ("misses", "miss"), ("false alarms", "false alarm"), ("correct rej.", "correct rejection"))
for k, (lab, cls) in enumerate(labels):
    y = -1.0 - 0.75 * k
    ax.text(-0.08, y + 0.35, lab, ha="right", va="center", fontsize=5.6, color=INK2)
    n_meas = {"hit": sum(t["propagated"] for t in order), "miss": None, "false alarm": None,
              "correct rejection": sum(not t["propagated"] for t in order)}[cls]
    if n_meas is not None:
        ax.text(0.5, y + 0.35, f"({n_meas})", ha="center", va="center", fontsize=5.6, color=MUTED)
    for j, c in enumerate(CRIT):
        rs = [P.get((t["test"], c)) for t in order]
        if all(r is not None for r in rs):
            n = sum(r["class"] == cls for r in rs)
            ax.add_patch(Rectangle((1 + j + 0.12, y + 0.05), 0.76, 0.6, facecolor=FILL[cls], edgecolor="none"))
            ax.text(1 + j + 0.5, y + 0.35, f"{n}", ha="center", va="center", fontsize=5.8, color=INK)
ax.set_xlim(-3.6, ncol + 0.05)
ax.set_ylim(-4.0, nrow + 2.6)
ax.axis("off")
ax.text(-3.6, -4.0, "times in s: model from the start of cell 1's release, measured from the trigger's runaway (D34)",
        fontsize=5.2, color=MUTED, va="bottom")
ax.set_title("a", loc="left", fontsize=8.5, fontweight="bold", color=INK, x=0.0)

# b: the event runs
ax = axs[1]
lo, hi = IN.measured()["neighbour_max_propagated_range_C"]
ax.axhspan(lo, hi, color=BAND, zorder=0)
xs = {t["test"]: k for k, t in enumerate(order)}
for t in order:
    x = xs[t["test"]]
    ax.scatter([x], [t["neighbour_max_C"]], s=16, marker="o", zorder=4, facecolor=INK if t["propagated"] else SURF,
               edgecolor=INK, lw=0.9)
off = {"C4": -0.17, "C5": 0.17}
for r in E:
    x = xs[r["test"]] + off[r["criterion"]]
    hol = r["criterion"] == "C5"
    if r["hot_after_C"] is not None:
        ax.scatter([x], [r["hot_after_C"]], s=14, marker="D", zorder=3, facecolor=SURF if hol else ORANGE,
                   edgecolor=ORANGE, lw=0.8)
    if r["lumped_after_C"] is not None:
        ax.scatter([x], [r["lumped_after_C"]], s=14, marker="o", zorder=3, facecolor=SURF if hol else BLUE,
                   edgecolor=BLUE, lw=0.8)
ax.axvline(7.5, ymax=0.85, color=INK2, lw=0.7, ls=(0, (2, 2)))
ax.set_xticks(range(len(order)))
ax.set_xticklabels([t["test"][4:] for t in order], rotation=90, fontsize=5.4)
vals = [v for r in E for v in (r["hot_after_C"], r["lumped_after_C"]) if v is not None]
ymax = max([900.0] + [v for v in vals]) * 1.42
ax.set_ylim(0, ymax)
top = max([900.0] + vals)
ax.set_yticks([250.0 * k for k in range(int(top // 250) + 2)])    # no grid line under the legend
ax.set_xlim(-0.7, len(order) - 0.3)
ax.set_ylabel("Neighbour peak (C)")
ax.text(3.5, ymax * 0.985, "parallel", ha="center", va="top", fontsize=6.0, color=INK2)
ax.text(11.5, ymax * 0.985, "series", ha="center", va="top", fontsize=6.0, color=INK2)
ax.grid(True, axis="y", color=GRID, lw=0.7)
ax.set_axisbelow(True)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
hs = [Line2D([], [], ls="", marker="o", mfc=INK, mec=INK, ms=3.8, label="measured, propagated"),
      Line2D([], [], ls="", marker="o", mfc=SURF, mec=INK, ms=3.8, label="measured, not propagated"),
      Line2D([], [], ls="", marker="D", mfc=ORANGE, mec=ORANGE, ms=3.4, label="hot spot, event at C4"),
      Line2D([], [], ls="", marker="D", mfc=SURF, mec=ORANGE, ms=3.4, label="hot spot, event at C5"),
      Line2D([], [], ls="", marker="o", mfc=BLUE, mec=BLUE, ms=3.6, label="lumped, event at C4"),
      Line2D([], [], ls="", marker="o", mfc=SURF, mec=BLUE, ms=3.6, label="lumped, event at C5")]
ax.legend(handles=hs, loc="upper center", bbox_to_anchor=(0.5, 0.95), ncol=3, fontsize=5.0, frameon=False,
          handletextpad=0.25, columnspacing=0.7)
ax.set_title("b", loc="left", fontsize=8.5, fontweight="bold", color=INK)
fig.subplots_adjust(left=0.01, right=0.99, top=0.96, bottom=0.13)
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(OUT, f"stage7_figure.{ext}"), dpi=300)
print("wrote stage7_figure.png and .pdf")
