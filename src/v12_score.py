#!/usr/bin/env python3
"""Stage 5 (version 1.2.0): scoring of P1 to P7 and every registered Stage 5 quantity, by the rules of
predictions_v12.md, from the run records (results/v12_runs/*.json).

Writes results/v12_runs.csv (one row per run), results/v12_results.json (every quantity) and
results/v12_scorecard.json. With some runs still missing it scores what the records allow and says which sets are
incomplete; a verdict is final only when its sets are complete.
"""
import csv, glob, json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v12_run as RUN

RES = os.path.join(HERE, "..", "results")
MEASURED = os.path.join(HERE, "..", "inputs", "fransson2024", "m50_tests.csv")
LO_T, HI_T = 147.0, 342.0          # P1: the measured M50 range, both connections
P3_LO, P3_HI = 150.0, 255.7        # C
P4_LO, P4_HI = 0.2, 0.8            # C/s
P5_MAX = 30.0                      # s
P6_LO, P6_HI = 0.30, 0.90
FACES = ("toward", "away")
# the predictions commit (README); this script was committed before it existed (03af770), so it is recorded here (D48 (1))
PREDICTIONS_COMMIT = "b4883baeac2220b117cd66c28bd8d38dde2d5d62"


def load():
    """Records of the runs that completed, and the ids of any whose integration failed (D43 (3))."""
    recs, failed = {}, []
    for f in glob.glob(os.path.join(RES, "v12_runs", "*.json")):
        r = json.load(open(f))
        if r.get("failed"):
            failed.append(r["id"])
        else:
            recs[r["id"]] = r
    return recs, sorted(failed)


def measured():
    rows = list(csv.DictReader(open(MEASURED)))
    out = {"tests": rows}
    for conn in ("parallel", "series"):
        r = [x for x in rows if x["connection"] == conn]
        t = [float(x["time_to_propagation_s"]) for x in r if x["propagated"] == "Yes"]
        out[conn] = {"n_tests": len(r), "n_propagated": len(t), "times_s": t, "mean_s": float(np.mean(t)),
                     "sd_s": float(np.std(t, ddof=1))}
    allt = out["parallel"]["times_s"] + out["series"]["times_s"]
    out["all"] = {"n_tests": len(rows), "n_propagated": len(allt), "share": len(allt) / len(rows),
                  "min_s": min(allt), "max_s": max(allt), "mean_s": float(np.mean(allt))}
    return out


def flat(r):
    rr, ll = r["resolved"], r["lumped"]
    row = {k: r[k] for k in ("id", "set", "kin", "connection", "h", "g", "tau", "E_body_J", "T_amb_K", "refine", "dt_scale",
                             "h_c_W_m2K", "G_tab_W_K", "G_contact_W_K", "T1max_C", "t_T1max_s", "n_nodes", "wall_s")}
    row.update({"res_propagated": rr["propagated"], "res_t_prop_s": rr.get("t_prop_s"),
                "res_T_mid_toward_C": rr.get("T_mid_toward_C"), "res_T_mid_away_C": rr.get("T_mid_away_C"),
                "res_rate_toward_C_per_s": rr.get("rate_toward_C_per_s"), "res_rate_away_C_per_s": rr.get("rate_away_C_per_s"),
                "res_rate_window_s": rr.get("rate_window_s"),
                "res_rate_section2_toward_C_per_s": rr.get("rate_section2_toward_C_per_s"),
                "res_rate_section2_away_C_per_s": rr.get("rate_section2_away_C_per_s"),
                "res_mean_at_prop_C": rr.get("mean_at_prop_C"), "res_T1_at_prop_C": rr.get("T1_at_prop_C"),
                "res_where_r_mm": (rr.get("where") or {}).get("r_mm"), "res_where_theta_deg": (rr.get("where") or {}).get("theta_deg"),
                "res_where_z_mm": (rr.get("where") or {}).get("z_mm"),
                "res_peak_hottest_C": rr["peak_hottest_C"], "res_t_peak_hottest_s": rr["t_peak_hottest_s"],
                "res_peak_mean_C": rr["peak_mean_C"],
                "res_peak_toward_C": rr["probe_peak"]["toward"]["T_C"], "res_peak_away_C": rr["probe_peak"]["away"]["T_C"],
                "res_energy_residual_rel": rr["energy_residual_rel"], "res_steps": rr["steps"], "res_t_end_s": rr["t_end_s"],
                "lum_propagated": ll["propagated"], "lum_t_prop_s": ll.get("t_prop_s"), "lum_rate_C_per_s": ll.get("rate_C_per_s"),
                "lum_peak_C": ll["peak_C"], "lum_t_peak_s": ll["t_peak_s"]})
    if r.get("draw"):
        row["draw"] = r["draw"]["draw"]
    return row


