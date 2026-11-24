"""Figures of the rebuilt manuscript (manuscript/rebuild/, Brief 29), drawn from the results files only.

No figure computes a new quantity: each plots values read from a results file, converted to the units the text uses
(J to kJ, a fraction of a test's ejected energy to an energy by that test's ejected energy, kelvin to degrees
Celsius), or a bracket's midpoint. Every figure carries plain labels; no stage, decision or criterion label of the
archive appears on it.

Colours: the Okabe and Ito set, distinguishable under the common colour-vision deficiencies; every series also has
its own marker or line style and a legend or a direct label, so no identity rests on colour alone.

Writes manuscript/rebuild/figures/fig1.pdf ... fig7.pdf (numbered as the paper cites them since Brief 30: fig2()
draws the thresholds as Figure 3, fig3() why they differ as Figure 4 and fig4() the needs as Figure 2), a PNG of each at 300 dpi and a TIFF of each for submission
(Figure_1.tif ..., at 1,000 dpi, the guides' resolution for line art; the PDFs are vector).

Usage: python3 src/make_rebuild_figures.py
"""
import csv
import json
import math
import os
import re
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
from matplotlib.patches import Circle, Wedge, FancyArrowPatch, Rectangle
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rebuild_brackets as RB                     # noqa: E402
ROOT = os.path.join(HERE, "..")
RES = os.path.join(ROOT, "results")
OUT = os.path.join(ROOT, "manuscript", "rebuild", "figures")
K0 = 273.15

INK, MUTED, GRID = "#222222", "#6b6b6b", "#e6e6e6"
C_LOCAL, C_LUMP, C_RES, C_PURPLE, C_ORANGE, C_SKY = "#D55E00", "#0072B2", "#009E73", "#CC79A7", "#E69F00", "#56B4E9"
LEVEL_C = 255.7

TESTS = ["M50_PT_Exp1", "M50_PT_Exp2", "M50_PT_Exp3", "M50_PT_Exp4", "M50_PP_Exp1", "M50_PP_Exp2", "M50_PP_Exp3",
         "M50_PP_Exp4", "M50_ST_Exp1", "M50_ST_Exp2", "M50_ST_Exp3", "M50_ST_Exp4", "M50_SP_Exp1", "M50_SP_Exp2",
         "M50_SP_Exp3", "M50_SP_Exp4"]


def short(t):
    return t.replace("M50_", "").replace("_", "-")


def style():
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8,
        "legend.fontsize": 7, "xtick.labelsize": 7, "ytick.labelsize": 7,
        "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
        "text.color": INK, "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.7,
        "lines.linewidth": 1.4, "legend.frameon": False, "savefig.dpi": 300, "pdf.fonttype": 42})


def grid(ax, axis="y"):
    ax.grid(True, axis=axis, color=GRID, lw=0.6, zorder=0)
    ax.set_axisbelow(True)


def panel(ax, letter):
    ax.text(-0.12, 1.04, f"({letter})", transform=ax.transAxes, fontsize=9, fontweight="bold", va="bottom")


def save(fig, n):
    os.makedirs(OUT, exist_ok=True)
    base = os.path.join(OUT, f"fig{n}")
    fig.savefig(base + ".pdf")
    fig.savefig(base + ".png", dpi=300)
    fig.savefig(os.path.join(OUT, f"Figure_{n}.tif"), dpi=1000, pil_kwargs={"compression": "tiff_lzw"})
    plt.close(fig)


# ------------------------------------------------------------------------------------------------ the inputs
def read_csv(path):
    with open(path) as fh:
        return list(csv.DictReader(fh))


