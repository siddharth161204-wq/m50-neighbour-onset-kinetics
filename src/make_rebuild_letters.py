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


W = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten",
     11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen", 15: "fifteen", 16: "sixteen"}

# The manuscript of the same author under consideration at the Journal of Energy Storage (Brief 32), on another question
EST_OTHER = ("EST-D-26-19130", "the error of assuming uniform heat generation in the thermal model of a cell")


def jes_letter(j, title, H, n_pred, author, sign, C):
    """The letter for the Journal of Energy Storage (Brief 32): under one page; the question, what was done, what was
    found with its numbers and why the journal's readers would use it; no claim that the manuscript's abstract for that
    journal does not make, and no limitation restated. C holds the counts written in words, each read from the files."""
    return [
        f"Dear {j['to']},",
        "",
        f"I submit the manuscript \"{title}\" for consideration as a research article in the {j['name']}.",
        "",
        ("Propagation models must assume how much heat a failing cell gives its neighbour and whether each cell is one "
         "temperature (lumped) or a temperature field (resolved). The manuscript asks how much heat must reach a "
         "neighbour for it to follow, and whether published tests can say."),
        "",
        (f"{W[C['tests']].capitalize()} published tests of two touching LG M50 cells are modelled with decomposition "
         "kinetics of NCM811 and graphite, each failing cell's energy fitted to its measured peak temperature: 31.6 to "
         f"54.3 kJ in {W[C['strong']]} tests (strong triggers) and 9.0 and 16.6 kJ in {W[C['weak']]} (weak). With the "
         "neighbour either lumped or resolved in three dimensions, its need, the least heat that, delivered to its side "
         "facing "
         "the failing cell, runs it away by the test's measured time, is searched."),
        "",
        ("With the failing cell's energy fitted or held to 33.2 kJ, the most that calorimetry gives for this cell, "
         "conduction and radiation run no resolved neighbour away. With heat delivered over 21.4 s, the mean rise time "
         f"derived from two published records, the {W[C['needs']]} tests that propagated after strong triggers need "
         f"{H['n3'][0]:.2f} to {H['n3'][1]:.2f} kJ if the neighbour is resolved, {W[C['at_thr']]} of them its "
         f"threshold, the least heat that runs it away at all, and {H['nl'][0]:.2f} to {H['nl'][1]:.2f} kJ if it is "
         f"lumped. At nominal inputs, the resolved threshold is at least {H['rs'][0]:.2f} times the lumped one after the "
         f"{W[H['ns']]} strong triggers searched in three dimensions and at most {H['rw'][1]:.2f} times after both weak "
         "ones. Published inputs rule out no path delivering 27.9 kJ to the facing side within 21.4 s."),
        "",
        ("For readers who model propagation in modules, a neighbour's share of vented heat calibrated in a lumped model "
         "may therefore need correcting for a resolved neighbour, in a direction that goes with the failing cell's "
         "energy, and a heat flux measured on the neighbour's facing side could test the needs. The work falls within "
         "the journal's topics of modelling and of the safety of energy storage systems."),
        "",
        (f"A separate manuscript of mine on a different question, {EST_OTHER[1]} ({EST_OTHER[0]}), is under "
         "consideration at the journal and shares no results or text with this one."),
        "",
        (author + ", with no funding and no competing interests. The manuscript has not been published and is not "
         "under consideration elsewhere."),
        "",
    ] + sign


def counts():
    """The counts the letter for the Journal of Energy Storage writes in words, from the files the numbers check reads."""
    import csv
    import json
    root = os.path.join(HERE, "..")
    with open(os.path.join(root, "inputs", "fransson2024", "m50_tests.csv")) as fh:
        tests = list(csv.DictReader(fh))
    with open(os.path.join(root, "results", "stage7_triggers.csv")) as fh:
        trig = [float(r["E_J"]) for r in csv.DictReader(fh) if r["kind"] == "test"]
    n16 = json.load(open(os.path.join(root, "results", "stage16_scorecard.json")))["N"]
    return {"tests": len(tests), "strong": sum(1 for e in trig if e > 30000), "weak": sum(1 for e in trig if e < 30000),
            "needs": len(n16), "at_thr": sum(1 for r in n16 if r["at_threshold"])}


