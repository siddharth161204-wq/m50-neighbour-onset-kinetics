"""Step 16 (Brief 31, DECISIONS.md D190): the resolved needs at the measured times in three dimensions, a second
weak-trigger threshold in three dimensions, and one refinement check at a need. Nothing in the model changes: every
run is Stage 15's (`stage15_run.run_one`, unchanged), with Stage 15's configuration: one test of Fransson et al. with
its fitted trigger, the central contact and tabs, 25 C, the posterior-mean kinetics, the fresh SEI, the nominal roll
properties, the base mesh and step limits unless stated, both neighbours, a delivered energy through the facing half
from t = 0, and the resolved neighbour's run stopped at C8 (its mean at 255.68 C) or at 900 s.

The searches (each next run a function of the records already made):

  N   The need, for each of the eight tests that propagated after strong triggers (STRONG8), with the 21.39 s
      triangular pulse. A run is "early" if its C8 comes no later than t_m + 10 s (t_m the test's measured time) and
      "late" if its C8 comes later than that or not at all within 900 s. The need is the least energy whose run is
      early; its bracket is (the highest late energy below every early one, the lowest early energy]. Every
      three-dimensional run already made in the same configuration (the archived runs Stage 15 set the reactive
      cross-section against, and Stage 15's B1 runs) counts. The next run: with no early run, the lowest point above
      every late run of the grid E_x + k g (k = 0, 1, 2, ...); with no late run, the highest point of the grid below
      every early run (k = -1, -2, ...); with both, the midpoint of the bracket; until the bracket is at most
      FINAL_FRAC E_e wide. E_x is the reactive cross-section's need for the same test and delivery (Table S7), g is
      GRID_FRAC E_e, and at most MAX_GRID_STEPS grid steps are taken either way.
  T   PT-Exp1's threshold with the pulse, by Stage 15's B1 rule (as for ST-Exp3): runs at the cross-section's
      E*(C8) less and plus 5 %, then steps of 10 % of it on the side needed, until a run with C8 lies one step above
      one without; the bracket is (highest without C8, lowest with C8].
  V   The refinement check: once no N search is running, the need with the latest measured time among those whose
      bracket's lower end also runs away within 900 s (a need above its threshold and the nearest to it; else the
      latest among all the needs found) has both ends of its bracket run again with the mesh refined by 1.5 and every
      step limit halved together. Where an end changes class, one further refined run one bracket width beyond it on
      that side, at most two in all.
  X   Then, as computing allows: N's rule for constant power over 240 s, then 120 s, then 360 s, test by test in
      STRONG8's order, until every such search is done or the X runs have taken X_CAP_WORKER_H worker-hours; a search
      unfinished at the cap is reported as unfinished. For these shapes the need is counted as delivered by its
      runaway, as Table S7 counts it: the energy times the share of the delivery made by t_m + 10 s.

  A run that fails is made again at once; one that fails twice stops its search, which is reported as stopped.

Records go to results/stage16_runs/<id>.json and series to results/stage16_series/<id>.npz; V1's repeat of an
archived Stage 15 run to results/stage16_repeats/.

Usage:
  python3 stage16_run.py repeat --worker K       # V1, before the predictions: one Stage 15 run made again
  python3 stage16_run.py list | status
  python3 stage16_run.py work --worker K [--max-minutes M] [--v-window W]
"""
import os as _os
for _k in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "NUMBA_NUM_THREADS"):
    _os.environ.setdefault(_k, "1")

import argparse
import csv
import hashlib
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage15_inputs as IN              # noqa: E402  (unchanged)
import stage15_run as R15                # noqa: E402  (unchanged)
import stage15_partb as PB               # noqa: E402  (unchanged)
import v12_run as RUN                    # noqa: E402  (unchanged)
import rebuild_brackets as RBK           # noqa: E402  (unchanged)

RES = IN.RES
RUNS = os.path.join(RES, "stage16_runs")
SERIES = os.path.join(RES, "stage16_series")
REPEATS = os.path.join(RES, "stage16_repeats")
STOP_FILE = os.path.join(RES, "stage16_STOP")
XS_OUT = os.path.join(RES, "stage15_cross_section.json")
TABLE15 = os.path.join(RES, "stage15_table.csv")

