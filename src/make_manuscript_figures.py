#!/usr/bin/env python3
"""The manuscript's eight figures (Brief 20, M4), each from the results files, at 300 dpi.

Every figure is drawn at the width of the manuscript's text block (elsarticle's preprint, 390 pt = 5.42 in; about an
Elsevier 1.5-column width, 140 mm), so that every font is at least 7 pt as printed. Colours: the hot spot (C1)
orange, the lumped neighbour (C2) blue, the far face and f_max aqua, the one exploratory set violet, the measured
tests black; every series also has its own marker or line style, so no reading rests on colour alone. The palette's
three hues and its greys pass the colour-vision checks of the plotting guide used (worst pair in deuteranopia,
protanopia and tritanopia above the 8-unit target).

F1 the geometry and the kinetics; F2 the onset lead over the draws (Stage 3); F3 the passive runs against the tests
(Stage 6); F4 the sixteen tests against the seven criteria (Stage 7); F5 the thresholds and the times at a common
fraction (Stage 8); F6 the induction curves and the fractions read from the times and peaks (Stage 9); F7 the one
history and the held-out scores (Stage 10); F8 Stage 11's bands (once its results files exist).

Usage: python3 make_manuscript_figures.py [--res ../results] [--out ../manuscript/figures] [--only 1,2,...]
"""
import argparse, csv, json, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle, Circle, Arc, FancyArrowPatch
from matplotlib.ticker import NullLocator

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

INK, INK2, MUTED, GRID, AXIS, SURF, BAND = "#0b0b0b", "#52514e", "#77756f", "#e1e0d9", "#b9b8ad", "#ffffff", "#ecebe6"
BLUE, ORANGE, AQUA, VIOLET, RED = "#2a78d6", "#eb6834", "#1baf7a", "#6250d6", "#e34948"
W_IN = 390.0 / 72.27                       # the text block's width in inches
FS, FS_TICK, FS_SMALL, FS_LETTER = 8.0, 7.5, 7.0, 9.0
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": FS, "axes.edgecolor": AXIS, "axes.labelcolor": INK2,
                     "axes.labelsize": FS, "xtick.color": INK2, "ytick.color": INK2, "axes.linewidth": 0.8,
                     "xtick.major.width": 0.8, "ytick.major.width": 0.8, "figure.facecolor": SURF,
                     "axes.facecolor": SURF, "xtick.labelsize": FS_TICK, "ytick.labelsize": FS_TICK,
                     "legend.fontsize": FS_SMALL, "pdf.fonttype": 42, "ps.fonttype": 42, "savefig.dpi": 300})
SQ = (lambda y: np.sqrt(np.clip(y, 0, None)), lambda y: np.square(y))


def tidy(ax, axis="both"):
    ax.grid(True, axis=axis, which="major", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)


def letter(ax, s, x=-0.02, y=1.02):
    ax.text(x, y, s, transform=ax.transAxes, fontsize=FS_LETTER, fontweight="bold", color=INK, ha="right", va="bottom")


def rows_of(res, name):
    out = []
    for r in csv.DictReader(open(os.path.join(res, name))):
        for k, v in list(r.items()):
            if v in ("", "None"):
                r[k] = None
            elif v in ("True", "False"):
                r[k] = v == "True"
            else:
                try:
                    r[k] = float(v)
                except (ValueError, TypeError):
                    pass
        out.append(r)
    return out


def save(fig, out, name):
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(out, f"{name}.{ext}"), dpi=300)
    plt.close(fig)
    print("wrote", name)


