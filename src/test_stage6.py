#!/usr/bin/env python3
"""Tests of the Stage 6 code on synthetic inputs only, run before the predictions (DECISIONS.md D56 (4)).

Nothing here integrates the model in the Stage 6 configuration or reads a Stage 5 record or series: the histories
are piecewise linear, so that the interpolated crossings are exact; the cell-1 peak of the trigger step and of V2
is replaced by a synthetic function of the energy and the duration; the runs of the work loop are replaced by
synthetic records. Every file is written to a temporary folder.
Usage: python3 test_stage6.py
"""
import csv, json, os, shutil, subprocess, sys, tempfile
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage6_inputs as IN
import stage6_crossings as CR
import stage6_run as S6
import stage6_score as SC
import stage6_checks as CK
import v12_run as RUN

K0 = 273.15
TA = 25.0 + K0


def ramp(t_peak, T_peak_C, t_end=900.0, dt=0.1, fall=0.2):
    """Rises linearly from 25 C to T_peak_C at t_peak, then falls at `fall` K/s; samples every dt."""
    t = np.round(np.arange(0.0, t_end + 1e-9, dt), 10)
    up = TA + (T_peak_C + K0 - TA) * t / t_peak
    down = T_peak_C + K0 - fall * (t - t_peak)
    return t, np.where(t <= t_peak, up, np.maximum(down, TA))


def exact_cross(t_peak, T_peak_C, level=150.0):
    return None if T_peak_C < level else (level - 25.0) / (T_peak_C - 25.0) * t_peak


def synth(spec, hot=(30.0, 190.0), mean=(250.0, 140.0), away=(300.0, 134.0), toward=(30.0, 189.5),
          lumped=(260.0, 160.0), T1=530.0, prop=None, lprop=None):
    """A record and series of the shape v12_run.run_one returns."""
    t, Th = ramp(*hot)
    _, Tm = ramp(*mean)
    pt, Ta_ = ramp(*away, dt=0.05)
    _, Tt = ramp(*toward, dt=0.05)
    tl, Tl = ramp(*lumped)
    if prop is not None:                                    # the resolved run stops at the hot spot's crossing
        keep, keep_p = t <= prop, pt <= prop
        t, Th, Tm = t[keep], Th[keep], Tm[keep]
        pt, Ta_, Tt = pt[keep_p], Ta_[keep_p], Tt[keep_p]
    if lprop is not None:
        keep = tl <= lprop
        tl, Tl = tl[keep], Tl[keep]
    series = {"t": t, "T1": np.full(t.size, 400.0), "Tmax": Th, "Tmean": Tm, "imax": np.zeros(t.size, int),
              "probe_t": pt, "probe_toward": Tt, "probe_away": Ta_, "t_lumped": tl, "T_lumped": Tl,
              "t1_t": np.array([0.0, 1.0]), "t1_T1_C": np.array([25.0, T1]), "t1_T2_C": np.array([25.0, 25.0])}
    res = {"propagated": prop is not None, "t_end_s": float(t[-1]), "steps": 9000, "rejected": 0,
           "max_implicit_nodes": 0, "energy_residual_rel": 1e-12, "peak_hottest_C": float(Th.max() - K0),
           "t_peak_hottest_s": float(t[int(np.argmax(Th))]), "peak_mean_C": float(Tm.max() - K0),
           "probe_peak": {"toward": {"T_C": float(Tt.max() - K0), "t_s": float(pt[int(np.argmax(Tt))])},
                          "away": {"T_C": float(Ta_.max() - K0), "t_s": float(pt[int(np.argmax(Ta_))])}},
           "in_rxn_J": 100.0, "cross_s": {}}
    if prop is not None:
        res.update({"t_prop_s": prop, "where": {"r_mm": 10.55, "theta_deg": 0.0, "z_mm": 35.0}})
    lres = {"propagated": lprop is not None, "peak_C": float(Tl.max() - K0), "t_peak_s": float(tl[int(np.argmax(Tl))]),
            "reaction_heat_J": 200.0, "t_end_s": float(tl[-1])}
    if lprop is not None:
        lres["t_prop_s"] = lprop
    rec = dict(spec)
    rec.update({"draw": {"draw": spec["kin"]} if spec["kin"] != "mean" else None, "T1max_C": T1, "t_T1max_s": spec["tau"],
                "n_nodes": 19355, "resolved": res, "lumped": lres, "wall_s": 1.0})
    return rec, series


def check(cond, what):
    if not cond:
        raise AssertionError(what)
    print("ok  ", what)


