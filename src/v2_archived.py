#!/usr/bin/env python3
"""V2 repeated after Stage 1 on the archived headline cases (DECISIONS.md D10): 33.2 kJ, 500 mW/K, 10 and 30 s.
Tolerances, the largest step and the evaluation grid are halved; acceptance: no onset time moves by more than 1 %.
Usage: python3 v2_archived.py --series <clone>/results/resolved_series --out ../results
"""
import argparse, json, os
import onset_kinetics as OK

ap = argparse.ArgumentParser()
ap.add_argument("--series", default="../external/m50-two-cell-pilot/results/resolved_series")
ap.add_argument("--out", default="../results")
a = ap.parse_args()
half = dict(rtol=OK.RTOL / 2, atol=OK.ATOL / 2, max_step=OK.MAX_STEP / 2, grid=OK.GRID / 2)
out, worst = {}, 0.0
for case in ("two_E33223_tau10_G0.5", "two_E33223_tau30_G0.5"):
    p = os.path.join(a.series, case + ".npz")
    b, h = OK.run_case(p), OK.run_case(p, **half)
    rec = {}
    for k, v in b.items():
        if "_t_" in k and k.endswith("Kpm_s") and v is not None:
            rc = abs(h[k] - v) / v
            rec[k] = {"base_s": v, "halved_s": h[k], "rel_change": rc}
            worst = max(worst, rc)
    out[case] = rec
out["max_relative_change"] = worst
out["pass"] = worst < 0.01
json.dump(out, open(os.path.join(a.out, "v2_archived.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
