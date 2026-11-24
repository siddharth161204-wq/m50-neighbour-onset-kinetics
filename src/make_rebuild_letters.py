"""The cover letter and the pre-submission enquiry of the rebuilt manuscript (Brief 29), one of each per journal.

The title and the abstract are read from manuscript/rebuild/main.tex, so the letters always carry the manuscript's
own; every number in the letters is traced by manuscript/numbers_check.py --rebuild. The letters differ between the
journals only in the editor addressed, the sentence on the journal's scope and, for the Journal of Power Sources,
whose guide asks that a cover letter carry no funding information or author declarations, the end of the sentence
about the author. Nothing here is sent: the files are drafts for the author.

Writes manuscript/rebuild/cover_letter.md and presubmission_enquiry.md (all three journals in each), and, for each
journal, letters/Cover_letter_<journal>.docx with its text in letters/Cover_letter_<journal>.txt, and
letters/Enquiry_<journal>.txt; the numbers check reads the .txt files.

Usage: python3 src/make_rebuild_letters.py
"""
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
RB = os.path.join(HERE, "..", "manuscript", "rebuild")

JOURNALS = [
    dict(key="J_Power_Sources", name="Journal of Power Sources", to="Dr Belharouak",
         editor="Ilias Belharouak, Editor-in-Chief",
         fit=("It falls within the journal's priority area of safety, as a computational study set against "
              "published experiments."),
         declarations=False),
    dict(key="J_Energy_Storage", name="Journal of Energy Storage", to="Professor Cabeza and Dr Jurasz",
         editor="Luisa F. Cabeza and Jakub Jurasz, Editors-in-Chief",
         fit=("It falls within the journal's topics of modelling and of the safety of energy storage systems: it "
              "gives what a neighbouring cell in a module needs before it follows a failing one."),
         declarations=True),
    dict(key="Fire_Safety_J", name="Fire Safety Journal", to="Professor Bisby and Professor Merci",
         editor="Luke Bisby and Bart Merci, Editors",
         fit=("It falls within fire safety science and engineering as a quantitative account of the heat that "
              "carries thermal runaway from one cell to the next."),
         declarations=True),
]


def plain(tex):
    s = re.sub(r"%[A-Z-]+\n?", "", tex)
    s = s.replace("\\degC{}", " °C").replace("\\degC", " °C").replace("\\,\\%", " %").replace("~", " ")
    s = s.replace("\\,", " ").replace("{}", "")
    s = re.sub(r"\s+", " ", s).strip()
    return s.replace("  ", " ")


