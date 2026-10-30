#!/usr/bin/env python3
"""Every Stage 10 number quoted in the README, the note, the release notes and the Zenodo description
(results/stage10_paper_numbers.json; DECISIONS.md D107), computed from the Stage 10 records and the files the
scoring, Part C, the survey and the checks wrote: the file from which a manuscript of Stages 1 to 10 is to be written.
Usage: python3 stage10_numbers.py
"""
import csv, glob, json, os, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage10_inputs as IN              # noqa: E402

RES = os.path.join(HERE, "..", "results")
J = lambda name: json.load(open(os.path.join(RES, name)))
READ_KEYS = ("rms_K", "mean_K", "max_abs_K", "diff_at_end_K", "model_at_end_C", "measured_at_end_C",
             "rise_last_model_K", "rise_last_measured_K", "pass_100_model_s", "pass_150_model_s")


def span(vals):
    vals = [v for v in vals if v is not None]
    return [min(vals), max(vals)] if vals else None


def measured():
    t, T, Tg = IN.history("a")
    at = lambda s: T[min(range(len(t)), key=lambda i: abs(t[i] - s))]
    ex = json.load(open(IN.EXTRACTION))["panels"]["a"]
    tb, Tb, _ = IN.history("b")
    pk = max(range(len(tb)), key=lambda i: Tb[i])
    return {"uncertainty_K": ex["uncertainty_K"], "uncertainty_s": ex["uncertainty_s"],
            "onset_figure_s": IN.T_PROP_S, "onset_table3_s": IN.T_TABLE_S, "section_I_end_s": IN.T_SECTION_I_END_S,
            "at_onset_C": at(IN.T_PROP_S), "at_onset_less_60_s_C": at(IN.T_PROP_S - IN.LAST_S),
            "rise_last_60_s_K": at(IN.T_PROP_S) - at(IN.T_PROP_S - IN.LAST_S),
            "at_45_s_C": at(45.0), "at_100_s_C": at(100.0), "at_268_s_C": at(268.0), "at_273_s_C": at(273.0),
            "rise_268_to_onset_K": at(IN.T_PROP_S) - at(268.0),
            "PP_Exp3": {"peak_C": Tb[pk], "peak_t_s": tb[pk], "section_II_end_s": IN.T_SECTION_II_END_B_S}}


