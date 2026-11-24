"""Step 16's check V4, its first part: every bracket and every verdict recomputed from the run records by code separate
from src/stage16_run.py and src/stage16_score.py (it imports neither, nor the model's input modules), and set against
results/stage16_scorecard.json. The second part is an independent read by a separate agent.

It reads only files: the Step 16 and Stage 15 run records (results/stage16_runs/, results/stage15_runs/), the archived
runs Stage 15 set the cross-section against (results/stage15_cross_section.json, A1_rows), Table S7's source
(results/stage15_table.csv), the ejected energies (results/stage14_needs.csv) and the registered rules as written in
predictions_stage16.md (restated here as constants).

Writes results/stage16_recheck.json. Run: python3 src/stage16_recheck.py
"""
import csv
import glob
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RES = os.path.join(ROOT, "results")
STRONG = ["M50_PT_Exp4", "M50_PP_Exp1", "M50_PP_Exp2", "M50_PP_Exp4", "M50_ST_Exp4", "M50_SP_Exp1", "M50_SP_Exp2",
          "M50_SP_Exp3"]
PULSE = 21.38651984299561           # the pulse's length (s), as every record of the configuration carries it
WINDOW, FINAL = 10.0, 0.00125
XS_T_PT1 = 10781.25                 # the cross-section's E*(C8) for PT-Exp1 (predictions_stage16.md)
LUMPED_T = (12848.834034982421, 12892.389404592532)
LABEL = {"tri": "21.39 s pulse", 120.0: "120 s constant power", 240.0: "240 s constant power",
         360.0: "360 s constant power"}


def records(d):
    out = {}
    for f in glob.glob(os.path.join(RES, d, "*.json")):
        r = json.load(open(f))
        out[r["id"]] = r
    return out


def table():
    with open(os.path.join(RES, "stage15_table.csv")) as fh:
        return {(r["test"], r["delivery"]): r for r in csv.DictReader(fh)}


def ejected():
    with open(os.path.join(RES, "stage14_needs.csv")) as fh:
        return {r["test"]: float(r["E_e_J"]) for r in csv.DictReader(fh)}


def base_config(r):
    if r.get("failed") or r.get("h") != "central" or r.get("kin") != "mean" or r.get("sei0") is not None:
        return False
    if (r.get("shift_K") or 0.0) != 0.0 or r.get("refine", 1.0) != 1.0 or r.get("dt_scale", 1.0) != 1.0:
        return False
    return len(r["deliveries"]) == 1


def same_delivery(shape, tau, d_shape, d_tau):
    if shape == "tri":
        return d_shape == "tri" and abs(d_tau - PULSE) < 1e-6
    return d_shape == "con" and abs(d_tau - tau) < 1e-6


def counted_runs(test, shape, tau, r15, r16, a1):
    out = []
    for a in a1:
        if a["test"] == test and same_delivery(shape, tau, a["shape"], a["tau_d_s"]):
            out.append((float(a["E_J"]), a["t_C8_3d_s"], float(a["t_end_s"]), a["id"]))
    for recs in (r15, r16):
        for r in recs.values():
            if r["test"] == test and base_config(r):
                d = r["deliveries"][0]
                if same_delivery(shape, tau, d["shape"], d["tau_s"]):
                    p = r["resolved"]
                    out.append((float(r["E_delivered_J"]), p["t_C8_s"] if p["C8"] else None, float(p["t_end_s"]),
                                r["id"]))
    return out


def cls(t_c8, t_end, t_m):
    if t_c8 is not None:
        return "early" if t_c8 <= t_m + WINDOW + 1e-9 else "late"
    if t_end >= min(900.0, t_m + WINDOW) - 1e-9:
        return "late"
    return None


def share(shape, tau, t):
    if shape == "tri":
        x = min(1.0, t / PULSE)
        return 2 * x * x if x <= 0.5 else 1 - 2 * (1 - x) ** 2
    return min(1.0, t / tau)


