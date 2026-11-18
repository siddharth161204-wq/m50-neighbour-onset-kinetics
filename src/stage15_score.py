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
def _pulses_of(rec):
    """Each source of a record by its name, built from the record's deliveries as `stage15_run.run_one` built it."""
    import stage15_model as M15
    out = {}
    for j, d in enumerate(rec["deliveries"]):
        nm = "delivery" if j == 0 else f"delivery{j + 1}"
        if d["shape"] == "tri":
            out[nm] = M15.Triangular(d["E_J"], d["tau_s"], d.get("t0_s", 0.0))
        elif d["shape"] == "con":
            out[nm] = M15.Constant(d["E_J"], d["tau_s"], d.get("t0_s", 0.0))
        else:
            out[nm] = M15.Hold(d["P_W"], d["t0_s"], max(rec["t_end_s"], IN.T_END))
    return out


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
        pulses = _pulses_of(r)
        for part, t_end in (("resolved", r["resolved"]["t_end_s"]), ("lumped", r["lumped"]["t_end_s"])):
            for name, s in r[part]["sources"].items():
                want = pulses[name].cumulative(t_end)
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


_IDX = None


def _archive_index():
    """Every archived run of Stages 9, 10 and 12 at the posterior-mean kinetics, the central properties and contact and
    the fresh SEI, by (test, shape, duration, delivered energy to the joule): the hot spot's crossing time (C1, from the
    resolved neighbour) and the lumped neighbour's (C2), where the record has that neighbour."""
    global _IDX
    if _IDX is None:
        import glob
        _IDX = {}
        for st in ("stage9_runs", "stage10_runs", "stage12_runs"):
            for p in sorted(glob.glob(os.path.join(RES, st, "*.json"))):
                d = json.load(open(p))
                if (d.get("kin") != "mean" or d.get("sei") != "fresh" or (d.get("h") or "central") != "central"
                        or d.get("thermal") not in (None, "central") or d.get("shape") not in ("tri", "con")):
                    continue
                k = (d["test"], d["shape"], round(float(d["tau_d_s"]), 2), round(float(d["E_delivered_J"])))
                e = _IDX.setdefault(k, {})
                for crit, part in (("C1", "resolved"), ("C2", "lumped")):
                    q = d.get(part)
                    if not q:
                        continue
                    t = q.get("t_prop_s")
                    if t is None:
                        t = (q.get("cross_s") or {}).get("T_onset_low")
                    e.setdefault(crit, {"t_s": t, "id": d["id"]})
    return _IDX


def _time_at(test, shape, tau, E, crit):
    """The archived crossing time of crit at delivered energy E (None where no record holds it, or it does not cross)."""
    if E is None:
        return None, None
    e = _archive_index().get((test, shape, round(float(tau), 2), round(float(E))), {}).get(crit)
    return (e["t_s"], e["id"]) if e else (None, None)


def _by_t(shape, tau, E, t):
    """The energy a delivery of E over tau has given by time t (all of it once it has ended)."""
    import stage15_model as M15
    if E is None or t is None:
        return None
    p = M15.Triangular(E, tau, 0.0) if shape == "tri" else M15.Constant(E, tau, 0.0)
    return float(p.cumulative(min(t, tau)))


def _entry(test, shape, tau, tm, E_e, status, f, lo, hi, crit, t_run=None, E_run=None):
    """One criterion's entry in C1's table, from Stage 9's (or Stage 12's) reading at the measured time: the energy it
    needs, the time it gives, and the energy delivered by then."""
    out = {"status": status}
    if status in ("matched", "bracketed"):
        E = E_run if E_run is not None else f * E_e
        if status == "matched":
            t = t_run if t_run is not None else _time_at(test, shape, tau, E, crit)[0]
        else:
            t = tm                                   # linear between the bracket's ends, by the reading's rule
        out.update({"E_J": E, "t_s": t})
    elif status == "threshold":
        E = hi * E_e
        out.update({"E_J": E, "t_s": t_run if t_run is not None else _time_at(test, shape, tau, E, crit)[0],
                    "note": "the threshold: the bracket's upper end, the least energy the reading ran whose crossing "
                            "comes before the measured time; its lower end gives no crossing"})
    elif status == "early":
        out.update({"E_J": 0.0, "t_s": None, "note": "it comes before the measured time with no delivery"})
    else:
        out.update({"E_J": None, "t_s": None})
    out["E_by_t_J"] = _by_t(shape, tau, out.get("E_J"), out.get("t_s")) if out.get("E_J") else out.get("E_J")
    return out


