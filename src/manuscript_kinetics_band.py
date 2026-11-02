#!/usr/bin/env python3
"""The three submodels' heat release rate against temperature, for the manuscript's Figure 1(b).

Each of the kinetic model's three submodels (the seven anode-electrolyte-SEI-binder reactions, the three NCM811
cathode reactions and the separator's melting; `bcrnn.py`) is integrated in a linear temperature ramp of 5 K/min from
25 C to 400 C, from the fresh state, at the posterior mean (`inputs/kinetics/bcrnn_mean_model.json`) and at each of
Stage 3's 200 joint posterior draws (`results/stage3_draw_indices.csv`, `stage3_draws.py`). The ramp is the source's
DSC rate (`v0_dsc_check.py`). The heat is per kilogram of cell, at the reactant mass fractions the model uses in the
neighbour (`bcrnn.Kinetics.h_mass`), so the curves are the source terms the cell model integrates, not DSC signals.
The three submodels share no species, so one integration of the whole network gives each submodel's own curve.

Writes results/manuscript_kinetics_band.csv: temperature, then for each submodel the posterior mean's rate and the
2.5, 50 and 97.5 percentiles over the 200 draws at that temperature (W/kg; the separator's is negative, heat absorbed).
Usage: python3 manuscript_kinetics_band.py --out ../results [--workers 2]
"""
import argparse, csv, os
from multiprocessing import Pool
import numpy as np
from scipy.integrate import solve_ivp
import bcrnn
import stage3_draws as D

BETA_K_S = 5.0 / 60.0
T0_C, T1_C, DT_C = 25.0, 400.0, 0.5
GROUPS = {"anode_electrolyte": list(range(0, 7)), "cathode": [7, 8, 9], "separator": [10]}
HERE = os.path.dirname(os.path.abspath(__file__))


def ramp(kin):
    """Heat release rate of each submodel (W/kg of cell) on the temperature grid."""
    t_end = (T1_C - T0_C) / BETA_K_S
    Tof = lambda t: T0_C + 273.15 + BETA_K_S * t

    def f(t, c):
        return kin.dcdt(kin.rates(Tof(t), c[:, None])[:, 0])

    sol = solve_ivp(f, (0.0, t_end), bcrnn.C0.copy(), method="BDF", rtol=1e-8, atol=1e-12, dense_output=True,
                    max_step=5.0)
    assert sol.success, sol.message
    TC = np.arange(T0_C, T1_C + 1e-9, DT_C)
    tt = (TC - T0_C) / BETA_K_S
    C = np.clip(sol.sol(tt), 0.0, None)
    r = kin.rates(TC + 273.15, C)                       # (NR, N)
    q = kin.q_mass_by_reaction(r)                       # W/kg, (NR, N)
    return TC, {g: q[idx].sum(axis=0) for g, idx in GROUPS.items()}


def one_draw(row):
    P = D.load_particles()
    kin = D.draw_kinetics(P, int(row["an_ele_column"]), int(row["separator_column"]), int(row["ncm811_column"]))
    return int(row["draw"]), ramp(kin)[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "..", "results"))
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    TC, mean = ramp(bcrnn.Kinetics())
    rows = list(csv.DictReader(open(os.path.join(a.out, "stage3_draw_indices.csv"))))
    assert len(rows) == 200
    with Pool(a.workers) as pool:
        res = dict(pool.map(one_draw, rows))
    cols = ["T_C"]
    data = [TC]
    for g in GROUPS:
        Q = np.array([res[d][g] for d in sorted(res)])       # (200, N)
        p = np.percentile(Q, [2.5, 50.0, 97.5], axis=0)
        cols += [f"{g}_mean", f"{g}_p2.5", f"{g}_p50", f"{g}_p97.5"]
        data += [mean[g], p[0], p[1], p[2]]
    with open(os.path.join(a.out, "manuscript_kinetics_band.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for i in range(len(TC)):
            w.writerow([f"{TC[i]:.1f}"] + [f"{x[i]:.6e}" for x in data[1:]])
    for g in GROUPS:
        k = int(np.argmax(np.abs(mean[g])))
        print(f"{g}: posterior mean peak {mean[g][k]:.1f} W/kg at {TC[k]:.1f} C")


if __name__ == "__main__":
    main()