def bracket(test, shape, tau, r15, r16, a1, E_e, t_m):
    runs = [(E, cls(t, te, t_m), t, rid) for E, t, te, rid in counted_runs(test, shape, tau, r15, r16, a1)]
    runs = [x for x in runs if x[1] is not None]
    early = sorted(x for x in runs if x[1] == "early")
    late = sorted(x for x in runs if x[1] == "late")
    if early and late and late[-1][0] > early[0][0] + 1e-6 * E_e:
        return {"status": "not monotone"}
    if not early or not late:
        return {"status": "open"}
    lo, hi = late[-1], early[0]
    if hi[0] - lo[0] > FINAL * E_e + 1e-6 * E_e:
        return {"status": "open", "lo_J": lo[0], "hi_J": hi[0]}
    return {"status": "done", "lo_J": lo[0], "hi_J": hi[0], "lo_id": lo[3], "hi_id": hi[3], "lo_t": lo[2],
            "hi_t": hi[2]}


def main():
    r15 = {k: v for k, v in records("stage15_runs").items()}
    r16 = records("stage16_runs")
    a1 = json.load(open(os.path.join(RES, "stage15_cross_section.json")))["A1_rows"]
    tab = table()
    E_e = ejected()
    sc = json.load(open(os.path.join(RES, "stage16_scorecard.json")))
    out = {"N": {}, "X": {}, "agree": True, "differences": []}

    def need(test, shape, tau):
        row = tab[(test, LABEL["tri" if shape == "tri" else tau])]
        t_m = float(row["t_measured_s"])
        b = bracket(test, shape, tau, r15, {k: v for k, v in r16.items() if v.get("kind") in ("N", "X")}, a1,
                    E_e[test], t_m)
        s = share(shape, tau, t_m + WINDOW)
        if b["status"] == "done":
            mid = 0.5 * (b["lo_J"] + b["hi_J"]) * s
            b["d"] = (float(row["C8_xs_E_by_t_J"]) - mid) / mid
            b["lo_by_t"], b["hi_by_t"] = b["lo_J"] * s, b["hi_J"] * s
            b["lumped"] = float(row["C2_E_by_t_J"])
        return b

    for t in STRONG:
        b = need(t, "tri", None)
        out["N"][t] = b
        mine = next(r for r in sc["N"] if r["test"] == t)
        if b["status"] != mine["status"] or (b["status"] == "done" and (abs(b["lo_J"] - mine["lo_J"]) > 1e-6 or
                                                                        abs(b["hi_J"] - mine["hi_J"]) > 1e-6)):
            out["agree"] = False
            out["differences"].append(("N", t, b, {k: mine.get(k) for k in ("status", "lo_J", "hi_J")}))
    for tau in (240.0, 120.0, 360.0):
        for t in STRONG:
            b = need(t, "con", tau)
            out["X"]["%s %s" % (t, LABEL[tau])] = b
            mine = next(r for r in sc["X"] if r["test"] == t and r["delivery"] == LABEL[tau])
            if b["status"] == "done" or mine["status"] == "done":
                if b["status"] != mine["status"] or abs(b["lo_J"] - mine["lo_J"]) > 1e-6 or \
                        abs(b["hi_J"] - mine["hi_J"]) > 1e-6:
                    out["agree"] = False
                    out["differences"].append(("X", t, tau, b, {k: mine.get(k) for k in ("status", "lo_J", "hi_J")}))
    # T: the runs at the cross-section's value times 1 + 0.05 k; the bracket is two steps wide
    T = sorted(((round((r["E_delivered_J"] / XS_T_PT1 - 1) / 0.05), r["E_delivered_J"], r["resolved"]["C8"])
                for r in r16.values() if r.get("kind") == "T" and not r.get("failed")))
    yes = [x for x in T if x[2]]
    no = [x for x in T if not x[2]]
    tb = None
    if yes and no and min(yes)[0] - max(no)[0] == 2:
        tb = {"lo_J": max(no)[1], "hi_J": min(yes)[1]}
        mid = 0.5 * (tb["lo_J"] + tb["hi_J"])
        tb["ratio_mid"] = mid / (0.5 * sum(LUMPED_T))
    out["T"] = tb
    mine = sc["T"]
    if tb and (abs(tb["lo_J"] - mine.get("lo_J", -1)) > 1e-6 or abs(tb["hi_J"] - mine.get("hi_J", -1)) > 1e-6):
        out["agree"] = False
        out["differences"].append(("T", tb, {k: mine.get(k) for k in ("lo_J", "hi_J")}))
    # the verdicts, by the registered rules
    N = out["N"]
    done = all(N[t]["status"] == "done" for t in STRONG)
    v = {}
    v["P1"] = done and all(abs(N[t]["d"]) <= 0.10 for t in STRONG)
    v["P2"] = done and all(N[t]["d"] > 0 for t in STRONG)
    v["P3"] = done and all(N[t]["lo_by_t"] >= 4050 and N[t]["hi_by_t"] <= 8150 for t in STRONG)
    v["P4"] = done and all(N[t]["lo_by_t"] >= N[t]["lumped"] - 0.05 - 1e-6 for t in STRONG)
    v["P5"] = done and all(N[t]["lo_by_t"] - N[t]["lumped"] >= 1000 and N[t]["hi_by_t"] - N[t]["lumped"] <= 5000
                           for t in STRONG)
    v["P6"] = bool(tb) and tb["hi_J"] <= LUMPED_T[0]
    v["P7"] = bool(tb) and 0.75 <= tb["ratio_mid"] <= 0.95
    # V: the refined runs (kind V) against the base ends of the chosen test's bracket
    V = [r for r in r16.values() if r.get("kind") == "V"]
    if V:
        test = V[0]["test"]
        row = tab[(test, LABEL["tri"])]
        t_m = float(row["t_measured_s"])
        b = N[test]
        w = b["hi_J"] - b["lo_J"]
        ref = sorted((r["E_delivered_J"], cls(r["resolved"]["t_C8_s"] if r["resolved"]["C8"] else None,
                                              r["resolved"]["t_end_s"], t_m), r["resolved"]["t_C8_s"]) for r in V)
        early = [x[0] for x in ref if x[1] == "early"]
        late = [x[0] for x in ref if x[1] == "late"]
        ok8 = bool(early and late) and max(late) < min(early) and max(late) >= b["lo_J"] - w - 1e-6 and \
            min(early) <= b["hi_J"] + w + 1e-6
        rel = []
        for E, c, t in ref:
            for side, Eb, tb_ in (("lo", b["lo_J"], b["lo_t"]), ("hi", b["hi_J"], b["hi_t"])):
                if abs(E - Eb) < 1e-6:
                    rel.append(None if (t is None or tb_ is None) else (t - tb_) / tb_)
        v["P8"] = ok8
        v["P9"] = bool(rel) and all(x is not None and abs(x) < 0.03 for x in rel)
        out["V"] = {"test": test, "refined": ref, "rel": rel}
    X = [b for b in out["X"].values() if b["status"] == "done"]
    v["P10"] = (all(abs(b["d"]) <= 0.10 for b in X)) if X else None
    v["P11"] = (all(b["lo_by_t"] >= b["lumped"] - 0.05 - 1e-6 for b in X)) if X else None
    out["verdicts"] = v
    theirs = {k: p["held"] for k, p in sc["scorecard"]["predictions"].items()}
    out["verdicts_agree"] = all(theirs.get(k) == v.get(k) for k in v)
    if not out["verdicts_agree"]:
        out["differences"].append(("verdicts", v, theirs))
    json.dump(out, open(os.path.join(RES, "stage16_recheck.json"), "w"), indent=1, default=float)
    print("brackets agree:", out["agree"], "verdicts agree:", out["verdicts_agree"])
    print(v)
    for d in out["differences"]:
        print("DIFF", d)


if __name__ == "__main__":
    main()