def c1_table(xs, recs, S):
    """C1 (brief): for the nine propagated tests and each delivery, the delivered energy each criterion needs to give
    the measured time t_m, the time it gives, the energy delivered by then, the energy's share of 76.74 kJ and the
    paths of Stage 14 whose corrected upper bound within the delivery's duration reaches it. The whole-cell clock
    (C2) and the hot spot (C1) from the archive's readings (Stage 12's for C2 with the 21.39 s pulse, Stage 9's
    otherwise); the cell's own runaway (C8) from the reactive cross-section (Part A) and, where Part B made them, the
    three-dimensional runs."""
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
            row = {"test": t, "connection": conn,
                   "delivery": "21.39 s pulse" if shape == "tri" else f"{tau:g} s constant power", "tau_s": tau,
                   "t_measured_s": tm}
            ent = {}
            # the whole-cell clock, C2
            if shape == "tri":
                b = s12[t]
                if b["status"] == "matched":
                    ent["C2"] = _entry(t, shape, tau, tm, E_e, "matched", None, None, None, "C2", t_run=b["t_run_s"],
                                       E_run=b["E_t_J"])
                elif b["status"] == "threshold":
                    hi_J = 1e3 * b["E_bracket_kJ"][1]
                    rid = [k for k in _archive_index() if k[0] == t and k[1] == "tri" and abs(k[3] - hi_J) <= 1.0]
                    tt = _archive_index()[rid[0]].get("C2", {}).get("t_s") if rid else None
                    ent["C2"] = _entry(t, shape, tau, tm, E_e, "threshold", None, None, hi_J / E_e, "C2", t_run=tt)
                else:
                    r9 = s9[t]
                    ent["C2"] = _entry(t, shape, tau, tm, E_e, r9["ft_C2_status"], _f(r9["ft_C2"]), _f(r9["ft_C2_lo"]),
                                       _f(r9["ft_C2_hi"]), "C2")
            else:
                r = s9l[(t, tau)]
                ent["C2"] = _entry(t, shape, tau, tm, E_e, r["ft_C2_status"], _f(r["ft_C2"]), _f(r["ft_C2_lo"]),
                                   _f(r["ft_C2_hi"]), "C2")
            # the hot spot, C1
            r = s9[t] if shape == "tri" else s9l[(t, tau)]
            tt = _f(r.get("ft_C1_t_hi_s")) if (shape == "tri" and r["ft_C1_status"] == "threshold") else None
            ent["C1"] = _entry(t, shape, tau, tm, E_e, r["ft_C1_status"], _f(r["ft_C1"]), _f(r["ft_C1_lo"]),
                               _f(r["ft_C1_hi"]), "C1", t_run=tt)
            # the cell's own runaway, C8, in the cross-section
            e8 = a2[(t, shape, tau)]
            m8 = ft[(t, shape, tau)]
            row["C8_xs_E_star_J"] = e8["E_star_J"]
            row["C8_xs_t_at_E_star_hi_s"] = m8["points"][0][1]
            if m8["status"] == "matched":
                ent["C8_xs"] = {"status": "matched", "E_J": m8["E_J"], "t_s": m8["t_C8_s"]}
            elif m8["status"] == "threshold":
                ent["C8_xs"] = {"status": "threshold", "E_J": m8["hi_f"] * E_e, "t_s": m8["t_hi_s"],
                                "note": "the measured time lies within the rule's resolution of the threshold"
                                if m8["points"][0][1] > tm else "C8 comes before the measured time at the threshold"}
            else:
                ent["C8_xs"] = {"status": m8["status"], "E_J": None, "t_s": None}
            ent["C8_xs"]["E_by_t_J"] = _by_t(shape, tau, ent["C8_xs"].get("E_J"), ent["C8_xs"].get("t_s"))
            # the three-dimensional cell's own runaway, where Part B made it
            if shape == "tri" and t in S["B1"] and S["B1"][t]["bracket"]:
                br = S["B1"][t]["bracket"]
                row["C8_3d_E_star_J"] = br["mid_J"]
                row["C8_3d_bracket_J"] = f"({br['lo_J']:.0f}, {br['hi_J']:.0f}]"
                row["C8_3d_t_at_bracket_hi_s"] = recs[br["hi_id"]]["resolved"]["t_C8_s"]
            if shape == "con" and tau == 240.0 and t == IN.HIST_TEST:
                for f in PB.B2_F:
                    r2 = recs.get(PB.b2_spec(f)["id"])
                    if r2 and not r2.get("failed"):
                        row[f"C8_3d_B2_{r2['E_delivered_J']:.0f}J_t_s"] = r2["resolved"]["t_C8_s"]
            for crit, e in ent.items():
                for k, v in e.items():
                    row[f"{crit}_{k}"] = v
                E = e.get("E_J")
                row[f"{crit}_share_of_76.74kJ"] = (E / E_FIX) if E is not None else None
                row[f"{crit}_stage14_paths"] = " ".join(_reach(E, tau, bounds, conn)) if E is not None else None
            least = min(b.get(tau) for p, b in bounds.items() if b.get(tau) is not None and
                        (p != "A6" or conn == "parallel"))
            row["stage14_least_bound_J"] = least
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


