#!/usr/bin/env python3
"""Stage 11's scoring (predictions_stage11.md; DECISIONS.md D113 to D116): every registered Stage 11 quantity, from the
Stage 11 records (results/stage11_runs/) and the earlier stages' files, and P1 to P6.

Writes results/stage11_draws.csv, stage11_thresholds.csv, stage11_overshoot.csv, stage11_times.csv,
stage11_bands.json and stage11_scorecard.json.
Usage: python3 stage11_score.py [--runs DIR] [--out DIR]
"""
import argparse, csv, glob, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage9_run as R9                  # noqa: E402  (unchanged)
import stage10_partc as PC               # noqa: E402  (unchanged)
import stage11_inputs as IN              # noqa: E402
import stage11_run as R                  # noqa: E402

RES = os.path.join(HERE, "..", "results")
N_PERM_E4 = 10000
SEED_E4 = 20261102


def e_e(test):
    t = R9.by_test()[test]
    return float(R9.ratios()["central"] * t["E_b_J"])


def mean_fstar(test, crit):
    s = R9.fstar8()[test][crit]
    if s["status"] == "zero":
        return {"status": "zero", "lo": 0.0, "hi": 0.0, "f": 0.0}
    return {"status": s["status"], "lo": float(s["lo"]), "hi": float(s["hi"]), "f": 0.5 * (float(s["lo"]) + float(s["hi"]))}


def draw_labels():
    """The eight draws: four kinetic (by rank) and four thermal (by property)."""
    kin = [("kin", f"d{IN.KIN_DRAWS[r]}", IN.KIN_DRAWS[r], "central") for r in IN.KIN_RANKS]
    th = [("thermal", lab, "mean", lab) for lab in IN.THERMAL_DRAWS]
    return kin + th


# ------------------------------------------------------------------------------------------------ A, B: the thresholds
def thresholds(recs, pts):
    chains = R.threshold_chains(recs, pts)
    rows = []
    for name, st in chains.items():
        f = R.fstar_value(st)
        rows.append({"chain": name, "part": st["part"], "criterion": st["crit"], "test": st["test"],
                     "draw": f"d{st['kin']}" if st["kin"] != "mean" else st["thermal"], "status": st["status"],
                     "lo": st["lo"], "hi": st["hi"], "f_star": f, "E_star_J": None if f is None else f * e_e(st["test"]),
                     "n_points": st["n_points"]})
    for test in IN.A_TESTS:
        for crit in ("C1", "C2"):
            m = mean_fstar(test, crit)
            rows.append({"chain": f"mean_{crit}_{test}", "part": "mean", "criterion": crit, "test": test, "draw": "mean",
                         "status": m["status"], "lo": m["lo"], "hi": m["hi"], "f_star": m["f"],
                         "E_star_J": m["f"] * e_e(test), "n_points": None})
    return rows


def fval(row):
    """A row's f* for the arithmetic: 0, the bracket's midpoint, infinity for a threshold above 1 (D116 (2)), or None
    for a chain that is broken or not finished."""
    if row is None:
        return None
    if row["status"] == "above":
        return math.inf
    return row["f_star"]


def jnum(x):
    """A number for the JSON files: infinity is written "above 1"."""
    return "above 1" if (isinstance(x, float) and math.isinf(x)) else x


def table(rows):
    """{(criterion, test): {draw: row}}"""
    out = {}
    for r in rows:
        out.setdefault((r["criterion"], r["test"]), {})[r["draw"]] = r
    return out


def bands(rows):
    """A2 and B2: for each test and criterion, the smallest and largest f* (and E*) over the four draws of each kind and
    the posterior mean; and the bands over the four draws alone (P5)."""
    tb = table(rows)
    kin = [d for kind, d, _, _ in draw_labels() if kind == "kin"]
    th = [d for kind, d, _, _ in draw_labels() if kind == "thermal"]
    out = {}
    for (crit, test), by in tb.items():
        e = {}
        for kind, labs in (("kinetic", kin), ("thermal", th)):
            vals = [fval(by.get(d)) for d in labs]
            ok = all(v is not None for v in vals)
            with_mean = vals + [fval(by["mean"])]
            e[kind] = {"f_star": {d: jnum(fval(by.get(d))) for d in labs},
                       "complete": ok,
                       "band_with_mean": [jnum(min(with_mean)), jnum(max(with_mean))] if ok else None,
                       "E_band_with_mean_J": [jnum(min(with_mean) * e_e(test)), jnum(max(with_mean) * e_e(test))]
                       if ok else None,
                       "band_of_draws": jnum(max(vals) - min(vals)) if ok else None,
                       "statuses": {d: by[d]["status"] if d in by else None for d in labs}}
        e["mean"] = by["mean"]["f_star"]
        out[f"{crit}_{test}"] = e
    return out


