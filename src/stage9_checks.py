#!/usr/bin/env python3
"""Stage 9 checks (brief; DECISIONS.md D95): V1 to V4 and the laptop-against-cloud check, written to
results/stage9_checks.json.

  V1  t_c against f on every A1 grid, read again from the records, against results/stage9_v1.json (written by the
      workers before any A2 run) and against the scoring, within 1e-6 s (D99 (4)).
  V2  the searches of A2 (C1 and C2) for M50_PT_Exp4 and M50_ST_Exp3 and of A3 for M50_PT_Exp1, replayed by this
      file's own statement of the rules from the records themselves (found by their ids, not through
      stage9_run's tables), each outcome read from the record and checked against its stored series; acceptance: the
      same status and bracket as the scoring's.
  V3  the long-delivery run of M50_PP_Exp3 under 240 s at f*_lo(C1) with every mesh spacing halved and with every step
      limit halved: the hot spot's peak rise (its peak less 25 C) within 1 % of the base run's.
  V4  every Stage 9 record's energy accounts under 1e-9 of the heat taken in (resolved and lumped), and every
      delivery equal to f E_e (or to the pulse's integral up to the run's end, where it ended first) to 1e-9; where
      two records hold the same point, their crossing times within 1e-6 s (D95 (4), D99 (5)).
  X   the three Stage 8 runs made again on the laptop against their cloud records: the same outcomes, crossings and
      peaks within 1e-6 s and 1e-6 K, and the series within 1e-6 K.
Usage: python3 stage9_checks.py
"""
import glob, json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage9_inputs as IN               # noqa: E402
import stage9_run as R9                  # noqa: E402
import stage9_score as SC                # noqa: E402
import stage9_model as M9                # noqa: E402

RES = os.path.join(HERE, "..", "results")
LEVEL = 255.68157499999995 + 273.15


def _load(d, rid):
    p = os.path.join(RES, d, rid + ".json")
    return json.load(open(p)) if os.path.exists(p) else None


def _series(d, rid):
    p = os.path.join(RES, d, rid + ".npz")
    return np.load(p) if os.path.exists(p) else None


def find(test, f, part, nostop_ok=True, need_full=False, sei="fresh"):
    """V2's own lookup: the record holding (test, f) with the 21.39 s delivery, by id."""
    t = R9.by_test()[test]
    cands = []
    if round(f, 12) == 0.0:
        pre = "pertest" if sei == "fresh" else "aged"
        suf = "_aged" if sei == "aged" else ""
        rid = f"{pre}_{test}_{t['connection']}_hcentral_gcentral_tau{R9.tau_median():.2f}_E{t['E_b_J'] / 1e3:.2f}{suf}"
        cands.append(("stage7_runs", "stage7_series", rid))
        cands.append(("stage9_runs", "stage9_series", f"s9_none_{sei}_both_ns_{test}_f{0.0:.9f}"))
    else:
        for s in ("first", "c1", "c2", "refA_c1", "refA_c2"):
            cands.append(("stage8_runs", "stage8_series", f"{s}_{test}_f{f:.9f}"))
        for m in ("both", "lum"):
            for ns in ("", "_ns"):
                cands.append(("stage9_runs", "stage9_series", f"s9_tri21_{sei}_{m}{ns}_{test}_f{f:.9f}"))
    for d, sd, rid in cands:
        r = _load(d, rid)
        if r is None or r.get("failed"):
            continue
        p = r.get("resolved") if part == "res" else r.get("lumped")
        if p is None:
            continue
        full = p["t_end_s"] >= 900.0 - 1e-9
        if need_full and not full:
            continue
        return r, p, _series(sd, rid), full
    return None, None, None, None


def outcome(p, z, part):
    """The crossing time read from the record and checked against the stored series: before it every sample lies
    below 255.7 C; a run that did not cross went to 900 s with every sample below."""
    tc = p.get("t_prop_s") if p.get("propagated") else None
    if z is not None:
        if part == "res":
            t, T = z["t"], z["Tmax"]
        else:
            t, T = z["t_lumped"], z["T_lumped"]
        if tc is None:
            assert p["t_end_s"] >= 900.0 - 1e-9 and np.all(T < LEVEL), "a run without a crossing reached 255.7 C"
        else:
            assert np.all(T[t < tc - 1e-9] < LEVEL), "a stored sample before the crossing reaches 255.7 C"
    return tc


