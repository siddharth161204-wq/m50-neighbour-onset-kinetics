#!/usr/bin/env python3
"""Every number quoted in the note and the README, computed from the result files (results/note_numbers.json).

Usage: python3 note_numbers.py --out ../results
"""
import argparse, json, os

ap = argparse.ArgumentParser(); ap.add_argument("--out", default="../results"); a = ap.parse_args()
J = lambda f: json.load(open(os.path.join(a.out, f)))
on = {r["case"]: r for r in J("onset_results.json")["cases"]}
s1 = J("stage1_scorecard.json")
v1 = J("v1_arc_check.json")
v0 = J("v0_dsc_check.json")
v2s, v2a = J("v2_synthetic.json"), J("v2_archived.json")
n = {}
hl = {t: on[f"two_E33223_tau{t}_G0.5"] for t in (10, 30)}
n["headline_0.15"] = {f"tau{t}": {"hottest_s": r["hottest_node_t_0.15Kpm_s"], "lumped_s": r["lumped_t_0.15Kpm_s"],
                                  "mean_s": r["resolved_mean_t_0.15Kpm_s"],
                                  "lead_s": r["lumped_t_0.15Kpm_s"] - r["hottest_node_t_0.15Kpm_s"],
                                  "earlier_percent": 100 * (1 - r["hottest_node_t_0.15Kpm_s"] / r["lumped_t_0.15Kpm_s"])}
                      for t, r in hl.items()}
n["onset_temperature_0.15_C_range"] = s1["summary"]["temperature_at_0.15Kpm_C_range"]
n["only_local_smallest_mWK"] = s1["P3"]["smallest_G_mWK"]
n["only_local_cases"] = s1["P3"]["only_hottest_cases"]
n["levels_reached_two_strip"] = s1["summary"]["levels_reached_two_strip"]
n["V0"] = {"cathode_peak": v0["cathode"]["sum"], "cathode_third": v0["cathode"]["third_peak"],
           "separator": v0["separator"]["reading_i_minus_dH_times_rate"], "ln_k": {k: v["ln_k"] for k, v in v0["cathode_ln_k_check"].items()}}
n["V1"] = {"T_in_C": v1["arc_base"]["T_in_C"], "T_at_1_C_per_s_C": v1["arc_base"]["T_at_1_C_per_s_C"],
           "T_on_1_C_per_min_C": v1["arc_base"]["T_on_C"], "t_in_h": v1["arc_base"]["t_in_h"],
           "sensitivity_T_in_C": sorted(r["T_in_C"] for r in v1["arc_sensitivity"]),
           "an_ele_anode_only_T_in_C": v1["arc_an_ele_mass_anode_only"]["T_in_C"],
           "fresh_onset_0.15_m50_C": v1["fresh_onset_temperature_C"]["m50_cp950"]["0.15"]}
n["V2"] = {"synthetic_max_rel": v2s["summary"]["max_relative_change_halved"], "archived_max_rel": v2a["max_relative_change"]}
st2 = os.path.join(a.out, "stage2_scorecard.json")
if os.path.exists(st2):
    n["stage2_scorecard"] = J("stage2_scorecard.json")
    import csv
    rows = list(csv.DictReader(open(os.path.join(a.out, "stage2_table.csv"))))
    n["stage2_table"] = rows
    hl2 = {r["case"]: r for r in rows}
    out = {}
    for t in (10, 30):
        r = hl2.get(f"two_E33223_tau{t}_G0.5")
        if r:
            entry, cons = float(r["hottest_enters_255.7C_s"]), float(r["layered_cathode_consumed_at_a_node_s"])
            out[f"tau{t}"] = {"hottest_entry_s": entry, "cathode_consumed_after_entry_s": cons - entry,
                              "lumped_peak_C": float(r["lumped_peak_reactive_C"]),
                              "heat_ratio_lumped_over_resolved": float(r["lumped_reaction_heat_J"]) / float(r["resolved_reaction_heat_J"]),
                              "lumped_cathode_conversion": float(r["lumped_layered_cathode_conversion_900s"]),
                              "resolved_cathode_conversion": float(r["resolved_layered_cathode_conversion_volume_mean_900s"]),
                              "max_volume_percent_above_255.7": float(r["max_volume_fraction_above_255.7C_percent"]),
                              "mean_peak_reactive_C": float(r["mean_peak_reactive_C"]), "hottest_peak_reactive_C": float(r["hottest_peak_reactive_C"]),
                              "hottest_peak_passive_C": float(r["hottest_peak_passive_C"])}
    n["stage2_headline"] = out
if os.path.exists(os.path.join(a.out, "stage2_checks.json")):
    c = J("stage2_checks.json")
    n["stage2_checks"] = {"energy_residual_max_abs": c["energy_account"]["max_abs"],
                          "no_source_resolved_vs_archived_max_abs_K": c.get("no_source", {}).get("resolved_vs_archived_max_abs_K"),
                          "no_source_lumped_vs_archived_max_abs_K": c.get("no_source", {}).get("lumped_vs_archived_max_abs_K"),
                          "step_halved_max_relative_move": c.get("step_halved", {}).get("max_relative_move"),
                          "step_halved_band_entry_s": [c["step_halved"]["band_entry_s_base"]["T_onset_low"],
                                                       c["step_halved"]["band_entry_s_halved"]["T_onset_low"]] if "step_halved" in c else None,
                          "V3_high_k": {k: {"mean_K": v["max_abs_Tmean_minus_lumped_K"], "hottest_K": v["max_abs_Tmax_minus_lumped_K"],
                                            "peaks_C": [v["resolved_peak_C"], v["lumped_peak_C"]], "residual": v["energy_residual_rel"],
                                            "pass": v["pass_1K"]} for k, v in c.get("V3_high_k", {}).items()}}
