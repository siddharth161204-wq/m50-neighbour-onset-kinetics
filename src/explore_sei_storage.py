#!/usr/bin/env python3
"""Exploratory, not pre-registered (DECISIONS.md D19): how much of Stage 1 rests on a fresh SEI.

Stage 1 starts every history from the fresh state of the source paper's Fig. 2 (SEI 0.15), as the paper's own ARC
simulation does. The posterior-mean SEI reaction (Ea 43.8 kJ/mol, order 0.16) is active even at 25 C, so this script
first stores the neighbour isothermally at 25 C for 0 to 30 days under the same kinetics, then repeats the Stage 1
integration from each stored state along chosen archived histories: the headline cases (33.2 kJ, 500 mW/K), the cases
where only the hottest node starts at 100 mW/K (21.5 kJ) and the P4 cases (33.2 kJ at 200 mW/K, 21.5 kJ at 500 mW/K),
30 s release. It also records the temperature at which a 1 K/s ramp from 25 C first self-heats at 0.15 K/min.
No kinetic parameter is changed; only the initial state differs. Nothing else in the study uses these results.

Usage: python3 explore_sei_storage.py --series ../external/m50-two-cell-pilot/results/resolved_series --out ../results
"""
import argparse, json, os
import numpy as np
from scipy.integrate import solve_ivp
import bcrnn
import onset_kinetics as OK

DAYS = (0, 1, 3, 7, 30)
CASES = ("two_E33223_tau10_G0.5", "two_E33223_tau30_G0.5", "two_E21495_tau30_G0.1", "two_E33223_tau30_G0.2",
         "two_E21495_tau30_G0.5")
I_SEI = bcrnn.SPECIES.index("sei")


def stored_state(days, T_C=25.0):
    if days == 0:
        return bcrnn.C0.copy()
    T = T_C + 273.15
    sol = solve_ivp(lambda t, c: OK._rhs(t, c, lambda _t: T), (0.0, days * 86400.0), bcrnn.C0.copy(), method="BDF",
                    rtol=1e-9, atol=1e-14, jac=lambda t, c: OK._jac(t, c, lambda _t: T))
    if not sol.success:
        raise RuntimeError(sol.message)
    return np.clip(sol.y[:, -1], 0.0, None)


def ramp_onset(c0, beta=1.0):
    t = np.arange(0.0, 400.0 + 1e-9, 0.5)
    T = 298.15 + beta * t
    tt, sh, Y, Tg, _ = OK.integrate_along(t, T, c0=c0)
    tc = OK.first_crossing(tt, sh, 0.15)
    if tc is None:
        return None, None
    k = int(np.searchsorted(tt, tc))
    return float(np.interp(tc, tt, Tg) - 273.15), OK.dominant_reaction(Tg[k], Y[:, k])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", default="../external/m50-two-cell-pilot/results/resolved_series")
    ap.add_argument("--out", default="../results")
    a = ap.parse_args()
    res = {"note": "exploratory, not pre-registered (DECISIONS.md D19); storage at 25 C under the same posterior-mean "
                   "kinetics, then Stage 1 from the stored state; fresh = 0 days, as in Stage 1",
           "storage": {}}
    for d in DAYS:
        c0 = stored_state(d)
        sh25 = float(OK.self_heating_K_per_min(np.array([298.15]), c0[:, None])[0])
        Tr, rr = ramp_onset(c0)
        rec = {"sei_converted": float(1.0 - c0[I_SEI] / bcrnn.C0[I_SEI]),
               "state": dict(zip(bcrnn.SPECIES, c0.tolist())),
               "self_heating_at_25C_K_per_min": sh25,
               "ramp_1Kps_T_at_0.15Kpm_C": Tr, "ramp_1Kps_rxn_at_0.15Kpm": rr, "cases": {}}
        for case in CASES:
            r = OK.run_case(os.path.join(a.series, case + ".npz"), c0=c0)
            rec["cases"][case] = {f"{h}_{q}": r[f"{h}_{q}"] for h in ("hottest_node", "lumped", "resolved_mean")
                                  for q in ("t_0.15Kpm_s", "T_at_0.15Kpm_C", "rxn_at_0.15Kpm", "t_1.0Kpm_s", "peak_Kpm")}
        res["storage"][f"{d}_days"] = rec
        hl = rec["cases"]["two_E33223_tau30_G0.5"]
        print(f"{d:3d} days: SEI converted {rec['sei_converted']:.3f}, self-heating at 25 C {sh25:.2e} K/min, "
              f"1 K/s ramp starts at {Tr} C ({rr}); 33.2 kJ 30 s 500 mW/K: hottest {hl['hottest_node_t_0.15Kpm_s']} s "
              f"at {hl['hottest_node_T_at_0.15Kpm_C']} C ({hl['hottest_node_rxn_at_0.15Kpm']}), lumped {hl['lumped_t_0.15Kpm_s']} s "
              f"at {hl['lumped_T_at_0.15Kpm_C']} C ({hl['lumped_rxn_at_0.15Kpm']})", flush=True)
    json.dump(res, open(os.path.join(a.out, "explore_sei_storage.json"), "w"), indent=1, default=float)
    print("wrote", os.path.join(a.out, "explore_sei_storage.json"))
