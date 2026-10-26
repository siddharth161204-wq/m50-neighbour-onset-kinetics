#!/usr/bin/env python3
"""Stage 7 checks V1 and V2 (DECISIONS.md D70), written apart from the code they check.

V1  The sixteen trigger energies re-derived from the recorded peak-to-energy table (results/stage7_triggers.csv, its
    `mapping` rows) and the trigger maxima of the paper's Tables 3 and 4, typed here from the paper: for each test the
    table of its connection is scanned in a plain loop for the two energies whose cell-1 peaks bracket the test's
    trigger maximum, and the energy is interpolated linearly between them. Compared with the file's `test` rows.
    Acceptance: every energy within 2 J, and every recorded peak within 0.01 K of its target.
V2  The Part B crossings of three runs, fixed before the predictions, recomputed by hand from their archived series:
    each history is scanned sample by sample, the two samples that bracket each level are printed, and the crossing
    is interpolated with the formula written out here; the peaks are compared with the largest stored sample. The
    runs' own 255.7 C crossings (C1, C2 and C6) are interpolated within the step that crossed (D35), and the stored
    series ends with that step's sample, at or above 255.7 C (D76 (2) corrects D70 (2), which had it end before the
    stop); for them V2 checks that every sample stored before the crossing lies below 255.7 C and that the run ended
    within a step of it. Compared with the records' Stage 7 quantities and results/stage7_crossings.csv.
    Acceptance: the same crossings within 1e-9 s.
Usage: python3 stage7_checks.py v1 | v2 [--res DIR]
"""
import argparse, csv, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
# Tables 3 (parallel) and 4 (series) of Fransson et al. (2024), the trigger cell's maximum temperature, typed here
TABLE_TRIGGER_MAX_C = {
    "M50_PT_Exp1": ("parallel", 164), "M50_PT_Exp2": ("parallel", 679), "M50_PT_Exp3": ("parallel", 507),
    "M50_PT_Exp4": ("parallel", 630), "M50_PP_Exp1": ("parallel", 787), "M50_PP_Exp2": ("parallel", 644),
    "M50_PP_Exp3": ("parallel", 686), "M50_PP_Exp4": ("parallel", 728),
    "M50_ST_Exp1": ("series", 788), "M50_ST_Exp2": ("series", 723), "M50_ST_Exp3": ("series", 282),
    "M50_ST_Exp4": ("series", 756), "M50_SP_Exp1": ("series", 728), "M50_SP_Exp2": ("series", 755),
    "M50_SP_Exp3": ("series", 832), "M50_SP_Exp4": ("series", 625)}
V1_TOL_J, V1_TOL_K = 2.0, 0.01
V2_RUNS = (("pertest", "M50_PT_Exp4", "central"), ("aged", "M50_SP_Exp3", "high"), ("pertest", "M50_ST_Exp3", "low"))
LEVELS_C = {"sep": 138.5, "150": 150.0, "prop": 278.9 * (1 - 0.1665 / 2)}


def v1(res):
    rows = list(csv.DictReader(open(os.path.join(res, "stage7_triggers.csv"))))
    table = {"series": [], "parallel": []}
    rec = {}
    for r in rows:
        if r["kind"] == "mapping":
            table[r["connection"]].append((float(r["E_J"]), float(r["T1max_C"])))
        else:
            rec[r["test"]] = r
    out, worst_J, worst_K, ok = {}, 0.0, 0.0, True
    for test, (conn, target) in TABLE_TRIGGER_MAX_C.items():
        pts = sorted(table[conn])
        e = None
        for i in range(1, len(pts)):
            (e0, p0), (e1, p1) = pts[i - 1], pts[i]
            if p0 <= target <= p1:
                e = e0 + (target - p0) * (e1 - e0) / (p1 - p0)
                lo, hi = (e0, p0), (e1, p1)
                break
        r = rec[test]
        mine_ok = e is not None and r["connection"] == conn and float(r["target_C"]) == float(target)
        dJ = abs(e - float(r["E_J"])) if e is not None else float("inf")
        dK = abs(float(r["T1max_C"]) - target)
        agree = mine_ok and dJ <= V1_TOL_J and dK <= V1_TOL_K and r["in_range"] == "True"
        ok &= agree
        worst_J, worst_K = max(worst_J, dJ), max(worst_K, dK)
        out[test] = {"connection": conn, "target_C": target, "bracket": [lo, hi] if e is not None else None,
                     "by_hand_E_J": e, "file_E_J": float(r["E_J"]), "abs_diff_J": dJ,
                     "file_T1max_C": float(r["T1max_C"]), "peak_minus_target_K": float(r["T1max_C"]) - target,
                     "agree": agree}
    res_ = {"tests": out, "pass": ok, "largest_difference_J": worst_J, "largest_peak_offset_K": worst_K,
            "acceptance": {"J": V1_TOL_J, "K": V1_TOL_K}, "mapping_rows": {k: len(v) for k, v in table.items()}}
    json.dump(res_, open(os.path.join(res, "stage7_v1.json"), "w"), indent=1)
    print("V1", "pass" if ok else "FAIL", "largest difference", worst_J, "J; largest peak offset", worst_K, "K")
    return res_


