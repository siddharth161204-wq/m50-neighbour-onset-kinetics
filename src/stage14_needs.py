"""Stage 14, Part A0.3: what each of the sixteen tests needs in delivered energy, read from earlier results.

Nothing is run. Every number is read from files that Stages 8 to 12 committed:
  results/stage8_thresholds.csv   thresholds f* (C1, C2) with the 21.39 s delivery, as fractions of r E_b
  results/stage9_fractions.csv    f_t (C2) and f_max (far face) with the 21.39 s delivery
  results/stage9_long.csv         the same readings with a constant power over 120, 240 and 360 s
  results/stage12_fixed_ejecta.csv  Stage 12's narrowed searches, in joules
  inputs/fransson2024/m50_tests.csv  outcome, time, maxima and failure category
A delivered energy is a fraction times that test's E_e (r E_b); a run depends on the two only through
their product (DECISIONS.md D122 (7)), so the energies below are the energies the model received.

Output: results/stage14_needs.csv, one row per test.
"""
import csv
import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(path):
    with open(os.path.join(ROOT, path), newline="") as fh:
        return list(csv.DictReader(fh))


def fnum(x):
    if x is None:
        return None
    x = str(x).strip()
    if x in ("", "nan", "NaN", "None"):
        return None
    return float(x)


def main():
    tests = {r["test"]: r for r in read("inputs/fransson2024/m50_tests.csv")}
    s8 = {r["test"]: r for r in read("results/stage8_thresholds.csv")}
    s9 = {r["test"]: r for r in read("results/stage9_fractions.csv")}
    s9l = {}
    for r in read("results/stage9_long.csv"):
        s9l[(r["test"], float(r["tau_s"]))] = r
    s12 = {}
    for r in read("results/stage12_fixed_ejecta.csv"):
        s12[(r["part"], r["test"], r["criterion"])] = r

    rows = []
    for name, t in tests.items():
        e8 = s8[name]
        e9 = s9[name]
        Ee = float(e8["E_e_J"])
        prop = t["propagated"] == "Yes"
        row = {
            "test": name,
            "connection": t["connection"],
            "propagated": "yes" if prop else "no",
            "time_to_propagation_s": t["time_to_propagation_s"],
            "trigger_max_C": t["trigger_max_C"],
            "neighbour_max_C": t["neighbour_max_C"],
            "failure_category": t["failure_category"],
            "E_e_J": round(Ee, 1),
        }
        # Thresholds with the 21.39 s delivery (Stage 8), narrowed by Stage 12 where it searched further.
        for crit, lo_k, hi_k in (("C1", "fC1_lo", "fC1_hi"), ("C2", "fC2_lo", "fC2_hi")):
            lo, hi = float(e8[lo_k]) * Ee, float(e8[hi_k]) * Ee
            src = "stage8_thresholds.csv"
            k12 = ("B1", name, crit)
            if k12 in s12:
                lo, hi = fnum(s12[k12]["E_lo_J"]), fnum(s12[k12]["E_hi_J"])
                src = "stage12_fixed_ejecta.csv (B1)"
            row[f"threshold_{crit}_lo_J"] = round(lo, 1)
            row[f"threshold_{crit}_hi_J"] = round(hi, 1)
            row[f"threshold_{crit}_source"] = src
        # The test's own reading with the 21.39 s delivery.
        if prop:
            k12 = ("B2", name, "C2")
            r12 = s12[k12]
            status = r12["status"]
            row["reading_21s"] = "f_t(C2) " + status
            if status == "matched":
                row["need_21s_lo_J"] = round(fnum(r12["E_t_J"]), 1)
                row["need_21s_hi_J"] = round(fnum(r12["E_t_J"]), 1)
            else:
                row["need_21s_lo_J"] = round(fnum(r12["E_lo_J"]), 1)
                row["need_21s_hi_J"] = round(fnum(r12["E_hi_J"]), 1)
            row["need_21s_source"] = "stage12_fixed_ejecta.csv (B2), from Stage 9's search"
        else:
            st = e9["fmax_status"]
            expl = e9["fmax_exploratory"] == "True"
            row["reading_21s"] = "f_max far face " + st + (" (exploratory)" if expl else "")
            E = fnum(e9["fmax_E_J"])
            row["need_21s_lo_J"] = round(E, 1)
            row["need_21s_hi_J"] = round(E, 1)
            row["need_21s_source"] = "stage9_fractions.csv"
        row["need_21s_duration_s"] = 21.39
        # Long deliveries (Stage 9, constant power).
        for tau in (120.0, 240.0, 360.0):
            r = s9l[(name, tau)]
            key = f"need_{int(tau)}s"
            if prop:
                st = r["ft_C2_status"]
                if st in ("matched", "bracketed"):
                    v = fnum(r["ft_C2_E_J"])
                    row[key + "_reading"] = "f_t(C2) " + st
                    row[key + "_lo_J"] = round(v, 1)
                    row[key + "_hi_J"] = round(v, 1)
                elif st == "threshold":
                    row[key + "_reading"] = "f_t(C2) threshold"
                    row[key + "_lo_J"] = round(float(r["ft_C2_lo"]) * Ee, 1)
                    row[key + "_hi_J"] = round(float(r["ft_C2_hi"]) * Ee, 1)
                else:
                    row[key + "_reading"] = "f_t(C2) " + st
                    row[key + "_lo_J"] = ""
                    row[key + "_hi_J"] = ""
            else:
                st = r["fmax_status"]
                row[key + "_reading"] = "f_max far face " + st + (" (exploratory)" if r["fmax_exploratory"] == "True" else "")
                v = fnum(r["fmax_E_J"])
                row[key + "_lo_J"] = "" if v is None else round(v, 1)
                row[key + "_hi_J"] = "" if v is None else round(v, 1)
        rows.append(row)

    out = os.path.join(ROOT, "results", "stage14_needs.csv")
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {out} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
