#!/usr/bin/env python3
"""Stage 11's checks (brief; DECISIONS.md D116 (4)), written before the predictions:
  V1  the draw selection of A0.1 and A0.2 reproduced from Stage 3's files by separate code: the kinetic ranks from
      Stage 3a's per-case onsets (not its per-draw summary), the thermal extremes with numpy;
  V2  the energy accounts of every Stage 11 record, under 1e-9 of the heat taken in, and every delivery exact to the
      run's end (Stage 9's V4, `stage9_checks.v4`, unchanged);
  V3  Part E recomputed by separate code from the run records (its own reading of the records, its own brackets, the
      ejected energies from Stage 8's file, scipy's Spearman), agreeing with the scoring to 1e-10;
  V4  the three earlier records that Stage 11's V4 runs repeat at the posterior mean on the laptop: the crossings and
      peaks within 1e-6 s and 1e-6 K, and every history they share within 1e-6 K.
Writes results/stage11_checks.json."""
import csv, glob, json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage9_checks as C9               # noqa: E402  (unchanged)
import stage11_inputs as IN              # noqa: E402

RES = os.path.join(HERE, "..", "results")
RUNS = os.path.join(RES, "stage11_runs")
SERIES = os.path.join(RES, "stage11_series")
TOL = 1e-10


# ------------------------------------------------------------------------------------------------ V1
def v1():
    rows = [r for r in csv.DictReader(open(os.path.join(RES, "stage3a_onsets.csv")))
            if r["case"] == IN.HEADLINE_CASE and r["history"] == "hottest_node"]
    d = np.array([int(r["draw"]) for r in rows])
    t = np.array([float(r["t_0.15Kpm_s"]) for r in rows])
    order = np.lexsort((d, t))
    kin = {int(rank): int(d[order[rank - 1]]) for rank in IN.KIN_RANKS}
    cols = {int(r["draw"]): (int(r["an_ele_column"]), int(r["separator_column"]), int(r["ncm811_column"])) for r in rows}
    T = np.genfromtxt(os.path.join(RES, "stage3_thermal_draws.csv"), delimiter=",", names=True)
    th = {"kr_min": int(T["thermal_draw"][np.argmin(T["k_radial_W_per_mK"])]),
          "kr_max": int(T["thermal_draw"][np.argmax(T["k_radial_W_per_mK"])]),
          "c_min": int(T["thermal_draw"][np.argmin(T["c_roll_J_per_kgK"])]),
          "c_max": int(T["thermal_draw"][np.argmax(T["c_roll_J_per_kgK"])])}
    ok = (kin == {int(k): int(v) for k, v in IN.KIN_DRAWS.items()} and th == IN.THERMAL_DRAWS
          and all(cols[v] == IN.KIN_COLUMNS[v] for v in kin.values()) and len(rows) == 200)
    return {"pass": bool(ok), "kinetic": kin, "thermal": th,
            "onsets_s": {str(v): float(t[d == v][0]) for v in kin.values()}}


# ------------------------------------------------------------------------------------------------ V3's own reading
def _records():
    out = []
    for p in glob.glob(os.path.join(RUNS, "s11_*.json")):
        r = json.load(open(p))
        if not r.get("failed"):
            out.append(r)
    return out


def _e_e():
    return {r["id"]: float(r["E_e_J"]) for r in csv.DictReader(open(os.path.join(RES, "stage8_ejected.csv")))
            if r["kind"] == "test"}


def _stage8(test, crit):
    r = [x for x in csv.DictReader(open(os.path.join(RES, "stage8_thresholds.csv"))) if x["test"] == test][0]
    lo, hi = float(r[f"f{crit}_lo"]), float(r[f"f{crit}_hi"])
    return 0.5 * (lo + hi) if hi > 0 else 0.0


def _fstar(recs, test, crit, kin, thermal):
    part = "resolved" if crit == "C1" else "lumped"
    pts = {}
    for r in recs:
        if (str(r["kin"]) == str(kin) and r["thermal"] == thermal and r["h"] == "central" and r["test"] == test
                and r.get(part)):
            pts[round(r["f"], 12)] = bool(r[part]["propagated"])
    met = [f for f, m in pts.items() if m]
    no = [f for f, m in pts.items() if not m]
    if met and min(met) == 0.0:
        return 0.0
    if not met:
        return math.inf if (no and max(no) >= 1.0 - 1e-12) else None
    lo, hi = max(no), min(met)
    return 0.5 * (lo + hi) if hi - lo <= IN.WIDTH + 1e-12 else None


