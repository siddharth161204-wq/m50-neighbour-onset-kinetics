"""The narrowest bracket the archive holds on each threshold with the 21.39 s pulse, for the rebuilt manuscript.

results/stage14_needs.csv carries each test's local (C1) and lumped (C2) threshold brackets as Stages 8 and 12 left
them. Stage 13 narrowed four of those brackets at the central contact: the local threshold of M50_PT_Exp1, ST_Exp3
and PT_Exp3 (results/stage13_skin.csv, the facing half at 21.39 s, res_source "archived bracket refined in Stage 13",
fractions of the test's ejected energy E_e) and the lumped threshold of M50_PT_Exp1 (results/stage13_twobody.csv, the
central contact at 21.39 s, lum_source "archived (Stage 8, refined)", in J). Table S3, Table S8 and Fig. 2 draw the
narrower bracket wherever there is one, so that the main text, its figures and the supplement quote one bracket for
each threshold. Nothing is computed beyond the fraction's conversion to J (fraction times E_e, the stage14_needs value).
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
TAU21 = "21.38651984299561"


def _csv(name):
    with open(os.path.join(RES, name)) as fh:
        return list(csv.DictReader(fh))


def e_e():
    """Each test's ejected energy E_e (J), as stage14_needs.csv gives it."""
    return {r["test"]: float(r["E_e_J"]) for r in _csv("stage14_needs.csv")}


def refined():
    """{test: {"C1": (lo_J, hi_J), "C2": (lo_J, hi_J)}} for the brackets Stage 13 narrowed (21.39 s, central)."""
    ee = e_e()
    out = {}
    for r in _csv("stage13_skin.csv"):
        if r["region"] == "half" and r["tau_d_s"] == TAU21 and r["res_source"] == "archived bracket refined in Stage 13":
            out.setdefault(r["test"], {})["C1"] = (float(r["res_lo"]) * ee[r["test"]], float(r["res_hi"]) * ee[r["test"]])
    for r in _csv("stage13_twobody.csv"):
        if r["h"] == "central" and r["tau_d_s"] == TAU21 and r["lum_source"] == "archived (Stage 8, refined)":
            out.setdefault(r["test"], {})["C2"] = (float(r["lum_lo_J"]), float(r["lum_hi_J"]))
    return out


def brackets(row):
    """(C1 (lo, hi), C2 (lo, hi)) in J for one row of stage14_needs.csv: the narrowest the archive holds."""
    t = row["test"]
    c1 = (float(row["threshold_C1_lo_J"]), float(row["threshold_C1_hi_J"]))
    c2 = (float(row["threshold_C2_lo_J"]), float(row["threshold_C2_hi_J"]))
    if "threshold" in row["reading_21s"]:          # the measured-time search narrowed the lumped bracket (Stage 12)
        c2 = (float(row["need_21s_lo_J"]), float(row["need_21s_hi_J"]))
    r = refined().get(t, {})
    return r.get("C1", c1), r.get("C2", c2)


if __name__ == "__main__":
    for t, v in sorted(refined().items()):
        print(t, {k: tuple(round(x, 1) for x in b) for k, b in v.items()})
