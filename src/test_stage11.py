#!/usr/bin/env python3
"""Stage 11's tests on synthetic inputs and short runs (DECISIONS.md D116 (3)), before the predictions:
  1. a Stage 11 run at the posterior mean and the central properties equals Stage 10's run of the same point bitwise
     (both neighbours, the five probes, the energy accounts), and its lumped-only run equals the lumped neighbour of
     that run;
  2. a thermal draw: the resolved cell carries the draw's heat capacity and conductivities, the lumped neighbour its
     heat capacity, the trigger's history the central one, and the module's heat capacity is restored after the run,
     also when it fails; at the central properties the context's model is the published one, bitwise;
  3. a kinetic draw: the kinetics are Stage 3's draw (its three columns), and a short run with it closes its energy
     accounts and differs from the mean's;
  4. the threshold search of D113 on made-up thresholds (inside Stage 8's bracket, above it, below it, at zero, above
     1, and a broken chain);
  5. every chain to its end with a made-up run in place of the model, through the work loop, and the scoring of those
     records: every chain ends, every output is written, and Part E's arithmetic and the verdicts are those computed
     by hand from the made-up thresholds;
  6. the scorecard's rules on made-up values (P1's factor and zero tolerance, P5's tie); and V3's separate code on
     the made-up records of 5."""
import json, math, os, shutil, sys, tempfile
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v12_model as V                    # noqa: E402
import stage9_run as R9                  # noqa: E402
import stage10_run as R10                # noqa: E402
import stage11_inputs as IN              # noqa: E402
import stage11_run as R                  # noqa: E402
import stage11_score as SC               # noqa: E402

FAILS = []


def check(name, cond, info=""):
    print(("ok   " if cond else "FAIL ") + name + (f"  {info}" if info else ""), flush=True)
    if not cond:
        FAILS.append(name)


# ------------------------------------------------------------------------------------------------ 1
def test_bitwise():
    sp10 = R10.spec("A", "M50_PT_Exp4", "tri21", 0.0375, "central", 3.0, reading="tri21_C2_lo")
    sp11 = R.spec("T", "M50_PT_Exp4", 0.0375, "mean", "central", "central", "both", False, t_end=3.0)
    ctx10, ctx11 = R9.Context(), R.Context()
    r10, s10 = R10.run_one(sp10, ctx10)
    r11, s11 = R.run_one(sp11, ctx11)
    keys = ("t", "Tmax", "Tmean", "probe_t", "t_lumped", "T_lumped", "t1_T1_C") + tuple("probe_" + k for k in R.IN.PROBES)
    check("a Stage 11 run at the mean and central properties equals Stage 10's, bitwise",
          all(np.array_equal(s10[k], s11[k]) for k in keys))
    check("its energy accounts are Stage 10's", r10["resolved"]["energy_J"] == r11["resolved"]["energy_J"]
          and r10["lumped"]["energy_J"] == r11["lumped"]["energy_J"])
    spl = R.spec("T", "M50_PT_Exp4", 0.0375, "mean", "central", "central", "lumped", False, t_end=3.0)
    rl, sl = R.run_one(spl, ctx11)
    check("its lumped-only run equals the lumped neighbour of that run, bitwise",
          np.array_equal(sl["T_lumped"], s11["T_lumped"]) and rl["lumped"]["energy_J"] == r11["lumped"]["energy_J"])