def by_hand(t, y, level_C):
    level = level_C + 273.15
    for i in range(len(y)):
        if y[i] >= level:
            if i == 0:
                return {"i": 0, "t_cross_s": float(t[0])}
            t0, t1, y0, y1 = float(t[i - 1]), float(t[i]), float(y[i - 1]), float(y[i])
            tc = t0 + (level - y0) * (t1 - t0) / (y1 - y0)
            return {"i": i, "before": [t0, y0 - 273.15], "after": [t1, y1 - 273.15], "t_cross_s": tc}
    return None


def v2(res):
    import numpy as np
    recs = {}
    for f in os.listdir(os.path.join(res, "stage7_runs")):
        if f.endswith(".json"):
            r = json.load(open(os.path.join(res, "stage7_runs", f)))
            if not r.get("failed"):
                recs[(r["set"], r["test"], r["h"], round(r["tau"], 2))] = r
    csvrows = {r["id"]: r for r in csv.DictReader(open(os.path.join(res, "stage7_crossings.csv")))}
    tm = json.load(open(os.path.join(res, "stage7_triggers.json")))["levels"]["tau_median_s"]
    out, ok, worst = {}, True, 0.0
    for set_, test, h in V2_RUNS:
        rec = recs[(set_, test, h, round(tm, 2))]
        z = np.load(os.path.join(res, "stage7_series", rec["id"] + ".npz"))
        hist = {"hot": (z["t"], z["Tmax"]), "mean": (z["t"], z["Tmean"]), "away": (z["probe_t"], z["probe_away"]),
                "toward": (z["probe_t"], z["probe_toward"]), "lumped": (z["t_lumped"], z["T_lumped"])}
        d = {}
        for c, (t, y) in hist.items():
            t, y = list(t), list(y)
            big = max(range(len(y)), key=lambda i: y[i])
            dc = {"largest_stored_C": y[big] - 273.15, "at_s": t[big],
                  "record_peak_C": rec["stage7"]["clocks"][c]["peak_C"]}
            for name, lv in LEVELS_C.items():
                hnd = by_hand(t, y, lv)
                mine = None if hnd is None else hnd["t_cross_s"]
                theirs = rec["stage7"]["clocks"][c][f"t_{name}_s"]
                file_v = csvrows[rec["id"]][f"{c}_t_{name}_s"]
                file_v = None if file_v in ("", "None") else float(file_v)
                diff = None if (mine is None or theirs is None) else abs(mine - theirs)
                agree = ((mine is None and theirs is None and file_v is None) or
                         (diff is not None and diff < 1e-9 and file_v is not None and abs(file_v - theirs) < 1e-9))
                ok &= agree
                worst = max(worst, diff or 0.0)
                dc[name] = {"by_hand": hnd, "record_t_s": theirs, "file_t_s": file_v, "abs_diff_s": diff, "agree": agree}
            d[c] = dc
        stops = {}
        lvK = LEVELS_C["prop"] + 273.15
        for c, key in (("hot", "resolved"), ("lumped", "lumped")):
            tp = rec[key].get("t_prop_s")
            t, y = (list(v) for v in hist[c])
            t_end = rec[key]["t_end_s"]
            if tp is None:        # never reached: the run went to 900 s and no stored sample reaches the level
                fine = t_end >= 900.0 - 1e-6 and max(y) < lvK
            else:                 # every sample stored before the crossing lies below it; the run ended in its step
                fine = (all(yy < lvK for tt, yy in zip(t, y) if tt < tp) and tp <= t_end + 1e-9
                        and t_end - tp <= 0.1 + 1e-9)
            ok &= fine
            stops[c] = {"t_prop_s": tp, "last_stored_s": t[-1], "last_stored_C": y[-1] - 273.15,
                        "t_end_s": t_end, "consistent": fine}
        d["stop_crossings"] = stops
        out[rec["id"]] = d
    res_ = {"runs": out, "pass": ok, "largest_difference_s": worst}
    json.dump(res_, open(os.path.join(res, "stage7_v2.json"), "w"), indent=1, default=float)
    print("V2", "pass" if ok else "FAIL", "largest difference", worst)
    return res_


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("check", choices=["v1", "v2"])
    ap.add_argument("--res", default=os.path.join(HERE, "..", "results"))
    a = ap.parse_args()
    (v1 if a.check == "v1" else v2)(a.res)
