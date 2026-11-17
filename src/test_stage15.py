"""Stage 15 tests, run before the predictions (DECISIONS.md D176): the new loops against Stage 9's, bitwise, on a
synthetic trigger (a made-up ramp to 600 C), the stop at the mean, the shift of the rate laws, the hold, and the
reactive cross-section against Stage 13's conduction model with the reaction off (V3) and its kinetics against the
three-dimensional model's local kinetics on one cell.

Run: python3 src/test_stage15.py   (or with pytest)
"""
import os as _os
for _k in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "NUMBA_NUM_THREADS"):
    _os.environ.setdefault(_k, "1")
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v12_model as V                    # noqa: E402
import stage9_model as M9                # noqa: E402
import stage15_model as M15              # noqa: E402

PASSED = []


def ok(name):
    PASSED.append(name)
    print("ok", name, flush=True)


def _ramp():
    Ta = V.LP.T_AMB
    return lambda t: Ta + min(t / 20.0, 1.0) * 575.0


_MODEL = {}


def _model():
    if "m" not in _MODEL:
        _MODEL["m"] = V.Cell2Contact(V.H_CONTACT["central"], refine=1.0)
    return _MODEL["m"]


def test_resolved_bitwise():
    m = _model()
    gp, gn = V.tabs("parallel", V.G_TAB["central"])
    sh = M9.share_surface(m, "half")
    ramp = _ramp()
    a = M9.run_resolved(m, ramp, gp, gn, t_end=3.0, probes=m.probes, stop_level=None,
                        sources=[M9.Source("delivery", M9.Triangular(2000.0, 21.39, 0.0), sh)], max_sub=4096)
    b = M15.run_resolved15(m, ramp, gp, gn, t_end=3.0, probes=m.probes, stop_level=None,
                           sources=[M9.Source("delivery", M9.Triangular(2000.0, 21.39, 0.0), sh)], max_sub=4096)
    assert np.array_equal(a["T_final"], b["T_final"]) and np.array_equal(a["c_final"], b["c_final"])
    assert np.array_equal(a["series"], b["series"]) and a["energy_J"] == b["energy_J"] and a["steps"] == b["steps"]
    assert all(np.array_equal(a["probe_T"][k], b["probe_T"][k]) for k in a["probe_T"])
    assert b["stop_mean"] is None and b["accounts"] is None
    c = M9.run_resolved(m, ramp, gp, gn, t_end=3.0, probes=m.probes, sei0=0.0)
    d = M15.run_resolved15(m, ramp, gp, gn, t_end=3.0, probes=m.probes, sei0=0.0)
    assert np.array_equal(c["T_final"], d["T_final"]) and np.array_equal(c["series"], d["series"])
    assert c["conversion_volume_mean_end"] == d["conversion_volume_mean_end"]
    ok("run_resolved15 with its additions off is stage9_model.run_resolved, bitwise (fresh with a source; aged)")