# ------------------------------------------------------------------------------------------------------------ F1
def fig1(res, out):
    import v12_model as V
    LP = V.LP
    import stage10_inputs as IN10
    R = LP.D_CELL / 2 * 1e3
    fig = plt.figure(figsize=(W_IN, 2.75))
    ax = fig.add_axes([0.0, 0.03, 0.43, 0.9])
    ax.set_aspect("equal")
    ax.axis("off")
    c1, c2 = (-R, 0.0), (R, 0.0)
    ax.add_patch(Circle(c1, R, facecolor="#f4f3ef", edgecolor=INK2, lw=1.0))
    ax.add_patch(Circle(c2, R, facecolor=SURF, edgecolor=INK2, lw=1.0))
    for rr in np.linspace(0.18, 0.92, 7):                   # the roll's layers, schematic
        ax.add_patch(Circle(c2, rr * R, facecolor="none", edgecolor=GRID, lw=0.6))
    # the facing half of the neighbour's can, through which the delivery enters
    ax.add_patch(Arc(c2, 2 * R + 0.9, 2 * R + 0.9, theta1=90, theta2=270, color=RED, lw=2.4))
    for th in (-60, -25, 25, 60):
        a = np.deg2rad(180 + th)
        p0 = (c2[0] + (R + 4.2) * np.cos(a), c2[1] + (R + 4.2) * np.sin(a))
        p1 = (c2[0] + (R + 1.1) * np.cos(a), c2[1] + (R + 1.1) * np.sin(a))
        ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=6, color=RED, lw=0.9))
    # the symmetry plane of the resolved half model
    ax.plot([-2 * R - 1.5, 2 * R + 1.5], [0, 0], color=MUTED, lw=0.7, ls=(0, (6, 2, 1, 2)))
    # the three thermocouple nodes at mid-length, on the half model's side
    for name, lab, dx, dy, ha in (("facing", "facing, 0.3°", 1.2, -1.8, "left"),
                                   ("side", "side, 88.3°", 0.6, 1.7, "center"),
                                   ("away", "far face, 180°", -0.9, 1.9, "right")):
        th = np.deg2rad(IN10.NODES[name]["theta_deg"])
        x, y = c2[0] - R * np.cos(th), c2[1] + R * np.sin(th)
        ax.plot([x], [y], marker="o", ms=4.6, mfc=AQUA, mec=INK, mew=0.6, zorder=5)
        ax.text(x + dx, y + dy, lab, fontsize=FS_SMALL, color=INK, ha=ha, va="center")
    ax.text(c1[0], c1[1] + 3.6, "trigger\n(cell 1)", ha="center", va="center", fontsize=FS_SMALL, color=INK)
    ax.text(c1[0] - 0.6, c1[1] - 4.4, "lumped;\n$E_\\mathrm{b}$ over\n21.39 s", ha="center", va="center",
            fontsize=FS_SMALL, color=INK2)
    ax.text(c2[0] + 0.4, c2[1] - 5.6, "neighbour\n(cell 2)", ha="center", va="center", fontsize=FS_SMALL, color=INK)
    ax.text(0.0, -R - 3.6, "line of contact", ha="center", va="top", fontsize=FS_SMALL, color=INK2)
    ax.plot([0, 0], [-R - 3.3, -0.6], color=INK2, lw=0.6)
    ax.text(c2[0] - 2.0, R + 5.8, "facing half: $f\\,E_\\mathrm{e}$ over 21.39 s", ha="center", va="bottom",
            fontsize=FS_SMALL, color=RED)
    ax.plot([-2 * R, -2 * R + 10], [-R - 7.8] * 2, color=INK, lw=1.2)
    ax.text(-2 * R + 5, -R - 8.6, "10 mm", ha="center", va="top", fontsize=FS_SMALL, color=INK2)
    ax.set_xlim(-2 * R - 2, 2 * R + 6)
    ax.set_ylim(-R - 11, R + 9)
    letter(ax, "a", x=0.04, y=0.97)

    ax = fig.add_axes([0.56, 0.17, 0.41, 0.76])
    b = rows_of(res, "manuscript_kinetics_band.csv")
    T = np.array([r["T_C"] for r in b])
    sets = (("anode_electrolyte", "anode-electrolyte", INK, "-"),
            ("cathode", "NCM811 cathode", VIOLET, "-"),
            ("separator", "separator (absorbed)", AQUA, (0, (4, 1.6))))
    for g, lab, col, ls in sets:
        sgn = -1.0 if g == "separator" else 1.0
        m = sgn * np.array([r[f"{g}_mean"] for r in b])
        lo = sgn * np.array([r[f"{g}_p2.5"] for r in b])
        hi = sgn * np.array([r[f"{g}_p97.5"] for r in b])
        lo, hi = np.minimum(lo, hi), np.maximum(lo, hi)
        ax.fill_between(T, np.clip(lo, 1e-4, None), np.clip(hi, 1e-4, None), color=col, alpha=0.16, lw=0)
        ax.plot(T, np.where(m > 1e-4, m, np.nan), color=col, lw=1.3, ls=ls, label=lab)
    q_on = 0.15 / 60.0 * LP.CP_CELL                          # 0.15 K/min at the cell's specific heat, W/kg
    ax.axhline(q_on, color=MUTED, lw=0.7, ls=(0, (1, 1.5)))
    ax.text(30, q_on * 1.25, "0.15 K/min", fontsize=FS_SMALL, color=INK2, va="bottom")
    ax.set_yscale("log")
    ax.set_ylim(1e-3, 5e3)
    ax.set_xlim(25, 352)
    ax.set_xticks([50, 100, 150, 200, 250, 300])
    ax.set_xlabel("Temperature in a 5 K/min ramp (°C)")
    ax.set_ylabel("Heat release rate (W/kg of cell)")
    tidy(ax)
    ax.legend(loc="upper left", frameon=False, handlelength=1.6, borderaxespad=0.05, labelspacing=0.25)
    letter(ax, "b")
    save(fig, out, "fig1")


