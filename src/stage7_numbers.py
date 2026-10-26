#!/usr/bin/env python3
"""Stage 7: every number that the note, the README, the release notes and the Zenodo description quote, computed from
the triggers (results/stage7_triggers.json and .csv), the separator's spread (results/stage7_separator.json), the
records (results/stage7_runs/), the Part B and Part C tables (results/stage7_pertest.csv, results/stage7_events.csv)
and the scorecard (results/stage7_scorecard.json, stage7_score.py). Writes results/stage7_paper_numbers.json, from
which a manuscript of Stages 1 to 7 is to be written (D72). Nothing here is scored.
Usage: python3 stage7_numbers.py [--res DIR]
"""
import argparse, csv, glob, json, os, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage7_inputs as IN          # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--res", default=os.path.join(HERE, "..", "results"))
a = ap.parse_args()
RES = a.res
CRIT = ("C1", "C2", "C3", "C4", "C5", "C6", "C7")


def rng(v):
    v = [x for x in v if x is not None]
    return [min(v), max(v)] if v else None


def num(x):
    if x in ("", None, "None"):
        return None
    if x in ("True", "False", "Yes", "No"):
        return x in ("True", "Yes")
    try:
        return float(x)
    except ValueError:
        return x


def rows(name):
    p = os.path.join(RES, name)
    if not os.path.exists(p):
        return []
    out = []
    for r in csv.DictReader(open(p)):
        out.append({k: (v if k in ("test", "connection", "contact", "criterion", "criterion_text", "run", "set",
                                   "class", "role", "id", "h", "model", "event_criterion") else num(v))
                    for k, v in r.items()})
    return out


out = {"measured": {k: v for k, v in IN.measured().items() if k != "by_test"}}
TR = json.load(open(os.path.join(RES, "stage7_triggers.json")))
SC = json.load(open(os.path.join(RES, "stage7_scorecard.json")))
SEP = json.load(open(os.path.join(RES, "stage7_separator.json"))) if os.path.exists(os.path.join(RES, "stage7_separator.json")) else None
PT = rows("stage7_pertest.csv")
EV = rows("stage7_events.csv")
CX = rows("stage7_crossings.csv")
recs = {}
for f in glob.glob(os.path.join(RES, "stage7_runs", "*.json")):
    r = json.load(open(f))
    recs[r["id"]] = r

# ---------------------------------------------------------------- the triggers
tr = TR["rows"]
out["triggers"] = {
    "energy_J": {r["test"]: r["E_J"] for r in tr}, "energy_range_J": rng([r["E_J"] for r in tr]),
    "T1max_central_C": {r["test"]: r["T1max_C"] for r in tr},
    "peak_minus_target_K": rng([r["T1max_C"] - r["target_C"] for r in tr]),
    "halvings": rng([r["iterations"] for r in tr]), "out_of_range": TR["out_of_range"],
    "T1max_low_minus_target_K": rng([r["T1max_by_contact_C"]["low"] - r["target_C"] for r in tr]),
    "T1max_high_minus_target_K": rng([r["T1max_by_contact_C"]["high"] - r["target_C"] for r in tr]),
    "T1max_by_tau_minus_target_K": {k: rng([r["T1max_by_tau_C"][k] - r["target_C"] for r in tr])
                                    for k in tr[0]["T1max_by_tau_C"]},
    "mapping_rows": len(TR["mapping"]), "levels": TR["levels"]}
if SEP:
    out["separator_spread"] = {k: SEP[k] for k in ("p2.5_C", "p97.5_C", "min_C", "max_C", "median_C",
                                                   "posterior_mean_model_peak_C", "n_particles")}

# ---------------------------------------------------------------- Part B
pb = {}
for c in CRIT:
    pb[c] = {}
    for h in ("low", "central", "high"):
        d = SC["criteria"].get(c, {}).get(h)
        if d is None:
            continue
        pb[c][h] = {k: d[k] for k in ("predicted", "hits", "misses", "false_alarms", "correct_rejections", "hit_rate",
                                      "time_error_range_s", "time_error_median_s", "within_60s", "by_connection",
                                      "predicted_time_range_s")}
        pb[c][h]["predicted_tests"] = sorted(r["test"] for r in PT if r["criterion"] == c and r["contact"] == h
                                             and r["predicted"] is True)
