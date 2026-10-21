#!/usr/bin/env python3
"""Stage 5 (version 1.2.0) checks that run before the predictions: V1, V2 and the kernel check (DECISIONS.md D41,
D44). None of them uses a temperature history of the Stage 5 configuration.

  v1        V1. (a) Every boundary path on a uniform field against the lumped formula, at the three contact
            conductances. (b) The analytic steady case: cell 1 held at a fixed temperature, the neighbour's roll
            conductivity raised to 1e4 W/mK so that it is isothermal, contact (and tabs) and room convection only;
            the resolved mean must lie within 1 % of the rise of (G T1 + hA Ta) / (G + hA). (c) The energy account of
            a passive run of the Stage 5 cell under a synthetic 10 K step of cell 1, roll at 1e4 W/mK. (d) The energy
            account of a reactive run of the Stage 5 cell with every path off, started uniformly at 150 C.
  kernel    D41. The compiled reaction sub-step against the published numpy one on synthetic node states.
  v2-arrays V2 (a) the lumped pair with the two-cell paths against the archived cell-1 histories, all 42 cases, as
            written; (b) every array of the Stage 5 class in its two-cell configuration against the published model.
  v2-passive V2 (c) passive runs of the two-cell configuration through the Stage 5 loop against the archived series
            (Stage 1's inputs), then Stage 1's onsets from the regenerated series against results/onset_results.csv.
  v2-stage1 V2 (c) Stage 1's records from the regenerated series, field by field, step counts apart.
  v2-reactive V2 (d) the reactive two-cell cases through the Stage 5 loop against the Stage 2 records: the published
            numpy kernel on the headline case, and the compiled kernel on all five cases.
  merge     results/v12_checks.json from the parts.

Usage: python3 v12_checks.py <part> [--cases ...]
"""
import os as _os
for _k in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "NUMBA_NUM_THREADS"):
    _os.environ.setdefault(_k, "1")      # D43 (4): one thread per library; set before numpy and numba load
import argparse, csv, glob, json, math, os, sys, time
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

import v12_model as V
import lumped_two_cell as LP
import bcrnn
import reactive as RX

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
PARTS = os.path.join(RES, "v12_checks")
PUB = os.path.join(V.EXT, "..")
STAGE2_CASES = ("max:10:0.5", "max:30:0.5", "max:10:0.2", "max:30:0.2", "median:30:0.5")
E = dict(zip(("min", "median", "max"), sorted(LP.E_BODY_LIST)))


def case_name(en, tau, g):
    return f"two_E{int(round(E[en]))}_tau{int(tau)}_G{g:g}"


def save(part, rec):
    os.makedirs(PARTS, exist_ok=True)
    json.dump(rec, open(os.path.join(PARTS, part + ".json"), "w"), indent=1, default=float)
    print(json.dumps(rec, indent=1, default=float)[:4000])


