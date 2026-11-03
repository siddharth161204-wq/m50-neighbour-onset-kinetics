#!/usr/bin/env python3
"""Stage 12 scoring (predictions_stage12.md; DECISIONS.md D122 to D124). No run is made here: everything is read from
the Stage 12 records (results/stage12_runs/) and the records of Stages 6 to 10 that the brief names.

Part A (P1, P2): the four capped runs, one per connection and contact (D122 (6)), written out per test for the eight
tests in which the fitted trigger meets C1 at f = 0, beside the fitted trigger's crossing (Stage 7) and, at the central
contact, Stage 6's record at the same energy and release.
Part B: B1, f*(C1) and f*(C2) of the four Stage 11 tests, and B2, f_t(C2) of the nine propagated tests, each as a
fraction of the fixed ejected energy (76,741.25 J), with the delivered energy beside Stage 8's or Stage 9's (D123 (2),
(3)). A run depends on the fraction and the ejected energy only through the delivered energy (D122 (7)), so a fraction
of the fixed energy is the delivered energy over 76,741.25 J.
Part C: the spread between tests of the fractions read from the tests under Part B (Stage 10 C3's set and rule: f_t(C2)
where B2 ends matched or bracketed, the registered f_max, the two exploratory maxima apart), which with one ejected
energy for every test is also the spread in delivered energy, against Stage 10's; the share of zeros; the ends with
Fransson et al.'s "cell movement" marks.

Writes results/stage12_capped.csv, results/stage12_fixed_ejecta.csv and results/stage12_scorecard.json.
Usage: python3 stage12_score.py
"""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage9_run as R9                  # noqa: E402  (unchanged)
import stage12_inputs as IN              # noqa: E402
import stage12_run as R12                # noqa: E402

ROOT = os.path.join(HERE, "..")
RES = os.path.join(ROOT, "results")
T_ONSET_C = 255.7                        # D35: C1 and C2 are met when the hot spot or the lumped neighbour reaches it
DELIVERIES = ("tri21", "120", "240", "360")


def rows(path):
    with open(path) as fh:
        return list(csv.DictReader(fh))


def categories():
    return {r["test"]: r["failure_category"] for r in rows(os.path.join(ROOT, "inputs", "fransson2024", "m50_tests.csv"))}


def fitted_c1_times():
    """{(test, contact): the fitted trigger's C1 crossing at f = 0} (Stage 7's per-test runs, central and high)."""
    out = {}
    for r in rows(os.path.join(RES, "stage7_pertest.csv")):
        if r["criterion"] == "C1" and r["contact"] in IN.H_A and r["predicted"] == "Yes":
            out[(r["test"], r["contact"])] = float(r["predicted_time_s"])
    return out


