#!/usr/bin/env python3
"""The Word copy of the manuscript for the author's pass (Brief 21, M5): manuscript/main_for_author.docx, made by
pandoc from manuscript/main.tex as compiled, with the figures in place and every number as in the PDF.

Pandoc does not run BibTeX or resolve LaTeX's cross-references, so the source is first rewritten from the compiled
files: each \\cite becomes its number from main.aux, compressed as natbib compresses it ([1-4]); each \\ref its number;
each table input its table; each figure its PNG (from the submission TIFFs); the references the formatted list of
main.bbl; the red placeholders bracketed text. An instruction for the pass heads the document. The numbers in the Word
copy's text are then compared with the PDF's (pdftotext), and the comparison is written beside the copy
(manuscript/main_for_author_numbers.txt).

Usage: python3 make_author_docx.py
"""
import collections, os, re, subprocess, tempfile
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
MS = os.path.join(HERE, "..", "manuscript")
FIGS = os.path.join(MS, "submission", "figures")
OUT = os.path.join(MS, "main_for_author.docx")
INSTRUCTION = (
    r"\textbf{For the author's pass.} This Word copy is made from the LaTeX source of the manuscript as it stands for the "
    r"Journal of The Electrochemical Society; every number in it is as in the PDF. Please revise freely in Track Changes: "
    r"wording, order, emphasis, cuts, additions and comments. Do not change a number, in the text, the tables or the "
    r"captions; if a number looks wrong, leave a comment on it instead. After the pass the chat applies the changes to the "
    r"LaTeX source, re-checks every number against the results files, rebuilds the PDF and records the pass in the "
    r"decisions log; a number changed here is reverted and reported. The journal allows text drafted with a generative AI "
    r"tool only when the authors critically review and substantially revise it, and the declaration in the Methods and the "
    r"Acknowledgments will say that the author revised the text, and validated every finding and interpretation, only "
    r"after this pass. Text in square brackets marked PLACEHOLDER is filled at submission or after the pass.")


def aux_maps():
    aux = open(os.path.join(MS, "main.aux")).read()
    cites = {k: int(n) for k, n in re.findall(r"\\bibcite\{([^}]+)\}\{\{(\d+)\}", aux)}
    labels = {k: n for k, n in re.findall(r"\\newlabel\{([^}]+)\}\{\{([^}]*)\}", aux)}
    return cites, labels


def compress(nums):
    nums = sorted(set(nums))
    out, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        out.append(f"{nums[i]}--{nums[j]}" if j - i >= 2 else ", ".join(str(x) for x in nums[i:j + 1]))
        i = j + 1
    return ", ".join(out)


def strip_comments(s):
    return "\n".join(re.sub(r"(?<!\\)%.*$", "", line) for line in s.split("\n"))


def braced(s, i):
    """The text of the brace group starting at s[i] == '{', and the index after it."""
    assert s[i] == "{", s[i:i + 30]
    depth, j = 0, i
    while True:
        if s[j] == "{" and s[j - 1] != "\\":
            depth += 1
        elif s[j] == "}" and s[j - 1] != "\\":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1


def replace_command(s, name, fn, nargs=1):
    out, i = [], 0
    pat = re.compile(r"\\" + name + r"(?![A-Za-z])")
    while True:
        m = pat.search(s, i)
        if not m:
            out.append(s[i:])
            return "".join(out)
        out.append(s[i:m.start()])
        j = m.end()
        opt = None
        if j < len(s) and s[j] == "[":
            k = s.index("]", j)
            opt, j = s[j + 1:k], k + 1
        args = []
        for _ in range(nargs):
            while s[j] in " \n\t":
                j += 1
            a, j = braced(s, j)
            args.append(a)
        out.append(fn(opt, *args))
        i = j


def bibliography():
    bbl = strip_comments(open(os.path.join(MS, "main.bbl")).read())
    items = re.split(r"\\bibitem\{[^}]+\}", bbl)[1:]
    out = []
    for n, it in enumerate(items, 1):
        it = it.replace(r"\end{thebibliography}", "")
        it = replace_command(it, "href", lambda o, url, txt: txt, nargs=2)
        it = replace_command(it, "path", lambda o, x: x)
        it = replace_command(it, "url", lambda o, x: x)
        it = it.replace(r"\newblock", " ")
        it = re.sub(r"\s+", " ", it).strip()
        out.append(f"[{n}] {it}\n")
    return r"\section*{References}" + "\n\n" + "\n\n".join(out)


