#!/usr/bin/env python3
"""Tests of the Stage 7 code on synthetic inputs only (DECISIONS.md D70 (4)), run before the predictions were public.

No history of cell 1 for a Stage 7 trigger and no run of the neighbour in a Stage 7 configuration is computed here:
the model tests drive the neighbour with made-up histories of cell 1 (a ramp held at a made-up temperature, or the
ambient), the trigger tests use a made-up function in place of cell 1's peak, and the scoring tests use made-up
records and series.
  1. stage7_model with the fresh state and no event equals v12_model bitwise (resolved and lumped);
  2. the event: its pulse, the energy it delivers, and the energy accounts with it (resolved and lumped);
  3. the aged initial state, and an aged lumped run against a fresh one;
  4. the Part B quantities and crossings on piecewise-linear histories, where every interpolated crossing is exact;
  5. the bisection, its out-of-range rule, the triggers file and V1 on it;
  6. the run lists: Part A, and Part C's rule from synthetic Part A records and series;
  7. the scoring (stage7_score.py), V2 and the figure on synthetic records.
Usage: python3 test_stage7.py [--quick]   (--quick leaves out the resolved runs of 1 and 2)
"""
import json, math, os, shutil, subprocess, sys, tempfile
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v12_model as V                    # noqa: E402
import stage7_model as M                 # noqa: E402
import stage7_inputs as IN               # noqa: E402
import stage7_criteria as CQ             # noqa: E402
import stage7_run as R7                  # noqa: E402
import stage7_checks as CK               # noqa: E402

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


# ------------------------------------------------------------------------------------------------ 1 and 2: the model
def test_model(quick):
    t1 = ramp(600.0)
    g_link = V.g_contact(V.H_CONTACT["central"])
    a = V.run_lumped(t1, 0.0068, g_link=g_link, f_view=V.F_TOUCH, t_end=120.0, stop_level=V.LEVEL_PROP)
    b = M.run_lumped(t1, 0.0068, g_link=g_link, f_view=V.F_TOUCH, t_end=120.0, stop_level=V.LEVEL_PROP)
    same = all(equal(a[k], b[k]) for k in a)
    check("1 lumped: fresh, no event, equals v12_model bitwise", same and set(a) <= set(b))
    check("1 lumped: the new account closes", abs(b["energy_residual_rel"]) < 1e-12, f"{b['energy_residual_rel']:.2e}")
    if not quick:
        model = V.Cell2Contact(V.H_CONTACT["central"], refine=1.0)
        g_pos, g_neg = V.tabs("series", V.G_TAB["central"])
        a = V.run_resolved(model, t1, g_pos, g_neg, t_end=3.0, probes=model.probes, stop_level=V.LEVEL_PROP)
        b = M.run_resolved(model, t1, g_pos, g_neg, t_end=3.0, probes=model.probes, stop_level=V.LEVEL_PROP)
        same = all(equal(a[k], b[k]) for k in a)
        check("1 resolved: fresh, no event, equals v12_model bitwise", same and set(a) == set(b))
        # 2: the event, without kinetics (energy only), and with them over a short window
        ev = M.Event(1000.0, 2.0, 0.55)
        r = M.run_resolved(model, lambda t: Ta, g_pos, g_neg, t_end=4.0, probes=model.probes, reaction=False, event=ev)
        check("2 resolved: the event delivers its energy", abs(r["event"]["delivered_J"] - 1000.0) < 1e-9,
              f"{r['event']['delivered_J']!r}")
        check("2 resolved: the account closes with the event", abs(r["energy_residual_rel"]) < 1e-10,
              f"{r['energy_residual_rel']:.2e}")
        check("2 resolved: the peak after the event is recorded", r["after_event"]["Tmax_C"] > 25.0 and
              r["after_event"]["t_Tmax_s"] > 0.55)
        r2 = M.run_resolved(model, lambda t: Ta, g_pos, g_neg, t_end=1.0, probes=model.probes, reaction=True,
                            event=M.Event(500.0, 0.5, 0.2))
        check("2 resolved: the account closes with the event and the kinetics", abs(r2["energy_residual_rel"]) < 1e-9,
              f"{r2['energy_residual_rel']:.2e}")
        n_ev = r["steps"]
        r0 = M.run_resolved(model, lambda t: Ta, g_pos, g_neg, t_end=4.0, probes=model.probes, reaction=False)
        check("2 resolved: the event's heating refines the step", n_ev > r0["steps"], f"{n_ev} against {r0['steps']}")
    ev = M.Event(65520.0, 21.38651984299561, 3.0)
    lr = M.run_lumped(lambda t: Ta, 0.0068, g_link=g_link, f_view=V.F_TOUCH, t_end=40.0, reaction=False, event=ev)
    check("2 lumped: the event delivers its energy", abs(lr["event"]["delivered_J"] - 65520.0) < 1e-7,
          f"{lr['event']['delivered_J']!r}")
    check("2 lumped: the account closes with the event", abs(lr["energy_residual_rel"]) < 1e-12,
          f"{lr['energy_residual_rel']:.2e}")
    # the pulse
    ts = np.linspace(0.0, 30.0, 300001)
    p = np.array([ev.power(t) for t in ts])
    num = float(np.sum(0.5 * (p[1:] + p[:-1]) * np.diff(ts)))
    check("2 pulse: its integral is the energy", abs(num - 65520.0) < 1e-3, f"{num:.6f}")
    check("2 pulse: cumulative at the ends and the middle", ev.cumulative(3.0) == 0.0 and ev.cumulative(40.0) == 65520.0
          and abs(ev.cumulative(3.0 + ev.tau / 2) - 32760.0) < 1e-9)
    check("2 pulse: largest power over an interval", ev.max_power(10.0, 20.0) == 2 * 65520.0 / ev.tau and
          ev.max_power(0.0, 2.0) == 0.0 and abs(ev.max_power(3.0, 4.0) - ev.power(4.0)) < 1e-12)