# ------------------------------------------------------------------------------------------------ 2
def test_thermal():
    ctx = R.Context()
    m0 = ctx.model("central", 1.0, "central")
    ref = V.Cell2Contact(V.H_CONTACT["central"], refine=1.0)
    check("at the central properties the context's model is the published one, bitwise",
          np.array_equal(m0.C, ref.C) and (m0.K != ref.K).nnz == 0)
    for lab, p in IN.thermal_draws().items():
        m = ctx.model("central", 1.0, lab)
        ok_c = abs(2.0 * float(m.C.sum()) - p["C_cell"]) < 1e-9 * p["C_cell"]
        ok_k = (m.K != m0.K).nnz > 0
        check(f"the {lab} draw's cell carries its heat capacity ({p['C_cell']:.3f} J/K) and conductivities",
              ok_c and ok_k and abs(V.LP.C_CELL - R.CENTRAL["C_cell"]) == 0.0)
    sp = R.spec("T", "M50_PT_Exp1", 0.15, "mean", "c_min", "central", "both", False, t_end=2.0)
    rec, ser = R.run_one(sp, ctx)
    sp0 = R.spec("T", "M50_PT_Exp1", 0.15, "mean", "central", "central", "both", False, t_end=2.0)
    rec0, ser0 = R.run_one(sp0, ctx)
    check("a thermal draw's run: the trigger's history is the central one, the neighbour's differs",
          np.array_equal(ser["t1_T1_C"], ser0["t1_T1_C"]) and not np.array_equal(ser["Tmax"], ser0["Tmax"]))
    check("its energy accounts close (resolved and lumped, under 1e-9 of the heat taken in)",
          abs(rec["resolved"]["energy_residual_rel"]) < 1e-9 and abs(rec["lumped"]["energy_residual_rel"]) < 1e-9)
    check("its records carry the draw's heat capacity", abs(rec["C_total_J_K"] - IN.thermal_draws()["c_min"]["C_cell"]) < 1e-9
          and rec["lumped"]["C_J_K"] == IN.thermal_draws()["c_min"]["C_cell"])
    check("the module's heat capacity is the central one after the run", V.LP.C_CELL == R.CENTRAL["C_cell"])
    try:
        with R.heat_capacity(1.0):
            raise RuntimeError("made-up failure")
    except RuntimeError:
        pass
    check("and after a run that fails", V.LP.C_CELL == R.CENTRAL["C_cell"])


# ------------------------------------------------------------------------------------------------ 3
def test_kinetic():
    import stage3_draws as S
    ctx = R.Context()
    kin, draw = ctx.kinetics(188)
    P = S.load_particles()
    ref = S.draw_kinetics(P, *(IN.KIN_COLUMNS[188][i] for i in (0, 1, 2)))
    check("draw 188's kinetics are Stage 3's draw of its three columns",
          draw == {"draw": 188, "an_ele_column": 71, "separator_column": 52, "ncm811_column": 3}
          and all(np.array_equal(np.asarray(getattr(kin, a)), np.asarray(getattr(ref, a)))
                  for a in vars(ref) if isinstance(getattr(ref, a), (np.ndarray, float, int))))
    sp = R.spec("T", "M50_ST_Exp2", 0.0, 188, "central", "central", "both", False, t_end=3.0)
    rec, ser = R.run_one(sp, ctx)
    sp0 = R.spec("T", "M50_ST_Exp2", 0.0, "mean", "central", "central", "both", False, t_end=3.0)
    rec0, ser0 = R.run_one(sp0, ctx)
    check("a kinetic draw's short run closes its energy accounts", abs(rec["resolved"]["energy_residual_rel"]) < 1e-9
          and abs(rec["lumped"]["energy_residual_rel"]) < 1e-9)
    check("and differs from the mean's", not np.array_equal(ser["Tmax"], ser0["Tmax"]))


# ------------------------------------------------------------------------------------------------ 4
def run_chain(T, s8, tol=0.0):
    """The search with the criterion met where f >= T (made up); returns the final state and the fractions run."""
    pts, ran = {}, []
    for _ in range(60):
        st = R.threshold_state(pts, s8)
        if st["status"] != "searching":
            return st, ran
        for f in st["next"]:
            pts[f] = f >= T - tol
            ran.append(f)
    raise RuntimeError("no end")