# ------------------------------------------------------------------------------------------------ C: the far face
def overshoot(recs, pts):
    """C1: the far face's peak at f = 0 for each low-maximum test and case (each thermal draw at the central contact;
    the low and high contacts at the central properties; the central case, Stage 9's A3, for reference)."""
    rows = []
    cases = [(lab, "central") for lab in IN.THERMAL_DRAWS] + [("central", "low"), ("central", "high")]
    for test in IN.C_TESTS:
        M = R9.max_meas(test)
        for thermal, h in [("central", "central")] + cases:
            if (thermal, h) == ("central", "central"):
                peak, src = _central_peak(test), "stage10_fmax_nodes.csv (Stage 7 and Stage 9 runs)"
            else:
                e = pts.get(R.pkey("mean", thermal, h, test, 0.0), {})
                peak, src = e.get("away"), e.get("full_id")
            row = {"test": test, "thermal": thermal, "contact": h, "M_C": M, "peak_f0_C": peak, "source": src,
                   "overshoot_K": None if peak is None else peak - M}
            if peak is not None:
                row["exceeds"] = peak > M
                row["f_max_zero"] = peak >= M - IN.PEAK_TOL_K
            rows.append(row)
    return rows


def _central_peak(test):
    """The far face's peak at f = 0, the posterior mean and the central properties and contact, as Stage 10's Part B
    read it from Stage 7's and Stage 9's records (`results/stage10_fmax_nodes.csv`, the away node)."""
    for r in csv.DictReader(open(os.path.join(RES, "stage10_fmax_nodes.csv"))):
        if r["test"] == test and r["node"] == "away":
            return float(r["peak_f0_C"])
    raise KeyError(test)


# ------------------------------------------------------------------------------------------------ D: the clock
def mean_crossing(test, f):
    """The lumped neighbour's crossing at the posterior mean at fraction f with the 21.39 s delivery: Stage 9's records
    at that fraction (every one that holds the lumped neighbour must agree)."""
    vals = set()
    for p in glob.glob(os.path.join(RES, "stage9_runs", f"s9_tri21_fresh_*_{test}_f{f:.9f}.json")):
        r = json.load(open(p))
        if r.get("failed") or not r.get("lumped"):
            continue
        vals.add(r["lumped"]["t_prop_s"] if r["lumped"]["propagated"] else None)
    assert len(vals) == 1, (test, f, vals)
    return vals.pop()


def times(recs, pts):
    rows = []
    for test, f in IN.D_FRACTIONS.items():
        tm = R9.t_meas(test)
        t0 = mean_crossing(test, f)
        for r in IN.KIN_RANKS:
            d = IN.KIN_DRAWS[r]
            e = pts.get(R.pkey(d, "central", "central", test, f), {})
            t = e.get("C2", "missing") if "C2" in e else "missing"
            row = {"test": test, "f": f, "status9": IN.D_STATUS9.get(test, "matched"), "draw": f"d{d}", "rank": r,
                   "t_measured_s": tm, "t_mean_s": t0, "t_draw_s": None if t == "missing" else t,
                   "recorded": t != "missing"}
            if row["recorded"]:
                row["crossed"] = t is not None
                row["shift_from_mean_s"] = None if (t is None or t0 is None) else t - t0
                row["shift_from_measured_s"] = None if t is None else t - tm
                row["within_10_s"] = t is not None and abs(t - tm) <= IN.D_WITHIN_S[0]
                row["within_60_s"] = t is not None and abs(t - tm) <= IN.D_WITHIN_S[1]
            rows.append(row)
    return rows


def time_counts(trows):
    out = {}
    for d in sorted({r["draw"] for r in trows}):
        rs = [r for r in trows if r["draw"] == d]
        done = all(r["recorded"] for r in rs)
        out[d] = {"complete": done, "within_10_s": sum(bool(r.get("within_10_s")) for r in rs) if done else None,
                  "within_60_s": sum(bool(r.get("within_60_s")) for r in rs) if done else None,
                  "no_crossing": [r["test"] for r in rs if r["recorded"] and not r["crossed"]]}
    mean = [(t, abs(mean_crossing(t, f) - R9.t_meas(t)) if mean_crossing(t, f) is not None else None)
            for t, f in IN.D_FRACTIONS.items()]
    out["mean"] = {"complete": True, "within_10_s": sum(1 for _, x in mean if x is not None and x <= IN.D_WITHIN_S[0]),
                   "within_60_s": sum(1 for _, x in mean if x is not None and x <= IN.D_WITHIN_S[1])}
    return out


