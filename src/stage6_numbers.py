#!/usr/bin/env python3
"""Stage 6: every number that the README, the note, the release notes and the Zenodo description quote, computed
from the Part A file (results/stage6_crossings.csv and .json), the Part B records (results/stage6_runs/), the
selection (results/stage6_trigger.json), the scorecard (results/stage6_scorecard.json, stage6_score.py) and the
Stage 5 grid records. Writes results/stage6_numbers.json. Nothing here is scored.
Usage: python3 stage6_numbers.py [--res DIR]
"""
import argparse, csv, glob, json, os, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage6_inputs as IN

ap = argparse.ArgumentParser()
ap.add_argument("--res", default=os.path.join(HERE, "..", "results"))
a = ap.parse_args()
RES = a.res
LO, HI = IN.WINDOW_S
CLOCKS = ("hot", "mean", "away", "toward", "lumped")


def rng(v):
    v = [x for x in v if x is not None]
    return [min(v), max(v)] if v else None


def num(x):
    if x in ("", None, "None"):
        return None
    if x in ("True", "False"):
        return x == "True"
    try:
        return float(x)
    except ValueError:
        return x


A = list(csv.DictReader(open(os.path.join(RES, "stage6_crossings.csv"))))
for r in A:
    for k in list(r):
        if k not in ("id", "set", "connection", "h", "g", "kin") and not k.endswith("_window"):
            r[k] = num(r[k])
AJ = json.load(open(os.path.join(RES, "stage6_crossings.json")))
TR = json.load(open(os.path.join(RES, "stage6_trigger.json")))
SC = json.load(open(os.path.join(RES, "stage6_scorecard.json")))
MJ = json.load(open(os.path.join(RES, "stage6_matched.json")))
B = {}
for f in glob.glob(os.path.join(RES, "stage6_runs", "*.json")):
    r = json.load(open(f))
    if not r.get("failed"):
        B[r["id"]] = r
out = {}

# ---------------------------------------------------------------- Part A
grid = [r for r in A if r["set"] == "grid"]
pa = {}
for c in CLOCKS:
    d = {"cross": sum(r[f"{c}_crosses"] for r in grid), "times_s": rng([r[f"{c}_t_cross_s"] for r in grid]),
         "inside": sum(r[f"{c}_window"] == "inside" for r in grid), "below": sum(r[f"{c}_window"] == "below" for r in grid),
         "above": sum(r[f"{c}_window"] == "above" for r in grid), "peak_C": rng([r[f"{c}_peak_C"] for r in grid])}
    for h in ("low", "central", "high"):
        rs = [r for r in grid if r["h"] == h]
        d[h] = {"cross": sum(r[f"{c}_crosses"] for r in rs), "inside": sum(r[f"{c}_window"] == "inside" for r in rs),
                "times_s": rng([r[f"{c}_t_cross_s"] for r in rs]), "peak_C": rng([r[f"{c}_peak_C"] for r in rs]),
                "t_return_s": rng([r[f"{c}_t_return_s"] for r in rs])}
    pa[c] = d
out["part_a_grid"] = pa
out["part_a_all_records"] = {c: {"cross": sum(r[f"{c}_crosses"] for r in A), "n": len(A),
                                 "peak_C": rng([r[f"{c}_peak_C"] for r in A])} for c in CLOCKS}
fact_mean = [r for r in A if r["set"] == "fact" and r["mean_crosses"]]
out["part_a_mean_reaches_150_fact"] = {"n": len(fact_mean), "contacts": sorted({r["h"] for r in fact_mean}),
                                       "peak_C": rng([r["mean_peak_C"] for r in fact_mean])}
out["part_a_sets_with_series"] = {s: AJ["a3_counts_with_series"][s]["all"] for s in ("sens", "v3")}
lag = [r["toward_t_cross_s"] - r["hot_t_cross_s"] for r in grid
       if r["toward_t_cross_s"] is not None and r["hot_t_cross_s"] is not None]
out["part_a_toward_after_hot_150C_s"] = rng(lag)
out["measured"] = {k: v for k, v in AJ["a2_measured"].items()}

# ---------------------------------------------------------------- Part B
def summary(rs):
    if not rs:
        return None
    d = {"n": len(rs), "T1max_C": rng([r["T1max_C"] for r in rs]), "t_T1max_s": rng([r["t_T1max_s"] for r in rs]),
         "hot_peak_C": rng([r["resolved"]["peak_hottest_C"] for r in rs]),
         "hot_t_peak_s": rng([r["resolved"]["t_peak_hottest_s"] for r in rs]),
         "mean_peak_C": rng([r["resolved"]["peak_mean_C"] for r in rs]),
         "away_peak_C": rng([r["resolved"]["probe_peak"]["away"]["T_C"] for r in rs]),
         "toward_peak_C": rng([r["resolved"]["probe_peak"]["toward"]["T_C"] for r in rs]),
         "lumped_peak_C": rng([r["lumped"]["peak_C"] for r in rs]),
         "lumped_t_peak_s": rng([r["lumped"]["t_peak_s"] for r in rs]),
         "hot_reaches": sum(r["resolved"]["propagated"] for r in rs),
         "lumped_reaches": sum(r["lumped"]["propagated"] for r in rs),
         "hot_t_255_7_s": rng([r["resolved"].get("t_prop_s") for r in rs]),
         "lumped_t_255_7_s": rng([r["lumped"].get("t_prop_s") for r in rs]),
         "reaction_heat_resolved_J": rng([r["resolved"]["in_rxn_J"] for r in rs]),
         "reaction_heat_lumped_J": rng([r["lumped"]["reaction_heat_J"] for r in rs])}
    lags = [r["lumped"]["t_prop_s"] - r["resolved"]["t_prop_s"] for r in rs
            if r["lumped"]["propagated"] and r["resolved"]["propagated"]]
    d["lumped_minus_hot_255_7_s"] = rng(lags)
    for c in CLOCKS:
        tc = [r["stage6"]["crossings_150C"][c]["t_cross_s"] for r in rs]
        d[f"{c}_150C"] = {"cross": sum(t is not None for t in tc), "inside": sum(t is not None and LO <= t <= HI for t in tc),
                          "times_s": rng(tc)}
    where = [r["resolved"].get("where") for r in rs if r["resolved"]["propagated"]]
    if where:
        d["hot_at_255_7_where"] = {"theta_deg": rng([w["theta_deg"] for w in where]), "r_mm": rng([w["r_mm"] for w in where]),
                                   "z_mm": rng([w["z_mm"] for w in where])}
    return d