def v2_a2(test, crit):
    fs = IN.stage8_fstar()[test][crit]
    tm = R9.t_meas(test)
    part = "res" if crit == "C1" else "lum"
    tc = {}

    def get(f):
        f = round(f, 12)
        if f not in tc:
            r, p, z, _ = find(test, f, part)
            assert r is not None, f"V2: no record for {test} {crit} f={f}"
            tc[f] = outcome(p, z, part)
        return tc[f]

    hi0 = None
    for d in IN.GRID_STEPS:
        g = round(fs["hi"] + d, 12)
        t = get(g)
        if t is not None and t < tm:
            hi0 = g
            break
    if hi0 is None:
        return {"status": "above grid"}
    lo, hi = fs["lo"], hi0
    if hi <= lo:
        return {"status": "matched" if abs(tc[hi] - tm) <= IN.T_TOL_S else "early", "lo": lo, "hi": hi}
    if abs(tc[hi] - tm) <= IN.T_TOL_S:
        return {"status": "matched", "lo": lo, "hi": hi, "f_t": hi}
    while hi - lo > IN.WIDTH_T + 1e-12:
        m = round(0.5 * (lo + hi), 12)
        t = get(m)
        if t is not None and abs(t - tm) <= IN.T_TOL_S:
            lo, hi = (lo, m) if t < tm else (m, hi)
            return {"status": "matched", "lo": lo, "hi": hi, "f_t": m}
        lo, hi = (lo, m) if (t is not None and t < tm) else (m, hi)
    lo_t = tc.get(round(lo, 12)) if round(lo, 12) in tc else get(lo)
    return {"status": "bracketed" if lo_t is not None else "threshold", "lo": lo, "hi": hi}


def v2_a3(test):
    M = R9.max_meas(test)
    fs = IN.stage8_fstar()[test]["C1"]
    pk = {}

    def get(f):
        f = round(f, 12)
        if f not in pk:
            r, p, z, full = find(test, f, "res", need_full=True)
            assert r is not None, f"V2: no full record for {test} f={f}"
            pk[f] = p["probe_peak"]["away"]["T_C"]
            if z is not None:
                assert abs(float(np.max(z["probe_away"])) - 273.15 - pk[f]) < 1e-9
        return pk[f]

    p0 = get(0.0)
    if p0 >= M:
        return {"status": "zero", "lo": 0.0, "hi": 0.0}
    if M - p0 <= IN.PEAK_TOL_K:
        return {"status": "matched", "lo": 0.0, "hi": 0.0}
    lo, hi = 0.0, fs["lo"]
    if hi <= 0.0 or get(hi) < M - IN.PEAK_TOL_K:
        return {"status": "extended (not replayed)"}
    if abs(get(hi) - M) <= IN.PEAK_TOL_K:
        return {"status": "matched", "lo": lo, "hi": hi}
    while hi - lo > IN.WIDTH_M + 1e-12:
        m = round(0.5 * (lo + hi), 12)
        p = get(m)
        if abs(p - M) <= IN.PEAK_TOL_K:
            lo, hi = (lo, m) if p >= M else (m, hi)
            return {"status": "matched", "lo": lo, "hi": hi, "f_max": m}
        lo, hi = (lo, m) if p >= M else (m, hi)
    return {"status": "bracketed", "lo": lo, "hi": hi}


def v2(states):
    out = {}
    for test, what in IN.V2_TESTS.items():
        if what == "A2":
            for crit in IN.CRITERIA:
                mine = v2_a2(test, crit)
                st = states[f"A2_{crit}_{test}"]
                same = mine["status"] == st["status"] and all(
                    abs((mine.get(k) or 0.0) - (st.get(k) or 0.0)) < 1e-12 for k in ("lo", "hi"))
                out[f"A2_{crit}_{test}"] = {"replay": mine, "scoring": {k: st.get(k) for k in ("status", "lo", "hi", "f_t")},
                                            "same": same}
        else:
            mine = v2_a3(test)
            st = states[f"A3_{test}"]
            same = mine["status"] == st["status"] and all(
                abs((mine.get(k) or 0.0) - (st.get(k) or 0.0)) < 1e-12 for k in ("lo", "hi"))
            out[f"A3_{test}"] = {"replay": mine, "scoring": {k: st.get(k) for k in ("status", "lo", "hi", "f_max")},
                                 "same": same}
    return {"pass": all(v["same"] for v in out.values()), "searches": out}


def _tc_diff(a, b):
    """The largest difference between two lists of crossing times (None where no crossing), inf where they differ in
    length or in which runs cross."""
    if len(a) != len(b):
        return math.inf
    d = 0.0
    for x, y in zip(a, b):
        if (x is None) != (y is None):
            return math.inf
        if x is not None:
            d = max(d, abs(x - y))
    return d


def v1(states):
    """D99 (4): the grids read now and as the file has them agree within 1e-6 s, the laptop check's tolerance (a point
    may be held by two records, from two machines, D95 (4))."""
    file = json.load(open(R9.V1_FILE)) if os.path.exists(R9.V1_FILE) else None
    now = R9.v1_payload(states)
    diff = max((_tc_diff(now["chains"][k]["t_c"], file["chains"][k]["t_c"]) for k in now["chains"]),
               default=0.0) if file is not None else None
    same = file is not None and set(now["chains"]) == set(file["chains"]) and diff <= 1e-6 and \
        now["flagged"] == file["flagged"]
    return {"written_before_A2": file is not None, "written_utc": file and file["written_utc"],
            "flagged": now["flagged"], "same_as_file": same, "largest_difference_s": diff, "chains": now["chains"]}