def fnum(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def tests_table():
    meas = {r["test"]: r for r in read_csv(os.path.join(ROOT, "inputs", "fransson2024", "m50_tests.csv"))}
    trig = {r["test"]: float(r["E_J"]) for r in read_csv(os.path.join(RES, "stage7_triggers.csv")) if r["kind"] == "test"}
    out = {}
    for t in TESTS:
        m = meas[t]
        out[t] = {"connection": m["connection"], "propagated": m["propagated"].strip().lower() == "yes",
                  "time_s": fnum(m["time_to_propagation_s"]), "E_b_J": trig[t],
                  "trigger_max_C": fnum(m["trigger_max_C"]), "neighbour_max_C": fnum(m["neighbour_max_C"])}
    return out


def needs_table():
    return {r["test"]: r for r in read_csv(os.path.join(RES, "stage14_needs.csv"))}


def cross_section():
    return json.load(open(os.path.join(RES, "stage15_cross_section.json")))


def stage15_numbers():
    return json.load(open(os.path.join(RES, "stage15_paper_numbers.json")))


def series(rid):
    z = np.load(os.path.join(RES, "stage15_series", rid + ".npz"))
    return {k: z[k] for k in z.files}


def measured_pt_exp4():
    """PT-Exp4's neighbour thermocouple, read from the supplement's Figure 10 of Fransson et al., every 0.5 s."""
    rows = read_csv(os.path.join(ROOT, "inputs", "fransson2024", "pt_exp4_history.csv"))
    return np.array([float(r["t_s"]) for r in rows]), np.array([float(r["T_neighbour_C"]) for r in rows])


# ------------------------------------------------------------------------------------------------ Figure 1
def fig1():
    """(a) the pair at mid-length and what each neighbour model reads; (b) the three readings in one run."""
    fig = plt.figure(figsize=(7.2, 3.1))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.25], wspace=0.28, left=0.03, right=0.98, bottom=0.14, top=0.9)
    ax = fig.add_subplot(gs[0])
    ax.set_aspect("equal")
    ax.axis("off")
    R = 1.0
    c1, c2 = (-R, 0.25), (R, 0.25)
    ax.add_patch(Circle(c1, R, fc="#f3d9c9", ec=INK, lw=1.0))
    ax.add_patch(Circle(c2, R, fc="#f2f2f2", ec=INK, lw=1.0))
    ax.text(c1[0], c1[1] + 0.32, "trigger", ha="center", va="center", fontsize=7.5)
    ax.text(c1[0], c1[1] - 0.45, "one temperature;\nreleases its\nbody energy\nover 21.4 s", ha="center",
            va="center", fontsize=6.3, color=MUTED, linespacing=1.15)
    # the facing half of the neighbour, where the delivered heat enters
    ax.add_patch(Wedge(c2, R * 1.09, 90, 270, width=0.08, fc=C_LOCAL, ec="none"))
    ax.annotate("delivered heat enters\nthe facing half", (c2[0] - 0.72, c2[1] + 0.78), xytext=(-0.55, 1.5),
                ha="center", va="bottom", fontsize=6.3, color=C_LOCAL,
                arrowprops=dict(arrowstyle="-", color=C_LOCAL, lw=0.6))
    # the contact and its air wedge, within 45 degrees of the line of contact
    ax.add_patch(Wedge(c2, R, 135, 225, width=0.13, fc=C_LUMP, ec="none", alpha=0.55))
    ax.annotate("contact and air wedge,\nwithin 45\u00b0 of the line\nof contact", (c2[0] - 0.83, c2[1] - 0.55),
                xytext=(-0.85, -1.3), fontsize=6.0, color=C_LUMP, ha="center", va="top",
                arrowprops=dict(arrowstyle="-", color=C_LUMP, lw=0.6))
    # symmetry plane of the resolved half model
    ax.plot([-2.1, 2.2], [c2[1], c2[1]], color=MUTED, lw=0.6, ls=(0, (6, 2, 1, 2)))
    # probes at mid-length: facing, side, far face
    for ang, lab, dx, dy, ha in [(180, "contact", 0.12, 0.13, "left"), (90, "side", 0.0, 0.2, "center"),
                                 (0, "far face", 0.12, 0.0, "left")]:
        x = c2[0] + R * math.cos(math.radians(ang))
        y = c2[1] + R * math.sin(math.radians(ang))
        ax.plot(x, y, "o", ms=4.2, mfc="white", mec=INK, mew=0.9, zorder=5)
        ax.text(x + dx, y + dy, lab, fontsize=6.3, ha=ha, va="center")
    ax.text(c2[0] + 0.12, c2[1] - 0.42, "neighbour", ha="center", fontsize=7.5)
    ax.text(c2[0] + 0.7, -1.0, "one temperature (lumped),\nor a resolved field\n(half model, 19,355 nodes)",
            ha="center", va="top", fontsize=6.0, color=MUTED)
    ax.set_xlim(-2.15, 2.65)
    ax.set_ylim(-1.75, 1.85)
    ax.text(-2.1, 1.8, "(a)", fontsize=9, fontweight="bold", va="top")

    # (b) one run: PT-Exp4, 7.4 kJ delivered over 21.4 s
    ax = fig.add_subplot(gs[1])
    s = series("s15_B1_PT_Exp4_s+1")
    ax.plot(s["t"], s["Tmax"] - K0, color=C_LOCAL, lw=1.3, label="resolved neighbour, hottest point")
    ax.plot(s["t_lumped"], s["T_lumped"] - K0, color=C_LUMP, lw=1.3, ls="--", label="lumped neighbour")
    ax.plot(s["mean_step_t"], s["mean_step_T"] - K0, color=C_RES, lw=1.6, label="resolved neighbour, mean")
    ax.plot(s["probe_t"], s["probe_away"] - K0, color=MUTED, lw=1.0, ls=":", label="resolved neighbour, far face")
    ax.axhline(LEVEL_C, color=INK, lw=0.7, ls=(0, (3, 2)))
    ax.text(298, LEVEL_C + 6, "255.7 °C", ha="right", va="bottom", fontsize=6.5, color=INK)
    n = stage15_numbers()["B1"]["M50_PT_Exp4"]["runs"][1]
    for tt, col, lab in [(n["C1_t_s"], C_LOCAL, "hottest point\n%.0f s" % n["C1_t_s"]),
                         (n["lumped_C2_t_s"], C_LUMP, "lumped\n%.0f s" % n["lumped_C2_t_s"]),
                         (n["t_C8_s"], C_RES, "mean\n%.0f s" % n["t_C8_s"])]:
        ax.plot([tt], [LEVEL_C], "o", ms=4, color=col, zorder=6)
        off = {C_LOCAL: (30, 60), C_LUMP: (62, 345), C_RES: (200, 130)}[col]
        ax.annotate(lab, (tt, LEVEL_C), xytext=off, fontsize=6.3, color=col, ha="left", va="center",
                    arrowprops=dict(arrowstyle="-", color=col, lw=0.6))
    ax.set_xlim(0, 300)
    ax.set_ylim(0, 720)                    # head room for the legend above every curve (read 7, D19)
    ax.set_yticks(range(0, 701, 100))
    ax.set_xlabel("Time from the start of the trigger's release (s)")
    ax.set_ylabel("Temperature (°C)")
    ax.set_title("PT-Exp4, 7.4 kJ delivered to the facing half over 21.4 s", loc="left", fontsize=7.5)
    grid(ax)
    ax.legend(loc="upper right", fontsize=6.0, handlelength=1.6, ncol=2, columnspacing=0.9, borderaxespad=0.3)
    ax.text(-0.13, 1.04, "(b)", transform=ax.transAxes, fontsize=9, fontweight="bold", va="bottom")
    save(fig, 1)


