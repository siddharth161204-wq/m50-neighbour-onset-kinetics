#!/usr/bin/env python3
"""Stage 10 scoring (predictions_stage10.md; DECISIONS.md D103 to D106): Part A's history test, Part B's f_max at the
three nodes and their separation, and the scorecard of P1 to P8 with Part C's files and Part D's record.

Writes results/stage10_history.csv, results/stage10_history_scores.json, results/stage10_fmax_nodes.csv and
results/stage10_scorecard.json."""
import csv, json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage9_run as R9                  # noqa: E402  (unchanged)
import stage9_search as S9               # noqa: E402  (unchanged)
import stage10_inputs as IN              # noqa: E402
import stage10_run as R10                # noqa: E402

RES = os.path.join(HERE, "..", "results")
NODES = tuple(IN.NODES)                  # away, side, facing
ALL_PROBES = NODES + tuple(IN.EXTRA_PROBES)


# ------------------------------------------------------------------------------------------------ the histories
def series(rid, runs_dir=None):
    import numpy as np
    d = os.path.join(RES, "stage10_series") if runs_dir is None else runs_dir
    z = np.load(os.path.join(d, rid + ".npz"))
    return {k: z[k] for k in z.files}


def first_pass(t, T, level):
    t, T = np.asarray(t, float), np.asarray(T, float)
    i = np.where(T >= level)[0]
    if not len(i):
        return None
    i = int(i[0])
    if i == 0:
        return float(t[0])
    return float(t[i - 1] + (level - T[i - 1]) * (t[i] - t[i - 1]) / (T[i] - T[i - 1]))


def metrics(tm, Tm, tmod, Tmod, t0=IN.WINDOW[0], t1=IN.WINDOW[1]):
    """A2 (D103 (3)): over the window [t0, t1] on the measured record's samples (every 0.5 s), the root mean square of
    the model's history less the measured one (the time average, by the trapezoid rule), the difference at t1, each
    history's rise over the last 60 s before t1, and the times at which each first passes 100 and 150 C (the model's
    over its whole run, the measured over its record)."""
    tm, Tm = np.asarray(tm, float), np.asarray(Tm, float)
    sel = (tm >= t0 - 1e-9) & (tm <= t1 + 1e-9)
    g = tm[sel]
    d = np.interp(g, tmod, Tmod) - Tm[sel]
    rms = math.sqrt(float(np.trapezoid(d ** 2, g)) / (g[-1] - g[0]))
    at = lambda t, T, x: float(np.interp(x, t, T))
    out = {"rms_K": rms, "mean_K": float(np.trapezoid(d, g) / (g[-1] - g[0])), "max_abs_K": float(np.max(np.abs(d))),
           "diff_at_end_K": at(tmod, Tmod, t1) - at(tm, Tm, t1), "model_at_end_C": at(tmod, Tmod, t1),
           "measured_at_end_C": at(tm, Tm, t1),
           "rise_last_model_K": at(tmod, Tmod, t1) - at(tmod, Tmod, t1 - IN.LAST_S),
           "rise_last_measured_K": at(tm, Tm, t1) - at(tm, Tm, t1 - IN.LAST_S)}
    for lev in IN.LEVELS_C:
        out[f"pass_{lev:.0f}_model_s"] = first_pass(tmod, Tmod, lev)
        out[f"pass_{lev:.0f}_measured_s"] = first_pass(tm, Tm, lev)
    return out


def part_a(recs):
    """Every Part A run at every probe, against M50_PT_Exp4's record: the registered window (0 to 271.50 s) and, not
    registered, the window after Section I (24.16 to 271.50 s)."""
    tm, Tm, _ = IN.history("a")
    out, rows_t = {}, None
    cols = {}
    for rid, r in sorted(recs.items()):
        if r.get("kind") != "A" or r.get("failed"):
            continue
        s = series(rid)
        tp = s["probe_t"]
        key = f"{r['reading']}_h{r['h']}"
        out[key] = {"id": rid, "reading": r["reading"], "contact": r["h"], "f": r["f"], "cfg": r["cfg"],
                    "registered": IN.READINGS[r["reading"]]["registered"], "nodes": {}}
        for n in ALL_PROBES:
            Tn = s["probe_" + n] - 273.15
            out[key]["nodes"][n] = {"window": metrics(tm, Tm, tp, Tn),
                                    "after_section_I": metrics(tm, Tm, tp, Tn, IN.T_SECTION_I_END_S, IN.T_PROP_S)}
            cols[f"{key}_{n}_C"] = np.interp(np.asarray(tm), tp, Tn)
    return out, cols


