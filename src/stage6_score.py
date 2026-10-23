#!/usr/bin/env python3
"""Stage 6: scoring of P1 to P7 by the rules of predictions_stage6.md, and the Part B tables.

Reads results/stage6_crossings.csv (Part A, stage6_crossings.py), results/stage6_trigger.json and
results/stage6_runs/*.json (Part B, stage6_run.py), and the Stage 5 grid records for P3's reference values.
Writes results/stage6_matched.csv (one row per Part B run), results/stage6_matched.json (the selection, the Part B
quantities by set, V3 and the energy accounts) and results/stage6_scorecard.json. With runs missing it scores what
the records allow and says which sets are incomplete; a verdict is final only when its sets are complete.
Usage: python3 stage6_score.py [--res DIR] [--predictions-commit HASH]
"""
import argparse, csv, glob, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage6_inputs as IN

LO, HI = IN.WINDOW_S                 # 147 and 342 s, inclusive
P2_LEVEL = IN.NP_QUOTED_MAX_C       # 133 C, strictly above
P3_RISE_K = 20.0
P6_LO, P6_HI = 0.10, 0.70
V3_TOL = 0.01                       # 1 % (the brief)
ENERGY_TOL = 1e-9
T_AMB_C = 25.0
SETS6 = ("v3", "body", "total", "bracket", "peak", "draws")


def num(x):
    if x in ("", None, "None"):
        return None
    if x in ("True", "False"):
        return x == "True"
    try:
        return float(x)
    except ValueError:
        return x


def part_a_rows(res):
    rows = list(csv.DictReader(open(os.path.join(res, "stage6_crossings.csv"))))
    for r in rows:
        for k in list(r):
            if k not in ("id", "set", "connection", "h", "g", "kin") and not k.endswith("_window"):
                r[k] = num(r[k])
            elif k.endswith("_window"):
                r[k] = r[k] or None
    return rows


def score_part_a(rows):
    grid = [r for r in rows if r["set"] == "grid"]
    withs = [r for r in rows if r["has_series"]]
    sc = {}
    # P1
    lum = [r for r in grid if r["lumped_crosses"]]
    inside = [r for r in lum if r["lumped_t_cross_s"] is not None and LO <= r["lumped_t_cross_s"] <= HI]
    share = len(inside) / len(lum) if lum else None
    part1 = share is not None and share > 0.5
    hot = [r for r in grid if r["hot_crosses"]]
    below = [r for r in hot if r["hot_t_cross_s"] is not None and r["hot_t_cross_s"] < LO]
    part2 = len(hot) > 0 and len(below) == len(hot)
    strict2 = len(grid) > 0 and all(r["hot_crosses"] and r["hot_t_cross_s"] is not None and r["hot_t_cross_s"] < LO
                                    for r in grid)

    def p1_on(rs):
        l = [r for r in rs if r["lumped_crosses"]]
        i = [r for r in l if r["lumped_t_cross_s"] is not None and LO <= r["lumped_t_cross_s"] <= HI]
        h = [r for r in rs if r["hot_crosses"]]
        b = [r for r in h if r["hot_t_cross_s"] is not None and r["hot_t_cross_s"] < LO]
        return {"n": len(rs), "lumped_crossing": len(l), "lumped_inside": len(i),
                "lumped_share_inside": (len(i) / len(l)) if l else None, "hot_crossing": len(h), "hot_below_147": len(b)}

    sc["P1"] = {"held": bool(part1 and part2), "verdict": "held" if (part1 and part2) else "failed",
                "scored_on": "the 36 grid runs (posterior mean, every contact, tab, release and connection)",
                "lumped": {"crossing": len(lum), "inside": len(inside), "share_inside": share, "held": part1,
                           "times_s": sorted(r["lumped_t_cross_s"] for r in lum)},
                "hot": {"crossing": len(hot), "below_147": len(below), "held": part2,
                        "times_s": sorted(r["hot_t_cross_s"] for r in hot), "not_crossing": len(grid) - len(hot),
                        "strict_reading_every_grid_run_held": strict2},
                "reported": {"sens": p1_on([r for r in rows if r["set"] == "sens"]),
                             "v3": p1_on([r for r in rows if r["set"] == "v3"]), "all_with_series": p1_on(withs)}}
    # P2
    above = [r for r in rows if r["away_peak_C"] > P2_LEVEL]
    share2 = len(above) / len(rows)
    per = {}
    for s in ("grid", "sens", "v3", "draws", "fact"):
        rs = [r for r in rows if r["set"] == s]
        per[s] = {"n": len(rs), "above_133": sum(r["away_peak_C"] > P2_LEVEL for r in rs)}
    per_h = {}
    for h in ("low", "central", "high"):
        rs = [r for r in rows if r["h"] == h]
        per_h[h] = {"n": len(rs), "above_133": sum(r["away_peak_C"] > P2_LEVEL for r in rs),
                    "away_peak_min_C": min(r["away_peak_C"] for r in rs), "away_peak_max_C": max(r["away_peak_C"] for r in rs)}
    sc["P2"] = {"held": share2 < 0.5, "verdict": "held" if share2 < 0.5 else "failed", "n": len(rows),
                "above_133": len(above), "share_above": share2, "by_set": per, "by_contact": per_h,
                "toward_above_133": sum(r["toward_peak_C"] > P2_LEVEL for r in rows)}
    return sc


