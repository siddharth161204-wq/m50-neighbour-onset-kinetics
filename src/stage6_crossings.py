#!/usr/bin/env python3
"""Stage 6, Part A: the paper's 150 C criterion applied to the archived Stage 5 runs (DECISIONS.md D51); no new
physics and no Stage 5 run repeated.

For every Stage 5 record (results/v12_runs/, 5,248 runs) and five histories of the neighbour:
  hot     the hottest node (the hot spot);
  mean    the resolved mean, weighted by heat capacity;
  away    the surface node at mid-height on the face away from the trigger (theta = 180 degrees), the thermocouple's
          position used for the comparison;
  toward  the surface node at mid-height on the line of contact (theta = 0), reported separately: the paper does not
          say on which side its thermocouple sat, and one taped to the can could not sit between the cans;
  lumped  the lumped neighbour;
it gives each history's peak and the time of its peak, whether it reaches 150 C, and, for the 48 runs whose
histories were archived (results/v12_series/: the grid, sens and v3 sets), the time of the first crossing of 150 C
and of the return below it, interpolated linearly between the two stored samples that bracket each crossing (the
hottest node, the mean and the lumped neighbour every 0.1 s, the probes at every step), as D35 and D48 (2) do.
The peaks are the records' (taken at every step); the mean's peak time, which the records do not keep, comes from
the series. Writes results/stage6_crossings.csv (one row per run) and results/stage6_crossings.json (the measured
values of A2 beside the counts of A3).

The same functions give the Part B runs their A1 quantities (stage6_run.py).
Usage: python3 stage6_crossings.py [--runs DIR] [--series DIR] [--out DIR]
"""
import argparse, csv, glob, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage6_inputs as IN

RES = os.path.join(HERE, "..", "results")
K0 = 273.15
CLOCKS = ("hot", "mean", "away", "toward", "lumped")
COMPARED = ("hot", "mean", "away", "lumped")          # the four clocks of the comparison (the brief's A1)
LO, HI = IN.WINDOW_S


def first_crossing(t, y, level):
    """First time the history reaches `level`, linear between the two samples that bracket it; None if never."""
    y = np.asarray(y, dtype=float)
    idx = np.flatnonzero(y >= level)
    if idx.size == 0:
        return None
    i = int(idx[0])
    if i == 0:
        return float(t[0])
    y0, y1, t0, t1 = float(y[i - 1]), float(y[i]), float(t[i - 1]), float(t[i])
    return t0 + (t1 - t0) * (level - y0) / (y1 - y0) if y1 > y0 else t1


def return_below(t, y, level, after):
    """First time after `after` at which the history falls below `level` again; None if it stays at or above."""
    t = np.asarray(t, dtype=float)
    y = np.asarray(y, dtype=float)
    idx = np.flatnonzero((t > after) & (y < level))
    if idx.size == 0:
        return None
    i = int(idx[0])
    y0, y1, t0, t1 = float(y[i - 1]), float(y[i]), float(t[i - 1]), float(t[i])
    return t0 + (t1 - t0) * (y0 - level) / (y0 - y1) if y0 > y1 else t1


def histories(series):
    """The five histories of a run's series, in K, with their sample times."""
    return {"hot": (series["t"], series["Tmax"]), "mean": (series["t"], series["Tmean"]),
            "away": (series["probe_t"], series["probe_away"]), "toward": (series["probe_t"], series["probe_toward"]),
            "lumped": (series["t_lumped"], series["T_lumped"])}


def record_peaks(rec):
    """Each history's peak (C) and its time (s) from a record; the mean's time is not kept there (None)."""
    rr, ll = rec["resolved"], rec["lumped"]
    return {"hot": (rr["peak_hottest_C"], rr["t_peak_hottest_s"]), "mean": (rr["peak_mean_C"], None),
            "away": (rr["probe_peak"]["away"]["T_C"], rr["probe_peak"]["away"]["t_s"]),
            "toward": (rr["probe_peak"]["toward"]["T_C"], rr["probe_peak"]["toward"]["t_s"]),
            "lumped": (ll["peak_C"], ll["t_peak_s"])}


def a1(rec, series=None, level_C=IN.LEVEL_150_C):
    """The A1 quantities of one run: per history, its peak and time, whether it reaches the level, and with the
    series the first crossing and the return below it."""
    out = {}
    pk = record_peaks(rec)
    hs = histories(series) if series is not None else None
    for c in CLOCKS:
        T, tp = pk[c]
        d = {"peak_C": float(T), "t_peak_s": None if tp is None else float(tp), "crosses": bool(T >= level_C),
             "t_cross_s": None, "t_return_s": None}
        if hs is not None:
            t, y = hs[c]
            if c == "mean":
                d["t_peak_s"] = float(t[int(np.argmax(y))])
            tc = first_crossing(t, y, level_C + K0)
            if (tc is None) == d["crosses"]:
                # a peak at or above the level always has a crossing in its own series; the only way they can
                # disagree is a peak within one sample of the level, between the stored samples
                d["note"] = "peak and series disagree on the crossing"
            d["t_cross_s"] = tc
            if tc is not None:
                d["t_return_s"] = return_below(t, y, level_C + K0, tc)
        out[c] = d
    return out


def window(tc):
    if tc is None:
        return "none"
    return "below" if tc < LO else ("above" if tc > HI else "inside")


