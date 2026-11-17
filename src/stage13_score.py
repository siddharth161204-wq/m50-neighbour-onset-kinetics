"""Stage 13 scoring: the brackets of every search, P1 to P10 against predictions_stage13.md, and the results tables
(DECISIONS.md D139 onward).

Writes results/stage13_skin.csv, stage13_twobody.csv, stage13_map.csv and stage13_scorecard.json; stage13_tign.csv
is stage13_tign.py's and stage13_conditioning.csv stage13_conditioning.py's.
"""
import csv
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage13_inputs as IN                # noqa: E402
import stage13_run as RN                   # noqa: E402

T21 = IN.TAU_TRIGGER
PT1 = "M50_PT_Exp1"
C2_REF21 = (0.4609375, 0.4625)              # the archive's refined f*(C2) of PT_Exp1 at 21.39 s (refA_c2)


def brackets():
    recs = RN.load_records()
    red = RN._reduced()
    out = {}
    for kind, lst in IN.run_lists().items():
        for s in lst:
            st, x, br, mine = RN.search_state(s, recs, red)
            lo, hi = (br if br else (None, None))
            out[s["name"]] = {"spec": s, "status": st, "lo": lo, "hi": hi,
                              "mid": (0.5 * (lo + hi) if lo is not None and hi is not None else None),
                              "n_runs": len(mine), "runs": [r["id"] for r in mine]}
    return out, recs, red


def a2(red, test, tau, region="half"):
    return red[f"A2_{test}_{region}_tau{tau:.4f}_r1_dt1"]


def b2(red, test, tau=T21, h="central", d=0.0):
    return red[f"B2_{test}_tau{tau:.4f}_{h}_dEb{d:+.0f}"]


def _inert(recs, name):
    for r in recs.values():
        if r.get("search") == name and not r.get("reaction", True) and not r["id"].endswith("_V2"):
            return r
    return None


