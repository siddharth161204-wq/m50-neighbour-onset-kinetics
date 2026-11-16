"""Stage 13, Part A0.2: the archived values as context, and the three readings of the brief checked against the
archived records (DECISIONS.md D130).

Writes results/stage13_archive_runs.csv (every archived run of Stages 8 and 9 with its fraction, the hot spot's and
the lumped neighbour's peak and crossing time), results/stage13_archive_brackets.csv (the sixteen f*(C1) and f*(C2)
brackets and the five tests' duration, region and ratio brackets) and results/stage13_readings.json.
"""
import csv
import glob
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage13_inputs as IN                # noqa: E402
import stage13_tign as B1                  # noqa: E402
import bcrnn                               # noqa: E402

LP = IN.LP
K0 = IN.K0


def _g(d, *ks):
    for k in ks:
        if d is None:
            return None
        d = d.get(k) if isinstance(d, dict) else None
    return d


def records():
    rows = []
    for src in ("stage8_runs", "stage9_runs"):
        for fn in sorted(glob.glob(os.path.join(IN.RES, src, "*.json"))):
            d = json.load(open(fn))
            r, l = d.get("resolved"), d.get("lumped")
            t_res = _g(r, "t_prop_s") if r and "t_prop_s" in r else _g(r, "cross_s", "T_onset_low")
            t_lum = _g(l, "t_prop_s") if l and "t_prop_s" in l else _g(l, "cross_s", "T_onset_low")
            rows.append({
                "source": src, "id": d["id"], "set": d.get("set", d.get("cfg", d.get("kind"))), "test": d["test"],
                "connection": d.get("connection"), "E_b_J": d.get("E_body_J"), "shape": d.get("shape", "tri"),
                "tau_d_s": d.get("tau_d_s"), "geometry": d.get("geometry"), "ratio": d.get("ratio"), "f": d.get("f"),
                "E_delivered_J": d.get("E_delivered_J"), "kin": d.get("kin"), "sei": d.get("sei"),
                "res_propagated": _g(r, "propagated"), "res_t_prop_s": t_res,
                "res_peak_C": _g(r, "peak_hottest_C"), "res_t_peak_s": _g(r, "t_peak_hottest_s"),
                "res_theta_deg": _g(r, "where_peak", "theta_deg"), "res_z_mm": _g(r, "where_peak", "z_mm"),
                "res_theta_cross_deg": _g(r, "where", "theta_deg"), "res_in_rxn_J": _g(r, "in_rxn_J"),
                "res_stopped": _g(r, "stopped"),
                "lum_propagated": _g(l, "propagated"), "lum_t_prop_s": t_lum, "lum_peak_C": _g(l, "peak_C"),
                "lum_t_peak_s": _g(l, "t_peak_s"), "lum_stopped": _g(l, "stopped"),
                "lum_reaction_heat_J": _g(l, "reaction_heat_J")})
    return rows


def brackets():
    rows = list(csv.DictReader(open(os.path.join(IN.RES, "stage8_thresholds.csv"))))
    keep = ["test", "connection", "E_b_J", "E_e_J", "propagated", "fC1", "fC2"]
    for k in rows[0]:
        if k.startswith(("dur10_c", "dur60_c", "capend_c", "ratiolow_c", "ratiohigh_c")) and \
                (k.endswith(("_c1", "_c2")) or k.endswith("_refined")):
            keep.append(k)
    return [{k: r.get(k, "") for k in keep} for r in rows], keep


def _pick(rows, set_, test, f):
    sets = (set_,) if isinstance(set_, str) else set_
    for r in rows:
        if r["set"] in sets and r["test"] == test and r["f"] is not None and abs(r["f"] - f) < 1e-9:
            return r
    return None