def load_runs(runs_dir):
    recs = {}
    for f in sorted(glob.glob(os.path.join(runs_dir, "*.json"))):
        r = json.load(open(f))
        if not r.get("failed"):
            recs[r["id"]] = r
    return recs


def load_series(path):
    z = np.load(path)
    return {k: z[k] for k in z.files}


def count(rows, clock):
    out = {"n": len(rows), "cross": 0, "inside": 0, "below": 0, "above": 0, "none": 0, "unknown_time": 0}
    for r in rows:
        if r[f"{clock}_crosses"]:
            out["cross"] += 1
        w = r[f"{clock}_window"]
        if w is None:
            out["unknown_time"] += r[f"{clock}_crosses"]
        else:
            out[w] += 1
    times = [r[f"{clock}_t_cross_s"] for r in rows if r[f"{clock}_t_cross_s"] is not None]
    out["t_cross_min_s"] = min(times) if times else None
    out["t_cross_max_s"] = max(times) if times else None
    return out


def main(runs_dir, series_dir, out_dir):
    recs = load_runs(runs_dir)
    keys = ("id", "set", "kin", "connection", "h", "g", "tau", "E_body_J", "T_amb_K", "refine", "dt_scale")
    rows = []
    for rid, rec in recs.items():
        sp = os.path.join(series_dir, rid + ".npz")
        series = load_series(sp) if os.path.exists(sp) else None
        q = a1(rec, series)
        row = {k: rec[k] for k in keys}
        row["has_series"] = series is not None
        for c in CLOCKS:
            d = q[c]
            row.update({f"{c}_peak_C": d["peak_C"], f"{c}_t_peak_s": d["t_peak_s"], f"{c}_crosses": d["crosses"],
                        f"{c}_t_cross_s": d["t_cross_s"], f"{c}_t_return_s": d["t_return_s"],
                        f"{c}_window": window(d["t_cross_s"]) if series is not None else None})
            if d.get("note"):
                row[f"{c}_note"] = d["note"]
        rows.append(row)
    rows.sort(key=lambda r: r["id"])
    os.makedirs(out_dir, exist_ok=True)
    fields = list(keys) + ["has_series"]
    for c in CLOCKS:
        fields += [f"{c}_peak_C", f"{c}_t_peak_s", f"{c}_crosses", f"{c}_t_cross_s", f"{c}_t_return_s", f"{c}_window"]
    notes = sorted({k for r in rows for k in r if k.endswith("_note")})
    with open(os.path.join(out_dir, "stage6_crossings.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields + notes, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    # A3: counts per clock, for the sets with series, by connection, contact, tabs and release
    by = {}
    for s in ("grid", "sens", "v3"):
        rs = [r for r in rows if r["set"] == s]
        d = {"all": {c: count(rs, c) for c in CLOCKS}}
        if s == "grid":
            for key, vals in (("connection", ("series", "parallel")), ("h", ("low", "central", "high")),
                              ("g", ("low", "central", "high")), ("tau", (10.0, 30.0))):
                for v in vals:
                    sub = [r for r in rs if r[key] == v]
                    d[f"{key}={v}"] = {c: count(sub, c) for c in CLOCKS}
            for conn in ("series", "parallel"):
                for h in ("low", "central", "high"):
                    for g in ("low", "central", "high"):
                        sub = [r for r in rs if r["connection"] == conn and r["h"] == h and r["g"] == g]
                        d[f"{conn}_h{h}_g{g}"] = {c: count(sub, c) for c in CLOCKS}
        by[s] = d
    # every record: whether each history reaches 150 C (from its peak), by set and contact
    status = {}
    for s in ("grid", "sens", "v3", "draws", "fact"):
        rs = [r for r in rows if r["set"] == s]
        status[s] = {"n": len(rs), **{c: sum(r[f"{c}_crosses"] for r in rs) for c in CLOCKS}}
        for h in ("low", "central", "high"):
            sub = [r for r in rs if r["h"] == h]
            if sub:
                status[s][f"h={h}"] = {"n": len(sub), **{c: sum(r[f"{c}_crosses"] for r in sub) for c in CLOCKS}}
    status["all"] = {"n": len(rows), **{c: sum(r[f"{c}_crosses"] for r in rows) for c in CLOCKS}}
    m = IN.measured()
    m.pop("by_test")
    out = {"level_C": IN.LEVEL_150_C, "window_s": [LO, HI], "clocks": list(CLOCKS), "compared": list(COMPARED),
           "comparison_face": "away", "n_records": len(rows), "n_with_series": sum(r["has_series"] for r in rows),
           "a2_measured": m, "a3_counts_with_series": by, "a1_crosses_by_set": status,
           "notes": sorted({f"{r['id']}:{k}" for r in rows for k in r if k.endswith("_note")})}
    json.dump(out, open(os.path.join(out_dir, "stage6_crossings.json"), "w"), indent=1, default=float)
    print(f"{len(rows)} records, {out['n_with_series']} with series; written to {out_dir}")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default=os.path.join(RES, "v12_runs"))
    ap.add_argument("--series", default=os.path.join(RES, "v12_series"))
    ap.add_argument("--out", default=RES)
    a = ap.parse_args()
    main(a.runs, a.series, a.out)
