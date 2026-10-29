#!/usr/bin/env python3
"""Tests of the Stage 9 code on synthetic inputs (DECISIONS.md D95 (5)), run before the predictions were public.

  - stage9_model against stage8_model bitwise with the fresh state and a triangular source, and against stage7_model
    bitwise with the aged state and no source (resolved, 3 s; lumped, 120 s; cell 1 a made-up ramp to 600 C);
  - a run with the stop lifted equals the stopped run up to its stop, and records the crossing;
  - the constant pulse: its integral, power and largest power, and the energy it delivers over uneven steps;
  - the searches (stage9_search) on made-up crossing times and peaks: every status of f_t and f_max;
  - the relation of f_max to f*;
  - the choices of tests against the real data files;
  - the chains to their ends, the V1 file before any A2 run, the scoring, V2's replay and V4, with a made-up run in
    place of the model (every record written to a scratch directory; no model run), and from those records every
    output: the scoring's files, the checks, the numbers file and the figure (D99 (2));
  - D98 (added while the runs went): a run recorded since a worker read the list, the record's replacement when
    Windows refuses it, and the helpers of stage9_laptop.py --add.
Usage: python3 test_stage9.py   (exit status 0 when every test passes)
"""
import os as _os
for _k in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "NUMBA_NUM_THREADS"):
    _os.environ.setdefault(_k, "1")
import json, math, os, shutil, sys, tempfile, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v12_model as V                    # noqa: E402
import stage7_model as M7                # noqa: E402
import stage8_model as M8                # noqa: E402
import stage9_model as M9                # noqa: E402
import stage9_search as S9               # noqa: E402
import stage9_inputs as IN               # noqa: E402

PASSED = []


def ok(name):
    PASSED.append(name)
    print("ok", name, flush=True)


def test_constant_pulse():
    p = M9.Constant(5000.0, 240.0, 0.0)
    assert p.cumulative(-1.0) == 0.0 and p.cumulative(0.0) == 0.0 and p.cumulative(240.0) == 5000.0
    assert abs(p.cumulative(60.0) - 1250.0) < 1e-12 and p.cumulative(1e4) == 5000.0
    assert p.power(-0.1) == 0.0 and abs(p.power(10.0) - 5000.0 / 240.0) < 1e-15 and p.power(240.0) == 0.0
    assert p.max_power(239.9, 240.1) == 5000.0 / 240.0 and p.max_power(240.0, 241.0) == 0.0
    assert p.max_power(-0.1, 0.0) == 0.0 and p.max_power(-0.1, 0.05) == 5000.0 / 240.0
    rng = np.random.default_rng(1)
    t = np.concatenate([[0.0], np.cumsum(rng.uniform(1e-4, 0.7, 2000))])
    t = t[t <= 300.0]
    tot = sum(p.cumulative(b) - p.cumulative(a) for a, b in zip(t[:-1], t[1:])) + p.cumulative(300.0) - p.cumulative(t[-1])
    assert abs(tot - 5000.0) < 1e-9
    ok("constant pulse")


def _ramp():
    Ta = V.LP.T_AMB
    return lambda t: Ta + min(t / 20.0, 1.0) * 575.0


