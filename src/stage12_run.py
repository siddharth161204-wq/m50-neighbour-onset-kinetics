#!/usr/bin/env python3
"""Stage 12 runs (predictions_stage12.md; DECISIONS.md D122 to D124).

Every run is a Stage 11 run (`stage11_run.run_one`: Stage 10's run, Stage 9's inputs, Stage 10's five probes) at the
posterior-mean kinetics, the central properties and the central tabs. What Stage 12 changes, by the brief:
  - Part A: the trigger's body energy capped at the Databank's largest, 33,222.9 J (D122 (1)), with no delivery and the
    release unchanged (21.39 s), at the central and the high contact, to 900 s with the stop lifted. With the cap a run
    depends on the test only through its connection, so the eight tests of D122 (3) fall on four runs (D122 (6)).
  - Part B: the thresholds f*(C1) and f*(C2) of the four Stage 11 tests (B1) and f_t(C2) of the nine propagated tests
    (B2) as fractions of the fixed ejected energy, 76,741.25 J (D122 (2)). A run depends on f and E_e only through the
    delivered energy (D122 (7)); a run is therefore specified as in Stages 9 to 11, by its fraction of r E_b, at the
    energy the search asks for, and its fraction of the fixed energy is that energy over 76,741.25 J. B1 starts from
    Stage 8's bracket and B2 from Stage 9's state, and each halves its bracket until it is at most 0.02 (B1) or 0.005
    (B2) of the fixed energy wide, or (B2) a run comes within 10 s of the measured time (D123 (2), (3)).

Records go to results/stage12_runs/<id>.json and series to results/stage12_series/<id>.npz.

Usage:
  python3 stage12_run.py list | states | status | reset-claims
  python3 stage12_run.py work --worker K --label NAME
"""
import os as _os
for _k in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "NUMBA_NUM_THREADS"):
    _os.environ.setdefault(_k, "1")      # D43 (4): one thread per library; set before numpy and numba load
import argparse, glob, hashlib, json, os, signal, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v12_run as RUN                    # noqa: E402  (unchanged)
import reactive as RX                    # noqa: E402  (unchanged)
import stage9_run as R9                  # noqa: E402  (unchanged)
import stage9_search as S9               # noqa: E402  (unchanged)
import stage8_search as SR8              # noqa: E402  (unchanged)
import stage11_run as S11                # noqa: E402  (unchanged)
import stage12_inputs as IN              # noqa: E402

LP = S11.LP
RES = os.path.join(HERE, "..", "results")
TAG = os.environ.get("STAGE12_RUNS_TAG", "")
RUNS = os.path.join(RES, "stage12_runs" + TAG)
SERIES = os.path.join(RES, "stage12_series" + TAG)
STOP_FILE = os.path.join(RES, "stage12_STOP")
RUN_LIMIT_MIN = 1440.0
key = SR8.key


# ------------------------------------------------------------------------------------------------ the specifications
def spec_a(connection, h):
    """Part A: one point, the capped trigger with a connection at a contact, both neighbours, to 900 s, the stop lifted.
    The specification is Stage 11's for the first test of the point, with the body energy capped; `tests` names every
    test the point stands for."""
    tests = IN.a_points()[(connection, h)]
    sp = S11.spec("A", tests[0], 0.0, "mean", "central", h, "both", False)
    r = float(R9.ratios()["central"])
    sp.update({"stage": 12, "test": f"capped_{connection}", "tests": list(tests), "E_body_J": IN.E_CAP_J,
               "E_body_fitted_J": None, "E_e_J": r * IN.E_CAP_J, "E_delivered_J": 0.0, "f": 0.0})
    sp["id"] = f"s12_A_cap_{connection}_h{h}_both_ns"
    return sp


def spec_b(part, test, f_old, models, stop):
    """Part B: Stage 11's specification at the posterior mean, the central properties and contact, at the fraction of
    r E_b that gives the energy the search asks for; f_fixed is that energy's fraction of the fixed ejected energy."""
    sp = S11.spec(part, test, f_old, "mean", "central", "central", models, stop)
    sp.update({"stage": 12, "E_fix_J": IN.E_FIX_J, "f_fixed": sp["E_delivered_J"] / IN.E_FIX_J})
    assert sp["id"].startswith("s11_")
    sp["id"] = "s12_" + part + "_" + sp["id"][4:]
    return sp


def part_a_specs():
    return [spec_a(c, h) for (c, h) in IN.a_points()]