# ------------------------------------------------------------------------------------------------ Part A
def part_a(recs):
    s6 = {c: json.load(open(os.path.join(RES, "stage6_runs", rid + ".json"))) for c, rid in IN.STAGE6_IDS.items()}
    fit = fitted_c1_times()
    bt = R9.by_test()
    out, runs = [], {}
    for (c, h), tests in sorted(IN.a_points().items(), key=lambda kv: (kv[0][1] != "central", kv[0][0])):
        rid = f"s12_A_cap_{c}_h{h}_both_ns"
        r = recs[rid]
        rr, ll = r["resolved"], r["lumped"]
        c1 = rr["t_prop_s"] if rr["propagated"] else None
        c2 = ll["t_prop_s"] if ll["propagated"] else None
        runs[f"{c}_{h}"] = {"id": rid, "tests": tests, "C1_s": c1, "C2_s": c2,
                            "hot_spot_peak_C": rr["peak_hottest_C"], "hot_spot_t_peak_s": rr["t_peak_hottest_s"],
                            "lumped_peak_C": ll["peak_C"], "lumped_t_peak_s": ll["t_peak_s"],
                            "far_face_peak_C": rr["probe_peak"]["away"]["T_C"], "far_face_t_peak_s": rr["probe_peak"]["away"]["t_s"],
                            "mean_peak_C": rr["peak_mean_C"], "trigger_peak_C": r["T1max_C"], "h_c_W_m2K": r["h_c_W_m2K"],
                            "shortfall_hot_spot_K": T_ONSET_C - rr["peak_hottest_C"],
                            "shortfall_lumped_K": T_ONSET_C - ll["peak_C"], "t_end_s": rr["t_end_s"]}
        st6 = s6[c] if h == "central" else None
        for t in sorted(tests, key=lambda x: bt[x]["E_b_J"]):
            out.append({"test": t, "connection": c, "contact": h, "h_c_W_m2K": r["h_c_W_m2K"],
                        "E_b_fitted_J": round(bt[t]["E_b_J"], 1), "E_b_capped_J": r["E_body_J"], "run": rid,
                        "fitted_C1_at_f0_s": round(fit[(t, h)], 2) if (t, h) in fit else "",
                        "capped_C1_s": "" if c1 is None else round(c1, 2), "capped_C2_s": "" if c2 is None else round(c2, 2),
                        "hot_spot_peak_C": round(rr["peak_hottest_C"], 2), "hot_spot_t_peak_s": rr["t_peak_hottest_s"],
                        "lumped_peak_C": round(ll["peak_C"], 2), "lumped_t_peak_s": ll["t_peak_s"],
                        "far_face_peak_C": round(rr["probe_peak"]["away"]["T_C"], 2),
                        "trigger_peak_C": round(r["T1max_C"], 2),
                        "stage6_record": st6["id"] if st6 else "",
                        "stage6_hot_spot_peak_C": round(st6["resolved"]["peak_hottest_C"], 2) if st6 else "",
                        "stage6_lumped_peak_C": round(st6["lumped"]["peak_C"], 2) if st6 else ""})
    return out, runs


def score_a(runs, h):
    sel = {k: v for k, v in runs.items() if k.endswith("_" + h)}
    holds = all(v["C1_s"] is None and v["hot_spot_peak_C"] < T_ONSET_C for v in sel.values())
    return {"verdict": "holds" if holds else "fails", "runs": sel,
            "tests_meeting_C1": sum(len(v["tests"]) for v in sel.values() if v["C1_s"] is not None),
            "tests_meeting_C2": sum(len(v["tests"]) for v in sel.values() if v["C2_s"] is not None),
            "hot_spot_peak_C": [min(v["hot_spot_peak_C"] for v in sel.values()), max(v["hot_spot_peak_C"] for v in sel.values())],
            "lumped_peak_C": [min(v["lumped_peak_C"] for v in sel.values()), max(v["lumped_peak_C"] for v in sel.values())],
            "far_face_peak_C": [min(v["far_face_peak_C"] for v in sel.values()), max(v["far_face_peak_C"] for v in sel.values())],
            "shortfall_hot_spot_K": [min(v["shortfall_hot_spot_K"] for v in sel.values()),
                                     max(v["shortfall_hot_spot_K"] for v in sel.values())]}


# ------------------------------------------------------------------------------------------------ Part B
def _fx(f, ee):
    """A fraction of r E_b as a fraction of the fixed energy."""
    return f * ee / IN.E_FIX_J