STRONG8 = ("M50_PT_Exp4", "M50_PP_Exp1", "M50_PP_Exp2", "M50_PP_Exp4", "M50_ST_Exp4", "M50_SP_Exp1", "M50_SP_Exp2",
           "M50_SP_Exp3")
WEAK2 = "M50_PT_Exp1"
WINDOW_S = 10.0                          # a need's run reaches C8 within 10 s of the measured time, or before it
GRID_FRAC = 0.0025                       # N's grid step g, of the test's ejected energy E_e
FINAL_FRAC = 0.00125                     # N's final bracket width, of E_e
MAX_GRID_STEPS = 8                       # at most 8 grid steps either way from E_x
T_FIRST = (-1, +1)                       # T: the cross-section's E*(C8) less and plus 5 %
T_STEP_RANGE = (-19, 39)
V_REFINE, V_DT = 1.5, 0.5                # V: the mesh refined by 1.5 with every step limit halved
V_MAX_EXTRA = 2
X_SHAPES = (240.0, 120.0, 360.0)         # X: constant power, in this order
X_CAP_WORKER_H = 6.0
DELIVERY = {"tri": "21.39 s pulse", 120.0: "120 s constant power", 240.0: "240 s constant power",
            360.0: "360 s constant power"}


# ------------------------------------------------------------------------------------------------ inputs
def _table15():
    with open(TABLE15) as fh:
        return list(csv.DictReader(fh))


def t_measured(test):
    for r in _table15():
        if r["test"] == test:
            return float(r["t_measured_s"])
    raise KeyError(test)


def xs_need(test, shape, tau):
    """E_x: the reactive cross-section's need (the nominal energy of its run, results/stage15_table.csv C8_xs_E_J)
    for the test and delivery, and its status; None where the cross-section found none."""
    lab = DELIVERY["tri"] if shape == "tri" else DELIVERY[float(tau)]
    for r in _table15():
        if r["test"] == test and r["delivery"] == lab:
            return (float(r["C8_xs_E_J"]), r["C8_xs_status"]) if r["C8_xs_E_J"] else (None, r["C8_xs_status"])
    raise KeyError((test, lab))


def xs_threshold(test):
    """The cross-section's E*(C8) with the pulse (results/stage15_cross_section.json A2), T's anchor as B1's."""
    return PB.a2_value(test)


def lumped_threshold(test):
    """The lumped threshold with the pulse at the central contact, the narrowest bracket the archive holds (J)."""
    with open(os.path.join(RES, "stage14_needs.csv")) as fh:
        row = next(r for r in csv.DictReader(fh) if r["test"] == test)
    return RBK.brackets(row)[1]


def tau_of(shape, tau):
    return IN.TAU_TRIGGER if shape == "tri" else float(tau)


def share_by(shape, tau, t):
    """The share of a delivery made by time t (the triangular pulse rises to its peak at half its length)."""
    tau = tau_of(shape, tau)
    if t is None:
        return 1.0
    x = max(0.0, min(1.0, t / tau))
    if shape == "tri":
        return 2.0 * x * x if x <= 0.5 else 1.0 - 2.0 * (1.0 - x) ** 2
    return x


# ------------------------------------------------------------------------------------------------ specifications
def spec16(name, test, deliveries, kind, refine=1.0, dt_scale=1.0, search=None):
    s = R15.spec(name, test, deliveries, kind, refine=refine, dt_scale=dt_scale, search=search)
    s["id"] = "s16_" + name
    s["stage"] = 16
    return s


def _dl(test, shape, tau, E):
    f = E / IN.e_e(test)
    return [{"shape": shape, "f": f, "tau_s": tau_of(shape, tau), "t0_s": 0.0}]


def n_spec(test, shape, tau, E, kind="N"):
    f = IN.key(E / IN.e_e(test), 9)
    lab = "tri21" if shape == "tri" else "con%.0f" % tau
    return spec16(f"{kind}_{test[4:]}_{lab}_f{f:.9f}", test, _dl(test, shape, tau, E), kind,
                  search=f"{kind}_{test}_{lab}")


def t_spec(step):
    E = xs_threshold(WEAK2) * (1.0 + 0.05 * step)
    return spec16(f"T_{WEAK2[4:]}_s{step:+d}", WEAK2, _dl(WEAK2, "tri", None, E), "T", search=f"T_{WEAK2}")


def v_spec(base):
    s = dict(base)
    s.update({"id": base["id"] + "_r1.5dt0.5", "kind": "V", "refine": V_REFINE, "dt_scale": V_DT,
              "search": "V"})
    return s


