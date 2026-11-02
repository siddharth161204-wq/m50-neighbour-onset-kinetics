#!/usr/bin/env python3
"""The manuscript's four tables (Brief 20, M4), each written as a LaTeX table from the results files.

T1 the sixteen tests: connection, the trigger's measured peak, its body energy E_b (Stage 7), the ejected energy E_e
   (Stage 8), the outcome, the time to propagation and the neighbour's measured maximum (Fransson et al. 2024, Tables
   3 and 4; inputs/fransson2024/m50_tests.csv).
T2 the model's parameters with their sources (manuscript/data/parameters.csv, extracted from DECISIONS.md and the code
   and checked against them).
T3 per test: f*(C1) and f*(C2) (Stage 8), f_t(C2) or f_max (Stage 9), and Stage 11's bands where it ran.
T4 the predictions by stage: committed, held, failed and foreseen (manuscript/data/predictions_by_stage.csv).

Usage: python3 make_manuscript_tables.py [--res ../results] [--out ../manuscript/tables] [--only 1,2,3,4]
"""
import argparse, csv, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
ORDER = [f"M50_{p}_Exp{k}" for p in ("PT", "PP", "ST", "SP") for k in (1, 2, 3, 4)]


def short(t):
    return t.replace("M50_", "").replace("_", r"\_")


def rows(path):
    with open(path) as fh:
        return list(csv.DictReader(fh))


def fnum(x, nd=None):
    """A fraction as written in the results: no trailing zeros beyond what the value holds."""
    x = float(x)
    if x == 0:
        return "0"
    s = f"{x:.{nd}f}" if nd is not None else f"{x:.6f}".rstrip("0").rstrip(".")
    return s


def bracket(s):
    """Stage 8's bracket string, "(lo, hi]" or "0", for LaTeX."""
    s = s.strip()
    if s in ("0", "0.0"):
        return "0"
    lo, hi = s.strip("(]").split(",")
    return f"({fnum(lo)}, {fnum(hi)}]"


def cat(c):
    return {"cell movement": "c.m.", "": "--"}.get(c, c)


def t1(res, out):
    tests = {r["test"]: r for r in rows(os.path.join(ROOT, "inputs", "fransson2024", "m50_tests.csv"))}
    trig = {r["test"]: r for r in rows(os.path.join(res, "stage7_triggers.csv")) if r["kind"] == "test"}
    ej = {r["id"]: r for r in rows(os.path.join(res, "stage8_ejected.csv")) if r["kind"] == "test"}
    lines = [r"\begin{table}[t]", r"\centering", r"\footnotesize", r"\setlength{\tabcolsep}{2.7pt}",
             r"\caption{The sixteen two-cell LG M50 tests of Fransson et al.~\cite{fransson2024exploring} (their Tables 3 and 4), "
             r"with the trigger's body energy $E_\mathrm{b}$ that puts the model's trigger at the measured peak at the central "
             r"contact over 21.39~s, and the ejected energy $E_\mathrm{e}=3.105\,E_\mathrm{b}$. Times run from the trigger's "
             r"runaway to the neighbour's onset. The two maxima marked $^{a}$ may not be the neighbour's surface and are read as "
             r"exploratory. Category, Fransson et al.'s failure category: 1, the trigger's nail-penetration failure; 2, failure "
             r"in the propagating cell; 4, sidewall rupture of the trigger; c.m., ``cell movement'' in the X-ray camera's "
             r"field of view, given in place of a category; a dash, none given.}",
             r"\label{tab:tests}",
             r"\begin{tabular}{llrrrlrrc}", r"\toprule",
             r"Test & Connection & \multicolumn{1}{c}{Trigger} & \multicolumn{1}{c}{$E_\mathrm{b}$} & "
             r"\multicolumn{1}{c}{$E_\mathrm{e}$} & Propagated & \multicolumn{1}{c}{Time} & \multicolumn{1}{c}{Neighbour} & Category \\",
             r" & & peak (\textdegree C) & (kJ) & (kJ) & & (s) & max. (\textdegree C) & \\", r"\midrule"]
    for t in ORDER:
        r = tests[t]
        prop = r["propagated"] == "Yes"
        nm = r["neighbour_max_C"] + (r"$^{a}$" if (not prop and float(r["neighbour_max_C"]) > 500) else "")
        lines.append(f"{short(t)} & {r['connection']} & {r['trigger_max_C']} & {float(trig[t]['E_J']) / 1e3:.1f} & "
                     f"{float(ej[t]['E_e_J']) / 1e3:.1f} & {'yes' if prop else 'no'} & "
                     f"{r['time_to_propagation_s'] if prop else ''} & {nm} & {cat(r['failure_category'])} \\\\")
        if t in ("M50_PP_Exp4",):
            lines.append(r"\midrule")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    open(os.path.join(out, "t1_tests.tex"), "w").write("\n".join(lines) + "\n")
    print("wrote t1_tests.tex")