def score(B, recs, red):
    sc = {}
    # P1
    b = B["A4_PT_Exp1_tri5"]
    A1 = a2(red, PT1, 5.0)["A1"]["f_star"]
    sc["P1"] = {"A1": A1, "bracket": [b["lo"], b["hi"]], "mid": b["mid"],
                "rel": abs(b["mid"] - A1) / A1, "holds": bool(abs(b["mid"] - A1) <= 0.10 * A1)}
    # P2
    b = B["A4_PT_Exp1_tri40"]
    v = a2(red, PT1, 40.0)["f_star"]
    sc["P2"] = {"A2": v, "bracket": [b["lo"], b["hi"]], "mid": b["mid"], "rel": abs(v - b["mid"]) / b["mid"],
                "holds": bool(abs(v - b["mid"]) <= 0.05 * b["mid"])}
    # P3
    b = B["A4_PT_Exp1_tri120"]
    v = a2(red, PT1, 120.0)["f_star"]
    sc["P3"] = {"A2": v, "bracket": [b["lo"], b["hi"]], "mid": b["mid"], "below_rel": 1 - b["mid"] / v,
                "holds": bool(b["mid"] < 0.95 * v), "whole_bracket_below": bool(b["hi"] < 0.95 * v)}
    # P4
    cases = []
    ok = True
    for test in ("M50_ST_Exp3", "M50_PT_Exp3"):
        ref = B[f"A4ref_{test[4:]}_tri21"]
        v21 = a2(red, test, T21)["f_star"]
        for tau in (10.0, 60.0):
            b = B[f"A4_{test[4:]}_tri{tau:g}"]
            v = a2(red, test, tau)["f_star"]
            mag = abs(v - b["mid"]) <= 0.10 * b["mid"]
            d_a2 = np.sign(v - v21)
            d_res = np.sign(b["mid"] - ref["mid"])
            overlap = not (b["hi"] <= ref["lo"] or ref["hi"] <= b["lo"])
            cases.append({"test": test, "tau_d_s": tau, "A2": v, "A2_21": v21, "bracket": [b["lo"], b["hi"]],
                          "mid": b["mid"], "ref_bracket": [ref["lo"], ref["hi"]], "ref_mid": ref["mid"],
                          "rel": abs(v - b["mid"]) / b["mid"], "within_10pct": bool(mag),
                          "direction_A2": int(d_a2), "direction_runs": int(d_res), "brackets_overlap": bool(overlap),
                          "direction_matches": bool(d_a2 == d_res)})
            ok = ok and mag and d_a2 == d_res
    sc["P4"] = {"cases": cases, "holds": bool(ok)}
    # P5, P6
    ref = B["A4ref_PT_Exp1_tri21"]
    w = B["A4_PT_Exp1_whole"]
    e = B["A4_PT_Exp1_eighth"]
    r5 = w["mid"] / ref["mid"]
    sc["P5"] = {"whole": [w["lo"], w["hi"]], "half": [ref["lo"], ref["hi"]], "ratio": r5,
                "A2_ratio": a2(red, PT1, T21, "whole")["f_star"] / a2(red, PT1, T21)["f_star"],
                "holds": bool(1.8 <= r5 <= 2.2)}
    r6 = (e["mid"] / IN.A_EIGHTH) / (ref["mid"] / IN.A_HALF)
    sc["P6"] = {"eighth": [e["lo"], e["hi"]], "half": [ref["lo"], ref["hi"]], "per_area_ratio": r6,
                "holds": bool(r6 >= 1.25)}
    # P7
    rows = list(csv.DictReader(open(os.path.join(IN.RES, "stage13_tign.csv"))))
    own = [float(r["T_ign_C"]) for r in rows if r["kinetics"] != "mean" and r["trigger"] == "own"
           and r["connection"] == "parallel" and r["T_ign_C"] not in ("", "None")]
    mean = [float(r["T_ign_C"]) for r in rows if r["kinetics"] == "mean" and r["trigger"] == "own"][0]
    lo, hi = np.percentile(own, [2.5, 97.5]) if own else (None, None)
    sc["P7"] = {"mean_C": mean, "mean_clause_known_at_registration": True, "mean_in_range": bool(215 <= mean <= 240),
                "n_draws": len(own), "p2.5_C": lo, "p97.5_C": hi, "span_K": (hi - lo) if own else None,
                "holds": bool(own and hi - lo < 40.0)}
    # P8
    rowsP8 = []
    n_ok = 0
    for h in ("low", "high"):
        for t in IN.TEST_ORDER:
            b = B[f"B4_{h}_{t[4:]}"]
            v = b2(red, t, T21, h)["E_star_J"]
            tol = max(0.10 * b["mid"], 300.0)
            ok = abs(v - b["mid"]) <= tol
            n_ok += ok
            rowsP8.append({"test": t, "h": h, "B2_J": v, "bracket_J": [b["lo"], b["hi"]], "mid_J": b["mid"],
                           "diff_J": v - b["mid"], "tol_J": tol, "within": bool(ok)})
    sc["P8"] = {"n_within": int(n_ok), "of": len(rowsP8), "cases": rowsP8, "holds": bool(n_ok >= 28)}
    # P9
    Ee = IN.e_e(PT1)
    r = {}
    r[T21] = (0.5 * sum(C2_REF21)) / B["A4ref_PT_Exp1_tri21"]["mid"]
    for tau in (120.0, 360.0):
        r[tau] = (B[f"B4_tri{tau:g}_PT_Exp1"]["mid"] / Ee) / B[f"A4_PT_Exp1_tri{tau:g}"]["mid"]
    sc["P9"] = {"ratio": {f"{k:.4g}": v for k, v in r.items()},
                "falls": bool(r[T21] > r[120.0] > r[360.0]), "below_1.5_at_360": bool(r[360.0] < 1.5),
                "holds": bool(r[T21] > r[120.0] > r[360.0] and r[360.0] < 1.5)}
    # P10
    cs = []
    ok = True
    for t in ("M50_PP_Exp3", "M50_ST_Exp2", "M50_PT_Exp3"):
        bm, bp = B[f"B4_Ebm2_{t[4:]}"], B[f"B4_Ebp2_{t[4:]}"]
        slope = (bm["mid"] - bp["mid"]) / 4.0
        inr = 150.0 <= slope <= 300.0
        ok = ok and inr
        b2s = (b2(red, t, T21, "central", -2000.0)["E_star_J"] - b2(red, t, T21, "central", 2000.0)["E_star_J"]) / 4
        cs.append({"test": t, "minus2": [bm["lo"], bm["hi"]], "plus2": [bp["lo"], bp["hi"]],
                   "slope_J_per_kJ": slope, "B2_slope_J_per_kJ": b2s, "in_range": bool(inr)})
    sc["P10"] = {"cases": cs, "holds": bool(ok)}
    return sc


