"""Tables of the rebuilt manuscript (manuscript/rebuild/tables/), written from the inputs and results files.

Table 1, the sixteen tests: Fransson et al.'s measurements (inputs/fransson2024/m50_tests.csv) and the body energy
fitted to each test's trigger peak (results/stage7_triggers.csv).
Table 2, the model's parameters and their sources (the values are the model's inputs, as the code holds them).
Table 3, what each path can deliver: the bounds after their independent read (results/stage14_bounds_corrected.csv).
Table S3, the thresholds and needs of every test (results/stage14_needs.csv, results/stage15_cross_section.json,
results/stage15_table.csv, results/stage15_paper_numbers.json).

No table computes a new quantity: values are read, converted to kJ, or a bracket's ends are printed as they stand.
Usage: python3 src/make_rebuild_tables.py
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rebuild_brackets as RB                     # noqa: E402  (the narrowest bracket on each threshold)
ROOT = os.path.join(HERE, "..")
RES = os.path.join(ROOT, "results")
OUT = os.path.join(ROOT, "manuscript", "rebuild", "tables")

TESTS = ["M50_PT_Exp1", "M50_PT_Exp2", "M50_PT_Exp3", "M50_PT_Exp4", "M50_PP_Exp1", "M50_PP_Exp2", "M50_PP_Exp3",
         "M50_PP_Exp4", "M50_ST_Exp1", "M50_ST_Exp2", "M50_ST_Exp3", "M50_ST_Exp4", "M50_SP_Exp1", "M50_SP_Exp2",
         "M50_SP_Exp3", "M50_SP_Exp4"]


def read_csv(p):
    with open(p) as fh:
        return list(csv.DictReader(fh))


def tex_name(t):
    return t.replace("M50_", "").replace("_", "-")


def kj(x, nd=1):
    return ("%%.%df" % nd) % (float(x) / 1e3)


def databank_mass():
    """The smallest and largest pre-test mass of the Databank's seventeen LG M50 cells (g, two decimals)."""
    m = [float(r["Pre-Test-Cell-Mass-g"]) for r in read_csv(os.path.join(ROOT, "inputs", "databank", "databank_m50_used.csv"))]
    return "%.2f" % min(m), "%.2f" % max(m)


def flame_s():
    """The longest published combustion of a 21700 cell, the bounds' time window (results/stage14_inputs.csv)."""
    return float(next(r for r in read_csv(os.path.join(RES, "stage14_inputs.csv")) if r["key"] == "t_flame_max")["value"])


def table1():
    meas = {r["test"]: r for r in read_csv(os.path.join(ROOT, "inputs", "fransson2024", "m50_tests.csv"))}
    trig = {r["test"]: float(r["E_J"]) for r in read_csv(os.path.join(RES, "stage7_triggers.csv")) if r["kind"] == "test"}
    cat = {"cell movement": "c.m.", "": "--"}
    lines = [r"\begin{table}[!tbp]", r"\centering", r"\footnotesize", r"\setlength{\tabcolsep}{2.6pt}",
             r"\caption{The sixteen two-cell tests of LG M50 cells of Fransson et al.~\cite{fransson2024exploring} "
             r"(their Tables 3 and 4), named as they name them without the prefix M50 (PT and PP connected in parallel, "
             r"ST and SP in series, the second letter naming the cell in the X-ray camera's field of view, the trigger "
             r"or the propagating cell), and the body energy $E_\mathrm{b}$ that puts the model's trigger at the measured "
             r"trigger peak at the central contact when released over 21.39~s. Times run from the trigger's runaway "
             r"to the neighbour's. The two maxima marked $^{a}$ may not be the neighbour's surface and are treated as "
             r"exploratory. Category, Fransson et al.'s failure category: 1, the trigger's nail-penetration failure; "
             r"2, failure in the propagating cell; 4, sidewall rupture of the trigger (3, sidewall melting, is given for "
             r"none of these tests); c.m., ``cell movement'' in the X-ray camera's field of view, given in place of a "
             r"category; a dash, none given. A test propagated when the neighbour's thermocouple shows a second spike.}",
             r"\label{tab:tests}",
             r"\begin{tabular}{llrrlrrc}", r"\toprule",
             r"Test & Connection & Trigger peak & $E_\mathrm{b}$ & Propagated & Time & Neighbour peak & Category \\",
             r" & & (\textdegree C) & (kJ) & & (s) & (\textdegree C) & \\", r"\midrule"]
    for i, t in enumerate(TESTS):
        m = meas[t]
        prop = m["propagated"].strip().lower() == "yes"
        nmax = m["neighbour_max_C"] + (r"$^{a}$" if t in ("M50_PT_Exp2", "M50_SP_Exp4") else "")
        lines.append(" & ".join([tex_name(t), m["connection"], m["trigger_max_C"], kj(trig[t]),
                                 "yes" if prop else "no", (m["time_to_propagation_s"] if prop else ""), nmax,
                                 cat.get(m["failure_category"], m["failure_category"])]) + r" \\")
        if i == 7:
            lines.append(r"\midrule")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(lines) + "\n"


def table2():
    rows = [
        (r"\textit{Geometry and cells}", None, None),
        ("Cell diameter and length", "21.1 and 70.1 mm", r"\cite{oregan2022thermal}"),
        ("Can wall", "0.25 mm", r"\cite[Table 1]{finegan2024databank}"),
        ("Can: conductivity; mass and specific heat",
         r"15 W\,m$^{-1}$\,K$^{-1}$, a stainless steel's (no source gives the grade); 9 g, 500 J\,kg$^{-1}$\,K$^{-1}$",
         r"assumed$^{a}$"),
        ("Roll conductivity across and along the layers", r"1.3 and 25 W\,m$^{-1}$\,K$^{-1}$",
         r"\cite{oregan2022thermal,chen2021simplified}"),
        ("Cell heat capacity", r"61.75 J\,K$^{-1}$ (65 g at 950 J\,kg$^{-1}$\,K$^{-1}$; the Databank's cells weighed %s "
         r"to %s g before their tests~\cite{finegan2024databank})" % databank_mass(),
         r"\cite{oregan2022thermal}; mass assumed$^{a}$"),
        ("Resolved neighbour", "half model, 19,355 nodes", "this study"),
        (r"\textit{Heat paths}", None, None),
        (r"Contact conductance between the cans, $h_c$", r"200, 2,000, 3,700 W\,m$^{-2}$\,K$^{-1}$ (low, central, high)",
         r"\cite[Table 2.1]{lienhard2024heat}"),
        ("Air in the wedge beside the contact", r"0.03 W\,m$^{-1}$\,K$^{-1}$", r"assumed$^{a}$"),
        ("Contact sector, either side of the line of contact", r"45\textdegree", r"assumed$^{a}$"),
        ("Welded tabs: series one, parallel two", r"6.8 mW\,K$^{-1}$ per tab (5 and 10 as brackets)",
         r"assumed$^{a}$"),
        ("View factor between the cans; emissivity", "0.1817; 0.8",
         r"\cite{bergman2011fundamentals}; assumed$^{a}$, as in \cite{chen2021simplified}"),
        ("Room convection; ambient and start", r"10 W\,m$^{-2}$\,K$^{-1}$; 25\textdegree C", r"assumed$^{a}$"),
        (r"\textit{Trigger}", None, None),
        ("Model and release", ("one temperature; triangular over 21.39 s, the mean of the two rise times read from "
                               "the two published records (17.53 and 25.24 s; Supplementary Section~S7)"),
         r"read from \cite{fransson2024exploring}"),
        (r"Body energy $E_\mathrm{b}$", "9.0 to 54.3 kJ, one per test (Table 1); 33.2 kJ held to calorimetry",
         r"\cite{fransson2024exploring,finegan2024databank}"),
        (r"\textit{Kinetics}", None, None),
        ("Model", "Bayesian chemical reaction neural network: posterior mean, and 200 joint draws",
         r"\cite{koenig2025uncertainty}"),
        ("Reactant masses; initial SEI amount", r"per 720 g reference cell; 0.15 of the source's normalised amount (fresh), 0 (aged)",
         r"\cite{koenig2025uncertainty}"),
        ("Runaway level; window", r"255.7\textdegree C; within 900 s", r"\cite{koenig2025uncertainty}; this study"),
        (r"\textit{Delivered heat}", None, None),
        ("Region", "the half of the neighbour's can facing the trigger, a uniform flux", "this study"),
        ("Shapes", ("triangular over 21.39 s; constant power over 120, 240 or 360 s, the last outlasting the "
                    "longest combustion reported for a 21700 cell, about %.0f s~\\cite{chen2023comprehensive}; in "
                    "PT-Exp4 also the pulse " % flame_s()) +
                   r"followed by a constant power; for Section~\ref{sec:res-why}, triangular over 5 to 360 s",
         "this study"),
    ]
    lines = [r"\begin{table}[!tbp]", r"\centering", r"\scriptsize",
             r"\caption{The model's parameters and their sources. The two-cell geometry and its solver are those of "
             r"an earlier, archived study by the author~\cite{satte2026twocell}, whose cells stood apart and were joined "
             r"by busbars; here the cans touch along a line and welded tabs join the cells, as in the tests. $^{a}$, a "
             r"value that study set without a primary source, held here as an assumption.}",
             r"\label{tab:params}", r"\renewcommand{\arraystretch}{0.9}",
             r"\setlength{\tabcolsep}{4pt}", r"\begin{tabular}{>{\raggedright\arraybackslash}p{0.28\textwidth}>{\raggedright\arraybackslash}p{0.43\textwidth}>{\raggedright\arraybackslash}p{0.21\textwidth}}", r"\toprule",
             r"Quantity & Value & Source \\", r"\midrule"]
    for q, v, s in rows:
        if v is None:
            lines.append(r"\multicolumn{3}{l}{%s} \\" % q)
        else:
            lines.append("%s & %s & %s \\\\" % (q, v, s))
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(lines) + "\n"


