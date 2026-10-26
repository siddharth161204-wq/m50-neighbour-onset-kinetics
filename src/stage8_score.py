#!/usr/bin/env python3
"""Stage 8 scoring (predictions_stage8.md; DECISIONS.md D78 to D82): the thresholds, Part C's scorecard, Part D's
changes and the verdicts on P1 to P8, from the Stage 8 records and Stage 7's pertest records at the central contact
(f = 0, read and not rerun).

Writes results/stage8_thresholds.csv (one row per test), results/stage8_scorecard.json (Part C, with f = 0 from
Stage 7 beside it), results/stage8_partd.json and results/stage8_verdicts.json.
Usage: python3 stage8_score.py [--runs DIR] [--out DIR]
"""
import argparse, csv, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage8_inputs as IN               # noqa: E402
import stage8_search as SR               # noqa: E402
import stage8_run as R8                  # noqa: E402

RES = os.path.join(HERE, "..", "results")
K0 = 273.15


# ------------------------------------------------------------------------------------------------ helpers
def fs_text(fs):
    if fs is None:
        return ""
    if fs["status"] == "zero":
        return "0"
    if fs["status"] == "above":
        return "above 1"
    if fs["status"] == "bracket":
        return f"({fs['lo']:.6g}, {fs['hi']:.6g}]"
    return fs["status"]


def fs_mid(fs):
    """A single value for plotting only: 0, the bracket's middle, or None above 1."""
    if fs["status"] == "zero":
        return 0.0
    if fs["status"] == "bracket":
        return 0.5 * (fs["lo"] + fs["hi"])
    return None


def lowering(a, b):
    """The interval of f*(a) - f*(b) from the two brackets (a the reference): (smallest, largest); None if either is
    above 1 or unfinished."""
    def lohi(fs):
        if fs["status"] == "zero":
            return 0.0, 0.0
        if fs["status"] == "bracket":
            return fs["lo"], fs["hi"]
        return None
    x, y = lohi(a), lohi(b)
    if x is None or y is None:
        return None
    return x[0] - y[1], x[1] - y[0]


def relation(ref, var):
    """Whether var's f* is established lower than ref's, higher, the same bracket, or equal (both 0)."""
    if ref["status"] == "zero" and var["status"] == "zero":
        return "equal (both 0)"
    lv = lowering(ref, var)
    if lv is None:
        if ref["status"] == "above" and var["status"] == "above":
            return "both above 1"
        if ref["status"] == "above":
            return "lower"
        if var["status"] == "above":
            return "higher"
        return "unfinished"
    if lv[0] >= -1e-12 and lv[1] > 1e-12:
        return "lower"
    if lv[1] <= 1e-12 and lv[0] < -1e-12:
        return "higher"
    return "same bracket"


def measured():
    return {t["test"]: t for t in R8.tests()}


def classify(pred, meas):
    if pred and meas:
        return "hit"
    if pred:
        return "false alarm"
    if meas:
        return "miss"
    return "correct rejection"


# ------------------------------------------------------------------------------------------------ the thresholds
def thresholds(recs, states):
    ms = measured()
    s7 = R8.stage7_zero()
    sens = R8.sens_tests()
    rows = []
    for t in R8.tests():
        x = t["test"]
        fa1 = SR.f_star(states[f"A_C1_{x}"])
        fa2 = SR.f_star(states[f"A_C2_{x}"])
        row = {"test": x, "connection": t["connection"], "E_b_J": t["E_b_J"], "E_e_J": R8.ratios()["central"] * t["E_b_J"],
               "propagated": ms[x]["propagated"], "time_s": ms[x]["time_s"], "stage7_C1": s7[x]["C1"],
               "stage7_C2": s7[x]["C2"], "stage7_C3": s7[x]["C3"], "fC1": fa1, "fC2": fa2,
               "fC3_exploratory": f3_interp(x, recs, s7[x]), "sensitivity": x in sens, "variants": {}}
        if x in sens:
            for set_ in ("dur10_c1", "dur10_c2", "dur60_c1", "dur60_c2", "capend_c1", "ratiolow_c1", "ratiolow_c2",
                         "ratiohigh_c1", "ratiohigh_c2"):
                ref = fa1 if set_.endswith("c1") else fa2
                v = SR.f_star(states[f"{set_}_{x}"])
                row["variants"][set_] = {"f": v, "relation": relation(ref, v), "lowering": lowering(ref, v)}
            row["variants"]["capend_c2"] = {"f": fa2, "relation": "unchanged by construction",
                                            "lowering": (0.0, 0.0) if fa2["status"] != "above" else None}
        if t["connection"] == "parallel":
            for set_ in ("elec05_c1", "elec20_c1"):
                v = SR.f_star(states[f"{set_}_{x}"])
                row["variants"][set_] = {"f": v, "relation": relation(fa1, v), "lowering": lowering(fa1, v)}
        rows.append(row)
    return rows


