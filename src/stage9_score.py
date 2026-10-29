#!/usr/bin/env python3
"""Stage 9 scoring (predictions_stage9.md; DECISIONS.md D91 to D95): the induction curves, the fractions, the long
deliveries and the verdicts on P1 to P8, from the Stage 9 records and the Stage 7 and Stage 8 records they reuse.

Writes results/stage9_induction.csv (one row per point of every f_t search), results/stage9_fractions.csv (one row
per test), results/stage9_long.csv (one row per test and duration), results/stage9_scorecard.json (Part C and P1 to
P8) and results/stage9_states.json (every chain's end). Added after the independent read (D101): each bracketed f_t
is flagged where its bracket straddles a jump of the crossing (jumps), P2 reports for every test the run nearest
in time, and "extended" marks D92 (4)'s extension only, not the exploratory searches.
Usage: python3 stage9_score.py [--out DIR]
"""
import argparse, csv, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage9_inputs as IN               # noqa: E402
import stage9_run as R9                  # noqa: E402
import stage9_search as S9               # noqa: E402
import stage8_search as SR8              # noqa: E402

RES = os.path.join(HERE, "..", "results")


def _f(x):
    return "" if x is None else repr(float(x))


def ft_result(st):
    """The f_t of a chain's end: its status, value, bracket and sensitivity (D91 (3))."""
    if st is None:
        return {"status": "missing"}
    out = {"status": st["status"], "f_t": st.get("f_t"), "lo": st.get("lo"), "hi": st.get("hi"),
           "t_lo": st.get("t_lo"), "t_hi": st.get("t_hi"), "t_m": st.get("t_m"), "runs": st.get("runs", []),
           "sensitivity": st.get("sensitivity"), "f_run": st.get("f_run"), "t_run": st.get("t_run"),
           "fs": st.get("fs")}
    out["found"] = out["status"] in ("matched", "bracketed")
    out["across_jump"] = bool(st.get("across_jump"))     # D101 (2): set by jumps(), from the records' histories
    out["reproduces"] = out["found"] and not out["across_jump"]
    return out


def fmax_result(st):
    if st is None:
        return {"status": "missing"}
    out = {k: st.get(k) for k in ("status", "f_max", "lo", "hi", "overshoot_K", "f_run", "p_run", "p_lo", "p_hi",
                                  "extended", "peak_at_end", "M", "f_up")}
    out["runs"] = st.get("runs", [])
    out["found"] = out["status"] in ("zero", "matched", "bracketed")
    return out


def fs_result(fs):
    return {"status": fs["status"], "lo": fs.get("lo"), "hi": fs.get("hi")}


def fs_text(fs):
    if fs["status"] == "zero":
        return "0"
    if fs["status"] == "above":
        return "above 1"
    if fs["status"] == "bracket":
        return f"({fs['lo']:.10g}, {fs['hi']:.10g}]"
    return fs["status"]


def collect(recs=None):
    recs = R9.load_records() if recs is None else recs
    P = R9.points(recs)
    states = R9.all_states(P, os.path.exists(R9.V1_FILE))
    for name, flag in jumps(P, states).items():
        states[name]["across_jump"] = flag
    return recs, P, states


def _series_of(rid):
    """A record's stored histories, from Stage 9's, Stage 8's or Stage 7's series."""
    import numpy as np
    for d in (R9.SERIES, os.path.join(RES, "stage8_series"), os.path.join(RES, "stage7_series")):
        p = os.path.join(d, rid + ".npz")
        if os.path.exists(p):
            return np.load(p)
    return None