# ------------------------------------------------------------------------------------------------ 2b: the kernel
def test_kernel():
    import v12_kernel as KN
    import stage7_kernel as K7
    rng = np.random.default_rng(7)
    n = 400
    T = 400.0 + 500.0 * rng.random(n)
    c = V.bcrnn.fresh_state(n) * rng.uniform(0.0, 1.0, (V.bcrnn.NS, n))
    m, C = np.full(n, 1e-4), np.full(n, 0.1)
    fk = KN.FastKinetics(V.bcrnn.Kinetics(), m, C)
    R0, H0 = fk.start(T, c)
    for dt in (0.1, 0.0125, 0.00078125):
        a_ = KN.substeps(T, np.ascontiguousarray(c), R0, H0, dt, fk.m, fk.C, *fk.p)
        b_ = K7.substeps_max(T, np.ascontiguousarray(c), R0, H0, dt, fk.m, fk.C, *fk.p, 64)
        check(f"2b kernel: substeps_max with 64 equals v12_kernel.substeps bitwise (dt {dt})",
              all(np.array_equal(x, y) for x, y in zip(a_, b_)), f"{int(a_[2].sum())} nodes left implicit")
    g_link = V.g_contact(V.H_CONTACT["central"])
    ev = M.Event(65520.0, 21.38651984299561, 30.0)
    t1 = ramp(450.0, t_rise=20.0)
    a_ = M.run_lumped(t1, 0.0068, g_link=g_link, f_view=V.F_TOUCH, t_end=80.0, event=ev)
    b_ = M.run_lumped(t1, 0.0068, g_link=g_link, f_view=V.F_TOUCH, t_end=80.0, event=ev, max_sub_event=4096)
    k = int(np.searchsorted(a_["steps_t"], 30.0))
    check("2b lumped event run: identical before the event with the larger limit",
          np.array_equal(a_["steps_T"][:k], b_["steps_T"][:k]) and np.array_equal(a_["steps_t"][:k], b_["steps_t"][:k]))
    check("2b lumped event run: the account closes with the larger limit", abs(b_["energy_residual_rel"]) < 1e-12,
          f"{b_['energy_residual_rel']:.1e}; peak after the event {b_['after_event']['T_C']:.2f} C against "
          f"{a_['after_event']['T_C']:.2f} C")


