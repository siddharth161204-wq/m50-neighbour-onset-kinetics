"""Stage 15, Part A0.4 and A0.5 (DECISIONS.md D171, D172): the two neighbours' energy accounts in the same run, and
the sizing.

A0.4 reads the archive repeats (`stage15_run.py repeats`): Stage 10's runs of M50_PT_Exp4, PP_Exp3 and ST_Exp2 with
no delivery made again through `stage15_model`, which keeps both neighbours' accounts every 0.5 s. Each repeat is
checked against its archived record (every stored history within 1e-6 K, the accounts within 1e-6 of their totals).
The lumped neighbour's link carries its tabs with its contact (one conductance, G = g_bus + g_link, D-entries of the
two-cell study); its tabs' share of the link's heat is g_bus / G exactly, since both see the same difference
T1 - T. Since both neighbours have the same heat capacity C (61.75 J/K), the lumped neighbour's excess temperature
over the resolved mean is (stored_lumped - stored_resolved) / C, and the excess's sources are the differences of
the accounts' terms.

A0.5 reads the archive's continued runs (`stage15_archive`): their wall times, the share of their steps made before
the mean crosses, what steps_with_max_sub and max_implicit_nodes record and whether any run reached a limit of its
reaction step; and the repeats' wall times on this machine.

Usage: python3 src/stage15_a0.py  (writes results/stage15_accounts.json and results/stage15_sizing.json)
"""
import csv
import json
import os
import statistics as st
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v12_model as V                    # noqa: E402
import stage15_inputs as IN              # noqa: E402
import stage15_archive as AR             # noqa: E402

LP = V.LP
REP = os.path.join(IN.RES, "stage15_repeats")
TIMES = (10.0, 21.4, 30.0, 60.0, 100.0, 150.0, 200.0, 250.0, 300.0, 332.0, 450.0, 600.0, 900.0)


def _rec(rid, d):
    return json.load(open(os.path.join(d, rid + ".json")))


def check_repeat(name):
    a = _rec("s15_rep_" + name, REP)
    arch = a["archived_id"]
    stage = "stage10" if arch.startswith("s10") else "stage9"
    b = _rec(arch, os.path.join(IN.RES, f"{stage}_runs"))
    za = np.load(os.path.join(IN.SERIES, a["id"] + ".npz"))
    zb = np.load(os.path.join(IN.RES, f"{stage}_series", arch + ".npz"))
    worst = 0.0
    for k in ("Tmean", "Tmax", "T1", "T_lumped") + tuple("probe_" + p for p in ("away", "toward")):
        if k in zb.files:
            n = min(len(za[k]), len(zb[k]))
            worst = max(worst, float(np.abs(za[k][:n] - zb[k][:n]).max()))
    ea, eb = a["resolved"]["energy_J"], b["resolved"]["energy_J"]
    same_end = abs(a["resolved"]["t_end_s"] - b["resolved"]["t_end_s"]) < 1e-9
    # a repeat stopped at C8 ends before its archived run: its accounts are not the record's totals, and its C8 is
    # checked against the archived series' crossing of the level instead (read every 0.1 s there, every step here)
    acc = max(abs(ea[k] - eb[k]) / max(1.0, abs(eb[k])) for k in eb if k in ea) if same_end else None
    c8_arch = AR._reader_a(zb["t"], zb["Tmean"] - IN.K0)[0]
    c8_diff = (abs(a["resolved"]["t_C8_s"] - c8_arch) if (a["resolved"]["C8"] and c8_arch is not None) else None)
    ok = worst < 1e-6 and (acc < 1e-6 if acc is not None else (c8_diff is not None and c8_diff <= 0.1))
    return {"repeat": a["id"], "archived": arch, "worst_history_K": worst, "worst_account_rel": acc,
            "C8_archived_s": c8_arch, "C8_difference_s": c8_diff, "same_end": same_end,
            "passed": ok, "wall_s_here": a["wall_s"], "wall_s_archived": b.get("wall_s"),
            "machine_archived": (b.get("machine") or {}).get("label"), "steps": a["resolved"]["steps"],
            "C8": a["resolved"]["C8"], "t_C8_s": a["resolved"]["t_C8_s"]}


