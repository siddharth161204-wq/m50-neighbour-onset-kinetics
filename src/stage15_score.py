"""Stage 15: the scoring of P1 to P8, Part C's tables, the paper numbers and the checks V2 and V4 (DECISIONS.md
D177 onward), from the records (`results/stage15_runs/`), the reduced model's file (`results/stage15_cross_section.json`,
registered) and the archive.

Writes results/stage15_scorecard.json, stage15_table.csv (C1), stage15_nodelivery.csv (C2), stage15_checks.json,
stage15_paper_numbers.json.
"""
import csv
import json
import math
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage15_inputs as IN              # noqa: E402
import stage15_partb as PB               # noqa: E402
import stage15_predictions as PR         # noqa: E402
import stage15_archive as AR             # noqa: E402
import stage10_score as S10              # noqa: E402  (unchanged)

RES = IN.RES
E_FIX = 76741.25                         # Stage 12's fixed ejected energy, the Databank's median (D122)
STAGE14 = ("026b9c0", "results/stage14_module_table_corrected.csv")


def _f(x):
    return None if x in ("", None) else float(x)


# ------------------------------------------------------------------------------------------------ Part B's states
def states(recs):
    out = {"B1": {}}
    for t in IN.B1_TESTS:
        st, _, br = PB.b1_state(t, recs)
        out["B1"][t] = {"status": st, "bracket": br}
        if br:
            br["mid_J"] = 0.5 * (br["lo_J"] + br["hi_J"])
    out["B2"] = {f: recs.get(PB.b2_spec(f)["id"]) for f in PB.B2_F}
    st, _, res = PB.b3_state(recs)
    out["B3"] = {"status": st, "result": res}
    _, res4 = PB.b4_state(recs)
    out["B4"] = {"draws": {r: recs.get(PB.b4_spec(kin=IN.KIN_DRAWS[r])["id"]) for r in (5, 50, 151, 196)},
                 "aged": recs.get(PB.b4_spec(sei0=IN.SEI_AGED)["id"]), "shift": res4}
    return out


def history_score(rec):
    """B3 (a): Stage 10's rule (D103 (2)) at the far face, over 0 to 271.5 s, or to C8 where it comes first."""
    z = np.load(os.path.join(IN.SERIES, rec["id"] + ".npz"))
    tp, Tp = z["probe_t"], z["probe_away"] - IN.K0
    tm, Tm = IN.measured_history()
    t1 = min(IN.T_PROP_FIG_S, float(tp[-1]))
    m = S10.metrics(tm, Tm, tp, Tp, 0.0, t1)
    m["window_s"] = [0.0, t1]
    return m


