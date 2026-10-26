"""Stage 7 inputs, each read from its file or its source (DECISIONS.md D64 to D68); nothing here is a model result.

- The measured tests (D64): Fransson et al. (2024), Table 3 (the eight M50 parallel tests) and Table 4 (the eight
  M50 series tests), in inputs/fransson2024/m50_tests_stage7.csv: per test the connection, the table, the trigger
  cell's and the propagation cell's maximum temperature (the tables' columns "Maximum temperature [°C]", "Trigger
  cell" and "Propagation cell"), whether it propagated ("Propagation") and the time to propagation ("Time to
  propagation [s]").
- The levels of the ignition conditions (D67): 255.7 C, the two-cell study's lower edge of the internal-short band
  (D35); 150 C, the paper's minimum neighbour temperature for propagation (D33 (2)); 138.5 C, the peak of the
  posterior-mean separator melting at 5 C/min (D5, results/v0_dsc_check.json).
- The event (D68): the cell's stored electrical energy, 18.2 Wh (65.52 kJ), and the specification's minimum,
  17.6 Wh (63.36 kJ), from LG Chem's product specification for the INR21700 M50 (D57 (2)); the median release
  duration, 21.39 s (D52), as its length.
- The aged SEI (D66): the SEI's initial amount 0, in place of the fresh 0.15 (bcrnn.C0), the reference.
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage6_inputs as IN6                       # noqa: E402  (the Stage 6 inputs, unchanged)

INPUTS = os.path.join(HERE, "..", "inputs")
RES = os.path.join(HERE, "..", "results")
TESTS = os.path.join(INPUTS, "fransson2024", "m50_tests_stage7.csv")
DSC = os.path.join(RES, "v0_dsc_check.json")

LEVEL_PROP_C = 278.9 * (1 - 0.1665 / 2)           # 255.68 C: LP.T_ONSET_BAND[0] in C (two-cell D2, D35)
LEVEL_150_C = IN6.LEVEL_150_C                      # 150 C (D33 (2))
WH_TO_J = 3600.0
E_EVENT_WH, E_EVENT_LOW_WH = 18.2, 17.6           # LG Chem LRB-PS-CY18.2Wh-M50, section 2.1: nominal and minimum
E_EVENT_J = round(E_EVENT_WH * WH_TO_J, 6)         # 65,520 J
E_EVENT_LOW_J = round(E_EVENT_LOW_WH * WH_TO_J, 6) # 63,360 J
SEI_AGED = 0.0                                     # D57 (1): the SEI's initial amount in the aged cell
SEI_FRESH = 0.15                                   # bcrnn.C0, the reference
T_AMB_C = 25.0


def separator_melt_C(path=DSC):
    """D5: the temperature of the posterior-mean separator melting's peak at 5 C/min, as V0 recorded it."""
    d = json.load(open(path))
    return float(d["separator"]["reading_i_minus_dH_times_rate"]["at_C"])


LEVEL_SEP_C = 138.5                                # D5; checked against results/v0_dsc_check.json in test_stage7.py


def tests():
    rows = list(csv.DictReader(open(TESTS)))
    out = []
    for r in rows:
        out.append({"test": r["test"], "connection": r["connection"], "table": r["table"],
                    "trigger_max_C": float(r["trigger_max_C"]), "neighbour_max_C": float(r["neighbour_max_C"]),
                    "propagated": r["propagated"] == "Yes",
                    "time_s": float(r["time_to_propagation_s"]) if r["time_to_propagation_s"] else None})
    return out


def measured():
    rows = tests()
    prop = [r for r in rows if r["propagated"]]
    return {"n": len(rows), "propagated": len(prop),
            "propagated_by_connection": {c: sum(r["propagated"] for r in rows if r["connection"] == c)
                                         for c in ("series", "parallel")},
            "times_s": sorted(r["time_s"] for r in prop),
            "neighbour_max_propagated_C": sorted(r["neighbour_max_C"] for r in prop),
            "neighbour_max_propagated_range_C": [min(r["neighbour_max_C"] for r in prop),
                                                 max(r["neighbour_max_C"] for r in prop)],
            "trigger_max_range_C": [min(r["trigger_max_C"] for r in rows), max(r["trigger_max_C"] for r in rows)],
            "by_test": {r["test"]: r for r in rows}}


def durations():
    return IN6.durations()


def energies():
    return IN6.energies()


if __name__ == "__main__":
    m = measured()
    m.pop("by_test")
    print(json.dumps({"measured": m, "levels_C": {"prop": LEVEL_PROP_C, "150": LEVEL_150_C, "sep": LEVEL_SEP_C},
                      "separator_melt_from_v0_C": separator_melt_C(), "event_J": [E_EVENT_J, E_EVENT_LOW_J],
                      "durations": durations()["release_durations_s"]}, indent=1))
