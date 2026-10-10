#!/usr/bin/env python3
"""V2 before any case is run, on synthetic histories only (no archived history is touched here).

Synthetic histories, sampled every 0.5 s like the archive: isothermal holds; linear ramps from 25 C at 0.3 to 30 K/s,
capped at 400 C; and smooth pulses T = 25 + A (t/tp) exp(1 - t/tp) with peaks of 120 to 350 C reached at tp = 5, 30
and 80 s. Each is integrated with the base numerics of onset_kinetics.py and with the tolerances, the largest step
and the evaluation grid all halved. Acceptance (brief, V2): no onset time moves by more than 1 % of itself.

The ramp runs also give the temperature at which each level is first reached as a function of the heating rate,
which predictions.md uses.
"""
import argparse, json, os
import numpy as np
import onset_kinetics as OK

LEVELS = OK.LEVELS_K_PER_MIN


def histories():
    t = np.arange(0.0, 900.0 + 1e-9, 0.5)
    H = {}
    for TC in (110.0, 130.0, 150.0, 180.0, 200.0):
        H[f"hold_{TC:.0f}C"] = np.full_like(t, TC + 273.15)
    for beta in (0.3, 1.0, 3.0, 10.0, 30.0):
        H[f"ramp_{beta:g}Kps"] = np.minimum(25.0 + beta * t, 400.0) + 273.15
    for peak in (120.0, 180.0, 250.0, 350.0):
        for tp in (5.0, 30.0, 80.0):
            x = t / tp
            H[f"pulse_{peak:.0f}C_tp{tp:.0f}s"] = 298.15 + (peak - 25.0) * x * np.exp(1.0 - x)
    return t, H


def onsets(t, T, **kw):
    tt, sh, Y, Tg, n = OK.integrate_along(t, T, **kw)
    res = {}
    for lv in LEVELS:
        tc = OK.first_crossing(tt, sh, lv)
        res[str(lv)] = None if tc is None else {"t_s": tc, "T_C": float(np.interp(tc, tt, Tg) - 273.15)}
    res["peak_Kpm"] = float(sh.max())
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="../results"); a = ap.parse_args()
    t, H = histories()
    base_kw = dict(rtol=OK.RTOL, atol=OK.ATOL, max_step=OK.MAX_STEP, grid=OK.GRID)
    half_kw = dict(rtol=OK.RTOL / 2, atol=OK.ATOL / 2, max_step=OK.MAX_STEP / 2, grid=OK.GRID / 2)
    tight_kw = dict(rtol=1e-11, atol=1e-14, max_step=0.05, grid=0.002)
    out, worst = {}, 0.0
    worst_tight = 0.0
    for name, T in H.items():
        b, h, ti = onsets(t, T, **base_kw), onsets(t, T, **half_kw), onsets(t, T, **tight_kw)
        rec = {"base": b, "halved": h, "tight": ti, "rel_change": {}, "rel_change_tight": {}}
        for lv in map(str, LEVELS):
            if (b[lv] is None) != (h[lv] is None) or (b[lv] is None) != (ti[lv] is None):
                rec["rel_change"][lv] = "crossing appears or disappears"
                worst = float("inf")
                continue
            if b[lv] is None:
                continue
            for key, other, store in (("rel_change", h, None), ("rel_change_tight", ti, None)):
                denom = max(b[lv]["t_s"], 1e-9)
                rc = abs(other[lv]["t_s"] - b[lv]["t_s"]) / denom if b[lv]["t_s"] > 0 else abs(other[lv]["t_s"] - b[lv]["t_s"])
                rec[key][lv] = rc
                if key == "rel_change":
                    worst = max(worst, rc)
                else:
                    worst_tight = max(worst_tight, rc)
        out[name] = rec
        print(name, {lv: (None if b[lv] is None else (round(b[lv]["t_s"], 3), round(b[lv]["T_C"], 2))) for lv in map(str, LEVELS)},
              "peak", round(b["peak_Kpm"], 4), "max rel change", {k: f"{v:.2e}" if isinstance(v, float) else v for k, v in rec["rel_change"].items()})
    summary = {"max_relative_change_halved": worst, "max_relative_change_tight": worst_tight, "pass": worst < 0.01,
               "note": "a crossing at t = 0 (holds above the fresh onset temperature) is compared in absolute seconds"}
    json.dump({"summary": summary, "histories": out}, open(os.path.join(a.out, "v2_synthetic.json"), "w"), indent=1)
    print(json.dumps(summary, indent=1))
