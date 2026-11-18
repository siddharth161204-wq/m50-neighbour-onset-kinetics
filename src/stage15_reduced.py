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


# ------------------------------------------------------------------------------------------------ A1's comparison
def a1_summary():
    """The cross-section against every central continued run (explanatory): the outcome (C8 within the archived
    run's span or not), the mean's crossing time where both cross, the mean's peak and its time where neither does,
    and the far face's peak; by delivery, and the largest differences. A3: the model cannot stand for the
    three-dimensional cell if it misses the outcome in more than one run in ten."""
    arch = {r["id"]: r for r in AR.table() if r["group"] == "central"}
    rows = []
    for c in a1_cases():
        x = run(c)
        a = arch[c["archived"]]
        rows.append({"id": a["id"], "test": a["test"], "shape": a["shape"], "tau_d_s": a["tau_d_s"],
                     "E_J": a["E_delivered_J"], "t_end_s": a["t_end_s"],
                     "C8_3d": a["mean_t_cross_s"] is not None, "C8_xs": x["C8"],
                     "t_C8_3d_s": a["mean_t_cross_s"], "t_C8_xs_s": x["t_c8_s"],
                     "mean_peak_3d_C": a["mean_peak_C"], "mean_peak_xs_C": x["peak_mean_C"],
                     "t_mean_peak_3d_s": a["mean_t_peak_s"], "t_mean_peak_xs_s": x["t_peak_mean_s"],
                     "far_peak_3d_C": a["far_peak_C"], "far_peak_xs_C": x["peak_far_C"],
                     "t_far_peak_3d_s": a["far_t_peak_s"], "t_far_peak_xs_s": x["t_peak_far_s"],
                     "hot_cross_3d_s": a["res_t_cross_s"], "hot_cross_xs_s": x["t_c1_s"],
                     "hot_peak_3d_C": a["res_peak_C"], "hot_peak_xs_C": x["peak_max_C"],
                     "rxn_3d_J": a["res_rxn_J"], "rxn_xs_J": x["rxn_J"]})
    same = [r for r in rows if r["C8_3d"] == r["C8_xs"]]
    miss = [r for r in rows if r["C8_3d"] != r["C8_xs"]]
    both = [r for r in rows if r["C8_3d"] and r["C8_xs"]]
    neither = [r for r in rows if not r["C8_3d"] and not r["C8_xs"]]

    def stats(xs):
        xs = [x for x in xs if x is not None]
        if not xs:
            return None
        return {"n": len(xs), "mean": float(np.mean(xs)), "min": float(min(xs)), "max": float(max(xs))}

    by = {}
    for key, sel in (("none", lambda r: r["shape"] == "none"), ("tri21", lambda r: r["shape"] == "tri"),
                     ("con120", lambda r: r["shape"] == "con" and r["tau_d_s"] == 120.0),
                     ("con240", lambda r: r["shape"] == "con" and r["tau_d_s"] == 240.0),
                     ("con360", lambda r: r["shape"] == "con" and r["tau_d_s"] == 360.0)):
        rr = [r for r in rows if sel(r)]
        by[key] = {"runs": len(rr), "same_outcome": sum(r["C8_3d"] == r["C8_xs"] for r in rr),
                   "C8_3d": sum(r["C8_3d"] for r in rr), "C8_xs": sum(r["C8_xs"] for r in rr),
                   "dt_C8_s": stats([r["t_C8_xs_s"] - r["t_C8_3d_s"] for r in rr if r["C8_3d"] and r["C8_xs"]]),
                   "d_mean_peak_K": stats([r["mean_peak_xs_C"] - r["mean_peak_3d_C"] for r in rr
                                           if not r["C8_3d"] and not r["C8_xs"]]),
                   "d_far_peak_K": stats([r["far_peak_xs_C"] - r["far_peak_3d_C"] for r in rr
                                          if not r["C8_3d"] and not r["C8_xs"] and r["far_peak_3d_C"] is not None])}
    return {"runs": len(rows), "same_outcome": len(same), "missed": len(miss),
            "missed_runs": [{k: r[k] for k in ("id", "E_J", "C8_3d", "C8_xs", "t_C8_3d_s", "t_C8_xs_s",
                                              "mean_peak_3d_C", "mean_peak_xs_C")} for r in miss],
            "A3_cannot_stand": len(miss) > 0.1 * len(rows),
            "dt_C8_s": stats([r["t_C8_xs_s"] - r["t_C8_3d_s"] for r in both]),
            "d_mean_peak_K": stats([r["mean_peak_xs_C"] - r["mean_peak_3d_C"] for r in neither]),
            "d_t_mean_peak_s": stats([r["t_mean_peak_xs_s"] - r["t_mean_peak_3d_s"] for r in neither]),
            "d_far_peak_K": stats([r["far_peak_xs_C"] - r["far_peak_3d_C"] for r in neither
                                   if r["far_peak_3d_C"] is not None]),
            "d_hot_peak_K": stats([r["hot_peak_xs_C"] - r["hot_peak_3d_C"] for r in neither]),
            "d_rxn_J": stats([r["rxn_xs_J"] - r["rxn_3d_J"] for r in neither]),
            "by_delivery": by, "rows": rows}


