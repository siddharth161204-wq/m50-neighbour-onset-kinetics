#!/usr/bin/env python3
"""Stage 12's inputs (brief of 3 November; predictions_stage12.md; DECISIONS.md D122 and D123), each read from its
file and checked against the values D122 records.

  - The cap: the largest body energy of the ten LG M50 nail tests of D53 (rows 9 to 18 of
    inputs/databank/databank_m50_used.csv, the header being row 1), RUN195's on row 15, as Stages 5 and 6 used it,
    33,222.9 J (D38, D53, D122 (1)).
  - The fixed ejected energy: the median of the ten tests' ejected energies (positive plus negative ejecta), 76,741.25 J
    (D122 (2)).
  - Part A's eight tests (the hot spot met at f = 0 with the fitted trigger, Stage 7) and their two points per contact
    (D122 (6)); Part B's four Stage 11 tests and the nine propagated tests (D122 (4), (5)).
"""
import csv, json, os, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
import stage9_run as R9                  # noqa: E402  (unchanged)

DATABANK = os.path.join(ROOT, "inputs", "databank", "databank_m50_used.csv")
NAIL_ROWS = tuple(range(9, 19))
E_CAP_J = 33222.9                        # D122 (1)
E_FIX_J = 76741.25365663527              # D122 (2)
H_A = ("central", "high")                # Part A: the central contact (A1) and the high one (A2)
B1_TESTS = ("M50_PT_Exp1", "M50_PP_Exp3", "M50_ST_Exp2", "M50_SP_Exp3")
WIDTH_B1 = 0.02                          # B1: the bracket's width, as a fraction of the fixed ejected energy
WIDTH_B2 = 0.005                         # B2: likewise (Stage 9's 0.005, now of the fixed energy)
T_TOL_S = 10.0                           # B2: a run within 10 s of the measured time ends the search (Stage 9)
T_END_S = 900.0
STAGE6_IDS = {"series": "body_mean_series_hcentral_gcentral_tau21.39_E33.22",
              "parallel": "body_mean_parallel_hcentral_gcentral_tau21.39_E33.22"}


def databank_rows():
    """{row number in the file (the header is row 1): row}."""
    with open(DATABANK) as fh:
        return {i: r for i, r in enumerate(csv.DictReader(fh), start=2)}


def ejected_J(row):
    return (float(row["Energy-Fraction-Positive-Ejecta-kJ"]) + float(row["Energy-Fraction-Negative-Ejecta-kJ"])) * 1e3


def cap_row():
    rows = databank_rows()
    i = max(NAIL_ROWS, key=lambda k: float(rows[k]["Energy-Fraction-Cell-Body-kJ"]))
    return i, rows[i]["Test-ID"], float(rows[i]["Energy-Fraction-Cell-Body-kJ"]) * 1e3


def fixed_ejecta():
    rows = databank_rows()
    e = sorted(ejected_J(rows[i]) for i in NAIL_ROWS)
    return statistics.median(e), e


def check():
    rows = databank_rows()
    assert all(rows[k]["Trigger-Mechanism"] == "Nail" for k in NAIL_ROWS)
    i, tid, cap = cap_row()
    assert i == 15 and tid == "SPR2021_ESTA_8B100-01_SOC_RUN195", (i, tid)
    assert round(cap, 1) == E_CAP_J, cap
    med, _ = fixed_ejecta()
    assert abs(med - E_FIX_J) < 1e-6, med
    return True


def a_tests():
    """The eight tests whose hot spot reaches 255.7 C at f = 0 with the fitted trigger (Stage 7, central contact), in
    order of their fitted body energy."""
    p7 = json.load(open(os.path.join(ROOT, "results", "stage7_paper_numbers.json")))
    ts = p7["part_b"]["C1"]["central"]["predicted_tests"]
    bt = R9.by_test()
    return sorted(ts, key=lambda t: bt[t]["E_b_J"])


def a_points():
    """{(connection, contact): [tests]}: with the trigger capped and no delivery a run depends on the test only through
    its connection (D122 (6)), so the eight tests fall on two points per contact."""
    bt = R9.by_test()
    out = {}
    for h in H_A:
        for t in a_tests():
            out.setdefault((bt[t]["connection"], h), []).append(t)
    return out


def e_e(test):
    """Stage 8's ejected energy of a test, r E_b (the central ratio)."""
    return float(R9.ratios()["central"] * R9.by_test()[test]["E_b_J"])


def b2_tests():
    return [t["test"] for t in R9.tests() if t["propagated"]]


def stage9_a2(test):
    st = json.load(open(os.path.join(ROOT, "results", "stage9_states.json")))
    return st[f"A2_C2_{test}"]


def fmax_registered():
    """{test: (f_max, its energy in J)} of the registered non-propagated tests (Stage 9, A3), the two exploratory
    maxima apart."""
    out = {}
    with open(os.path.join(ROOT, "results", "stage9_fractions.csv")) as fh:
        for r in csv.DictReader(fh):
            if r["propagated"] == "True" or r["fmax_exploratory"] == "True":
                continue
            out[r["test"]] = (float(r["fmax"]), float(r["fmax_E_J"]))
    return out


if __name__ == "__main__":
    check()
    print(json.dumps({"cap": cap_row(), "fixed_ejecta_J": fixed_ejecta()[0], "a_points": {f"{k[0]}_{k[1]}": v for k, v in a_points().items()},
                      "e_e": {t: e_e(t) for t in B1_TESTS}, "b2": b2_tests()}, indent=1))
