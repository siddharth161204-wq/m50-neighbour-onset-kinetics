#!/usr/bin/env python3
"""Stage 3b and 3c (DECISIONS.md D27): thermophysical draws through the published two-cell solver, then the kinetics.

3b. A Latin hypercube over the roll's conductivity across and along the layers and the roll's specific heat (ranges
and sources in D27), M = 30, rng numpy.random.default_rng(20261012), written to results/stage3_thermal_draws.csv.
Each draw sets the published study's constants (lumped_two_cell.K_RADIAL, K_AXIAL and C_CELL = can 4.5 J/K + 0.056 kg
x the roll's specific heat) and runs, in a fresh process, one resolved solve of cell 2 with the published solver
(Cell2Model, refine 1, dt 0.1 s, 900 s, 0.5 s archive, two strips of 250 mW/K each, cell 1's archived T1 of 33.2 kJ,
30 s, 500 mW/K: one-way, as before) and one lumped one-way solve with the same heat capacity; both histories are
archived like the Stage 1 series (results/stage3b_series/thermal_NN.npz). The posterior-mean kinetics are then
integrated along each draw's hottest-node and lumped histories with the Stage 1 driver.

V6. Every 3b solve's energy account must close below 1e-9 of the heat taken in; for the draws with the smallest,
median and largest roll specific heat the resolved solve is repeated with both roll conductivities at 1e4 W/mK, whose
hottest node and mean must stay within 1 K of the lumped node at every archived time. Before the draws, the nominal
inputs through this harness must reproduce the published archived series of the case.

3c. Each thermal draw is paired with 7 distinct kinetic draws (numpy.random.default_rng(20261012), choice without
replacement within a thermal draw; 210 pairs, results/stage3c_pairs.csv), and each kinetic draw is integrated along
its thermal draw's hottest-node and lumped histories.

Usage:
  python3 stage3b.py --out ../results design          the thermal draws and the 3c pairs (no solve)
  python3 stage3b.py --out ../results nominal         the published case through this harness, against the archive
  python3 stage3b.py --out ../results solve [--jobs 2]   the 30 resolved and lumped solves, then V6's high-k runs
  python3 stage3b.py --out ../results kinetics [--jobs 2]   mean kinetics on each draw, and the 210 pairs of 3c
"""
import argparse, csv, json, os, sys, time
from multiprocessing import Pool
import numpy as np
from scipy.stats import qmc

HERE = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.join(HERE, "..", "external", "m50-two-cell-pilot")
sys.path.insert(0, os.path.join(PUB, "src"))

SEED, M, PAIRS_PER_DRAW = 20261012, 30, 7
RANGES = {"k_radial_W_per_mK": (0.998, 1.38), "k_axial_W_per_mK": (24.9, 25.8), "c_roll_J_per_kgK": (842.0, 1110.0)}
CASE = {"E_J": 33222.9, "tau_s": 30.0, "G_W_per_K": 0.5, "name": "two_E33223_tau30_G0.5"}
HIGH_K = 1.0e4


def published():
    import lumped_two_cell as LP
    import resolved_cell2 as RC
    return LP, RC


