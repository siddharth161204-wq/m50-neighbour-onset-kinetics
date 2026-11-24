"""Step 16 tests, run before the predictions (DECISIONS.md D190): N's, T's and V's rules on synthetic records, with a
made-up runaway time standing in for the three-dimensional model, and the share of a delivery made by a time.

Run: python3 src/test_stage16.py   (or with pytest)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage15_inputs as IN              # noqa: E402
import stage16_run as S                  # noqa: E402

PASSED = []


def ok(name):
    PASSED.append(name)
    print("ok", name, flush=True)


def fake_record(sp, t_c8_of_E):
    """A record of the spec as the run would leave it, with C8 at t_c8_of_E(E) (None: no C8 within 900 s)."""
    r = dict(sp)
    E = sp["E_delivered_J"]
    t = t_c8_of_E(E)
    r["resolved"] = {"C8": t is not None, "t_C8_s": t, "t_end_s": t if t is not None else IN.T_END}
    r["wall_s"] = 300.0
    return r


def drive(test, t_c8_of_E, shape="tri", tau=None, kind="N", max_runs=40):
    recs = {}
    for _ in range(max_runs):
        st, sp, res = S.need_state(test, shape, tau, recs, kind, recs15={}, a1=[])
        if st != "running":
            return st, res, recs
        recs[sp["id"]] = fake_record(sp, t_c8_of_E)
    raise AssertionError("no end in %d runs" % max_runs)


def test_classify():
    assert S.classify(100.0, 100.0, 95.0) == "early"
    assert S.classify(105.0, 105.0, 95.0) == "early"        # exactly t_m + 10 s
    assert S.classify(105.1, 105.1, 95.0) == "late"
    assert S.classify(None, 900.0, 95.0) == "late"
    assert S.classify(None, 104.0, 95.0) is None             # stopped before the window ends, no C8: no class
    ok("classify")


def test_share():
    tau = IN.TAU_TRIGGER
    assert abs(S.share_by("tri", None, 0.5 * tau) - 0.5) < 1e-12
    assert abs(S.share_by("tri", None, 2 * tau) - 1.0) < 1e-12
    assert abs(S.share_by("con", 240.0, 120.0) - 0.5) < 1e-12
    assert abs(S.share_by("con", 360.0, 400.0) - 1.0) < 1e-12
    ok("share of a delivery by a time")


def _need_case(test, E_true, slope_s_per_J=0.1, thr=None):
    """A runaway time falling with energy through t_m at E_true; below thr (if given) no C8."""
    t_m = S.t_measured(test)

    def f(E):
        if thr is not None and E <= thr:
            return None
        return t_m + S.WINDOW_S - slope_s_per_J * (E - E_true)
    return f


def test_need_converges_each_side():
    E_e = IN.e_e("M50_PP_Exp1")
    E_x = S.xs_need("M50_PP_Exp1", "tri", None)[0]
    for E_true in (E_x - 3.3 * S.GRID_FRAC * E_e, E_x - 0.4 * S.GRID_FRAC * E_e, E_x + 0.2 * S.GRID_FRAC * E_e,
                   E_x + 2.7 * S.GRID_FRAC * E_e):
        st, res, recs = drive("M50_PP_Exp1", _need_case("M50_PP_Exp1", E_true))
        assert st == "done", st
        lo, hi = res["lo"][0], res["hi"][0]
        assert lo < E_true + 1e-6 <= hi + 1e-6, (lo, E_true, hi)
        assert hi - lo <= S.FINAL_FRAC * E_e + 1e-6
        assert len(recs) <= 6, len(recs)
    ok("N closes a bracket on the need from either side of the cross-section's value")


def test_need_at_threshold():
    """A need at a threshold: below it no C8, just above it C8 well before t_m; the bracket straddles the threshold."""
    test = "M50_PT_Exp4"
    t_m = S.t_measured(test)
    thr = 7000.0
    f = lambda E: None if E <= thr else t_m - 60.0 - 0.05 * (E - thr)
    st, res, recs = drive(test, f)
    assert st == "done"
    assert res["lo"][2] is None and res["hi"][2] < t_m - S.WINDOW_S
    assert res["lo"][0] <= thr < res["hi"][0]
    ok("N at a threshold: the bracket straddles it, its lower end without C8")


def test_need_uses_existing_runs():
    """Archived runs of the configuration count: a bracket they already close needs no run."""
    test = "M50_SP_Exp1"
    t_m = S.t_measured(test)
    a1 = [{"test": test, "shape": "tri", "tau_d_s": IN.TAU_TRIGGER, "E_J": 6000.0, "t_C8_3d_s": t_m - 5.0,
           "t_end_s": t_m - 5.0, "id": "a"},
          {"test": test, "shape": "tri", "tau_d_s": IN.TAU_TRIGGER, "E_J": 5900.0, "t_C8_3d_s": t_m + 30.0,
           "t_end_s": t_m + 30.0, "id": "b"}]
    st, sp, res = S.need_state(test, "tri", None, {}, "N", recs15={}, a1=a1)
    assert st == "done" and res["lo"][4] == "b" and res["hi"][4] == "a"
    ok("N reads the runs already made and runs none where they bracket the need")


def test_need_not_monotone_and_range():
    test = "M50_SP_Exp2"
    t_m = S.t_measured(test)
    a1 = [{"test": test, "shape": "tri", "tau_d_s": IN.TAU_TRIGGER, "E_J": 5000.0, "t_C8_3d_s": t_m - 50.0,
           "t_end_s": t_m - 50.0, "id": "a"},
          {"test": test, "shape": "tri", "tau_d_s": IN.TAU_TRIGGER, "E_J": 6000.0, "t_C8_3d_s": None,
           "t_end_s": 900.0, "id": "b"}]
    st, sp, res = S.need_state(test, "tri", None, {}, "N", recs15={}, a1=a1)
    assert st == "not monotone"
    st, res, recs = drive(test, lambda E: None)                      # never runs away: stops at the grid's end
    assert st == "out of range" and len(recs) == S.MAX_GRID_STEPS + 1
    ok("N stops and says so where the runs are not monotone or the grid ends")


def test_t_rule():
    """T: B1's rule on PT-Exp1, from either side, closes one step apart."""
    A = S.xs_threshold(S.WEAK2)
    for thr in (0.93 * A, 0.99 * A, 1.02 * A, 1.17 * A):
        recs = {}
        for _ in range(30):
            st, p, br = S.t_state(recs)
            if st != "running":
                break
            for sp in p:
                r = dict(sp)
                r["resolved"] = {"C8": sp["E_delivered_J"] > thr, "t_C8_s": 50.0 if sp["E_delivered_J"] > thr else None,
                                 "t_end_s": 50.0 if sp["E_delivered_J"] > thr else 900.0}
                recs[sp["id"]] = r
        assert st == "done", st
        assert br["lo_J"] < thr < br["hi_J"]
        assert br["hi_step"] - br["lo_step"] == 2
    ok("T closes PT-Exp1's bracket one step of 10 % wide on either side")