# ------------------------------------------------------------------------------------------------ Figure 2
def fig2():
    """The thresholds of the sixteen tests with the 21.4 s delivery: local, lumped, resolved (cross-section, and
    three-dimensional in four tests)."""
    tt = tests_table()
    nd = needs_table()
    xs = {r["test"]: r for r in cross_section()["A2"] if r["shape"] == "tri"}
    b1 = stage15_numbers()["B1"]
    order = sorted(TESTS, key=lambda t: tt[t]["E_b_J"])
    fig, ax = plt.subplots(figsize=(7.2, 3.3), constrained_layout=True)
    x = np.arange(len(order))
    for i, t in enumerate(order):
        (lo1, hi1), (lo2, hi2) = RB.brackets(nd[t])       # the narrowest bracket the archive holds (as Table S3)
        lo1, hi1, lo2, hi2 = lo1 / 1e3, hi1 / 1e3, lo2 / 1e3, hi2 / 1e3
        ax.plot([i - 0.22, i - 0.22], [lo1, hi1], color=C_LOCAL, lw=2.2, solid_capstyle="butt")
        ax.plot(i - 0.22, hi1, marker="v", ms=4.6, color=C_LOCAL, ls="none")
        ax.plot([i, i], [lo2, hi2], color=C_LUMP, lw=2.2, solid_capstyle="butt")
        ax.plot(i, hi2, marker="s", ms=4.0, color=C_LUMP, ls="none")
        ax.plot(i + 0.22, xs[t]["E_star_J"] / 1e3, marker="o", ms=4.6, mfc="white", mec=C_RES, mew=1.3, ls="none")
        if t in b1:
            br = b1[t]["bracket"]
            ax.plot([i + 0.22, i + 0.22], [br["lo_J"] / 1e3, br["hi_J"] / 1e3], color=C_RES, lw=2.6,
                    solid_capstyle="butt")
            ax.plot(i + 0.22, br["mid_J"] / 1e3, marker="D", ms=4.2, color=C_RES, ls="none")
    ax.set_xticks(x)
    ax.set_xticklabels([short(t) + ("\n\u25cf" if tt[t]["propagated"] else "\n\u25cb") for t in order], fontsize=6.8)
    for lab, t in zip(ax.get_xticklabels(), order):
        lab.set_color(INK if tt[t]["propagated"] else MUTED)
    ax.text(1.0, -0.2, "\u25cf propagated in the test   \u25cb did not", transform=ax.transAxes, ha="right",
            va="top", fontsize=6.8)
    ax2 = ax.secondary_xaxis("top")
    ax2.set_xticks(x)
    ax2.set_xticklabels(["%.1f" % (tt[t]["E_b_J"] / 1e3) for t in order], fontsize=6.6)
    ax2.set_xlabel("Trigger's body energy fitted to the measured trigger peak (kJ)", fontsize=7)
    ax.set_ylabel("Threshold: least energy delivered\nover 21.4 s to the facing half (kJ)")
    ax.set_ylim(-0.3, 14)
    ax.set_xlim(-0.6, len(order) - 0.4)
    grid(ax)
    h = [Line2D([], [], color=C_LOCAL, marker="v", lw=2.2, ms=4.6, label="hottest point reaches 255.7 °C (bracket)"),
         Line2D([], [], color=C_LUMP, marker="s", lw=2.2, ms=4.0, label="lumped neighbour reaches 255.7 °C (bracket)"),
         Line2D([], [], color=C_RES, marker="o", mfc="white", lw=0, ms=4.6,
                label="resolved neighbour's mean reaches 255.7 °C: reactive cross-section"),
         Line2D([], [], color=C_RES, marker="D", lw=2.6, ms=4.2,
                label="the same, three-dimensional model (bracket)")]
    ax.legend(handles=h, loc="upper right", fontsize=7.0, ncol=1)
    save(fig, 3)   # the thresholds: Figure 3 in Brief 30's order of the results