def figure_png(n, tmp):
    src = os.path.join(FIGS, f"figure{n}.tif")
    im = Image.open(src).convert("RGB")
    w = 1600
    im = im.resize((w, round(im.size[1] * w / im.size[0])), Image.LANCZOS)
    p = os.path.join(tmp, f"figure{n}.png")
    im.save(p, dpi=(190, 190))
    return p


# ------------------------------------------------------------------------------------------------ inline mathematics
MATH_MACROS = {r"\fs": ("f", "^", "*"), r"\ft": ("f", "_", "t"), r"\fmax": ("f", "_", "max"), r"\Eb": ("E", "_", "b"),
               r"\Ee": ("E", "_", "e")}
GREEK = {r"\rho": "ρ", r"\theta": "θ", r"\delta": "δ", r"\times": "×", r"\pm": "±",
         r"\cos": "cos\u2009"}


def _group(x, j):
    """The argument at x[j]: a brace group's text, a control word, or one character; and the index after it."""
    if x[j] == "{":
        depth, k = 0, j
        while True:
            if x[k] == "{":
                depth += 1
            elif x[k] == "}":
                depth -= 1
                if depth == 0:
                    return x[j + 1:k], k + 1
            k += 1
    if x[j] == "\\":
        k = j + 1
        while k < len(x) and x[k].isalpha():
            k += 1
        return x[j:k], k
    return x[j], j + 1


def _math_text(x, roman=False):
    res, j, prev = [], 0, False
    while j < len(x):
        c = x[j]
        if x.startswith(r"\mathrm", j):
            g, j = _group(x, j + len(r"\mathrm"))
            res.append(_math_text(g, True))
            prev = True
            continue
        if c == "\\":
            if x.startswith(r"\,", j):
                res.append(" ")
                j += 2
                continue
            k = j + 1
            while k < len(x) and x[k].isalpha():
                k += 1
            name = x[j:k]
            if name in MATH_MACROS:
                base, kind, sub = MATH_MACROS[name]
                res.append(r"\textit{" + base + "}" + (r"\textsuperscript{" if kind == "^" else r"\textsubscript{")
                           + sub + "}")
                prev = True
            elif name in GREEK:
                g = GREEK[name]
                binary = name in (r"\times", r"\pm")
                res.append(f" {g} " if binary and prev else g)
                prev = not binary
            else:
                raise ValueError(name)
            j = k
            continue
        if c in "_^":
            g, j = _group(x, j + 1)
            if g == r"\mathrm":
                g, j = _group(x, j)
                inner = _math_text(g, True)
            else:
                inner = _math_text(g, roman)
            res.append((r"\textsubscript{" if c == "_" else r"\textsuperscript{") + inner + "}")
            prev = True
            continue
        if c.isalpha():
            res.append(c if roman else r"\textit{" + c + "}")
            prev = True
        elif c.isdigit() or c == ".":
            res.append(c)
            prev = True
        elif c in "=+":
            res.append(f" {c} ")
            prev = False
        elif c == "-":
            res.append(" − " if prev else "−")
            prev = False
        elif c == ",":
            res.append(", ")
            prev = False
        elif c in "()[]/*":
            res.append(c)
            prev = c in ")]*"
        elif c == " ":
            pass
        else:
            raise ValueError(c)
        j += 1
    return "".join(res)


def math_to_text(m):
    """A simple inline formula as text with italic variables, sub- and superscripts (Word runs a reader can edit in
    Track Changes), or None if it holds anything else."""
    try:
        return _math_text(m)
    except (ValueError, IndexError, RecursionError):
        return None


def simplify_math(s):
    def rep(mm):
        t = math_to_text(mm.group(1))
        return mm.group(0) if t is None else t
    return re.sub(r"(?<!\\)\$([^$]+)\$", rep, s)


