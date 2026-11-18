"""Writes predictions_stage15.md from the reduced model's numbers (results/stage15_cross_section.json) and Part B's
registered list (`stage15_partb.registered_list`), before any new Stage 15 run of the three-dimensional model.

Usage: python3 src/stage15_predictions.py
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage15_inputs as IN              # noqa: E402
import stage15_partb as PB               # noqa: E402

OUT = os.path.join(IN.ROOT, "predictions_stage15.md")
XS = os.path.join(IN.RES, "stage15_cross_section.json")


def e_c2(test):
    """The whole-cell clock's threshold with the 21.39 s delivery, from the narrowest archived f*(C2) bracket:
    Stage 12's where its continuation of Stage 9's f_t search ended at the threshold (D123 (3)), else Stage 9's
    where its f_t search did (D91 (3)), else Stage 8's; 0 where the lumped neighbour crosses with no delivery."""
    s8 = {r["test"]: r for r in csv.DictReader(open(os.path.join(IN.RES, "stage8_thresholds.csv")))}
    s9 = {r["test"]: r for r in csv.DictReader(open(os.path.join(IN.RES, "stage9_fractions.csv")))}
    s12 = json.load(open(os.path.join(IN.RES, "stage12_paper_numbers.json")))["B2"]
    E_e = IN.e_e(test)
    r9 = s9.get(test)
    r12 = s12.get(test)
    if r12 and r12["status"] == "threshold":
        lo_J, hi_J = (1e3 * x for x in r12["E_bracket_kJ"])
        return {"lo_J": lo_J, "hi_J": hi_J, "mid_J": 0.5 * (lo_J + hi_J), "source": "Stage 12",
                "lo_f": lo_J / E_e, "hi_f": hi_J / E_e}
    if r9 and r9["ft_C2_status"] == "threshold":
        lo, hi, src = float(r9["ft_C2_lo"]), float(r9["ft_C2_hi"]), "Stage 9"
    else:
        b = s8[test]["fC2"].strip()
        if b == "0":
            return {"lo_J": 0.0, "hi_J": 0.0, "mid_J": 0.0, "source": "Stage 8 (0)"}
        lo, hi = (float(x) for x in b.strip("(]").split(","))
        src = "Stage 8"
    return {"lo_J": lo * E_e, "hi_J": hi * E_e, "mid_J": 0.5 * (lo + hi) * E_e, "source": src,
            "lo_f": lo, "hi_f": hi}


def fmt(x, nd=0):
    if x is None:
        return "none"
    return f"{x:,.{nd}f}"