def test_search():
    b = {"status": "bracket", "lo": 0.15, "hi": 0.1625}
    st, ran = run_chain(0.155, b)
    check("a threshold inside Stage 8's bracket: two runs, the same bracket", st["status"] == "bracket"
          and (st["lo"], st["hi"]) == (0.15, 0.1625) and sorted(ran) == [0.15, 0.1625])
    st, ran = run_chain(0.24, b)
    check("above it: followed up by 0.05, then halved to at most 0.02", st["status"] == "bracket"
          and st["lo"] < 0.24 <= st["hi"] and st["hi"] - st["lo"] <= 0.02 + 1e-12 and 0.2125 in ran and 0.2625 in ran,
          str((st["lo"], st["hi"], ran)))
    st, ran = run_chain(0.05, b)
    check("below it: followed down by 0.05, then halved", st["status"] == "bracket" and st["lo"] < 0.05 <= st["hi"]
          and st["hi"] - st["lo"] <= 0.02 + 1e-12 and 0.1 in ran, str((st["lo"], st["hi"], ran)))
    st, ran = run_chain(0.0, b)
    check("down to f = 0 where it is met everywhere", st["status"] == "zero" and 0.0 in ran, str(ran))
    z = {"status": "zero", "lo": 0.0, "hi": 0.0}
    st, ran = run_chain(0.0, z)
    check("Stage 8's zero met at f = 0: one run", st["status"] == "zero" and ran == [0.0])
    st, ran = run_chain(0.031, z)
    check("Stage 8's zero not met at f = 0: up by 0.05, then halved", st["status"] == "bracket"
          and st["lo"] < 0.031 <= st["hi"] and st["hi"] - st["lo"] <= 0.02 + 1e-12 and ran[:2] == [0.0, 0.05], str(ran))
    st, ran = run_chain(1.5, b)
    check("not met at f = 1: above 1", st["status"] == "above" and 1.0 in ran, str(ran))
    st = R.threshold_state({0.15: True, 0.1625: False}, b)
    check("a fraction met below one not met: broken", st["status"] == "broken" and st["next"] == [])
    b2 = {"status": "bracket", "lo": 0.0, "hi": 0.0125}
    st, ran = run_chain(0.0, b2)
    check("Stage 8's (0, 0.0125] met at f = 0: zero", st["status"] == "zero" and sorted(ran) == [0.0, 0.0125])


# ------------------------------------------------------------------------------------------------ 5
KIN_FACTOR = {188: 1.3, 83: 0.9, 40: 1.0, 184: 2.6}            # made-up multipliers of the threshold
TH_FACTOR = {"kr_min": 1.1, "kr_max": 0.95, "c_min": 0.8, "c_max": 1.2}


def made_up_threshold(test, crit, kin, thermal):
    s = R9.fstar8()[test][crit]
    m = 0.0 if s["status"] == "zero" else 0.5 * (s["lo"] + s["hi"])
    fac = KIN_FACTOR.get(kin, 1.0) if kin != "mean" else TH_FACTOR.get(thermal, 1.0)
    if m == 0.0:
        return 0.03 if (kin == 184 and test == "M50_SP_Exp3") else 0.0     # one zero that leaves
    return m * fac


def made_up_peak(test, thermal, h, f):
    M = R9.max_meas(test)
    base = {"M50_PT_Exp1": -10.0, "M50_PT_Exp3": 14.0, "M50_PP_Exp3": 50.0, "M50_ST_Exp1": 40.0, "M50_ST_Exp2": 30.0}
    off = {"central": 0.0, "kr_min": -8.0, "kr_max": 3.0, "c_min": 6.0, "c_max": -4.0}[thermal]
    off += {"central": 0.0, "low": -18.0, "high": 5.0}[h]
    return M + base[test] + off + 150.0 * f


