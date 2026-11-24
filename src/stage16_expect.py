"""Step 16's expectations, computed from the archived records before any Step 16 run (DECISIONS.md D190;
predictions_stage16.md). Nothing here is run in three dimensions: every number is read from the records already
archived (results/stage15_cross_section.json, results/stage15_table.csv, results/stage15_runs/) and from the reactive
cross-section's own runs.

For each need searched (the eight strong-trigger tests with the 21.39 s pulse, and the constant-power deliveries of
X), it gives:
  - the cross-section's need E_x (Table S7) and the time of its run;
  - the cross-section's own least energy whose runaway comes by t_m + 10 s, read between its runs by interpolating
    linearly in 1/t (an estimate, since the cross-section's search stopped at a match or at its resolution);
  - the same with the three-dimensional runaway taken earlier by a lead of 10, 20 or 30 s (the leads seen near the
    thresholds, below), an estimate of the three-dimensional need;
  - the bounds that the three-dimensional runs already made put on the need (the highest late and the lowest early);
  - the lumped need (Table S7) and whether a three-dimensional run at or above it is already late.
And for PT-Exp1, the cross-section's threshold, the lumped bracket and the ratio they give.

Run: python3 src/stage16_expect.py   (writes results/stage16_expectations.json)
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage15_inputs as IN              # noqa: E402
import stage15_partb as PB               # noqa: E402
import stage16_run as S                  # noqa: E402

OUT = os.path.join(IN.RES, "stage16_expectations.json")
LEADS = (0.0, 10.0, 20.0, 30.0)


def xs_points(test, shape, tau):
    """The cross-section's runs near the need and the threshold for one delivery: [(E_J, t_C8_s)] with C8."""
    d = json.load(open(S.XS_OUT))
    pts = []
    for r in d["A2_at_measured"]:
        if r["test"] == test and r["shape"] == shape and (shape == "tri" or abs(r["tau_s"] - tau) < 1e-6):
            E_e = IN.e_e(test)
            pts += [(f * E_e, t) for f, t in r["points"] if t is not None]
    for r in d["A2"]:
        if shape == "tri" and r["test"] == test and r["shape"] == "tri":
            pts += [(x[0], x[2]) for x in r["runs"] if x[1]]
    out = {}
    for E, t in pts:
        out[round(E, 3)] = t
    return sorted(out.items())


def e_of_t(pts, t_target):
    """The energy at which the runaway time falls to t_target, linear in 1/t between adjacent runs; None outside."""
    for (E1, t1), (E2, t2) in zip(pts, pts[1:]):
        if t1 >= t_target >= t2 and t1 != t2:
            a = (1.0 / t_target - 1.0 / t1) / (1.0 / t2 - 1.0 / t1)
            return E1 + a * (E2 - E1)
    return None


def lumped_need(test, label):
    for r in S._table15():
        if r["test"] == test and r["delivery"] == label:
            return float(r["C2_E_by_t_J"]), r["C2_status"], float(r["C2_E_J"])
    raise KeyError((test, label))


def need_expectation(test, shape, tau, recs15, a1):
    label = S.DELIVERY["tri"] if shape == "tri" else S.DELIVERY[float(tau)]
    E_x, st = S.xs_need(test, shape, tau)
    t_m = S.t_measured(test)
    lim = t_m + S.WINDOW_S
    row = next(r for r in S._table15() if r["test"] == test and r["delivery"] == label)
    pts = xs_points(test, shape, tau)
    est = {}
    for lead in LEADS:
        E = e_of_t(pts, lim + lead)
        est["%.0f" % lead] = E
    # counted as delivered by the runaway, as Table S7 counts a need: a three-dimensional run at the estimated energy
    # runs away at t_m + 10 s; the cross-section's need by the time of its own run
    E_x_by_t = float(row["C8_xs_E_by_t_J"]) if row["C8_xs_E_by_t_J"] else None
    est_by_t = {k: (v * S.share_by(shape, tau, lim) if v is not None else None) for k, v in est.items()}
    runs = S.existing_runs(test, shape, tau, {}, recs15, a1)
    cl = [(E, S.classify(t, te, t_m), t, src, rid) for E, t, te, src, rid in runs]
    late = [x for x in cl if x[1] == "late"]
    early = [x for x in cl if x[1] == "early"]
    lo = max(late) if late else None
    hi = min(early) if early else None
    L, Lst, L_nominal = lumped_need(test, label)
    first = S.need_state(test, shape, tau, {}, "N" if shape == "tri" else "X", recs15, a1)
    return {
        "test": test, "delivery": label, "t_m_s": t_m, "E_e_J": IN.e_e(test),
        "E_x_J": E_x, "E_x_status": st, "E_x_t_C8_s": float(row["C8_xs_t_s"]) if row["C8_xs_t_s"] else None,
        "E_x_by_t_J": float(row["C8_xs_E_by_t_J"]) if row["C8_xs_E_by_t_J"] else None,
        "xs_runs": [[E, t] for E, t in pts],
        "xs_E_at_tm_plus_10_J": est["0"],
        "estimate_3d_need_J_by_lead_s": {k: v for k, v in est.items() if k != "0"},
        "d_definition_only": (E_x - est["0"]) / est["0"] if est["0"] else None,
        "d_by_lead": {k: ((E_x - v) / v if v else None) for k, v in est.items() if k != "0"},
        "estimate_3d_need_by_t_J_by_lead_s": {k: v for k, v in est_by_t.items() if k != "0"},
        "d_by_t_by_lead": {k: ((E_x_by_t - v) / v if v and E_x_by_t else None) for k, v in est_by_t.items()
                           if k != "0"},
        "existing_3d_runs": [{"E_J": E, "class": c, "t_C8_s": t, "source": src, "id": rid} for E, c, t, src, rid in
                             sorted(cl)],
        "known_lower_J": lo[0] if lo else None, "known_lower_id": lo[4] if lo else None,
        "known_upper_J": hi[0] if hi else None, "known_upper_id": hi[4] if hi else None,
        "lumped_need_J": L, "lumped_status": Lst, "lumped_nominal_J": L_nominal,
        # a three-dimensional run at the lumped need's own nominal energy or above it is already late (Table S7 gives
        # the lumped need to 0.1 J); the lumped need's runaway comes no later than t_m + 10 s, so by the runaway too
        "lumped_need_already_exceeded": bool(lo and lo[0] >= L_nominal - 0.5),
        "lower_by_t_J": (lo[0] * S.share_by(shape, tau, lim)) if lo else None,
        "first_run": first[1]["id"] if first[1] else None, "first_state": first[0],
    }