# ------------------------------------------------------------------------------------------------ the predictions
P_TEXT = [
    ("P1", "The reactive cross-section's E*(C8) lies within 15 % of the midpoint of the three-dimensional bracket in "
           "at least three of B1's four tests.",
     "for each of B1's four tests, |E*(C8) of the cross-section - m| / m <= 0.15, m the midpoint of B1's final "
     "bracket (a test whose search does not bracket counts as not within); holds if at least three are within.",
     "uncertain."),
    ("P2", "For M50_PT_Exp4 with the 21.39 s delivery, E*(C8) lies between 6 and 10 kJ.",
     "holds if the midpoint of B1's final bracket for M50_PT_Exp4 lies between 6,000 and 10,000 J.",
     "likely (the mean peaks at 190.6 C with 5,045 J and gains about 9 K per further kilojoule)."),
    ("P3", "In at least three of B1's four tests E*(C8) exceeds the whole-cell clock's threshold by 25 % or more.",
     "for each test, the midpoint of B1's final bracket against E*(C2) (above): it exceeds it by 25 % or more if it "
     "is at least 1.25 E*(C2); where E*(C2) is 0 (M50_SP_Exp3) any E*(C8) above 0 does; holds if at least three "
     "tests do.",
     "likely for the three strong triggers, uncertain for M50_ST_Exp3, whose weak trigger leaves the delivery to "
     "heat the whole cell in either model."),
    ("P4", "For M50_PT_Exp4, in the crossing run at the upper end of B1's bracket the mean crosses between 150 and "
           "400 s after the trigger's start.",
     "holds if that run's C8 time lies between 150 and 400 s.", "likely."),
    ("P5", "In that run the far face reads more than 15 K above 197.3 C, the reading from which the measured "
           "neighbour jumped, when its own jump begins.",
     "holds if the far face's reading at its jump's start (the rule above) exceeds 212.3 C.", "likely."),
    ("P6", "In B3 (b) the hold that brings the cell's own runaway to 271.5 s lies between 5 and 25 W.",
     "holds if the power at which C8 falls within 10 s of 271.5 s lies between 5 and 25 W; where the search ends "
     "with two neighbouring powers bracketing 271.5 s instead, if both lie between 5 and 25 W; otherwise it fails.",
     "likely."),
    ("P7", "Under none of the four draws and not with the aged SEI does the resolved cell run away at M50_PT_Exp4's "
           "5,045 J; and the least shift of the rate laws that makes it run away is 10 K or more, against the 6.1 K "
           "that the posterior's ignition temperatures span.",
     "holds if none of B4's five runs reaches C8 and B4's least shift (on its 5 K, then 2.5 K steps) is at least "
     "10 K.", "likely."),
    ("P8", "M50_PT_Exp4's 240 s run at 6,209 J, carried to 900 s, runs away.",
     "holds if B2's run at f = 0.05 reaches C8 within 900 s.", "likely."),
]