REGIMES = ((1.0 / 9.0, "skin"), (1.0, "intermediate"), (float("inf"), "through-heated"))


def regime(fo):
    for edge, name in REGIMES:
        if fo < edge:
            return name


def _arch_br(text):
    """An archived bracket string "(lo, hi]" or "0" as (lo, hi)."""
    text = (text or "").strip()
    if text in ("", "None"):
        return None
    if text == "0":
        return (0.0, 0.0)
    lo, hi = text.strip("(]").split(",")
    return (float(lo), float(hi))


def _write(path, rows):
    keys = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in keys})


def skin_table(B, recs, red):
    arch = {r["test"]: r for r in csv.DictReader(open(os.path.join(IN.RES, "stage8_thresholds.csv")))}
    rows = []

    def row(test, region, tau, res=None, source=None, search=None):
        k = f"A2_{test}_{region}_tau{tau:.4f}_r1_dt1"
        a = red.get(k, {})
        r = {"test": test, "region": region, "tau_d_s": tau, "fourier": IN.fourier(tau), "regime": regime(IN.fourier(tau)),
             "A1_f": a.get("A1", {}).get("f_star"), "A1_pure_skin_f": a.get("A1", {}).get("pure_skin_f_star"),
             "A2_f": a.get("f_star"), "A2_theta_deg": a.get("theta_deg"), "A2_t_s": a.get("t_s"),
             "A2_T_cond_C": a.get("T_cond_C"), "A2_trigger_alone": a.get("trigger_alone")}
        if res is not None:
            r.update({"res_lo": res[0], "res_hi": res[1], "res_mid": 0.5 * (res[0] + res[1]), "res_source": source})
        if search is not None:
            b = B[search]
            r["n_runs"] = b["n_runs"]
            hi_rec = [recs[i] for i in b["runs"] if abs(recs[i]["f"] - b["hi"]) < 1e-12]
            if hi_rec:
                rr = hi_rec[0]["resolved"]
                r.update({"res_t_cross_hi_s": rr["t_prop_s"], "res_theta_cross_hi_deg": (rr.get("where") or {}).get("theta_deg"),
                          "res_z_cross_hi_mm": (rr.get("where") or {}).get("z_mm"), "res_rxn_heat_hi_J": rr["in_rxn_J"]})
            inert = _inert(recs, search)
            if inert is not None:
                pk = inert["resolved"]["peak_hottest_C"]
                r.update({"inert_peak_at_hi_C": pk, "inert_peak_minus_level_K": pk - IN.T_LEVEL_C,
                          "inert_t_peak_s": inert["resolved"]["t_peak_hottest_s"],
                          "inert_theta_peak_deg": inert["resolved"]["where_peak"]["theta_deg"]})
        rows.append(r)

    for tau in (5.0, 10.0, T21, 40.0, 60.0, 120.0, 240.0, 360.0):
        if tau in (5.0, 40.0, 120.0, 360.0):
            b = B[f"A4_PT_Exp1_tri{tau:g}"]
            row(PT1, "half", tau, (b["lo"], b["hi"]), "new search", f"A4_PT_Exp1_tri{tau:g}")
        elif tau == T21:
            b = B["A4ref_PT_Exp1_tri21"]
            row(PT1, "half", tau, (b["lo"], b["hi"]), "archived bracket refined in Stage 13", "A4ref_PT_Exp1_tri21")
        elif tau in (10.0, 60.0):
            row(PT1, "half", tau, _arch_br(arch[PT1][f"dur{tau:g}_c1"]), "archived (Stage 8)")
        else:
            row(PT1, "half", tau)
    for region, name in (("whole", "A4_PT_Exp1_whole"), ("eighth", "A4_PT_Exp1_eighth")):
        b = B[name]
        row(PT1, region, T21, (b["lo"], b["hi"]), "new search", name)
    for test in ("M50_ST_Exp3", "M50_PT_Exp3"):
        for tau in (10.0, T21, 60.0):
            name = f"A4_{test[4:]}_tri{tau:g}" if tau != T21 else f"A4ref_{test[4:]}_tri21"
            b = B[name]
            row(test, "half", tau, (b["lo"], b["hi"]), "new search" if tau != T21 else
                "archived bracket refined in Stage 13", name)
    for test in IN.TEST_ORDER:
        if test in (PT1, "M50_ST_Exp3", "M50_PT_Exp3"):
            continue
        row(test, "half", T21, _arch_br(arch[test]["fC1"]), "archived (Stage 8)")
    for test in ("M50_PP_Exp3", "M50_ST_Exp2", "M50_SP_Exp1", "M50_SP_Exp3"):
        for tau in (10.0, 60.0):
            ref = (arch[test].get(f"dur{tau:g}_c1_refined") or "").strip()
            if ref:
                row(test, "half", tau, _arch_br(ref), "archived (Stage 8)")
                rows[-1]["res_note"] = "the archive's refined bracket"
            else:
                row(test, "half", tau, _arch_br(arch[test][f"dur{tau:g}_c1"]), "archived (Stage 8)")
    return rows