# ------------------------------------------------------------------------------------------------ Figure 3
def fig3():
    """Why: (a) the local threshold against the delivery's Fourier number, the resolved runs against the conduction
    models; (b) the lumped threshold against a shift of the trigger's body energy; (c) the ignition temperature over
    the kinetic posterior; (d) that spread beside the shift of the rate laws the resolved neighbour needs."""
    fig, axs = plt.subplots(2, 2, figsize=(7.2, 5.0), constrained_layout=True)
    # (a)
    ax = axs[0, 0]
    skin = [r for r in read_csv(os.path.join(RES, "stage13_skin.csv")) if r["test"] == "M50_PT_Exp1" and r["region"] == "half"]
    Ee = {r["test"]: float(r["E_e_J"]) for r in read_csv(os.path.join(RES, "stage8_thresholds.csv"))}["M50_PT_Exp1"]
    fo = np.array([float(r["fourier"]) for r in skin])
    a2 = np.array([float(r["A2_f"]) for r in skin]) * Ee / 1e3
    a1 = np.array([fnum(r["A1_f"]) or np.nan for r in skin]) * Ee / 1e3
    ax.plot(fo, a2, color=INK, lw=1.2, label="conduction model of the mid-length cross-section")
    ax.plot(fo, a1, color=MUTED, lw=1.0, ls="--", label="conduction into a semi-infinite skin")
    for r in skin:
        lo, hi = fnum(r["res_lo"]), fnum(r["res_hi"])
        if lo is None or hi is None:
            continue
        f = float(r["fourier"])
        ax.plot([f, f], [lo * Ee / 1e3, hi * Ee / 1e3], color=C_LOCAL, lw=3.0, solid_capstyle="butt")
        ax.plot(f, 0.5 * (lo + hi) * Ee / 1e3, marker="v", color=C_LOCAL, ms=4.2, ls="none")
    ax.plot([], [], color=C_LOCAL, marker="v", lw=3.0, ms=4.2, label="resolved model with the reaction (bracket)")
    ax.set_xscale("log")
    ax.set_xlabel("Fourier number of the delivery, \u03b1\u03c4/a\u00b2")
    ax.set_ylabel("Local threshold of PT-Exp1 (kJ)")
    for f, lab in [(0.025, "5 s"), (0.107, "21.4 s"), (0.6, "120 s"), (1.8, "360 s")]:
        ax.text(f, 0.45, lab, fontsize=6, color=MUTED, ha="center")
    ax.set_ylim(0, 21)
    grid(ax)
    ax.legend(loc="upper left", fontsize=6.2)
    panel(ax, "a")
    # (b) the lumped threshold against a shift of the trigger's body energy
    ax = axs[0, 1]
    p10 = json.load(open(os.path.join(RES, "stage13_scorecard.json")))["P10"]["cases"]
    nd = needs_table()
    cols = {"M50_PP_Exp3": C_LUMP, "M50_ST_Exp2": C_PURPLE, "M50_PT_Exp3": C_ORANGE}
    marks = {"M50_PP_Exp3": "s", "M50_ST_Exp2": "^", "M50_PT_Exp3": "o"}
    for c in p10:
        t = c["test"]
        lo0, hi0 = float(nd[t]["threshold_C2_lo_J"]) / 1e3, float(nd[t]["threshold_C2_hi_J"]) / 1e3
        m2, p2 = 0.5 * sum(c["minus2"]) / 1e3, 0.5 * sum(c["plus2"]) / 1e3
        ax.plot([-2, 2], [m2, p2], color=cols[t], lw=1.2)
        for x0, br in [(-2, c["minus2"]), (2, c["plus2"])]:
            ax.plot([x0, x0], [br[0] / 1e3, br[1] / 1e3], color=cols[t], lw=2.4, solid_capstyle="butt")
            ax.plot(x0, 0.5 * (br[0] + br[1]) / 1e3, marker=marks[t], color=cols[t], ls="none", ms=4.3)
        ax.plot([0, 0], [lo0, hi0], color=cols[t], lw=1.0, alpha=0.6)
        ax.plot(0, 0.5 * (lo0 + hi0), marker=marks[t], mfc="white", mec=cols[t], ls="none", ms=4.3)
        dy = {"M50_PP_Exp3": 0.55, "M50_ST_Exp2": -0.45, "M50_PT_Exp3": 0.0}[t]
        ax.text(2.3, p2 + dy, "%s: %.0f J less\nper kJ more" % (short(t), c["slope_J_per_kJ"]), fontsize=6.0,
                color=cols[t], va="center")
    ax.set_xlabel("Shift of the trigger's body energy (kJ)")
    ax.set_ylabel("Lumped threshold over 21.4 s (kJ)")
    ax.set_xticks([-2, 0, 2])
    ax.set_xlim(-2.6, 4.9)
    ax.set_ylim(0, 10)
    grid(ax)
    ax.text(0.22, 0.985, "filled: searched with the body energy shifted by 2 kJ;\nhollow: the bracket at the fitted energy",
            transform=ax.transAxes, fontsize=5.9, color=MUTED, va="top")
    panel(ax, "b")
    # (c) the ignition temperature over the posterior
    ax = axs[1, 0]
    rows = [r for r in read_csv(os.path.join(RES, "stage13_tign.csv"))
            if r["trigger"] == "own" and r["connection"] == "parallel" and r["kinetics"] != "mean"]
    tig = np.array([float(r["T_ign_C"]) for r in rows])
    s13 = json.load(open(os.path.join(RES, "stage13_paper_numbers.json")))["scorecard"]["P7"]
    ax.hist(tig, bins=np.arange(213.5, 224.6, 0.5), color=C_LUMP, alpha=0.75, edgecolor="white", lw=0.4)
    ax.plot([s13["mean_C"]] * 2, [0, 44.5], color=INK, lw=1.0)
    ax.axvspan(s13["p2.5_C"], s13["p97.5_C"], color=C_LUMP, alpha=0.12, lw=0)
    ax.text(s13["mean_C"], 45.5, "posterior mean, %.1f \u00b0C" % s13["mean_C"], fontsize=6.4, ha="center",
            va="bottom")
    ax.text(s13["p2.5_C"] + 0.1, 57.5, "central 95 %%: %.1f to %.1f \u00b0C" % (s13["p2.5_C"], s13["p97.5_C"]),
            fontsize=6.4, color=C_LUMP, va="top")
    ax.set_xlim(213.5, 224.5)
    ax.set_ylim(0, 58)
    ax.set_ylabel("Kinetic draws")
    ax.set_xlabel("Ignition temperature of the lumped neighbour (\u00b0C)")
    grid(ax)
    panel(ax, "c")
    # (d) PT-Exp4's resolved neighbour under 5.04 kJ over 21.4 s: the peak of its mean against the shift of every rate
    # law, and with no shift under the four kinetic draws and the aged SEI (none of which runs it away)
    ax = axs[1, 1]
    b4 = stage15_numbers()["B4"]
    sh = sorted(b4["shift_runs"], key=lambda r: r["shift_K"])
    mean0 = json.load(open(os.path.join(RES, "stage15_readings.json")))["1"]["PT_Exp4"]["mean_peak_C"]
    others = [r["peak_mean_C"] for r in b4["draws"].values()] + [b4["aged"]["peak_mean_C"]]
    ax.axhline(LEVEL_C, color=INK, lw=0.7, ls=(0, (3, 2)))
    ax.text(16.6, LEVEL_C - 1.5, "255.7 \u00b0C: runaway", fontsize=6.4, ha="right", va="top")
    ax.plot([0, 0], [min(others), max(others)], color=MUTED, lw=4.0, alpha=0.55, solid_capstyle="butt", zorder=2)
    ax.annotate("no shift, the four kinetic draws and the aged SEI:\n%.1f to %.1f \u00b0C, none runs away"
                % (min(others), max(others)), (0.25, 0.5 * (min(others) + max(others))), xytext=(2.0, 205.0),
                fontsize=6.4, color=MUTED, va="center", arrowprops=dict(arrowstyle="-", lw=0.6, color=MUTED))
    xs = [0.0] + [r["shift_K"] for r in sh]
    ys = [mean0] + [r["peak_mean_C"] for r in sh]
    ax.plot(xs, ys, color=C_RES, lw=0.8, alpha=0.6, zorder=3)
    ax.plot([0.0], [mean0], marker="x", color=C_RES, ms=5.5, mew=1.3, ls="none", zorder=4)
    for r in sh:
        ax.plot(r["shift_K"], r["peak_mean_C"], marker="o" if r["C8"] else "x", color=C_RES, ms=5.5,
                mfc="white" if r["C8"] else C_RES, mew=1.3, ls="none", zorder=4)
    ax.text(0.3, 275.5, "PT-Exp4, 5.04 kJ over 21.4 s: \u00d7 no resolved runaway; \u25cb runaway", fontsize=6.4,
            color=C_RES, va="top")
    ax.set_xlim(-0.8, 22.5)
    ax.set_ylim(182, 276)
    ax.set_xticks([0, 5, 10, 15, 17.5, 20])
    ax.set_xticklabels(["0", "5", "10", "15", "17.5", "20"])
    ax.set_xlabel("Shift of the temperature in every rate law (K)")
    ax.set_ylabel("Peak of the resolved mean (\u00b0C)")
    grid(ax)
    panel(ax, "d")
    save(fig, 4)   # why the thresholds differ: Figure 4