# ------------------------------------------------------------------------------------------------ the scorecard
def scorecard(xs, recs, S):
    fp = xs["for_predictions"]
    b1 = S["B1"]
    P = {}
    # P1
    inside = {}
    for t in IN.B1_TESTS:
        br = b1[t]["bracket"]
        e2 = fp["B1"][t]["E_star_J"]
        inside[t] = (abs(e2 - br["mid_J"]) / br["mid_J"] <= 0.15) if br else False
    if xs["A1_summary"]["A3_cannot_stand"]:
        P["P1"] = {"verdict": "dropped", "why": "A3"}
    else:
        P["P1"] = {"verdict": "held" if sum(inside.values()) >= 3 else "failed", "within": inside,
                   "rel_diff": {t: ((fp["B1"][t]["E_star_J"] - b1[t]["bracket"]["mid_J"]) / b1[t]["bracket"]["mid_J"]
                                    if b1[t]["bracket"] else None) for t in IN.B1_TESTS}}
    # P2
    br = b1["M50_PT_Exp4"]["bracket"]
    P["P2"] = {"verdict": "held" if (br and 6000.0 <= br["mid_J"] <= 10000.0) else "failed",
               "mid_J": br["mid_J"] if br else None, "bracket_J": [br["lo_J"], br["hi_J"]] if br else None}
    # P3
    ex = {}
    for t in IN.B1_TESTS:
        brt = b1[t]["bracket"]
        c2 = PR.e_c2(t)["mid_J"]
        if not brt:
            ex[t] = False
        elif c2 == 0.0:
            ex[t] = brt["mid_J"] > 0.0
        else:
            ex[t] = brt["mid_J"] >= 1.25 * c2
    P["P3"] = {"verdict": "held" if sum(ex.values()) >= 3 else "failed", "exceeds": ex,
               "ratio": {t: (b1[t]["bracket"]["mid_J"] / PR.e_c2(t)["mid_J"]) if (b1[t]["bracket"] and
                                                                                 PR.e_c2(t)["mid_J"] > 0) else None
                         for t in IN.B1_TESTS},
               "E_C2_J": {t: PR.e_c2(t)["mid_J"] for t in IN.B1_TESTS}}
    # P4, P5
    if br:
        hi = recs[br["hi_id"]]["resolved"]
        t8 = hi["t_C8_s"]
        P["P4"] = {"verdict": "held" if (t8 is not None and 150.0 <= t8 <= 400.0) else "failed", "t_C8_s": t8,
                   "run": br["hi_id"]}
        fj = hi["far_jump"]
        P["P5"] = {"verdict": "held" if (fj and fj["T_C"] > IN.JUMP_FROM_C + 15.0) else "failed",
                   "far_jump": fj, "above_197.3_K": (fj["T_C"] - IN.JUMP_FROM_C) if fj else None}
    else:
        P["P4"] = {"verdict": "failed", "why": "no bracket"}
        P["P5"] = {"verdict": "failed", "why": "no bracket"}
    # P6
    b3 = S["B3"]
    if b3["status"] == "matched":
        p = b3["result"]["P_W"]
        P["P6"] = {"verdict": "held" if 5.0 <= p <= 25.0 else "failed", **b3["result"], "status": "matched"}
    elif b3["status"] == "bracketed":
        a, b = b3["result"]["P_lo_W"], b3["result"]["P_hi_W"]
        P["P6"] = {"verdict": "held" if (5.0 <= a <= 25.0 and 5.0 <= b <= 25.0) else "failed", **b3["result"],
                   "status": "bracketed"}
    else:
        P["P6"] = {"verdict": "failed", "status": b3["status"]}
    # P7
    b4 = S["B4"]
    five = list(b4["draws"].values()) + [b4["aged"]]
    any_c8 = any(PB.c8(r) for r in five)
    sh = b4["shift"] or {}
    least = sh.get("least_shift_K")
    P["P7"] = {"verdict": "held" if (not any_c8 and least is not None and least >= 10.0) else "failed",
               "C8_in_the_five": {r["id"]: r["resolved"]["C8"] for r in five if r},
               "least_shift_K": least, "shift": sh}
    # P8
    r8 = S["B2"][0.05]
    P["P8"] = {"verdict": "held" if PB.c8(r8) else "failed", "t_C8_s": r8["resolved"]["t_C8_s"] if r8 else None}
    held = sum(1 for v in P.values() if v["verdict"] == "held")
    failed = sum(1 for v in P.values() if v["verdict"] == "failed")
    return {"predictions": P, "held": held, "failed": failed, "dropped": sum(1 for v in P.values()
                                                                             if v["verdict"] == "dropped")}


# ------------------------------------------------------------------------------------------------ V2 and V4
def _source_pulse(s):
    import stage15_model as M15
    if s.get("shape") == "hold":
        return M15.Hold(s["P_W"], s["t0_s"], s["t0_s"] + s["tau_s"])
    if s.get("shape") == "constant":
        return M15.Constant(s["E_J"], s["tau_s"], s["t0_s"])
    return M15.Triangular(s["E_J"], s["tau_s"], s["t0_s"])