def part_a3(recs):
    """A3 (D103 (5)): M50_PP_Exp3's record against its runs at f = 0 and at f_max at each node (Part B's runs), over
    the record's 500 s: the root mean square, the difference at the end of Section II and the peaks."""
    tm, Tm, _ = IN.history("b")
    out = {}
    for rid, r in sorted(recs.items()):
        if r.get("kind") != "B" or r["test"] != IN.TEST_B or r.get("failed"):
            continue
        s = series(rid)
        tp = s["probe_t"]
        e = {"id": rid, "f": r["f"], "nodes": {}}
        for n in ALL_PROBES:
            Tn = s["probe_" + n] - 273.15
            m = metrics(tm, Tm, tp, Tn, 0.0, IN.RECORD_END_S)
            sel = tp <= IN.RECORD_END_S + 1e-9
            m["model_peak_C"] = float(Tn[sel].max())
            m["model_peak_t_s"] = float(tp[sel][int(np.argmax(Tn[sel]))])
            m["measured_peak_C"] = float(np.max(Tm))
            m["measured_peak_t_s"] = float(np.asarray(tm)[int(np.argmax(Tm))])
            m["diff_at_section_II_end_K"] = float(np.interp(IN.T_SECTION_II_END_B_S, tp, Tn)
                                                  - np.interp(IN.T_SECTION_II_END_B_S, tm, Tm))
            e["nodes"][n] = m
        out[f"f{r['f']:.9f}"] = e
    return out


# ------------------------------------------------------------------------------------------------ Part B
def part_b(recs):
    """B1: f_max at the side and facing nodes (Stage 9's search, D104 (2)), with Stage 9's at the away node; the
    overshoot at f = 0 at every node. B2: the separation at each node."""
    st = R10.chain_states(recs)
    s9 = json.load(open(os.path.join(RES, "stage9_states.json")))
    fm = {}
    for test in IN.PART_B_TESTS:
        a = s9[f"A3_{test}"]
        fm[test] = {"away": {k: a.get(k) for k in ("status", "f_max", "lo", "hi", "overshoot_K", "M", "f_up")}}
        for n in IN.PART_B_NODES:
            x = st[f"B_{n}_{test}"]
            fm[test][n] = {k: x.get(k) for k in ("status", "f_max", "lo", "hi", "overshoot_K", "M", "f_up", "f_run",
                                                 "p_run", "extended", "peak_at_end", "runs")}
        z = [r for r in recs.values() if r.get("kind") == "B" and r["test"] == test and r["f"] == 0.0 and not r.get("failed")]
        if z:
            pk = z[0]["resolved"]["probe_peak"]
            fm[test]["peak_f0_C"] = {n: pk[n]["T_C"] for n in ALL_PROBES}
            fm[test]["overshoot_f0_K"] = {n: pk[n]["T_C"] - R9.max_meas(test) for n in ALL_PROBES}
    small = IN.SMALLEST_FT_C2
    sep = {}
    for n in NODES:
        found = [(fm[t][n]["f_max"], t) for t in IN.PART_B_TESTS
                 if fm[t][n]["status"] in ("zero", "matched", "bracketed") and fm[t][n]["f_max"] is not None]
        if len(found) < len(IN.PART_B_TESTS):
            sep[n] = {"complete": False, "found": len(found)}
            continue
        big = max(found)
        sep[n] = {"complete": True, "largest_f_max": {"test": big[1], "f": big[0]},
                  "smallest_f_t_C2": {"test": small[0], "f": small[1]}, "separate": big[0] < small[1],
                  "margin": small[1] - big[0]}
    return fm, sep


# ------------------------------------------------------------------------------------------------ the scorecard
def _reg(a, reading, h="central"):
    return a.get(f"{reading}_h{h}", {}).get("nodes", {}).get(IN.REGISTERED_NODE, {}).get("window")


