#!/usr/bin/env python3
"""Word (.docx) and PDF files of the rebuilt manuscript and its supplement, for submission (Brief 29).

The LaTeX sources are the master: main.tex and supplement.tex, compiled by pdflatex, give main.pdf and supplement.pdf.
This script makes the Word files from the same sources with pandoc, after resolving what pandoc does not: the numbers
of sections, figures, tables and equations are read from the .aux files of the LaTeX build (so run pdflatex first),
captions get their "Fig. n." and "Table n." prefixes, the tables are put inline, the figures are the 300 dpi PNGs, and
references are formatted by the Elsevier numeric style (build/elsevier-with-titles.csl, from the Citation Style
Language project, CC BY-SA 3.0). Equations stay editable Word equations.

Writes, in manuscript/rebuild/submission/:
  Manuscript.docx, Manuscript.pdf (the LaTeX PDF), Supplementary_material.docx, Supplementary_material.pdf,
  Highlights.docx, Keywords.txt, Figure_1.pdf ... Figure_7.pdf (vector) and Figure_1.tif ... (1,000 dpi), Graphical_abstract.tif and .pdf,
  the three cover letters (Cover_letter_<journal>.docx and .txt) and the three enquiries (Enquiry_<journal>.txt),
  Manuscript_double_spaced.docx and .pdf (the same text double-spaced at 12 points, to count pages against the Fire
  Safety Journal's preference), and build_report.txt (page counts).

Brief 32: the set for the Journal of Energy Storage is built into submission/J_Energy_Storage/ by --journal jes, with that
journal's abstract of 250 words (main_jes.tex), its own letter, and the LaTeX sources in source/; the set for the Journal
of Power Sources in submission/ itself is left as it is unless --journal jps is given.

Usage: python3 manuscript/rebuild/build_word.py --journal jes   (or --journal jps)
"""
import os
import re
import shutil
import subprocess

from docx import Document
from docx.enum.text import WD_LINE_SPACING
from docx.shared import Pt, Cm

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "submission")
JOURNAL = "jps"         # set by main(): "jps" writes submission/, "jes" writes submission/J_Energy_Storage/
BUILD = os.path.join(HERE, "build")
CSL = os.path.join(BUILD, "elsevier-with-titles.csl")


def labels(aux):
    out = {}
    for m in re.finditer(r"\\newlabel\{([^}]*)\}\{\{([^}]*)\}", open(aux).read()):
        out[m.group(1)] = m.group(2).replace("Appendix ~", "").replace("Appendix~", "").strip()
    return out


def inline_tables(s):
    def rep(m):
        p = os.path.join(HERE, m.group(1))
        return open(p).read() if os.path.exists(p) else ""
    return re.sub(r"\\IfFileExists\{[^}]*\}\{\\input\{([^}]*)\}\}\{[^}]*\}", rep, s)


def resolve(s, lab, prefix_fig="Fig.", prefix_tab="Table"):
    # captions: "Fig. n." / "Table n." before the caption text of each float, from its label
    def float_rep(m):
        env, body = m.group(1), m.group(2)
        lm = re.search(r"\\label\{([^}]*)\}", body)
        if lm and lm.group(1) in lab:
            n = lab[lm.group(1)]
            pre = (prefix_fig if env == "figure" else prefix_tab) + f" {n}. "
            body = body.replace("\\caption{", "\\caption{" + pre, 1)
        return f"\\begin{{{env}}}" + body + f"\\end{{{env}}}"
    s = re.sub(r"\\begin\{(figure|table|longtable)\}(.*?)\\end\{\1\}", float_rep, s, flags=re.S)
    # equation numbers into the display, then display math without the numbering environment
    def eq_rep(m):
        body = m.group(1)
        lm = re.search(r"\\label\{([^}]*)\}", body)
        n = lab.get(lm.group(1), "") if lm else ""
        body = re.sub(r"\\label\{[^}]*\}", "", body)
        body = body.replace("\\begin{split}", "\\begin{aligned}").replace("\\end{split}", "\\end{aligned}")
        return "\n\\[" + body.strip() + (f"\\qquad\\qquad ({n})" if n else "") + "\\]\n"
    s = re.sub(r"\\begin\{equation\}(.*?)\\end\{equation\}", eq_rep, s, flags=re.S)
    s = re.sub(r"\\eqref\{([^}]*)\}", lambda m: f"({lab.get(m.group(1), '?')})", s)
    s = re.sub(r"\\ref\{([^}]*)\}", lambda m: lab.get(m.group(1), "?"), s)
    s = re.sub(r"(\\includegraphics(?:\[[^\]]*\])?\{figures/fig\d)\.pdf\}", r"\1.png}", s)
    return s