def f3_interp(test, recs, s7):
    """A5, exploratory: the fraction at which the lumped neighbour first reaches 150 C, from f = 0 (Stage 7), the
    first round and the C2 chain's runs: the bracket (the largest fraction tried without the crossing, the smallest
    with it), and the fraction at which the lumped neighbour's peak, linear in f between those two runs, reaches 150 C
    (a run stopped at 255.7 C enters with 255.7 C, a lower bound of its peak)."""
    pts = {0.0: (s7["C3"], s7["lumped_peak_C"], s7["C2"])}
    for r in recs.values():
        if r.get("failed") or r["test"] != test or r["set"] not in ("first", "c2"):
            continue
        q = r["stage8"]["clocks"]["lumped"]
        pts[SR.key(r["f"])] = (q["t_150_s"] is not None, r["lumped"]["peak_C"], r["lumped"]["propagated"])
    if pts[0.0][0]:
        return {"status": "zero", "lo": 0.0, "hi": 0.0, "value": 0.0}
    no = [f for f, v in pts.items() if not v[0]]
    yes = [f for f, v in pts.items() if v[0]]
    if not yes:
        return {"status": "above tried", "lo": max(no), "hi": None, "value": None}
    lo, hi = max(no), min(yes)
    if lo > hi:
        return {"status": "broken", "lo": lo, "hi": hi, "value": None}
    p_lo = pts[lo][1]
    p_hi = IN.LEVEL_PROP_C if pts[hi][2] else pts[hi][1]
    val = lo + (hi - lo) * (IN.LEVEL_150_C - p_lo) / (p_hi - p_lo) if p_hi > p_lo else hi
    return {"status": "interpolated", "lo": lo, "hi": hi, "value": val, "peak_lo_C": p_lo, "peak_hi_C": p_hi,
            "hi_stopped_at_255_7": bool(pts[hi][2])}


def write_thresholds(rows, path):
    cols = ["test", "connection", "E_b_J", "E_e_J", "propagated", "time_to_propagation_s", "stage7_C1", "stage7_C2",
            "stage7_C3", "fC1", "fC1_lo", "fC1_hi", "fC2", "fC2_lo", "fC2_hi", "fC3_exploratory", "fC3_lo", "fC3_hi"]
    vsets = ["dur10_c1", "dur10_c2", "dur60_c1", "dur60_c2", "capend_c1", "capend_c2", "ratiolow_c1", "ratiolow_c2",
             "ratiohigh_c1", "ratiohigh_c2", "elec05_c1", "elec20_c1"]
    for v in vsets:
        cols += [f"{v}", f"{v}_relation", f"{v}_lowering_min", f"{v}_lowering_max"]
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            d = {"test": r["test"], "connection": r["connection"], "E_b_J": repr(r["E_b_J"]), "E_e_J": repr(r["E_e_J"]),
                 "propagated": "yes" if r["propagated"] else "no",
                 "time_to_propagation_s": "" if r["time_s"] is None else r["time_s"],
                 "stage7_C1": r["stage7_C1"], "stage7_C2": r["stage7_C2"], "stage7_C3": r["stage7_C3"],
                 "fC1": fs_text(r["fC1"]), "fC1_lo": r["fC1"]["lo"], "fC1_hi": r["fC1"]["hi"],
                 "fC2": fs_text(r["fC2"]), "fC2_lo": r["fC2"]["lo"], "fC2_hi": r["fC2"]["hi"],
                 "fC3_exploratory": "" if r["fC3_exploratory"]["value"] is None else repr(r["fC3_exploratory"]["value"]),
                 "fC3_lo": r["fC3_exploratory"]["lo"], "fC3_hi": r["fC3_exploratory"]["hi"]}
            for v in vsets:
                x = r["variants"].get(v)
                if x is None:
                    continue
                d[v] = fs_text(x["f"])
                d[f"{v}_relation"] = x["relation"]
                if x["lowering"] is not None:
                    d[f"{v}_lowering_min"], d[f"{v}_lowering_max"] = x["lowering"]
            w.writerow(d)