def main():
    import math
    import sys
    sys.path.insert(0, HERE)
    import rebuild_headline as HL
    sys.path.insert(0, RB)
    import number_sources as NS
    # the strong triggers' ratio across the brackets, rounded outward, as the manuscript and the graphical abstract give it
    r_lo = min(math.floor(100 * NS.ratio_span(t)[0]) / 100 for t in ("PT_Exp4", "PP_Exp2"))
    r_hi = math.ceil(NS.ratio_span("PP_Exp2")[1] * 100) / 100
    H = {"n3": HL.range_3d_kJ(), "nl": HL.range_lumped_kJ(), "sh": HL.shares_pct(), "rs": (r_lo, r_hi),
         "rw": HL.weak_range()}
    import csv
    with open(os.path.join(RB, "data", "predictions_registry.csv")) as fh:
        n_pred = sum(1 for _ in csv.DictReader(fh))
    tex = open(os.path.join(RB, "main.tex")).read()
    title = re.search(r"\\title\{(.*?)\}\n", tex, re.S).group(1)
    abstract = plain(tex[tex.index("\\begin{abstract}") + len("\\begin{abstract}"):tex.index("\\end{abstract}")])
    author = "I am a mechanical engineer (B.Tech 2026, COEP Technological University, Pune), working independently"
    sign = ["Yours sincerely,", "", "Siddharth Satte", "Independent researcher, Pune, India",
            "siddharth161204@gmail.com"]
    letters, enquiries = [], []
    os.makedirs(os.path.join(RB, "letters"), exist_ok=True)
    for j in JOURNALS:
        body = [
            f"Dear {j['to']},",
            "",
            f"I submit the manuscript \"{title}\" for consideration as a research article in the {j['name']}.",
            "",
            ("Models of thermal runaway propagation in modules must choose how much of a failing cell's vented heat "
             "reaches its neighbour, which published tests do not measure, and must represent each cell as one "
             "temperature or as a resolved temperature field. The manuscript asks how much heat must reach a neighbour "
             "for it to follow, and whether published tests can say, for two touching LG M50 cells modelled with "
             "kinetics fitted to calorimetry of NCM811 and graphite, against sixteen published two-cell tests."),
            "",
            ("Each failing cell's energy is fitted to its test's peak temperature, and the neighbour is solved both as "
             "one temperature and as a three-dimensional field; in each, the heat it needs through its side facing the "
             "failing cell to run away at the test's measured time is searched, and the bounds that published inputs "
             "set on each path that could deliver it are worked out."),
            "",
            ("From a failing cell releasing at most the 33.2 kJ that calorimetry measured for this cell, conduction and "
             "radiation leave the neighbour at least 29 K short of runaway. With heat delivered over 21.4 s, the eight "
             f"tests that propagated after strong triggers need {H['n3'][0]:.1f} to {H['n3'][1]:.1f} kJ if the "
             f"neighbour is resolved and {H['nl'][0]:.1f} to {H['nl'][1]:.1f} kJ if it is lumped, "
             f"{H['sh'][0]:.1f} to {H['sh'][1]:.1f} % and {H['sh'][2]:.1f} to {H['sh'][3]:.1f} % of the Databank's "
             "median ejecta energy for this cell. The least energy that runs the resolved neighbour away is "
             f"{H['rs'][0]:.2f} to {H['rs'][1]:.2f} times the lumped neighbour's after two strong triggers and "
             f"{H['rw'][0]:.2f} to {H['rw'][1]:.2f} times after both weak ones. Published inputs cannot bound any "
             "delivery path below 27.9 kJ."),
            "",
            ("For readers who model propagation in packs, the paper gives the heat a neighbour needs under each of the "
             "two common representations of a cell, set against sixteen tests, the factor between them and its "
             "direction, and the measurement, a heat flux on the neighbour's facing side, that could test them."),
            "",
            j["fit"],
            "",
            (f"The code, inputs and run records are archived openly, with the study's {n_pred} predictions, each committed "
             "before its runs."),
            "",
            (author + (", with no funding and no competing interests." if j["declarations"] else ".")
             + " The manuscript has not been published and is not under consideration elsewhere."),
            "",
        ] + sign
        letters.append((j, body))
        enq = [
            f"Dear {j['to']},",
            "",
            (f"Would the manuscript below be within the scope of the {j['name']}? It estimates, against sixteen "
             "published two-cell tests, how much heat must reach a neighbouring lithium-ion cell for thermal runaway "
             "to propagate; it shows that the estimate depends on whether the neighbour is modelled as one "
             "temperature or as a resolved field, in a direction that went with the failing cell's energy in the "
             "tests searched in three dimensions, and names the measurement that could test it. "
             + j["fit"].replace("It falls", "It belongs", 1)
             + " " + author + ". The title and abstract follow."),
            "",
        ] + sign
        n = len(" ".join(enq).replace("siddharth161204@gmail.com", "x").split())
        assert n <= 150, (j["key"], n)
        assert sum(x.count("?") for x in enq) == 1
        enquiries.append((j, enq + ["", f"Title: {title}", "", f"Abstract: {abstract}"], n))
        md = os.path.join(RB, "letters", f"Cover_letter_{j['key']}.md")
        open(md, "w").write("\n".join(body) + "\n")
        subprocess.run(["pandoc", md, "-o", md.replace(".md", ".docx")], check=True)
        os.replace(md, md.replace(".md", ".txt"))
        open(os.path.join(RB, "letters", f"Enquiry_{j['key']}.txt"), "w").write(
            "\n".join(enquiries[-1][1]) + "\n")
    out = ["# Cover letters (drafts, not sent; 24 November 2026)", "",
           "One letter per journal; they differ only in the editor addressed, the sentence on the journal's scope and, "
           "for the Journal of Power Sources, whose guide asks that the letter carry no funding information or author "
           "declarations, the end of the sentence about the author. Word files of each are in `letters/`.", ""]
    for j, body in letters:
        words = len(" ".join(body).split())
        out += [f"## {j['name']} ({j['editor']}; {words} words)", ""] + body + [""]
    open(os.path.join(RB, "cover_letter.md"), "w").write("\n".join(out))
    out = ["# Pre-submission enquiries (drafts, not sent; 24 November 2026)", "",
           "One per journal: one question, whether the manuscript is within scope, and one sentence on why it belongs; "
           "the text before the title and abstract is at most 150 words. None of the three journals' guides or "
           "editorial-board pages gives an address for enquiries (journal_rules_20261120.md, section 7); the "
           "enquiry goes out from the main chat on the author's word.", ""]
    for j, enq, n in enquiries:
        out += [f"## {j['name']} (to {j['editor']}; {n} words before the title and abstract)", ""] + enq + [""]
    open(os.path.join(RB, "presubmission_enquiry.md"), "w").write("\n".join(out))
    for j, enq, n in enquiries:
        print(j["key"], "enquiry", n, "words")
    for j, body in letters:
        print(j["key"], "letter", len(" ".join(body).split()), "words")


if __name__ == "__main__":
    main()
