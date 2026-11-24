"""The registry of the study's predictions and its sixteen steps, for the rebuilt manuscript's supplement.

Rows 1 to 74 (Stages 1 to 12) are manuscript/data/predictions_by_stage.csv unchanged. Rows 75 to 109 (Stages 13 to
16) are shortened here from predictions_stage13.md to predictions_stage16.md (each row names its file and line), with
the verdicts read from results/stage13_scorecard.json to stage16_scorecard.json. A failure counts as foreseen under the rule of the counts file
(manuscript/data/predictions_by_stage_counts.md): the predictions file recorded it, before the runs, as expected or as
fixed by its design or by earlier records.

Supplementary Table S2 lists only the predictions whose runs the manuscript or its supplement reports (Brief 30, item
6): UNREPORTED names the others, each with the reason, and STRIP the reasons in a listed prediction's expectation that
rest on runs neither document reports, which leave the table. The registry file keeps all of them, with a column saying
whether the table lists each and, if not, why.

Writes manuscript/rebuild/data/predictions_registry.csv and manuscript/rebuild/data/steps.csv, and the supplement's
tables manuscript/rebuild/tables/s1_steps.tex and s2_registry.tex.

Usage: python3 src/make_rebuild_registry.py
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
RES = os.path.join(ROOT, "results")
OUTD = os.path.join(ROOT, "manuscript", "rebuild", "data")
OUTT = os.path.join(ROOT, "manuscript", "rebuild", "tables")

NEW = [
    # stage, label, statement, expectation, source line
    (13, "P1", "For PT_Exp1 with a 5 s triangular delivery over the facing half, the resolved f*(C1) lies within 10 % of the skin model's closed form (0.07701).",
     "likely", "predictions_stage13.md:9"),
    (13, "P2", "At 40 s (PT_Exp1, facing half), the cross-section conduction model (0.21775) lies within 5 % of the resolved bracket's midpoint.",
     "uncertain", "predictions_stage13.md:11"),
    (13, "P3", "At 120 s (PT_Exp1, facing half), the resolved threshold lies more than 5 % below the cross-section conduction model's (0.41450): local ignition.",
     "uncertain", "predictions_stage13.md:13"),
    (13, "P4", "For ST_Exp3 and PT_Exp3, the cross-section model with the trigger's conduction lies within 10 % of the resolved midpoints at 10 and 60 s, and gives the direction of change from 21.39 s in all four cases.",
     "uncertain", "predictions_stage13.md:15"),
    (13, "P5", "For PT_Exp1 at 21.39 s, the threshold energy over the whole lateral surface is 1.8 to 2.2 times the facing half's.",
     "likely", "predictions_stage13.md:17"),
    (13, "P6", "For PT_Exp1 at 21.39 s, over the eighth of the facing half nearest the cap the threshold energy per unit area exceeds the facing half's by at least 25 %.",
     "likely", "predictions_stage13.md:19"),
    (13, "P7", "The ignition temperature of the posterior-mean kinetics lies between 215 and 240 C (known when registered, so not scored), and the central 95 % of the 200 draws spans less than 40 K (scored).",
     "likely for the mean, uncertain for the span", "predictions_stage13.md:21"),
    (13, "P8", "The two-body model's whole-cell threshold lies within the larger of 10 % and 300 J of the lumped model's midpoint in at least 28 of the 32 low and high contact searches.",
     "uncertain", "predictions_stage13.md:23"),
    (13, "P9", "For PT_Exp1, the ratio f*(C2)/f*(C1) falls from 21.39 to 120 to 360 s and is below 1.5 at 360 s.",
     "likely for the fall, uncertain for the level", "predictions_stage13.md:25"),
    (13, "P10", "For PP_Exp3, ST_Exp2 and PT_Exp3, the lumped model's needed delivery falls by 150 to 300 J per kJ of the trigger's body energy across the 4 kJ between shifted runs.",
     "likely for the first two, uncertain for PT_Exp3", "predictions_stage13.md:27"),
    (14, "P1", "The upper bound of radiation from a cap-end vent to the facing half is below 2 % of 76.74 kJ.",
     "the bullet says likely; the file's analysis, written before any bound, says P1 is expected to fail", "predictions_stage14.md:7"),
    (14, "P2", "The upper bounds of the cap-end paths that are determinable sum to less than 5.96 kJ, the largest need among the seven matched times.",
     "uncertain; the file's analysis says P2 is expected to fail", "predictions_stage14.md:8"),
    (14, "P3", "They sum to more than 0.26 kJ, the smallest need.", "likely", "predictions_stage14.md:9"),
    (14, "P4", "The upper bound of a breach's jet facing the neighbour exceeds 5.96 kJ delivered within 21.39 s.",
     "likely", "predictions_stage14.md:10"),
    (14, "P5", "At least one of the six paths is not determinable from published inputs for this cell.", "likely",
     "predictions_stage14.md:11"),
    (14, "P6", "For the parallel tests the circuit's upper bound on the neighbour's own heating exceeds 1 kJ.",
     "uncertain; the file's analysis says P6 is expected to hold", "predictions_stage14.md:12"),
    (15, "P1", "The reactive cross-section's E*(C8) lies within 15 % of the midpoint of the three-dimensional bracket in at least three of four tests.",
     "uncertain; the reduced model's values are the searches' centres", "predictions_stage15.md:110"),
    (15, "P2", "For PT_Exp4 with the 21.39 s delivery, E*(C8) lies between 6 and 10 kJ.", "likely; the reduced model's value, registered with it: 7,062 J",
     "predictions_stage15.md:112"),
    (15, "P3", "In at least three of the four tests E*(C8) is at least 1.25 times the whole-cell clock's threshold E*(C2).",
     "likely for the three strong triggers, uncertain for ST_Exp3; the reduced model's values: 1.49, 1.72, above zero in SP_Exp3, 0.85", "predictions_stage15.md:114"),
    (15, "P4", "For PT_Exp4, in the run at the upper end of the bracket, the mean crosses 255.7 C between 150 and 400 s after the trigger's start.",
     "likely; the reduced model's value: 310.6 s at the upper end of its own bracket", "predictions_stage15.md:116"),
    (15, "P5", "In that run the far face reads more than 15 K above 197.3 C, the reading from which the measured neighbour jumped, when its own jump begins.",
     "likely; the reduced model's value: 240.1 C", "predictions_stage15.md:118"),
    (15, "P6", "The constant power after the 5.0 kJ pulse that brings the cell's own runaway to 271.5 s lies between 5 and 25 W.",
     "likely; the reduced model's value: 12.5 W", "predictions_stage15.md:120"),
    (15, "P7", "Under none of four kinetic draws and not with the aged SEI does the resolved cell run away at PT_Exp4's 5,045 J, and the least shift of the rate laws that makes it run away is 10 K or more.",
     "likely; the reduced model's values: no runaway in any of the five runs, the least shift 20.0 K", "predictions_stage15.md:122"),
    (15, "P8", "PT_Exp4's run with 6,209 J over 240 s, carried to 900 s, runs away.", "likely; the reduced model's value, registered with it: no runaway, the mean peaking at 220.5 C", "predictions_stage15.md:124"),
]
NEW += [
    (16, "P1", "With the 21.4 s pulse, the reactive cross-section's need lies within 10 % of the three-dimensional need in each of the eight strong-trigger tests that propagated.",
     "holds, the cross-section's need 2 to 9 % above, since its search stopped at the first run within 10 s of the measured time and the three-dimensional runaway came earlier near the thresholds", "predictions_stage16.md:30"),
    (16, "P2", "With the pulse, the cross-section's need lies above the three-dimensional need in each of the eight tests.",
     "holds, for the reasons of P1; least sure in PP-Exp4 and ST-Exp4, whose needs lie near their thresholds", "predictions_stage16.md:32"),
    (16, "P3", "With the pulse, every three-dimensional need lies within 4.1 to 8.1 kJ.",
     "holds; the cross-section's runs put the needs at 4.31 to 7.46 kJ", "predictions_stage16.md:34"),
    (16, "P4", "With the pulse, the resolved need exceeds the lumped need in each of the eight tests.",
     "holds; fixed, or nearly, by earlier records in seven of the eight, where a three-dimensional run at or above the lumped need already ran away late or not at all", "predictions_stage16.md:36"),
    (16, "P5", "With the pulse, the resolved need exceeds the lumped need by 1.0 to 5.0 kJ in each of the eight tests.",
     "holds, by 1.4 to 4.1 kJ on the cross-section's runs", "predictions_stage16.md:38"),
    (16, "P6", "After PT-Exp1's weak trigger the resolved threshold with the pulse lies below the lumped threshold, in three dimensions.",
     "holds; the cross-section's threshold is 0.84 times the lumped one, and the three-dimensional thresholds lay within 15 % of the cross-section's in the four tests searched", "predictions_stage16.md:40"),
    (16, "P7", "PT-Exp1's ratio of the resolved to the lumped threshold, by the brackets' midpoints, lies between 0.75 and 0.95.",
     "holds, at 0.84, fixed by construction if the search's first two runs close its bracket", "predictions_stage16.md:42"),
    (16, "P8", "Refining the mesh by 1.5 and halving every step limit moves a need by at most one bracket width.",
     "holds, most likely with both ends of the bracket keeping their outcome", "predictions_stage16.md:44"),
    (16, "P9", "That refinement moves the runaway time by less than 3 % at both ends of the need's bracket.",
     "holds, at about +1.5 %, as the earlier refinement at PT-Exp4's threshold", "predictions_stage16.md:46"),
    (16, "P10", "With constant power, the cross-section's needs lie within 10 % of the three-dimensional needs found.",
     "fails in at least one search, since with constant power the cross-section's runaway came up to 34.5 s after the three-dimensional model's", "predictions_stage16.md:48"),
    (16, "P11", "With constant power, the resolved need exceeds the lumped need in every three-dimensional search closed.",
     "holds; fixed, or nearly, by earlier records in 21 of the 24 cases", "predictions_stage16.md:50"),
]
FORESEEN = {(14, "P1"), (14, "P2"), (16, "P10")}

# The predictions whose runs neither the manuscript nor its supplement reports (Brief 30, item 6), with the reason. They
# leave Supplementary Table S2; each, with its file and its verdict, stays in this registry file and in the archive.
EARLIER_GEOMETRY = "its runs are on the earlier two-cell study's geometry, which neither document reports"
UNREPORTED = {
    1: {"all": EARLIER_GEOMETRY}, 2: {"all": EARLIER_GEOMETRY}, 3: {"all": EARLIER_GEOMETRY},
    4: {"all": EARLIER_GEOMETRY},
    6: {"all": "step 6's runs (the tests' 150 C criterion and the trigger's measured durations) are not reported"},
    7: {"P2": "the lumped criterion at 150 C (C3) test by test is not reported",
        "P3": "C3's crossing times are not reported",
        "P4": "the separator-melting criterion (C4) test by test is not reported",
        "P5": "the runs with an aged SEI are not reported",
        "P6": "the lumped neighbour's peaks with no delivered heat test by test are not reported",
        "P7": "every criterion's count by connection is not reported",
        "P8": "the internal-short event runs are not reported"},
    8: {"P4": "the runs at a delivered fraction of 0.2 are not reported",
        "P5": "the counts at the common fractions 0.1, 0.2 and 0.3 are not reported",
        "P7": "the runs with Joule heat (the electrical bracket) are not reported",
        "P8": "the delivery through the quarter of the facing half nearest the cap is not reported"},
    9: {"P6": "the local criterion's time-matching fractions with 240 s of constant power are not reported",
        "P8": "the runs with an aged SEI are not reported"},
    10: {"P2": "the fits of the long deliveries to the history are not reported",
         "P3": "the 60 s rise before propagation in the model's runs is not reported",
         "P4": "the peak-matching fractions at the facing and 90 degree nodes are not reported",
         "P5": "the separation at the facing and 90 degree nodes is not reported",
         "P7": "the rank correlations are not reported"},
    11: {"P6": "the six tests' runs under the kinetic draws at the matched fractions are not reported"},
    13: {"P5": "the threshold over the whole lateral surface is not reported",
         "P6": "the threshold over the eighth of the facing half nearest the cap is not reported"},
}

# Reasons in a listed prediction's expectation that rest on runs neither document reports: they leave the table (Brief
# 30, item 6), and the expectation keeps its verdict word. Each old string must occur in that expectation once.
STRIP = {
    (7, "P1"): ("; Stage 6 ignited the hot spot only at the Databank's total energy and, at the median peak, only at "
                "the high contact", ""),
    (8, "P1"): ("; the hot spot is close to 255.7 C in several misses", ""),
    (9, "P1"): (" (the hot spot crosses at 11.9 to 18.5 s at the threshold's upper end)", ""),
    (9, "P2"): (" (seven upper-end crossings lie inside the window; ST_Exp3's lies at 61.4 s)", ""),
    # counts the study's expectation drew from a sizing estimate on earlier, unreported runs (sixth read, A4)
    (7, "P1"): ("Study's expectation: Holds, with eight.", "Study's expectation: Holds."),
    (8, "P2"): ("Study's expectation: Holds, with all seven below 0.3.", "Study's expectation: Holds."),
    # the analyses that foresaw step 14's verdicts, quoted in short (sixth read, B6)
    (14, "P1"): ("the file's analysis, written before any bound, says P1 is expected to fail",
                 "the file's analysis, written before any bound: with no source placing the flame, the bound takes the "
                 "largest share of an emitter's directions that strike the facing half, at least a quarter at the half's "
                 "end edge, so P1 is expected to fail"),
    (14, "P2"): ("the file's analysis says P2 is expected to fail",
                 "the file's analysis: with no source for the share of the vent gas that passes the neighbour, the "
                 "whole of it counts, and its flux over 21.39 s is expected to exceed 5.96 kJ by a wide margin, so P2 "
                 "is expected to fail"),
    (14, "P6"): ("the file's analysis says P6 is expected to hold",
                 "the file's analysis: the bound is the neighbour's stored energy, 65,520 J, so P6 is expected to hold"),
    (11, "P4"): ("the smallest radial conductivity", "the smallest conductivity across the layers"),
    (15, "P2"): ("registered with it: 7,062 J", "registered with it: 7.06 kJ"),
    # step 6's six runs on which these two rest are reported in the supplement's Section S3: a pointer, no removal
    (12, "P1"): ("fixed by Stage 6's records", "fixed by Stage 6's records (SREFREGISTRY)"),
    (12, "P2"): ("(Stage 6, with other tabs)", "(Stage 6, with other tabs; SREFREGISTRY)"),
}


def short_date(d):
    """2026-10-10 as 10 Oct (Table S1's push dates, all in 2026)."""
    y, m, dd = d.split("-")
    assert y == "2026"
    return "%d %s" % (int(dd), ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][int(m) - 1])