# ------------------------------------------------------------------------------------------------ V1
def part_v1():
    rec = {"flux_identity": {}, "analytic_steady": {}, "energy_passive": {}, "energy_reactive_no_paths": {}}
    Ta = LP.T_AMB
    worst = 0.0
    for name, hc in V.H_CONTACT.items():
        m = V.Cell2Contact(hc)
        T0, T1 = 320.0, 600.0
        Tu = np.full(m.C.size, T0)
        g = V.G_TAB["central"]
        pairs = {
            "contact_and_wedge": (2 * float(m.d_gap_unit @ (T1 - Tu)), V.g_contact(hc) * (T1 - T0)),
            "tab_cap": (2 * float((g * m.d_pos_unit) @ (T1 - Tu)), g * (T1 - T0)),
            "tab_base": (2 * float((g * m.d_neg_unit) @ (T1 - Tu)), g * (T1 - T0)),
            "room_convection": (2 * float(m.d_conv_unit @ (Tu - Ta)), LP.H_CONV * V.A_CONV * (T0 - Ta)),
            "radiation_from_cell1": (2 * float(m.g_rad.sum() * (T1 ** 4 - Ta ** 4)),
                                     LP.EPS ** 2 * LP.SIGMA * V.F_TOUCH * LP.A_LAT * (T1 ** 4 - Ta ** 4)),
            "radiation_to_room": (2 * float(np.sum(m.w_rad * (Tu ** 4 - Ta ** 4))),
                                  LP.EPS * LP.SIGMA * LP.A_CELL * (T0 ** 4 - Ta ** 4)),
            "heat_capacity": (2 * float(m.C.sum()), LP.C_CELL),
        }
        rel = {k: abs(a - b) / abs(b) for k, (a, b) in pairs.items()}
        worst = max(worst, max(rel.values()))
        rec["flux_identity"][name] = {"h_c_W_m2K": hc, "G_contact_W_K": V.g_contact(hc), "relative_difference": rel,
                                      "geometry": m.geom, "mesh": m.mesh_info,
                                      "contact_split": V.contact_split(hc)}
    rec["flux_identity_worst"] = worst
    rec["flux_identity_pass"] = worst < 1e-12
    # (b) analytic steady case
    worst_b = 0.0
    T1 = 373.15
    for name, hc in V.H_CONTACT.items():
        m = V.Cell2Contact(hc, k_radial=1e4, k_axial=1e4)
        for conn in ("none",) + V.CONNECTIONS:
            g_pos, g_neg = (0.0, 0.0) if conn == "none" else V.tabs(conn, V.G_TAB["central"])
            d_link = m.d_gap_unit + g_pos * m.d_pos_unit + g_neg * m.d_neg_unit
            A = (m.K + sp.diags(m.d_conv_unit + d_link)).tocsc()
            b = m.d_conv_unit * Ta + d_link * T1
            T = spla.spsolve(A, b)
            G = V.g_contact(hc) + g_pos + g_neg
            hA = LP.H_CONV * V.A_CONV
            T2 = (G * T1 + hA * Ta) / (G + hA)
            Tmean = float(m.C @ T) / m.C_total
            err = (Tmean - T2) / (T2 - Ta)
            spread = (float(T.max() - T.min())) / (T2 - Ta)
            worst_b = max(worst_b, abs(err))
            rec["analytic_steady"][f"{name}_{conn}"] = {"T1_C": T1 - 273.15, "analytic_T2_C": T2 - 273.15,
                                                        "resolved_mean_C": Tmean - 273.15,
                                                        "error_of_rise": err, "max_minus_min_over_rise": spread}
    rec["analytic_steady_worst"] = worst_b
    rec["analytic_steady_pass"] = worst_b < 0.01
    # (c) energy account, passive, synthetic 10 K step of cell 1 held for 100 s; only the account is recorded.
    # With the published roll conductivities, and (for the record) with the roll at 1e4 W/mK, where the stiffer
    # system carries more round-off.
    rec["energy_passive_isothermal_roll"] = {}
    for label, kk in (("published_roll", None), ("isothermal_roll", 1e4)):
        m = V.Cell2Contact(V.H_CONTACT["central"], k_radial=kk, k_axial=kk)
        for conn in V.CONNECTIONS:
            g_pos, g_neg = V.tabs(conn, V.G_TAB["central"])
            r = V.run_resolved(m, lambda t: Ta + 10.0, g_pos, g_neg, reaction=False, t_end=100.0, keep_series=False)
            target = rec["energy_passive"] if label == "published_roll" else rec["energy_passive_isothermal_roll"]
            target[conn] = {"residual_rel": r["energy_residual_rel"], "stored_J": r["stored_J"],
                            "net_in_J": r["net_in_J"]}
    # (d) reactive, every path off, uniform start at 150 C (the ambient argument sets the initial field only)
    m = V.Cell2Contact(V.H_CONTACT["central"])
    for k in ("d_conv_unit", "d_gap_unit", "d_pos_unit", "d_neg_unit", "g_rad", "w_rad"):
        setattr(m, k, np.zeros_like(getattr(m, k)))
    t0 = time.time()
    r = V.run_resolved(m, lambda t: 423.15, 0.0, 0.0, t_amb=423.15, t_end=60.0, keep_series=False)
    rec["energy_reactive_no_paths"] = {"residual_rel": r["energy_residual_rel"], "in_rxn_J": r["energy_J"]["in_rxn"],
                                       "stored_J": r["stored_J"], "peak_C": r["peak"]["Tmax_C"], "steps": r["steps"],
                                       "wall_s": time.time() - t0}
    rec["energy_pass"] = (max(abs(v["residual_rel"]) for v in rec["energy_passive"].values()) < 1e-9
                          and abs(rec["energy_reactive_no_paths"]["residual_rel"]) < 1e-9)
    save("v1", rec)


