"""Stage 15, Part A0.1 and V1: the archive's continued runs, and the brief's five readings redone from them
(DECISIONS.md D170, D171).

A continued run is a resolved run of Stages 9 to 12 whose stop at the hot spot's 255.68 C was lifted ("stop": false)
with the reaction on: 199 records. For each the table holds the record's own fields (stage, test, kinetics, the
roll's properties, the contact, the SEI, the delivery and its energy, the hot spot's crossing and peak, the far face's
peak, the reaction heat, the lumped twin's crossing, peak and reaction heat, the run's end) and what is read from its
stored series: the mean temperature's crossing of 255.68 C (C8), its peak and the time of its peak, its value at the
run's end, and the start of the far face's jump (A0.2). Stage 11's thermal and contact variants, Stage 9's two
discretisation checks and Stage 12's capped trigger are marked and kept out of the central readings.

V1: the mean's crossing and peak read again by separate code (`_reader_b`: the series read from the npz archive's
raw arrays with the standard library's zipfile and numpy's format reader, then a plain loop), against `_reader_a`
(numpy on the loaded arrays); acceptance 0.1 s and 0.01 K.

Usage: python3 src/stage15_archive.py   (writes results/stage15_archive_table.csv, stage15_readings.json,
stage15_v1.json)
"""
import csv
import glob
import io
import json
import math
import os
import sys
import zipfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage15_inputs as IN               # noqa: E402

K0 = IN.K0
TL = IN.T_LEVEL_C
STAGES = ("stage9", "stage10", "stage11", "stage12")


def continued():
    """(stage, record) for every continued resolved run with the reaction on, in a fixed order."""
    out = []
    for s in STAGES:
        for fn in sorted(glob.glob(os.path.join(IN.RES, f"{s}_runs", "*.json"))):
            d = json.load(open(fn))
            if d.get("stop") is False and d.get("resolved") and d.get("reaction", True) is not False:
                out.append((s, d))
    return out


def series_path(stage, rid):
    return os.path.join(IN.RES, f"{stage}_series", rid + ".npz")


# ------------------------------------------------------------------------------------------------ the two readers
def _reader_a(t, Tm_C, level=TL):
    """numpy: the first sample at or above the level, the crossing linear between it and the sample before."""
    t, T = np.asarray(t, float), np.asarray(Tm_C, float)
    i = np.flatnonzero(T >= level)
    cross = None
    if i.size:
        k = int(i[0])
        cross = float(t[0]) if k == 0 else float(t[k - 1] + (level - T[k - 1]) * (t[k] - t[k - 1]) / (T[k] - T[k - 1]))
    j = int(np.argmax(T))
    return cross, float(T[j]), float(t[j])


def _load_raw(path, names):
    """The npz's members read as raw .npy files through zipfile, not np.load."""
    out = {}
    with zipfile.ZipFile(path) as z:
        for n in names:
            with z.open(n + ".npy") as f:
                out[n] = np.lib.format.read_array(io.BytesIO(f.read()))
    return out


def _reader_b(path):
    """A plain loop over the raw arrays: the crossing by the fraction of the step from the upper sample back, the peak
    as the largest sample (the first, where several are equal)."""
    raw = _load_raw(path, ("t", "Tmean"))
    t = [float(x) for x in raw["t"]]
    T = [float(x) - 273.15 for x in raw["Tmean"]]
    cross = None
    for n in range(len(T)):
        if T[n] >= TL:
            if n == 0:
                cross = t[0]
            else:
                back = (T[n] - TL) / (T[n] - T[n - 1])
                cross = t[n] - back * (t[n] - t[n - 1])
            break
    best, tb = -1e300, None
    for n in range(len(T)):
        if T[n] > best:
            best, tb = T[n], t[n]
    return cross, best, tb


