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
            ("Propagation models of modules choose what share of a failing cell's vented heat reaches its neighbour, "
             "a share the published tests do not measure, and treat each cell as one temperature or as a resolved "
             "field. The manuscript asks how much of that heat must reach a neighbour for it to follow, and whether "
             "published tests can say, for two touching LG M50 cells, with kinetics fitted to calorimetry of NCM811 "
             "and of graphite with electrolyte (the M50's negative electrode adds silicon), against "
             "sixteen published two-cell tests."),
            "",
            ("In the model, with the failing cell's energy held to calorimetry, conduction and radiation leave the "
             "neighbour at least 29 K short of runaway. With each trigger fitted to its test's measured peak, the "
             "model's neighbour needs, to run away when the tests propagated after strong triggers (31.6 to 54.3 kJ), "
             "4.1 to 8.1 kJ through its side facing the failing cell if resolved, by a two-dimensional reduced model, "
             "and 0.2 to 6.0 kJ if lumped: "
             "5.3 to 10.6 % and 0.3 to 7.8 % of the median 76.74 kJ that calorimetry measured in this cell's ejecta."),
            "",
            ("That estimate depends on the neighbour's treatment. With a 21.4 s "
             "pulse the least delivered heat that runs the resolved neighbour away is 1.36 to 2.27 times the lumped "
             "neighbour's in two strong-trigger tests searched in three dimensions and 0.80 to 0.91 times in one with a "
             "weak trigger, so in these tests a share calibrated with one treatment would need a correction, whose sign "
             "went with the trigger, to serve the other. Propagation models treat the cell one way or the other; "
             "here the two share every input. The reduced model reproduced the outcome of all 151 earlier "
             "three-dimensional runs, most of them far from a threshold, at a fraction of their cost."),
            "",
            ("Published inputs cap no path of the ejecta's heat to the facing side below 27.9 kJ within 21.4 s, "
             "more than either treatment needs, so the sixteen tests cannot remove that dependence; a heat flux "
             "measured where the neighbour faces the failing cell, to well within the 1.7 to 4.3 kJ by which the two "
             "treatments' needs differ, could, if the model is otherwise right and the resolved needs are computed in "
             "three dimensions."),
            "",
            j["fit"],
            "",
            ("The code, inputs and run records are archived openly, with the study's 98 predictions, each committed "
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
             "temperature or as a resolved field, in a direction that went with the failing cell in the tests "
             "searched, and names the measurement that could remove that dependence. "
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
    out = ["# Cover letters (drafts, not sent; 23 November 2026)", "",
           "One letter per journal; they differ only in the editor addressed, the sentence on the journal's scope and, "
           "for the Journal of Power Sources, whose guide asks that the letter carry no funding information or author "
           "declarations, the end of the sentence about the author. Word files of each are in `letters/`.", ""]
    for j, body in letters:
        words = len(" ".join(body).split())
        out += [f"## {j['name']} ({j['editor']}; {words} words)", ""] + body + [""]
    open(os.path.join(RB, "cover_letter.md"), "w").write("\n".join(out))
    out = ["# Pre-submission enquiries (drafts, not sent; 23 November 2026)", "",
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