n["stage1_scorecard"] = s1
if "stage2_table" in n:
    n["stage2_heat_ratio_lumped_over_resolved"] = {r["case"]: float(r["lumped_reaction_heat_J"]) / float(r["resolved_reaction_heat_J"])
                                                   for r in n["stage2_table"]}
# Further Stage 1 numbers quoted in the README and the note
r10, r30 = on["two_E33223_tau10_G0.5"], on["two_E33223_tau30_G0.5"]
two = [r for k, r in on.items() if k.startswith("two_")]
n["stage1_extra"] = {
    "lumped_peak_Kpm_33kJ_500mWK": [r10["lumped_peak_Kpm"], r30["lumped_peak_Kpm"]],
    "mean_Tpeak_C_33kJ_50mWK": [on["two_E33223_tau10_G0.05"]["resolved_mean_Tpeak_C"], on["two_E33223_tau30_G0.05"]["resolved_mean_Tpeak_C"]],
    "lumped_Tpeak_C_33kJ_500mWK": [r10["lumped_Tpeak_C"], r30["lumped_Tpeak_C"]],
    "mean_Tpeak_C_33kJ_500mWK": [r10["resolved_mean_Tpeak_C"], r30["resolved_mean_Tpeak_C"]],
    "lumped_minus_mean_peak_K_33kJ_500mWK": [r10["lumped_Tpeak_C"] - r10["resolved_mean_Tpeak_C"],
                                             r30["lumped_Tpeak_C"] - r30["resolved_mean_Tpeak_C"]],
    # 1 K/min of kinetic self-heating is the source paper's ISC trigger (its Table 1 and Section 3.2.2)
    "t_1Kpm_s_33kJ_500mWK": {"hottest_node": [r10["hottest_node_t_1.0Kpm_s"], r30["hottest_node_t_1.0Kpm_s"]],
                             "lumped": [r10["lumped_t_1.0Kpm_s"], r30["lumped_t_1.0Kpm_s"]]},
    "T_at_1Kpm_C_lumped_33kJ_500mWK": [r10["lumped_T_at_1.0Kpm_C"], r30["lumped_T_at_1.0Kpm_C"]],
    "lead_at_1Kpm_s_33kJ_500mWK": [r10["lumped_t_1.0Kpm_s"] - r10["hottest_node_t_1.0Kpm_s"],
                                   r30["lumped_t_1.0Kpm_s"] - r30["hottest_node_t_1.0Kpm_s"]],
    "two_strip_cases_only_hottest_reaches_1Kpm": sorted(r["case"] for r in two if r["hottest_node_t_1.0Kpm_s"] is not None
                                                        and r["lumped_t_1.0Kpm_s"] is None),
    "two_strip_cases_reaching_1Kpm": {h: sum(r[f"{h}_t_1.0Kpm_s"] is not None for r in two)
                                      for h in ("hottest_node", "resolved_mean", "lumped")},
    "median_500mWK_30s_lead_0.15_s": on["two_E21495_tau30_G0.5"]["lumped_t_0.15Kpm_s"] - on["two_E21495_tau30_G0.5"]["hottest_node_t_0.15Kpm_s"]}
fa = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "inputs", "kinetics", "figA1a_mass_basis.json")))
n["figA1a"] = {"sei_implied_mass_g": fa["sei_implied_mass_g"]["median"], "an_ele_implied_mass_g_corrected": fa["an_ele_implied_mass_g_corrected"]}
n["V1"]["fresh_onset_0.15_paper_cell_C"] = v1["fresh_onset_temperature_C"]["paper_cell"]["0.15"]
n["V1"]["paper_T_on_band_C"] = [255.7, 302.1]
n["V1"]["T_on_at_stated_trigger_in_band"] = 255.7 <= v1["arc_base"]["T_on_C"] <= 302.1
if os.path.exists(os.path.join(a.out, "stage2_scorecard.json")):
    n["stage2_passive_entry_s"] = J("stage2_scorecard.json")["P5a"].get("hottest_entry_without_reaction_heat_s")
if os.path.exists(os.path.join(a.out, "explore_sei_storage.json")):
    ss = J("explore_sei_storage.json")["storage"]
    n["sei_storage_exploratory"] = {
        k: {"sei_converted": v["sei_converted"], "ramp_1Kps_T_at_0.15Kpm_C": v["ramp_1Kps_T_at_0.15Kpm_C"],
            "headline": {c: {h: [v["cases"][c][f"{h}_t_0.15Kpm_s"], v["cases"][c][f"{h}_T_at_0.15Kpm_C"], v["cases"][c][f"{h}_rxn_at_0.15Kpm"]]
                             for h in ("hottest_node", "lumped", "resolved_mean")} for c in v["cases"]},
            "lead_s": {c: (v["cases"][c]["lumped_t_0.15Kpm_s"] - v["cases"][c]["hottest_node_t_0.15Kpm_s"])
                       if v["cases"][c]["lumped_t_0.15Kpm_s"] is not None and v["cases"][c]["hottest_node_t_0.15Kpm_s"] is not None else None
                       for c in v["cases"]}}
        for k, v in ss.items()}
if os.path.exists(os.path.join(a.out, "rerun_final_code.json")):
    n["rerun_final_code_max_relative"] = {k: v["max_relative_difference"] for k, v in J("rerun_final_code.json")["files"].items()}
json.dump(n, open(os.path.join(a.out, "note_numbers.json"), "w"), indent=1, default=float)
print(json.dumps({k: v for k, v in n.items() if k != "stage2_table"}, indent=1, default=float))