# ------------------------------------------------------------------------------------------------ the far face
def far_face_jump(tp, Tp_C, t_c8, diff_s=IN.DIFF_S, slow=IN.RISE_SLOW, jump=IN.RISE_JUMP, before=IN.BEFORE_S,
                  grid=IN.GRID_S):
    """A0.2: the far face's rate over centred diff_s differences, r(t) = (T(t + diff_s/2) - T(t - diff_s/2)) / diff_s,
    on the measured record's 0.5 s grid; t_rise its first passing slow (K/s), t_slow the first time after t_rise at
    which it falls below slow, t_jump the first time after t_slow at which it passes jump; the reading T(t_jump). Read
    only up to C8 (t_c8). Where the rise never slows below slow before C8, the reading at t_c8 - before. Returns
    (t, T, rule) or None without C8."""
    if t_c8 is None:
        return None
    tp, Tp = np.asarray(tp, float), np.asarray(Tp_C, float)
    half = diff_s / 2.0
    g = np.round(np.arange(half, t_c8 - half + 1e-9, grid), 10)
    Tg = np.interp(g, tp, Tp)
    r = (np.interp(g + half, tp, Tp) - np.interp(g - half, tp, Tp)) / diff_s
    up = np.flatnonzero(r >= slow)
    if up.size:
        dn = np.flatnonzero((r < slow) & (np.arange(r.size) > up[0]))
        if dn.size:
            jm = np.flatnonzero((r >= jump) & (np.arange(r.size) > dn[0]))
            if jm.size:
                return float(g[jm[0]]), float(Tg[jm[0]]), "jump"
    tb = t_c8 - before
    return float(tb), float(np.interp(tb, tp, Tp)), "20 s before C8"


# ------------------------------------------------------------------------------------------------ one row
def group(stage, d):
    """central, or the variant it is (kept out of the central readings)."""
    if d.get("kin", "mean") != "mean":
        return "kinetic draw"
    if d.get("sei", "fresh") != "fresh":
        return "aged SEI"
    if d.get("refine", 1.0) != 1.0 or d.get("dt_scale", 1.0) != 1.0:
        return "discretisation check"
    if d.get("thermal") not in (None, "central"):
        return "thermal variant"
    if d.get("h", "central") != "central" or d.get("g", "central") != "central":
        return "contact variant"
    if stage == "stage12":
        return "capped trigger"
    return "central"


def row(stage, d):
    r, l = d["resolved"], d.get("lumped") or {}
    path = series_path(stage, d["id"])
    z = np.load(path)
    t, Tm = z["t"], z["Tmean"] - K0
    c8, pk, tpk = _reader_a(t, Tm)
    fj = far_face_jump(z["probe_t"], z["probe_away"] - K0, c8) if "probe_away" in z.files else None
    tx = r.get("t_prop_s")
    if tx is None:
        tx = (r.get("cross_s") or {}).get("T_onset_low")
    txl = l.get("t_prop_s")
    if txl is None and l:
        txl = (l.get("cross_s") or {}).get("T_onset_low")
    pp = (r.get("probe_peak") or {}).get("away") or {}
    mach = d.get("machine") or {}
    return {
        "stage": int(stage.replace("stage", "")), "id": d["id"], "kind": d.get("kind"), "group": group(stage, d),
        "test": d["test"], "connection": d.get("connection"), "kin": d.get("kin"), "thermal": d.get("thermal"),
        "h": d.get("h"), "sei": d.get("sei"), "shape": d.get("shape"), "tau_d_s": d.get("tau_d_s"), "f": d.get("f"),
        "E_delivered_J": d.get("E_delivered_J"), "E_body_J": d.get("E_body_J"),
        "res_t_cross_s": tx, "res_peak_C": r.get("peak_hottest_C"), "res_t_peak_s": r.get("t_peak_hottest_s"),
        "mean_t_cross_s": c8, "mean_peak_C": pk, "mean_t_peak_s": tpk, "mean_at_end_C": float(Tm[-1]),
        "mean_peak_record_C": r.get("peak_mean_C"),
        "far_peak_C": pp.get("T_C"), "far_t_peak_s": pp.get("t_s"),
        "far_jump_t_s": fj[0] if fj else None, "far_jump_C": fj[1] if fj else None, "far_jump_rule": fj[2] if fj else None,
        "res_rxn_J": (r.get("energy_J") or {}).get("in_rxn", r.get("in_rxn_J")),
        "lum_t_cross_s": txl, "lum_peak_C": l.get("peak_C"), "lum_t_peak_s": l.get("t_peak_s"),
        "lum_rxn_J": l.get("reaction_heat_J"), "t_end_s": r.get("t_end_s"),
        "wall_s": d.get("wall_s"), "machine": mach.get("label"), "steps": r.get("steps"),
        "max_implicit_nodes": r.get("max_implicit_nodes"), "max_sub": r.get("max_sub", d.get("max_sub")),
        "steps_with_max_sub": r.get("steps_with_max_sub"),
        "implicit_node_steps_with_max_sub": r.get("implicit_node_steps_with_max_sub"), "rejected": r.get("rejected"),
    }


def table():
    return [row(s, d) for s, d in continued()]


def write_table(rows, path=os.path.join(IN.RES, "stage15_archive_table.csv")):
    keys = list(rows[0].keys())
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r[k] is None else r[k]) for k in keys})


