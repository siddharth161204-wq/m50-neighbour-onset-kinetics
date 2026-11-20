"""The registry of the study's 98 predictions and its fifteen steps, for the rebuilt manuscript's supplement.

Rows 1 to 74 (Stages 1 to 12) are manuscript/data/predictions_by_stage.csv unchanged. Rows 75 to 98 (Stages 13 to
15) are shortened here from predictions_stage13.md, predictions_stage14.md and predictions_stage15.md (each row names
its file and line), with the verdicts read from results/stage13_scorecard.json, stage14_scorecard.json and
stage15_scorecard.json. A failure counts as foreseen under the rule of the counts file
(manuscript/data/predictions_by_stage_counts.md): the predictions file recorded it, before the runs, as expected or as
fixed by its design or by earlier records.

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
     "uncertain", "predictions_stage15.md:110"),
    (15, "P2", "For PT_Exp4 with the 21.39 s delivery, E*(C8) lies between 6 and 10 kJ.", "likely",
     "predictions_stage15.md:112"),
    (15, "P3", "In at least three of the four tests E*(C8) is at least 1.25 times the whole-cell clock's threshold E*(C2).",
     "likely for the three strong triggers, uncertain for ST_Exp3", "predictions_stage15.md:114"),
    (15, "P4", "For PT_Exp4, in the run at the upper end of the bracket, the mean crosses 255.7 C between 150 and 400 s after the trigger's start.",
     "likely", "predictions_stage15.md:116"),
    (15, "P5", "In that run the far face reads more than 15 K above 197.3 C, the reading from which the measured neighbour jumped, when its own jump begins.",
     "likely", "predictions_stage15.md:118"),
    (15, "P6", "The constant power after the 5.0 kJ pulse that brings the cell's own runaway to 271.5 s lies between 5 and 25 W.",
     "likely", "predictions_stage15.md:120"),
    (15, "P7", "Under none of four kinetic draws and not with the aged SEI does the resolved cell run away at PT_Exp4's 5,045 J, and the least shift of the rate laws that makes it run away is 10 K or more.",
     "likely", "predictions_stage15.md:122"),
    (15, "P8", "PT_Exp4's run with 6,209 J over 240 s, carried to 900 s, runs away.", "likely", "predictions_stage15.md:124"),
]
FORESEEN = {(14, "P1"), (14, "P2")}

STEPS = [
    # step, question, file, registered (UTC date)
    (1, "Passive kinetics along the archived histories of the earlier two-cell study: when the chemistry starts at the hot spot, the mean and the lumped node", "predictions.md", "2026-10-10"),
    (2, "The reaction heat fed back, one way, to both neighbours", "predictions.md", "2026-10-10"),
    (3, "The onsets over 200 kinetic draws and 30 thermal draws", "predictions_stage3.md", "2026-10-12"),
    (4, "Which submodel of the kinetic posterior sets the lead of the hot spot", "predictions_v11.md", "2026-10-16"),
    (5, "The cans in contact and joined by tabs, against the sixteen measured tests", "predictions_v12.md", "2026-10-21"),
    (6, "Why the model does not propagate: the tests' 150 C criterion and the trigger's measured durations", "predictions_stage6.md", "2026-10-23"),
    (7, "Seven ignition criteria scored test by test, each test with its own trigger", "predictions_stage7.md", "2026-10-26"),
    (8, "The delivered fraction of the ejected energy that each test's outcome requires", "predictions_stage8.md", "2026-10-26"),
    (9, "The delivered fraction read from each test's time and peak", "predictions_stage9.md", "2026-10-29"),
    (10, "The one published history, the thermocouple's angle and held-out scores", "predictions_stage10.md", "2026-10-30"),
    (11, "Bands of the central numbers under kinetic and thermal draws chosen by rank", "predictions_stage11.md", "2026-11-02"),
    (12, "The trigger held to calorimetry's body energy and one ejected energy for every test", "predictions_stage12.md", "2026-11-03"),
    (13, "The mechanism of each threshold: reduced models of skin conduction and of an ignition temperature", "predictions_stage13.md", "2026-11-16"),
    (14, "What each path can deliver to the neighbour, bounded from published inputs", "predictions_stage14.md", "2026-11-17"),
    (15, "The resolved neighbour's own runaway: a reactive cross-section and three-dimensional searches", "predictions_stage15.md", "2026-11-18"),
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

    def verdict(stage, lab):
        if stage == 13:
            return "held" if v13[lab]["holds"] else "failed"
        if stage == 14:
            return "held" if v14[lab]["holds"] else "failed"
        return v15[lab]["verdict"]

    rows = []
    for r in old:
        rows.append({"stage": r["stage"], "prediction": r["prediction"], "statement": r["statement"],
                     "expectation": r["expectation"], "verdict": r["verdict"],
                     "foreseen": r["foreseen"] if r["verdict"] == "failed" else "",
                     "foreseen_basis": r["foreseen_basis"] if r["verdict"] == "failed" else "", "source": r["source"]})
    for st, lab, stmt, exp, src in NEW:
        v = verdict(st, lab)
        rows.append({"stage": str(st), "prediction": lab, "statement": stmt, "expectation": exp, "verdict": v,
                     "foreseen": ("yes" if (st, lab) in FORESEEN else "no") if v == "failed" else "",
                     "foreseen_basis": "", "source": src})
    with open(os.path.join(OUTD, "predictions_registry.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    steps = []
    for n, q, f, d in STEPS:
        rr = [r for r in rows if int(r["stage"]) == n]
        steps.append({"step": n, "question": q, "predictions_file": f, "registered_utc_date": d,
                      "committed": len(rr), "held": sum(r["verdict"] == "held" for r in rr),
                      "failed": sum(r["verdict"] == "failed" for r in rr),
                      "failed_foreseen": sum(r["foreseen"] == "yes" for r in rr)})
    with open(os.path.join(OUTD, "steps.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(steps[0].keys()))
        w.writeheader()
        w.writerows(steps)

    tot = {k: sum(s[k] for s in steps) for k in ("committed", "held", "failed", "failed_foreseen")}
    t1 = [r"\begin{table}[!htbp]", r"\centering", r"\scriptsize",
          r"\caption{The study's fifteen steps, each with its own predictions committed to the public repository "
          r"and pushed before its runs (the date is that of the push, UTC), and how many held and failed; a failure "
          r"is foreseen when the predictions file recorded it as expected before the runs.}",
          r"\label{tab:s-steps}", r"\setlength{\tabcolsep}{3pt}", r"\begin{tabular}{rp{0.44\textwidth}lrrrr}", r"\toprule",
          r"Step & What it asked & Registered & Predictions & Held & Failed & Foreseen \\", r"\midrule"]
    for s in steps:
        t1.append("%d & %s & %s & %d & %d & %d & %d \\\\" % (s["step"], tex(s["question"]), s["registered_utc_date"],
                                                         s["committed"], s["held"], s["failed"], s["failed_foreseen"]))
    t1 += [r"\midrule", r"All & & & %d & %d & %d & %d \\" % (tot["committed"], tot["held"], tot["failed"],
                                                           tot["failed_foreseen"]),
           r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    open(os.path.join(OUTT, "s1_steps.tex"), "w").write("\n".join(t1) + "\n")

    t2 = [r"{\sloppy\scriptsize\setlength{\tabcolsep}{3pt}", r"\begin{longtable}{>{\raggedright\arraybackslash}p{0.05\textwidth}>{\raggedright\arraybackslash}p{0.065\textwidth}>{\raggedright\arraybackslash}p{0.425\textwidth}>{\raggedright\arraybackslash}p{0.24\textwidth}>{\raggedright\arraybackslash}p{0.1\textwidth}}",
          r"\caption{Every prediction, as its predictions file states it (shortened), with the expectation recorded "
          r"before the runs and the verdict. Labels are defined in Section~\ref{sec:s-key}.}\label{tab:s-registry}\\",
          r"\toprule", r"Step & & Prediction & Expectation & Verdict \\", r"\midrule", r"\endfirsthead",
          r"\toprule", r"Step & & Prediction & Expectation & Verdict \\", r"\midrule", r"\endhead"]
    for r in rows:
        v = r["verdict"] + (", foreseen" if r["foreseen"] == "yes" else "")
        exp = r["expectation"]
        if r["foreseen"] == "yes" and "fail" not in exp.lower():
            exp = exp.rstrip(".") + "; the predictions file's analysis: " + basis_quote(r["foreseen_basis"])
        t2.append("%s & %s & %s & %s & %s \\\\" % (r["stage"], tex(r["prediction"]), tex(shown(r["statement"])),
                                                  tex(shown(exp)), v))
    t2 += [r"\bottomrule", r"\end{longtable}", r"}"]
    open(os.path.join(OUTT, "s2_registry.tex"), "w").write("\n".join(t2) + "\n")
    print("registry: %d predictions, %d held, %d failed, %d of the failures foreseen" %
          (tot["committed"], tot["held"], tot["failed"], tot["failed_foreseen"]))


if __name__ == "__main__":
    main()