def v2(recs):
    """Every record's energy accounts (resolved and lumped) within 1e-9 of the heat taken in, and every delivery
    its pulse's integral to the run's end, the stop at C8 included (1e-9 relative)."""
    worst_r = worst_l = worst_d = 0.0
    bad = []
    for r in recs.values():
        if r.get("failed"):
            bad.append((r["id"], "failed"))
            continue
        er, el = abs(r["resolved"]["energy_residual_rel"]), abs(r["lumped"]["energy_residual_rel"] or 0.0)
        worst_r, worst_l = max(worst_r, er), max(worst_l, el)
        if er > 1e-9 or el > 1e-9:
            bad.append((r["id"], "residual", er, el))
        for part, t_end in (("resolved", r["resolved"]["t_end_s"]), ("lumped", r["lumped"]["t_end_s"])):
            for name, s in r[part]["sources"].items():
                want = _source_pulse(s).cumulative(t_end)
                dd = abs(s["delivered_J"] - want) / max(1.0, abs(want))
                worst_d = max(worst_d, dd)
                if dd > 1e-9:
                    bad.append((r["id"], part, name, s["delivered_J"], want))
    return {"runs": len(recs), "worst_resolved": worst_r, "worst_lumped": worst_l, "worst_delivery": worst_d,
            "failures": bad, "passed": not bad}


def v4(recs, S):
    br = S["B1"]["M50_PT_Exp4"]["bracket"]
    if not br:
        return {"passed": False, "why": "no bracket"}
    out = {}
    ok = True
    for side in ("lo_id", "hi_id"):
        base = recs[br[side]]["resolved"]
        for suf in ("_r1.5", "_dt0.5"):
            r = recs.get(br[side] + suf)
            if r is None:
                out[br[side] + suf] = "missing"
                ok = False
                continue
            rr = r["resolved"]
            same = rr["C8"] == base["C8"]
            dt = (abs(rr["t_C8_s"] - base["t_C8_s"]) / base["t_C8_s"]) if (rr["C8"] and base["C8"]) else None
            okk = same and (dt is None or dt < 0.05)
            ok = ok and okk
            out[br[side] + suf] = {"C8_base": base["C8"], "C8": rr["C8"], "t_base_s": base["t_C8_s"],
                                   "t_s": rr["t_C8_s"], "rel_change": dt, "mean_peak_base_C": base["peak_mean_C"],
                                   "mean_peak_C": rr["peak_mean_C"], "passed": okk}
    out["passed"] = ok
    return out


# ------------------------------------------------------------------------------------------------ Part C
def _stage14_bounds():
    """Stage 14's corrected upper bounds by path and window (branch stage14 at 026b9c0), snapshot in results/."""
    path = os.path.join(RES, "stage15_stage14_bounds.csv")
    if not os.path.exists(path):
        text = subprocess.check_output(["git", "-C", IN.ROOT, "show", f"{STAGE14[0]}:{STAGE14[1]}"]).decode()
        with open(path, "w") as fh:
            fh.write(text)
    out = {}
    for r in csv.DictReader(open(path)):
        if r["determinable"] != "yes":
            continue
        out[r["path"]] = {"name": r["path_name"], 21.38651984299561: _f(r["upper_within_21.39s_J"]),
                          120.0: _f(r["upper_within_120.0s_J"]), 240.0: _f(r["upper_within_240.0s_J"]),
                          360.0: _f(r["upper_within_360.0s_J"]), "total": _f(r["upper_total_J"])}
    return out


def _reach(E, tau, bounds, connection):
    """Stage 14's paths whose corrected upper bound within the delivery's duration reaches E (A6, the neighbour's
    own discharge, only in the parallel tests)."""
    if E is None:
        return None
    out = []
    for p, b in sorted(bounds.items()):
        if p == "A6" and connection != "parallel":
            continue
        ub = b.get(tau)
        if ub is not None and ub >= E:
            out.append(p)
    return out


def _s9_record_time(test, tau, f, criterion):
    import glob
    pre = "tri21" if tau < 30 else f"con{int(tau)}"
    hits = glob.glob(os.path.join(RES, "stage9_runs", f"s9_{pre}_fresh_*_{test}_f{f:.9f}.json"))
    for h in hits:
        d = json.load(open(h))
        p = d.get("lumped") if criterion == "C2" else d.get("resolved")
        if p:
            t = p.get("t_prop_s")
            if t is None:
                t = (p.get("cross_s") or {}).get("T_onset_low")
            return t
    return None