# ------------------------------------------------------------------------------------------------ Part C
def crossing(rec, crit):
    if crit == "C1":
        return rec["resolved"]["propagated"], rec["resolved"].get("t_prop_s")
    if crit == "C2":
        return rec["lumped"]["propagated"], rec["lumped"].get("t_prop_s")
    t = rec["stage8"]["clocks"]["lumped"]["t_150_s"]
    return t is not None, t


def scorecard(recs):
    ms = measured()
    s7 = R8.stage7_zero()
    out = {"fractions": list(IN.COMMON_F), "criteria": {c: IN.CRITERIA_TEXT[c] for c in IN.CRITERIA},
           "by_fraction": {}, "stage7_f0": {}}
    first = {(r["test"], SR.key(r["f"])): r for r in recs.values() if r["set"] == "first" and not r.get("failed")}
    for f in [0.0] + list(IN.COMMON_F):
        card = {}
        for crit in IN.CRITERIA:
            per, counts, errs = {}, {"hit": 0, "miss": 0, "false alarm": 0, "correct rejection": 0}, []
            for t in R8.tests():
                x = t["test"]
                if f == 0.0:
                    p, tc = s7[x][crit], s7[x][f"t_{crit}_s"]
                    actual = 0.0
                else:
                    rec = first.get((x, SR.key(f)))
                    if rec is None:
                        per[x] = {"missing": True}
                        continue
                    p, tc = crossing(rec, crit)
                    actual = rec["f"]
                cl = classify(p, ms[x]["propagated"])
                counts[cl] += 1
                e = (tc - ms[x]["time_s"]) if cl == "hit" else None
                if e is not None:
                    errs.append(e)
                per[x] = {"predicted": bool(p), "t_s": tc, "class": cl, "error_s": e, "f_actual": actual,
                          "measured_s": ms[x]["time_s"]}
            n = sum(counts.values())
            card[crit] = {"per_test": per, "counts": counts, "predicted": counts["hit"] + counts["false alarm"],
                          "score": counts["hit"] + counts["correct rejection"], "n": n,
                          "errors_s": sorted(errs), "within_60_s": sum(1 for e in errs if abs(e) <= 60.0)}
        key = "stage7_f0" if f == 0.0 else "by_fraction"
        if f == 0.0:
            out[key] = card
        else:
            out[key][f"{f:g}"] = card
    return out


