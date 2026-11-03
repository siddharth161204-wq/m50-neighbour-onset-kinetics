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
                      ("stage10", "stage10_runs/*.json"), ("stage11", "stage11_runs/*.json"),
                      ("stage12", "stage12_runs/*.json")):
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
    s12 = [r for r in rows if int(r["stage"]) == 12]
    through11 = [r for r in rows if int(r["stage"]) <= 11]
    def counts(rs):
        failed = [r for r in rs if r["verdict"] == "failed"]
        foreseen = sum(r["foreseen"] == "yes" for r in failed)
        return {"committed": len(rs), "held": sum(r["verdict"] == "held" for r in rs), "failed": len(failed),
                "foreseen": foreseen, "unforeseen": len(failed) - foreseen}
    return {"through_stage10": counts(through10), "stage11": counts(s11), "through_stage11": counts(through11),
            "stage12": counts(s12), "all": counts(rows)}


def after_review(res):
    """Quantities the manuscript states after the reviewer's read (DECISIONS.md D121), computed here from the inputs
    and the registered results files. None is registered; each restates or combines registered values."""
    tests = {r["test"]: r for r in csv.DictReader(open(os.path.join(ROOT, "inputs", "fransson2024", "m50_tests.csv")))}
    trig = {}
    for r in csv.DictReader(open(os.path.join(res, "stage7_triggers.csv"))):
        if r["kind"] == "test":
            trig.setdefault(r["test"], float(r["E_J"]))
    ee = {r["test"]: float(r["E_e_J"]) for r in csv.DictReader(open(os.path.join(res, "stage9_fractions.csv")))}
    db = [r for r in csv.DictReader(open(os.path.join(ROOT, "inputs", "databank", "databank_m50_used.csv")))
          if r["Trigger-Mechanism"] == "Nail"]
    body_max = max(float(r["Energy-Fraction-Cell-Body-kJ"]) for r in db) * 1e3
    ej_max = max(float(r["Energy-Fraction-Positive-Ejecta-kJ"]) + float(r["Energy-Fraction-Negative-Ejecta-kJ"])
                 for r in db) * 1e3
    c1 = json.load(open(os.path.join(res, "stage7_paper_numbers.json")))["part_b"]["C1"]["central"]["predicted_tests"]
    out = {"what": "derived for the manuscript after the reviewer's read (DECISIONS.md D121); not registered",
           "trigger_vs_databank": {
               "databank_nail_tests": len(db), "body_max_J": body_max, "ejecta_max_J": ej_max,
               "n_tests_Eb_above_body_max": sum(e > body_max for e in trig.values()),
               "n_tests_Ee_above_ejecta_max": sum(ee[t] > ej_max for t in trig),
               "n_tests": len(trig),
               "C1_met_at_f0_tests": sorted(c1), "C1_met_at_f0_Eb_J": [min(trig[t] for t in c1), max(trig[t] for t in c1)],
               "others_Eb_J": [min(v for t, v in trig.items() if t not in c1), max(v for t, v in trig.items() if t not in c1)]},
           "categories": {c: sorted(t for t, r in tests.items() if r["failure_category"] == c)
                          for c in sorted(set(r["failure_category"] for r in tests.values()))}}
    rank = json.load(open(os.path.join(res, "stage10_rank.json")))

    def find(o):
        if isinstance(o, dict):
            if isinstance(o.get("spread"), dict) and "C2_tri21" in o["spread"]:
                return o["spread"]
            for v in o.values():
                r = find(v)
                if r:
                    return r
        return None
    sp = find(rank)
    spread = {}
    for k in ("C2_tri21", "C2_120", "C2_240", "C2_360"):
        nz = {t: x for t, x in sp[k]["fractions"].items() if x > 0}
        en = {t: x * ee[t] for t, x in nz.items()}
        spread[k] = {"fraction_ratio": max(nz.values()) / min(nz.values()),
                     "fraction_largest_test": max(nz, key=nz.get), "fraction_smallest_test": min(nz, key=nz.get),
                     "fraction_smallest": min(nz.values()),
                     "energy_ratio": max(en.values()) / min(en.values()),
                     "energy_largest_test": max(en, key=en.get), "energy_smallest_test": min(en, key=en.get),
                     "energy_J": [min(en.values()), max(en.values())],
                     "n_nonzero": len(nz), "zero_tests": sorted(t for t, x in sp[k]["fractions"].items() if x == 0)}
    out["spread"] = spread
    out["spread_energy_ratio_range"] = [min(v["energy_ratio"] for v in spread.values()),
                                        max(v["energy_ratio"] for v in spread.values())]
    out["spread_fraction_smallest_range"] = [min(v["fraction_smallest"] for v in spread.values()),
                                             max(v["fraction_smallest"] for v in spread.values())]
    tv = out["trigger_vs_databank"]
    out["trigger_vs_databank_kJ"] = {"body_max": tv["body_max_J"] / 1e3, "ejecta_max": tv["ejecta_max_J"] / 1e3,
                                     "C1_met_at_f0_Eb": [x / 1e3 for x in tv["C1_met_at_f0_Eb_J"]]}
    # Facts of the record that the manuscript states, with their source (not computed here)
    out["record"] = {"stage11_partial_scoring_records": 178, "stage11_records": 216,
                     "source": "DECISIONS.md D118 (1): the scoring run once on a copy of 178 of the 216 records",
                     "ai_use_first_commit_date": "2026-10-10", "ai_use_last_date": "2026-11-03"}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", default=os.path.join(ROOT, "results"))
    a = ap.parse_args()
    out = {"constants": constants(), "kinetics_band": kinetics_band(a.res), "runs": run_counts(a.res),
           "predictions": predictions(), "after_review": after_review(a.res)}
    json.dump(out, open(os.path.join(a.res, "manuscript_numbers.json"), "w"), indent=1, default=float)
    print(json.dumps(out, default=float)[:1500])


if __name__ == "__main__":
    main()
