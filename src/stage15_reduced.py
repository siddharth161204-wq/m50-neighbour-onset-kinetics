"""Stage 15, Part A: the reactive cross-section's runs (DECISIONS.md D173 to D175), before any new
three-dimensional run.

  A1  every central continued run of the archive (A0.1) made again in the cross-section, to the archived run's end,
      with its test's trigger and its delivery: whether the mean reaches 255.68 C (C8), the mean's peak or crossing
      time, the far face's peak (explanatory: the archive is read, not predicted).
  A2  E*(C8), the least delivered energy for which C8 happens within 900 s: for the sixteen tests with the 21.39 s
      triangular delivery, and for the nine propagated tests with constant power over 120, 240 and 360 s. The search
      starts at E0, multiplies or divides by 1.5 until a C8 run lies above a run without C8, then halves the bracket
      until it is no wider than 1 % of its midpoint; E*(C8) is the midpoint. For the nine, with each of the four
      deliveries, the energy at which C8 falls at the measured time t_m, by Stage 9's rule for f_t (D91 (3)): the
      grid f8_hi + 0, 0.0125, 0.025, 0.05, 0.1 and 0.2 (fractions of E_e, f8_hi the upper end of the E*(C8)
      bracket) read in order up to its first point whose C8 comes before t_m, then the bisection between f8_lo and
      that point on whether C8 comes before t_m, until the bracket is at most 0.005 E_e wide or a run's C8 lies
      within 10 s of t_m; "matched" (that run), "bracketed" (C8's time linear between the ends), "threshold" (the
      lower end without C8) or "above grid".
  C2  (for Part C) the sixteen tests with no delivery, at the low, central and high contacts.
Every run's summary is written to results/stage15_xs/<key>.json as it ends, so the work resumes from the records;
the searches' results go to results/stage15_cross_section.json.

Usage: python3 src/stage15_reduced.py a1 | a2 | ft | c2 | write   [--workers 2]
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
import v12_model as V                      # noqa: E402  (unchanged)
import stage9_run as R9                    # noqa: E402  (unchanged)
import stage15_inputs as IN                # noqa: E402
import stage15_model as M15                # noqa: E402
import stage15_section as S15              # noqa: E402
import stage15_archive as AR               # noqa: E402

XS = os.path.join(IN.RES, "stage15_xs")
OUT = os.path.join(IN.RES, "stage15_cross_section.json")
DT_EARLY, DT_LATE, T_SWITCH = 0.01, 0.1, 30.0
WIDTH = 0.01                                     # E*(C8): bracket at most 1 % of its midpoint
FACTOR = 1.5                                     # the bracketing step
GRID_FT = (0.0, 0.0125, 0.025, 0.05, 0.1, 0.2)   # Stage 9's grid (D91 (1)), fractions of E_e
WIDTH_FT, TOL_FT_S = 0.005, 10.0                 # Stage 9's tolerances (D91 (3))
E0 = {"tri": 8000.0, "con": 6000.0}              # where each E*(C8) search starts (J)


# ------------------------------------------------------------------------------------------------ one run
def case(test, deliveries, t_end=900.0, h="central", kin="mean", sei0=None, shift_K=0.0, stop=True):
    d = [dict(x) for x in deliveries]
    c = {"test": test, "deliveries": d, "t_end_s": float(t_end), "h": h, "kin": kin, "sei0": sei0,
         "shift_K": float(shift_K), "stop": bool(stop), "dt": [DT_EARLY, DT_LATE, T_SWITCH]}
    c["key"] = hashlib.sha256(json.dumps(c, sort_keys=True).encode()).hexdigest()[:20]
    return c


def tri(E, tau=IN.TAU_TRIGGER):
    return {"shape": "tri", "E_J": round(float(E), 6), "tau_s": float(tau), "t0_s": 0.0}


def con(E, tau):
    return {"shape": "con", "E_J": round(float(E), 6), "tau_s": float(tau), "t0_s": 0.0}


_CTX = {}


def _history(test, h):
    key = (test, h)
    if key not in _CTX:
        t = IN.tests()[test]
        _CTX[key] = V.stage5_t1(t["connection"], V.H_CONTACT[h], V.G_TAB["central"], IN.TAU_TRIGGER,
                                float(t["E_b_J"]), IN.T_AMB)[0]
    return _CTX[key]


def _section(h):
    key = ("sec", h)
    if key not in _CTX:
        _CTX[key] = S15.ReactiveSection(V.H_CONTACT[h])
    return _CTX[key]


def _kin(kin):
    if kin == "mean":
        return V.bcrnn.Kinetics()
    key = ("kin", kin)
    if key not in _CTX:
        _CTX[key] = R9.Context().kinetics(kin)[0]
    return _CTX[key]


def _src(d):
    if d["shape"] == "tri":
        return M15.Triangular(d["E_J"], d["tau_s"], d["t0_s"])
    if d["shape"] == "con":
        return M15.Constant(d["E_J"], d["tau_s"], d["t0_s"])
    if d["shape"] == "hold":
        return M15.Hold(d["P_W"], d["t0_s"], 900.0)
    raise ValueError(d)


def path_of(c):
    return os.path.join(XS, c["key"] + ".json")


def run(c):
    """One cross-section run, read from its record if it exists."""
    p = path_of(c)
    if os.path.exists(p):
        return json.load(open(p))
    t0 = time.time()
    sec = _section(c["h"])
    srcs = [_src(d) for d in c["deliveries"] if d.get("E_J", 1.0) > 0 and d.get("P_W", 1.0) > 0]
    r = sec.run(_history(c["test"], c["h"]), srcs, c["t_end_s"], dt_early=DT_EARLY, dt_late=DT_LATE,
                t_switch=T_SWITCH, kin=_kin(c["kin"]), stop_mean=IN.T_LEVEL if c["stop"] else None,
                shift_K=c["shift_K"], sei0=c["sei0"])
    fj = AR.far_face_jump(r["t"], r["far_C"], r["t_c8_s"])
    at = lambda x: float(np.interp(x, r["t"], r["far_C"])) if x <= r["t"][-1] + 1e-9 else None
    out = {k: v for k, v in r.items() if not isinstance(v, np.ndarray)}
    out.update({"case": c, "C8": r["t_c8_s"] is not None, "far_jump": fj, "far_at_45_C": at(45.0),
                "far_at_271.5_C": at(IN.T_PROP_FIG_S), "wall_s": time.time() - t0,
                "mean_at_271.5_C": float(np.interp(IN.T_PROP_FIG_S, r["t"], r["mean_C"]))
                if IN.T_PROP_FIG_S <= r["t"][-1] else None})
    os.makedirs(XS, exist_ok=True)
    np.savez_compressed(os.path.join(XS, c["key"] + ".npz"), t=r["t"], mean_C=r["mean_C"], far_C=r["far_C"],
                        max_C=r["max_C"], rxn_cum_J=r["rxn_cum_J"])
    tmp = p + f".tmp{os.getpid()}"
    json.dump(out, open(tmp, "w"), indent=1, default=float)
    os.replace(tmp, p)
    return out


# ------------------------------------------------------------------------------------------------ A1
def a1_cases():
    out = []
    for r in AR.table():
        if r["group"] != "central":
            continue
        if r["shape"] == "none":
            dl = []
        elif r["shape"] == "tri":
            dl = [tri(r["E_delivered_J"], r["tau_d_s"])]
        else:
            dl = [con(r["E_delivered_J"], r["tau_d_s"])]
        c = case(r["test"], dl, t_end=r["t_end_s"])
        c["archived"] = r["id"]
        out.append(c)
    return out


# ------------------------------------------------------------------------------------------------ A2: E*(C8)
def estar(test, shape, tau, E0_J=None, log=None):
    mk = (lambda E: [tri(E, tau)]) if shape == "tri" else (lambda E: [con(E, tau)])
    E = E0.get(shape) if E0_J is None else E0_J
    lo = hi = None
    runs = []
    for _ in range(40):
        r = run(case(test, mk(E)))
        runs.append((E, r["C8"], r["t_c8_s"], r["peak_mean_C"]))
        if r["C8"]:
            hi = E if hi is None else min(hi, E)
        else:
            lo = E if lo is None else max(lo, E)
        if lo is not None and hi is not None:
            if hi - lo <= WIDTH * 0.5 * (lo + hi):
                break
            E = 0.5 * (lo + hi)
        elif hi is None:
            E = E * FACTOR
            if E > 1.0e6:
                break
        else:
            E = E / FACTOR
            if E < 1.0:
                lo = 0.0
                r0 = run(case(test, []))                        # no delivery: C8 with the trigger alone?
                runs.append((0.0, r0["C8"], r0["t_c8_s"], r0["peak_mean_C"]))
                if r0["C8"]:
                    hi, lo = 0.0, 0.0
                break
    res = {"test": test, "shape": shape, "tau_s": tau, "lo_J": lo, "hi_J": hi,
           "E_star_J": None if (lo is None or hi is None) else 0.5 * (lo + hi), "runs": runs}
    if res["E_star_J"] is not None:
        res["f_star"] = res["E_star_J"] / IN.e_e(test)
    return res


def a2_specs():
    out = [(t, "tri", IN.TAU_TRIGGER) for t in IN.TEST_ORDER]
    for tau in IN.TAUS_LONG:
        out += [(t, "con", tau) for t in IN.propagated()]
    return out


def _estar_task(a):
    return estar(*a)


# ------------------------------------------------------------------------------------------------ A2: at t_m
def at_measured(test, shape, tau, est):
    """Stage 9's rule for f_t (D91 (3)) read on C8."""
    E_e = IN.e_e(test)
    tm = float(IN.tests()[test]["time_s"])
    mk = (lambda E: [tri(E, tau)]) if shape == "tri" else (lambda E: [con(E, tau)])
    f8_lo, f8_hi = est["lo_J"] / E_e, est["hi_J"] / E_e
    pts = []
    hi0 = None
    for g in GRID_FT:
        f = round(f8_hi + g, 12)
        r = run(case(test, mk(f * E_e)))
        pts.append((f, r["t_c8_s"]))
        if r["C8"] and abs(r["t_c8_s"] - tm) <= TOL_FT_S:
            return {"status": "matched", "f": f, "E_J": f * E_e, "t_C8_s": r["t_c8_s"], "t_m_s": tm, "points": pts}
        if r["C8"] and r["t_c8_s"] < tm:
            hi0 = f
            break
    if hi0 is None:
        return {"status": "above grid", "t_m_s": tm, "points": pts}
    lo, hi = f8_lo, hi0
    t_lo = None
    t_hi = dict(pts)[hi0]
    while hi - lo > WIDTH_FT + 1e-12:
        mid = round(0.5 * (lo + hi), 12)
        r = run(case(test, mk(mid * E_e)))
        pts.append((mid, r["t_c8_s"]))
        if r["C8"] and abs(r["t_c8_s"] - tm) <= TOL_FT_S:
            return {"status": "matched", "f": mid, "E_J": mid * E_e, "t_C8_s": r["t_c8_s"], "t_m_s": tm,
                    "points": pts}
        if r["C8"] and r["t_c8_s"] < tm:
            hi, t_hi = mid, r["t_c8_s"]
        else:
            lo, t_lo = mid, (r["t_c8_s"] if r["C8"] else None)
    if t_lo is None:
        return {"status": "threshold", "lo_f": lo, "hi_f": hi, "t_hi_s": t_hi, "t_m_s": tm, "points": pts}
    f = lo + (hi - lo) * (t_lo - tm) / (t_lo - t_hi)
    return {"status": "bracketed", "f": f, "E_J": f * E_e, "lo_f": lo, "hi_f": hi, "t_lo_s": t_lo, "t_hi_s": t_hi,
            "t_m_s": tm, "points": pts}