# ------------------------------------------------------------------------------------------------ E: arithmetic
def e1(rows, crit):
    """E1: under each draw, the range of E* across the four tests; the largest band of E* within any test across the
    eight draws and the mean; their ratio."""
    tb = table(rows)
    labs = [d for _, d, _, _ in draw_labels()]
    def ev(t, d):
        f = fval(tb[(crit, t)].get(d))
        return None if f is None else f * e_e(t)
    E = {t: {d: ev(t, d) for d in labs + ["mean"]} for t in IN.A_TESTS}
    complete = all(v is not None for t in E for v in E[t].values())
    out = {"criterion": crit, "E_star_J": {t: {d: jnum(v) for d, v in E[t].items()} for t in E}, "complete": complete}
    if not complete:
        out["missing"] = [(t, d) for t in E for d, v in E[t].items() if v is None]
        return out
    band = {t: max(E[t].values()) - min(E[t].values()) for t in IN.A_TESTS}
    largest = max(band.values())
    rng = {d: max(E[t][d] for t in IN.A_TESTS) - min(E[t][d] for t in IN.A_TESTS) for d in labs + ["mean"]}
    ratio = {d: (rng[d] / largest if (largest > 0 and not math.isinf(largest)) else None) for d in rng}
    out.update({"within_test_band_J": {t: jnum(v) for t, v in band.items()}, "largest_within_test_band_J": jnum(largest),
                "largest_band_test": max(band, key=band.get), "range_across_tests_J": {d: jnum(v) for d, v in rng.items()},
                "ratio_range_to_band": ratio, "_band": largest, "_range": rng})
    return out


def e2(rows, crit):
    """E2: the largest within-test factor of f* across the eight draws and the mean (the largest over the smallest
    non-zero value, per test), against Stage 10 C3's spread of the fractions read from the tests: its share, as the ratio of
    the logarithms."""
    tb = table(rows)
    labs = [d for _, d, _, _ in draw_labels()] + ["mean"]
    fac = {}
    for t in IN.A_TESTS:
        v = [fval(tb[(crit, t)].get(d)) for d in labs]
        nz = [x for x in v if x is not None and x > 0 and not math.isinf(x)]
        fac[t] = {"n_nonzero": len(nz), "n_zero": sum(1 for x in v if x == 0.0), "n_missing": sum(1 for x in v if x is None),
                  "n_above_1": sum(1 for x in v if x is not None and math.isinf(x)),
                  "factor": (max(nz) / min(nz)) if nz else None}       # one non-zero value: 1.0 (D119 (8))
    known = {t: x["factor"] for t, x in fac.items() if x["factor"] is not None}
    W = max(known.values()) if known else None
    sp = json.load(open(os.path.join(RES, "stage10_rank.json")))["spread"]
    S = {k: v["ratio_largest_to_smallest_nonzero"] for k, v in sp.items() if k.startswith(crit + "_")}
    share = {k: (math.log(W) / math.log(s) if (W is not None and s > 1) else None) for k, s in S.items()}
    return {"criterion": crit, "per_test": fac, "largest_factor": W,
            "largest_factor_test": max(known, key=known.get) if known else None,
            "stage10_spread": S, "share_of_log_spread": share}


def e4():
    """E4: Spearman's rho of the trigger's body energy with the outcome (16 tests) and with the measured time (9), with
    Stage 10's permutation p-value (10,000 relabellings, seed 20261102), beside the model quantities' rho with it (Stage
    10's rank file)."""
    import numpy as np
    rows = json.load(open(os.path.join(RES, "stage10_heldout.json")))["table"]
    rng = np.random.default_rng(SEED_E4)
    E = [r["E_b_J"] for r in rows]
    rho_y, p_y = PC.perm_spearman(E, [r["y"] for r in rows], rng, N_PERM_E4)
    prop = [r for r in rows if r["y"]]
    rho_t, p_t = PC.perm_spearman([r["E_b_J"] for r in prop], [r["time_s"] for r in prop], rng, N_PERM_E4)
    rk = json.load(open(os.path.join(RES, "stage10_rank.json")))["quantities"]
    return {"n_perm": N_PERM_E4, "seed": SEED_E4, "E_b_outcome": {"rho": rho_y, "p": p_y, "n": len(rows)},
            "E_b_time": {"rho": rho_t, "p": p_t, "n": len(prop)},
            "model_quantities_rho_with_E_b": {q: v["E_b"]["rho"] for q, v in rk.items() if "E_b" in v},
            "model_quantities_p_with_E_b": {q: v["E_b"]["p"] for q, v in rk.items() if "E_b" in v}}