def appendix_titles(s):
    i = s.find("\\appendix")
    if i < 0:
        return s
    head, tail = s[:i], s[i + len("\\appendix"):]
    letters = iter("ABCDEFGH")
    def rep(m):
        return f"\\section*{{Appendix {next(letters)}. {m.group(1)}}}"
    j = tail.find("\\section*{")
    apps, rest = (tail[:j], tail[j:]) if j >= 0 else (tail, "")
    apps = re.sub(r"\\section\{([^}]*)\}", rep, apps)
    return head + apps + rest


PREAMBLE = r"""\documentclass{article}
\newcommand{\degC}{\,°C}
\newcommand{\sep}{; }
\begin{document}
"""


def pandoc(tex, docx, title, extra_meta=(), numbered=False):
    tex = tex.replace("\\textdegree{}", "°").replace("\\textdegree", "°")
    src = os.path.join(BUILD, os.path.basename(docx).replace(".docx", ".pandoc.tex"))
    open(src, "w").write(tex)
    cmd = ["pandoc", src, "-f", "latex", "-o", docx, "--citeproc", "--bibliography", os.path.join(HERE, "references.bib"),
           "--csl", CSL, "--resource-path", HERE, "-M", f"title={title}", "-M", "link-citations=false"]
    for m in extra_meta:
        cmd += ["-M", m]
    if numbered:
        cmd.append("--number-sections")
    subprocess.run(cmd, check=True, cwd=HERE)


def style_docx(path, double=False):
    d = Document(path)
    for sec in d.sections:
        sec.top_margin = sec.bottom_margin = Cm(2.5)
        sec.left_margin = sec.right_margin = Cm(2.5)
    for st in d.styles:
        try:
            if st.font is not None:
                st.font.name = "Times New Roman"
        except Exception:
            pass
    for name in ("Normal", "Body Text", "First Paragraph", "Compact", "Bibliography", "Abstract", "Table Caption",
                 "Image Caption", "Author", "Date"):
        try:
            st = d.styles[name]
            st.font.size = Pt(12 if name not in ("Table Caption", "Image Caption", "Compact") else 11)
            pf = st.paragraph_format
            if double:
                pf.line_spacing_rule = WD_LINE_SPACING.DOUBLE
            else:
                pf.line_spacing = 1.15
        except KeyError:
            pass
    fit_tables(d)
    if double:
        for p in d.paragraphs:
            p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
        for t in d.tables:
            for row in t.rows:
                for c in row.cells:
                    for p in c.paragraphs:
                        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    d.save(path)


def fit_tables(d, text_width_cm=16.0):
    """Column widths in proportion to what each column holds (pandoc's own widths squeeze the text columns)."""
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    for t in d.tables:
        ncol = len(t.columns)
        lens = [0.0] * ncol
        for row in t.rows:
            for j, c in enumerate(row.cells[:ncol]):
                words = c.text.split()
                longest = max((len(w) for w in words), default=1)
                lens[j] = max(lens[j], min(len(c.text), 60) ** 0.5 * 1.0, longest * 0.32)
        tot = sum(lens) or 1.0
        widths = [max(1.3, text_width_cm * x / tot) for x in lens]
        scale = text_width_cm / sum(widths)
        widths = [w * scale for w in widths]
        t.autofit = False
        tblPr = t._tbl.tblPr
        lay = tblPr.find(qn("w:tblLayout"))
        if lay is None:
            lay = OxmlElement("w:tblLayout")
            tblPr.append(lay)
        lay.set(qn("w:type"), "fixed")
        tw = tblPr.find(qn("w:tblW"))
        if tw is None:
            tw = OxmlElement("w:tblW")
            tblPr.append(tw)
        tw.set(qn("w:type"), "dxa")
        tw.set(qn("w:w"), str(int(text_width_cm / 2.54 * 1440)))
        grid = t._tbl.find(qn("w:tblGrid"))
        if grid is not None:
            for gc, w in zip(grid.findall(qn("w:gridCol")), widths):
                gc.set(qn("w:w"), str(int(w / 2.54 * 1440)))
        for row in t.rows:
            for j, c in enumerate(row.cells[:ncol]):
                c.width = Cm(widths[j])


def to_pdf(docx):
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", os.path.dirname(docx), docx],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    pdf = docx[:-5] + ".pdf"
    n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout).group(1))
    return pdf, n


