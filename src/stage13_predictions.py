"""Write predictions_stage13.md from the registered reduced numbers (results/stage13_reduced.json) and the run lists
(DECISIONS.md D137). Run once, before any Stage 13 run of the resolved or the lumped model."""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage13_inputs as IN                # noqa: E402

RED = os.path.join(IN.RES, "stage13_reduced.json")
OUT = os.path.join(IN.ROOT, "predictions_stage13.md")
T21 = IN.TAU_TRIGGER


def a2(red, test, tau, region="half"):
    return red[f"A2_{test}_{region}_tau{tau:.4f}_r1_dt1"]


def b2(red, test, tau=T21, h="central", d=0.0):
    return red[f"B2_{test}_tau{tau:.4f}_{h}_dEb{d:+.0f}"]


def main():
    red = json.load(open(RED))
    sha_red = hashlib.sha256(open(RED, "rb").read()).hexdigest()
    pt1 = "M50_PT_Exp1"
    A1_5 = a2(red, pt1, 5.0)["A1"]
    L = []
    w = L.append
    w("# Stage 13 predictions (version 1.9.0, branch stage13)\n")
    w("Registered before any Stage 13 run of the resolved or the lumped neighbour (DECISIONS.md D130 to D137). Each "
      "prediction is the brief's, with its expectation and the rule by which it is scored; the reduced models' own "
      "numbers that a prediction states were computed before this file was pushed and are committed with it in "
      "`results/stage13_reduced.json`. Comparisons with archived values are explanatory and are not scored; only "
      "the new runs are. No tolerance moves after a run.\n")
    w("Symbols: f is the delivered fraction of a test's ejected energy E_e = r E_b (r = 3.105); E = f E_e is the "
      "delivered energy; f*(C1) is the least f for which the resolved neighbour's hottest node reaches T_L = 255.68 C "
      "within 900 s, f*(C2) the least f for which the lumped neighbour does; a search's bracket (lo, hi] has lo not "
      "crossing and hi crossing, and its midpoint is (lo + hi)/2. A1 is the closed form of the local threshold, A2 "
      "the cross-section conduction model, B1 the ignition temperature T_ign and B2 the two-body model of the "
      "whole-cell threshold.\n")
    w("## The predictions\n")
    w(f"**P1.** For PT_Exp1 with a 5 s triangular delivery over the facing half, the resolved f*(C1) lies within "
      f"10 % of A1's closed form. A1 gives f* = {A1_5['f_star']:.5f}, its peak at {A1_5['t_peak_s']:.2f} s, with the "
      f"hot spot's angle ({a2(red, pt1, 5.0)['theta_deg']:.1f} degrees) and its temperature with no delivery "
      f"({A1_5['T_b_C']:.1f} C) taken from A2; the pure skin (25 C, no loss) gives "
      f"{A1_5['pure_skin_f_star']:.5f}. Expectation: likely. Scored: |midpoint - A1| <= 0.10 A1.\n")
    v = a2(red, pt1, 40.0)
    w(f"**P2.** At 40 s (PT_Exp1, facing half), the cross-section model lies within 5 % of the resolved bracket's "
      f"midpoint. A2 gives f* = {v['f_star']:.5f} (hot spot at {v['theta_deg']:.1f} degrees, {v['t_s']:.1f} s). "
      f"Expectation: uncertain. Scored: |A2 - midpoint| <= 0.05 midpoint.\n")
    v = a2(red, pt1, 120.0)
    w(f"**P3.** At 120 s (PT_Exp1, facing half), the resolved threshold lies more than 5 % below the cross-section "
      f"conduction model's (local ignition). A2 gives f* = {v['f_star']:.5f} (hot spot at {v['theta_deg']:.1f} "
      f"degrees, {v['t_s']:.1f} s). Expectation: uncertain. Scored: midpoint < 0.95 A2; A5's run without the "
      f"reaction at the bracket's upper end is reported beside it.\n")
    s = []
    for t in ("M50_ST_Exp3", "M50_PT_Exp3"):
        vals = {tau: a2(red, t, tau)["f_star"] for tau in (10.0, T21, 60.0)}
        s.append(f"{t[4:]}: {vals[10.0]:.5f} at 10 s, {vals[T21]:.5f} at 21.39 s, {vals[60.0]:.5f} at 60 s")
    w(f"**P4.** For ST_Exp3 and PT_Exp3, the cross-section model with the trigger's conduction superposed lies "
      f"within 10 % of the resolved midpoints at 10 and at 60 s, and gives the direction of change from 21.39 s in "
      f"all four cases. A2 gives {s[0]}; {s[1]}. Expectation: uncertain. Scored: |A2 - midpoint| <= 0.10 midpoint "
      f"in each of the four cases, and in each the sign of A2(tau) - A2(21.39 s) equals the sign of midpoint(tau) "
      f"- midpoint(21.39 s), the latter the archived reference refined by A4 (D134); a case whose two resolved "
      f"brackets overlap is reported as such.\n")
    rw = a2(red, pt1, T21, "whole")["f_star"] / a2(red, pt1, T21)["f_star"]
    w(f"**P5.** For PT_Exp1 at 21.39 s, over the whole lateral surface the threshold in delivered energy is 1.8 to "
      f"2.2 times the facing half's. Expectation: likely. A2's own ratio, for the record, is {rw:.3f}. Scored: "
      f"midpoint(whole) / midpoint(half, the refined reference) within [1.8, 2.2].\n")
    w("**P6.** For PT_Exp1 at 21.39 s, over the eighth of the facing half nearest the cap (theta <= 90 degrees, "
      "z >= 0.875 L) the threshold in energy per unit area exceeds the facing half's by at least 25 %. Expectation: "
      "likely (the archived cap-end quarter exceeds it by about 12 %). A2 cannot hold an axial region and states no "
      "number. Scored: (midpoint(eighth) / A_eighth) / (midpoint(half) / A_half) >= 1.25, with A_eighth = A_half / "
      "8.\n")
    w("**P7.** T_ign of the posterior-mean kinetics, with the trigger at the neighbour's own temperature, lies "
      "between 215 and 240 C, and the central 95 % of the 200 draws spans less than 40 K. Expectation: likely for "
      "the mean, uncertain for the span. The first clause is known at registration, because B2 needs B1's mean: "
      "T_ign = 218.48 C (D132); it is reported and not counted. The second clause is computed after this file is "
      "pushed. Scored: the 97.5th less the 2.5th percentile of the 200 draws' T_ign (the trigger at the neighbour's "
      "own temperature) is below 40 K.\n")
    rows = []
    for h in ("low", "high"):
        for t in IN.TEST_ORDER:
            rows.append(f"{t[4:]} {h} {b2(red, t, T21, h)['E_star_J']:.0f}")
    w("**P8.** B2's delivered energy at the whole-cell threshold lies within the larger of 10 % and 300 J of the "
      "full lumped model's midpoint in at least 28 of the 32 low and high contact searches. Expectation: uncertain. "
      "B2's 32 values (J): " + "; ".join(rows) + ". Scored: the number of searches with |B2 - midpoint| <= "
      "max(0.10 midpoint, 300 J) is at least 28.\n")
    a1v = {tau: a2(red, pt1, tau)["f_star"] for tau in (T21, 120.0, 360.0)}
    b2v = {tau: b2(red, pt1, tau)["f_star"] for tau in (T21, 120.0, 360.0)}
    rr = ", ".join(f"{b2v[t] / a1v[t]:.3f} at {t:.4g} s" for t in (T21, 120.0, 360.0))
    w(f"**P9.** For PT_Exp1, the ratio f*(C2)/f*(C1) falls from 21.39 to 120 to 360 s and is below 1.5 at 360 s. "
      f"Expectation: likely for the fall, uncertain for the level. The reduced models' ratio B2/A2, for the record: "
      f"{rr}. Scored: with midpoints, f*(C1) from A4 (the refined reference at 21.39 s, the searches at 120 and "
      f"360 s) and f*(C2) from the archive's refined bracket at 21.39 s, (0.4609375, 0.4625], and B4's central "
      f"searches at 120 and 360 s: ratio(21.39) > ratio(120) > ratio(360), and ratio(360) < 1.5.\n")
    sl = []
    for t in ("M50_PP_Exp3", "M50_ST_Exp2", "M50_PT_Exp3"):
        lo, hi = b2(red, t, T21, "central", -2000.0)["E_star_J"], b2(red, t, T21, "central", 2000.0)["E_star_J"]
        sl.append(f"{t[4:]} {(lo - hi) / 4.0:.0f} J per kJ ({lo:.0f} J at E_b - 2 kJ, {hi:.0f} J at E_b + 2 kJ)")
    w("**P10.** For PP_Exp3, ST_Exp2 and PT_Exp3, the full lumped model's needed delivered energy falls by 150 to "
      "300 J per kJ of body energy, across the 4 kJ between the shifted runs. Expectation: likely for the first two, "
      "uncertain for PT_Exp3. B2's own slopes, for the record: " + "; ".join(sl) + ". Scored: for each test, "
      "(midpoint(E_b - 2 kJ) - midpoint(E_b + 2 kJ)) / 4 kJ within [150, 300] J per kJ; P10 holds if all three do, "
      "and each is reported.\n")
    w("## Where the searches start\n")
    w("Each resolved search starts at A2's f* (the eighth at the facing half's flux per area plus 25 %), each lumped "
      "search at B2's E* (D134, D135). The starting values, with every other reduced number, are in "
      "`results/stage13_reduced.json`.\n")
    w("## Provenance\n")
    w(f"- Run lists (`stage13_inputs.run_lists()`, 13 resolved and 70 lumped searches): SHA-256 "
      f"`{IN.run_lists_hash()}`.\n- `results/stage13_reduced.json`: SHA-256 `{sha_red}`.\n"
      "- The commit that registers this file and the time it was pushed are recorded in DECISIONS.md and in the "
      "state document after the push.\n")
    open(OUT, "w").write("\n".join(L))
    return OUT


if __name__ == "__main__":
    print(main())