# ------------------------------------------------------------------------------------------------ the scorecard
def _num(x):
    return math.inf if x == "above 1" else x


def within_factor(x, m):
    """P1 and P2's test for one draw: within a factor of two of the posterior-mean value, or within 0.025 of it where
    that value is 0 (D116 (1))."""
    if x is None or math.isinf(x):
        return False
    if m == 0.0:
        return abs(x) <= IN.P1_ZERO_TOL + 1e-12
    return m / IN.P1_FACTOR - 1e-12 <= x <= m * IN.P1_FACTOR + 1e-12


def scorecard(rows, orows, trows, B, E1c2):
    tb = table(rows)
    kin = [f"d{IN.KIN_DRAWS[r]}" for r in IN.KIN_RANKS]
    th = list(IN.THERMAL_DRAWS)
    P = {}
    for name, crit, exp in (("P1", "C2", "likely"), ("P2", "C1", "uncertain")):
        det = {}
        for t in IN.A_TESTS:
            m = tb[(crit, t)]["mean"]["f_star"]
            det[t] = {d: {"f_star": jnum(fval(tb[(crit, t)].get(d))), "within": within_factor(fval(tb[(crit, t)].get(d)), m)}
                      for d in kin}
            det[t]["mean"] = m
        complete = all(fval(tb[(crit, t)].get(d)) is not None for t in IN.A_TESTS for d in kin)
        holds = all(det[t][d]["within"] for t in IN.A_TESTS for d in kin)
        P[name] = {"criterion": crit, "holds": holds if complete else None, "detail": det, "expectation": exp}
    P["P3"] = {"holds": (all(E1c2["_range"][d] > E1c2["_band"] for d in kin + th) if E1c2.get("complete") else None),
               "range_across_tests_J": E1c2.get("range_across_tests_J"),
               "largest_within_test_band_J": E1c2.get("largest_within_test_band_J"),
               "largest_band_test": E1c2.get("largest_band_test"), "expectation": "likely"}
    zero_tests = [t for t in IN.C_TESTS if t != IN.FMAX_TEST]
    det = {}
    ok_all, complete = True, True
    for t in zero_tests:
        rs = {(r["thermal"], r["contact"]): r for r in orows if r["test"] == t}
        draws = [rs[(lab, "central")].get("exceeds") for lab in th]
        lowc, highc = rs[("central", "low")].get("exceeds"), rs[("central", "high")].get("exceeds")
        if any(x is None for x in draws + [lowc, highc]):
            complete = False
        n = sum(1 for x in draws if x)
        ok = n >= 3 and bool(lowc) and bool(highc)
        det[t] = {"draws_exceeding": n, "low_contact_exceeds": lowc, "high_contact_exceeds": highc, "holds": ok}
        ok_all = ok_all and ok
    P["P4"] = {"holds": ok_all if complete else (False if not ok_all and _p4_decided(det) else None), "detail": det,
               "expectation": "uncertain"}
    det = {}
    for t in IN.A_TESTS:
        bk, bt = _num(B[f"C2_{t}"]["kinetic"]["band_of_draws"]), _num(B[f"C2_{t}"]["thermal"]["band_of_draws"])
        det[t] = {"band_kinetic": jnum(bk), "band_thermal": jnum(bt),
                  "narrower": (bt < bk - 1e-12 if not math.isinf(bk) else not math.isinf(bt)) if None not in (bk, bt) else None}
    P["P5"] = {"holds": all(det[t]["narrower"] for t in IN.A_TESTS) if all(det[t]["narrower"] is not None
                                                                         for t in IN.A_TESTS) else None,
               "detail": det, "expectation": "uncertain"}
    six = [t for t in IN.D_FRACTIONS if t not in IN.D_STATUS9 or IN.D_STATUS9[t] == "bracketed"]
    det = {}
    for t in six:
        rs = [r for r in trows if r["test"] == t]
        moved = [r["draw"] for r in rs if r["recorded"] and (not r["crossed"] or abs(r["shift_from_mean_s"]) > 60.0)]
        det[t] = {"draws_moving": moved, "complete": all(r["recorded"] for r in rs)}
    n = sum(1 for t in six if det[t]["draws_moving"])
    complete = all(det[t]["complete"] for t in six)
    P["P6"] = {"holds": (n >= 2) if complete else (True if n >= 2 else None), "tests_moving": n, "detail": det,
               "six": six, "expectation": "likely"}
    return P


