#!/usr/bin/env python3
"""Stage 5 (version 1.2.0): every Stage 5 number that the README, the note and the Zenodo description quote,
computed from the scored records (results/v12_results.json, results/v12_runs.csv, written by v12_score.py), the
run records (results/v12_runs/, for when and where each ran), the series the runs kept (results/v12_series/: the
grid, sens and v3 sets) and the measured tests (inputs/fransson2024/m50_tests.csv). Writes results/v12_numbers.json.

Nothing here is scored; the verdicts are v12_score.py's. The quantities under "exploratory" were defined after the
results (DECISIONS.md D48): the paper's Section 2 heating rate read for runs without propagation, the time each
probe spends at or above the paper's 150 C, and where the hottest node is at its peak, from the series of the grid
and sens sets.
Usage: python3 v12_numbers.py --out ../results
"""
import argparse, csv, glob, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

ap = argparse.ArgumentParser()
ap.add_argument("--out", default=os.path.join(HERE, "..", "results"))
a = ap.parse_args()
OUT = a.out
BAND = 255.7          # C, D35
T150 = 150.0          # C, the paper's minimum (D33 (2))

R = json.load(open(os.path.join(OUT, "v12_results.json")))
rows = list(csv.DictReader(open(os.path.join(OUT, "v12_runs.csv"))))


def num(x):
    return None if x in ("", None, "None") else float(x)


for r in rows:
    for k in list(r):
        if k in ("id", "set", "connection", "h", "g"):
            continue
        if r[k] in ("True", "False"):
            r[k] = r[k] == "True"
        elif k == "kin":
            r[k] = r[k] if r[k] == "mean" else int(r[k])
        else:
            r[k] = num(r[k])


def span(rs, key):
    v = [r[key] for r in rs if r[key] is not None]
    if not v:
        return None
    i_lo, i_hi = int(np.argmin(v)), int(np.argmax(v))
    ids = [r["id"] for r in rs if r[key] is not None]
    return {"min": float(v[i_lo]), "max": float(v[i_hi]), "n": len(v), "min_run": ids[i_lo], "max_run": ids[i_hi]}


PEAKS = ("res_peak_hottest_C", "res_peak_mean_C", "res_peak_toward_C", "res_peak_away_C", "lum_peak_C", "T1max_C",
         "res_t_peak_hottest_s", "lum_t_peak_s", "t_T1max_s")
N = {}
sets = ("grid", "sens", "v3", "draws", "fact")
N["runs"] = {s: sum(r["set"] == s for r in rows) for s in sets}
N["runs"]["all"] = len(rows)
N["propagated"] = {s: {"resolved": sum(r["res_propagated"] for r in rows if r["set"] == s),
                       "lumped": sum(r["lum_propagated"] for r in rows if r["set"] == s)} for s in sets}
N["propagated"]["all"] = {"resolved": sum(r["res_propagated"] for r in rows),
                          "lumped": sum(r["lum_propagated"] for r in rows)}
N["failed_runs"] = R.get("failed_runs", [])
N["counts_complete"] = R["complete"]

# every run: the highest peaks, and how far short of the band
N["all_runs"] = {k: span(rows, k) for k in PEAKS}
N["all_runs"]["band_minus_highest_hottest_K"] = BAND - N["all_runs"]["res_peak_hottest_C"]["max"]
N["all_runs"]["band_minus_highest_lumped_K"] = BAND - N["all_runs"]["lum_peak_C"]["max"]

# the central case
cc = R["central_case"]
cen = {}
for k, v in cc.items():
    cen[k] = {x: v[x] for x in ("T1max_C", "t_T1max_s", "res_propagated", "lum_propagated", "res_peak_hottest_C",
                               "res_t_peak_hottest_s", "res_peak_mean_C", "res_peak_toward_C", "res_peak_away_C",
                               "lum_peak_C", "lum_t_peak_s", "res_energy_residual_rel")}
    cen[k]["resolved_minus_lumped_peak_K"] = v["res_peak_hottest_C"] - v["lum_peak_C"]
    cen[k]["lumped_peak_later_by_s"] = v["lum_t_peak_s"] - v["res_t_peak_hottest_s"]
    cen[k]["toward_below_hottest_K"] = v["res_peak_hottest_C"] - v["res_peak_toward_C"]
crow = [r for r in rows if r["set"] == "grid" and r["h"] == "central" and r["g"] == "central"]
N["central_case"] = {"runs": cen, "span": {k: span(crow, k) for k in PEAKS}}
for k in ("resolved_minus_lumped_peak_K", "lumped_peak_later_by_s", "toward_below_hottest_K"):
    vals = [c[k] for c in cen.values()]
    N["central_case"]["span"][k] = {"min": float(min(vals)), "max": float(max(vals))}