# ------------------------------------------------------------------------------------------------ V1
def v1(rows):
    worst_t = worst_T = 0.0
    bad = []
    for r in rows:
        c8b, pkb, _ = _reader_b(series_path(f"stage{r['stage']}", r["id"]))
        a, b = r["mean_t_cross_s"], c8b
        if (a is None) != (b is None):
            bad.append((r["id"], "crossing in one reader only"))
            continue
        dt = abs(a - b) if a is not None else 0.0
        dT = abs(r["mean_peak_C"] - pkb)
        worst_t, worst_T = max(worst_t, dt), max(worst_T, dT)
        if dt > 0.1 or dT > 0.01:
            bad.append((r["id"], dt, dT))
    rec_diff = max(abs(r["mean_peak_C"] - r["mean_peak_record_C"]) for r in rows if r["mean_peak_record_C"] is not None)
    return {"runs": len(rows), "worst_crossing_s": worst_t, "worst_peak_K": worst_T, "failures": bad,
            "passed": not bad, "acceptance": "0.1 s and 0.01 K",
            "series_peak_against_record_peak_K_max": rec_diff,
            "note": "the record's peak_mean_C is taken at every step, the series every 0.1 s; for the record only"}


# ------------------------------------------------------------------------------------------------ the readings
def _rng(xs, nd=1):
    xs = [x for x in xs if x is not None]
    return [round(min(xs), nd), round(max(xs), nd)] if xs else None