def preprocess(tmp):
    tex = open(os.path.join(MS, "main.tex")).read()
    pre = tex[:tex.index(r"\begin{document}")]
    macros = "\n".join(l for l in pre.split("\n") if l.startswith(r"\newcommand"))
    macros = re.sub(r"\\newcommand\{\\PH\}\[1\]\{[^\n]*", "", macros)
    title = braced(tex, tex.index(r"\title{") + len(r"\title"))[0]
    abstract = tex[tex.index("%ABSTRACT-START") + len("%ABSTRACT-START"):tex.index("%ABSTRACT-END")].strip()
    body = tex[tex.index("%BODY-START") + len("%BODY-START"):tex.index("%BODY-END")]
    body = strip_comments(body)
    # tables: inline the files
    def inline(m):
        return open(os.path.join(MS, m.group(1))).read()
    body = re.sub(r"\\IfFileExists\{[^}]*\}\{\\input\{([^}]*)\}\}\{\\PH\{table pending\}\}", inline, body)
    body = re.sub(r"\\IfFileExists\{[^}]*\}\{\\input\{([^}]*)\}\}\{\}", inline, body)
    cites, labels = aux_maps()
    # number the captions as the PDF does (pandoc does not)
    def number_captions(m):
        env, inner = m.group(1), m.group(2)
        lab = re.search(r"\\label\{([^}]+)\}", inner)
        if lab and r"\caption{" in inner:
            word = "Table" if env == "table" else "Figure"
            inner = inner.replace(r"\caption{", r"\caption{" + f"{word} {labels[lab.group(1)]}. ", 1)
        return r"\begin{" + env + "}" + inner + r"\end{" + env + "}"
    body = re.sub(r"\\begin\{(table|figure)\}(.*?)\\end\{\1\}", number_captions, body, flags=re.S)

    # a table environment with several tabulars would repeat its caption once per tabular in pandoc's output: the caption
    # becomes a paragraph above the tabulars, and the environment is dropped
    def unwrap_table(m):
        inner = m.group(1)
        i = inner.index(r"\caption{") + len(r"\caption")
        cap, j = braced(inner, i)
        inner = inner[:i - len(r"\caption")] + inner[j:]
        word, rest = cap.split(". ", 1)
        for x in (r"\centering", r"\footnotesize", r"\scriptsize", r"\par\bigskip", r"[!tbp]", r"[p]", r"[t]"):
            inner = inner.replace(x, "")
        inner = re.sub(r"\\setlength\{\\tabcolsep\}\{[^}]*\}", "", inner)
        return "\n\n" + r"\noindent\textbf{" + word + ".} " + rest + "\n\n" + inner + "\n\n"
    body = re.sub(r"\\begin\{table\}(.*?)\\end\{table\}", unwrap_table, body, flags=re.S)

    def cite(opt, keys):
        nums = [cites[k.strip()] for k in keys.split(",")]
        s = compress(nums)
        return f"[{s}, {opt}]" if opt else f"[{s}]"
    body = replace_command(body, "cite", cite)
    abstract = replace_command(abstract, "cite", cite)
    body = replace_command(body, "ref", lambda o, k: labels[k])
    body = replace_command(body, "label", lambda o, k: "")
    body = replace_command(body, "PH", lambda o, x: r"\textbf{[PLACEHOLDER: " + x + "]}")
    figs = {}

    def graphic(opt, path):
        n = int(re.search(r"fig(\d+)", path).group(1))
        figs[n] = figure_png(n, tmp)
        return r"\includegraphics[width=6.3in]{" + figs[n] + "}"
    body = replace_command(body, "includegraphics", graphic)
    body = body.replace("[!tbp]", "").replace("[p]", "").replace("[t]", "").replace("[!t]", "").replace("[h]", "")
    head = (r"\documentclass{article}" + "\n" + r"\usepackage{amsmath}\usepackage{graphicx}\usepackage{booktabs}"
            + "\n" + macros + "\n" + r"\title{" + title + "}\n" + r"\author{Siddharth Satte\textsuperscript{z}}" + "\n"
            + r"\date{}" + "\n" + r"\begin{document}" + "\n" + r"\maketitle" + "\n\n" + INSTRUCTION + "\n\n"
            + r"Independent researcher, Pune, India. \textsuperscript{z}E-mail: \textbf{[PLACEHOLDER: the author's e-mail, "
            + r"added at submission]}" + "\n\n" + r"\section*{Abstract}" + "\n\n" + abstract + "\n\n")
    doc = head + simplify_math(body) + "\n\n" + bibliography() + "\n\n" + r"\end{document}" + "\n"
    doc = doc.replace(r"\section*{Abstract}" + "\n\n" + abstract, r"\section*{Abstract}" + "\n\n" + simplify_math(abstract))
    # symbols pandoc's LaTeX reader drops: the degree sign
    doc = doc.replace(r"\newcommand{\degC}{\,\textdegree C}", r"\newcommand{\degC}{\,\textdegree{}C}")
    doc = doc.replace(r"\textdegree{}", "\u00b0").replace("\\textdegree ", "\u00b0").replace(r"\textdegree", "\u00b0")
    p = os.path.join(tmp, "main_for_pandoc.tex")
    open(p, "w").write(doc)
    return p, figs


