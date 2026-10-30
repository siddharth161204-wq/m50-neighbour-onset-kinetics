#!/usr/bin/env python3
"""Stage 10's tests on synthetic inputs and short runs (DECISIONS.md D106 (3)), before the predictions:
  1. a Stage 10 run equals Stage 9's run of the same point bitwise, at the probes they share (toward, away), the
     hottest node, the lumped neighbour and the energy accounts, over a short run with a delivery;
  2. the three nodes (and the two beside them) are where D102 (4) puts them on the base mesh, at every contact;
  3. the history metrics on made-up histories with known answers;
  4. Part B's chains: Stage 9's search on made-up peaks at two nodes, the runs shared;
  5. Firth's logistic against a direct maximisation of the penalised likelihood, and the constant's closed form;
  6. the held-out scores and their permutation p-values on made-up outcomes, and the ranks and Spearman's rho
     against scipy's;
  7. the scorecard's rules on made-up results."""
import math, os, sys, tempfile
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v12_model as V                    # noqa: E402
import stage9_run as R9                  # noqa: E402
import stage10_inputs as IN              # noqa: E402
import stage10_run as R10                # noqa: E402
import stage10_score as SC               # noqa: E402
import stage10_partc as PC               # noqa: E402

FAILS = []


def check(name, cond, info=""):
    print(("ok   " if cond else "FAIL ") + name + (f"  {info}" if info else ""), flush=True)
    if not cond:
        FAILS.append(name)


def test_bitwise():
    sp10 = R10.spec("A", "M50_PT_Exp4", "tri21", 0.0375, "central", 3.0, reading="tri21_C2_lo")
    sp9 = R9.spec(R9.TRI21(), "M50_PT_Exp4", 0.0375, "both", stop=False)
    sp9["t_end_s"] = 3.0
    ctx = R9.Context()
    r10, s10 = R10.run_one(sp10, ctx)
    r9, s9 = R9.run_one(sp9, ctx)
    same = all(np.array_equal(s10[k], s9[k]) for k in ("t", "Tmax", "Tmean", "probe_t", "probe_toward", "probe_away",
                                                       "t_lumped", "T_lumped", "t1_T1_C"))
    check("a Stage 10 run equals Stage 9's at the shared probes, bitwise", same)
    check("the energy accounts are the same", r10["resolved"]["energy_J"] == r9["resolved"]["energy_J"]
          and r10["lumped"]["energy_J"] == r9["lumped"]["energy_J"])
    check("the new probes are recorded", all(("probe_" + k) in s10 for k in R10.PROBES))


def test_nodes():
    for h in IN.CONTACTS:
        m = V.Cell2Contact(V.H_CONTACT[h], refine=1.0)
        w = IN.theta_ok(m)
        check(f"the probes' nodes at the {h} contact", abs(w["side"]["theta_deg"] - 88.277117) < 1e-5
              and abs(w["facing"]["theta_deg"] - 0.325853) < 1e-5 and w["away"]["theta_deg"] == 180.0)
    m = V.Cell2Contact(V.H_CONTACT["central"], refine=1.0)
    R = IN.model_R(m)
    on = np.where((np.abs(m.r_node - R) < 1e-12) & (np.abs(m.z_node - V.LZ / 2) < 1e-12))[0]
    th = np.degrees(m.th_node[on])
    near90 = on[int(np.argmin(np.abs(th - 90.0)))]
    off = sorted(th[th > 1e-9])[0]
    check("the side node is the mid-length surface node nearest 90 degrees", int(near90) == IN.NODES["side"]["node"])
    check("the facing node is the first mid-length surface node off the line", abs(off - 0.325853) < 1e-5)