# ------------------------------------------------------------------------------------------------ the records
def load(recs_dir=RUNS):
    out = {}
    if not os.path.isdir(recs_dir):
        return out
    for fn in os.listdir(recs_dir):
        if fn.endswith(".json"):
            try:
                r = json.load(open(os.path.join(recs_dir, fn)))
            except Exception:
                continue
            out[r["id"]] = r
    return out


def _same_config(r):
    """A three-dimensional run of N's configuration: one delivery, the central contact and tabs, the posterior mean,
    the fresh SEI, no shift, the base mesh and step limits."""
    return (not r.get("failed") and r.get("h") == "central" and r.get("g") == "central" and r.get("kin") == "mean"
            and r.get("sei0") is None and not r.get("shift_K") and r.get("refine", 1.0) == 1.0
            and r.get("dt_scale", 1.0) == 1.0 and len(r.get("deliveries", [])) == 1)


def _matches(shape, tau, d_shape, d_tau):
    return d_shape == shape and abs(d_tau - tau_of(shape, tau)) < 1e-6


def existing_runs(test, shape, tau, recs16, recs15=None, a1=None):
    """[(E_J, t_C8_s or None, t_end_s, source, id)]: every three-dimensional run of the configuration made so far."""
    out = []
    if a1 is None:
        a1 = json.load(open(XS_OUT))["A1_rows"]
    for a in a1:
        if a["test"] == test and _matches(shape, tau, a["shape"], a["tau_d_s"]):
            out.append((float(a["E_J"]), a["t_C8_3d_s"], float(a["t_end_s"]), "archive", a["id"]))
    if recs15 is None:
        recs15 = PB.load()
    for src, recs in (("stage15", recs15), ("stage16", recs16)):
        for r in recs.values():
            if r.get("test") == test and _same_config(r):
                d = r["deliveries"][0]
                if _matches(shape, tau, d["shape"], d["tau_s"]):
                    p = r["resolved"]
                    out.append((float(r["E_delivered_J"]), p["t_C8_s"] if p["C8"] else None, float(p["t_end_s"]),
                                src, r["id"]))
    return out


def classify(t_c8, t_end, t_m):
    lim = t_m + WINDOW_S
    if t_c8 is not None:
        return "early" if t_c8 <= lim + 1e-9 else "late"
    return "late" if t_end >= min(IN.T_END, lim) - 1e-9 else None


def failed_in(recs16, search):
    return any(r.get("failed") and r.get("search") == search for r in recs16.values())


def need_state(test, shape, tau, recs16, kind="N", recs15=None, a1=None):
    """(status, next spec or None, result). status: running, done, stopped, not monotone, out of range, no anchor."""
    lab = "tri21" if shape == "tri" else "con%.0f" % tau
    if failed_in(recs16, f"{kind}_{test}_{lab}"):
        return "stopped", None, None
    E_x, st = xs_need(test, shape, tau)
    if E_x is None:
        return "no anchor", None, None
    t_m = t_measured(test)
    E_e = IN.e_e(test)
    g = GRID_FRAC * E_e
    tol = 1e-6 * E_e                     # well above the energies' rounding (a fraction kept to 9 decimals), well below g
    runs = []
    for E, t, t_end, src, rid in existing_runs(test, shape, tau, recs16, recs15, a1):
        c = classify(t, t_end, t_m)
        if c is not None:
            runs.append((E, c, t, src, rid))
    early = sorted(x for x in runs if x[1] == "early")
    late = sorted(x for x in runs if x[1] == "late")
    if early and late and late[-1][0] > early[0][0] + tol:
        return "not monotone", None, {"runs": runs}
    lo = late[-1] if late else None
    hi = early[0] if early else None
    if lo is not None and hi is not None and hi[0] - lo[0] <= FINAL_FRAC * E_e + tol:
        return "done", None, {"lo": lo, "hi": hi, "E_x": E_x, "xs_status": st, "t_m": t_m, "runs": runs}
    if hi is None:
        k = 0
        while lo is not None and E_x + k * g <= lo[0] + tol:
            k += 1
        if k > MAX_GRID_STEPS:
            return "out of range", None, {"runs": runs}
        E = E_x + k * g
    elif lo is None:
        k = -1
        while E_x + k * g >= hi[0] - tol:
            k -= 1
        if k < -MAX_GRID_STEPS or E_x + k * g <= 0.0:
            return "out of range", None, {"runs": runs}
        E = E_x + k * g
    else:
        E = 0.5 * (lo[0] + hi[0])
    return "running", n_spec(test, shape, tau, E, kind), None


