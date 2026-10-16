#!/usr/bin/env python3
"""Stage 4 (version 1.1.0): which submodel of the kinetic posterior sets the onset lead (DECISIONS.md D29;
predictions_v11.md).

The posterior of Koenig, Zhao and Deng (2025) has three submodels, one per supplementary file: the anode-electrolyte
network (An_Ele.csv, which holds the SEI decomposition together with six other reactions), the NCM811 cathode
(NCM811.csv, three reactions) and the separator (Separator.csv, melting). Stage 3 (D22) took one particle from each
file for every draw, with independent column indices. Here one submodel is varied at a time: for each of the 200
Stage 3 draws, the kinetics take that draw's particle of the varied file and the posterior-mean rows of the other two
(inputs/kinetics/bcrnn_mean_model.json, the rows Stage 1 used, D3), and are integrated passively along the archived
hottest-node and lumped histories of two cases (33.2 kJ, 30 s release, 500 and 100 mW/K) with the Stage 1 driver,
its numerics unchanged (D26 (1)). Nothing is refitted, scaled, trimmed, reweighted or dropped.

Each grouped draw's records go to results/v11_runs/<group>_draw_NNN.json as soon as it is done, so a stopped run
resumes where it stopped; `merge` then writes results/v11_onsets.csv (one row per group, draw, case and history).

Usage:
  python3 v11_sensitivity.py --series <clone>/results/resolved_series --out ../results check
  python3 v11_sensitivity.py --series <clone>/results/resolved_series --out ../results run [--jobs 2]
  python3 v11_sensitivity.py --series <clone>/results/resolved_series --out ../results merge

`check` (brief, Stage 4 step 1) writes results/v11_checks.json:
  1. the three particle files match the SHA-256 recorded in inputs/kinetics/SOURCE.md;
  2. every draw's rows, loaded file by file, rebuild results/stage3_kinetic_draw_parameters.csv byte for byte (its
     SHA-256 is in results/stage3_draws.json);
  3. for every draw and submodel, the grouped model equals the joint draw's model on the varied file's block of
     reactions and species and the posterior-mean model everywhere else, exactly;
  4. the posterior-mean model built through this path reproduces Stage 1 (results/onset_results.csv) on both cases;
  5. the five V5 draws (D26 (6)) built jointly through this path reproduce Stage 3a (results/stage3a_onsets.csv).
"""
import argparse, csv, hashlib, io, json, os, time
from multiprocessing import Pool
import numpy as np
import bcrnn
import onset_kinetics as OK
import stage3_draws as S
import stage3a as A

CASES = ("two_E33223_tau30_G0.5", "two_E33223_tau30_G0.1")
HISTS = ("hottest_node", "lumped")
GROUPS = {"an_ele": "An_Ele.csv", "ncm811": "NCM811.csv", "separator": "Separator.csv"}
RUNDIR = "v11_runs"
V5_DRAWS = (179, 178, 73, 44, 53)          # results/stage3a_v5.json, chosen by D26 (6)
SOURCE_SHA256 = {"An_Ele.csv": "116ba9222f9841d6f1260960f74fcc50a4ac0aa8f73cd2bb8edf9d2cff4e57bd",
                 "NCM811.csv": "6edcf2579afc61eeb06f2d85b32708974aeeea37a0ff8f38bc8f492d77f88c5e",
                 "Separator.csv": "b6db19b96a720849df9109f583effde6927dfb603d5e826f122f43fe3681be93"}
# which reactions (columns of the model arrays) and species (rows) each file's rows set in bcrnn.rows_to_model
BLOCKS = {"An_Ele.csv": (list(range(0, 7)), list(range(0, 9))),
          "NCM811.csv": (list(range(7, 10)), list(range(9, 12))),
          "Separator.csv": ([10], [12])}


def mean_rows():
    """The posterior-mean rows of each file, as recorded (D3) and as Stage 1 used them."""
    rec = json.load(open(bcrnn.MODEL_JSON))
    return {"An_Ele.csv": np.array(rec["an_ele_rows_mean"], float), "NCM811.csv": np.array(rec["ncm811_rows_mean"], float),
            "Separator.csv": np.array(rec["separator_rows_mean"], float)}


def columns(ae, sep, cat):
    return {"An_Ele.csv": ae, "NCM811.csv": cat, "Separator.csv": sep}


def rows_for(P, M, group, ae, sep, cat):
    """The 220, 17 and 6 rows of a run. group: a submodel (its particle from the draw, the other two at the posterior
    mean), 'joint' (all three from the draw, as Stage 3a) or 'mean' (all three at the posterior mean, as Stage 1)."""
    col = columns(ae, sep, cat)
    out = {}
    for f in ("An_Ele.csv", "NCM811.csv", "Separator.csv"):
        varied = group == "joint" or (group in GROUPS and GROUPS[group] == f)
        out[f] = P[f][:, col[f] - 1] if varied else M[f]
    return out["An_Ele.csv"], out["NCM811.csv"], out["Separator.csv"]


