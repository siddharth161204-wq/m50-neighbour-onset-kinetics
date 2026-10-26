#!/usr/bin/env python3
"""Stage 8 checks (DECISIONS.md D83 (1) to (4)): V1 to V4.

  V1  the ejected energies and the ratios re-derived by separate code: the Databank rows read with the csv module,
      each ratio as (Corrected-Total-Energy-Yield-kJ - Energy-Fraction-Cell-Body-kJ) / Energy-Fraction-Cell-Body-kJ
      (stage8_inputs uses the two ejecta columns instead), the median by numpy, the trigger energies read from
      results/stage7_triggers.json; against results/stage8_ejected.csv, within 1e-9 relative.
  V2  the searches of C1 and C2 for three tests fixed in D83 (2), replayed by this script's own rules from the stored
      records and Stage 7's: from f = 0, each fraction the rules call for is looked up among the records (it must
      exist), its outcome read from the record and checked against its stored series, until the bracket is at most
      0.02 wide; the same f* to the interval as stage8_score.py's.
  V3  the first-round run of M50_PT_Exp1 at f = 0.1 against the same run with every mesh spacing halved (v3mesh) and
      with every step limit halved (v3step): the hot spot's peak rise (its peak less 25 C) changes by under 1 % in
      each; if the base run reaches 255.7 C, its crossing time instead.
  V4  every record's energy accounts close with the delivered and the Joule energy in them (resolved, as D44, and
      lumped, under 1e-9 of the heat taken in), and every delivery equals f E_e and every Joule source f_e 65.52 kJ
      (to 1e-9 relative), or, in a run stopped at 255.7 C before its pulse ended (D35), the pulse's integral up to
      the stop (D86 (3)).
Writes results/stage8_checks.json.
"""
import csv, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RES = os.path.join(HERE, "..", "results")
V2_TESTS = ("M50_PT_Exp4", "M50_ST_Exp3", "M50_PT_Exp1")       # D83 (2)
LEVEL_K = 278.9 * (1 - 0.1665 / 2) + 273.15


def v1(res=RES):
    rows = [r for r in csv.DictReader(open(os.path.join(HERE, "..", "inputs", "databank", "databank_m50_used.csv")))
            if "Nail" in r["Trigger-Mechanism"]]
    ratio = {r["Test-ID"]: (float(r["Corrected-Total-Energy-Yield-kJ"]) - float(r["Energy-Fraction-Cell-Body-kJ"]))
             / float(r["Energy-Fraction-Cell-Body-kJ"]) for r in rows}
    v = np.array(list(ratio.values()))
    central, low, high = float(np.median(v)), float(v.min()), float(v.max())
    trig = {r["test"]: r["E_J"] for r in json.load(open(os.path.join(res, "stage7_triggers.json")))["rows"]}
    rec = list(csv.DictReader(open(os.path.join(res, "stage8_ejected.csv"))))
    worst = 0.0
    n = 0
    for r in rec:
        if r["kind"] == "test":
            n += 1
            for col, rr in (("E_e_J", central), ("E_e_low_J", low), ("E_e_high_J", high)):
                worst = max(worst, abs(float(r[col]) / (rr * trig[r["id"]]) - 1))
            worst = max(worst, abs(float(r["ratio_central"]) / central - 1), abs(float(r["ratio_low"]) / low - 1),
                        abs(float(r["ratio_high"]) / high - 1))
        else:
            worst = max(worst, abs(float(r["ratio"]) / ratio[r["id"]] - 1))
    return {"pass": bool(n == 16 and len(ratio) == 10 and worst < 1e-9), "n_tests": n, "n_rows": len(ratio),
            "largest_relative_difference": worst, "central": central, "low": low, "high": high}


def _records(runs_dir):
    out = {}
    for f in os.listdir(runs_dir):
        if f.endswith(".json"):
            r = json.load(open(os.path.join(runs_dir, f)))
            out[r["id"]] = r
    return out