def load_b(res):
    recs, failed = {}, []
    for f in glob.glob(os.path.join(res, "stage6_runs", "*.json")):
        r = json.load(open(f))
        (failed.append(r["id"]) if r.get("failed") else recs.__setitem__(r["id"], r))
    return recs, sorted(failed)


def flat_b(r):
    rr, ll, q = r["resolved"], r["lumped"], r["stage6"]
    row = {k: r[k] for k in ("id", "set", "kin", "connection", "h", "g", "tau", "E_body_J", "refine", "dt_scale",
                             "T1max_C", "t_T1max_s", "wall_s")}
    row["draw"] = r["draw"]["draw"] if r.get("draw") else None
    for c, d in q["crossings_150C"].items():
        row.update({f"{c}_peak_C": d["peak_C"], f"{c}_t_peak_s": d["t_peak_s"], f"{c}_t_cross_150_s": d["t_cross_s"],
                    f"{c}_t_return_150_s": d["t_return_s"]})
    row.update({"hot_t_255_7_s": q["reach_255_7C"]["hot_t_s"], "lumped_t_255_7_s": q["reach_255_7C"]["lumped_t_s"],
                "res_t_end_s": rr["t_end_s"], "lum_t_end_s": ll["t_end_s"],
                "res_energy_residual_rel": rr["energy_residual_rel"], "res_in_rxn_J": rr["in_rxn_J"],
                "lum_reaction_heat_J": ll["reaction_heat_J"]})
    w = rr.get("where") or {}
    row.update({"res_where_theta_deg": w.get("theta_deg"), "res_where_z_mm": w.get("z_mm"), "res_where_r_mm": w.get("r_mm")})
    return row


