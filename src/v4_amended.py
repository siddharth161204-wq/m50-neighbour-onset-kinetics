#!/usr/bin/env python3
"""V4 as amended by DECISIONS.md D25, written after V4 failed under D23 (commit f9cabc7).

Nothing is rerun: the per-draw record of V4 (results/stage3_v4_arc_draws.csv) is read as committed.

D25 changes how the draws' band is compared with the paper's, not the draws, the emulation or the classes:
  (1) the statistic is the paper's own, the main-cluster mean plus and minus two standard deviations (its Fig. 7
      caption, p. 12, and p. 13), instead of the 2.5 and 97.5 percentiles of D23;
  (2) the band's edges are judged relative to the emulation's own T_in of the posterior-mean model (V1: 179.25 C),
      against the paper's edges relative to its mean (169.0 - 183.5 = -14.5 C and 198.0 - 183.5 = +14.5 C).
The mean criterion is unchanged and absolute: within 5 C of 183.5 C. The classes are D23's.

For transparency the script also evaluates every combination of the two changes, with D23's classes and with a
tighter main cluster (short times inside Tukey's far-out fence, Q3 + 3 IQR, of all shorts by 8500 min), so a reader
can see how the verdict depends on each choice. Only the D25 row is the amended acceptance.

Usage: python3 v4_amended.py --out ../results
"""
import argparse, csv, json, os
import numpy as np

PAPER_MEAN, PAPER_BAND, TOL = 183.5, (169.0, 198.0), 5.0


def load(path):
    rows = list(csv.DictReader(open(path)))
    num = lambda v: None if v in ("", "None") else float(v)
    for r in rows:
        for k in ("T_in_C", "t_in_min", "T_on_C", "t_on_min"):
            r[k] = num(r[k])
    return rows


def judge(T, statistic, reference, T_mean_model):
    m, s = float(T.mean()), float(T.std(ddof=1))
    if statistic == "mean_pm_2sd":
        lo, hi = m - 2 * s, m + 2 * s
    else:
        lo, hi = (float(x) for x in np.percentile(T, [2.5, 97.5]))
    if reference == "absolute":
        off_lo, off_hi = lo - PAPER_BAND[0], hi - PAPER_BAND[1]
    else:                                   # relative to the emulation's mean-model T_in, against the paper's +-14.5 C
        off_lo = (lo - T_mean_model) - (PAPER_BAND[0] - PAPER_MEAN)
        off_hi = (hi - T_mean_model) - (PAPER_BAND[1] - PAPER_MEAN)
    off_mean = m - PAPER_MEAN
    ok = abs(off_lo) <= TOL and abs(off_hi) <= TOL and abs(off_mean) <= TOL
    return {"n": int(T.size), "mean_C": m, "sd_C": s, "lower_edge_C": lo, "upper_edge_C": hi,
            "lower_edge_offset_C": off_lo, "upper_edge_offset_C": off_hi, "mean_offset_C": off_mean, "pass": bool(ok)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="../results")
    a = ap.parse_args()
    rows = load(os.path.join(a.out, "stage3_v4_arc_draws.csv"))
    v4 = json.load(open(os.path.join(a.out, "stage3_v4.json")))
    T_mm = v4["mean_model"]["T_in_C"]
    main = [r for r in rows if r["class"] == "main_cluster"]
    T_main = np.array([r["T_in_C"] for r in main])
    shorts = np.array([r["t_on_min"] for r in rows if r["class"] in ("main_cluster", "delayed_short")])
    q1, q3 = np.percentile(shorts, [25, 75])
    fence = float(q3 + 3 * (q3 - q1))
    tight = np.array([r["t_on_min"] <= fence for r in main])
    out = {"amendment": "DECISIONS.md D25, written after V4 failed under D23 (f9cabc7); post hoc",
           "emulation_mean_model_T_in_C": T_mm, "paper": {"mean_C": PAPER_MEAN, "band_C": list(PAPER_BAND),
                                                          "band_relative_to_mean_C": [PAPER_BAND[0] - PAPER_MEAN, PAPER_BAND[1] - PAPER_MEAN]},
           "tolerance_C": TOL,
           "D25": judge(T_main, "mean_pm_2sd", "relative", T_mm),
           "D23_as_registered": judge(T_main, "percentiles", "absolute", T_mm),
           "variants": [], "tight_cluster": {"rule": "short time at or below Q3 + 3 IQR of all shorts by 8500 min",
                                             "Q1_min": float(q1), "Q3_min": float(q3), "fence_min": fence,
                                             "draws_moved_out": [int(r["draw"]) for r in main if r["t_on_min"] > fence]}}
    for cname, sel in (("D23 classes (main cluster: short by 4000 min)", np.ones(len(main), bool)),
                       ("tighter cluster (Tukey far-out fence)", tight)):
        for statistic in ("percentiles_2.5_97.5", "mean_pm_2sd"):
            for reference in ("absolute", "relative_to_emulation_mean_model"):
                v = judge(T_main[sel], statistic, reference, T_mm)
                v.update({"cluster": cname, "statistic": statistic, "edges": reference})
                out["variants"].append(v)
    json.dump(out, open(os.path.join(a.out, "stage3_v4_amended.json"), "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("D25", "D23_as_registered", "tight_cluster")}, indent=1))
    for v in out["variants"]:
        print(f"{v['cluster'][:22]:22s} {v['statistic']:20s} {v['edges'][:8]:8s} n={v['n']:3d} "
              f"edges {v['lower_edge_C']:6.1f} {v['upper_edge_C']:6.1f} offsets {v['lower_edge_offset_C']:+6.1f} "
              f"{v['upper_edge_offset_C']:+6.1f} mean {v['mean_offset_C']:+5.1f} {'PASS' if v['pass'] else 'fail'}")