# ------------------------------------------------------------------------------------------------ kernel (D41)
def part_kernel():
    import v12_kernel as KN
    rng = np.random.default_rng(20261021)
    kin = bcrnn.Kinetics()
    out = {}
    worst_T = worst_c = 0.0
    for label, N, hot, power in (("cool", 20000, 120.0, 4), ("warm", 4000, 250.0, 6), ("hot", 1000, 330.0, 8)):
        m = np.full(N, LP.M_CELL / N); C = np.full(N, LP.C_CELL / N)
        T = 298.15 + rng.random(N) ** power * hot
        c = bcrnn.fresh_state(N) * (0.3 + 0.7 * rng.random((bcrnn.NS, N)))
        c[:, :3] = 0.0
        loc = RX.LocalKinetics(kin, m, C)
        fk = KN.FastKinetics(kin, m, C)
        R0, H0 = fk.start(T, c)
        r0n, H0n = loc.heating(T, c)
        rec = {"n_nodes": N, "rates_max_rel_diff": float(np.max(np.abs(R0 - r0n) / np.maximum(np.abs(r0n), 1e-300))),
               "heating_max_rel_diff": float(np.max(np.abs(H0 - H0n) / np.maximum(np.abs(H0n), 1e-300)))}
        for dt in (0.1, 0.0125):
            Tn, cn, ni = loc.step(T, c, dt)
            Tf, cf, nf = fk.step(T, c, R0, H0, dt)
            dT, dc = float(np.abs(Tn - Tf).max()), float(np.abs(cn - cf).max())
            worst_T, worst_c = max(worst_T, dT), max(worst_c, dc)
            rec[f"dt_{dt}"] = {"implicit_numpy": ni, "implicit_numba": nf, "T_max_abs_diff_K": dT, "c_max_abs_diff": dc}
        out[label] = rec
    out["worst_T_K"], out["worst_c"] = worst_T, worst_c
    save("kernel", out)


# ------------------------------------------------------------------------------------------------ V2
def part_v2_arrays():
    rec = {"lumped_pair": {}, "arrays": {}}
    n_same = n = 0
    worst = 0.0
    for en in ("min", "median", "max"):
        for tau in LP.TAU_REL_LIST:
            for g in LP.G_BUS_LIST:
                rows, _, _ = V.lumped_pair(E[en], tau, g, LP.G_GAP, LP.F_VIEW, LP.A_RAD)
                text = ["t_s,T1_C,T2_lumped_C"] + [f"{a:.1f},{b:.4f},{c:.4f}" for a, b, c in rows]
                arch = open(os.path.join(PUB, "results", "t1_series", LP.series_name(E[en], tau, g))).read().splitlines()
                same = text == arch
                n += 1; n_same += same
                ser = []
                LP.run(E[en], tau, g, series=ser)
                worst = max(worst, max(abs(a[1] - b[1]) + abs(a[2] - b[2]) for a, b in zip(rows, ser)))
    rec["lumped_pair"] = {"cases": n, "identical_to_archived_csv": n_same, "max_abs_diff_vs_published_run_K": worst}
    from resolved_cell2 import Cell2Model
    pub = Cell2Model(1.0)
    mine = V.Cell2Contact(geometry="two_cell")
    diffs = {}
    for k in ("C", "w_vol", "d_conv_unit", "d_gap_unit", "d_pos_unit", "d_neg_unit", "g_rad", "w_rad"):
        a, b = getattr(mine, k), getattr(pub, k)
        diffs[k] = float(np.abs(a - b).max()) if a.shape == b.shape else "shape differs"
    dK = (mine.K - pub.K)
    diffs["K"] = float(abs(dK).max()) if dK.nnz else 0.0
    diffs["n_nodes"] = [int(mine.C.size), int(pub.C.size)]
    rec["arrays"] = diffs
    rec["pass"] = (n_same == n and all((v == 0.0) for k, v in diffs.items() if k != "n_nodes"))
    save("v2_arrays", rec)


def _passive_case(spec, model_kind):
    en, tau, g = spec.split(":"); tau, g = float(tau), float(g)
    name = case_name(en, tau, g)
    t1f, _ = __import__("resolved_cell2").t1_interpolator(os.path.join(PUB, "results", "t1_series", LP.series_name(E[en], tau, g)))
    if model_kind == "published":
        from resolved_cell2 import Cell2Model
        model = Cell2Model(1.0)
    else:
        model = V.Cell2Contact(geometry="two_cell")
    r = V.run_resolved(model, t1f, g / 2, g / 2, reaction=False, record_dt=0.5, kernel="numpy")
    lp = V.run_lumped(t1f, g, reaction=False, record_dt=0.5, kernel="numpy")
    s = r["series"]
    return name, s, lp["series"]