def test_model_bitwise():
    m = V.Cell2Contact(V.H_CONTACT["central"], refine=1.0)
    gp, gn = V.tabs("parallel", V.G_TAB["central"])
    sh = M8.share_surface(m, "half")
    ramp = _ramp()
    a = M8.run_resolved(m, ramp, gp, gn, t_end=3.0, probes=m.probes, stop_level=V.LEVEL_PROP,
                        sources=[M8.Source("delivery", M8.Pulse(2000.0, 21.39, 0.0), sh)], max_sub=4096)
    b = M9.run_resolved(m, ramp, gp, gn, t_end=3.0, probes=m.probes, stop_level=V.LEVEL_PROP,
                        sources=[M9.Source("delivery", M9.Triangular(2000.0, 21.39, 0.0), sh)], max_sub=4096)
    assert np.array_equal(a["T_final"], b["T_final"]) and np.array_equal(a["c_final"], b["c_final"])
    assert np.array_equal(a["series"], b["series"]) and a["energy_J"] == b["energy_J"] and a["steps"] == b["steps"]
    assert all(np.array_equal(a["probe_T"][k], b["probe_T"][k]) for k in a["probe_T"])
    c7 = M7.run_resolved(m, ramp, gp, gn, t_end=3.0, probes=m.probes, stop_level=V.LEVEL_PROP, sei0=0.0)
    c9 = M9.run_resolved(m, ramp, gp, gn, t_end=3.0, probes=m.probes, stop_level=V.LEVEL_PROP, sei0=0.0)
    assert np.array_equal(c7["T_final"], c9["T_final"]) and np.array_equal(c7["c_final"], c9["c_final"])
    assert np.array_equal(c7["series"], c9["series"]) and c7["conversion_volume_mean_end"] == c9["conversion_volume_mean_end"]
    assert all(c7["energy_J"][k] == c9["energy_J"][k] for k in c9["energy_J"])
    g = V.g_contact(V.H_CONTACT["central"])
    la = M8.run_lumped(ramp, gp + gn, g_link=g, f_view=V.F_TOUCH, t_end=120.0, stop_level=V.LEVEL_PROP,
                       sources=[M8.Source("delivery", M8.Pulse(2000.0, 21.39, 0.0))], max_sub=4096)
    lb = M9.run_lumped(ramp, gp + gn, g_link=g, f_view=V.F_TOUCH, t_end=120.0, stop_level=V.LEVEL_PROP,
                       sources=[M9.Source("delivery", M9.Triangular(2000.0, 21.39, 0.0))], max_sub=4096)
    assert np.array_equal(la["series"], lb["series"]) and la["energy_J"] == lb["energy_J"] and la["peak"] == lb["peak"]
    l7 = M7.run_lumped(ramp, gp + gn, g_link=g, f_view=V.F_TOUCH, t_end=120.0, stop_level=V.LEVEL_PROP, sei0=0.0)
    l9 = M9.run_lumped(ramp, gp + gn, g_link=g, f_view=V.F_TOUCH, t_end=120.0, stop_level=V.LEVEL_PROP, sei0=0.0)
    assert np.array_equal(l7["series"], l9["series"]) and l7["peak"] == l9["peak"]
    assert l7["conversion_end"] == l9["conversion_end"] and all(l7["energy_J"][k] == l9["energy_J"][k] for k in l9["energy_J"])
    ok("stage9_model bitwise against stage8_model (fresh, source) and stage7_model (aged, no source)")


def test_nostop():
    g = V.g_contact(V.H_CONTACT["central"])
    gp, gn = V.tabs("series", V.G_TAB["central"])
    Ta = V.LP.T_AMB
    src = lambda: [M9.Source("delivery", M9.Constant(30000.0, 120.0, 0.0))]
    a = M9.run_lumped(lambda t: Ta, gp + gn, g_link=g, f_view=V.F_TOUCH, t_end=400.0, stop_level=V.LEVEL_PROP,
                      sources=src(), max_sub=4096)
    b = M9.run_lumped(lambda t: Ta, gp + gn, g_link=g, f_view=V.F_TOUCH, t_end=400.0, stop_level=None,
                      sources=src(), max_sub=4096)
    assert a["stop"] is not None and b["stop"] is None and b["t_end_s"] >= 400.0 - 1e-9
    assert a["cross_s"]["T_onset_low"] == b["cross_s"]["T_onset_low"] == a["stop"]["t_s"]
    n = len(a["steps_t"])
    assert np.array_equal(a["steps_T"], b["steps_T"][:n])
    assert abs(b["sources"]["delivery"]["delivered_J"] - 30000.0) < 1e-9 and abs(b["energy_residual_rel"]) < 1e-9
    ok("a run with the stop lifted repeats the stopped one up to its stop")


