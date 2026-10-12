#!/usr/bin/env python3
"""The study's own central estimates for predictions_stage3.md, made before any draw is integrated along an archived
history (the brief's rule).

Each kinetic draw is integrated with the Stage 1 driver (onset_kinetics.integrate_along: BDF, the same tolerances,
step limit and 0.5 s sampling) along two SYNTHETIC linear ramps from 25 C, never along an archived history:
  15 K/s, the hottest node's heating rate near 108 C in the headline case (33.2 kJ, 30 s, 500 mW/K), and
   3 K/s, the lumped node's rate there.
The archived histories enter only as temperature series: the time each first reaches a draw's onset temperature, and
its peak. Estimates (the mean model's onsets in Stage 1 sat at its fresh onset temperature in every case, 108.4 C):
  headline onset of a node = first time its archived history reaches the draw's onset temperature on that node's ramp;
  a node starts in a case if its archived peak reaches that temperature (P3 uses the 3 K/s value for both nodes,
  since near a peak both histories are slow); P6 = share of draws whose 15 K/s onset lies below 100 C.
These ignore reactant consumption along the real history and the history's curvature, so they are forecasts only.

Usage: python3 predictions_stage3_estimates.py --series <clone>/results/resolved_series --out ../results
"""
import argparse, glob, json, os
from multiprocessing import Pool
import numpy as np
import bcrnn
import onset_kinetics as OK
import stage3_draws as S

RAMPS_K_PER_S = {"hottest": 15.0, "lumped": 3.0}
HEADLINE = "two_E33223_tau30_G0.5"
_P = None


def _init():
    global _P
    _P = S.load_particles()


def ramp_onset(kin, rate):
    """Onset temperature (C) and reaction at 0.15 K/min along a synthetic ramp from 25 C to 400 C, sampled at 0.5 s."""
    OK.KIN = kin
    t = np.arange(0.0, (400.0 - 25.0) / rate + 0.5, 0.5)
    T = 298.15 + np.minimum(rate * t, 375.0)
    tt, sh, Y, Tg, _ = OK.integrate_along(t, T)
    tc = OK.first_crossing(tt, sh, 0.15)
    if tc is None:
        return None, None
    k = int(np.searchsorted(tt, tc))
    return float(np.interp(tc, tt, Tg) - 273.15), OK.dominant_reaction(Tg[k], Y[:, k])


def one(draw):
    d, ae, sep, cat = draw
    kin = S.draw_kinetics(_P, ae, sep, cat)
    out = {"draw": d}
    for node, rate in RAMPS_K_PER_S.items():
        out[f"T_on_{node}_ramp_C"], out[f"rxn_{node}_ramp"] = ramp_onset(kin, rate)
    return out


def first_time(t, T_C, level):
    i = np.where(T_C >= level)[0]
    if not i.size:
        return None
    k = int(i[0])
    if k == 0:
        return float(t[0])
    return float(t[k - 1] + (level - T_C[k - 1]) / (T_C[k] - T_C[k - 1]) * (t[k] - t[k - 1]))


def width95(times):
    v = np.array([np.inf if x is None else x for x in times], float)
    lo, hi = np.percentile(v, [2.5, 97.5])
    return float(hi - lo) if np.isfinite(hi) else None, float(lo), (float(hi) if np.isfinite(hi) else None)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", required=True)
    ap.add_argument("--out", default="../results")
    ap.add_argument("--jobs", type=int, default=2)
    a = ap.parse_args()
    draws, _ = S.all_draws()
    with Pool(a.jobs, initializer=_init) as pool:
        per = sorted(pool.map(one, draws, chunksize=4), key=lambda r: r["draw"])
    mean_model = {node: ramp_onset(bcrnn.Kinetics(), rate)[0] for node, rate in RAMPS_K_PER_S.items()}
    # archived temperature series only (no kinetics): peaks and first times
    cases = {}
    for f in sorted(glob.glob(os.path.join(a.series, "two_E*_tau*_G*.npz"))):
        dd = np.load(f)
        name = os.path.basename(f)[:-4]
        cases[name] = {"G": float(name.split("_G")[1]), "hot": (dd["t"], dd["Tmax"] - 273.15), "lump": (dd["t_be"], dd["T2_be"] - 273.15)}
    assert len(cases) == 42
    th, tl = cases[HEADLINE]["hot"], cases[HEADLINE]["lump"]
    hot_t, lump_t, before, p3, early = [], [], 0, [], 0
    for r in per:
        Th, Tl = r["T_on_hottest_ramp_C"], r["T_on_lumped_ramp_C"]
        a_ = None if Th is None else first_time(*th, Th)
        b_ = None if Tl is None else first_time(*tl, Tl)
        hot_t.append(a_); lump_t.append(b_)
        if a_ is not None and (b_ is None or a_ < b_):
            before += 1
        if Th is not None and Th < 100.0:
            early += 1
        T3 = Tl
        g = None
        if T3 is not None:
            only = [c["G"] for c in cases.values() if c["hot"][1].max() >= T3 and c["lump"][1].max() < T3]
            g = min(only) if only else None
        p3.append(g)
    n = len(per)
    wh, wl = width95(hot_t), width95(lump_t)
    vals = sorted(set(x for x in p3 if x is not None))
    est = {"method": __doc__.split("\n\n")[1], "n_draws": n, "ramps_K_per_s": RAMPS_K_PER_S,
           "mean_model_onset_on_ramps_C": mean_model,
           "onset_temperature_on_ramps_C": {node: {"p2.5": float(np.nanpercentile([np.nan if r[f"T_on_{node}_ramp_C"] is None else r[f"T_on_{node}_ramp_C"] for r in per], 2.5)),
                                                   "median": float(np.nanpercentile([np.nan if r[f"T_on_{node}_ramp_C"] is None else r[f"T_on_{node}_ramp_C"] for r in per], 50)),
                                                   "p97.5": float(np.nanpercentile([np.nan if r[f"T_on_{node}_ramp_C"] is None else r[f"T_on_{node}_ramp_C"] for r in per], 97.5)),
                                                   "no_onset_below_400C": sum(r[f"T_on_{node}_ramp_C"] is None for r in per),
                                                   "sei_starts": sum(r[f"rxn_{node}_ramp"] == "sei_decomp" for r in per)}
                                            for node in RAMPS_K_PER_S},
           "P1_share_hottest_first": before / n,
           "P2_width_s": {"hottest": wh[0], "hottest_p2.5_p97.5_s": wh[1:], "lumped": wl[0], "lumped_p2.5_p97.5_s": wl[1:]},
           "P3_distribution": {**{f"{int(round(v * 1000))} mW/K": sum(x == v for x in p3) / n for v in vals}, "none": sum(x is None for x in p3) / n},
           "P6_share_onset_below_100C": early / n,
           "per_draw": per}
    json.dump(est, open(os.path.join(a.out, "stage3_prediction_estimates.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in est.items() if k not in ("per_draw", "method")}, indent=1))
