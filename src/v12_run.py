#!/usr/bin/env python3
"""Stage 5 (version 1.2.0) runs, in the order and with the outputs fixed by predictions_v12.md and DECISIONS.md D35,
D39 and D43.

Sets, run in this order:
  grid   posterior-mean kinetics, 3 contact conductances x 3 tab conductances x 2 releases x 2 connections (36);
  sens   sensitivities at the central case (30 s release): ambient 20 and 30 C, trigger energy at the Databank nail
     tests' minimum and median (8);
  v3     V3 at the central case (30 s release): every mesh spacing halved; every step limit halved (4);
  draws  the 200 Stage 3 draws at the central case, 30 s release, both connections (400);
  fact   the factorial: 200 draws x 3 contacts x the tab bracket (low, high) x 2 releases x 2 connections (4800),
     ordered by draw so that a partial set is a set of whole draws.
Each run integrates the resolved neighbour (stopped when its hottest node reaches 255.7 C, or at 900 s) and the
lumped neighbour (stopped likewise), both driven by the same cell-1 history of the lumped pair, and writes one
record to results/v12_runs/<id>.json; the grid, sens and v3 sets also keep their series in results/v12_series/<id>.npz.

Usage:
  python3 v12_run.py list                          # the run list and its hash
  python3 v12_run.py work --worker 0 --of 2 [--budget-min 110] [--wall-min 115] [--sets grid sens v3 draws fact]
  python3 v12_run.py status
Workers take every run whose index modulo --of equals --worker, skip runs already recorded, and stop starting new
runs once the budget is spent or too little of the hosting shell's time (--wall-min) is left; a run still going at
the wall time is interrupted unrecorded and redone whole by the next pass, so an interrupted set resumes where it
stopped and no record depends on where a pass ended.
"""
import os as _os
for _k in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "NUMBA_NUM_THREADS"):
    _os.environ.setdefault(_k, "1")      # D43 (4): one thread per library; set before numpy and numba load
import _thread, argparse, csv, hashlib, json, math, os, signal, sys, threading, time
import numpy as np

import v12_model as V
import lumped_two_cell as LP
import bcrnn
import reactive as RX

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
RUNS = os.path.join(RES, "v12_runs")
SERIES = os.path.join(RES, "v12_series")
DATABANK_USED = os.path.join(HERE, "..", "inputs", "databank", "databank_m50_used.csv")
CENTRAL = {"h": "central", "g": "central", "tau": 30.0}


def nail_energies():
    """Cell-body energies of the Databank's LG M50 nail tests at 100 % SOC (the 17 rows the two-cell study used)."""
    rows = list(csv.DictReader(open(DATABANK_USED)))
    e = sorted(1e3 * float(r["Energy-Fraction-Cell-Body-kJ"]) for r in rows if "Nail" in r["Trigger-Mechanism"])
    return e


def build_runs():
    runs = []

    def add(set_, kin, conn, h, g, tau, e=V.E_BODY, ta=LP.T_AMB, refine=1.0, dt_scale=1.0, tag=""):
        kin_s = "mean" if kin == "mean" else f"d{kin:03d}"
        rid = f"{set_}_{kin_s}_{conn}_h{h}_g{g}_tau{int(tau)}" + tag
        runs.append({"id": rid, "set": set_, "kin": kin, "connection": conn, "h": h, "g": g, "tau": float(tau),
                     "E_body_J": float(e), "T_amb_K": float(ta), "refine": float(refine), "dt_scale": float(dt_scale)})

    for conn in V.CONNECTIONS:
        for tau in LP.TAU_REL_LIST:
            for h in ("low", "central", "high"):
                for g in ("low", "central", "high"):
                    add("grid", "mean", conn, h, g, tau)
    e_nail = nail_energies()
    e_min, e_med = e_nail[0], float(np.median(e_nail))
    for conn in V.CONNECTIONS:
        for ta_c in (20.0, 30.0):
            add("sens", "mean", conn, "central", "central", 30.0, ta=ta_c + 273.15, tag=f"_amb{int(ta_c)}")
        add("sens", "mean", conn, "central", "central", 30.0, e=e_min, tag="_Enailmin")
        add("sens", "mean", conn, "central", "central", 30.0, e=e_med, tag="_Enailmedian")
    for conn in V.CONNECTIONS:
        add("v3", "mean", conn, "central", "central", 30.0, refine=2.0, tag="_refine2")
        add("v3", "mean", conn, "central", "central", 30.0, dt_scale=0.5, tag="_dthalf")
    for d in range(1, 201):
        for conn in V.CONNECTIONS:
            add("draws", d, conn, "central", "central", 30.0)
    for d in range(1, 201):
        for conn in V.CONNECTIONS:
            for tau in LP.TAU_REL_LIST:
                for h in ("low", "central", "high"):
                    for g in ("low", "high"):
                        add("fact", d, conn, h, g, tau)
    return runs