def part_v2_passive(cases):
    import onset_kinetics as OK
    rec = {}
    onset_rows = {row["case"]: row for row in csv.DictReader(open(os.path.join(RES, "onset_results.csv")))}
    outdir = os.path.join(PARTS, "v2_series"); os.makedirs(outdir, exist_ok=True)
    for spec in cases:
        name, s, ls = _passive_case(spec, "stage5_class")
        arch = np.load(os.path.join(PUB, "results", "resolved_series", name + ".npz"))
        n = min(len(arch["t"]), len(s))
        d = {"t_grid_identical": bool(np.array_equal(s[:n, 0], arch["t"][:n])),
             "Tmax_max_abs_K": float(np.abs(s[:n, 2] - arch["Tmax"][:n]).max()),
             "Tmean_max_abs_K": float(np.abs(s[:n, 3] - arch["Tmean"][:n]).max()),
             "T2_be_max_abs_K": float(np.abs(ls[:len(arch["T2_be"]), 1] - arch["T2_be"]).max()),
             "imax_identical": bool(np.array_equal(s[:n, 4].astype(int), arch["imax"][:n]))}
        path = os.path.join(outdir, name + ".npz")
        np.savez_compressed(path, t=s[:, 0], T1=s[:, 1], Tmax=s[:, 2], Tmean=s[:, 3], imax=s[:, 4].astype(int),
                            t_be=ls[:, 0], T2_be=ls[:, 1])
        row = OK.run_case(path)
        ref = onset_rows[name]
        worst = 0.0
        labels_same = True
        for k, v in row.items():
            if k == "case":
                continue
            rv = ref.get(k, "")
            if isinstance(v, str) or (v is None) or rv in ("", None):
                same = (str(v) if v is not None else "") == (rv or "")
                labels_same &= same
                continue
            worst = max(worst, abs(float(v) - float(rv)) / max(abs(float(rv)), 1e-12))
        d["stage1_fields_max_rel_diff"] = worst
        d["stage1_labels_and_empty_fields_identical"] = labels_same
        d["stage1_headline"] = {k: row[k] for k in ("hottest_node_t_0.15Kpm_s", "lumped_t_0.15Kpm_s", "hottest_node_T_at_0.15Kpm_C")}
        rec[name] = d
        print(name, d, flush=True)
    save("v2_passive_" + "_".join(c.replace(":", "-") for c in cases), rec)


def part_v2_stage1():
    """Stage 1's records from the series regenerated by v2-passive, field by field: the onsets and their
    temperatures, the peaks and the conversions, apart from the integrator's step counts, which are reported
    separately (a series that differs at 1e-12 K lets BDF choose a few different steps)."""
    import onset_kinetics as OK
    ref_rows = {row["case"]: row for row in csv.DictReader(open(os.path.join(RES, "onset_results.csv")))}
    rec = {}
    for path in sorted(glob.glob(os.path.join(PARTS, "v2_series", "*.npz"))):
        name = os.path.basename(path)[:-4]
        row, ref = OK.run_case(path), ref_rows[name]
        worst, worst_key, steps, labels = 0.0, None, {}, True
        for k, v in row.items():
            if k == "case":
                continue
            rv = ref.get(k, "")
            if k.endswith("_bdf_steps"):
                steps[k] = [v, int(float(rv))]
                continue
            if v is None or isinstance(v, str) or rv in ("", None):
                labels &= (str(v) if v is not None else "") == (rv or "")
                continue
            d = abs(float(v) - float(rv)) / max(abs(float(rv)), 1e-12)
            if d > worst:
                worst, worst_key = d, k
        onset_keys = [k for k in row if "_t_" in k and k.endswith("Kpm_s")]
        same_digits = all((row[k] is None and ref[k] == "") or (row[k] is not None and ref[k] != "" and
                          round(float(row[k]), 2) == round(float(ref[k]), 2)) for k in onset_keys)
        rec[name] = {"max_rel_diff_excluding_step_counts": worst, "field": worst_key, "labels_identical": labels,
                     "onset_times_identical_to_0.01_s": same_digits, "bdf_steps_new_vs_registered": steps}
        print(name, rec[name], flush=True)
    save("v2_stage1", rec)


