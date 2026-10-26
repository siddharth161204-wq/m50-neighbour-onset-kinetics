#!/usr/bin/env python3
"""Stage 7 runs: the ignition condition scored test by test (predictions_stage7.md; DECISIONS.md D63 to D72).

Steps, in order:
  triggers  the trigger energy of each of the sixteen tests by bisection (D65), the peak-to-energy table, each
            test's cell-1 peak at the three contacts and at the other two release durations, and the separator's
            melting temperatures over the posterior (D71), into results/stage7_triggers.csv, results/stage7_triggers.json
            and results/stage7_separator.json. It computes no history of the neighbour.
  list      the Part A run list and its SHA-256 (with Part C's, once results/stage7_eventlist.json exists);
  events    Part C's run list from the Part A records (D68), into results/stage7_eventlist.json; `work` makes it
            itself once every Part A run of the pertest set is recorded;
  work      the runs. Part A first: the fresh runs as Stage 5 made them (v12_run.run_one, unchanged), the aged ones
            with the aged SEI (src/stage7_model.py), each resolved neighbour stopped when its hottest node reaches
            255.7 C or at 900 s, the lumped one likewise, both driven by the same cell-1 history, the reaction heat
            fed back one-way. Then Part C: the event runs, which go on to 900 s.
Sets (D66, D68), in this order:
  pertest   the sixteen tests at the three contacts, central tabs, the median release, fresh SEI (48);
  duration  the sixteen tests at the central contact with the other two releases, the same energies (32);
  aged      as pertest with the aged SEI (48);
  v3        Part C: one event run with every mesh spacing halved and with every step limit halved (2);
  event     Part C: 65.52 kJ in the neighbour from its 138.5 C crossing, for each test where C4 (the hot spot) or C5
            (the lumped neighbour) predicts propagation at the central contact, one run per criterion;
  eventlow  Part C: the same with 63.36 kJ.
A Part C run is not stopped at 255.7 C; it ends 120 s after its event has ended (D68 (5)).
Part C runs start only while the memory allows (D69 (4)): their memory slots (one for a run on the base mesh, six
for the refined one, 1 GB each) fit within the computer's memory less 4 GB, and as much is free.
Records go to results/stage7_runs/<id>.json and series to results/stage7_series/<id>.npz.

Usage:
  python3 stage7_run.py triggers
  python3 stage7_run.py list | events | status | reset-claims
  python3 stage7_run.py work --queue --label NAME [--worker K --of N]
"""
import os as _os
for _k in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "NUMBA_NUM_THREADS"):
    _os.environ.setdefault(_k, "1")      # D43 (4): one thread per library; set before numpy and numba load
import argparse, csv, hashlib, json, os, signal, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v12_model as V                    # noqa: E402  (unchanged)
import v12_run as RUN                    # noqa: E402  (unchanged)
import reactive as RX                    # noqa: E402
import stage6_crossings as CR            # noqa: E402  (unchanged: first_crossing, histories)
import stage7_inputs as IN               # noqa: E402
import stage7_model as M                 # noqa: E402

RES = os.path.join(HERE, "..", "results")
RUNS = os.path.join(RES, "stage7_runs" + os.environ.get("STAGE7_RUNS_TAG", ""))
SERIES = os.path.join(RES, "stage7_series" + os.environ.get("STAGE7_RUNS_TAG", ""))
TRIGGERS_CSV = os.path.join(RES, "stage7_triggers.csv")
TRIGGERS = os.path.join(RES, "stage7_triggers.json")
SEPARATOR = os.path.join(RES, "stage7_separator.json")
EVENTLIST = os.path.join(RES, "stage7_eventlist.json")
EVENTLOCK = os.path.join(RES, "stage7_eventlist.lock")
STOP_FILE = os.path.join(RES, "stage7_STOP")      # if this file exists, no worker starts another run
PART_A = ("pertest", "duration", "aged")
PART_C = ("v3", "event", "eventlow")
SETS = PART_A + PART_C
CONTACTS = ("low", "central", "high")
RUN_LIMIT_MIN = {1.0: 480.0, 2.0: 1440.0}       # D69 (4): a run that takes longer is recorded as failed
GB_EVENT = float(os.environ.get("STAGE7_GB_EVENT", 1.0))     # D69 (4): memory of one Part C run, base mesh
SLOTS = {1.0: 1, 2.0: 6}                        # memory slots of a Part C run on the base and the refined mesh
AFTER_EVENT_S = 120.0                           # D68 (5): a Part C run ends this long after its event has ended
MAX_SUB_EVENT = 4096                            # D68 (3): explicit sub-steps allowed per step from the event on
START_MARGIN_MIN = {1.0: 15.0, 2.0: 75.0}
PEAK_TOL_K = 0.01                               # D65: the bisection, as D54 (5)
MAPPING_STEP_J = 250.0                          # D65: the peak-to-energy table, every 0.25 kJ
V3_TEST, V3_FALLBACK_TEST = "M50_PT_Exp4", "M50_SP_Exp3"     # D69 (3)
K0 = 273.15