def design(out):
    LP, _ = published()
    m_roll = LP.M_CELL - LP.M_CAN
    u = qmc.LatinHypercube(d=len(RANGES), rng=np.random.default_rng(SEED)).random(M)
    lo = np.array([r[0] for r in RANGES.values()]); hi = np.array([r[1] for r in RANGES.values()])
    x = lo + u * (hi - lo)
    rows = []
    for i, (kr, ka, cr) in enumerate(x):
        rows.append({"thermal_draw": i + 1, "k_radial_W_per_mK": float(kr), "k_axial_W_per_mK": float(ka),
                     "c_roll_J_per_kgK": float(cr), "m_roll_kg": m_roll, "C_roll_J_per_K": float(m_roll * cr),
                     "C_cell_J_per_K": float(LP.M_CAN * LP.CP_CAN + m_roll * cr)})
    with open(os.path.join(out, "stage3_thermal_draws.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    rng = np.random.default_rng(SEED)
    pairs = []
    for r in rows:
        for k in rng.choice(np.arange(1, 201), size=PAIRS_PER_DRAW, replace=False):
            pairs.append({"thermal_draw": r["thermal_draw"], "kinetic_draw": int(k)})
    with open(os.path.join(out, "stage3c_pairs.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["thermal_draw", "kinetic_draw"]); w.writeheader(); w.writerows(pairs)
    nominal = {"k_radial_W_per_mK": LP.K_RADIAL, "k_axial_W_per_mK": LP.K_AXIAL, "C_cell_J_per_K": LP.C_CELL,
               "C_roll_J_per_K": LP.C_CELL - LP.M_CAN * LP.CP_CAN, "implied_c_roll_J_per_kgK": (LP.C_CELL - LP.M_CAN * LP.CP_CAN) / m_roll}
    return rows, pairs, nominal


def read_draws(out):
    return [{k: (int(v) if k == "thermal_draw" else float(v)) for k, v in r.items()}
            for r in csv.DictReader(open(os.path.join(out, "stage3_thermal_draws.csv")))]


def solve_one(args):
    """One resolved and one lumped solve with a draw's inputs, in a fresh process (maxtasksperchild=1)."""
    tag, kr, ka, C_cell, series_dir = args
    LP, RC = published()
    LP.K_RADIAL, LP.K_AXIAL, LP.C_CELL = kr, ka, C_cell        # before the model is built (the solver reads them there)
    t0 = time.time()
    model = RC.Cell2Model(1.0)
    t1f, _ = RC.t1_interpolator(os.path.join(PUB, "results", "t1_series", LP.series_name(CASE["E_J"], CASE["tau_s"], CASE["G_W_per_K"])))
    g = CASE["G_W_per_K"]
    res = model.run(t1f, t_end=LP.T_END, dt=0.1, g_pos=g / 2, g_neg=g / 2)
    c_be, s_be = RC.lumped_one_way(t1f, t_end=LP.T_END, dt=0.1, g_bus=g)
    ser = res["series"]
    path = os.path.join(series_dir, f"{tag}.npz")
    np.savez_compressed(path, t=ser[:, 0], T1=ser[:, 1], Tmax=ser[:, 2], Tmean=ser[:, 3], imax=ser[:, 4].astype(int),
                        t_be=s_be[::5, 0], T2_be=s_be[::5, 1])
    resid = (res["stored_J"] - res["net_in_J"]) / max(abs(res["net_in_J"]), 1e-9)
    Tl = np.interp(ser[:, 0], s_be[:, 0], s_be[:, 1])
    return {"tag": tag, "k_radial_W_per_mK": kr, "k_axial_W_per_mK": ka, "C_cell_J_per_K": C_cell,
            "C_total_model_J_per_K": 2 * float(model.C_total), "energy_residual_rel": float(resid),
            "heat_in_J": float(res["net_in_J"]), "Tmax_peak_C": float(ser[:, 2].max() - 273.15),
            "Tmean_peak_C": float(ser[:, 3].max() - 273.15), "lumped_peak_C": float(s_be[:, 1].max() - 273.15),
            "max_abs_Tmax_minus_lumped_K": float(np.abs(ser[:, 2] - Tl).max()),
            "max_abs_Tmean_minus_lumped_K": float(np.abs(ser[:, 3] - Tl).max()), "runtime_s": time.time() - t0}


def kin_one(args):
    """Integrate one kinetic draw (0 = the posterior-mean model) along one thermal draw's two histories."""
    import bcrnn, onset_kinetics as OK, stage3_draws as S
    tag, kdraw, series_dir = args
    if kdraw == 0:
        OK.KIN = bcrnn.Kinetics()
    else:
        P = S.load_particles()
        d = S.all_draws(P)[0][kdraw - 1]
        OK.KIN = S.draw_kinetics(P, *d[1:])
    out = OK.run_case(os.path.join(series_dir, f"{tag}.npz"), histories=("hottest_node", "lumped"))
    return {"tag": tag, "kinetic_draw": kdraw, **{k: v for k, v in out.items() if k != "case"}}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["design", "nominal", "solve", "kinetics"])
    ap.add_argument("--out", default="../results")
    ap.add_argument("--jobs", type=int, default=2)
    a = ap.parse_args()
    sdir = os.path.join(a.out, "stage3b_series")
    os.makedirs(sdir, exist_ok=True)
    if a.step == "design":
        rows, pairs, nominal = design(a.out)
        json.dump({"ranges": RANGES, "seed": SEED, "M": M, "pairs_per_draw": PAIRS_PER_DRAW, "nominal": nominal,
                   "case": CASE}, open(os.path.join(a.out, "stage3b_design.json"), "w"), indent=1)
        print(json.dumps({"nominal": nominal, "first_draws": rows[:3], "pairs": len(pairs)}, indent=1))
    elif a.step == "nominal":
        LP, _ = published()
        r = solve_one(("nominal_check", LP.K_RADIAL, LP.K_AXIAL, LP.C_CELL, sdir))
        new = np.load(os.path.join(sdir, "nominal_check.npz"))
        old = np.load(os.path.join(PUB, "results", "resolved_series", CASE["name"] + ".npz"))
        r["max_abs_difference_against_archive_K"] = {k: float(np.abs(new[k] - old[k]).max()) for k in ("Tmax", "Tmean", "T2_be")}
        json.dump(r, open(os.path.join(a.out, "stage3b_nominal_check.json"), "w"), indent=1)
        print(json.dumps(r, indent=1))
    elif a.step == "solve":
        draws = read_draws(a.out)
        jobs = [(f"thermal_{d['thermal_draw']:02d}", d["k_radial_W_per_mK"], d["k_axial_W_per_mK"], d["C_cell_J_per_K"], sdir)
                for d in draws if not os.path.exists(os.path.join(sdir, f"thermal_{d['thermal_draw']:02d}.npz"))]
        order = sorted(draws, key=lambda d: (d["c_roll_J_per_kgK"], d["thermal_draw"]))
        v6 = [order[0], order[len(order) // 2], order[-1]]
        jobs += [(f"highk_{d['thermal_draw']:02d}", HIGH_K, HIGH_K, d["C_cell_J_per_K"], sdir) for d in v6
                 if not os.path.exists(os.path.join(sdir, f"highk_{d['thermal_draw']:02d}.npz"))]
        logp = os.path.join(a.out, "stage3b_solves.jsonl")
        with Pool(a.jobs, maxtasksperchild=1) as pool:
            for r in pool.imap_unordered(solve_one, jobs):
                open(logp, "a").write(json.dumps(r) + "\n")
                print(f"{r['tag']}: Tmax peak {r['Tmax_peak_C']:.1f} C, lumped peak {r['lumped_peak_C']:.1f} C, "
                      f"residual {r['energy_residual_rel']:.1e}, {r['runtime_s']:.0f} s", flush=True)
    elif a.step == "kinetics":
        draws = read_draws(a.out)
        pairs = list(csv.DictReader(open(os.path.join(a.out, "stage3c_pairs.csv"))))
        jobs = [(f"thermal_{d['thermal_draw']:02d}", 0, sdir) for d in draws]
        jobs += [(f"thermal_{int(p['thermal_draw']):02d}", int(p["kinetic_draw"]), sdir) for p in pairs]
        with Pool(a.jobs) as pool:
            rows = pool.map(kin_one, jobs, chunksize=4)
        fields = list(rows[0].keys())
        for r in rows:
            fields += [k for k in r if k not in fields]
        with open(os.path.join(a.out, "stage3bc_onsets.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
        print("rows:", len(rows))