def leads_near_thresholds(recs15):
    """Where both models ran the same strong-trigger delivery near a threshold: the three-dimensional runaway's lead
    (the cross-section's time at the same energy, read between its runs, less the three-dimensional time)."""
    out = []
    for rid, r in sorted(recs15.items()):
        if r.get("kind") != "B1" or not r["resolved"]["C8"] or r.get("refine", 1.0) != 1.0 or \
                r.get("dt_scale", 1.0) != 1.0:
            continue
        test = r["test"]
        E = r["E_delivered_J"]
        pts = xs_points(test, "tri", None)
        t_xs = None
        for (E1, t1), (E2, t2) in zip(pts, pts[1:]):
            if E1 <= E <= E2:
                a = (E - E1) / (E2 - E1)
                t_xs = 1.0 / (1.0 / t1 + a * (1.0 / t2 - 1.0 / t1))
        out.append({"id": rid, "test": test, "E_J": E, "t_C8_3d_s": r["resolved"]["t_C8_s"], "t_C8_xs_s": t_xs,
                    "lead_s": (t_xs - r["resolved"]["t_C8_s"]) if t_xs else None})
    return out


def main():
    recs15 = PB.load()
    a1 = json.load(open(S.XS_OUT))["A1_rows"]
    N = [need_expectation(t, "tri", None, recs15, a1) for t in S.STRONG8]
    X = [need_expectation(t, "con", tau, recs15, a1) for tau in S.X_SHAPES for t in S.STRONG8]
    A = S.xs_threshold(S.WEAK2)
    lb = S.lumped_threshold(S.WEAK2)
    lm = 0.5 * (lb[0] + lb[1])
    st3 = {"xs_J": S.xs_threshold("M50_ST_Exp3"), "bracket_3d_J": [9767.2, 10795.3]}
    T = {"test": S.WEAK2, "xs_threshold_J": A, "lumped_bracket_J": list(lb), "lumped_mid_J": lm,
         "first_runs_J": [S.t_spec(s)["E_delivered_J"] for s in S.T_FIRST],
         "ratio_if_closed_by_first_two": A / lm,
         "ratio_range_if_closed_by_first_two": [A * 0.95 / lb[1], A * 1.05 / lb[0]],
         "ratio_if_5_to_15_above": 1.10 * A / lm, "ratio_if_5_to_15_below": 0.90 * A / lm}
    a1x = [r for r in a1 if r["test"] in S.STRONG8 and r["shape"] == "con" and r["C8_3d"] and r["C8_xs"]]
    out = {"N": N, "X": X, "T": T, "ST_Exp3": st3, "leads_near_thresholds": leads_near_thresholds(recs15),
           "a1_constant_power_with_both_C8": [{"test": r["test"], "tau_s": r["tau_d_s"], "E_J": r["E_J"],
                                                "t_C8_3d_s": r["t_C8_3d_s"], "t_C8_xs_s": r["t_C8_xs_s"],
                                                "xs_minus_3d_s": r["t_C8_xs_s"] - r["t_C8_3d_s"]} for r in a1x]}
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=1, default=float)
    print("wrote", OUT)
    for n in N:
        print("%-12s E_x %7.1f (%s) xs(t_m+10) %s est10 %s est20 %s d_def %s d10 %s d20 %s known (%s, %s] lumped %.1f "
              "exceeded %s" % (n["test"][4:], n["E_x_J"], n["E_x_status"], _f(n["xs_E_at_tm_plus_10_J"]),
                 _f(n["estimate_3d_need_J_by_lead_s"]["10"]), _f(n["estimate_3d_need_J_by_lead_s"]["20"]),
                 _p(n["d_definition_only"]), _p(n["d_by_lead"]["10"]), _p(n["d_by_lead"]["20"]),
                 _f(n["known_lower_J"]), _f(n["known_upper_J"]), n["lumped_need_J"], n["lumped_need_already_exceeded"]))
    for x in X:
        print("X %-12s %-22s E_x %7.1f by_t %7.1f d_by_t lead10 %s lead20 %s known (%s, %s] lumped %.1f exceeded %s"
              % (x["test"][4:], x["delivery"], x["E_x_J"], x["E_x_by_t_J"], _p(x["d_by_t_by_lead"]["10"]),
                 _p(x["d_by_t_by_lead"]["20"]), _f(x["known_lower_J"]), _f(x["known_upper_J"]), x["lumped_need_J"],
                 x["lumped_need_already_exceeded"]))
    print("T", json.dumps(T, default=float))
    for r in out["leads_near_thresholds"]:
        print("lead", r)


def _f(v):
    return "%.1f" % v if v is not None else "-"


def _p(v):
    return "%+.1f%%" % (100 * v) if v is not None else "-"


if __name__ == "__main__":
    main()
