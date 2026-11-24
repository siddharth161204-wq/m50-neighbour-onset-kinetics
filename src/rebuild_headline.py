"""The headline numbers of the rebuilt manuscript after step 16 (Brief 31), read from the results files, for the
scripts that write the cover letters and the graphical abstract and for the numbers check's entries
(manuscript/rebuild/number_sources.py). Nothing here computes a new result: values are read, converted to kJ or per
cent, and a range across brackets is rounded outward (its lower end down, its upper end up), so that it bounds them.

  needs_3d()      the eight three-dimensional needs with the pulse (results/stage16_scorecard.json, N)
  needs_lumped()  the lumped needs of the same eight with the pulse (results/stage15_table.csv)
  shares()        both as fractions of the Databank's median ejected energy (results/stage14_inputs.csv)
  ratio_spans()   the resolved over lumped threshold across the brackets, strong and weak triggers
  differences()   the resolved need less the lumped need, across the brackets
"""
import csv
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
RES = os.path.join(ROOT, "results")
sys.path.insert(0, HERE)
import rebuild_brackets as RB            # noqa: E402


def _csv(p):
    with open(os.path.join(ROOT, p)) as fh:
        return list(csv.DictReader(fh))


def scorecard():
    return json.load(open(os.path.join(RES, "stage16_scorecard.json")))


def needs_3d():
    """[(test, lo_J, hi_J)] of the eight needs with the pulse, every one bracketed."""
    out = []
    for r in scorecard()["N"]:
        if r["status"] != "done":
            raise ValueError("an N search ended " + r["status"])
        out.append((r["test"], r["lo_J"], r["hi_J"]))
    return out


def needs_lumped():
    return [(r["test"], float(r["C2_E_by_t_J"])) for r in _csv("results/stage15_table.csv")
            if r["delivery"] == "21.39 s pulse" and r["test"] != "M50_ST_Exp3"]


def e_fix():
    return float([r["value"] for r in _csv("results/stage14_inputs.csv") if r["key"] == "db_Eej_median"][0])


def down(x, nd):
    f = 10 ** nd
    return math.floor(x * f + 1e-9) / f


def up(x, nd):
    f = 10 ** nd
    return math.ceil(x * f - 1e-9) / f


def range_3d_kJ(nd=1):
    """The three-dimensional needs' range across their brackets in kJ, rounded outward."""
    n = needs_3d()
    return down(min(lo for _, lo, _ in n) / 1e3, nd), up(max(hi for _, _, hi in n) / 1e3, nd)


def range_lumped_kJ(nd=1):
    v = [x for _, x in needs_lumped()]
    return round(min(v) / 1e3, nd), round(max(v) / 1e3, nd)


def shares_pct(nd=1):
    """(3-D low, 3-D high, lumped low, lumped high) as per cent of the Databank's median ejected energy; the 3-D ends
    across the brackets rounded outward, the lumped ones rounded."""
    n = needs_3d()
    E = e_fix()
    v = [x for _, x in needs_lumped()]
    return (down(100 * min(lo for _, lo, _ in n) / E, nd), up(100 * max(hi for _, _, hi in n) / E, nd),
            round(100 * min(v) / E, nd), round(100 * max(v) / E, nd))


def differences_kJ(nd=1):
    """The resolved need less the lumped need, test by test across the bracket: the smallest lower end and the largest
    upper end, rounded outward."""
    L = dict(needs_lumped())
    n = needs_3d()
    return down(min(lo - L[t] for t, lo, _ in n) / 1e3, nd), up(max(hi - L[t] for t, _, hi in n) / 1e3, nd)


def _lumped_bracket(test):
    row = next(r for r in _csv("results/stage14_needs.csv") if r["test"] == test)
    return RB.brackets(row)[1]


def ratio_span(test, lo_J, hi_J):
    l2, h2 = _lumped_bracket(test)
    return lo_J / h2, hi_J / l2


def weak_spans():
    """[(test, lower, upper)] for ST-Exp3 (step 15) and PT-Exp1 (step 16), across the brackets (not yet rounded)."""
    b1 = json.load(open(os.path.join(RES, "stage15_paper_numbers.json")))["B1"]["M50_ST_Exp3"]["bracket"]
    T = scorecard()["T"]
    out = [("M50_ST_Exp3",) + ratio_span("M50_ST_Exp3", b1["lo_J"], b1["hi_J"])]
    if T.get("status") == "done":
        out.append((T["test"],) + ratio_span(T["test"], T["lo_J"], T["hi_J"]))
    return out


def weak_range(nd=2):
    s = weak_spans()
    return down(min(x[1] for x in s), nd), up(max(x[2] for x in s), nd)


if __name__ == "__main__":
    try:
        print("3-D needs (kJ):", range_3d_kJ(), "lumped:", range_lumped_kJ(), "shares (%):", shares_pct(),
              "differences (kJ):", differences_kJ())
    except ValueError as e:
        print("not yet:", e)
    print("weak spans:", weak_spans(), "range:", weak_range())
