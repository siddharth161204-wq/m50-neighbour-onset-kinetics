#!/usr/bin/env python3
"""Word count of the manuscript's main text (Brief 20, M1): from the Introduction to the end of the Conclusions,
excluding the abstract, the figures and tables (their environments and captions), the declarations and the references.
Inline mathematics counts as one word per formula; citations, references and labels count as nothing.
Prints the count per section and the total, and writes manuscript/word_count.txt.

Usage: python3 word_count.py
"""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))


def words(tex):
    s = re.sub(r"(?<!\\)%.*", "", tex)
    s = re.sub(r"\\begin\{(figure|table)\*?\}.*?\\end\{\1\*?\}", " ", s, flags=re.S)
    s = re.sub(r"\\IfFileExists\{[^}]*\}\{\\input\{[^}]*\}\}\{[^}]*\{[^}]*\}\}", " ", s)
    s = re.sub(r"\\IfFileExists\{[^}]*\}\{[^}]*\}\{[^}]*\}", " ", s)
    s = re.sub(r"\\(cite|ref|label|input|eqref)\*?(\[[^\]]*\])?\{[^}]*\}", " ", s)
    s = re.sub(r"\$[^$]*\$", " MATH ", s)
    s = re.sub(r"\\(sub)*section\*?\{([^}]*)\}", r" \2 ", s)
    s = re.sub(r"\\[a-zA-Z]+\*?", " ", s)
    s = re.sub(r"[{}~\\]", " ", s)
    return [w for w in s.split() if re.search(r"[A-Za-z0-9]", w)]


def main():
    tex = open(os.path.join(HERE, "main.tex")).read()
    body = tex[tex.index(r"\section{Introduction}"):tex.index(r"\section*{Acknowledgments}")]
    parts = re.split(r"(?=\\section\{)", body)
    out, total = [], 0
    for p in parts:
        if not p.strip():
            continue
        name = re.match(r"\\section\{([^}]*)\}", p).group(1)
        n = len(words(p))
        total += n
        out.append(f"{name}: {n}")
    abstract = tex[tex.index(r"\begin{abstract}"):tex.index(r"\end{abstract}")]
    out.append(f"Main text (Introduction to Conclusions, without figures, tables and declarations): {total}")
    out.append(f"Abstract: {len(words(abstract.replace(chr(92) + 'begin{abstract}', '')))}")
    nfig = len(re.findall(r"\\begin\{figure\}", tex))
    ntab = len(re.findall(r"\\IfFileExists\{tables/t", tex))
    out.append(f"Figures: {nfig}; tables: {ntab}")
    open(os.path.join(HERE, "word_count.txt"), "w").write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
