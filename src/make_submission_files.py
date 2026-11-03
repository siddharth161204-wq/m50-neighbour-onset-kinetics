#!/usr/bin/env python3
"""The submission files for the Journal of The Electrochemical Society (Brief 21, M7), from the compiled manuscript.

Writes to manuscript/submission/:
  Satte_JES_manuscript.pdf                the manuscript as compiled (manuscript/main.pdf), figures placed where cited;
  Satte_JES_manuscript.tex                the LaTeX source as one file: the tables and the formatted references (main.bbl)
                                          written in, the figures referenced as figureN.pdf (the vector files in figures/);
  Satte_JES_supplementary_material.pdf    the supplement as compiled (manuscript/supplement.pdf);
  Highlights.docx                         the highlights (manuscript/highlights.txt) as the Word file the journal asks for.
The single .tex is then compiled in a scratch folder with only itself and the figure PDFs, and its text compared with
the manuscript PDF's (pdftotext): the two must agree word for word, apart from the PDF's metadata.

Usage: python3 make_submission_files.py
"""
import os, re, shutil, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MS = os.path.join(HERE, "..", "manuscript")
SUB = os.path.join(MS, "submission")
NAME = "Satte_JES_manuscript"


def single_tex():
    tex = open(os.path.join(MS, "main.tex")).read()

    def inline(m):
        return open(os.path.join(MS, m.group(1))).read().rstrip("\n")
    tex = re.sub(r"\\IfFileExists\{[^}]*\}\{\\input\{([^}]*)\}\}\{\\PH\{table pending\}\}", inline, tex)
    tex = re.sub(r"\\includegraphics\[([^\]]*)\]\{figures/fig(\d+)\.pdf\}", r"\\includegraphics[\1]{figure\2.pdf}", tex)
    bbl = open(os.path.join(MS, "main.bbl")).read().rstrip("\n")
    tex = tex.replace("\\bibliographystyle{elsarticle-num}\n\\bibliography{references}", bbl)
    tex = tex.replace("% Manuscript of the study in this repository",
                      "% Single-file source for submission, written by src/make_submission_files.py from manuscript/main.tex.\n"
                      "% Manuscript of the study in this repository", 1)
    assert "\\input{" not in tex and "\\bibliography{" not in tex and "figures/fig" not in tex
    return tex


def text_of(pdf):
    t = subprocess.run(["pdftotext", pdf, "-"], capture_output=True, text=True, check=True).stdout
    return re.sub(r"\s+", " ", t).strip()


def main():
    os.makedirs(SUB, exist_ok=True)
    tex = single_tex()
    open(os.path.join(SUB, NAME + ".tex"), "w").write(tex)
    shutil.copyfile(os.path.join(MS, "main.pdf"), os.path.join(SUB, NAME + ".pdf"))
    shutil.copyfile(os.path.join(MS, "supplement.pdf"), os.path.join(SUB, "Satte_JES_supplementary_material.pdf"))
    hl = [l.strip() for l in open(os.path.join(MS, "highlights.txt")) if l.strip()]
    assert 3 <= len(hl) <= 5 and all(len(h) <= 85 for h in hl), [len(h) for h in hl]
    with tempfile.TemporaryDirectory() as td:
        md = os.path.join(td, "Highlights.md")
        open(md, "w").write("# Highlights\n\n" + "\n".join(f"- {h}" for h in hl) + "\n")
        subprocess.run(["pandoc", md, "-o", os.path.join(SUB, "Highlights.docx")], check=True)
        # the single file builds alone, with the figure files, to the same text as the manuscript PDF
        shutil.copyfile(os.path.join(SUB, NAME + ".tex"), os.path.join(td, NAME + ".tex"))
        for n in range(1, 9):
            shutil.copyfile(os.path.join(SUB, "figures", f"figure{n}.pdf"), os.path.join(td, f"figure{n}.pdf"))
        for _ in range(3):
            r = subprocess.run(["pdflatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=td, capture_output=True,
                               text=True)
        a, b = text_of(os.path.join(td, NAME + ".pdf")), text_of(os.path.join(MS, "main.pdf"))
        same = a == b
        print("single .tex builds alone:", os.path.exists(os.path.join(td, NAME + ".pdf")), "; text identical to main.pdf:",
              same)
        if not same:
            import difflib
            for d in list(difflib.unified_diff(a.split(" "), b.split(" "), lineterm="", n=3))[:40]:
                print(d)
    print("wrote", sorted(os.listdir(SUB)))


if __name__ == "__main__":
    main()