def jumps(P, states):
    """D101 (2), added after the independent read: for each bracketed f_t, whether the bracket straddles a jump of the
    crossing rather than a continuous change. In the run at the bracket's lower end (which crosses at or after the
    measured time t_m), the criterion's history reaches, before t_m, a maximum above its value at t_m: a slightly
    larger fraction then crosses first at that earlier maximum, so the crossing jumps from after t_m to before it
    and no fraction in the bracket reproduces t_m. The registered status (D91 (3)) is kept; the flag is reported
    beside it."""
    import numpy as np
    out = {}
    for ch in R9.chain_defs():
        if ch["kind"] != "ft":
            continue
        st = states.get(ch["name"], {})
        if st.get("status") != "bracketed":
            continue
        part = "res" if ch["crit"] == "C1" else "lum"
        e = P.entry(ch["cfg"], ch["test"], st["lo"], part)
        z = _series_of(e["id"]) if e else None
        if z is None:
            out[ch["name"]] = None
            continue
        t, T = (z["t"], z["Tmax"]) if part == "res" else (z["t_lumped"], z["T_lumped"])
        tm = st["t_m"]
        before = T[t <= tm]
        out[ch["name"]] = bool(before.size and float(before.max()) > float(np.interp(tm, t, T)) + 1e-9)
    return out


# ------------------------------------------------------------------------------------------------ the predictions
def score(P, states):
    ts = R9.by_test()
    f8 = R9.fstar8()
    prop = [t["test"] for t in R9.tests() if t["propagated"]]
    out = {}
    # P1: no C1 crossing within 30 s of the measured time at any f at or above f*_lo (the 21.39 s delivery)
    rows = []
    for x in prop:
        lo = f8[x]["C1"]["lo"]
        tc = P.tc(R9.TRI21(), x, "C1")
        near = [(f, t) for f, t in sorted(tc.items()) if f >= lo - 1e-12 and t is not None
                and abs(t - R9.t_meas(x)) <= IN.P1_TOL_S]
        latest = max((t for f, t in tc.items() if f >= lo - 1e-12 and t is not None), default=None)
        rows.append({"test": x, "t_m": R9.t_meas(x), "runs": sum(1 for f in tc if f >= lo - 1e-12),
                     "latest_crossing_s": latest, "within_30_s": near})
    out["P1"] = {"holds": all(not r["within_30_s"] for r in rows), "rows": rows}
    # P2 and P3: C2 within 30 s at some f in (f*_lo, f*_hi + 0.1]; f_t(C2) within 0.02 above f*_hi
    rows = []
    for x in prop:
        fs = f8[x]["C2"]
        tc = P.tc(R9.TRI21(), x, "C2")
        cand = [(abs(t - R9.t_meas(x)), f, t) for f, t in tc.items()
                if fs["lo"] + 1e-12 < f <= fs["hi"] + IN.P2_ABOVE + 1e-12 and t is not None
                and abs(t - R9.t_meas(x)) <= IN.P2_TOL_S]
        best = min(cand) if cand else None
        near = min(((abs(t - R9.t_meas(x)), f, t) for f, t in tc.items()
                    if fs["lo"] + 1e-12 < f <= fs["hi"] + IN.P2_ABOVE + 1e-12 and t is not None), default=None)
        a2 = ft_result(states[f"A2_C2_{x}"])
        f_p3 = a2["f_t"] if a2["found"] else (best[1] if best else None)
        rows.append({"test": x, "t_m": R9.t_meas(x), "fs": fs_result(fs), "match": bool(cand),
                     "best_run": {"f": best[1], "t_c": best[2], "dt_s": best[2] - R9.t_meas(x)} if best else None,
                     "nearest_run": {"f": near[1], "t_c": near[2], "dt_s": near[2] - R9.t_meas(x)} if near else None,
                     "f_t_A2": a2.get("f_t"), "A2_status": a2["status"], "f_for_P3": f_p3,
                     "above_fs_hi": (f_p3 - fs["hi"]) if f_p3 is not None else None})
    n = sum(r["match"] for r in rows)
    out["P2"] = {"holds": n >= IN.P2_MIN, "count": n, "rows": rows}
    p3 = [r for r in rows if r["match"]]
    out["P3"] = {"holds": bool(p3) and all(r["above_fs_hi"] is not None and r["above_fs_hi"] <= IN.P3_ABOVE + 1e-12
                                            for r in p3),
                 "tests": [r["test"] for r in p3],
                 "largest_above_fs_hi": max((r["above_fs_hi"] for r in p3 if r["above_fs_hi"] is not None), default=None)}
    # P4: the five registered f_max below both f*(C1) and f*(C2)
    rows = []
    for x in IN.REGISTERED_FMAX:
        fm = fmax_result(states[f"A3_{x}"])
        b1 = S9.below(fm, f8[x]["C1"]) if fm["found"] else None
        b2 = S9.below(fm, f8[x]["C2"]) if fm["found"] else None
        rows.append({"test": x, "M_C": R9.max_meas(x), "f_max": fm, "fC1": fs_result(f8[x]["C1"]),
                     "fC2": fs_result(f8[x]["C2"]), "below_C1": b1, "below_C2": b2})
    out["P4"] = {"holds": all(r["below_C1"] is True and r["below_C2"] is True for r in rows), "rows": rows}
    # P5: the largest registered f_max smaller than the smallest f_t(C2)
    out["P5"] = separation(states, 1.0)
    # P6: f_t(C1) under 240 s above 0.2 in the three tests where it can exist
    rows = []
    for x in IN.P6_TESTS:
        a = ft_result(states[f"B_ft_C1_{IN.P6_TAU_S:.0f}_{x}"])
        ok = a["found"] and a["f_t"] > IN.P6_F
        rows.append({"test": x, "f_t": a, "exceeds": ok})
    out["P6"] = {"holds": all(r["exceeds"] for r in rows), "rows": rows}
    # P7: the ratio's bracket rescales every f_t and f_max by r_c / r and leaves P5's verdict unchanged
    rr = R9.ratios()
    fac = {"low": rr["central"] / rr["low"], "high": rr["central"] / rr["high"]}
    rounded = sorted(round(v, 2) for v in fac.values())
    same = {k: separation(states, v)["holds"] == out["P5"]["holds"] for k, v in fac.items()}
    out["P7"] = {"holds": rounded == sorted(IN.P7_FACTORS) and all(same.values()), "factors": fac,
                 "factors_rounded": rounded, "P5_same": same,
                 "P5_rescaled": {k: separation(states, v) for k, v in fac.items()}}
    # P8: the aged SEI changes f_t(C2) by less than 0.01 in the three tests
    rows = []
    for x in IN.P8_TESTS:
        a = ft_result(states[f"C3_ft_C2_{x}"])
        b = ft_result(states[f"A2_C2_{x}"])
        d = (a["f_t"] - b["f_t"]) if (a["found"] and b["found"]) else None
        rows.append({"test": x, "aged": a, "fresh": b, "change": d,
                     "under": d is not None and abs(d) < IN.P8_D})
    out["P8"] = {"holds": all(r["under"] for r in rows), "rows": rows}
    return out