# ------------------------------------------------------------------------------------------------ Figure 4
NONE_Y = 0.1                                                        # Fig. 4b: the row of the zero needs


def fig4():
    """What each neighbour model needs at the measured times (the nine propagated tests, four deliveries): the lumped
    neighbour, the resolved neighbour by the reactive cross-section, and the resolved neighbour in three dimensions
    where step 16 searched it (results/stage16_scorecard.json); and the energy read from each non-propagated test's
    measured maximum."""
    tt = tests_table()
    rows = read_csv(os.path.join(RES, "stage15_table.csv"))
    nd = needs_table()
    s16p = os.path.join(RES, "stage16_scorecard.json")
    s16 = json.load(open(s16p)) if os.path.exists(s16p) else {"N": [], "X": []}
    d3 = {(r["test"], r["delivery"]): r for r in s16["N"] + s16["X"] if r["status"] == "done"}
    deliveries = [("21.39 s pulse", "o", "pulse over 21.4 s"), ("120 s constant power", "s", "120 s"),
                  ("240 s constant power", "^", "240 s"), ("360 s constant power", "D", "360 s")]
    prop = sorted([t for t in TESTS if tt[t]["propagated"]], key=lambda t: tt[t]["time_s"])
    nonp = [t for t in TESTS if not tt[t]["propagated"]]
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.8), constrained_layout=True, gridspec_kw={"width_ratios": [2.1, 1.0]})
    ax = axs[0]

    def letter(x, y, status, col):
        """t: the time reproduced only within the search's resolution of the threshold; b: interpolated."""
        if status in ("threshold", "bracketed"):
            ax.annotate({"threshold": "t", "bracketed": "b"}[status], (x, y), xytext=(0, 4.2),
                        textcoords="offset points", ha="center", va="bottom", fontsize=6.2, color=col,
                        fontweight="bold")

    for i, t in enumerate(prop):
        for j, (dname, mk, _) in enumerate(deliveries):
            r = next((r for r in rows if r["test"] == t and r["delivery"] == dname), None)
            if r is None:
                continue
            dx = -0.3 + 0.2 * j
            e2 = fnum(r["C2_E_by_t_J"])
            e8 = fnum(r["C8_xs_E_by_t_J"])
            if e2 is not None and r["C2_status"] in ("matched", "threshold", "bracketed"):
                y2 = max(e2, 1.0) / 1e3
                ax.plot(i + dx, y2, marker=mk, ms=4.2, mfc=C_LUMP, mec=C_LUMP, ls="none")
                letter(i + dx, y2, r["C2_status"], C_LUMP)
            if e8 is not None and r["C8_xs_status"] in ("matched", "threshold"):
                ax.plot(i + dx - 0.035, e8 / 1e3, marker=mk, ms=4.4, mfc="white", mec=C_RES, mew=1.1, ls="none")
                letter(i + dx - 0.035, e8 / 1e3, r["C8_xs_status"], C_RES)
            q = d3.get((t, dname))
            if q is not None:
                lo, hi = q["lo_by_t_J"] / 1e3, q["hi_by_t_J"] / 1e3
                ax.plot([i + dx + 0.05] * 2, [lo, hi], color=C_RES, lw=1.4, solid_capstyle="butt")
                ax.plot(i + dx + 0.05, 0.5 * (lo + hi), marker=mk, ms=4.0, mfc=C_RES, mec=C_RES, ls="none")
    ax.set_yscale("log")
    ax.set_ylim(0.12, 100)
    ax.set_xticks(range(len(prop)))
    ax.set_xticklabels(["%s\n%.0f s" % (short(t), tt[t]["time_s"]) for t in prop], fontsize=6.6)
    ax.set_ylabel("Energy delivered to the facing half\nby the runaway (kJ)")
    ax.set_title("Propagated tests, in order of the measured time", loc="left", fontsize=7.5)
    grid(ax)
    h = [Line2D([], [], color=C_LUMP, marker="o", ls="none", ms=4.2, label="lumped neighbour"),
         Line2D([], [], color=C_RES, marker="o", mfc="white", ls="none", ms=4.4, mew=1.1,
                label="resolved: reactive cross-section"),
         Line2D([], [], color=C_RES, marker="o", ls="-", lw=1.4, ms=4.0,
                label="resolved: three-dimensional (bracket)")]
    h += [Line2D([], [], color=MUTED, marker=mk, ls="none", ms=4.2, label=lab) for _, mk, lab in deliveries]
    h += [Line2D([], [], color="none", marker="$t$", ms=6.0, mec=INK, mfc=INK, ls="none",
                 label="time met only within the search's resolution"),
          Line2D([], [], color="none", marker="$b$", ms=6.0, mec=INK, mfc=INK, ls="none",
                 label="interpolated between two runs")]
    fig.legend(handles=h, loc="outside lower center", fontsize=6.3, ncol=3, frameon=False)
    panel(ax, "a")
    ax = axs[1]
    for i, t in enumerate(nonp):
        v = fnum(nd[t]["need_21s_lo_J"])
        expl = "exploratory" in nd[t]["reading_21s"]
        zero = v is None or v == 0
        y = NONE_Y if zero else v / 1e3                              # a need of zero sits in its own row, "none"
        ax.plot(i, y, marker=("v" if zero else "o"), ms=4.6, mfc=("white" if expl else INK), mec=INK, ls="none")
    ax.axhline(0.15, color=MUTED, lw=0.6, ls=(0, (1, 2)))
    ax.text(0.03, 0.135, "below the line: with no delivery the\nfar face already peaks above the\nmaximum",
            transform=ax.transAxes, ha="left", va="bottom", fontsize=6.3, color=MUTED)
    ax.set_yscale("log")
    ax.set_ylim(0.075, 100)
    ax.set_yticks([NONE_Y, 1, 10, 100])
    ax.set_yticklabels(["none", "1", "10", "100"])
    ax.yaxis.set_minor_locator(matplotlib.ticker.FixedLocator(
        [m * 10.0 ** k for k in (-1, 0, 1) for m in range(2, 10) if m * 10.0 ** k > 0.15]))
    ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_xticks(range(len(nonp)))
    ax.set_xticklabels([short(t) for t in nonp], rotation=60, fontsize=6.8, ha="right")
    ax.set_ylabel("Energy over 21.4 s that puts the far face's\npeak at the measured maximum (kJ)", fontsize=7)
    ax.set_title("Tests that did not propagate", loc="left", fontsize=7.5)
    grid(ax)
    ax.text(0.97, 0.64, "hollow: maxima that may\nnot be the neighbour's\nsurface", transform=ax.transAxes,
            fontsize=6.3, ha="right", va="center", color=MUTED)
    panel(ax, "b")
    save(fig, 2)   # what the tests need: Figure 2, the paper's lead result


