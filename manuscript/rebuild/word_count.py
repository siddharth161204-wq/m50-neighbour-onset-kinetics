#!/usr/bin/env python3
"""Word count of the rebuilt manuscript (Brief 29): the main text from the Introduction to the end of the
Conclusions, excluding the abstract, the figures and tables (their environments and captions), the appendices, the
declarations and the references, as the Journal of Power Sources counts it; the appendices separately; the abstract;
the highlights' characters; and the counts of figures and tables. Inline mathematics counts as one word per formula,
a display equation as nothing; citations, references and labels count as nothing.

Writes manuscript/rebuild/word_count.txt.  Usage: python3 manuscript/rebuild/word_count.py
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))


def words(tex):
    s = re.sub(r"(?<!\\)%.*", "", tex)
    s = re.sub(r"\\begin\{(figure|table|equation)\*?\}.*?\\end\{\1\*?\}", " ", s, flags=re.S)
    s = re.sub(r"\\IfFileExists\{[^}]*\}\{\\input\{[^}]*\}\}\{[^}]*\}", " ", s)
    s = re.sub(r"\\(cite|ref|label|input|eqref)\*?(\[[^\]]*\])?\{[^}]*\}", " ", s)
    s = re.sub(r"\$[^$]*\$", " MATH ", s)
    s = re.sub(r"\\(sub)*section\*?\{([^}]*)\}", r" \2 ", s)
    s = re.sub(r"\\[a-zA-Z]+\*?", " ", s)
    s = re.sub(r"[{}~\\]", " ", s)
    return [w for w in s.split() if re.search(r"[A-Za-z0-9]", w)]


def main():
    tex = open(os.path.join(HERE, "main.tex")).read()
    body = tex[tex.index(r"\section{Introduction}"):tex.index(r"\appendix")]
    apps = tex[tex.index(r"\appendix"):tex.index(r"\section*{CRediT")]
    parts = re.split(r"(?=\\section\{)", body)
    out, total = [], 0
    for p in parts:
        if not p.strip():
            continue
        name = re.match(r"\\section\{([^}]*)\}", p).group(1)
        n = len(words(p))
        total += n
        out.append(f"{name}: {n}")
    abstract = tex[tex.index(r"\begin{abstract}") + len(r"\begin{abstract}"):tex.index(r"\end{abstract}")]
    out.append(f"Main text (Introduction to Conclusions, without figures, tables, appendices and declarations): {total}")
    out.append(f"Appendices: {len(words(apps))}; main text and appendices: {total + len(words(apps))}")
    out.append(f"Abstract: {len(words(abstract))} words")
    nfig = len(re.findall(r"\\begin\{figure\}", tex))
    ntab = len(re.findall(r"\\IfFileExists\{tables/t", tex))
    out.append(f"Figures: {nfig}; tables: {ntab}; together: {nfig + ntab}")
    hl = os.path.join(HERE, "highlights.txt")
    if os.path.exists(hl):
        for line in open(hl).read().splitlines():
            if line.strip():
                out.append(f"Highlight ({len(line.strip())} characters): {line.strip()}")
    open(os.path.join(HERE, "word_count.txt"), "w").write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
