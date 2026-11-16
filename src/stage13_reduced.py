"""Stage 13: every number of the reduced models (A1, A2, B1, B2) that the predictions state or the searches start
from, computed before any Stage 13 run of the resolved or the lumped model (DECISIONS.md D136).

Writes results/stage13_reduced.json. Usage: python3 stage13_reduced.py [--workers 2] [--part a|b|all]
"""
import argparse
import json
import math
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage13_inputs as IN                # noqa: E402

OUT = os.path.join(IN.RES, "stage13_reduced.json")
TAUS_PT1 = (5.0, 10.0, IN.TAU_TRIGGER, 40.0, 60.0, 120.0, 240.0, 360.0)
FIVE = ("M50_PT_Exp1", "M50_PP_Exp3", "M50_ST_Exp2", "M50_SP_Exp1", "M50_SP_Exp3")


def a_tasks():
    t = []
    for tau in TAUS_PT1:
        t.append(("A", "M50_PT_Exp1", tau, "half", 1.0, 1.0))
    t.append(("A", "M50_PT_Exp1", IN.TAU_TRIGGER, "whole", 1.0, 1.0))
    for test in ("M50_ST_Exp3", "M50_PT_Exp3"):
        for tau in (10.0, IN.TAU_TRIGGER, 60.0):
            t.append(("A", test, tau, "half", 1.0, 1.0))
    for test in IN.TEST_ORDER:                           # A3, explanatory
        if test not in ("M50_PT_Exp1", "M50_ST_Exp3", "M50_PT_Exp3"):
            t.append(("A", test, IN.TAU_TRIGGER, "half", 1.0, 1.0))
    for test in FIVE:
        if test != "M50_PT_Exp1":
            for tau in (10.0, 60.0):
                t.append(("A", test, tau, "half", 1.0, 1.0))
    # A2's discretisation: a finer grid and half the steps, PT_Exp1 at 21.39 and 120 s
    for tau in (IN.TAU_TRIGGER, 120.0):
        t.append(("A", "M50_PT_Exp1", tau, "half", 1.5, 0.5))
    return t


def b_tasks():
    t = []
    for test in IN.TEST_ORDER:
        for h in ("low", "central", "high"):
            t.append(("B", test, IN.TAU_TRIGGER, h, 0.0))
        for tau in (120.0, 360.0):
            t.append(("B", test, tau, "central", 0.0))
    for test in ("M50_PP_Exp3", "M50_ST_Exp2", "M50_PT_Exp3"):
        for d in (-2000.0, 2000.0):
            t.append(("B", test, IN.TAU_TRIGGER, "central", d))
    return t


def do(task):
    t0 = time.time()
    if task[0] == "A":
        import stage13_section as A2
        import stage13_skin as A1
        import numpy as np
        _, test, tau, region, refine, dt_scale = task
        kw = {}
        if dt_scale != 1.0:
            kw = {"dt_early": 0.01 * dt_scale, "dt_late": max(0.01, min(0.1, tau / 1000.0)) * dt_scale}
        r = A2.threshold(test, tau, region=region, refine=refine, **kw)
        out = {k: v for k, v in r.items() if k != "T_cond_at_hot_spot"}
        if not r["trigger_alone"] and region in ("half", "whole") and refine == 1.0 and dt_scale == 1.0:
            tt, Tc = r["T_cond_at_hot_spot"]
            Tb = lambda x, tt=tt, Tc=Tc: float(np.interp(x, tt, Tc))
            out["A1"] = A1.threshold(test, tau, r["theta_deg"], Tb, region)
            out["A1_laplace_f_star"] = A1.threshold(test, tau, r["theta_deg"], Tb, region, impl="laplace")["f_star"]
        out.update({"key": f"A2_{test}_{region}_tau{tau:.4f}_r{refine:g}_dt{dt_scale:g}", "refine": refine,
                    "dt_scale": dt_scale, "wall_s": time.time() - t0})
        return out
    import stage13_twobody as B2
    _, test, tau, h, d = task
    c = B2.Case(test, tau_d=tau, h=h, dE_body=d)
    E = c.threshold()
    s = c.summary(E)
    return {"key": f"B2_{test}_tau{tau:.4f}_{h}_dEb{d:+.0f}", "test": test, "tau_d_s": tau, "h": h, "dE_body_J": d,
            "E_star_J": E, "f_star": E / IN.e_e(test), "binding": s["binding"], "above": s.get("above"),
            "below": s.get("below"), "wall_s": time.time() - t0}


def _key(task):
    if task[0] == "A":
        _, test, tau, region, refine, dt_scale = task
        return f"A2_{test}_{region}_tau{tau:.4f}_r{refine:g}_dt{dt_scale:g}"
    _, test, tau, h, d = task
    return f"B2_{test}_tau{tau:.4f}_{h}_dEb{d:+.0f}"


def main(workers=2, part="all"):
    tasks = (a_tasks() if part in ("a", "all") else []) + (b_tasks() if part in ("b", "all") else [])
    res = {}
    if os.path.exists(OUT):
        res = json.load(open(OUT))
    keys_done = set(res)
    tasks = [t for t in tasks if _key(t) not in keys_done]
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for r in ex.map(do, tasks):
            res[r["key"]] = r
            print(r["key"], round(r.get("f_star", float("nan")), 6), round(r["wall_s"], 1), flush=True)
            json.dump(res, open(OUT, "w"), indent=1, default=float)
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--part", default="all")
    a = ap.parse_args()
    main(a.workers, a.part)