NUM = re.compile(r"(?<![\w.])-?\d[\d,]*(?:\.\d+)?")


def numbers(text):
    text = text.replace("\u2212", "-").replace("\u2013", " ").replace("\u2014", " ")
    text = re.sub(r"(?<=[A-Za-z)^(])\s*-\s*[12](?![\d.])", " ", text)    # unit exponents (K-1, m-2), not data
    text = re.sub(r"zenodo\.\s*\d+\s*\d*", " ", text)                     # DOIs broken over lines in the PDF
    return collections.Counter(m.group(0).replace(",", "") for m in NUM.finditer(text))


def pdf_text_without_figures(tmp):
    """The PDF's text with the figures' own lettering left out: main.tex compiled again with graphicx in draft mode
    (each figure a frame), its references from the compiled main.aux and main.bbl."""
    d = os.path.join(tmp, "draft")
    os.makedirs(d)
    tex = open(os.path.join(MS, "main.tex")).read()
    open(os.path.join(d, "main.tex"), "w").write(r"\PassOptionsToPackage{draft}{graphicx}" + "\n" + tex)
    for f in ("main.bbl",):
        open(os.path.join(d, f), "w").write(open(os.path.join(MS, f)).read())
    for sub in ("tables", "figures"):
        os.symlink(os.path.join(MS, sub), os.path.join(d, sub))
    for _ in range(2):
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "main.tex"], cwd=d, capture_output=True)
    return subprocess.run(["pdftotext", "-layout", os.path.join(d, "main.pdf"), "-"], capture_output=True, text=True,
                          check=True).stdout


def compare(docx, tmp):
    plain = subprocess.run(["pandoc", docx, "-t", "plain", "--wrap=none"], capture_output=True, text=True,
                           check=True).stdout
    plain = plain[plain.index("Abstract"):]
    plain = re.sub(r"\u2212\s+", "-", plain)
    pdf = pdf_text_without_figures(tmp)
    pdf = pdf[pdf.index("Abstract"):]
    pdf = re.sub(r"\n\s*\d+\s*\n", "\n", pdf)               # page numbers
    pdf = re.sub(r"Preprint submitted to Journal of The Electrochemical Society\s+\w+ \d+, \d{4}", "", pdf)
    a, b = numbers(plain), numbers(pdf)
    only_docx = {k: v - b.get(k, 0) for k, v in a.items() if v > b.get(k, 0)}
    only_pdf = {k: v - a.get(k, 0) for k, v in b.items() if v > a.get(k, 0)}
    return a, b, only_docx, only_pdf


def main():
    with tempfile.TemporaryDirectory() as tmp:
        src, figs = preprocess(tmp)
        subprocess.run(["pandoc", src, "-f", "latex", "-t", "docx", "-o", OUT, "--resource-path", tmp], check=True)
        a, b, only_docx, only_pdf = compare(OUT, tmp)
    rep = [f"Word copy: {sum(a.values())} numbers; PDF (from the abstract on, page numbers removed): {sum(b.values())}.",
           f"In the Word copy more often than in the PDF ({sum(only_docx.values())}): "
           + ", ".join(f"{k} (+{v})" for k, v in sorted(only_docx.items(), key=lambda kv: kv[0])),
           f"In the PDF more often than in the Word copy ({sum(only_pdf.values())}): "
           + ", ".join(f"{k} (+{v})" for k, v in sorted(only_pdf.items(), key=lambda kv: kv[0]))]
    open(os.path.join(MS, "main_for_author_numbers.txt"), "w").write("\n".join(rep) + "\n")
    print("\n".join(rep))
    print("wrote", OUT, "with figures", sorted(figs))


if __name__ == "__main__":
    main()