def part_a(h):
    A = h["part_a"]
    out = {}
    for k, v in A.items():
        out[k] = {"reading": v["reading"], "contact": v["contact"], "f": v["f"], "cfg": v["cfg"],
                  "registered": v["registered"],
                  "nodes": {n: {"window": {kk: v["nodes"][n]["window"][kk] for kk in READ_KEYS},
                                "after_section_I": {kk: v["nodes"][n]["after_section_I"][kk]
                                                    for kk in ("rms_K", "mean_K", "max_abs_K")},
                                "pass_150_measured_s": v["nodes"][n]["window"]["pass_150_measured_s"],
                                "pass_100_measured_s": v["nodes"][n]["window"]["pass_100_measured_s"]}
                            for n in v["nodes"]}}
    c = lambda key: A[key]["nodes"]["away"]["window"]
    short = [c("tri21_C2_lo_hcentral"), c("tri21_C2_hi_hcentral")]
    longs = [c(f"{k}_hcentral") for k in IN.LONG]
    summary = {
        "registered_node_contact": "away, central",
        "short_rms_K": [s["rms_K"] for s in short], "long_rms_K": {k: c(f"{k}_hcentral")["rms_K"] for k in IN.LONG},
        "none_rms_K": c("none_hcentral")["rms_K"],
        "short_after_section_I_rms_K": [A[k]["nodes"]["away"]["after_section_I"]["rms_K"]
                                        for k in ("tri21_C2_lo_hcentral", "tri21_C2_hi_hcentral")],
        "long_after_section_I_rms_K": span([A[f"{k}_hcentral"]["nodes"]["away"]["after_section_I"]["rms_K"]
                                            for k in IN.LONG]),
        "short_diff_at_onset_K": [s["diff_at_end_K"] for s in short],
        "long_diff_at_onset_K": {k: c(f"{k}_hcentral")["diff_at_end_K"] for k in IN.LONG},
        "none_diff_at_onset_K": c("none_hcentral")["diff_at_end_K"],
        "short_rise_K": [s["rise_last_model_K"] for s in short],
        "long_rise_K": {k: c(f"{k}_hcentral")["rise_last_model_K"] for k in IN.LONG},
        "none_rise_K": c("none_hcentral")["rise_last_model_K"],
        "short_pass_150_s": [s["pass_150_model_s"] for s in short],
        "long_pass_150_s": {k: c(f"{k}_hcentral")["pass_150_model_s"] for k in IN.LONG},
        "none_pass_150_s": c("none_hcentral")["pass_150_model_s"],
        "short_pass_100_s": [s["pass_100_model_s"] for s in short],
        "measured_pass_100_s": A["tri21_C2_lo_hcentral"]["nodes"]["away"]["window"]["pass_100_measured_s"],
        "measured_pass_150_s": A["tri21_C2_lo_hcentral"]["nodes"]["away"]["window"]["pass_150_measured_s"],
        "short_by_contact_rms_K": {h_: [A[f"tri21_C2_{e}_h{h_}"]["nodes"]["away"]["window"]["rms_K"] for e in ("lo", "hi")]
                                   for h_ in IN.CONTACTS},
        "short_by_node_rms_K": {n: [A[f"tri21_C2_{e}_hcentral"]["nodes"][n]["window"]["rms_K"] for e in ("lo", "hi")]
                                for n in ("away", "side", "facing")},
        "long_by_node_rms_K": {n: span([A[f"{k}_hcentral"]["nodes"][n]["window"]["rms_K"] for k in IN.LONG])
                               for n in ("away", "side", "facing")},
        "best_rms_by_node": {n: min(((k, v["nodes"][n]["window"]["rms_K"]) for k, v in A.items()
                                     if v["contact"] == "central"), key=lambda kv: kv[1])
                             for n in ("away", "side", "facing")},
    }
    return out, summary


def segments(h):
    """Exploratory, not registered (D108): the away node's root mean square, largest difference and mean difference
    over parts of the window, the same trapezoid average as D103 (2), from the records' probe series."""
    import numpy as np
    A = h["part_a"]
    tm, Tm, _ = IN.history("a")
    tm, Tm = np.array(tm), np.array(Tm)
    parts = {"24.16-100": (24.16, 100.0), "100-271.5": (100.0, 271.5), "211.5-271.5": (211.5, 271.5)}
    out = {}
    for key in ("none_hcentral", "tri21_C2_lo_hcentral", "tri21_C2_hi_hcentral", "con240_C2_hcentral",
                "con360_C2_hcentral", "con360_C1_hcentral"):
        z = np.load(os.path.join(RES, "stage10_series", A[key]["id"] + ".npz"))
        Tmod = np.interp(tm, z["probe_t"], z["probe_away"] - 273.15)          # the series are in K
        out[key] = {}
        for name, (a, b) in parts.items():
            s = (tm >= a - 1e-9) & (tm <= b + 1e-9)
            d = Tmod[s] - Tm[s]
            out[key][name] = {"rms_K": float(np.sqrt(np.trapezoid(d ** 2, tm[s]) / (tm[s][-1] - tm[s][0]))),
                              "max_abs_K": float(np.max(np.abs(d))), "mean_K": float(np.mean(d))}
    return out


def part_a3(h):
    out = {}
    for k, v in h["part_a3"].items():
        out[k] = {"f": v["f"], "nodes": {n: {kk: v["nodes"][n][kk] for kk in
                                             ("rms_K", "mean_K", "max_abs_K", "model_peak_C", "model_peak_t_s",
                                              "measured_peak_C", "measured_peak_t_s", "diff_at_section_II_end_K")}
                                         for n in v["nodes"]}}
    return out