# ------------------------------------------------------------------------------------------------------------ F2
def fig2(res, out):
    LV, HEADLINE, GS = "0.15Kpm", "two_E33223_tau30_G0.5", [0.05, 0.1, 0.2, 0.5]

    def num(v):
        return None if v in ("", "None", None) else float(v)

    on = {}
    for r in csv.DictReader(open(os.path.join(res, "stage3a_onsets.csv"))):
        on[(int(r["draw"]), r["case"], r["history"])] = num(r[f"t_{LV}_s"])
    draws = sorted({k[0] for k in on})
    bc = list(csv.DictReader(open(os.path.join(res, "stage3bc_onsets.csv"))))
    s1 = {r["case"]: r for r in json.load(open(os.path.join(res, "onset_results.json")))["cases"]}
    LK = np.array([on[(d, HEADLINE, "lumped")] - on[(d, HEADLINE, "hottest_node")] for d in draws
                   if on[(d, HEADLINE, "lumped")] is not None and on[(d, HEADLINE, "hottest_node")] is not None])

    def leads_bc(kind):
        o = []
        for r in bc:
            if (kind == "thermal") != (int(r["kinetic_draw"]) == 0):
                continue
            h, l = num(r[f"hottest_node_t_{LV}_s"]), num(r[f"lumped_t_{LV}_s"])
            if h is not None and l is not None:
                o.append(l - h)
        return np.array(o)

    LT, LC = leads_bc("thermal"), leads_bc("combined")
    mean_lead = s1[HEADLINE][f"lumped_t_{LV}_s"] - s1[HEADLINE][f"hottest_node_t_{LV}_s"]
    fig, axs = plt.subplots(1, 2, figsize=(W_IN, 2.55), gridspec_kw={"wspace": 0.42, "width_ratios": [1.12, 1.0]})
    ax = axs[0]
    bins = np.arange(0, np.ceil(max(LK.max(), LT.max(), LC.max()) / 2) * 2 + 2, 2.0)
    w = lambda x: np.full(x.size, 100.0 / x.size)
    ax.hist(LC, bins=bins, weights=w(LC), histtype="stepfilled", color=BAND, ec="none", zorder=1)
    ax.hist(LC, bins=bins, weights=w(LC), histtype="step", color=INK2, lw=0.8, zorder=2)
    ax.hist(LK, bins=bins, weights=w(LK), histtype="step", color=INK, lw=1.4, zorder=3)
    ax.hist(LT, bins=bins, weights=w(LT), histtype="step", color=MUTED, lw=1.2, ls=(0, (3, 2)), zorder=4)
    ax.axvline(mean_lead, color=ORANGE, lw=1.0, ls=(0, (1, 1.2)), zorder=5)
    ax.legend(handles=[Line2D([], [], color=INK, lw=1.4, label=f"kinetic ({LK.size})"),
                       Line2D([], [], color=MUTED, lw=1.2, ls=(0, (3, 2)), label=f"thermal ({LT.size})"),
                       Patch(facecolor=BAND, edgecolor=INK2, lw=0.8, label=f"both ({LC.size})"),
                       Line2D([], [], color=ORANGE, lw=1.0, ls=(0, (1, 1.2)), label="posterior mean")],
              loc="upper right", frameon=False, handlelength=1.8, borderaxespad=0.1, labelspacing=0.3)
    ax.set_xlim(0, bins[-1])
    ax.set_xlabel("Lead of the hottest node (s)")
    ax.set_ylabel("Share of draws per 2 s (%)")
    tidy(ax)
    letter(ax, "a")
    ax = axs[1]
    for hist, col, mk, lab in (("lumped", BLUE, "o", "lumped node"), ("hottest_node", ORANGE, "^", "hottest node")):
        med, p_lo, p_hi, ref = [], [], [], []
        for g in GS:
            case = f"two_E33223_tau30_G{g:g}"
            v = np.array([1e9 if on[(d, case, hist)] is None else on[(d, case, hist)] for d in draws])
            q = np.percentile(v, [2.5, 50, 97.5])
            p_lo.append(min(q[0], 900.0)); med.append(min(q[1], 900.0)); p_hi.append(min(q[2], 900.0))
            ref.append(s1[case][f"{hist}_t_{LV}_s"])
        ax.fill_between(GS, p_lo, p_hi, color=col, alpha=0.18, lw=0, zorder=1)
        ax.plot(GS, med, color=col, lw=1.4, zorder=2, label=f"{lab}, median")
        ax.scatter(GS, [np.nan if r is None else r for r in ref], marker=mk, s=20, facecolor=SURF, edgecolor=col,
                   lw=1.1, zorder=3)
    ax.axhline(900.0, color=MUTED, lw=0.8, ls=(0, (3, 2)), zorder=0)
    ax.text(0.5, 900.0 * 0.82, "end of run", color=INK2, fontsize=FS_SMALL, va="top", ha="right")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xticks(GS); ax.set_xticklabels([f"{int(g * 1000)}" for g in GS]); ax.xaxis.set_minor_locator(NullLocator())
    ax.set_ylim(3, 1500)
    ax.set_xlabel("Busbar conductance (mW/K)")
    ax.set_ylabel("Onset at 0.15 K/min (s)")
    ax.legend(handles=[Line2D([], [], color=BLUE, lw=1.4, marker="o", mfc=SURF, ms=4, label="lumped node"),
                       Line2D([], [], color=ORANGE, lw=1.4, marker="^", mfc=SURF, ms=4, label="hottest node")],
              loc="lower left", frameon=False, borderaxespad=0.1)
    tidy(ax)
    letter(ax, "b")
    fig.subplots_adjust(left=0.1, right=0.99, top=0.93, bottom=0.17)
    save(fig, out, "fig2")
    return {"leads": [int(LK.size), int(LT.size), int(LC.size)], "mean_lead_s": mean_lead}


