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

HERE = os.path.dirname(os.path.abspath(__file__))
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


def table1():
    meas = {r["test"]: r for r in read_csv(os.path.join(ROOT, "inputs", "fransson2024", "m50_tests.csv"))}
    trig = {r["test"]: float(r["E_J"]) for r in read_csv(os.path.join(RES, "stage7_triggers.csv")) if r["kind"] == "test"}
    cat = {"cell movement": "c.m.", "": "--"}
    lines = [r"\begin{table}[!tbp]", r"\centering", r"\footnotesize", r"\setlength{\tabcolsep}{2.6pt}",
             r"\caption{The sixteen two-cell tests of LG M50 cells of Fransson et al.~\cite{fransson2024exploring} "
             r"(their Tables 3 and 4), and the body energy $E_\mathrm{b}$ that puts the model's trigger at the measured "
             r"trigger peak at the central contact when released over 21.39~s. Times run from the trigger's runaway "
             r"to the neighbour's. The two maxima marked $^{a}$ may not be the neighbour's surface and are treated as "
             r"exploratory. Category, Fransson et al.'s failure category: 1, the trigger's nail-penetration failure; "
             r"2, failure in the propagating cell; 4, sidewall rupture of the trigger; c.m., ``cell movement'' in the "
             r"X-ray camera's field of view, given in place of a category; a dash, none given.}",
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
        ("Cell diameter and length", "21.1 and 70.1 mm", r"\cite{satte2026twocell}"),
        ("Can: wall and conductivity; mass and specific heat",
         r"0.25 mm, 15 W\,m$^{-1}$\,K$^{-1}$; 9 g, 500 J\,kg$^{-1}$\,K$^{-1}$", r"\cite{satte2026twocell}"),
        ("Roll conductivity across and along the layers", r"1.3 and 25 W\,m$^{-1}$\,K$^{-1}$",
         r"\cite{oregan2022thermal,chen2021simplified}"),
        ("Cell heat capacity", r"61.75 J\,K$^{-1}$ (65 g at 950 J\,kg$^{-1}$\,K$^{-1}$)", r"\cite{satte2026twocell}"),
        ("Resolved neighbour", "half model, 19,355 nodes", "this study"),
        (r"\textit{Heat paths}", None, None),
        (r"Contact conductance between the cans, $h_c$", r"200, 2,000, 3,700 W\,m$^{-2}$\,K$^{-1}$ (low, central, high)",
         r"\cite[Table 2.1]{lienhard2024heat}"),
        ("Air in the wedge beside the contact", r"0.03 W\,m$^{-1}$\,K$^{-1}$", r"\cite{satte2026twocell}"),
        ("Welded tabs: series one, parallel two", r"6.8 mW\,K$^{-1}$ per tab (5 and 10 as brackets)",
         r"\cite{satte2026twocell}"),
        ("View factor between the cans; emissivity", "0.1817; 0.8", r"\cite{bergman2011fundamentals}"),
        ("Room convection; ambient", r"10 W\,m$^{-2}$\,K$^{-1}$; 25\textdegree C", r"\cite{satte2026twocell}"),
        (r"\textit{Trigger}", None, None),
        ("Model and release", "one temperature; triangular over 21.39 s", r"\cite{fransson2024exploring}"),
        (r"Body energy $E_\mathrm{b}$", "9.0 to 54.3 kJ, one per test (Table 1); 33.2 kJ held to calorimetry",
         r"\cite{fransson2024exploring,finegan2024databank}"),
        (r"\textit{Kinetics}", None, None),
        ("Model", "Bayesian chemical reaction neural network: posterior mean, and 200 joint draws",
         r"\cite{koenig2025uncertainty}"),
        ("Reactant masses; initial SEI amount", r"per 720 g reference cell; 0.15 (fresh), 0 (aged)",
         r"\cite{koenig2025uncertainty}"),
        ("Runaway level", r"255.7\textdegree C, within 900 s", r"\cite{koenig2025uncertainty}"),
        (r"\textit{Delivered heat}", None, None),
        ("Region", "the half of the neighbour's can facing the trigger, a uniform flux", "this study"),
        ("Shapes", "triangular over 21.39 s; constant power over 120, 240 or 360 s", "this study"),
    ]
    lines = [r"\begin{table}[!tbp]", r"\centering", r"\footnotesize",
             r"\caption{The model's parameters and their sources. The two-cell geometry and its solver are those of "
             r"an earlier, archived study by the author~\cite{satte2026twocell}.}",
             r"\label{tab:params}", r"\renewcommand{\arraystretch}{0.95}",
             r"\setlength{\tabcolsep}{4pt}", r"\begin{tabular}{p{0.33\textwidth}p{0.42\textwidth}p{0.17\textwidth}}", r"\toprule",
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
             "A6": "The neighbour's own discharge (parallel tests)"}
    sets = {"A1": r"a black body at 1500\textdegree C filling the facing half's view, the holder possibly reflecting; "
                  r"held on the vent's axis, about 0.85~kJ",
            "A2": r"convection at 398.5~m\,s$^{-1}$ with hydrogen's properties~\cite{churchill1977correlating}, "
                  r"at most twice its whole-cylinder mean on one half, and radiation at 1500\textdegree C",
            "A3": r"what the ejecta can release; a narrow jet strikes the facing half from a sixth of the circumference",
            "A4": r"what the ejecta can release; melt falls onto the facing half from half of the circumference",
            "A5": r"no source gives the inserts' material or contact (247.3~kJ if bounded as the jet and melt are)",
            "A6": r"the rated stored energy (15.6~kJ within 21.4~s if the resistance stayed at its 25\textdegree C value)"}
    meas = {"A1": "the flame's position and temperature beside the cells",
            "A2": "the gas's temperature and velocity in the wedges beside the line of contact",
            "A3": "where breaches face and what they carry",
            "A4": "the debris left on the neighbour",
            "A5": "the holder's inserts and their contact",
            "A6": "the current between parallel cells"}
    lines = [r"\begin{table}[!tbp]", r"\centering", r"\footnotesize",
             r"\caption{What each path can deliver to the neighbour's facing half, from published inputs alone: the "
             r"upper bound within the 21.4~s of the pulse and in total (every lower bound is zero), what sets it, and "
             r"the measurement that would bound it more tightly. What the ejecta can release in the rig is 225.8~kJ, "
             r"the most calorimetry measured for this cell's ejecta (89.34~kJ)~\cite{finegan2024databank} with the "
             r"heat of burning the vent gas in open air (at most 136.5~kJ, measured on another 21700 "
             r"cell)~\cite{vendra2022numerical}; the gas and flame are taken at up to 1500\textdegree C~\cite{chen2020experimental} "
             r"and the vent gas at up to 398.5~m\,s$^{-1}$~\cite{gillich2024mechanical}.}",
             r"\label{tab:bounds}", r"\renewcommand{\arraystretch}{0.95}",
             r"\setlength{\tabcolsep}{4pt}", r"\begin{tabular}{p{0.19\textwidth}rrp{0.29\textwidth}p{0.19\textwidth}}", r"\toprule",
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
             r"\caption{The thresholds of the sixteen tests with the 21.4~s pulse (kJ; a bracket is the largest "
             r"energy run that does not meet the criterion and the smallest that does), and, for the nine propagated "
             r"tests, the energy delivered by the measured time at which the lumped neighbour and the resolved "
             r"neighbour run away then (by the reactive cross-section). An energy marked $^{t}$ is a threshold whose "
             r"search ended there because the measured time lies within its resolution.}\label{tab:s-thresholds}\\",
             r"\toprule", r"Test & Hottest point & Lumped & Resolved, cross-section & Resolved, three-dimensional & "
             r"By the measured time: lumped; resolved \\", r"\midrule", r"\endfirsthead", r"\toprule",
             r"Test & Hottest point & Lumped & Resolved, cross-section & Resolved, three-dimensional & "
             r"By the measured time: lumped; resolved \\", r"\midrule", r"\endhead"]
    for t in TESTS:
        r = nd[t]
        c1 = "0" if float(r["threshold_C1_hi_J"]) == 0 else "(%s, %s]" % (kj(r["threshold_C1_lo_J"], 2), kj(r["threshold_C1_hi_J"], 2))
        lo2, hi2 = r["threshold_C2_lo_J"], r["threshold_C2_hi_J"]
        if "threshold" in r["reading_21s"]:
            lo2, hi2 = r["need_21s_lo_J"], r["need_21s_hi_J"]
        c2 = "0" if float(hi2) == 0 else "(%s, %s]" % (kj(lo2, 2), kj(hi2, 2))
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


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, fn in [("t1_tests.tex", table1), ("t2_parameters.tex", table2), ("t3_bounds.tex", table3),
                     ("s3_thresholds.tex", table_s3)]:
        open(os.path.join(OUT, name), "w").write(fn())
    print("tables written to", os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