# the probes' peak times are in the records (not the csv)
recs = {}
for f in glob.glob(os.path.join(OUT, "v12_runs", "*.json")):
    r = json.load(open(f))
    recs[r["id"]] = r
for k in cen:
    rid = f"grid_mean_{k.split('_')[0]}_hcentral_gcentral_tau{k.split('tau')[1]}"
    pp = recs[rid]["resolved"]["probe_peak"]
    cen[k]["t_peak_toward_s"], cen[k]["t_peak_away_s"] = pp["toward"]["t_s"], pp["away"]["t_s"]
    cen[k]["in_rxn_J"] = recs[rid]["resolved"]["in_rxn_J"]
    cen[k]["lumped_reaction_heat_J"] = recs[rid]["lumped"]["reaction_heat_J"]

# the grid: by contact level, and by tab level at the central contact
grid = [r for r in rows if r["set"] == "grid"]
N["grid"] = {"by_contact": {h: {k: span([r for r in grid if r["h"] == h], k) for k in PEAKS}
                            for h in ("low", "central", "high")},
             "by_tab_central_contact": {g: {k: span([r for r in grid if r["h"] == "central" and r["g"] == g], k)
                                            for k in ("res_peak_hottest_C", "res_peak_away_C", "lum_peak_C")}
                                        for g in ("low", "central", "high")},
             "h_c_W_m2K": {h: next(r["h_c_W_m2K"] for r in grid if r["h"] == h) for h in ("low", "central", "high")},
             "G_contact_W_K": {h: next(r["G_contact_W_K"] for r in grid if r["h"] == h) for h in ("low", "central", "high")},
             "G_tab_W_K": {g: next(r["G_tab_W_K"] for r in grid if r["g"] == g) for g in ("low", "central", "high")}}
gk = {(r["connection"], r["h"], r["g"], r["tau"]): r for r in grid}
PK3 = ("res_peak_hottest_C", "res_peak_mean_C", "res_peak_away_C", "lum_peak_C")
N["grid"]["tab_high_minus_low"] = {f"{c}_h{h}_tau{int(t)}": {k: gk[(c, h, "high", t)][k] - gk[(c, h, "low", t)][k] for k in PK3}
                                   for c in ("series", "parallel") for h in ("low", "central", "high") for t in (10.0, 30.0)}
N["grid"]["tab_high_minus_low_span"] = {k: {"min": min(v[k] for v in N["grid"]["tab_high_minus_low"].values()),
                                            "max": max(v[k] for v in N["grid"]["tab_high_minus_low"].values())} for k in PK3}
N["central_case"]["series_minus_parallel"] = {f"tau{int(t)}": {k: gk[("series", "central", "central", t)][k]
                                                               - gk[("parallel", "central", "central", t)][k] for k in PK3}
                                              for t in (10.0, 30.0)}

# the 200 kinetic draws at the central case, 30 s release
dr = [r for r in rows if r["set"] == "draws"]
N["draws"] = {c: {k: span([r for r in dr if r["connection"] == c], k) for k in PEAKS} for c in ("series", "parallel")}
for c in ("series", "parallel"):
    ids = [r["id"] for r in dr if r["connection"] == c]
    N["draws"][c]["in_rxn_J"] = {"min": min(recs[i]["resolved"]["in_rxn_J"] for i in ids),
                                 "max": max(recs[i]["resolved"]["in_rxn_J"] for i in ids)}
    N["draws"][c]["lumped_reaction_heat_J"] = {"min": min(recs[i]["lumped"]["reaction_heat_J"] for i in ids),
                                               "max": max(recs[i]["lumped"]["reaction_heat_J"] for i in ids)}

# the factorial: all, and by contact level
fa = [r for r in rows if r["set"] == "fact"]
N["fact"] = {"all": {k: span(fa, k) for k in PEAKS},
             "by_contact": {h: {k: span([r for r in fa if r["h"] == h], k) for k in ("res_peak_hottest_C", "lum_peak_C",
                                                                                     "res_peak_away_C")}
                            for h in ("low", "central", "high")},
             "by_connection": {c: {k: span([r for r in fa if r["connection"] == c], k)
                                   for k in ("res_peak_hottest_C", "lum_peak_C")} for c in ("series", "parallel")}}