def _stage7_outcome(res, test, crit):
    for f in os.listdir(os.path.join(res, "stage7_runs")):
        if f.startswith(f"pertest_{test}_") and "_hcentral_" in f:
            r = json.load(open(os.path.join(res, "stage7_runs", f)))
            return bool(r["resolved"]["propagated"] if crit == "C1" else r["lumped"]["propagated"])
    raise KeyError(test)


def _outcome(rec, crit, series_dir):
    """The record's outcome, checked against its stored series (as Stage 7's V2): met if every sample stored before
    the crossing lies below 255.7 C and the run ended within a step of it, before 900 s; not met if the run went to
    900 s and no stored sample reaches 255.7 C."""
    z = np.load(os.path.join(series_dir, rec["id"] + ".npz"))
    if crit == "C1":
        part, t, y = rec["resolved"], z["t"], z["Tmax"]
    else:
        part, t, y = rec["lumped"], z["t_lumped"], z["T_lumped"]
    met = bool(part["propagated"])
    if met:
        tp, te = part["t_prop_s"], part["t_end_s"]
        ok = bool(np.all(y[t < tp] < LEVEL_K)) and tp <= te + 1e-9 and te - tp <= 0.1 + 1e-9 and te < 900.0 - 1e-9
    else:
        ok = bool(np.all(y < LEVEL_K)) and abs(part["t_end_s"] - 900.0) < 1e-6
    return met, bool(ok)


def replay(points_of, probes=(0.1, 0.2, 0.3, 0.5, 1.0), width=0.02):
    """This script's own statement of D78's rules: try the probes inside the bracket in order, then halve it, until it
    is at most `width` wide; points_of(f) returns the outcome at f (None if no record)."""
    pts = {0.0: points_of(0.0)}
    seq = []
    while True:
        no = [f for f, m in pts.items() if m is False]
        yes = [f for f, m in pts.items() if m is True]
        lo = max(no) if no else None
        hi = min(yes) if yes else None
        if hi == 0.0:
            return {"status": "zero", "lo": 0.0, "hi": 0.0, "sequence": seq}
        if lo is not None and lo >= 1.0:
            return {"status": "above", "lo": lo, "hi": None, "sequence": seq}
        nxt = None
        for p in probes:
            if p not in pts and (lo is None or p > lo) and (hi is None or p < hi):
                nxt = p
                break
        if nxt is None:
            if hi - lo <= width + 1e-12:
                return {"status": "bracket", "lo": lo, "hi": hi, "sequence": seq}
            nxt = round(0.5 * (lo + hi), 12)
        m = points_of(nxt)
        if m is None:
            return {"status": "missing", "missing_f": nxt, "sequence": seq}
        pts[nxt] = m
        seq.append((nxt, m))


def v2(res=RES, runs_dir=None, series_dir=None, scored=None):
    runs_dir = os.path.join(res, "stage8_runs") if runs_dir is None else runs_dir
    series_dir = os.path.join(res, "stage8_series") if series_dir is None else series_dir
    recs = _records(runs_dir)
    out, ok_all = {}, True
    for test in V2_TESTS:
        for crit, set_ in (("C1", "c1"), ("C2", "c2")):
            checks = []

            def points_of(f):
                if f == 0.0:
                    return _stage7_outcome(res, test, crit)
                for s in ("first", set_):
                    rid = f"{s}_{test}_f{f:.9f}"
                    if rid in recs:
                        m, ok = _outcome(recs[rid], crit, series_dir)
                        checks.append(ok)
                        return m
                return None
            rp = replay(points_of)
            same = None
            if scored is not None:
                fs = scored[test][crit]
                same = (fs["status"] == rp["status"] and fs.get("lo") == rp.get("lo") and fs.get("hi") == rp.get("hi"))
            ok = rp["status"] in ("zero", "bracket", "above") and all(checks) and same is not False
            ok_all &= ok
            out[f"{test} {crit}"] = dict(rp, series_agree=all(checks), same_as_scoring=same, pass_=ok)
    return {"pass": bool(ok_all), "tests": list(V2_TESTS), "chains": out}