def sd(x):
    x = [v for v in x if v is not None]
    return float(np.std(x, ddof=1)) if len(x) >= 2 else None


def score(recs, failed=()):
    runs = RUN.build_runs()
    want = {s: [r["id"] for r in runs if r["set"] == s] for s in ("grid", "sens", "v3", "draws", "fact")}
    ended = set(recs) | set(failed)
    complete = {s: all(i in ended for i in ids) for s, ids in want.items()}
    counts = {s: {"total": len(ids), "done": sum(i in recs for i in ids), "failed": sum(i in failed for i in ids)}
              for s, ids in want.items()}
    out = {"complete": complete, "counts": counts, "measured": measured()}
    g = lambda conn, h, gg, tau: recs.get(f"grid_mean_{conn}_h{h}_g{gg}_tau{int(tau)}")
    central = {(conn, tau): g(conn, "central", "central", tau) for conn in ("series", "parallel") for tau in (10.0, 30.0)}
    ok_c = all(v is not None for v in central.values())
    out["central_case"] = {f"{c}_tau{int(t)}": (flat(v) if v else None) for (c, t), v in central.items()}
    sc = {}
    # P1
    if ok_c:
        res = [(k, v["resolved"]) for k, v in central.items()]
        held = all(r["propagated"] and LO_T <= r["t_prop_s"] <= HI_T for _, r in res)
        sc["P1"] = {"held": held, "times_s": {f"{c}_tau{int(t)}": (r["t_prop_s"] if r["propagated"] else None) for (c, t), r in res}}
    # P2
    if ok_c:
        det = {}
        held = True
        for (c, t), v in central.items():
            rr, ll = v["resolved"], v["lumped"]
            if not ll["propagated"]:
                ok, lag = True, None
            elif not rr["propagated"]:
                ok, lag = False, None
            else:
                lag = ll["t_prop_s"] - rr["t_prop_s"]; ok = lag > 20.0
            held &= ok
            det[f"{c}_tau{int(t)}"] = {"held": ok, "lumped_minus_resolved_s": lag, "lumped_propagated": ll["propagated"],
                                       "resolved_propagated": rr["propagated"]}
        sc["P2"] = {"held": held, "cases": det}
    # P3 and P4, per face
    for P, key, lo, hi in (("P3", "T_mid_{}_C", P3_LO, P3_HI), ("P4", "rate_{}_C_per_s", P4_LO, P4_HI)):
        if not ok_c:
            continue
        per_face = {}
        for face in FACES:
            vals, ok = {}, True
            for (c, t), v in central.items():
                rr = v["resolved"]
                x = rr.get(key.format(face)) if rr["propagated"] else None
                vals[f"{c}_tau{int(t)}"] = x
                ok &= (x is not None) and (lo <= x <= hi)
            per_face[face] = {"held": ok, "values": vals}
        both = per_face["toward"]["held"] and per_face["away"]["held"]
        neither = (not per_face["toward"]["held"]) and (not per_face["away"]["held"])
        sc[P] = {"held": both, "verdict": "held" if both else ("failed" if neither else "split"), "faces": per_face}
    # P5
    if ok_c:
        det, held = {}, True
        for t in (10.0, 30.0):
            a, b = central[("series", t)]["resolved"], central[("parallel", t)]["resolved"]
            if a["propagated"] and b["propagated"]:
                d = abs(a["t_prop_s"] - b["t_prop_s"]); ok = d < P5_MAX
            else:
                d, ok = None, False
            held &= ok
            det[f"tau{int(t)}"] = {"held": ok, "abs_difference_s": d}
        sc["P5"] = {"held": held, "pairs": det}
    # P6: the resolved share over the factorial, pooled over both connections
    fact = [recs[i] for i in want["fact"] if i in recs]
    if fact:
        def share(rs, which):
            return float(np.mean([r[which]["propagated"] for r in rs])) if rs else None
        p = share(fact, "resolved")
        n = len(fact)
        sc["P6"] = {"held": (P6_LO <= p <= P6_HI), "share": p, "n": n, "final": complete["fact"],
                    "binomial_se": math.sqrt(p * (1 - p) / n),
                    "by_connection": {c: share([r for r in fact if r["connection"] == c], "resolved") for c in ("series", "parallel")},
                    "lumped_share": share(fact, "lumped"),
                    "lumped_by_connection": {c: share([r for r in fact if r["connection"] == c], "lumped") for c in ("series", "parallel")}}
    # P7: per connection at the 30 s release
    det, held, have7 = {}, True, True
    for c in ("series", "parallel"):
        th = [g(c, h, gg, 30.0) for h in ("low", "central", "high") for gg in ("low", "central", "high")]
        kd = [recs.get(i) for i in want["draws"] if i.endswith(f"_{c}_hcentral_gcentral_tau30")]
        if any(x is None for x in th) or not kd or any(x is None for x in kd):
            have7 = False
        th = [x for x in th if x is not None]
        kd = [x for x in kd if x is not None]
        t_th = [x["resolved"]["t_prop_s"] for x in th if x["resolved"]["propagated"]]
        t_kd = [x["resolved"]["t_prop_s"] for x in kd if x["resolved"]["propagated"]]
        s_th, s_kd = sd(t_th), sd(t_kd)
        ratio = s_th / s_kd if (s_th is not None and s_kd not in (None, 0.0)) else None
        ok = ratio is not None and ratio > 1.0
        held &= ok
        det[c] = {"held": ok, "ratio": ratio, "sd_thermal_s": s_th, "sd_kinetic_s": s_kd,
                  "n_thermal": len(th), "n_thermal_propagated": len(t_th),
                  "n_kinetic": len(kd), "n_kinetic_propagated": len(t_kd)}
    if have7 or any(d["n_kinetic"] for d in det.values()):
        sc["P7"] = {"held": held, "final": have7 and complete["draws"], "by_connection": det}
    out["scorecard"] = sc
    # V3
    v3 = {}
    for c in ("series", "parallel"):
        base = g(c, "central", "central", 30.0)
        for tag in ("refine2", "dthalf"):
            r = recs.get(f"v3_mean_{c}_hcentral_gcentral_tau30_{tag}")
            if base and r:
                b, x = base["resolved"], r["resolved"]
                if b["propagated"] and x["propagated"]:
                    rel = abs(x["t_prop_s"] - b["t_prop_s"]) / b["t_prop_s"]
                    v3[f"{c}_{tag}"] = {"t_base_s": b["t_prop_s"], "t_check_s": x["t_prop_s"], "relative_change": rel,
                                        "pass": rel < 0.02}
                else:
                    # predictions_v12.md: without propagation in both, the check is on the rise of the hottest node's
                    # peak above ambient; if only one of the two propagates, it fails
                    ta = base["T_amb_K"] - 273.15
                    rel = abs(x["peak_hottest_C"] - b["peak_hottest_C"]) / (b["peak_hottest_C"] - ta)
                    v3[f"{c}_{tag}"] = {"base_propagated": b["propagated"], "check_propagated": x["propagated"],
                                        "peak_base_C": b["peak_hottest_C"], "peak_check_C": x["peak_hottest_C"],
                                        "relative_change_of_peak_rise": rel,
                                        "pass": (not b["propagated"]) and (not x["propagated"]) and rel < 0.02}
    out["v3"] = v3
    # energy accounts of every run
    res_all = [abs(r["resolved"]["energy_residual_rel"]) for r in recs.values()]
    out["energy_residual_max"] = max(res_all) if res_all else None
    # the mean grid, the sensitivities and the 10 s release, reported
    out["grid"] = {k: flat(v) for k, v in recs.items() if v["set"] == "grid"}
    out["sens"] = {k: flat(v) for k, v in recs.items() if v["set"] == "sens"}
    out["v3_runs"] = {k: flat(v) for k, v in recs.items() if v["set"] == "v3"}
    return out


def main():
    recs, failed = load()
    out = score(recs, failed)
    out["failed_runs"] = failed
    rows = [flat(r) for r in sorted(recs.values(), key=lambda r: r["id"])]
    if rows:
        keys = sorted({k for r in rows for k in r})
        with open(os.path.join(RES, "v12_runs.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)
    json.dump(out, open(os.path.join(RES, "v12_results.json"), "w"), indent=1, default=float)
    card = {"predictions_commit": PREDICTIONS_COMMIT, "complete": out["complete"], "counts": out["counts"], "failed_runs": failed,
            "scorecard": out["scorecard"], "v3": out["v3"], "energy_residual_max": out["energy_residual_max"]}
    json.dump(card, open(os.path.join(RES, "v12_scorecard.json"), "w"), indent=1, default=float)
    print(json.dumps({"counts": out["counts"], "scorecard": {k: v.get("held") for k, v in out["scorecard"].items()},
                      "v3": {k: v.get("pass") for k, v in out["v3"].items()}}, indent=1))


if __name__ == "__main__":
    main()