# the sensitivities at the central case (30 s), against the central case
sens = {}
for r in rows:
    if r["set"] != "sens":
        continue
    base = cc[f"{r['connection']}_tau30"]
    sens[r["id"]] = {"E_body_J": r["E_body_J"], "T_amb_C": r["T_amb_K"] - 273.15,
                     "res_peak_hottest_C": r["res_peak_hottest_C"], "lum_peak_C": r["lum_peak_C"],
                     "res_peak_away_C": r["res_peak_away_C"], "T1max_C": r["T1max_C"],
                     "d_res_peak_hottest_K": r["res_peak_hottest_C"] - base["res_peak_hottest_C"],
                     "d_lum_peak_K": r["lum_peak_C"] - base["lum_peak_C"],
                     "d_res_peak_away_K": r["res_peak_away_C"] - base["res_peak_away_C"],
                     "propagated": [r["res_propagated"], r["lum_propagated"]]}
N["sens"] = sens

# the measurements beside them
M = R["measured"]
tests = M["tests"]
N["measured"] = {
    "propagated": {"n": M["all"]["n_propagated"], "of": M["all"]["n_tests"], "share": M["all"]["share"],
                   "times_min_s": M["all"]["min_s"], "times_max_s": M["all"]["max_s"], "mean_s": M["all"]["mean_s"]},
    "by_connection": {c: {k: M[c][k] for k in ("n_tests", "n_propagated", "mean_s", "sd_s")} for c in ("series", "parallel")},
    "trigger_max_C": {"min": min(float(t["trigger_max_C"]) for t in tests), "max": max(float(t["trigger_max_C"]) for t in tests),
                      "median": float(np.median([float(t["trigger_max_C"]) for t in tests]))},
    "neighbour_max_not_propagated_C": sorted(float(t["neighbour_max_C"]) for t in tests if t["propagated"] == "No"),
    "neighbour_max_propagated_C": sorted(float(t["neighbour_max_C"]) for t in tests if t["propagated"] == "Yes")}
t1c = N["central_case"]["span"]["T1max_C"]["max"]
N["measured"]["trigger_max_above_model_central_C"] = {
    "model_central_T1max_C": t1c,
    "n_above": sum(float(t["trigger_max_C"]) > t1c for t in tests),
    "above_min_C": min(float(t["trigger_max_C"]) for t in tests if float(t["trigger_max_C"]) > t1c),
    "not_above_C": sorted(float(t["trigger_max_C"]) for t in tests if float(t["trigger_max_C"]) <= t1c)}

# where and when the runs were made (D45 to D47)
mach = {}
for r in recs.values():
    lab = r.get("machine", {}).get("label", "none")
    m = mach.setdefault(lab, {"runs": 0, "first_start_utc": "9", "last_finish_utc": "0", "wall_s": []})
    m["runs"] += 1
    m["first_start_utc"] = min(m["first_start_utc"], r["started_utc"])
    m["last_finish_utc"] = max(m["last_finish_utc"], r["finished_utc"])
    m["wall_s"].append(r["wall_s"])
for m in mach.values():
    w = np.array(m.pop("wall_s"))
    m["wall_s_median"], m["wall_s_total_h"] = float(np.median(w)), float(w.sum() / 3600)
N["machines"] = mach
N["memory_retries"] = {"runs_with_retries": sum(1 for r in recs.values() if r.get("memory_retries")),
                       "retries": int(sum(r.get("memory_retries") or 0 for r in recs.values()))}
merge = os.path.join(OUT, "v12_merge.json")
if os.path.exists(merge):
    mg = json.load(open(merge))
    md = mg["both_machines"]["max_abs_difference"]
    temps = [v["value"] for k, v in md.items() if k.endswith("_C") or k.endswith("T_C")]
    N["merge"] = {"by_source": mg["by_source"], "by_machine_label": mg["by_machine_label"], "missing": len(mg["missing"]),
                  "failed": len(mg["failed"]), "both_machines": mg["both_machines"]["n"],
                  "non_numeric_differences": len(mg["both_machines"]["non_numeric_differences"]),
                  "largest": dict(list(md.items())[:3]), "largest_temperature_difference_K": max(temps) if temps else None,
                  "energy_residual_difference": md.get("resolved.energy_residual_rel", {}).get("value")}
fm = os.path.join(OUT, "v12_failed_memory")
if os.path.isdir(fm):
    fr = [json.load(open(f)) for f in glob.glob(os.path.join(fm, "*.json"))]
    ev = {}
    for r in fr:
        ev[r["finished_utc"][:16]] = ev.get(r["finished_utc"][:16], 0) + 1
    N["failed_memory"] = {"records": len(fr), "events_by_minute_utc": ev,
                          "draws": [min(r["kin"] for r in fr), max(r["kin"] for r in fr)] if fr else None,
                          "redone_all": all(r["id"] in recs and not recs[r["id"]].get("failed") for r in fr)}