def _ft_task(a):
    test, shape, tau, est = a
    return {"test": test, "shape": shape, "tau_s": tau, **at_measured(test, shape, tau, est)}


# ------------------------------------------------------------------------------------------------ C2 (no delivery)
def c2_cases():
    return [case(t, [], h=h) for h in ("low", "central", "high") for t in IN.TEST_ORDER]


# ------------------------------------------------------------------------------------------------ B3 and B4's cases
F_B4 = 0.040625                                   # M50_PT_Exp4's 5,045 J (Stage 10's tri21_C2_hi)
HOLD_START_W = 10.0


def _pulse_hold(P):
    E = F_B4 * IN.e_e(IN.HIST_TEST)
    return [tri(E), {"shape": "hold", "P_W": float(P), "t0_s": IN.TAU_TRIGGER}]


def b3_hold():
    """The cross-section's hold: Part B3 (b)'s rule on the 2.5 W grid from HOLD_START_W."""
    tgt, tol, step = IN.T_PROP_FIG_S, IN.B3_TOL_S, IN.B3_STEP_W
    runs = {}

    def cls(r):
        if not r["C8"]:
            return "late"
        return "early" if r["t_c8_s"] < tgt - tol else ("late" if r["t_c8_s"] > tgt + tol else "hit")

    P = HOLD_START_W
    for _ in range(40):
        r = run(case(IN.HIST_TEST, _pulse_hold(P)))
        runs[P] = r
        k = cls(r)
        if k == "hit":
            return {"status": "matched", "P_W": P, "t_C8_s": r["t_c8_s"], "P_start_W": P,
                    "runs": {p: x["t_c8_s"] for p, x in runs.items()}}
        Ps = sorted(runs)
        for a, b in zip(Ps[:-1], Ps[1:]):
            if cls(runs[a]) == "late" and cls(runs[b]) == "early":
                ta, tb = runs[a]["t_c8_s"], runs[b]["t_c8_s"]
                near = a if (ta is not None and abs(ta - tgt) < abs(tb - tgt)) else b
                return {"status": "bracketed", "P_lo_W": a, "P_hi_W": b, "P_start_W": near,
                        "runs": {p: x["t_c8_s"] for p, x in runs.items()}}
        P = P + step if k == "late" else P - step
        if P <= 0:
            break
    return {"status": "no result", "runs": {p: x["t_c8_s"] for p, x in runs.items()}}


