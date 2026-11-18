"""Stage 14 scoring of P1 to P6 (DECISIONS D155; predictions_stage14.md).

Reads results/stage14_bounds.json, results/stage14_bounds.csv and results/stage14_needs.csv;
writes results/stage14_scorecard.json.
"""
import csv
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    bj = json.load(open(os.path.join(ROOT, "results", "stage14_bounds.json")))
    with open(os.path.join(ROOT, "results", "stage14_bounds.csv"), newline="") as fh:
        brow = list(csv.DictReader(fh))
    det = {r["path"]: r["determinable"] == "yes" for r in brow}
    with open(os.path.join(ROOT, "results", "stage14_needs.csv"), newline="") as fh:
        needs = {r["test"]: r for r in csv.DictReader(fh)}
    E_fix = bj["inputs"]["E_fix_J"]
    largest = float(needs["M50_PP_Exp2"]["need_21s_hi_J"])
    smallest = float(needs["M50_SP_Exp3"]["need_21s_hi_J"])

    a1_total = bj["A1"]["bounds_J"]["total"]
    p1_line = 0.02 * E_fix
    cap_end = [p for p in ("A1", "A2", "A5") if det[p]]
    s21 = sum(bj[p]["bounds_J"]["21.39"] for p in cap_end)
    stot = sum(bj[p]["bounds_J"]["total"] for p in cap_end)
    a3_21 = bj["A3"]["bounds_J"]["21.39"]
    not_det = [p for p in ("A1", "A2", "A3", "A4", "A5", "A6") if not det[p]]
    a6_total = bj["A6"]["bounds_J"]["total"]

    card = {
        "P1": dict(holds=a1_total < p1_line, A1_total_upper_J=a1_total, line_J=p1_line,
                   beside=dict(A1_within_21s_J=bj["A1"]["bounds_J"]["21.39"],
                               flame_on_vent_axis_J=bj["A1"]["conditional_axis_J"],
                               flame_in_front_of_trigger_end_J=bj["A1"]["conditional_column_J"])),
        "P2": dict(holds=s21 < largest, determinable_cap_end_paths=cap_end, sum_within_21s_J=s21, line_J=largest,
                   beside=dict(sum_totals_J=stot)),
        "P3": dict(holds=s21 > smallest, sum_within_21s_J=s21, line_J=smallest, beside=dict(sum_totals_J=stot)),
        "P4": dict(holds=a3_21 > largest, A3_facing_within_21s_J=a3_21, line_J=largest),
        "P5": dict(holds=len(not_det) >= 1, not_determinable=not_det),
        "P6": dict(holds=a6_total > 1000.0, A6_total_upper_J=a6_total, line_J=1000.0,
                   beside=dict(A6_within_21s_rate_at_25C_J=bj["A6"]["conditional_25C_J"]["21.39"])),
    }
    # What predictions_stage14.md recorded as fixed by the design, before any bound was computed.
    fixed = {"P1": False, "P2": False, "P3": True, "P4": True, "P5": True, "P6": True}
    for k, exp in fixed.items():
        card[k]["design_fixed_outcome"] = exp
        card[k]["as_the_design_fixed"] = card[k]["holds"] == exp
    with open(os.path.join(ROOT, "results", "stage14_scorecard.json"), "w") as fh:
        json.dump(card, fh, indent=1)
    print(json.dumps({k: v["holds"] for k, v in card.items() if isinstance(v, dict)}, indent=1))


if __name__ == "__main__":
    main()
