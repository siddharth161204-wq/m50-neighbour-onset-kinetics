#!/usr/bin/env python3
"""The manuscript's numbers that are not already in a results file: the model's constants read from the code, the
counts of runs and predictions read from the records, and the derived figures the texts quote, each computed here
from the files (never typed). Writes results/manuscript_numbers.json, which manuscript/numbers_check.py reads with every
other results file.

Usage: python3 manuscript_numbers.py [--res ../results]
"""
import argparse, csv, glob, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.join(HERE, "..")


def constants():
    import v12_model as V
    import bcrnn
    import stage10_inputs as IN10
    import stage11_inputs as IN11
    LP = V.LP
    out = {
        "cell_diameter_mm": LP.D_CELL * 1e3, "cell_length_mm": LP.L_CELL * 1e3, "cell_radius_mm": LP.D_CELL / 2 * 1e3,
        "can_thickness_mm": LP.T_CAN * 1e3, "can_conductivity_W_mK": LP.K_CAN, "k_radial_W_mK": LP.K_RADIAL,
        "k_axial_W_mK": LP.K_AXIAL, "C_cell_J_K": LP.C_CELL, "m_cell_kg": LP.M_CELL, "cp_cell_J_kgK": LP.CP_CELL,
        "emissivity": LP.EPS, "h_conv_W_m2K": LP.H_CONV, "T_amb_C": LP.T_AMB - 273.15, "gap_two_cell_mm": LP.GAP * 1e3,
        "run_end_s": LP.T_END, "level_propagation_C": V.LEVEL_PROP - 273.15,
        "onset_rate_K_per_min": 0.15, "onset_rate_W_per_kg": 0.15 / 60.0 * LP.CP_CELL,
        "M_ref_g": bcrnn.M_REF_G, "sei_initial_amount": float(bcrnn.C0[bcrnn.SPECIES.index("sei")]),
        "n_reactions": bcrnn.NR, "n_an_ele_reactions": len(bcrnn.AN_ELE_COLUMNS),
        "nodes_theta_deg": {k: v["theta_deg"] for k, v in IN10.NODES.items()},
        "kin_ranks": list(IN11.KIN_RANKS), "kin_draws": dict(IN11.KIN_DRAWS),
        "view_factor_cans_in_contact": V.F_TOUCH, "h_contact_W_m2K": dict(V.H_CONTACT),
        "g_tab_mW_K": {k: v * 1e3 for k, v in V.G_TAB.items()}, "k_air_W_mK": LP.K_AIR,
        "E_body_stage5_J": V.E_BODY,
    }
    return out


def kinetics_band(res):
    """Peaks of the three submodels' heat release rate in the 5 K/min ramp (Figure 1b)."""
    rows = list(csv.DictReader(open(os.path.join(res, "manuscript_kinetics_band.csv"))))
    out = {}
    for g in ("anode_electrolyte", "cathode", "separator"):
        sgn = -1.0 if g == "separator" else 1.0
        best = max(rows, key=lambda r: sgn * float(r[f"{g}_mean"]))
        out[g] = {"peak_W_kg": float(best[f"{g}_mean"]), "at_C": float(best["T_C"])}
    return out


def run_counts(res):
    """Runs recorded per stage, from the records directories (failed records excluded)."""
    out = {}
    for name, pat in (("stage5", "v12_runs/*.json"), ("stage6", "stage6_runs/*.json"), ("stage7", "stage7_runs/*.json"),
                      ("stage8", "stage8_runs/*.json"), ("stage9", "stage9_runs/*.json"),
                      ("stage10", "stage10_runs/*.json"), ("stage11", "stage11_runs/*.json")):
        fs = glob.glob(os.path.join(res, pat))
        n_failed = 0
        for f in fs:
            try:
                if json.load(open(f)).get("failed"):
                    n_failed += 1
            except Exception:
                pass
        out[name] = {"records": len(fs), "failed": n_failed}
    return out


def predictions():
    p = os.path.join(ROOT, "manuscript", "data", "predictions_by_stage.csv")
    if not os.path.exists(p):
        return None
    rows = list(csv.DictReader(open(p)))
    through10 = [r for r in rows if int(r["stage"]) <= 10]
    s11 = [r for r in rows if int(r["stage"]) == 11]
    return {"through_stage10": {"committed": len(through10), "held": sum(r["verdict"] == "held" for r in through10),
                                "failed": sum(r["verdict"] == "failed" for r in through10),
                                "foreseen": sum(r["verdict"] == "failed" and r["foreseen"] == "yes" for r in through10)},
            "stage11": {"committed": len(s11), "held": sum(r["verdict"] == "held" for r in s11),
                        "failed": sum(r["verdict"] == "failed" for r in s11)},
            "all": {"committed": len(rows), "held": sum(r["verdict"] == "held" for r in rows),
                    "failed": sum(r["verdict"] == "failed" for r in rows)}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", default=os.path.join(ROOT, "results"))
    a = ap.parse_args()
    out = {"constants": constants(), "kinetics_band": kinetics_band(a.res), "runs": run_counts(a.res),
           "predictions": predictions()}
    json.dump(out, open(os.path.join(a.res, "manuscript_numbers.json"), "w"), indent=1, default=float)
    print(json.dumps(out, default=float)[:1500])


if __name__ == "__main__":
    main()