# ------------------------------------------------------------------------------------------------ Figure 5
def fig5():
    """PT-Exp4's neighbour: the measured surface record against the model's far face, and the mean."""
    n15 = stage15_numbers()
    b1 = {r["id"]: r for r in n15["B1"]["M50_PT_Exp4"]["runs"]}
    runs = [("s15_rep_size_PT_Exp4_tri21", "5.0 kJ over 21.4 s (no runaway; the lumped neighbour's at 216 s)", C_LUMP, "-"),
            ("s15_B1_PT_Exp4_s-1", "6.7 kJ over 21.4 s (no runaway)" if not b1["s15_B1_PT_Exp4_s-1"]["C8"] else
             "6.7 kJ over 21.4 s", C_RES, "--"),
            ("s15_B1_PT_Exp4_s+1", "7.4 kJ over 21.4 s (runaway at %.0f s)" % b1["s15_B1_PT_Exp4_s+1"]["t_C8_s"],
             C_RES, "-"),
            ("s15_B3_PT_Exp4_hold12.5W", "5.0 kJ pulse, then 12.5 W", C_PURPLE, "-"),
            ("s15_B2_PT_Exp4_con240_f0.050000", "6.2 kJ over 240 s", C_ORANGE, "-")]
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.35), constrained_layout=True)
    tm, Tm = measured_pt_exp4()
    for rid, lab, col, ls in runs:
        p = os.path.join(RES, "stage15_series", rid + ".npz")
        if not os.path.exists(p):
            continue
        s = series(rid)
        axs[0].plot(s["probe_t"], s["probe_away"] - K0, color=col, ls=ls, lw=1.2, label=lab)
        if "mean_step_T" in s:
            axs[1].plot(s["mean_step_t"], s["mean_step_T"] - K0, color=col, ls=ls, lw=1.2, label=lab)
    axs[0].plot(tm, Tm, color=INK, lw=1.6, label="measured (Fransson et al.)")
    fj = n15["B1"]["M50_PT_Exp4"]["runs"][1]["far_jump"]
    axs[0].plot([fj["t_s"]], [fj["T_C"]], marker="o", ms=4.5, color=C_RES, zorder=6)
    hj = [r for r in n15["B3b"]["runs"] if r["id"] == "s15_B3_PT_Exp4_hold12.5W"][0]["far_jump"]
    axs[0].plot([hj["t_s"]], [hj["T_C"]], marker="o", ms=4.5, color=C_PURPLE, zorder=6)
    axs[0].annotate("model's jump begins\n%.1f °C at %.0f s" % (fj["T_C"], fj["t_s"]), (fj["t_s"], fj["T_C"]),
                    xytext=(95, 292), fontsize=6.2, color=C_RES, arrowprops=dict(arrowstyle="-", lw=0.6, color=C_RES))
    axs[0].plot([271.5], [197.3], marker="o", ms=4.5, color=INK, zorder=6)
    axs[0].annotate("measured jump\n197.3 °C at 271.5 s", (271.5, 197.3), xytext=(200, 95), fontsize=6.2,
                    arrowprops=dict(arrowstyle="-", lw=0.6, color=INK))
    axs[0].set_xlim(0, 332)
    axs[0].set_ylim(20, 320)
    axs[0].set_xlabel("Time (s)")
    axs[0].set_ylabel("Surface temperature at mid-length (°C)")
    axs[0].set_title("Far face of the model, and the measured thermocouple", loc="left", fontsize=7.5)
    grid(axs[0])
    panel(axs[0], "a")
    axs[1].axhline(LEVEL_C, color=INK, lw=0.7, ls=(0, (3, 2)))
    axs[1].text(330, LEVEL_C + 4, "255.7 °C", ha="right", va="bottom", fontsize=6.3)
    axs[1].set_xlim(0, 400)
    axs[1].set_ylim(20, 320)
    axs[1].set_xlabel("Time (s)")
    axs[1].set_ylabel("Resolved neighbour's mean temperature (°C)")
    axs[1].set_title("Mean temperature of the resolved neighbour", loc="left", fontsize=7.5)
    grid(axs[1])
    ha, la = axs[0].get_legend_handles_labels()                     # panel a: the measured record only
    axs[0].legend([ha[la.index("measured (Fransson et al.)")]], ["measured (Fransson et al.)"], loc="lower right",
                  fontsize=6.0)
    h, l = axs[1].get_legend_handles_labels()                       # panel b: the five model runs, its own lines
    fig.legend(h, l, loc="outside lower center", ncol=3, fontsize=6.0, frameon=False)
    panel(axs[1], "b")
    save(fig, 5)