def test_crossings():
    t, y = ramp(40.0, 190.0)
    tc = CR.first_crossing(t, y, 150.0 + K0)
    check(abs(tc - exact_cross(40.0, 190.0)) < 1e-9, "first crossing exact on a linear rise")
    tr = CR.return_below(t, y, 150.0 + K0, tc)
    check(abs(tr - (40.0 + 40.0 / 0.2)) < 1e-9, "return below exact on a linear fall")
    check(CR.first_crossing(*ramp(40.0, 140.0), 150.0 + K0) is None, "no crossing below the level")
    spec = {"id": "x", "set": "grid", "kin": "mean", "connection": "series", "h": "central", "g": "central",
            "tau": 30.0, "E_body_J": 1.0, "T_amb_K": TA, "refine": 1.0, "dt_scale": 1.0}
    rec, s = synth(spec)
    q = CR.a1(rec, s)
    check(q["hot"]["crosses"] and abs(q["hot"]["t_cross_s"] - exact_cross(30.0, 190.0)) < 1e-9, "a1: hot spot")
    check(abs(q["lumped"]["t_cross_s"] - exact_cross(260.0, 160.0)) < 1e-9, "a1: lumped")
    check(not q["away"]["crosses"] and q["away"]["t_cross_s"] is None, "a1: face away below 150 C")
    check(abs(q["mean"]["t_peak_s"] - 250.0) < 1e-9 and q["mean"]["peak_C"] == rec["resolved"]["peak_mean_C"],
          "a1: the mean's peak time from the series, its value from the record")
    q2 = CR.a1(rec, None)
    check(q2["hot"]["crosses"] and q2["hot"]["t_cross_s"] is None and q2["mean"]["t_peak_s"] is None,
          "a1 without series: status only")


def grid_specs():
    out = []
    for conn in ("series", "parallel"):
        for tau in (10.0, 30.0):
            for h in ("low", "central", "high"):
                for g in ("low", "central", "high"):
                    out.append({"id": f"grid_mean_{conn}_h{h}_g{g}_tau{int(tau)}", "set": "grid", "kin": "mean",
                                "connection": conn, "h": h, "g": g, "tau": tau, "E_body_J": 33222.9, "T_amb_K": TA,
                                "refine": 1.0, "dt_scale": 1.0})
    return out


def write_stage5(res):
    """36 synthetic grid records with series and 10 synthetic fact records without."""
    os.makedirs(os.path.join(res, "v12_runs"))
    os.makedirs(os.path.join(res, "v12_series"))
    peaks = {"low": (115.0, 100.0, 108.0), "central": (192.0, 134.0, 160.0), "high": (226.0, 142.0, 177.0)}
    t_lum = {"low": 380.0, "central": 260.0, "high": 230.0}
    for s in grid_specs():
        hot, away, lum = peaks[s["h"]]
        rec, ser = synth(s, hot=(28.0 if s["tau"] == 10 else 40.0, hot), toward=(28.0, hot - 0.3),
                         away=(310.0, away), lumped=(t_lum[s["h"]], lum), mean=(260.0, lum - 20))
        json.dump(rec, open(os.path.join(res, "v12_runs", s["id"] + ".json"), "w"), default=float)
        np.savez_compressed(os.path.join(res, "v12_series", s["id"] + ".npz"), **ser)
    for k in range(10):
        s = dict(grid_specs()[k], id=f"fact_d{k + 1:03d}_x", set="fact", kin=k + 1)
        rec, _ = synth(s, away=(300.0, 130.0 + k))
        json.dump(rec, open(os.path.join(res, "v12_runs", s["id"] + ".json"), "w"), default=float)


def test_part_a(res):
    write_stage5(res)
    out = CR.main(os.path.join(res, "v12_runs"), os.path.join(res, "v12_series"), res)
    rows = list(csv.DictReader(open(os.path.join(res, "stage6_crossings.csv"))))
    check(len(rows) == 46 and out["n_with_series"] == 36, "Part A: one row per record, series for the grid")
    g = out["a3_counts_with_series"]["grid"]["all"]
    check(g["lumped"]["cross"] == 24 and g["lumped"]["none"] == 12, "Part A: lumped crossings counted")
    exp_c = exact_cross(260.0, 160.0)
    check(g["lumped"]["inside"] == 12 * (147 <= exp_c <= 342) + 12 * (147 <= exact_cross(230.0, 177.0) <= 342),
          "Part A: window counts")
    sc = SC.score_part_a(SC.part_a_rows(res))
    check(sc["P1"]["lumped"]["crossing"] == 24 and sc["P1"]["hot"]["crossing"] == 24, "P1 counts")
    check(sc["P2"]["n"] == 46, "P2 counts every record")
    return out


def fake_peak(e, tau, connection, h="central", g="central"):
    """A synthetic cell-1 peak, monotonic in the energy (no model)."""
    return 25.0 + 0.0155 * e - 0.6 * tau + (0.4 if connection == "series" else 0.0), tau


