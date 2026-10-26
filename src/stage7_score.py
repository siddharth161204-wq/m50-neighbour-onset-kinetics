#!/usr/bin/env python3
"""Stage 7: Part B, the ignition conditions scored test by test, and the scoring of P1 to P8 by the rules of
predictions_stage7.md (DECISIONS.md D67 to D70).

Reads results/stage7_triggers.json, results/stage7_separator.json, results/stage7_eventlist.json and the records and
series in results/stage7_runs/ and results/stage7_series/. Writes:
  results/stage7_crossings.csv   one row per run: every clock's peak, its time and its crossings of 138.5, 150 and
                                 255.7 C, the runs' own stop crossings, and, for an event run, the peaks after it;
  results/stage7_pertest.csv     one row per test, contact and criterion: predicted outcome and time, measured outcome
                                 and time, the class (hit, miss, false alarm, correct rejection) and the time error;
  results/stage7_events.csv      one row per Part C run: the neighbour's peaks after the event beside the measured
                                 neighbour maximum;
  results/stage7_scorecard.json  the seven criteria by three contacts, P1 to P8, the sensitivities, V3, V4.
With runs missing it scores what the records allow and says which sets are incomplete.
Usage: python3 stage7_score.py [--res DIR] [--predictions-commit HASH] [--no-self-heating]
"""
import argparse, csv, glob, json, math, os, statistics, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage7_inputs as IN          # noqa: E402
import stage7_criteria as CQ        # noqa: E402

CONTACTS = ("low", "central", "high")
REGISTERED = "central"
P8_RANGE = None                     # the measured range of the propagating neighbours' maxima (set from the inputs)
V3_TOL = 0.01                       # 1 % (the brief)
ENERGY_TOL = 1e-9
T_AMB_C = IN.T_AMB_C
K0 = 273.15


def load(res):
    recs, failed = {}, []
    for f in glob.glob(os.path.join(res, "stage7_runs", "*.json")):
        r = json.load(open(f))
        (failed.append(r["id"]) if r.get("failed") else recs.__setitem__(r["id"], r))
    return recs, sorted(failed)


def series_of(res, rid):
    p = os.path.join(res, "stage7_series", rid + ".npz")
    if not os.path.exists(p):
        return None
    z = np.load(p)
    return {k: z[k] for k in z.files}


def index(recs):
    """(set, test, contact, tau) -> record, for Part A; Part C by (set, test, contact, criterion, mesh, step), so that
    V3's two runs of one test keep a row each."""
    a, c = {}, {}
    for r in recs.values():
        if r["set"] in ("pertest", "duration", "aged"):
            a[(r["set"], r["test"], r["h"], round(r["tau"], 2))] = r
        else:
            c[(r["set"], r["test"], r["h"], r["event"]["criterion"], r.get("refine", 1.0), r.get("dt_scale", 1.0))] = r
    return a, c


def classify(pred, meas):
    if pred and meas:
        return "hit"
    if not pred and meas:
        return "miss"
    if pred and not meas:
        return "false alarm"
    return "correct rejection"


def tally(rows):
    d = {"n": len(rows), "predicted": sum(r["predicted"] for r in rows),
         "hits": sum(r["class"] == "hit" for r in rows), "misses": sum(r["class"] == "miss" for r in rows),
         "false_alarms": sum(r["class"] == "false alarm" for r in rows),
         "correct_rejections": sum(r["class"] == "correct rejection" for r in rows)}
    d["hit_rate"] = (d["hits"] + d["correct_rejections"]) / d["n"] if d["n"] else None
    err = [r["error_s"] for r in rows if r["error_s"] is not None]
    d["time_errors_s"] = {r["test"]: r["error_s"] for r in rows if r["error_s"] is not None}
    d["time_error_range_s"] = [min(err), max(err)] if err else None
    d["time_error_median_s"] = statistics.median(err) if err else None
    d["within_60s"] = sum(abs(e) <= 60.0 for e in err)
    d["by_connection"] = {c: sum(r["predicted"] for r in rows if r["connection"] == c) for c in ("series", "parallel")}
    pt = [r["predicted_time_s"] for r in rows if r["predicted_time_s"] is not None]
    d["predicted_time_range_s"] = [min(pt), max(pt)] if pt else None
    return d