def _p4_decided(det):
    """P4 is decided before every run is in where one test already fails on a reading that is in."""
    return any(d["low_contact_exceeds"] is False or d["high_contact_exceeds"] is False for d in det.values())


# ------------------------------------------------------------------------------------------------ main
def write_csv(path, rows, fields=None):
    fields = fields or sorted({k for r in rows for k in r})
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in fields})


def draws_rows():
    per = {int(r["draw"]): r for r in csv.DictReader(open(os.path.join(RES, "stage3a_per_draw.csv")))}
    out = []
    for rank in IN.KIN_RANKS:
        d = IN.KIN_DRAWS[rank]
        ae, sep, cat = IN.KIN_COLUMNS[d]
        out.append({"kind": "kinetic", "label": f"d{d}", "stage3_draw": d, "rank": rank,
                    "headline_hottest_onset_s": float(per[d]["headline_hottest_onset_s"]),
                    "an_ele_column": ae, "separator_column": sep, "ncm811_column": cat})
    for lab, p in IN.thermal_draws().items():
        out.append({"kind": "thermal", "label": lab, "stage3_draw": p["thermal_draw"], "k_radial_W_mK": p["k_radial"],
                    "k_axial_W_mK": p["k_axial"], "c_roll_J_kgK": p["c_roll"], "C_cell_J_K": p["C_cell"]})
    return out


def main(runs_dir=None, out=RES):
    recs = R.load_records(runs_dir)
    pts = R.points(recs)
    rows = thresholds(recs, pts)
    B = bands(rows)
    orows = overshoot(recs, pts)
    trows = times(recs, pts)
    fm = R.fmax_chains(recs, pts)
    e3 = R.e3_cases(recs, pts)
    E1 = {"C2": e1(rows, "C2"), "C1": e1(rows, "C1")}
    E2 = {"C2": e2(rows, "C2"), "C1": e2(rows, "C1")}
    E4 = e4()
    card = scorecard(rows, orows, trows, B, E1["C2"])
    write_csv(os.path.join(out, "stage11_draws.csv"), draws_rows(),
              ["kind", "label", "stage3_draw", "rank", "headline_hottest_onset_s", "an_ele_column", "separator_column",
               "ncm811_column", "k_radial_W_mK", "k_axial_W_mK", "c_roll_J_kgK", "C_cell_J_K"])
    write_csv(os.path.join(out, "stage11_thresholds.csv"), rows,
              ["chain", "part", "criterion", "test", "draw", "status", "lo", "hi", "f_star", "E_star_J", "n_points"])
    write_csv(os.path.join(out, "stage11_overshoot.csv"), orows,
              ["test", "thermal", "contact", "M_C", "peak_f0_C", "overshoot_K", "exceeds", "f_max_zero", "source"])
    write_csv(os.path.join(out, "stage11_times.csv"), trows,
              ["test", "f", "status9", "draw", "rank", "t_measured_s", "t_mean_s", "t_draw_s", "recorded", "crossed",
               "shift_from_mean_s", "shift_from_measured_s", "within_10_s", "within_60_s"])
    bands_out = {"A2_B2": B, "C2_fmax": {k: {kk: v.get(kk) for kk in ("status", "f_max", "lo", "hi", "f_run", "p_run",
                                                                        "M", "f_up", "thermal", "h")}
                                         for k, v in fm.items()},
                 "D2_counts": time_counts(trows),
                 "E1": {c: {k: v for k, v in x.items() if not k.startswith("_")} for c, x in E1.items()},
                 "E2": E2, "E3": e3, "E4": E4,
                 "records": len(recs), "failed": sum(1 for r in recs.values() if r.get("failed"))}
    json.dump(bands_out, open(os.path.join(out, "stage11_bands.json"), "w"), indent=1, default=float)
    verdicts = {k: ("held" if v["holds"] else "failed") if v["holds"] is not None else "open" for k, v in card.items()}
    json.dump({"verdicts": verdicts, "predictions": card}, open(os.path.join(out, "stage11_scorecard.json"), "w"),
              indent=1, default=float)
    print(json.dumps(verdicts))
    return verdicts


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default=None)
    ap.add_argument("--out", default=RES)
    a = ap.parse_args()
    main(a.runs, a.out)