def t_state(recs16):
    """PT-Exp1's threshold by B1's rule: (status, pending specs, bracket)."""
    if failed_in(recs16, f"T_{WEAK2}"):
        return "stopped", [], None
    have = {}
    for step in range(T_STEP_RANGE[0], T_STEP_RANGE[1] + 1, 2):
        sp = t_spec(step)
        if sp["id"] in recs16:
            have[step] = recs16[sp["id"]]
    need = [s for s in T_FIRST if s not in have]
    if need:
        return "running", [t_spec(s) for s in need], None
    yes = sorted(s for s, r in have.items() if r["resolved"]["C8"])
    no = sorted(s for s, r in have.items() if not r["resolved"]["C8"])
    if yes and no and max(no) < min(yes) and min(yes) - max(no) == 2:
        lo, hi = max(no), min(yes)
        return "done", [], {"lo_step": lo, "hi_step": hi, "lo_id": have[lo]["id"], "hi_id": have[hi]["id"],
                            "lo_J": have[lo]["E_delivered_J"], "hi_J": have[hi]["E_delivered_J"],
                            "t_C8_hi_s": have[hi]["resolved"]["t_C8_s"]}
    if yes and no and max(no) > min(yes):
        return "not monotone", [], None
    nxt = (min(yes) - 2) if not no else (max(no) + 2)
    if nxt < T_STEP_RANGE[0] or nxt > T_STEP_RANGE[1]:
        return "out of range", [], None
    return "running", [t_spec(nxt)], None


def n_all(recs16, recs15=None, a1=None):
    return {t: need_state(t, "tri", None, recs16, "N", recs15, a1) for t in STRONG8}


def v_choice(nres):
    """The test V refines, once no N search is running: among the needs found whose bracket's lower end also runs away
    within 900 s (a need above its threshold), the one with the latest measured time, the nearest above its threshold,
    where the runaway time is the most sensitive to the model's details; else the latest among all the needs found.
    Ties: STRONG8's order. None while an N search runs or where no need was found."""
    if any(st == "running" for st, _, _ in nres.values()):
        return None
    done = [(t, r) for t, (st, _, r) in nres.items() if st == "done"]
    if not done:
        return None
    both = [(t, r) for t, r in done if r["lo"][2] is not None]
    pool = both if both else done
    return max(pool, key=lambda x: (x[1]["t_m"], -STRONG8.index(x[0])))[0]


def v_state(recs16, nres):
    """(status, pending specs, result)."""
    t = v_choice(nres)
    if t is None:
        return "waiting", [], None
    res = nres[t][2]
    t_m = res["t_m"]
    base = {}
    for side in ("lo", "hi"):
        E = res[side][0]
        base[side] = n_spec(t, "tri", None, E, "N")
    pend, out = [], {"test": t, "t_m": t_m, "base": {s: res[s] for s in ("lo", "hi")}}
    refined = {}
    for side in ("lo", "hi"):
        sp = v_spec(base[side])
        if sp["id"] in recs16:
            refined[side] = recs16[sp["id"]]
        else:
            pend.append(sp)
    if pend:
        return "running", pend, out
    if any(r.get("failed") for r in refined.values()):
        return "stopped", [], out

    def cl(r):
        p = r["resolved"]
        return classify(p["t_C8_s"] if p["C8"] else None, p["t_end_s"], t_m)

    out["refined"] = {s: {"id": r["id"], "E_J": r["E_delivered_J"], "C8": r["resolved"]["C8"],
                          "t_C8_s": r["resolved"]["t_C8_s"], "class": cl(r)} for s, r in refined.items()}
    width = res["hi"][0] - res["lo"][0]
    extra = []
    if out["refined"]["lo"]["class"] == "early":
        extra.append(("lo", res["lo"][0] - width))
    if out["refined"]["hi"]["class"] == "late":
        extra.append(("hi", res["hi"][0] + width))
    for side, E in extra[:V_MAX_EXTRA]:
        sp = v_spec(n_spec(t, "tri", None, E, "N"))
        if sp["id"] in recs16:
            r = recs16[sp["id"]]
            out.setdefault("extra", {})[side] = {"id": r["id"], "E_J": r["E_delivered_J"], "C8": r["resolved"]["C8"],
                                                 "t_C8_s": r["resolved"]["t_C8_s"], "class": cl(r)}
        else:
            pend.append(sp)
    if pend:
        return "running", pend, out
    return "done", [], out


