#!/usr/bin/env python3
"""Stage 10 runs (predictions_stage10.md; DECISIONS.md D103 to D106).

Every run is a Stage 9 run (`stage9_run.run_one`'s inputs and loops, unchanged): one test of Fransson et al. with
its Stage 7 trigger, the central tabs, 25 C, the posterior-mean kinetics with the reaction heat fed back one-way, and a
fraction f of the test's ejected energy delivered to the neighbour from t = 0 through the half of its can facing the
trigger (Stage 8's triangular pulse over 21.39 s, or a constant power over 120, 240 or 360 s). What Stage 10 adds:
every run holds both neighbours with the stop at 255.7 C lifted, and records five probes of the resolved neighbour at
mid-length, the three thermocouple nodes of D102 (4) ("away", the Stage 9 node; "side", 88.3 degrees from the line
of contact; "facing", 0.33 degrees from it) and two beside them ("toward", on the line; "side_out", 94.4 degrees).

  Part A (D103): M50_PT_Exp4 under each reading Stage 9 found for it, to 332 s (Table 3's 272 s plus 60 s): no
  delivery; the 21.39 s delivery at both ends of its C2 threshold bracket, at the low, central and high contacts; the
  long deliveries at their f_t (C2 over 240 and 360 s, C1 over 360 s); and, not registered, the 21.39 s C1 bracket's
  ends, the 120 s C2 bracket's ends and the 240 s C1 bracket's ends, at the central contact.
  Part B (D104): for the five low-maximum tests, f_max at the side and facing nodes, by Stage 9's search
  (`stage9_search.fmax_state`) on each node's peak over 900 s, from f = 0 to f*_lo(C1) of Stage 8 and beyond to 1
  where the peak there still falls short; the runs of a test are shared by its two nodes' searches.
  Part C's six no-delivery runs (D104 (4)): f = 0 to 900 s for the six tests whose Stage 7 run stopped at the hot
  spot's crossing and that Stage 9 did not run with the stop lifted, for the no-delivery peak of C2.

Records go to results/stage10_runs/<id>.json and series to results/stage10_series/<id>.npz.

Usage:
  python3 stage10_run.py list | chains | status | reset-claims
  python3 stage10_run.py work --worker K --label NAME
"""
import os as _os
for _k in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "NUMBA_NUM_THREADS"):
    _os.environ.setdefault(_k, "1")      # D43 (4): one thread per library; set before numpy and numba load
import argparse, glob, hashlib, json, os, signal, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v12_model as V                    # noqa: E402  (unchanged)
import v12_run as RUN                    # noqa: E402  (unchanged)
import reactive as RX                    # noqa: E402  (unchanged)
import stage9_run as R9                  # noqa: E402  (unchanged)
import stage9_model as M9                # noqa: E402  (unchanged)
import stage9_search as S9               # noqa: E402  (unchanged)
import stage8_search as SR8              # noqa: E402  (unchanged)
import stage10_inputs as IN              # noqa: E402

RES = os.path.join(HERE, "..", "results")
TAG = os.environ.get("STAGE10_RUNS_TAG", "")
RUNS = os.path.join(RES, "stage10_runs" + TAG)
SERIES = os.path.join(RES, "stage10_series" + TAG)
STOP_FILE = os.path.join(RES, "stage10_STOP")
RUN_LIMIT_MIN = 1440.0                   # as D96 (1): a run that takes longer is recorded as failed
START_MARGIN_MIN = 5.0
PROBES = {k: d["node"] for k, d in list(IN.NODES.items()) + list(IN.EXTRA_PROBES.items())}
PART_B_T_END = 900.0


# ------------------------------------------------------------------------------------------------ the runs
def cfg_of(name):
    if name in ("none", "tri21"):
        return R9.TRI21()
    if name.startswith("con"):
        return R9.CON(float(name[3:]))
    raise ValueError(name)


def spec(kind, test, cfg_name, f, h="central", t_end=900.0, reading=None):
    c = cfg_of(cfg_name)
    sp = R9.spec(c, test, f, "both", stop=False, kind=kind)
    f = sp["f"]
    sp.update({"stage": 10, "h": h, "t_end_s": float(t_end), "probes": dict(PROBES), "reading": reading})
    sp["id"] = f"s10_{sp['cfg']}_h{h}_{test}_f{f:.9f}_t{int(round(t_end))}"
    return sp