def main():
    xs = json.load(open(XS))
    xs_hash = IN.sha256_file(XS)
    lh, _ = PB.list_hash()
    a2 = {(r["test"], r["shape"], r["tau_s"]): r for r in xs["A2"]}
    a1 = xs["A1_summary"]
    L = []
    w = L.append
    w("# Stage 15 predictions: the resolved neighbour's own runaway")
    w("")
    w("Written on branch `stage15` and committed and pushed before any new Stage 15 run of the three-dimensional "
      "model. The reduced model's numbers stated here were computed before this file and are committed with it in "
      f"`results/stage15_cross_section.json` (SHA-256 {xs_hash}). The registered list of Part B's runs and its "
      f"rules (`src/stage15_partb.py`, `registered_list`) has the SHA-256 {lh}. DECISIONS.md D170 to D176 record "
      "the design.")
    w("")
    w("## The quantities")
    w("")
    w("- T_L, the level: 255.68 C, the lower end of the two-cell study's onset band.")
    w("- The resolved neighbour: the three-dimensional model of the neighbouring cell (19,355 nodes on the half "
      "cell), with the posterior-mean decomposition kinetics and their heat fed back, the trigger cell's archived "
      "temperature history (its fitted body energy E_b released over 21.39 s), the central contact (2,000 W/(m2 K)) "
      "and tabs, 25 C. The lumped neighbour: the same cell as one temperature with one heat capacity, 61.75 J/K, "
      "linked to the trigger through the same conductances.")
    w("- Tmean, the resolved neighbour's mean temperature: the sum of C_i T_i over the sum of C_i over its nodes, "
      "C_i each node's heat capacity (the roll's volumetric heat capacity times the node's volume, plus its share of "
      "the can's). It is the stored heat over the heat capacity, the quantity the lumped neighbour's one "
      "temperature stands for.")
    w("- C1: the resolved neighbour's hottest node reaches T_L (the local criterion). C2: the lumped neighbour "
      "reaches T_L (the whole-cell clock). C8: the first time within 900 s at which Tmean reaches T_L (the "
      "neighbour's own runaway).")
    w("- A delivery: energy E delivered from t = 0 as a uniform flux over the half of the neighbour's can facing the "
      "trigger, as the archive's triangular pulse over 21.39 s (zero at 0 and 21.39 s, its peak at 10.69 s) or as a "
      "constant power over 120, 240 or 360 s. E_e = 3.105 E_b is a test's ejected energy and f = E / E_e.")
    w("- E*(C8): the least delivered energy for which C8 happens, for a stated delivery; E*(C2) likewise for C2. "
      "The whole-cell clock's threshold E*(C2) with the 21.39 s delivery is the midpoint of the narrowest archived "
      "bracket of the least energy for C2 (Stage 12's, where its continuation of Stage 9's search for the measured "
      "time ended at the threshold; otherwise Stage 9's, where its own search did; otherwise Stage 8's), 0 where "
      "the lumped neighbour crosses with no delivery.")
    w("- The far face: the resolved neighbour's surface node at mid-length opposite the line of contact. Its jump's "
      "start: with its rate of rise r(t) = [T(t + 1 s) - T(t - 1 s)] / 2 s on a 0.5 s grid, the first time r reaches "
      "1 K/s after r has first reached 0.5 K/s and then fallen below it, before C8; where r never falls below "
      "0.5 K/s before C8, the reading 20 s before C8.")
    w("- M50_PT_Exp4's measured history: the neighbour's thermocouple in the supplement's Figure 10 of Fransson et "
      "al. (2024), read every 0.5 s; it reads 197.3 C at 271.5 s, the onset the figure marks, and then jumps. "
      "Stage 10's rule scores a run against it at the far face over 0 to 271.5 s (the root mean square of the "
      "difference, the difference at 271.5 s, the rise over the last 60 s).")
    w("")
    w("## The reduced model (Part A)")
    w("")
    w("The reactive cross-section is Stage 13's conduction model of the mid-height cross-section (conduction in r "
      "and theta, the can, the contact and air wedge, convection, radiation, the delivery over the facing half) "
      "with the archive's kinetics in every cell of the roll and their heat fed back, the reaction step the "
      "three-dimensional model's own. It has neither the ends nor the tabs. With the reaction off it equals "
      "Stage 13's model to 7.4e-13 K (V3).")
    w("")
    w(f"Against the archive's {a1['runs']} central continued runs (explanatory; DECISIONS.md D174) it gives the "
      f"same outcome, C8 or none within the archived run's span, in {a1['same_outcome']} and misses "
      f"{a1['missed']}. " + ("That is more than one run in ten, so it cannot stand for the three-dimensional "
                             "cell: P1 is dropped and Part B's searches are centred on the archive's brackets."
                             if a1["A3_cannot_stand"] else
                             "That is no more than one run in ten, so it stands for the three-dimensional cell "
                             "(A3) and P1 is kept."))
    w("")
    w("E*(C8) with the 21.39 s delivery (the bracket's midpoint, J; the bracket no wider than 1 % of it):")
    w("")
    w("| Test | E*(C8) | f*(C8) | E*(C2), archived | ratio |")
    w("|---|---|---|---|---|")
    for t in IN.TEST_ORDER:
        r = a2[(t, "tri", IN.TAU_TRIGGER)]
        c2 = e_c2(t)
        ratio = (r["E_star_J"] / c2["mid_J"]) if (r["E_star_J"] is not None and c2["mid_J"] > 0) else None
        w(f"| {t} | {fmt(r['E_star_J'])} | {fmt(r.get('f_star'), 5) if r.get('f_star') is not None else 'none'} | "
          f"{fmt(c2['mid_J'])} ({c2['source']}) | {fmt(ratio, 2) if ratio else '-'} |")
    w("")
    w("E*(C8) with constant power, the nine propagated tests (J):")
    w("")
    w("| Test | 120 s | 240 s | 360 s |")
    w("|---|---|---|---|")
    for t in IN.propagated():
        cells = [fmt(a2[(t, 'con', tau)]["E_star_J"]) for tau in IN.TAUS_LONG]
        w(f"| {t} | " + " | ".join(cells) + " |")
    w("")
    ft = {(r["test"], r["shape"], r["tau_s"]): r for r in xs.get("A2_at_measured", [])}
    w("The delivered energy at which the cross-section's C8 falls at the measured time t_m, by Stage 9's rule for "
      "f_t read on C8 (J): \"matched\", a run whose C8 lies within 10 s of t_m (its C8 time in brackets); "
      "\"bracketed\", the energy at which C8's time, taken linear between the ends of the final bracket, equals t_m; "
      "\"threshold\", C8 already comes before t_m at the least energy that gives it (the bracket's upper end is "
      "given), so no delivered energy puts it at t_m; \"above grid\", C8 does not come before t_m up to "
      "f8_hi + 0.2 (f8_hi the upper end of the E*(C8) bracket as a fraction of E_e).")
    w("")
    w("| Test | t_m (s) | 21.39 s | 120 s | 240 s | 360 s |")
    w("|---|---|---|---|---|---|")
    for t in IN.propagated():
        cells = []
        for shape, tau in [("tri", IN.TAU_TRIGGER)] + [("con", x) for x in IN.TAUS_LONG]:
            m = ft.get((t, shape, tau))
            if m is None:
                cells.append("none")
            elif m["status"] == "matched":
                cells.append(f"{fmt(m['E_J'])} (matched, {m['t_C8_s']:.1f} s)")
            elif m["status"] == "bracketed":
                cells.append(f"{fmt(m['E_J'])} (bracketed)")
            elif m["status"] == "threshold":
                cells.append(f"threshold, {fmt(m['hi_f'] * IN.e_e(t))}")
            else:
                cells.append(m["status"])
        w(f"| {t} | {float(IN.tests()[t]['time_s']):.0f} | " + " | ".join(cells) + " |")
    w("")
    b1x = xs["for_predictions"]
    w("The reduced model's values for the predictions:")
    w("")
    for line in b1x["lines"]:
        w(f"- {line}")
    w("")
    w("## Part B, the registered list")
    w("")
    doc = PB.__doc__.split("\n\n", 1)[1] if PB.__doc__ else ""
    paras = []
    for line in doc.splitlines():                # a paragraph starts at a two-space indent, continues at six
        if not line.strip():
            continue
        if line.startswith("  ") and not line.startswith("   "):
            paras.append(line.strip())
        elif paras:
            paras[-1] += " " + line.strip()
    for para in paras:
        w(f"- {' '.join(para.split())}")
    w("")
    w("Every run: both neighbours, the resolved one stopped at C8 or run to 900 s, its hot spot's crossing recorded "
      "without a stop, the lumped twin to 900 s; Stage 10's five probes of the resolved neighbour at mid-length; the "
      "sub-step limit 4,096 from the delivery's start. The first runs of every chain:")
    w("")
    for s in PB.registered_list()["first"]:
        w(f"- `{s['id']}`")
    w("")
    w("## Predictions")
    w("")
    for p in b1x["predictions"]:
        w(f"**{p['id']}.** {p['statement']} *Scored:* {p['rule']} *Reduced model:* {p['reduced']} "
          f"*Expectation (unscored):* {p['expectation']}")
        w("")
    w("## Checks")
    w("")
    w("- V1 (made in Part A0): the mean's crossing and peak of every archived continued run read by two separate "
      "codes from the stored series agree to 0.1 s and 0.01 K. Result: they agree to 0 s and 0 K in all 199.")
    w("- V2: every new run's energy account closes to under 1e-9 of the heat taken in, and a run stopped at C8 "
      "reports the energy delivered up to its stop (each delivery equal to its pulse's integral to the stop, to "
      "1e-9 relative).")
    w("- V3 (made in Part A): the reactive cross-section with the reaction off equals Stage 13's conduction model to "
      "1e-8 K. Result: 7.4e-13 K.")
    w("- V4: B1's two M50_PT_Exp4 runs at the ends of its bracket made again with the mesh refined by 1.5 and with "
      "every step limit halved: the outcome (C8 or none) does not change, and the C8 time moves by less than 5 %.")
    w("- V5: an independent read by a separate agent that has not seen the work being produced: every number of the "
      "note's Stage 15 lines, the table and the sentences recomputed from the records.")
    w("")
    open(OUT, "w").write("\n".join(L) + "\n")
    print("written", OUT)


if __name__ == "__main__":
    main()
