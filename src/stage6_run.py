#!/usr/bin/env python3
"""Stage 6, Part B runs: the trigger matched to the tests (predictions_stage6.md; DECISIONS.md D52 to D56).

Steps, in order:
  trigger   cell 1's history at the central case for every trigger energy and release duration of D52 and D53, the
            selection of the matched case (D54 (2) and (3)) and the exploratory peak-matched energy (D54 (5)), into
            results/stage6_trigger.json. It computes no history of the neighbour.
  list      the run list and its SHA-256 (after `trigger`; before it, the registered sets under both outcomes of the
            selection, as predictions_stage6.md records them);
  work      the runs, as Stage 5 ran them (v12_run.run_one, unchanged): the resolved neighbour stopped when its
            hottest node reaches 255.7 C or at 900 s, the lumped neighbour likewise, both driven by the same cell-1
            history, with the reaction heat fed back one-way. Each record carries, beside Stage 5's fields, the A1
            quantities of stage6_crossings.a1 computed from the run's own histories (every run, the draws included),
            and the times at which the hottest node and the lumped neighbour reach 255.7 C.
Sets, run in this order (D55 (1)); the reference case is Stage 5's grid, archived and not rerun:
  v3       at the central matched case: every mesh spacing halved; every step limit halved (4);
  body     33.2 kJ (Stage 5's energy) x the three release durations x 7 configurations x 2 connections (42);
  total    the Databank's median total energy, 107.0 kJ, likewise (42);
  bracket  the total's minimum and maximum, 91.2 and 110.8 kJ, at the central configuration, median duration (4);
  peak     exploratory: the peak-matched energy at the median duration x 7 configurations x 2 connections (14);
  draws    the 200 Stage 3 draws at the central matched case, both connections (400).
The 7 configurations: each contact (low, central, high) with the tab bracket (5 and 10 mW/K), and the central
contact with the central tabs (6.8 mW/K). Records go to results/stage6_runs/<id>.json; every set but the draws also
keeps its series in results/stage6_series/<id>.npz.

Usage:
  python3 stage6_run.py trigger
  python3 stage6_run.py list
  python3 stage6_run.py work --queue --label NAME [--worker K --of N] [--budget-min M] [--wall-min W]
  python3 stage6_run.py status | reset-claims
"""
import os as _os
for _k in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "NUMBA_NUM_THREADS"):
    _os.environ.setdefault(_k, "1")      # D43 (4): one thread per library; set before numpy and numba load
import argparse, hashlib, json, os, signal, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v12_model as V
import v12_run as RUN
import reactive as RX
import stage6_inputs as IN
import stage6_crossings as CR

RES = os.path.join(HERE, "..", "results")
RUNS = os.path.join(RES, "stage6_runs" + os.environ.get("STAGE6_RUNS_TAG", ""))
SERIES = os.path.join(RES, "stage6_series" + os.environ.get("STAGE6_RUNS_TAG", ""))
TRIGGER = os.path.join(RES, "stage6_trigger.json")
STOP_FILE = os.path.join(RES, "stage6_STOP")      # if this file exists, no worker starts another run
SETS = ("v3", "body", "total", "bracket", "peak", "draws")
CONFIGS = [("low", "low"), ("low", "high"), ("central", "low"), ("central", "high"), ("high", "low"), ("high", "high"),
           ("central", "central")]
RUN_LIMIT_MIN = {1.0: 40.0, 2.0: 180.0}          # D55 (4): a run that takes longer is recorded as failed
PEAK_TOL_K = 0.01                                 # D54 (5): the peak-matched energy's bisection
T1_LO, T1_HI = IN.measured()["trigger_max_range_C"]          # 164 and 832 C, inclusive (D54 (2))
T1_TARGET = IN.measured()["trigger_max_median_C"]            # 704.5 C (D54 (5))


def levels():
    dur = IN.durations()
    en = IN.energies()
    return {"tau_s": dur["release_durations_s"], "tau_median_s": dur["median_s"],
            "E_body_J": V.E_BODY, "E_total_J": en["total_median_J"],
            "E_bracket_J": [en["total_min_J"], en["total_max_J"]]}


# ------------------------------------------------------------------------------------------------ the trigger
def t1_peak(e, tau, connection, h="central", g="central"):
    f, data, T1max, tmax = V.stage5_t1(connection, V.H_CONTACT[h], V.G_TAB[g], tau, e)
    return float(T1max), float(tmax)


def qualifies(T1max_C):
    return T1_LO <= T1max_C <= T1_HI