# checks quoted from the scoring
N["v3"] = R["v3"]
N["energy_residual_max"] = R["energy_residual_max"]

# ------------------------------------------------------------------------------------------- exploratory (D48)
import v12_model as V          # noqa: E402  (sets the paths of the published solver)
import v12_mesh as MS          # noqa: E402
mesh, _ = MS.build_mesh(V.R, V.LZ, 1.0)
p = mesh.p
EX = {"section2_rate_without_propagation": {}, "time_above_150C": {}, "hottest_node_at_peak": {}}
for f in sorted(glob.glob(os.path.join(OUT, "v12_series", "*.npz"))):
    rid = os.path.basename(f)[:-4]
    if rid not in recs or recs[rid]["set"] not in ("grid", "sens"):
        continue
    S = np.load(f)
    rec = recs[rid]
    if rec["resolved"]["propagated"]:
        continue
    t1m = float(rec["t_T1max_s"])                        # cell 1's maximum (the record's): the start of Section 2
    tr = {}
    for name, t, T in (("toward", S["probe_t"], S["probe_toward"] - 273.15),
                       ("away", S["probe_t"], S["probe_away"] - 273.15),
                       ("lumped", S["t_lumped"], S["T_lumped"] - 273.15)):
        j = int(np.argmax(T)); tm = float(t[j])             # the neighbour's maximum: the end of Section 2 here
        T_at = float(np.interp(t1m, t, T))
        tr[name] = {"t_start_s": t1m, "T_start_C": T_at, "t_end_s": tm, "T_end_C": float(T[j]),
                    "rate_C_per_s": (float(T[j]) - T_at) / (tm - t1m) if tm > t1m else None}
        idx = np.where(T >= T150)[0]
        if idx.size:                                       # crossings interpolated within the step, as D35
            i0, i1 = int(idx[0]), int(idx[-1])
            t_on = float(t[i0]) if i0 == 0 else float(t[i0 - 1] + (T150 - T[i0 - 1]) / (T[i0] - T[i0 - 1]) * (t[i0] - t[i0 - 1]))
            t_off = float(t[i1]) if i1 == len(t) - 1 else float(t[i1] + (T[i1] - T150) / (T[i1] - T[i1 + 1]) * (t[i1 + 1] - t[i1]))
            EX["time_above_150C"].setdefault(rid, {})[name] = {"from_s": t_on, "to_s": t_off, "duration_s": t_off - t_on}
        else:
            EX["time_above_150C"].setdefault(rid, {})[name] = None
    EX["section2_rate_without_propagation"][rid] = tr
    k = int(np.argmax(S["Tmax"]))
    node = int(S["imax"][k])
    x, y, z = p[0, node], p[1, node], p[2, node]
    EX["hottest_node_at_peak"][rid] = {"t_s": float(S["t"][k]), "T_C": float(S["Tmax"][k] - 273.15), "node": node,
                                       "r_mm": 1e3 * float(np.hypot(x, y)),
                                       "theta_deg": float(np.degrees(np.arctan2(y, x))), "z_mm": 1e3 * float(z)}
# summaries over the grid (posterior-mean kinetics, 36 runs)
gr = {k: v for k, v in EX["section2_rate_without_propagation"].items() if k.startswith("grid_")}
EX["section2_rate_grid_span"] = {n: {"min": min(v[n]["rate_C_per_s"] for v in gr.values()),
                                     "max": max(v[n]["rate_C_per_s"] for v in gr.values())} for n in ("toward", "away", "lumped")}
hn = [v for k, v in EX["hottest_node_at_peak"].items() if k.startswith("grid_")]
EX["hottest_node_grid_span"] = {q: {"min": min(v[q] for v in hn), "max": max(v[q] for v in hn)}
                                for q in ("r_mm", "theta_deg", "z_mm", "t_s")}
N["exploratory"] = EX
json.dump(N, open(os.path.join(OUT, "v12_numbers.json"), "w"), indent=1, default=float)
c30 = N["central_case"]["runs"]
print(json.dumps({"runs": N["runs"], "propagated_all": N["propagated"]["all"],
                  "highest_hottest": N["all_runs"]["res_peak_hottest_C"], "highest_lumped": N["all_runs"]["lum_peak_C"],
                  "central": {k: [round(v["res_peak_hottest_C"], 2), round(v["lum_peak_C"], 2), round(v["res_peak_away_C"], 2)]
                              for k, v in c30.items()}}, indent=1))
