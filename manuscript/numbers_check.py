#!/usr/bin/env python3
"""Every number in the manuscript traced to a numbers file or a results file (Brief 20, M7).

Reads manuscript/main.tex with the tables it inputs (and, with --supplement, manuscript/supplement.tex), strips what
is not text (comments, citations, labels, references, URLs, file names), extracts every number with the precision it
is written to, and looks for it among the numeric values of the results files (every number in results/*.json and
results/*.csv, the inputs of the tests, the predictions files, and results/manuscript_numbers.json, which holds the
model's constants read from the code and the counts read from the records). A number matches a value when the value,
rounded to the number's written precision, equals it, directly or after one of the unit changes the texts use (J to
kJ, a fraction to a percentage, K to C), and in magnitude when the text states a sign in words.

Numbers that are structure, not data, are listed apart and not looked for: stage, section, figure, table, equation and
prediction numbers, criterion and test labels, decision numbers, years in references, the cell format (21700) and the
chemistry's name (NCM811). Everything else that matches nothing is listed as NOT FOUND, for a person to trace or
correct. Writes manuscript/numbers_check.log.

Usage: python3 numbers_check.py [--supplement]
"""
import argparse, csv, glob, json, math, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
RES = os.path.join(ROOT, "results")


# ------------------------------------------------------------------------------------------------ the reference values
def json_numbers(obj, out, path=""):
    if isinstance(obj, bool):
        return
    if isinstance(obj, (int, float)):
        if not (isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj))):
            out.append((float(obj), path))
        return
    if isinstance(obj, str):
        for m in re.finditer(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", obj):
            try:
                out.append((float(m.group(0)), path + "~str"))
            except ValueError:
                pass
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            json_numbers(v, out, f"{path}.{k}" if path else str(k))
            for m in re.finditer(r"-?\d+(?:\.\d+)?", str(k)):
                out.append((float(m.group(0)), f"{path}.{k}~key"))
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            json_numbers(v, out, f"{path}[{i}]")


CURATED_JSON = ["note_numbers.json", "stage3_numbers.json", "v11_sensitivity.json", "v12_numbers.json",
                "stage6_numbers.json", "stage7_paper_numbers.json", "stage8_paper_numbers.json",
                "stage9_paper_numbers.json", "stage10_paper_numbers.json", "stage11_paper_numbers.json",
                "manuscript_numbers.json", "stage11_bands.json", "stage11_scorecard.json", "stage10_v1.json", "stage2_checks.json", "explore_sei_storage.json",
                "stage12_paper_numbers.json", "stage12_scorecard.json", "stage12_checks.json"]
CURATED_CSV = ["stage7_triggers.csv", "stage8_ejected.csv", "stage8_thresholds.csv", "stage9_fractions.csv",
               "stage11_thresholds.csv", "stage11_overshoot.csv", "stage11_times.csv", "stage11_draws.csv",
               "stage12_capped.csv", "stage12_fixed_ejecta.csv"]


def reference_values(loose=False):
    """(value, file) pairs. By default only the curated numbers files, the files the texts are written from, and the
    per-test tables; with loose=True every results file (which makes chance matches likely and is for diagnosis)."""
    vals = []
    jfiles = sorted(glob.glob(os.path.join(RES, "*.json"))) if loose else [os.path.join(RES, f) for f in CURATED_JSON]
    jfiles.append(os.path.join(ROOT, "inputs", "fransson2024", "fig10_extraction.json"))
    for f in jfiles:
        if not os.path.exists(f):
            continue
        try:
            json_numbers(json.load(open(f)), vals, os.path.relpath(f, ROOT))
        except Exception:
            pass
    cfiles = (sorted(glob.glob(os.path.join(RES, "*.csv"))) if loose else [os.path.join(RES, f) for f in CURATED_CSV]) \
        + [os.path.join(ROOT, "inputs", "fransson2024", "m50_tests.csv")] \
        + sorted(glob.glob(os.path.join(ROOT, "manuscript", "data", "*.csv")))
    for f in cfiles:
        if not os.path.exists(f):
            continue
        rel = os.path.relpath(f, ROOT)
        with open(f) as fh:
            for i, row in enumerate(csv.DictReader(fh)):
                for k, v in row.items():
                    if v is None:
                        continue
                    for m in re.finditer(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", v):
                        try:
                            vals.append((float(m.group(0)), f"{rel}:{i + 2}:{k}"))
                        except ValueError:
                            pass
    return vals


# ------------------------------------------------------------------------------------------------ the manuscript's numbers
STRUCT_BEFORE = re.compile(r"(Stages?|Sections?|Fig\.|Figs\.|Figure|Table|Tables|Eq\.|Equations?|P|C|D|Exp|version|"
                           r"rank|ranks|Part|V|S|Appendix|Run)\s*~?$")


def strip_tex(s):
    s = re.sub(r"(?<!\\)%.*", "", s)
    s = re.sub(r"\\(cite|ref|label|url|input|includegraphics|bibliography|bibliographystyle|documentclass|usepackage|"
               r"newcommand|renewcommand|biboptions|journal|eqref)\*?(\[[^\]]*\])?\{[^}]*\}", " ", s)
    s = re.sub(r"\\begin\{tabular\}\{[^}]*\}", " ", s)
    s = re.sub(r"\\begin\{longtable\}\{[^}]*\}", " ", s)
    s = re.sub(r"p\{0\.\d+\\textwidth\}", " ", s)
    s = re.sub(r"\[(t|h|p|ht|htb)\]", " ", s)
    s = re.sub(r"\\(?:textwidth|linewidth)", " ", s)
    s = s.replace("{,}", ",")
    return s


def tex_numbers(text):
    """(value, decimals, raw, context) for every number in the text; '2\\times10^{-11}' is one number."""
    out = []
    pat = re.compile(r"(?<![\w.])(-|\$-|−)?(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?(?:\s*\\times\s*10\^\{?(-?\d+)\}?)?")
    for m in pat.finditer(text):
        sign, ip, fp, ex = m.group(1), m.group(2), m.group(3), m.group(4)
        raw = m.group(0)
        num = ip.replace(",", "") + (fp or "")
        dec = len(fp) - 1 if fp else 0
        v = float(num)
        if sign and sign.strip("$") in ("-", "−"):
            v = -v
        if ex is not None:
            v = v * 10 ** int(ex)
            dec = None                     # scientific: compare to two significant figures
        ctx = text[max(0, m.start() - 40):m.end() + 25].replace("\n", " ")
        before = text[max(0, m.start() - 12):m.start()]
        after = text[m.end():m.end() + 16]
        out.append((v, dec, raw, ctx, before, after))
    return out


def structural(v, raw, before, ctx):
    b = before.rstrip()
    if STRUCT_BEFORE.search(before.replace("~", " ").rstrip()):
        return "label"
    if re.search(r"(PT|PP|ST|SP)\\?_Exp$", before):
        return "test name"
    if raw in ("21700",) or re.search(r"NCM$", before) or raw == "811":
        return "name"
    if re.match(r"^(19|20)\d\d$", raw) and ("et al" in ctx or "~\\cite" in ctx or re.search(r"\(\d{4}\)", ctx)):
        return "year"
    if re.search(r"(Stages|stages) [\d, and to]*$", before):
        return "label"
    if re.search(r"\b\d{1,3},\s*$", before) and re.search(r"(J\.|Sources|Storage|eTransportation|Soc\.|Adv\.)", ctx):
        return "reference"           # an article number after a journal's volume, in a table of the literature
    return None


def unit_after(ctx_after):
    t = ctx_after.lstrip("$ ~").replace("\\,", "").replace("~", " ").lstrip()
    if t.startswith("kJ"):
        return "kJ"
    if t.startswith("\\%") or t.startswith("%"):
        return "%"
    if t.startswith("\\degC") or t.startswith("\\textdegree") or t.startswith("°C"):
        return "C"
    return ""


def matches(v, dec, ref, unit="", limit=4):
    """Every file (up to `limit` distinct ones) holding a value that rounds to v at its written precision."""
    scales = {"kJ": (1.0, 1e-3), "%": (1.0, 100.0), "table": (1.0, 1e-3, 100.0)}.get(unit, (1.0,))
    shifts = (0.0, -273.15) if unit == "C" else (0.0,)
    hits, files = [], set()
    for x, path in ref:
        f = path.split(":")[0].split(".json")[0]
        if f in files:
            continue
        ok = False
        for sc in scales:
            for sh in shifts:
                y = x * sc + sh
                for cand in (y, -y):
                    if dec is None:
                        ok = ok or (v != 0 and abs(cand - v) <= 0.051 * abs(v))
                    else:
                        ok = ok or abs(cand - v) <= 0.5 * 10 ** (-dec) + 1e-9 * max(1.0, abs(v))
        if ok:
            files.add(f)
            hits.append(path)
            if len(hits) >= limit:
                break
    return hits


# ------------------------------------------------------------------------------------------------ the rebuilt manuscript
# Brief 29, rule 4: every number of the rebuilt manuscript (manuscript/rebuild/) traced by script to a results file.
# Each number is first matched to an entry of manuscript/rebuild/number_sources.py, which names the file and the value
# it is read from; the value, after the entry's unit change and rounded to the number's written precision, must equal
# the number. A number in the manuscript's own text with no entry is a failure (NO ENTRY), even when some value in the
# results files happens to equal it; in the tables a number may instead be found among the values of the files that
# table is made from; in the supplement a broad match among the results files is reported and accepted.
REBUILD_CURATED_JSON = ["stage13_paper_numbers.json", "stage13_scorecard.json", "stage13_checks.json",
                        "stage13_readings.json", "stage14_corrections.json", "stage14_paper_numbers.json",
                        "stage15_paper_numbers.json", "stage15_readings.json", "stage15_scorecard.json",
                        "stage15_checks.json", "stage15_cross_section.json", "stage15_accounts.json"]
REBUILD_CURATED_CSV = ["stage13_skin.csv", "stage13_tign.csv", "stage14_needs.csv", "stage14_bounds_corrected.csv",
                       "stage14_inputs.csv", "stage15_table.csv"]
TABLE_SOURCES = {
    "t1_tests.tex": ["inputs/fransson2024/m50_tests.csv", "results/stage7_triggers.csv"],
    "s1_steps.tex": ["manuscript/rebuild/data/steps.csv", "manuscript/rebuild/data/predictions_registry.csv"],
    "s2_registry.tex": ["manuscript/rebuild/data/predictions_registry.csv"],
    "s3_thresholds.tex": ["results/stage14_needs.csv", "results/stage15_cross_section.json",
                          "results/stage15_table.csv", "results/stage15_paper_numbers.json", "results/stage13_skin.csv",
                          "results/stage13_twobody.csv"],
    "s7_needs.tex": ["results/stage15_table.csv", "results/stage14_needs.csv"],
    "s9_heldout.tex": ["results/stage10_heldout.json"],
    "s10_twobody.tex": ["results/stage13_twobody.csv"],
    "s11_archived.tex": ["results/stage15_cross_section.json"],
}
MONTHS = r"(January|February|March|April|May|June|July|August|September|October|November|December)"


def rb_strip(s):
    s = re.sub(r"(?<!\\)%.*", "", s)
    s = re.sub(r"\\begin\{(equation|align|split|displaymath)\*?\}.*?\\end\{\1\*?\}", " [display] ", s, flags=re.S)
    s = re.sub(r"\\\[.*?\\\]", " [display] ", s, flags=re.S)
    s = re.sub(r"\\setlength\{[^}]*\}\{[^}]*\}", " ", s)
    s = re.sub(r"\\renewcommand\{\\arraystretch\}\{[^}]*\}", " ", s)
    s = re.sub(r"\\(h|v)space\*?\{[^}]*\}", " ", s)
    s = re.sub(r"\\\\\[[\d.]+(pt|em|ex|mm|cm)\]", " ", s)
    s = re.sub(r"\\(begin|end)\{(figure|table|longtable|tabular|enumerate|itemize|abstract|keyword|frontmatter|"
               r"document|appendices|center)\*?\}(\[[^\]]*\])?(\{[^}]*\})?", " ", s)
    s = re.sub(r"\\(ead|href|url|includegraphics|IfFileExists|biboptions|journal|bibliographystyle|bibliography|"
               r"documentclass|usepackage|newcommand|renewcommand|hypersetup)\*?(\[[^\]]*\])?\{[^}]*\}", " ", s)
    s = re.sub(r"\[(width|height|scale)=[^\]]*\]", " ", s)
    s = re.sub(r"[pmb]\{[\d.]+\\(textwidth|linewidth)\}", " ", s)
    s = re.sub(r"\\multicolumn\{\d+\}\{[^}]*\}", " ", s)
    s = re.sub(r"\\cmidrule(\([^)]*\))?\{[^}]*\}", " ", s)
    s = strip_tex(s)
    return s


def rb_norm(s):
    s = s.replace("\\,", " ").replace("~", " ").replace("\\%", "%").replace("\\degC{}", "°C").replace("\\degC", "°C")
    s = s.replace("\\textdegree{}", "°").replace("\\textdegree", "°").replace("$", "").replace("−", "-")
    s = s.replace("\\ ", " ").replace("{}", "")
    return re.sub(r"\s+", " ", s)


def rb_norm_pat(p):
    p = p.replace("\\\\,", " ").replace("\\\\%", "%").replace("~", " ").replace("\\\\degC", "°C")
    p = p.replace("\\\\textdegree", "°").replace("\\$", "")
    return re.sub(r" +", " ", p)


def rb_numbers(text):
    """(value, tolerance, raw, start, end) for every number; '5.565\\times10^{-7}' is one number."""
    out = []
    pat = re.compile(r"(?<![\w.^_\\])(-|\$-|−)?(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?(?:\s*\\times\s*10\^\{?(-?\d+)\}?)?")
    for m in pat.finditer(text):
        sign, ip, fp, ex = m.group(1), m.group(2), m.group(3), m.group(4)
        dec = len(fp) - 1 if fp else 0
        v = float(ip.replace(",", "") + (fp or ""))
        tol = 0.5 * 10 ** (-dec)
        if ex is not None:
            v, tol = v * 10 ** int(ex), tol * 10 ** int(ex)
        if sign and sign.strip("$") in ("-", "−"):
            v = -v
        out.append((v, tol, m.group(0), m.start(), m.end()))
    return out


def rb_structural(raw, before, after, ctx):
    b_raw = before.replace("~", " ")
    b = b_raw.rstrip()
    if STRUCT_BEFORE.search(b) or re.search(r"(Sections?|Figs?\.|Figures?|Tables?|Steps?|steps?|Appendix)\s+[\dA-Z.]+"
                                            r"((,\s*|\s+and\s+|\s*(to|--|–)\s*)[\dA-Z.]+)*(,\s*|\s+and\s+|\s*(to|--|–)\s*)$",
                                            b_raw):
        return "label"
    if re.search(r"(eqs?\.|Eqs?\.|equations?)\s*\(?$", b) or re.search(r"\(\d\)(,\s*|\s+and\s+|\s*(to|--|–)\s*)\($", b):
        return "label"
    if re.search(r"[\^_]\{?-?$", before) or re.search(r"[\^_]\{-?\d+/$", before):
        return "exponent or subscript"
    if raw == "0" and re.match(r"^\s*to\b", after) and re.search(r"\b(over|from)\s*$", b):
        return "start of a time window"
    if raw in ("21700", "18650") or re.search(r"(NCM|LG M|M)$", before):
        return "name"
    if re.search(r"CC\s*BY\s*$", b) or re.search(r"(doi|DOI|zenodo|Zenodo)[:./ ]*[\d./]*$", b) \
            or re.match(r"^\.\d", after) or re.search(r"10\.\d{4,5}/", ctx):
        return "identifier"
    if re.match(r"^(19|20)\d\d$", raw) and (re.search(r"et al|\\cite|\(\d{4}\)|B\.\s?Tech|" + MONTHS, ctx)):
        return "year or date"
    if re.match(r"^\d{1,2}$", raw) and re.match(r"^\s*" + MONTHS, after):
        return "year or date"
    if re.search(r"\(\s*$", b) and re.match(r"^\)", after) and re.search(r"(finding|Finding|item)\s*$", b[:-1].rstrip()):
        return "label"
    if re.match(r"^\s*-?(fold|times)\b", after) is None and re.search(r"\b(of|in|Step)\s+(Step|step)\s*$", b):
        return "label"
    if re.search(r"(PT|PP|ST|SP)(\\?_|-)Exp$", before):
        return "test name"
    return None


def rb_unit(v, unit):
    if unit in (None, "round0", "round1"):
        return v
    if unit in ("kJ", "kJround0"):
        return v / 1000.0
    if unit == "pct":
        return 100.0 * v
    if unit == "pctabs":
        return abs(100.0 * v)
    if unit == "abs":
        return abs(v)
    if unit == "C":
        return v - 273.15
    if unit == "sci":
        return v
    if unit in ("g", "milli"):                    # kg to g; ohm to milliohm
        return 1000.0 * v
    raise ValueError(f"unknown unit change {unit}")


def rb_segments(rb):
    """(name, text, mode): mode 'map' (an entry needed), 'table:<file>' or 'broad'."""
    segs = []
    tex = open(os.path.join(rb, "main.tex")).read()
    def cut(a, b):
        i = tex.index(a)
        j = tex.index(b, i) if b else len(tex)
        return tex[i:j]
    segs.append(("main.tex: title", re.search(r"\\title\{(.*?)\}\n", tex, re.S).group(1), "map"))
    segs.append(("main.tex: abstract", cut(r"\begin{abstract}", r"\end{abstract}"), "map"))
    body = cut(r"\section{Introduction}", r"\section{Conclusions}")
    segs.append(("main.tex: Introduction to Discussion, with figure captions", body, "map"))
    segs.append(("main.tex: Conclusions", cut(r"\section{Conclusions}", r"\appendix"), "map"))
    segs.append(("main.tex: appendices", cut(r"\appendix", r"\section*{CRediT"), "map"))
    segs.append(("main.tex: declarations", cut(r"\section*{CRediT", r"\bibliography"), "map"))
    for f in sorted(glob.glob(os.path.join(rb, "tables", "t*.tex"))):
        t = open(f).read()
        if os.path.basename(f) == "t1_tests.tex":
            i = t.index(r"\begin{tabular}")
            segs.append((os.path.relpath(f, ROOT) + ": caption", t[:i], "map"))
            segs.append((os.path.relpath(f, ROOT) + ": rows", t[i:], "columns:t1"))
        else:
            segs.append((os.path.relpath(f, ROOT), t, "map"))
    for name in ["highlights.txt", "keywords.txt", "titles.md", "ga_text.txt"] + sorted(
            os.path.join("letters", os.path.basename(f)) for f in glob.glob(os.path.join(rb, "letters", "*.txt"))):
        p = os.path.join(rb, name)
        if os.path.exists(p):
            t = open(p).read()
            if name == "titles.md":        # the titles only, without the list's numbering and word counts
                t = "\n".join(re.sub(r"^\d+\.\s+|\s+\(\d+ words\)$", "", x) for x in t.splitlines() if re.match(r"^\d+\. ", x))
            segs.append((os.path.relpath(p, ROOT), t, "map"))
    return segs


def check_t1(tex, lines):
    """Table 1: every cell of every row against the column it is made from, for the test the row names
    (inputs/fransson2024/m50_tests.csv for the measurements, results/stage7_triggers.csv for the body energy)."""
    tests = {r["test"]: r for r in csv.DictReader(open(os.path.join(ROOT, "inputs", "fransson2024", "m50_tests.csv")))}
    trig = {r["test"]: float(r["E_J"]) for r in csv.DictReader(open(os.path.join(RES, "stage7_triggers.csv")))
            if r["kind"] == "test"}
    body = tex[tex.index(r"\midrule"):tex.index(r"\bottomrule")]
    n_ok, bad = 0, []
    for row in body.split(r"\\"):
        row = row.replace(r"\midrule", "").strip()
        if "&" not in row:
            continue
        c = [x.strip() for x in row.split("&")]
        t = "M50_" + c[0].replace("-", "_")
        m = tests.get(t)
        if m is None:
            bad.append((c[0], row, "row names no test"))
            continue
        cat = {"cell movement": "c.m.", "": "--"}.get(m["failure_category"], m["failure_category"])
        want = [("connection", c[1], m["connection"]),
                ("trigger_max_C", c[2], m["trigger_max_C"]),
                ("E_J (kJ)", c[3], f"{trig[t] / 1000:.1f}"),
                ("propagated", c[4], m["propagated"].lower()),
                ("time_to_propagation_s", c[5], m["time_to_propagation_s"]),
                ("neighbour_max_C", c[6].replace("$^{a}$", ""), m["neighbour_max_C"]),
                ("failure_category", c[7], cat)]
        for col, got, exp in want:
            if got == exp:
                if re.search(r"\d", got):
                    n_ok += 1
                lines.append(f"   column {c[0]} {col}: {got} = {exp}")
            else:
                bad.append((got, row, f"MISMATCH in {col}: table {got!r}, source {exp!r}"))
                lines.append(f"   MISMATCH {c[0]} {col}: table {got!r}, source {exp!r}")
    return n_ok, bad


def check_cells(tex, spec_path, lines):
    """A table whose cells are conversions of file values (Table S8: fractions of a test's ejected energy E_e, in kJ):
    each cell's source, as the table's writer recorded it (file, row, column, whether it is times E_e, scale and
    decimals), is read again here from the file itself, converted and rounded, and must equal the printed cell; and the
    printed cells must appear in the table in that order."""
    spec = json.load(open(spec_path))
    ee = {r["test"]: float(r["E_e_J"]) for r in csv.DictReader(open(os.path.join(RES, "stage14_needs.csv")))}
    body = tex[tex.index(r"\midrule"):tex.index(r"\bottomrule")]
    pos, n_ok, bad = 0, 0, []
    for c in spec:
        rows = [r for r in csv.DictReader(open(os.path.join(ROOT, c["file"])))
                if all(r.get(k) == v for k, v in c["where"].items())]
        if len(rows) != 1:
            bad.append((c["text"], str(c["where"]), f"{len(rows)} rows match {c['where']} in {c['file']}"))
            continue
        v = float(rows[0][c["col"]]) * (ee[c["where"]["test"]] if c["times_E_e"] else 1.0) * c["scale"]
        want = f"{v:.{c['dec']}f}"
        k = body.find(c["text"], pos)
        if want != c["text"]:
            bad.append((c["text"], str(c["where"]), f"MISMATCH: source gives {want}"))
            lines.append(f"   MISMATCH {c['text']} <- {c['file']} {c['where']} {c['col']}: {want}")
        elif k < 0:
            bad.append((c["text"], str(c["where"]), "cell not found in the table in order"))
        else:
            pos = k + len(c["text"])
            n_ok += 1
            lines.append(f"   cell {c['text']} <- {c['file']} {c['where']} {c['col']}"
                         + (" x E_e" if c["times_E_e"] else "") + f" x {c['scale']:g}")
    return n_ok, bad


def check_s11(tex, lines):
    """Table S11, the archived runs by test: every row recomputed here, by this code's own grouping, from the rows of
    results/stage15_cross_section.json (A1_rows), and compared with the printed row."""
    rows = json.load(open(os.path.join(RES, "stage15_cross_section.json")))["A1_rows"]
    body = tex[tex.index(r"\midrule"):tex.index(r"\bottomrule")]
    printed = [ln.strip().rstrip("\\").strip() for ln in body.splitlines() if "&" in ln]
    order = [f"M50_{c}_Exp{i}" for c in ("PT", "PP", "ST", "SP") for i in range(1, 5)] + [None]
    want = []
    for t in order:
        sel = [r for r in rows if t is None or r["test"] == t]
        if not sel:
            continue
        by = {}
        for r in sel:
            key = "none" if r["shape"] == "none" else ("tri" if r["shape"] == "tri" else f"con{round(r['tau_d_s'])}")
            by[key] = by.get(key, 0) + 1
        es = sorted(r["E_J"] for r in sel if r["E_J"] > 0)
        rng = "--" if not es else (f"{es[0] / 1e3:.1f}" if len(es) == 1 else f"{es[0] / 1e3:.1f} to {es[-1] / 1e3:.1f}")
        both = len([r for r in sel if r["C8_3d"] is True and r["C8_xs"] is True])
        short = len([r for r in sel if r["t_end_s"] < 899.0])
        label = "All" if t is None else t.split("_", 1)[1].replace("_", "-")
        cells = [label, len(sel), by.get("none", 0), by.get("tri", 0), by.get("con120", 0), by.get("con240", 0),
                 by.get("con360", 0), rng, both, short]
        want.append(" & ".join(str(c) for c in cells))
    n_ok, bad = 0, []
    for k, w in enumerate(want):
        got = printed[k] if k < len(printed) else None
        if got == w:
            n_ok += 1
            lines.append(f"   row {w}")
        else:
            bad.append((str(got), w, "MISMATCH: recomputed row differs"))
            lines.append(f"   MISMATCH row: table {got!r}, recomputed {w!r}")
    if len(printed) != len(want):
        bad.append((str(len(printed)), str(len(want)), "row count differs"))
    return n_ok, bad


def rebuild(a):
    import sys
    rb = os.path.join(HERE, "rebuild")
    sys.path.insert(0, rb)
    import number_sources as NS
    entries = []
    for ctx_rx, nums, sel, unit in NS.E:
        entries.append((re.compile(rb_norm_pat(ctx_rx)), {n.replace("$", "").replace(" ", "") for n in nums}, sel, unit))
    broad = reference_values(False)
    for f in REBUILD_CURATED_JSON:
        p = os.path.join(RES, f)
        if os.path.exists(p):
            json_numbers(json.load(open(p)), broad, os.path.relpath(p, ROOT))
    for f in REBUILD_CURATED_CSV:
        p = os.path.join(RES, f)
        with open(p) as fh:
            for i, row in enumerate(csv.DictReader(fh)):
                for k, v in row.items():
                    for m in re.finditer(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", v or ""):
                        broad.append((float(m.group(0)), f"{os.path.relpath(p, ROOT)}:{i + 2}:{k}"))
    bset = {}
    for x, p in broad:
        bset.setdefault(x, p)
    broad = list(bset.items())

    def file_values(rel):
        vals, p = [], os.path.join(ROOT, rel)
        if not os.path.exists(p):
            return vals
        if p.endswith(".json"):
            json_numbers(json.load(open(p)), vals, rel)
        else:
            with open(p) as fh:
                for i, row in enumerate(csv.DictReader(fh)):
                    for k, v in row.items():
                        for m in re.finditer(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", v or ""):
                            vals.append((float(m.group(0)), f"{rel}:{i + 2}:{k}"))
        return vals

    segs = rb_segments(rb)
    if a.supplement:
        segs.append(("manuscript/rebuild/supplement.tex", open(os.path.join(rb, "supplement.tex")).read(), "broad"))
        for f in sorted(glob.glob(os.path.join(rb, "tables", "s*.tex"))):
            segs.append((os.path.relpath(f, ROOT), open(f).read(), "table:" + os.path.basename(f)))
    cache, lines, fails, counts = {}, [], [], {"traced": 0, "table": 0, "broad": 0, "structural": 0}
    trace = []
    for name, raw_text, mode in segs:
        if mode == "columns:t1":
            lines.append(f"== {name}  [each cell against its column of the test's row]")
            n_ok, bad = check_t1(raw_text, lines)
            counts["table"] += n_ok
            fails += [(name, raw, ctx, why) for raw, ctx, why in bad]
            continue
        if mode == "table:s11_archived.tex":
            lines.append(f"== {name}  [each row recomputed from the archived runs]")
            n_ok, bad = check_s11(raw_text, lines)
            counts["table"] += n_ok
            fails += [(name, raw, ctx, why) for raw, ctx, why in bad]
            raw_text = raw_text[:raw_text.index(r"\midrule")]
        if mode == "table:s8_reduced.tex":
            lines.append(f"== {name}  [each cell against the file value it is converted from]")
            n_ok, bad = check_cells(raw_text, os.path.join(rb, "tables", "s8_reduced.cells.json"), lines)
            counts["table"] += n_ok
            fails += [(name, raw, ctx, why) for raw, ctx, why in bad]
            # the caption's and the headers' numbers are checked as the other tables' are
            raw_text = raw_text[:raw_text.index(r"\midrule")]
            mode = "table:s8_reduced.tex"
        text = rb_strip(raw_text) if (name.endswith(".tex") or ".tex:" in name) else raw_text
        starts = [0] + [m.end() for m in re.finditer(r"(?<=[.?!])\s+(?=[A-Z(\\])|\n\s*\n", text)]
        lines.append(f"== {name}  [{mode}]")
        for v, tol, raw, s, e in rb_numbers(text):
            before, after = text[max(0, s - 40):s], text[e:e + 20]
            ctx = text[max(0, s - 60):e + 40].replace("\n", " ")
            st = rb_structural(raw, before, after, ctx)
            if st:
                counts["structural"] += 1
                lines.append(f"   [{st}] {raw}  ...{ctx}...")
                continue
            key = raw.replace("$", "").replace(" ", "").replace("−", "-")
            win = rb_norm(text[max(0, s - 110):e + 80])
            applicable = [en for en in entries if key in en[1] and en[0].search(win)]
            if applicable:
                tried = []
                ok_where = None
                for _, _, sel, unit in applicable:
                    try:
                        vals = cache[id(sel)] if id(sel) in cache else cache.setdefault(id(sel), sel())
                        got = [rb_unit(x, unit) for x in vals]
                    except Exception as exc:  # a selector that cannot read its file is a failure, reported
                        tried.append(f"{getattr(sel, 'where', '?')}: ERROR {type(exc).__name__}: {exc}")
                        continue
                    hit = [g for g in got if abs(g - v) <= tol * (1 + 1e-9) + 1e-12]
                    if hit:
                        ok_where = f"{getattr(sel, 'where', '?')} = {hit[0]:.6g}"
                        break
                    tried.append(f"{getattr(sel, 'where', '?')} = " + ", ".join(f"{g:.6g}" for g in got[:6]))
                if ok_where:
                    counts["traced"] += 1
                    lines.append(f"   traced {raw} <- {ok_where}")
                    k = max(i for i, st in enumerate(starts) if st <= s)
                    end = starts[k + 1] if k + 1 < len(starts) else len(text)
                    trace.append(dict(segment=name, sentence=re.sub(r"\s+", " ", text[starts[k]:end]).strip(),
                                      number=raw, source=ok_where))
                else:
                    fails.append((name, raw, ctx, "MISMATCH: " + " | ".join(tried)))
                    lines.append(f"   MISMATCH {raw}  ...{ctx}...  tried: " + " | ".join(tried))
                continue
            if mode.startswith("table:"):
                files = TABLE_SOURCES.get(mode[6:], [])
                vals = []
                for f in files:
                    vals += cache.setdefault(f, file_values(f))
                hit = matches(v, None if tol == 0 else max(0, round(-math.log10(2 * tol))), vals, "table", 2)
                if hit:
                    counts["table"] += 1
                    lines.append(f"   table {raw} <- " + " | ".join(hit))
                    continue
            if mode == "broad" or mode.startswith("table:"):
                dec = max(0, round(-math.log10(2 * tol)))
                hit = matches(v, dec, broad, unit_after(after) or ("table" if mode.startswith("table:") else ""))
                if hit:
                    counts["broad"] += 1
                    lines.append(f"   broad {raw} <- " + " | ".join(hit))
                    continue
            fails.append((name, raw, ctx, "NO ENTRY" if mode == "map" else "NOT FOUND"))
            lines.append(f"   {'NO ENTRY' if mode == 'map' else 'NOT FOUND'} {raw}  ...{ctx}...")
    # counts written in words: each phrase must be in the main text and its count must equal the files' count
    body_text = re.sub(r"\s+", " ", rb_strip(open(os.path.join(rb, "main.tex")).read()).replace("~", " "))
    lines.append("== counts written in words (main.tex)")
    n_words = 0
    for phrase, want, sel in getattr(NS, "WORDS", []):
        if not re.search(phrase, body_text):
            fails.append(("main.tex", phrase, "", "WORDED COUNT: phrase not in the text"))
            lines.append(f"   MISSING PHRASE {phrase}")
            continue
        try:
            got = sel()[0]
        except Exception as exc:
            fails.append(("main.tex", phrase, "", f"WORDED COUNT: ERROR {exc}"))
            continue
        if abs(got - want) < 1e-9:
            n_words += 1
            lines.append(f"   words ok '{phrase}' = {want} <- {sel.where}")
        else:
            fails.append(("main.tex", phrase, "", f"WORDED COUNT: text {want}, files {got}"))
            lines.append(f"   WORDED COUNT MISMATCH '{phrase}': text {want}, files {got}")
    counts["words"] = n_words
    head = [f"numbers_check --rebuild{' --supplement' if a.supplement else ''}: {counts['traced']} traced to a named "
            f"value, {counts['table']} found in their table's source files, {counts['broad']} broad matches "
            f"(supplement only), {counts['words']} counts written in words checked, {len(fails)} failures, "
            f"{counts['structural']} structural (not looked for)", ""]
    if fails:
        head.append("FAILURES:")
        head += [f"  {f}: {raw}  [{why}]  ...{ctx}..." for f, raw, ctx, why in fails]
        head.append("")
    out = os.path.join(rb, "numbers_check_supplement.log" if a.supplement else "numbers_check.log")
    open(out, "w").write("\n".join(head + lines) + "\n")
    if not a.supplement:
        json.dump(trace, open(os.path.join(rb, "numbers_trace.json"), "w"), indent=1)
    print(head[0])
    for f, raw, ctx, why in fails[:200]:
        print(f"  {f}: {raw}  [{why[:300]}]  ...{ctx[:110]}...")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--supplement", action="store_true")
    ap.add_argument("--loose", action="store_true")
    ap.add_argument("--rebuild", action="store_true", help="check manuscript/rebuild/ against its source map")
    a = ap.parse_args()
    if a.rebuild:
        return rebuild(a)
    ref = reference_values(a.loose)
    ref_set = {}
    for x, p in ref:
        ref_set.setdefault(x, p)
    ref = list(ref_set.items())
    srcs = [os.path.join(HERE, "main.tex")]
    for f in sorted(glob.glob(os.path.join(HERE, "tables", "t*.tex"))):
        srcs.append(f)
    if a.supplement:
        srcs.append(os.path.join(HERE, "supplement.tex"))
    lines, n_found, n_struct, missing = [], 0, 0, []
    for src in srcs:
        text = strip_tex(open(src).read())
        lines.append(f"== {os.path.relpath(src, ROOT)}")
        for v, dec, raw, ctx, before, after in tex_numbers(text):
            st = structural(v, raw, before, ctx)
            if st:
                n_struct += 1
                lines.append(f"   [{st}] {raw}  ...{ctx}...")
                continue
            unit = unit_after(after) or ("table" if "/tables/" in src else "")
            hit = matches(v, dec, ref, unit)
            if hit:
                n_found += 1
                lines.append(f"   ok {raw} <- " + " | ".join(hit) + ("" if len(hit) == 1 else "  [several files]"))
            else:
                missing.append((os.path.relpath(src, ROOT), raw, ctx))
                lines.append(f"   NOT FOUND {raw}  ...{ctx}...")
    head = [f"numbers_check: {n_found} found, {len(missing)} not found, {n_struct} structural (not looked for); "
            f"{len(ref)} reference values from the results, inputs and predictions files", ""]
    if missing:
        head.append("NOT FOUND:")
        head += [f"  {f}: {raw}  ...{ctx}..." for f, raw, ctx in missing]
        head.append("")
    open(os.path.join(HERE, "numbers_check.log"), "w").write("\n".join(head + lines) + "\n")
    print(head[0])
    for f, raw, ctx in missing[:80]:
        print(f"  NOT FOUND {raw}  ...{ctx}...")


if __name__ == "__main__":
    main()
