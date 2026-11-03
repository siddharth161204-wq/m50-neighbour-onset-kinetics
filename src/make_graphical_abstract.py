#!/usr/bin/env python3
"""The graphical abstract for the Journal of The Electrochemical Society (Brief 21, M4), drawn from the results files.

One image in two parts: (left) the whole-cell threshold f*(C2) of the sixteen tests against the trigger's energy, the
propagated tests filled and the others hollow, with the range where the two groups overlap (Fig. 5a's left half);
(right) the one published neighbour history, M50_PT_Exp4's, beside the model's far face with no delivery, the short
delivery at its threshold and a long one (Fig. 7a, simplified). Written to manuscript/submission/GA_two_cell_propagation.png
(300 dpi, 16 by 7 cm) with the one-sentence caption in GA_caption.txt beside it.

Usage: python3 make_graphical_abstract.py
"""
import json, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RES = os.path.join(HERE, "..", "results")
OUT = os.path.join(HERE, "..", "manuscript", "submission")
INK, INK2, MUTED, GRID, AXIS, SURF, BAND = "#0b0b0b", "#52514e", "#77756f", "#e1e0d9", "#b9b8ad", "#ffffff", "#ecebe6"
BLUE, ORANGE = "#2a78d6", "#eb6834"
SQ = (lambda y: np.sqrt(np.clip(y, 0, None)), lambda y: np.square(y))
CAPTION = ("No single fraction of the trigger's ejected energy, delivered to the neighbour, reproduces the sixteen "
           "two-cell tests, and the one published neighbour history follows a short delivery near its threshold "
           "more closely than a long one.")


def tidy(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(AXIS)
    ax.tick_params(colors=INK2, length=3)
    ax.grid(True, axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)


def main():
    import stage10_inputs as IN10
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.labelcolor": INK2,
                         "xtick.labelsize": 9.5, "ytick.labelsize": 9.5})
    v = json.load(open(os.path.join(RES, "stage8_verdicts.json")))["thresholds"]
    fig = plt.figure(figsize=(16 / 2.54, 7.0 / 2.54))
    ax = fig.add_axes([0.125, 0.18, 0.34, 0.67])
    ax.set_yscale("function", functions=SQ)
    rng = {}
    for grp in (True, False):
        g = [r for r in v if r["propagated"] == grp]
        rng[grp] = (min(0.0 if r["fC2"]["status"] == "zero" else r["fC2"]["lo"] for r in g),
                    max(0.0 if r["fC2"]["status"] == "zero" else r["fC2"]["hi"] for r in g))
    ov = (max(rng[True][0], rng[False][0]), min(rng[True][1], rng[False][1]))
    ax.axhspan(ov[0], ov[1], color=BAND, lw=0, zorder=0)
    ax.text(6.0, 0.0006, "range shared by\nboth groups", ha="left", va="bottom", fontsize=8.5, color=INK2,
            linespacing=1.1)
    for r in v:
        fs = r["fC2"]
        y = 0.0 if fs["status"] == "zero" else 0.5 * (fs["lo"] + fs["hi"])
        ax.scatter([r["E_b_J"] / 1e3], [y], s=30, marker="s", facecolor=BLUE if r["propagated"] else SURF,
                   edgecolor=BLUE, lw=1.1, zorder=3, clip_on=False)
    ax.set_yticks([0, 0.01, 0.05, 0.1, 0.2, 0.5])
    ax.set_yticklabels(["0", "0.01", "0.05", "0.1", "0.2", "0.5"])
    ax.set_ylim(0, 0.55)
    ax.set_xlim(5, 57)
    ax.set_xlabel("Trigger energy (kJ)")
    ax.set_ylabel("Share of the ejected\nenergy needed", linespacing=1.1)
    tidy(ax)
    hs = [Line2D([], [], ls="", marker="s", mfc=BLUE, mec=BLUE, ms=6, label="propagated"),
          Line2D([], [], ls="", marker="s", mfc=SURF, mec=BLUE, ms=6, label="did not")]
    ax.legend(handles=hs, loc="upper right", frameon=False, handletextpad=0.2, borderaxespad=0.1)
    ax.set_title("Each test needs a different share", fontsize=10.5, color=INK, loc="left", pad=6)

    hsc = json.load(open(os.path.join(RES, "stage10_history_scores.json")))["part_a"]
    ax = fig.add_axes([0.6, 0.18, 0.38, 0.67])
    tm, Tm, _ = IN10.history("a")
    tm, Tm = np.array(tm), np.array(Tm)
    keep = tm <= 290.0
    for key, col, ls, lab in (("none_hcentral", MUTED, (0, (3, 2)), "no delivery"),
                              ("con240_C2_hcentral", ORANGE, "-", "long delivery"),
                              ("tri21_C2_lo_hcentral", BLUE, "-", "short delivery")):
        z = np.load(os.path.join(RES, "stage10_series", hsc[key]["id"] + ".npz"))
        ax.plot(z["probe_t"], z["probe_away"] - 273.15, color=col, ls=ls, lw=1.5, zorder=3, label=lab)
    ax.plot(tm[keep], Tm[keep], color=INK, lw=1.8, zorder=5, label="measured")
    ax.set_xlim(0, 290)
    ax.set_ylim(20, 260)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Neighbour surface (°C)")
    tidy(ax)
    ax.legend(loc="upper left", frameon=False, handlelength=1.8, handletextpad=0.4, borderaxespad=0.1,
              labelspacing=0.25, fontsize=9)
    ax.set_title("The one published history", fontsize=10.5, color=INK, loc="left", pad=6)
    os.makedirs(OUT, exist_ok=True)
    png = os.path.join(OUT, "GA_two_cell_propagation.png")
    fig.savefig(png, dpi=300, facecolor=SURF)
    open(os.path.join(OUT, "GA_caption.txt"), "w").write(CAPTION + "\n")
    print("wrote", png)


if __name__ == "__main__":
    main()