def score_part_b(recs, failed, trig, stage5_runs):
    sys.path.insert(0, HERE)
    import stage6_run as S6
    runs = S6.build_runs(trig["central_matched_case"]["E_J"], trig["peak_matched_exploratory"]["E_J"])
    want = {s: [r["id"] for r in runs if r["set"] == s] for s in SETS6}
    ended = set(recs) | set(failed)
    complete = {s: all(i in ended for i in ids) for s, ids in want.items()}
    counts = {s: {"total": len(ids), "done": sum(i in recs for i in ids), "failed": sum(i in failed for i in ids)}
              for s, ids in want.items()}
    L = trig["levels"]
    tm = L["tau_median_s"]
    sc, out = {}, {"complete": complete, "counts": counts, "failed": failed}
    central = lambda s, conn, tau, e: recs.get(f"{s}_mean_{conn}_hcentral_gcentral_tau{tau:.2f}_E{e / 1e3:.2f}")
    # P3
    ref = {}
    for conn in ("series", "parallel"):
        vals = [stage5_runs[f"grid_mean_{conn}_hcentral_gcentral_tau{t}"]["lumped"]["peak_C"] for t in (10, 30)]
        ref[conn] = {"stage5_tau10_C": vals[0], "stage5_tau30_C": vals[1], "reference_C": max(vals)}
    det, ok3, have3 = {}, True, True
    for conn in ("series", "parallel"):
        for tau in L["tau_s"]:
            r = central("body", conn, tau, L["E_body_J"])
            if r is None:
                have3 = False
                continue
            pk = r["lumped"]["peak_C"]
            rise = pk - ref[conn]["reference_C"]
            det[f"{conn}_tau{tau:.2f}"] = {"lumped_peak_C": pk, "above_reference_K": rise, "held": rise >= P3_RISE_K}
            ok3 &= rise >= P3_RISE_K
    if have3:
        n_ok = sum(v["held"] for v in det.values())
        sc["P3"] = {"held": ok3, "verdict": "held" if ok3 else "failed", "reference": ref, "runs": det,
                    "held_in": n_ok, "of": len(det)}
    # P4
    rows4 = [r for r in trig["rows"] if r["energy"] == "total"]
    ok4 = all(r["inside_measured_range"] for r in rows4)
    sc["P4"] = {"held": ok4, "verdict": "held" if ok4 else "failed", "inside": sum(r["inside_measured_range"] for r in rows4),
                "of": len(rows4), "T1max_C": {f"{r['connection']}_tau{r['tau_s']:.2f}": r["T1max_C"] for r in rows4},
                "measured_range_C": trig["measured_trigger_max_range_C"],
                "bracket_T1max_C": {f"{r['energy']}_{r['connection']}_tau{r['tau_s']:.2f}": r["T1max_C"]
                                    for r in trig["rows"] if r["energy"].startswith("bracket")}}
    # P5: the posterior-mean runs of every qualifying pair (D54 (2))
    pairs = [(name, float(tau_s)) for name in ("body", "total")
             for tau_s in L["tau_s"] if trig["qualifies_at_every_connection"][name][f"{tau_s:.2f}"]]
    sel = [r for r in recs.values() if r["set"] in ("body", "total") and any(r["set"] == n and abs(r["tau"] - t) < 1e-9
                                                                              for n, t in pairs)]
    n_want5 = 14 * len(pairs)
    if pairs and len(sel) == n_want5:
        hot5 = [r["id"] for r in sel if r["resolved"]["propagated"]]
        lum5 = [r["id"] for r in sel if r["lumped"]["propagated"]]
        ok5 = len(hot5) >= 1 and len(lum5) == 0
        sc["P5"] = {"held": ok5, "verdict": "held" if ok5 else "failed",
                    "matched_pairs": [{"energy": n, "tau_s": t} for n, t in pairs], "n_runs": len(sel),
                    "hot_reaches": len(hot5), "lumped_reaches": len(lum5), "hot_runs": sorted(hot5),
                    "lumped_runs": sorted(lum5), "part_hot_held": len(hot5) >= 1, "part_lumped_held": len(lum5) == 0,
                    "hot_peak_max_C": max(r["resolved"]["peak_hottest_C"] for r in sel),
                    "lumped_peak_max_C": max(r["lumped"]["peak_C"] for r in sel)}
    elif not pairs:
        sc["P5"] = {"held": None, "verdict": "not scored: no matched case"}
    # P6
    dr = [r for r in recs.values() if r["set"] == "draws"]
    if complete["draws"] and dr:
        k = sum(r["resolved"]["propagated"] for r in dr)
        n = len(dr)
        share = k / n
        ok6 = P6_LO <= share <= P6_HI
        per = {c: {"n": sum(r["connection"] == c for r in dr),
                   "hot_reaches": sum(r["resolved"]["propagated"] for r in dr if r["connection"] == c)} for c in ("series", "parallel")}
        sc["P6"] = {"held": ok6, "verdict": "held" if ok6 else "failed", "hot_reaches": k, "n": n, "share": share,
                    "binomial_se": math.sqrt(share * (1 - share) / n), "by_connection": per,
                    "lumped_reaches": sum(r["lumped"]["propagated"] for r in dr),
                    "hot_peak_min_C": min(r["resolved"]["peak_hottest_C"] for r in dr),
                    "hot_peak_max_C": max(r["resolved"]["peak_hottest_C"] for r in dr)}
    # P7: every Part B run
    allb = list(recs.values())
    if all(complete.values()):
        lum = [r for r in allb if r["lumped"]["propagated"]]
        bad = [r["id"] for r in lum if not (r["resolved"]["propagated"] and r["resolved"]["t_prop_s"] < r["lumped"]["t_prop_s"])]
        reg_lum = [r for r in lum if r["set"] != "peak"]
        reg_bad = [i for i in bad if not i.startswith("peak_")]
        lags = [r["lumped"]["t_prop_s"] - r["resolved"]["t_prop_s"] for r in lum if r["resolved"]["propagated"]]
        sc["P7"] = {"held": len(bad) == 0, "verdict": "held" if not bad else "failed", "n_runs": len(allb),
                    "lumped_reaches": len(lum), "violations": sorted(bad),
                    "registered_sets_only": {"lumped_reaches": len(reg_lum), "violations": sorted(reg_bad),
                                             "held": len(reg_bad) == 0},
                    "lumped_minus_hot_s": {"min": min(lags), "max": max(lags)} if lags else None,
                    "hot_reaches": sum(r["resolved"]["propagated"] for r in allb)}
    # V3
    ce = trig["central_matched_case"]
    v3 = {}
    if ce["E_J"] is not None:
        base_set = ce["energy"]
        for conn in ("series", "parallel"):
            b = central(base_set, conn, tm, ce["E_J"])
            for tag in ("refine2", "dthalf"):
                v = recs.get(f"v3_mean_{conn}_hcentral_gcentral_tau{tm:.2f}_E{ce['E_J'] / 1e3:.2f}_{tag}")
                if b is None or v is None:
                    continue
                if b["resolved"]["propagated"] and v["resolved"]["propagated"]:
                    q = abs(v["resolved"]["t_prop_s"] - b["resolved"]["t_prop_s"]) / b["resolved"]["t_prop_s"]
                    what = "time of the hottest node's 255.7 C crossing"
                elif not b["resolved"]["propagated"] and not v["resolved"]["propagated"]:
                    rise = b["resolved"]["peak_hottest_C"] - T_AMB_C
                    q = abs(v["resolved"]["peak_hottest_C"] - b["resolved"]["peak_hottest_C"]) / rise
                    what = "peak rise of the hottest node"
                else:
                    q, what = float("inf"), "one propagates and the other does not"
                lum_q = abs(v["lumped"]["peak_C"] - b["lumped"]["peak_C"]) / (b["lumped"]["peak_C"] - T_AMB_C)
                v3[f"{conn}_{tag}"] = {"relative_change": q, "quantity": what, "pass": q < V3_TOL,
                                       "lumped_peak_relative_change": lum_q, "base": b["id"], "check": v["id"]}
        out["v3"] = {"cases": v3, "acceptance": V3_TOL, "pass": bool(v3) and all(c["pass"] for c in v3.values())}
    res_max = max((abs(r["resolved"]["energy_residual_rel"]) for r in allb), default=None)
    out["energy"] = {"max_abs_residual_rel": res_max, "acceptance": ENERGY_TOL,
                     "pass": res_max is not None and res_max < ENERGY_TOL}
    # by set, for the tables
    by = {}
    for s in SETS6:
        rs = [r for r in allb if r["set"] == s]
        if not rs:
            continue
        by[s] = {"n": len(rs), "hot_reaches": sum(r["resolved"]["propagated"] for r in rs),
                 "lumped_reaches": sum(r["lumped"]["propagated"] for r in rs),
                 "T1max_C": [min(r["T1max_C"] for r in rs), max(r["T1max_C"] for r in rs)],
                 "hot_peak_C": [min(r["resolved"]["peak_hottest_C"] for r in rs), max(r["resolved"]["peak_hottest_C"] for r in rs)],
                 "lumped_peak_C": [min(r["lumped"]["peak_C"] for r in rs), max(r["lumped"]["peak_C"] for r in rs)],
                 "away_peak_C": [min(r["resolved"]["probe_peak"]["away"]["T_C"] for r in rs),
                                 max(r["resolved"]["probe_peak"]["away"]["T_C"] for r in rs)]}
        t_hot = [r["resolved"]["t_prop_s"] for r in rs if r["resolved"]["propagated"]]
        t_lum = [r["lumped"]["t_prop_s"] for r in rs if r["lumped"]["propagated"]]
        by[s]["hot_t_255_7_s"] = [min(t_hot), max(t_hot)] if t_hot else None
        by[s]["lumped_t_255_7_s"] = [min(t_lum), max(t_lum)] if t_lum else None
        for c in ("hot", "mean", "away", "toward", "lumped"):
            tc = [r["stage6"]["crossings_150C"][c]["t_cross_s"] for r in rs if r["stage6"]["crossings_150C"][c]["t_cross_s"] is not None]
            by[s][f"{c}_150C"] = {"crossing": len(tc), "inside": sum(LO <= t <= HI for t in tc),
                                  "range_s": [min(tc), max(tc)] if tc else None}
    out["by_set"] = by
    out["selection"] = {k: trig[k] for k in ("qualifies_at_every_connection", "central_matched_case",
                                             "peak_matched_exploratory")}
    return sc, out