def part_b(recs):
    pts = R12.points(recs)
    b1, b2 = R12.states(recs)
    f8 = R9.fstar8()
    out_rows, B1, B2 = [], {}, {}
    for t in IN.B1_TESTS:
        for crit in ("C1", "C2"):
            st = b1[f"B1_{crit}_{t}"]
            ee = st["e_e"]
            s8 = f8[t][crit]
            lo8, hi8 = (0.0, 0.0) if s8["status"] == "zero" else (s8["lo"], s8["hi"])
            runs = [{"f": m, "E_J": m * ee, "crossing_s": pts[(t, m)][crit], "id": [i for i in pts[(t, m)]["ids"]]}
                    for m in st["runs"]] if st["status"] != "searching" else []
            B1[f"{crit}_{t}"] = {
                "status": st["status"], "E_e_J": ee,
                "stage8": {"status": s8["status"], "f": [lo8, hi8], "E_J": [lo8 * ee, hi8 * ee]},
                "f_r_Eb": [st["lo"], st["hi"]], "E_star_J": [st["lo"] * ee, st["hi"] * ee],
                "f_fixed": [_fx(st["lo"], ee), _fx(st["hi"], ee)], "width_fixed": _fx(st["hi"] - st["lo"], ee),
                "stage8_f_fixed": [_fx(lo8, ee), _fx(hi8, ee)], "runs": runs}
            out_rows.append({"part": "B1", "test": t, "criterion": crit, "propagated": R9.by_test()[t]["propagated"],
                             "E_e_test_J": round(ee, 1), "prior_stage": 8, "prior_status": s8["status"],
                             "prior_lo_f": lo8, "prior_hi_f": hi8, "prior_E_lo_J": round(lo8 * ee, 1),
                             "prior_E_hi_J": round(hi8 * ee, 1), "status": st["status"], "lo_f": st["lo"], "hi_f": st["hi"],
                             "f_t": "", "t_run_s": "", "measured_s": "",
                             "E_lo_J": round(st["lo"] * ee, 1), "E_hi_J": round(st["hi"] * ee, 1), "E_t_J": "",
                             "f_fixed_lo": round(_fx(st["lo"], ee), 6), "f_fixed_hi": round(_fx(st["hi"], ee), 6),
                             "f_fixed_t": "", "stage12_runs": " ".join(f"{m:g}" for m in st["runs"])})
    for t in IN.b2_tests():
        st = b2[f"B2_{t}"]
        ee = st["e_e"]
        ft = st.get("f_t")
        runs = [{"f": m, "E_J": m * ee, "crossing_s": pts[(t, m)]["C2"], "id": pts[(t, m)]["ids"]} for m in st["runs"]]
        B2[t] = {"status": st["status"], "t_m_s": st["t_m"], "E_e_J": ee,
                 "stage9": {"status": st["stage9_status"], "f": [st["stage9_lo"], st["stage9_hi"]],
                            "f_t": IN.stage9_a2(t).get("f_t")},
                 "f_r_Eb": [st["lo"], st["hi"]], "f_t_r_Eb": ft, "E_t_J": None if ft is None else ft * ee,
                 "f_t_fixed": None if ft is None else _fx(ft, ee), "E_bracket_J": [st["lo"] * ee, st["hi"] * ee],
                 "f_fixed_bracket": [_fx(st["lo"], ee), _fx(st["hi"], ee)], "t_run_s": st.get("t_run"),
                 "t_lo_s": st.get("t_lo"), "t_hi_s": st.get("t_hi"), "runs": runs}
        s9 = IN.stage9_a2(t)
        out_rows.append({"part": "B2", "test": t, "criterion": "C2", "propagated": True, "E_e_test_J": round(ee, 1),
                         "prior_stage": 9, "prior_status": s9["status"], "prior_lo_f": s9.get("lo"),
                         "prior_hi_f": s9.get("hi"), "prior_E_lo_J": round(s9["lo"] * ee, 1),
                         "prior_E_hi_J": round(s9["hi"] * ee, 1), "status": st["status"], "lo_f": st["lo"],
                         "hi_f": st["hi"], "f_t": "" if ft is None else ft,
                         "t_run_s": "" if st.get("t_run") is None else round(st["t_run"], 2), "measured_s": st["t_m"],
                         "E_lo_J": round(st["lo"] * ee, 1), "E_hi_J": round(st["hi"] * ee, 1),
                         "E_t_J": "" if ft is None else round(ft * ee, 1),
                         "f_fixed_lo": round(_fx(st["lo"], ee), 6), "f_fixed_hi": round(_fx(st["hi"], ee), 6),
                         "f_fixed_t": "" if ft is None else round(_fx(ft, ee), 6),
                         "stage12_runs": " ".join(f"{m:g}" for m in st["runs"])})
    st9 = {r["test"]: r["fmax_status"] for r in rows(os.path.join(RES, "stage9_fractions.csv"))}
    for t, (fm, e) in sorted(IN.fmax_registered().items()):
        ee = IN.e_e(t)
        out_rows.append({"part": "f_max (Stage 9, restated)", "test": t, "criterion": "far face peak", "propagated": False,
                         "E_e_test_J": round(ee, 1), "prior_stage": 9, "prior_status": st9[t],
                         "prior_lo_f": "", "prior_hi_f": "", "prior_E_lo_J": "", "prior_E_hi_J": "",
                         "status": "restated", "lo_f": "", "hi_f": "", "f_t": fm, "t_run_s": "", "measured_s": "",
                         "E_lo_J": "", "E_hi_J": "", "E_t_J": round(e, 1), "f_fixed_lo": "", "f_fixed_hi": "",
                         "f_fixed_t": round(e / IN.E_FIX_J, 6), "stage12_runs": ""})
    return out_rows, B1, B2