def separation(states, factor=1.0):
    """Part C1 (P5): the five registered f_max against the nine f_t(C2), each times `factor` (P7); the same for C1
    where A2 found any f_t."""
    fms = []
    for x in IN.REGISTERED_FMAX:
        fm = fmax_result(states[f"A3_{x}"])
        if fm["found"]:
            fms.append((fm["f_max"] * factor, x, (fm["lo"] or 0.0) * factor, (fm["hi"] or 0.0) * factor))
    out = {"factor": factor}
    for crit in ("C2", "C1"):
        fts = []
        for t in R9.tests():
            if not t["propagated"]:
                continue
            a = ft_result(states[f"A2_{crit}_{t['test']}"])
            if a["found"]:
                fts.append((a["f_t"] * factor, t["test"], a["lo"] * factor, a["hi"] * factor))
        if fms and fts:
            big, small = max(fms), min(fts)
            d = {"largest_f_max": {"test": big[1], "f": big[0], "bracket": [big[2], big[3]]},
                 "smallest_f_t": {"test": small[1], "f": small[0], "bracket": [small[2], small[3]]},
                 "separate": big[0] < small[0], "margin": small[0] - big[0],
                 "separate_by_brackets": big[3] < small[2] - 1e-12, "n_f_t": len(fts), "n_f_max": len(fms)}
        else:
            d = {"separate": None, "n_f_t": len(fts), "n_f_max": len(fms)}
        out[crit] = d
    out["holds"] = out["C2"]["separate"] is True
    return out