def part_v2_reactive(cases, kernel):
    from resolved_cell2 import t1_interpolator
    rec = {}
    model = V.Cell2Contact(geometry="two_cell")
    for spec in cases:
        en, tau, g = spec.split(":"); tau, g = float(tau), float(g)
        name = case_name(en, tau, g)
        t1f, _ = t1_interpolator(os.path.join(PUB, "results", "t1_series", LP.series_name(E[en], tau, g)))
        t0 = time.time()
        r = V.run_resolved(model, t1f, g / 2, g / 2, kernel=kernel)
        lr = V.run_lumped(t1f, g, kernel=kernel)
        ref = json.load(open(os.path.join(RES, "stage2", name + ".json")))
        arch = np.load(os.path.join(RES, "stage2", name + ".npz"))
        s = r["series"]
        n = min(len(s), len(arch["t"]))
        rr = ref["resolved"]
        d = {"kernel": kernel, "wall_s": time.time() - t0,
             "cross_s": {k: [r["cross_s"][k], rr["cross_s"][k]] for k in rr["cross_s"]},
             "peak_Tmax_C": [r["peak"]["Tmax_C"], rr["peak"]["Tmax_C"]],
             "peak_Tmean_C": [r["peak"]["Tmean_C"], rr["peak"]["Tmean_C"]],
             "steps": [r["steps"], rr["steps"]], "rejected": [r["rejected"], rr["rejected"]],
             "max_implicit_nodes": [r["max_implicit_nodes"], rr["max_implicit_nodes"]],
             "energy_residual_rel": [r["energy_residual_rel"], rr["energy_residual_rel"]],
             "in_rxn_J": [r["energy_J"]["in_rxn"], rr["energy_J"]["in_rxn"]],
             "series_Tmax_max_abs_K": float(np.abs(s[:n, 2] - arch["Tmax"][:n]).max()),
             "series_Tmean_max_abs_K": float(np.abs(s[:n, 3] - arch["Tmean"][:n]).max()),
             "series_length": [len(s), len(arch["t"])],
             "lumped_peak_C": [lr["peak"]["T_C"], ref["lumped_reactive"]["peak"]["T_C"]],
             "lumped_cross_s": [lr["cross_s"], ref["lumped_reactive"]["cross_s"]],
             "lumped_reaction_heat_J": [lr["reaction_heat_J"], ref["lumped_reactive"]["reaction_heat_J"]],
             "lumped_series_max_abs_K": float(np.abs(lr["series"][:, 1] - arch["T_lumped"][:len(lr["series"])]).max())}
        d["identical"] = (d["series_Tmax_max_abs_K"] == 0.0 and d["series_Tmean_max_abs_K"] == 0.0
                          and all(a == b for a, b in d["cross_s"].values()) and d["lumped_series_max_abs_K"] == 0.0)
        rec[name] = d
        print(name, json.dumps(d, default=float), flush=True)
    save(f"v2_reactive_{kernel}_" + "_".join(c.replace(":", "-") for c in cases), rec)


def part_merge():
    out = {}
    for f in sorted(glob.glob(os.path.join(PARTS, "*.json"))):
        out[os.path.basename(f)[:-5]] = json.load(open(f))
    json.dump(out, open(os.path.join(RES, "v12_checks.json"), "w"), indent=1, default=float)
    print("merged", list(out))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("part", choices=["v1", "kernel", "v2-arrays", "v2-passive", "v2-stage1", "v2-reactive", "merge"])
    ap.add_argument("--cases", nargs="*")
    ap.add_argument("--kernel", default="numba")
    a = ap.parse_args()
    if a.part == "v1":
        part_v1()
    elif a.part == "kernel":
        part_kernel()
    elif a.part == "v2-arrays":
        part_v2_arrays()
    elif a.part == "v2-passive":
        part_v2_passive(a.cases or ["max:30:0.5", "max:10:0.5", "median:30:0.5"])
    elif a.part == "v2-stage1":
        part_v2_stage1()
    elif a.part == "v2-reactive":
        part_v2_reactive(a.cases or list(STAGE2_CASES), a.kernel)
    else:
        part_merge()