ARCH_RUNS = list(csv.DictReader(open(os.path.join(IN.RES, "stage13_archive_runs.csv"))))


def twobody_table(B, red):
    arch = {r["test"]: r for r in csv.DictReader(open(os.path.join(IN.RES, "stage8_thresholds.csv")))}
    rows = []
    for k, v in red.items():
        if not k.startswith("B2_"):
            continue
        t, tau, h, d = v["test"], v["tau_d_s"], v["h"], v["dE_body_J"]
        r = {"test": t, "connection": IN.tests()[t]["connection"], "E_b_J": float(IN.tests()[t]["E_b_J"]) + d,
             "dE_body_J": d, "h": h, "tau_d_s": tau, "B2_E_J": v["E_star_J"], "B2_f": v["f_star"],
             "B2_binding": v["binding"],
             "B2_t_ignition_s": (v.get("above") or {}).get("t_first_admissible_s"),
             "B2_t_margin_s": (v.get("above") or {}).get("t_g_s")}
        name = None
        if abs(tau - T21) < 1e-9 and h in ("low", "high") and d == 0.0:
            name = f"B4_{h}_{t[4:]}"
        elif h == "central" and d == 0.0 and tau in (120.0, 360.0):
            name = f"B4_tri{tau:g}_{t[4:]}"
        elif h == "central" and d != 0.0:
            name = f"B4_Eb{'m' if d < 0 else 'p'}2_{t[4:]}"
        if name is not None and name in B and B[name]["mid"] is not None:
            b = B[name]
            r.update({"lum_lo_J": b["lo"], "lum_hi_J": b["hi"], "lum_mid_J": b["mid"], "lum_source": "new search",
                      "n_runs": b["n_runs"], "B2_minus_mid_J": v["E_star_J"] - b["mid"],
                      "P8_tol_J": max(0.10 * b["mid"], 300.0) if h in ("low", "high") else None})
        elif abs(tau - T21) < 1e-9 and h == "central" and d == 0.0:
            br = _arch_br(arch[t]["fC2"])
            if t == PT1:
                br = C2_REF21
            Ee = IN.e_e(t)
            r.update({"lum_lo_J": br[0] * Ee, "lum_hi_J": br[1] * Ee, "lum_mid_J": 0.5 * (br[0] + br[1]) * Ee,
                      "lum_source": "archived (Stage 8" + (", refined)" if t == PT1 else ")"),
                      "B2_minus_mid_J": v["E_star_J"] - 0.5 * (br[0] + br[1]) * Ee})
            # the archived crossing time at the bracket's upper end (the lumped neighbour of that run)
            hit = [a for a in ARCH_RUNS if a["test"] == t and a["source"] == "stage8_runs" and a["f"] not in ("", None)
                   and abs(float(a["f"]) - br[1]) < 1e-9 and a["lum_propagated"] == "True"
                   and a["lum_t_prop_s"] not in ("", None)]
            if hit:
                r["archived_t_cross_s"] = float(hit[0]["lum_t_prop_s"])
        rows.append(r)
    return rows