# ------------------------------------------------------------------------------------------------------------ F3
def fig3(res, out):
    import stage6_inputs as IN
    LO, HI = IN.WINDOW_S
    M = IN.measured()
    A = [r for r in rows_of(res, "stage6_crossings.csv") if r["set"] == "grid"]
    B = rows_of(res, "stage6_matched.csv")
    fig = plt.figure(figsize=(W_IN, 5.15))
    ax = fig.add_axes([0.2, 0.615, 0.77, 0.345])
    ax.axvspan(LO, HI, color=BAND, zorder=0)
    clocks = [("lumped", "lumped", BLUE), ("away", "far face", AQUA), ("mean", "resolved mean", VIOLET),
              ("hot", "hot spot", ORANGE)]
    dy = {"low": -0.24, "central": 0.0, "high": 0.24}
    for k, (c, label, col) in enumerate(clocks):
        n_cross = n_in = n_none = 0
        for r in A:
            t = r[f"{c}_t_cross_s"]
            if t is None:
                n_none += 1
                continue
            n_cross += 1
            n_in += LO <= t <= HI
            ax.scatter([t], [k + dy[r["h"]]], s=13, marker="o" if r["connection"] == "series" else "s",
                       facecolor=col if r["tau"] == 30.0 else SURF, edgecolor=col, lw=0.8, zorder=3)
        txt = (f"{n_in} of {n_cross} in window" + (f"; {n_none} never" if n_none else "")) if n_cross \
            else f"none of {n_none}"
        ax.text(408, k + 0.33, txt, ha="right", va="bottom", fontsize=FS_SMALL, color=INK2)
    mt = M["times_to_propagation_s"]
    ax.scatter(mt, [len(clocks)] * len(mt), s=14, color=INK, zorder=4, lw=0)
    ax.text(408, len(clocks) + 0.33, f"{len(mt)} of 16 propagated", ha="right", va="bottom", fontsize=FS_SMALL,
            color=INK2)
    ax.set_yticks(range(len(clocks) + 1))
    ax.set_yticklabels([c[1] for c in clocks] + ["tests"])
    ax.set_xlim(0, 410)
    ax.set_ylim(-0.6, len(clocks) + 0.85)
    ax.set_xlabel("First crossing of 150 °C (s)")
    tidy(ax, "x")
    ax.legend(handles=[Line2D([], [], ls="", marker="o", mfc=INK2, mec=INK2, ms=3.8, label="series, 30 s"),
                       Line2D([], [], ls="", marker="s", mfc=SURF, mec=INK2, ms=3.8, label="parallel; hollow 10 s")],
              loc="upper left", bbox_to_anchor=(0.0, 0.97), frameon=False, handletextpad=0.2, borderaxespad=0.1)
    letter(ax, "a", x=-0.2)
    ax = fig.add_axes([0.13, 0.08, 0.84, 0.43])
    ax.axvspan(*M["trigger_max_range_C"], color=BAND, zorder=0)
    for t, r in M["by_test"].items():
        prop = r["propagated"] == "Yes"
        ax.scatter([float(r["trigger_max_C"])], [float(r["neighbour_max_C"])], s=17, marker="o", zorder=5,
                   facecolor=INK if prop else SURF, edgecolor=INK, lw=0.9)
    t1_5 = {}
    for r in A:
        t1_5[r["id"]] = json.load(open(os.path.join(res, "v12_runs", r["id"] + ".json")))["T1max_C"]
    sets = [("two-cell study's, 33.2 kJ", MUTED,
             [(t1_5[r["id"]], r["away_peak_C"], r["hot_peak_C"], False) for r in A])]
    for name, label, col in (("body", "tests' durations, 33.2 kJ", ORANGE),
                             ("total", "with ejecta, 107.0 kJ", VIOLET)):
        rs = [r for r in B if r["set"] == name]
        sets.append((label, col, [(r["T1max_C"], r["away_peak_C"], r["hot_peak_C"], r["hot_t_255_7_s"] is not None)
                                  for r in rs]))
    for label, col, pts in sets:
        for x, y_away, y_hot, reached in pts:
            if reached:
                ax.scatter([x], [255.7], s=16, marker="^", facecolor=col, edgecolor=col, lw=0.6, zorder=3)
                continue
            ax.plot([x, x], [y_away, y_hot], color=col, lw=0.6, alpha=0.6, zorder=2)
            ax.scatter([x], [y_away], s=10, marker="o", facecolor=SURF, edgecolor=col, lw=0.8, zorder=3)
            ax.scatter([x], [y_hot], s=11, marker="D", facecolor=col, edgecolor=col, lw=0.6, zorder=3)
    ax.axhline(150, color=INK2, lw=0.7, ls=(0, (4, 3)))
    ax.axhline(255.7, color=INK2, lw=0.7, ls=(0, (1, 2)))
    ax.text(1590, 160, "150 °C", ha="right", va="bottom", fontsize=FS_SMALL, color=INK2)
    ax.text(1590, 268, "255.7 °C", ha="right", va="bottom", fontsize=FS_SMALL, color=INK2)
    ax.set_xlim(100, 1600)
    ax.set_ylim(0, 860)
    ax.set_xlabel("Trigger's peak (°C)")
    ax.set_ylabel("Neighbour's peak (°C)")
    tidy(ax)
    hs = [Line2D([], [], ls="", marker="o", mfc=INK, mec=INK, ms=4, label="tests, propagated"),
          Line2D([], [], ls="", marker="o", mfc=SURF, mec=INK, ms=4, label="tests, not propagated")]
    hs += [Line2D([], [], ls="-", lw=0.8, color=col, marker="D", ms=3.4, label=label) for label, col, _ in sets]
    hs += [Line2D([], [], ls="", marker="o", mfc=SURF, mec=INK2, ms=3.6, label="model, far face"),
           Line2D([], [], ls="", marker="D", mfc=INK2, mec=INK2, ms=3.4, label="model, hot spot"),
           Line2D([], [], ls="", marker="^", mfc=INK2, mec=INK2, ms=4, label="hot spot reaches 255.7 °C")]
    ax.legend(handles=hs, loc="upper right", frameon=False, handlelength=1.4, ncol=1, borderaxespad=0.1,
              labelspacing=0.3)
    letter(ax, "b", x=-0.08)
    save(fig, out, "fig3")


