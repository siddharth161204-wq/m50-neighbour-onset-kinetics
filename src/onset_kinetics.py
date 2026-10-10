#!/usr/bin/env python3
"""
Onset kinetics on a resolved neighbour cell, Stage 1 (passive).

Integrates published decomposition kinetics along three archived temperature histories of each case of the two-cell
study (github.com/siddharth161204-wq/m50-two-cell-pilot, v1.0.0, doi:10.5281/zenodo.23253738): the resolved hottest
node (Tmax), the resolved mean (Tmean) and the lumped neighbour (T2_be). The reaction heat does NOT feed back into the
temperature here. For each history it reports the first time the kinetic self-heating rate, q_rxn / (rho * cp),
reaches 0.15, 1 and 10 K/min, the reaction that dominates the heat at that moment, the peak rate, and the reactant
conversions at 900 s.

This is the driver of the study brief with its FILL markers resolved (DECISIONS.md D2): the kinetics are the
posterior-mean B-CRNN model of Koenig, Zhao and Deng (2025) in src/bcrnn.py, which replaces the brief's Hatchard-type
rates() and state vector, as the brief allows; everything else is kept: linear interpolation of the archived
temperature between its 0.5 s samples, implicit integration (BDF), crossing times, conversions at 900 s, CSV and JSON.
Two changes to the brief's numerics (D8): the crossing times are interpolated linearly on a 0.01 s grid instead of
being read off a 0.1 s grid, and the largest integration step is 0.25 s instead of 0.5 s.

Usage:
  python3 onset_kinetics.py --series <clone>/results/resolved_series --out ../results
  python3 onset_kinetics.py --isothermal 100 110 150 200        (prints the onset behaviour at fixed temperatures)
"""
import argparse, glob, json, os, csv
import numpy as np
from scipy.integrate import solve_ivp
import bcrnn

# ---------------- cell thermal properties: the published study's inputs/oregan2022_properties.txt and D3 ----------------
RHO = 2938.7     # kg/m3, jelly-roll effective density (PyBaMM ORegan2022, published study inputs/oregan2022_properties.txt)
CP = 950.0       # J/(kg K), the constant cell-average value both published models use for cell 2 (published D3)

KIN = bcrnn.Kinetics()
LEVELS_K_PER_MIN = (0.15, 1.0, 10.0)   # 0.15 K/min is the exotherm trigger behind T_initial in Koenig, Zhao and Deng (2025)
GRID = 0.01                            # s, evaluation grid for the self-heating rate and its crossings (D8)
MAX_STEP = 0.25                        # s, largest BDF step (half the archived sampling interval)
RTOL, ATOL = 1e-8, 1e-12


def q_vol(T, C):
    """Reaction heat per unit volume, W/m3: reactant contents per unit volume are the paper's mass fractions times RHO."""
    return RHO * KIN.q_mass(KIN.rates(T, C))


def self_heating_K_per_min(T, C):
    return q_vol(T, C) / (RHO * CP) * 60.0


def _rhs(t, c, T_of_t):
    return KIN.stoich @ KIN.rates_scalar(T_of_t(t), c)


def _jac(t, c, T_of_t):
    r = KIN.rates_scalar(T_of_t(t), c)
    J = np.zeros((bcrnn.NR, bcrnn.NS))
    for j in range(bcrnn.NR):
        if r[j] > 0.0:
            for s_, n in KIN._react[j]:
                J[j, s_] = n * r[j] / c[s_]
    return KIN.stoich @ J


def integrate_along(t, T, t_end=None, rtol=RTOL, atol=ATOL, max_step=MAX_STEP, grid=GRID, c0=None):
    """Integrate the kinetics along a prescribed history T(t) (K), linearly interpolated between samples, from the
    fresh state bcrnn.C0 (or from c0, used only by the exploratory explore_sei_storage.py).
    Returns the evaluation grid, the self-heating rate (K/min), the states on the grid, and the solver's step count."""
    t = np.asarray(t, float); T = np.asarray(T, float)
    dt0 = t[1] - t[0]
    uniform = np.allclose(np.diff(t), dt0)

    def T_of_t(tt):
        if uniform:                       # the archive's uniform 0.5 s grid: direct linear interpolation
            k = min(max(int((tt - t[0]) / dt0), 0), t.size - 2)
            f = (tt - t[k]) / dt0
            return float(T[k] + f * (T[k + 1] - T[k]))
        return float(np.interp(tt, t, T))
    t_end = t[-1] if t_end is None else t_end
    y0 = bcrnn.C0.copy() if c0 is None else np.asarray(c0, float).copy()
    sol = solve_ivp(_rhs, (t[0], t_end), y0, args=(T_of_t,), method="BDF", rtol=rtol, atol=atol,
                    dense_output=True, max_step=max_step, jac=_jac)
    if not sol.success:
        raise RuntimeError(sol.message)
    tt = np.round(np.arange(t[0], t_end + 1e-9, grid), 10)
    Y = sol.sol(tt)
    Tg = np.interp(tt, t, T)
    sh = self_heating_K_per_min(Tg, np.clip(Y, 0.0, None))
    return tt, sh, Y, Tg, int(sol.t.size)