def readings(rows):
    out = {}
    TL, Ta = IN.T_LEVEL_C, IN.T_AMB - K0
    # 1. the local threshold is conduction into a skin
    a = _pick(rows, ("c1", "first"), "M50_PT_Exp1", 0.1)
    b = _pick(rows, "c1", "M50_PT_Exp1", 0.15)
    x = _pick(rows, "c1", "M50_PT_Exp1", 0.1625)
    rise = lambda r: r["res_peak_C"] - Ta
    slope = (rise(b) - rise(a)) / 0.05
    f_line = 0.1 + (TL - Ta - rise(a)) / slope
    d60 = {f: _pick(rows, "dur60_c1", "M50_PT_Exp1", f) for f in (0.2, 0.25, 0.275, 0.2875)}
    s60 = (rise(d60[0.25]) - rise(d60[0.2])) / 0.05
    f60 = 0.2 + (TL - Ta - rise(d60[0.2])) / s60
    d10 = {f: _pick(rows, "dur10_c1", "M50_PT_Exp1", f) for f in (0.1, 0.1125)}
    cap = {f: _pick(rows, "capend_c1", "M50_PT_Exp1", f) for f in (0.0375, 0.05)}
    Epp = IN.e_e("M50_PT_Exp1") / IN.A_HALF
    tau = IN.TAU_TRIGGER
    e_slope = 1.2284236 * Epp / (slope * math.sqrt(tau))
    e_ratio = 1.2284236 * Epp * 0.15 / (rise(b) * math.sqrt(tau))
    e_cell = math.sqrt(IN.K_R * LP.C_CELL / IN.V_CELL)
    out["reading_1"] = {
        "fC1_brackets": {"21.39 s": [0.15, 0.1625], "10 s": [0.1, 0.1125], "60 s": [0.275, 0.2875],
                         "cap-end quarter": [0.0375, 0.05]},
        "rise_f0.1_K": rise(a), "rise_f0.15_K": rise(b), "t_peak_f0.1_s": a["res_t_peak_s"],
        "t_peak_f0.15_s": b["res_t_peak_s"], "theta_f0.15_deg": b["res_theta_deg"], "z_f0.15_mm": b["res_z_mm"],
        "two_thirds_of_pulse_s": 2 * tau / 3, "slope_K_per_f": slope, "level_rise_K": TL - Ta, "f_line": f_line,
        "f0.1625_cross_s": x["res_t_prop_s"], "f0.1625_theta_cross_deg": x["res_theta_cross_deg"],
        "f0.1625_reaction_heat_J": x["res_in_rxn_J"],
        "dur60_rises_K": {str(f): rise(d60[f]) for f in (0.2, 0.25)}, "dur60_peak_f0.275_C": d60[0.275]["res_peak_C"],
        "dur60_f0.275_propagated": d60[0.275]["res_propagated"], "dur60_f0.2875_cross_s": d60[0.2875]["res_t_prop_s"],
        "dur60_line_f": f60, "dur10_peak_f0.1_C": d10[0.1]["res_peak_C"], "dur10_t_peak_f0.1_s": d10[0.1]["res_t_peak_s"],
        "dur10_f0.1125_propagated": d10[0.1125]["res_propagated"], "capend_peak_f0.0375_C": cap[0.0375]["res_peak_C"],
        "capend_f0.05_propagated": cap[0.05]["res_propagated"],
        "capend_per_area_ratio_to_half": (0.04375 * 4) / 0.15625,
        "E_pp_per_f_J_m2": Epp, "e_implied_from_slope": e_slope, "e_implied_from_ratio": e_ratio,
        "e_roll_as_resolved": IN.E_ROLL, "e_whole_cell_heat_capacity": e_cell,
        "C_s_J_m2K": IN.C_S, "slope_ratio_21_to_60": slope / s60, "sqrt_60_over_21": math.sqrt(60.0 / tau),
    }
    out["reading_1"]["reproduced"] = bool(abs(rise(a) - 150.8) < 0.1 and abs(rise(b) - 220.3) < 0.1 and
                                          abs(f_line - 0.157) < 0.001 and abs(f60 - 0.277) < 0.001)
    # 2. the whole-cell threshold is an energy balance to an ignition temperature
    kin = bcrnn.Kinetics()
    tab = B1.table(kin, (220, 230, 240, 250))
    Gp, Gs = B1.g_link("parallel"), B1.g_link("series")
    loss230 = {"trigger at 25 C, parallel": B1.loss(230 + K0, IN.T_AMB, Gp),
               "trigger at 25 C, series": B1.loss(230 + K0, IN.T_AMB, Gs),
               "trigger at 230 C": B1.loss(230 + K0, 230 + K0, Gp)}
    ref = sorted([r for r in rows if r["set"] in ("c2", "refA_c2") and r["test"] == "M50_PT_Exp1"],
                 key=lambda r: r["f"])
    below = [r for r in ref if not r["lum_propagated"]]
    above = [r for r in ref if r["lum_propagated"]]
    lo, hi = max(r["f"] for r in below), min(r["f"] for r in above)
    Ee = IN.e_e("M50_PT_Exp1")
    pp3 = sorted([r for r in rows if r["source"] == "stage8_runs" and r["test"] == "M50_PP_Exp3" and
                  r["set"] in ("c2", "refA_c2", "first", "c1") and r["lum_peak_C"] is not None and
                  not r["lum_propagated"]], key=lambda r: r["f"])
    steps = []
    for i in range(len(pp3) - 1):
        df = pp3[i + 1]["f"] - pp3[i]["f"]
        if df > 0:
            dE = df * IN.e_e("M50_PP_Exp3")
            steps.append({"f": [pp3[i]["f"], pp3[i + 1]["f"]], "dE_J": dE,
                          "dpeak_K": pp3[i + 1]["lum_peak_C"] - pp3[i]["lum_peak_C"], "dE_over_C_K": dE / LP.C_CELL})
    out["reading_2"] = {
        "heat_W_molten": tab, "loss_230C_W": loss230,
        "T_ign_C": {"own": B1.t_ign(kin, "own", Gp) - K0, "ambient, parallel": B1.t_ign(kin, "ambient", Gp) - K0},
        "PT_Exp1_E_star_kJ": [lo * Ee / 1e3, hi * Ee / 1e3], "C_times_205K_kJ": LP.C_CELL * 205 / 1e3,
        "peaks_below_C": [(r["f"], r["lum_peak_C"], r["lum_t_peak_s"]) for r in below[-4:]],
        "PP_Exp3_steps": steps}
    out["reading_2"]["reproduced"] = bool(abs(tab[1]["cat1_W"] - 48.2) < 0.1 and abs(tab[2]["cat1_W"] - 136.7) < 0.1
                                          and abs(lo * Ee / 1e3 - 12.85) < 0.01)
    # 3. E* is a difference: the archived f*(C2) against the trigger's body energy
    br = {r["test"]: r for r in csv.DictReader(open(os.path.join(IN.RES, "stage8_thresholds.csv")))}
    pts = []
    for t, r in br.items():
        if r["fC2_hi"] not in ("", None) and float(r["fC2_hi"]) > 0:
            mid = 0.5 * (float(r["fC2_lo"]) + float(r["fC2_hi"])) * float(r["E_e_J"])
            pts.append((t, r["connection"], float(r["E_b_J"]), mid, r["propagated"]))
    par = [p for p in pts if p[1] == "parallel" and p[4] == "no"]
    pair = {}
    for i in range(len(par)):
        for j in range(i + 1, len(par)):
            a_, b_ = par[i], par[j]
            pair[f"{a_[0][4:]}-{b_[0][4:]}"] = -(b_[3] - a_[3]) / (b_[2] - a_[2])
    out["reading_3"] = {"points_E_b_J_E_star_mid_J": pts, "pairwise_slopes_parallel_not_propagated": pair}
    return out


def main():
    rows = records()
    keys = list(rows[0].keys())
    with open(os.path.join(IN.RES, "stage13_archive_runs.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    br, keep = brackets()
    with open(os.path.join(IN.RES, "stage13_archive_brackets.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keep)
        w.writeheader()
        w.writerows(br)
    rd = readings(rows)
    json.dump(rd, open(os.path.join(IN.RES, "stage13_readings.json"), "w"), indent=1, default=float)
    return rows, rd


if __name__ == "__main__":
    rows, rd = main()
    print(len(rows), "records")
    print(json.dumps(rd, indent=1, default=float)[:6000])
