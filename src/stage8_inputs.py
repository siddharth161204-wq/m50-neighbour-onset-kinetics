"""Stage 8 inputs, each read from its file or its source (DECISIONS.md D77, D80 and D82); nothing here is a model result.

- The trigger energies (D77 (1)): Stage 7's, one per test (results/stage7_triggers.json, D65), read and not recomputed.
- The ejected-to-body ratio (D77 (2)): for each of the Databank's ten M50 nail tests of D53 (the rows of
  inputs/databank/databank_m50_used.csv whose Trigger-Mechanism is "Nail"), the energy of the positive and the negative
  ejecta over the energy through the cell body, (Energy-Fraction-Positive-Ejecta-kJ + Energy-Fraction-Negative-Ejecta-kJ)
  / Energy-Fraction-Cell-Body-kJ, which is (Corrected-Total-Energy-Yield-kJ - Energy-Fraction-Cell-Body-kJ) /
  Energy-Fraction-Cell-Body-kJ to rounding; central the median of the ten, bracket the smallest and the largest.
- The ejected energy per test: E_e = r E_b (A1).
- The delivery (D77 (4)): a fraction f of E_e, from the start of the trigger's release (t = 0), over the median
  release, 21.39 s (D52), as a triangular pulse, the trigger's own shape (D38); 10 and 60 s, the brief's bracket,
  labelled conditional (no source gives the delivery's duration).
- The electrical path (D80): the cell's stored electrical energy of D68, 65.52 kJ, with the dissipated fractions 0.05
  and 0.2, the brief's bracket.
- The gas layer (D82): Hoelle, Zimmermann and Hinrichsen, J. Electrochem. Soc. 170 (2023) 060516: Eq. 28 and 29, a
  thermal resistance between the jelly roll and the can that is 0 below the boiling point of DMC, rises with the square
  of the interface temperature above it, and is R_max above the boiling point of EC; Table V, the boiling points (DMC
  91 C, EC 248 C); Table VI, the final parameter set, cell 2 (the first cell heated by the failed one): R_max 0.03077
  m2 K/W on the heated side and 0.00962 m2 K/W on the "cold" side; the text after Eq. 28: 0.03077 m2 K/W is a gas layer
  of 0.8 mm at 0.026 W/(m K).
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage6_inputs as IN6                       # noqa: E402  (unchanged)
import stage7_inputs as IN7                       # noqa: E402  (unchanged)

RES = os.path.join(HERE, "..", "results")
DATABANK_USED = os.path.join(HERE, "..", "inputs", "databank", "databank_m50_used.csv")
TRIGGERS = os.path.join(RES, "stage7_triggers.json")

LEVEL_PROP_C = IN7.LEVEL_PROP_C                  # 255.68 C (D35): C1 and C2
LEVEL_150_C = IN7.LEVEL_150_C                    # 150 C (D33 (2)): C3
CRITERIA = ("C1", "C2", "C3")
CRITERIA_TEXT = {"C1": "hot spot reaches 255.7 C", "C2": "lumped neighbour reaches 255.7 C",
                 "C3": "lumped neighbour reaches 150 C"}

# the search for the threshold fraction (D78)
COMMON_F = (0.1, 0.2, 0.3)                       # Part C's fractions, the first round for every test
PROBES_A = (0.1, 0.2, 0.3, 0.5, 1.0)             # the points tried before halving, in order, where inside the bracket
WIDTH = 0.02                                     # the bracket is halved until its width is at most this
F_MAX = 1.0

# the delivery (D77)
TAU_D_CONDITIONAL_S = (10.0, 60.0)               # the brief's bracket, labelled conditional
GEOMETRIES = ("half", "capend")                  # the facing half; the quarter of it nearest the cap (the bracket)
CAPEND_FROM = 0.75                               # the cap-end quarter: z >= 0.75 L, theta <= 90 degrees

# the electrical path (D80)
E_STORED_J = IN7.E_EVENT_J                       # 65,520 J (D68)
F_E = (0.05, 0.2)

# the gas layer (D82), Hoelle et al. (2023)
T_VAP_DMC_C = 91.0                               # Table V
T_VAP_EC_C = 248.0                               # Table V
R_MAX_HEATED = 0.03077                           # m2 K/W, Table VI, cell 2, heated side (= Eq. 28's value)
R_MAX_COLD = 0.00962                             # m2 K/W, Table VI, cell 2, "cold" side
D_VAP_MAX_M, LAMBDA_GAS = 0.8e-3, 0.026          # the text after Eq. 28 (0.8 mm at 0.026 W/(m K))
R_FLOOR = 1.0e-7                                 # m2 K/W: in place of 0 below 91 C, so the two copies stay coupled
N_BANDS = 64                                     # the interface temperature's bands between 91 and 248 C


def r_vap(T_IF_C, R_max):
    """Hoelle et al. (2023), Eq. 28 and 29: the gas layer's resistance (m2 K/W) at the interface temperature (C)."""
    if T_IF_C < T_VAP_DMC_C:
        return 0.0
    if T_IF_C > T_VAP_EC_C:
        return R_max
    return R_max / (T_VAP_EC_C - T_VAP_DMC_C) ** 2 * (T_IF_C - T_VAP_DMC_C) ** 2


