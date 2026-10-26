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


def verdicts(crit, h):
    return {r["test"]: r["predicted"] is True for r in PT if r["criterion"] == crit and r["contact"] == h}


# the sensitivities, test by test: which central-contact verdicts differ from the registered ones (D67 (6))
sens_tests = {}
tm = TR["levels"]["tau_median_s"]
for tau in TR["levels"]["tau_s"]:
    if abs(tau - tm) < 1e-9:
        continue
    d = {}
    for crit, (clock, level, source) in {"C1": ("hot", "prop", "stop"), "C2": ("lumped", "prop", "stop"),
                                          "C3": ("lumped", "150", "series"), "C4": ("hot", "sep", "series"),
                                          "C5": ("lumped", "sep", "series")}.items():
        reg = verdicts(crit, "central")
        alt = {}
        for r in recs.values():
            if r["set"] == "duration" and abs(r["tau"] - tau) < 5e-3:
                q = r["stage7"]
                t = (q["stop"]["hot_t_s"] if clock == "hot" else q["stop"]["lumped_t_s"]) if source == "stop" \
                    else q["clocks"][clock][f"t_{level}_s"]
                alt[r["test"]] = t is not None
        d[crit] = sorted(t for t in reg if t in alt and alt[t] != reg[t]) if len(alt) == 16 else None
    sens_tests[f"release_{tau:.2f}s_verdicts_differing"] = d
if SEP:
    import numpy as np
    import stage6_crossings as CR6
    for name in ("p2.5_C", "p97.5_C"):
        lv = SEP[name] + 273.15
        d = {}
        for crit, (set_, clock) in {"C4": ("pertest", "hot"), "C5": ("pertest", "lumped"), "C7": ("aged", "hot")}.items():
            reg = verdicts(crit, "central")
            alt = {}
            for r in recs.values():
                if r["set"] == set_ and r["h"] == "central":
                    p = os.path.join(RES, "stage7_series", r["id"] + ".npz")
                    if not os.path.exists(p):
                        continue
                    z = np.load(p)
                    hs = CR6.histories({k: z[k] for k in z.files})
                    alt[r["test"]] = CR6.first_crossing(*hs[clock], lv) is not None
            d[crit] = sorted(t for t in reg if t in alt and alt[t] != reg[t]) if len(alt) == 16 else None
        sens_tests[f"melting_{name[:-2]}_{SEP[name]:.2f}C_verdicts_differing"] = d
out["sensitivities_central_tests"] = sens_tests

# the aged SEI beside the fresh, at each contact (P5 scores the central contact; the rest is reported)
af = {}
for h in ("low", "central", "high"):
    v1, v6, v4, v7 = verdicts("C1", h), verdicts("C6", h), verdicts("C4", h), verdicts("C7", h)
    pair = {}
    for r in recs.values():
        if r["set"] in ("pertest", "aged") and r["h"] == h:
            pair.setdefault(r["test"], {})[r["set"]] = r
    full = [p for p in pair.values() if len(p) == 2]
    dt1 = [abs(p["aged"]["resolved"]["t_prop_s"] - p["pertest"]["resolved"]["t_prop_s"]) for p in full
           if p["aged"]["resolved"].get("t_prop_s") is not None and p["pertest"]["resolved"].get("t_prop_s") is not None]
    dt4 = [abs(p["aged"]["stage7"]["clocks"]["hot"]["t_sep_s"] - p["pertest"]["stage7"]["clocks"]["hot"]["t_sep_s"])
           for p in full if p["aged"]["stage7"]["clocks"]["hot"]["t_sep_s"] is not None
           and p["pertest"]["stage7"]["clocks"]["hot"]["t_sep_s"] is not None]
    drop = [p["pertest"]["lumped"]["peak_C"] - p["aged"]["lumped"]["peak_C"] for p in full]
    af[h] = {"C6_differs_from_C1": sorted(t for t in v1 if v1[t] != v6.get(t)),
             "C7_differs_from_C4": sorted(t for t in v4 if v4[t] != v7.get(t)),
             "largest_change_hot_255_7_crossing_s": max(dt1) if dt1 else None,
             "largest_change_hot_138_5_crossing_s": max(dt4) if dt4 else None,
             "lumped_reaches_255_7_fresh": sorted(t for t, p in pair.items() if "pertest" in p
                                                  and p["pertest"]["lumped"]["propagated"]),
             "lumped_reaches_255_7_aged": sorted(t for t, p in pair.items() if "aged" in p
                                                 and p["aged"]["lumped"]["propagated"]),
             "lumped_peak_fresh_minus_aged_K": rng(drop),
             "lumped_reaction_heat_fresh_J": rng([p["pertest"]["lumped"]["reaction_heat_J"] for p in full]),
             "lumped_reaction_heat_aged_J": rng([p["aged"]["lumped"]["reaction_heat_J"] for p in full])}
