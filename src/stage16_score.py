"""Step 16: the results of the searches N, T, V and X, the scoring of P1 to P11 by the rules registered in
predictions_stage16.md, and the check V2 (DECISIONS.md D190 and after).

Every bracket is read from the run records by the registered rules themselves (`stage16_run.need_state`, `t_state`,
`v_state`, unchanged since the registration); `src/stage16_recheck.py` recomputes them by separate code.

Writes results/stage16_needs.csv (one row per need searched, with the cross-section's and the lumped needs beside it),
results/stage16_runs.csv (every Step 16 run), results/stage16_scorecard.json, results/stage16_checks.json and
results/stage16_paper_numbers.json.

Run: python3 src/stage16_score.py
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage15_inputs as IN              # noqa: E402
import stage15_partb as PB               # noqa: E402
import stage16_run as S                  # noqa: E402

RES = IN.RES
LUMPED_T = (12848.834034982421, 12892.389404592532)     # PT-Exp1's lumped bracket (predictions_stage16.md)
LUMPED_T_MID = 0.5 * (LUMPED_T[0] + LUMPED_T[1])


def lumped_need(test, label):
    for r in S._table15():
        if r["test"] == test and r["delivery"] == label:
            return {"E_by_t_J": float(r["C2_E_by_t_J"]), "E_J": float(r["C2_E_J"]), "status": r["C2_status"],
                    "t_s": float(r["C2_t_s"]) if r["C2_t_s"] else None}
    raise KeyError((test, label))


def xs_row(test, label):
    for r in S._table15():
        if r["test"] == test and r["delivery"] == label:
            return r
    raise KeyError((test, label))


def need_row(test, shape, tau, recs, kind, recs15, a1):
    label = S.DELIVERY["tri"] if shape == "tri" else S.DELIVERY[float(tau)]
    st, sp, res = S.need_state(test, shape, tau, recs, kind, recs15, a1)
    t_m = S.t_measured(test)
    share = S.share_by(shape, tau, t_m + S.WINDOW_S)
    xr = xs_row(test, label)
    L = lumped_need(test, label)
    E_x = float(xr["C8_xs_E_J"])
    E_x_by_t = float(xr["C8_xs_E_by_t_J"])
    row = {"test": test, "delivery": label, "search": kind, "status": st, "t_m_s": t_m, "E_e_J": IN.e_e(test),
           "E_b_J": IN.e_e(test) / 3.105, "share_by_t_m_plus_10": share,
           "xs_E_J": E_x, "xs_E_by_t_J": E_x_by_t, "xs_status": xr["C8_xs_status"],
           "xs_t_C8_s": float(xr["C8_xs_t_s"]) if xr["C8_xs_t_s"] else None,
           "lumped_E_by_t_J": L["E_by_t_J"], "lumped_E_J": L["E_J"], "lumped_status": L["status"],
           "lumped_t_s": L["t_s"]}
    runs = S.existing_runs(test, shape, tau, recs, recs15, a1)
    row["n_runs_counted"] = len(runs)
    row["n_runs_step16"] = sum(1 for x in runs if x[3] == "stage16")
    row["runs"] = [{"E_J": E, "t_C8_s": t, "t_end_s": te, "source": src, "id": rid,
                    "class": S.classify(t, te, t_m)} for E, t, te, src, rid in sorted(runs)]
    if st == "done":
        lo, hi = res["lo"], res["hi"]
        mid = 0.5 * (lo[0] + hi[0])
        row.update({"lo_J": lo[0], "lo_id": lo[4], "lo_t_C8_s": lo[2], "lo_source": lo[3],
                    "hi_J": hi[0], "hi_id": hi[4], "hi_t_C8_s": hi[2], "hi_source": hi[3],
                    "width_J": hi[0] - lo[0], "mid_J": mid,
                    "lo_by_t_J": lo[0] * share, "hi_by_t_J": hi[0] * share, "mid_by_t_J": mid * share,
                    "d": (E_x_by_t - mid * share) / (mid * share),
                    "lo_minus_lumped_J": lo[0] * share - L["E_by_t_J"],
                    "hi_minus_lumped_J": hi[0] * share - L["E_by_t_J"],
                    "lo_runs_away": lo[2] is not None,
                    "at_threshold": lo[2] is None})
    return row


def t_result(recs):
    st, _, br = S.t_state(recs)
    out = {"test": S.WEAK2, "status": st, "xs_threshold_J": S.xs_threshold(S.WEAK2),
           "lumped_bracket_J": list(LUMPED_T), "lumped_mid_J": LUMPED_T_MID,
           "runs": sorted([{"id": r["id"], "E_J": r["E_delivered_J"], "C8": r["resolved"]["C8"],
                            "t_C8_s": r["resolved"]["t_C8_s"], "peak_mean_C": r["resolved"]["peak_mean_C"],
                            "lumped_C2": r["lumped"].get("propagated"), "lumped_t_C2_s": r["lumped"].get("t_prop_s"),
                            "lumped_peak_C": r["lumped"].get("peak_C"),
                            "wall_s": r.get("wall_s")}
                           for r in recs.values() if r.get("kind") == "T" and not r.get("failed")],
                          key=lambda x: x["E_J"])}
    if st == "done":
        mid = 0.5 * (br["lo_J"] + br["hi_J"])
        out.update(br)
        out.update({"mid_J": mid, "ratio_mid": mid / LUMPED_T_MID,
                    "ratio_lo": br["lo_J"] / LUMPED_T[1], "ratio_hi": br["hi_J"] / LUMPED_T[0],
                    "xs_in_bracket": br["lo_J"] < S.xs_threshold(S.WEAK2) <= br["hi_J"],
                    "closed_by_first_two": (br["lo_step"], br["hi_step"]) == (-1, 1)})
    return out


def v_result(recs, nres):
    st, pend, out = S.v_state(recs, nres)
    out = out or {}
    out["status"] = st
    if not out.get("refined"):
        return out
    base = out["base"]
    lo, hi = base["lo"][0], base["hi"][0]
    w = hi - lo
    ref = dict(out["refined"])
    for side, v in (out.get("extra") or {}).items():
        ref["extra_" + side] = v
    early = sorted(v["E_J"] for v in ref.values() if v["class"] == "early")
    late = sorted(v["E_J"] for v in ref.values() if v["class"] == "late")
    rlo = late[-1] if late else None
    rhi = early[0] if early else None
    closed = rlo is not None and rhi is not None and rlo < rhi
    out["refined_bracket_J"] = [rlo, rhi] if closed else None
    out["base_bracket_J"] = [lo, hi]
    out["width_J"] = w
    out["within_one_width"] = bool(closed and rlo >= lo - w - 1e-6 and rhi <= hi + w + 1e-6)
    out["shift_J"] = (0.5 * (rlo + rhi) - 0.5 * (lo + hi)) if closed else None
    out["shift_rel"] = (out["shift_J"] / (0.5 * (lo + hi))) if closed else None
    rel = {}
    for side in ("lo", "hi"):
        b = base[side]
        r = out["refined"][side]
        if b[2] is not None and r["C8"]:
            rel[side] = {"base_t_C8_s": b[2], "refined_t_C8_s": r["t_C8_s"], "dt_s": r["t_C8_s"] - b[2],
                         "rel": (r["t_C8_s"] - b[2]) / b[2]}
        else:
            rel[side] = {"base_t_C8_s": b[2], "refined_t_C8_s": r["t_C8_s"] if r["C8"] else None, "rel": None,
                         "one_mesh_only": (b[2] is None) != (not r["C8"])}
    out["C8_change"] = rel
    return out


def scorecard(nrows, trow, v, xrows):
    P = {}
    done = [r for r in nrows if r["status"] == "done"]
    alln = len(done) == len(S.STRONG8)

    def each(cond):
        per = {r["test"]: (bool(cond(r)) if r["status"] == "done" else False) for r in nrows}
        return per, all(per.values()) and alln

    per, ok = each(lambda r: abs(r["d"]) <= 0.10)
    P["P1"] = {"held": ok, "per_test": per, "d": {r["test"]: r.get("d") for r in nrows}}
    per, ok = each(lambda r: r["xs_E_by_t_J"] > r["mid_by_t_J"])
    P["P2"] = {"held": ok, "per_test": per}
    per, ok = each(lambda r: r["lo_by_t_J"] >= 4050.0 and r["hi_by_t_J"] <= 8150.0)
    P["P3"] = {"held": ok, "per_test": per,
               "range_J": [min(r["lo_by_t_J"] for r in done), max(r["hi_by_t_J"] for r in done)] if done else None}
    per, ok = each(lambda r: r["lo_by_t_J"] >= r["lumped_E_by_t_J"] - 0.05 - 1e-6)
    P["P4"] = {"held": ok, "per_test": per}
    per, ok = each(lambda r: r["lo_minus_lumped_J"] >= 1000.0 and r["hi_minus_lumped_J"] <= 5000.0)
    P["P5"] = {"held": ok, "per_test": per,
               "diff_J": {r["test"]: [r.get("lo_minus_lumped_J"), r.get("hi_minus_lumped_J")] for r in nrows}}
    if trow["status"] == "done":
        P["P6"] = {"held": trow["hi_J"] <= LUMPED_T[0], "hi_J": trow["hi_J"], "lumped_lo_J": LUMPED_T[0]}
        P["P7"] = {"held": 0.75 <= trow["ratio_mid"] <= 0.95, "ratio_mid": trow["ratio_mid"]}
    else:
        P["P6"] = {"held": False, "why": "T ended " + trow["status"]}
        P["P7"] = {"held": False, "why": "T ended " + trow["status"]}
    if v.get("refined"):
        P["P8"] = {"held": v["within_one_width"], "test": v["test"], "base_bracket_J": v["base_bracket_J"],
                   "refined_bracket_J": v["refined_bracket_J"]}
        ch = v["C8_change"]
        oks = []
        for side in ("lo", "hi"):
            c = ch[side]
            if c.get("rel") is not None:
                oks.append(abs(c["rel"]) < 0.03)
            elif c.get("one_mesh_only"):
                oks.append(False)
        P["P9"] = {"held": bool(oks) and all(oks), "C8_change": ch}
    else:
        P["P8"] = {"held": False, "why": "V ended " + v.get("status", "?")}
        P["P9"] = {"held": False, "why": "V ended " + v.get("status", "?")}
    closed = [r for r in xrows if r["status"] == "done"]
    if closed:
        per = {(r["test"], r["delivery"]): abs(r["d"]) <= 0.10 for r in closed}
        P["P10"] = {"held": all(per.values()), "per_search": {f"{k[0]} {k[1]}": v_ for k, v_ in per.items()},
                    "d": {f"{r['test']} {r['delivery']}": r["d"] for r in closed}}
        per = {(r["test"], r["delivery"]): r["lo_by_t_J"] >= r["lumped_E_by_t_J"] - 0.05 - 1e-6 for r in closed}
        P["P11"] = {"held": all(per.values()), "per_search": {f"{k[0]} {k[1]}": v_ for k, v_ in per.items()}}
    else:
        P["P10"] = {"held": None, "why": "X closed no search: not scored"}
        P["P11"] = {"held": None, "why": "X closed no search: not scored"}
    scored = [k for k, v_ in P.items() if v_["held"] is not None]
    return {"predictions": P, "scored": len(scored), "held": sum(1 for k in scored if P[k]["held"]),
            "failed": sum(1 for k in scored if not P[k]["held"])}


# ------------------------------------------------------------------------------------------------ V2
def _pulses_of(rec):
    import stage15_model as M15
    out = {}
    for j, d in enumerate(rec["deliveries"]):
        nm = "delivery" if j == 0 else f"delivery{j + 1}"
        if d["shape"] == "tri":
            out[nm] = M15.Triangular(d["E_J"], d["tau_s"], d.get("t0_s", 0.0))
        else:
            out[nm] = M15.Constant(d["E_J"], d["tau_s"], d.get("t0_s", 0.0))
    return out


def v2(recs):
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


def write_csv(rows, path, skip=("runs",)):
    keys = []
    for r in rows:
        for k in r:
            if k not in keys and k not in skip:
                keys.append(k)
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in keys})


def run_rows(recs):
    out = []
    for r in sorted(recs.values(), key=lambda x: (x.get("kind", ""), x.get("test", ""), x.get("id"))):
        p, l = r.get("resolved", {}), r.get("lumped", {})
        d = r["deliveries"][0]
        out.append({"id": r["id"], "kind": r.get("kind"), "search": r.get("search"), "test": r["test"],
                    "shape": d["shape"], "tau_s": d["tau_s"], "f": d["f"], "E_J": r.get("E_delivered_J"),
                    "refine": r.get("refine", 1.0), "dt_scale": r.get("dt_scale", 1.0), "failed": r.get("failed", False),
                    "C8": p.get("C8"), "t_C8_s": p.get("t_C8_s"), "t_end_s": p.get("t_end_s"),
                    "peak_mean_C": p.get("peak_mean_C"), "peak_hottest_C": p.get("peak_hottest_C"),
                    "in_rxn_J": p.get("in_rxn_J"), "energy_residual_rel": p.get("energy_residual_rel"),
                    "lumped_C2": l.get("propagated"), "lumped_t_C2_s": l.get("t_prop_s"), "lumped_peak_C": l.get("peak_C"),
                    "lumped_energy_residual_rel": l.get("energy_residual_rel"),
                    "wall_s": r.get("wall_s"), "started_utc": r.get("started_utc"),
                    "finished_utc": r.get("finished_utc"), "worker": r.get("worker")})
    return out


def main():
    recs = S.load()
    recs15 = PB.load()
    a1 = json.load(open(S.XS_OUT))["A1_rows"]
    nrows = [need_row(t, "tri", None, recs, "N", recs15, a1) for t in S.STRONG8]
    xrows = []
    for tau in S.X_SHAPES:
        for t in S.STRONG8:
            r = need_row(t, "con", tau, recs, "X", recs15, a1)
            if r["status"] == "running" and r["n_runs_step16"] == 0:
                r["status"] = "not started"
            elif r["status"] == "running":
                r["status"] = "unfinished"
            xrows.append(r)
    trow = t_result(recs)
    nres = S.n_all(recs, recs15, a1)
    v = v_result(recs, nres)
    sc = scorecard(nrows, trow, v, xrows)
    checks = {"V2": v2(recs)}
    write_csv(nrows + xrows, os.path.join(RES, "stage16_needs.csv"))
    write_csv(run_rows(recs), os.path.join(RES, "stage16_runs.csv"))
    out = {"N": nrows, "X": xrows, "T": trow, "V": v, "scorecard": sc,
           "X_worker_hours": S.x_worker_hours(recs), "n_records": len(recs),
           "wall_s": {k: [min(r.get("wall_s", 0) for r in recs.values() if r.get("kind") == k),
                          max(r.get("wall_s", 0) for r in recs.values() if r.get("kind") == k)]
                      for k in ("N", "T", "V", "X") if any(r.get("kind") == k for r in recs.values())},
           "first_utc": min((r.get("started_utc") for r in recs.values()), default=None),
           "last_utc": max((r.get("finished_utc") for r in recs.values()), default=None)}
    json.dump(out, open(os.path.join(RES, "stage16_scorecard.json"), "w"), indent=1, default=float)
    json.dump(checks, open(os.path.join(RES, "stage16_checks.json"), "w"), indent=1, default=float)
    print("records", len(recs), "X worker-hours %.2f" % out["X_worker_hours"])
    for r in nrows:
        if r["status"] == "done":
            print("N %-12s (%7.1f, %7.1f] C8 %s/%s  E_x %7.1f d %+.1f%%  lumped %7.1f  diff %.0f..%.0f  runs %d new"
                  % (r["test"][4:], r["lo_J"], r["hi_J"], _t(r["lo_t_C8_s"]), _t(r["hi_t_C8_s"]), r["xs_E_J"],
                     100 * r["d"], r["lumped_E_by_t_J"], r["lo_minus_lumped_J"], r["hi_minus_lumped_J"],
                     r["n_runs_step16"]))
        else:
            print("N %-12s %s (%d new runs)" % (r["test"][4:], r["status"], r["n_runs_step16"]))
    print("T", {k: trow.get(k) for k in ("status", "lo_J", "hi_J", "ratio_mid", "ratio_lo", "ratio_hi")})
    print("V", {k: v.get(k) for k in ("status", "test", "base_bracket_J", "refined_bracket_J", "C8_change")})
    for r in xrows:
        if r["status"] == "done":
            print("X %-12s %-22s (%7.1f, %7.1f] by_t (%7.1f, %7.1f] E_x_by_t %7.1f d %+.1f%% lumped %7.1f"
                  % (r["test"][4:], r["delivery"], r["lo_J"], r["hi_J"], r["lo_by_t_J"], r["hi_by_t_J"],
                     r["xs_E_by_t_J"], 100 * r["d"], r["lumped_E_by_t_J"]))
        elif r["status"] != "not started":
            print("X %-12s %-22s %s" % (r["test"][4:], r["delivery"], r["status"]))
    for k, p in sc["predictions"].items():
        print(k, p["held"])
    print("V2", checks["V2"]["passed"], checks["V2"]["worst_resolved"], checks["V2"]["worst_lumped"],
          checks["V2"]["worst_delivery"])


def _t(x):
    return "%.1f" % x if x is not None else "none"


if __name__ == "__main__":
    main()