# ------------------------------------------------------------------------------------------------ Part D
def partd(recs):
    out = {"tests": IN.median_tests(), "f": 0.2, "per_test": {}, "lumped": "unchanged by construction: the lumped "
           "neighbour is one node, with no boundary between the roll and the can (D82 (4)); its crossings are those of "
           "the first-round run at f = 0.2"}
    for x in IN.median_tests():
        g = recs.get(R8.spec("gas", x, 0.2, models="split", gas="layer")["id"])
        c = recs.get(R8.spec("gasctl", x, 0.2, models="split", gas="control")["id"])
        a = recs.get(R8.spec("first", x, 0.2)["id"])
        d = {}
        for name, r in (("layer", g), ("control", c), ("partA", a)):
            if r is None or r.get("failed"):
                d[name] = None
                continue
            rr = r["resolved"]
            d[name] = {"C1": rr["propagated"], "t_C1_s": rr.get("t_prop_s"), "hot_peak_C": rr["peak_hottest_C"],
                       "can_peak_C": rr.get("can_peak", {}).get("T_C"), "where": rr.get("where"),
                       "factorisations": rr.get("factorisations"), "wall_s": r.get("wall_s")}
            if name == "partA":
                ll = r["lumped"]
                q = r["stage8"]["clocks"]["lumped"]
                d[name].update({"C2": ll["propagated"], "t_C2_s": ll.get("t_prop_s"), "C3": q["t_150_s"] is not None,
                                "t_C3_s": q["t_150_s"]})
        if d.get("layer") and d.get("control") and d["layer"]["t_C1_s"] is not None and d["control"]["t_C1_s"] is not None:
            d["change_C1_s"] = d["layer"]["t_C1_s"] - d["control"]["t_C1_s"]
        if d.get("control") and d.get("partA") and d["control"]["t_C1_s"] is not None and d["partA"]["t_C1_s"] is not None:
            d["split_alone_C1_s"] = d["control"]["t_C1_s"] - d["partA"]["t_C1_s"]
        out["per_test"][x] = d
    return out