p5 = SC.get("P5", {}).get("self_heating_0.15Kpm")
if p5:
    fr = [v["fresh_T_C"] for v in p5.values() if v["fresh_T_C"] is not None]
    ag = [v["aged_T_C"] for v in p5.values() if v["aged_T_C"] is not None]
    af["first_self_heating_central"] = {
        "fresh_T_C": rng(fr), "fresh_reactions": sorted({v["fresh_reaction"] for v in p5.values() if v["fresh_reaction"]}),
        "aged_T_C": rng(ag), "aged_reactions": sorted({v["aged_reaction"] for v in p5.values() if v["aged_reaction"]}),
        "fresh_n": len(fr), "aged_n": len(ag),
        "neither": sorted(t for t, v in p5.items() if v["fresh_T_C"] is None and v["aged_T_C"] is None),
        "fresh_only": sorted(t for t, v in p5.items() if v["fresh_T_C"] is not None and v["aged_T_C"] is None),
        "rise_K": rng([v["aged_T_C"] - v["fresh_T_C"] for v in p5.values()
                       if v["aged_T_C"] is not None and v["fresh_T_C"] is not None])}
out["aged_vs_fresh"] = af

# the measured outcomes against the trigger's maximum (Tables 3 and 4), for the texts
mt = IN.tests()
out["measured_by_trigger"] = {
    "propagated_trigger_max_C": sorted(t["trigger_max_C"] for t in mt if t["propagated"]),
    "not_propagated_trigger_max_C": sorted(t["trigger_max_C"] for t in mt if not t["propagated"]),
    "not_propagated_neighbour_max_C": sorted(t["neighbour_max_C"] for t in mt if not t["propagated"])}


def best_threshold(ts):
    """Exploratory, written after the results: the most outcomes that the rule 'propagates if the trigger's maximum
    is at least x' gets right, over every x between and beyond the measured maxima."""
    v = sorted(t["trigger_max_C"] for t in ts)
    xs = [v[0] - 1.0] + [(v[i] + v[i + 1]) / 2 for i in range(len(v) - 1) if v[i] != v[i + 1]] + [v[-1] + 1.0]
    sc_ = [(sum((t["trigger_max_C"] >= x) == t["propagated"] for t in ts), x) for x in xs]
    n = max(s for s, _ in sc_)
    return {"right": n, "of": len(ts), "thresholds_C": [x for s, x in sc_ if s == n]}


out["exploratory_threshold_on_trigger_max"] = {
    "both_connections": best_threshold(mt),
    **{c: best_threshold([t for t in mt if t["connection"] == c]) for c in ("series", "parallel")}}

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

# Part C's timing, from the records: how long after the event's start each peak comes, and when the lumped neighbour
# reaches 255.7 C (D68 (5)); and the event's energy against the lumped neighbour's heat capacity, before any loss
tm_ = {}
for s in ("event", "eventlow"):
    for c in ("C4", "C5"):
        q = [r for r in recs.values() if r["set"] == s and r.get("event", {}).get("criterion") == c]
        if not q:
            continue
        ae = [(r["stage7"]["after_event"], r["event"]["t_s"]) for r in q]
        tm_[f"{s}_{c}"] = {
            "n": len(q),
            "hot_peak_after_start_s": rng([a["t_hot_s"] - t0 for a, t0 in ae]),
            "lumped_peak_after_start_s": rng([a["t_lumped_s"] - t0 for a, t0 in ae]),
            "lumped_reaches_255_7_after_start_s": rng([a["lumped_t_prop_after_event_s"] - t0 for a, t0 in ae
                                                       if a["lumped_t_prop_after_event_s"] is not None]),
            "lumped_reaches_255_7_s": rng([a["lumped_t_prop_after_event_s"] for a, t0 in ae]),
            "away_reaches_255_7_after_start_s": rng([a["away_t_prop_after_event_s"] - t0 for a, t0 in ae
                                                     if a["away_t_prop_after_event_s"] is not None])}
out["part_c_timing"] = tm_
out["event"] = {"E_J": IN.E_EVENT_J, "E_low_J": IN.E_EVENT_LOW_J, "Wh": [IN.E_EVENT_WH, IN.E_EVENT_LOW_WH],
                "tau_s": TR["levels"]["tau_median_s"], "level_C": IN.LEVEL_SEP_C}
# the two timings of one test against each other: an event at the whole cell's melting starts from a hotter cell
pairs = {}
for r in recs.values():
    if r["set"] == "event":
        pairs.setdefault(r["test"], {})[r["event"]["criterion"]] = r["stage7"]["after_event"]