# ------------------------------------------------------------------------------------------------ 3: the aged SEI
def test_aged():
    c = M.initial_state(3, 0.0)
    i = M.I_SEI
    check("3 aged state: SEI 0, the rest fresh", np.all(c[i] == 0.0) and
          np.array_equal(np.delete(c, i, axis=0), np.delete(V.bcrnn.fresh_state(3), i, axis=0)))
    t1 = ramp(450.0, t_rise=20.0)
    g_link = V.g_contact(V.H_CONTACT["central"])
    f = M.run_lumped(t1, 0.0068, g_link=g_link, f_view=V.F_TOUCH, t_end=200.0)
    a = M.run_lumped(t1, 0.0068, g_link=g_link, f_view=V.F_TOUCH, t_end=200.0, sei0=0.0)
    check("3 aged lumped run: less reaction heat than fresh on the same history",
          a["reaction_heat_J"] < f["reaction_heat_J"], f"{a['reaction_heat_J']:.1f} J against {f['reaction_heat_J']:.1f} J")
    check("3 aged lumped run: its SEI conversion is undefined", a["conversion_end"]["sei"] is None)
    check("3 inputs: 138.5 C is V0's separator peak", abs(IN.separator_melt_C() - IN.LEVEL_SEP_C) < 1e-9)
    check("3 inputs: the event energies", IN.E_EVENT_J == 65520.0 and IN.E_EVENT_LOW_J == 63360.0)


# ------------------------------------------------------------------------------------------------ synthetic records
def synth_series(P_hot, P_lum, t_hot=20.0, t_lum=250.0, stop_hot=None, stop_lum=None):
    """Piecewise-linear histories: each clock rises linearly from 25 C at t = 0 to its peak, then falls."""
    def h(P, tp, t):
        return np.where(t <= tp, 25.0 + (P - 25.0) * t / tp, P - (P - 25.0) * 0.5 * (t - tp) / (900.0 - tp)) + K0
    t = np.round(np.arange(0.0, 900.0 + 1e-9, 0.1), 10)
    tr = t if stop_hot is None else t[t <= stop_hot]
    tl = t if stop_lum is None else t[t <= stop_lum]
    return {"t": tr, "T1": h(500.0, 21.0, tr), "Tmax": h(P_hot, t_hot, tr), "Tmean": h(0.8 * P_hot, t_hot * 3, tr),
            "imax": np.zeros(tr.size, int), "probe_t": tr, "probe_toward": h(0.99 * P_hot, t_hot, tr),
            "probe_away": h(0.7 * P_hot, t_hot * 4, tr), "t_lumped": tl, "T_lumped": h(P_lum, t_lum, tl),
            "t1_t": tr, "t1_T1_C": h(500.0, 21.0, tr) - K0, "t1_T2_C": h(100.0, 200.0, tr) - K0}


