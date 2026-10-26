#!/usr/bin/env python3
"""Every Stage 8 number quoted in the README, the note, the release notes and the Zenodo description
(results/stage8_paper_numbers.json; DECISIONS.md D84), computed from the Stage 8 records and the scoring's outputs,
the file from which a manuscript of Stages 1 to 8 is to be written.
Usage: python3 stage8_numbers.py
"""
import csv, json, os, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage8_inputs as IN               # noqa: E402
import stage8_run as R8                  # noqa: E402
import stage8_search as SR               # noqa: E402

RES = os.path.join(HERE, "..", "results")


def r1(x, n=1):
    return None if x is None else round(float(x), n)


def fsd(fs):
    """f* as a dict for the file: status, lower and upper end."""
    return {"status": fs["status"], "lo": fs.get("lo"), "hi": fs.get("hi")}


def main():
    recs = R8.load_records()
    states = R8.all_states(recs)
    v = json.load(open(os.path.join(RES, "stage8_verdicts.json")))
    card = json.load(open(os.path.join(RES, "stage8_scorecard.json")))
    pd = json.load(open(os.path.join(RES, "stage8_partd.json")))
    chk = json.load(open(os.path.join(RES, "stage8_checks.json"))) if os.path.exists(
        os.path.join(RES, "stage8_checks.json")) else None
    rows = v["thresholds"]
    by = {r["test"]: r for r in rows}
    rat = IN.ratios()
    ej = IN.ejected(rat)
    out = {"what": "Every Stage 8 number quoted in the README, the note, the release notes and the Zenodo description "
                   "(DECISIONS.md D84), computed by src/stage8_numbers.py from the Stage 8 records and the scoring."}
    # inputs
    ee = sorted((x["E_e_J"], k) for k, x in ej.items())
    out["inputs"] = {
        "ratio": {"central": rat["central"], "low": rat["low"], "high": rat["high"], "low_test": rat["low_test"],
                  "high_test": rat["high_test"], "n_rows": len(rat["rows"]),
                  "body_percent_range": [min(d["body_percent"] for d in rat["rows"]),
                                         max(d["body_percent"] for d in rat["rows"])]},
        "E_e_J_range": [ee[0][0], ee[-1][0]], "E_e_J_range_tests": [ee[0][1], ee[-1][1]],
        "E_b_J_range": [min(x["E_b_J"] for x in ej.values()), max(x["E_b_J"] for x in ej.values())],
        "tau_d_s": IN.tau_median_s(), "tau_d_conditional_s": list(IN.TAU_D_CONDITIONAL_S),
        "f_e": list(IN.F_E), "E_joule_J": [f * IN.E_STORED_J for f in IN.F_E], "E_stored_J": IN.E_STORED_J,
        "gas_layer": {"T_vap_DMC_C": IN.T_VAP_DMC_C, "T_vap_EC_C": IN.T_VAP_EC_C, "R_max_heated": IN.R_MAX_HEATED,
                      "R_max_cold": IN.R_MAX_COLD, "d_max_m": IN.D_VAP_MAX_M, "lambda_W_mK": IN.LAMBDA_GAS},
        "levels_C": {"C1_C2": IN.LEVEL_PROP_C, "C3": IN.LEVEL_150_C}, "width": IN.WIDTH,
        "common_f": list(IN.COMMON_F), "sensitivity_tests": R8.sens_tests(), "median_tests": IN.median_tests(),
        "median_trigger_J": IN.sensitivity_tests()["median_J"]}
    # runs
    good = [r for r in recs.values() if not r.get("failed")]
    by_set = {}
    for r in recs.values():
        by_set[r["set"]] = by_set.get(r["set"], 0) + 1
    walls = [r["wall_s"] for r in good if r.get("wall_s") is not None]
    st_utc = sorted(r["started_utc"] for r in recs.values() if r.get("started_utc"))
    fi_utc = sorted(r["finished_utc"] for r in recs.values() if r.get("finished_utc"))
    out["runs"] = {"n": len(recs), "failed": sorted(k for k, r in recs.items() if r.get("failed")), "by_set": by_set,
                   "first_started_utc": st_utc[0] if st_utc else None, "last_finished_utc": fi_utc[-1] if fi_utc else None,
                   "wall_s_median": statistics.median(walls) if walls else None, "wall_s_max": max(walls) if walls else None,
                   "resumed": {k: r["resolved"].get("resumed") for k, r in recs.items()
                               if r.get("resolved") and r["resolved"].get("resumed")},
                   "chains_unfinished": v["unfinished_chains"]}
    # Part A
    pa = {"per_test": {}}
    for r in rows:
        pa["per_test"][r["test"]] = {"connection": r["connection"], "E_b_J": r["E_b_J"], "E_e_J": r["E_e_J"],
                                     "propagated": r["propagated"], "time_s": r["time_s"], "fC1": fsd(r["fC1"]),
                                     "fC2": fsd(r["fC2"]), "fC3_exploratory": r["fC3_exploratory"]}
    for key in ("fC1", "fC2"):
        zero = [r["test"] for r in rows if r[key]["status"] == "zero"]
        brk = [r for r in rows if r[key]["status"] == "bracket"]
        pa[key] = {"zero": zero, "n_zero": len(zero), "above_1": [r["test"] for r in rows if r[key]["status"] == "above"],
                   "largest_hi": max((r[key]["hi"] for r in brk), default=None),
                   "largest_hi_test": max(brk, key=lambda r: r[key]["hi"])["test"] if brk else None,
                   "n_hi_at_most_0.0125": sum(1 for r in brk if r[key]["hi"] <= 0.0125 + 1e-12),
                   "n_below_0.05": sum(1 for r in rows if SR.below(r[key], 0.05) is True),
                   "n_below_0.1": sum(1 for r in rows if SR.below(r[key], 0.1) is True),
                   "n_below_0.3": sum(1 for r in rows if SR.below(r[key], 0.3) is True)}
        for grp, name in ((True, "propagated"), (False, "not_propagated")):
            g = [r for r in rows if r["propagated"] == grp]
            pa[key][name] = {r["test"]: fsd(r[key]) for r in g}
    out["part_a"] = pa
    # Part C
    pc = {}
    for f, d in card["by_fraction"].items():
        pc[f] = {c: {"predicted": d[c]["predicted"], "score": d[c]["score"], "counts": d[c]["counts"],
                     "errors_s": d[c]["errors_s"], "within_60_s": d[c]["within_60_s"],
                     "times_s": sorted(x["t_s"] for x in d[c]["per_test"].values() if x.get("predicted"))}
                 for c in IN.CRITERIA}
    pc["0"] = {c: {"predicted": card["stage7_f0"][c]["predicted"], "score": card["stage7_f0"][c]["score"],
                   "counts": card["stage7_f0"][c]["counts"]} for c in IN.CRITERIA}
    out["part_c"] = pc
    # Part B
    pb = {}
    for r in rows:
        if r["connection"] != "parallel":
            continue
        pb[r["test"]] = {"partA": fsd(r["fC1"])}
        for s in ("elec05_c1", "elec20_c1"):
            x = r["variants"][s]
            pb[r["test"]][s] = {"f": fsd(x["f"]), "lowering": x["lowering"], "relation": x["relation"]}
    out["part_b"] = pb
    # A4
    a4 = {}
    for r in rows:
        if r["sensitivity"]:
            a4[r["test"]] = {s: {"f": fsd(x["f"]), "lowering": x["lowering"], "relation": x["relation"]}
                             for s, x in r["variants"].items() if not s.startswith("elec")}
    refined = {k: {"status": s["status"], "lo": s.get("lo"), "hi": s.get("hi"), "from": s.get("refined_from")}
               for k, s in states.items() if k.startswith("ref") and s["status"] != "not needed"}
    out["a4"] = {"per_test": a4, "refined": refined}
    # Part D
    out["part_d"] = pd
    # verdicts and checks
    out["verdicts"] = {k: x["holds"] for k, x in v["verdicts"].items()}
    out["verdict_details"] = v["verdicts"]
    out["checks"] = chk
    more(out, recs, rows, card, rat, ej, v)
    json.dump(out, open(os.path.join(RES, "stage8_paper_numbers.json"), "w"), indent=1, default=float)
    return out


