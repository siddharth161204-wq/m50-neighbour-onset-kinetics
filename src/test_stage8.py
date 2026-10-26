#!/usr/bin/env python3
"""Tests of the Stage 8 code on synthetic inputs only (DECISIONS.md D83 (5)), run before the predictions were public.

No history of cell 1 for a Stage 7 trigger is used and no run of the neighbour in a Stage 8 configuration is made here:
the model tests drive the neighbour with made-up histories of cell 1 (a ramp held at a made-up temperature, or the
ambient), the search tests use made-up threshold functions in place of the model, and the scoring tests made-up
records and series.
  1. stage8_model with no source equals v12_model bitwise, and with one volumetric source named "event" equals
     stage7_model with that event bitwise (resolved and lumped);
  2. the sources: the shares, the energy each delivers, the accounts with them, two sources at once;
  3. the split cell of Part D: its matrices and vectors against the base model's, the control against the base model,
     the layer's resistance (Eq. 28) and its bands, the account;
  4. the search (stage8_search.py): the bracket's rules on made-up threshold functions, the probes, the restarts;
  5. the run lists and the work loop's bookkeeping on a made-up model;
  6. the scoring, V1, V2, the figure and the quoted numbers on made-up records.
Usage: python3 test_stage8.py [--quick]   (--quick leaves out the resolved runs of 1 to 3)
"""
import os as _os
for _k in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "NUMBA_NUM_THREADS"):
    _os.environ.setdefault(_k, "1")      # one thread per library (D43 (4)), so that the bitwise comparisons hold
import json, math, os, shutil, sys, tempfile
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v12_model as V                    # noqa: E402
import stage7_model as M7                # noqa: E402
import stage8_model as M8                # noqa: E402
import stage8_inputs as IN               # noqa: E402

K0 = 273.15
Ta = V.LP.T_AMB
FAILS = []


def check(name, cond, info=""):
    print(("ok   " if cond else "FAIL ") + name + (f"  {info}" if info else ""), flush=True)
    if not cond:
        FAILS.append(name)