def part_b():
    rows = list(csv.DictReader(open(os.path.join(RES, "stage10_fmax_nodes.csv"))))
    num = lambda s: None if s in ("", "None") else float(s)
    by = {}
    for r in rows:
        by.setdefault(r["test"], {})[r["node"]] = {"M_C": num(r["M_C"]), "status": r["status"], "f_max": num(r["f_max"]),
                                                   "lo": num(r["lo"]), "hi": num(r["hi"]),
                                                   "overshoot_K": num(r["overshoot_K"]), "peak_f0_C": num(r["peak_f0_C"])}
    four = [t for t in IN.PART_B_TESTS if t != "M50_PT_Exp1"]
    over = {n: span([by[t][n]["overshoot_K"] for t in four]) for n in ("away", "side", "facing")}
    return by, {"four_overshoot_K": over,
                "PT_Exp1_f_max": {n: by["M50_PT_Exp1"][n]["f_max"] for n in ("away", "side", "facing")},
                "PT_Exp1_peak_f0_C": {n: by["M50_PT_Exp1"][n]["peak_f0_C"] for n in ("away", "side", "facing")},
                "PT_Exp1_energy_J": {n: by["M50_PT_Exp1"][n]["f_max"] * _ee("M50_PT_Exp1")
                                     for n in ("away", "side", "facing")}}


def _ee(test):
    """The trigger's ejected energy E_e of a test, as its Stage 10 records carry it (one value per test)."""
    vals = {json.load(open(p))["E_e_J"] for p in glob.glob(os.path.join(RES, "stage10_runs", f"s10_*_{test}_*.json"))}
    assert len(vals) == 1, (test, vals)
    return vals.pop()


def part_c():
    ho, rk = J("stage10_heldout.json"), J("stage10_rank.json")
    held = {}
    for name, pr in ho["predictors"].items():
        held[name] = {d: {"d_log": v["observed"]["d_log"], "d_brier": v["observed"]["d_brier"], "p_log": v["p_log"],
                          "p_brier": v["p_brier"], "band_log": v["band_log_2.5_97.5"],
                          "band_brier": v["band_brier_2.5_97.5"],
                          "log_constant": v["observed"]["constant"]["log"],
                          "log_logistic": v["observed"]["logistic"]["log"]}
                      for d, v in pr.items()}
    allv = [v for p in held.values() for v in p.values()]
    rank = {q: {w: {"rho": d[w].get("rho"), "p": d[w]["p"]} for w in ("outcome", "time", "E_b", "connection")}
            for q, d in rk["quantities"].items()}
    nonE = [v[w] for v in rank.values() for w in ("outcome", "time")]
    spread = {k: {"ratio": v["ratio_largest_to_smallest_nonzero"], "zero_share": v["zero_share_of_16"],
                  "n_with_fraction": v["n_with_fraction"], "fstar_ratio": v.get("fstar_ratio_largest_to_smallest_nonzero"),
                  "fstar_zero_share": v.get("fstar_zero_share_of_16")} for k, v in rk["spread"].items()}
    return {"n_perm": ho["n_perm"], "seed_C1": ho["seed"], "seed_C2": rk["seed"],
            "fits_not_converged": ho.get("fits_not_converged"),
            "split": {"series": ho["n_series"], "parallel": ho["n_parallel"], "propagated_series": ho["propagated_series"],
                      "propagated_parallel": ho["propagated_parallel"]},
            "held_out": held, "largest_d_log": max(v["d_log"] for v in allv), "smallest_d_log": min(v["d_log"] for v in allv),
            "smallest_p_log": min(v["p_log"] for v in allv), "smallest_p_brier": min(v["p_brier"] for v in allv),
            "rank": rank, "smallest_p_outcome_time": min(v["p"] for v in nonE),
            "smallest_p_connection": min(v["connection"]["p"] for v in rank.values()),
            "rho_outcome_span": span([v["outcome"]["rho"] for v in rank.values()]),
            "rho_E_b": {q: v["E_b"]["rho"] for q, v in rank.items()}, "spread": spread}