def x_worker_hours(recs16):
    return sum(r.get("wall_s", 0.0) for r in recs16.values() if r.get("kind") == "X") / 3600.0


def x_states(recs16, recs15=None, a1=None):
    out = []
    for tau in X_SHAPES:
        for t in STRONG8:
            out.append(((t, tau), need_state(t, "con", tau, recs16, "X", recs15, a1)))
    return out


def pending(recs16, recs15=None, a1=None):
    """The runs due now, in the order the workers take them: T's, then N's (one per unfinished search), then V's
    once every N search is done, then X's while under the cap."""
    out = []
    st, p, _ = t_state(recs16)
    out += p
    nres = n_all(recs16, recs15, a1)
    for t in STRONG8:
        st, sp, _ = nres[t]
        if st == "running":
            out.append(sp)
    st, p, _ = v_state(recs16, nres)
    out += p
    if all(nres[t][0] != "running" for t in STRONG8) and x_worker_hours(recs16) < X_CAP_WORKER_H:
        for key, (st, sp, _) in x_states(recs16, recs15, a1):
            if st == "running":
                out.append(sp)
    return out


def registered_list():
    """The first run of every search, with the rules' parameters, as hashed before any Step 16 run."""
    recs15 = PB.load()
    a1 = json.load(open(XS_OUT))["A1_rows"]
    first = [t_spec(s) for s in T_FIRST]
    for t in STRONG8:
        st, sp, _ = need_state(t, "tri", None, {}, "N", recs15, a1)
        first.append(sp)
    for tau in X_SHAPES:
        for t in STRONG8:
            st, sp, _ = need_state(t, "con", tau, {}, "X", recs15, a1)
            if sp is not None:
                first.append(sp)
    rules = {"N": {"early": "C8 no later than t_m + 10 s", "late": "C8 later, or none within 900 s",
                   "grid": "E_x + k g, g = %.4f E_e, |k| <= %d" % (GRID_FRAC, MAX_GRID_STEPS),
                   "bisect_until": "%.5f E_e" % FINAL_FRAC, "E_x": "results/stage15_table.csv C8_xs_E_J",
                   "counts": "archived A1 runs and Stage 15 runs of the same configuration"},
             "T": {"first": [-0.05, 0.05], "step": 0.10, "of": "A2's E*(C8)", "test": WEAK2},
             "V": {"refine": V_REFINE, "dt_scale": V_DT,
                   "choice": "once no N search runs: the latest t_m among needs whose lower end has C8, else among all",
                   "extra": V_MAX_EXTRA},
             "X": {"shapes_s": list(X_SHAPES), "cap_worker_h": X_CAP_WORKER_H},
             "stop": "C8 (mean 255.68 C) or 900 s", "lumped": "to 900 s, no stop",
             "failure": "a failed run is made again at once; a second failure stops its search"}
    keep = ("id", "test", "deliveries", "kin", "sei0", "shift_K", "h", "refine", "dt_scale", "t_end_s",
            "stop_mean", "max_sub")
    return {"first": [{k: s[k] for k in keep} for s in first], "rules": rules}


def list_hash():
    text = json.dumps(registered_list(), sort_keys=True, default=float)
    return hashlib.sha256(text.encode()).hexdigest(), text


# ------------------------------------------------------------------------------------------------ running
def _write(path_dir, rec, series):
    os.makedirs(path_dir, exist_ok=True)
    os.makedirs(SERIES, exist_ok=True)
    if series is not None:
        np.savez_compressed(os.path.join(SERIES, rec["id"] + ".npz"), **series)
    path = os.path.join(path_dir, rec["id"] + ".json")
    tmp = path + f".tmp{os.getpid()}"
    with open(tmp, "w") as fh:
        json.dump(rec, fh, indent=1, default=float)
    os.replace(tmp, path)