def first_crossing(tt, rate, level):
    """First time the rate reaches the level, interpolated linearly between grid points; None if never."""
    idx = np.where(rate >= level)[0]
    if not idx.size:
        return None
    i = int(idx[0])
    if i == 0:
        return float(tt[0])
    return float(tt[i - 1] + (level - rate[i - 1]) / (rate[i] - rate[i - 1]) * (tt[i] - tt[i - 1]))


def dominant_reaction(T, c):
    by = KIN.q_mass_by_reaction(KIN.rates(np.array([T]), np.clip(c, 0, None)[:, None]))[:, 0]
    return bcrnn.REACTIONS[int(np.argmax(by))]


HISTORIES = {"hottest_node": ("t", "Tmax"), "resolved_mean": ("t", "Tmean"), "lumped": ("t_be", "T2_be")}


def run_case(path, keep_series=False, **kw):
    d = np.load(path)
    out = {"case": os.path.basename(path)[:-4]}
    series = {}
    for label, (tkey, Tkey) in HISTORIES.items():
        tt, sh, Y, Tg, nsteps = integrate_along(d[tkey], d[Tkey], **kw)
        for lv in LEVELS_K_PER_MIN:
            tc = first_crossing(tt, sh, lv)
            out[f"{label}_t_{lv}Kpm_s"] = tc
            if tc is not None:
                k = int(np.searchsorted(tt, tc))
                out[f"{label}_T_at_{lv}Kpm_C"] = float(np.interp(tc, tt, Tg) - 273.15)
                out[f"{label}_rxn_at_{lv}Kpm"] = dominant_reaction(Tg[k], Y[:, k])
            else:
                out[f"{label}_T_at_{lv}Kpm_C"] = None
                out[f"{label}_rxn_at_{lv}Kpm"] = None
        k = int(np.argmax(sh))
        out[f"{label}_peak_Kpm"] = float(sh[k])
        out[f"{label}_t_peak_s"] = float(tt[k])
        out[f"{label}_Tpeak_C"] = float(Tg.max() - 273.15)
        for s in ("sei", "li_an", "ele_liq", "cat1", "sep"):
            i = bcrnn.SPECIES.index(s)
            out[f"{label}_conv_{s}_900s"] = float(1.0 - Y[i, -1] / bcrnn.C0[i])
        out[f"{label}_bdf_steps"] = nsteps
        if keep_series:
            series[label] = (tt, sh, Tg)
    return (out, series) if keep_series else out


def isothermal_check(temps_C, hold_s=3600.0):
    """Hold the cell at fixed temperatures with fresh reactants; print the peak self-heating rate and the time to 0.15 K/min."""
    for TC in temps_C:
        t = np.array([0.0, hold_s]); T = np.array([TC + 273.15, TC + 273.15])
        tt, sh, Y, Tg, _ = integrate_along(t, T, grid=0.5)
        print(f"{TC:6.1f} C: initial {sh[0]:.4g} K/min, peak {sh.max():.4g} K/min, first 0.15 K/min at "
              f"{first_crossing(tt, sh, 0.15)} s, SEI conversion {1 - Y[4, -1] / bcrnn.C0[4]:.3f}, "
              f"layered cathode conversion {1 - Y[9, -1]:.3f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", help="folder with the archived resolved_series npz files")
    ap.add_argument("--out", default="../results")
    ap.add_argument("--isothermal", nargs="*", type=float, help="temperatures in C for the isothermal printout")
    ap.add_argument("--only", nargs="*", help="run only these case names (no extension)")
    a = ap.parse_args()
    if a.isothermal:
        isothermal_check(a.isothermal); raise SystemExit
    os.makedirs(a.out, exist_ok=True)
    files = sorted(glob.glob(os.path.join(a.series, "two_E*_tau*_G*.npz"))) + sorted(glob.glob(os.path.join(a.series, "one_E*_tau*_G*.npz")))
    if a.only:
        files = [f for f in files if os.path.basename(f)[:-4] in a.only]
    rows = []
    for f in files:
        rows.append(run_case(f))
        print(rows[-1]["case"], {k: rows[-1][k] for k in ("hottest_node_t_0.15Kpm_s", "lumped_t_0.15Kpm_s", "resolved_mean_t_0.15Kpm_s")}, flush=True)
    with open(os.path.join(a.out, "onset_results.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    with open(os.path.join(a.out, "onset_results.json"), "w") as f:
        json.dump({"levels_K_per_min": LEVELS_K_PER_MIN, "rho": RHO, "cp": CP, "grid_s": GRID, "max_step_s": MAX_STEP,
                   "rtol": RTOL, "atol": ATOL, "kinetics": "posterior-mean B-CRNN, inputs/kinetics/bcrnn_mean_model.json",
                   "reaction_masses_g_in_720g_cell": dict(zip(bcrnn.REACTIONS, KIN.mass_g.tolist())),
                   "cases": rows}, f, indent=1)
    print("wrote", len(rows), "cases to", a.out)