def trigger(path=TRIGGER):
    """D54: cell 1's peak at the central case for each energy and duration, the selection, and the peak-matched
    energy. No history of the neighbour is computed here."""
    L = levels()
    taus = L["tau_s"]
    rows = []
    named = [("body", L["E_body_J"]), ("total", L["E_total_J"]), ("bracket_min", L["E_bracket_J"][0]),
             ("bracket_max", L["E_bracket_J"][1])]
    for name, e in named:
        for tau in taus:
            for conn in V.CONNECTIONS:
                T1, t1 = t1_peak(e, tau, conn)
                rows.append({"energy": name, "E_J": e, "tau_s": tau, "connection": conn, "T1max_C": T1,
                             "t_T1max_s": t1, "inside_measured_range": qualifies(T1)})
    sel = {}
    for name in ("body", "total"):
        sel[name] = {f"{tau:.2f}": all(r["inside_measured_range"] for r in rows
                                       if r["energy"] == name and r["tau_s"] == tau) for tau in taus}
    tm = L["tau_median_s"]
    q_body, q_total = sel["body"][f"{tm:.2f}"], sel["total"][f"{tm:.2f}"]
    if q_total:
        central_energy = ("total", L["E_total_J"])
    elif q_body:
        central_energy = ("body", L["E_body_J"])
    else:
        central_energy = (None, None)
    # D54 (5), exploratory: the energy that puts cell 1's peak at the measured median, series, median duration
    lo, hi = L["E_body_J"], L["E_total_J"]
    f_lo, f_hi = t1_peak(lo, tm, "series")[0] - T1_TARGET, t1_peak(hi, tm, "series")[0] - T1_TARGET
    it = []
    if f_lo < 0 < f_hi:
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            T1 = t1_peak(mid, tm, "series")[0]
            it.append((mid, T1))
            if abs(T1 - T1_TARGET) <= PEAK_TOL_K:
                break
            if T1 < T1_TARGET:
                lo = mid
            else:
                hi = mid
        e_peak = it[-1][0]
        peak = {"E_J": e_peak, "T1max_series_C": it[-1][1], "T1max_parallel_C": t1_peak(e_peak, tm, "parallel")[0],
                "iterations": len(it), "target_C": T1_TARGET, "tolerance_K": PEAK_TOL_K}
    else:
        peak = {"E_J": None, "note": "the target lies outside the bracket of the two energy levels"}
    out = {"measured_trigger_max_range_C": [T1_LO, T1_HI], "measured_trigger_max_median_C": T1_TARGET,
           "levels": L, "durations": IN.durations(), "energies": IN.energies(), "rows": rows,
           "qualifies_at_every_connection": sel, "central_matched_case": {"energy": central_energy[0],
                                                                         "E_J": central_energy[1], "tau_s": tm},
           "peak_matched_exploratory": peak, "computed_utc": RUN._utc()}
    if path:
        json.dump(out, open(path, "w"), indent=1, default=float)
    return out


# ------------------------------------------------------------------------------------------------ the run list
def build_runs(central_energy_J=None, e_peak_J=None):
    """The run list (D55 (1)). With no arguments it reads results/stage6_trigger.json for the central matched
    case's energy and the peak-matched energy."""
    L = levels()
    if central_energy_J is None and e_peak_J is None and os.path.exists(TRIGGER):
        tr = json.load(open(TRIGGER))
        central_energy_J = tr["central_matched_case"]["E_J"]
        e_peak_J = tr["peak_matched_exploratory"]["E_J"]
    runs = []
    tm = L["tau_median_s"]

    def add(set_, kin, conn, h, g, tau, e, refine=1.0, dt_scale=1.0, tag=""):
        kin_s = "mean" if kin == "mean" else f"d{kin:03d}"
        rid = f"{set_}_{kin_s}_{conn}_h{h}_g{g}_tau{tau:.2f}_E{e / 1e3:.2f}" + tag
        runs.append({"id": rid, "set": set_, "kin": kin, "connection": conn, "h": h, "g": g, "tau": float(tau),
                     "E_body_J": float(e), "T_amb_K": float(V.LP.T_AMB), "refine": float(refine),
                     "dt_scale": float(dt_scale)})

    if central_energy_J is not None:
        for conn in V.CONNECTIONS:
            add("v3", "mean", conn, "central", "central", tm, central_energy_J, refine=2.0, tag="_refine2")
            add("v3", "mean", conn, "central", "central", tm, central_energy_J, dt_scale=0.5, tag="_dthalf")
    for set_, e in (("body", L["E_body_J"]), ("total", L["E_total_J"])):
        for tau in L["tau_s"]:
            for conn in V.CONNECTIONS:
                for h, g in CONFIGS:
                    add(set_, "mean", conn, h, g, tau, e)
    for e in L["E_bracket_J"]:
        for conn in V.CONNECTIONS:
            add("bracket", "mean", conn, "central", "central", tm, e)
    if e_peak_J is not None:
        for conn in V.CONNECTIONS:
            for h, g in CONFIGS:
                add("peak", "mean", conn, h, g, tm, e_peak_J)
    if central_energy_J is not None:
        for d in range(1, 201):
            for conn in V.CONNECTIONS:
                add("draws", d, conn, "central", "central", tm, central_energy_J)
    order = {s: i for i, s in enumerate(SETS)}
    runs.sort(key=lambda r: order[r["set"]])           # stable: the order within each set is kept
    return runs


