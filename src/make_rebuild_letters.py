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
         fit=("It falls within the journal's priority areas of safety and of multiscale simulation set against "
              "experiments: it couples a cell's decomposition kinetics to its heat transfer and compares the result "
              "with measured propagation tests."),
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
    sign = ["Yours sincerely,", "", "Siddharth Satte", "Independent researcher, Pune, Maharashtra, India",
            "siddharth161204@gmail.com"]
    letters, enquiries = [], []
    os.makedirs(os.path.join(RB, "letters"), exist_ok=True)
    for j in JOURNALS:
        body = [
            f"Dear {j['to']},",
            "",
            f"I submit the manuscript \"{title}\" for consideration as a research article in the {j['name']}.",
            "",
            ("Models of thermal runaway propagation in lithium-ion modules treat each cell either as one temperature "
             "or as a resolved temperature field, and where they include the heat of the failing cell's vented ejecta "
             "they choose what share of it reaches the neighbour. The manuscript asks how much delivered heat a "
             "neighbour needs under each treatment, for two touching LG M50 cells with published decomposition "
             "kinetics, and sets both against sixteen published two-cell tests."),
            "",
            ("It finds that the choice matters, and in a direction that depends on the trigger. With each test's "
             "trigger fitted to its measured peak, the resolved neighbour needs 1.5 and 1.7 times the heat of the "
             "lumped neighbour in the two tests with strong triggers (fitted body energies of 31.6 to 54.3 kJ) where "
             "both thresholds are bracketed, and 0.85 times in the one with a weak trigger. A share of the ejected "
             "energy calibrated on such tests with one treatment therefore cannot be carried to the other without a "
             "correction whose sign depends on the trigger. Each threshold has a "
             "mechanism that a reduced model captures: for pulses up to 120 s, conduction into the surface layer sets "
             "the resolved cell's hot spot, and an energy balance to an ignition temperature of 218.5 °C sets the "
             "lumped cell's runaway. The published uncertainty of the kinetics moves that temperature by 6.1 K, while "
             "matching the two thresholds in one test would need reaction rates of a cell over 17.5 K hotter. At the "
             "central contact a reactive cross-section of the cell reproduced the runaway outcome of all 151 "
             "three-dimensional runs it was checked against, at a fraction of their cost, which makes a resolved "
             "neighbour affordable in a module model."),
            "",
            ("In the model, with the failing cell's energy limited to its calorimetry value, conduction and radiation "
             "leave the neighbour at least 29 K short of runaway, so the rest of the heat must come from the ejecta or "
             "other paths. Published inputs cannot bound any path through the neighbour's facing half below 27.9 kJ "
             "within 21.4 s, above what either treatment needs at the measured times, so the sixteen tests cannot "
             "decide between the treatments; the paper names the measurement that would, the heat flux on the "
             "neighbour's facing side."),
            "",
            j["fit"],
            "",
            ("The code, inputs and run records are openly archived, and the study's 98 predictions were committed "
             "before the runs they concern."),
            "",
            (author + (", with no funding and no competing interests." if j["declarations"] else ".")
             + " The manuscript has not been published and is not under consideration elsewhere."),
            "",
        ] + sign
        letters.append((j, body))
        enq = [
            f"Dear {j['to']},",
            "",
            (f"Would the manuscript below be within the scope of the {j['name']}? It asks how much heat must reach a "
             "neighbouring lithium-ion cell for thermal runaway to propagate, with the cell modelled as one "
             "temperature or as a resolved field; it finds that the two differ in a direction set by the trigger, "
             "explains each with a reduced model and names the measurement that would decide. "
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
    out = ["# Cover letters (drafts, not sent; 20 November 2026)", "",
           "One letter per journal; they differ only in the editor addressed, the sentence on the journal's scope and, "
           "for the Journal of Power Sources, whose guide asks that the letter carry no funding information or author "
           "declarations, the end of the sentence about the author. Word files of each are in `letters/`.", ""]
    for j, body in letters:
        words = len(" ".join(body).split())
        out += [f"## {j['name']} ({j['editor']}; {words} words)", ""] + body + [""]
    open(os.path.join(RB, "cover_letter.md"), "w").write("\n".join(out))
    out = ["# Pre-submission enquiries (drafts, not sent; 20 November 2026)", "",
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