def t3(res, out):
    fr = {r["test"]: r for r in rows(os.path.join(res, "stage9_fractions.csv"))}
    s11 = os.path.exists(os.path.join(res, "stage11_bands.json"))
    bands = json.load(open(os.path.join(res, "stage11_bands.json")))["A2_B2"] if s11 else {}
    ov = rows(os.path.join(res, "stage11_overshoot.csv")) if s11 else []
    tr = rows(os.path.join(res, "stage11_times.csv")) if s11 else []

    def band(crit, t):
        b = bands.get(f"{crit}_{t}")
        if not b:
            return ""
        vals = [v for kind in ("kinetic", "thermal") for v in b[kind]["f_star"].values()] + [b["mean"]]
        if any(v in (None, "above 1") for v in vals):
            return "above 1" if "above 1" in vals else ""
        lo, hi = min(vals), max(vals)
        return fnum(lo) if lo == hi else f"{fnum(lo)}--{fnum(hi)}"

    def over(t):
        vs = [float(r["overshoot_K"]) for r in ov if r["test"] == t and r["overshoot_K"] not in ("", None)]
        return "" if not vs else f"${min(vs):.1f}$ to ${max(vs):.1f}$"

    def cross(t):
        rs = [r for r in tr if r["test"] == t]
        if not rs:
            return ""
        vs = [r["t_draw_s"] for r in rs]
        n_none = sum(1 for v in vs if v in ("", None))
        num = [float(v) for v in vs if v not in ("", None)]
        s = f"{min(num):.0f}--{max(num):.0f}" if num else ""
        return s + (f" ({n_none} none)" if n_none else "")

    def band1(crit, t):
        return band(crit, t)

    lines = [r"\begin{table}[p]", r"\centering", r"\scriptsize",
             r"\caption{The fractions of the ejected energy each test needs in the model, and Stage 11's ranges. (a) $f^*$(C1) "
             r"and $f^*$(C2): the threshold bracket $(\mathrm{lo},\mathrm{hi}]$ at which the hot spot (C1) or the lumped "
             r"neighbour (C2) reaches 255.7\textdegree C with the 21.39~s delivery, 0 where no delivery is needed. "
             r"$f_\mathrm{t}$(C2): the fraction at which the lumped neighbour's crossing comes at the measured time ($^{b}$ the "
             r"search ended at the threshold, its bracket given). $f_\mathrm{max}$: the fraction at which the far face peaks at "
             r"the measured maximum ($^{a}$ exploratory). (b) Over the posterior mean and Stage 11's draws: $f^*$(C1) and "
             r"$f^*$(C2) over the nine (four kinetic, four thermal, the mean), the far face's peak at $f=0$ less the measured "
             r"maximum over the central case, the four thermal draws and the two contact brackets, and the lumped neighbour's "
             r"crossing at $f_\mathrm{t}$(C2) under the four kinetic draws, with the number that do not cross within 900~s.}",
             r"\label{tab:fractions}",
             r"\begin{tabular}{llll}", r"\multicolumn{4}{l}{(a) Stages 8 and 9, at the posterior mean} \\", r"\toprule",
             r"Test & $f^*$(C1) & $f^*$(C2) & $f_\mathrm{t}$(C2) or $f_\mathrm{max}$ \\", r"\midrule"]
    for t in ORDER:
        r = fr[t]
        prop = r["propagated"] == "True"
        if prop:
            st = r["ft_C2_status"]
            if st == "threshold":
                read = f"({fnum(r['ft_C2_lo'])}, {fnum(r['ft_C2_hi'])}]$^{{b}}$"
            else:
                read = fnum(r["ft_C2"], 4 if float(r["ft_C2"]) < 0.01 else None)
        else:
            read = fnum(r["fmax"]) + (r"$^{a}$" if r["fmax_exploratory"] == "True" else "")
        lines.append(f"{short(t)} & {bracket(r['fC1_stage8'])} & {bracket(r['fC2_stage8'])} & {read} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    if s11:
        lines += [r"\par\bigskip", r"\begin{tabular}{lllll}",
                  r"\multicolumn{5}{l}{(b) Stage 11: ranges over the posterior mean and the draws} \\", r"\toprule",
                  r"Test & $f^*$(C1) & $f^*$(C2) & Far face at & C2 crossing, \\",
                  r" & & & $f=0$ (K) & kinetic draws (s) \\", r"\midrule"]
        for t in ORDER:
            b1, b2, o, c = band1("C1", t), band1("C2", t), over(t), cross(t)
            if any((b1, b2, o, c)):
                lines.append(f"{short(t)} & {b1} & {b2} & {o} & {c} \\\\")
        lines += [r"\bottomrule", r"\end{tabular}"]
    lines += [r"\end{table}"]
    open(os.path.join(out, "t3_fractions.tex"), "w").write("\n".join(lines) + "\n")
    print("wrote t3_fractions.tex")


def t2(res, out):
    p = os.path.join(ROOT, "manuscript", "data", "parameters_table.csv")
    if not os.path.exists(p):
        print("no parameters_table.csv yet")
        return
    lines = [r"\begin{table}[p]", r"\centering", r"\scriptsize",
             r"\caption{The model's parameters and their sources: a published source, the two-cell study whose geometry and "
             r"solver this study takes~\cite{satte2026twocell}, or an entry of this study's decisions log (D, in the "
             r"repository~\cite{satte2026repo}). Values in parentheses are brackets run as sensitivities or the ranges of the "
             r"thermal draws.}",
             r"\label{tab:params}",
             r"\renewcommand{\arraystretch}{0.92}",
             r"\begin{tabular}{p{0.29\textwidth}p{0.37\textwidth}p{0.24\textwidth}}", r"\toprule",
             r"Quantity & Value & Source \\", r"\midrule"]
    group = None
    for r in rows(p):
        if r["group"] != group:
            group = r["group"]
            lines.append(r"\multicolumn{3}{l}{\textit{" + group + r"}} \\")
        lines.append(f"{r['quantity']} & {r['value']} & {r['source']} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    open(os.path.join(out, "t2_parameters.tex"), "w").write("\n".join(lines) + "\n")
    print("wrote t2_parameters.tex")


def t4(res, out):
    p = os.path.join(ROOT, "manuscript", "data", "predictions_by_stage.csv")
    if not os.path.exists(p):
        print("no predictions_by_stage.csv yet")
        return
    rs = rows(p)
    names = {1: "1 and 2: passive and reactive onset", 3: "3: onset over the posterior and thermal draws",
             4: "4: which submodel sets the lead", 5: "5: neighbours against the tests",
             6: "6: the paper's 150\\textdegree C criterion; matched trigger", 7: "7: seven criteria, test by test",
             8: "8: the delivered fraction $f^*$", 9: "9: fractions from times and peaks",
             10: "10: one history; held-out scores", 11: "11: bands under the draws"}
    lines = [r"\begin{table}[t]", r"\centering", r"\footnotesize",
             r"\caption{The predictions by stage: committed before the stage's runs, held, failed, and of the failures those "
             r"foreseen, which the predictions file had recorded before the runs as expected to fail, as already fixed by earlier "
             r"records or an energy balance, or as failing under a condition it named that then held. The stages' own texts "
             r"label 17 of the 21 through Stage 10 so (Supplement S2). Every prediction, its expectation and its verdict are in "
             r"the supplement.}",
             r"\label{tab:predictions}",
             r"\begin{tabular}{p{0.44\textwidth}rrrr}", r"\toprule",
             r"Stage & Committed & Held & Failed & Foreseen \\", r"\midrule"]
    tot = [0, 0, 0, 0]
    for st in (1, 3, 4, 5, 6, 7, 8, 9, 10, 11):
        g = [r for r in rs if int(r["stage"]) in ((1, 2) if st == 1 else (st,))]
        c = len(g)
        h = sum(r["verdict"] == "held" for r in g)
        f = sum(r["verdict"] == "failed" for r in g)
        fo = sum(r["verdict"] == "failed" and r["foreseen"] == "yes" for r in g)
        if st <= 10:
            tot = [tot[0] + c, tot[1] + h, tot[2] + f, tot[3] + fo]
        lines.append(f"{names[st]} & {c} & {h} & {f} & {fo} \\\\")
        if st == 10:
            lines.append(r"\midrule")
            lines.append(f"Stages 1 to 10 & {tot[0]} & {tot[1]} & {tot[2]} & {tot[3]} \\\\")
            lines.append(r"\midrule")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    open(os.path.join(out, "t4_predictions.tex"), "w").write("\n".join(lines) + "\n")
    print("wrote t4_predictions.tex")


def s2(res, out):
    """The supplement's full prediction table: every prediction of Stages 1 to 11, its expectation and its verdict."""
    p = os.path.join(ROOT, "manuscript", "data", "predictions_by_stage.csv")
    if not os.path.exists(p):
        print("no predictions_by_stage.csv yet")
        return
    esc = lambda x: (x or "").replace("&", r"\&").replace("%", r"\%").replace("_", r"\_").replace("#", r"\#")
    lines = [r"{\sloppy\footnotesize", r"\begin{longtable}{>{\raggedright\arraybackslash}p{0.062\textwidth}>{\raggedright\arraybackslash}p{0.07\textwidth}>{\raggedright\arraybackslash}p{0.408\textwidth}>{\raggedright\arraybackslash}p{0.2\textwidth}>{\raggedright\arraybackslash}p{0.1\textwidth}}",
             r"\caption{Every prediction, as its predictions file states it (shortened), with the expectation recorded before the "
             r"runs and the verdict. Foreseen: a failure the predictions file recorded before the runs as expected to fail, as "
             r"already fixed by earlier records or an energy balance, or as failing under a condition it named that then "
             r"held. The verdicts of Stage 11 are its scorecard's.}\label{tab:s-predictions}\\",
             r"\toprule", r"Stage & & Prediction & Expectation & Verdict \\", r"\midrule", r"\endfirsthead",
             r"\toprule", r"Stage & & Prediction & Expectation & Verdict \\", r"\midrule", r"\endhead"]
    for r in rows(p):
        v = r["verdict"]
        if v == "failed" and r.get("foreseen") == "yes":
            v = "failed, foreseen"
        lines.append(f"{r['stage']} & {esc(r['prediction'])} & {esc(r['statement'])} & {esc(r['expectation'])} & {v} \\\\")
    lines += [r"\bottomrule", r"\end{longtable}", r"}"]
    open(os.path.join(out, "s2_predictions.tex"), "w").write("\n".join(lines) + "\n")
    print("wrote s2_predictions.tex")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", default=os.path.join(ROOT, "results"))
    ap.add_argument("--out", default=os.path.join(ROOT, "manuscript", "tables"))
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    only = [int(x) for x in a.only.split(",") if x] or [1, 2, 3, 4, 5]
    for k in only:
        {1: t1, 2: t2, 3: t3, 4: t4, 5: s2}[k](a.res, a.out)
