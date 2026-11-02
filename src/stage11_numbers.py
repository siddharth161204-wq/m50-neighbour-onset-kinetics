#!/usr/bin/env python3
"""Every Stage 11 number the texts quote (the note, the README, the release notes, the Zenodo description and the
manuscript), computed from the scoring's outputs and the records (results/stage11_*.csv, stage11_bands.json,
stage11_scorecard.json, stage11_checks.json, stage11_runs/). Writes results/stage11_paper_numbers.json, the file from
which the texts' Stage 11 lines are written.

Usage: python3 stage11_numbers.py
"""
import csv, glob, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage11_inputs as IN              # noqa: E402

RES = os.path.join(HERE, "..", "results")


def rows(name):
    with open(os.path.join(RES, name)) as fh:
        return list(csv.DictReader(fh))


def num(s):
    return None if s in ("", None, "None") else float(s)


def main():
    th = rows("stage11_thresholds.csv")
    ov = rows("stage11_overshoot.csv")
    tr = rows("stage11_times.csv")
    dr = rows("stage11_draws.csv")
    B = json.load(open(os.path.join(RES, "stage11_bands.json")))
    S = json.load(open(os.path.join(RES, "stage11_scorecard.json")))
    C = json.load(open(os.path.join(RES, "stage11_checks.json")))
    recs = [json.load(open(p)) for p in glob.glob(os.path.join(RES, "stage11_runs", "s11_*.json"))]
    kin = [f"d{IN.KIN_DRAWS[r]}" for r in IN.KIN_RANKS]
    therm = list(IN.THERMAL_DRAWS)
    out = {"what": "Stage 11's quoted numbers (brief of 2 November; predictions_stage11.md; DECISIONS.md D111 to D118)"}

    out["draws"] = {r["label"]: {k: (num(v) if k not in ("kind", "label") else v) for k, v in r.items() if v != ""}
                    for r in dr}
    walls = [r["wall_s"] for r in recs if not r.get("failed")]
    out["runs"] = {"records": len(recs), "failed": sum(1 for r in recs if r.get("failed")),
                   "resolved": sum(1 for r in recs if r.get("resolved")), "lumped": sum(1 for r in recs if r.get("lumped")),
                   "wall_s_range": [min(walls), max(walls)],
                   "to_900_s_with_stop_lifted": sum(1 for r in recs if "_ns_" in r["id"]),
                   "workers": json.load(open(os.path.join(RES, "stage11_laptop_workers.json")))["workers"]}

    # A and B: the thresholds, per test and criterion, under each draw
    tb = {}
    for r in th:
        tb.setdefault((r["criterion"], r["test"]), {})[r["draw"]] = {
            "status": r["status"], "lo": num(r["lo"]), "hi": num(r["hi"]), "f_star": num(r["f_star"]),
            "E_star_J": num(r["E_star_J"])}
    thr = {}
    for (crit, test), by in tb.items():
        m = by["mean"]
        e = {"mean": m}
        for kind, labs in (("kinetic", kin), ("thermal", therm)):
            e[kind] = {d: by[d] for d in labs}
            same = lambda x: ("zero",) if x["status"] == "zero" else (x["status"], x["lo"], x["hi"])
            e[kind + "_changed_from_mean"] = [d for d in labs if same(by[d]) != same(m)]
            vals = [by[d]["f_star"] for d in labs]
            e[kind + "_range"] = [min(vals), max(vals)]
        allv = [by[d]["f_star"] for d in kin + therm + ["mean"]]
        e["range_all_nine"] = [min(allv), max(allv)]
        ev = [by[d]["E_star_J"] for d in kin + therm + ["mean"]]
        e["E_star_range_all_nine_J"] = [min(ev), max(ev)]
        thr[f"{crit}_{test}"] = e
    out["thresholds"] = thr
    out["C1_unchanged_under_every_kinetic_draw"] = all(not thr[f"C1_{t}"]["kinetic_changed_from_mean"]
                                                       for t in IN.A_TESTS)

    # C1: the far face at f = 0
    oc = {}
    for t in IN.C_TESTS:
        rs = {(r["thermal"], r["contact"]): r for r in ov if r["test"] == t}
        dv = {lab: num(rs[(lab, "central")]["overshoot_K"]) for lab in therm}
        oc[t] = {"M_C": num(rs[("central", "central")]["M_C"]),
                 "central_K": num(rs[("central", "central")]["overshoot_K"]),
                 "thermal_K": dv, "thermal_range_K": [min(dv.values()), max(dv.values())],
                 "low_K": num(rs[("central", "low")]["overshoot_K"]), "high_K": num(rs[("central", "high")]["overshoot_K"]),
                 "peaks_C": {f"{k[0]}_{k[1]}": num(v["peak_f0_C"]) for k, v in rs.items()},
                 "thermal_draws_exceeding": sum(1 for v in dv.values() if v > 0),
                 "low_exceeds": rs[("central", "low")]["exceeds"] == "True",
                 "high_exceeds": rs[("central", "high")]["exceeds"] == "True",
                 "f_max_zero_low": rs[("central", "low")]["f_max_zero"] == "True"}
    four = [t for t in IN.C_TESTS if t != IN.FMAX_TEST]
    out["far_face"] = {"per_test": oc,
                       "four_low_maxima_thermal_range_K": [min(oc[t]["thermal_range_K"][0] for t in four),
                                                           max(oc[t]["thermal_range_K"][1] for t in four)],
                       "four_low_maxima_high_range_K": [min(oc[t]["high_K"] for t in four), max(oc[t]["high_K"] for t in four)],
                       "four_low_maxima_low_K": {t: oc[t]["low_K"] for t in four},
                       "pt_exp1_range_K": [min([oc[IN.FMAX_TEST]["central_K"], oc[IN.FMAX_TEST]["low_K"],
                                                oc[IN.FMAX_TEST]["high_K"]] + list(oc[IN.FMAX_TEST]["thermal_K"].values())),
                                           max([oc[IN.FMAX_TEST]["central_K"], oc[IN.FMAX_TEST]["low_K"],
                                                oc[IN.FMAX_TEST]["high_K"]] + list(oc[IN.FMAX_TEST]["thermal_K"].values()))]}
    out["f_max_pt_exp1"] = {k: {"f_max": v["f_max"], "status": v["status"], "lo": v["lo"], "hi": v["hi"],
                                "peak_C_at_f_max": v["p_run"]} for k, v in B["C2_fmax"].items()}

    # D: the clock under the kinetic draws
    six = S["predictions"]["P6"]["six"]
    per = {}
    for t in sorted({r["test"] for r in tr}):
        rs = {r["draw"]: r for r in tr if r["test"] == t}
        per[t] = {"f": num(rs[kin[0]]["f"]), "t_measured_s": num(rs[kin[0]]["t_measured_s"]),
                  "t_mean_s": num(rs[kin[0]]["t_mean_s"]),
                  "t_draw_s": {d: num(rs[d]["t_draw_s"]) for d in kin},
                  "shift_from_mean_s": {d: num(rs[d]["shift_from_mean_s"]) for d in kin},
                  "no_crossing": [d for d in kin if rs[d]["crossed"] == "False"]}
    moving = [t for t in six if per[t]["no_crossing"] or any(abs(x) > 60 for x in per[t]["shift_from_mean_s"].values()
                                                            if x is not None)]
    stable = [t for t in six if t not in moving]
    shifts = [abs(x) for t in stable for x in per[t]["shift_from_mean_s"].values() if x is not None]
    out["clock"] = {"per_test": per, "six": six, "moving_tests": moving, "stable_tests": stable,
                    "stable_abs_shift_range_s": [min(shifts), max(shifts)],
                    "counts": B["D2_counts"],
                    "within_10_s_range_over_draws": [min(B["D2_counts"][d]["within_10_s"] for d in kin),
                                                     max(B["D2_counts"][d]["within_10_s"] for d in kin)],
                    "within_60_s_range_over_draws": [min(B["D2_counts"][d]["within_60_s"] for d in kin),
                                                     max(B["D2_counts"][d]["within_60_s"] for d in kin)],
                    "no_crossing_tests": sorted({t for t in per if per[t]["no_crossing"]}),
                    "no_crossing_draws": sorted({d for t in per for d in per[t]["no_crossing"]})}

    # E
    e1 = B["E1"]["C2"]
    rng = {k: v for k, v in e1["range_across_tests_J"].items()}
    out["E1"] = {"C2": {"range_across_tests_J": rng, "range_min_J": min(rng.values()), "range_max_J": max(rng.values()),
                        "largest_within_test_band_J": e1["largest_within_test_band_J"],
                        "largest_band_test": e1["largest_band_test"],
                        "within_test_band_J": e1["within_test_band_J"],
                        "ratio_min": min(v for v in e1["ratio_range_to_band"].values() if v is not None)},
                 "C1": {k: v for k, v in B["E1"]["C1"].items() if k in ("range_across_tests_J", "largest_within_test_band_J",
                                                                         "largest_band_test", "within_test_band_J")}}
    e2 = B["E2"]["C2"]
    out["E2"] = {"C2": {"largest_factor": e2["largest_factor"], "largest_factor_test": e2["largest_factor_test"],
                        "per_test_factor": {t: v["factor"] for t, v in e2["per_test"].items()},
                        "stage10_spread": e2["stage10_spread"], "share_of_log_spread": e2["share_of_log_spread"],
                        "share_range": [min(v for v in e2["share_of_log_spread"].values() if v is not None),
                                        max(v for v in e2["share_of_log_spread"].values() if v is not None)]},
                 "C1": {"largest_factor": B["E2"]["C1"]["largest_factor"],
                        "largest_factor_test": B["E2"]["C1"]["largest_factor_test"]}}
    out["E3"] = {k: {"verdict": v["verdict"], "per_test": v["per_test"]} for k, v in B["E3"].items()}
    out["E4"] = B["E4"]
    out["verdicts"] = S["verdicts"]
    P = S["predictions"]
    out["P_details"] = {
        "P1_failing": {t: [d for d, x in v.items() if d != "mean" and not x["within"]] for t, v in P["P1"]["detail"].items()},
        "P3": {"range_min_J": min(P["P3"]["range_across_tests_J"].values()),
               "largest_within_test_band_J": P["P3"]["largest_within_test_band_J"]},
        "P4": P["P4"]["detail"], "P5": P["P5"]["detail"], "P6_tests_moving": P["P6"]["tests_moving"]}
    out["checks"] = {"V1": C["V1"]["pass"], "V2": {"pass": C["V2"]["pass"], "largest": C["V2"]["largest"],
                                                   "counts": C["V2"]["counts"]},
                     "V3": {"pass": C["V3"]["pass"], "largest_relative_difference": C["V3"]["largest_relative_difference"]},
                     "V4": {"pass": C["V4"]["pass"],
                            "largest_K": max(abs(x) for r in C["V4"]["runs"].values() for side in ("resolved", "lumped")
                                             if side in r for k, x in r[side].items() if k.endswith("_K")),
                            "largest_s": max(abs(x) for r in C["V4"]["runs"].values() for side in ("resolved", "lumped")
                                             if side in r for k, x in r[side].items() if k.endswith("_s"))}}
    json.dump(out, open(os.path.join(RES, "stage11_paper_numbers.json"), "w"), indent=1, default=float)
    print(json.dumps({k: out[k] for k in ("verdicts", "runs")}, default=float))
    print("C1 unchanged under kinetic draws:", out["C1_unchanged_under_every_kinetic_draw"])
    print("far face:", json.dumps({k: v for k, v in out["far_face"].items() if k != "per_test"}))
    print("clock:", json.dumps({k: v for k, v in out["clock"].items() if k not in ("per_test", "counts")}))
    print("E1:", out["E1"]["C2"]["range_min_J"], out["E1"]["C2"]["range_max_J"], out["E1"]["C2"]["largest_within_test_band_J"],
          out["E1"]["C2"]["ratio_min"])
    print("E2:", json.dumps(out["E2"]["C2"]["share_range"]), out["E2"]["C2"]["largest_factor"])


if __name__ == "__main__":
    main()
