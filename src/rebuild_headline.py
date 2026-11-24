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


def shares_pct_round(nd=1):
    """(3-D low, 3-D high, lumped low, lumped high) as per cent of the Databank's median ejected energy, each rounded
    to nd decimals in the usual way (the 3-D ends from the brackets' ends)."""
    n = needs_3d()
    E = e_fix()
    v = [x for _, x in needs_lumped()]
    return (round(100 * min(lo for _, lo, _ in n) / E, nd), round(100 * max(hi for _, _, hi in n) / E, nd),
            round(100 * min(v) / E, nd), round(100 * max(v) / E, nd))


def _lumped_bracket(test):
    row = next(r for r in _csv("results/stage14_needs.csv") if r["test"] == test)
    return RB.brackets(row)[1]


def thresholds_3d():
    """[(test, lo_J, hi_J, source)] of every threshold with the pulse bracketed in three dimensions: step 15's B1
    searches ("B1") and step 16's T ("T"), and step 16's need searches (N) where the need's bracket has a lower end that
    does not run away within 900 s, so that the same two runs bracket the threshold too, a reading made after the runs
    ("N", or "B1+N" where it narrows a B1 bracket, the narrower bounds being taken). The two ends of an N bracket are
    adjacent among that search's runs, so no run lies between them."""
    b1 = json.load(open(os.path.join(RES, "stage15_paper_numbers.json")))["B1"]
    out = {t: [v["bracket"]["lo_J"], v["bracket"]["hi_J"], "B1"] for t, v in b1.items()}
    sc = scorecard()
    T = sc["T"]
    if T.get("status") == "done":
        out[T["test"]] = [T["lo_J"], T["hi_J"], "T"]
    for r in sc["N"]:
        if r["status"] == "done" and not r["lo_runs_away"]:
            t = r["test"]
            if t in out:
                lo, hi, s = out[t]
                if not (lo <= r["lo_J"] < r["hi_J"] <= hi):
                    raise ValueError("an N bracket of %s does not lie inside its threshold bracket" % t)
                out[t] = [r["lo_J"], r["hi_J"], s + "+N"]
            else:
                out[t] = [r["lo_J"], r["hi_J"], "N"]
    return [(t,) + tuple(v) for t, v in out.items()]


def threshold_ratio_spans():
    """[(test, lower, upper)] of the resolved over the lumped threshold across the brackets (not rounded) for every
    threshold of thresholds_3d() whose lumped threshold is not zero; upper is None where the lumped bracket's lower
    end is zero (no delivery does not run the lumped neighbour away, and the least run that does bounds it above)."""
    out = []
    for t, lo, hi, _ in thresholds_3d():
        l2, h2 = _lumped_bracket(t)
        if h2 == 0:
            continue
        out.append((t, lo / h2, (hi / l2) if l2 > 0 else None))
    return out


def strong_bounded_range(nd=2):
    """The ratio's range across the brackets, rounded outward, over the strong-trigger tests whose lumped bracket is
    bounded away from zero (PT-Exp4 and PP-Exp2)."""
    s = [x for x in threshold_ratio_spans() if x[2] is not None and x[0] not in ("M50_ST_Exp3", "M50_PT_Exp1")]
    return down(min(x[1] for x in s), nd), up(max(x[2] for x in s), nd)


def strong_unbounded_lower(nd=2):
    """[(test, lower bound rounded down)] of the strong-trigger tests whose ratio is bounded only below."""
    return [(t, down(a, nd)) for t, a, b in threshold_ratio_spans() if b is None]


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