def levels():
    dur = IN.durations()
    en = IN.energies()
    return {"tau_s": dur["release_durations_s"], "tau_median_s": dur["median_s"],
            "E_lo_J": 0.0, "E_hi_J": en["total_max_J"], "E_hi_test": en["total_max_test"],
            "E_event_J": IN.E_EVENT_J, "E_event_low_J": IN.E_EVENT_LOW_J, "sep_C": IN.LEVEL_SEP_C}


# ------------------------------------------------------------------------------------------------ the triggers
def t1_peak(e, tau, connection, h="central", g="central"):
    f, data, T1max, tmax = V.stage5_t1(connection, V.H_CONTACT[h], V.G_TAB[g], tau, e)
    return float(T1max), float(tmax)


def bisect(target_C, connection, tau, lo, hi, peak=t1_peak, tol=PEAK_TOL_K, max_iter=200):
    """D65: the energy whose cell-1 peak (central case, this connection, this release) equals target_C within tol,
    by halving [lo, hi] as D54 (5) did. A target outside the peaks at the two ends is out of range and takes the
    nearer end."""
    p_lo, p_hi = peak(lo, tau, connection)[0], peak(hi, tau, connection)[0]
    if target_C <= p_lo:
        return {"E_J": lo, "T1max_C": p_lo, "in_range": False, "nearest": "lower end", "iterations": []}
    if target_C >= p_hi:
        return {"E_J": hi, "T1max_C": p_hi, "in_range": False, "nearest": "upper end", "iterations": []}
    it = []
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        T1 = peak(mid, tau, connection)[0]
        it.append((mid, T1))
        if abs(T1 - target_C) <= tol:
            break
        if T1 < target_C:
            lo = mid
        else:
            hi = mid
    return {"E_J": it[-1][0], "T1max_C": it[-1][1], "in_range": True, "nearest": None, "iterations": it,
            "end_peaks_C": [p_lo, p_hi]}


def separator_bracket():
    """D71: the DSC peak of the separator's melting at 5 C/min for each of the posterior's 100 separator particles,
    computed as V0 computes the posterior mean's (src/v0_dsc_check.py), and their 2.5 and 97.5 % points."""
    import bcrnn
    import stage3_draws as S
    import v0_dsc_check as V0
    P = S.load_particles()
    sep_cols = P["Separator.csv"].shape[1]
    an, cat = P["An_Ele.csv"][:, 0], P["NCM811.csv"][:, 0]           # any column: the ramp holds the separator only
    i_sep = bcrnn.SPECIES.index("sep")
    j_melt = bcrnn.REACTIONS.index("sep_melt")

    def melt_peak(kin):
        """The ramp's temperature where the melting rate, and so its heat (-dH times the rate, D5), peaks."""
        tt, TC, C, r = V0.dsc(kin, [i_sep], T_end_C=200.0)
        return float(TC[int(np.argmax(np.abs(r[j_melt])))])
    temps = [melt_peak(bcrnn.Kinetics(model=bcrnn.rows_to_model(an, cat, P["Separator.csv"][:, j])))
             for j in range(sep_cols)]
    mean_peak = melt_peak(bcrnn.Kinetics())
    a = np.array(temps)
    return {"n_particles": int(a.size), "peak_C_by_particle": temps, "posterior_mean_model_peak_C": mean_peak,
            "p2.5_C": float(np.percentile(a, 2.5)), "p97.5_C": float(np.percentile(a, 97.5)),
            "min_C": float(a.min()), "max_C": float(a.max()), "median_C": float(np.median(a)),
            "grid_K": 5.0 / 60.0 * 2.0, "method": "src/v0_dsc_check.py dsc(), 5 C/min, 2 s output grid"}