def _median(v):
    v = sorted(v)
    n = len(v)
    return v[n // 2] if n % 2 else 0.5 * (v[n // 2 - 1] + v[n // 2])


def ratios(path=DATABANK_USED):
    """D77 (2): the ejected-to-body ratio of each of the ten D53 nail tests, with its row of the file (the header is
    row 1) and the columns read."""
    ids = IN6.energies()["test_ids"]
    rows = []
    with open(path) as fh:
        for k, r in enumerate(csv.DictReader(fh), start=2):
            if r["Test-ID"] not in ids:
                continue
            assert "Nail" in r["Trigger-Mechanism"]
            body = float(r["Energy-Fraction-Cell-Body-kJ"])
            pos = float(r["Energy-Fraction-Positive-Ejecta-kJ"])
            neg = float(r["Energy-Fraction-Negative-Ejecta-kJ"])
            total = float(r["Corrected-Total-Energy-Yield-kJ"])
            rows.append({"row": k, "test_id": r["Test-ID"], "body_kJ": body, "positive_ejecta_kJ": pos,
                         "negative_ejecta_kJ": neg, "total_kJ": total, "ratio": (pos + neg) / body,
                         "ratio_from_total": (total - body) / body,
                         "body_percent": float(r["Energy-Percent-Cell-Body-%"])})
    assert [r["test_id"] for r in rows] == ids and len(rows) == 10
    v = [r["ratio"] for r in rows]
    lo = min(rows, key=lambda r: r["ratio"])
    hi = max(rows, key=lambda r: r["ratio"])
    srt = sorted(rows, key=lambda r: r["ratio"])
    return {"rows": rows, "central": _median(v), "low": lo["ratio"], "high": hi["ratio"],
            "low_test": lo["test_id"], "high_test": hi["test_id"],
            "median_tests": [srt[4]["test_id"], srt[5]["test_id"]],
            "columns": ["Energy-Fraction-Positive-Ejecta-kJ", "Energy-Fraction-Negative-Ejecta-kJ",
                        "Energy-Fraction-Cell-Body-kJ"], "file": "inputs/databank/databank_m50_used.csv"}


def triggers(path=TRIGGERS):
    """Stage 7's trigger energies (D65), one per test, with the test's connection."""
    d = json.load(open(path))
    return {r["test"]: {"E_J": float(r["E_J"]), "connection": r["connection"], "target_C": float(r["target_C"])}
            for r in d["rows"]}


def tests():
    """The sixteen measured tests (D64), with their Stage 7 trigger energies."""
    tr = triggers()
    out = []
    for t in IN7.tests():
        assert tr[t["test"]]["connection"] == t["connection"]
        out.append(dict(t, E_b_J=tr[t["test"]]["E_J"]))
    return out


def ejected(r=None):
    """A1: E_e = r E_b per test, at the central ratio and at the bracket's two ends."""
    r = ratios() if r is None else r
    return {t["test"]: {"connection": t["connection"], "E_b_J": t["E_b_J"], "E_e_J": r["central"] * t["E_b_J"],
                        "E_e_low_J": r["low"] * t["E_b_J"], "E_e_high_J": r["high"] * t["E_b_J"]} for t in tests()}


def tau_median_s():
    return IN6.durations()["median_s"]


def sensitivity_tests():
    """A4: the three tests nearest the median trigger energy, and the two extremes."""
    ts = tests()
    e = sorted(t["E_b_J"] for t in ts)
    med = _median(e)
    near = sorted(ts, key=lambda t: (abs(t["E_b_J"] - med), t["test"]))[:3]
    lo = min(ts, key=lambda t: t["E_b_J"])
    hi = max(ts, key=lambda t: t["E_b_J"])
    return {"median_J": med, "nearest": [t["test"] for t in near], "extremes": [lo["test"], hi["test"]],
            "distances_J": {t["test"]: abs(t["E_b_J"] - med) for t in ts}}


def median_tests():
    """Part D: the three tests nearest the median trigger energy (as A4's)."""
    return sensitivity_tests()["nearest"]


if __name__ == "__main__":
    r = ratios()
    print(json.dumps({"ratio": {k: r[k] for k in ("central", "low", "high", "low_test", "high_test", "median_tests")},
                      "sensitivity": sensitivity_tests(), "tau_median_s": tau_median_s()}, indent=1))