def kinetics_for(P, M, group, ae, sep, cat):
    return bcrnn.Kinetics(model=bcrnn.rows_to_model(*rows_for(P, M, group, ae, sep, cat)))


def case_paths(series):
    paths = [os.path.join(series, c + ".npz") for c in CASES]
    assert all(os.path.exists(p) for p in paths), paths
    return paths


def run_one(kin, paths, draw):
    """Both cases along the hottest-node and lumped histories, with the Stage 1 driver (D26 (1))."""
    OK.KIN = kin
    rows = []
    for p in paths:
        rows += A.per_history_rows(OK.run_case(p, histories=HISTS), draw)
    return rows


# ------------------------------------------------------------------ checks (step 1)

def _sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def check_parameter_file(P, draws, out):
    """Rebuild results/stage3_kinetic_draw_parameters.csv from rows loaded file by file, as stage3_draws.py writes it."""
    buf = io.StringIO(newline="")
    w = csv.writer(buf)
    w.writerow(["draw"] + [f"an_ele_row_{i + 1}" for i in range(220)] + [f"ncm811_row_{i + 1}" for i in range(17)]
               + [f"separator_row_{i + 1}" for i in range(6)])
    for d, ae, sep, cat in draws:
        ra = P["An_Ele.csv"][:, ae - 1]          # each file on its own
        rc = P["NCM811.csv"][:, cat - 1]
        rs = P["Separator.csv"][:, sep - 1]
        w.writerow([d] + [repr(float(x)) for x in np.concatenate([ra, rc, rs])])
    sha = hashlib.sha256(buf.getvalue().encode()).hexdigest()
    rec = json.load(open(os.path.join(out, "stage3_draws.json")))["parameter_vectors_sha256"]
    return {"rebuilt_sha256": sha, "recorded_sha256": rec, "pass": sha == rec}


def check_blocks(P, M, draws):
    """Grouped model = joint model on the varied file's block, mean model elsewhere; exact equality."""
    mean_m = bcrnn.rows_to_model(M["An_Ele.csv"], M["NCM811.csv"], M["Separator.csv"])
    n_bad, n = 0, 0
    for d, ae, sep, cat in draws:
        joint_m = bcrnn.rows_to_model(*rows_for(P, M, "joint", ae, sep, cat))
        for g, f in GROUPS.items():
            gm = bcrnn.rows_to_model(*rows_for(P, M, g, ae, sep, cat))
            rx, sp = BLOCKS[f]
            rmask = np.zeros(bcrnn.NR, bool); rmask[rx] = True
            smask = np.zeros(bcrnn.NS, bool); smask[sp] = True
            for k in ("lnA", "Ea", "b", "dH"):
                expect = np.where(rmask, joint_m[k], mean_m[k])
                n += 1; n_bad += int(not np.array_equal(gm[k], expect))
            for k in ("order", "stoich"):
                blk = smask[:, None] & rmask[None, :]
                expect = np.where(blk, joint_m[k], mean_m[k])
                n += 1; n_bad += int(not np.array_equal(gm[k], expect))
    return {"arrays_compared": n, "arrays_differing": n_bad, "pass": n_bad == 0}


def compare_rows(rows, ref_lookup):
    """Largest relative difference over the numeric fields, and the number of text fields that differ."""
    worst, text_diff, n = 0.0, 0, 0
    for row in rows:
        ref = ref_lookup(row)
        for k, v in row.items():
            if k in ("draw", "case", "history"):
                continue
            r = ref[k]
            if v is None or isinstance(v, str) or r in ("", "None"):
                n += 1
                text_diff += int(str(v) != str(r) and not (v is None and r in ("", "None")))
                continue
            n += 1
            worst = max(worst, abs(float(r) - float(v)) / max(abs(float(r)), 1e-30))
    return worst, text_diff, n