# ------------------------------------------------------------------------------------------------ the verdicts
def verdicts(rows, card):
    by = {r["test"]: r for r in rows}
    prop = [r for r in rows if r["propagated"]]
    nonp = [r for r in rows if not r["propagated"]]
    v = {}
    # P1
    hits7 = [r for r in prop if r["stage7_C1"]]
    rest = [r for r in prop if not r["stage7_C1"]]
    p1a = all(r["fC1"]["status"] == "zero" for r in hits7)
    p1b = [SR.below(r["fC1"], 0.3) for r in rest]
    v["P1"] = {"holds": bool(p1a and all(b is True for b in p1b)), "stage7_hits": [r["test"] for r in hits7],
               "hits_at_zero": p1a, "others": {r["test"]: fs_text(r["fC1"]) for r in rest},
               "others_below_0_3": dict(zip([r["test"] for r in rest], p1b))}
    # P2
    below = {r["test"]: SR.below(r["fC1"], 0.3) for r in nonp}
    fa = [r["test"] for r in nonp if r["stage7_C1"]]
    n_below = sum(1 for b in below.values() if b is True)
    rng = {}
    for name, grp in (("propagated", prop), ("not_propagated", nonp)):
        lo = [0.0 if r["fC1"]["status"] == "zero" else r["fC1"]["lo"] for r in grp if r["fC1"]["status"] != "above"]
        hi = [0.0 if r["fC1"]["status"] == "zero" else r["fC1"]["hi"] for r in grp if r["fC1"]["status"] != "above"]
        above = any(r["fC1"]["status"] == "above" for r in grp)
        rng[name] = {"min": min(lo) if lo else None, "max": None if above else (max(hi) if hi else None),
                     "any_above_1": above}
    a, b = rng["propagated"], rng["not_propagated"]
    top_a = 1e9 if a["any_above_1"] else a["max"]
    top_b = 1e9 if b["any_above_1"] else b["max"]
    overlap = max(a["min"], b["min"]) <= min(top_a, top_b)
    fa_zero = all(by[x]["fC1"]["status"] == "zero" for x in fa)
    v["P2"] = {"holds": bool(n_below >= 3 and fa_zero and overlap), "n_below_0_3": n_below, "below_0_3": below,
               "stage7_false_alarms": fa, "false_alarms_at_zero": fa_zero, "ranges": rng, "overlap": bool(overlap)}
    # P3
    inside = {}
    for r in rows:
        above05 = SR.below(r["fC2"], 0.05)
        below5 = SR.below(r["fC2"], 0.5)
        inside[r["test"]] = (above05 is False) and (below5 is True) if None not in (above05, below5) else None
    n_in = sum(1 for x in inside.values() if x is True)
    v["P3"] = {"holds": n_in >= 12, "n_inside": n_in, "inside": inside, "undecided": [k for k, x in inside.items() if x is None],
               "fC2": {r["test"]: fs_text(r["fC2"]) for r in rows}}
    # P4
    c2 = card["by_fraction"]["0.2"]["C2"]
    v["P4"] = {"holds": bool(c2["predicted"] >= 9 and c2["within_60_s"] >= 4), "predicted": c2["predicted"],
               "hits": c2["counts"]["hit"], "within_60_s": c2["within_60_s"], "errors_s": c2["errors_s"]}
    # P5
    scores = {f: {c: card["by_fraction"][f][c]["score"] for c in IN.CRITERIA} for f in card["by_fraction"]}
    v["P5"] = {"holds": all(s <= 12 for d in scores.values() for s in d.values()), "scores": scores}
    # P6
    inv, ties = [], []
    for conn in ("series", "parallel"):
        grp = sorted([r for r in rows if r["connection"] == conn], key=lambda r: r["E_b_J"])
        for crit in ("fC1", "fC2"):
            for i in range(len(grp)):
                for j in range(i + 1, len(grp)):
                    rel = relation(grp[i][crit], grp[j][crit])      # j has the larger energy
                    if rel == "higher":
                        inv.append([conn, crit, grp[i]["test"], grp[j]["test"]])
                    elif rel in ("same bracket", "both above 1"):
                        ties.append([conn, crit, grp[i]["test"], grp[j]["test"]])
    v["P6"] = {"holds": not inv, "inversions": inv, "ties_within_the_resolution": ties}
    # P7
    p7 = {}
    for r in rows:
        if r["connection"] != "parallel":
            continue
        x = r["variants"]["elec20_c1"]
        p7[r["test"]] = {"partA": fs_text(r["fC1"]), "elec20": fs_text(x["f"]), "lowering": x["lowering"]}
    ok = all(d["lowering"] is not None and d["lowering"][1] < 0.1 for d in p7.values())
    fail = any(d["lowering"] is not None and d["lowering"][0] >= 0.1 for d in p7.values())
    v["P7"] = {"holds": ok, "fails_established": fail, "per_test": p7,
               "undecided": [k for k, d in p7.items() if d["lowering"] is not None and d["lowering"][0] < 0.1 <= d["lowering"][1]]}
    # P8
    p8a, p8b = {}, {}
    for r in rows:
        if not r["sensitivity"]:
            continue
        if r["fC1"]["status"] != "zero":
            p8a[r["test"]] = r["variants"]["capend_c1"]["relation"]
        p8b[r["test"]] = r["variants"]["capend_c2"]["relation"]
    first_ok = all(x == "lower" for x in p8a.values())
    v["P8"] = {"holds": bool(first_ok), "first_part": first_ok, "second_part": True, "capend_C1": p8a,
               "capend_C2": p8b, "second_part_by_construction": True}
    return v


def main(runs_dir=None, out_dir=RES):
    recs = R8.load_records(runs_dir)
    states = R8.all_states(recs)
    rows = thresholds(recs, states)
    write_thresholds(rows, os.path.join(out_dir, "stage8_thresholds.csv"))
    card = scorecard(recs)
    json.dump(card, open(os.path.join(out_dir, "stage8_scorecard.json"), "w"), indent=1, default=float)
    pd = partd(recs)
    json.dump(pd, open(os.path.join(out_dir, "stage8_partd.json"), "w"), indent=1, default=float)
    v = verdicts(rows, card)
    unfinished = [k for k, s in states.items() if s["status"] in ("searching", "waiting", "broken")]
    out = {"verdicts": v, "unfinished_chains": unfinished, "n_records": len(recs),
           "failed": [k for k, r in recs.items() if r.get("failed")], "thresholds": rows}
    json.dump(out, open(os.path.join(out_dir, "stage8_verdicts.json"), "w"), indent=1, default=float)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default=None)
    ap.add_argument("--out", default=RES)
    a = ap.parse_args()
    o = main(a.runs, a.out)
    print(json.dumps({k: {"holds": x["holds"]} for k, x in o["verdicts"].items()}), "unfinished", o["unfinished_chains"])