sets = {}
for s in ("body", "total", "bracket", "peak", "draws", "v3"):
    rs = [r for r in B.values() if r["set"] == s]
    sets[s] = summary(rs)
    if s in ("body", "total", "peak"):
        sets[s + "_by_contact"] = {h: summary([r for r in rs if r["h"] == h]) for h in ("low", "central", "high")}
        sets[s + "_by_tau"] = {f"{t:.2f}": summary([r for r in rs if abs(r["tau"] - t) < 1e-9])
                               for t in sorted({r["tau"] for r in rs})}
    if s == "draws":
        sets["draws_by_connection"] = {c: summary([r for r in rs if r["connection"] == c]) for c in ("series", "parallel")}
out["part_b_sets"] = sets
win = {}
for s_ in ("body", "total", "bracket", "peak", "draws", "v3", "all"):
    rs = [r for r in B.values() if (s_ == "all" or r["set"] == s_) and r["lumped"]["propagated"]]
    t = [r["lumped"]["t_prop_s"] for r in rs]
    win[s_] = {"lumped_reaches": len(t), "inside": sum(LO <= x <= HI for x in t), "before": sum(x < LO for x in t),
               "after": sum(x > HI for x in t), "inside_range_s": rng([x for x in t if LO <= x <= HI]),
               "before_range_s": rng([x for x in t if x < LO]),
               "inside_by_contact": {h: sum(LO <= r["lumped"]["t_prop_s"] <= HI for r in rs if r["h"] == h)
                                     for h in ("low", "central", "high")}}
    th = [r["resolved"]["t_prop_s"] for r in B.values() if (s_ == "all" or r["set"] == s_) and r["resolved"]["propagated"]]
    win[s_]["hot_reaches"] = len(th)
    win[s_]["hot_range_s"] = rng(th)
out["part_b_255_7C_against_window"] = win
L = TR["levels"]
tm = L["tau_median_s"]
cmc = {}
for conn in ("series", "parallel"):
    r = B.get(f"body_mean_{conn}_hcentral_gcentral_tau{tm:.2f}_E{L['E_body_J'] / 1e3:.2f}")
    if r:
        cmc[conn] = summary([r])
    for t in (10, 30):
        p = os.path.join(RES, "v12_runs", f"grid_mean_{conn}_hcentral_gcentral_tau{t}.json")
        s5 = json.load(open(p))
        cmc[f"stage5_{conn}_tau{t}"] = {"T1max_C": s5["T1max_C"], "hot_peak_C": s5["resolved"]["peak_hottest_C"],
                                        "lumped_peak_C": s5["lumped"]["peak_C"],
                                        "away_peak_C": s5["resolved"]["probe_peak"]["away"]["T_C"]}
out["central_matched_case"] = cmc
out["selection"] = {"rows": TR["rows"], "central_matched_case": TR["central_matched_case"],
                    "peak_matched_exploratory": TR["peak_matched_exploratory"], "levels": L}
out["scorecard"] = {k: (v.get("verdict") if isinstance(v, dict) and "verdict" in v else v) for k, v in SC.items()
                    if k.startswith("P")}
out["v3"] = SC.get("V3")
out["energy"] = SC.get("energy")
# runs: where, when, how long
recs = list(B.values())
if recs:
    walls = [r["wall_s"] for r in recs]
    base = [r["wall_s"] for r in recs if r["refine"] == 1.0]
    out["runs"] = {"n": len(recs), "failed": len(glob.glob(os.path.join(RES, "stage6_runs", "*.json"))) - len(recs),
                   "first_start_utc": min(r["started_utc"] for r in recs), "last_finish_utc": max(r["finished_utc"] for r in recs),
                   "wall_median_base_s": statistics.median(base) if base else None,
                   "wall_refined_s": rng([r["wall_s"] for r in recs if r["refine"] == 2.0]),
                   "wall_hot_reaches_255_7_s": rng([r["wall_s"] for r in recs if r["resolved"]["propagated"]]),
                   "machines": sorted({r["machine"]["label"] for r in recs}),
                   "memory_retries": sum(r.get("memory_retries", 0) for r in recs)}
json.dump(out, open(os.path.join(RES, "stage6_numbers.json"), "w"), indent=1, default=float)
print("wrote stage6_numbers.json")
