"""Stage 14, check V5 (DECISIONS D156): Part B recomputed by separate code.

Imports nothing of the study's. Reads results/stage14_bounds.csv and results/stage14_needs.csv, decides
every B1 verdict again with its own reading of D154 (1), recounts B2's sums, and compares with
results/stage14_tests.csv and results/stage14_partb.json. Writes results/stage14_v5.json.
"""
import csv
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(name):
    with open(os.path.join(ROOT, "results", name), newline="") as fh:
        return list(csv.DictReader(fh))


def main():
    ub = {}
    det = {}
    for r in load("stage14_bounds.csv"):
        w = r["window_s"]
        det[r["path"]] = r["determinable"]
        if r["upper_J"] != "":
            ub[(r["path"], w if w == "total" else "%.2f" % float(w))] = float(r["upper_J"])
    cols = [("21.39", "need_21s_lo_J", "need_21s_hi_J"), ("120.00", "need_120s_lo_J", "need_120s_hi_J"),
            ("240.00", "need_240s_lo_J", "need_240s_hi_J"), ("360.00", "need_360s_lo_J", "need_360s_hi_J")]
    mine = {}
    for t in load("stage14_needs.csv"):
        for w, cl, ch in cols:
            if t[ch].strip() == "":
                continue
            lo, hi = float(t[cl]), float(t[ch])
            for p in ("A1", "A2", "A3", "A4", "A5", "A6"):
                if det[p] == "no":
                    v = "not determinable"
                elif p == "A6" and t["connection"] == "series":
                    v = "does not act (series)"
                else:
                    u = ub[(p, w)]
                    v = "needs nothing" if hi == 0 else ("reaches" if u >= hi else ("reaches part" if u >= lo else "does not reach"))
                mine[(t["test"], w, p)] = v
    theirs = {(r["test"], "%.2f" % float(r["window_s"]), r["path"]): r["verdict"] for r in load("stage14_tests.csv")}
    diffs = [dict(key=list(k), v5=mine.get(k), study=theirs.get(k)) for k in set(mine) | set(theirs) if mine.get(k) != theirs.get(k)]

    # B2's sums at 21.39 s and whether any test needs more than every determinable bound together
    pb = json.load(open(os.path.join(ROOT, "results", "stage14_partb.json")))
    s_ser = sum(ub[(p, "21.39")] for p in ("A1", "A2", "A3", "A4") if det[p] == "yes")
    s_par = s_ser + ub[("A6", "21.39")]
    sums_ok = (abs(s_ser - pb["B2"]["sums_of_determinable_bounds"]["21.39"]["sum_series_J"]) <= 1e-6 * s_ser
               and abs(s_par - pb["B2"]["sums_of_determinable_bounds"]["21.39"]["sum_parallel_J"]) <= 1e-6 * s_par)
    out = dict(verdicts_compared=len(mine), differences=diffs, all_identical=not diffs and len(mine) == len(theirs),
               sums_21s=dict(series_J=s_ser, parallel_J=s_par, agree=sums_ok))
    with open(os.path.join(ROOT, "results", "stage14_v5.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "differences"}, indent=1), len(diffs), "differences")


if __name__ == "__main__":
    main()