def table3():
    b = read_csv(os.path.join(RES, "stage14_bounds_corrected.csv"))
    get = lambda p, w: next((r for r in b if r["path"] == p and r["window_s"] == w), None)
    names = {"A1": "Radiation from a vent's jet or flame",
             "A2": "Gas beside the neighbour, burning or not",
             "A3": "A breach's jet facing the neighbour",
             "A4": "Solids and melt on or against the facing half",
             "A5": "Conduction through the cell holder",
             "A6": "The neighbour's own discharge (parallel tests; for comparison)"}
    sets = {"A1": r"a black body at 1500\textdegree C filling the facing half's view (the holder may reflect); "
                  r"a flame held on the vent's axis, about 0.85~kJ",
            "A2": r"convection by Churchill and Bernstein's relation~\cite{churchill1977correlating} at "
                  r"398.5~m\,s$^{-1}$~\cite{gillich2024mechanical}, at the film temperature of gas at 1500\textdegree C "
                  r"over a can at 25\textdegree C, with hydrogen's properties at 1000~K, the highest tabulated, which give a "
                  r"larger coefficient than air's~\cite{lienhard2024heat}, at most "
                  r"twice the whole-cylinder mean on one half, as the other half's cannot be negative; radiation at "
                  r"1500\textdegree C",
            "A3": r"what the ejecta can release; a narrow jet strikes only from within 30\textdegree{} of the line of "
                  r"centres, a sixth of the circumference",
            "A4": r"what the ejecta can release; melt falls onto it from a breach on the trigger's lower half, half "
                  r"of the circumference",
            "A5": r"not determinable: the inserts' material and contact are not given; energy conservation alone caps it "
                  r"at 247.3~kJ, all the trigger can release, the most measured for this cell in all (110.8~kJ"
                  r"~\cite{finegan2024databank}) with the vent gas burning",
            "A6": r"heats from inside: the stored energy, 18.2~Wh, in every window; beside it, a short across "
                  r"24~m$\Omega$~\cite{lg2017m50} at 4.189~V and 25\textdegree C, 731~W or 15.6~kJ within 21.4~s"}
    meas = {"A1": "the flame's position and temperature beside the cells",
            "A2": "the gas's temperature and velocity in the wedges beside the line of contact",
            "A3": "where breaches face and what they carry",
            "A4": "the debris left on the neighbour",
            "A5": "the holder's inserts and their contact",
            "A6": "the current between parallel cells"}
    lines = [r"\begin{table}[!tbp]", r"\centering", r"\scriptsize",
             r"\caption{What each path can deliver to the neighbour's facing half, from published inputs alone "
             r"(Supplementary Table~S5): the upper bound within the pulse's 21.4~s and in total (every lower bound is "
             r"zero), what sets it, and the measurement that would bound it more tightly. The ejecta can release at "
             r"most 225.8~kJ in the rig: the most calorimetry measured for this cell's ejecta, 89.34~kJ~\cite{finegan2024databank}, "
             r"with the heat of burning the vent gas in open air, at most 136.5~kJ on another 21700 "
             r"cell~\cite{vendra2022numerical}; gas and flame are taken at up to 1500\textdegree C~\cite{chen2020experimental}, "
             r"the vent gas at up to 398.5~m\,s$^{-1}$~\cite{gillich2024mechanical}. The neighbour's own discharge heats "
             r"it from inside and is set beside the paths for comparison.}",
             r"\label{tab:bounds}", r"\renewcommand{\arraystretch}{0.95}",
             r"\setlength{\tabcolsep}{3pt}",
             r"\begin{tabular}{>{\raggedright\arraybackslash}p{0.18\textwidth}rr>{\raggedright\arraybackslash}p{0.39\textwidth}>{\raggedright\arraybackslash}p{0.22\textwidth}}", r"\toprule",
             r"Path & \multicolumn{1}{c}{21.4 s} & \multicolumn{1}{c}{Total} & What sets the bound & Measurement that would bound it \\",
             r" & (kJ) & (kJ) & & \\", r"\midrule"]
    for p in ["A1", "A2", "A3", "A4", "A5", "A6"]:
        r21, rt = get(p, "21.39"), get(p, "total")
        if r21 is None or r21["determinable"] != "yes":
            v21 = vt = "--"
        else:
            v21, vt = kj(r21["upper_J"]), kj(rt["upper_J"])
        lines.append("%s & %s & %s & %s & %s \\\\" % (names[p], v21, vt, sets[p], meas[p]))
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(lines) + "\n"


def table_s3():
    nd = {r["test"]: r for r in read_csv(os.path.join(RES, "stage14_needs.csv"))}
    xs = {r["test"]: r for r in json.load(open(os.path.join(RES, "stage15_cross_section.json")))["A2"] if r["shape"] == "tri"}
    b1 = json.load(open(os.path.join(RES, "stage15_paper_numbers.json")))["B1"]
    tab = read_csv(os.path.join(RES, "stage15_table.csv"))
    s16 = _s16()
    n16 = {r["test"]: r for r in s16["N"]}
    lines = [r"{\footnotesize\setlength{\tabcolsep}{3pt}", r"\begin{longtable}{p{0.1\textwidth}p{0.13\textwidth}p{0.15\textwidth}p{0.15\textwidth}p{0.15\textwidth}p{0.18\textwidth}}",
             r"\caption{The thresholds of the sixteen tests with the 21.4~s pulse at the central contact (kJ; a bracket is the largest "
             r"energy run that does not meet the criterion and the smallest that does), and, for the nine propagated "
             r"tests, their needs: the least energy with which the lumped neighbour and the resolved neighbour (by "
             r"the reactive cross-section, and in the eight tests with strong triggers bracketed in three dimensions) "
             r"run away within 10~s of the measured time, counted as delivered by the "
             r"run's own runaway. An energy marked $^{t}$ is the least energy "
             r"run whose runaway comes before the measured time when the next lower run, 0.5\,\% of the test's "
             r"ejected energy below, gives none within 900~s: the measured time is reproduced only between the two, "
             r"within that resolution of the threshold, and the value, the higher, can exceed the bracket beside it. Supplementary Table~\ref{tab:s-needs} gives the other delivery shapes.}"
             r"\label{tab:s-thresholds}\\",
             r"\toprule", r"Test & Hottest point & Lumped & Resolved, cross-section & Resolved, three-dimensional & "
             r"Needs: lumped; cross-section; three-dimensional \\", r"\midrule", r"\endfirsthead",
             r"\multicolumn{6}{l}{\textit{Continued}} \\", r"\toprule",
             r"Test & Hottest point & Lumped & Resolved, cross-section & Resolved, three-dimensional & "
             r"Needs: lumped; cross-section; three-dimensional \\", r"\midrule", r"\endhead"]
    for t in TESTS:
        r = nd[t]
        (lo1, hi1), (lo2, hi2) = RB.brackets(r)          # the narrowest bracket the archive holds (Stage 13 refined four)
        c1 = "0" if hi1 == 0 else "(%s, %s]" % (kj(lo1, 2), kj(hi1, 2))
        c2 = "0" if hi2 == 0 else "(%s, %s]" % (kj(lo2, 2), kj(hi2, 2))
        c8 = "(%s, %s]" % (kj(xs[t]["lo_J"], 2), kj(xs[t]["hi_J"], 2))
        d3 = "(%s, %s]" % (kj(b1[t]["bracket"]["lo_J"], 2), kj(b1[t]["bracket"]["hi_J"], 2)) if t in b1 else ""
        if t == s16["T"].get("test") and s16["T"].get("status") == "done":
            d3 = "(%s, %s]" % (kj(s16["T"]["lo_J"], 2), kj(s16["T"]["hi_J"], 2))
        row = next((x for x in tab if x["test"] == t and x["delivery"].startswith("21.39")), None)
        if row is not None:
            mk2 = r"$^{t}$" if row["C2_status"] == "threshold" else ""
            mk8 = r"$^{t}$" if row["C8_xs_status"] == "threshold" else ""
            need = "%s%s; %s%s" % (kj(row["C2_E_by_t_J"], 2), mk2, kj(row["C8_xs_E_by_t_J"], 2), mk8)
            q = n16.get(t)
            if q is not None and q["status"] == "done":
                need += "; (%s, %s]" % (kj(q["lo_J"], 2), kj(q["hi_J"], 2))
        else:
            need = ""
        lines.append(" & ".join([tex_name(t), c1, c2, c8, d3, need]) + r" \\")
    lines += [r"\bottomrule", r"\end{longtable}", r"}"]
    return "\n".join(lines) + "\n"


SHAPES = [("21.39 s pulse", "21.4~s pulse"), ("120 s constant power", "120~s power"),
          ("240 s constant power", "240~s power"), ("360 s constant power", "360~s power")]