def fake_run(sp, ctx):
    test, f, kin, th, h = sp["test"], sp["f"], sp["kin"], sp["thermal"], sp["h"]
    rec = dict(sp)
    rec["draw"], rec["wall_s"] = None, 0.0
    tm = {"M50_PT_Exp4": 215.0, "M50_PP_Exp1": 143.5, "M50_PP_Exp2": 143.9, "M50_PP_Exp4": 268.9, "M50_ST_Exp3": 95.1,
          "M50_ST_Exp4": 268.8, "M50_SP_Exp1": 219.0, "M50_SP_Exp2": 148.5, "M50_SP_Exp3": 209.3}
    if sp["kind"] == "D":
        shift = {188: -70.0, 83: 5.0, 40: 0.0, 184: None}[kin]
        t = None if shift is None else tm[test] + shift
        rec["lumped"] = {"propagated": t is not None, "t_prop_s": t, "t_end_s": 900.0, "energy_residual_rel": 0.0}
        return rec, None
    if sp["models"] in ("both", "lumped"):
        T2 = made_up_threshold(test, "C2", kin, th) if test in IN.A_TESTS else 9.0
        met = f >= T2 - 1e-12
        rec["lumped"] = {"propagated": met, "t_prop_s": 100.0 if met else None, "t_end_s": 900.0,
                         "energy_residual_rel": 0.0}
    if sp["models"] in ("both", "resolved"):
        T1 = made_up_threshold(test, "C1", kin, th) if test in IN.A_TESTS else 9.0
        met = f >= T1 - 1e-12
        pk = made_up_peak(test, th, h, f) if test in IN.C_TESTS else 150.0
        end = 900.0 if (not sp["stop"] or not met) else 20.0
        rec["resolved"] = {"propagated": met, "t_prop_s": 20.0 if met else None, "t_end_s": end,
                           "probe_peak": {"away": {"T_C": pk}}, "energy_residual_rel": 0.0, "peak_hottest_C": 200.0}
    rec["wall_s"] = 0.0
    return rec, None