def test_resolved_stop_mean_and_accounts():
    m = _model()
    gp, gn = V.tabs("parallel", V.G_TAB["central"])
    sh = M9.share_surface(m, "half")
    ramp = _ramp()
    src = lambda: [M9.Source("delivery", M9.Triangular(30000.0, 21.39, 0.0), sh)]
    full = M15.run_resolved15(m, ramp, gp, gn, t_end=3.0, probes=m.probes, sources=src(), max_sub=4096,
                              accounts_dt=0.5)
    mt, mT = full["mean_steps"]
    level = float(mT[len(mT) // 2])                     # a level the mean reaches half-way through the run
    st = M15.run_resolved15(m, ramp, gp, gn, t_end=3.0, probes=m.probes, sources=src(), max_sub=4096,
                            stop_mean=level)
    sm = st["stop_mean"]
    assert sm is not None and st["t_end_s"] < 3.0
    k = int(np.argmax(mT >= level))
    assert abs(st["t_end_s"] - mt[k]) < 1e-12                     # stopped at the first step at or above the level
    assert mt[k - 1] <= sm["t_s"] <= mt[k]
    n = len(st["probe_t"])
    assert np.array_equal(st["probe_T"]["away"], full["probe_T"]["away"][:n])
    acc = full["accounts"]
    assert acc["keys"][0] == "t_s" and acc["rows"].shape[1] == len(acc["keys"])
    last = dict(zip(acc["keys"][1:], acc["rows"][-1, 1:]))
    for kk, v in full["energy_J"].items():                         # the last row is the record's (doubled) total
        if abs(acc["rows"][-1, 0] - full["t_end_s"]) < 1e-9:
            assert abs(last[kk] - v) <= 1e-9 * max(1.0, abs(v)), (kk, last[kk], v)
    ok("the stop at the mean comes at the first step the mean reaches the level; the accounts close on the record")


def test_shift_and_hold():
    import v12_kernel as KN
    kin = V.bcrnn.Kinetics()
    m1, C1 = np.array([V.LP.M_CELL]), np.array([V.LP.C_CELL])
    base = KN.FastKinetics(kin, m1, C1)
    T = np.array([450.0]); c = V.bcrnn.fresh_state(1)
    s0 = M15.Shifted(base, 0.0)
    a, b = base.start(T, c), s0.start(T, c)
    assert all(np.array_equal(x, y) for x, y in zip(a, b))
    s10 = M15.Shifted(base, 10.0)
    R0, H0 = s10.start(T, c)
    R1, H1 = base.start(T + 10.0, c)
    assert np.array_equal(H0, H1)
    Tn, cn, _ = s10.step(T, c, R0, H0, 0.01)
    Tm, cm, _ = base.step(T + 10.0, c, R1, H1, 0.01)
    assert np.allclose(Tn + 10.0, Tm, rtol=0, atol=1e-12) and np.array_equal(cn, cm)
    h = M15.Hold(12.5, 21.38651984299561, 900.0)
    assert h.cumulative(21.0) == 0.0 and abs(h.cumulative(121.38651984299561) - 1250.0) < 1e-9
    assert abs(h.power(100.0) - 12.5) < 1e-12 and h.power(10.0) == 0.0
    ok("the shift evaluates the rate laws at T + shift and returns the node's own temperature; the hold's energy")


def test_lumped_bitwise_and_shift():
    gp, gn = V.tabs("parallel", V.G_TAB["central"])
    g = V.g_contact(V.H_CONTACT["central"])
    ramp = _ramp()
    a = M9.run_lumped(ramp, gp + gn, g_link=g, f_view=V.F_TOUCH, t_end=120.0, stop_level=None,
                      sources=[M9.Source("delivery", M9.Triangular(2000.0, 21.39, 0.0))], max_sub=4096)
    b = M15.run_lumped15(ramp, gp + gn, g_link=g, f_view=V.F_TOUCH, t_end=120.0, stop_level=None,
                         sources=[M9.Source("delivery", M9.Triangular(2000.0, 21.39, 0.0))], max_sub=4096,
                         accounts_dt=1.0)
    assert np.array_equal(a["series"], b["series"]) and a["energy_J"] == b["energy_J"] and a["peak"] == b["peak"]
    s = M15.run_lumped15(ramp, gp + gn, g_link=g, f_view=V.F_TOUCH, t_end=120.0, shift_K=10.0)
    u = M15.run_lumped15(ramp, gp + gn, g_link=g, f_view=V.F_TOUCH, t_end=120.0)
    assert s["reaction_heat_J"] > u["reaction_heat_J"]           # faster rate laws release more by 120 s
    ok("run_lumped15 is stage9_model.run_lumped bitwise; a positive shift speeds the reaction")


def test_section_v3():
    import stage15_section as S15
    import stage13_section as S13
    import stage13_inputs as IN13
    f1, _, _, _ = V.stage5_t1("parallel", V.H_CONTACT["central"], V.G_TAB["central"], IN13.TAU_TRIGGER,
                              float(IN13.tests()["M50_PT_Exp1"]["E_b_J"]), IN13.T_AMB)
    sec13 = S13.Section(V.H_CONTACT["central"])
    pulse = S13.tri_cumulative(21.38651984299561)
    tt, surf, inner = sec13.run(f1, pulse, 3000.0, 30.0, 0.01, 0.05)
    rs = S15.ReactiveSection(V.H_CONTACT["central"])
    r = rs.run(f1, [M9.Triangular(3000.0, 21.38651984299561, 0.0)], 30.0, dt_early=0.01, dt_late=0.05,
               reaction=False)
    d = np.abs(r["surface_history"] - surf).max()
    assert d < 1e-8, d
    ok(f"V3: the reactive cross-section with the reaction off is Stage 13's model (largest difference {d:.1e} K)")


def test_partb_chains():
    """Part B's chains to their ends with a made-up model in place of the runs (no run is made)."""
    import stage15_partb as PB
    import stage15_inputs as IN
    a2 = {"M50_PT_Exp4": 8000.0, "M50_PP_Exp2": 6000.0, "M50_SP_Exp3": 9000.0, "M50_ST_Exp3": 15000.0}
    true = {"M50_PT_Exp4": 1.12, "M50_PP_Exp2": 0.71, "M50_SP_Exp3": 1.0, "M50_ST_Exp3": 1.31}
    saved = (PB.a2_value, PB.b3_start)
    PB.a2_value = lambda t, xs=None: a2[t]
    PB.b3_start = lambda xs=None: 10.0
    try:
        recs = {}

        def fake(sp):
            res = {"C8": False, "t_C8_s": None, "far_jump": None, "peak_mean_C": 200.0}
            d = sp["deliveries"]
            if sp["kind"] == "B1":
                E = d[0]["E_J"]
                if E >= true[sp["test"]] * a2[sp["test"]]:
                    res.update(C8=True, t_C8_s=300.0)
            elif sp["kind"] == "B3":
                P = d[1]["P_W"]
                t = 300.0 - 4.0 * (P - 10.0)
                res.update(C8=True, t_C8_s=t)
            elif sp["kind"] == "B4":
                if sp["shift_K"] >= 12.0:
                    res.update(C8=True, t_C8_s=250.0)
            elif sp["kind"] == "B2":
                res.update(C8=sp["deliveries"][0]["f"] > 0.048, t_C8_s=400.0)
            elif sp["kind"] == "V4":
                pass
            return dict(sp, resolved=res, E_delivered_J=sp["E_delivered_J"])

        for _ in range(200):
            pend = PB.pending(recs)
            if not pend:
                break
            for sp in pend:
                r = fake(sp)
                if sp["kind"] == "V4":
                    base = recs[sp["id"].replace("_r1.5", "").replace("_dt0.5", "")]
                    r["resolved"] = dict(base["resolved"])
                recs[sp["id"]] = r
        assert not PB.pending(recs)
        st, _, br = PB.b1_state("M50_PT_Exp4", recs)
        assert st == "done" and br["lo_step"] == 1 and br["hi_step"] == 3, (st, br)
        st, _, br = PB.b1_state("M50_PP_Exp2", recs)
        assert st == "done" and br["lo_step"] == -7 and br["hi_step"] == -5, (st, br)
        st, _, br = PB.b1_state("M50_SP_Exp3", recs)
        assert st == "done" and br["lo_step"] == -1 and br["hi_step"] == 1, (st, br)
        st, _, br = PB.b1_state("M50_ST_Exp3", recs)
        assert st == "done" and br["lo_step"] == 5 and br["hi_step"] == 7, (st, br)
        st, _, res = PB.b3_state(recs)
        assert st == "matched" and abs(res["P_W"] - 15.0) < 1e-9, (st, res)
        _, res4 = PB.b4_state(recs)
        assert res4["status"] == "found" and res4["least_shift_K"] == 12.5, res4
        assert sum(1 for k in recs if k.endswith(("_r1.5", "_dt0.5"))) == 4
    finally:
        PB.a2_value, PB.b3_start = saved
    ok("Part B's chains end where their rules say on a made-up model (B1's four brackets, B3's 15 W, B4's 12.5 K, V4)")


def run_all():
    test_shift_and_hold()
    test_lumped_bitwise_and_shift()
    test_resolved_bitwise()
    test_resolved_stop_mean_and_accounts()
    test_section_v3()
    test_partb_chains()
    print(len(PASSED), "passed")


if __name__ == "__main__":
    run_all()
