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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--supplement", action="store_true")
    ap.add_argument("--loose", action="store_true")
    a = ap.parse_args()
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