def runs_hash(runs):
    return hashlib.sha256(json.dumps(runs, sort_keys=True).encode()).hexdigest()


# ------------------------------------------------------------------------------------------------ one run
class Context:
    def __init__(self):
        self.models = {}
        self.t1 = {}
        self.draws = None
        self.particles = None

    def model(self, h, refine):
        key = (h, refine)
        if key not in self.models:
            if len(self.models) >= 3:
                self.models.pop(next(iter(self.models)))
            self.models[key] = V.Cell2Contact(V.H_CONTACT[h], refine=refine)
        return self.models[key]

    def history(self, spec):
        key = (spec["connection"], spec["h"], spec["g"], spec["tau"], spec["E_body_J"], spec["T_amb_K"])
        if key not in self.t1:
            if len(self.t1) > 64:
                self.t1.clear()
            self.t1[key] = V.stage5_t1(spec["connection"], V.H_CONTACT[spec["h"]], V.G_TAB[spec["g"]], spec["tau"],
                                       spec["E_body_J"], spec["T_amb_K"])
        return self.t1[key]

    def kinetics(self, kin):
        if kin == "mean":
            return bcrnn.Kinetics(), None
        if self.draws is None:
            import stage3_draws as S
            self.draws, self.particles = S.all_draws()
        d, ae, sep, cat = self.draws[kin - 1]
        assert d == kin
        import stage3_draws as S
        return S.draw_kinetics(self.particles, ae, sep, cat), {"draw": d, "an_ele_column": ae, "separator_column": sep,
                                                               "ncm811_column": cat}


def _at(t_arr, y_arr, t):
    return float(np.interp(t, t_arr, y_arr))