MARK = {"matched": "", "threshold": r"$^{t}$", "bracketed": r"$^{b}$"}


def table_s7():
    """The needs of every test under the four delivery shapes (results/stage15_table.csv for the nine propagated
    tests, results/stage14_needs.csv for the seven that did not propagate)."""
    tab = read_csv(os.path.join(RES, "stage15_table.csv"))
    nd = {r["test"]: r for r in read_csv(os.path.join(RES, "stage14_needs.csv"))}
    s16 = _s16()
    d3 = {(r["test"], r["delivery"]): r for r in s16["N"] + s16["X"]}
    head = (r"Test & Time (s) & Delivery & Lumped & Resolved & Resolved, in all & Its runaway (s) & "
            r"Three-dimensional \\")
    lines = [r"{\scriptsize\setlength{\tabcolsep}{3pt}",
             r"\begin{longtable}{p{0.08\textwidth}p{0.06\textwidth}p{0.12\textwidth}p{0.09\textwidth}p{0.09\textwidth}"
             r"p{0.09\textwidth}p{0.08\textwidth}p{0.17\textwidth}}",
             r"\caption{The needs of the nine tests that propagated under the four delivery shapes (kJ): the least "
             r"energy with which the lumped neighbour (Lumped), and the resolved neighbour by the reactive cross-section "
             r"(Resolved), run away within 10~s of the measured time (Time), counted as delivered by the run's own "
             r"runaway; for the resolved neighbour, the energy of that delivery in all, over its whole shape, and the "
             r"time of its runaway in that run. $^{t}$, the least energy run whose runaway comes before the measured "
             r"time, the next lower run, 0.5\,\% of the test's ejected energy below, giving none within 900~s, so that "
             r"the measured time is reproduced only between the two, within that resolution of the threshold; the "
             r"energy is counted to that run's runaway; "
             r"$^{b}$, interpolated between the two runs whose runaways bracket the measured time, and counted "
             r"to the measured time; a dash, no energy on the search's grid, which ran to 0.2 of the test's ejected "
             r"energy above the threshold's upper end, brought the runaway within 10~s of the measured time (in ST-Exp3 "
             r"over 360~s it came no earlier than 196.4~s, with 25.6~kJ). The four shapes deliver the "
             r"same energy by the runaway only where the delivery ends before it. Three-dimensional: the need bracketed "
             r"in three dimensions (step 16), counted as delivered by 10~s after the measured time; the searches with "
             r"constant power that the computing allowed are given, and one not finished is marked so. Below, for the seven tests that did not propagate, the energy "
             r"that puts the far face's peak at the measured maximum, within 5~K, under each shape; $^{a}$, a maximum "
             r"that may not be the neighbour's surface (exploratory); a dash, a far face that stays below the measured "
             r"maximum with up to the test's whole ejected energy.}\label{tab:s-needs}\\",
             r"\toprule", head, r"\midrule", r"\endfirsthead", r"\multicolumn{8}{l}{\textit{Continued}} \\",
             r"\toprule", head, r"\midrule", r"\endhead"]
    for t in TESTS:
        rows = [x for x in tab if x["test"] == t]
        if not rows:
            continue
        for i, (key, lab) in enumerate(SHAPES):
            x = next(r for r in rows if r["delivery"] == key)
            c2 = kj(x["C2_E_by_t_J"], 2) + MARK[x["C2_status"]]
            if x["C8_xs_status"] in MARK and x["C8_xs_E_by_t_J"]:
                c8 = kj(x["C8_xs_E_by_t_J"], 2) + MARK[x["C8_xs_status"]]
                e8 = kj(x["C8_xs_E_J"], 2)
                t8 = "%.1f" % float(x["C8_xs_t_s"])
            else:
                c8, e8, t8 = "--", "", ""
            q = d3.get((t, key))
            if q is None:
                c3 = ""
            elif q["status"] == "done":
                c3 = "(%s, %s]" % (kj(q["lo_by_t_J"], 2), kj(q["hi_by_t_J"], 2))
            elif q["status"] in ("unfinished", "stopped", "out of range", "not monotone"):
                c3 = q["status"]
            else:
                c3 = ""
            lines.append(" & ".join([tex_name(t) if i == 0 else "", x["t_measured_s"].split(".")[0] if i == 0 else "",
                                     lab, c2, c8, e8, t8, c3]) + r" \\")
        lines.append(r"\midrule")
    lines += [r"\multicolumn{8}{l}{\textit{Tests that did not propagate}} \\",
              r"Test & Peak (\textdegree C) & Delivery & \multicolumn{5}{l}{Far face's peak at the measured peak (kJ)} \\",
              r"\midrule"]
    keys = [("need_21s", "21.4~s pulse"), ("need_120s", "120~s power"), ("need_240s", "240~s power"),
            ("need_360s", "360~s power")]
    for t in TESTS:
        r = nd[t]
        if r["propagated"] != "no":
            continue
        expl = "exploratory" in r["reading_21s"]
        for i, (k, lab) in enumerate(keys):
            lo, hi = r[k + "_lo_J"], r[k + "_hi_J"]
            if hi == "":
                v = "--"
            elif float(lo) == float(hi):
                v = kj(hi, 2)
            else:
                v = "(%s, %s]" % (kj(lo, 2), kj(hi, 2))
            mx = (r["neighbour_max_C"] + (r"$^{a}$" if expl else "")) if i == 0 else ""
            lines.append(" & ".join([tex_name(t) if i == 0 else "", mx, lab, r"\multicolumn{5}{l}{%s}" % v]) + r" \\")
    lines += [r"\bottomrule", r"\end{longtable}", r"}"]
    return "\n".join(lines) + "\n"


def table_s8():
    """The local threshold against the reduced models: M50_PT_Exp1 by delivery duration, and ST_Exp3 and PT_Exp3 at
    10, 21.39 and 60 s (results/stage13_skin.csv, fractions of each test's E_e from results/stage14_needs.csv), with
    M50_PT_Exp1's lumped threshold (results/stage13_twobody.csv, central contact) and the ratio of the midpoints
    (results/stage13_map.csv). Every cell's source is written to tables/s8_reduced.cells.json for the numbers check."""
    skin = read_csv(os.path.join(RES, "stage13_skin.csv"))
    tb = read_csv(os.path.join(RES, "stage13_twobody.csv"))
    mp = read_csv(os.path.join(RES, "stage13_map.csv"))
    ee = RB.e_e()
    cells = []

    def cell(text, file, where, col, times_ee=False, scale=1.0, dec=2):
        cells.append({"text": text, "file": file, "where": where, "col": col, "times_E_e": times_ee,
                      "scale": scale, "dec": dec})
        return text

    def frac_kj(r, col):
        if r[col] == "":
            return ""
        v = float(r[col]) * ee[r["test"]] / 1e3
        return cell("%.2f" % v, "results/stage13_skin.csv",
                    {"test": r["test"], "region": "half", "tau_d_s": r["tau_d_s"]}, col, True, 1e-3, 2)

    head = (r"Test & Pulse (s) & Fourier number & Local threshold, resolved & Cross-section conduction & Skin model & "
            r"Hottest point, no reaction (K) & Lumped threshold & Ratio \\")
    lines = [r"\begin{table}[!htbp]", r"\centering", r"\scriptsize",
             r"\caption{The local threshold against the reduced models of Section~2.5 of the main text, with triangular "
             r"pulses over the facing half (kJ): PT-Exp1 by the pulse's duration, and ST-Exp3 and PT-Exp3 at 10, 21.4 "
             r"and 60~s. Fourier number, $\alpha\tau/a^2$ with the roll's diffusivity across its layers. Skin model: "
             r"PT-Exp1 only, as Fig.~4a of the main text draws it. Hottest point "
             r"without the reaction: with the reaction switched off at the upper end of the resolved bracket, the "
             r"hottest point's peak less 255.7\textdegree C (a negative value falls short). Lumped threshold and the "
             r"ratio of the lumped to the local threshold's midpoint: PT-Exp1 at the central contact. A blank: no "
             r"search or run at that duration.}",
             r"\label{tab:s-reduced}", r"\setlength{\tabcolsep}{2.5pt}",
             r"\begin{tabular}{p{0.075\textwidth}>{\raggedleft\arraybackslash}p{0.055\textwidth}"
             r">{\raggedleft\arraybackslash}p{0.075\textwidth}>{\raggedleft\arraybackslash}p{0.13\textwidth}"
             r">{\raggedleft\arraybackslash}p{0.085\textwidth}>{\raggedleft\arraybackslash}p{0.06\textwidth}"
             r">{\raggedleft\arraybackslash}p{0.1\textwidth}>{\raggedleft\arraybackslash}p{0.13\textwidth}"
             r">{\raggedleft\arraybackslash}p{0.055\textwidth}}", r"\toprule", head, r"\midrule"]
    order = [("M50_PT_Exp1", None), ("M50_ST_Exp3", None), ("M50_PT_Exp3", None)]
    for t, _ in order:
        rows = [r for r in skin if r["test"] == t and r["region"] == "half"]
        rows.sort(key=lambda r: float(r["tau_d_s"]))
        for i, r in enumerate(rows):
            tau = float(r["tau_d_s"])
            fo = cell("%.3f" % float(r["fourier"]), "results/stage13_skin.csv",
                      {"test": t, "region": "half", "tau_d_s": r["tau_d_s"]}, "fourier", False, 1.0, 3)
            res = ""
            if r["res_lo"] != "" and r["res_hi"] != "":
                res = "(%s, %s]" % (frac_kj(r, "res_lo"), frac_kj(r, "res_hi"))
            a2_kj = frac_kj(r, "A2_f")                                   # cells recorded in the table's order
            skin_kj = frac_kj(r, "A1_f") if t == "M50_PT_Exp1" else ""      # as Fig. 3a draws it
            sh = ""
            if r["inert_peak_minus_level_K"] != "":
                sh = cell("%.1f" % float(r["inert_peak_minus_level_K"]), "results/stage13_skin.csv",
                          {"test": t, "region": "half", "tau_d_s": r["tau_d_s"]}, "inert_peak_minus_level_K",
                          False, 1.0, 1)
            lum, ratio = "", ""
            if t == "M50_PT_Exp1":
                q = next((x for x in tb if x["test"] == t and x["h"] == "central" and x["tau_d_s"] == r["tau_d_s"]), None)
                if q is not None:
                    w = {"test": t, "h": "central", "tau_d_s": r["tau_d_s"]}
                    lum = "(%s, %s]" % (cell(kj(q["lum_lo_J"], 2), "results/stage13_twobody.csv", w, "lum_lo_J",
                                             False, 1e-3, 2),
                                        cell(kj(q["lum_hi_J"], 2), "results/stage13_twobody.csv", w, "lum_hi_J",
                                             False, 1e-3, 2))
                m = next((x for x in mp if x["tau_d_s"] == r["tau_d_s"] and x["runs_ratio"] != ""), None)
                if m is not None:
                    ratio = cell("%.2f" % float(m["runs_ratio"]), "results/stage13_map.csv",
                                 {"tau_d_s": r["tau_d_s"]}, "runs_ratio", False, 1.0, 2)
            pulse = ("%.1f" % tau) if abs(tau - round(tau)) > 1e-6 else "%d" % round(tau)
            lines.append(" & ".join([tex_name(t) if i == 0 else "", pulse, fo, res, a2_kj,
                                     skin_kj, sh, lum, ratio]) + r" \\")
        lines.append(r"\midrule" if t != order[-1][0] else "")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    json.dump(cells, open(os.path.join(OUT, "s8_reduced.cells.json"), "w"), indent=1)
    return "\n".join(x for x in lines if x != "") + "\n"