def part_a_runs():
    out = []
    for name, r in IN.READINGS.items():
        for h in (IN.CONTACTS if name in IN.CONTACT_BRACKET else ("central",)):
            out.append(spec("A", IN.TEST_A, r["cfg"], r["f"], h, IN.T_END_A_S, reading=name))
    return out


def run_one(sp, ctx, keep_series=True):
    """Stage 9's run (`stage9_run.run_one`) with five probes in place of two: the same history, source, kinetics and
    loops (stage9_model), recorded with every probe's history and peak."""
    t_start = time.time()
    t1f, t1data, T1max_C, tT1max = ctx.history(sp)
    kin, draw = ctx.kinetics(sp["kin"])
    g_pos, g_neg = V.tabs(sp["connection"], V.G_TAB[sp["g"]])
    model = ctx.model(sp["h"], sp["refine"])
    where = IN.theta_ok(model)                                       # V2: the nodes are those of D102 (4)
    src_r, src_l = [], []
    if sp["E_delivered_J"] > 0.0:
        src_r = [M9.Source("delivery", R9._pulse(sp), ctx.share(sp["h"], sp["refine"]))]
        src_l = [M9.Source("delivery", R9._pulse(sp))]
    r = M9.run_resolved(model, t1f, g_pos, g_neg, kin=kin, t_amb=sp["T_amb_K"], t_end=sp["t_end_s"], stop_level=None,
                        probes=sp["probes"], keep_series=keep_series, max_facts=6, sources=src_r, max_sub=sp["max_sub"],
                        sei0=sp["sei0"])
    lr = M9.run_lumped(t1f, g_pos + g_neg, g_link=V.g_contact(V.H_CONTACT[sp["h"]]), f_view=V.F_TOUCH, kin=kin,
                       t_amb=sp["T_amb_K"], t_end=sp["t_end_s"], stop_level=None, sources=src_l, max_sub=sp["max_sub"],
                       sei0=sp["sei0"])
    rec = dict(sp)
    rec.update({"draw": draw, "h_c_W_m2K": V.H_CONTACT[sp["h"]], "G_tab_W_K": V.G_TAB[sp["g"]],
                "G_contact_W_K": V.g_contact(V.H_CONTACT[sp["h"]]), "g_pos_W_K": g_pos, "g_neg_W_K": g_neg,
                "T1max_C": T1max_C, "t_T1max_s": tT1max, "n_nodes": int(model.C.size), "probe_where": where})
    t_x = r["cross_s"]["T_onset_low"]
    rec["resolved"] = {"propagated": t_x is not None, "t_prop_s": t_x, "t_end_s": r["t_end_s"], "steps": r["steps"],
                       "rejected": r["rejected"], "max_implicit_nodes": r["max_implicit_nodes"],
                       "energy_residual_rel": r["energy_residual_rel"], "peak_hottest_C": r["peak"]["Tmax_C"],
                       "t_peak_hottest_s": r["peak"]["t_s"], "where_peak": model.where(r["peak"]["imax"]),
                       "peak_mean_C": r["peak"]["Tmean_C"], "probe_peak": r["probe_peak"], "cross_s": r["cross_s"],
                       "energy_J": r["energy_J"], "stored_J": r["stored_J"], "net_in_J": r["net_in_J"],
                       "sources": r["sources"], "max_sub": r["max_sub"], "steps_with_max_sub": r["steps_with_max_sub"],
                       "conversion_volume_mean_end": r["conversion_volume_mean_end"]}
    t_xl = lr["cross_s"]["T_onset_low"]
    rec["lumped"] = {"propagated": t_xl is not None, "t_prop_s": t_xl, "peak_C": lr["peak"]["T_C"],
                     "t_peak_s": lr["peak"]["t_s"], "reaction_heat_J": lr["reaction_heat_J"], "t_end_s": lr["t_end_s"],
                     "energy_J": lr["energy_J"], "energy_residual_rel": lr["energy_residual_rel"],
                     "cross_s": lr["cross_s"], "sources": lr["sources"], "stored_J": lr["stored_J"],
                     "net_in_J": lr["net_in_J"]}
    series = {"t1_t": t1data[:, 0], "t1_T1_C": t1data[:, 1], "t1_T2_C": t1data[:, 2]}
    s = r["series"]
    series.update({"t": s[:, 0], "T1": s[:, 1], "Tmax": s[:, 2], "Tmean": s[:, 3], "imax": s[:, 4].astype(int),
                   "probe_t": r["probe_t"], "t_lumped": lr["series"][:, 0], "T_lumped": lr["series"][:, 1]})
    for k in sp["probes"]:
        series["probe_" + k] = r["probe_T"][k]
    rec["wall_s"] = time.time() - t_start
    return rec, (series if keep_series else None)