def pertest_rows(A, tests, tau, contacts=CONTACTS, criteria=tuple(CQ.CRITERIA), sep_level=None):
    """One row per test, contact and criterion. sep_level, if given, reads C4, C5 and C7 at another melting
    temperature (the D71 sensitivity) from the stored series."""
    rows, missing = [], []
    for crit in criteria:
        set_, clock, level, source = CQ.CRITERIA[crit]
        for h in contacts:
            for t in tests:
                rec = A.get((set_, t["test"], h, round(tau, 2)))
                if rec is None:
                    missing.append((crit, h, t["test"]))
                    continue
                if sep_level is not None and level == "sep":
                    s = rec["_series"]
                    import stage6_crossings as CR
                    hs = CR.histories(s)
                    tc = CR.first_crossing(*hs[clock], sep_level + K0)
                    pred, tp = tc is not None, tc
                else:
                    pred, tp = CQ.crossing(rec, crit)
                meas, tm = t["propagated"], t["time_s"]
                cls = classify(pred, meas)
                rows.append({"test": t["test"], "connection": t["connection"], "contact": h, "criterion": crit,
                             "criterion_text": CQ.CRITERIA_TEXT[crit], "run": rec["id"], "predicted": pred,
                             "predicted_time_s": tp, "measured": meas, "measured_time_s": tm, "class": cls,
                             "error_s": (tp - tm) if cls == "hit" else None,
                             "role": "registered" if h == REGISTERED else "bracket"})
    return rows, missing


def scorecard_table(rows):
    out = {}
    for crit in CQ.CRITERIA:
        out[crit] = {"text": CQ.CRITERIA_TEXT[crit]}
        for h in CONTACTS:
            rs = [r for r in rows if r["criterion"] == crit and r["contact"] == h]
            if rs:
                out[crit][h] = tally(rs)
    return out


def p6(A, tests, tau, h):
    """Within each connection, the tests in order of trigger energy; an inversion is a pair whose lower-energy test
    has the hotter lumped neighbour. A lumped neighbour that reaches 255.7 C stops there (D35): it ranks above every
    one that does not, and two that do rank by their crossing times, the earlier hotter."""
    out = {"contact": h, "by_connection": {}}
    total_inv = 0
    for conn in ("series", "parallel"):
        rs = []
        for t in tests:
            if t["connection"] != conn:
                continue
            r = A.get(("pertest", t["test"], h, round(tau, 2)))
            if r is None:
                return None
            ll = r["lumped"]
            rs.append({"test": t["test"], "E_J": r["E_body_J"], "peak_C": ll["peak_C"],
                       "reaches": ll["propagated"], "t_s": ll.get("t_prop_s")})
        rs.sort(key=lambda x: x["E_J"])

        def hotter(a, b):           # True if a is strictly hotter than b
            if a["reaches"] and b["reaches"]:
                return a["t_s"] < b["t_s"]
            if a["reaches"] != b["reaches"]:
                return a["reaches"]
            return a["peak_C"] > b["peak_C"]
        inv, ties = [], []
        for i in range(len(rs)):
            for j in range(i + 1, len(rs)):
                if hotter(rs[i], rs[j]):
                    inv.append([rs[i]["test"], rs[j]["test"]])
                elif not hotter(rs[j], rs[i]):
                    ties.append([rs[i]["test"], rs[j]["test"]])
        total_inv += len(inv)
        out["by_connection"][conn] = {"order_by_energy": [x["test"] for x in rs],
                                      "lumped_peaks_C": [x["peak_C"] for x in rs],
                                      "reaches_255_7": [x["reaches"] for x in rs], "inversions": inv, "ties": ties}
    out["inversions"] = total_inv
    out["held"] = total_inv == 0
    return out