def table_s9():
    """The held-out scores of step 10 (results/stage10_heldout.json)."""
    h = json.load(open(os.path.join(RES, "stage10_heldout.json")))
    names = {"fC1": "Local threshold", "fC2": "Lumped threshold",
             "f9": "Need: lumped where propagated, far face where not"}
    dirs = {"series_to_parallel": ("series", "parallel"), "parallel_to_series": ("parallel", "series")}
    lines = [r"\begin{table}[!htbp]", r"\centering", r"\footnotesize",
             r"\caption{The held-out test of Section~2.7 of the main text, with the 21.4~s pulse: each quantity fitted "
             r"as a logistic predictor of the outcome on the eight tests of one connection and scored on the other "
             r"eight by the mean log score (higher is better), against one probability for every test fitted on the "
             r"same eight; the gain is the difference, and $p$ the share of %s permutations of the outcomes whose gain "
             r"is at least the observed one.}" % ("{:,}".format(h["n_perm"])),
             r"\label{tab:s-heldout}", r"\setlength{\tabcolsep}{4pt}",
             r"\begin{tabular}{p{0.25\textwidth}llrrrr}", r"\toprule",
             r"Quantity & Fitted on & Scored on & One probability & Logistic & Gain & $p$ \\", r"\midrule"]
    for k in ("fC1", "fC2", "f9"):
        for i, (d, (a, b)) in enumerate(dirs.items()):
            w = h["predictors"][k][d]
            o = w["observed"]
            lines.append(" & ".join([names[k] if i == 0 else "", a, b, "%.3f" % o["constant"]["log"],
                                     "%.3f" % o["logistic"]["log"], "%.3f" % o["d_log"], "%.2f" % w["p_log"]]) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(lines) + "\n"


def table_s10():
    """The two-body model against the lumped searches (results/stage13_twobody.csv): at the low and high contacts with
    the 21.39 s pulse, as registered, and at the central contact with triangular pulses of 120 and 360 s, compared
    afterwards and unscored. The tolerance is the larger of 10 % of the bracket's midpoint and 300 J, as registered;
    the central rows' tolerance, which the file does not hold, and each row's verdict are written to
    manuscript/rebuild/data/s10_twobody.csv for the numbers check."""
    tb = read_csv(os.path.join(RES, "stage13_twobody.csv"))
    head = r"Test & Case & $E_\mathrm{b}$ & Lumped bracket & Two-body & Difference & Tolerance & Within \\"
    lines = [r"{\footnotesize\setlength{\tabcolsep}{2.5pt}",
             r"\begin{longtable}{llrrrrrl}",
             r"\caption{The lumped threshold against the two-body model of Section~2.5 of the main text (kJ): above, "
             r"with the 21.4~s pulse at the low and the high contact, the 32 searches the model was registered against "
             r"before them; below, with triangular pulses of 120 and 360~s at the central contact, the 32 searches it "
             r"was compared with afterwards, unscored. Each row gives the search's bracket, the two-body model's value "
             r"and its difference from the bracket's midpoint, against the larger of 10\,\% of the midpoint and "
             r"300~J, the tolerance registered with the model.}\label{tab:s-twobody}\\",
             r"\toprule", head, r"\midrule", r"\endfirsthead", r"\multicolumn{8}{l}{\textit{Continued}} \\",
             r"\toprule", head, r"\midrule", r"\endhead"]
    data = []
    blocks = [("At the low and the high contact, the 21.4~s pulse (registered)",
               [("low", RB.TAU21, "low"), ("high", RB.TAU21, "high")]),
              ("At the central contact, triangular pulses (compared afterwards, unscored)",
               [("central", "120.0", "120~s"), ("central", "360.0", "360~s")])]
    for bname, cases in blocks:
        lines.append(r"\multicolumn{8}{l}{\textit{%s}} \\" % bname)
        for t in TESTS:
            for j, (h, tau, lab) in enumerate(cases):
                r = next(x for x in tb if x["test"] == t and x["h"] == h and x["tau_d_s"] == tau)
                mid = float(r["lum_mid_J"])
                tol = float(r["P8_tol_J"]) if r["P8_tol_J"] else max(0.1 * mid, 300.0)
                diff = float(r["B2_minus_mid_J"])
                within = abs(diff) <= tol + 1e-9
                br = "0" if float(r["lum_hi_J"]) == 0 else "(%s, %s]" % (kj(r["lum_lo_J"], 2), kj(r["lum_hi_J"], 2))
                lines.append(" & ".join([tex_name(t) if j == 0 else "", lab, kj(r["E_b_J"], 1) if j == 0 else "",
                                         br, kj(r["B2_E_J"], 2), kj(diff, 2), kj(tol, 2),
                                         "yes" if within else "no"]) + r" \\")
                data.append({"test": t, "contact": h, "tau_s": tau, "lum_lo_J": r["lum_lo_J"], "lum_hi_J": r["lum_hi_J"],
                             "mid_J": mid, "two_body_J": r["B2_E_J"], "diff_J": diff, "tol_J": tol,
                             "beyond_J": max(0.0, abs(diff) - tol), "within": "yes" if within else "no"})
        if bname.startswith("At the low"):
            lines.append(r"\midrule")
    lines += [r"\bottomrule", r"\end{longtable}", r"}"]
    out = os.path.join(ROOT, "manuscript", "rebuild", "data", "s10_twobody.csv")
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(data[0].keys()))
        w.writeheader()
        w.writerows(data)
    return "\n".join(lines) + "\n"


TESTS16 = [f"M50_{c}_Exp{i}" for c in ("PT", "PP", "ST", "SP") for i in range(1, 5)]


def table_s11():
    """The 151 archived three-dimensional runs at the central contact that the reactive cross-section was set against
    (results/stage15_cross_section.json, A1_rows), by test and delivery. The numbers check recomputes every row from
    the same rows by its own code."""
    rows = json.load(open(os.path.join(RES, "stage15_cross_section.json")))["A1_rows"]
    lines = [r"\begin{table}[!htbp]", r"\centering", r"\footnotesize",
             r"\caption{The 151 archived three-dimensional runs at the central contact against which the reactive "
             r"cross-section was set (Section~3.7 of the main text), by test and delivery: the runs with no delivery, "
             r"with the 21.4~s pulse and with constant power over 120, 240 and 360~s; the range of energy delivered; "
             r"the runs in which both models' means reach 255.7\textdegree C; and those held to 332~s, PT-Exp4's "
             r"measured time plus 60~s, made to compare with its history, every other run going to 900~s. In all 151 "
             r"the cross-section gave the three-dimensional outcome.}",
             r"\label{tab:s-archived}", r"\setlength{\tabcolsep}{2.5pt}",
             r"\begin{tabular}{lrrrrrr@{\hspace{9pt}}lrr}", r"\toprule",
             r"Test & Runs & None & Pulse & 120~s & 240~s & 360~s & Energy (kJ) & Both run away & To 332~s \\",
             r"\midrule"]
    for t in TESTS16 + ["all"]:
        rr = [r for r in rows if t == "all" or r["test"] == t]
        if not rr:
            continue
        n = lambda shape, tau=None: sum(1 for r in rr if r["shape"] == shape and (tau is None or abs(r["tau_d_s"] - tau) < 1))
        e = [r["E_J"] / 1e3 for r in rr if r["E_J"] > 0]
        er = (f"{min(e):.1f} to {max(e):.1f}" if len(e) > 1 else f"{e[0]:.1f}") if e else "--"
        name = "All" if t == "all" else t[4:].replace("_", "-")
        if t == "all":
            lines.append(r"\midrule")
        lines.append(f"{name} & {len(rr)} & {n('none')} & {n('tri')} & {n('con', 120)} & {n('con', 240)} & "
                     f"{n('con', 360)} & {er} & {sum(1 for r in rr if r['C8_3d'] and r['C8_xs'])} & "
                     f"{sum(1 for r in rr if r['t_end_s'] < 899)} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}", ""]
    return "\n".join(lines)


