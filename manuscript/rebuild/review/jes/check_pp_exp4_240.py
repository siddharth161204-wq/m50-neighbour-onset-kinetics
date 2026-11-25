"""Brief 32, item 5: PP-Exp4's constant-power search over 240 s, the cross-section's need against the
three-dimensional bracket's midpoint, unrounded from the results file and from the values as Table 3 prints them.

Usage: python3 manuscript/rebuild/review/jes/check_pp_exp4_240.py
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
S16 = os.path.join(ROOT, "results", "stage16_scorecard.json")

x = next(r for r in json.load(open(S16))["X"]
         if r["test"] == "M50_PP_Exp4" and r["delivery"] == "240 s constant power")
xs, lo, hi, mid = x["xs_E_by_t_J"], x["lo_by_t_J"], x["hi_by_t_J"], x["mid_by_t_J"]
print("results/stage16_scorecard.json, X, M50_PP_Exp4, 240 s constant power")
print("  cross-section's need, counted to its own runaway: %.4f J" % xs)
print("  three-dimensional bracket, counted to 10 s after the measured time: (%.4f, %.4f] J, midpoint %.4f J" % (lo, hi, mid))
print("  difference, unrounded: %.6f %% (the scorecard's d = %.10f)" % (100.0 * (xs - mid) / mid, x["d"]))
plo, phi, pxs = round(lo / 1000.0, 2), round(hi / 1000.0, 2), round(xs / 1000.0, 2)
pmid = (plo + phi) / 2.0
print("  from the values as Table 3 prints them, (%.2f, %.2f] and %.2f kJ: %.4f %%" % (plo, phi, pxs, 100.0 * (pxs - pmid) / pmid))
print("  above 10 %%: %s" % ((xs - mid) / mid > 0.10))