def run_one(spec, ctx, keep_series):
    t_start = time.time()
    model = ctx.model(spec["h"], spec["refine"])
    t1f, t1data, T1max_C, tT1max = ctx.history(spec)
    kin, draw = ctx.kinetics(spec["kin"])
    g_pos, g_neg = V.tabs(spec["connection"], V.G_TAB[spec["g"]])
    saved = (RX.DT_BASE, RX.DT_TARGET, RX.DT_ACCEPT)
    if spec["dt_scale"] != 1.0:
        RX.DT_BASE, RX.DT_TARGET, RX.DT_ACCEPT = (x * spec["dt_scale"] for x in saved)
    try:
        r = V.run_resolved(model, t1f, g_pos, g_neg, kin=kin, t_amb=spec["T_amb_K"], stop_level=V.LEVEL_PROP,
                           probes=model.probes, keep_series=keep_series, max_facts=6 if spec["refine"] == 1.0 else 2)
        lr = V.run_lumped(t1f, g_pos + g_neg, g_link=V.g_contact(V.H_CONTACT[spec["h"]]), f_view=V.F_TOUCH, kin=kin,
                          t_amb=spec["T_amb_K"], stop_level=V.LEVEL_PROP)
    finally:
        RX.DT_BASE, RX.DT_TARGET, RX.DT_ACCEPT = saved
    res = {"propagated": r["stop"] is not None, "t_end_s": r["t_end_s"], "steps": r["steps"], "rejected": r["rejected"],
           "max_implicit_nodes": r["max_implicit_nodes"], "energy_residual_rel": r["energy_residual_rel"],
           "peak_hottest_C": r["peak"]["Tmax_C"], "t_peak_hottest_s": r["peak"]["t_s"],
           "peak_mean_C": r["peak"]["Tmean_C"], "probe_peak": r["probe_peak"],
           "in_rxn_J": r["energy_J"]["in_rxn"], "cross_s": r["cross_s"]}
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
            # exploratory (D39): over the paper's Section 2, from cell 1's maximum to propagation
            if tp > tT1max:
                res[f"rate_section2_{k}_C_per_s"] = (Tp - _at(pt, pT[k], tT1max)) / (tp - tT1max)
    lres = {"propagated": lr["stop"] is not None, "peak_C": lr["peak"]["T_C"], "t_peak_s": lr["peak"]["t_s"],
            "reaction_heat_J": lr["reaction_heat_J"], "t_end_s": lr["t_end_s"]}
    if lr["stop"] is not None:
        tp = lr["stop"]["t_s"]
        w0 = max(0.0, tp - 60.0)
        Tp = _at(lr["steps_t"], lr["steps_T"], tp); T0 = _at(lr["steps_t"], lr["steps_T"], w0)
        lres.update({"t_prop_s": tp, "rate_C_per_s": (Tp - T0) / (tp - w0) if tp > w0 else None,
                     "rate_window_s": tp - w0})
    rec = dict(spec)
    rec.update({"draw": draw, "h_c_W_m2K": V.H_CONTACT[spec["h"]], "G_tab_W_K": V.G_TAB[spec["g"]],
                "G_contact_W_K": V.g_contact(V.H_CONTACT[spec["h"]]), "g_pos_W_K": g_pos, "g_neg_W_K": g_neg,
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


RUN_LIMIT_MIN = {1.0: 40.0, 2.0: 100.0}         # D43 (3): a run that takes longer is recorded as failed
START_MARGIN_MIN = {1.0: 15.0, 2.0: 75.0}       # a run starts only if this much of the hosting shell's time is left
WALL_MARGIN_S = 30                              # a run still going this close to wall_min is interrupted


class RunTimeLimit(Exception):
    pass


class WallTime(Exception):
    pass


_DEADLINE = {"kind": "limit", "timer": None, "fired": False}


def _alarm(signum, frame):
    if _DEADLINE["kind"] == "wall":
        raise WallTime("the hosting shell's time ran out")
    raise RunTimeLimit("the run exceeded its time limit")


def _fire():
    """Where there is no SIGALRM (Windows), a timer thread interrupts the main thread at the deadline."""
    _DEADLINE["fired"] = True
    _thread.interrupt_main()


def _arm(seconds, kind):
    _DEADLINE.update(kind=kind, fired=False)
    if hasattr(signal, "SIGALRM"):
        signal.alarm(max(1, int(seconds)))
    else:
        _DEADLINE["timer"] = threading.Timer(max(1, int(seconds)), _fire)
        _DEADLINE["timer"].daemon = True
        _DEADLINE["timer"].start()


def _disarm():
    if hasattr(signal, "SIGALRM"):
        signal.alarm(0)
    elif _DEADLINE["timer"] is not None:
        _DEADLINE["timer"].cancel()
        _DEADLINE["timer"] = None


def _utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def work(worker, of, budget_min, sets, wall_min=115.0):
    """Runs this worker's share in list order. No run starts once budget_min is spent, or when less than its start
    margin is left before wall_min, the length of the shell command that hosts the worker. A run still going 30 s
    before wall_min is interrupted and left unrecorded, so the next pass runs it again from the start; a run that
    exceeds its own time limit (D43 (3)) is recorded as failed. Each record carries its start and finish (UTC)."""
    os.makedirs(RUNS, exist_ok=True); os.makedirs(SERIES, exist_ok=True)
    runs = build_runs()
    ctx = Context()
    t0 = time.time()
    done = 0
    if hasattr(signal, "SIGALRM"):
        signal.signal(signal.SIGALRM, _alarm)
    for i, spec in enumerate(runs):
        if i % of != worker or spec["set"] not in sets:
            continue
        path = os.path.join(RUNS, spec["id"] + ".json")
        if os.path.exists(path):
            continue
        elapsed = (time.time() - t0) / 60.0
        left = wall_min - elapsed
        if elapsed > budget_min or left < START_MARGIN_MIN[spec["refine"]]:
            print(f"{_utc()} worker {worker}: stopping after {done} runs (budget or wall time); next run {spec['id']}",
                  flush=True)
            return
        limit_s = int(RUN_LIMIT_MIN[spec["refine"]] * 60)
        wall_s = int(left * 60) - WALL_MARGIN_S
        started = _utc()
        _arm(min(limit_s, wall_s), "wall" if wall_s < limit_s else "limit")
        try:
            try:
                rec, series = run_one(spec, ctx, keep_series=spec["set"] in ("grid", "sens", "v3"))
            except KeyboardInterrupt:                  # the timer thread's interrupt, not a user's Ctrl-C
                if not _DEADLINE["fired"]:
                    raise
                if _DEADLINE["kind"] == "wall":
                    raise WallTime("the hosting shell's time ran out") from None
                raise RunTimeLimit("the run exceeded its time limit") from None
        except WallTime:                               # not a failure: the run is redone whole by the next pass
            _disarm()
            RX.DT_BASE, RX.DT_TARGET, RX.DT_ACCEPT = 0.1, 1.0, 4.0
            print(f"{_utc()} worker {worker}: {spec['id']} interrupted at the wall time and not recorded; "
                  f"stopping after {done} runs", flush=True)
            return
        except Exception as exc:                       # D43 (3): recorded as failed, never rerun differently
            import traceback
            rec, series = dict(spec), None
            rec.update({"failed": True, "error": repr(exc), "traceback": traceback.format_exc()})
            RX.DT_BASE, RX.DT_TARGET, RX.DT_ACCEPT = 0.1, 1.0, 4.0
        finally:
            _disarm()
        rec["started_utc"], rec["finished_utc"] = started, _utc()
        if series is not None:
            np.savez_compressed(os.path.join(SERIES, spec["id"] + ".npz"), **series)
        tmp = path + f".tmp{os.getpid()}"
        with open(tmp, "w") as fh:
            json.dump(rec, fh, indent=1, default=float)
        os.replace(tmp, path)
        done += 1
        if rec.get("failed"):
            print(f"{_utc()} {spec['id']}: FAILED {rec['error']}", flush=True)
            continue
        rr, ll = rec["resolved"], rec["lumped"]
        print(f"{_utc()} {spec['id']}: resolved {'%.1f s' % rr['t_prop_s'] if rr['propagated'] else 'none'} "
              f"(peak {rr['peak_hottest_C']:.1f} C), lumped {'%.1f s' % ll['t_prop_s'] if ll['propagated'] else 'none'} "
              f"(peak {ll['peak_C']:.1f} C), residual {rr['energy_residual_rel']:.1e}, {rec['wall_s']:.0f} s", flush=True)
    print(f"{_utc()} worker {worker}: all assigned runs recorded ({done} this pass)", flush=True)


def status():
    runs = build_runs()
    have = {f[:-5] for f in os.listdir(RUNS)} if os.path.isdir(RUNS) else set()
    by = {}
    for s in runs:
        b = by.setdefault(s["set"], [0, 0])
        b[0] += 1; b[1] += s["id"] in have
    walls = []
    for f in os.listdir(RUNS) if os.path.isdir(RUNS) else []:
        if f.endswith(".json"):
            try:
                walls.append(json.load(open(os.path.join(RUNS, f)))["wall_s"])
            except Exception:
                pass
    print(json.dumps({k: {"total": v[0], "done": v[1]} for k, v in by.items()}),
          "mean wall", round(float(np.mean(walls)), 1) if walls else None)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["list", "work", "status"])
    ap.add_argument("--worker", type=int, default=0)
    ap.add_argument("--of", type=int, default=1)
    ap.add_argument("--budget-min", type=float, default=110.0)
    ap.add_argument("--wall-min", type=float, default=115.0)
    ap.add_argument("--sets", nargs="*", default=["grid", "sens", "v3", "draws", "fact"])
    a = ap.parse_args()
    if a.cmd == "list":
        runs = build_runs()
        print(len(runs), "runs; sha256 of the run list", runs_hash(runs))
        print({s: sum(r["set"] == s for r in runs) for s in ("grid", "sens", "v3", "draws", "fact")})
        print("nail-test energies (J):", nail_energies())
    elif a.cmd == "work":
        work(a.worker, a.of, a.budget_min, set(a.sets), a.wall_min)
    else:
        status()