def registered(runs):
    """The registered sets (every set but the exploratory peak-matched one)."""
    return [r for r in runs if r["set"] != "peak"]


def runs_hash(runs):
    return hashlib.sha256(json.dumps(runs, sort_keys=True).encode()).hexdigest()


# ------------------------------------------------------------------------------------------------ one run
def stage6_quantities(rec, series):
    """A1 at 150 C for the five histories, and the 255.7 C crossings of the hottest node and the lumped neighbour
    (each run stops at its own, D35); the mean and the probes cannot exceed the hottest node, so within the resolved
    run they reach 255.7 C no earlier than it, and their values at its end are given."""
    q = {"crossings_150C": CR.a1(rec, series)}
    rr, ll = rec["resolved"], rec["lumped"]
    hs = CR.histories(series)
    last = {c: float(hs[c][1][-1] - CR.K0) for c in ("hot", "mean", "away", "toward")}
    q["reach_255_7C"] = {"hot_t_s": rr.get("t_prop_s"), "lumped_t_s": ll.get("t_prop_s"),
                         "resolved_t_end_s": rr["t_end_s"], "lumped_t_end_s": ll["t_end_s"],
                         "resolved_last_stored_C": last,       # the last stored sample of each resolved history
                         "level_C": V.LEVEL_PROP - CR.K0}
    return q


def run_one(spec, ctx):
    rec, series = RUN.run_one(spec, ctx, keep_series=True)
    rec["stage6"] = stage6_quantities(rec, series)
    return rec, (series if spec["set"] != "draws" else None)


def work(worker, of, budget_min, sets, wall_min=1e9, queue=False, label="unlabelled"):
    """v12_run.work with the Stage 6 list, folders, time limits and outputs; every rule of D43 (3), D47 (3) and
    D55 (4) is kept: a run still going at the wall time is left unrecorded and redone; a run that fails is recorded
    as failed, except for want of memory, when it is retried after a minute, up to 10 times."""
    if not os.path.exists(TRIGGER):
        raise SystemExit("results/stage6_trigger.json is missing: run `stage6_run.py trigger` first")
    os.makedirs(RUNS, exist_ok=True)
    os.makedirs(SERIES, exist_ok=True)
    runs = build_runs()
    ctx = RUN.Context()
    machine = RUN.machine_info(label)
    t0 = time.time()
    done = 0
    if hasattr(signal, "SIGALRM"):
        signal.signal(signal.SIGALRM, RUN._alarm)
    for i, spec in enumerate(runs):
        if spec["set"] not in sets or (not queue and i % of != worker):
            continue
        path = os.path.join(RUNS, spec["id"] + ".json")
        if os.path.exists(path):
            continue
        elapsed = (time.time() - t0) / 60.0
        left = wall_min - elapsed
        if elapsed > budget_min or left < RUN.START_MARGIN_MIN[spec["refine"]] or os.path.exists(STOP_FILE):
            print(f"{RUN._utc()} worker {worker}: stopping after {done} runs (budget, wall time or stop file); "
                  f"next run {spec['id']}", flush=True)
            return
        claim = os.path.join(RUNS, spec["id"] + ".claim")
        if queue and not RUN._claim(claim, worker):
            continue
        limit_s = int(RUN_LIMIT_MIN[spec["refine"]] * 60)
        wall_s = int(left * 60) - RUN.WALL_MARGIN_S
        tries = 0
        while True:
            started = RUN._utc()
            try:
                try:
                    RUN._arm(min(limit_s, wall_s), "wall" if wall_s < limit_s else "limit")
                    rec, series = run_one(spec, ctx)
                except KeyboardInterrupt:              # the timer thread's interrupt, not a user's Ctrl-C
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
                print(f"{RUN._utc()} worker {worker}: {spec['id']} interrupted at the wall time and not recorded; "
                      f"stopping after {done} runs", flush=True)
                return
            except Exception as exc:
                import gc, traceback
                RX.DT_BASE, RX.DT_TARGET, RX.DT_ACCEPT = 0.1, 1.0, 4.0
                if RUN.is_memory_failure(repr(exc)) and tries < RUN.MEM_RETRIES:
                    tries += 1
                    RUN._disarm()
                    gc.collect()
                    print(f"{RUN._utc()} worker {worker}: {spec['id']} short of memory ({repr(exc)[:60]}); "
                          f"retry {tries} in {RUN.MEM_WAIT_S} s", flush=True)
                    time.sleep(RUN.MEM_WAIT_S)
                    continue
                rec, series = dict(spec), None
                rec.update({"failed": True, "error": repr(exc), "traceback": traceback.format_exc()})
            finally:
                RUN._disarm()
            break
        if tries:
            rec["memory_retries"] = tries
        rec["started_utc"], rec["finished_utc"] = started, RUN._utc()
        rec["machine"] = machine
        if series is not None:
            np.savez_compressed(os.path.join(SERIES, spec["id"] + ".npz"), **series)
        tmp = path + f".tmp{os.getpid()}"
        with open(tmp, "w") as fh:
            json.dump(rec, fh, indent=1, default=float)
        os.replace(tmp, path)
        if queue:
            RUN._unclaim(claim)
        done += 1
        if rec.get("failed"):
            print(f"{RUN._utc()} {spec['id']}: FAILED {rec['error']}", flush=True)
            continue
        rr, ll = rec["resolved"], rec["lumped"]
        print(f"{RUN._utc()} {spec['id']}: cell 1 {rec['T1max_C']:.1f} C; resolved "
              f"{'%.1f s' % rr['t_prop_s'] if rr['propagated'] else 'none'} (peak {rr['peak_hottest_C']:.1f} C), "
              f"lumped {'%.1f s' % ll['t_prop_s'] if ll['propagated'] else 'none'} (peak {ll['peak_C']:.1f} C), "
              f"residual {rr['energy_residual_rel']:.1e}, {rec['wall_s']:.0f} s", flush=True)
    print(f"{RUN._utc()} worker {worker}: all assigned runs recorded ({done} this pass)", flush=True)