def _num(x):
    return math.inf if x == "above 1" else x


def v3(bands):
    recs = _records()
    ee = _e_e()
    draws = [(IN.KIN_DRAWS[r], "central", f"d{IN.KIN_DRAWS[r]}") for r in IN.KIN_RANKS] + \
            [("mean", lab, lab) for lab in IN.THERMAL_DRAWS]
    worst, bad = 0.0, []

    def cmp(name, a, b):
        nonlocal worst
        a, b = _num(a), _num(b)
        if a is None or b is None or (isinstance(a, float) and math.isinf(a)) or (isinstance(b, float) and math.isinf(b)):
            if a != b:
                bad.append((name, a, b))
            return
        d = abs(float(a) - float(b))
        worst = max(worst, d / max(1.0, abs(float(b))))
        if d > TOL * max(1.0, abs(float(b))):
            bad.append((name, a, b))

    for crit in ("C2", "C1"):
        E = {}
        for t in IN.A_TESTS:
            E[t] = {lab: (lambda f: None if f is None else f * ee[t])(_fstar(recs, t, crit, k, th)) for k, th, lab in draws}
            E[t]["mean"] = _stage8(t, crit) * ee[t]
        b = bands["E1"][crit]
        if any(v is None for t in E for v in E[t].values()):
            cmp(f"E1 {crit} complete", False, b["complete"])
            continue
        band = {t: max(E[t].values()) - min(E[t].values()) for t in E}
        rng = {lab: max(E[t][lab] for t in E) - min(E[t][lab] for t in E) for lab in list(E[IN.A_TESTS[0]])}
        cmp(f"E1 {crit} band", max(band.values()), b["largest_within_test_band_J"])
        for lab, v in rng.items():
            cmp(f"E1 {crit} range {lab}", v, b["range_across_tests_J"][lab])
        for t in E:
            for lab, v in E[t].items():
                cmp(f"E1 {crit} E* {t} {lab}", v, b["E_star_J"][t][lab])
        # E2
        fac = {}
        for t in E:
            nz = [v / ee[t] for v in E[t].values() if v > 0 and not math.isinf(v)]
            if len(nz) >= 2:
                fac[t] = max(nz) / min(nz)
        W = max(fac.values()) if fac else None
        cmp(f"E2 {crit} largest factor", W, bands["E2"][crit]["largest_factor"])
        sp = json.load(open(os.path.join(RES, "stage10_rank.json")))["spread"]
        for k, v in sp.items():
            if k.startswith(crit + "_"):
                s = v["ratio_largest_to_smallest_nonzero"]
                cmp(f"E2 {crit} share {k}", math.log(W) / math.log(s) if (W is not None and s > 1) else None,
                    bands["E2"][crit]["share_of_log_spread"][k])
    # E4: scipy's Spearman, the same relabellings
    from scipy.stats import spearmanr
    rows = json.load(open(os.path.join(RES, "stage10_heldout.json")))["table"]
    rng_ = np.random.default_rng(bands["E4"]["seed"])

    def perm(a, b_):
        obs = spearmanr(a, b_)[0]
        cnt = 0
        for _ in range(bands["E4"]["n_perm"]):
            idx = rng_.permutation(len(b_))
            if abs(spearmanr(a, [b_[i] for i in idx])[0]) >= abs(obs) - 1e-12:
                cnt += 1
        return float(obs), (1 + cnt) / (1 + bands["E4"]["n_perm"])
    ry, py = perm([r["E_b_J"] for r in rows], [r["y"] for r in rows])
    prop = [r for r in rows if r["y"]]
    rt, pt = perm([r["E_b_J"] for r in prop], [r["time_s"] for r in prop])
    cmp("E4 rho outcome", ry, bands["E4"]["E_b_outcome"]["rho"])
    cmp("E4 p outcome", py, bands["E4"]["E_b_outcome"]["p"])
    cmp("E4 rho time", rt, bands["E4"]["E_b_time"]["rho"])
    cmp("E4 p time", pt, bands["E4"]["E_b_time"]["p"])
    # E3: each case's verdict from the far face's peaks
    s7 = {}
    for p in glob.glob(os.path.join(RES, "stage7_runs", "pertest_*_h*_gcentral_tau21.39_*.json")):
        b_ = os.path.basename(p)
        if "_aged" in b_:
            continue
        r = json.load(open(p))["resolved"]
        for t in IN.C_TESTS:
            for h in ("low", "high"):
                if b_.startswith(f"pertest_{t}_") and f"_h{h}_" in b_ and r["t_end_s"] >= 900.0 - 1e-9:
                    s7[(t, h)] = r["probe_peak"]["away"]["T_C"]
    meas = {r["test"]: float(r["M_C"]) for r in csv.DictReader(open(os.path.join(RES, "stage9_fractions.csv")))}
    for case, c in bands["E3"].items():
        th, h = c["thermal"], c["h"]
        for t in IN.C_TESTS:
            full = [r for r in recs if r["test"] == t and r["thermal"] == th and r["h"] == h and str(r["kin"]) == "mean"
                    and r.get("resolved") and r["resolved"]["t_end_s"] >= 900.0 - 1e-9]
            p0 = [r["resolved"]["probe_peak"]["away"]["T_C"] for r in full if r["f"] == 0.0] or \
                 ([s7[(t, h)]] if (th == "central" and (t, h) in s7) else [])
            if p0 and p0[0] >= meas[t] - IN.PEAK_TOL_K and c["per_test"][t] != "zero":
                bad.append((f"E3 {case} {t}", "zero", c["per_test"][t]))
    return {"pass": not bad and worst <= TOL, "largest_relative_difference": worst, "disagreeing": bad[:20],
            "compared": "E1, E2, E3 (zeros), E4"}