S11_TESTS = ["M50_PT_Exp1", "M50_PP_Exp3", "M50_ST_Exp2", "M50_SP_Exp3"]


def s11_draw_labels():
    d = {r["label"]: r for r in read_csv(os.path.join(RES, "stage11_draws.csv"))}
    lab = [("mean", "Posterior mean, nominal properties")]
    for k in ("d188", "d83", "d40", "d184"):
        lab.append((k, "Kinetic draw ranked %s of 200" % d[k]["rank"]))
    three = lambda k: r"%.3f and %.2f W\,m$^{-1}$\,K$^{-1}$, %.0f J\,kg$^{-1}$\,K$^{-1}$" % (
        float(d[k]["k_radial_W_mK"]), float(d[k]["k_axial_W_mK"]), float(d[k]["c_roll_J_kgK"]))
    lab += [("kr_min", "Least conductivity across the layers: " + three("kr_min")),
            ("kr_max", "Largest conductivity across the layers: " + three("kr_max")),
            ("c_min", "Least specific heat: " + three("c_min")),
            ("c_max", "Largest specific heat: " + three("c_max"))]
    return lab


def table_s12():
    """Step 11's lumped and local thresholds with the 21.39 s pulse at the central contact, under the posterior mean
    and its eight draws (results/stage11_thresholds.csv, criteria C2 and C1), in kJ: the fractions' bracket times the
    test's ejected energy (results/stage8_ejected.csv). Also writes manuscript/rebuild/data/step11_lumped_kJ.csv and
    step11_local_kJ.csv, the table's values, for the numbers check."""
    ee = {r["id"]: float(r["E_e_J"]) for r in read_csv(os.path.join(RES, "stage8_ejected.csv")) if r["kind"] == "test"}
    allth = read_csv(os.path.join(RES, "stage11_thresholds.csv"))
    lines = [r"\begin{table}[!htbp]", r"\centering", r"\scriptsize",
             r"\caption{The lumped and the hottest point's thresholds of the four tests that step~11 searched, with the "
             r"21.4~s pulse at the "
             r"central contact, under the posterior mean and the nominal properties and under the step's eight draws "
             r"(Section~\ref{sec:s-key}): the bracket between the largest energy run that does not meet the criterion "
             r"and the smallest that does, in kJ, on a grid of 0.0125 of the test's ejected energy "
             r"(the last row); 0, met with no delivery. The main text quotes a bracket's midpoint. The kinetic draws "
             r"are ranked, earliest first, by the time of the hot spot's onset in step~3's case; the thermal draws "
             r"are the extremes among thirty over the roll's published ranges, each named by the property in which it "
             r"is extreme and setting all three: the conductivity across and along the layers and the specific heat.}",
             r"\label{tab:s-step11}", r"\setlength{\tabcolsep}{4pt}",
             r"\begin{tabular}{>{\raggedright\arraybackslash}p{0.33\textwidth}rrrr}", r"\toprule",
             r"Draw & PT-Exp1 & PP-Exp3 & ST-Exp2 & SP-Exp3 \\", r"\midrule"]
    for crit, head, fname in (("C2", "The lumped threshold", "step11_lumped_kJ.csv"),
                              ("C1", "The hottest point's threshold", "step11_local_kJ.csv")):
        th = {(r["test"], r["draw"]): r for r in allth if r["criterion"] == crit}
        data = []
        lines.append(r"\multicolumn{5}{l}{\textit{%s}} \\" % head)
        for key, label in s11_draw_labels():
            cells = []
            for t in S11_TESTS:
                r = th[(t, key)]
                lo, hi = float(r["lo"] or 0) * ee[t] / 1e3, float(r["hi"] or 0) * ee[t] / 1e3
                data.append({"test": t, "draw": key, "status": r["status"], "lo_kJ": lo, "hi_kJ": hi,
                             "E_e_kJ": ee[t] / 1e3})
                cells.append("0" if r["status"] == "zero" else "(%.2f, %.2f]" % (lo, hi))
            lines.append(label + " & " + " & ".join(cells) + r" \\")
            if key in ("mean", "d184"):
                lines.append(r"\addlinespace[2pt]")
        lines.append(r"\midrule")
        out = os.path.join(ROOT, "manuscript", "rebuild", "data", fname)
        with open(out, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(data[0].keys()))
            w.writeheader()
            w.writerows(data)
    lines.append(r"Ejected energy (kJ) & " + " & ".join("%.2f" % (ee[t] / 1e3) for t in S11_TESTS) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}", ""]
    return "\n".join(lines)


def table_s13():
    """Step 11's far-face peaks with no delivery in the five low-maximum tests that did not propagate
    (results/stage11_overshoot.csv)."""
    ov = {(r["test"], r["thermal"], r["contact"]): r for r in read_csv(os.path.join(RES, "stage11_overshoot.csv"))}
    tests = ["M50_PT_Exp1", "M50_PT_Exp3", "M50_PP_Exp3", "M50_ST_Exp1", "M50_ST_Exp2"]
    lab = dict(s11_draw_labels())
    rows = [("Measured maximum", None)]
    rows += [("Central contact: " + lab["mean"][0].lower() + lab["mean"][1:], ("central", "central"))]
    rows += [("Central contact: " + lab[k][0].lower() + lab[k][1:], (k, "central")) for k in ("kr_min", "kr_max", "c_min", "c_max")]
    rows += [("Low contact, posterior mean and nominal properties", ("central", "low")),
             ("High contact, posterior mean and nominal properties", ("central", "high"))]
    lines = [r"\begin{table}[!htbp]", r"\centering", r"\footnotesize",
             r"\caption{The far face's peak with no delivered heat over 900~s (\textdegree C) in the five tests that did "
             r"not propagate and report low maxima, with each test's fitted trigger, against the maximum Fransson et "
             r"al.\ measured: at the central contact under the posterior mean and the nominal properties and under "
             r"step~11's four thermal draws, each with its three properties as in Table~\ref{tab:s-step11}, and at the "
             r"low and high contacts under the posterior mean and the nominal properties.}",
             r"\label{tab:s-farface}", r"\setlength{\tabcolsep}{3pt}",
             r"\begin{tabular}{>{\raggedright\arraybackslash}p{0.36\textwidth}rrrrr}", r"\toprule",
             r" & " + " & ".join(tex_name(t) for t in tests) + r" \\", r"\midrule"]
    for name, key in rows:
        if key is None:
            cells = ["%.0f" % float(ov[(t, "central", "central")]["M_C"]) for t in tests]
        else:
            cells = ["%.1f" % float(ov[(t, key[0], key[1])]["peak_f0_C"]) for t in tests]
        lines.append(name + " & " + " & ".join(cells) + r" \\")
        if key is None or key == ("c_max", "central"):
            lines.append(r"\midrule")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}", ""]
    return "\n".join(lines)