def b4_cases():
    E = F_B4 * IN.e_e(IN.HIST_TEST)
    out = [case(IN.HIST_TEST, [tri(E)], kin=IN.KIN_DRAWS[r]) for r in (5, 50, 151, 196)]
    out.append(case(IN.HIST_TEST, [tri(E)], sei0=IN.SEI_AGED))
    return out


def b4_shift():
    E = F_B4 * IN.e_e(IN.HIST_TEST)
    s, first, rs = 5.0, None, {}
    while s <= 60.0 + 1e-9:
        r = run(case(IN.HIST_TEST, [tri(E)], shift_K=s))
        rs[s] = r["t_c8_s"]
        if r["C8"]:
            first = s
            break
        s += 5.0
    if first is None:
        return {"status": "no C8 up to 60 K", "runs": rs}
    r = run(case(IN.HIST_TEST, [tri(E)], shift_K=first - 2.5))
    rs[first - 2.5] = r["t_c8_s"]
    least = first - 2.5 if r["C8"] else first
    return {"status": "found", "least_shift_K": least, "t_C8_s": rs[least], "runs": rs}


def _b_task(name):
    if name == "b3":
        return ("B3_hold", b3_hold())
    if name == "b4shift":
        return ("B4_shift", b4_shift())
    if name == "b4":
        return ("B4_cases", [{"kin": c["kin"], "sei0": c["sei0"], **{k: run(c)[k] for k in
                                                                     ("C8", "t_c8_s", "peak_mean_C")}}
                             for c in b4_cases()])
    if name == "b2":
        E_e = IN.e_e(IN.HIST_TEST)
        return ("B2_cases", [{"f": f, **{k: run(case(IN.HIST_TEST, [con(f * E_e, 240.0)]))[k]
                                        for k in ("C8", "t_c8_s", "peak_mean_C")}} for f in (0.05, 0.046875)])
    raise ValueError(name)