# ------------------------------------------------------------------------------------------------ the files
def induction_rows(P, states):
    rows = []
    for ch in R9.chain_defs():
        if ch["kind"] not in ("grid", "ft"):
            continue
        st = states[ch["name"]]
        x, crit, c = ch["test"], ch["crit"], ch["cfg"]
        if ch["kind"] == "grid":
            fs = R9.fstar8()[x][crit]
        else:
            fs = st.get("fs") or {"status": "waiting"}
        if ch["kind"] == "ft" and ch["part"] == "A":
            continue                           # A2's points are A1's configuration: listed once, by A1's chain below
        tc = P.tc(c, x, crit)
        for f in sorted(tc):
            e = P.entry(c, x, f, "res" if crit == "C1" else "lum")
            rows.append({"chain": ch["name"], "part": ch["part"], "test": x, "criterion": crit,
                         "delivery": R9.cfg_key(c), "f": f,
                         "f_minus_fs_hi": (f - fs["hi"]) if fs.get("hi") is not None else None,
                         "t_c_s": tc[f], "t_m_s": R9.t_meas(x),
                         "peak_thermocouple_C": e.get("peak_away") if crit == "C1" else None,
                         "peak_lumped_C": e.get("peak") if crit == "C2" else None,
                         "to_end": e["full"], "record": e["id"]})
    return rows


def write_csv(path, rows):
    keys = []                                  # D99 (1): every row's columns, in the order first met
    for r in rows:
        keys += [k for k in r if k not in keys]
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if v is None else (repr(v) if isinstance(v, float) else v)) for k, v in r.items()})


def fraction_rows(states):
    f8 = R9.fstar8()
    rows = []
    for t in R9.tests():
        x = t["test"]
        Ee = R9.ratios()["central"] * t["E_b_J"]
        r = {"test": x, "connection": t["connection"], "propagated": t["propagated"], "t_m_s": t["time_s"],
             "M_C": t["neighbour_max_C"], "E_b_J": t["E_b_J"], "E_e_J": Ee,
             "fC1_stage8": fs_text(f8[x]["C1"]), "fC2_stage8": fs_text(f8[x]["C2"])}
        if t["propagated"]:
            for crit in IN.CRITERIA:
                a = ft_result(states[f"A2_{crit}_{x}"])
                fs = f8[x][crit]
                r.update({f"ft_{crit}_status": a["status"], f"ft_{crit}": a.get("f_t"), f"ft_{crit}_lo": a.get("lo"),
                          f"ft_{crit}_hi": a.get("hi"),
                          f"ft_{crit}_minus_fs_hi": (a["f_t"] - fs["hi"]) if a.get("f_t") is not None else None,
                          f"ft_{crit}_minus_fs_lo": (a["f_t"] - fs["lo"]) if a.get("f_t") is not None else None,
                          f"ft_{crit}_dtc_df_s": (a["sensitivity"] or {}).get("dtc_df_s"),
                          f"ft_{crit}_E_J": (a["f_t"] * Ee) if a.get("f_t") is not None else None,
                          f"ft_{crit}_t_hi_s": a.get("t_hi"), f"ft_{crit}_across_jump": a["across_jump"]})
        else:
            fm = fmax_result(states[f"A3_{x}"])
            fl = fmax_result(states[f"A3L_{x}"])
            r.update({"fmax_exploratory": x in IN.EXPLORATORY_FMAX, "fmax_status": fm["status"],
                      "fmax": fm.get("f_max"), "fmax_lo": fm.get("lo"), "fmax_hi": fm.get("hi"),
                      "fmax_overshoot_K": fm.get("overshoot_K"),
                      "fmax_extended": bool(fm.get("extended")) and x not in IN.EXPLORATORY_FMAX,   # D101 (6)
                      "fmax_E_J": (fm["f_max"] * Ee) if fm.get("f_max") is not None else None,
                      "fmax_below_fC1": S9.below(fm, f8[x]["C1"]) if fm["found"] else None,
                      "fmax_below_fC2": S9.below(fm, f8[x]["C2"]) if fm["found"] else None,
                      "fmaxL_status": fl["status"], "fmaxL": fl.get("f_max"), "fmaxL_lo": fl.get("lo"),
                      "fmaxL_hi": fl.get("hi")})
        rows.append(r)
    return rows