def test_trigger_and_runs(res):
    real = S6.t1_peak
    S6.t1_peak = fake_peak
    try:
        tr = S6.trigger(path=os.path.join(res, "stage6_trigger.json"))
    finally:
        S6.t1_peak = real
    ce = tr["central_matched_case"]
    check(ce["energy"] == "body", "selection: the synthetic body energy qualifies, the total does not")
    pk = tr["peak_matched_exploratory"]
    check(abs(fake_peak(pk["E_J"], tr["levels"]["tau_median_s"], "series")[0] - 704.5) <= 0.01,
          "peak-matched energy by bisection")
    runs = S6.build_runs(ce["E_J"], pk["E_J"])
    n = {s: sum(r["set"] == s for r in runs) for s in S6.SETS}
    check(n == {"v3": 4, "body": 42, "total": 42, "bracket": 4, "peak": 14, "draws": 400}, f"run list {n}")
    check(len({r["id"] for r in runs}) == len(runs), "run ids unique")
    check([r["set"] for r in runs][:4] == ["v3"] * 4 and runs[-1]["set"] == "draws", "run order")
    reg = S6.build_runs(ce["E_J"], None)
    check(S6.runs_hash(S6.registered(runs)) == S6.runs_hash(reg), "registered list independent of the peak set")
    return tr, runs


def test_work(res, tr, runs):
    saved = (S6.RUNS, S6.SERIES, S6.TRIGGER, S6.STOP_FILE, RUN.run_one, S6.build_runs)
    S6.RUNS, S6.SERIES = os.path.join(res, "stage6_runs"), os.path.join(res, "stage6_series")
    S6.TRIGGER, S6.STOP_FILE = os.path.join(res, "stage6_trigger.json"), os.path.join(res, "stage6_STOP")
    ce, pk = tr["central_matched_case"]["E_J"], tr["peak_matched_exploratory"]["E_J"]

    def fake_run(spec, ctx, keep_series):
        e = spec["E_body_J"]
        reach = e > 60000.0                                     # synthetic: only the large energies reach 255.7 C
        hot = (30.0, 300.0 if reach else 190.0)
        rec, s = synth(spec, hot=hot, toward=(30.0, hot[1] - 0.3), T1=fake_peak(e, spec["tau"], spec["connection"])[0],
                       prop=(30.0 * (255.68 - 25) / (300 - 25)) if reach else None,
                       lumped=(150.0, 280.0) if reach else (260.0, 160.0),
                       lprop=(150.0 * (255.68 - 25) / (280 - 25)) if reach else None)
        return rec, s

    RUN.run_one = fake_run
    S6.build_runs = lambda *a, **k: runs
    try:
        S6.work(0, 1, 1e9, set(S6.SETS), queue=True, label="test")
    finally:
        S6.RUNS, S6.SERIES, S6.TRIGGER, S6.STOP_FILE, RUN.run_one, S6.build_runs = saved
    recs = os.listdir(os.path.join(res, "stage6_runs"))
    ser = os.listdir(os.path.join(res, "stage6_series"))
    check(len([f for f in recs if f.endswith(".json")]) == 506 and not [f for f in recs if f.endswith(".claim")],
          "work: 506 records, no claim left")
    check(len(ser) == 106 and not any(f.startswith("draws_") for f in ser), "work: series for every set but the draws")
    r = json.load(open(os.path.join(res, "stage6_runs", runs[-1]["id"] + ".json")))
    check("stage6" in r and "crossings_150C" in r["stage6"], "work: the A1 quantities in every record")


def test_score_and_checks(res, tr):
    os.makedirs(os.path.join(res, "repo_results"), exist_ok=True)
    sc = SC.main(res, predictions_commit="test")
    check(all(k in sc for k in ("P1", "P2", "P3", "P4", "P5", "P6", "P7")), "scorecard has P1 to P7")
    check(sc["P5"]["verdict"] == "failed" and sc["P7"]["verdict"] == "held", "synthetic P5 and P7 verdicts")
    check(os.path.exists(os.path.join(res, "stage6_matched.csv")), "stage6_matched.csv written")
    # V1 on the synthetic series (the three runs exist among the synthetic grid records)
    v = CK.v1(res)
    check(v["pass"], "V1 on synthetic series")
    # V2 with the synthetic cell-1 peak in place of the model
    real = (CK.Pair.peak_euler, CK.Pair.peak_rk4)
    CK.Pair.peak_euler = lambda self, e, tau, dt=0.01, t_end=None: fake_peak(e, tau, "series" if self.G < 0.180 else "parallel")
    CK.Pair.peak_rk4 = lambda self, e, tau, dt=0.001, t_end=None: CK.Pair.peak_euler(self, e, tau)[0]
    try:
        v2 = CK.v2(res)
    finally:
        CK.Pair.peak_euler, CK.Pair.peak_rk4 = real
    check(v2["same_selection"] and v2["input_differences"]["total_median_J"] < 1e-6, "V2 inputs and selection")
    p = subprocess.run([sys.executable, os.path.join(HERE, "make_figure_stage6.py"), "--res", res],
                       capture_output=True, text=True)
    check(p.returncode == 0 and os.path.exists(os.path.join(res, "stage6_figure.png")), "figure on synthetic records "
          + p.stderr[-300:])


if __name__ == "__main__":
    tmp = tempfile.mkdtemp(prefix="stage6_test_")
    try:
        test_crossings()
        test_part_a(tmp)
        tr, runs = test_trigger_and_runs(tmp)
        test_work(tmp, tr, runs)
        test_score_and_checks(tmp, tr)
        print("all Stage 6 tests passed;", tmp)
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(tmp, ignore_errors=True)