def synth_record(spec, s, P_hot, P_lum, after=None):
    lvp = IN.LEVEL_PROP_C
    rr = {"propagated": P_hot >= lvp, "t_end_s": float(s["t"][-1]) if P_hot < lvp else None, "steps": 1, "rejected": 0,
          "max_implicit_nodes": 0, "energy_residual_rel": 1e-13, "peak_hottest_C": float(s["Tmax"].max() - K0),
          "t_peak_hottest_s": float(s["t"][int(np.argmax(s["Tmax"]))]), "peak_mean_C": float(s["Tmean"].max() - K0),
          "probe_peak": {"away": {"T_C": float(s["probe_away"].max() - K0), "t_s": float(s["probe_t"][int(np.argmax(s["probe_away"]))])},
                         "toward": {"T_C": float(s["probe_toward"].max() - K0), "t_s": float(s["probe_t"][int(np.argmax(s["probe_toward"]))])}},
          "in_rxn_J": 1.0, "cross_s": {}}
    if rr["propagated"]:
        tp = 20.0 * (lvp - 25.0) / (P_hot - 25.0)
        rr.update(t_prop_s=tp, t_end_s=tp + 0.05)
    ll = {"propagated": P_lum >= lvp, "peak_C": float(s["T_lumped"].max() - K0),
          "t_peak_s": float(s["t_lumped"][int(np.argmax(s["T_lumped"]))]), "reaction_heat_J": 2.0,
          "t_end_s": float(s["t_lumped"][-1]), "energy_residual_rel": 1e-14}
    if ll["propagated"]:
        tp = 250.0 * (lvp - 25.0) / (P_lum - 25.0)
        ll.update(t_prop_s=tp, t_end_s=tp + 0.05)
    if after is not None:
        ev = spec["event"]
        rr["event"] = {"E_J": ev["E_J"], "tau_s": ev["tau_s"], "t0_s": ev["t_s"], "delivered_J": ev["E_J"]}
        rr["after_event"] = {"Tmax_C": after[0], "t_Tmax_s": ev["t_s"] + 22.0, "Tmean_C": after[0] - 50,
                             "t_Tmean_s": ev["t_s"] + 23.0, "probes": {"away": {"T_C": after[0] - 100, "t_s": ev["t_s"] + 25},
                                                                      "toward": {"T_C": after[0] - 10, "t_s": ev["t_s"] + 22}}}
        ll["event"] = dict(rr["event"])
        ll["after_event"] = {"T_C": after[1], "t_s": ev["t_s"] + 22.0}
    rec = dict(spec)
    rec.update({"T1max_C": 500.0, "t_T1max_s": 21.0, "resolved": rr, "lumped": ll, "wall_s": 1.0, "model": "synthetic",
                "started_utc": "x", "finished_utc": "x"})
    rec["stage7"] = CQ.quantities(rec, s)
    return rec


def make_synthetic(res):
    """Synthetic records of every Part A run and of Part C's list, in res. The hot spot peaks at 0.3 times the test's
    trigger maximum, the lumped neighbour at 0.2 times it (5 K lower each with the aged SEI)."""
    os.makedirs(os.path.join(res, "stage7_runs"), exist_ok=True)
    os.makedirs(os.path.join(res, "stage7_series"), exist_ok=True)
    tests = {t["test"]: t for t in IN.tests()}
    e_by = {t: 50.0 * v["trigger_max_C"] for t, v in tests.items()}
    L = R7.levels()
    rows = [{"test": t, "connection": v["connection"], "target_C": v["trigger_max_C"], "E_J": e_by[t],
             "T1max_C": v["trigger_max_C"], "in_range": True, "iterations": 17,
             "T1max_by_contact_C": {"low": v["trigger_max_C"] + 1.0, "central": v["trigger_max_C"],
                                    "high": v["trigger_max_C"] - 1.0},
             "T1max_by_tau_C": {f"{x:.2f}": v["trigger_max_C"] for x in L["tau_s"]}} for t, v in tests.items()]
    json.dump({"levels": L, "rows": rows, "mapping": [], "out_of_range": []},
              open(os.path.join(res, "stage7_triggers.json"), "w"))
    recs = {}
    for sp_ in R7.build_part_a(e_by):
        tmax = tests[sp_["test"]]["trigger_max_C"]
        k = {"low": 0.8, "central": 1.0, "high": 1.2}[sp_["h"]] * (1.0 + 0.01 * (sp_["tau"] - L["tau_median_s"]))
        P_hot, P_lum = 0.3 * tmax * k, 0.2 * tmax * k
        if sp_["sei0"] is not None:
            P_hot, P_lum = P_hot - 5.0, P_lum - 5.0
        lvp = IN.LEVEL_PROP_C
        stop_h = 20.0 * (lvp - 25.0) / (P_hot - 25.0) + 0.05 if P_hot >= lvp else None
        stop_l = 250.0 * (lvp - 25.0) / (P_lum - 25.0) + 0.05 if P_lum >= lvp else None
        s = synth_series(P_hot, P_lum, stop_hot=stop_h, stop_lum=stop_l)
        rec = synth_record(sp_, s, P_hot, P_lum)
        recs[sp_["id"]] = rec
        np.savez_compressed(os.path.join(res, "stage7_series", sp_["id"] + ".npz"), **s)
        json.dump(rec, open(os.path.join(res, "stage7_runs", sp_["id"] + ".json"), "w"), default=float)
    runs, missing = R7.build_part_c(recs, series_dir=os.path.join(res, "stage7_series"), e_by_test=e_by)
    json.dump({"runs": runs, "n": len(runs), "sha256": R7.runs_hash(runs)}, open(os.path.join(res, "stage7_eventlist.json"), "w"))
    for sp_ in runs:
        base = recs[sp_["event"]["from"]]
        s = synth_series(*[base["stage7"]["clocks"][c]["peak_C"] for c in ("hot", "lumped")])
        hot_after = 1000.0 + 0.5 * tests[sp_["test"]]["trigger_max_C"] - (300.0 if sp_["event"]["criterion"] == "C5" else 0.0)
        rec = synth_record(sp_, s, base["stage7"]["clocks"]["hot"]["peak_C"], base["stage7"]["clocks"]["lumped"]["peak_C"],
                           after=(hot_after * (1.001 if sp_["set"] == "v3" else 1.0), hot_after - 200.0))
        recs[sp_["id"]] = rec
        np.savez_compressed(os.path.join(res, "stage7_series", sp_["id"] + ".npz"), **s)
        json.dump(rec, open(os.path.join(res, "stage7_runs", sp_["id"] + ".json"), "w"), default=float)
    return recs, runs, missing, e_by, tests