def long_rows(states):
    rows = []
    for tau in IN.TAUS_B:
        for t in R9.tests():
            x = t["test"]
            Ee = R9.ratios()["central"] * t["E_b_J"]
            r = {"test": x, "tau_s": tau, "propagated": t["propagated"], "t_m_s": t["time_s"], "M_C": t["neighbour_max_C"],
                 "E_e_J": Ee}
            for crit in IN.CRITERIA:
                st = states[f"B_fs_{crit}_{tau:.0f}_{x}"]
                fs = SR8.f_star(st)
                r[f"fs_{crit}"] = fs_text(fs)
                r[f"fs_{crit}_lo"], r[f"fs_{crit}_hi"] = fs.get("lo"), fs.get("hi")
            if t["propagated"]:
                for crit in IN.CRITERIA:
                    a = ft_result(states[f"B_ft_{crit}_{tau:.0f}_{x}"])
                    r.update({f"ft_{crit}_status": a["status"], f"ft_{crit}": a.get("f_t"),
                              f"ft_{crit}_lo": a.get("lo"), f"ft_{crit}_hi": a.get("hi"),
                              f"ft_{crit}_E_J": (a["f_t"] * Ee) if a.get("f_t") is not None else None,
                              f"ft_{crit}_power_W": (a["f_t"] * Ee / tau) if a.get("f_t") is not None else None,
                              f"ft_{crit}_dtc_df_s": (a["sensitivity"] or {}).get("dtc_df_s"),
                              f"ft_{crit}_across_jump": a["across_jump"]})
            else:
                for nm, ch in (("fmax", f"B_fm_{tau:.0f}_{x}"), ("fmaxL", f"B_fmL_{tau:.0f}_{x}")):
                    fm = fmax_result(states[ch])
                    r.update({f"{nm}_status": fm["status"], nm: fm.get("f_max"), f"{nm}_lo": fm.get("lo"),
                              f"{nm}_hi": fm.get("hi"), f"{nm}_overshoot_K": fm.get("overshoot_K"),
                              f"{nm}_extended": bool(fm.get("extended")) and x not in IN.EXPLORATORY_FMAX,
                              f"{nm}_E_J": (fm["f_max"] * Ee) if fm.get("f_max") is not None else None,
                              f"{nm}_power_W": (fm["f_max"] * Ee / tau) if fm.get("f_max") is not None else None})
                r["fmax_exploratory"] = x in IN.EXPLORATORY_FMAX
            rows.append(r)
    return rows