def unreported(stage, lab):
    u = UNREPORTED.get(int(stage), {})
    return u.get("all") or u.get(lab, "")

STEPS = [
    # step, question, file, registered (UTC date)
    (1, "Passive kinetics along the archived histories of the earlier two-cell study: when the chemistry starts at the hot spot, the mean and the lumped node", "predictions.md", "2026-10-10"),
    (2, "The reaction heat fed back, one way, to both neighbours", "predictions.md", "2026-10-10"),
    (3, "The onsets over 200 kinetic draws and 30 thermal draws", "predictions_stage3.md", "2026-10-12"),
    (4, "Which submodel of the kinetic posterior sets the lead of the hot spot", "predictions_v11.md", "2026-10-16"),
    (5, "The cans in contact and joined by tabs, against the sixteen measured tests", "predictions_v12.md", "2026-10-21"),
    (6, "Why the model does not propagate: propagation read at 150 C, the least onset temperature of propagation in Fransson et al.'s tests, and the trigger released over the two measured rise times", "predictions_stage6.md", "2026-10-23"),
    (7, "Seven ignition criteria scored test by test, each test with its own trigger", "predictions_stage7.md", "2026-10-26"),
    (8, "The delivered fraction of the ejected energy that each test's outcome requires", "predictions_stage8.md", "2026-10-26"),
    (9, "The delivered fraction read from each test's time and peak", "predictions_stage9.md", "2026-10-29"),
    (10, "The one published history, the thermocouple's angle and held-out scores", "predictions_stage10.md", "2026-10-30"),
    (11, "Bands of the earlier steps' main numbers under four kinetic draws chosen by rank and four thermal draws at the extremes", "predictions_stage11.md", "2026-11-02"),
    (12, "The trigger held to calorimetry's body energy and one ejected energy for every test", "predictions_stage12.md", "2026-11-03"),
    (13, "Reduced models of each threshold: skin conduction and an ignition temperature", "predictions_stage13.md", "2026-11-16"),
    (14, "What each path can deliver to the neighbour, bounded from published inputs", "predictions_stage14.md", "2026-11-17"),
    (15, "The resolved neighbour's own runaway: a reactive cross-section and three-dimensional searches", "predictions_stage15.md", "2026-11-18"),
    (16, "The resolved needs and a second weak-trigger threshold in three dimensions, and a refinement at a need", "predictions_stage16.md", "2026-11-24"),
]