def table_s14():
    """The 151 archived runs one by one (results/stage15_cross_section.json, A1_rows): test, delivery, energy, the step
    whose search made the run, how far it was carried, and each model's outcome, the mean's runaway time or, with none,
    its peak. A run marked with a dagger repeats the configuration of another run, made in a different step."""
    rows = json.load(open(os.path.join(RES, "stage15_cross_section.json")))["A1_rows"]
    key = lambda r: (r["test"], r["shape"], round(r["tau_d_s"], 2), round(r["E_J"], 1))
    seen = {}
    for r in rows:
        seen.setdefault(key(r), []).append(r["id"])
    order = {t: i for i, t in enumerate(TESTS16)}
    shape = lambda r: ("none" if r["shape"] == "none" else "pulse" if r["shape"] == "tri" else "%.0f~s" % r["tau_d_s"])
    srt = sorted(rows, key=lambda r: (order[r["test"]], {"none": 0, "tri": 1, "con": 2}[r["shape"]], r["tau_d_s"], r["E_J"],
                                      int(r["id"].split("_")[0][1:]), r["id"]))
    def out(r, m):
        if r["C8_" + m]:
            return "runs away, %.1f~s" % r["t_C8_%s_s" % m]
        return "peak %.1f\\textdegree C" % r["mean_peak_%s_C" % m]
    lines = [r"{\scriptsize\setlength{\tabcolsep}{4pt}",
             r"\begin{longtable}{llrrrll}",
             r"\caption{The 151 archived three-dimensional runs of Table~\ref{tab:s-archived} one by one, at the central "
             r"contact: the test, the delivery (none, the 21.4~s pulse, or constant power over the time given), the "
             r"energy delivered to the facing half, the step whose search made the run, how far it was carried, and each "
             r"model's outcome, the time at which the resolved neighbour's mean reaches 255.7\textdegree C or, where it "
             r"does not, the mean's peak. A dagger marks the six runs that repeat another's configuration in a different "
             r"step; they are counted as they were run. Two energies differ in the last digit from the needs of "
             r"Tables~\ref{tab:s-thresholds} and~\ref{tab:s-needs}: PT-Exp1's over 360~s is the same run, whose energy "
             r"the needs file records to 0.1~J, and SP-Exp3's with the pulse is step 9's run at the fraction its search "
             r"interpolated, while the need is that of step 12's run, which met the measured time.}"
             r"\label{tab:s-archived-runs}\\",
             r"\toprule", r"Test & Delivery & Energy (kJ) & Step & To (s) & Three-dimensional & Cross-section \\",
             r"\midrule", r"\endfirsthead",
             r"\multicolumn{7}{l}{\textit{Continued}} \\", r"\toprule",
             r"Test & Delivery & Energy (kJ) & Step & To (s) & Three-dimensional & Cross-section \\", r"\midrule",
             r"\endhead"]
    first = {}
    for r in srt:
        k = key(r)
        dup = len(seen[k]) > 1 and first.setdefault(k, r["id"]) != r["id"]
        step = r["id"].split("_")[0][1:]
        name = r["test"][4:].replace("_", "-") + (r"$^\dagger$" if dup else "")
        lines.append("%s & %s & %s & %s & %.0f & %s & %s \\\\" % (name, shape(r), ("%.2f" % (r["E_J"] / 1e3)) if r["E_J"] else "0",
                                                                step, r["t_end_s"], out(r, "3d"), out(r, "xs")))
    assert sum(1 for x in lines if "dagger" in x and "&" in x and "caption" not in x) == 6
    lines += [r"\bottomrule", r"\end{longtable}", r"}", ""]
    return "\n".join(lines)


def table_s15():
    """The resolved neighbour with no delivered heat, every test at the three contacts (results/stage15_nodelivery.csv):
    the peak of its mean and how its outcome is established. h: the hottest point stays below 255.7 C in a
    three-dimensional run to 900 s (the mean cannot pass it); r: a three-dimensional run carried to 900 s; x: the
    reactive cross-section alone. The peak is the three-dimensional run's where there is one, else the cross-section's."""
    nd = read_csv(os.path.join(RES, "stage15_nodelivery.csv"))
    lines = [r"\begin{table}[!htbp]", r"\centering", r"\footnotesize",
             r"\caption{The resolved neighbour with no delivered heat, test by test at the three contacts, with each "
             r"test's fitted trigger under the posterior mean and the nominal properties: the peak of its mean "
             r"temperature within 900~s (\textdegree C) and how its outcome, no runaway in every case, is established. "
             r"$^{h}$, the hottest point stays below 255.7\textdegree C in a three-dimensional run to 900~s, so the mean "
             r"cannot reach it; $^{r}$, a three-dimensional run carried to 900~s; $^{x}$, the reactive cross-section "
             r"alone (Section~3.7 of the main text). The peak is the three-dimensional run's where there is one and "
             r"the cross-section's otherwise.}",
             r"\label{tab:s-nodelivery}", r"\setlength{\tabcolsep}{6pt}",
             r"\begin{tabular}{lrrr}", r"\toprule", r"Test & Low contact & Central contact & High contact \\",
             r"\midrule"]
    counts = {}
    for t in TESTS16:
        cells = []
        for h in ("low", "central", "high"):
            r = next(x for x in nd if x["test"] == t and x["h"] == h)
            assert r["C8"] == "False" and r["C8_xs"] == "False"
            if r["C1"] == "False":
                m, peak = "h", r["mean_peak_3d_C"]
            elif r["C8_source"].startswith("archive"):
                m, peak = "r", r["mean_peak_3d_C"]
            else:
                assert r["C8_source"] == "cross-section"
                m, peak = "x", r["mean_peak_xs_C"]
            counts[(h, m)] = counts.get((h, m), 0) + 1
            cells.append("%.1f$^{%s}$" % (float(peak), m))
        lines.append(tex_name(t) + " & " + " & ".join(cells) + r" \\")
    assert counts == {("low", "h"): 16, ("central", "h"): 8, ("central", "r"): 8, ("high", "h"): 3, ("high", "r"): 3,
                      ("high", "x"): 10}, counts
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}", ""]
    return "\n".join(lines)


def _s16():
    return json.load(open(os.path.join(RES, "stage16_scorecard.json")))


def _br(lo, hi, nd=2):
    return "(%s, %s]" % (kj(lo, nd), kj(hi, nd))


def table4():
    """Table 4 of the main text: the resolved needs and thresholds in three dimensions with the 21.4 s pulse at the
    central contact (step 16, results/stage16_scorecard.json; step 15, results/stage15_paper_numbers.json), beside the
    reduced model's (results/stage15_table.csv, results/stage15_cross_section.json) and the lumped neighbour's
    (results/stage15_table.csv; the thresholds' brackets by rebuild_brackets from results/stage14_needs.csv); and the
    needs with constant power that step 16 found in three dimensions, where it found any."""
    s16 = _s16()
    tt = {r["test"]: r for r in read_csv(os.path.join(ROOT, "inputs", "fransson2024", "m50_tests.csv"))}
    trig = {r["test"]: float(r["E_J"]) for r in read_csv(os.path.join(RES, "stage7_triggers.csv")) if r["kind"] == "test"}
    nd = {r["test"]: r for r in read_csv(os.path.join(RES, "stage14_needs.csv"))}
    b1 = json.load(open(os.path.join(RES, "stage15_paper_numbers.json")))["B1"]
    xs = {r["test"]: r for r in json.load(open(os.path.join(RES, "stage15_cross_section.json")))["A2"] if r["shape"] == "tri"}
    N = sorted(s16["N"], key=lambda r: float(tt[r["test"]]["time_to_propagation_s"]))
    lines = [r"\begin{table}[!tbp]", r"\centering", r"\footnotesize",
             r"\caption{The resolved neighbour in three dimensions, with the 21.4~s pulse at the central contact, beside "
             r"the reactive cross-section (a reduced model) and the lumped neighbour (kJ). Above, the needs of the eight "
             r"tests that propagated after strong triggers, in order of the measured time: the least energy delivered to "
             r"the facing half with which the neighbour runs away within 10~s of the measured time; a three-dimensional "
             r"need is bracketed between the highest energy run whose mean reaches 255.7\textdegree C later, or not at "
             r"all, and the lowest whose mean reaches it by then. The cross-section's need is set against the "
             r"bracket's midpoint (difference, \%). $^{t}$, as in Supplementary Table~S7: the measured time is "
             r"reproduced only within the search's resolution of the threshold. Below, the thresholds of the tests "
             r"searched in three dimensions, in order of the trigger's fitted body energy: the least energy at which the "
             r"neighbour runs away within 900~s, with the ratio of the resolved to the lumped threshold by the brackets' "
             r"midpoints.}",
             r"\label{tab:3d}", r"\setlength{\tabcolsep}{4pt}",
             r"\begin{tabular}{lrrrrr}", r"\toprule",
             r"\multicolumn{6}{l}{\textit{Needs at the measured times}} \\",
             r"Test & Time (s) & Three-dimensional & Cross-section & Difference (\%) & Lumped \\", r"\midrule"]
    mark = {"matched": "", "threshold": r"$^{t}$", "bracketed": r"$^{b}$"}
    for r in N:
        t = r["test"]
        if r["status"] != "done":
            cell, diff = r["status"], ""
        else:
            cell, diff = _br(r["lo_J"], r["hi_J"]), "%+.1f" % (100 * r["d"])
        lines.append(" & ".join([tex_name(t), "%.0f" % float(tt[t]["time_to_propagation_s"]), cell,
                                 kj(r["xs_E_by_t_J"], 2) + mark.get(r["xs_status"], ""), diff,
                                 kj(r["lumped_E_by_t_J"], 2) + mark.get(r["lumped_status"], "")]) + r" \\")
    X = [r for r in s16["X"] if r["status"] == "done"]
    if X:
        for tau_lab in ("240 s constant power", "120 s constant power", "360 s constant power"):
            rows = sorted([r for r in X if r["delivery"] == tau_lab],
                          key=lambda r: float(tt[r["test"]]["time_to_propagation_s"]))
            if not rows:
                continue
            lines += [r"\midrule", r"\multicolumn{6}{l}{\textit{Needs with constant power over %s~s, counted as "
                                    r"delivered by the runaway}} \\" % tau_lab.split()[0]]
            for r in rows:
                t = r["test"]
                lines.append(" & ".join([tex_name(t), "%.0f" % float(tt[t]["time_to_propagation_s"]),
                                         _br(r["lo_by_t_J"], r["hi_by_t_J"]),
                                         kj(r["xs_E_by_t_J"], 2) + mark.get(r["xs_status"], ""),
                                         "%+.1f" % (100 * r["d"]),
                                         kj(r["lumped_E_by_t_J"], 2) + mark.get(r["lumped_status"], "")]) + r" \\")
    lines += [r"\midrule", r"\multicolumn{6}{l}{\textit{Thresholds}} \\",
              r"Test & Trigger & Three-dimensional & Cross-section & Lumped & Ratio \\", r"\midrule"]
    th = []
    for t, v in b1.items():
        th.append((t, v["bracket"]["lo_J"], v["bracket"]["hi_J"]))
    T = s16["T"]
    if T.get("status") == "done":
        th.append((T["test"], T["lo_J"], T["hi_J"]))
    for t, lo, hi in sorted(th, key=lambda x: -trig[x[0]]):
        (l1, h1), (l2, h2) = RB.brackets(nd[t])
        lump = "0" if h2 == 0 else _br(l2, h2)
        ratio = "" if h2 == 0 else "%.2f" % (0.5 * (lo + hi) / (0.5 * (l2 + h2)))
        lines.append(" & ".join([tex_name(t), kj(trig[t]), _br(lo, hi), kj(xs[t]["E_star_J"], 2), lump, ratio])
                     + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}", ""]
    return "\n".join(lines)


