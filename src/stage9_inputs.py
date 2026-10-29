"""Stage 9 inputs (DECISIONS.md D90 to D96): every physical input is Stage 8's, read and not recomputed; this file
holds the rules' constants and the choices of tests, each checked against the data it rests on.

- The tests, their trigger energies E_b and ejected energies E_e (D77 (1) to (3)): `stage8_inputs`, unchanged.
- f* (D78): Stage 8's thresholds, read from `results/stage8_thresholds.csv` (the columns fC1, fC1_lo, fC1_hi, fC2,
  fC2_lo, fC2_hi): the Part A bracket (lo, hi], or 0 where the criterion is met at f = 0.
- A1 (D91): the induction curve's fractions are f*_hi plus 0, 0.0125, 0.025, 0.05, 0.1 and 0.2 (the brief).
- A2 (D91): the bisection ends when its bracket is at most 0.005 wide or a crossing lies within 10 s of the measured
  time (the brief). A3 (D92): at most 0.005 or a peak within 5 K (the brief).
- Part B (D93): constant power over 120, 240 and 360 s (the brief's bracket, conditional).
- The tests the predictions name (D90 (2), the author's answers of 29 October): P6 on the three propagated tests whose
  hot spot does not reach 255.7 C at f = 0 (M50_PT_Exp4, M50_PP_Exp2, M50_ST_Exp3), the only ones where f_t(C1) can
  exist; P8 and C3's aged SEI on the three propagated tests nearest the median trigger energy (M50_PP_Exp4,
  M50_SP_Exp1, M50_SP_Exp2).
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import stage8_inputs as IN8                       # noqa: E402  (unchanged)
import stage8_search as SR8                       # noqa: E402  (unchanged)

RES = os.path.join(HERE, "..", "results")
THRESHOLDS8 = os.path.join(RES, "stage8_thresholds.csv")

LEVEL_PROP_C = IN8.LEVEL_PROP_C                  # 255.68 C (D35): C1 and C2
CRITERIA = ("C1", "C2")

# A1 and A2 (D91)
GRID_STEPS = (0.0, 0.0125, 0.025, 0.05, 0.1, 0.2)
T_TOL_S = 10.0                                   # the bisection's tolerance on the crossing time
WIDTH_T = 0.005                                  # and on its bracket
# A3 (D92)
PEAK_TOL_K = 5.0
WIDTH_M = 0.005
F_MAX = 1.0                                      # the exploratory search's end, and the extension's (D92 (4))
# Part B (D93)
TAUS_B = (120.0, 240.0, 360.0)
PROBES_FSTAR = IN8.PROBES_A                      # D78's search for f* under a new delivery or the aged SEI
WIDTH_FSTAR = IN8.WIDTH
# the predictions (predictions_stage9.md)
P1_TOL_S = 30.0
P2_TOL_S, P2_ABOVE, P2_MIN = 30.0, 0.1, 6
P3_ABOVE = 0.02
P6_TAU_S, P6_F = 240.0, 0.2
P8_D = 0.01
P7_FACTORS = (0.75, 1.40)                        # as the prediction states them, to two decimals

REGISTERED_FMAX = ("M50_PT_Exp1", "M50_PT_Exp3", "M50_PP_Exp3", "M50_ST_Exp1", "M50_ST_Exp2")   # maxima 71 to 133 C
EXPLORATORY_FMAX = ("M50_PT_Exp2", "M50_SP_Exp4")                                            # 808 and 626 C (D89 (5))
P6_TESTS = ("M50_PT_Exp4", "M50_PP_Exp2", "M50_ST_Exp3")
P8_TESTS = ("M50_PP_Exp4", "M50_SP_Exp1", "M50_SP_Exp2")
V2_TESTS = {"M50_PT_Exp4": "A2", "M50_ST_Exp3": "A2", "M50_PT_Exp1": "A3"}                      # D95 (2)
V3_CASE = {"test": "M50_PP_Exp3", "tau_s": 240.0, "criterion": "C1"}                         # D95 (3)
XCHECK = ("c1_M50_PT_Exp4_f0.012500000", "first_M50_PT_Exp1_f0.100000000", "c2_M50_PP_Exp2_f0.037500000")


def key(f):
    return SR8.key(f)


def tests():
    return IN8.tests()


def by_test():
    return {t["test"]: t for t in tests()}


def ratios():
    return IN8.ratios()


def ejected():
    return IN8.ejected()


def tau_median_s():
    return IN8.tau_median_s()


def propagated():
    return [t["test"] for t in tests() if t["propagated"]]


def not_propagated():
    return [t["test"] for t in tests() if not t["propagated"]]


def _fs(text, lo, hi):
    text = text.strip()
    if text == "0":
        return {"status": "zero", "lo": 0.0, "hi": 0.0}
    if text.startswith("above"):
        return {"status": "above", "lo": float(lo), "hi": None}
    return {"status": "bracket", "lo": key(float(lo)), "hi": key(float(hi))}


def stage8_fstar(path=THRESHOLDS8):
    """Stage 8's f*(C1) and f*(C2) for each test, Part A's bracket (D78), from the thresholds file."""
    out = {}
    with open(path) as fh:
        for r in csv.DictReader(fh):
            out[r["test"]] = {"C1": _fs(r["fC1"], r["fC1_lo"], r["fC1_hi"]),
                              "C2": _fs(r["fC2"], r["fC2_lo"], r["fC2_hi"])}
    return out


def grid(f_hi):
    """A1: the induction curve's fractions above f*_hi, in order (D91 (1))."""
    return [key(f_hi + d) for d in GRID_STEPS]


def median_propagated():
    """The three propagated tests nearest the median trigger energy of the nine (D90 (2)); also the three nearest the
    median of the sixteen."""
    ts = [t for t in tests() if t["propagated"]]
    e = sorted(t["E_b_J"] for t in ts)
    med = IN8._median(e)
    return [t["test"] for t in sorted(ts, key=lambda t: (abs(t["E_b_J"] - med), t["test"]))[:3]], med


def check_choices(stage7_zero):
    """The named tests against the data they rest on (src/test_stage9.py runs it on the real files)."""
    bt = by_test()
    lows = [t for t in not_propagated() if bt[t]["neighbour_max_C"] < IN8.LEVEL_150_C]
    highs = [t for t in not_propagated() if bt[t]["neighbour_max_C"] >= IN8.LEVEL_150_C]
    assert sorted(lows) == sorted(REGISTERED_FMAX) and sorted(highs) == sorted(EXPLORATORY_FMAX)
    p6 = [t for t in propagated() if not stage7_zero[t]["C1"]]
    assert sorted(p6) == sorted(P6_TESTS), p6
    p8, _ = median_propagated()
    assert sorted(p8) == sorted(P8_TESTS), p8
    return True