def manuscript():
    tex = open(os.path.join(HERE, "main.tex")).read()
    lab = labels(os.path.join(HERE, "main_jes.aux" if JOURNAL == "jes" else "main.aux"))
    title = re.search(r"\\title\{(.*?)\}\n", tex, re.S).group(1)
    author = re.search(r"\\author\{(.*?)\}", tex).group(1)
    email = re.search(r"\\ead\{(.*?)\}", tex).group(1)
    address = re.search(r"\\address\{(.*?)\}", tex).group(1)
    a, b = ("%JES-ABSTRACT-START", "%JES-ABSTRACT-END") if JOURNAL == "jes" else ("%ABSTRACT-START", "%ABSTRACT-END")
    abstract = tex[tex.index(a) + len(a):tex.index(b)].strip()
    keywords = re.search(r"\\begin\{keyword\}(.*?)\\end\{keyword\}", tex, re.S).group(1).strip().replace("\\sep", ";")
    body = tex[tex.index("%BODY-START") + len("%BODY-START"):tex.index("%BODY-END")]
    body = appendix_titles(resolve(inline_tables(body), lab))
    front = (f"{author}\n\n{address}\n\nCorresponding author: {author}, {email}\n\n"
             f"\\section*{{Abstract}}\n{abstract}\n\n\\noindent Keywords: {keywords}\n\n")
    doc = PREAMBLE + front + body + "\n\\section*{References}\n\\end{document}\n"
    out = os.path.join(OUT, "Manuscript.docx")
    pandoc(doc, out, title, ["reference-section-title="], numbered=True)
    style_docx(out)
    dbl = os.path.join(OUT, "Manuscript_double_spaced.docx")
    shutil.copy(out, dbl)
    style_docx(dbl, double=True)
    return title, keywords


def supplement(title_main):
    tex = open(os.path.join(HERE, "supplement.tex")).read()
    lab = labels(os.path.join(HERE, "supplement.aux"))
    title = re.search(r"\\title\{(.*?)\}\n", tex, re.S).group(1)
    author = re.search(r"\\author\{(.*?)\}", tex).group(1)
    address = re.search(r"\\address\{(.*?)\}", tex).group(1)
    body = tex[tex.index("\\end{frontmatter}") + len("\\end{frontmatter}"):tex.index("\\bibliographystyle")]
    body = resolve(inline_tables(body), lab, prefix_fig="Fig.", prefix_tab="Table")
    # sections as S1, S2, ... (the supplement's own numbering), unnumbered in Word with the number in the title
    n = iter(range(1, 50))
    body = re.sub(r"\\section\{([^}]*)\}", lambda m: f"\\section*{{S{next(n)}. {m.group(1)}}}", body)
    doc = PREAMBLE + f"{author}\n\n{address}\n\n" + body + "\n\\section*{References}\n\\end{document}\n"
    out = os.path.join(OUT, "Supplementary_material.docx")
    pandoc(doc, out, title, ["reference-section-title="])
    style_docx(out)


def latex_sources(src):
    """The LaTeX sources of the set for the Journal of Energy Storage (Brief 32), each compiling alone: Manuscript.tex is
    main.tex with that journal's abstract in place of the switch between the two, with its bibliography (.bbl, from the
    build of main_jes.tex) beside the .bib; Supplementary_material.tex is supplement.tex; the tables and figures they
    read are copied beside them."""
    os.makedirs(os.path.join(src, "tables"), exist_ok=True)
    os.makedirs(os.path.join(src, "figures"), exist_ok=True)
    tex = open(os.path.join(HERE, "main.tex")).read()
    i, j = tex.index("\\ifdefined\\JESabstract"), tex.index("\\fi\n\\end{abstract}")
    jes = tex[tex.index("%JES-ABSTRACT-START"):tex.index("%JES-ABSTRACT-END") + len("%JES-ABSTRACT-END")]
    head = tex[:tex.index("% Two abstracts (Brief 32)")]
    tex = head + jes + "\n" + tex[j + len("\\fi\n"):]
    # the working comments (the build's own notes and markers) are left out of the files sent; none is inline
    nocomment = lambda t: "\n".join(x for x in t.splitlines() if not x.lstrip().startswith("%")) + "\n"
    open(os.path.join(src, "Manuscript.tex"), "w").write(nocomment(tex))
    shutil.copy(os.path.join(HERE, "main_jes.bbl"), os.path.join(src, "Manuscript.bbl"))
    open(os.path.join(src, "Supplementary_material.tex"), "w").write(
        nocomment(open(os.path.join(HERE, "supplement.tex")).read()))
    shutil.copy(os.path.join(HERE, "supplement.bbl"), os.path.join(src, "Supplementary_material.bbl"))
    shutil.copy(os.path.join(HERE, "references.bib"), os.path.join(src, "references.bib"))
    import glob as _glob
    for f in _glob.glob(os.path.join(HERE, "tables", "*.tex")):
        shutil.copy(f, os.path.join(src, "tables", os.path.basename(f)))
    for i in range(1, 8):
        shutil.copy(os.path.join(HERE, "figures", f"fig{i}.pdf"), os.path.join(src, "figures", f"fig{i}.pdf"))


