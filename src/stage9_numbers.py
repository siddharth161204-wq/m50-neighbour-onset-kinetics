#!/usr/bin/env python3
"""Every Stage 9 number quoted in the README, the note, the release notes and the Zenodo description
(results/stage9_paper_numbers.json; DECISIONS.md D97), computed from the Stage 9 records, the Stage 7 and Stage 8
records they reuse and the scoring's and the checks' outputs: the file from which a manuscript of Stages 1 to 9 is to
be written.
Usage: python3 stage9_numbers.py [--res DIR]   (DIR holds stage9_scorecard.json and stage9_checks.json; default
       results/, where the numbers file is written)
"""
import argparse, json, os, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage9_inputs as IN               # noqa: E402
import stage9_run as R9                  # noqa: E402
import stage9_score as SC                # noqa: E402
import stage8_search as SR8              # noqa: E402

RES = os.path.join(HERE, "..", "results")


def span(vals):
    vals = [v for v in vals if v is not None]
    return [min(vals), max(vals)] if vals else None


def fsd(fs):
    return {"status": fs["status"], "lo": fs.get("lo"), "hi": fs.get("hi")}


def ft_block(a, fs, Ee, tau=None):
    """An f_t as the texts quote it: status, value, bracket, its distance from f*, sensitivity, energy and power."""
    out = {"status": a["status"], "found": a.get("found", False), "f_t": a.get("f_t"), "lo": a.get("lo"),
           "hi": a.get("hi"), "t_lo_s": a.get("t_lo"), "t_hi_s": a.get("t_hi"), "t_m_s": a.get("t_m"),
           "f_run": a.get("f_run"), "t_run_s": a.get("t_run"),
           "dtc_df_s": (a.get("sensitivity") or {}).get("dtc_df_s"),
           "sensitivity_runs": [(a.get("sensitivity") or {}).get("f_a"), (a.get("sensitivity") or {}).get("f_b")],
           "bisection_runs": a.get("runs", [])}
    if fs is not None and fs.get("status") in ("zero", "bracket"):
        out["fs"] = fsd(fs)
        if a.get("f_t") is not None:
            out["f_t_minus_fs_hi"] = a["f_t"] - fs["hi"]
            out["f_t_minus_fs_lo"] = a["f_t"] - fs["lo"]
    if a.get("f_t") is not None:
        out["E_J"] = a["f_t"] * Ee
        if tau:
            out["power_W"] = a["f_t"] * Ee / tau
    if a.get("lo") is not None and a.get("hi") is not None:
        out["E_bracket_J"] = [a["lo"] * Ee, a["hi"] * Ee]
    return out


def fm_block(m, Ee, tau=None):
    out = {"status": m["status"], "found": m.get("found", False), "f_max": m.get("f_max"), "lo": m.get("lo"),
           "hi": m.get("hi"), "overshoot_K": m.get("overshoot_K"), "extended": m.get("extended"),
           "M_C": m.get("M"), "f_up": m.get("f_up"), "f_run": m.get("f_run"), "peak_run_C": m.get("p_run"),
           "peak_lo_C": m.get("p_lo"), "peak_hi_C": m.get("p_hi"), "bisection_runs": m.get("runs", [])}
    if m.get("f_max") is not None:
        out["E_J"] = m["f_max"] * Ee
        if tau:
            out["power_W"] = m["f_max"] * Ee / tau
    return out


def runs_block(recs):
    good = [r for r in recs.values() if not r.get("failed")]
    by = {}
    for r in recs.values():
        k = "_".join(str(x) for x in (r.get("shape"), int(round(r.get("tau_d_s") or 0)), r.get("sei"), r.get("models"),
                                      "stopped" if r.get("stop") else "to900", f"mesh{r.get('refine', 1.0):g}",
                                      f"step{r.get('dt_scale', 1.0):g}"))
        by[k] = by.get(k, 0) + 1
    walls = {m: [r["wall_s"] for r in good if r.get("models") == m and r.get("wall_s") is not None]
             for m in ("lumped", "both", "resolved")}
    st = sorted(r["started_utc"] for r in recs.values() if r.get("started_utc"))
    fi = sorted(r["finished_utc"] for r in recs.values() if r.get("finished_utc"))
    lock = os.path.join(RES, "stage9_laptop_workers.json")
    lk = json.load(open(lock)) if os.path.exists(lock) else {}
    machines = sorted({(r.get("machine") or {}).get("label", "") for r in recs.values()})
    return {"n": len(recs), "failed": sorted(k for k, r in recs.items() if r.get("failed")), "by_kind": by,
            "machines": machines, "first_started_utc": st[0] if st else None,
            "last_finished_utc": fi[-1] if fi else None,
            "wall_s": {m: {"n": len(v), "median": statistics.median(v) if v else None, "max": max(v) if v else None,
                           "sum_h": sum(v) / 3600.0 if v else None} for m, v in walls.items()},
            "workers": {"started_utc": lk.get("started_utc"), "first_start": lk.get("workers"),
                        "added": [{"utc": a.get("utc"), "n": len(a.get("pids", [])), "replacing": a.get("replacing")}
                                  for a in lk.get("added", [])],
                        "replaced": len(lk.get("replaced", []))},
            "speculative_recorded": sum(1 for r in recs.values() if r.get("speculative"))}


