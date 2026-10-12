#!/usr/bin/env python3
"""V5 (brief; DECISIONS.md D26 (6)): five kinetic draws rerun on the nine cases along the three histories with the
integration tolerances, the step limit and the evaluation grid all halved; no first time at 0.15, 1 or 10 K/min may
move by more than 1 % of itself (by more than 0.01 s, one evaluation step, for a first time under 1 s).

The five draws are those at the minimum, lower quartile, median, upper quartile and maximum of the hottest-ramp onset
temperature in results/stage3_prediction_estimates.json (the lower draw number on ties), chosen before 3a ran.

Usage: python3 v5_tolerance.py --series <clone>/results/resolved_series --out ../results [--jobs 2]
"""
import argparse, csv, json, os
from multiprocessing import Pool
import numpy as np
import onset_kinetics as OK
import stage3_draws as S
import stage3a as A

HALF = dict(rtol=OK.RTOL / 2, atol=OK.ATOL / 2, max_step=OK.MAX_STEP / 2, grid=OK.GRID / 2)
LEVELS = ("0.15Kpm", "1.0Kpm", "10.0Kpm")


def pick_draws(est_path):
    per = json.load(open(est_path))["per_draw"]
    v = sorted(((r["T_on_hottest_ramp_C"], r["draw"]) for r in per), key=lambda x: (x[0], x[1]))
    n = len(v)
    idx = [0, int(round(0.25 * (n - 1))), int(round(0.5 * (n - 1))), int(round(0.75 * (n - 1))), n - 1]
    return [v[i][1] for i in idx], [v[i][0] for i in idx]


def _one(args):
    d, series = args
    P = S.load_particles()
    draws, _ = S.all_draws(P)
    dt = draws[d - 1]
    files = [f for f in A.case_files(series) if os.path.basename(f)[:-4] in A.NINE]
    OK.KIN = S.draw_kinetics(P, *dt[1:])
    rows = []
    for f in files:
        out = OK.run_case(f, **HALF)
        rows += A.per_history_rows(out, d)
    return d, rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", required=True)
    ap.add_argument("--out", default="../results")
    ap.add_argument("--jobs", type=int, default=2)
    a = ap.parse_args()
    chosen, temps = pick_draws(os.path.join(a.out, "stage3_prediction_estimates.json"))
    base = {}
    for r in csv.DictReader(open(os.path.join(a.out, "stage3a_onsets.csv"))):
        if int(r["draw"]) in chosen and r["case"] in A.NINE:
            base[(int(r["draw"]), r["case"], r["history"])] = r
    with Pool(a.jobs) as pool:
        results = pool.map(_one, [(d, a.series) for d in chosen])
    worst, worst_abs_under_1s, fails, compared = 0.0, 0.0, [], 0
    for d, rows in results:
        for r in rows:
            b = base[(d, r["case"], r["history"])]
            for lv in LEVELS:
                t0 = None if b[f"t_{lv}_s"] in ("", "None") else float(b[f"t_{lv}_s"])
                t1 = r[f"t_{lv}_s"]
                if (t0 is None) != (t1 is None):
                    fails.append({"draw": d, "case": r["case"], "history": r["history"], "level": lv, "base": t0, "halved": t1})
                    continue
                if t0 is None:
                    continue
                compared += 1
                lim = 0.01 * t0 if t0 >= 1.0 else 0.01
                if t0 >= 1.0:
                    worst = max(worst, abs(t1 - t0) / t0)
                else:
                    worst_abs_under_1s = max(worst_abs_under_1s, abs(t1 - t0))
                if abs(t1 - t0) > lim:
                    fails.append({"draw": d, "case": r["case"], "history": r["history"], "level": lv, "base": t0, "halved": t1})
    rec = {"draws": chosen, "their_hottest_ramp_onset_C": temps, "halved": HALF, "first_times_compared": compared,
           "worst_relative_change": worst, "worst_absolute_change_s_for_first_times_under_1s": worst_abs_under_1s, "failures": fails, "pass": not fails}
    json.dump(rec, open(os.path.join(a.out, "stage3a_v5.json"), "w"), indent=1)
    print(json.dumps({k: rec[k] for k in ("draws", "first_times_compared", "worst_relative_change", "pass")}))
