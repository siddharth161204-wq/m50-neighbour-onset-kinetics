"""Stage 14 after the independent read (DECISIONS D162): the bounds corrected to the stage's own rule.

The registered bounds (results/stage14_bounds.csv, D158) stay as computed. The independent read
(results/stage14_independent_read.md) found that four of them are not what D153 (1) asks of an upper
bound ("A share or fraction that no source gives enters at 1 in the upper bound"):
  A1  reflected radiation was left out and only one venting end counted: with the reflectivity of the
      holder and the cans at 1, the only caps left are those that need no geometry, the irradiation of a
      black body at the largest flame temperature over the facing half's whole view, sigma T^4 A_f, and
      the energy E_avail;
  A2  the gas's radiation left out the rays that end on the trigger (gas in the wedges hides the can),
      and Churchill and Bernstein's mean over the whole circumference was applied to one half; with no
      source for the half's own mean, it is at most twice the whole's (the other half's is not negative);
  A3  at exactly 30 degrees a grazing ray was counted as a strike (a cone gives about one half there),
      and the shortest time, 0.35 s, is no source's shortest jet;
  A6  the rated energy leaves out the excess of the open-circuit voltage and the reversible heat, which no
      source gives: the bound holds with them left out.
This script writes the corrected bounds, Part B's verdicts and the module table under them, the scores
under them, and two scans that check the readings beside P1 (the vent's axis, and the trigger's rim
beside the line of contact). It changes no registered file.

Writes results/stage14_bounds_corrected.csv, results/stage14_tests_corrected.csv,
results/stage14_module_table_corrected.csv and results/stage14_corrections.json.
"""
import csv
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import stage14_view as v  # noqa: E402

WINDOWS = (21.39, 120.0, 240.0, 360.0)