def test_metrics():
    tm = np.arange(0.0, 500.0 + 1e-9, 0.5)
    Tm = 25.0 + 0.5 * tm
    m = SC.metrics(tm, Tm, tm, Tm + 3.0)
    check("a history 3 K above has a root mean square of 3 K", abs(m["rms_K"] - 3.0) < 1e-12 and abs(m["diff_at_end_K"] - 3.0) < 1e-12)
    check("the rise over the last 60 s", abs(m["rise_last_measured_K"] - 30.0) < 1e-9 and abs(m["rise_last_model_K"] - 30.0) < 1e-9)
    check("the first passes of 100 and 150 C", abs(m["pass_100_measured_s"] - 150.0) < 1e-9 and abs(m["pass_150_model_s"] - 244.0) < 1e-9)
    tmod = np.arange(0.0, 332.0, 0.1)
    m2 = SC.metrics(tm, Tm, tmod, 25.0 + 0.5 * tmod + 2.0 * np.sin(tmod))
    check("a model on its own time grid", abs(m2["rms_K"] - math.sqrt(2.0)) < 0.05, f"{m2['rms_K']:.4f}")


def test_chains():
    recs = {}

    def add(test, f, peaks):
        sp = R10.spec("B", test, "tri21", f, "central", 900.0)
        sp["resolved"] = {"probe_peak": {n: {"T_C": peaks[n]} for n in ("away", "side", "facing", "toward", "side_out")}}
        recs[sp["id"]] = sp
    st = R10.chain_states(recs)
    check("each Part B chain starts at f = 0", all(s["next"] == 0.0 for s in st.values()))
    for t in IN.PART_B_TESTS:
        add(t, 0.0, {"away": 0, "side": 200.0, "facing": 300.0, "toward": 300, "side_out": 0})
    st = R10.chain_states(recs)
    check("f_max = 0 at both nodes where f = 0 exceeds every maximum", all(s["status"] == "zero" for s in st.values()))
    recs.clear()
    add("M50_PT_Exp1", 0.0, {"away": 60, "side": 64.0, "facing": 70.9, "toward": 71, "side_out": 63})
    st = R10.chain_states(recs)
    s_side, s_face = st["B_side_M50_PT_Exp1"], st["B_facing_M50_PT_Exp1"]
    check("within 5 K at f = 0 is f_max = 0 (facing)", s_face["status"] == "matched" and s_face["f_max"] == 0.0)
    check("short at f = 0 asks for f*_lo(C1) next (side)", s_side["status"] == "searching" and s_side["next"] == 0.15)
    ids = [r["id"] for r in R10.build_runs(recs)]
    check("the runs are listed once", len(ids) == len(set(ids)))


def test_firth():
    from scipy.optimize import minimize
    rng = np.random.default_rng(1)
    for k in range(5):
        x = rng.normal(size=8)
        y = (rng.random(8) < 1 / (1 + np.exp(-2 * x))).astype(float)
        if y.sum() in (0, 8):
            y[0] = 1 - y[0]
        f = PC.firth(x, y)

        def neg(b):
            eta = b[0] + b[1] * x
            p = 1 / (1 + np.exp(-eta))
            X = np.column_stack([np.ones(8), x])
            I = X.T @ ((p * (1 - p))[:, None] * X)
            return -(np.sum(y * eta - np.logaddexp(0, eta)) + 0.5 * np.linalg.slogdet(I)[1])
        o = minimize(neg, [0.0, 0.0], method="Nelder-Mead", options={"xatol": 1e-12, "fatol": 1e-14, "maxiter": 20000})
        check(f"Firth's logistic against a direct maximisation ({k})", abs(f["a"] - o.x[0]) < 1e-5 and abs(f["b"] - o.x[1]) < 1e-5,
              f"{f['a']:.6f},{f['b']:.6f} vs {o.x[0]:.6f},{o.x[1]:.6f}")
    x = np.array([0, 0, 0, 0, 1, 1, 1, 1.0])
    y = np.array([0, 0, 0, 0, 1, 1, 1, 1.0])
    f = PC.firth(x, y)
    check("a separating predictor stays finite", math.isfinite(f["b"]) and f["b"] > 0, f"{f['b']:.3f}")
    c = PC.firth(None, np.array([1, 1, 1, 1, 1, 0, 0, 0.0]))
    check("the constant is (k + 1/2) / (n + 1)", abs(c["p"] - 5.5 / 9) < 1e-15)
    # D108: the near-separating training half on which V3 found the Fisher-scoring steps short of the maximum
    xs = np.array([0.0, 0.0, 0.08125, 0.0, 0.0, 0.0, 0.0, 0.00625])
    ys = np.array([0, 0, 1, 1, 1, 1, 1, 0.0])
    f = PC.firth(xs, ys)

    def neg2(b):
        eta = b[0] + b[1] * xs
        p = 1 / (1 + np.exp(-eta))
        X = np.column_stack([np.ones(8), xs])
        I = X.T @ ((p * (1 - p))[:, None] * X)
        return -(np.sum(ys * eta - np.logaddexp(0, eta)) + 0.5 * np.linalg.slogdet(I)[1])
    o = minimize(neg2, [0.27, 8.8], method="Nelder-Mead", options={"xatol": 1e-12, "fatol": 1e-15, "maxiter": 40000})
    check("Firth's logistic converges near separation (D108)", f["converged"] and abs(f["a"] - o.x[0]) < 1e-7
          and abs(f["b"] - o.x[1]) < 1e-5, f"{f['a']:.9f},{f['b']:.7f} vs {o.x[0]:.9f},{o.x[1]:.7f}")