# ------------------------------------------------------------------------------------------------ Figure 6
def fig6():
    """What each path can deliver within 21.4 s and in total, against what the neighbour models need."""
    b = read_csv(os.path.join(RES, "stage14_bounds_corrected.csv"))
    get = lambda p, w: next((fnum(r["upper_J"]) for r in b if r["path"] == p and r["window_s"] == w), None)
    paths = [("A1", "radiation from a vent's jet or flame"), ("A2", "gas beside the neighbour"),
             ("A3", "a breach's jet facing the neighbour"), ("A4", "solids and melt on the facing half"),
             ("A5", "conduction through the holder"), ("A6", "the neighbour's own discharge (parallel)")]
    fig, ax = plt.subplots(figsize=(7.2, 3.3), constrained_layout=True)
    y = np.arange(len(paths))[::-1]
    # the bands read from the files: the lumped needs with the pulse and the resolved needs under the four shapes,
    # after the strong triggers (results/stage15_table.csv, every propagated test but ST_Exp3), and the Databank's
    # median and largest ejected energy (results/stage14_inputs.csv)
    t15 = [r for r in read_csv(os.path.join(RES, "stage15_table.csv")) if r["test"] != "M50_ST_Exp3"]
    lum = [float(r["C2_E_by_t_J"]) / 1e3 for r in t15 if r["delivery"] == "21.39 s pulse"]
    res = [float(r["C8_xs_E_by_t_J"]) / 1e3 for r in t15 if r["C8_xs_E_by_t_J"]]
    inp = {r["key"]: float(r["value"]) for r in read_csv(os.path.join(RES, "stage14_inputs.csv"))
           if r["key"] in ("db_Eej_median", "db_Eej_max")}
    bands = [(min(lum), max(lum), C_LUMP, 0.13, "lumped needs, strong triggers, 21.4 s pulse"),
             (min(res), max(res), C_RES, 0.16, "resolved needs, strong triggers, four shapes"),
             (inp["db_Eej_median"] / 1e3, inp["db_Eej_max"] / 1e3, INK, 0.10, "ejected energy measured, median to largest")]
    for lo, hi, col, al, lab in bands:
        ax.axvspan(lo, hi, color=col, alpha=al, lw=0, zorder=0)
    for yy, (p, lab) in zip(y, paths):
        u21, ut = get(p, "21.39"), get(p, "total")
        if u21 is None:
            ax.text(0.115, yy, "not determinable; energy conservation alone caps it at 247.3 kJ", va="center",
                    fontsize=6.8, color=MUTED)
        else:
            ax.barh(yy + 0.17, u21 / 1e3, height=0.3, left=0.1, color=C_SKY, edgecolor="none", zorder=2)
            ax.barh(yy - 0.17, ut / 1e3, height=0.3, left=0.1, color="#9e9e9e", edgecolor="none", zorder=2)
            ax.text(u21 / 1e3 * 1.08, yy + 0.17, "%.1f" % (u21 / 1e3), va="center", fontsize=6.8, zorder=3)
            ax.text(ut / 1e3 * 1.08, yy - 0.17, "%.1f" % (ut / 1e3), va="center", fontsize=6.8, color=MUTED, zorder=3)
    # a flame held on the vent's axis: the finer scan of the bounds' independent read (about 849 J)
    txt = open(os.path.join(RES, "stage14_independent_read.md")).read()
    axial = float(re.search(r"at most about (\d+) J \(1\.11 %\)", txt).group(1))
    ax.plot([axial / 1e3], [y[0] + 0.17], marker="|", ms=11, color=C_LOCAL, mew=1.8, zorder=4)
    ax.annotate("flame held on the vent's axis", (axial / 1e3, y[0] + 0.3), xytext=(0.3, y[0] + 0.62),
                fontsize=6.6, color=C_LOCAL, arrowprops=dict(arrowstyle="-", lw=0.6, color=C_LOCAL))
    ax.set_xscale("log")
    ax.set_xlim(0.1, 600)
    ax.set_ylim(-0.6, len(paths) - 0.2)
    ax.set_yticks(y)
    ax.set_yticklabels([lab for _, lab in paths], fontsize=7.2)
    ax.set_xlabel("Energy delivered to the neighbour's facing half (kJ)")
    h = [Rectangle((0, 0), 1, 1, color=C_SKY, label="upper bound within 21.4 s"),
         Rectangle((0, 0), 1, 1, color="#9e9e9e", label="upper bound in total")]
    h += [Rectangle((0, 0), 1, 1, color=col, alpha=al + 0.1, label=lab) for _, _, col, al, lab in bands]
    ax.legend(handles=h, loc="upper center", bbox_to_anchor=(0.42, -0.17), ncol=2, fontsize=6.8)
    grid(ax, "x")
    save(fig, 6)