def tex(s):
    return (s.replace("\\", "\\textbackslash{}").replace("%", "\\%").replace("_", "\\_").replace("&", "\\&")
            .replace("#", "\\#").replace("~", "\\~{}").replace(" C,", "\\degC,").replace(" C ", "\\degC{} ")
            .replace(" C)", "\\degC)").replace(" C.", "\\degC."))


def shown(text):
    """The registry as the supplement shows it: the records' test names and "Stage" written as the paper writes them
    (M50_PT_Exp1 as PT-Exp1, Stage 7 as step 7), and "the file" named as the predictions file. Nothing else changes."""
    import re
    t = re.sub(r"\bM50_(PT|PP|ST|SP)_Exp(\d)", r"\1-Exp\2", text)
    t = re.sub(r"\b(PT|PP|ST|SP)_Exp(\d)", r"\1-Exp\2", t)
    t = re.sub(r"\bStages (\d+) (to|and) (\d+)", r"steps \1 \2 \3", t)
    t = re.sub(r"\bStage (\d+)", r"step \1", t)
    t = t.replace("the stage's question", "the step's question").replace("this stage's", "this step's")
    t = t.replace("the file's analysis", "the predictions file's analysis").replace("the file records",
                                                                                  "the predictions file records")
    t = t.replace("the bullet says", "the plan's line for it says").replace("Brief's expectation", "Plan's expectation")
    return t


