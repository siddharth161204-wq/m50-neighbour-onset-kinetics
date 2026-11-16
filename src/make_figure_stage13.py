"""Stage 13's figure (results/stage13_figure.pdf and .png), from the Stage 13 results tables.

(a) PT_Exp1's local threshold f*(C1) against the delivery's duration: the closed form A1, the cross-section model A2
    and the resolved runs' brackets (new, refined and archived).
(b) The delivered energy at the whole-cell threshold against the trigger's body energy at the three contacts: B2 and
    the lumped runs' brackets; inset, T_ign over the 200 posterior draws (the trigger at the neighbour's temperature).
(c) The ratio f*(C2)/f*(C1) for PT_Exp1 against the Fourier number alpha_r tau / a^2, the runs and the reduced
    models' ratio B2/A2, with the three regimes and the manuscript's deliveries.
"""
import csv
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402
import numpy as np                       # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage13_inputs as IN              # noqa: E402

INK, MUTED = "#222222", "#6b6b6b"
C_A1, C_A2, C_RUN = "#2a6fdb", "#e07b00", "#222222"
C_H = {"low": "#2a6fdb", "central": "#7a7a7a", "high": "#c0392b"}


def _rows(name):
    return list(csv.DictReader(open(os.path.join(IN.RES, name))))


def _f(x):
    return None if x in (None, "", "None") else float(x)


def panel_a(ax):
    rows = [r for r in _rows("stage13_skin.csv") if r["test"] == "M50_PT_Exp1" and r["region"] == "half"]
    rows.sort(key=lambda r: float(r["tau_d_s"]))
    tau = np.array([float(r["tau_d_s"]) for r in rows])
    ax.plot(tau, [_f(r["A1_f"]) for r in rows], "-", color=C_A1, lw=1.5, marker="o", ms=4, label="A1, closed form")
    ax.plot(tau, [_f(r["A1_pure_skin_f"]) for r in rows], ":", color=C_A1, lw=1.2, label="A1, pure skin")
    ax.plot(tau, [_f(r["A2_f"]) for r in rows], "-", color=C_A2, lw=1.5, marker="s", ms=4, label="A2, cross-section")
    for r in rows:
        if r.get("res_lo") in (None, ""):
            continue
        lo, hi = float(r["res_lo"]), float(r["res_hi"])
        new = r["res_source"] != "archived (Stage 8)"
        ax.errorbar(float(r["tau_d_s"]), 0.5 * (lo + hi), yerr=0.5 * (hi - lo), fmt="D" if new else "d",
                    color=C_RUN if new else MUTED, ms=5 if new else 4, mfc=C_RUN if new else "white", capsize=3,
                    lw=1.2, zorder=5)
    ax.errorbar([], [], yerr=[], fmt="D", color=C_RUN, ms=5, label="resolved runs (Stage 13)")
    ax.errorbar([], [], yerr=[], fmt="d", color=MUTED, mfc="white", ms=4, label="resolved runs (archived)")
    ax.set_xscale("log")
    ax.set_xlabel("delivery duration tau_d (s)")
    ax.set_ylabel("local threshold f*(C1), PT_Exp1")
    ax.set_title("(a) the local threshold", loc="left", fontsize=10)
    ax.legend(fontsize=7, frameon=False, loc="upper left")