# ------------------------------------------------------------------------------------------------ Figure 7
def fig7():
    """The reactive cross-section against the three-dimensional model: (a) the time the mean reaches 255.7 C and (b)
    its peak in the archived runs (results/stage15_cross_section.json, A1_rows); (c) the thresholds searched in three
    dimensions with the pulse (step 15, results/stage15_paper_numbers.json; step 16, results/stage16_scorecard.json);
    (d) the needs with the pulse at the measured times (step 16)."""
    d = cross_section()
    rows = d["A1_rows"]
    s16p = os.path.join(RES, "stage16_scorecard.json")
    s16 = json.load(open(s16p)) if os.path.exists(s16p) else None
    fig, axs = plt.subplots(2, 2, figsize=(7.2, 5.4), constrained_layout=True)
    axs = axs.ravel()
    par = lambda r: r["test"].split("_")[1] in ("PT", "PP")
    ax = axs[0]
    for r in rows:
        if r["C8_3d"] and r["C8_xs"]:
            mk = "o" if r["shape"] == "tri" else "s"
            col = C_PURPLE if par(r) else C_RES
            ax.plot(r["t_C8_3d_s"], r["t_C8_xs_s"], marker=mk, ms=3.2, mfc="white", mec=col, mew=0.9, ls="none")
    lim = [0, 900]
    ax.plot(lim, lim, color=MUTED, lw=0.7)
    ax.set_xlim(0, 350)
    ax.set_ylim(0, 350)
    ax.set_xlabel("Three-dimensional model (s)")
    ax.set_ylabel("Reactive cross-section (s)")
    ax.set_title("Time the mean reaches 255.7 °C", loc="left", fontsize=7.2)
    grid(ax, "both")
    h = [Line2D([], [], marker="o", mfc="white", mec=C_RES, ls="none", ms=3.6, label="series tests"),
         Line2D([], [], marker="o", mfc="white", mec=C_PURPLE, ls="none", ms=3.6, label="parallel tests"),
         Line2D([], [], marker="o", color=MUTED, mfc="white", ls="none", ms=3.6, label="pulse over 21.4 s"),
         Line2D([], [], marker="s", color=MUTED, mfc="white", ls="none", ms=3.6, label="constant power"),
         Line2D([], [], marker="^", color=MUTED, mfc="white", ls="none", ms=3.6, label="no delivery (b)")]
    ax.legend(handles=h, loc="upper left", fontsize=6.2, title="(a) and (b)", title_fontsize=6.2)
    panel(ax, "a")
    ax = axs[1]
    for r in rows:
        if not r["C8_3d"] and not r["C8_xs"] and r["mean_peak_3d_C"] is not None:
            mk = "o" if r["shape"] == "tri" else ("s" if r["shape"] == "con" else "^")
            col = C_PURPLE if par(r) else C_RES
            ax.plot(r["mean_peak_3d_C"], r["mean_peak_xs_C"], marker=mk, ms=3.2, mfc="white", mec=col, mew=0.9,
                    ls="none")
    ax.plot([50, 260], [50, 260], color=MUTED, lw=0.7)
    ax.set_xlim(50, 260)
    ax.set_ylim(50, 260)
    ax.set_xlabel("Three-dimensional model (°C)")
    ax.set_ylabel("Reactive cross-section (°C)")
    ax.set_title("Peak of the mean, runs without runaway", loc="left", fontsize=7.2)
    grid(ax, "both")
    panel(ax, "b")
    ax = axs[2]
    b1 = stage15_numbers()["B1"]
    xs = {r["test"]: r for r in d["A2"] if r["shape"] == "tri"}
    th = [(t, v["bracket"]["lo_J"], v["bracket"]["hi_J"]) for t, v in b1.items()]
    if s16 and s16["T"].get("status") == "done":
        th.append((s16["T"]["test"], s16["T"]["lo_J"], s16["T"]["hi_J"]))
    tt = tests_table()
    th = sorted(th, key=lambda x: -tt[x[0]]["E_b_J"])
    for i, (t, lo, hi) in enumerate(th):
        ax.plot([i, i], [lo / 1e3, hi / 1e3], color=C_RES, lw=3, solid_capstyle="butt")
        ax.plot(i, 0.5 * (lo + hi) / 1e3, marker="D", color=C_RES, ms=4, ls="none")
        ax.plot(i + 0.18, xs[t]["E_star_J"] / 1e3, marker="o", mfc="white", mec=INK, ms=4.4, ls="none")
    ax.set_xticks(range(len(th)))
    ax.set_xticklabels([short(t) for t, _, _ in th], fontsize=6.3)
    ax.set_ylabel("Resolved threshold over 21.4 s (kJ)")
    ax.set_ylim(0, 13)
    ax.set_xlim(-0.5, len(th) - 0.3)
    ax.set_title("Thresholds, in order of the trigger's energy", loc="left", fontsize=7.2)
    h = [Line2D([], [], color=C_RES, marker="D", lw=3, ms=4, label="three-dimensional (bracket)"),
         Line2D([], [], color=INK, marker="o", mfc="white", lw=0, ms=4.4, label="reactive cross-section")]
    ax.legend(handles=h, loc="upper left", fontsize=6.2)
    grid(ax)
    panel(ax, "c")
    ax = axs[3]
    if s16:
        N = [r for r in s16["N"] if r["status"] == "done"]
        N = sorted(N, key=lambda r: tt[r["test"]]["time_s"])
        for i, r in enumerate(N):
            ax.plot([i, i], [r["lo_J"] / 1e3, r["hi_J"] / 1e3], color=C_RES, lw=3, solid_capstyle="butt")
            ax.plot(i, r["mid_J"] / 1e3, marker="D", color=C_RES, ms=4, ls="none")
            ax.plot(i + 0.18, r["xs_E_by_t_J"] / 1e3, marker="o", mfc="white", mec=INK, ms=4.4, ls="none")
            ax.plot(i - 0.18, r["lumped_E_by_t_J"] / 1e3, marker="s", color=C_LUMP, ms=3.8, ls="none")
        ax.set_xticks(range(len(N)))
        ax.set_xticklabels(["%s\n%.0f s" % (short(r["test"]), tt[r["test"]]["time_s"]) for r in N], fontsize=6.0)
    ax.set_ylabel("Need with the 21.4 s pulse (kJ)")
    ax.set_ylim(0, 9)
    ax.set_title("Needs at the measured times, strong triggers", loc="left", fontsize=7.2)
    h = [Line2D([], [], color=C_RES, marker="D", lw=3, ms=4, label="resolved, three-dimensional (bracket)"),
         Line2D([], [], color=INK, marker="o", mfc="white", lw=0, ms=4.4, label="resolved, reactive cross-section"),
         Line2D([], [], color=C_LUMP, marker="s", lw=0, ms=3.8, label="lumped")]
    ax.legend(handles=h, loc="lower left", fontsize=6.0, ncol=1)
    grid(ax)
    panel(ax, "d")
    save(fig, 7)


def main():
    style()
    fig1()
    fig2()
    fig3()
    fig4()
    fig5()
    fig6()
    fig7()
    print("figures written to", os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
