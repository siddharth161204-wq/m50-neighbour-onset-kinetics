#!/usr/bin/env python3
"""Compare check records written by two runs of the same script (for example the committed V0 to V2 records against
a re-run with the final code). Every numeric leaf of each JSON pair, and every numeric cell of each CSV pair, is
compared; the largest relative difference |a - b| / max(|a|, |b|, 1e-300) is reported per file, with the count of
leaves that differ in kind (a number on one side and not the other, or two different strings). Leaves that are
themselves small differences (relative changes, residuals) are compared in absolute terms. Writes the summary as JSON.

Usage: python3 compare_records.py --a ../results --b /path/to/rerun --files v0_dsc_check.json v1_arc_check.json \
           v1_arc_trace.csv v2_synthetic.json --out ../results/rerun_final_code.json
"""
import argparse, csv, json, math, os, re


def leaves(x, path=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from leaves(v, f"{path}/{k}")
    elif isinstance(x, (list, tuple)):
        for i, v in enumerate(x):
            yield from leaves(v, f"{path}[{i}]")
    else:
        yield path, x


def num(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


ABSOLUTE = re.compile(r"rel_change|relative_change|residual")


def compare(pa, pb):
    """Quantities that are themselves small differences (paths matching ABSOLUTE: the relative changes of V2, energy
    residuals) are compared in absolute terms, since their relative difference is noise; every other number relatively."""
    if pa.endswith(".csv"):
        A = {f"[{i}]/{k}": v for i, r in enumerate(csv.DictReader(open(pa))) for k, v in r.items()}
        B = {f"[{i}]/{k}": v for i, r in enumerate(csv.DictReader(open(pb))) for k, v in r.items()}
    else:
        A, B = dict(leaves(json.load(open(pa)))), dict(leaves(json.load(open(pb))))
    worst, where, n, kind, worst_abs, where_abs, n_abs = 0.0, None, 0, 0, 0.0, None, 0
    for k in sorted(set(A) | set(B)):
        a, b = num(A.get(k)), num(B.get(k))
        if a is None and b is None:
            if A.get(k) != B.get(k):
                kind += 1
            continue
        if (a is None) != (b is None) or (a is not None and (math.isnan(a) != math.isnan(b))):
            kind += 1
            continue
        if math.isnan(a):
            continue
        if ABSOLUTE.search(k):
            n_abs += 1
            if abs(a - b) > worst_abs:
                worst_abs, where_abs = abs(a - b), k
            continue
        n += 1
        d = abs(a - b) / max(abs(a), abs(b), 1e-300)
        if d > worst:
            worst, where = d, k
    out = {"numbers_compared": n, "max_relative_difference": worst, "at": where, "leaves_differing_in_kind": kind}
    if n_abs:
        out.update({"small_differences_compared_absolutely": n_abs, "their_max_absolute_difference": worst_abs,
                    "their_at": where_abs})
    return out


ap = argparse.ArgumentParser()
ap.add_argument("--a", required=True); ap.add_argument("--b", required=True)
ap.add_argument("--files", nargs="+", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--label-a", default="committed records"); ap.add_argument("--label-b", default="re-run with the final code")
ap.add_argument("--note", default="")
a = ap.parse_args()
res = {"a": a.label_a, "b": a.label_b, "note": a.note,
       "files": {f: compare(os.path.join(a.a, f), os.path.join(a.b, f)) for f in a.files}}
json.dump(res, open(a.out, "w"), indent=1)
print(json.dumps(res, indent=1))