# ------------------------------------------------------------------------------------------------ the records' points
def load_records(runs_dir=None):
    d = runs_dir or RUNS
    out = {}
    for p in glob.glob(os.path.join(d, "s12_*.json")):
        r = json.load(open(p))
        out[r["id"]] = r
    return out


def points(recs):
    """{(test, f): {"C1": crossing or None, "C2": ...}} from Part B's records that did not fail."""
    out = {}
    for r in recs.values():
        if r.get("failed") or r["id"].startswith("s12_A_"):
            continue
        e = out.setdefault((r["test"], key(r["f"])), {"ids": []})
        e["ids"].append(r["id"])
        if r.get("resolved"):
            rr = r["resolved"]
            e["C1"] = rr["t_prop_s"] if rr["propagated"] else None
        if r.get("lumped"):
            ll = r["lumped"]
            e["C2"] = ll["t_prop_s"] if ll["propagated"] else None
    return out


# ------------------------------------------------------------------------------------------------ B1 and B2
def b1_state(test, crit, pts):
    """f* of a criterion as a fraction of the fixed energy (D123 (2)): from Stage 8's bracket, halved until its width
    times E_e / E_fix is at most 0.02. Brackets and runs are in fractions of r E_b, the energies the records hold."""
    s8 = R9.fstar8()[test][crit]
    ee = IN.e_e(test)
    if s8["status"] == "zero":
        return {"status": "zero", "lo": 0.0, "hi": 0.0, "runs": [], "e_e": ee}
    lo, hi = key(s8["lo"]), key(s8["hi"])
    runs = []
    while True:
        if (hi - lo) * ee / IN.E_FIX_J <= IN.WIDTH_B1 + 1e-12:
            return {"status": "bracket", "lo": lo, "hi": hi, "runs": runs, "e_e": ee}
        m = key(0.5 * (lo + hi))
        e = pts.get((test, m), {})
        if crit not in e:
            return {"status": "searching", "next": m, "lo": lo, "hi": hi, "runs": runs, "e_e": ee}
        runs.append(m)
        if e[crit] is not None:
            hi = m
        else:
            lo = m


def b2_state(test, pts):
    """f_t(C2) as a fraction of the fixed energy (D123 (3)): from Stage 9's state; a matched search stays matched; a
    bracketed or threshold one is halved, as Stage 9's bisection halves it, until its width times E_e / E_fix is at most
    0.005 or a run comes within 10 s of the measured time."""
    s9 = IN.stage9_a2(test)
    ee = IN.e_e(test)
    t_m = R9.t_meas(test)
    base = {"test": test, "t_m": t_m, "e_e": ee, "stage9_status": s9["status"], "stage9_lo": s9.get("lo"),
            "stage9_hi": s9.get("hi")}
    if s9["status"] == "matched":
        return dict(base, status="matched", f_t=key(s9["f_t"]), lo=s9["lo"], hi=s9["hi"], t_run=s9["t_run"], runs=[])
    if s9["status"] not in ("bracketed", "threshold"):
        return dict(base, status="not searched", runs=[])
    lo, hi, t_lo, t_hi = key(s9["lo"]), key(s9["hi"]), s9.get("t_lo"), s9.get("t_hi")
    runs = []
    while True:
        if (hi - lo) * ee / IN.E_FIX_J <= IN.WIDTH_B2 + 1e-12:
            st = "bracketed" if t_lo is not None else "threshold"
            out = dict(base, status=st, lo=lo, hi=hi, t_lo=t_lo, t_hi=t_hi, runs=runs)
            if st == "bracketed":
                out["f_t"] = S9.interp_t(lo, t_lo, hi, t_hi, t_m)
            return out
        m = key(0.5 * (lo + hi))
        e = pts.get((test, m), {})
        if "C2" not in e:
            return dict(base, status="searching", next=m, lo=lo, hi=hi, t_lo=t_lo, t_hi=t_hi, runs=runs)
        runs.append(m)
        t = e["C2"]
        if t is not None and abs(t - t_m) <= IN.T_TOL_S:
            return dict(base, status="matched", f_t=m, lo=lo, hi=hi, t_run=t, runs=runs)
        if t is not None and t < t_m:
            hi, t_hi = m, t
        else:
            lo, t_lo = m, t


def states(recs):
    pts = points(recs)
    b1 = {f"B1_{c}_{t}": b1_state(t, c, pts) for t in IN.B1_TESTS for c in ("C1", "C2")}
    b2 = {f"B2_{t}": b2_state(t, pts) for t in IN.b2_tests()}
    return b1, b2