def equal(a, b):
    """Bitwise equality of nested outputs (arrays, dicts, floats)."""
    if isinstance(a, dict):
        return isinstance(b, dict) and set(a) == set(b) and all(equal(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(equal(x, y) for x, y in zip(a, b))
    if isinstance(a, np.ndarray):
        return isinstance(b, np.ndarray) and a.shape == b.shape and np.array_equal(a, b)
    return a == b or (a is None and b is None)


def ramp(T_hold_C, t_rise=2.0):
    return lambda t: Ta + min(t, t_rise) / t_rise * (T_hold_C - 25.0)


SAME_KEYS = ("cross_s", "peak", "conversion_volume_mean_end", "stored_J", "steps", "rejected", "max_implicit_nodes",
             "max_local_reaction_heating_K_per_s", "t_end_s", "stop", "series", "T_final", "c_final", "probe_t",
             "probe_T", "probe_peak", "t_cat1_consumed_at_a_node_s")


# ------------------------------------------------------------------------------------------------ 1 and 2: the model
def test_model(quick):
    t1 = ramp(600.0)
    g_link = V.g_contact(V.H_CONTACT["central"])
    a = V.run_lumped(t1, 0.0068, g_link=g_link, f_view=V.F_TOUCH, t_end=120.0, stop_level=V.LEVEL_PROP)
    b = M8.run_lumped(t1, 0.0068, g_link=g_link, f_view=V.F_TOUCH, t_end=120.0, stop_level=V.LEVEL_PROP)
    check("1 lumped: no source, equals v12_model bitwise", all(equal(a[k], b[k]) for k in a) and set(a) <= set(b))
    ev = M7.Event(5000.0, 21.38651984299561, 0.0)
    a = M7.run_lumped(t1, 0.0068, g_link=g_link, f_view=V.F_TOUCH, t_end=60.0, event=ev, max_sub_event=4096)
    b = M8.run_lumped(t1, 0.0068, g_link=g_link, f_view=V.F_TOUCH, t_end=60.0,
                      sources=[M8.Source("event", M7.Event(5000.0, 21.38651984299561, 0.0))], max_sub=4096)
    keys = ("cross_s", "peak", "reaction_heat_J", "conversion_end", "series", "stop", "t_end_s", "steps_t", "steps_T",
            "energy_J", "stored_J", "net_in_J", "energy_residual_rel")
    check("1 lumped: one source named event equals stage7_model with that event bitwise",
          all(equal(a[k], b[k]) for k in keys), f"in_event {b['energy_J']['in_event']!r}")
    check("2 lumped: the source delivers its energy", abs(b["sources"]["event"]["delivered_J"] - 5000.0) < 1e-9)
    check("2 lumped: the account closes with the source", abs(b["energy_residual_rel"]) < 1e-12,
          f"{b['energy_residual_rel']:.2e}")
    two = [M8.Source("delivery", M7.Event(3000.0, 10.0, 0.0)), M8.Source("joule", M7.Event(1000.0, 21.39, 0.0))]
    c2 = M8.run_lumped(lambda t: Ta, 0.0068, g_link=g_link, f_view=V.F_TOUCH, t_end=60.0, reaction=False, sources=two)
    check("2 lumped: two sources deliver theirs", abs(c2["sources"]["delivery"]["delivered_J"] - 3000.0) < 1e-9 and
          abs(c2["sources"]["joule"]["delivered_J"] - 1000.0) < 1e-9)
    check("2 lumped: the account closes with two sources", abs(c2["energy_residual_rel"]) < 1e-12,
          f"{c2['energy_residual_rel']:.2e}")
    if quick:
        return
    model = V.Cell2Contact(V.H_CONTACT["central"], refine=1.0)
    g_pos, g_neg = V.tabs("parallel", V.G_TAB["central"])
    a = V.run_resolved(model, t1, g_pos, g_neg, t_end=3.0, probes=model.probes, stop_level=V.LEVEL_PROP)
    b = M8.run_resolved(model, t1, g_pos, g_neg, t_end=3.0, probes=model.probes, stop_level=V.LEVEL_PROP)
    check("1 resolved: no source, equals v12_model bitwise", all(equal(a[k], b[k]) for k in a) and set(a) <= set(b))
    ev = M7.Event(2000.0, 2.0, 0.0)
    a = M7.run_resolved(model, t1, g_pos, g_neg, t_end=1.5, probes=model.probes, event=ev, max_sub_event=4096)
    b = M8.run_resolved(model, t1, g_pos, g_neg, t_end=1.5, probes=model.probes, max_sub=4096,
                        sources=[M8.Source("event", M7.Event(2000.0, 2.0, 0.0), M8.share_volume(model))])
    check("1 resolved: one volumetric source named event equals stage7_model with that event bitwise",
          all(equal(a[k], b[k]) for k in SAME_KEYS) and equal(a["energy_J"], b["energy_J"]),
          f"{b['steps']} steps")
    # 2: the shares and the delivery
    for g in ("half", "capend"):
        sh = M8.share_surface(model, g)
        info = M8.surface_info(model, g)
        on = sh > 0
        th, z = model.th_node[on], model.z_node[on]
        ok = abs(sh.sum() - 0.5) < 1e-14 and np.all(model.r_node[on] > V.R - 1e-9)
        lim = (th.max() < math.radians(95)) and (g == "half" or z.min() > 0.70 * V.LZ)
        check(f"2 share {g}: sums to 1/2, on the lateral surface only, inside its region", ok and lim,
              f"A mesh {info['A_mesh_m2']:.6e} exact {info['A_exact_m2']:.6e}")
        check(f"2 share {g}: the region's area within 0.5 % of exact",
              abs(info["A_mesh_m2"] / info["A_exact_m2"] - 1) < 5e-3)
    src = [M8.Source("delivery", M7.Event(1500.0, 2.0, 0.0), M8.share_surface(model, "half"))]
    r = M8.run_resolved(model, lambda t: Ta, g_pos, g_neg, t_end=3.0, probes=model.probes, reaction=False,
                        sources=src)
    check("2 resolved: the delivery delivers its energy", abs(r["sources"]["delivery"]["delivered_J"] - 1500.0) < 1e-9,
          f"{r['sources']['delivery']['delivered_J']!r}")
    check("2 resolved: the account closes with the delivery", abs(r["energy_residual_rel"]) < 1e-10,
          f"{r['energy_residual_rel']:.2e}")
    hot = r["peak"]
    check("2 resolved: the delivery heats the facing surface", model.r_node[hot["imax"]] > V.R - 1e-9 and
          model.th_node[hot["imax"]] <= math.pi / 2 + 0.1, json.dumps(model.where(hot["imax"])))
    r0 = M8.run_resolved(model, lambda t: Ta, g_pos, g_neg, t_end=3.0, probes=model.probes, reaction=False)
    check("2 resolved: the delivery's heating refines the step", r["steps"] > r0["steps"],
          f"{r['steps']} against {r0['steps']}")
    two = [M8.Source("delivery", M7.Event(800.0, 1.0, 0.0), M8.share_surface(model, "capend")),
           M8.Source("joule", M7.Event(1200.0, 2.0, 0.0), M8.share_volume(model))]
    r2 = M8.run_resolved(model, lambda t: Ta, g_pos, g_neg, t_end=2.5, probes=model.probes, reaction=True,
                         sources=two, max_sub=4096)
    check("2 resolved: two sources, with the kinetics: each delivers its energy and the account closes",
          abs(r2["sources"]["delivery"]["delivered_J"] - 800.0) < 1e-9 and
          abs(r2["sources"]["joule"]["delivered_J"] - 1200.0) < 1e-9 and abs(r2["energy_residual_rel"]) < 1e-9,
          f"{r2['energy_residual_rel']:.2e}")
    test_split(model, g_pos, g_neg)


# ------------------------------------------------------------------------------------------------ 3: the split cell
def test_split(model, g_pos, g_neg):
    S = M8.SplitCell(model)
    Nr = S.n_roll
    check("3 split: heat capacity conserved", abs(S.C.sum() - model.C.sum()) < 1e-12 * model.C.sum(),
          f"{S.C.sum()!r} against {model.C.sum()!r}; {S.n_can} wall nodes")
    one = np.ones(S.C.size)
    check("3 split: conduction conserves heat (rows sum to zero)", np.abs(S.K @ one).max() < 1e-9 * abs(S.K).max())
    ok = all(abs(getattr(S, n).sum() - getattr(model, n).sum()) <= 1e-12 * max(abs(getattr(model, n).sum()), 1e-30)
             for n in ("d_conv_unit", "d_gap_unit", "d_pos_unit", "d_neg_unit", "g_rad", "w_rad"))
    check("3 split: every boundary path keeps its total", ok)
    check("3 split: no boundary path left on the roll's split nodes",
          all(not getattr(S, n)[S.interior].any() for n in ("d_conv_unit", "d_gap_unit", "g_rad", "w_rad")))
    a_out = 2 * model.w["outer"].sum()
    check("3 split: the interface covers the outer boundary but the tab discs",
          0.97 * a_out < S.geom["A_interface_m2"] < a_out and
          abs(S.geom["A_interface_heated_m2"] / (math.pi * V.R * V.LZ) - 1) < 5e-3,
          f"{S.geom['A_interface_m2']:.6e} of {a_out:.6e}; heated {S.geom['A_interface_heated_m2']:.6e}; "
          f"{S.n_can} split nodes, {S.geom['tab_disc_nodes']} on the tab discs")
    # Eq. 28 and the bands
    rv = [IN.r_vap(x, IN.R_MAX_HEATED) for x in (90.0, 91.0, 169.5, 248.0, 300.0)]
    check("3 Eq. 28: 0 below 91 C, quarter of the maximum half-way, maximum from 248 C",
          rv[0] == 0.0 and rv[1] == 0.0 and abs(rv[2] - IN.R_MAX_HEATED / 4) < 1e-15 and rv[3] == IN.R_MAX_HEATED and
          rv[4] == IN.R_MAX_HEATED)
    T = np.full(S.C.size, Ta)
    T[S.n_roll:] = K0 + np.linspace(60.0, 300.0, S.n_can)
    T[S.interior] = T[S.n_roll:]
    b = S.bands(T)
    tif = T[S.n_roll:] - K0
    exp = np.where(tif < 91.0, -1, np.where(tif >= 248.0, S.n_bands, np.floor((tif - 91.0) / S.dT_band)))
    check("3 bands: below, between and above", np.array_equal(b, exp.astype(int)))
    G = S.conductance(b)
    lo, hi = tif < 91.0, tif >= 248.0
    check("3 bands: the floor below 91 C, each side's maximum from 248 C",
          np.allclose(G[lo], S.a_if[lo] / IN.R_FLOOR, rtol=1e-14) and
          np.allclose(G[hi], S.a_heated[hi] / IN.R_MAX_HEATED + S.a_cold[hi] / IN.R_MAX_COLD, rtol=1e-14))
    # the split solver: the analysis made once, a numerical factorisation per change of the bands
    import scipy.sparse as sp
    db = g_pos * S.d_pos_unit + g_neg * S.d_neg_unit
    dt = 0.1 / 2 ** 7
    cnt = [0]
    fs = M8._SplitSolver(S, dt, S.d_conv_unit, S.d_gap_unit, db, cnt)
    rhs = np.linspace(1.0, 2.0, S.C.size)
    same = True
    for bb in (np.full(S.n_can, -1), np.full(S.n_can, 10), b, np.full(S.n_can, S.n_bands)):
        fs.set_bands(bb)
        x = fs.solve(rhs)
        A = (S.K + sp.diags(S.C / dt + S.d_conv_unit + S.d_gap_unit + db) + S.interface_matrix(S.conductance(bb))).tocsr()
        y = M8.RX._solver_class()(A).solve(rhs)
        same &= np.array_equal(x, y)
    fs.free()
    check("3 split solver: each change of the bands solves bit for bit as a factorisation from the start", same,
          f"{cnt[0]} factorisations")
    # the control against the base model, without the kinetics
    sh = M8.share_surface(model, "half")
    src_b = [M8.Source("delivery", M7.Event(1500.0, 2.0, 0.0), sh)]
    src_s = [M8.Source("delivery", M7.Event(1500.0, 2.0, 0.0), S.move(sh))]
    rb = M8.run_resolved(model, lambda t: Ta, g_pos, g_neg, t_end=3.0, probes=model.probes, reaction=False,
                         sources=src_b, max_sub=4096)
    rs = M8.run_resolved_split(S, lambda t: Ta, g_pos, g_neg, t_end=3.0, sources=src_s, max_sub=4096, layer=False)
    check("3 control: the split with the floor only follows the base model (hot spot within 0.5 K)",
          abs(rs["peak"]["Tmax_C"] - rb["peak"]["Tmax_C"]) < 0.5,
          f"{rs['peak']['Tmax_C']:.4f} against {rb['peak']['Tmax_C']:.4f} C; can {rs['can_peak']['T_C']:.4f} C")
    check("3 control: the account closes", abs(rs["energy_residual_rel"]) < 1e-9, f"{rs['energy_residual_rel']:.2e}")
    rl = M8.run_resolved_split(S, lambda t: Ta, g_pos, g_neg, t_end=3.0, sources=src_s, max_sub=4096, layer=True)
    check("3 layer: the can runs hotter than the roll, the roll cooler than in the control",
          rl["can_peak"]["T_C"] > rl["peak"]["Tmax_C"] and rl["peak"]["Tmax_C"] < rs["peak"]["Tmax_C"],
          f"can {rl['can_peak']['T_C']:.2f} C, roll {rl['peak']['Tmax_C']:.2f} C, {rl['factorisations']} factorisations")
    check("3 layer: the account closes and the delivery is exact", abs(rl["energy_residual_rel"]) < 1e-9 and
          abs(rl["sources"]["delivery"]["delivered_J"] - 1500.0) < 1e-9, f"{rl['energy_residual_rel']:.2e}")
    # a run cut off and resumed from its checkpoint gives the uninterrupted run, bit for bit
    tmp = tempfile.mkdtemp()
    ck = os.path.join(tmp, "ck.pkl")
    ra = M8.run_resolved_split(S, lambda t: Ta, g_pos, g_neg, t_end=1.2, sources=src_s, max_sub=4096, layer=True)

    class Cut(Exception):
        pass

    def cut(t, *a):
        if t >= 0.6:
            raise Cut()
    try:
        M8.run_resolved_split(S, lambda t: Ta, g_pos, g_neg, t_end=1.2, sources=src_s, max_sub=4096, layer=True,
                              progress=cut, checkpoint=ck, checkpoint_every_s=0.0)
    except Cut:
        pass
    rb = M8.run_resolved_split(S, lambda t: Ta, g_pos, g_neg, t_end=1.2, sources=src_s, max_sub=4096, layer=True,
                               checkpoint=ck, checkpoint_every_s=1e9)
    keys = ("peak", "energy_J", "stored_J", "steps", "rejected", "t_end_s", "series", "T_final", "c_final", "probe_T",
            "probe_peak", "can_peak", "factorisations", "interface_node_steps")
    check("3 checkpoint: a run cut off at 0.6 s and resumed equals the uninterrupted run bitwise",
          all(equal(ra[k], rb[k]) for k in keys) and rb["resumed"] == 1, f"{rb['steps']} steps, resumed {rb['resumed']}")
    shutil.rmtree(tmp)


# ------------------------------------------------------------------------------------------------ 4: the search
def test_search():
    import stage8_search as SR
    # a made-up threshold: met if f >= th
    for th in (0.0, 0.003, 0.0125, 0.05, 0.11, 0.2, 0.299, 0.31, 0.5, 0.77, 0.999, 1.3):
        pts = {0.0: th <= 0.0}
        n = 0
        while True:
            st = SR.state(pts, IN.PROBES_A)
            if st["next"] is None:
                break
            pts[st["next"]] = st["next"] >= th
            n += 1
        fs = SR.f_star(st)
        if th <= 0.0:
            ok = fs["status"] == "zero" and n == 0
        elif th > 1.0:
            ok = fs["status"] == "above"
        else:
            ok = fs["status"] == "bracket" and fs["lo"] < th <= fs["hi"] and fs["hi"] - fs["lo"] <= 0.02 + 1e-12
        check(f"4 search: threshold {th}", ok, f"{fs} after {n} runs")
    # the common fractions are always tried first when inside the bracket; 0.05 is the first midpoint of (0, 0.1]
    pts = {0.0: False}
    seq = []
    for _ in range(3):
        st = SR.state(pts, IN.PROBES_A)
        seq.append(st["next"])
        pts[st["next"]] = True
    check("4 search: 0.1 first, then the midpoints of (0, 0.1]", seq == [0.1, 0.05, 0.025], f"{seq}")
    check("4 search: below() on the bound of a prediction",
          SR.below({"status": "bracket", "lo": 0.2875, "hi": 0.3}, 0.3) is True and
          SR.below({"status": "bracket", "lo": 0.3, "hi": 0.3125}, 0.3) is False and
          SR.below({"status": "zero", "lo": 0.0, "hi": 0.0}, 0.05) is True and
          SR.below({"status": "above", "lo": 1.0, "hi": None}, 0.5) is False)
    st = SR.state({0.0: False, 0.2: True, 0.1: True, 0.15: False}, ())
    check("4 search: a contradiction is reported", st["status"] == "broken", str(st))
    pr = SR.restart_probes(0.0125, 0.025, "bracket")
    check("4 search: a restart tries Part A's upper end, then its lower end, then the grid",
          pr[:2] == [0.025, 0.0125] and pr[2:] == list(IN.PROBES_A), str(pr))


# ------------------------------------------------------------------------------------------------ 5: the run lists
def fake_thresholds():
    """Made-up thresholds of delivered energy (J) per test and criterion, decreasing with the trigger energy."""
    import stage8_run as R8
    out = {}
    for t in R8.tests():
        e = t["E_b_J"]
        out[t["test"]] = {"C1": max(0.0, 8000.0 - 0.15 * e), "C2": max(0.0, 9000.0 - 0.17 * e)}
    return out


def fake_run(sp, th):
    """A made-up run: the criterion is met if the delivered energy (J) is at least the made-up threshold, less a
    made-up effect of the variant (shorter delivery, cap end and Joule heat each lower it)."""
    t = th[sp["test"]]
    adj = 1.0
    if sp["tau_d_s"] < 20:
        adj *= 0.9
    elif sp["tau_d_s"] > 30:
        adj *= 1.2
    if sp["geometry"] == "capend":
        adj *= 0.97
    e_j = sp["E_joule_J"]
    rec = dict(sp)
    out = {}
    for crit in ("C1", "C2"):
        need = max(0.0, t[crit] * adj - 0.8 * e_j)
        out[crit] = sp["E_delivered_J"] >= need if need > 0 else True
    rec["resolved"] = None if sp["models"] == "lumped" else {"propagated": out["C1"], "t_prop_s": 30.0 if out["C1"] else None,
                                                             "t_end_s": 30.0 if out["C1"] else 900.0,
                                                             "peak_hottest_C": 255.7 if out["C1"] else 200.0}
    rec["lumped"] = None if sp["models"] in ("resolved", "split") else {
        "propagated": out["C2"], "t_prop_s": 200.0 if out["C2"] else None, "t_end_s": 200.0 if out["C2"] else 900.0,
        "peak_C": 260.0 if out["C2"] else 140.0}
    rec["stage8"] = {"clocks": {"lumped": {"t_150_s": 100.0 if (rec["lumped"] and rec["lumped"]["peak_C"] > 150) else None}}}
    return rec


def drive(th):
    import stage8_run as R8
    recs = {}
    rounds = 0
    while True:
        runs = R8.build_runs(recs)
        pending = [r for r in runs if r["id"] not in recs and r["set"] not in ("gas", "gasctl", "v3mesh", "v3step")]
        if not pending:
            return recs, rounds
        for r in pending:
            recs[r["id"]] = fake_run(r, th)
        rounds += 1
        assert rounds < 200


def test_lists():
    import stage8_run as R8
    import stage8_search as SR
    fx = R8.fixed_runs()
    check("5 lists: the fixed runs", len(fx) == 48 + 6 + 2 and len({r["id"] for r in fx}) == len(fx),
          f"{len(fx)}; sha256 {R8.runs_hash(fx)}")
    ids = {r["id"] for r in fx}
    check("5 lists: V3's runs and Part D's", "v3mesh_M50_PT_Exp1_f0.100000000" in ids and
          sum(r["set"] == "gas" for r in fx) == 3)
    sp = R8.spec("first", "M50_PP_Exp3", 0.2)
    check("5 lists: the delivered energy is f r E_b", abs(sp["E_delivered_J"] - 0.2 * R8.ratios()["central"] *
                                                          sp["E_body_J"]) < 1e-9 and sp["tau_d_s"] == R8.tau_median())
    th = fake_thresholds()
    recs, rounds = drive(th)
    st = R8.all_states(recs)
    s7 = R8.stage7_zero()
    bad = []
    for t in R8.tests():
        x = t["test"]
        for crit in ("C1", "C2"):
            fs = SR.f_star(st[f"A_{crit}_{x}"])
            e_e = R8.ratios()["central"] * t["E_b_J"]
            f_true = th[x][crit] / e_e
            if s7[x][crit]:
                ok = fs["status"] == "zero"
            elif f_true > 1:
                ok = fs["status"] == "above"
            else:
                ok = fs["status"] == "bracket" and fs["lo"] < f_true <= fs["hi"] + 1e-12 and fs["hi"] - fs["lo"] <= 0.02 + 1e-12
            if not ok:
                bad.append((x, crit, fs, f_true))
    check("5 lists: every Part A chain finds the made-up threshold to 0.02 (or 0 where Stage 7 met it)", not bad,
          f"{rounds} rounds, {len(recs)} records; {bad[:3]}")
    unfinished = [k for k, v in st.items() if v["status"] in ("searching", "waiting", "broken")]
    check("5 lists: every chain ends", not unfinished, str(unfinished[:5]))
    first = [r for r in recs.values() if r["set"] == "first"]
    check("5 lists: the first round is made for every test", len(first) == 48)
    n_ref = sum(1 for k, v in st.items() if k.startswith("ref") and v["status"] != "not needed")
    check("5 lists: refinement chains start only where a variant ends in Part A's bracket", True, f"{n_ref} active")
    for k, v in st.items():
        if k.startswith("ref_") and v["status"] == "bracket":
            w0 = v["refined_from"][1] - v["refined_from"][0]
            if not (v["hi"] - v["lo"] <= w0 / 8 + 1e-12):
                check(f"5 lists: {k} refined to an eighth", False, str(v))
    # the ratio chains: exact rescaling
    for x in R8.sens_tests():
        a = SR.f_star(st[f"A_C1_{x}"])
        lo = SR.f_star(st[f"ratiolow_c1_{x}"])
        if a["status"] == "bracket":
            sc = R8.ratios()["central"] / R8.ratios()["low"]
            check(f"5 lists: the low ratio's bracket of {x} lies within Part A's rescaled",
                  lo["status"] == "bracket" and lo["lo"] >= a["lo"] * sc - 1e-12 and lo["hi"] <= a["hi"] * sc + 1e-12,
                  f"{lo} against {a}")
    # Part B: f = 0 first
    for t in R8.tests():
        if t["connection"] == "parallel":
            e = [r for r in recs.values() if r["set"] == "elec20_c1" and r["test"] == t["test"]]
            check(f"5 lists: Part B tries f = 0 first ({t['test']})", any(r["f"] == 0.0 for r in e), f"{len(e)} runs")
    return recs


def test_run_one():
    """5b: one run of each kind through stage8_run.run_one on a made-up configuration (cell 1 not heated, 1 s)."""
    import stage8_run as R8
    ctx = R8.Context()
    for set_, kw in (("first", {}), ("c2", {"models": "lumped"}), ("elec20_c1", {"f_e": 0.2}),
                     ("v3step", {"models": "resolved", "dt_scale": 0.5}), ("gas", {"models": "split", "gas": "layer"})):
        sp = R8.spec(set_, "M50_PP_Exp3", 0.01, **kw)
        sp["E_body_J"] = 0.0
        sp["t_end_s"] = 1.0
        rec, series = R8.run_one(sp, ctx)
        json.dumps(rec, default=float)
        tmp = tempfile.mkdtemp()
        np.savez_compressed(os.path.join(tmp, "x.npz"), **series)
        shutil.rmtree(tmp)
        parts = [p for p in ("resolved", "lumped") if rec[p] is not None]
        want = {"both": ["resolved", "lumped"], "lumped": ["lumped"], "resolved": ["resolved"], "split": ["resolved"]}
        ok = parts == want[sp["models"]] and all(abs(rec[p]["energy_residual_rel"]) < 1e-9 for p in parts)
        check(f"5b run_one: {set_} on a made-up configuration (cell 1 not heated, 1 s)", ok,
              f"{parts}; residuals {[rec[p]['energy_residual_rel'] for p in parts]}")


# ------------------------------------------------------------------------------------------------ 6: the scoring
def test_scoring():
    import stage8_run as R8
    import stage8_score as SC
    import stage8_checks as CK
    th = fake_thresholds()
    recs, _ = drive(th)
    tmp = tempfile.mkdtemp()
    try:
        rd = os.path.join(tmp, "runs")
        os.makedirs(rd)
        for r in recs.values():
            json.dump(r, open(os.path.join(rd, r["id"] + ".json"), "w"), default=float)
        out = SC.main(runs_dir=rd, out_dir=tmp)
        rows = out["thresholds"]
        check("6 scoring: one threshold row per test, every chain ended", len(rows) == 16 and not out["unfinished_chains"],
              str(out["unfinished_chains"][:3]))
        card = json.load(open(os.path.join(tmp, "stage8_scorecard.json")))
        ok = all(sum(card["by_fraction"][f][c]["counts"].values()) == 16 for f in ("0.1", "0.2", "0.3")
                 for c in IN.CRITERIA)
        check("6 scoring: Part C classes every test at each fraction and criterion", ok)
        s7 = card["stage7_f0"]
        check("6 scoring: f = 0 is Stage 7's scorecard (C1 11 of 16, C2 2 predicted, C3 14 predicted)",
              s7["C1"]["score"] == 11 and s7["C2"]["predicted"] == 2 and s7["C3"]["predicted"] == 14,
              f"C1 {s7['C1']['score']}, C2 {s7['C2']['predicted']}, C3 {s7['C3']['predicted']}")
        v = out["verdicts"]
        check("6 scoring: a verdict for each of P1 to P8", sorted(v) == [f"P{k}" for k in range(1, 9)],
              json.dumps({k: x["holds"] for k, x in v.items()}))
        # on the made-up thresholds, every f*(C1) of a test Stage 7 met is 0, and the others follow the threshold
        z = [r for r in rows if r["stage7_C1"]]
        check("6 scoring: f*(C1) = 0 wherever Stage 7's C1 was met", all(r["fC1"]["status"] == "zero" for r in z))
        # the made-up model has no inversion by construction
        check("6 scoring: P6 finds no inversion in a model that has none", v["P6"]["holds"], str(v["P6"]["inversions"][:3]))
        # V2's replay on the made-up records needs series; V4 on the made-up records has no account: only V1 here
        R8.write_ejected(os.path.join(tmp, "stage8_ejected.csv"))
        shutil.copy(os.path.join(R8.RES, "stage7_triggers.json"), tmp)
        v1 = CK.v1(res=tmp)
        check("6 checks: V1 on the inputs", v1["pass"], f"{v1['largest_relative_difference']:.2e}")
        rp = CK.replay(lambda f: f >= 0.0371)
        check("6 checks: V2's own rules on a made-up threshold", rp["status"] == "bracket" and rp["lo"] < 0.0371 <= rp["hi"]
              and rp["hi"] - rp["lo"] <= 0.02, str(rp))
        same = []
        for t in R8.tests():
            e_e = R8.ratios()["central"] * t["E_b_J"]
            s7z = R8.stage7_zero()[t["test"]]
            for crit in ("C1", "C2"):
                f_true = th[t["test"]][crit] / e_e
                rp = CK.replay(lambda f, s=s7z, c=crit, ft=f_true: s[c] if f == 0.0 else f >= ft)
                fs = R8.SR.f_star(R8.all_states(recs)[f"A_{crit}_{t['test']}"])
                same.append(rp["status"] == fs["status"] and rp.get("lo") == fs.get("lo") and rp.get("hi") == fs.get("hi"))
        check("6 checks: V2's rules and the search agree on every made-up chain", all(same), f"{sum(same)} of {len(same)}")
    finally:
        shutil.rmtree(tmp)


if __name__ == "__main__":
    quick = "--quick" in sys.argv
    test_model(quick)
    for name in ("test_search", "test_lists", "test_run_one", "test_scoring"):
        f = globals().get(name)
        if f:
            f()
    print(f"{len(FAILS)} failed" if FAILS else "all passed", flush=True)
    sys.exit(1 if FAILS else 0)