def part_a(P, states, f8):
    out = {"A1": {}, "A2": {}, "A3": {}, "A3_lumped": {}}
    for t in R9.tests():
        x = t["test"]
        Ee = R9.ratios()["central"] * t["E_b_J"]
        if t["propagated"]:
            out["A1"][x], out["A2"][x] = {}, {}
            for crit in IN.CRITERIA:
                g = states[f"A1_{crit}_{x}"]
                tc = P.tc(R9.TRI21(), x, crit)
                pts = [{"f": f, "t_c_s": tc.get(f)} for f in g.get("grid", [])]
                out["A1"][x][crit] = {"status": g["status"], "fs": fsd(f8[x][crit]), "grid": pts,
                                      "t_c_at_fs_hi_s": pts[0]["t_c_s"] if pts else None}
                out["A2"][x][crit] = ft_block(SC.ft_result(states[f"A2_{crit}_{x}"]), f8[x][crit], Ee)
        else:
            m = SC.fmax_result(states[f"A3_{x}"])
            b = fm_block(m, Ee)
            b.update({"exploratory": x in IN.EXPLORATORY_FMAX, "fC1": fsd(f8[x]["C1"]), "fC2": fsd(f8[x]["C2"]),
                      "below_fC1": _below(m, f8[x]["C1"]), "below_fC2": _below(m, f8[x]["C2"])})
            out["A3"][x] = b
            out["A3_lumped"][x] = fm_block(SC.fmax_result(states[f"A3L_{x}"]), Ee)
    d = {}
    for crit in IN.CRITERIA:
        a2 = [out["A2"][x][crit] for x in out["A2"]]
        found = [a for a in a2 if a["found"]]
        d[crit] = {"t_c_at_fs_hi_s": span(out["A1"][x][crit]["t_c_at_fs_hi_s"] for x in out["A1"]),
                   "status_counts": _count(a["status"] for a in a2), "n_found": len(found),
                   "f_t": span(a["f_t"] for a in found), "f_t_minus_fs_hi": span(a.get("f_t_minus_fs_hi") for a in found),
                   "E_J": span(a.get("E_J") for a in found), "dtc_df_s": span(a["dtc_df_s"] for a in found)}
    reg = [out["A3"][x] for x in IN.REGISTERED_FMAX]
    d["A3_registered"] = {"status_counts": _count(b["status"] for b in reg),
                          "f_max": span(b["f_max"] for b in reg if b["found"]),
                          "overshoot_K": span(b["overshoot_K"] for b in reg if b["status"] == "zero"),
                          "zero": [x for x in IN.REGISTERED_FMAX if out["A3"][x]["status"] == "zero"]}
    d["A3_exploratory"] = {x: {k: out["A3"][x].get(k) for k in ("status", "f_max", "lo", "hi", "E_J")}
                           for x in IN.EXPLORATORY_FMAX}
    out["summary"] = d
    return out


def _below(m, fs):
    import stage9_search as S9
    return S9.below(m, fs) if m.get("found") else None


def _count(it):
    c = {}
    for v in it:
        c[v] = c.get(v, 0) + 1
    return c


def part_b(states):
    out = {}
    for tau in IN.TAUS_B:
        k = f"{tau:.0f}"
        out[k] = {"per_test": {}}
        for t in R9.tests():
            x = t["test"]
            Ee = R9.ratios()["central"] * t["E_b_J"]
            r = {"propagated": t["propagated"], "fs": {}}
            for crit in IN.CRITERIA:
                fs = SR8.f_star(states[f"B_fs_{crit}_{tau:.0f}_{x}"])
                r["fs"][crit] = fsd(fs)
            if t["propagated"]:
                for crit in IN.CRITERIA:
                    a = SC.ft_result(states[f"B_ft_{crit}_{tau:.0f}_{x}"])
                    r[f"ft_{crit}"] = ft_block(a, r["fs"][crit], Ee, tau)
            else:
                r["fmax"] = fm_block(SC.fmax_result(states[f"B_fm_{tau:.0f}_{x}"]), Ee, tau)
                r["fmax_lumped"] = fm_block(SC.fmax_result(states[f"B_fmL_{tau:.0f}_{x}"]), Ee, tau)
                r["exploratory"] = x in IN.EXPLORATORY_FMAX
            out[k]["per_test"][x] = r
        pt = out[k]["per_test"]
        s = {}
        for crit in IN.CRITERIA:
            fts = [pt[x][f"ft_{crit}"] for x in pt if pt[x]["propagated"]]
            found = [a for a in fts if a["found"]]
            s[crit] = {"status_counts": _count(a["status"] for a in fts), "n_found": len(found),
                       "f_t": span(a["f_t"] for a in found), "E_J": span(a.get("E_J") for a in found),
                       "power_W": span(a.get("power_W") for a in found),
                       "fs_status_counts": _count(pt[x]["fs"][crit]["status"] for x in pt)}
        reg = [pt[x]["fmax"] for x in IN.REGISTERED_FMAX]
        s["fmax_registered"] = {"status_counts": _count(b["status"] for b in reg),
                                "f_max": span(b["f_max"] for b in reg if b["found"]),
                                "power_W": span(b.get("power_W") for b in reg if b["found"])}
        out[k]["summary"] = s
    return out


