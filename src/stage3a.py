#!/usr/bin/env python3
"""Stage 3a (DECISIONS.md D26): every kinetic draw integrated passively along the archived histories, as in Stage 1.

For each of the 200 draws of D22 the Stage 1 driver (`onset_kinetics.run_case`, unchanged numerics) runs with the
draw's kinetics in place of the posterior-mean model: the brief's nine cases along the hottest node, the resolved mean
and the lumped node; the other 33 two-strip cases along the hottest node and the lumped node only (for P3, the
author's choice of 12 October). One draw and one history at a time; nothing is batched across draws.

Each draw's records are written to results/stage3a_draws/draw_NNN.json as soon as the draw is done, so a stopped run
resumes where it stopped; --merge then writes results/stage3a_onsets.csv (one row per draw, case and history).

Usage:
  python3 stage3a.py --series <clone>/results/resolved_series --out ../results [--jobs 2]
  python3 stage3a.py --series ... --out ../results --merge
  python3 stage3a.py --series ... --out ../results --check-mean   (the mean model through this path equals Stage 1)
"""
import argparse, csv, glob, json, os, time
from multiprocessing import Pool
import numpy as np
import bcrnn
import onset_kinetics as OK
import stage3_draws as S

NINE = ["two_E33223_tau10_G0.5", "two_E33223_tau10_G0.2", "two_E33223_tau10_G0.1", "two_E33223_tau10_G0.05",
        "two_E33223_tau30_G0.5", "two_E33223_tau30_G0.2", "two_E33223_tau30_G0.1", "two_E33223_tau30_G0.05",
        "two_E21495_tau30_G0.5"]
TWO = ("hottest_node", "lumped")
_P, _SERIES = None, None


def case_files(series):
    files = sorted(glob.glob(os.path.join(series, "two_E*_tau*_G*.npz")))
    assert len(files) == 42, len(files)
    names = [os.path.basename(f)[:-4] for f in files]
    assert all(c in names for c in NINE)
    return files


def per_history_rows(out, draw):
    """Split a run_case record into one row per history, with Stage 1's field names minus the history prefix."""
    rows = []
    for h in OK.HISTORIES:
        keys = [k for k in out if k.startswith(h + "_")]
        if not keys:
            continue
        r = {"draw": draw, "case": out["case"], "history": h}
        r.update({k[len(h) + 1:]: out[k] for k in keys})
        rows.append(r)
    return rows


def run_draw(draw_tuple, files, kin, **kw):
    d, ae, sep, cat = draw_tuple
    OK.KIN = kin
    rows = []
    for f in files:
        name = os.path.basename(f)[:-4]
        out = OK.run_case(f, histories=None if name in NINE else TWO, **kw)
        rows += per_history_rows(out, d)
    return rows


def _init(series):
    global _P, _SERIES
    _P, _SERIES = S.load_particles(), series


def _work(args):
    draw_tuple, outdir = args
    d, ae, sep, cat = draw_tuple
    path = os.path.join(outdir, f"draw_{d:03d}.json")
    if os.path.exists(path):
        return d, "kept", 0.0
    t0 = time.time()
    rows = run_draw(draw_tuple, case_files(_SERIES), S.draw_kinetics(_P, ae, sep, cat))
    rec = {"draw": d, "an_ele_column": ae, "separator_column": sep, "ncm811_column": cat, "rows": rows,
           "seconds": time.time() - t0}
    tmp = path + ".tmp"
    json.dump(rec, open(tmp, "w"))
    os.replace(tmp, path)
    return d, "done", rec["seconds"]


def merge(outdir, out_csv, n=S.N_DRAWS):
    rows, missing = [], []
    for d in range(1, n + 1):
        p = os.path.join(outdir, f"draw_{d:03d}.json")
        if not os.path.exists(p):
            missing.append(d)
            continue
        rec = json.load(open(p))
        for r in rec["rows"]:
            rows.append({"draw": d, "an_ele_column": rec["an_ele_column"], "separator_column": rec["separator_column"],
                         "ncm811_column": rec["ncm811_column"], **{k: v for k, v in r.items() if k != "draw"}})
    if missing:
        raise SystemExit(f"missing draws: {missing}")
    fields = list(rows[0].keys())
    for r in rows:
        for k in r:
            if k not in fields:
                fields.append(k)
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    return len(rows)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", required=True)
    ap.add_argument("--out", default="../results")
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--merge", action="store_true")
    ap.add_argument("--check-mean", action="store_true")
    a = ap.parse_args()
    outdir = os.path.join(a.out, "stage3a_draws")
    os.makedirs(outdir, exist_ok=True)
    if a.check_mean:
        # the posterior-mean model through this path must reproduce Stage 1's records exactly
        ref = {r["case"]: r for r in csv.DictReader(open(os.path.join(a.out, "onset_results.csv")))}
        files = [f for f in case_files(a.series) if os.path.basename(f)[:-4] in ("two_E33223_tau30_G0.5", "two_E21495_tau30_G0.1")]
        worst = 0.0
        for row in run_draw((0, 0, 0, 0), files, bcrnn.Kinetics()):
            for k, v in row.items():
                if k in ("draw", "case", "history") or v is None or isinstance(v, str):
                    continue
                r = ref[row["case"]][f"{row['history']}_{k}"]
                worst = max(worst, abs(float(r) - float(v)) / max(abs(float(r)), 1e-30))
        print(json.dumps({"check": "mean model through stage3a.py against results/onset_results.csv",
                          "cases": [os.path.basename(f)[:-4] for f in files], "max_relative_difference": worst}))
        raise SystemExit(0 if worst < 1e-12 else 1)
    if a.merge:
        print("rows:", merge(outdir, os.path.join(a.out, "stage3a_onsets.csv")))
        raise SystemExit
    draws, _ = S.all_draws()
    t0 = time.time()
    with Pool(a.jobs, initializer=_init, initargs=(a.series,)) as pool:
        for i, (d, status, sec) in enumerate(pool.imap_unordered(_work, [(dr, outdir) for dr in draws], chunksize=1)):
            print(f"{i + 1:3d}/200 draw {d:3d} {status} {sec:6.1f} s  elapsed {time.time() - t0:7.0f} s", flush=True)