def main():
    global OUT, JOURNAL
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--journal", choices=["jps", "jes"], required=True,
                    help="jes: the Journal of Energy Storage's set in submission/J_Energy_Storage/ (Brief 32); "
                         "jps: the Journal of Power Sources' set in submission/, which Brief 32 leaves as it is")
    JOURNAL = ap.parse_args().journal
    if JOURNAL == "jes":
        OUT = os.path.join(HERE, "submission", "J_Energy_Storage")
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(BUILD, exist_ok=True)
    if not os.path.exists(CSL):
        raise SystemExit(f"missing {CSL}")
    title, keywords = manuscript()
    supplement(title)
    hl = [x for x in open(os.path.join(HERE, "highlights.txt")).read().splitlines() if x.strip()]
    md = os.path.join(BUILD, "Highlights.md")
    open(md, "w").write("Highlights\n\n" + "\n".join(f"- {h}" for h in hl) + "\n")
    subprocess.run(["pandoc", md, "-o", os.path.join(OUT, "Highlights.docx")], check=True)
    open(os.path.join(OUT, "Keywords.txt"), "w").write("\n".join(k.strip() for k in keywords.split(";")) + "\n")
    for i in range(1, 8):
        shutil.copy(os.path.join(HERE, "figures", f"Figure_{i}.tif"), os.path.join(OUT, f"Figure_{i}.tif"))
        shutil.copy(os.path.join(HERE, "figures", f"fig{i}.pdf"), os.path.join(OUT, f"Figure_{i}.pdf"))
    for ext in ("tif", "pdf"):
        shutil.copy(os.path.join(HERE, "figures", f"graphical_abstract.{ext}"), os.path.join(OUT, f"Graphical_abstract.{ext}"))
    rep = []
    names = ("Manuscript.docx", "Supplementary_material.docx") if JOURNAL == "jes" else \
        ("Manuscript.docx", "Manuscript_double_spaced.docx", "Supplementary_material.docx")
    if JOURNAL == "jes":     # the double-spaced copy was for the Fire Safety Journal's page count only
        dbl = os.path.join(OUT, "Manuscript_double_spaced.docx")
        if os.path.exists(dbl):
            os.remove(dbl)
    for name in names:
        pdf, n = to_pdf(os.path.join(OUT, name))
        if name != "Manuscript_double_spaced.docx":
            os.remove(pdf)      # LibreOffice does not draw Word equations; the PDFs are the LaTeX ones
        rep.append(f"{name}: {n} pages as LibreOffice lays it out (A4, 2.5 cm margins, Times New Roman 12 pt; "
                   "LibreOffice leaves the Word equations out of its PDF, so the count is low by their lines)")
    import glob as _glob
    if JOURNAL == "jes":     # the journal's own letter only (Brief 32), and the LaTeX sources
        for ext in ("docx", "txt"):
            shutil.copy(os.path.join(HERE, "letters", f"Cover_letter_J_Energy_Storage.{ext}"),
                        os.path.join(OUT, f"Cover_letter_J_Energy_Storage.{ext}"))
        pdf, n = to_pdf(os.path.join(OUT, "Cover_letter_J_Energy_Storage.docx"))
        os.remove(pdf)
        rep.append(f"Cover_letter_J_Energy_Storage.docx: {n} page as LibreOffice lays it out")
        latex_sources(os.path.join(OUT, "source"))
        shutil.copy(os.path.join(HERE, "main_jes.pdf"), os.path.join(OUT, "Manuscript.pdf"))
    else:
        # the three cover letters (Word, with their text) and the three enquiries, so that the set is in one folder
        for f in sorted(_glob.glob(os.path.join(HERE, "letters", "Cover_letter_*.docx"))
                        + _glob.glob(os.path.join(HERE, "letters", "Cover_letter_*.txt"))
                        + _glob.glob(os.path.join(HERE, "letters", "Enquiry_*.txt"))):
            shutil.copy(f, os.path.join(OUT, os.path.basename(f)))
        shutil.copy(os.path.join(HERE, "main.pdf"), os.path.join(OUT, "Manuscript.pdf"))
    shutil.copy(os.path.join(HERE, "supplement.pdf"), os.path.join(OUT, "Supplementary_material.pdf"))
    n_tex = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", os.path.join(OUT, "Manuscript.pdf")],
                                                            capture_output=True, text=True).stdout).group(1))
    rep.append(f"Manuscript.pdf (LaTeX, elsarticle preprint, 12 pt): {n_tex} pages")
    open(os.path.join(OUT, "build_report.txt"), "w").write("\n".join(rep) + "\n")
    print("\n".join(rep))


if __name__ == "__main__":
    main()