def triggers(path=TRIGGERS, csv_path=TRIGGERS_CSV, sep_path=SEPARATOR, peak=t1_peak, with_separator=True):
    L = levels()
    tm = L["tau_median_s"]
    rows = []
    for t in IN.tests():
        b = bisect(t["trigger_max_C"], t["connection"], tm, L["E_lo_J"], L["E_hi_J"], peak=peak)
        e = b["E_J"]
        per = {h: peak(e, tm, t["connection"], h, "central") for h in CONTACTS}
        dur = {f"{tau:.2f}": peak(e, tau, t["connection"]) for tau in L["tau_s"]}
        rows.append({"test": t["test"], "connection": t["connection"], "target_C": t["trigger_max_C"], "E_J": e,
                     "T1max_C": b["T1max_C"], "in_range": b["in_range"], "nearest": b["nearest"],
                     "iterations": len(b["iterations"]), "bisection": b["iterations"],
                     "T1max_by_contact_C": {h: v[0] for h, v in per.items()},
                     "t_T1max_by_contact_s": {h: v[1] for h, v in per.items()},
                     "T1max_by_tau_C": {k: v[0] for k, v in dur.items()}})
    grid = []
    n = int(np.floor(L["E_hi_J"] / MAPPING_STEP_J))
    energies = [k * MAPPING_STEP_J for k in range(n + 1)] + ([L["E_hi_J"]] if n * MAPPING_STEP_J < L["E_hi_J"] else [])
    for conn in V.CONNECTIONS:
        for e in energies:
            T1, t1 = peak(e, tm, conn)
            grid.append({"connection": conn, "E_J": e, "T1max_C": T1, "t_T1max_s": t1})
    out = {"levels": L, "rows": rows, "mapping": grid, "tolerance_K": PEAK_TOL_K, "mapping_step_J": MAPPING_STEP_J,
           "out_of_range": [r["test"] for r in rows if not r["in_range"]], "computed_utc": RUN._utc()}
    if path:
        json.dump(out, open(path, "w"), indent=1, default=float)
    if csv_path:
        fields = ["kind", "test", "connection", "target_C", "E_J", "T1max_C", "t_T1max_s", "iterations", "in_range",
                  "T1max_low_C", "T1max_high_C", "T1max_tau17.53_C", "T1max_tau25.24_C"]
        ts = sorted(L["tau_s"])
        with open(csv_path, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            for r in rows:
                w.writerow({"kind": "test", "test": r["test"], "connection": r["connection"], "target_C": r["target_C"],
                            "E_J": repr(r["E_J"]), "T1max_C": repr(r["T1max_C"]),
                            "t_T1max_s": repr(r["t_T1max_by_contact_s"]["central"]), "iterations": r["iterations"],
                            "in_range": r["in_range"], "T1max_low_C": repr(r["T1max_by_contact_C"]["low"]),
                            "T1max_high_C": repr(r["T1max_by_contact_C"]["high"]),
                            "T1max_tau17.53_C": repr(r["T1max_by_tau_C"][f"{ts[0]:.2f}"]),
                            "T1max_tau25.24_C": repr(r["T1max_by_tau_C"][f"{ts[-1]:.2f}"])})
            for g in grid:
                w.writerow({"kind": "mapping", "connection": g["connection"], "E_J": repr(g["E_J"]),
                            "T1max_C": repr(g["T1max_C"]), "t_T1max_s": repr(g["t_T1max_s"])})
    if with_separator and sep_path:
        json.dump(separator_bracket(), open(sep_path, "w"), indent=1)
    return out


def energies_by_test():
    tr = json.load(open(TRIGGERS))
    return {r["test"]: r["E_J"] for r in tr["rows"]}


# ------------------------------------------------------------------------------------------------ the run lists
def spec(set_, test, conn, h, tau, e, sei0=None, event=None, refine=1.0, dt_scale=1.0, tag="", t_end=900.0):
    rid = f"{set_}_{test}_{conn}_h{h}_gcentral_tau{tau:.2f}_E{e / 1e3:.2f}" + tag
    if event is not None:
        event = dict(event, max_sub_after=MAX_SUB_EVENT)
    return {"id": rid, "set": set_, "test": test, "kin": "mean", "connection": conn, "h": h, "g": "central",
            "tau": float(tau), "E_body_J": float(e), "T_amb_K": float(V.LP.T_AMB), "refine": float(refine),
            "dt_scale": float(dt_scale), "sei0": sei0, "event": event, "t_end_s": float(t_end)}


def build_part_a(e_by_test=None):
    """Part A (D66): pertest, duration and aged, in this order."""
    L = levels()
    tm = L["tau_median_s"]
    e_by_test = energies_by_test() if e_by_test is None else e_by_test
    tests = IN.tests()
    runs = []
    for t in tests:
        for h in CONTACTS:
            runs.append(spec("pertest", t["test"], t["connection"], h, tm, e_by_test[t["test"]]))
    for t in tests:
        for tau in (L["tau_s"][0], L["tau_s"][-1]):
            runs.append(spec("duration", t["test"], t["connection"], "central", tau, e_by_test[t["test"]]))
    for t in tests:
        for h in CONTACTS:
            runs.append(spec("aged", t["test"], t["connection"], h, tm, e_by_test[t["test"]], sei0=IN.SEI_AGED,
                             tag="_aged"))
    return runs


def event_crossings(series):
    """The times at which the hot spot (C4) and the lumped neighbour (C5) first reach 138.5 C in a Part A run's
    series: Part B's crossings (stage7_criteria.py), the event times of D68."""
    hs = CR.histories(series)
    lv = IN.LEVEL_SEP_C + K0
    return {"C4": CR.first_crossing(*hs["hot"], lv), "C5": CR.first_crossing(*hs["lumped"], lv)}


def build_part_c(recs, series_dir=SERIES, e_by_test=None):
    """Part C (D68): from the pertest records at the central contact. For each test, one run per criterion (C4:
    the hot spot, C5: the lumped neighbour) whose 138.5 C crossing exists, with 65.52 kJ from that crossing and
    with 63.36 kJ, each to 120 s after its event has ended; and V3's two runs on the run of D69 (3).
    Returns (runs, missing)."""
    L = levels()
    tm = L["tau_median_s"]
    e_by_test = energies_by_test() if e_by_test is None else e_by_test
    runs, missing, base = [], [], {}
    for t in IN.tests():
        for h in ("central",):
            a = spec("pertest", t["test"], t["connection"], h, tm, e_by_test[t["test"]])
            rec = recs.get(a["id"])
            sp_ = os.path.join(series_dir, a["id"] + ".npz")
            if rec is None or rec.get("failed") or not os.path.exists(sp_):
                missing.append(a["id"])
                continue
            z = np.load(sp_)
            tx = event_crossings({k: z[k] for k in z.files})
            for crit in ("C4", "C5"):
                if tx[crit] is None:
                    continue
                t_end = min(900.0, float(tx[crit]) + float(tm) + AFTER_EVENT_S)
                for set_, e in (("event", L["E_event_J"]), ("eventlow", L["E_event_low_J"])):
                    ev = {"criterion": crit, "t_s": float(tx[crit]), "E_J": float(e), "tau_s": float(tm),
                          "from": a["id"]}
                    s = spec(set_, t["test"], t["connection"], h, tm, e_by_test[t["test"]], event=ev,
                             tag=f"_{crit}_ev{e / 1e3:.2f}", t_end=t_end)
                    runs.append(s)
                    base[(t["test"], h, crit, set_)] = s
    v3 = []
    for test, crit in ((V3_TEST, "C4"), (V3_TEST, "C5"), (V3_FALLBACK_TEST, "C4")):
        b = base.get((test, "central", crit, "event"))
        if b is not None:
            t_end = b["t_end_s"]
            for tag, kw in (("_refine2", {"refine": 2.0}), ("_dthalf", {"dt_scale": 0.5})):
                s = spec("v3", b["test"], b["connection"], "central", tm, b["E_body_J"], event=dict(b["event"]),
                         tag=f"_{crit}_ev{b['event']['E_J'] / 1e3:.2f}" + tag, t_end=t_end, **kw)
                s["v3_base"] = b["id"]
                v3.append(s)
            break
    return v3 + runs, missing


def early_v3(e_by_test=None):
    """V3's two runs as soon as the pertest runs they depend on are recorded (D69 (3)): the same specifications as
    in the Part C list, so that the long refined run can start while Part A goes on."""
    e_by_test = energies_by_test() if e_by_test is None else e_by_test
    tm = levels()["tau_median_s"]
    by = {t["test"]: t for t in IN.tests()}
    recs = {}
    for test in (V3_TEST, V3_FALLBACK_TEST):
        a_ = spec("pertest", test, by[test]["connection"], "central", tm, e_by_test[test])
        p = os.path.join(RUNS, a_["id"] + ".json")
        if os.path.exists(p):
            try:
                recs[a_["id"]] = json.load(open(p))
            except (OSError, ValueError):
                pass
    if not recs:
        return []
    runs, _ = build_part_c(recs, series_dir=SERIES, e_by_test=e_by_test)
    v3 = [r for r in runs if r["set"] == "v3"]
    if v3 and v3[0]["test"] == V3_FALLBACK_TEST:
        base = spec("pertest", V3_TEST, by[V3_TEST]["connection"], "central", tm, e_by_test[V3_TEST])["id"]
        if base not in recs:                         # the rule's first choice is not decided yet
            return []
    return v3


def build_runs():
    """The run list as it stands: V3's runs first (once their base is recorded; the refined one is the longest),
    then Part A, then the rest of Part C once its list exists."""
    part_c = json.load(open(EVENTLIST))["runs"] if os.path.exists(EVENTLIST) else early_v3()
    return [r for r in part_c if r["set"] == "v3"] + build_part_a() + [r for r in part_c if r["set"] != "v3"]


def runs_hash(runs):
    return hashlib.sha256(json.dumps(runs, sort_keys=True).encode()).hexdigest()


def make_eventlist(path=None):
    path = EVENTLIST if path is None else path
    recs = load_records(RUNS)
    a = [r for r in build_part_a() if r["set"] == "pertest"]
    runs, missing = build_part_c(recs, series_dir=SERIES)
    out = {"runs": runs, "sha256": runs_hash(runs), "n": len(runs),
           "by_set": {s: sum(r["set"] == s for r in runs) for s in PART_C}, "pertest_missing": missing,
           "pertest_n": len(a), "made_utc": RUN._utc(), "rule": "DECISIONS.md D68 and D69 (3)"}
    tmp = path + f".tmp{os.getpid()}"
    json.dump(out, open(tmp, "w"), indent=1, default=float)
    os.replace(tmp, path)
    return out


def load_records(runs_dir=RUNS):
    recs = {}
    if os.path.isdir(runs_dir):
        for f in os.listdir(runs_dir):
            if f.endswith(".json"):
                try:
                    r = json.load(open(os.path.join(runs_dir, f)))
                except (OSError, ValueError):
                    continue
                recs[r["id"]] = r
    return recs


# ------------------------------------------------------------------------------------------------ one run
def _at(t_arr, y_arr, t):
    return float(np.interp(t, t_arr, y_arr))


def run_one_s7(spec_, ctx, keep_series=True):
    """v12_run.run_one with the Stage 7 model (stage7_model.py): the initial SEI and the event as arguments; an event
    run is not stopped at 255.7 C. The record has v12_run.run_one's fields, and the event's quantities."""
    t_start = time.time()
    model = ctx.model(spec_["h"], spec_["refine"])
    t1f, t1data, T1max_C, tT1max = ctx.history(spec_)
    kin, draw = ctx.kinetics(spec_["kin"])
    g_pos, g_neg = V.tabs(spec_["connection"], V.G_TAB[spec_["g"]])
    ev = spec_.get("event")
    event = M.Event(ev["E_J"], ev["tau_s"], ev["t_s"]) if ev else None
    stop = None if event is not None else V.LEVEL_PROP
    saved = (RX.DT_BASE, RX.DT_TARGET, RX.DT_ACCEPT)
    if spec_["dt_scale"] != 1.0:
        RX.DT_BASE, RX.DT_TARGET, RX.DT_ACCEPT = (x * spec_["dt_scale"] for x in saved)
    try:
        t_end = spec_.get("t_end_s", 900.0)
        ms = ev.get("max_sub_after") if ev else None
        r = M.run_resolved(model, t1f, g_pos, g_neg, kin=kin, t_amb=spec_["T_amb_K"], t_end=t_end, stop_level=stop,
                           probes=model.probes, keep_series=keep_series, max_facts=6 if spec_["refine"] == 1.0 else 2,
                           sei0=spec_.get("sei0"), event=event, max_sub_event=ms)
        lr = M.run_lumped(t1f, g_pos + g_neg, g_link=V.g_contact(V.H_CONTACT[spec_["h"]]), f_view=V.F_TOUCH, kin=kin,
                          t_amb=spec_["T_amb_K"], t_end=t_end, stop_level=stop, sei0=spec_.get("sei0"), event=event,
                          max_sub_event=ms)
    finally:
        RX.DT_BASE, RX.DT_TARGET, RX.DT_ACCEPT = saved
    res = {"propagated": r["stop"] is not None, "t_end_s": r["t_end_s"], "steps": r["steps"], "rejected": r["rejected"],
           "max_implicit_nodes": r["max_implicit_nodes"], "energy_residual_rel": r["energy_residual_rel"],
           "peak_hottest_C": r["peak"]["Tmax_C"], "t_peak_hottest_s": r["peak"]["t_s"],
           "peak_mean_C": r["peak"]["Tmean_C"], "probe_peak": r["probe_peak"],
           "in_rxn_J": r["energy_J"]["in_rxn"], "cross_s": r["cross_s"], "energy_J": r["energy_J"],
           "conversion_volume_mean_end": r["conversion_volume_mean_end"],
           "max_local_reaction_heating_K_per_s": r["max_local_reaction_heating_K_per_s"]}
    pt, pT = r["probe_t"], r["probe_T"]
    if r["stop"] is not None:
        tp = r["stop"]["t_s"]
        res.update({"t_prop_s": tp, "where": r["stop"]["where"], "mean_at_prop_C": r["stop"]["Tmean_C"],
                    "T1_at_prop_C": t1f(tp) - 273.15})
        w0 = max(0.0, tp - 60.0)
        res["rate_window_s"] = tp - w0
        for k in ("toward", "away"):
            Tp, T0 = _at(pt, pT[k], tp), _at(pt, pT[k], w0)
            res[f"T_mid_{k}_C"] = Tp - 273.15
            res[f"rate_{k}_C_per_s"] = (Tp - T0) / (tp - w0) if tp > w0 else None
            if tp > tT1max:
                res[f"rate_section2_{k}_C_per_s"] = (Tp - _at(pt, pT[k], tT1max)) / (tp - tT1max)
    if event is not None:
        res["event"] = r["event"]
        res["after_event"] = r["after_event"]
    lres = {"propagated": lr["stop"] is not None, "peak_C": lr["peak"]["T_C"], "t_peak_s": lr["peak"]["t_s"],
            "reaction_heat_J": lr["reaction_heat_J"], "t_end_s": lr["t_end_s"], "energy_J": lr["energy_J"],
            "energy_residual_rel": lr["energy_residual_rel"], "conversion_end": lr["conversion_end"],
            "cross_s": lr["cross_s"]}
    if lr["stop"] is not None:
        tp = lr["stop"]["t_s"]
        w0 = max(0.0, tp - 60.0)
        Tp = _at(lr["steps_t"], lr["steps_T"], tp); T0 = _at(lr["steps_t"], lr["steps_T"], w0)
        lres.update({"t_prop_s": tp, "rate_C_per_s": (Tp - T0) / (tp - w0) if tp > w0 else None,
                     "rate_window_s": tp - w0})
    if event is not None:
        lres["event"] = lr["event"]
        lres["after_event"] = lr["after_event"]
    rec = dict(spec_)
    rec.update({"draw": draw, "h_c_W_m2K": V.H_CONTACT[spec_["h"]], "G_tab_W_K": V.G_TAB[spec_["g"]],
                "G_contact_W_K": V.g_contact(V.H_CONTACT[spec_["h"]]), "g_pos_W_K": g_pos, "g_neg_W_K": g_neg,
                "T1max_C": T1max_C, "t_T1max_s": tT1max, "n_nodes": int(model.C.size),
                "resolved": res, "lumped": lres, "wall_s": time.time() - t_start})
    series = None
    if keep_series:
        s = r["series"]
        series = {"t": s[:, 0], "T1": s[:, 1], "Tmax": s[:, 2], "Tmean": s[:, 3], "imax": s[:, 4].astype(int),
                  "probe_t": pt, "probe_toward": pT["toward"], "probe_away": pT["away"],
                  "t_lumped": lr["series"][:, 0], "T_lumped": lr["series"][:, 1],
                  "t1_t": t1data[:, 0], "t1_T1_C": t1data[:, 1], "t1_T2_C": t1data[:, 2]}
    return rec, series


def run_one(spec_, ctx):
    """A fresh run without an event is made by v12_run.run_one, unchanged (D66 (2)); the others by run_one_s7."""
    import stage7_criteria as CQ
    if spec_.get("sei0") is None and spec_.get("event") is None:
        rec, series = RUN.run_one(spec_, ctx, keep_series=True)
        rec["model"] = "v12_run.run_one"
    else:
        rec, series = run_one_s7(spec_, ctx, keep_series=True)
        rec["model"] = "stage7_run.run_one_s7"
    rec["stage7"] = CQ.quantities(rec, series)
    return rec, series


# ------------------------------------------------------------------------------------------------ the work loop
def mem_gb():
    """(total, available) memory in GB, as Stage 5's laptop script reads them (v12_laptop.mem_gb)."""
    import v12_laptop as L5
    return L5.mem_gb()


def peak_memory_mb():
    """The worker process's largest memory use so far (its peak working set on Windows, its peak resident set
    elsewhere), recorded with each run; for the record only."""
    try:
        if os.name == "nt":
            import ctypes
            from ctypes import wintypes

            class PMC(ctypes.Structure):
                _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                            ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                            ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]
            pmc = PMC()
            pmc.cb = ctypes.sizeof(PMC)
            ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.windll.kernel32.GetCurrentProcess(), ctypes.byref(pmc),
                                                     pmc.cb)
            return pmc.PeakWorkingSetSize / 2 ** 20
        import resource
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    except Exception:
        return None