def test_heldout_rank():
    from scipy.stats import spearmanr
    rows = []
    for i in range(16):
        rows.append({"test": f"t{i}", "connection": "series" if i < 8 else "parallel", "y": int(i % 2 == 0),
                     "fC1": float(i % 2 == 0) + 0.01 * i, "fC2": float(i), "f9": 0.5, "time_s": 100.0 + i if i % 2 == 0 else None,
                     "E_b_J": 1000.0 + 13 * i, "peak_away_f0": 50.0 + (i * 7) % 11, "t_c1_f0": None if i % 3 else 20.0 + i})
    ho = PC.heldout(rows, n_perm=500, seed=3)
    check("a predictor equal to the outcome beats the constant held out",
          ho["predictors"]["fC1"]["series_to_parallel"]["observed"]["d_log"] > 0.2
          and ho["predictors"]["fC1"]["series_to_parallel"]["p_log"] < 0.05)
    check("a constant predictor does not", abs(ho["predictors"]["f9"]["series_to_parallel"]["observed"]["d_log"]) < 1e-9)
    a = [r["peak_away_f0"] for r in rows]
    b = [r["E_b_J"] for r in rows]
    check("Spearman's rho with ties against scipy's", abs(PC.spearman(a, b) - spearmanr(a, b)[0]) < 1e-12)
    v = [r["t_c1_f0"] for r in rows]
    vv = [1e9 if x is None else x for x in v]
    check("a crossing that did not happen ranks above every number", abs(PC.spearman(v, b) - spearmanr(vv, b)[0]) < 1e-12)
    rk = PC.rank(rows, n_perm=500, seed=3)
    check("the ranking runs on every quantity", all("outcome" in rk["quantities"][q] for q in PC.QUANTITIES))


def test_scorecard():
    w = lambda rms, rise, meas=22.8: {"window": {"rms_K": rms, "rise_last_model_K": rise, "rise_last_measured_K": meas}}
    a = {f"{k}_hcentral": {"nodes": {"away": w(*v)}} for k, v in
         {"tri21_C2_lo": (30.0, 20.0), "tri21_C2_hi": (24.0, 50.0), "con240_C2": (20.0, 5.0), "con360_C2": (22.0, 9.0),
          "con360_C1": (23.0, 25.0)}.items()}
    P = SC.scorecard(a, None, None, None, None, None)
    check("P1 holds at one bracket end below 25 K", P["P1"]["holds"])
    check("P2 needs every long reading below the short one's best", P["P2"]["holds"])
    check("P3 fails where the measured rise is not above 30 K", not P["P3"]["holds"] and not P["P3"]["parts"]["measured_above_30_K"])


def main():
    test_metrics()
    test_chains()
    test_firth()
    test_heldout_rank()
    test_scorecard()
    test_nodes()
    test_bitwise()
    print(("all tests passed" if not FAILS else f"{len(FAILS)} FAILED: {FAILS}"), flush=True)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