def main(res, predictions_commit=None, self_heating=True):
    tests = IN.tests()
    meas = IN.measured()
    lo8, hi8 = meas["neighbour_max_propagated_range_C"]
    tr = json.load(open(os.path.join(res, "stage7_triggers.json")))
    L = tr["levels"]
    tm = L["tau_median_s"]
    recs, failed = load(res)
    for r in recs.values():
        r["_series"] = None
    A, C = index(recs)
    sc = {"predictions": "predictions_stage7.md", "predictions_commit": predictions_commit}
    # completeness
    import stage7_run as R7
    want_a = R7.build_part_a({r["test"]: r["E_J"] for r in tr["rows"]})
    evp = os.path.join(res, "stage7_eventlist.json")
    want_c = json.load(open(evp))["runs"] if os.path.exists(evp) else []
    ended = set(recs) | set(failed)
    sets = {}
    for s in R7.SETS:
        ids = [x["id"] for x in want_a + want_c if x["set"] == s]
        sets[s] = {"total": len(ids), "done": sum(i in recs for i in ids), "failed": sum(i in failed for i in ids),
                   "complete": bool(ids) and all(i in ended for i in ids)}
    sc["complete"] = sets
    sc["failed"] = failed
    # series for the sensitivities and P5
    for r in recs.values():
        if r["set"] in ("pertest", "aged", "duration") and r["h"] == "central":
            r["_series"] = series_of(res, r["id"])
    # ------------------------------------------------------------ Part B
    rows, missing = pertest_rows(A, tests, tm)
    sc["missing_rows"] = len(missing)
    table = scorecard_table(rows)
    sc["criteria"] = table
    flat = [dict(r, predicted="Yes" if r["predicted"] else "No", measured="Yes" if r["measured"] else "No")
            for r in rows]
    fields = ["test", "connection", "contact", "criterion", "criterion_text", "role", "run", "predicted",
              "predicted_time_s", "measured", "measured_time_s", "class", "error_s"]
    with open(os.path.join(res, "stage7_pertest.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in flat:
            w.writerow(r)
    # sensitivities at the central contact: the two other releases, and the melting temperature's spread (D71)
    sens = {}
    for tau in (L["tau_s"][0], L["tau_s"][-1]):
        A2 = {(("pertest",) + k[1:]): v for k, v in A.items() if k[0] == "duration" and k[3] == round(tau, 2)}
        rs, miss = pertest_rows(A2, tests, tau, contacts=("central",), criteria=("C1", "C2", "C3", "C4", "C5"))
        if not miss:
            sens[f"release_{tau:.2f}s"] = {c: tally([r for r in rs if r["criterion"] == c])
                                           for c in ("C1", "C2", "C3", "C4", "C5")}
    sp = os.path.join(res, "stage7_separator.json")
    if os.path.exists(sp):
        sepd = json.load(open(sp))
        for name in ("p2.5_C", "p97.5_C"):
            lv = sepd[name]
            ok = all(A.get((s, t["test"], "central", round(tm, 2))) is not None and
                     A[(s, t["test"], "central", round(tm, 2))]["_series"] is not None
                     for s in ("pertest", "aged") for t in tests)
            if ok:
                rs, miss = pertest_rows(A, tests, tm, contacts=("central",), criteria=("C4", "C5", "C7"), sep_level=lv)
                sens[f"melting_{name[:-2]}_{lv:.2f}C"] = {c: tally([r for r in rs if r["criterion"] == c])
                                                         for c in ("C4", "C5", "C7")}
    sc["sensitivities_central"] = sens
    # ------------------------------------------------------------ the predictions
    cen = lambda crit: [r for r in rows if r["criterion"] == crit and r["contact"] == REGISTERED]
    have = lambda crit: len(cen(crit)) == len(tests)
    if have("C1"):
        n1 = sum(r["predicted"] for r in cen("C1"))
        sc["P1"] = {"held": n1 < 9, "verdict": "held" if n1 < 9 else "failed", "predicted": n1, "of": len(tests),
                    "by_contact": {h: table["C1"][h]["predicted"] for h in CONTACTS if h in table["C1"]}}
    if have("C3"):
        t3 = table["C3"][REGISTERED]
        part_a = t3["predicted"] >= 9
        part_b = t3["hits"] + t3["correct_rejections"] >= 10
        sc["P2"] = {"held": part_a and part_b, "verdict": "held" if (part_a and part_b) else "failed",
                    "predicted": t3["predicted"], "hits_plus_correct_rejections": t3["hits"] + t3["correct_rejections"],
                    "part_count_held": part_a, "part_rate_held": part_b, "tally": t3}
        hits = [r for r in cen("C3") if r["class"] == "hit"]
        within = [r for r in hits if abs(r["error_s"]) <= 60.0]
        ok3 = len(hits) > 0 and 2 * len(within) >= len(hits)
        sc["P3"] = {"held": ok3, "verdict": "held" if ok3 else "failed", "hits": len(hits), "within_60s": len(within),
                    "errors_s": {r["test"]: r["error_s"] for r in hits}}
    if have("C4"):
        n4 = sum(r["predicted"] for r in cen("C4"))
        sc["P4"] = {"held": n4 > 9, "verdict": "held" if n4 > 9 else "failed", "predicted": n4, "measured": meas["propagated"]}
    # P5
    if have("C4") and have("C5") and have("C7"):
        aged_c5 = []
        for t in tests:
            r = A[("aged", t["test"], REGISTERED, round(tm, 2))]
            aged_c5.append(r["stage7"]["clocks"]["lumped"]["t_sep_s"] is not None)
        c4f = [r["predicted"] for r in cen("C4")]
        c4a = [r["predicted"] for r in cen("C7")]
        c5f = [r["predicted"] for r in cen("C5")]
        changed = [t["test"] for t, a, b in zip(tests, c4f, c4a) if a != b]
        changed5 = [t["test"] for t, a, b in zip(tests, c5f, aged_c5) if a != b]
        part_b = not changed and not changed5
        d5 = {"C4_changed": changed, "C5_changed": changed5, "part_verdicts_held": part_b}
        if self_heating:
            sh, lowered, compared = {}, 0, 0
            for t in tests:
                f = A[("pertest", t["test"], REGISTERED, round(tm, 2))]
                g = A[("aged", t["test"], REGISTERED, round(tm, 2))]
                if f["_series"] is None or g["_series"] is None:
                    sh = None
                    break
                tf, Tf, rf = CQ.first_self_heating(f["_series"])
                ta, Ta, ra = CQ.first_self_heating(g["_series"], sei0=IN.SEI_AGED)
                if Tf is None and Ta is None:
                    v = None
                else:
                    compared += 1
                    v = (Ta is not None) and (Tf is None or Ta < Tf)
                    lowered += bool(v)
                sh[t["test"]] = {"fresh_t_s": tf, "fresh_T_C": Tf, "fresh_reaction": rf, "aged_t_s": ta, "aged_T_C": Ta,
                                 "aged_reaction": ra, "lowered": v}
            if sh is not None:
                part_a = compared > 0 and lowered == compared
                d5.update({"self_heating_0.15Kpm": sh, "compared": compared, "lowered": lowered,
                           "part_lowered_held": part_a})
                d5["held"] = part_a and part_b
                d5["verdict"] = "held" if d5["held"] else "failed"
        sc["P5"] = d5
    # P6
    v6 = p6(A, tests, tm, REGISTERED)
    if v6 is not None:
        v6["bracket"] = {h: (lambda x: None if x is None else {"inversions": x["inversions"], "held": x["held"]})(p6(A, tests, tm, h))
                         for h in ("low", "high")}
        v6["verdict"] = "held" if v6["held"] else "failed"
        sc["P6"] = v6
    # P7
    if all(have(c) for c in CQ.CRITERIA):
        diffs = {c: table[c][REGISTERED]["by_connection"] for c in CQ.CRITERIA}
        bad = [c for c, d in diffs.items() if abs(d["series"] - d["parallel"]) > 1]
        sc["P7"] = {"held": not bad, "verdict": "held" if not bad else "failed", "counts": diffs, "split_by_more_than_one": bad,
                    "measured": meas["propagated_by_connection"]}
    # ------------------------------------------------------------ Part C
    ev_rows = []
    for (s, test, h, crit, _refine, _dt_scale), r in sorted(C.items()):
        q = r["stage7"].get("after_event") or {}
        t = meas["by_test"][test]
        # D68 (3): until 0.1 s before its event, an event run repeats the Part A run its event time was read from. Not
        # for V3's runs, whose mesh or steps differ from that run's by design (D75 (3))
        same, span = None, None
        base = recs.get(r["event"].get("from", "")) if s in ("event", "eventlow") else None
        se, sb = series_of(res, r["id"]), (series_of(res, base["id"]) if base else None)
        if se is not None and sb is not None:
            # compared over the span both runs stored before 0.1 s before the event: a Part A run whose hot spot
            # reached 255.7 C stopped there (D35) and stored its resolved history only until then (D75 (3))
            t0 = r["event"]["t_s"] - 0.1
            tr_, tp_, tl_ = (min(t0, float(sb[k][-1])) for k in ("t", "probe_t", "t_lumped"))
            me, mb = se["t"] < tr_, sb["t"] < tr_
            pe, pb_ = se["probe_t"] < tp_, sb["probe_t"] < tp_
            le, lb = se["t_lumped"] < tl_, sb["t_lumped"] < tl_
            same = bool(me.sum() == mb.sum() and pe.sum() == pb_.sum() and le.sum() == lb.sum()
                        and all(np.array_equal(se[k][me], sb[k][mb]) for k in ("t", "Tmax", "Tmean", "T1"))
                        and all(np.array_equal(se[k][pe], sb[k][pb_]) for k in ("probe_t", "probe_toward", "probe_away"))
                        and all(np.array_equal(se[k][le], sb[k][lb]) for k in ("t_lumped", "T_lumped")))
            span = tr_
        ev_rows.append({"run": r["id"], "set": s, "test": test, "connection": r["connection"], "contact": h,
                        "criterion": crit, "E_event_J": r["event"]["E_J"], "t_event_s": r["event"]["t_s"],
                        "hot_after_C": q.get("hot_C"), "t_hot_after_s": q.get("t_hot_s"),
                        "mean_after_C": q.get("mean_C"), "away_after_C": q.get("away_C"),
                        "toward_after_C": q.get("toward_C"), "lumped_after_C": q.get("lumped_C"),
                        "t_lumped_after_s": q.get("t_lumped_s"),
                        "measured_propagated": "Yes" if t["propagated"] else "No",
                        "measured_neighbour_max_C": t["neighbour_max_C"],
                        "hot_inside_measured_range": (q.get("hot_C") is not None and lo8 <= q["hot_C"] <= hi8),
                        "lumped_inside_measured_range": (q.get("lumped_C") is not None and lo8 <= q["lumped_C"] <= hi8),
                        "delivered_resolved_J": q.get("delivered_resolved_J"), "delivered_lumped_J": q.get("delivered_lumped_J"),
                        "residual_resolved": r["resolved"]["energy_residual_rel"],
                        "residual_lumped": r["lumped"]["energy_residual_rel"],
                        "reaction_heat_resolved_J": r["resolved"]["in_rxn_J"], "reaction_heat_lumped_J": r["lumped"]["reaction_heat_J"],
                        "t_end_s": r["resolved"]["t_end_s"], "repeats_part_a_until_event": same,
                        "repeat_compared_until_s": span,
                        "peaked_before_end": all(x is not None and x < r["resolved"]["t_end_s"] - 1.0 for x in
                                                 (q.get("t_hot_s"), q.get("t_lumped_s"), q.get("t_mean_s"), q.get("t_away_s"))),
                        "wall_s": r["wall_s"]})
    if ev_rows:
        with open(os.path.join(res, "stage7_events.csv"), "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(ev_rows[0].keys()))
            w.writeheader()
            for r in ev_rows:
                w.writerow(r)
    cen8 = [r for r in ev_rows if r["set"] == "event" and r["contact"] == REGISTERED]
    if sets["event"]["complete"] and cen8:
        k = sum(r["hot_inside_measured_range"] for r in cen8)
        ok8 = 2 * k >= len(cen8)
        sc["P8"] = {"held": ok8, "verdict": "held" if ok8 else "failed", "runs": len(cen8), "inside": k,
                    "every_clock_peaked_before_the_end": all(r["peaked_before_end"] for r in ev_rows),
                    "measured_range_C": [lo8, hi8],
                    "hot_after_range_C": [min(r["hot_after_C"] for r in cen8), max(r["hot_after_C"] for r in cen8)],
                    "lumped_after_range_C": [min(r["lumped_after_C"] for r in cen8), max(r["lumped_after_C"] for r in cen8)],
                    "lumped_inside": sum(r["lumped_inside_measured_range"] for r in cen8),
                    "by_criterion": {c: {"runs": sum(r["criterion"] == c for r in cen8),
                                         "inside": sum(r["hot_inside_measured_range"] for r in cen8 if r["criterion"] == c)}
                                     for c in ("C4", "C5")}}
        low = [r for r in ev_rows if r["set"] == "eventlow"]
        if low:
            sc["P8"]["lower_bracket_63_36kJ"] = {"runs": len(low), "inside": sum(r["hot_inside_measured_range"] for r in low),
                                                 "hot_after_range_C": [min(r["hot_after_C"] for r in low),
                                                                       max(r["hot_after_C"] for r in low)]}
        brk = [r for r in ev_rows if r["set"] == "event" and r["contact"] != REGISTERED]
        if brk:
            sc["P8"]["bracket_contacts"] = {"runs": len(brk), "inside": sum(r["hot_inside_measured_range"] for r in brk)}
    # ------------------------------------------------------------ V3 and V4
    v3 = {}
    for r in recs.values():
        if r["set"] != "v3":
            continue
        b = recs.get(r["v3_base"])
        if b is None:
            continue
        tag = "refine2" if r["refine"] == 2.0 else "dthalf"
        hb, hv = b["resolved"]["after_event"]["Tmax_C"], r["resolved"]["after_event"]["Tmax_C"]
        lb, lv = b["lumped"]["after_event"]["T_C"], r["lumped"]["after_event"]["T_C"]
        q = abs(hv - hb) / (hb - T_AMB_C)
        v3[tag] = {"base": b["id"], "check": r["id"], "hot_after_base_C": hb, "hot_after_check_C": hv,
                   "relative_change_of_rise": q, "pass": q < V3_TOL, "lumped_after_base_C": lb, "lumped_after_check_C": lv,
                   "lumped_relative_change_of_rise": abs(lv - lb) / (lb - T_AMB_C), "wall_s": r["wall_s"]}
    sc["V3"] = {"cases": v3, "acceptance": V3_TOL, "pass": len(v3) == 2 and all(c["pass"] for c in v3.values())}
    allr = list(recs.values())
    res_r = [abs(r["resolved"]["energy_residual_rel"]) for r in allr]
    res_l = [abs(r["lumped"]["energy_residual_rel"]) for r in allr if r["lumped"].get("energy_residual_rel") is not None]
    dl = [abs(r["resolved"]["event"]["delivered_J"] - r["event"]["E_J"]) / r["event"]["E_J"]
          for r in allr if r.get("event") and r["resolved"].get("event")]
    sc["V4"] = {"max_abs_residual_resolved": max(res_r) if res_r else None,
                "max_abs_residual_lumped": max(res_l) if res_l else None, "n_resolved": len(res_r), "n_lumped": len(res_l),
                "max_event_delivery_error_rel": max(dl) if dl else None, "acceptance": ENERGY_TOL,
                "event_runs_repeating_part_a_until_event": sum(r["repeats_part_a_until_event"] is True for r in ev_rows
                                                               if r["set"] in ("event", "eventlow")),
                "event_runs_compared": sum(r["repeats_part_a_until_event"] is not None for r in ev_rows
                                           if r["set"] in ("event", "eventlow")),
                "event_runs": sum(r["set"] in ("event", "eventlow") for r in ev_rows),
                "event_runs_compared_until_their_part_a_runs_stop": sum(
                    r["repeat_compared_until_s"] is not None and r["repeat_compared_until_s"] < r["t_event_s"] - 0.1
                    for r in ev_rows if r["set"] in ("event", "eventlow")),
                "pass": bool(res_r) and max(res_r) < ENERGY_TOL and (not res_l or max(res_l) < ENERGY_TOL)}
    # ------------------------------------------------------------ the per-run file
    keys = ("id", "set", "test", "connection", "h", "tau", "E_body_J", "sei0", "refine", "dt_scale", "T1max_C", "t_T1max_s",
            "wall_s", "model")
    out_rows = []
    for r in sorted(allr, key=lambda x: x["id"]):
        row = {k: r.get(k) for k in keys}
        q = r["stage7"]
        for c in CQ.CLOCKS:
            d = q["clocks"][c]
            row.update({f"{c}_peak_C": d["peak_C"], f"{c}_t_peak_s": d["t_peak_s"],
                        **{f"{c}_t_{n}_s": d.get(f"t_{n}_s") for n in CQ.LEVELS_C}})
        row.update({"hot_t_stop_s": q["stop"]["hot_t_s"], "lumped_t_stop_s": q["stop"]["lumped_t_s"],
                    "resolved_t_end_s": q["stop"]["resolved_t_end_s"], "lumped_t_end_s": q["stop"]["lumped_t_end_s"],
                    "residual_resolved": r["resolved"]["energy_residual_rel"],
                    "residual_lumped": r["lumped"].get("energy_residual_rel"),
                    "reaction_heat_resolved_J": r["resolved"]["in_rxn_J"],
                    "reaction_heat_lumped_J": r["lumped"]["reaction_heat_J"]})
        if r.get("event"):
            ae = q.get("after_event") or {}
            row.update({"event_criterion": r["event"]["criterion"], "event_t_s": r["event"]["t_s"],
                        "event_E_J": r["event"]["E_J"], "hot_after_C": ae.get("hot_C"), "lumped_after_C": ae.get("lumped_C")})
        out_rows.append(row)
    if out_rows:
        fields = list(dict.fromkeys(k for r in out_rows for k in r))
        with open(os.path.join(res, "stage7_crossings.csv"), "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            for r in out_rows:
                w.writerow(r)
    json.dump(sc, open(os.path.join(res, "stage7_scorecard.json"), "w"), indent=1, default=float)
    brief = {k: v.get("verdict") for k, v in sc.items() if k.startswith("P") and isinstance(v, dict)}
    print(json.dumps(brief, indent=1))
    return sc


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", default=os.path.join(HERE, "..", "results"))
    ap.add_argument("--predictions-commit", default=None)
    ap.add_argument("--no-self-heating", action="store_true")
    a = ap.parse_args()
    main(a.res, a.predictions_commit, self_heating=not a.no_self_heating)