def v3(states, P):
    st = states["V3"]
    if st["status"] != "done":
        return {"status": st["status"]}
    v = IN.V3_CASE
    c = R9.CON(v["tau_s"])
    f = st["f"]
    out = {"f": f}
    base = P.entry(c, v["test"], f, "res")
    out["base"] = {"id": base["id"], "peak_hot_C": base["peak_hot"]}
    for nm, cc in (("mesh", dict(c, refine=2.0)), ("step", dict(c, dt_scale=0.5))):
        e = P.entry(cc, v["test"], f, "res")
        rise_b = base["peak_hot"] - 25.0
        out[nm] = {"id": e["id"], "peak_hot_C": e["peak_hot"],
                   "change_of_rise": (e["peak_hot"] - base["peak_hot"]) / rise_b}
    out["pass"] = all(abs(out[k]["change_of_rise"]) < 0.01 for k in ("mesh", "step"))
    return out


def v4(recs, P=None):
    worst = {"res": 0.0, "lum": 0.0, "delivery": 0.0}
    n = {"res": 0, "lum": 0, "deliveries": 0, "whole": 0}
    for r in recs.values():
        if r.get("failed") or r.get("kind") == "xcheck":
            continue
        for part, k in (("resolved", "res"), ("lumped", "lum")):
            p = r.get(part)
            if p is None:
                continue
            if p.get("energy_residual_rel") is not None:
                worst[k] = max(worst[k], abs(p["energy_residual_rel"]))
                n[k] += 1
            src = p.get("sources", {}).get("delivery")
            if src is not None:
                pulse = (M9.Constant if src.get("shape") == "constant" else M9.Triangular)(src["E_J"], src["tau_s"], 0.0)
                want = pulse.cumulative(p["t_end_s"])
                if p["t_end_s"] >= src["tau_s"]:
                    n["whole"] += 1
                    assert abs(src["E_J"] - r["E_delivered_J"]) <= 1e-9 * max(1.0, r["E_delivered_J"])
                worst["delivery"] = max(worst["delivery"], abs(src["delivered_J"] - want) / max(want, 1e-30))
                n["deliveries"] += 1
    # D95 (4), D99 (5): where two records hold the same point, their crossing times agree (within 1e-6 s)
    dup = {"n": 0, "largest_s": 0.0, "disagreeing": []}
    for part, k, a_id, b_id, ta, tb in (P.dups if P is not None else []):
        dup["n"] += 1
        d = math.inf if (ta is None) != (tb is None) else (abs(ta - tb) if ta is not None else 0.0)
        if d > 1e-6:
            dup["disagreeing"].append({"part": part, "point": list(k), "records": [a_id, b_id], "t_c": [ta, tb]})
        elif d > dup["largest_s"]:
            dup["largest_s"] = d
    return {"pass": worst["res"] < 1e-9 and worst["lum"] < 1e-9 and worst["delivery"] < 1e-9 and not dup["disagreeing"],
            "largest": worst, "counts": n, "duplicate_points": dup}


def xcheck():
    out = {}
    for rid in IN.XCHECK:
        a = _load("stage8_runs", rid)
        b = _load("stage9_xcheck", "xcheck_" + rid)
        if b is None:
            out[rid] = {"status": "missing"}
            continue
        d = {"machine": b.get("machine", {}).get("label")}
        ok = True
        for part in ("resolved", "lumped"):
            pa, pb = a.get(part), b.get(part)
            if pa is None:
                continue
            same = pa["propagated"] == pb["propagated"]
            dt = abs((pa.get("t_prop_s") or 0.0) - (pb.get("t_prop_s") or 0.0))
            kpk = "peak_hottest_C" if part == "resolved" else "peak_C"
            dp = abs(pa[kpk] - pb[kpk])
            d[part] = {"same_outcome": same, "crossing_diff_s": dt, "peak_diff_K": dp}
            ok = ok and same and dt < 1e-6 and dp < 1e-6
        za = np.load(os.path.join(RES, "stage8_series", rid + ".npz"))
        zb = np.load(os.path.join(RES, "stage9_xcheck", "xcheck_" + rid + ".npz"))
        diffs = {}
        for k in za.files:
            if k == "imax":                      # D99 (3): the hottest node's index, compared apart, not in the pass
                if k in zb.files and za[k].shape == zb[k].shape:
                    d["imax_entries_differing"] = int(np.sum(za[k] != zb[k]))
                continue
            if k in zb.files and za[k].shape == zb[k].shape:
                diffs[k] = float(np.max(np.abs(za[k] - zb[k]))) if za[k].size else 0.0
            elif k in zb.files:
                diffs[k] = f"shapes {za[k].shape} and {zb[k].shape}"
        d["series_max_abs_diff"] = diffs
        ok = ok and all(isinstance(v, float) and v < 1e-6 for v in diffs.values())
        d["pass"] = ok
        out[rid] = d
    return {"pass": all(v.get("pass") for v in out.values()), "runs": out}


def main():
    recs, P, states = SC.collect()
    out = {"V1": v1(states), "V2": v2(states), "V3": v3(states, P), "V4": v4(recs, P), "X": xcheck()}
    json.dump(SC.clean(out), open(os.path.join(RES, "stage9_checks.json"), "w"), indent=1, default=float)
    print(json.dumps({k: v.get("pass", v.get("flagged")) for k, v in out.items()}))
    return out


if __name__ == "__main__":
    main()