def _lohi(fs):
    if fs["status"] == "zero":
        return 0.0, 0.0
    if fs["status"] == "bracket":
        return fs["lo"], fs["hi"]
    return None


def stage7_peaks():
    """Each test's Stage 7 pertest run at the central contact (f = 0): the hot spot's and the lumped neighbour's peaks
    and their times, as the texts quote them beside the thresholds."""
    out = {}
    for t in R8.tests():
        rid = R8.stage7_zero()[t["test"]]["id"]
        rec = json.load(open(os.path.join(R8.S7RUNS, rid + ".json")))
        out[t["test"]] = {"hot_peak_C": rec["resolved"]["peak_hottest_C"], "t_hot_peak_s": rec["resolved"]["t_peak_hottest_s"],
                          "lumped_peak_C": rec["lumped"]["peak_C"], "t_lumped_peak_s": rec["lumped"]["t_peak_s"],
                          "hot_reached_255_7": bool(rec["resolved"]["propagated"])}
    return out


def more(out, recs, rows, card, rat, ej, v):
    """The derived numbers the texts quote (D87 (1)): ranges, counts and bounds read from the blocks above, the
    defining constants, Stage 7's context and the estimates of predictions_stage8.md as quoted."""
    import math
    import v12_model as V12
    by = {r["test"]: r for r in rows}
    # the defining constants
    out["definitions"] = {
        "levels_C": {"C1": IN.LEVEL_PROP_C, "C2": IN.LEVEL_PROP_C, "C3": IN.LEVEL_150_C},
        "run_end_s": 900.0, "P4_window_s": 60.0, "width": IN.WIDTH, "probes": list(IN.PROBES_A),
        "common_f": list(IN.COMMON_F), "refined_to_fraction_of_bracket": 1.0 / R8.REFINE_FACTOR,
        "tau_d_s": IN.tau_median_s(), "tau_d_conditional_s": list(IN.TAU_D_CONDITIONAL_S),
        "pulse_peak_s": {"21.39": IN.tau_median_s() / 2, "10": 5.0, "60": 30.0},
        "facing_half_deg": 90.0, "capend_from_z_over_L": IN.CAPEND_FROM,
        "lumped_heat_capacity_J_per_K": float(V12.LP.C_CELL),
        "E_stored_J": IN.E_STORED_J, "f_e": list(IN.F_E), "E_joule_J": [f * IN.E_STORED_J for f in IN.F_E],
        "state_of_charge_percent": 100,
        "R_floor_m2K_per_W": IN.R_FLOOR, "acceptance": {"V1_relative": 1e-9, "V3_relative_change": 0.01,
                                                         "V4_energy_residual_relative": 1e-9, "V4_source_relative": 1e-9},
        "prediction_bounds": {"P1_below": 0.3, "P2_below": 0.3, "P2_at_least": 3, "P3_band": [0.05, 0.5], "P3_at_least": 12,
                              "P4_at_least_predicted": 9, "P4_at_least_within": 4, "P4_window_s": 60.0, "P5_at_most": 12,
                              "P7_lowering_below": 0.1},
        "sources": {"levels_C": "src/stage8_inputs.py (D35, D67)", "run_end_s": "D35", "P4_window_s": "predictions_stage8.md, P4",
                    "width": "D78", "lumped_heat_capacity_J_per_K": "src/v12_model.py LP.C_CELL (the two-cell study's)",
                    "E_stored_J": "D68", "state_of_charge_percent": "assumed since Stage 5, as the Databank's nail tests (D53)",
                    "prediction_bounds": "predictions_stage8.md, P1 to P7 as registered"}}
    # inputs
    ee_lo = sorted(x["E_e_low_J"] for x in ej.values())
    ee_hi = sorted(x["E_e_high_J"] for x in ej.values())
    out["inputs"]["E_e_low_J_range"] = [ee_lo[0], ee_lo[-1]]
    out["inputs"]["E_e_high_J_range"] = [ee_hi[0], ee_hi[-1]]
    out["inputs"]["ratio"]["ejecta_percent_range"] = [100.0 - out["inputs"]["ratio"]["body_percent_range"][1],
                                                      100.0 - out["inputs"]["ratio"]["body_percent_range"][0]]
    out["inputs"]["ratio"]["rescale_low"] = rat["central"] / rat["low"]
    out["inputs"]["ratio"]["rescale_high"] = rat["central"] / rat["high"]
    out["inputs"]["ratio"]["databank_rows"] = [d["row"] for d in rat["rows"]]
    # Stage 7's context
    s7 = stage7_peaks()
    n7 = json.load(open(os.path.join(RES, "stage7_paper_numbers.json")))
    out["stage7_context"] = {"f0_peaks": s7, "C1_score_f0": card["stage7_f0"]["C1"]["score"],
                             "trigger_threshold_best_of_16": n7["exploratory_threshold_on_trigger_max"]["both_connections"]["right"],
                             "sources": {"trigger_threshold_best_of_16": "results/stage7_paper_numbers.json, "
                                                                         "exploratory_threshold_on_trigger_max (Stage 7)"}}
    # Part A, derived
    pa = out["part_a"]
    for key in ("fC1", "fC2"):
        bins = {"zero": 0, "(0, 0.0125]": 0, "(0.0125, 0.025]": 0, "(0.025, 0.05]": 0, "above 0.05": 0}
        for r in rows:
            lh = _lohi(r[key])
            if r[key]["status"] == "zero":
                bins["zero"] += 1
            elif lh[1] <= 0.0125 + 1e-12:
                bins["(0, 0.0125]"] += 1
            elif lh[1] <= 0.025 + 1e-12:
                bins["(0.0125, 0.025]"] += 1
            elif lh[1] <= 0.05 + 1e-12:
                bins["(0.025, 0.05]"] += 1
            else:
                bins["above 0.05"] += 1
        pa[key]["bins_by_upper_end"] = bins
        for grp, name in ((True, "propagated"), (False, "not_propagated")):
            g = [_lohi(r[key]) for r in rows if r["propagated"] == grp]
            pa[key][name + "_range"] = [min(x[0] for x in g), max(x[1] for x in g)]
        # the crossing time at the bracket's upper end (the run there meets the criterion)
        side = "resolved" if key == "fC1" else "lumped"
        tt = {}
        for r in rows:
            if r[key]["status"] != "bracket":
                continue
            hi = r[key]["hi"]
            c = [x for x in recs.values() if not x.get("failed") and x["test"] == r["test"] and x["set"] in ("first", "c1", "c2")
                 and abs(x["f"] - hi) < 1e-12 and x.get(side) and x[side].get("t_prop_s") is not None]
            if c:
                tt[r["test"]] = c[0][side]["t_prop_s"]
        pa[key]["t_cross_at_upper_end_s"] = tt
        pa[key]["t_cross_at_upper_end_range_s"] = [min(tt.values()), max(tt.values())] if tt else None
    pa["fC1_delivered_J"] = {r["test"]: [r["fC1"]["lo"] * r["E_e_J"], r["fC1"]["hi"] * r["E_e_J"]]
                             for r in rows if r["fC1"]["status"] == "bracket"}
    pa["fC2_above_fC1"] = sum(1 for r in rows if _lohi(r["fC2"])[0] >= _lohi(r["fC1"])[1] and r["fC2"]["status"] != "zero")
    f3 = {r["test"]: r["fC3_exploratory"] for r in rows}
    pa["fC3_exploratory"] = {"per_test": f3, "n_zero": sum(1 for x in f3.values() if x["status"] == "zero"),
                             "interpolated": {k: x for k, x in f3.items() if x["status"] == "interpolated"}}
    # A4, derived
    a4 = out["a4"]
    c2_shift = []
    c2_shift_median = []
    for t, d in a4["per_test"].items():
        for s, x in d.items():
            if s.endswith("c2") and x["lowering"] is not None and not s.startswith("capend"):
                if s.startswith("ratio"):
                    continue
                m = max(abs(x["lowering"][0]), abs(x["lowering"][1]))
                c2_shift.append(m)
                if t in IN.median_tests():
                    c2_shift_median.append(m)
    a4["duration_c2_largest_shift"] = max(c2_shift)
    a4["duration_c2_largest_shift_median_tests"] = max(c2_shift_median)
    a4["refined_partA_C1_PP_Exp3"] = a4["refined"].get("refA_C1_M50_PP_Exp3")
    # Part B, derived
    pb = out["part_b"]
    lw = {t: d["elec20_c1"]["lowering"] for t, d in pb.items()}
    pb["elec20_largest_lowering_others"] = max(x[1] for t, x in lw.items() if t != "M50_PT_Exp1")
    pb["elec20_all_zero"] = all(d["elec20_c1"]["f"]["status"] == "zero" for d in pb.values() if isinstance(d, dict) and "elec20_c1" in d)
    # Part C, derived
    pc = out["part_c"]
    all_err, all_t, npred = [], [], []
    for f in ("0.1", "0.2", "0.3"):
        for c in IN.CRITERIA:
            d = pc[f][c]
            d["times_range_s"] = [min(d["times_s"]), max(d["times_s"])] if d["times_s"] else None
            d["errors_range_s"] = [min(d["errors_s"]), max(d["errors_s"])] if d["errors_s"] else None
            pt = card["by_fraction"][f][c]["per_test"]
            d["false_alarms"] = sorted(t for t, x in pt.items() if x["class"] == "false alarm")
            d["misses"] = sorted(t for t, x in pt.items() if x["class"] == "miss")
            all_err += d["errors_s"]
            all_t += d["times_s"]
            npred.append(d["predicted"])
    pc["all_common"] = {"errors_range_s": [min(all_err), max(all_err)], "times_max_s": max(all_t),
                        "predicted_range": [min(npred), max(npred)],
                        "scores": sorted({pc[f][c]["score"] for f in ("0.1", "0.2", "0.3") for c in IN.CRITERIA})}
    for c in IN.CRITERIA:
        pt = card["stage7_f0"][c]["per_test"]
        ts = sorted(x["t_s"] for x in pt.values() if x["predicted"])
        er = sorted(x["error_s"] for x in pt.values() if x["class"] == "hit")
        pc["0"][c]["times_range_s"] = [ts[0], ts[-1]] if ts else None
        pc["0"][c]["errors_range_s"] = [er[0], er[-1]] if er else None
    ms = {t["test"]: t for t in R8.tests()}
    tm = sorted(x["time_s"] for x in by.values() if x["propagated"])
    pc["measured"] = {"propagated": sum(1 for x in by.values() if x["propagated"]), "time_range_s": [tm[0], tm[-1]]}
    # P6's ties
    out["verdict_details"]["P6"]["n_ties"] = len(v["verdicts"]["P6"]["ties_within_the_resolution"])
    # Part D, from the records themselves: the peaks' times, the attempts and the factorisations (D83 (6), D87 (4))
    pdx = {}
    for x in IN.median_tests():
        d = {}
        for name, set_, gas in (("layer", "gas", "layer"), ("control", "gasctl", "control")):
            r = recs.get(R8.spec(set_, x, 0.2, models="split", gas=gas)["id"])
            if r is None or r.get("failed"):
                d[name] = None
                continue
            rr = r["resolved"]
            d[name] = {"C1": rr["propagated"], "t_C1_s": rr.get("t_prop_s"), "roll_peak_C": rr["peak_hottest_C"],
                       "t_roll_peak_s": rr["t_peak_hottest_s"], "where_roll_peak": rr.get("where_peak"),
                       "can_peak_C": rr.get("can_peak", {}).get("T_C"), "t_can_peak_s": rr.get("can_peak", {}).get("t_s"),
                       "where_can_peak": rr.get("can_peak", {}).get("where"), "can_at_C1_C": rr.get("can_at_prop_C"),
                       "t_end_s": rr["t_end_s"], "steps": rr["steps"], "factorisations": rr.get("factorisations"),
                       "interface_node_steps": rr.get("interface_node_steps"), "resumed": rr.get("resumed"),
                       "wall_all_attempts_s": rr.get("wall_all_attempts_s"), "energy_residual_rel": rr["energy_residual_rel"],
                       "probe_peak": rr.get("probe_peak"), "n_nodes": r.get("n_nodes"), "geom": rr.get("geom"),
                       "energy_J": rr.get("energy_J"), "stored_J": rr.get("stored_J")}
        pdx[x] = d
    out["part_d_records"] = pdx
    # Part D's ranges over the three tests, as the texts quote them
    lay = [d["layer"] for d in pdx.values() if d.get("layer")]
    ctl = [d["control"] for d in pdx.values() if d.get("control")]
    rng = lambda v: [min(v), max(v)] if v else None
    pa_d = {t: out["part_d"]["per_test"][t]["partA"] for t in pdx if out["part_d"]["per_test"][t].get("partA")}
    out["part_d_summary"] = {
        "n_layer_runs": len(lay), "n_control_runs": len(ctl),
        "layer_C1_any": any(x["C1"] for x in lay) if lay else None,
        "layer_roll_peak_C": rng([x["roll_peak_C"] for x in lay]), "layer_t_roll_peak_s": rng([x["t_roll_peak_s"] for x in lay]),
        "layer_roll_peak_where_z_mm": sorted({round(x["where_roll_peak"]["z_mm"], 3) for x in lay}) if lay else None,
        "layer_can_peak_C": rng([x["can_peak_C"] for x in lay]), "layer_t_can_peak_s": rng([x["t_can_peak_s"] for x in lay]),
        "layer_wall_all_attempts_min": rng([x["wall_all_attempts_s"] / 60.0 for x in lay]),
        "layer_attempts": sorted({x["resumed"] + 1 for x in lay}) if lay else None,
        "layer_factorisations": rng([x["factorisations"] for x in lay]), "layer_steps": rng([x["steps"] for x in lay]),
        "layer_energy_residual_max": max(x["energy_residual_rel"] for x in lay) if lay else None,
        "layer_delivered_J": rng([x["energy_J"]["in_delivery"] for x in lay]),
        "layer_radiated_out_J": rng([x["energy_J"]["out_rad"] for x in lay]),
        "layer_convected_out_J": rng([x["energy_J"]["out_conv"] for x in lay]),
        "layer_stored_J": rng([x["stored_J"] for x in lay]),
        "control_t_C1_s": rng([x["t_C1_s"] for x in ctl]),
        "control_less_partA_s": rng([out["part_d"]["per_test"][t]["split_alone_C1_s"] for t in pdx
                                      if out["part_d"]["per_test"][t].get("split_alone_C1_s") is not None]),
        "partA_t_C1_s": rng([x["t_C1_s"] for x in pa_d.values()]), "partA_t_C2_s": rng([x["t_C2_s"] for x in pa_d.values()]),
        "partA_t_C3_s": rng([x["t_C3_s"] for x in pa_d.values()]),
        "fC1_without_layer": {t: fsd(by[t]["fC1"]) for t in pdx}}
    # V3's runs beside their base run (D83 (3))
    base = recs.get("first_M50_PT_Exp1_f0.100000000")
    v3 = {"base": {"id": base["id"], "n_nodes": base["n_nodes"], "hot_peak_C": base["resolved"]["peak_hottest_C"],
                   "t_hot_peak_s": base["resolved"]["t_peak_hottest_s"], "steps": base["resolved"]["steps"]} if base else None}
    for vset in ("v3mesh", "v3step"):
        r = recs.get(f"{vset}_M50_PT_Exp1_f0.100000000")
        if r is None or r.get("failed") or base is None:
            v3[vset] = None
            continue
        rise_b, rise_v = base["resolved"]["peak_hottest_C"] - 25.0, r["resolved"]["peak_hottest_C"] - 25.0
        v3[vset] = {"n_nodes": r["n_nodes"], "hot_peak_C": r["resolved"]["peak_hottest_C"],
                    "t_hot_peak_s": r["resolved"]["t_peak_hottest_s"], "steps": r["resolved"]["steps"],
                    "relative_change_of_peak_rise": abs(rise_v / rise_b - 1.0), "wall_s": r["wall_s"],
                    "energy_residual_rel": r["resolved"]["energy_residual_rel"]}
    out["v3"] = v3
    # the runs, grouped as the texts count them, and their times on the cloud machine
    bs = out["runs"]["by_set"]
    grp = {"first": ["first"], "searches": ["c1", "c2"],
           "a4": ["dur10_c1", "dur10_c2", "dur60_c1", "dur60_c2", "capend_c1"],
           "refinements": [s for s in bs if s.startswith("ref")], "part_b": ["elec05_c1", "elec20_c1"],
           "part_d": ["gas", "gasctl"], "v3": ["v3mesh", "v3step"]}
    out["runs"]["groups"] = {g: sum(bs.get(s, 0) for s in ss) for g, ss in grp.items()}
    out["runs"]["groups_sum"] = sum(out["runs"]["groups"].values())
    good = [r for r in recs.values() if not r.get("failed")]
    base900 = [r["wall_s"] for r in good if r.get("resolved") and r.get("models") != "split" and r.get("refine", 1.0) == 1.0
               and r.get("dt_scale", 1.0) == 1.0 and r["resolved"]["t_end_s"] >= 900.0 - 1e-6]
    early = [r["wall_s"] for r in good if r.get("resolved") and r.get("models") != "split" and r.get("refine", 1.0) == 1.0
             and r.get("dt_scale", 1.0) == 1.0 and r["resolved"]["t_end_s"] < 900.0 - 1e-6]
    lumped_only = [r["wall_s"] for r in good if r.get("resolved") is None and r.get("lumped")]
    out["runs"]["times_s"] = {
        "base_to_900_s": {"n": len(base900), "median": statistics.median(base900) if base900 else None,
                          "min": min(base900) if base900 else None, "max": max(base900) if base900 else None},
        "base_stopped_early": {"n": len(early), "median": statistics.median(early) if early else None,
                               "max": max(early) if early else None},
        "lumped_only": {"n": len(lumped_only), "max": max(lumped_only) if lumped_only else None},
        "split": {r["id"]: {"wall_all_attempts_s": r["resolved"].get("wall_all_attempts_s"),
                            "resumed": r["resolved"].get("resumed"), "last_attempt_s": r["wall_s"]}
                  for r in good if r.get("models") == "split"},
        "v3": {r["id"]: r["wall_s"] for r in good if r["set"] in ("v3mesh", "v3step")}}
    # the exploratory fit (D87 (3))
    ex_path = os.path.join(RES, "stage8_explore.json")
    if os.path.exists(ex_path):
        ex = json.load(open(ex_path))
        lg = ex["logistic_in_trigger_energy"]
        eb = sorted(r["E_b_J"] for r in rows)
        p = lambda e: 1.0 / (1.0 + math.exp(-(lg["intercept"] + lg["slope_per_kJ"] * e / 1e3)))
        out["exploratory"] = {"C2": ex["C2"], "C1": ex["C1"], "constant_model_loglik": ex["constant_model_loglik"],
                              "constant_probability": ex["propagated"] / ex["n"],
                              "logistic": dict(lg, p_at_smallest_trigger=p(eb[0]), p_at_largest_trigger=p(eb[-1]),
                                               smallest_trigger_J=eb[0], largest_trigger_J=eb[-1])}
    # the predictions' estimates, as quoted beside the results (predictions_stage8.md, commit b8dafb4)
    out["predictions_estimates"] = {
        "what": "quoted from predictions_stage8.md (commit b8dafb4), not computed here",
        "fC1_sizing": {"M50_PT_Exp1": "about 0.16", "M50_ST_Exp3": "near 0.09 or below",
                       "M50_PT_Exp4": "below 0.0125", "M50_PP_Exp2": "below 0.0125"},
        "fC2_balance": {"M50_PT_Exp1": 0.42, "M50_ST_Exp3": 0.19, "M50_PT_Exp3": 0.063, "others": [0.017, 0.038],
                        "M50_ST_Exp1": 0.009, "zero": ["M50_PP_Exp1", "M50_SP_Exp3"]},
        "joule_K_f_e_0.2": 212, "joule_K_f_e_0.05": 53}


if __name__ == "__main__":
    o = main()
    print(json.dumps(o["verdicts"]), o["runs"]["n"], "runs")