def test_v_rule():
    """V waits for all eight, chooses by its rule, refines both ends, and adds a run where an end changes class."""
    recs = {}
    truth = {t: S.xs_need(t, "tri", None)[0] * 0.97 for t in S.STRONG8}
    for t in S.STRONG8:
        f = _need_case(t, truth[t])
        for _ in range(20):
            st, sp, res = S.need_state(t, "tri", None, recs, "N", recs15={}, a1=[])
            if st != "running":
                break
            recs[sp["id"]] = fake_record(sp, f)
    nres = {t: S.need_state(t, "tri", None, recs, "N", recs15={}, a1=[]) for t in S.STRONG8}
    assert all(v[0] == "done" for v in nres.values())
    st, p, out = S.v_state(recs, nres)
    assert st == "running" and len(p) == 2 and all(sp["refine"] == 1.5 and sp["dt_scale"] == 0.5 for sp in p)
    tv = out["test"]
    assert tv == "M50_ST_Exp4"                       # every lower end runs away here: the latest measured time
    # where the latest test's lower end does not run away, the next latest whose lower end does is chosen
    alt = dict(nres)
    st4, sp4, r4 = alt["M50_ST_Exp4"]
    r4 = dict(r4)
    r4["lo"] = (r4["lo"][0], "late", None, r4["lo"][3], r4["lo"][4])
    alt["M50_ST_Exp4"] = (st4, sp4, r4)
    assert S.v_choice(alt) == "M50_PP_Exp4"
    # while an N search runs, V waits
    alt["M50_SP_Exp3"] = ("running", None, None)
    assert S.v_choice(alt) is None
    t_m = S.t_measured(tv)
    # the refined model: the lower end now early (C8 earlier by 15 s), so one extra run below
    for sp in p:
        r = fake_record(sp, lambda E: _need_case(tv, truth[tv])(E) - 15.0 if _need_case(tv, truth[tv])(E) else None)
        recs[sp["id"]] = r
    st, p2, out = S.v_state(recs, nres)
    classes = {s: v["class"] for s, v in out["refined"].items()}
    if classes["lo"] == "early":
        assert st == "running" and len(p2) == 1 and p2[0]["E_delivered_J"] < out["base"]["lo"][0]
    ok("V chooses one test by its rule, refines both ends and extends where an end changes class")


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
    print(len(PASSED), "passed")