def main():
    with open(os.path.join(ROOT, "results", "stage14_inputs.csv"), newline="") as fh:
        rows = {r["key"]: r for r in csv.DictReader(fh)}
    num = lambda k, f="value": float(rows[k][f])  # noqa: E731
    bj = json.load(open(os.path.join(ROOT, "results", "stage14_bounds.json")))
    rt = json.load(open(os.path.join(ROOT, "results", "stage14_raytrace.json")))
    Rc, Lc = num("R_cell"), num("L_cell")
    A_f = num("A_facing")
    E_avail = bj["inputs"]["E_avail_J"]
    E_global = bj["inputs"]["E_global_J"]
    sigma, Tf, T0 = num("sigma"), num("T_flame_max") + 273.15, num("T0") + 273.15
    t_min, t_max = num("t_vent_min", "range_lo"), num("t_flame_max")
    E_s = num("db_stored_energy")
    blackbody = sigma * Tf ** 4                      # W/m2
    F_trig, F_end = rt["facing_view"]["trigger"], rt["facing_view"]["beyond_L"]

    # A1: direct radiation, one end (registered); both ends; with reflection at its cap (corrected)
    P1_one = blackbody * A_f * F_end
    P1_both = blackbody * A_f * (F_end + rt["facing_view"]["beyond_0"])
    P1_refl = blackbody * A_f
    U1E_direct = 0.25 * E_avail
    A1 = {}
    for tau in list(WINDOWS) + ["total"]:
        t = t_max if tau == "total" else tau
        A1[str(tau)] = dict(registered_direct_one_end=min(U1E_direct, P1_one * t),
                            direct_both_ends=min(U1E_direct, P1_both * t),
                            corrected=min(E_avail, P1_refl * t))

    # A2: the gas's radiation over the whole view, convection at most twice the whole-circumference mean
    h_mean = bj["A2"]["h_max"]
    q2 = 2.0 * h_mean * (Tf - T0) + blackbody
    P2 = q2 * A_f
    A2 = {str(tau): dict(registered=bj["A2"]["bounds_J"][str(tau)],
                         corrected=min(E_avail, P2 * (t_max if tau == "total" else tau)))
          for tau in list(WINDOWS) + ["total"]}

    # A3 at 30 degrees: the cones' shares (the narrow jet only grazes there)
    b30 = next(r for r in rt["breach"] if r["phi_deg"] == 30)
    s30 = max(b30[f"s_beta{b}"] for b in (5, 10, 15, 30, 45, 60, 90))

    # Scans that check the readings beside P1
    v.R, v.L = Rc, Lc
    cells = v.cells_default(trigger=True, length=Lc, radius=Rc)
    rng = np.random.default_rng(1462)
    axis = []
    for k in np.round(np.arange(0.50, 1.501, 0.05), 2):
        w = v.point_fraction(np.array([0.0, 2.0 * Rc, Lc + k * Rc]), 4_000_000, rng, cells=cells)
        axis.append(dict(beyond_R=float(k), w=w, se=math.sqrt(w * (1 - w) / 4e6)))
    rim = []
    for psi in (2.0, 5.0, 15.0):
        for h in (1e-4, 1e-3, 1e-2):
            ps = math.radians(psi)
            p = np.array([Rc * math.sin(ps), 2.0 * Rc - Rc * math.cos(ps), Lc + h * Rc])
            w = v.point_fraction(p, 2_000_000, rng, cells=cells)
            rim.append(dict(psi_deg=psi, beyond_R=h, w=w, se=math.sqrt(w * (1 - w) / 2e6)))
    w_axis = max(a["w"] for a in axis)
    w_rim = max(r["w"] for r in rim)

    corrected = {
        "A1": {k: x["corrected"] for k, x in A1.items()},
        "A2": {k: x["corrected"] for k, x in A2.items()},
        "A3": {str(t): E_avail for t in list(WINDOWS) + ["total"]},
        "A4": {str(t): E_avail for t in list(WINDOWS) + ["total"]},
        "A6": {str(t): E_s for t in list(WINDOWS) + ["total"]},
    }
    times = {"A1": (t_min, t_max), "A2": (t_min, t_max), "A3": (None, t_max), "A4": (t_min, t_max), "A5": (None, None), "A6": (None, None)}
    notes = {
        "A1": f"min(E_avail, sigma T^4 A_f t = {P1_refl:.2f} W x t): reflection at its cap; direct radiation from both ends would give min(0.25 E_avail, {P1_both:.2f} W x t), from one end (registered) min(0.25 E_avail, {P1_one:.2f} W x t)",
        "A2": f"min(E_avail, [2 h_mean (T - T0) + sigma T^4] A_f t = {P2:.2f} W x t), for a cross flow: h_mean {h_mean:.1f} W/(m2 K) is Churchill and Bernstein's mean over the whole circumference, and a half's mean is at most twice it",
        "A3": "E_avail for a breach facing the neighbour; the shortest time is not given by any source (0.84 s if the shortest runaway bounds it)",
        "A4": "E_avail; no rate term",
        "A5": f"not determinable under D153 (3); read as A3 and A4 are, a share of the trigger's release would give {E_global:.1f} J",
        "A6": "the rated stored energy, with the excess of the open-circuit voltage and the reversible heat left out (no source gives them)",
    }
    out = []
    for p in ("A1", "A2", "A3", "A4", "A5", "A6"):
        for tau in list(WINDOWS) + ["total"]:
            u = corrected.get(p, {}).get(str(tau), "")
            out.append(dict(path=p, determinable="no" if p == "A5" else "yes", window_s=tau, lower_J="" if p == "A5" else 0.0,
                            upper_J=("" if u == "" else round(u, 3)),
                            registered_upper_J=("" if p == "A5" else round(bj[p]["bounds_J"][str(tau)], 3)),
                            time_lo_s=("" if times[p][0] is None else times[p][0]), time_hi_s=("" if times[p][1] is None else times[p][1]),
                            note=notes[p]))
    with open(os.path.join(ROOT, "results", "stage14_bounds_corrected.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)

    # Part B under the corrected bounds
    with open(os.path.join(ROOT, "results", "stage14_tests.csv"), newline="") as fh:
        tests = list(csv.DictReader(fh))
    changed = []
    for r in tests:
        r["registered_upper_J"], r["registered_verdict"] = r["upper_J"], r["verdict"]
        p, win = r["path"], r["window_s"]
        if p in corrected and r["verdict"] not in ("does not act (series)",):
            u = corrected[p][str(float(win))]
            lo, hi = float(r["need_lo_J"]), float(r["need_hi_J"])
            r["upper_J"] = round(u, 3)
            r["verdict"] = "needs nothing" if hi == 0 else ("reaches" if u >= hi else ("reaches part" if u >= lo else "does not reach"))
        if r["verdict"] != r["registered_verdict"]:
            changed.append(dict(test=r["test"], window_s=win, path=p, registered=r["registered_verdict"], corrected=r["verdict"],
                                need_hi_J=float(r["need_hi_J"]), corrected_upper_J=r["upper_J"]))
    with open(os.path.join(ROOT, "results", "stage14_tests_corrected.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(tests[0].keys()))
        w.writeheader()
        w.writerows(tests)

    # The module table under the corrected bounds
    with open(os.path.join(ROOT, "results", "stage14_module_table.csv"), newline="") as fh:
        mod = list(csv.DictReader(fh))
    for r in mod:
        p = r["path"]
        if p in corrected:
            for tau in WINDOWS:
                r[f"upper_within_{tau}s_J"] = round(corrected[p][str(tau)], 3)
            r["upper_total_J"] = round(corrected[p]["total"], 3)
        r["note"] = notes[p]
        if p == "A3":
            r["time_lo_s"] = ""
    with open(os.path.join(ROOT, "results", "stage14_module_table_corrected.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(mod[0].keys()))
        w.writeheader()
        w.writerows(mod)

    # The scores under the corrected bounds (registered scores unchanged)
    E_fix = bj["inputs"]["E_fix_J"]
    s21 = corrected["A1"]["21.39"] + corrected["A2"]["21.39"]
    scores = dict(
        P1=dict(holds=corrected["A1"]["total"] < 0.02 * E_fix, A1_total_J=corrected["A1"]["total"]),
        P2=dict(holds=s21 < 5962.4, sum_21s_J=s21),
        P3=dict(holds=s21 > 263.5, sum_21s_J=s21),
        P4=dict(holds=corrected["A3"]["21.39"] > 5962.4, A3_21s_J=corrected["A3"]["21.39"]),
        P5=dict(holds=True, note=f"A5 is not determinable under the rule of D153 (3) as written; read as A3 and A4 are, A5 would be bounded by E_global = {E_global:.1f} J and P5 would fail"),
        P6=dict(holds=corrected["A6"]["total"] > 1000.0, A6_total_J=corrected["A6"]["total"]),
    )
    res = dict(
        A1=dict(rate_one_end_W=P1_one, rate_both_ends_W=P1_both, rate_reflection_cap_W=P1_refl, by_window=A1,
                energy_term_binds_from_s=E_avail / P1_refl),
        A2=dict(q_W_m2=q2, rate_W=P2, by_window=A2, energy_term_binds_from_s=E_avail / P2),
        A3=dict(s_30deg_cones_max=s30, narrow_jet_strikes_for_phi_below_deg=30.0),
        A6=dict(condition="the excess of the open-circuit voltage over the rated energy and the reversible heat are left out"),
        scans=dict(axis=axis, axis_max_w=w_axis, axis_max_J=w_axis * E_avail, axis_max_share_of_Efix=w_axis * E_avail / E_fix,
                   rim=rim, rim_max_w=w_rim, rim_max_J=w_rim * E_avail),
        partB_changed=changed, scores=scores,
        largest_need_any_window_J=max(float(r["need_hi_J"]) for r in tests), E_avail_J=E_avail, E_global_J=E_global,
    )
    with open(os.path.join(ROOT, "results", "stage14_corrections.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(dict(A1={k: round(x["corrected"], 1) for k, x in A1.items()}, A1_both_21s=round(A1["21.39"]["direct_both_ends"], 1),
                          A2={k: round(x["corrected"], 1) for k, x in A2.items()}, s30=s30, axis_max=(w_axis, w_axis * E_avail),
                          rim=[(r["psi_deg"], r["beyond_R"], round(r["w"], 4)) for r in rim], changed=changed,
                          scores={k: v_["holds"] for k, v_ in scores.items()}), indent=1))


if __name__ == "__main__":
    main()