# ------------------------------------------------------------------------------------------------ Part B's chains
def load_records(runs_dir=None):
    d = runs_dir or RUNS
    out = {}
    for p in glob.glob(os.path.join(d, "s10_*.json")):
        r = json.load(open(p))
        out[r["id"]] = r
    return out


def fstar_lo_c1(test):
    fs = R9.fstar8()[test]["C1"]
    return 0.0 if fs["status"] == "zero" else float(fs["lo"])


def chain_states(recs):
    """For each of the five tests and the side and facing nodes: Stage 9's f_max search on that node's peak."""
    out = {}
    for test in IN.PART_B_TESTS:
        pk = {n: {} for n in IN.PART_B_NODES}
        for r in recs.values():
            if r.get("kind") == "B" and r["test"] == test and not r.get("failed"):
                for n in IN.PART_B_NODES:
                    pk[n][r["f"]] = r["resolved"]["probe_peak"][n]["T_C"]
        M = R9.max_meas(test)
        for n in IN.PART_B_NODES:
            st = S9.fmax_state(M, fstar_lo_c1(test), pk[n], tol_k=IN.PEAK_TOL_K, width=IN.WIDTH_M, f_end=IN.F_MAX)
            st["test"], st["node"] = test, n
            out[f"B_{n}_{test}"] = st
    return out


def build_runs(recs):
    runs = []
    for st in chain_states(recs).values():
        if st["status"] == "searching" and st.get("next") is not None:
            runs.append(spec("B", st["test"], "tri21", st["next"], "central", PART_B_T_END))
    runs += part_a_runs()
    runs += [spec("C", x, "none", 0.0, "central", PART_B_T_END) for x in IN.PART_C_ZERO_TESTS]
    seen, out = set(), []
    for r in runs:                                  # the two nodes' searches can ask for the same run
        if r["id"] not in seen:
            seen.add(r["id"])
            out.append(r)
    return out


def runs_hash(runs):
    keys = sorted(json.dumps({k: v for k, v in r.items() if k not in ("kind", "reading")}, sort_keys=True,
                             default=float) for r in runs)
    return hashlib.sha256("\n".join(keys).encode()).hexdigest()


# ------------------------------------------------------------------------------------------------ the work loop
def _paths(sp):
    return os.path.join(RUNS, sp["id"] + ".json"), os.path.join(SERIES, sp["id"] + ".npz")


