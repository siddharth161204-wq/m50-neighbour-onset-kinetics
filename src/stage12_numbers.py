#!/usr/bin/env python3
"""Every Stage 12 number the texts quote (the note, the README, the release notes, the Zenodo description and the
manuscript), from the scoring's outputs, the checks and the records (results/stage12_scorecard.json,
stage12_checks.json, stage12_capped.csv, stage12_runs/) and the provenance of the predictions' push. Writes
results/stage12_paper_numbers.json, the file from which the texts' Stage 12 lines are written.

Usage: python3 stage12_numbers.py
"""
import csv, glob, hashlib, json, os, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
RES = os.path.join(ROOT, "results")


def rows(path):
    with open(path) as fh:
        return list(csv.DictReader(fh))


def rng(xs, nd=2):
    return [round(min(xs), nd), round(max(xs), nd)]


def main():
    card = json.load(open(os.path.join(RES, "stage12_scorecard.json")))
    checks = json.load(open(os.path.join(RES, "stage12_checks.json")))
    recs = [json.load(open(p)) for p in sorted(glob.glob(os.path.join(RES, "stage12_runs", "s12_*.json")))]
    cap = rows(os.path.join(RES, "stage12_capped.csv"))
    P = card["predictions"]
    pc = card["part_c"]
    B1, B2 = card["part_b"]["B1"], card["part_b"]["B2"]
    db = rows(os.path.join(ROOT, "inputs", "databank", "databank_m50_used.csv"))
    nail = [r for r in db if r["Trigger-Mechanism"] == "Nail"]
    ej = sorted((float(r["Energy-Fraction-Positive-Ejecta-kJ"]) + float(r["Energy-Fraction-Negative-Ejecta-kJ"])) for r in nail)
    prov = json.load(open(os.path.join(ROOT, "provenance", "github_activity_stage12.json")))
    push = [a for a in prov["activity"] if a["after"].startswith("981c1e6")][0]
    pred_hash = hashlib.sha256(open(os.path.join(ROOT, "predictions_stage12.md"), "rb").read()).hexdigest()
    first_run = min(r["started_utc"] for r in recs)
    last_run = max(r["finished_utc"] for r in recs)
    by_pt = {}
    for r in cap:
        by_pt.setdefault((r["connection"], r["contact"]), []).append(r)

    def part_a(h):
        p = P["P1" if h == "central" else "P2"]
        return {"verdict": p["verdict"], "tests_meeting_C1": p["tests_meeting_C1"], "tests_meeting_C2": p["tests_meeting_C2"],
                "hot_spot_peak_C": rng(p["hot_spot_peak_C"]), "lumped_peak_C": rng(p["lumped_peak_C"]),
                "far_face_peak_C": rng(p["far_face_peak_C"]),
                "shortfall_hot_spot_K": rng(p["shortfall_hot_spot_K"], 1),
                "h_c_W_m2K": {k: v["h_c_W_m2K"] for k, v in p["runs"].items()},
                "trigger_peak_C": rng([v["trigger_peak_C"] for v in p["runs"].values()], 1),
                "fitted_C1_at_f0_s": rng([float(r["fitted_C1_at_f0_s"]) for (c, hh), rs in by_pt.items() if hh == h
                                          for r in rs], 1),
                "runs": {k: {"tests": len(v["tests"]), "hot_spot_peak_C": round(v["hot_spot_peak_C"], 2),
                             "lumped_peak_C": round(v["lumped_peak_C"], 2), "far_face_peak_C": round(v["far_face_peak_C"], 2)}
                         for k, v in p["runs"].items()}}

    b1 = {}
    for k, v in B1.items():
        b1[k] = {"status": v["status"], "stage8_f": v["stage8"]["f"], "stage12_f": v["f_r_Eb"],
                 "f_fixed": [round(x, 4) for x in v["f_fixed"]], "E_star_kJ": [round(x / 1e3, 3) for x in v["E_star_J"]],
                 "stage8_E_kJ": [round(x / 1e3, 3) for x in v["stage8"]["E_J"]], "E_e_kJ": round(v["E_e_J"] / 1e3, 1),
                 "runs": len(v["runs"])}
    b2 = {}
    for t, v in B2.items():
        b2[t] = {"status": v["status"], "stage9_status": v["stage9"]["status"], "t_m_s": v["t_m_s"],
                 "f_t_fixed": None if v["f_t_fixed"] is None else round(v["f_t_fixed"], 4),
                 "E_t_J": None if v["E_t_J"] is None else round(v["E_t_J"], 1),
                 "f_fixed_bracket": [round(x, 4) for x in v["f_fixed_bracket"]],
                 "E_bracket_kJ": [round(x / 1e3, 3) for x in v["E_bracket_J"]],
                 "t_run_s": None if v["t_run_s"] is None else round(v["t_run_s"], 1), "stage12_runs": len(v["runs"])}
    pbs = rows(os.path.join(ROOT, "manuscript", "data", "predictions_by_stage.csv"))
    through11 = {"committed": len(pbs), "failed": sum(1 for r in pbs if r["verdict"] == "failed"),
                 "foreseen": sum(1 for r in pbs if r["foreseen"] == "yes")}
    n12_fail = card["failed"]
    out = {
        "what": "Stage 12's quoted numbers (brief of 3 November 2026; predictions_stage12.md; DECISIONS.md D122 to D124)",
        "predictions_file": {"sha256": pred_hash, "commit": push["after"][:7], "pushed_utc": push["timestamp"],
                             "first_run_started_utc": first_run, "last_run_finished_utc": last_run},
        "inputs": {"E_cap_J": card["inputs"]["E_cap_J"], "E_cap_kJ": round(card["inputs"]["E_cap_J"] / 1e3, 1),
                   "cap_row": card["inputs"]["cap_row"][:2], "E_fix_J": round(card["inputs"]["E_fix_J"], 2),
                   "E_fix_kJ": round(card["inputs"]["E_fix_J"] / 1e3, 2), "nail_tests": len(nail),
                   "ejected_kJ_range": [round(ej[0], 2), round(ej[-1], 2)], "ejected_median_kJ": round(statistics.median(ej), 2),
                   "eight_tests": sorted(r["test"] for r in cap if r["contact"] == "central"),
                   "eight_tests_E_b_kJ": rng([float(r["E_b_fitted_J"]) / 1e3 for r in cap if r["contact"] == "central"], 1),
                   "E_b_over_cap": rng([float(r["E_b_fitted_J"]) / card["inputs"]["E_cap_J"] for r in cap
                                        if r["contact"] == "central"], 2),
                   "series_parallel": [sum(1 for r in cap if r["contact"] == "central" and r["connection"] == c)
                                       for c in ("series", "parallel")]},
        "runs": {"n": len(recs), "part_a": sum(1 for r in recs if r["kind"] == "A"),
                 "part_b": sum(1 for r in recs if r["kind"] in ("B1", "B2")),
                 "wall_s_part_a": rng([r["wall_s"] for r in recs if r["kind"] == "A"], 0)},
        "part_a": {"central": part_a("central"), "high": part_a("high")},
        "B1": b1, "B2": b2,
        "P3": {"verdict": P["P3"]["verdict"], "ratio": round(P["P3"]["ratio"], 1), "n": P["P3"]["n"],
               "smallest": [P["P3"]["smallest"][0], round(P["P3"]["smallest"][1], 1)],
               "largest": [P["P3"]["largest"][0], round(P["P3"]["largest"][1], 1)],
               "not_counted": P["P3"]["not_counted"]},
        "P4": {"verdict": P["P4"]["verdict"],
               "largest_f_max": [P["P4"]["largest_registered_f_max"]["test"],
                                 round(P["P4"]["largest_registered_f_max"]["f_fixed"], 4),
                                 round(P["P4"]["largest_registered_f_max"]["E_J"], 1)],
               "smallest_f_t": [P["P4"]["smallest_f_t"]["test"], round(P["P4"]["smallest_f_t"]["f_fixed"], 4),
                                round(P["P4"]["smallest_f_t"]["E_J"], 1)],
               "ratio": round(P["P4"]["ratio"], 1)},
        "part_c": {"ratio": round(pc["ratio_largest_to_smallest_nonzero"], 1),
                   "smallest": [pc["smallest"]["test"], round(pc["smallest"]["E_J"], 1), round(pc["smallest"]["f_fixed"], 4),
                                pc["smallest"]["category"]],
                   "largest": [pc["largest"]["test"], round(pc["largest"]["E_J"], 1), round(pc["largest"]["f_fixed"], 4),
                               pc["largest"]["category"]],
                   "n_with_fraction": pc["n_with_fraction"], "zero_tests": pc["zero_tests"],
                   "zero_share_of_16": pc["zero_share_of_16"], "no_fraction": pc["no_fraction"],
                   "cell_movement_tests": pc["cell_movement_tests"],
                   "threshold_brackets_kJ": {t: [round(x / 1e3, 2) for x in b] for t, b in pc["threshold_brackets_J"].items()},
                   "ratio_if_thresholds_counted": [round(x, 1) for x in pc["ratio_if_thresholds_counted_at_bracket_ends"]],
                   "stage10_energy_ratio_range": [round(x, 1) for x in pc["stage10_energy_ratio_range"]],
                   "stage10_fraction_ratio_range": [round(x, 1) for x in pc["stage10_fraction_ratio_range"]],
                   "stage10_tri21": {"fraction_ratio": round(pc["stage10"]["tri21"]["fraction_ratio"], 1),
                                     "energy_ratio": round(pc["stage10"]["tri21"]["energy_ratio"], 1),
                                     "fstar_ratio": round(pc["stage10"]["tri21"]["fstar_ratio"], 1)},
                   "stage10_fstar_ratio_range": rng([v["fstar_ratio"] for v in pc["stage10"].values()], 1),
                   "fstar_C2_fixed_ratio_of_midpoints": round(pc["fstar_C2_fixed_ratio_of_midpoints"], 1),
                   "fstar_C2_fixed_ends": pc["fstar_C2_fixed_ends"],
                   "fstar_C2_fixed_zero_tests": pc["fstar_C2_fixed_zero_tests"],
                   "fstar_C2_fixed_end_brackets": {t: [round(x, 4) for x in pc["fstar_C2_fixed"][t]["f_fixed"]]
                                                   for t in pc["fstar_C2_fixed_ends"]},
                   "fstar_C2_fixed_by_group": {g: [round(x, 4) for x in v] for g, v in pc["fstar_C2_fixed_by_group"].items()},
                   "fstar_C1_fixed_by_group": {g: [round(x, 4) for x in v] for g, v in pc["fstar_C1_fixed_by_group"].items()},
                   "fstar_C1_fixed_zero_tests": pc["fstar_C1_fixed_zero_tests"]},
        "verdicts": card["verdicts"],
        "counts": {"stage12": {"committed": card["n_predictions"], "failed": n12_fail, "held": card["n_predictions"] - n12_fail},
                   "through_stage11": through11,
                   "all": {"committed": through11["committed"] + card["n_predictions"],
                           "failed": through11["failed"] + n12_fail,
                           "held": through11["committed"] + card["n_predictions"] - through11["failed"] - n12_fail,
                           "foreseen": through11["foreseen"] + card["failed_foreseen"]}},
        "checks": {k: v["ok"] for k, v in checks.items() if isinstance(v, dict)},
        "check_details": {"X_worst_K": checks["X"]["worst_K"], "V2_worst": checks["V2"]["worst_relative"],
                          "V2_counts": checks["V2"]["counts"]}}
    json.dump(out, open(os.path.join(RES, "stage12_paper_numbers.json"), "w"), indent=1, default=float)
    print(json.dumps({k: out[k] for k in ("verdicts", "counts", "checks", "predictions_file")}, indent=1))


if __name__ == "__main__":
    main()