def table_s16():
    """Supplementary Table S16: every run of step 16 (results/stage16_runs.csv), search by search, with the archived
    runs that close a bracket (results/stage16_scorecard.json)."""
    s16 = _s16()
    runs = read_csv(os.path.join(RES, "stage16_runs.csv"))
    tt = {r["test"]: r for r in read_csv(os.path.join(ROOT, "inputs", "fransson2024", "m50_tests.csv"))}
    head = r"Search & Test & Delivery & Energy (kJ) & Mean reaches 255.7\textdegree C & Class \\"
    lines = [r"{\scriptsize\setlength{\tabcolsep}{4pt}",
             r"\begin{longtable}{llllll}",
             r"\caption{The runs of step 16, search by search: N, the needs with the 21.4~s pulse; T, PT-Exp1's "
             r"threshold; V, the need refined (the mesh by a factor of 1.5 and every step limit halved, together); X, "
             r"the needs with constant power. Each gives the energy delivered to the facing half, when the resolved "
             r"neighbour's mean reaches 255.7\textdegree C (or its peak where it does not within 900~s), and, for "
             r"a need, whether that comes no later than 10~s after the measured time (early) or later or not at all "
             r"(late). An asterisk marks an archived run that closes a bracket. The brackets are in "
             r"Table~4 of the main text and Table~\ref{tab:s-needs}.}\label{tab:s-step16}\\",
             r"\toprule", head, r"\midrule", r"\endfirsthead", r"\multicolumn{6}{l}{\textit{Continued}} \\",
             r"\toprule", head, r"\midrule", r"\endhead"]
    order = {"T": 0, "N": 1, "V": 2, "X": 3}
    lab = lambda r: ("pulse" if r["shape"] == "tri" else "%.0f~s" % float(r["tau_s"]))
    closing = {}
    for r in s16["N"] + s16["X"]:
        if r["status"] == "done":
            for side in ("lo", "hi"):
                if r[side + "_source"] != "stage16":
                    closing[r[side + "_id"]] = (r, side)
    tm = lambda t: float(tt[t]["time_to_propagation_s"])

    def outcome(c8, t, peak):
        return ("%.1f~s" % float(t)) if c8 == "True" else ("no; peak %.1f\\textdegree C" % float(peak))

    srt = sorted(runs, key=lambda r: (order.get(r["kind"], 9), r["test"], lab(r), float(r["E_J"])))
    for r in srt:
        if r["failed"] == "True":
            lines.append(" & ".join([r["kind"], tex_name(r["test"]), lab(r), kj(r["E_J"], 3), "failed", ""]) + r" \\")
            continue
        if r["kind"] in ("N", "X", "V"):
            lim = tm(r["test"]) + 10.0
            cl = "early" if (r["C8"] == "True" and float(r["t_C8_s"]) <= lim + 1e-9) else "late"
        else:
            cl = ""
        lines.append(" & ".join([r["kind"], tex_name(r["test"]), lab(r), kj(r["E_J"], 3),
                                 outcome(r["C8"], r["t_C8_s"], r["peak_mean_C"]), cl]) + r" \\")
    if closing:
        lines.append(r"\midrule")
        for rid, (r, side) in sorted(closing.items(), key=lambda x: x[1][0]["test"]):
            t = r[side + "_t_C8_s"]
            lines.append(" & ".join(["N" if r["search"] == "N" else "X", tex_name(r["test"]) + "$^{*}$",
                                     "pulse" if r["delivery"].startswith("21.39") else r["delivery"].split()[0] + "~s",
                                     kj(r[side + "_J"], 3),
                                     ("%.1f~s" % t) if t is not None else "no", "early" if side == "hi" else "late"])
                         + r" \\")
    lines += [r"\bottomrule", r"\end{longtable}", r"}", ""]
    return "\n".join(lines)


def _ns_value(pattern, idx=0, nd=1, unit="entry"):
    """A value as the numbers check traces it: the entry of manuscript/rebuild/number_sources.py whose context is
    `pattern`, its selector read from the files, its unit change applied, rounded to nd decimals; with the file and key
    it is read from."""
    sys.path.insert(0, os.path.join(ROOT, "manuscript", "rebuild"))
    import number_sources as NS
    for rx, nums, sel, u in NS.E:
        if rx == pattern:
            v = float(sel()[idx])
            u = u if unit == "entry" else unit
            if u == "kJ":
                v /= 1000.0
            elif u == "pct":
                v *= 100.0
            elif u == "abs":
                v = abs(v)
            return ("%%.%df" % nd) % v, sel.where
    raise KeyError(pattern)