# ------------------------------------------------------------------------------------------------------------ F4
def fig4(res, out):
    import stage7_inputs as IN
    FILL = {"hit": "#cfe0f6", "correct rejection": "#eef4fc", "false alarm": "#fbd9c9", "miss": "#f6cfe0"}
    CRIT = ("C1", "C2", "C3", "C4", "C5", "C6", "C7")
    HEAD = {"C1": "C1\nhot spot\n255.7", "C2": "C2\nlumped\n255.7", "C3": "C3\nlumped\n150",
            "C4": "C4\nhot spot\n138.5", "C5": "C5\nlumped\n138.5", "C6": "C6\nhot spot\n255.7\naged",
            "C7": "C7\nhot spot\n138.5\naged"}
    tests = IN.tests()
    order = sorted([t for t in tests if t["connection"] == "parallel"], key=lambda t: t["trigger_max_C"]) + \
        sorted([t for t in tests if t["connection"] == "series"], key=lambda t: t["trigger_max_C"])
    P = {(r["test"], r["criterion"]): r for r in rows_of(res, "stage7_pertest.csv") if r["contact"] == "central"}
    fig = plt.figure(figsize=(W_IN, 5.0))
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    nrow = len(order)
    for i, t in enumerate(order):
        y = nrow - 1 - i
        txt = f"{t['time_s']:.0f} s" if t["propagated"] else "no"
        ax.add_patch(Rectangle((0, y), 1, 1, facecolor="#d9d8d3" if t["propagated"] else SURF, edgecolor=GRID, lw=0.6))
        ax.text(0.5, y + 0.5, txt, ha="center", va="center", fontsize=FS_SMALL, color=INK,
                fontweight="bold" if t["propagated"] else None)
        for j, c in enumerate(CRIT):
            r = P[(t["test"], c)]
            x = 1 + j
            ax.add_patch(Rectangle((x, y), 1, 1, facecolor=FILL[r["class"]], edgecolor=GRID, lw=0.6))
            s = (f"{r['predicted_time_s']:.0f}" if r["predicted_time_s"] >= 9.5 else f"{r['predicted_time_s']:.1f}") \
                if r["predicted"] == "Yes" else "no"
            ax.text(x + 0.5, y + 0.5, s, ha="center", va="center", fontsize=FS_SMALL,
                    color=INK if r["predicted"] == "Yes" else INK2)
        ax.text(-0.1, y + 0.5, f"{t['test'][4:]}  {t['trigger_max_C']:.0f} °C", ha="right", va="center",
                fontsize=FS_SMALL, color=INK2)
    ax.plot([-2.85, 1 + len(CRIT)], [8, 8], color=INK2, lw=0.9)
    ax.text(-3.0, 12, "parallel", rotation=90, ha="center", va="center", fontsize=FS_SMALL, color=INK2)
    ax.text(-3.0, 4, "series", rotation=90, ha="center", va="center", fontsize=FS_SMALL, color=INK2)
    ax.text(0.5, nrow + 0.12, "tests", ha="center", va="bottom", fontsize=FS_SMALL, color=INK2)
    for j, c in enumerate(CRIT):
        ax.text(1 + j + 0.5, nrow + 0.12, HEAD[c], ha="center", va="bottom", fontsize=FS_SMALL, color=INK2,
                linespacing=1.0)
    labels = (("hits", "hit"), ("misses", "miss"), ("false alarms", "false alarm"), ("correct rejections", "correct rejection"))
    for k, (lab, cls) in enumerate(labels):
        y = -1.05 - 0.8 * k
        ax.text(-0.1, y + 0.35, lab, ha="right", va="center", fontsize=FS_SMALL, color=INK2)
        n_meas = {"hit": sum(t["propagated"] for t in order), "correct rejection": sum(not t["propagated"] for t in order)}
        if cls in n_meas:
            ax.text(0.5, y + 0.35, f"({n_meas[cls]})", ha="center", va="center", fontsize=FS_SMALL, color=INK2)
        for j, c in enumerate(CRIT):
            n = sum(P[(t["test"], c)]["class"] == cls for t in order)
            ax.add_patch(Rectangle((1 + j + 0.1, y + 0.03), 0.8, 0.64, facecolor=FILL[cls], edgecolor="none"))
            ax.text(1 + j + 0.5, y + 0.35, f"{n}", ha="center", va="center", fontsize=FS_SMALL, color=INK)
    ax.set_xlim(-3.35, 1 + len(CRIT) + 0.05)
    ax.set_ylim(-4.2, nrow + 2.25)
    ax.axis("off")
    save(fig, out, "fig4")