# ------------------------------------------------------------------------------------------------ V4
def v4_repeats():
    import stage11_run as R
    out = {}
    ok_all = True
    for test, f, models, stop, (d, rid) in R.V4_REPEATS:
        sp = R.spec("V4", test, f, "mean", "central", "central", models, stop)
        a = C9._load(d, rid)
        bp = os.path.join(RUNS, sp["id"] + ".json")
        if a is None or not os.path.exists(bp):
            out[rid] = {"status": "missing"}
            ok_all = False
            continue
        b = json.load(open(bp))
        res = {"repeat": sp["id"], "machine": b.get("machine", {}).get("label")}
        ok = True
        for part in ("resolved", "lumped"):
            pa, pb = a.get(part), b.get(part)
            if pa is None or pb is None:
                continue
            same = pa["propagated"] == pb["propagated"]
            dt = abs((pa.get("t_prop_s") or 0.0) - (pb.get("t_prop_s") or 0.0))
            pk = "peak_hottest_C" if part == "resolved" else "peak_C"
            dp = abs(pa[pk] - pb[pk])
            res[part] = {"same_outcome": same, "crossing_diff_s": dt, "peak_diff_K": dp}
            ok &= same and dt <= 1e-6 and dp <= 1e-6
            if part == "resolved":
                for pr in ("toward", "away"):
                    dd = abs(pa["probe_peak"][pr]["T_C"] - pb["probe_peak"][pr]["T_C"])
                    res[part][f"{pr}_peak_diff_K"] = dd
                    ok &= dd <= 1e-6
        sa = C9._series(d, rid)
        sb = np.load(os.path.join(SERIES, sp["id"] + ".npz")) if os.path.exists(os.path.join(SERIES, sp["id"] + ".npz")) else None
        if sa is not None and sb is not None:
            worst = 0.0
            for k in sa.files:
                if k in sb.files and k not in ("imax",):
                    n = min(len(sa[k]), len(sb[k]))
                    if n:
                        worst = max(worst, float(np.max(np.abs(sa[k][:n] - sb[k][:n]))))
            res["series_largest_diff"] = worst
            ok &= worst <= 1e-6
        res["pass"] = bool(ok)
        ok_all &= ok
        out[rid] = res
    return {"pass": bool(ok_all), "runs": out}


def main():
    import stage11_run as R
    recs = R.load_records()
    out = {"V1": v1(), "V2": C9.v4(recs)}
    bp = os.path.join(RES, "stage11_bands.json")
    if os.path.exists(bp):
        out["V3"] = v3(json.load(open(bp)))
    out["V4"] = v4_repeats()
    json.dump(out, open(os.path.join(RES, "stage11_checks.json"), "w"), indent=1, default=float)
    print(json.dumps({k: v.get("pass") for k, v in out.items()}))


if __name__ == "__main__":
    main()