def test_chains_to_end():
    tmp = tempfile.mkdtemp()
    saved = (R.RUNS, R.SERIES, R.STOP_FILE)
    R.RUNS, R.SERIES, R.STOP_FILE = os.path.join(tmp, "runs"), os.path.join(tmp, "series"), os.path.join(tmp, "STOP")
    try:
        n = R.work(0, label="test", wait_s=0.0, run_fn=fake_run)
        recs = R.load_records()
        left = [r for r in R.build_runs(recs) if r["id"] not in recs]
        ch = R.threshold_chains(recs)
        check("every threshold chain ends", all(c["status"] in ("zero", "bracket", "above") for c in ch.values())
              and not left, f"{n} runs; " + str([k for k, c in ch.items() if c["status"] == "searching"][:3]))
        ok = True
        for c in ch.values():
            T = made_up_threshold(c["test"], c["crit"], c["kin"], c["thermal"])
            if c["status"] == "zero":
                ok &= T == 0.0
            elif c["status"] == "bracket":
                ok &= c["lo"] < T <= c["hi"] + 1e-12 and c["hi"] - c["lo"] <= IN.WIDTH + 1e-12
        check("each holds its made-up threshold, to Stage 8's width", ok)
        fm = R.fmax_chains(recs)
        check("C2's two searches end", all(s["status"] in ("matched", "bracketed", "zero", "above 1") for s in fm.values()),
              str({k: s["status"] for k, s in fm.items()}))
        e3 = R.e3_cases(recs)
        check("every E3 case is decided", all(c["verdict"] != "undecided" for c in e3.values()),
              str({k: c["verdict"] for k, c in e3.items()}))
        out = os.path.join(tmp, "out")
        os.makedirs(out)
        v = SC.main(R.RUNS, out)
        check("the scoring writes every output", all(os.path.exists(os.path.join(out, f)) for f in
              ("stage11_draws.csv", "stage11_thresholds.csv", "stage11_overshoot.csv", "stage11_times.csv",
               "stage11_bands.json", "stage11_scorecard.json")))
        sc = json.load(open(os.path.join(out, "stage11_scorecard.json")))
        b = json.load(open(os.path.join(out, "stage11_bands.json")))
        # by hand: P1 fails (draw 184 at 2.6 times the mean); P2 likewise; P6 holds (draw 184 does not cross, draw 188
        # moves by 70 s, in every one of the six)
        check("P1 and P2 fail on the made-up factor of 2.6", sc["verdicts"]["P1"] == "failed"
              and sc["verdicts"]["P2"] == "failed")
        check("P6 holds where a draw does not cross", sc["verdicts"]["P6"] == "held"
              and sc["predictions"]["P6"]["tests_moving"] == 6)
        rows = list(__import__("csv").DictReader(open(os.path.join(out, "stage11_thresholds.csv"))))
        E, above = {}, False
        for r in rows:
            if r["criterion"] == "C2":
                ee = SC.e_e(r["test"])
                v = math.inf if r["status"] == "above" else float(r["f_star"]) * ee
                above |= r["status"] == "above"
                E.setdefault(r["test"], {})[r["draw"]] = v
        band = max(max(v.values()) - min(v.values()) for v in E.values())
        rng = {d: max(E[t][d] for t in E) - min(E[t][d] for t in E) for d in E["M50_PT_Exp1"]}
        jb = b["E1"]["C2"]["largest_within_test_band_J"]
        check("E1's band and ranges, by hand (a threshold above 1 unbounded)",
              (jb == "above 1" if math.isinf(band) else abs(jb - band) < 1e-9)
              and all((b["E1"]["C2"]["range_across_tests_J"][d] == "above 1") if math.isinf(rng[d])
                      else abs(b["E1"]["C2"]["range_across_tests_J"][d] - rng[d]) < 1e-9 for d in rng))
        check("P3 by hand", (sc["verdicts"]["P3"] == "held") == all(rng[d] > band for d in rng if d != "mean")
              and sc["verdicts"]["P3"] != "open")
        bk = {t: max(E[t][d] / SC.e_e(t) for d in ("d188", "d83", "d40", "d184"))
              - min(E[t][d] / SC.e_e(t) for d in ("d188", "d83", "d40", "d184")) for t in E}
        bt = {t: max(E[t][d] / SC.e_e(t) for d in IN.THERMAL_DRAWS) - min(E[t][d] / SC.e_e(t) for d in IN.THERMAL_DRAWS)
              for t in E}
        p5 = all((bt[t] < bk[t]) if not math.isinf(bk[t]) else not math.isinf(bt[t]) for t in E)
        check("P5 by hand", (sc["verdicts"]["P5"] == "held") == p5 and sc["verdicts"]["P5"] != "open")
        check("P4 fails on the low contact (made-up and Stage 7's records)", sc["verdicts"]["P4"] == "failed")
        import stage11_checks as CK
        saved_ck = CK.RUNS
        CK.RUNS = R.RUNS
        try:
            v3 = CK.v3(b)
        finally:
            CK.RUNS = saved_ck
        check("V3 on the made-up records: Part E by separate code agrees", v3["pass"], str(v3["disagreeing"][:3]))
    finally:
        R.RUNS, R.SERIES, R.STOP_FILE = saved
        shutil.rmtree(tmp, ignore_errors=True)


# ------------------------------------------------------------------------------------------------ 6
def test_rules():
    check("P1: within a factor of two, ends included", SC.within_factor(0.2, 0.1) and SC.within_factor(0.05, 0.1)
          and not SC.within_factor(0.201, 0.1) and not SC.within_factor(0.0499, 0.1))
    check("P1: within 0.025 of a mean of 0", SC.within_factor(0.025, 0.0) and not SC.within_factor(0.03125, 0.0))
    check("P1: a threshold above 1 is outside", not SC.within_factor(None, 0.45625))


def main():
    test_search()
    test_rules()
    test_chains_to_end()
    test_bitwise()
    test_thermal()
    test_kinetic()
    print(("all tests passed" if not FAILS else f"{len(FAILS)} FAILED: {FAILS}"), flush=True)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