# ------------------------------------------------------------------------------------------------------------ F5
def fig5(res, out):
    MARK = {"C1": "o", "C2": "s", "C3": "^"}
    COL = {"C1": ORANGE, "C2": BLUE, "C3": AQUA}
    v = json.load(open(os.path.join(res, "stage8_verdicts.json")))
    card = json.load(open(os.path.join(res, "stage8_scorecard.json")))
    rows = v["thresholds"]
    fig, axs = plt.subplots(1, 2, figsize=(W_IN, 2.95), gridspec_kw={"wspace": 0.36, "width_ratios": [1.1, 1.0]})
    ax = axs[0]
    ax.set_yscale("function", functions=SQ)
    top = 1.0
    X_OV = {"C1": 57.4, "C2": 59.2}
    for crit, key, dx in (("C1", "fC1", -0.35), ("C2", "fC2", 0.35)):
        rng = {}
        for grp in (True, False):
            g = [r for r in rows if r["propagated"] == grp]
            los = [0.0 if r[key]["status"] == "zero" else r[key]["lo"] for r in g]
            his = [0.0 if r[key]["status"] == "zero" else r[key]["hi"] for r in g]
            rng[grp] = (min(los), max(his))
        ov = (max(rng[True][0], rng[False][0]), min(rng[True][1], rng[False][1]))
        if ov[1] >= ov[0]:
            ax.plot([X_OV[crit]] * 2, [ov[0], ov[1]], color=COL[crit], lw=3.0, alpha=0.55, solid_capstyle="butt",
                    zorder=1, clip_on=False)
        for r in rows:
            x = r["E_b_J"] / 1e3 + dx
            fs = r[key]
            y0, y1 = (0.0, 0.0) if fs["status"] == "zero" else (fs["lo"], fs["hi"])
            ax.plot([x, x], [y0, y1], color=COL[crit], lw=0.8, alpha=0.7, zorder=2)
            ax.scatter([x], [y1], s=15, marker=MARK[crit], zorder=3, facecolor=COL[crit] if r["propagated"] else SURF,
                       edgecolor=COL[crit], lw=0.9, clip_on=False)
    ax.text(58.3, 0.29, "overlap", ha="center", va="bottom", fontsize=FS_SMALL, color=INK2, rotation=90)
    ticks = [0, 0.01, 0.05, 0.1, 0.2, 0.5]
    ax.set_yticks(ticks); ax.set_yticklabels(["0", "0.01", "0.05", "0.1", "0.2", "0.5"])
    ax.set_ylim(0, 0.62)
    ax.set_xlim(5, 56.5)
    ax.set_xlabel("Trigger energy $E_\\mathrm{b}$ (kJ)")
    ax.set_ylabel("Threshold $f^*$ (square-root scale)")
    tidy(ax, "y")
    hs = [Line2D([], [], ls="", marker="o", mfc=ORANGE, mec=ORANGE, ms=4, label="$f^*$(C1)"),
          Line2D([], [], ls="", marker="s", mfc=BLUE, mec=BLUE, ms=3.8, label="$f^*$(C2)"),
          Line2D([], [], ls="", marker="o", mfc=SURF, mec=INK2, ms=4, label="hollow: not propagated")]
    ax.legend(handles=hs, loc="upper right", frameon=False, handletextpad=0.2, borderaxespad=0.1, labelspacing=0.3)
    letter(ax, "a")
    ax = axs[1]
    c02 = card["by_fraction"]["0.2"]
    xmax = 380.0
    ax.fill_between([0, xmax], [-60, xmax - 60], [60, xmax + 60], color=BAND, lw=0, zorder=0)
    ax.plot([0, xmax], [0, xmax], color=INK2, lw=0.8, zorder=1)
    fa_x = {"C1": xmax + 28, "C2": xmax + 56, "C3": xmax + 84}
    off = {"C1": -4.0, "C2": 0.0, "C3": 4.0}
    for crit in ("C1", "C2", "C3"):
        k = 0
        for test, d in sorted(c02[crit]["per_test"].items()):
            if d.get("missing") or not d["predicted"]:
                continue
            if d["class"] == "hit":
                ax.scatter([d["measured_s"] + off[crit]], [d["t_s"]], s=14, marker=MARK[crit], color=COL[crit],
                           zorder=3)
            else:
                ax.scatter([fa_x[crit] + 3.5 * (k % 3 - 1)], [d["t_s"]], s=14, marker=MARK[crit], facecolor=SURF,
                           edgecolor=COL[crit], lw=0.9, zorder=3)
                k += 1
        if k:
            ax.text(fa_x[crit], 38.0, f"{k}", ha="center", va="bottom", fontsize=FS_SMALL, color=INK)
        for t, d in c02[crit]["per_test"].items():
            if not d.get("missing") and d["class"] == "miss":
                ax.scatter([d["measured_s"] + off[crit]], [-14.0], s=14, marker=MARK[crit], facecolor=SURF,
                           edgecolor=COL[crit], lw=0.9, zorder=3, clip_on=False)
    ax.axvline(xmax + 12, color=INK2, lw=0.7, ls=(0, (2, 2)))
    ax.text(xmax + 56, 392, "false\nalarms", ha="center", va="top", fontsize=FS_SMALL, color=INK2)
    ax.set_xlim(120, xmax + 100)
    ax.set_ylim(-26, 400)
    ax.axhline(0, color=AXIS, lw=0.8)
    ax.text(188, -14.0, "missed", ha="left", va="center", fontsize=FS_SMALL, color=INK2)
    ax.set_xticks([150, 250, 350])
    ax.set_xlabel("Measured time (s)")
    ax.set_ylabel("Predicted time at f = 0.2 (s)")
    tidy(ax)
    hs = [Line2D([], [], ls="", marker=MARK[c], color=COL[c], ms=4, label=c) for c in ("C1", "C2", "C3")]
    ax.legend(handles=hs, loc="upper left", frameon=False, handletextpad=0.2, borderaxespad=0.1, labelspacing=0.3)
    letter(ax, "b")
    fig.subplots_adjust(left=0.1, right=0.99, top=0.93, bottom=0.15)
    save(fig, out, "fig5")


