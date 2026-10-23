"""Stage 6 inputs, each read from its file (DECISIONS.md D51 to D54); nothing here is a model result.

- The measured tests: Fransson et al. (2024), Tables 3 and 4, in inputs/fransson2024/m50_tests.csv (D33): the nine
  times to propagation, the neighbour maxima of the seven tests that did not propagate, the sixteen trigger maxima.
- The release durations (D52): the paper's supplementary Figure 10 gives the trigger cell's mean heating rate over
  Section I, from the start of its runaway to its maximum, for two tests (inputs/fransson2024/fig10_section_rates.csv);
  the length of Section I is the trigger's rise over it divided by that rate, the rise being the trigger's maximum in
  Table 3 minus 25 C (the start is not reported; 25 C, the model's ambient, is a conditional choice). The range of the
  two lengths and their median are the release durations.
- The trigger energies (D53): the Battery Failure Databank's ten LG M50 nail tests at 100 % state of charge
  (inputs/databank/databank_m50_used.csv): the largest cell-body energy, Stage 5's 33.2 kJ, and the corrected total
  energy including the ejected fractions, its median as the level and its minimum and maximum as the bracket.
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
INPUTS = os.path.join(HERE, "..", "inputs")
TESTS = os.path.join(INPUTS, "fransson2024", "m50_tests.csv")
FIG10 = os.path.join(INPUTS, "fransson2024", "fig10_section_rates.csv")
DATABANK_USED = os.path.join(INPUTS, "databank", "databank_m50_used.csv")

T_START_C = 25.0                 # the trigger's temperature at the start of Section I (not reported; D52, conditional)
LEVEL_150_C = 150.0              # the paper's minimum neighbour temperature for propagation (D33 (2))
WINDOW_S = (147.0, 342.0)        # the measured times to propagation, both connections (D33 (1)), inclusive
NP_QUOTED_MAX_C = 133.0          # the largest neighbour maximum of the five non-propagating tests the note quotes


def _median(v):
    v = sorted(v)
    n = len(v)
    return v[n // 2] if n % 2 else 0.5 * (v[n // 2 - 1] + v[n // 2])


def tests():
    return list(csv.DictReader(open(TESTS)))


def measured():
    rows = tests()
    prop = [r for r in rows if r["propagated"] == "Yes"]
    notp = [r for r in rows if r["propagated"] == "No"]
    trig = [float(r["trigger_max_C"]) for r in rows]
    return {
        "times_to_propagation_s": sorted(float(r["time_to_propagation_s"]) for r in prop),
        "propagated_tests": [r["test"] for r in prop],
        "neighbour_max_not_propagated_C": sorted(float(r["neighbour_max_C"]) for r in notp),
        "not_propagated_tests": [r["test"] for r in notp],
        "neighbour_max_propagated_C": sorted(float(r["neighbour_max_C"]) for r in prop),
        "trigger_max_C": sorted(trig),
        "trigger_max_range_C": (min(trig), max(trig)),
        "trigger_max_median_C": _median(trig),
        "by_test": {r["test"]: r for r in rows},
    }


def durations():
    """Section I lengths of the two tests of the supplementary Figure 10 (D52)."""
    by_test = {r["test"]: r for r in tests()}
    out = []
    for r in csv.DictReader(open(FIG10)):
        if r["section"] == "I" and r["cell"] == "trigger":
            tmax = float(by_test[r["test"]]["trigger_max_C"])
            rate = float(r["rate_C_per_s"])
            out.append({"test": r["test"], "trigger_max_C": tmax, "section1_rate_C_per_s": rate,
                        "duration_s": (tmax - T_START_C) / rate})
    out.sort(key=lambda d: d["duration_s"])
    ds = [d["duration_s"] for d in out]
    return {"tests": out, "min_s": ds[0], "median_s": _median(ds), "max_s": ds[-1],
            "release_durations_s": [ds[0], _median(ds), ds[-1]]}


def energies():
    """Cell-body maximum and the corrected total energy of the Databank's ten M50 nail tests at 100 % SOC (D53)."""
    rows = [r for r in csv.DictReader(open(DATABANK_USED)) if "Nail" in r["Trigger-Mechanism"]]
    body = [(1e3 * float(r["Energy-Fraction-Cell-Body-kJ"]), r["Test-ID"]) for r in rows]
    total = sorted((1e3 * float(r["Corrected-Total-Energy-Yield-kJ"]), r["Test-ID"]) for r in rows)
    tv = [e for e, _ in total]
    n = len(tv)
    med_ids = [total[n // 2][1]] if n % 2 else [total[n // 2 - 1][1], total[n // 2][1]]
    return {"n_nail_tests": n, "test_ids": [r["Test-ID"] for r in rows],
            "body_max_J": max(body)[0], "body_max_test": max(body)[1],
            "total_min_J": tv[0], "total_min_test": total[0][1],
            "total_median_J": _median(tv), "total_median_tests": med_ids,
            "total_max_J": tv[-1], "total_max_test": total[-1][1],
            "total_J_by_test": {t: e for e, t in total}}


if __name__ == "__main__":
    import json
    m = measured()
    m.pop("by_test")
    print(json.dumps({"measured": m, "durations": durations(), "energies": energies()}, indent=1))