def test_ft_search():
    grid = IN.grid(0.05)
    fs = {"status": "bracket", "lo": 0.0375, "hi": 0.05}
    # an induction that grows without bound at the threshold 0.04: t_c = 30 / (f - 0.04) + 20
    tcf = lambda f: (30.0 / (f - 0.04) + 20.0) if f > 0.04 else None
    tc = {0.0375: None}
    for _ in range(40):
        st = S9.ft_state(272.0, fs, grid, tc)
        if st["status"] != "searching":
            break
        tc[st["next"]] = tcf(st["next"])
    assert st["status"] in ("matched", "bracketed"), st["status"]
    assert abs(tcf(st["f_t"]) - 272.0) <= 10.0 or st["hi"] - st["lo"] <= 0.005 + 1e-12
    assert st["lo"] <= st["f_t"] <= st["hi"] and st["sensitivity"] is not None
    assert st["runs"][0] == S9.key(0.5 * (0.0375 + 0.25))      # the bisection starts from f*_lo (D91 (3))
    # a jump at the threshold (the hot spot): t_c = 15 s above 0.04, none below
    tc = {0.0375: None}
    for _ in range(40):
        st = S9.ft_state(272.0, fs, grid, tc)
        if st["status"] != "searching":
            break
        tc[st["next"]] = 15.0 if st["next"] > 0.04 else None
    assert st["status"] == "threshold" and st["hi"] - st["lo"] <= 0.005 + 1e-12 and st["f_t"] is None
    # f* = 0 and the crossing at f = 0 already before the measured time
    fz = {"status": "zero", "lo": 0.0, "hi": 0.0}
    st = S9.ft_state(223.0, fz, IN.grid(0.0), {0.0: 21.1})
    assert st["status"] == "early"
    st = S9.ft_state(25.0, fz, IN.grid(0.0), {0.0: 21.1})
    assert st["status"] == "matched" and st["f_t"] == 0.0
    # f* = 0 and the crossing at f = 0 after the measured time: the bisection from 0
    tcz = lambda f: 277.0 - 4000.0 * f
    tc = {0.0: 277.0}
    for _ in range(40):
        st = S9.ft_state(152.0, fz, IN.grid(0.0), tc)
        if st["status"] != "searching":
            break
        tc[st["next"]] = tcz(st["next"])
    assert st["status"] in ("matched", "bracketed") and abs(st["f_t"] - 0.03125) < 0.005
    # not monotone before the measured time is reached
    tc = {0.0375: None, 0.05: 300.0, 0.0625: 250.0, 0.075: 290.0, 0.1: 100.0, 0.15: 90.0, 0.25: 80.0}
    st = S9.ft_state(200.0, fs, grid, tc)
    assert st["status"] == "not monotone" and st["pairs"] == [(0.0625, 0.075)]
    # above the grid
    tc = {f: 500.0 for f in grid}
    st = S9.ft_state(200.0, fs, grid, tc)
    assert st["status"] == "above grid"
    st = S9.ft_state(200.0, {"status": "above", "lo": 1.0, "hi": None}, [], {})
    assert st["status"] == "no crossing"
    ok("f_t search: matched, bracketed, threshold, early, not monotone, above grid, no crossing")


def test_fmax_search():
    pkf = lambda f: 60.2 + 900.0 * f
    pk = {0.0: 60.2, 0.15: pkf(0.15)}
    for _ in range(40):
        st = S9.fmax_state(71.0, 0.15, pk)
        if st["status"] != "searching":
            break
        pk[st["next"]] = pkf(st["next"])
    assert st["status"] in ("matched", "bracketed") and abs(pkf(st["f_max"]) - 71.0) <= 5.0 + 1e-9
    assert st["extended"] is False
    st = S9.fmax_state(105.0, 0.0, {0.0: 161.3})
    assert st["status"] == "zero" and abs(st["overshoot_K"] - 56.3) < 1e-9
    st = S9.fmax_state(71.0, 0.15, {0.0: 67.0})
    assert st["status"] == "matched" and st["f_max"] == 0.0
    # the registered range exhausted (f*_lo = 0): the extension on (0, 1], f = 1 never run
    pkf2 = lambda f: 120.0 + 300.0 * f
    pk = {0.0: 120.0}
    seen_one = False
    for _ in range(60):
        st = S9.fmax_state(133.0 + 40.0, 0.0, pk)
        if st["status"] != "searching":
            break
        seen_one = seen_one or st["next"] == 1.0
        if st.get("stage") == "extension":
            assert set(st["speculative"]) <= {S9.key(0.5 * (st["lo"] + st["next"])), S9.key(0.5 * (st["next"] + st["hi"]))}
        pk[st["next"]] = pkf2(st["next"])
    assert st["status"] in ("matched", "bracketed") and st["extended"] and not seen_one
    # above 1: the end is run last
    pk = {0.0: 100.0}
    for _ in range(60):
        st = S9.fmax_state(808.0, 0.0, pk)
        if st["status"] != "searching":
            break
        pk[st["next"]] = 100.0 + 200.0 * st["next"]
    assert st["status"] == "above 1" and 1.0 in pk
    ok("f_max search: zero, matched at 0, bisection, extension, above 1, speculative midpoints")


