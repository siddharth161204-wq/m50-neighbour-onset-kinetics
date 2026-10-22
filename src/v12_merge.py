#!/usr/bin/env python3
"""Stage 5: the registered run records, merged from the two machines by the rule of DECISIONS.md D46 (2).

The fact runs of draws 166 to 200 come from the cloud machine (results/v12_runs_cloud/), every other run from the
author's laptop (a folder of its records, unpacked from results_v12_laptop.zip). Every run of the list must be
present exactly once. Runs that both machines made (the cloud's D45 (3) copies of the grid, sens and v3 sets, and any
other) are compared field by field as the check across platforms. Writes results/v12_runs/ (the registered records),
results/v12_series/ (the laptop's series), and results/v12_merge.json (where each record came from and the comparison).

Usage: python3 v12_merge.py --laptop <folder holding the laptop's v12_runs/ and v12_series/> [--check-only]
"""
import argparse, glob, json, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v12_run as RUN

RES = os.path.join(HERE, "..", "results")
CLOUD = os.path.join(RES, "v12_runs_cloud")
CLOUD_SHARE = (166, 200)                 # D46 (2) and (3)
SKIP = ("wall_s", "started_utc", "finished_utc", "machine")


def cloud_share(spec):
    return spec["set"] == "fact" and CLOUD_SHARE[0] <= spec["kin"] <= CLOUD_SHARE[1]


def flat(d, p=""):
    out = {}
    if isinstance(d, dict):
        for k, v in d.items():
            out.update(flat(v, f"{p}.{k}" if p else k))
    elif isinstance(d, (list, tuple)):
        for i, v in enumerate(d):
            out.update(flat(v, f"{p}[{i}]"))
    else:
        out[p] = d
    return out


def compare(a, b):
    fa, fb = flat(a), flat(b)
    worst, other = {}, []
    for k in sorted(set(fa) | set(fb)):
        if k.split(".")[0].split("[")[0] in SKIP:
            continue
        x, y = fa.get(k), fb.get(k)
        if isinstance(x, float) and isinstance(y, float) and not isinstance(x, bool):
            worst[k] = abs(x - y)
        elif x != y:
            other.append(k)
    return worst, other


def load_dir(d):
    return {os.path.basename(f)[:-5]: f for f in glob.glob(os.path.join(d, "*.json"))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--laptop", required=True)
    ap.add_argument("--check-only", action="store_true")
    a = ap.parse_args()
    runs = RUN.build_runs()
    lap = load_dir(os.path.join(a.laptop, "v12_runs"))
    cld = load_dir(CLOUD)
    chosen, missing, source = {}, [], {"laptop": 0, "cloud": 0}
    for s in runs:
        i = s["id"]
        if cloud_share(s):
            f, tag = cld.get(i), "cloud"
        else:
            f, tag = lap.get(i), "laptop"
        if f is None:
            missing.append(i)
            continue
        chosen[i] = (f, tag)
        source[tag] += 1
    both = sorted(set(lap) & set(cld))
    worst, other, labels = {}, {}, {}
    for i in both:
        w, o = compare(json.load(open(lap[i])), json.load(open(cld[i])))
        for k, v in w.items():
            if v > worst.get(k, (-1.0, ""))[0]:
                worst[k] = (v, i)
        if o:
            other[i] = o
    for i, (f, tag) in chosen.items():
        m = json.load(open(f)).get("machine", {}).get("label", "none")
        labels[m] = labels.get(m, 0) + 1
    failed = [i for i, (f, _) in chosen.items() if json.load(open(f)).get("failed")]
    rec = {"rule": "DECISIONS.md D46 (2) and (3): fact runs of draws 166 to 200 from the cloud machine, every other run from the laptop",
           "runs_in_list": len(runs), "records_chosen": len(chosen), "missing": missing, "failed": failed,
           "by_source": source, "by_machine_label": labels,
           "both_machines": {"n": len(both), "ids": both,
                             "max_abs_difference": {k: {"value": v, "run": i} for k, (v, i) in
                                                    sorted(worst.items(), key=lambda kv: -kv[1][0])},
                             "non_numeric_differences": other}}
    if not a.check_only and not missing:
        out = os.path.join(RES, "v12_runs")
        os.makedirs(out, exist_ok=True)
        for i, (f, _) in chosen.items():
            shutil.copy2(f, os.path.join(out, i + ".json"))
        sdir = os.path.join(RES, "v12_series")
        os.makedirs(sdir, exist_ok=True)
        for f in glob.glob(os.path.join(a.laptop, "v12_series", "*.npz")):
            shutil.copy2(f, sdir)
        rec["written"] = {"records": len(chosen), "series": len(glob.glob(os.path.join(sdir, "*.npz")))}
    json.dump(rec, open(os.path.join(RES, "v12_merge.json") if not a.check_only else os.devnull, "w"), indent=1,
              default=float)
    top = list(rec["both_machines"]["max_abs_difference"].items())[:5]
    print(json.dumps({k: rec[k] for k in ("runs_in_list", "records_chosen", "by_source", "by_machine_label")}),
          "missing", len(missing), "failed", len(failed), "| both machines", len(both),
          "non-numeric differences", len(other), "| largest", top)


if __name__ == "__main__":
    main()