def quoted_rows():
    """Read 7's list A (Brief 31, item 4): the results the main text and the supplement quote from runs or computations
    that no other table or figure shows, with the inputs held as assumptions from the earlier study. Every value is
    read by the numbers check's own entry for it (manuscript/rebuild/number_sources.py), or from the parameters file
    (manuscript/data/parameters.csv) for the inputs."""
    V = _ns_value
    rows = []

    def add(where, what, parts, src):
        import re
        rows.append({"where": where, "what": what, "value": "; ".join(parts),
                     "source": re.sub(r"(?<!\\)_", r"\\_", src)})

    a, w1 = V(r"at most at 226\.7")
    b, _ = V(r"226\.7\\degC, 29\.0~K short")
    c, w2 = V(r"lumped neighbour at 180\.6")
    add("3.1", "With body energies up to 33.2 kJ and no delivered heat, over the 5,248 runs at every contact, tab "
        "conductance, release time and connection and under the 200 kinetic draws: the highest peak of the resolved "
        "neighbour's hottest point, its margin to 255.7 \\textdegree C, and the lumped neighbour's highest peak",
        [a + " \\textdegree C", b + " K", c + " \\textdegree C"], "step 5's runs; " + w1.split(":")[0] + ", all\\_runs")
    sys.path.insert(0, os.path.join(ROOT, "manuscript", "rebuild"))
    import number_sources as NS
    hp = [e for e in NS.E if e[0] == r"226\.4 (to|and) 226\.7"]
    v226 = ["%.1f" % float(e[2]()[0]) for e in hp]
    lp, wl = V(r"175\.9 (to|and) 177\.4|lumped neighbour at most at 177\.4")
    add("3.1", "The eight tests with the largest fitted triggers held to 33.2 kJ, no delivered heat: the hottest "
        "point's peak at the high contact (two connections) and the lumped neighbour's highest peak",
        [" and ".join(v226) + " \\textdegree C", lp + " \\textdegree C"],
        "step 12's runs; " + wl.split(":")[0] + ", part\\_a.high")
    a, w = V(r"within 21\.7~s")
    add("3.1", "With the fitted triggers and no delivered heat, the latest time by which conduction carries the "
        "hottest point over 255.7 \\textdegree C in the eight tests with the largest triggers", [a + " s"],
        "step 12's runs; " + w.split(":")[0] + ", part\\_a.central")
    a, w = V(r"low contact its hottest point peaks at most at 162\.6|in all sixteen tests, peaking at most at 162\.6")
    add("3.1", "With the fitted triggers and no delivered heat at the low contact, the highest peak of the hottest "
        "point over the sixteen tests", [a + " \\textdegree C"], "step 7's runs; " + w.split(":")[0])
    a, w = V(r"106 to 128", 0, 0)
    b, _ = V(r"106 to 128", 1, 0)
    c, _ = V(r"22\.4 to 22\.6", 0)
    d, _ = V(r"22\.4 to 22\.6", 1)
    e, _ = V(r"4\.1 to 4\.8~kJ", 0)
    f, _ = V(r"4\.1 to 4\.8~kJ", 1)
    add("3.3", "In the three-dimensional threshold searches of PT-Exp4, PP-Exp2 and SP-Exp3: the lumped neighbour's "
        "runaway times, its reaction heat by 900 s, and the resolved neighbour's reaction heat by its own runaway",
        [a + " to " + b + " s", c + " to " + d + " kJ", e + " to " + f + " kJ"],
        "step 15's runs; results/stage15\\_paper\\_numbers.json, B1")
    a, w = V(r"runs away at 61\.5")
    add("3.3", "ST-Exp3 with 10.80 kJ over 21.4 s: the resolved neighbour's runaway", [a + " s"],
        "step 15's run; results/stage15\\_paper\\_numbers.json, B1")
    a, w = V(r"316\.5~s")
    b, _ = V(r"mean at 240\.1")
    add("3.4", "PT-Exp1 with a 360 s pulse at the upper end of the local threshold's bracket: the hottest point's "
        "crossing, on the cell's axis, and the mean then", [a + " s", b + " \\textdegree C"],
        "step 13's run; results/stage13\\_skin.csv")
    a, w = V(r"230\.4")
    b, _ = V(r"73\.3")
    add("3.4", "The lumped neighbour's ignition temperature with the trigger at 25 \\textdegree C, and the share of "
        "the low-temperature cathode reaction in the reaction heat at the ignition temperature",
        [a + " \\textdegree C", b + " \\%"], "step 13's computation; results/stage13\\_tign.csv")
    a, w = V(r"2\.1 to 2\.3", 0)
    b, _ = V(r"2\.1 to 2\.3", 1)
    add("3.4", "With no delivered heat in PT-Exp4, PP-Exp3 and ST-Exp2 at the central contact, the heat the lumped "
        "neighbour has taken in through the contact and wedge by 250 s beyond the resolved one's",
        [a + " to " + b + " kJ"], "step 15's accounts of archived runs; results/stage15\\_accounts.json")
    a, w = V(r"first two draws, at 191\.0 and 196\.5", 0)
    b, _ = V(r"first two draws, at 191\.0 and 196\.5", 1)
    add("3.4", "PT-Exp4 with 5.04 kJ over 21.4 s: the lumped neighbour's runaway under the kinetic draws ranked 5 "
        "and 50", [a + " and " + b + " s"], "step 15's runs; results/stage15\\_paper\\_numbers.json, B4")
    a, w = V(r"270\.3~s")
    b, _ = V(r"jump at 240\.4|jump beginning at 240\.4|233\.6 and 240\.4")
    add("3.4", "PT-Exp4 with 5.04 kJ over 21.4 s and every rate law shifted by 20 K: the resolved neighbour's "
        "runaway, and the far face's reading where its jump begins", [a + " s", b + " \\textdegree C"],
        "step 15's run; results/stage15\\_paper\\_numbers.json, B4")
    a, w = V(r"369\.3")
    add("3.5", "PT-Exp4, the 5.04 kJ pulse followed by 10 W: the resolved neighbour's runaway", [a + " s"],
        "step 15's run; results/stage15\\_paper\\_numbers.json, B3b")
    hp = [e for e in NS.E if e[0] == r"16\.3 and 16\.8|16\.3 to 16\.8"]
    v16 = ["%.1f" % float(e[2]()[0]) for e in hp]
    b, _ = V(r"51\.4~K")
    add("3.5", "PT-Exp4: the root mean square of the far face's difference from the record over 0 to 271.5 s with "
        "4.66 and 5.04 kJ over 21.4 s, and over 0 to 181.9 s with 7.42 kJ", [" and ".join(v16) + " K", b + " K"],
        "steps 10 and 15; results/stage10\\_paper\\_numbers.json, results/stage15\\_paper\\_numbers.json")
    a, w = V(r"235\.5 and 235\.8", 1)
    b, _ = V(r"235\.5 and 235\.8", 0)
    add("3.5", "PT-Exp4 with 7.42 kJ over 21.4 s, read post hoc: the two side probes' readings where the far face's "
        "jump begins", [a + " and " + b + " \\textdegree C"], "step 15's run; its series, read by its independent "
        "read (results/stage15\\_independent\\_read.md)")
    a, w = V(r"17 to 71~s", 0, 0)
    b, _ = V(r"17 to 71~s", 1, 0)
    c, _ = V(r"against 246 to 512~s", 0, 0)
    d, _ = V(r"against 246 to 512~s", 1, 0)
    add("3.7", "Wall time of a run on one two-core machine: the reactive cross-section, and the three-dimensional "
        "model in the same searches", [a + " to " + b + " s", c + " to " + d + " s"],
        "results/stage15\\_xs/*.json and results/stage15\\_runs/*.json, wall\\_s")
    a, w = V(r"came 6\.01 to 17\.13", 0, 2)
    b, _ = V(r"came 6\.01 to 17\.13", 1, 2)
    four = ["%.2f" % float(e[2]()[0]) for e in NS.E if e[0] == r"at 6\.25, 10\.23, 16\.04 and 17\.02"]
    c, _ = V(r"at 11\.48~s under the posterior mean", 0, 2)
    sd_k = json.load(open(os.path.join(RES, "stage3a_metrics.json")))["metrics"]["two_E33223_tau30_G0.5"]["onset_s"]["hottest_node"]["sd"]
    sd_t = json.load(open(os.path.join(RES, "stage3bc_metrics.json")))["thermal_30_at_mean_kinetics"]["hottest_onset_s"]["sd"]
    add("S2", "Step 3, the earlier geometry's case (33.2 kJ over 30 s, a 500 mW\\,K$^{-1}$ busbar): the hot spot's "
        "onset over the 200 kinetic draws, under the four draws step 11 took, under the posterior mean, and its "
        "standard deviation over the kinetic and over the 30 thermal draws",
        [a + " to " + b + " s", ", ".join(four) + " s", c + " s", "%.2f and %.3f s" % (sd_k, sd_t)],
        "step 3's runs; results/stage3a\\_onsets.csv, stage3a\\_metrics.json, stage11\\_draws.csv, stage3bc\\_metrics.json")
    par = {r["symbol"]: r for r in read_csv(os.path.join(ROOT, "manuscript", "data", "parameters.csv"))}
    for sym, what, val in (("g_tab", "Tab conductance per tab", "6.8 mW\\,K$^{-1}$ (5 and 10 as brackets)"),
                           ("k_can", "Can conductivity", "15 W\\,m$^{-1}$\\,K$^{-1}$"),
                           ("m_can; c_can", "Can mass and specific heat", "9 g; 500 J\\,kg$^{-1}$\\,K$^{-1}$"),
                           ("k_air", "Air in the wedge", "0.03 W\\,m$^{-1}$\\,K$^{-1}$"),
                           ("theta_s", "Contact sector, either side of the line of contact", "45\\textdegree"),
                           ("h_room", "Room convection", "10 W\\,m$^{-2}$\\,K$^{-1}$"),
                           ("m_cell", "Cell mass", "65 g")):
        ev = par[sym]["file_evidence"].split(";")[0]
        add("Table 2", what + ", set by the earlier study without a primary source and held here as an assumption",
            [val], ev.replace("_", "\\_"))
    return rows


def table_s17():
    rows = quoted_rows()
    with open(os.path.join(ROOT, "manuscript", "rebuild", "data", "s17_quoted.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["where", "what", "value", "source"])
        w.writeheader()
        w.writerows(rows)
    lines = [r"{\scriptsize\setlength{\tabcolsep}{4pt}",
             r"\begin{longtable}{>{\raggedright\arraybackslash}p{0.07\textwidth}>{\raggedright\arraybackslash}p{0.41\textwidth}"
             r">{\raggedright\arraybackslash}p{0.17\textwidth}>{\raggedright\arraybackslash}p{0.25\textwidth}}",
             r"\caption{Results that the main text (by section) and the supplement quote from runs or computations "
             r"that no other table or figure shows, and the inputs that the earlier study set without a primary source "
             r"(Table~2 of the main text, $^{a}$), each with the runs or the code it comes from. Every value here is "
             r"read from its file by the numbers check's own entry for it.}\label{tab:s-quoted}\\",
             r"\toprule", r"Where & Result & Value & From \\", r"\midrule", r"\endfirsthead",
             r"\multicolumn{4}{l}{\textit{Continued}} \\", r"\toprule", r"Where & Result & Value & From \\",
             r"\midrule", r"\endhead"]
    import re as _re

    def paths(src):
        """File paths in \\nolinkurl, so that xurl may break them; the underscores unescaped inside."""
        return _re.sub(r"((?:[A-Za-z0-9.*\-]|\\_)+/(?:[A-Za-z0-9./*\-]|\\_)+)",
                       lambda m: r"\nolinkurl{%s}" % m.group(1).replace("\\_", "_"), src)

    for r in rows:
        lines.append("%s & %s & %s & %s \\\\" % (r["where"], r["what"], r["value"], paths(r["source"])))
    lines += [r"\bottomrule", r"\end{longtable}", r"}", ""]
    return "\n".join(lines)


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, fn in [("t1_tests.tex", table1), ("t2_parameters.tex", table2), ("t3_bounds.tex", table3),
                     ("s3_thresholds.tex", table_s3), ("s7_needs.tex", table_s7), ("s8_reduced.tex", table_s8),
                     ("s9_heldout.tex", table_s9), ("s10_twobody.tex", table_s10),
                     ("s11_archived.tex", table_s11), ("s12_step11.tex", table_s12),
                     ("s13_farface.tex", table_s13), ("s14_archived_runs.tex", table_s14),
                     ("s15_nodelivery.tex", table_s15), ("s17_quoted.tex", table_s17),
                     ("t4_3d.tex", table4), ("s16_step16.tex", table_s16)]:
        open(os.path.join(OUT, name), "w").write(fn())
    print("tables written to", os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