def scorecard(a, fm, sep, held, rank, survey):
    P = {}
    s_lo, s_hi = _reg(a, "tri21_C2_lo"), _reg(a, "tri21_C2_hi")
    if s_lo and s_hi:
        best = min(s_lo["rms_K"], s_hi["rms_K"])
        P["P1"] = {"holds": best < 25.0, "rms_lo_K": s_lo["rms_K"], "rms_hi_K": s_hi["rms_K"], "threshold_K": 25.0}
        longs = {k: _reg(a, k) for k in IN.LONG}
        if all(longs.values()):
            P["P2"] = {"holds": all(v["rms_K"] < best for v in longs.values()), "short_best_rms_K": best,
                       "long_rms_K": {k: v["rms_K"] for k, v in longs.items()}}
        meas = s_lo["rise_last_measured_K"]
        lo2, hi2 = meas / 2.0, meas * 2.0
        short_in = [k for k, v in (("lo", s_lo), ("hi", s_hi)) if lo2 <= v["rise_last_model_K"] <= hi2]
        l360 = {k: _reg(a, k) for k in ("con360_C2", "con360_C1")}
        l360_out = all(v and not (lo2 <= v["rise_last_model_K"] <= hi2) for v in l360.values())
        P["P3"] = {"holds": meas > 30.0 and bool(short_in) and l360_out, "measured_rise_K": meas,
                   "factor_two_range_K": [lo2, hi2], "short_rise_K": {"lo": s_lo["rise_last_model_K"],
                                                                      "hi": s_hi["rise_last_model_K"]},
                   "short_within": short_in, "rise_360_K": {k: v["rise_last_model_K"] for k, v in l360.items() if v},
                   "parts": {"measured_above_30_K": meas > 30.0, "short_within_factor_two": bool(short_in),
                             "360_outside": l360_out}}
    if fm:
        four = [t for t in IN.PART_B_TESTS if t != "M50_PT_Exp1"]
        zero_all = all(fm[t][n]["status"] == "zero" or (fm[t][n]["f_max"] == 0.0) for t in four for n in NODES)
        pt1 = fm["M50_PT_Exp1"]
        below = pt1["facing"]["f_max"] is not None and pt1["facing"]["f_max"] < pt1["away"]["f_max"]
        P["P4"] = {"holds": zero_all and below, "four_zero_at_all_nodes": zero_all,
                   "PT_Exp1_f_max": {n: pt1[n]["f_max"] for n in NODES}, "facing_below_stage9": below}
        if all(sep[n].get("complete") for n in NODES):
            P["P5"] = {"holds": all(not sep[n]["separate"] for n in NODES),
                       "separate_at": [n for n in NODES if sep[n]["separate"]], "by_node": sep}
    if held:
        worst = []
        ok = True
        for name, pr in held["predictors"].items():
            for d, v in pr.items():
                o = v["observed"]
                bad = o["d_log"] > IN.LOG_MARGIN or v["p_log"] < IN.P_LEVEL or v["p_brier"] < IN.P_LEVEL
                ok = ok and not bad
                worst.append({"predictor": name, "direction": d, "d_log": o["d_log"], "d_brier": o["d_brier"],
                              "p_log": v["p_log"], "p_brier": v["p_brier"], "breaks": bad})
        P["P6"] = {"holds": ok, "rows": worst}
    if rank:
        hits = []
        for q, d in rank["quantities"].items():
            if "outcome" not in d:
                continue
            for what in ("outcome", "time", "connection"):
                if d[what]["p"] < IN.P_LEVEL:
                    hits.append({"quantity": q, "with": what, "p": d[what]["p"]})
        P["P7"] = {"holds": not hits, "below_0.05": hits}
    if survey:
        P["P8"] = {"holds": bool(survey["contact_datasets_with_outcomes_and_times"]) and not survey["covered_without_invention"],
                   "contact_datasets_with_outcomes_and_times": survey["contact_datasets_with_outcomes_and_times"],
                   "covered_without_invention": survey["covered_without_invention"]}
    for k, v in P.items():
        v["verdict"] = "held" if v["holds"] else "failed"
    return P


def write_history_csv(cols):
    tm, Tm, Tg = IN.history("a")
    names = sorted(cols)
    with open(os.path.join(RES, "stage10_history.csv"), "w") as f:
        f.write("t_s,measured_neighbour_C,measured_trigger_C," + ",".join(names) + "\n")
        for i, t in enumerate(tm):
            f.write(f"{t:.1f},{Tm[i]:.4f},{Tg[i]:.4f}," + ",".join(f"{cols[n][i]:.4f}" for n in names) + "\n")


def write_fmax_csv(fm):
    with open(os.path.join(RES, "stage10_fmax_nodes.csv"), "w") as f:
        f.write("test,M_C,node,theta_deg,status,f_max,lo,hi,overshoot_K,peak_f0_C\n")
        for t in IN.PART_B_TESTS:
            for n in NODES:
                e = fm[t][n]
                th = IN.NODES[n]["theta_deg"]
                pk = fm[t].get("peak_f0_C", {}).get(n)
                f.write(f"{t},{R9.max_meas(t)},{n},{th},{e['status']},{e.get('f_max')},{e.get('lo')},{e.get('hi')},"
                        f"{e.get('overshoot_K')},{pk}\n")


def main():
    recs = R10.load_records()
    a, cols = part_a(recs)
    a3 = part_a3(recs)
    fm, sep = part_b(recs)
    held = json.load(open(os.path.join(RES, "stage10_heldout.json"))) if os.path.exists(os.path.join(RES, "stage10_heldout.json")) else None
    rank = json.load(open(os.path.join(RES, "stage10_rank.json"))) if os.path.exists(os.path.join(RES, "stage10_rank.json")) else None
    sv = os.path.join(RES, "stage10_survey.json")
    survey = json.load(open(sv)) if os.path.exists(sv) else None
    P = scorecard(a, fm, sep, held, rank, survey)
    write_history_csv(cols)
    write_fmax_csv(fm)
    json.dump({"part_a": a, "part_a3": a3, "registered": {"node": IN.REGISTERED_NODE, "contact": "central",
                                                          "window_s": list(IN.WINDOW)}},
              open(os.path.join(RES, "stage10_history_scores.json"), "w"), indent=1, default=float)
    card = {"n_records": len(recs), "n_failed": sum(1 for r in recs.values() if r.get("failed")), "predictions": P,
            "verdicts": {k: v["verdict"] for k, v in P.items()}, "fmax_nodes": fm, "separation": sep}
    json.dump(card, open(os.path.join(RES, "stage10_scorecard.json"), "w"), indent=1, default=float)
    print(json.dumps(card["verdicts"]))


if __name__ == "__main__":
    main()