def part_d():
    s = J("stage10_survey.json")
    q = [d for d in s["datasets"] if d.get("qualifies")][0]
    return {"searches": len([x for x in s["searches"] if x["tool"] == "web search"]), "pages_read": len(s["pages_read"]),
            "pages_not_read": len(s["pages_not_read"]), "datasets_listed": len(s["datasets"]),
            "datasets_scored": len([d for d in s["datasets"] if d.get("scored")]),
            "found_outside": len(s["found_outside_the_question"]), "qualifying": s["qualifying_dataset"],
            "qualifying_detail": {k: q[k] for k in ("reference", "cell", "n_tests", "arrangement", "trigger", "per_test", "access")},
            "contact_datasets_with_outcomes_and_times": s["contact_datasets_with_outcomes_and_times"],
            "covered_without_invention": s["covered_without_invention"]}


def runs():
    recs = [json.load(open(p)) for p in glob.glob(os.path.join(RES, "stage10_runs", "s10_*.json"))]
    walls = [r["wall_s"] for r in recs if r.get("wall_s")]
    lock = J("stage10_laptop_workers.json")
    ends = sorted(r.get("finished_utc") or "" for r in recs)
    kinds = {}
    for r in recs:
        kinds.setdefault(r["kind"], 0)
        kinds[r["kind"]] += 1
    return {"records": len(recs), "failed": sum(1 for r in recs if r.get("failed")), "by_part": kinds,
            "wall_s": span(walls), "wall_median_s": statistics.median(walls) if walls else None,
            "wall_total_s": sum(walls), "started_utc": lock["started_utc"], "workers": lock["workers"],
            "last_finished_utc": ends[-1] if ends else None}


def checks():
    c = J("stage10_checks.json")
    return {"V1": c["V1"], "V2": {"pass": c["V2"]["pass"], "records": c["V2"]["records"],
                                  "distances_from_line_mm": {n: d["arc_mm"] for n, d in c["V2"]["distances_from_line"].items()}},
            "V3": {k: c["V3"][k] for k in ("pass", "largest_score_difference", "largest_rho_difference", "seed")},
            "V4": {"pass": c["V4"]["pass"]}, "X": {k: c["X"][k] for k in ("pass", "pairs", "largest_K")}}


def main():
    h = J("stage10_history_scores.json")
    a, a_sum = part_a(h)
    b, b_sum = part_b()
    card = J("stage10_scorecard.json")
    out = {"measured": measured(), "nodes": {n: {"theta_deg": d["theta_deg"], "node": d["node"],
                                                 "arc_mm": IN.arc_mm(d["theta_deg"])} for n, d in IN.NODES.items()},
           "readings": {k: {kk: vv for kk, vv in v.items()} for k, v in IN.READINGS.items()},
           "part_a": a, "part_a_summary": a_sum, "part_a_segments_exploratory": segments(h), "part_a3": part_a3(h),
           "part_b": b, "part_b_summary": b_sum,
           "separation": card["separation"], "part_c": part_c(), "part_d": part_d(), "runs": runs(), "checks": checks(),
           "verdicts": card["verdicts"],
           "held": [k for k, v in card["verdicts"].items() if v == "held"],
           "failed": [k for k, v in card["verdicts"].items() if v == "failed"]}
    json.dump(out, open(os.path.join(RES, "stage10_paper_numbers.json"), "w"), indent=1, default=float)
    print(json.dumps({"held": out["held"], "failed": out["failed"], "runs": out["runs"]["records"]}))


if __name__ == "__main__":
    main()