def run_checks(series, out):
    P, M = S.load_particles(), mean_rows()
    draws, _ = S.all_draws(P)
    res = {"source_files": {f: {"sha256": _sha(os.path.join(S.SUPP, f)), "recorded": SOURCE_SHA256[f],
                                "pass": _sha(os.path.join(S.SUPP, f)) == SOURCE_SHA256[f]} for f in SOURCE_SHA256}}
    res["parameters_loaded_file_by_file"] = check_parameter_file(P, draws, out)
    res["grouped_model_blocks"] = check_blocks(P, M, draws)
    paths = case_paths(series)
    s1 = {r["case"]: r for r in csv.DictReader(open(os.path.join(out, "onset_results.csv")))}
    t0 = time.time()
    rows = run_one(bcrnn.Kinetics(model=bcrnn.rows_to_model(*rows_for(P, M, "mean", 0, 0, 0))), paths, 0)
    worst, td, n = compare_rows(rows, lambda r: {k[len(r["history"]) + 1:]: v for k, v in s1[r["case"]].items()
                                                 if k.startswith(r["history"] + "_")})
    res["mean_model_against_stage1"] = {"cases": list(CASES), "histories": list(HISTS), "fields_compared": n,
                                        "max_relative_difference": worst, "text_fields_differing": td,
                                        "pass": worst < 1e-12 and td == 0, "seconds": round(time.time() - t0, 1)}
    s3 = {}
    for r in csv.DictReader(open(os.path.join(out, "stage3a_onsets.csv"))):
        if r["case"] in CASES and r["history"] in HISTS and int(r["draw"]) in V5_DRAWS:
            s3[(int(r["draw"]), r["case"], r["history"])] = r
    t0 = time.time()
    worst_all, td_all, n_all = 0.0, 0, 0
    for d, ae, sep, cat in draws:
        if d not in V5_DRAWS:
            continue
        rows = run_one(kinetics_for(P, M, "joint", ae, sep, cat), paths, d)
        w_, t_, n_ = compare_rows(rows, lambda r: s3[(r["draw"], r["case"], r["history"])])
        worst_all, td_all, n_all = max(worst_all, w_), td_all + t_, n_all + n_
    res["joint_draws_against_stage3a"] = {"draws": list(V5_DRAWS), "cases": list(CASES), "histories": list(HISTS),
                                          "fields_compared": n_all, "max_relative_difference": worst_all,
                                          "text_fields_differing": td_all, "pass": worst_all < 1e-12 and td_all == 0,
                                          "seconds": round(time.time() - t0, 1)}
    res["pass"] = all(v["pass"] for k, v in res.items() if isinstance(v, dict) and "pass" in v) and \
        all(v["pass"] for v in res["source_files"].values())
    json.dump(res, open(os.path.join(out, "v11_checks.json"), "w"), indent=1)
    return res


# ------------------------------------------------------------------ grouped runs

_P, _M, _SERIES = None, None, None


def _init(series):
    global _P, _M, _SERIES
    _P, _M, _SERIES = S.load_particles(), mean_rows(), series


def _work(args):
    group, draw_tuple, outdir = args
    d, ae, sep, cat = draw_tuple
    path = os.path.join(outdir, f"{group}_draw_{d:03d}.json")
    if os.path.exists(path):
        return group, d, "kept", 0.0
    t0 = time.time()
    rows = run_one(kinetics_for(_P, _M, group, ae, sep, cat), case_paths(_SERIES), d)
    rec = {"group": group, "varied_file": GROUPS[group], "draw": d, "varied_column": columns(ae, sep, cat)[GROUPS[group]],
           "an_ele_column": ae, "separator_column": sep, "ncm811_column": cat, "rows": rows, "seconds": time.time() - t0}
    tmp = path + ".tmp"
    json.dump(rec, open(tmp, "w"))
    os.replace(tmp, path)
    return group, d, "done", rec["seconds"]


def merge(outdir, out_csv, n=S.N_DRAWS):
    rows, missing = [], []
    for g in GROUPS:
        for d in range(1, n + 1):
            p = os.path.join(outdir, f"{g}_draw_{d:03d}.json")
            if not os.path.exists(p):
                missing.append((g, d))
                continue
            rec = json.load(open(p))
            for r in rec["rows"]:
                rows.append({"group": g, "varied_file": rec["varied_file"], "draw": d, "varied_column": rec["varied_column"],
                             "an_ele_column": rec["an_ele_column"], "separator_column": rec["separator_column"],
                             "ncm811_column": rec["ncm811_column"], **{k: v for k, v in r.items() if k != "draw"}})
    if missing:
        raise SystemExit(f"missing grouped draws: {missing[:10]} ... ({len(missing)} in all)")
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
    ap.add_argument("step", choices=("check", "run", "merge"))
    a = ap.parse_args()
    outdir = os.path.join(a.out, RUNDIR)
    if a.step == "check":
        res = run_checks(a.series, a.out)
        print(json.dumps(res, indent=1))
        raise SystemExit(0 if res["pass"] else 1)
    if a.step == "merge":
        print("rows:", merge(outdir, os.path.join(a.out, "v11_onsets.csv")))
        raise SystemExit
    os.makedirs(outdir, exist_ok=True)
    draws, _ = S.all_draws()
    tasks = [(g, dr, outdir) for g in GROUPS for dr in draws]
    t0 = time.time()
    with Pool(a.jobs, initializer=_init, initargs=(a.series,), maxtasksperchild=50) as pool:
        for i, (g, d, status, sec) in enumerate(pool.imap_unordered(_work, tasks, chunksize=1)):
            print(f"{i + 1:3d}/{len(tasks)} {g:9s} draw {d:3d} {status} {sec:6.1f} s  elapsed {time.time() - t0:7.0f} s", flush=True)