# ------------------------------------------------------------------------------------------------------------ F6
def fig6(res, out):
    import stage9_inputs as IN
    COL = {"C1": ORANGE, "C2": BLUE}
    MARK = {"C1": "o", "C2": "s"}

    def num(s):
        return None if s in ("", None) else float(s)

    ind = list(csv.DictReader(open(os.path.join(res, "stage9_induction.csv"))))
    frac = {r["test"]: r for r in csv.DictReader(open(os.path.join(res, "stage9_fractions.csv")))}
    card = json.load(open(os.path.join(res, "stage9_scorecard.json")))
    f8 = IN.stage8_fstar()
    tests = {t["test"]: t for t in IN.tests()}
    prop = [x for x, t in tests.items() if t["propagated"]]
    fig, axs = plt.subplots(1, 2, figsize=(W_IN, 2.95), gridspec_kw={"wspace": 0.38, "width_ratios": [1.0, 1.05]})
    ax = axs[0]
    ax.set_xscale("function", functions=SQ)
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
            ax.plot([f - lo for f, _ in pts], [t for _, t in pts], color=COL[crit], lw=0.8, alpha=0.75, zorder=2)
            ax.scatter([f - lo for f, _ in pts], [t for _, t in pts], s=6, marker=MARK[crit], color=COL[crit],
                       zorder=3, lw=0)
    for x in prop:
        tm = tests[x]["time_s"]
        lo = f8[x]["C2"]["lo"] or 0.0
        ft = num(frac[x].get("ft_C2"))
        if ft is not None:
            xm = ft - lo
        else:
            pts = sorted(num(r["f"]) for r in ind if r["chain"] == f"A1_C2_{x}" and r["t_c_s"] not in ("", None))
            xm = (pts[0] - lo) if pts else 0.0
        q = SQ[0](max(xm, 0.0))
        ax.plot([SQ[1](max(q - 0.014, 0.0)), SQ[1](q + 0.014)], [tm, tm], color=INK, lw=1.4, solid_capstyle="butt",
                zorder=4)
    ax.set_xlim(0, xr)
    ax.set_ylim(0, 420)
    ax.set_xticks([0, 0.0125, 0.05, 0.1, 0.2])
    ax.set_xticklabels(["0", "0.0125", "0.05", "0.1", "0.2"])
    ax.set_xlabel("$f$ above the threshold's\nbracket (square-root scale)")
    ax.set_ylabel("Crossing time (s)")
    tidy(ax)
    hs = [Line2D([], [], color=ORANGE, marker="o", ms=3.0, lw=0.8, label="C1"),
          Line2D([], [], color=BLUE, marker="s", ms=3.0, lw=0.8, label="C2"),
          Line2D([], [], color=INK, lw=1.4, label="measured")]
    ax.legend(handles=hs, loc="upper right", frameon=False, handletextpad=0.4, borderaxespad=0.1, labelspacing=0.3)
    letter(ax, "a")
    ax = axs[1]
    ax.set_yscale("function", functions=SQ)
    for x, t in tests.items():
        r = frac[x]
        E = t["E_b_J"] / 1e3
        if t["propagated"]:
            st = r.get("ft_C2_status")
            if st == "threshold":
                lo, hi = num(r["ft_C2_lo"]), num(r["ft_C2_hi"])
                ax.plot([E] * 2, [lo, hi], color=BLUE, lw=0.9, alpha=0.8, zorder=2)
                ax.scatter([E], [hi], s=16, marker="s", facecolor=SURF, edgecolor=BLUE, lw=0.9, zorder=3)
                continue
            if st not in ("matched", "bracketed") or r.get("ft_C2_across_jump") == "True":
                continue
            lo, hi, ft = num(r["ft_C2_lo"]), num(r["ft_C2_hi"]), num(r["ft_C2"])
            if st == "bracketed":
                ax.plot([E] * 2, [lo, hi], color=BLUE, lw=0.9, alpha=0.8, zorder=2)
            ax.scatter([E], [ft], s=16, marker="s", color=BLUE, zorder=3, lw=0)
        else:
            st = r.get("fmax_status")
            if st not in ("zero", "matched", "bracketed"):
                continue
            expl = x in IN.EXPLORATORY_FMAX
            lo, hi, fm = num(r["fmax_lo"]) or 0.0, num(r["fmax_hi"]) or 0.0, num(r["fmax"])
            if st == "bracketed":
                ax.plot([E, E], [lo, hi], color=AQUA, lw=0.9, alpha=0.8, zorder=2)
            ax.scatter([E], [fm], s=18, marker="D", zorder=3, facecolor=SURF if expl else AQUA, edgecolor=AQUA,
                       lw=0.9, clip_on=False)
    sep = card["separation"]["C2"]
    ax.axhline(sep["largest_f_max"]["f"], color=AQUA, lw=0.7, ls=(0, (3, 2)), zorder=1)
    ax.axhline(sep["smallest_f_t"]["f"], color=BLUE, lw=0.7, ls=(0, (3, 2)), zorder=1)
    ticks = [0, 0.005, 0.02, 0.05, 0.1, 0.2, 0.5]
    ax.set_yticks(ticks); ax.set_yticklabels(["0", "0.005", "0.02", "0.05", "0.1", "0.2", "0.5"])
    ax.set_ylim(0, 0.62)
    ax.set_xlim(5, 56.5)
    ax.set_xlabel("Trigger energy $E_\\mathrm{b}$ (kJ)")
    ax.set_ylabel("Fraction read (square-root scale)")
    tidy(ax, "y")
    hs = [Line2D([], [], ls="", marker="s", color=BLUE, ms=3.8, label="$f_\\mathrm{t}$(C2)"),
          Line2D([], [], ls="", marker="s", mfc=SURF, mec=BLUE, ms=3.8, label="threshold only"),
          Line2D([], [], ls="", marker="D", mfc=AQUA, mec=AQUA, ms=3.6, label="$f_\\mathrm{max}$"),
          Line2D([], [], ls="", marker="D", mfc=SURF, mec=AQUA, ms=3.6, label="exploratory")]
    ax.legend(handles=hs, loc="lower left", bbox_to_anchor=(-0.02, 1.0), ncol=2, frameon=False, handletextpad=0.2,
              borderaxespad=0.1, labelspacing=0.25, columnspacing=0.8)
    letter(ax, "b")
    fig.subplots_adjust(left=0.1, right=0.99, top=0.84, bottom=0.2)
    save(fig, out, "fig6")


