#!/usr/bin/env python3
"""V0: does this implementation of the posterior-mean B-CRNN reproduce the paper's own DSC curves?

Simulates each submodel in a DSC ramp at 5 C/min (dimensionless amounts, no cell masses) and reports the peak heat
release rate and its temperature for every reaction, in W/g of the reaction's own basis, to compare with the paper's
Fig. 3(a) (cathode, B-CRNN mean curve), Fig. 3(e) (separator) and Fig. 4(b) (anode-electrolyte network). It also
decides the sign convention of the separator heat (DECISIONS.md D5): Fig. 3(e) shows the separator mean curve at
about -0.080 W/g near 139 C.
"""
import argparse, json, os
import numpy as np
from scipy.integrate import solve_ivp
import bcrnn

BETA = 5.0 / 60.0      # K/s


def dsc(kin, species_on, T_start_C=100.0, T_end_C=500.0, sep_mode="sign"):
    c0 = bcrnn.C0.copy()
    mask = np.zeros(bcrnn.NS, bool); mask[species_on] = True
    c0[~mask] = 0.0
    t_end = (T_end_C - T_start_C) / BETA
    Tof = lambda t: T_start_C + 273.15 + BETA * t

    def f(t, c):
        r = kin.rates(Tof(t), c[:, None])[:, 0]
        if sep_mode == "stoich":
            pass
        return kin.dcdt(r)
    sol = solve_ivp(f, (0, t_end), c0, method="BDF", rtol=1e-8, atol=1e-12, dense_output=True, max_step=5.0)
    tt = np.linspace(0, t_end, int(t_end / 2) + 1)
    C = sol.sol(tt)
    r = np.array([kin.rates(Tof(t), C[:, i:i + 1])[:, 0] for i, t in enumerate(tt)]).T
    return tt, Tof(tt) - 273.15, C, r


def peaks(TC, q, names):
    out = {}
    for j, nm in enumerate(names):
        k = int(np.argmax(np.abs(q[j])))
        out[nm] = {"peak_W_per_g": float(q[j, k]), "at_C": float(TC[k])}
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="../results"); a = ap.parse_args()
    kin = bcrnn.Kinetics()
    S = {s: i for i, s in enumerate(bcrnn.SPECIES)}
    res = {}
    # cathode
    tt, TC, C, r = dsc(kin, [S["cat1"], S["cat2"], S["cat3"]])
    q = kin.dH[:, None] * r                          # W/g of the reaction's own basis
    qc = q[7:10].sum(axis=0)
    res["cathode"] = {"sum": {"peak_W_per_g": float(qc.max()), "at_C": float(TC[np.argmax(qc)])},
                      **peaks(TC, q[7:10], ["cat1", "cat2", "cat3"])}
    hi = TC > 330
    res["cathode"]["third_peak"] = {"peak_W_per_g": float(qc[hi].max()), "at_C": float(TC[hi][np.argmax(qc[hi])])}
    # separator, both readings of the sign
    tt, TC, C, r = dsc(kin, [S["sep"]], T_end_C=200.0)
    raw_dH = kin.m["raw"]["separator_rows_mean"][5]
    v = kin.stoich[S["sep"], 10]
    q_i = -raw_dH * r[10]                 # reading (i): heat = -dH * rate (adopted)
    q_ii = raw_dH * v * r[10]             # reading (ii): heat = dH * dc/dt
    res["separator"] = {"reading_i_minus_dH_times_rate": {"peak_W_per_g": float(q_i.min()), "at_C": float(TC[np.argmin(q_i)])},
                        "reading_ii_dH_times_dcdt": {"peak_W_per_g": float(q_ii.min()), "at_C": float(TC[np.argmin(q_ii)])},
                        "paper_fig3e_mean_curve": {"peak_W_per_g": -0.080, "at_C": 139.0},
                        "integral_reading_i_J_per_g": float(np.trapezoid(q_i, tt))}
    # anode-electrolyte-SEI-binder network (combined dataset initial state, paper Fig. 2)
    tt, TC, C, r = dsc(kin, [S["ele_liq"], S["li_an"], S["binder"], S["sei"]], T_start_C=100.0, T_end_C=380.0)
    q = kin.dH[:, None] * r
    res["an_ele_network"] = peaks(TC, q[:7], list(bcrnn.AN_ELE_COLUMNS))
    res["an_ele_network"]["sum_peaks"] = {}
    qs = q[:7].sum(axis=0)
    for lo, hi_ in ((230, 275), (275, 330)):
        m = (TC >= lo) & (TC < hi_)
        res["an_ele_network"]["sum_peaks"][f"{lo}_{hi_}"] = {"peak_W_per_g": float(qs[m].max()), "at_C": float(TC[m][np.argmax(qs[m])])}
    # rate constants of the mean cathode model against Table 1 of Koenig et al., Proc. Combust. Inst. 40 (2024) 105243
    lnk = {}
    for j, TC, ref in ((7, 225.0, -4.55), (8, 275.0, -4.31), (9, 410.0, -5.16)):
        T = TC + 273.15
        lnk[bcrnn.REACTIONS[j]] = {"T_C": TC, "ln_k": float(kin.lnA[j] + kin.b[j] * np.log(T) - kin.Ea[j] / (bcrnn.R_GAS * T)),
                                   "paper_table1_mean": ref}
    res["cathode_ln_k_check"] = lnk
    os.makedirs(a.out, exist_ok=True)
    json.dump(res, open(os.path.join(a.out, "v0_dsc_check.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))