out["part_b"] = pb
out["sensitivities_central"] = SC.get("sensitivities_central")

# clocks of the pertest runs at the central contact
cen = [r for r in CX if r["set"] == "pertest" and r["h"] == "central"]
out["clocks_pertest_central"] = {c: {"peak_C": rng([r[f"{c}_peak_C"] for r in cen]),
                                     "t_sep_s": rng([r[f"{c}_t_sep_s"] for r in cen]),
                                     "t_150_s": rng([r[f"{c}_t_150_s"] for r in cen])}
                                 for c in ("hot", "mean", "away", "toward", "lumped")}

# ---------------------------------------------------------------- Part C
pc = {}
for s in ("event", "eventlow", "v3"):
    rs = [r for r in EV if r["set"] == s]
    if not rs:
        continue
    pc[s] = {"n": len(rs), "by_criterion": {c: sum(r["criterion"] == c for r in rs) for c in ("C4", "C5")},
             "hot_after_C": rng([r["hot_after_C"] for r in rs]), "lumped_after_C": rng([r["lumped_after_C"] for r in rs]),
             "mean_after_C": rng([r["mean_after_C"] for r in rs]), "away_after_C": rng([r["away_after_C"] for r in rs]),
             "t_event_s": {c: rng([r["t_event_s"] for r in rs if r["criterion"] == c]) for c in ("C4", "C5")},
             "hot_inside": sum(bool(r["hot_inside_measured_range"]) for r in rs),
             "lumped_inside": sum(bool(r["lumped_inside_measured_range"]) for r in rs),
             "reaction_heat_lumped_J": rng([r["reaction_heat_lumped_J"] for r in rs]),
             "reaction_heat_resolved_J": rng([r["reaction_heat_resolved_J"] for r in rs]),
             "peaked_before_end": all(bool(r["peaked_before_end"]) for r in rs)}
    for c in ("C4", "C5"):
        q = [r for r in rs if r["criterion"] == c]
        if q:
            pc[s][c] = {"hot_after_C": rng([r["hot_after_C"] for r in q]),
                        "lumped_after_C": rng([r["lumped_after_C"] for r in q]),
                        "away_after_C": rng([r["away_after_C"] for r in q])}
out["part_c"] = pc

# ---------------------------------------------------------------- the scorecard, V3, V4 and the runs
out["scorecard"] = {k: (v.get("verdict") if isinstance(v, dict) else v) for k, v in SC.items() if k.startswith("P")}
out["P_details"] = {k: v for k, v in SC.items() if k.startswith("P")}
out["V3"] = SC.get("V3")
out["V4"] = SC.get("V4")
if recs:
    good = [r for r in recs.values() if not r.get("failed")]
    by = {}
    for s in ("pertest", "duration", "aged", "v3", "event", "eventlow"):
        w = [r["wall_s"] for r in good if r["set"] == s]
        if w:
            by[s] = {"n": len(w), "wall_median_s": statistics.median(w), "wall_range_s": rng(w)}
    out["runs"] = {"n": len(good), "failed": len(recs) - len(good),
                   "first_start_utc": min(r["started_utc"] for r in good), "last_finish_utc": max(r["finished_utc"] for r in good),
                   "by_set": by, "machines": sorted({(r.get("machine") or {}).get("label", "unrecorded") for r in good}),
                   "memory_retries": sum(r.get("memory_retries", 0) for r in good),
                   "worker_peak_memory_MB": rng([r.get("worker_peak_memory_MB") or None for r in good]),
                   "worker_peak_memory_note": "None where every record carries 0.0: the reading failed on Windows (D75)"}
json.dump(out, open(os.path.join(RES, "stage7_paper_numbers.json"), "w"), indent=1, default=float)
print("wrote stage7_paper_numbers.json")