def test_below():
    fz = {"status": "zero", "lo": 0.0, "hi": 0.0}
    fb = {"status": "bracket", "lo": 0.15, "hi": 0.1625}
    f0 = {"status": "bracket", "lo": 0.0, "hi": 0.0125}
    assert S9.below({"status": "zero", "f_max": 0.0}, f0) is True
    assert S9.below({"status": "zero", "f_max": 0.0}, fz) is False
    assert S9.below({"status": "bracketed", "f_max": 0.02, "lo": 0.0186, "hi": 0.0234}, fb) is True
    assert S9.below({"status": "bracketed", "f_max": 0.2, "lo": 0.19, "hi": 0.195}, fb) is False
    assert S9.below({"status": "bracketed", "f_max": 0.155, "lo": 0.15, "hi": 0.155}, fb) is None
    ok("f_max against f*")


def test_choices():
    import stage9_run as R
    assert IN.check_choices(R.stage7_zero())
    f8 = IN.stage8_fstar()
    assert f8["M50_PT_Exp1"]["C1"] == {"status": "bracket", "lo": 0.15, "hi": 0.1625}
    assert f8["M50_SP_Exp1"]["C1"]["status"] == "zero" and f8["M50_ST_Exp3"]["C2"]["hi"] == 0.2375
    ok("the named tests against the data; Stage 8's f* read from its thresholds file")