# ------------------------------------------------------------------------------------------------ 6b: the work loop
def test_work_loop(tmp):
    """The workers' loop with a made-up run in place of the model: Part A, then the Part C list made by the loop
    itself, then Part C, with V3 early; every run recorded once."""
    res = os.path.join(tmp, "work")
    os.makedirs(res, exist_ok=True)
    tests = {t["test"]: t for t in IN.tests()}
    e_by = {t: 50.0 * v["trigger_max_C"] for t, v in tests.items()}
    L = R7.levels()
    json.dump({"levels": L, "rows": [{"test": t, "E_J": e} for t, e in e_by.items()]},
              open(os.path.join(res, "stage7_triggers.json"), "w"))
    saved = {k: getattr(R7, k) for k in ("RUNS", "SERIES", "TRIGGERS", "EVENTLIST", "EVENTLOCK", "STOP_FILE", "run_one")}
    R7.RUNS, R7.SERIES = os.path.join(res, "stage7_runs"), os.path.join(res, "stage7_series")
    R7.TRIGGERS, R7.EVENTLIST = os.path.join(res, "stage7_triggers.json"), os.path.join(res, "stage7_eventlist.json")
    R7.EVENTLOCK, R7.STOP_FILE = os.path.join(res, "stage7_eventlist.lock"), os.path.join(res, "stage7_STOP")
    order = []

    def fake_run_one(sp_, ctx):
        order.append(sp_["id"])
        tmax = tests[sp_["test"]]["trigger_max_C"]
        k = {"low": 0.8, "central": 1.0, "high": 1.2}[sp_["h"]]
        P_hot, P_lum = 0.3 * tmax * k, 0.2 * tmax * k
        s = synth_series(P_hot, P_lum)
        after = (1400.0, 1200.0) if sp_.get("event") else None
        return synth_record(sp_, s, P_hot, P_lum, after=after), s

    R7.run_one = fake_run_one
    saved["mem_gb"] = R7.mem_gb
    R7.mem_gb = lambda: (64.0, 60.0)                   # a made-up computer with room for every run
    os.environ["STAGE7_EVENT_SLOTS"] = "64"
    try:
        R7.work(0, 1, 1e9, set(R7.SETS), queue=True, label="test", wait_s=0.01)
        recs = R7.load_records(R7.RUNS)
        ev = json.load(open(R7.EVENTLIST))
        want = R7.build_part_a(e_by) + ev["runs"]
        check("6b work loop: every run of Parts A and C recorded once", sorted(recs) == sorted(r["id"] for r in want)
              and len(order) == len(set(order)) == len(want), f"{len(recs)} records, {len(want)} runs")
        first_c = min(i for i, x in enumerate(order) if x.split("_")[0] in R7.PART_C)
        first_v3 = min(i for i, x in enumerate(order) if x.startswith("v3_"))
        check("6b work loop: V3 starts as soon as its base run is recorded, before Part A ends",
              first_v3 < len(R7.build_part_a(e_by)) and first_v3 == first_c, f"V3 at run {first_v3 + 1}")
        check("6b work loop: no claim left behind", not any(f.endswith(".claim") for f in os.listdir(R7.RUNS)))
    finally:
        for k, v in saved.items():
            setattr(R7, k, v)
        os.environ.pop("STAGE7_EVENT_SLOTS", None)