def score_p3_p4(B2):
    used = {t: v for t, v in B2.items() if v["status"] in ("matched", "bracketed")}
    en = {t: v["E_t_J"] for t, v in used.items()}
    big, small = max(en, key=en.get), min(en, key=en.get)
    ratio = en[big] / en[small]
    p3 = {"verdict": "holds" if ratio >= 10.0 else "fails", "ratio": ratio, "n": len(en), "E_t_J": en,
          "largest": [big, en[big]], "smallest": [small, en[small]],
          "not_counted": {t: v["status"] for t, v in B2.items() if t not in used}}
    fm = {t: (f, e) for t, (f, e) in IN.fmax_registered().items()}
    tmax = max(fm, key=lambda t: fm[t][1])
    fmax_fixed = fm[tmax][1] / IN.E_FIX_J
    ft_fixed = {t: v["f_t_fixed"] for t, v in used.items()}
    tmin = min(ft_fixed, key=ft_fixed.get)
    p4 = {"verdict": "holds" if fmax_fixed > ft_fixed[tmin] else "fails",
          "largest_registered_f_max": {"test": tmax, "f_r_Eb": fm[tmax][0], "E_J": fm[tmax][1], "f_fixed": fmax_fixed},
          "smallest_f_t": {"test": tmin, "f_fixed": ft_fixed[tmin], "E_J": en[tmin]},
          "ratio": fmax_fixed / ft_fixed[tmin]}
    return p3, p4


# ------------------------------------------------------------------------------------------------ Part C
def stage10_spreads():
    """Stage 10 C3's spreads (C2, the four deliveries) in fraction (as recorded) and in energy (each fraction times the
    test's r E_b, as the manuscript's numbers compute it)."""
    sp = json.load(open(os.path.join(RES, "stage10_rank.json")))["spread"]
    out = {}
    for d in DELIVERIES:
        s = sp[f"C2_{d}"]
        nz = {t: x for t, x in s["fractions"].items() if x > 0}
        en = {t: x * IN.e_e(t) for t, x in nz.items()}
        out[d] = {"fraction_ratio": s["ratio_largest_to_smallest_nonzero"],
                  "energy_ratio": max(en.values()) / min(en.values()),
                  "energy_ends": [min(en, key=en.get), max(en, key=en.get)],
                  "fraction_ends": [min(nz, key=nz.get), max(nz, key=nz.get)],
                  "zero_share_of_16": s["zero_share_of_16"], "n_with_fraction": s["n_with_fraction"],
                  "fstar_ratio": s["fstar_ratio_largest_to_smallest_nonzero"]}
    return out