def c1_table(xs, recs, S):
    s9 = {r["test"]: r for r in csv.DictReader(open(os.path.join(RES, "stage9_fractions.csv")))}
    s9l = {(r["test"], float(r["tau_s"])): r for r in csv.DictReader(open(os.path.join(RES, "stage9_long.csv")))}
    s12 = json.load(open(os.path.join(RES, "stage12_paper_numbers.json")))["B2"]
    a2 = {(r["test"], r["shape"], r["tau_s"]): r for r in xs["A2"]}
    ft = {(r["test"], r["shape"], r["tau_s"]): r for r in xs.get("A2_at_measured", [])}
    bounds = _stage14_bounds()
    T = IN.tests()
    rows = []
    for t in IN.propagated():
        E_e = IN.e_e(t)
        tm = float(T[t]["time_s"])
        conn = T[t]["connection"]
        for shape, tau in [("tri", IN.TAU_TRIGGER)] + [("con", x) for x in IN.TAUS_LONG]:
            row = {"test": t, "connection": conn, "delivery": "21.39 s pulse" if shape == "tri" else f"{tau:g} s power",
                   "tau_s": tau, "t_measured_s": tm}
            # the whole-cell clock (C2)
            if shape == "tri":
                b = s12[t]
                row["C2_status"] = b["status"]
                if b["status"] == "matched":
                    row["C2_E_J"], row["C2_t_s"] = b["E_t_J"], b["t_run_s"]
                else:
                    row["C2_E_J"] = 1e3 * b["E_bracket_kJ"][1]
                    row["C2_t_s"] = float(s9[t]["ft_C2_t_hi_s"]) if s9[t]["ft_C2_t_hi_s"] else None
                    row["C2_note"] = "the threshold bracket's upper end; no energy gives the time"
            else:
                r = s9l[(t, tau)]
                row["C2_status"] = r["ft_C2_status"]
                f = _f(r["ft_C2"]) if r["ft_C2_status"] in ("matched", "bracketed") else _f(r["ft_C2_hi"])
                row["C2_E_J"] = f * E_e if f is not None else None
                row["C2_t_s"] = (tm if r["ft_C2_status"] == "bracketed" else
                                 (_s9_record_time(t, tau, f, "C2") if f is not None else None))
            # the hot spot (C1)
            r = s9[t] if shape == "tri" else s9l[(t, tau)]
            row["C1_status"] = r["ft_C1_status"]
            if r["ft_C1_status"] in ("matched", "bracketed"):
                f = _f(r["ft_C1"])
            elif r["ft_C1_status"] == "threshold":
                f = _f(r["ft_C1_hi"])
            elif r["ft_C1_status"] == "early":
                f = 0.0
            else:
                f = None
            row["C1_E_J"] = f * E_e if f is not None else None
            row["C1_t_s"] = (tm if r["ft_C1_status"] == "bracketed" else
                             (_s9_record_time(t, tau, f, "C1") if (f is not None and f > 0) else None))
            # the cell's own runaway (C8): the three-dimensional runs where Part B made them, the cross-section
            e8 = a2.get((t, shape, tau))
            row["C8_xs_E_star_J"] = e8["E_star_J"] if e8 else None
            m8 = ft.get((t, shape, tau))
            if m8:
                row["C8_xs_at_tm_status"] = m8["status"]
                row["C8_xs_at_tm_E_J"] = m8.get("E_J")
                row["C8_xs_at_tm_t_s"] = m8.get("t_C8_s") if m8["status"] == "matched" else (
                    tm if m8["status"] == "bracketed" else m8.get("t_hi_s"))
            if shape == "tri" and t in S["B1"] and S["B1"][t]["bracket"]:
                br = S["B1"][t]["bracket"]
                row["C8_3d_E_star_J"] = br["mid_J"]
                row["C8_3d_bracket_J"] = f"({br['lo_J']:.0f}, {br['hi_J']:.0f}]"
                row["C8_3d_t_at_hi_s"] = recs[br["hi_id"]]["resolved"]["t_C8_s"]
            for k in ("C2_E_J", "C1_E_J", "C8_xs_E_star_J", "C8_xs_at_tm_E_J", "C8_3d_E_star_J"):
                v = row.get(k)
                row[k.replace("_J", "_share_of_76.74kJ")] = (v / E_FIX) if v is not None else None
                row[k.replace("_J", "_stage14_paths")] = (" ".join(_reach(v, tau, bounds, conn))
                                                         if v is not None else None)
            rows.append(row)
    return rows