def main(res, predictions_commit=None):
    scorecard = {"predictions": "predictions_stage6.md", "predictions_commit": predictions_commit}
    rows = part_a_rows(res)
    scorecard.update(score_part_a(rows))
    trig = json.load(open(os.path.join(res, "stage6_trigger.json")))
    recs, failed = load_b(res)
    stage5 = {}
    for conn in ("series", "parallel"):
        for t in (10, 30):
            i = f"grid_mean_{conn}_hcentral_gcentral_tau{t}"
            stage5[i] = json.load(open(os.path.join(res, "v12_runs", i + ".json")))
    sc, out = score_part_b(recs, failed, trig, stage5)
    scorecard.update(sc)
    scorecard["V3"] = out.get("v3")
    scorecard["energy"] = out["energy"]
    scorecard["complete"] = out["complete"]
    flat = [flat_b(r) for r in sorted(recs.values(), key=lambda r: r["id"])]
    if flat:
        with open(os.path.join(res, "stage6_matched.csv"), "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(flat[0].keys()))
            w.writeheader()
            for r in flat:
                w.writerow(r)
    json.dump(out, open(os.path.join(res, "stage6_matched.json"), "w"), indent=1, default=float)
    json.dump(scorecard, open(os.path.join(res, "stage6_scorecard.json"), "w"), indent=1, default=float)
    brief = {k: (v.get("verdict") if isinstance(v, dict) else v) for k, v in scorecard.items() if k.startswith("P")}
    print(json.dumps(brief, indent=1))
    return scorecard


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", default=os.path.join(HERE, "..", "results"))
    ap.add_argument("--predictions-commit", default=None)
    a = ap.parse_args()
    main(a.res, a.predictions_commit)