def _run_row(r):
    """The quantities of one record that the texts quote."""
    if r is None:
        return None
    if r.get("failed"):
        return {"id": r["id"], "failed": True, "error": r.get("error")}
    p, q = r["resolved"], r["lumped"]
    return {"id": r["id"], "E_J": r["E_delivered_J"], "C8": p["C8"], "t_C8_s": p["t_C8_s"],
            "peak_mean_C": p["peak_mean_C"], "t_peak_mean_s": p["t_peak_mean_s"], "mean_end_C": p["mean_end_C"],
            "t_end_s": p["t_end_s"], "C1_t_s": p["t_prop_s"], "peak_hottest_C": p["peak_hottest_C"],
            "rxn_J": p["in_rxn_J"], "t_rxn_11.3kJ_s": p["t_rxn_mark_s"], "far_jump": p["far_jump"],
            "far_at_45_C": p["far_at_45_C"], "far_at_271.5_C": p["far_at_271.5_C"],
            "far_peak": (p.get("probe_peak") or {}).get("away"),
            "lumped_C2_t_s": q["t_prop_s"], "lumped_peak_C": q["peak_C"], "lumped_rxn_J": q["reaction_heat_J"],
            "delivered_J": {k: v["delivered_J"] for k, v in p["sources"].items()},
            "wall_s": r.get("wall_s"), "started_utc": r.get("started_utc"), "worker": r.get("worker")}


def paper_numbers(xs, recs, S, sc, checks, hist, hist_hold):
    """Every Stage 15 number the texts quote, from the records (`results/stage15_paper_numbers.json`)."""
    out = {"registration": {"commit": "3f5e3b65906bd34de4f321476720f7528b8bfd42",
                            "pushed_utc": "2026-11-18T05:12:45Z", "list_sha256": PB.list_hash()[0],
                            "cross_section_sha256": IN.sha256_file(os.path.join(RES, "stage15_cross_section.json"))}}
    rs = list(recs.values())
    st = sorted(r["started_utc"] for r in rs if r.get("started_utc"))
    fi = sorted(r["finished_utc"] for r in rs if r.get("finished_utc"))
    kinds = {}
    for r in rs:
        kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
    out["runs"] = {"n": len(rs), "by_kind": kinds, "failed": [r["id"] for r in rs if r.get("failed")],
                   "first_start_utc": st[0] if st else None, "last_finish_utc": fi[-1] if fi else None,
                   "wall_s": {"total": sum(r.get("wall_s") or 0.0 for r in rs),
                              "min": min((r.get("wall_s") or 0.0) for r in rs) if rs else None,
                              "max": max((r.get("wall_s") or 0.0) for r in rs) if rs else None}}
    fp = xs["for_predictions"]
    b1 = {}
    for t in IN.B1_TESTS:
        chain = sorted((x for x in rs if x["kind"] == "B1" and x["test"] == t), key=lambda x: x["E_delivered_J"])
        br = S["B1"][t]["bracket"]
        e_xs = fp["B1"][t]["E_star_J"]
        c2 = PR.e_c2(t)["mid_J"]
        b1[t] = {"status": S["B1"][t]["status"], "runs": [_run_row(x) for x in chain], "bracket": br,
                 "E_star_xs_J": e_xs, "E_C2_J": c2,
                 "rel_diff_xs": ((e_xs - br["mid_J"]) / br["mid_J"]) if br else None,
                 "ratio_to_C2": (br["mid_J"] / c2) if (br and c2 > 0) else None}
    out["B1"] = b1
    br = S["B1"]["M50_PT_Exp4"]["bracket"]
    out["B3a"] = {"run": _run_row(recs[br["hi_id"]]) if br else None, "history": hist}
    b3runs = sorted((x for x in rs if x["kind"] == "B3"), key=lambda x: x["deliveries"][1]["P_W"])
    out["B3b"] = {"status": S["B3"]["status"], "result": S["B3"]["result"], "start_W": PB.b3_start(),
                  "runs": [dict(_run_row(x), P_W=x["deliveries"][1]["P_W"]) for x in b3runs],
                  "history": hist_hold}
    b4 = S["B4"]
    out["B4"] = {"draws": {str(k): _run_row(v) for k, v in b4["draws"].items()}, "aged": _run_row(b4["aged"]),
                 "shift": b4["shift"],
                 "shift_runs": [dict(_run_row(x), shift_K=x["shift_K"]) for x in
                                sorted((x for x in rs if x["kind"] == "B4" and x["shift_K"]),
                                       key=lambda x: x["shift_K"])]}
    out["B2"] = {str(f): _run_row(v) for f, v in S["B2"].items()}
    out["V2"] = {k: checks["V2"][k] for k in ("runs", "worst_resolved", "worst_lumped", "worst_delivery", "passed")}
    out["V4"] = checks["V4"]
    out["V4_runs"] = [_run_row(x) for x in rs if x["kind"] == "V4"]
    out["scorecard"] = {k: v["verdict"] for k, v in sc["predictions"].items()}
    out["held"], out["failed"] = sc["held"], sc["failed"]
    return out


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
    json.dump(paper_numbers(xs, recs, S, sc, checks, hist, hist_hold),
              open(os.path.join(RES, "stage15_paper_numbers.json"), "w"), indent=1, default=str)
    print({k: v["verdict"] for k, v in sc["predictions"].items()}, "held", sc["held"], "failed", sc["failed"])
    print("V2", checks["V2"]["passed"], "V4", checks["V4"].get("passed"))


if __name__ == "__main__":
    main()
