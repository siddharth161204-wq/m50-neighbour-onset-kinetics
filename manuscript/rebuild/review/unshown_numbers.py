"""Numbers in the running text of the main text or the supplement that no table, figure or caption shows.

Usage: python3 manuscript/rebuild/review/unshown_numbers.py main|supplement [--strict] > out.md
A number shown elsewhere with more decimals counts as shown unless --strict is given.
Uses the numbers check's own text functions; 'shown' means the number as written appears in a table (main or
supplement, inline or input), in a figure's or table's caption, or in a figure's own text (pdftotext).
"""
import glob
import os
import re
import subprocess
import sys

ROOT = "/home/claude/m50-neighbour-onset-kinetics"
RB = os.path.join(ROOT, "manuscript", "rebuild")
sys.path.insert(0, os.path.join(ROOT, "manuscript"))
import numbers_check as NC  # noqa: E402


def raw_key(raw):
    r = raw.replace("$", "").replace("−", "-").replace(",", "")
    r = re.sub(r"\s*\\times\s*10\^\{?(-?\d+)\}?", r"e\1", r)
    return r.lstrip("-")


def numbers_in(text):
    t = NC.rb_norm(NC.rb_strip(text))
    return t, NC.rb_numbers(t)


VALS = []


def shown_set():
    keys = set()
    texts = []
    for f in glob.glob(os.path.join(RB, "tables", "*.tex")):
        texts.append(open(f).read())
    for name in ("main.tex", "supplement.tex"):
        tex = open(os.path.join(RB, name)).read()
        for env in ("figure", "table", "longtable"):
            texts += re.findall(r"\\begin\{%s\*?\}.*?\\end\{%s\*?\}" % (env, env), tex, flags=re.S)
        texts += re.findall(r"\\caption\{.*?\}\\label", tex, flags=re.S)
    for f in sorted(glob.glob(os.path.join(RB, "figures", "fig*.pdf"))):
        texts.append(subprocess.check_output(["pdftotext", "-layout", f, "-"], text=True))
    for t in texts:
        tt = NC.rb_norm(NC.rb_strip(t)) if "\\" in t else t
        for v, tol, raw, a, b in NC.rb_numbers(tt):
            keys.add(raw_key(raw))
            VALS.append((abs(v), tol))
        # figure text may use a minus sign or thin spaces
        for m in re.finditer(r"\d+(?:\.\d+)?", t):
            keys.add(m.group(0))
    return keys


def body(which):
    tex = open(os.path.join(RB, "main.tex" if which == "main" else "supplement.tex")).read()
    if which == "main":
        i = tex.index(r"\begin{abstract}")
        j = tex.index(r"\section*{CRediT")
    else:
        i = tex.index(r"\begin{document}")
        j = tex.index(r"\bibliography") if r"\bibliography" in tex else len(tex)
    s = tex[i:j]
    for env in ("figure", "table", "longtable"):
        s = re.sub(r"\\begin\{%s\*?\}.*?\\end\{%s\*?\}" % (env, env), " ", s, flags=re.S)
    s = re.sub(r"\\IfFileExists\{[^}]*\}\{\\input\{[^}]*\}\}\{[^}]*\}", " ", s)
    s = re.sub(r"\\input\{[^}]*\}", " ", s)
    return s


def main(which):
    keys = shown_set()
    t, nums = numbers_in(body(which))
    out = []
    for v, tol, raw, a, b in nums:
        before, after = t[max(0, a - 60):a], t[b:b + 40]
        if NC.rb_structural(raw, before, after, t[max(0, a - 80):b + 80]):
            continue
        k = raw_key(raw)
        if k in keys:
            continue
        near = [x for x, xt in VALS if xt < tol and abs(x - abs(v)) <= tol * 1.0001 and abs(x) > 0]
        if near and "--strict" not in sys.argv:
            continue
        if re.match(r"^\d$", k):          # single digits are mostly counts and labels
            continue
        out.append((raw, t[max(0, a - 110):b + 60].replace("\n", " ")))
    print("# %s: %d numbers not shown in any table, caption or figure\n" % (which, len(out)))
    for raw, ctx in out:
        print("- **%s**: %s" % (raw, ctx))


if __name__ == "__main__":
    main(sys.argv[1])