def story(P, states):
    """Part C2 (D94): for each propagated test, the energies of the two readings, and (exploratory) the thermocouple
    node's temperature at the measured time in the run at f_t(C2) of each delivery."""
    import numpy as np
    rows = []
    for t in R9.tests():
        if not t["propagated"]:
            continue
        x = t["test"]
        Ee = R9.ratios()["central"] * t["E_b_J"]
        r = {"test": x, "t_m_s": t["time_s"], "E_e_J": Ee}
        for d in ["tri21"] + [f"{tau:.0f}" for tau in IN.TAUS_B]:
            name = f"A2_C2_{x}" if d == "tri21" else f"B_ft_C2_{d}_{x}"
            a = ft_result(states[name])
            tau = R9.tau_median() if d == "tri21" else float(d)
            e = {"f_t": a.get("f_t"), "status": a["status"]}
            if a.get("f_t") is not None:
                e.update({"E_J": a["f_t"] * Ee, "power_W": a["f_t"] * Ee / tau})
            s = states.get(f"S_{d}_{x}")
            if s and s.get("status") == "done":
                c = R9.TRI21() if d == "tri21" else R9.CON(float(d))
                ent = P.entry(c, x, s["f"], "res")
                path = os.path.join(R9.SERIES, ent["id"] + ".npz")
                if os.path.exists(path):
                    z = np.load(path)
                    tt, Ta = z["probe_t"], z["probe_away"] - 273.15
                    tm = float(t["time_s"])
                    e["thermocouple_at_t_m_C"] = float(np.interp(tm, tt, Ta))
                    e["thermocouple_60s_before_C"] = float(np.interp(max(tm - 60.0, 0.0), tt, Ta))
                    e["hot_spot_crossing_s"] = ent["t_c"]
                    e["story_record"] = ent["id"]
            r[d] = e
            if d != "tri21":
                b = ft_result(states[f"B_ft_C1_{d}_{x}"])
                r[d]["C1"] = {"f_t": b.get("f_t"), "status": b["status"],
                              "E_J": (b["f_t"] * Ee) if b.get("f_t") is not None else None,
                              "power_W": (b["f_t"] * Ee / tau) if b.get("f_t") is not None else None}
        rows.append(r)
    return rows


def sensitivities(states):
    """C3 (not registered): the ratio's bracket by exact rescaling, and the aged SEI."""
    rr = R9.ratios()
    fac = {"low": rr["central"] / rr["low"], "high": rr["central"] / rr["high"]}
    out = {"factors": fac, "ratios": {k: rr[k] for k in ("central", "low", "high")}, "rescaled": {}, "aged": {}}
    for t in R9.tests():
        x = t["test"]
        if t["propagated"]:
            for crit in IN.CRITERIA:
                a = ft_result(states[f"A2_{crit}_{x}"])
                if a.get("f_t") is not None:
                    out["rescaled"][f"ft_{crit}_{x}"] = {k: a["f_t"] * v for k, v in fac.items()}
        else:
            fm = fmax_result(states[f"A3_{x}"])
            if fm.get("f_max") is not None:
                out["rescaled"][f"fmax_{x}"] = {k: fm["f_max"] * v for k, v in fac.items()}
    for x in IN.P8_TESTS:
        for crit in IN.CRITERIA:
            out["aged"][f"{crit}_{x}"] = {"fs_aged": fs_result(SR8.f_star(states[f"C3_fs_{crit}_{x}"])),
                                          "ft_aged": ft_result(states[f"C3_ft_{crit}_{x}"]),
                                          "ft_fresh": ft_result(states[f"A2_{crit}_{x}"])}
    return out


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, float) and (math.isnan(o) or math.isinf(o)):
        return None
    return o


def main(out=RES):
    recs, P, states = collect()
    rows = induction_rows(P, states)
    write_csv(os.path.join(out, "stage9_induction.csv"), rows)
    write_csv(os.path.join(out, "stage9_fractions.csv"), fraction_rows(states))
    write_csv(os.path.join(out, "stage9_long.csv"), long_rows(states))
    sc = score(P, states)
    card = {"predictions": sc, "verdicts": {k: ("held" if v["holds"] else "failed") for k, v in sc.items()},
            "separation": separation(states), "story": story(P, states), "sensitivities": sensitivities(states),
            "n_records": len(recs), "n_failed": sum(1 for r in recs.values() if r.get("failed")),
            "duplicate_points": [list(d) for d in P.dups]}
    json.dump(clean(card), open(os.path.join(out, "stage9_scorecard.json"), "w"), indent=1, default=float)
    keep = {n: {k: v for k, v in st.items() if k not in ("runs", "speculative_runs", "tc", "pk", "points")}
            for n, st in states.items()}
    json.dump(clean(keep), open(os.path.join(out, "stage9_states.json"), "w"), indent=1, default=float)
    print(json.dumps(card["verdicts"]))
    return card


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=RES)
    main(ap.parse_args().out)