# ------------------------------------------------------------------------------------------------ the list
def build_runs(recs):
    """Part A's four runs, then the searches' next runs: C1's hold both neighbours and stop at their crossings, C2's
    hold the lumped neighbour alone (as in Stages 9 and 11)."""
    runs = part_a_specs()
    b1, b2 = states(recs)
    for name, st in b1.items():
        if st["status"] == "searching":
            crit, test = name.split("_")[1], name.split("_", 2)[2]
            runs.append(spec_b("B1", test, st["next"], "both" if crit == "C1" else "lumped", True))
    for name, st in b2.items():
        if st["status"] == "searching":
            runs.append(spec_b("B2", st["test"], st["next"], "lumped", True))
    seen, out = set(), []
    for r in runs:
        if r["id"] not in seen:
            seen.add(r["id"])
            out.append(r)
    return out


def runs_hash(runs):
    keys = sorted(json.dumps({k: v for k, v in r.items() if k not in ("kind", "chain")}, sort_keys=True,
                             default=float) for r in runs)
    return hashlib.sha256("\n".join(keys).encode()).hexdigest()


# ------------------------------------------------------------------------------------------------ the work loop
def _paths(sp):
    return os.path.join(RUNS, sp["id"] + ".json"), os.path.join(SERIES, sp["id"] + ".npz")


def work(worker, label="unlabelled", wait_s=10.0, once=False, run_fn=None):
    """Stage 11's loop (claims; a failed run recorded as failed) on Stage 12's list, which grows as the searches advance.
    `run_fn` replaces the model in the tests."""
    for d in (RUNS, SERIES):
        os.makedirs(d, exist_ok=True)
    ctx = S11.Context()
    machine = RUN.machine_info(label)
    run_fn = run_fn or S11.run_one
    done = 0
    if hasattr(signal, "SIGALRM"):
        signal.signal(signal.SIGALRM, RUN._alarm)
    while True:
        recs = load_records()
        pending = [r for r in build_runs(recs) if r["id"] not in recs]
        if not pending:
            if [f for f in os.listdir(RUNS) if f.endswith(".claim")]:
                time.sleep(wait_s)
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
                    rec, series = run_fn(sp, ctx)
                except KeyboardInterrupt:
                    if not RUN._DEADLINE["fired"]:
                        raise
                    raise RUN.RunTimeLimit("the run exceeded its time limit") from None
            except Exception as exc:
                import traceback
                RX.DT_BASE, RX.DT_TARGET, RX.DT_ACCEPT = 0.1, 1.0, 4.0
                LP.C_CELL = S11.CENTRAL["C_cell"]
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
            print(f"{RUN._utc()} {S11.summary(rec)}", flush=True)
            break
        if once:
            return done
        if not started:
            time.sleep(wait_s)


def status():
    recs = load_records()
    runs = build_runs(recs)
    b1, b2 = states(recs)
    print(json.dumps({"records": len(recs), "failed": sum(1 for r in recs.values() if r.get("failed")),
                      "pending_now": [r["id"] for r in runs if r["id"] not in recs],
                      "b1": {k: (s["status"], s.get("lo"), s.get("hi"), s.get("next")) for k, s in b1.items()},
                      "b2": {k: (s["status"], s.get("lo"), s.get("hi"), s.get("next"), s.get("f_t")) for k, s in b2.items()},
                      "claims": [f for f in os.listdir(RUNS) if f.endswith(".claim")] if os.path.isdir(RUNS) else []},
                     indent=1, default=float))


def reset_claims():
    n = 0
    for f in os.listdir(RUNS) if os.path.isdir(RUNS) else []:
        if f.endswith(".claim"):
            RUN._unclaim(os.path.join(RUNS, f))
            n += 1
    print(f"{n} claims removed")


if __name__ == "__main__":
    IN.check()
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["list", "states", "work", "status", "reset-claims"])
    ap.add_argument("--worker", type=int, default=0)
    ap.add_argument("--label", default="unlabelled")
    a = ap.parse_args()
    if a.cmd == "list":
        runs = build_runs(load_records())
        print(len(runs), "runs listed now; sha256", runs_hash(runs))
        for r in runs:
            print(r["id"])
    elif a.cmd == "states":
        b1, b2 = states(load_records())
        for k, s in list(b1.items()) + list(b2.items()):
            print(k, s["status"], s.get("lo"), s.get("hi"), s.get("next"), s.get("f_t"))
    elif a.cmd == "work":
        work(a.worker, label=a.label)
    elif a.cmd == "reset-claims":
        reset_claims()
    else:
        status()