# ------------------------------------------------------------------------------------------------ driving
def _pool(fn, items, workers):
    if workers <= 1:
        return [fn(x) for x in items]
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(fn, items, chunksize=1))


def _load_out():
    return json.load(open(OUT)) if os.path.exists(OUT) else {}


def _save_out(d):
    tmp = OUT + ".tmp"
    json.dump(d, open(tmp, "w"), indent=1, default=float)
    os.replace(tmp, OUT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    out = _load_out()
    if a.cmd == "a1":
        cs = a1_cases()
        res = _pool(run, cs, a.workers)
        out["A1"] = [{"archived": c["archived"], "key": c["key"]} for c in cs]
    elif a.cmd == "a2":
        res = _pool(_estar_task, a2_specs(), a.workers)
        out["A2"] = res
    elif a.cmd == "ft":
        est = {(r["test"], r["shape"], r["tau_s"]): r for r in out["A2"]}
        items = []
        for t in IN.propagated():
            for shape, tau in [("tri", IN.TAU_TRIGGER)] + [("con", x) for x in IN.TAUS_LONG]:
                e = est[(t, shape, tau)]
                if e["E_star_J"] is not None:
                    items.append((t, shape, tau, e))
        out["A2_at_measured"] = _pool(_ft_task, items, a.workers)
    elif a.cmd == "c2":
        cs = c2_cases()
        _pool(run, cs, a.workers)
        out["C2"] = [{"test": c["test"], "h": c["h"], "key": c["key"]} for c in cs]
    elif a.cmd == "b":
        for k, v in _pool(_b_task, ["b3", "b4shift", "b4", "b2"], a.workers):
            out[k] = v
    _save_out(out)
    print("done", a.cmd)


if __name__ == "__main__":
    main()