def panel_b(ax):
    rows = [r for r in _rows("stage13_twobody.csv") if abs(float(r["tau_d_s"]) - IN.TAU_TRIGGER) < 1e-6
            and float(r["dE_body_J"]) == 0.0]
    for h in ("low", "central", "high"):
        rr = sorted([r for r in rows if r["h"] == h], key=lambda r: float(r["E_b_J"]))
        Eb = np.array([float(r["E_b_J"]) for r in rr]) / 1e3
        ax.plot(Eb, [float(r["B2_E_J"]) / 1e3 for r in rr], "o", mfc="none", color=C_H[h], ms=5,
                label=f"B2, {h} contact")
        for r in rr:
            if r.get("lum_mid_J") in (None, ""):
                continue
            lo, hi = float(r["lum_lo_J"]) / 1e3, float(r["lum_hi_J"]) / 1e3
            ax.errorbar(float(r["E_b_J"]) / 1e3, 0.5 * (lo + hi), yerr=0.5 * (hi - lo), fmt="s", color=C_H[h],
                        ms=3.5, capsize=2, lw=1)
    ax.errorbar([], [], yerr=[], fmt="s", color=MUTED, ms=3.5, label="lumped runs (brackets)")
    ax.set_xlabel("trigger's body energy E_b (kJ)")
    ax.set_ylabel("delivered energy at the whole-cell threshold (kJ)")
    ax.set_title("(b) the whole-cell threshold", loc="left", fontsize=10)
    ax.legend(fontsize=7, frameon=False, loc="upper right")
    ins = ax.inset_axes([0.12, 0.10, 0.36, 0.33])
    t = [float(r["T_ign_C"]) for r in _rows("stage13_tign.csv") if r["kinetics"] != "mean" and r["trigger"] == "own"
         and r["connection"] == "parallel" and r["T_ign_C"] not in ("", "None")]
    if t:
        ins.hist(t, bins=20, color="#9aa7b8", edgecolor="white", lw=0.5)
        m = [float(r["T_ign_C"]) for r in _rows("stage13_tign.csv") if r["kinetics"] == "mean"
             and r["trigger"] == "own" and r["connection"] == "parallel"][0]
        ins.axvline(m, color=INK, lw=1)
    ins.set_xlabel("T_ign over the draws (C)", fontsize=7)
    ins.tick_params(labelsize=6)
    ins.set_yticks([])


def panel_c(ax):
    rows = _rows("stage13_map.csv")
    fo = np.array([float(r["fourier"]) for r in rows])
    ax.axvspan(1e-3, 1 / 9, color="#eef3fb", lw=0)
    ax.axvspan(1 / 9, 1.0, color="#f7f7f7", lw=0)
    ax.axvspan(1.0, 10.0, color="#fbf0ee", lw=0)
    for x, name in ((0.035, "skin"), (0.33, "intermediate"), (2.0, "through-heated")):
        ax.text(x, 0.96, name, transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=7, color=MUTED)
    ax.plot(fo, [_f(r["B2_over_A2"]) for r in rows], "-", color=C_A2, lw=1.5, marker="s", ms=4,
            label="reduced models, B2/A2")
    rr = [r for r in rows if r.get("runs_ratio") not in (None, "")]
    ax.plot([float(r["fourier"]) for r in rr], [float(r["runs_ratio"]) for r in rr], "D", color=C_RUN, ms=6,
            label="runs (midpoints)")
    for tau, lab in ((10.0, "10"), (IN.TAU_TRIGGER, "21"), (60.0, "60"), (120.0, "120"), (240.0, "240"),
                     (360.0, "360")):
        ax.axvline(IN.fourier(tau), color="#cccccc", lw=0.6, zorder=0)
        ax.text(IN.fourier(tau), 0.02, lab, transform=ax.get_xaxis_transform(), ha="center", fontsize=6,
                color=MUTED)
    ax.axhline(1.0, color=MUTED, lw=0.8, ls="--")
    ax.set_xscale("log")
    ax.set_xlim(0.02, 3.0)
    ax.set_xlabel("Fourier number alpha_r tau / a^2")
    ax.set_ylabel("f*(C2) / f*(C1), PT_Exp1")
    ax.set_title("(c) the two thresholds' ratio", loc="left", fontsize=10)
    ax.legend(fontsize=7, frameon=False, loc="upper right", bbox_to_anchor=(1.0, 0.9))


def main():
    plt.rcParams.update({"font.size": 8, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                         "ytick.color": MUTED})
    fig, axs = plt.subplots(1, 3, figsize=(13.5, 4.2))
    panel_a(axs[0])
    panel_b(axs[1])
    panel_c(axs[2])
    for ax in axs:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(IN.RES, f"stage13_figure.{ext}"), dpi=200)
    return os.path.join(IN.RES, "stage13_figure.png")


if __name__ == "__main__":
    print(main())