def typeset(t):
    """After escaping: the records' plain symbols set as the paper sets them (E_b, E_e, f_max, f_t, f* and E*, and
    degrees Celsius after a number). The words are not changed."""
    import re
    t = t.replace("E\\_b", "$E_\\mathrm{b}$").replace("E\\_e", "$E_\\mathrm{e}$")
    t = t.replace("f\\_max", "$f_\\mathrm{max}$").replace("f\\_t", "$f_\\mathrm{t}$")
    t = re.sub(r"\b([fE])\*", lambda m: "$" + m.group(1) + "^*$", t)
    t = re.sub(r"(\d) C\b", lambda m: m.group(1) + "\\,\\textdegree C", t)
    return t


def basis_quote(basis):
    """The quoted words of a foreseen failure's basis, without its file and line references."""
    import re
    q = re.findall(r'"([^"]+)"', basis)
    return " ... ".join("\u201c%s\u201d" % x for x in q) if q else basis


def main():
    os.makedirs(OUTD, exist_ok=True)
    os.makedirs(OUTT, exist_ok=True)
    old = list(csv.DictReader(open(os.path.join(ROOT, "manuscript", "data", "predictions_by_stage.csv"))))
    v13 = json.load(open(os.path.join(RES, "stage13_scorecard.json")))
    v14 = json.load(open(os.path.join(RES, "stage14_scorecard.json")))
    v15 = json.load(open(os.path.join(RES, "stage15_scorecard.json")))["scorecard"]["predictions"]
    p16 = os.path.join(RES, "stage16_scorecard.json")
    v16 = json.load(open(p16))["scorecard"]["predictions"] if os.path.exists(p16) else {}

    def verdict(stage, lab):
        if stage == 13:
            return "held" if v13[lab]["holds"] else "failed"
        if stage == 14:
            return "held" if v14[lab]["holds"] else "failed"
        if stage == 16:
            h = v16.get(lab, {}).get("held")
            return "held" if h is True else ("failed" if h is False else "not scored")
        return v15[lab]["verdict"]

    rows = []
    def attributed(stage, exp):
        """Steps 1 and 2 had one predictions file and no separate plan's estimates: their expectations are the study's."""
        if str(stage) not in ("1", "2") or exp == "none recorded":
            return exp
        if exp.startswith("Central estimate"):
            return "Study's central estimate" + exp[len("Central estimate"):]
        return "Study's expectation: " + (exp if exp.startswith("P5") else exp[0].lower() + exp[1:])

    for r in old:
        rows.append({"stage": r["stage"], "prediction": r["prediction"], "statement": r["statement"],
                     "expectation": attributed(r["stage"], r["expectation"]), "verdict": r["verdict"],
                     "foreseen": r["foreseen"] if r["verdict"] == "failed" else "",
                     "foreseen_basis": r["foreseen_basis"] if r["verdict"] == "failed" else "", "source": r["source"]})
    for st, lab, stmt, exp, src in NEW:
        v = verdict(st, lab)
        rows.append({"stage": str(st), "prediction": lab, "statement": stmt, "expectation": exp, "verdict": v,
                     "foreseen": ("yes" if (st, lab) in FORESEEN else "no") if v == "failed" else "",
                     "foreseen_basis": "", "source": src})
    for r in rows:
        why = unreported(r["stage"], r["prediction"])
        r["in_table_s2"] = "no" if why else "yes"
        r["not_listed_because"] = why
        key = (int(r["stage"]), r["prediction"])
        r["expectation_in_table_s2"] = ""
        if not why:
            e = r["expectation"]
            if key in STRIP:
                o, n = STRIP[key]
                assert e.count(o) == 1, (key, o)
                e = e.replace(o, n)
            r["expectation_in_table_s2"] = e
    assert sum(r["in_table_s2"] == "yes" for r in rows) + sum(r["in_table_s2"] == "no" for r in rows) == len(rows)
    with open(os.path.join(OUTD, "predictions_registry.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows([dict(r, expectation_in_table_s2=r["expectation_in_table_s2"].replace(
            "SREFREGISTRY", "Section S3 of the supplement")) for r in rows])

    steps = []
    for n, q, f, d in STEPS:
        rr = [r for r in rows if int(r["stage"]) == n]
        ll = [r for r in rr if r["in_table_s2"] == "yes"]
        steps.append({"step": n, "question": q, "predictions_file": f, "registered_utc_date": d,
                      "committed": len(rr), "held": sum(r["verdict"] == "held" for r in rr),
                      "failed": sum(r["verdict"] == "failed" for r in rr),
                      "failed_foreseen": sum(r["foreseen"] == "yes" for r in rr),
                      "listed": len(ll), "listed_held": sum(r["verdict"] == "held" for r in ll),
                      "listed_failed": sum(r["verdict"] == "failed" for r in ll),
                      "listed_failed_foreseen": sum(r["foreseen"] == "yes" for r in ll)})
    with open(os.path.join(OUTD, "steps.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(steps[0].keys()))
        w.writeheader()
        w.writerows(steps)

    keys = ("committed", "held", "failed", "failed_foreseen", "listed", "listed_held", "listed_failed",
            "listed_failed_foreseen")
    tot = {k: sum(s[k] for s in steps) for k in keys}
    t1 = [r"\begin{table}[!htbp]", r"\centering", r"\scriptsize",
          r"\caption{The study's sixteen steps, each with its own predictions pushed to the public repository before "
          r"its runs (the push's date, UTC, in 2026): how many predictions each registered, and how many held and "
          r"failed among those Table~\ref{tab:s-registry} lists, whose runs the main text or this supplement reports, "
          r"and among the others; a listed failure is foreseen when the predictions file recorded it as expected "
          r"before the runs.}",
          r"\label{tab:s-steps}", r"\setlength{\tabcolsep}{2pt}",
          r"\begin{tabular}{rp{0.345\textwidth}lrrrrrrr}", r"\toprule",
          r" & & & & \multicolumn{4}{c}{Listed in Table~\ref{tab:s-registry}} & \multicolumn{2}{c}{Not listed} \\",
          r"\cmidrule(lr){5-8}\cmidrule(lr){9-10}",
          r"Step & What it asked & Pushed & Predictions & All & Held & Failed & Foreseen & Held & Failed \\",
          r"\midrule"]
    for s in steps:
        nh, nf = s["held"] - s["listed_held"], s["failed"] - s["listed_failed"]
        t1.append("%d & %s & %s & %d & %d & %d & %d & %d & %d & %d \\\\" % (
            s["step"], tex(s["question"]), short_date(s["registered_utc_date"]), s["committed"], s["listed"], s["listed_held"],
            s["listed_failed"], s["listed_failed_foreseen"], nh, nf))
    t1 += [r"\midrule", r"All & & & %d & %d & %d & %d & %d & %d & %d \\" % (
        tot["committed"], tot["listed"], tot["listed_held"], tot["listed_failed"], tot["listed_failed_foreseen"],
        tot["held"] - tot["listed_held"], tot["failed"] - tot["listed_failed"]),
           r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    open(os.path.join(OUTT, "s1_steps.tex"), "w").write("\n".join(t1) + "\n")

    t2 = [r"{\sloppy\scriptsize\setlength{\tabcolsep}{3pt}", r"\begin{longtable}{>{\raggedright\arraybackslash}p{0.05\textwidth}>{\raggedright\arraybackslash}p{0.065\textwidth}>{\raggedright\arraybackslash}p{0.425\textwidth}>{\raggedright\arraybackslash}p{0.24\textwidth}>{\raggedright\arraybackslash}p{0.1\textwidth}}",
          (r"\caption{The %d predictions whose runs the main text or this supplement reports, of the %d the study "
           r"registered: %d held and %d failed, %d of the failures foreseen. Each is given as its predictions file states it "
           r"(shortened where long), with the expectation recorded before the runs and the verdict. Labels are defined in "
           r"Section~\ref{sec:s-key}.}\label{tab:s-registry}\\") % (tot["listed"], tot["committed"], tot["listed_held"],
                                                                   tot["listed_failed"], tot["listed_failed_foreseen"]),
          r"\toprule", r"Step & & Prediction & Expectation & Verdict \\", r"\midrule", r"\endfirsthead",
          r"\multicolumn{5}{l}{\textit{Continued}} \\", r"\toprule", r"Step & & Prediction & Expectation & Verdict \\", r"\midrule", r"\endhead"]
    for r in rows:
        if r["in_table_s2"] != "yes":
            continue
        v = r["verdict"] + (", foreseen" if r["foreseen"] == "yes" else "")
        exp = r["expectation_in_table_s2"]
        if r["foreseen"] == "yes" and "fail" not in exp.lower():
            exp = exp.rstrip(".") + "; the predictions file's analysis: " + basis_quote(r["foreseen_basis"])
        t2.append("%s & %s & %s & %s & %s \\\\" % (r["stage"], tex(r["prediction"]), typeset(tex(shown(r["statement"]))),
                                                  typeset(tex(shown(exp))).replace("SREFREGISTRY", r"Section~\ref{sec:s-registry}"), v))
    t2 += [r"\bottomrule", r"\end{longtable}", r"}"]
    open(os.path.join(OUTT, "s2_registry.tex"), "w").write("\n".join(t2) + "\n")
    print("registry: %d predictions, %d held, %d failed, %d of the failures foreseen; Table S2 lists %d, %d held, "
          "%d failed, %d foreseen" % (tot["committed"], tot["held"], tot["failed"], tot["failed_foreseen"],
                                      tot["listed"], tot["listed_held"], tot["listed_failed"],
                                      tot["listed_failed_foreseen"]))


if __name__ == "__main__":
    main()