# ------------------------------------------------------------------------------------------------ the chains end to end
def _fake_run(sp, ctx=None, keep_series=True):
    """A made-up run in place of the model: the criteria and peaks as smooth functions of the delivered energy, with
    the delivery's form changing them; no model is run."""
    import stage9_run as R
    if sp.get("kind") == "xcheck":              # the cloud record itself, as a laptop that reproduces it would give
        rid = sp["stage8_id"]
        rec = dict(json.load(open(os.path.join(R.S8RUNS, rid + ".json"))), id=sp["id"], kind="xcheck")
        z = np.load(os.path.join(R.RES, "stage8_series", rid + ".npz"))
        return rec, {k: z[k] for k in z.files}
    f, x = sp["f"], sp["test"]
    f8 = R.fstar8()[x]
    tm = R.by_test()[x]["time_s"] or 250.0
    slow = {"tri": 1.0, "con": 1.0 + sp["tau_d_s"] / 120.0, "none": 1.0}[sp["shape"]]
    aged = 1.2 if sp["sei"] == "aged" else 1.0
    th1 = (f8["C1"]["lo"] + f8["C1"]["hi"]) / 2 * slow * aged if f8["C1"]["status"] == "bracket" else -1.0
    th2 = (f8["C2"]["lo"] + f8["C2"]["hi"]) / 2 * slow * aged if f8["C2"]["status"] == "bracket" else -1.0
    rec = dict(sp, resolved=None, lumped=None, wall_s=0.0)
    series = {"t1_t": np.array([0.0, 900.0]), "t1_T1_C": np.array([25.0, 25.0]), "t1_T2_C": np.array([25.0, 25.0])}
    E = sp["E_delivered_J"]
    shape = {"tri": "triangular", "con": "constant"}.get(sp["shape"])
    srcd = ({"delivery": {"E_J": E, "tau_s": sp["tau_d_s"], "t0_s": 0.0, "shape": shape, "delivered_J": E}}
            if E > 0 else {})
    if sp["models"] in ("both", "resolved"):
        cross = f > th1
        tc = (12.0 + 8.0 * slow) if cross else None
        t_end = tc if (cross and sp["stop"]) else 900.0
        peak_away = 50.0 + 2000.0 * f + (100.0 if x.startswith("M50_ST") else 0.0)
        rec["resolved"] = {"propagated": cross, "t_prop_s": tc, "stopped": bool(cross and sp["stop"]), "t_end_s": t_end,
                           "peak_hottest_C": 255.7 if cross else 200.0, "t_peak_hottest_s": 20.0,
                           "probe_peak": {"away": {"T_C": peak_away if t_end >= 900.0 else 30.0, "t_s": 300.0},
                                          "toward": {"T_C": 250.0, "t_s": 20.0}},
                           "energy_residual_rel": 1e-13, "sources": {k: dict(v, delivered_J=min(E, E)) for k, v in srcd.items()},
                           "cross_s": {"T_onset_low": tc}}
        if sp["stop"] and cross:
            for v in rec["resolved"]["sources"].values():
                pul = (M9.Constant if v["shape"] == "constant" else M9.Triangular)(v["E_J"], v["tau_s"], 0.0)
                v["delivered_J"] = pul.cumulative(t_end)
        tt = np.linspace(0.0, t_end, 50)
        series.update({"t": tt, "Tmax": np.full(50, 400.0) if not cross else np.full(50, 300.0),
                       "probe_t": tt, "probe_away": np.full(50, peak_away + 273.15)})
        if cross:
            series["Tmax"] = np.where(tt < tc, 300.0, 530.0)
        else:
            series["Tmax"] = np.full(50, 400.0)
    if sp["models"] in ("both", "lumped"):
        cross = f > th2
        tc = (60.0 + 0.6 * tm * slow * (max(th2, 0.0) + 0.01) / (f - th2 + 0.01) * 0.5) if cross else None
        t_end = tc if (cross and sp["stop"]) else 900.0
        rec["lumped"] = {"propagated": cross, "t_prop_s": tc, "stopped": bool(cross and sp["stop"]), "t_end_s": t_end,
                         "peak_C": 60.0 + 800.0 * f if t_end >= 900.0 else 255.7, "t_peak_s": 250.0,
                         "energy_residual_rel": 1e-14,
                         "sources": {k: dict(v) for k, v in srcd.items()}, "cross_s": {"T_onset_low": tc}}
        if sp["stop"] and cross:
            for v in rec["lumped"]["sources"].values():
                pul = (M9.Constant if v["shape"] == "constant" else M9.Triangular)(v["E_J"], v["tau_s"], 0.0)
                v["delivered_J"] = pul.cumulative(t_end)
        tl = np.linspace(0.0, t_end, 50)
        series.update({"t_lumped": tl, "T_lumped": np.where(tl < (tc or 1e9), 400.0, 530.0)})
    # D99 (2): where Stage 7 or Stage 8 already holds the point, the made-up run crosses when that record does, as a
    # run of the model would (a point held by two records, D95 (4))
    real = None
    if sp["shape"] == "none" and f == 0.0:
        real = R.stage7_records().get((sp["sei"], x))
    elif sp["cfg"] == R.cfg_key(R.TRI21()):
        real = _stage8_points().get((x, R.SR8.key(f)))
    for part in ("resolved", "lumped"):
        if real is not None and rec.get(part) and real.get(part):
            t_c = real[part].get("t_prop_s") if real[part]["propagated"] else None
            rec[part]["propagated"] = bool(real[part]["propagated"])
            rec[part]["t_prop_s"] = t_c
            rec[part]["cross_s"] = {"T_onset_low": t_c}
    return rec, series


_S8P = {}


def _stage8_points():
    import stage9_run as R
    if not _S8P:
        for r in R.stage8_records():
            _S8P[(r["test"], R.SR8.key(r["f"]))] = r
    return _S8P