def accounts(name):
    a = _rec("s15_rep_" + name, REP)
    z = np.load(os.path.join(IN.SERIES, a["id"] + ".npz"))
    rk, rr = [str(x) for x in z["acc_res_keys"]], z["acc_res"]
    lk, lr = [str(x) for x in z["acc_lum_keys"]], z["acc_lum"]
    G = a["g_pos_W_K"] + a["g_neg_W_K"] + a["G_contact_W_K"]
    tab = (a["g_pos_W_K"] + a["g_neg_W_K"]) / G
    t_end = a["resolved"]["t_end_s"]
    out = []
    for t in TIMES:
        if t > t_end + 1e-9:
            continue
        R = {k: float(np.interp(t, rr[:, 0], rr[:, j])) for j, k in enumerate(rk) if k != "t_s"}
        L = {k: float(np.interp(t, lr[:, 0], lr[:, j])) for j, k in enumerate(lk) if k != "t_s"}
        res = {"contact_and_wedge": R["in_gap"], "tabs": R["in_bus"], "radiation_in": R["in_rad"],
               "convection_out": R["out_conv"], "radiation_out": R["out_rad"], "reaction": R["in_rxn"]}
        lum = {"contact_and_wedge": L["in_link"] * (1 - tab), "tabs": L["in_link"] * tab, "radiation_in": L["in_rad"],
               "convection_out": L["out_conv"], "radiation_out": L["out_rad"], "reaction": L["in_rxn"]}
        for d in (res, lum):
            d["stored"] = (d["contact_and_wedge"] + d["tabs"] + d["radiation_in"] + d["reaction"]
                           - d["convection_out"] - d["radiation_out"])
            d["T_C"] = IN.T_AMB - IN.K0 + d["stored"] / LP.C_CELL
        diff = {k: lum[k] - res[k] for k in res}
        out.append({"t_s": t, "resolved": res, "lumped": lum, "lumped_less_resolved": diff})
    # at the lumped neighbour's peak
    tl = float(a["lumped"]["t_peak_s"])
    return {"test": a["test"], "t_end_s": t_end, "tab_share_of_link": tab, "rows": out,
            "lumped_peak_C": a["lumped"]["peak_C"], "t_lumped_peak_s": tl,
            "resolved_mean_peak_C": a["resolved"]["peak_mean_C"], "t_resolved_mean_peak_s": a["resolved"]["t_peak_mean_s"]}


def sizing():
    rows = list(csv.DictReader(open(os.path.join(IN.RES, "stage15_archive_table.csv"))))
    f = lambda x: None if x in ("", None) else float(x)
    run = [r for r in rows if r["mean_t_cross_s"]]
    norun = [r for r in rows if not r["mean_t_cross_s"]]
    frac = []
    for r in run:
        z = np.load(AR.series_path("stage%s" % r["stage"], r["id"]))
        pt = z["probe_t"]
        frac.append(((pt <= f(r["mean_t_cross_s"])).sum() - 1) / (len(pt) - 1))
    imp = [r for r in rows if (f(r["max_implicit_nodes"]) or 0) > 0]
    return {
        "continued_runs": len(rows),
        "wall_median_s": {"no C8": st.median(f(r["wall_s"]) for r in norun), "C8": st.median(f(r["wall_s"]) for r in run)},
        "n": {"no C8": len(norun), "C8": len(run)},
        "machines": sorted(set(r["machine"] for r in rows)),
        "share_of_steps_before_C8": {"median": st.median(frac), "min": min(frac), "max": max(frac)},
        "max_implicit_nodes": {"runs_above_0": len(imp), "largest": max(f(r["max_implicit_nodes"]) for r in rows),
                               "all_without_delivery": all(r["shape"] == "none" for r in imp)},
        "implicit_node_steps_with_max_sub": {"runs_above_0": sum((f(r["implicit_node_steps_with_max_sub"]) or 0) > 0
                                                                 for r in rows)},
        "rejected_steps": {"runs_above_0": sum((f(r["rejected"]) or 0) > 0 for r in rows),
                           "largest": max(f(r["rejected"]) or 0 for r in rows)},
        "max_sub_values": sorted(set(r["max_sub"] for r in rows)),
    }


def main():
    reps = {n: check_repeat(n) for n in ("acc_PT_Exp4", "acc_PP_Exp3", "acc_ST_Exp2", "size_PT_Exp4_con240",
                                         "size_PT_Exp4_tri21")
            if os.path.exists(os.path.join(REP, "s15_rep_" + n + ".json"))}
    acc = {n: accounts(n) for n in ("acc_PT_Exp4", "acc_PP_Exp3", "acc_ST_Exp2") if n in reps}
    json.dump({"repeats": reps, "accounts": acc}, open(os.path.join(IN.RES, "stage15_accounts.json"), "w"), indent=1)
    json.dump({"archive": sizing(), "repeats_here": reps}, open(os.path.join(IN.RES, "stage15_sizing.json"), "w"),
              indent=1)
    for n, r in reps.items():
        print(n, "passed" if r["passed"] else "FAILED", r["worst_history_K"], r["worst_account_rel"],
              round(r["wall_s_here"]), "s here,", round(r["wall_s_archived"] or 0), "s archived")


if __name__ == "__main__":
    main()