# ------------------------------------------------------------------------------------------------ 4: Part B quantities
def test_quantities():
    s = synth_series(200.0, 160.0)
    rec = synth_record({"id": "x", "set": "pertest", "test": "M50_PT_Exp4", "h": "central", "tau": 21.39}, s, 200.0, 160.0)
    q = rec["stage7"]["clocks"]
    exact = {("hot", "sep"): 20.0 * (138.5 - 25.0) / 175.0, ("lumped", "150"): 250.0 * 125.0 / 135.0,
             ("lumped", "sep"): 250.0 * 113.5 / 135.0}
    ok = all(abs(q[c][f"t_{lv}_s"] - v) < 1e-6 for (c, lv), v in exact.items())
    check("4 crossings on piecewise-linear histories are exact", ok,
          str({f"{c}_{lv}": q[c][f"t_{lv}_s"] for (c, lv) in exact}))
    check("4 a clock that never reaches a level has no crossing", q["hot"]["t_prop_s"] is None and q["lumped"]["t_prop_s"] is None)
    p, t = CQ.crossing(rec, "C4")
    check("4 criterion C4 reads the hot spot at 138.5 C", p and abs(t - exact[("hot", "sep")]) < 1e-6)
    p, t = CQ.crossing(rec, "C1")
    check("4 criterion C1 reads the run's own stop", (not p) and t is None)


# ------------------------------------------------------------------------------------------------ 5: the triggers
def fake_peak(e, tau, connection, h="central", g="central"):
    k = {"low": 1.01, "central": 1.0, "high": 0.99}[h] * (1.0 + 0.002 * (21.38651984299561 - tau)) * \
        (1.0 if connection == "series" else 0.999)
    return 25.0 + k * (0.0152 * e - 2.0e-8 * e * e), 20.0


def test_triggers(tmp):
    b = R7.bisect(630.0, "parallel", 21.39, 0.0, 110830.0, peak=fake_peak)
    check("5 bisection: within 0.01 K", b["in_range"] and abs(b["T1max_C"] - 630.0) <= 0.01, f"{b['E_J']:.3f} J")
    lo = R7.bisect(20.0, "series", 21.39, 0.0, 110830.0, peak=fake_peak)
    hi = R7.bisect(5000.0, "series", 21.39, 0.0, 110830.0, peak=fake_peak)
    check("5 bisection: out of range below and above", (not lo["in_range"]) and lo["E_J"] == 0.0 and
          (not hi["in_range"]) and hi["E_J"] == 110830.0)
    out = R7.triggers(path=os.path.join(tmp, "stage7_triggers.json"), csv_path=os.path.join(tmp, "stage7_triggers.csv"),
                      peak=fake_peak, with_separator=False)
    check("5 triggers: sixteen tests, all in range", len(out["rows"]) == 16 and not out["out_of_range"])
    check("5 triggers: the mapping covers 0 to the Databank's maximum", out["mapping"][0]["E_J"] == 0.0 and
          max(g["E_J"] for g in out["mapping"]) == R7.levels()["E_hi_J"])
    v = CK.v1(tmp)
    check("5 V1 passes on the synthetic table", v["pass"], f"{v['largest_difference_J']:.3f} J")