def for_predictions(xs):
    import stage15_predictions as PR
    a2 = {(r["test"], r["shape"], r["tau_s"]): r for r in xs["A2"]}
    E_e = IN.e_e(IN.HIST_TEST)
    b1 = {}
    for t in IN.B1_TESTS:
        r = a2[(t, "tri", IN.TAU_TRIGGER)]
        c2 = PR.e_c2(t)
        b1[t] = {"E_star_J": r["E_star_J"], "lo_J": r["lo_J"], "hi_J": r["hi_J"], "E_C2_J": c2["mid_J"],
                 "E_C2_source": c2["source"],
                 "ratio_to_C2": (r["E_star_J"] / c2["mid_J"]) if c2["mid_J"] > 0 else None}
    pt = b1[IN.HIST_TEST]
    upper = {}
    for k in (1.05, 1.15):
        x = run(case(IN.HIST_TEST, [tri(pt["E_star_J"] * k)]))
        upper[k] = {"E_J": pt["E_star_J"] * k, "t_C8_s": x["t_c8_s"], "far_jump": x["far_jump"]}
    xhi = run(case(IN.HIST_TEST, [tri(pt["hi_J"])]))
    upper["hi"] = {"E_J": pt["hi_J"], "t_C8_s": xhi["t_c8_s"], "far_jump": xhi["far_jump"]}
    b3, b4, b4s, b2 = xs["B3_hold"], xs["B4_cases"], xs["B4_shift"], xs["B2_cases"]

    def jr(u):
        if u["t_C8_s"] is None:
            return "no C8"
        if u["far_jump"][2] == "jump":
            return f"C8 at {u['t_C8_s']:.1f} s, the far face's jump starting at {u['far_jump'][1]:.1f} C"
        return (f"C8 at {u['t_C8_s']:.1f} s, the far face reading {u['far_jump'][1]:.1f} C twenty seconds before it "
                f"(no jump before C8)")
    n_within = sum(1 for t in IN.B1_TESTS if b1[t]["E_star_J"] is not None)
    lines = [
        "E*(C8) with the 21.39 s delivery for B1's four tests: " + "; ".join(
            f"{t} {b1[t]['E_star_J']:,.0f} J (bracket {b1[t]['lo_J']:,.0f} to {b1[t]['hi_J']:,.0f} J), "
            + (f"{b1[t]['ratio_to_C2']:.2f} times E*(C2) = {b1[t]['E_C2_J']:,.0f} J" if b1[t]["ratio_to_C2"]
               else "E*(C2) = 0") for t in IN.B1_TESTS) + ". B1's first runs lie 5 % below and above these.",
        f"M50_PT_Exp4, 21.39 s: at the upper end of the bracket ({pt['hi_J']:,.0f} J) {jr(upper['hi'])}; at 1.05 "
        f"E*(C8) {jr(upper[1.05])}; at 1.15 E*(C8) {jr(upper[1.15])}.",
        f"The hold (B3 (b)'s rule on the 2.5 W grid from {HOLD_START_W:.0f} W): {b3['status']}"
        + (f", {b3.get('P_W', b3.get('P_lo_W'))} W" if b3["status"] in ("matched",) else
           (f" between {b3['P_lo_W']} and {b3['P_hi_W']} W" if b3["status"] == "bracketed" else ""))
        + "; C8 times by power: " + ", ".join(
            f"{float(p):g} W {('%.1f s' % v) if v is not None else 'none'}" for p, v in sorted(
                b3["runs"].items(), key=lambda x: float(x[0]))) + f". B3 (b)'s first run is at {b3['P_start_W']} W.",
        "M50_PT_Exp4 at 5,045 J under the draws of rank 5, 50, 151, 196 and the aged SEI: " + ", ".join(
            ("C8 at %.1f s" % c["t_c8_s"]) if c["C8"] else ("no C8 (mean peak %.1f C)" % c["peak_mean_C"])
            for c in b4) + "; the least shift: " + (f"{b4s['least_shift_K']} K (C8 at {b4s['t_C8_s']:.1f} s)"
                                                  if b4s["status"] == "found" else b4s["status"]) + ".",
        "M50_PT_Exp4 with 240 s of constant power: " + ", ".join(
            f"{c['f'] * E_e:,.0f} J " + (("C8 at %.1f s" % c["t_c8_s"]) if c["C8"] else
                                        ("no C8 (mean peak %.1f C)" % c["peak_mean_C"])) for c in b2) + ".",
    ]
    reduced = {
        "P1": "the cross-section's E*(C8) are the centres of B1's searches (above); P1 measures how near the "
              "three-dimensional threshold lies to them.",
        "P2": f"{pt['E_star_J']:,.0f} J.",
        "P3": "; ".join(f"{t[4:]} " + (f"{b1[t]['ratio_to_C2']:.2f}" if b1[t]["ratio_to_C2"] else "E*(C2) = 0")
                        for t in IN.B1_TESTS) + " times E*(C2).",
        "P4": f"C8 at {upper['hi']['t_C8_s']:.1f} s at the upper end of its bracket, "
              f"{upper[1.05]['t_C8_s']:.1f} s at 1.05 E*(C8)." if upper["hi"]["t_C8_s"] and upper[1.05]["t_C8_s"]
        else "see above.",
        "P5": (f"{upper['hi']['far_jump'][1]:.1f} C at the upper end of its bracket, "
               f"{upper[1.05]['far_jump'][1]:.1f} C at 1.05 E*(C8).") if (upper["hi"]["far_jump"] and
                                                                          upper[1.05]["far_jump"]) else "see above.",
        "P6": (f"{b3['P_W']} W." if b3["status"] == "matched" else
               (f"between {b3['P_lo_W']} and {b3['P_hi_W']} W." if b3["status"] == "bracketed" else b3["status"])),
        "P7": ("none of the five reaches C8" if not any(c["C8"] for c in b4) else
               f"{sum(c['C8'] for c in b4)} of the five reach C8") + "; the least shift " + (
            f"{b4s['least_shift_K']} K." if b4s["status"] == "found" else b4s["status"] + "."),
        "P8": ("C8 at %.1f s." % b2[0]["t_c8_s"]) if b2[0]["C8"] else "no C8.",
    }
    preds = [{"id": i, "statement": s, "rule": r, "expectation": e, "reduced": reduced[i]} for i, s, r, e in P_TEXT]
    return {"B1": b1, "PT_Exp4_upper": upper, "lines": lines, "predictions": preds}


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
    elif a.cmd == "write":
        s = a1_summary()
        out["A1_summary"] = {k: v for k, v in s.items() if k != "rows"}
        out["A1_rows"] = s["rows"]
        out["for_predictions"] = for_predictions(out)
        out["settings"] = {"dt_early_s": DT_EARLY, "dt_late_s": DT_LATE, "t_switch_s": T_SWITCH, "width": WIDTH,
                           "factor": FACTOR, "E0_J": E0, "grid_ft": GRID_FT, "width_ft": WIDTH_FT,
                           "tol_ft_s": TOL_FT_S, "hold_start_W": HOLD_START_W}
    _save_out(out)
    print("done", a.cmd)


if __name__ == "__main__":
    main()