def work(worker, label="unlabelled", wait_s=10.0, once=False):
    """Stage 9's loop (claims, a run recorded since the list was read let go, a failed run recorded as failed), on
    Stage 10's list, which grows as Part B's searches advance."""
    for d in (RUNS, SERIES):
        os.makedirs(d, exist_ok=True)
    ctx = R9.Context()
    machine = RUN.machine_info(label)
    done = 0
    if hasattr(signal, "SIGALRM"):
        signal.signal(signal.SIGALRM, RUN._alarm)
    while True:
        recs = load_records()
        pending = [r for r in build_runs(recs) if r["id"] not in recs]
        if not pending:
            if [f for f in os.listdir(RUNS) if f.endswith(".claim")]:
                time.sleep(wait_s)                   # another worker's run may extend the list
                continue
            print(f"{RUN._utc()} worker {worker}: nothing left to run ({done} this pass)", flush=True)
            return done
        started = False
        for sp in pending:
            if os.path.exists(STOP_FILE):
                print(f"{RUN._utc()} worker {worker}: stop file; stopping after {done} runs", flush=True)
                return done
            claim = os.path.join(RUNS, sp["id"] + ".claim")
            if not RUN._claim(claim, worker):
                continue
            path, spath = _paths(sp)
            if os.path.exists(path):
                RUN._unclaim(claim)
                continue
            started = True
            st_utc = RUN._utc()
            try:
                try:
                    RUN._arm(int(RUN_LIMIT_MIN * 60), "limit")
                    rec, series = run_one(sp, ctx)
                except KeyboardInterrupt:
                    if not RUN._DEADLINE["fired"]:
                        raise
                    raise RUN.RunTimeLimit("the run exceeded its time limit") from None
            except Exception as exc:
                import traceback
                RX.DT_BASE, RX.DT_TARGET, RX.DT_ACCEPT = 0.1, 1.0, 4.0
                rec, series = dict(sp), None
                rec.update({"failed": True, "error": repr(exc), "traceback": traceback.format_exc()})
            finally:
                RUN._disarm()
            rec["worker_peak_memory_MB"] = R9.peak_memory_mb()
            rec["started_utc"], rec["finished_utc"] = st_utc, RUN._utc()
            rec["machine"], rec["worker"] = machine, worker
            if series is not None:
                np.savez_compressed(spath, **series)
            tmp = path + f".tmp{os.getpid()}"
            with open(tmp, "w") as fh:
                json.dump(rec, fh, indent=1, default=float)
            R9._put(tmp, path)
            RUN._unclaim(claim)
            done += 1
            print(f"{RUN._utc()} {summary(rec)}", flush=True)
            break
        if once:
            return done
        if not started:
            time.sleep(wait_s)


def summary(rec):
    if rec.get("failed"):
        return f"{rec['id']}: FAILED {rec['error']}"
    rr, ll = rec["resolved"], rec["lumped"]
    pk = rr["probe_peak"]
    return (f"{rec['id']}; hot spot {'%.1f s' % rr['t_prop_s'] if rr['propagated'] else 'none'} (peak "
            f"{rr['peak_hottest_C']:.1f} C); away {pk['away']['T_C']:.1f}, side {pk['side']['T_C']:.1f}, facing "
            f"{pk['facing']['T_C']:.1f} C; lumped {'%.1f s' % ll['t_prop_s'] if ll['propagated'] else 'none'}; "
            f"{rec['wall_s']:.0f} s")


def status():
    recs = load_records()
    runs = build_runs(recs)
    pend = [r for r in runs if r["id"] not in recs]
    print(json.dumps({"records": len(recs), "failed": sum(1 for r in recs.values() if r.get("failed")),
                      "pending_now": len(pend), "chains": {k: (s["status"], s.get("next"), s.get("f_max"))
                                                           for k, s in chain_states(recs).items()},
                      "claims": [f for f in os.listdir(RUNS) if f.endswith(".claim")] if os.path.isdir(RUNS) else []}))


def reset_claims():
    n = 0
    for f in os.listdir(RUNS) if os.path.isdir(RUNS) else []:
        if f.endswith(".claim"):
            RUN._unclaim(os.path.join(RUNS, f))
            n += 1
    print(f"{n} claims removed")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["list", "chains", "work", "status", "reset-claims"])
    ap.add_argument("--worker", type=int, default=0)
    ap.add_argument("--label", default="unlabelled")
    a = ap.parse_args()
    if a.cmd == "list":
        runs = build_runs(load_records())
        print(len(runs), "runs listed now; sha256", runs_hash(runs))
        for r in runs:
            print(r["id"])
    elif a.cmd == "chains":
        for name, st in chain_states(load_records()).items():
            print(name, st["status"], st.get("lo"), st.get("hi"), st.get("next"), st.get("f_max"))
    elif a.cmd == "work":
        work(a.worker, label=a.label)
    elif a.cmd == "reset-claims":
        reset_claims()
    else:
        status()