def main(res=RES):
    recs, P, states = SC.collect()
    f8 = R9.fstar8()
    card = json.load(open(os.path.join(res, "stage9_scorecard.json")))
    cp = os.path.join(res, "stage9_checks.json")
    chk = json.load(open(cp)) if os.path.exists(cp) else None
    rr = R9.ratios()
    out = {"what": "Every Stage 9 number quoted in the README, the note, the release notes and the Zenodo description "
                   "(DECISIONS.md D97), computed by src/stage9_numbers.py from the Stage 9 records, the Stage 7 and "
                   "Stage 8 records they reuse, the scoring and the checks."}
    out["definitions"] = {
        "level_C": IN.LEVEL_PROP_C, "run_end_s": 900.0, "criteria": {"C1": "the hot spot (resolved neighbour) at the "
                                                                     "level", "C2": "the lumped neighbour at the level"},
        "A1_grid_steps": list(IN.GRID_STEPS), "A2": {"tol_s": IN.T_TOL_S, "width": IN.WIDTH_T},
        "A3": {"tol_K": IN.PEAK_TOL_K, "width": IN.WIDTH_M, "f_end": IN.F_MAX}, "taus_B_s": list(IN.TAUS_B),
        "tau_d_s": R9.tau_median(), "facing_half_deg": 90.0,
        "thermocouple_node": {"base_mesh_node": 9953, "r_mm": 10.55, "theta_deg": 180.0, "z_mm": 35.05,
                              "source": "D89 (6), v12_model.Cell2Contact.probes['away']"},
        "predictions": {"P1_tol_s": IN.P1_TOL_S, "P2_tol_s": IN.P2_TOL_S, "P2_above_fs_hi": IN.P2_ABOVE,
                        "P2_at_least": IN.P2_MIN, "P3_above_fs_hi": IN.P3_ABOVE, "P6_tau_s": IN.P6_TAU_S,
                        "P6_f": IN.P6_F, "P7_factors": list(IN.P7_FACTORS), "P8_change": IN.P8_D},
        "tests": {"registered_fmax": list(IN.REGISTERED_FMAX), "exploratory_fmax": list(IN.EXPLORATORY_FMAX),
                  "P6": list(IN.P6_TESTS), "P8_and_aged": list(IN.P8_TESTS), "V2": IN.V2_TESTS, "V3": IN.V3_CASE,
                  "cross_check": list(IN.XCHECK)},
        "acceptance": {"V3_relative_change_of_rise": 0.01, "V4_relative": 1e-9, "X_s_and_K": 1e-6}}
    out["inputs"] = {"ratio": {"central": rr["central"], "low": rr["low"], "high": rr["high"],
                               "rescale_low": rr["central"] / rr["low"], "rescale_high": rr["central"] / rr["high"]},
                     "per_test": {t["test"]: {"connection": t["connection"], "propagated": t["propagated"],
                                              "t_m_s": t["time_s"], "M_C": t["neighbour_max_C"], "E_b_J": t["E_b_J"],
                                              "E_e_J": rr["central"] * t["E_b_J"], "fC1": fsd(f8[t["test"]]["C1"]),
                                              "fC2": fsd(f8[t["test"]]["C2"])} for t in R9.tests()}}
    out["runs"] = runs_block(recs)
    out["part_a"] = part_a(P, states, f8)
    out["part_b"] = part_b(states)
    out["part_c"] = {"separation": card["separation"], "story": card["story"], "sensitivities": card["sensitivities"]}
    out["verdicts"] = card["verdicts"]
    out["verdict_details"] = card["predictions"]
    out["checks"] = chk
    out["unfinished_chains"] = sorted(k for k, s in states.items() if s["status"] in ("searching", "waiting", "broken"))
    json.dump(SC.clean(out), open(os.path.join(res, "stage9_paper_numbers.json"), "w"), indent=1, default=float)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", default=RES)
    main(ap.parse_args().res)