# ------------------------------------------------------------------------------------------------------------ F7
def fig7(res, out):
    import stage10_inputs as IN
    hs = json.load(open(os.path.join(res, "stage10_history_scores.json")))["part_a"]
    held = json.load(open(os.path.join(res, "stage10_heldout.json")))
    fig = plt.figure(figsize=(W_IN, 5.1))
    ax = fig.add_axes([0.1, 0.47, 0.88, 0.5])
    tm, Tm, _ = IN.history("a")
    tm, Tm = np.array(tm), np.array(Tm)
    keep = tm <= 290.0
    ax.axvspan(0.0, 8.5, color="#f6dccf", lw=0, zorder=0)
    ax.axvspan(IN.T_PROP_S - IN.LAST_S, IN.T_PROP_S, color="#f1f0ec", lw=0, zorder=0)
    ax.fill_between(tm[keep], Tm[keep] - IN.UNC_K, Tm[keep] + IN.UNC_K, color="#d9d8d3", lw=0, zorder=1)
    ax.plot(tm[keep], Tm[keep], color=INK, lw=1.3, zorder=5)
    lines = [("none_hcentral", MUTED, (0, (3, 2)), 1.0, "no delivery"),
             ("tri21_C2_lo_hcentral", BLUE, "-", 1.2, "21.39 s, f = 0.0375"),
             ("tri21_C2_hi_hcentral", BLUE, (0, (4, 1.5)), 1.2, "21.39 s, f = 0.040625"),
             ("con240_C2_hcentral", ORANGE, (0, (5, 1.5, 1, 1.5)), 1.1, "240 s, f = 0.028125 (C2)"),
             ("con360_C2_hcentral", ORANGE, "-", 1.1, "360 s, f = 0.040625 (C2)"),
             ("con360_C1_hcentral", AQUA, "-", 1.1, "360 s, f = 0.071875 (C1)")]
    handles = [Line2D([], [], color=INK, lw=1.3, label="measured, 2.47 K band")]
    for key, col, ls, lw, lab in lines:
        z = np.load(os.path.join(res, "stage10_series", hs[key]["id"] + ".npz"))
        ax.plot(z["probe_t"], z["probe_away"] - 273.15, color=col, ls=ls, lw=lw, zorder=3)
        rms = hs[key]["nodes"]["away"]["window"]["rms_K"]
        handles.append(Line2D([], [], color=col, ls=ls, lw=lw, label=f"{lab}; {rms:.1f} K"))
    ax.axvline(IN.T_PROP_S, color=INK2, lw=0.7, zorder=2)
    ax.text(IN.T_PROP_S - 3, 30, "onset 271.5 s", rotation=90, ha="right", va="bottom", fontsize=FS_SMALL, color=INK2)
    ax.text(4.4, 112, "thermocouple's exposure", rotation=90, ha="center", va="bottom", fontsize=FS_SMALL,
            color=INK2)
    ax.set_xlim(0, 300)
    ax.set_ylim(20, 300)
    ax.set_xlabel("Time from the trigger's runaway (s)")
    ax.set_ylabel("Far face of the neighbour (°C)")
    tidy(ax)
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.04, 1.0), frameon=False, handlelength=2.6,
              handletextpad=0.4, borderaxespad=0.1, labelspacing=0.3)
    letter(ax, "a", x=-0.07)
    ax = fig.add_axes([0.13, 0.07, 0.85, 0.28])
    names = {"fC1": "$f^*$(C1)", "fC2": "$f^*$(C2)", "f9": "fraction read\nfrom time or peak"}
    dirs = [("series_to_parallel", "o", "fit on series, scored on parallel", -0.11),
            ("parallel_to_series", "s", "fit on parallel, scored on series", 0.11)]
    for i, name in enumerate(("fC1", "fC2", "f9")):
        for d, mk, _, dx in dirs:
            v = held["predictors"][name][d]
            lo, hi = v["band_log_2.5_97.5"]
            x = i + dx
            ax.plot([x, x], [lo, hi], color=AXIS, lw=3.0, solid_capstyle="round", zorder=2)
            ax.scatter([x], [v["observed"]["d_log"]], marker=mk, s=22, color=BLUE, zorder=4, edgecolor=SURF, lw=0.6)
    ax.axhline(0.0, color=INK2, lw=0.8, zorder=1)
    ax.axhline(IN.LOG_MARGIN, color=MUTED, lw=0.7, ls=(0, (3, 2)), zorder=1)
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels([names[n] for n in ("fC1", "fC2", "f9")])
    ax.set_xlim(-0.45, 3.6)
    ax.set_ylim(-0.72, 0.26)
    ax.set_ylabel("Held-out log score\nless the constant's")
    tidy(ax, "y")
    hb = [Line2D([], [], ls="", marker=mk, color=BLUE, ms=4, label=lab) for _, mk, lab, _ in dirs]
    hb.append(Line2D([], [], color=AXIS, lw=3.0, label="2.5 to 97.5 %, relabelled"))
    hb.append(Line2D([], [], color=MUTED, lw=0.7, ls=(0, (3, 2)), label="margin of 0.1"))
    ax.legend(handles=hb, loc="center right", frameon=False, handletextpad=0.4, borderaxespad=0.1, labelspacing=0.3)
    letter(ax, "b", x=-0.1)
    save(fig, out, "fig7")


FIGS = {1: fig1, 2: fig2, 3: fig3, 4: fig4, 5: fig5, 6: fig6, 7: fig7}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", default=os.path.join(HERE, "..", "results"))
    ap.add_argument("--out", default=os.path.join(HERE, "..", "manuscript", "figures"))
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    only = [int(x) for x in a.only.split(",") if x] or sorted(FIGS)
    for k in only:
        FIGS[k](a.res, a.out)