def status():
    runs = build_runs()
    have = {f[:-5] for f in os.listdir(RUNS) if f.endswith(".json")} if os.path.isdir(RUNS) else set()
    by = {}
    for s in runs:
        b = by.setdefault(s["set"], [0, 0])
        b[0] += 1
        b[1] += s["id"] in have
    print(json.dumps({k: {"total": v[0], "done": v[1]} for k, v in by.items()}))


def reset_claims():
    n = 0
    for f in os.listdir(RUNS) if os.path.isdir(RUNS) else []:
        if f.endswith(".claim"):
            RUN._unclaim(os.path.join(RUNS, f))
            n += 1
    print(f"{n} claims removed")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["trigger", "list", "work", "status", "reset-claims"])
    ap.add_argument("--worker", type=int, default=0)
    ap.add_argument("--of", type=int, default=1)
    ap.add_argument("--budget-min", type=float, default=1e9)
    ap.add_argument("--wall-min", type=float, default=1e9)
    ap.add_argument("--sets", nargs="*", default=list(SETS))
    ap.add_argument("--queue", action="store_true")
    ap.add_argument("--label", default="unlabelled")
    a = ap.parse_args()
    if a.cmd == "trigger":
        if os.path.exists(TRIGGER):
            raise SystemExit("results/stage6_trigger.json exists; the selection is made once")
        out = trigger()
        print(json.dumps({k: out[k] for k in ("qualifies_at_every_connection", "central_matched_case",
                                              "peak_matched_exploratory")}, indent=1, default=float))
        runs = build_runs()
        print(len(runs), "runs; sha256", runs_hash(runs), "; registered sets", len(registered(runs)), "runs, sha256",
              runs_hash(registered(runs)))
    elif a.cmd == "list":
        if os.path.exists(TRIGGER):
            runs = build_runs()
            print(len(runs), "runs; sha256 of the run list", runs_hash(runs))
            print({s: sum(r["set"] == s for r in runs) for s in SETS})
        else:
            L = levels()
            for name, e in (("body", L["E_body_J"]), ("total", L["E_total_J"])):
                rs = build_runs(central_energy_J=e, e_peak_J=None)
                print(f"central matched case at the {name} energy: {len(rs)} registered runs; sha256 {runs_hash(rs)}")
                print({s: sum(r["set"] == s for r in rs) for s in SETS})
    elif a.cmd == "work":
        work(a.worker, a.of, a.budget_min, set(a.sets), a.wall_min, queue=a.queue, label=a.label)
    elif a.cmd == "reset-claims":
        reset_claims()
    else:
        status()