def c2_table(xs):
    """With no delivery: C1 and C2 from Stage 7's per-test runs at the low, central and high contacts; C8 from the
    archive's continued runs where they exist, else impossible where the hot spot never reached the level (the mean
    cannot exceed the hottest node), else the cross-section's."""
    import glob
    arch = [r for r in AR.table() if r["shape"] == "none" and r["group"] in ("central", "contact variant")]
    xs_runs = {}
    for c in xs.get("C2", []):
        p = os.path.join(RES, "stage15_xs", c["key"] + ".json")
        if os.path.exists(p):
            xs_runs[(c["test"], c["h"])] = json.load(open(p))
    rows = []
    for t in IN.TEST_ORDER:
        for h in ("low", "central", "high"):
            fn = glob.glob(os.path.join(RES, "stage7_runs", f"pertest_{t}_*_h{h}_gcentral_*.json"))
            d = json.load(open(fn[0])) if fn else None
            r7, l7 = (d["resolved"], d["lumped"]) if d else ({}, {})
            row = {"test": t, "h": h, "propagated_measured": IN.tests()[t]["propagated"],
                   "C1": r7.get("propagated"), "C1_t_s": r7.get("t_prop_s"), "C2": l7.get("propagated"),
                   "C2_t_s": l7.get("t_prop_s")}
            a = [r for r in arch if r["test"] == t and (r["h"] or "central") == h and r["thermal"] in (None, "central")
                 and r["t_end_s"] >= 899.9]
            x = xs_runs.get((t, h))
            row["C8_xs"] = x["C8"] if x else None
            row["C8_xs_t_s"] = x["t_c8_s"] if x else None
            row["mean_peak_xs_C"] = x["peak_mean_C"] if x else None
            if a:
                row["C8"] = a[0]["mean_t_cross_s"] is not None
                row["C8_source"] = "archive " + a[0]["id"]
                row["mean_peak_3d_C"] = a[0]["mean_peak_C"]
            elif d and not r7.get("propagated") and r7.get("t_end_s", 0) >= 899.9:
                row["C8"] = False
                row["C8_source"] = "no C1 by 900 s (Stage 7), so no C8"
                row["mean_peak_3d_C"] = r7.get("peak_mean_C")
            else:
                row["C8"] = row["C8_xs"]
                row["C8_source"] = "cross-section"
            rows.append(row)
    return rows


def write_csv(rows, name):
    keys = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with open(os.path.join(RES, name), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in keys})


def main():
    xs = json.load(open(os.path.join(RES, "stage15_cross_section.json")))
    recs = PB.load()
    S = states(recs)
    sc = scorecard(xs, recs, S)
    checks = {"V2": v2(recs), "V4": v4(recs, S),
              "V1": json.load(open(os.path.join(RES, "stage15_v1.json")))}
    br = S["B1"]["M50_PT_Exp4"]["bracket"]
    hist = history_score(recs[br["hi_id"]]) if br else None
    b3r = S["B3"]["result"]
    hist_hold = history_score(recs[b3r.get("id") or b3r.get("id_hi")]) if b3r else None
    c1 = c1_table(xs, recs, S)
    c2 = c2_table(xs)
    write_csv(c1, "stage15_table.csv")
    write_csv(c2, "stage15_nodelivery.csv")
    json.dump({"scorecard": sc, "states": {k: v for k, v in S.items() if k != "B2" and k != "B4"},
               "B3a_history": hist, "B3b_history": hist_hold},
              open(os.path.join(RES, "stage15_scorecard.json"), "w"), indent=1, default=str)
    json.dump(checks, open(os.path.join(RES, "stage15_checks.json"), "w"), indent=1, default=str)
    print({k: v["verdict"] for k, v in sc["predictions"].items()}, "held", sc["held"], "failed", sc["failed"])
    print("V2", checks["V2"]["passed"], "V4", checks["V4"].get("passed"))


if __name__ == "__main__":
    main()