# ------------------------------------------------------------------------------------------------ 6 and 7
def test_lists_and_scoring(tmp):
    res = os.path.join(tmp, "res")
    recs, runs, missing, e_by, tests = make_synthetic(res)
    a = R7.build_part_a(e_by)
    check("6 Part A: 48 + 32 + 48 runs, ids unique", len(a) == 128 and len({r["id"] for r in a}) == 128 and
          [sum(r["set"] == s for r in a) for s in R7.PART_A] == [48, 32, 48])
    # expected Part C from the synthetic rule: hot spot peak 0.3 Tmax k, lumped 0.2 Tmax k, at 21.39 s
    k = {"low": 0.8, "central": 1.0, "high": 1.2}
    want = set()
    for t, v in tests.items():
        if 0.3 * v["trigger_max_C"] >= 138.5:
            want.add((t, "central", "C4"))
        if 0.2 * v["trigger_max_C"] >= 138.5:
            want.add((t, "central", "C5"))
    got = {(r["test"], r["h"], r["event"]["criterion"]) for r in runs if r["set"] == "event"}
    low = {(r["test"], r["h"], r["event"]["criterion"]) for r in runs if r["set"] == "eventlow"}
    check("6 Part C: one event run per test and criterion that reaches 138.5 C at the central contact", got == want,
          f"{len(got)} runs")
    check("6 Part C: the lower bracket for each of them", low == want and all(
        r["event"]["E_J"] == 63360.0 or abs(r["event"]["E_J"] - 63360.0) < 1e-6 for r in runs if r["set"] == "eventlow"))
    v3 = [r for r in runs if r["set"] == "v3"]
    check("6 Part C: V3 on M50_PT_Exp4's central C4 run, to 120 s after its event", len(v3) == 2 and all(
        r["test"] == "M50_PT_Exp4" and r["event"]["criterion"] == "C4" and
        abs(r["t_end_s"] - (r["event"]["t_s"] + r["event"]["tau_s"] + 120.0)) < 1e-9 for r in v3)
        and {r["refine"] for r in v3} == {1.0, 2.0})
    check("6 Part C: every Part C run ends 120 s after its event", all(
        abs(r["t_end_s"] - min(900.0, r["event"]["t_s"] + r["event"]["tau_s"] + 120.0)) < 1e-9 for r in runs))
    check("6 Part A runs go to 900 s", all(r["t_end_s"] == 900.0 for r in a))
    # the memory gate (D69 (4)), with claim files of synthetic runs in a scratch folder
    saved = R7.RUNS
    R7.RUNS = os.path.join(tmp, "claims")
    os.makedirs(R7.RUNS, exist_ok=True)
    os.environ["STAGE7_EVENT_SLOTS"] = "6"
    try:
        for r in [x for x in runs if x["set"] == "event"][:4]:
            open(os.path.join(R7.RUNS, r["id"] + ".claim"), "w").write("w")
        used = R7.part_c_slots_in_use()
        fits_base = R7.part_c_slots_in_use() + R7.SLOTS[1.0] <= R7.event_slots()
        fits_ref = R7.part_c_slots_in_use() + R7.SLOTS[2.0] <= R7.event_slots()
        check("6 memory gate: four runs going hold four slots; a base run fits, a refined one does not",
              used == 4 and fits_base and not fits_ref and R7.room_for(a[0]))
        for f in os.listdir(R7.RUNS):
            os.remove(os.path.join(R7.RUNS, f))
        check("6 memory gate: with no Part C run going, any Part C run may start",
              R7.room_for([x for x in runs if x["set"] == "v3" and x["refine"] == 2.0][0]))
    finally:
        R7.RUNS = saved
        os.environ.pop("STAGE7_EVENT_SLOTS", None)
    saved_runs, saved_series = R7.RUNS, R7.SERIES
    R7.RUNS, R7.SERIES = os.path.join(res, "stage7_runs"), os.path.join(res, "stage7_series")
    try:
        ev3 = R7.early_v3(e_by)
    finally:
        R7.RUNS, R7.SERIES = saved_runs, saved_series
    check("6 V3's runs early, from their base record alone, equal those of the Part C list",
          ev3 == v3, f"{len(ev3)} runs")
    ev = [r for r in runs if r["set"] == "event" and r["test"] == "M50_PT_Exp4" and r["h"] == "central"
          and r["event"]["criterion"] == "C4"][0]
    check("6 Part C: the event time is the hot spot's 138.5 C crossing",
          abs(ev["event"]["t_s"] - 20.0 * 113.5 / (0.3 * 630.0 - 25.0)) < 1e-9)
    import stage7_score as SC
    sc = SC.main(res, "synthetic", self_heating=False)
    cen = {c: sc["criteria"][c]["central"] for c in CQ.CRITERIA}
    # by hand from the rule
    n4 = sum(0.3 * v["trigger_max_C"] >= 138.5 for v in tests.values())
    n3 = sum(0.2 * v["trigger_max_C"] >= 150.0 for v in tests.values())
    hits3 = sum(0.2 * v["trigger_max_C"] >= 150.0 and v["propagated"] for v in tests.values())
    cr3 = sum(0.2 * v["trigger_max_C"] < 150.0 and not v["propagated"] for v in tests.values())
    check("7 scoring: C4 and C3 counts as by hand", cen["C4"]["predicted"] == n4 and cen["C3"]["predicted"] == n3 and
          cen["C3"]["hits"] == hits3 and cen["C3"]["correct_rejections"] == cr3)
    check("7 scoring: every class counted once", all(d["hits"] + d["misses"] + d["false_alarms"] +
                                                     d["correct_rejections"] == 16 for d in cen.values()))
    check("7 scoring: P1 and P4 verdicts", sc["P1"]["verdict"] == ("held" if cen["C1"]["predicted"] < 9 else "failed")
          and sc["P4"]["verdict"] == ("held" if n4 > 9 else "failed"))
    check("7 scoring: P2 by its two parts", sc["P2"]["held"] == (n3 >= 9 and hits3 + cr3 >= 10))
    check("7 scoring: P6 without inversions on a monotone rule", sc["P6"]["held"] and sc["P6"]["inversions"] == 0)
    d7 = {c: abs(cen[c]["by_connection"]["series"] - cen[c]["by_connection"]["parallel"]) for c in CQ.CRITERIA}
    check("7 scoring: P7 from the split counts", sc["P7"]["held"] == all(v <= 1 for v in d7.values()), str(d7))
    p8 = sc["P8"]
    check("7 scoring: P8 counts the central event runs", p8["runs"] == sum(1 for r in runs if r["set"] == "event"
                                                                          and r["h"] == "central"))
    check("7 scoring: V3 from the synthetic 0.1 %", sc["V3"]["pass"] and len(sc["V3"]["cases"]) == 2)
    check("7 scoring: the files", all(os.path.exists(os.path.join(res, f)) for f in
                                      ("stage7_pertest.csv", "stage7_events.csv", "stage7_crossings.csv",
                                       "stage7_scorecard.json")))
    import csv
    pr = list(csv.DictReader(open(os.path.join(res, "stage7_pertest.csv"))))
    check("7 per-test file: 16 tests x 3 contacts x 7 criteria", len(pr) == 336)
    v = CK.v2(res)
    check("7 V2 passes on synthetic records", v["pass"], f"{v['largest_difference_s']:.2e} s")
    r = subprocess.run([sys.executable, os.path.join(HERE, "stage7_numbers.py"), "--res", res], capture_output=True,
                       text=True)
    check("7 the quoted numbers are written", r.returncode == 0 and
          os.path.exists(os.path.join(res, "stage7_paper_numbers.json")), r.stderr[-300:])
    r = subprocess.run([sys.executable, os.path.join(HERE, "make_figure_stage7.py"), "--res", res], capture_output=True,
                       text=True)
    check("7 the figure renders", r.returncode == 0 and os.path.exists(os.path.join(res, "stage7_figure.png")),
          r.stderr[-300:])
    return res


if __name__ == "__main__":
    quick = "--quick" in sys.argv
    tmp = tempfile.mkdtemp(prefix="stage7_test_")
    try:
        test_quantities()
        test_triggers(tmp)
        res = test_lists_and_scoring(tmp)
        test_work_loop(tmp)
        test_aged()
        test_kernel()
        test_model(quick)
        if "--keep" in sys.argv:
            print("synthetic results kept in", res)
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(tmp, ignore_errors=True)
    print("ALL PASS" if not FAILS else f"{len(FAILS)} FAILED: {FAILS}")
    sys.exit(1 if FAILS else 0)