both = [p for p in pairs.values() if "C4" in p and "C5" in p]
out["part_c_c5_minus_c4_K"] = {"tests": len(both),
                               "hot": rng([p["C5"]["hot_C"] - p["C4"]["hot_C"] for p in both]),
                               "lumped": rng([p["C5"]["lumped_C"] - p["C4"]["lumped_C"] for p in both]),
                               "hot_spread_within_C4_K": (lambda v: v[1] - v[0] if v else None)(
                                   rng([p["C4"]["hot_C"] for p in both])),
                               "hot_spread_within_C5_K": (lambda v: v[1] - v[0] if v else None)(
                                   rng([p["C5"]["hot_C"] for p in both]))}
try:
    import v12_model as V12
    C_lumped = float(V12.LP.C_CELL)
    out["event_energy_over_lumped_heat_capacity_K"] = {"E_J": IN.E_EVENT_J, "C_J_per_K": C_lumped,
                                                       "rise_K": IN.E_EVENT_J / C_lumped}
except Exception as e:                                   # the two-cell study's code is not on this machine
    out["event_energy_over_lumped_heat_capacity_K"] = {"error": repr(e)}

# exploratory, written after the results: the hot spot past its Part A stop. A Part A run stops at the hot spot's
# 255.7 C crossing (D35); the C5 event runs of the same tests repeat it until their events, which come later (D75 (3)),
# so their histories show what the hot spot does next
past = {}
for r in recs.values():
    if r["set"] != "event" or r["event"]["criterion"] != "C5":
        continue
    base = recs.get(r["event"]["from"])
    if base is None or not base["resolved"]["propagated"]:
        continue
    p = os.path.join(RES, "stage7_series", r["id"] + ".npz")
    if not os.path.exists(p):
        continue
    import numpy as np
    z = np.load(p)
    m = z["t"] < r["event"]["t_s"]
    k = int(np.argmax(z["Tmax"][m]))
    above = np.where(z["Tmax"][m] >= IN.LEVEL_PROP_C + 273.15)[0]
    past[r["test"]] = {"part_a_stop_s": base["resolved"]["t_prop_s"], "t_event_s": r["event"]["t_s"],
                       "hot_peak_before_event_C": float(z["Tmax"][m][k] - 273.15), "t_hot_peak_s": float(z["t"][m][k]),
                       "last_sample_at_or_above_255_7_s": float(z["t"][m][above[-1]]) if above.size else None,
                       "hot_at_event_C": float(z["Tmax"][m][-1] - 273.15),
                       "back_below_255_7_before_event": bool(z["Tmax"][m][-1] < IN.LEVEL_PROP_C + 273.15)}
out["exploratory_hot_spot_past_its_stop"] = {
    "tests": past, "n": len(past),
    "hot_peak_before_event_C": rng([v["hot_peak_before_event_C"] for v in past.values()]),
    "t_hot_peak_s": rng([v["t_hot_peak_s"] for v in past.values()]),
    "back_below_255_7_before_event": sum(v["back_below_255_7_before_event"] for v in past.values()),
    "back_below_by_s": rng([v["last_sample_at_or_above_255_7_s"] for v in past.values()
                            if v["back_below_255_7_before_event"]])}

# the Databank's ten nail tests of this cell at 100 % state of charge (D53): how much of each test's energy the cell
# body kept, for the texts
dbp = os.path.join(HERE, "..", "inputs", "databank", "databank_m50_used.csv")
if os.path.exists(dbp):
    import stage6_inputs as IN6
    ids = set(IN6.energies()["test_ids"])
    db = [r for r in csv.DictReader(open(dbp)) if r["Test-ID"] in ids]
    out["databank_nail_tests"] = {
        "n": len(db),
        "cell_body_kJ": rng([float(r["Energy-Fraction-Cell-Body-kJ"]) for r in db]),
        "cell_body_percent": rng([float(r["Energy-Percent-Cell-Body-%"]) for r in db]),
        "total_kJ": rng([float(r["Corrected-Total-Energy-Yield-kJ"]) for r in db])}

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
    pa = [r for r in good if r["set"] in ("pertest", "duration", "aged")]
    w9 = [r["wall_s"] for r in pa if r["resolved"]["t_end_s"] >= 900.0 - 1e-6]
    ws = [r["wall_s"] for r in pa if r["resolved"]["t_end_s"] < 900.0 - 1e-6]
    we = [r["wall_s"] for r in good if r["set"] in ("event", "eventlow")]
    out["runs"]["part_a_to_900_s"] = {"n": len(w9), "wall_median_s": statistics.median(w9) if w9 else None,
                                      "wall_range_s": rng(w9)}
    out["runs"]["part_a_stopped_early"] = {"n": len(ws), "wall_range_s": rng(ws)}
    out["runs"]["part_c_event_runs"] = {"n": len(we), "wall_median_s": statistics.median(we) if we else None,
                                        "wall_range_s": rng(we)}
json.dump(out, open(os.path.join(RES, "stage7_paper_numbers.json"), "w"), indent=1, default=float)
print("wrote stage7_paper_numbers.json")
