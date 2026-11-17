"""Stage 15's figure (DECISIONS.md D178): M50_PT_Exp4's resolved neighbour under four deliveries, (a) its mean
temperature and (b) its far face against time, with the measured history in (b).

The runs: the short delivery (5,045 J over 21.39 s, Stage 10's run repeated to 332 s, D172), B1's two runs at the
ends of its bracket (the threshold delivery: the one that reaches C8 and the one just below it), B3 (b)'s pulse and
hold, and B2's 240 s delivery of 6,209 J. Colours are the Okabe and Ito set (safe under the common colour-vision
deficiencies); each run keeps its colour in both panels, and line styles separate the two threshold runs.

Writes results/stage15_figure.pdf and .png.
"""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage15_inputs as IN              # noqa: E402
import stage15_partb as PB               # noqa: E402

INK, MUTED, GRID = "#222222", "#6b6b6b", "#e4e4e4"
COL = {"short": "#0072B2", "hi": "#D55E00", "lo": "#D55E00", "hold": "#009E73", "con240": "#CC79A7",
       "measured": "#222222"}


def _series(rid):
    z = np.load(os.path.join(IN.SERIES, rid + ".npz"))
    return {"t_mean": z["mean_step_t"], "mean": z["mean_step_T"] - IN.K0 if "mean_step_T" in z.files else None,
            "t_far": z["probe_t"], "far": z["probe_away"] - IN.K0}


def runs():
    recs = PB.load()
    out = []
    out.append(("short", "5.0 kJ over 21.4 s (no C8)", "s15_rep_size_PT_Exp4_tri21", "-"))
    st, _, br = PB.b1_state("M50_PT_Exp4", recs)
    if br:
        lo, hi = recs[br["lo_id"]], recs[br["hi_id"]]
        out.append(("lo", f"{lo['E_delivered_J'] / 1e3:.1f} kJ over 21.4 s (no C8)", br["lo_id"], "--"))
        out.append(("hi", f"{hi['E_delivered_J'] / 1e3:.1f} kJ over 21.4 s (C8)", br["hi_id"], "-"))
    st, _, res = PB.b3_state(recs)
    if res:
        rid = res.get("id") or res.get("id_hi")
        P = res.get("P_W") or res.get("P_hi_W")
        out.append(("hold", f"5.0 kJ pulse, then {P:g} W", rid, "-"))
    r2 = recs.get(PB.b2_spec(0.05)["id"])
    if r2:
        out.append(("con240", "6.2 kJ over 240 s", r2["id"], "-"))
    return out


def main():
    plt.rcParams.update({"font.size": 8, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                         "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.0), constrained_layout=True)
    rr = runs()
    for key, label, rid, ls in rr:
        s = _series(rid)
        if s["mean"] is not None:
            axs[0].plot(s["t_mean"], s["mean"], ls, color=COL[key], lw=1.3, label=label)
        axs[1].plot(s["t_far"], s["far"], ls, color=COL[key], lw=1.3, label=label)
    tm, Tm = IN.measured_history()
    axs[1].plot(tm, Tm, ":", color=COL["measured"], lw=1.4, label="measured (M50_PT_Exp4)")
    for ax in axs:
        ax.axhline(IN.T_LEVEL_C, color=MUTED, lw=0.8, ls=(0, (4, 3)))
        ax.axvline(IN.T_PROP_FIG_S, color=MUTED, lw=0.6, ls=":")
        ax.grid(True, color=GRID, lw=0.5)
        ax.set_xlim(0, 600)
        ax.set_xlabel("time from the trigger's runaway (s)")
    axs[0].set_ylim(20, 320)
    axs[1].set_ylim(20, 320)
    axs[0].set_ylabel("resolved neighbour's mean temperature (C)")
    axs[1].set_ylabel("far face (C)")
    axs[0].text(590, IN.T_LEVEL_C + 4, "255.7 C", ha="right", va="bottom", fontsize=7, color=MUTED)
    axs[0].set_title("(a) the mean: C8 where it reaches 255.7 C", fontsize=8, loc="left", color=INK)
    axs[1].set_title("(b) the far face, with the measured history", fontsize=8, loc="left", color=INK)
    axs[1].legend(loc="upper right", fontsize=6.5, frameon=False)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(IN.RES, f"stage15_figure.{ext}"), dpi=200)
    print("written", [r[2] for r in rr])


if __name__ == "__main__":
    main()