MANUSCRIPT_DELIVERIES = ((10.0, "10 s pulse"), (T21, "21.39 s pulse"), (60.0, "60 s pulse"), (120.0, "120 s power"),
                         (240.0, "240 s power"), (360.0, "360 s power"))


def map_table(B, red):
    Ee = IN.e_e(PT1)
    post = os.path.join(IN.RES, "stage13_reduced_post.json")
    red = dict(red, **(json.load(open(post)) if os.path.exists(post) else {}))
    rows = []
    for tau in (5.0, 10.0, T21, 40.0, 60.0, 120.0, 240.0, 360.0):
        a = red[f"A2_{PT1}_half_tau{tau:.4f}_r1_dt1"]["f_star"]
        kb = f"B2_{PT1}_tau{tau:.4f}_central_dEb+0"
        b = red[kb]["f_star"] if kb in red else None
        r = {"tau_d_s": tau, "fourier": IN.fourier(tau), "regime": regime(IN.fourier(tau)), "A2_fC1": a,
             "B2_fC2": b, "B2_over_A2": (b / a) if b is not None else None,
             "manuscript_delivery": dict(MANUSCRIPT_DELIVERIES).get(tau)}
        if tau == T21:
            c1, c2 = B["A4ref_PT_Exp1_tri21"]["mid"], 0.5 * sum(C2_REF21)
        elif tau in (120.0, 360.0):
            c1, c2 = B[f"A4_PT_Exp1_tri{tau:g}"]["mid"], B[f"B4_tri{tau:g}_PT_Exp1"]["mid"] / Ee
        else:
            c1 = c2 = None
        if c1 is not None:
            r.update({"runs_fC1_mid": c1, "runs_fC2_mid": c2, "runs_ratio": c2 / c1})
        rows.append(r)
    return rows


if __name__ == "__main__":
    B, recs, red = brackets()
    for k, v in B.items():
        print(k, v["status"], v["lo"], v["hi"], v["n_runs"])
    sc = score(B, recs, red)
    json.dump(sc, open(os.path.join(IN.RES, "stage13_scorecard.json"), "w"), indent=1, default=float)
    _write(os.path.join(IN.RES, "stage13_skin.csv"), skin_table(B, recs, red))
    _write(os.path.join(IN.RES, "stage13_twobody.csv"), twobody_table(B, red))
    _write(os.path.join(IN.RES, "stage13_map.csv"), map_table(B, red))
    for k, v in sc.items():
        print(k, v["holds"])