def part_c(B1, B2):
    cat = categories()
    fm = IN.fmax_registered()
    frac, energy, none = {}, {}, []
    for t, v in B2.items():
        if v["status"] in ("matched", "bracketed"):
            frac[t], energy[t] = v["f_t_fixed"], v["E_t_J"]
        else:
            none.append([t, v["status"]])
    for t, (f, e) in fm.items():
        frac[t], energy[t] = e / IN.E_FIX_J, e
    nz = {t: x for t, x in frac.items() if x > 0}
    big, small = max(nz, key=nz.get), min(nz, key=nz.get)
    ratio = nz[big] / nz[small]
    zeros = sorted(t for t, x in frac.items() if x == 0.0)
    thr = {t: B2[t]["E_bracket_J"] for t, _ in none}
    with_thr = [max(max(energy.values()), max(b[i] for b in thr.values())) / min(e for e in energy.values() if e > 0)
                for i in (0, 1)] if thr else None
    s10 = stage10_spreads()
    # the thresholds f*(C2) as fractions of the fixed energy: B1's brackets for its four tests, Stage 8's restated for the
    # other twelve (the same delivered energies, D122 (7)); the midpoints' spread as Stage 10 C3 took it
    f8 = R9.fstar8()
    bt = R9.by_test()

    def fixed_thresholds(crit):
        fs = {}
        for t in bt:
            ee = IN.e_e(t)
            if f"{crit}_{t}" in B1:
                lo, hi = B1[f"{crit}_{t}"]["f_r_Eb"]
                src = "Stage 12 (B1)"
            else:
                s = f8[t][crit]
                lo, hi = (0.0, 0.0) if s["status"] == "zero" else (s["lo"], s["hi"])
                src = "Stage 8, restated"
            fs[t] = {"f_fixed": [_fx(lo, ee), _fx(hi, ee)], "mid_fixed": _fx(0.5 * (lo + hi), ee),
                     "E_J": [lo * ee, hi * ee], "source": src, "propagated": bt[t]["propagated"]}
        return fs

    def by_group(fs):
        return {g: [min(v["f_fixed"][0] for v in fs.values() if v["propagated"] == p),
                    max(v["f_fixed"][1] for v in fs.values() if v["propagated"] == p)]
                for g, p in (("propagated", True), ("not_propagated", False))}

    fs = fixed_thresholds("C2")
    fs1 = fixed_thresholds("C1")
    mids = {t: v["mid_fixed"] for t, v in fs.items() if v["mid_fixed"] > 0}
    fs_ratio = max(mids.values()) / min(mids.values())
    return {"set": "Stage 10 C3's (C2, 21.39 s): f_t(C2) where B2 ends matched or bracketed, the registered f_max",
            "fractions_fixed": frac, "energies_J": energy, "no_fraction": none,
            "ratio_largest_to_smallest_nonzero": ratio,
            "largest": {"test": big, "f_fixed": nz[big], "E_J": energy[big], "category": cat[big],
                        "cell_movement": cat[big] == "cell movement"},
            "smallest": {"test": small, "f_fixed": nz[small], "E_J": energy[small], "category": cat[small],
                         "cell_movement": cat[small] == "cell movement"},
            "zero_tests": zeros, "zero_share_of_16": len(zeros) / 16.0, "n_with_fraction": len(frac),
            "cell_movement_tests": sorted(t for t, c in cat.items() if c == "cell movement"),
            "threshold_brackets_J": thr, "ratio_if_thresholds_counted_at_bracket_ends": with_thr,
            "stage10": s10,
            "stage10_energy_ratio_range": [min(v["energy_ratio"] for v in s10.values()),
                                           max(v["energy_ratio"] for v in s10.values())],
            "stage10_fraction_ratio_range": [min(v["fraction_ratio"] for v in s10.values()),
                                             max(v["fraction_ratio"] for v in s10.values())],
            "fstar_C2_fixed": fs, "fstar_C2_fixed_ratio_of_midpoints": fs_ratio,
            "fstar_C2_fixed_zero_tests": sorted(t for t, v in fs.items() if v["mid_fixed"] == 0.0),
            "fstar_C2_fixed_ends": [min(mids, key=mids.get), max(mids, key=mids.get)],
            "fstar_C2_fixed_by_group": by_group(fs),
            "fstar_C1_fixed": fs1, "fstar_C1_fixed_by_group": by_group(fs1),
            "fstar_C1_fixed_zero_tests": sorted(t for t, v in fs1.items() if v["mid_fixed"] == 0.0)}