def part_c_slots_in_use():
    """Memory slots held by the Part C runs now going: each run in progress has a claim file (D69 (4))."""
    n = 0
    for f in os.listdir(RUNS) if os.path.isdir(RUNS) else []:
        if f.endswith(".claim") and f.split("_")[0] in PART_C:
            n += SLOTS[2.0] if f[:-6].endswith("_refine2") else SLOTS[1.0]
    return n


def event_slots():
    cap = int(os.environ.get("STAGE7_EVENT_SLOTS", "0"))
    if cap <= 0:
        tot, _ = mem_gb()
        cap = max(SLOTS[2.0], int((tot - 4.0) / GB_EVENT))
    return cap


def room_for(sp_):
    """A Part C run starts only if its memory slots fit beside those of the Part C runs going and the free memory
    covers them (D69 (4)), or if no other Part C run is going; a Part A run always may."""
    if sp_["set"] not in PART_C:
        return True
    used = part_c_slots_in_use()
    if used == 0:
        return True
    need = SLOTS[sp_["refine"]]
    _, avail = mem_gb()
    return used + need <= event_slots() and avail >= need * GB_EVENT + 1.0


def _try_eventlist(worker):
    """Once every pertest run has ended, one worker writes the event list (a lock file decides which)."""
    if os.path.exists(EVENTLIST):
        return True
    a = [r["id"] for r in build_part_a() if r["set"] == "pertest"]
    have = {f[:-5] for f in os.listdir(RUNS) if f.endswith(".json")}
    if not all(i in have for i in a):
        return False
    try:
        fd = os.open(EVENTLOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return os.path.exists(EVENTLIST)
    with os.fdopen(fd, "w") as fh:
        fh.write(f"{worker} {os.getpid()} {RUN._utc()}\n")
    out = make_eventlist()
    print(f"{RUN._utc()} worker {worker}: Part C list written: {out['n']} runs {out['by_set']}, sha256 {out['sha256']}",
          flush=True)
    return True


def work(worker, of, budget_min, sets, wall_min=1e9, queue=False, label="unlabelled", wait_s=30.0):
    """v12_run.work's loop with the Stage 7 lists, folders and limits, in two phases: Part A's sets, then, once the
    event list exists, Part C's. Every rule of D43 (3), D47 (3) and D55 (3) is kept."""
    if not os.path.exists(TRIGGERS):
        raise SystemExit("results/stage7_triggers.json is missing: run `stage7_run.py triggers` first")
    os.makedirs(RUNS, exist_ok=True)
    os.makedirs(SERIES, exist_ok=True)
    ctx = RUN.Context()
    machine = RUN.machine_info(label)
    t0 = time.time()
    done = 0
    if hasattr(signal, "SIGALRM"):
        signal.signal(signal.SIGALRM, RUN._alarm)
    while True:
        runs = build_runs()
        started_any = waiting = False
        for i, sp_ in enumerate(runs):
            if sp_["set"] not in sets or (not queue and i % of != worker):
                continue
            path = os.path.join(RUNS, sp_["id"] + ".json")
            if os.path.exists(path):
                continue
            elapsed = (time.time() - t0) / 60.0
            left = wall_min - elapsed
            if elapsed > budget_min or left < START_MARGIN_MIN[sp_["refine"]] or os.path.exists(STOP_FILE):
                print(f"{RUN._utc()} worker {worker}: stopping after {done} runs (budget, wall time or stop file); "
                      f"next run {sp_['id']}", flush=True)
                return
            if not room_for(sp_):
                waiting = True
                continue
            claim = os.path.join(RUNS, sp_["id"] + ".claim")
            if queue and not RUN._claim(claim, worker):
                continue
            if sp_["set"] in PART_C and part_c_slots_in_use() > event_slots():     # another worker claimed first
                RUN._unclaim(claim)
                waiting = True
                continue
            started_any = True
            limit_s = int(RUN_LIMIT_MIN[sp_["refine"]] * 60)
            wall_s = int(left * 60) - RUN.WALL_MARGIN_S
            tries = 0
            while True:
                started = RUN._utc()
                try:
                    try:
                        RUN._arm(min(limit_s, wall_s), "wall" if wall_s < limit_s else "limit")
                        rec, series = run_one(sp_, ctx)
                    except KeyboardInterrupt:
                        if not RUN._DEADLINE["fired"]:
                            raise
                        if RUN._DEADLINE["kind"] == "wall":
                            raise RUN.WallTime("the hosting shell's time ran out") from None
                        raise RUN.RunTimeLimit("the run exceeded its time limit") from None
                except RUN.WallTime:
                    RUN._disarm()
                    RX.DT_BASE, RX.DT_TARGET, RX.DT_ACCEPT = 0.1, 1.0, 4.0
                    if queue:
                        RUN._unclaim(claim)
                    print(f"{RUN._utc()} worker {worker}: {sp_['id']} interrupted at the wall time and not recorded; "
                          f"stopping after {done} runs", flush=True)
                    return
                except Exception as exc:
                    import gc, traceback
                    RX.DT_BASE, RX.DT_TARGET, RX.DT_ACCEPT = 0.1, 1.0, 4.0
                    if RUN.is_memory_failure(repr(exc)) and tries < RUN.MEM_RETRIES:
                        tries += 1
                        RUN._disarm()
                        gc.collect()
                        print(f"{RUN._utc()} worker {worker}: {sp_['id']} short of memory ({repr(exc)[:60]}); "
                              f"retry {tries} in {RUN.MEM_WAIT_S} s", flush=True)
                        time.sleep(RUN.MEM_WAIT_S)
                        continue
                    rec, series = dict(sp_), None
                    rec.update({"failed": True, "error": repr(exc), "traceback": traceback.format_exc()})
                finally:
                    RUN._disarm()
                break
            if tries:
                rec["memory_retries"] = tries
            rec["worker_peak_memory_MB"] = peak_memory_mb()
            rec["started_utc"], rec["finished_utc"] = started, RUN._utc()
            rec["machine"] = machine
            if series is not None:
                np.savez_compressed(os.path.join(SERIES, sp_["id"] + ".npz"), **series)
            tmp = path + f".tmp{os.getpid()}"
            with open(tmp, "w") as fh:
                json.dump(rec, fh, indent=1, default=float)
            os.replace(tmp, path)
            if queue:
                RUN._unclaim(claim)
            done += 1
            if rec.get("failed"):
                print(f"{RUN._utc()} {sp_['id']}: FAILED {rec['error']}", flush=True)
            else:
                rr, ll = rec["resolved"], rec["lumped"]
                extra = ""
                if rr.get("after_event"):
                    extra = (f"; after the event: hot spot {rr['after_event']['Tmax_C']:.0f} C, "
                             f"lumped {ll['after_event']['T_C']:.0f} C")
                print(f"{RUN._utc()} {sp_['id']}: cell 1 {rec['T1max_C']:.1f} C; resolved "
                      f"{'%.1f s' % rr['t_prop_s'] if rr['propagated'] else 'none'} (peak {rr['peak_hottest_C']:.1f} C), "
                      f"lumped {'%.1f s' % ll['t_prop_s'] if ll['propagated'] else 'none'} (peak {ll['peak_C']:.1f} C)"
                      f"{extra}, residual {rr['energy_residual_rel']:.1e}, {rec['wall_s']:.0f} s", flush=True)
            break                                    # re-read the list: Part C may have appeared
        if started_any:
            continue
        if waiting:                                  # Part C runs wait for memory
            time.sleep(wait_s)
            continue
        if os.path.exists(EVENTLIST) or not any(s in sets for s in PART_C):
            print(f"{RUN._utc()} worker {worker}: all runs recorded ({done} this pass)", flush=True)
            return
        if not _try_eventlist(worker):
            time.sleep(wait_s)                       # the other workers' pertest runs are still going


def status():
    runs = build_runs()
    have = {f[:-5] for f in os.listdir(RUNS) if f.endswith(".json")} if os.path.isdir(RUNS) else set()
    by = {}
    for s in runs:
        b = by.setdefault(s["set"], [0, 0])
        b[0] += 1
        b[1] += s["id"] in have
    print(json.dumps({k: {"total": v[0], "done": v[1]} for k, v in by.items()}),
          "event list", "written" if os.path.exists(EVENTLIST) else "not yet")


def reset_claims():
    n = 0
    for f in os.listdir(RUNS) if os.path.isdir(RUNS) else []:
        if f.endswith(".claim"):
            RUN._unclaim(os.path.join(RUNS, f))
            n += 1
    if os.path.exists(EVENTLOCK) and not os.path.exists(EVENTLIST):
        os.remove(EVENTLOCK)
    print(f"{n} claims removed")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["triggers", "list", "events", "work", "status", "reset-claims"])
    ap.add_argument("--worker", type=int, default=0)
    ap.add_argument("--of", type=int, default=1)
    ap.add_argument("--budget-min", type=float, default=1e9)
    ap.add_argument("--wall-min", type=float, default=1e9)
    ap.add_argument("--sets", nargs="*", default=list(SETS))
    ap.add_argument("--queue", action="store_true")
    ap.add_argument("--label", default="unlabelled")
    a = ap.parse_args()
    if a.cmd == "triggers":
        if os.path.exists(TRIGGERS):
            raise SystemExit("results/stage7_triggers.json exists; the energies are found once")
        out = triggers()
        print(json.dumps([{k: r[k] for k in ("test", "connection", "target_C", "E_J", "T1max_C", "in_range",
                                             "iterations")} for r in out["rows"]], indent=1, default=float))
        runs = build_part_a()
        print(len(runs), "Part A runs; sha256", runs_hash(runs))
    elif a.cmd == "list":
        runs = build_part_a()
        print(len(runs), "Part A runs; sha256 of the list", runs_hash(runs))
        print({s: sum(r["set"] == s for r in runs) for s in PART_A})
        if os.path.exists(EVENTLIST):
            ev = json.load(open(EVENTLIST))
            print(ev["n"], "Part C runs; sha256", ev["sha256"], ev["by_set"])
    elif a.cmd == "events":
        if os.path.exists(EVENTLIST):
            raise SystemExit("results/stage7_eventlist.json exists; the Part C list is made once")
        out = make_eventlist()
        print(out["n"], "Part C runs", out["by_set"], "sha256", out["sha256"], "missing", out["pertest_missing"])
    elif a.cmd == "work":
        work(a.worker, a.of, a.budget_min, set(a.sets), a.wall_min, queue=a.queue, label=a.label)
    elif a.cmd == "reset-claims":
        reset_claims()
    else:
        status()