def work_one(sp, out_dir, worker, ctx, machine):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, sp["id"] + ".json")
    claim = path[:-5] + ".claim"
    if os.path.exists(path) or not RUN._claim(claim, worker):
        return False
    st = RUN._utc()
    rec = series = None
    errors = []
    for attempt in (1, 2):
        try:
            rec, series = R15.run_one(sp, ctx)
            break
        except Exception as exc:
            import traceback
            R15.RX.DT_BASE, R15.RX.DT_TARGET, R15.RX.DT_ACCEPT = 0.1, 1.0, 4.0
            errors.append({"attempt": attempt, "error": repr(exc), "traceback": traceback.format_exc()})
            print(f"{RUN._utc()} {sp['id']}: attempt {attempt} failed: {exc!r}", flush=True)
    if rec is None:
        rec, series = dict(sp), None
        rec.update({"failed": True, "error": errors[-1]["error"], "attempts": errors})
    elif errors:
        rec["failed_attempts"] = errors
    rec.update({"started_utc": st, "finished_utc": RUN._utc(), "machine": machine, "worker": worker})
    _write(out_dir, rec, series)
    RUN._unclaim(claim)
    print(f"{RUN._utc()} {R15.summary(rec)}", flush=True)
    return True


REPEAT_OF = "s15_B1_SP_Exp3_s+3"         # V1: an archived Stage 15 run with C8 (270.23 s), made again here


def repeat_spec():
    sp = PB.b1_spec("M50_SP_Exp3", 3)
    assert sp["id"] == REPEAT_OF
    sp = dict(sp)
    sp.update({"id": "s16_rep_" + REPEAT_OF[4:], "stage": 16, "kind": "repeat", "archived_id": REPEAT_OF})
    return sp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--worker", type=int, default=0)
    ap.add_argument("--max-minutes", type=float, default=None)
    ap.add_argument("--v-window", type=float, default=20.0)
    a = ap.parse_args()
    if a.cmd == "list":
        h, text = list_hash()
        print(h)
        print(text[:3000])
        return
    if a.cmd == "status":
        recs = load()
        print(len(recs), "records;", "X worker-hours %.2f" % x_worker_hours(recs))
        print("T:", t_state(recs)[0])
        for t, (st, sp, res) in n_all(recs).items():
            print("N", t, st, (sp or {}).get("id"),
                  ("(%.1f, %.1f]" % (res["lo"][0], res["hi"][0])) if res and "lo" in res else "")
        print("V:", v_state(recs, n_all(recs))[0])
        for sp in pending(recs):
            print("pending", sp["id"])
        return
    ctx = R15.Context()
    if a.cmd == "repeat":
        machine = RUN.machine_info(f"stage16-{a.worker}")
        work_one(repeat_spec(), REPEATS, a.worker, ctx, machine)
        return
    if a.cmd == "work":
        # An order of work, not a result: a worker stops taking runs after --max-minutes (so that no run is cut short
        # by the background job's two-hour limit), and takes a refined run of V only within its first --v-window
        # minutes (a refined run takes about an hour); older, it leaves V's runs to a fresh worker.
        machine = RUN.machine_info(f"stage16-{a.worker}")
        t0 = time.time()
        recs15 = PB.load()
        a1 = json.load(open(XS_OUT))["A1_rows"]
        while True:
            if os.path.exists(STOP_FILE):
                return
            age = time.time() - t0
            if a.max_minutes is not None and age > 60.0 * a.max_minutes:
                print("max minutes reached", flush=True)
                return
            recs = load()
            os.makedirs(RUNS, exist_ok=True)
            pend = [sp for sp in pending(recs, recs15, a1)
                    if not os.path.exists(os.path.join(RUNS, sp["id"] + ".claim"))]
            if age > 60.0 * a.v_window:
                if any(sp["kind"] == "V" for sp in pend):
                    print("a V run is due: it waits for a fresh worker", flush=True)
                pend = [sp for sp in pend if sp["kind"] != "V"]
                if not pend and any(sp["kind"] == "V" for sp in pending(recs, recs15, a1)
                                    if not os.path.exists(os.path.join(RUNS, sp["id"] + ".claim"))):
                    print("only V runs are due: this worker ends", flush=True)
                    return
            if not pend:
                if [f for f in os.listdir(RUNS) if f.endswith(".claim")]:
                    time.sleep(10)
                    continue
                print("nothing left", flush=True)
                return
            work_one(pend[0], RUNS, a.worker, ctx, machine)


if __name__ == "__main__":
    main()