# ------------------------------------------------------------------------------------------------ main
def write_csv(path, rws):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rws[0].keys()))
        w.writeheader()
        for r in rws:
            w.writerow(r)


def main(runs_dir=None, out=RES):
    recs = R12.load_records(runs_dir)
    b1, b2 = R12.states(recs)
    open_ = [k for k, v in {**b1, **b2}.items() if v["status"] == "searching"]
    if open_:
        raise SystemExit(f"searches still open: {open_}")
    arows, runs = part_a(recs)
    brows, B1, B2 = part_b(recs)
    p3, p4 = score_p3_p4(B2)
    pc = part_c(B1, B2)
    card = {"P1": dict(score_a(runs, "central"), foreseen_by_records=True,
                       statement="With E_b capped at 33.2 kJ, conduction and radiation alone meet C1 in none of the eight "
                                 "tests at the central contact."),
            "P2": dict(score_a(runs, "high"), foreseen_by_records=False,
                       statement="At the high contact the same holds."),
            "P3": dict(p3, foreseen_by_records=True,
                       statement="With E_e fixed at the Databank's median, the delivered energies E* across the nine "
                                 "propagated tests still span at least tenfold."),
            "P4": dict(p4, foreseen_by_records=True,
                       statement="With E_e fixed, the propagated and non-propagated tests' fractions still overlap (the "
                                 "largest f_max above the smallest f_t(C2)).")}
    verdicts = {k: v["verdict"] for k, v in card.items()}
    n_fail = sum(1 for v in verdicts.values() if v == "fails")
    write_csv(os.path.join(out, "stage12_capped.csv"), arows)
    write_csv(os.path.join(out, "stage12_fixed_ejecta.csv"), brows)
    json.dump({"verdicts": verdicts, "predictions": card, "failed": n_fail, "n_predictions": len(card),
               "failed_foreseen": sum(1 for k, v in card.items() if v["verdict"] == "fails" and v["foreseen_by_records"]),
               "part_b": {"B1": B1, "B2": B2}, "part_c": pc,
               "inputs": {"E_cap_J": IN.E_CAP_J, "E_fix_J": IN.E_FIX_J, "cap_row": list(IN.cap_row()),
                          "T_onset_C": T_ONSET_C, "records": len(recs)}},
              open(os.path.join(out, "stage12_scorecard.json"), "w"), indent=1, default=float)
    print(json.dumps(verdicts))
    print("Part A:", {k: (round(v["hot_spot_peak_C"], 2), round(v["lumped_peak_C"], 2), v["C1_s"], v["C2_s"])
                      for k, v in runs.items()})
    print("P3 ratio", round(p3["ratio"], 3), p3["smallest"], p3["largest"], "P4", p4["largest_registered_f_max"]["f_fixed"],
          p4["smallest_f_t"])
    print("Part C ratio", round(pc["ratio_largest_to_smallest_nonzero"], 3), pc["smallest"]["test"], pc["largest"]["test"],
          "zeros", pc["zero_share_of_16"], "stage10 energy", [round(x, 2) for x in pc["stage10_energy_ratio_range"]],
          "fraction", [round(x, 2) for x in pc["stage10_fraction_ratio_range"]], "f* ratio",
          round(pc["fstar_C2_fixed_ratio_of_midpoints"], 2))


if __name__ == "__main__":
    main()