def v3(res=RES, runs_dir=None):
    runs_dir = os.path.join(res, "stage8_runs") if runs_dir is None else runs_dir
    base = json.load(open(os.path.join(runs_dir, "first_M50_PT_Exp1_f0.100000000.json")))
    out = {"base": base["id"]}
    ok = True
    for v in ("v3mesh", "v3step"):
        r = json.load(open(os.path.join(runs_dir, f"{v}_M50_PT_Exp1_f0.100000000.json")))
        if base["resolved"]["propagated"] or r["resolved"]["propagated"]:
            a, b = base["resolved"].get("t_prop_s"), r["resolved"].get("t_prop_s")
            rel = abs(b / a - 1) if (a and b) else None
            q = "crossing time"
        else:
            a, b = base["resolved"]["peak_hottest_C"] - 25.0, r["resolved"]["peak_hottest_C"] - 25.0
            rel = abs(b / a - 1)
            q = "hot spot's peak rise"
        out[v] = {"quantity": q, "base": a, "variant": b, "relative_change": rel, "nodes": r["n_nodes"],
                  "pass": rel is not None and rel < 0.01}
        ok &= out[v]["pass"]
    out["pass"] = bool(ok)
    return out


def _triangle(E, tau, t):
    """The energy a triangular pulse of E over tau from t = 0 has released by t (the check's own statement)."""
    if t <= 0.0:
        return 0.0
    if t >= tau:
        return E
    if t <= tau / 2:
        return 2.0 * E * (t / tau) ** 2
    return E - 2.0 * E * ((tau - t) / tau) ** 2


def v4(res=RES, runs_dir=None):
    """Every account closes, and every source delivered what its pulse releases up to the run's end: f E_e (or f_e
    65.52 kJ) for a run that went past the pulse's end, the pulse's integral up to the stop for one stopped at
    255.7 C before it (D35; D86 (3))."""
    runs_dir = os.path.join(res, "stage8_runs") if runs_dir is None else runs_dir
    recs = _records(runs_dir)
    worst = {"resolved": 0.0, "lumped": 0.0, "delivery": 0.0, "joule": 0.0}
    n = {"resolved": 0, "lumped": 0, "delivery": 0, "joule": 0, "delivery_whole": 0, "joule_whole": 0}
    bad = []
    for r in recs.values():
        if r.get("failed"):
            continue
        for part in ("resolved", "lumped"):
            p = r.get(part)
            if p is None:
                continue
            n[part] += 1
            worst[part] = max(worst[part], abs(p["energy_residual_rel"]))
            t_end = p["t_end_s"]
            for name, E, tau in (("delivery", r["E_delivered_J"], r["tau_d_s"]), ("joule", r["E_joule_J"], r["tau"])):
                got = p["sources"].get(name, {}).get("delivered_J")
                if E > 0.0:
                    want = _triangle(E, tau, t_end)
                    n[name] += 1
                    if t_end >= tau:
                        n[name + "_whole"] += 1
                    d = abs(got / want - 1) if (got is not None and want > 0) else (0.0 if got == want else 1.0)
                    worst[name] = max(worst[name], d)
                    if d > 1e-9:
                        bad.append([r["id"], part, name, got, want])
                elif got is not None:
                    bad.append([r["id"], part, name, got, 0.0])
    ok = worst["resolved"] < 1e-9 and worst["lumped"] < 1e-9 and not bad
    return {"pass": bool(ok), "largest_relative": worst, "counts": n, "bad": bad, "n_records": len(recs)}


def main():
    import stage8_score as SC
    import stage8_run as R8
    recs = R8.load_records()
    st = R8.all_states(recs)
    scored = {t: {"C1": R8.SR.f_star(st[f"A_C1_{t}"]), "C2": R8.SR.f_star(st[f"A_C2_{t}"])} for t in V2_TESTS}
    out = {"V1": v1(), "V2": v2(scored=scored), "V4": v4()}
    try:
        out["V3"] = v3()
    except FileNotFoundError as e:
        out["V3"] = {"pass": None, "missing": str(e)}
    json.dump(out, open(os.path.join(RES, "stage8_checks.json"), "w"), indent=1, default=float)
    print(json.dumps({k: v["pass"] for k, v in out.items()}))


if __name__ == "__main__":
    main()