def test_chains_end_to_end():
    tmp = tempfile.mkdtemp(prefix="stage9_test_")
    try:
        import stage9_run as R
        R.RUNS, R.SERIES, R.XCHK = (os.path.join(tmp, d) for d in ("runs", "series", "xcheck"))
        R.V1_FILE = os.path.join(tmp, "v1.json")
        R.STOP_FILE = os.path.join(tmp, "STOP")
        R._RECS.clear()
        real = R.run_one
        R.run_one = _fake_run
        a2_before_v1 = []
        n = 0
        while n < 6000:
            recs = R.load_records()
            runs = R.build_runs(recs)
            pend = [r for r in runs if not R._recorded(r, recs)]
            if not pend:
                break
            for sp in pend[:40]:
                if sp.get("kind") == "ft" and not os.path.exists(R.V1_FILE) and sp["cfg"] == R.cfg_key(R.TRI21()):
                    a2_before_v1.append(sp["id"])
                rec, series = _fake_run(sp)
                path, spath = R._paths(sp)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                os.makedirs(os.path.dirname(spath), exist_ok=True)
                np.savez_compressed(spath, **series)
                json.dump(rec, open(path, "w"), default=float)
                n += 1
        R.run_one = real
        recs = R.load_records()
        P = R.points(recs)
        states = R.all_states(P, os.path.exists(R.V1_FILE))
        bad = {k: s["status"] for k, s in states.items() if s["status"] in ("searching", "waiting", "broken")}
        assert not bad, bad
        assert os.path.exists(R.V1_FILE) and not a2_before_v1
        import stage9_score as SC
        sc = SC.score(P, states)
        assert set(sc) == {f"P{i}" for i in range(1, 9)}
        assert sc["P1"]["holds"] is True              # the made-up hot spot crosses at 20 s
        assert all(isinstance(v["holds"], bool) for v in sc.values())
        rows = SC.induction_rows(P, states)
        assert rows and all(r["t_c_s"] is None or r["t_c_s"] > 0 for r in rows)
        SC.fraction_rows(states), SC.long_rows(states), SC.sensitivities(states)
        # D99 (2): the whole of the outputs, as they will be made from the records: the scoring's files, the checks,
        # the numbers file and the figure, into a scratch results folder that sees the made-up Stage 9 records beside
        # the real Stage 7 and Stage 8 ones
        import stage9_checks as CK
        import stage9_numbers as NU
        import subprocess
        res = os.path.join(tmp, "res")
        os.makedirs(res)
        real = os.path.join(HERE, "..", "results")
        for d in ("stage7_runs", "stage7_series", "stage8_runs", "stage8_series"):
            os.symlink(os.path.abspath(os.path.join(real, d)), os.path.join(res, d))
        for d, src in (("stage9_runs", R.RUNS), ("stage9_series", R.SERIES), ("stage9_xcheck", R.XCHK)):
            os.symlink(src, os.path.join(res, d))
        ck_res = CK.RES
        CK.RES = res
        try:
            card = SC.main(res)
            CK.main()
            chk = json.load(open(os.path.join(res, "stage9_checks.json")))
            assert chk["X"]["pass"] and chk["V4"]["pass"] and chk["V2"]["pass"], {k: chk[k].get("pass") for k in chk}
            assert chk["V1"]["written_before_A2"] and chk["V1"]["same_as_file"]
            assert chk["V3"].get("pass") is not None, chk["V3"]
            nu = NU.main(res)
            assert not nu["unfinished_chains"], nu["unfinished_chains"]
            assert set(nu["verdicts"]) == {f"P{i}" for i in range(1, 9)}
            for f in ("stage9_induction.csv", "stage9_fractions.csv", "stage9_long.csv", "stage9_scorecard.json",
                      "stage9_states.json", "stage9_checks.json", "stage9_paper_numbers.json"):
                assert os.path.getsize(os.path.join(res, f)) > 0, f
            fig = subprocess.run([sys.executable, os.path.join(HERE, "make_figure_stage9.py"), "--res", res],
                                 capture_output=True, text=True)
            assert fig.returncode == 0, fig.stderr
            assert os.path.getsize(os.path.join(res, "stage9_figure.png")) > 0
        finally:
            CK.RES = ck_res
        ok(f"the chains end to end with a made-up run ({n} runs, {len(states)} chains), V1 before any A2 run, the scoring; "
           f"the scoring's files, the checks, the numbers file and the figure")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_workers_d98():
    """D98 (added while the runs went): a worker lets go of a run recorded since it read the list and keeps the
    record already there; the record's replacement when Windows refuses it; the launcher's helpers of --add."""
    import subprocess
    tmp = tempfile.mkdtemp(prefix="stage9_test_")
    import stage9_run as R
    real_run, real_load, real_replace = R.run_one, R.load_records, os.replace
    saved = (R.RUNS, R.SERIES, R.XCHK, R.V1_FILE, R.STOP_FILE)
    try:
        R.RUNS, R.SERIES, R.XCHK = (os.path.join(tmp, d) for d in ("runs", "series", "xcheck"))
        R.V1_FILE, R.STOP_FILE = os.path.join(tmp, "v1.json"), os.path.join(tmp, "STOP")
        R._RECS.clear()
        for d in (R.RUNS, R.SERIES, R.XCHK):
            os.makedirs(d, exist_ok=True)
        pend = [r for r in R.build_runs(R.load_records()) if r.get("kind") != "xcheck"]
        kinds = {pend[0]["kind"]}
        first, second = [r for r in pend if r["kind"] in kinds][:2]
        path0 = R._paths(first)[0]
        json.dump({"id": first["id"], "mark": "the first record"}, open(path0, "w"))
        R.run_one = _fake_run
        R.load_records = lambda runs_dir=None: {}  # the list as read before that record was made
        assert R.work(0, once=True, wait_s=0.0, sets=kinds) == 1
        assert json.load(open(path0))["mark"] == "the first record"
        assert json.load(open(R._paths(second)[0]))["id"] == second["id"]
        assert not [f for f in os.listdir(R.RUNS) if f.endswith(".claim") or ".tmp" in f]
        R.run_one, R.load_records = real_run, real_load
        a, b = os.path.join(tmp, "a.json"), os.path.join(tmp, "b.json")
        calls = []

        def refuse(n):
            def rep(src, dst):
                calls.append(1)
                if len(calls) <= n:
                    raise PermissionError(13, "Access is denied")
                return real_replace(src, dst)
            return rep
        open(a, "w").write("new")
        open(b, "w").write("old")
        os.replace = refuse(99)
        assert R._put(a, b, tries=3, wait_s=0.0) is False and open(b).read() == "old" and not os.path.exists(a)
        os.remove(b)
        open(a, "w").write("new")
        calls.clear()
        os.replace = refuse(2)
        assert R._put(a, b, tries=3, wait_s=0.0) is True and open(b).read() == "new"
        os.remove(b)
        open(a, "w").write("new")
        calls.clear()
        os.replace = refuse(99)
        try:
            R._put(a, b, tries=3, wait_s=0.0)
            raise AssertionError("no error")
        except PermissionError:
            pass
        os.replace = real_replace
        import stage9_laptop as L
        L.RES, L.LOGS = tmp, os.path.join(tmp, "logs")
        os.makedirs(L.LOGS)
        for name, text in (("laptop_20261029T050011Z_w00.log", "run\nworker 0: nothing left to run (3 this pass)\n"),
                           ("laptop_20261029T050011Z_w01.log", "run\nTraceback (most recent call last):\n"),
                           ("laptop_20261029T060000Z_w00.log", "a later start\n")):
            open(os.path.join(L.LOGS, name), "w").write(text)
        lock = {"started_utc": "2026-10-29T05:00:14Z", "workers": 2, "pids": [11, 12, 13],
                "added": [{"utc": "2026-10-29T05:20:00Z", "pids": [13], "logs": ["w24.log"]}]}
        lg = L._logs(lock)
        assert lg == {11: os.path.join(L.LOGS, "laptop_20261029T050011Z_w00.log"),
                      12: os.path.join(L.LOGS, "laptop_20261029T050011Z_w01.log"), 13: "w24.log"}, lg
        assert L._ended_well(lg[11]) and not L._ended_well(lg[12]) and L._ended_well(None)
        assert L._ended_well(os.path.join(tmp, "missing.log"))
        dead = subprocess.Popen(["true"])
        dead.wait()
        runs = os.path.join(tmp, "stage9_runs")
        os.makedirs(runs)
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        open(os.path.join(runs, "x_dead.claim"), "w").write(f"14 {dead.pid} {now}\n")
        open(os.path.join(runs, "x_live.claim"), "w").write(f"3 {os.getpid()} {now}\n")
        open(os.path.join(runs, "x_new.claim"), "w").write("")
        assert L._free_claims() == 1
        assert sorted(os.listdir(runs)) == ["x_live.claim", "x_new.claim"]
        ok("D98: a run recorded since the list was read is let go and its record kept; the record's replacement; "
           "the launcher's logs, normal ends and claims of workers no longer running")
    finally:
        os.replace = real_replace
        R.run_one, R.load_records = real_run, real_load
        R.RUNS, R.SERIES, R.XCHK, R.V1_FILE, R.STOP_FILE = saved
        R._RECS.clear()
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    for t in (test_constant_pulse, test_ft_search, test_fmax_search, test_below, test_choices, test_chains_end_to_end,
              test_workers_d98, test_model_bitwise, test_nostop):
        t()
    print(f"all {len(PASSED)} tests passed")
