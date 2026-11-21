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
        ("Model and release", "one temperature; triangular over 21.39 s", r"\cite{fransson2024exploring}"),
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
                    "longest combustion reported for a 21700 cell, about %.0f s (Supplementary Section S6); in "
                    "PT-Exp4 also the pulse " % flame_s()) +
                   r"followed by a constant power; for Section~\ref{sec:res-why}, triangular over 5 to 360 s",
         "this study"),
    ]
    lines = [r"\begin{table}[!tbp]", r"\centering", r"\scriptsize",
             r"\caption{The model's parameters and their sources. The two-cell geometry and its solver are those of "
             r"an earlier, archived study by the author~\cite{satte2026twocell}; $^{a}$, a value that study set "
             r"without a primary source, held here as an assumption.}",
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
    lines = [r"{\footnotesize\setlength{\tabcolsep}{3pt}", r"\begin{longtable}{p{0.1\textwidth}p{0.13\textwidth}p{0.15\textwidth}p{0.15\textwidth}p{0.15\textwidth}p{0.18\textwidth}}",
             r"\caption{The thresholds of the sixteen tests with the 21.4~s pulse at the central contact (kJ; a bracket is the largest "
             r"energy run that does not meet the criterion and the smallest that does), and, for the nine propagated "
             r"tests, their needs: the least energy with which the lumped neighbour and the resolved neighbour (by "
             r"the reactive cross-section) run away within 10~s of the measured time, counted as delivered by the "
             r"run's own runaway. An energy marked $^{t}$ is the least energy "
             r"run whose runaway comes before the measured time when the next lower run, 0.5\,\% of the test's "
             r"ejected energy below, gives none within 900~s: the measured time is reproduced only between the two, "
             r"within that resolution of the threshold, and the value, the higher, can exceed the bracket beside it. Supplementary Table~\ref{tab:s-needs} gives the other delivery shapes.}"
             r"\label{tab:s-thresholds}\\",
             r"\toprule", r"Test & Hottest point & Lumped & Resolved, cross-section & Resolved, three-dimensional & "
             r"Needs: lumped; resolved \\", r"\midrule", r"\endfirsthead",
             r"\multicolumn{6}{l}{\textit{Continued}} \\", r"\toprule",
             r"Test & Hottest point & Lumped & Resolved, cross-section & Resolved, three-dimensional & "
             r"Needs: lumped; resolved \\", r"\midrule", r"\endhead"]
    for t in TESTS:
        r = nd[t]
        (lo1, hi1), (lo2, hi2) = RB.brackets(r)          # the narrowest bracket the archive holds (Stage 13 refined four)
        c1 = "0" if hi1 == 0 else "(%s, %s]" % (kj(lo1, 2), kj(hi1, 2))
        c2 = "0" if hi2 == 0 else "(%s, %s]" % (kj(lo2, 2), kj(hi2, 2))
        c8 = "(%s, %s]" % (kj(xs[t]["lo_J"], 2), kj(xs[t]["hi_J"], 2))
        d3 = "(%s, %s]" % (kj(b1[t]["bracket"]["lo_J"], 2), kj(b1[t]["bracket"]["hi_J"], 2)) if t in b1 else ""
        row = next((x for x in tab if x["test"] == t and x["delivery"].startswith("21.39")), None)
        if row is not None:
            mk2 = r"$^{t}$" if row["C2_status"] == "threshold" else ""
            mk8 = r"$^{t}$" if row["C8_xs_status"] == "threshold" else ""
            need = "%s%s; %s%s" % (kj(row["C2_E_by_t_J"], 2), mk2, kj(row["C8_xs_E_by_t_J"], 2), mk8)
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
    head = (r"Test & Time (s) & Delivery & Lumped & Resolved & Resolved, in all & Its runaway (s) \\")
    lines = [r"{\footnotesize\setlength{\tabcolsep}{3pt}",
             r"\begin{longtable}{p{0.09\textwidth}p{0.065\textwidth}p{0.17\textwidth}p{0.1\textwidth}p{0.1\textwidth}"
             r"p{0.11\textwidth}p{0.09\textwidth}}",
             r"\caption{The needs of the nine tests that propagated under the four delivery shapes (kJ): the least "
             r"energy with which the lumped neighbour (Lumped), and the resolved neighbour by the reactive cross-section "
             r"(Resolved), run away within 10~s of the measured time (Time), counted as delivered by the run's own "
             r"runaway; for the resolved neighbour, the energy of that delivery in all, over its whole shape, and the "
             r"time of its runaway in that run. $^{t}$, the least energy run whose runaway comes before the measured "
             r"time, the next lower run, 0.5\,\% of the test's ejected energy below, giving none within 900~s, so that "
             r"the measured time is reproduced only between the two, within that resolution of the threshold; the "
             r"energy is counted to that run's runaway; "
             r"$^{b}$, interpolated between the two runs whose runaways bracket the measured time, and counted "
             r"to the measured time; a dash, no energy on the search's grid gave a runaway. The four shapes deliver the "
             r"same energy by the runaway only where the delivery ends before it. Below, for the seven tests that did not propagate, the energy "
             r"that puts the far face's peak at the measured maximum, within 5~K, under each shape; $^{a}$, a maximum "
             r"that may not be the neighbour's surface (exploratory).}\label{tab:s-needs}\\",
             r"\toprule", head, r"\midrule", r"\endfirsthead", r"\multicolumn{7}{l}{\textit{Continued}} \\",
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
            lines.append(" & ".join([tex_name(t) if i == 0 else "", x["t_measured_s"].split(".")[0] if i == 0 else "",
                                     lab, c2, c8, e8, t8]) + r" \\")
        lines.append(r"\midrule")
    lines += [r"\multicolumn{7}{l}{\textit{Tests that did not propagate}} \\",
              r"Test & Peak (\textdegree C) & Delivery & \multicolumn{4}{l}{Far face's peak at the measured peak (kJ)} \\",
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
            lines.append(" & ".join([tex_name(t) if i == 0 else "", mx, lab, r"\multicolumn{4}{l}{%s}" % v]) + r" \\")
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
             r"PT-Exp1 only, as Fig.~3a of the main text draws it. Hottest point "
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
    """The two-body model against the lumped searches at the low and high contacts (results/stage13_twobody.csv)."""
    tb = read_csv(os.path.join(RES, "stage13_twobody.csv"))
    rows = [r for r in tb if r["h"] in ("low", "high") and r["tau_d_s"] == RB.TAU21]
    lines = [r"{\footnotesize\setlength{\tabcolsep}{2.5pt}",
             r"\begin{longtable}{llrrrrrl}",
             r"\caption{The lumped threshold with the 21.4~s pulse at the low and the high contact against the "
             r"two-body model of Section~2.5 of the main text (kJ): the search's bracket, the two-body model's value "
             r"and its difference from the bracket's midpoint, against the larger of 10\,\% of the midpoint and "
             r"300~J, registered before the searches.}\label{tab:s-twobody}\\",
             r"\toprule", r"Test & Contact & $E_\mathrm{b}$ & Lumped bracket & Two-body & Difference & Tolerance & Within \\",
             r"\midrule", r"\endfirsthead", r"\multicolumn{8}{l}{\textit{Continued}} \\", r"\toprule",
             r"Test & Contact & $E_\mathrm{b}$ & Lumped bracket & Two-body & Difference & Tolerance & Within \\",
             r"\midrule", r"\endhead"]
    for t in TESTS:
        for h in ("low", "high"):
            r = next(x for x in rows if x["test"] == t and x["h"] == h)
            br = "0" if float(r["lum_hi_J"]) == 0 else "(%s, %s]" % (kj(r["lum_lo_J"], 2), kj(r["lum_hi_J"], 2))
            within = "yes" if abs(float(r["B2_minus_mid_J"])) <= float(r["P8_tol_J"]) + 1e-9 else "no"
            lines.append(" & ".join([tex_name(t) if h == "low" else "", h, kj(r["E_b_J"], 1) if h == "low" else "",
                                     br, kj(r["B2_E_J"], 2), kj(r["B2_minus_mid_J"], 2), kj(r["P8_tol_J"], 2),
                                     within]) + r" \\")
    lines += [r"\bottomrule", r"\end{longtable}", r"}"]
    return "\n".join(lines) + "\n"


TESTS16 = [f"M50_{c}_Exp{i}" for c in ("PT", "PP", "ST", "SP") for i in range(1, 5)]


def table_s11():
    """The 151 archived three-dimensional runs at the central contact that the reactive cross-section was set against
    (results/stage15_cross_section.json, A1_rows), by test and delivery. The numbers check recomputes every row from
    the same rows by its own code."""
    rows = json.load(open(os.path.join(RES, "stage15_cross_section.json")))["A1_rows"]
    lines = [r"\begin{table}[!htbp]", r"\centering", r"\footnotesize",
             r"\caption{The 151 archived three-dimensional runs at the central contact against which the reactive "
             r"cross-section was set (Section~3.6 of the main text), by test and delivery: the runs with no delivery, "
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
    lab = [("mean", "Posterior mean, central properties")]
    for k in ("d188", "d83", "d40", "d184"):
        lab.append((k, "Kinetic draw ranked %s of 200" % d[k]["rank"]))
    lab += [("kr_min", r"Least conductivity across the layers, %.3f W\,m$^{-1}$\,K$^{-1}$" % float(d["kr_min"]["k_radial_W_mK"])),
            ("kr_max", r"Largest conductivity across the layers, %.3f W\,m$^{-1}$\,K$^{-1}$" % float(d["kr_max"]["k_radial_W_mK"])),
            ("c_min", r"Least specific heat, %.0f J\,kg$^{-1}$\,K$^{-1}$" % float(d["c_min"]["c_roll_J_kgK"])),
            ("c_max", r"Largest specific heat, %.0f J\,kg$^{-1}$\,K$^{-1}$" % float(d["c_max"]["c_roll_J_kgK"]))]
    return lab


def table_s12():
    """Step 11's lumped thresholds with the 21.39 s pulse at the central contact, under the posterior mean and its eight
    draws (results/stage11_thresholds.csv, criterion C2), in kJ: the fractions' bracket times the test's ejected energy
    (results/stage8_ejected.csv). Also writes manuscript/rebuild/data/step11_lumped_kJ.csv, the table's values, for the
    numbers check."""
    ee = {r["id"]: float(r["E_e_J"]) for r in read_csv(os.path.join(RES, "stage8_ejected.csv")) if r["kind"] == "test"}
    th = {(r["test"], r["draw"]): r for r in read_csv(os.path.join(RES, "stage11_thresholds.csv")) if r["criterion"] == "C2"}
    data = []
    lines = [r"\begin{table}[!htbp]", r"\centering", r"\footnotesize",
             r"\caption{The lumped threshold of the four tests that step~11 searched, with the 21.4~s pulse at the "
             r"central contact, under the posterior mean and the central properties and under the step's eight draws "
             r"(Section~\ref{sec:s-key}): the bracket between the largest energy run that does not run the lumped "
             r"neighbour away and the smallest that does, in kJ, on a grid of 0.0125 of the test's ejected energy "
             r"(the last row); 0, met with no delivery. The main text quotes a bracket's midpoint. The kinetic draws "
             r"are ranked, earliest first, by the time of the hot spot's onset in step~3's case; the thermal draws "
             r"are the extremes among thirty over the roll's published ranges.}",
             r"\label{tab:s-step11}", r"\setlength{\tabcolsep}{4pt}",
             r"\begin{tabular}{>{\raggedright\arraybackslash}p{0.33\textwidth}rrrr}", r"\toprule",
             r"Draw & PT-Exp1 & PP-Exp3 & ST-Exp2 & SP-Exp3 \\", r"\midrule"]
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
            lines.append(r"\midrule")
    lines.append(r"\midrule")
    lines.append(r"Ejected energy (kJ) & " + " & ".join("%.2f" % (ee[t] / 1e3) for t in S11_TESTS) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}", ""]
    out = os.path.join(ROOT, "manuscript", "rebuild", "data", "step11_lumped_kJ.csv")
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(data[0].keys()))
        w.writeheader()
        w.writerows(data)
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
    rows += [("Low contact, posterior mean and central properties", ("central", "low")),
             ("High contact, posterior mean and central properties", ("central", "high"))]
    lines = [r"\begin{table}[!htbp]", r"\centering", r"\footnotesize",
             r"\caption{The far face's peak with no delivered heat over 900~s (\textdegree C) in the five tests that did "
             r"not propagate and report low maxima, with each test's fitted trigger, against the maximum Fransson et "
             r"al.\ measured: at the central contact under the posterior mean and the central properties and under "
             r"step~11's four thermal draws, and at the low and high contacts under the posterior mean and the "
             r"central properties.}",
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


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, fn in [("t1_tests.tex", table1), ("t2_parameters.tex", table2), ("t3_bounds.tex", table3),
                     ("s3_thresholds.tex", table_s3), ("s7_needs.tex", table_s7), ("s8_reduced.tex", table_s8),
                     ("s9_heldout.tex", table_s9), ("s10_twobody.tex", table_s10),
                     ("s11_archived.tex", table_s11), ("s12_step11.tex", table_s12),
                     ("s13_farface.tex", table_s13)]:
        open(os.path.join(OUT, name), "w").write(fn())
    print("tables written to", os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