def readings(rows):
    T = IN.tests()
    cen = [r for r in rows if r["group"] == "central"]
    out = {}
    # 1. at the delivery where the whole-cell clock reproduces the measured time, 21.39 s (Stage 9's story runs)
    s1 = [r for r in cen if r["stage"] == 9 and r["kind"] == "story" and r["shape"] == "tri"]
    pt = [r for r in cen if r["id"] == "s10_tri21_fresh_hcentral_M50_PT_Exp4_f0.040625000_t332"]
    out["1"] = {
        "runs": [r["id"] for r in s1], "tests_J": {r["test"]: round(r["E_delivered_J"]) for r in s1},
        "lumped_cross_s": _rng([r["lum_t_cross_s"] for r in s1]), "lumped_rxn_kJ": _rng([r["lum_rxn_J"] / 1e3 for r in s1], 1),
        "hot_cross_s": _rng([r["res_t_cross_s"] for r in s1]), "hot_peak_C": _rng([r["res_peak_C"] for r in s1]),
        "mean_peak_C": _rng([r["mean_peak_C"] for r in s1]), "mean_t_peak_s": _rng([r["mean_t_peak_s"] for r in s1], 0),
        "mean_at_900_C": _rng([r["mean_at_end_C"] for r in s1], 0), "res_rxn_kJ": _rng([r["res_rxn_J"] / 1e3 for r in s1], 1),
        "any_C8": any(r["mean_t_cross_s"] is not None for r in s1),
        "PT_Exp4": ({"E_J": round(pt[0]["E_delivered_J"]), "lumped_cross_s": round(pt[0]["lum_t_cross_s"], 1),
                     "mean_peak_C": round(pt[0]["mean_peak_C"], 1), "mean_t_peak_s": round(pt[0]["mean_t_peak_s"], 0),
                     "t_end_s": pt[0]["t_end_s"], "C8": pt[0]["mean_t_cross_s"]} if pt else None)}
    # 2. no delivery, the eight tests whose trigger alone takes the hot spot over the level
    s2 = {}
    for r in cen:
        if r["shape"] == "none" and r["res_t_cross_s"] is not None and r["t_end_s"] >= 899.9:
            s2.setdefault(r["test"], r)
    s2 = list(s2.values())
    out["2"] = {"tests": sorted(r["test"] for r in s2), "runs": [r["id"] for r in s2],
                "hot_cross_s": _rng([r["res_t_cross_s"] for r in s2]), "hot_peak_C": _rng([r["res_peak_C"] for r in s2]),
                "mean_peak_C": _rng([r["mean_peak_C"] for r in s2]), "res_rxn_kJ": _rng([r["res_rxn_J"] / 1e3 for r in s2], 2),
                "any_C8": any(r["mean_t_cross_s"] is not None for r in s2),
                "propagated_measured": sum(bool(T[r["test"]]["propagated"]) for r in s2)}
    # 3. the long deliveries at the matched energies (Stage 9's story runs; M50_PT_Exp4's Stage 10 runs)
    s3 = [r for r in cen if r["shape"] == "con" and ((r["stage"] == 9 and r["kind"] == "story") or
                                                     (r["stage"] == 10 and r["test"] == "M50_PT_Exp4"))]
    by = {}
    for r in s3:
        by.setdefault(r["tau_d_s"], []).append({
            "test": r["test"], "E_J": round(r["E_delivered_J"]), "id": r["id"], "C8_s": r["mean_t_cross_s"],
            "lumped_s": r["lum_t_cross_s"], "measured_s": T[r["test"]]["time_s"], "t_end_s": r["t_end_s"],
            "mean_at_end_C": r["mean_at_end_C"], "mean_peak_C": r["mean_peak_C"]})
    out["3"] = {str(k): sorted(v, key=lambda x: (x["test"], x["E_J"])) for k, v in sorted(by.items())}
    # 4. with no delivery, the lumped neighbour against the resolved mean, where the lumped does not run away
    s4 = {}
    for r in cen:
        if r["shape"] == "none" and r["lum_t_cross_s"] is None:
            s4.setdefault(r["test"], r)
    diffs = {k: {"lumped_peak_C": round(v["lum_peak_C"], 1), "mean_peak_C": round(v["mean_peak_C"], 1),
                 "diff_K": round(v["lum_peak_C"] - v["mean_peak_C"], 1), "t_end_s": v["t_end_s"]} for k, v in s4.items()}
    out["4"] = {"tests": len(s4), "diff_K": _rng([v["diff_K"] for v in diffs.values()]), "by_test": diffs}
    st2 = json.load(open(os.path.join(IN.RES, "stage10_runs", "s10_none_fresh_hcentral_M50_ST_Exp2_f0.000000000_t900.json")))
    out["4"]["ST_Exp2_intake_900s_J"] = {
        "lumped_link_with_tabs": st2["lumped"]["energy_J"]["in_link"],
        "resolved_contact_and_tabs": st2["resolved"]["energy_J"]["in_gap"] + st2["resolved"]["energy_J"]["in_bus"]}
    # 5. M50_PT_Exp4's measured history against the model's far face; the far face in the runs of reading 3
    tm, Tmeas = IN.measured_history()
    z = np.load(series_path("stage10", "s10_tri21_fresh_hcentral_M50_PT_Exp4_f0.040625000_t332"))
    tp, Tp = z["probe_t"], z["probe_away"] - K0
    at = lambda x: float(np.interp(x, tp, Tp))
    slope = (at(271.5) - at(261.5)) / 10.0
    r5 = {"measured_45_C": float(np.interp(45.0, tm, Tmeas)), "measured_271.5_C": float(np.interp(271.5, tm, Tmeas)),
          "model_45_C": at(45.0), "model_271.5_C": at(271.5), "model_minus_measured_271.5_K":
          at(271.5) - float(np.interp(271.5, tm, Tmeas)), "model_slope_261.5_271.5_K_per_s": slope}
    ten = [x for v in out["3"].values() for x in v if x["C8_s"] is not None]
    rr = {r["id"]: r for r in cen}
    fj = [(x["test"], x["E_J"], rr[x["id"]]["far_jump_rule"], rr[x["id"]]["far_jump_C"],
           float(np.interp(x["C8_s"] - IN.BEFORE_S, *_probe(rr[x["id"]])))) for x in ten]
    r5["runaway_runs"] = len(ten)
    r5["far_20s_before_C8_C"] = _rng([x[4] for x in fj])
    r5["far_jump_C_where_slowed"] = _rng([x[3] for x in fj if x[2] == "jump"])
    r5["n_slowed"] = sum(1 for x in fj if x[2] == "jump")
    r5["by_run"] = [{"test": a, "E_J": b, "rule": c, "reading_C": d, "far_20s_before_C": e} for a, b, c, d, e in fj]
    out["5"] = r5
    return out


def _probe(r):
    z = np.load(series_path(f"stage{r['stage']}", r["id"]))
    return z["probe_t"], z["probe_away"] - K0


def main():
    rows = table()
    write_table(rows)
    v = v1(rows)
    json.dump(v, open(os.path.join(IN.RES, "stage15_v1.json"), "w"), indent=1)
    rd = readings(rows)
    json.dump(rd, open(os.path.join(IN.RES, "stage15_readings.json"), "w"), indent=1, default=float)
    print(len(rows), "continued runs;", sum(r["group"] == "central" for r in rows), "central; V1",
          "passed" if v["passed"] else "FAILED", v["worst_crossing_s"], v["worst_peak_K"])
    return rows, v, rd


if __name__ == "__main__":
    main()