def main():
    import math
    import sys
    sys.path.insert(0, HERE)
    import rebuild_headline as HL
    sys.path.insert(0, RB)
    import number_sources as NS
    # step 16's needs and thresholds in three dimensions, as the abstract gives them (src/rebuild_headline.py): the
    # needs' range across the brackets, the shares rounded as usual, the ratio's least value after strong triggers and
    # its largest after weak ones, both rounded outward
    H = {"n3": HL.range_3d_kJ(2), "nl": HL.range_lumped_kJ(2), "sh": HL.shares_pct_round(),
         "rs": HL.strong_bounded_range(), "rw": HL.weak_range(),
         "ns": sum(1 for x in HL.thresholds_3d() if x[0] not in ("M50_ST_Exp3", "M50_PT_Exp1"))}
    words = {4: "four", 3: "three", 5: "five", 6: "six"}
    import csv
    with open(os.path.join(RB, "data", "predictions_registry.csv")) as fh:
        n_pred = sum(1 for _ in csv.DictReader(fh))
    tex = open(os.path.join(RB, "main.tex")).read()
    title = re.search(r"\\title\{(.*?)\}\n", tex, re.S).group(1)
    # two abstracts since Brief 32: the Journal of Power Sources' (200 words) and the Journal of Energy Storage's (250)
    abstract = plain(tex[tex.index("%ABSTRACT-START") + len("%ABSTRACT-START"):tex.index("%ABSTRACT-END")])
    abstract_jes = plain(tex[tex.index("%JES-ABSTRACT-START") + len("%JES-ABSTRACT-START"):
                             tex.index("%JES-ABSTRACT-END")])
    author = "I am a mechanical engineer (B.Tech 2026, COEP Technological University, Pune), working independently"
    sign = ["Yours sincerely,", "", "Siddharth Satte", "Independent researcher, Pune, India",
            "siddharth161204@gmail.com"]
    letters, enquiries = [], []
    os.makedirs(os.path.join(RB, "letters"), exist_ok=True)
    C = counts()
    for j in JOURNALS:
        if j["key"] == "J_Energy_Storage":       # Brief 32: its own letter, with the journal's own abstract
            body = jes_letter(j, title, H, n_pred, author, sign, C)
        else:
            body = generic_letter(j, title, H, n_pred, author, sign, words)
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
        enquiries.append((j, enq + ["", f"Title: {title}", "",
                                    f"Abstract: {abstract_jes if j['key'] == 'J_Energy_Storage' else abstract}"], n))
        txt = os.path.join(RB, "letters", f"Cover_letter_{j['key']}.txt")
        text = "\n".join(body) + "\n"
        if not (os.path.exists(txt) and open(txt).read() == text):   # the Word file is remade only when the text changes
            md = txt.replace(".txt", ".md")
            lines = list(body)
            if j["key"] == "J_Energy_Storage":    # Brief 32: the signature's lines kept apart in the Word file
                k = len(lines) - len(sign)          # pandoc's hard line break is a backslash at the end of a line
                lines = lines[:k] + sign[:2] + [x + "\\" for x in sign[2:-1]] + sign[-1:]
            open(md, "w").write("\n".join(lines) + "\n")
            subprocess.run(["pandoc", md, "-o", txt.replace(".txt", ".docx")], check=True)
            os.remove(md)
            open(txt, "w").write(text)
        open(os.path.join(RB, "letters", f"Enquiry_{j['key']}.txt"), "w").write(
            "\n".join(enquiries[-1][1]) + "\n")
    finish(letters, enquiries)


def generic_letter(j, title, H, n_pred, author, sign, words):
    """The letter of Brief 29 to 31, kept for the Journal of Power Sources and the Fire Safety Journal."""
    return [
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
            ("Each failing cell's energy is fitted to its own measured peak temperature, 31.6 to 54.3 kJ in fourteen "
             "tests (strong triggers), mostly above the 33.2 kJ that calorimetry measured at most for this cell, and "
             "9.0 and 16.6 kJ in two (weak), and the neighbour is solved both as one "
             "temperature and as a three-dimensional field; in each, the heat it needs through its side facing the "
             "failing cell to run away by the test's measured time is searched, and the bounds that published inputs "
             "set on each path that could deliver it are worked out."),
            "",
            ("At either energy, conduction and radiation run no resolved neighbour away, so further heat must reach it. "
             "With heat delivered over 21.4 s, the mean rise time derived from the two published records, the "
             "eight tests that propagated after strong triggers need, by their measured times, "
             f"{H['n3'][0]:.2f} to {H['n3'][1]:.2f} kJ if the neighbour is resolved in three dimensions, two of them "
             "its threshold, and "
             f"{H['nl'][0]:.2f} to {H['nl'][1]:.2f} kJ if it is lumped. To run away at all, the resolved neighbour "
             f"needs at least {H['rs'][0]:.2f} times the lumped neighbour's energy after the {words[H['ns']]} strong "
             f"triggers searched in three dimensions and at most {H['rw'][1]:.2f} times after both weak ones, at nominal "
             "inputs, so in "
             "these tests a heat share calibrated with one representation may need a correction that depends on the "
             "trigger before it can serve the other. Published inputs rule out no path delivering 27.9 kJ to the facing side within "
             "21.4 s."),
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


def finish(letters, enquiries):
    out = ["# Cover letters (drafts, not sent; 25 November 2026)", "",
           "One letter per journal. The Journal of Power Sources' and the Fire Safety Journal's are those of Brief 31 and "
           "differ only in the editor addressed, the sentence on the journal's scope and, for the Journal of Power "
           "Sources, whose guide asks that the letter carry no funding information or author declarations, the end of "
           "the sentence about the author. The Journal of Energy Storage's is Brief 32's, written to that journal's "
           "abstract of 250 words and under one page. Word files of each are in `letters/`.", ""]
    for j, body in letters:
        words = len(" ".join(body).split())
        out += [f"## {j['name']} ({j['editor']}; {words} words)", ""] + body + [""]
    open(os.path.join(RB, "cover_letter.md"), "w").write("\n".join(out))
    out = ["# Pre-submission enquiries (drafts, not sent; 25 November 2026)", "",
           "One per journal: one question, whether the manuscript is within scope, and one sentence on why it belongs; "
           "the text before the title and abstract is at most 150 words. None of the three journals' guides or "
           "editorial-board pages gives an address for enquiries (journal_rules_20261120.md, section 7); the "
           "enquiry goes out from the main chat on the author's word. Since Brief 32 the Journal of Energy Storage's "
           "carries that journal's abstract of 250 words, the other two the abstract of 200.", ""]
    for j, enq, n in enquiries:
        out += [f"## {j['name']} (to {j['editor']}; {n} words before the title and abstract)", ""] + enq + [""]
    open(os.path.join(RB, "presubmission_enquiry.md"), "w").write("\n".join(out))
    for j, enq, n in enquiries:
        print(j["key"], "enquiry", n, "words")
    for j, body in letters:
        print(j["key"], "letter", len(" ".join(body).split()), "words")


if __name__ == "__main__":
    main()
