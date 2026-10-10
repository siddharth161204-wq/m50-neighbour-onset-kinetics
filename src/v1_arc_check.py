#!/usr/bin/env python3
"""V1: reproduce the source paper's own onset behaviour with this implementation, before any case is run.

(a) Isothermal table: the self-heating rate of the paper's 720 g cell (Table 1) at fixed temperatures with fresh
    reactants, to compare with the SEI and anode-electrolyte curves of the paper's Fig. A.1(a), and the same table
    for the LG M50 neighbour (cp 950 J/kgK), with the time to 0.15 K/min during a one-hour hold.
(b) ARC test: the heat-wait-seek procedure of the paper's Section 2.7 applied to its 720 g cell with the
    posterior-mean kinetics. T_in is the battery temperature at which the seek first finds a self-heating rate of
    0.15 C/min; T_on the temperature at which the self-heating rate reaches 1 C/min (the paper's ISC trigger).
    Acceptance (brief, V1): T_in within the paper's two-sigma band of the main-cluster mean, 169.0 to 198.0 C.

Heat-wait-seek details not given in the paper are fixed in DECISIONS.md D6: the chamber ramps at 1 C/min from the
battery temperature until the battery reaches the target, 5 C above the previous one; wait 30 min; seek 10 min.
Sensitivity runs vary the ramp (0.5 and 2 C/min) and the seek (5 and 20 min).
"""
import argparse, json, os
import numpy as np
from scipy.integrate import solve_ivp
import bcrnn

M_KG, CP = bcrnn.M_REF_G / 1e3, bcrnn.CP_REF          # 0.720 kg, 1100 J/kgK
H, A = 25.0, 0.04                                      # W/(m2 K), m2 (Table 1)
MCP = M_KG * CP


def self_heating(kin, T, c, cp=CP):
    """K/s from reaction heat alone, per unit cell mass (paper Eq. 16 and 20)."""
    r = kin.rates(np.atleast_1d(T), np.asarray(c).reshape(bcrnn.NS, -1))
    return kin.q_mass(r) / cp


def arc_test(kin, ramp_C_per_min=1.0, wait_min=30.0, seek_min=10.0, step_C=5.0, trigger=0.15, isc_trigger=1.0,
             T_start_C=25.0, T_max_C=400.0, record=False):
    beta = ramp_C_per_min / 60.0
    y = np.concatenate([[T_start_C + 273.15], bcrnn.C0.copy()])
    t = 0.0
    T_goal = T_start_C + step_C + 273.15
    trace = [] if record else None
    opts = dict(method="BDF", rtol=1e-9, atol=1e-12)

    def adiabatic(tt, yy):
        r = kin.rates(np.array([yy[0]]), yy[1:, None])[:, 0]
        return np.concatenate([[kin.q_mass(r[:, None])[0] / CP], kin.dcdt(r)])

    def rate_event(level):
        def ev(tt, yy):
            return self_heating(kin, yy[0], yy[1:])[0] - level / 60.0
        ev.terminal, ev.direction = True, 1
        return ev

    while y[0] < T_max_C + 273.15:
        # HEAT: the chamber ramps from the battery temperature until the battery reaches the target
        T_arc0, t0 = y[0], t

        def heat(tt, yy):
            r = kin.rates(np.array([yy[0]]), yy[1:, None])[:, 0]
            T_arc = T_arc0 + beta * (tt - t0)
            dT = (kin.q_mass(r[:, None])[0] * M_KG + H * A * (T_arc - yy[0])) / MCP
            return np.concatenate([[dT], kin.dcdt(r)])

        def reached(tt, yy):
            return yy[0] - T_goal
        reached.terminal, reached.direction = True, 1
        if y[0] < T_goal:
            sol = solve_ivp(heat, (t, t + 5e5), y, events=reached, max_step=60.0, **opts)
            if record:
                trace += [("heat", float(a), float(b)) for a, b in zip(sol.t[::5], sol.y[0, ::5])]
            t, y = sol.t[-1], sol.y[:, -1]
        # WAIT (adiabatic)
        sol = solve_ivp(adiabatic, (t, t + wait_min * 60.0), y, max_step=60.0, **opts)
        t, y = sol.t[-1], sol.y[:, -1]
        # SEEK (adiabatic), with the exotherm trigger; a rate already above the trigger when the seek opens counts
        already = self_heating(kin, y[0], y[1:])[0] >= trigger / 60.0
        if not already:
            ev = rate_event(trigger)
            sol = solve_ivp(adiabatic, (t, t + seek_min * 60.0), y, events=ev, max_step=30.0, **opts)
            t, y = sol.t[-1], sol.y[:, -1]
        if already or sol.status == 1:
            T_in = y[0]
            t_in = t
            # EXOTHERM (adiabatic tracking) until the self-heating rate reaches the ISC trigger
            ev2 = rate_event(isc_trigger)
            sol = solve_ivp(adiabatic, (t, t + 1e7), y, events=ev2, max_step=600.0, **opts)
            T_on = sol.y[0, -1] if sol.status == 1 else None
            ev3 = rate_event(60.0)
            sol3 = solve_ivp(adiabatic, (sol.t[-1], sol.t[-1] + 1e7), sol.y[:, -1], events=ev3, max_step=600.0, **opts)
            T_1Cps = sol3.y[0, -1] if sol3.status == 1 else None
            conv = {s: float(1 - y[1 + i] / bcrnn.C0[i]) for i, s in enumerate(bcrnn.SPECIES) if bcrnn.C0[i] > 0}
            return {"T_in_C": float(T_in - 273.15), "t_in_h": float(t_in / 3600), "T_on_C": None if T_on is None else float(T_on - 273.15),
                    "t_on_h": float(sol.t[-1] / 3600), "T_at_1_C_per_s_C": None if T_1Cps is None else float(T_1Cps - 273.15),
                    "conversion_at_T_in": conv, "trace": trace}
        T_goal += step_C
    return {"T_in_C": None}


def isothermal_table(kin, temps_C, cp, hold_s=3600.0):
    rows = []
    for TC in temps_C:
        T = TC + 273.15
        r0 = kin.rates(np.array([T]), bcrnn.C0[:, None])
        by = kin.q_mass_by_reaction(r0)[:, 0] / cp * 60.0
        rate0 = by.sum()

        def f(tt, c):
            r = kin.rates(np.array([T]), c[:, None])[:, 0]
            return kin.dcdt(r)
        sol = solve_ivp(f, (0, hold_s), bcrnn.C0.copy(), method="BDF", rtol=1e-9, atol=1e-13, dense_output=True)
        tt = np.linspace(0, hold_s, 7201)
        C = sol.sol(tt)
        sh = kin.q_mass(kin.rates(np.full(tt.size, T), C)) / cp * 60.0
        idx = np.where(sh >= 0.15)[0]
        rows.append({"T_C": TC, "initial_K_per_min": float(rate0), "peak_K_per_min": float(sh.max()),
                     "first_0.15_s": float(tt[idx[0]]) if idx.size else None,
                     "by_reaction_K_per_min": {n: float(v) for n, v in zip(bcrnn.REACTIONS, by)},
                     "sei_conversion_1h": float(1 - C[4, -1] / bcrnn.C0[4])})
    return rows


def onset_temperature(kin, cp, level_K_per_min, T_lo_C=25.0, T_hi_C=400.0, step=0.01):
    """Lowest temperature at which FRESH reactants self-heat at the given rate (upward scan, 0.01 K)."""
    TC = np.arange(T_lo_C, T_hi_C, step)
    c = np.repeat(bcrnn.C0[:, None], TC.size, axis=1)
    v = kin.q_mass(kin.rates(TC + 273.15, c)) / cp * 60.0
    idx = np.where(v >= level_K_per_min)[0]
    return float(TC[idx[0]]) if idx.size else None


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="../results")
    ap.add_argument("--sensitivity", action="store_true")
    a = ap.parse_args()
    kin = bcrnn.Kinetics()
    out = {"cell": {"M_kg": M_KG, "cp": CP, "h": H, "A": A}}
    # (a) isothermal: the paper's cell, compared with Fig. A.1(a) at low temperature, and the M50 neighbour
    temps = [25, 50, 75, 100, 105, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 220, 250]
    out["isothermal_paper_cell"] = isothermal_table(kin, temps, CP)
    out["isothermal_m50"] = isothermal_table(kin, temps, 950.0)
    out["fresh_onset_temperature_C"] = {
        "paper_cell": {str(lv): onset_temperature(kin, CP, lv) for lv in (0.15, 1.0, 10.0)},
        "m50_cp950": {str(lv): onset_temperature(kin, 950.0, lv) for lv in (0.15, 1.0, 10.0)},
        "note": "fresh reactants at a fixed temperature; above about 140 C the instantaneous rate of fresh reactants is dominated by the separator's endothermic melting, so only the 0.15 K/min value is a meaningful fresh onset; see the one-hour hold columns for the others"}
    # (b) the ARC test of the paper, base settings (D6)
    base = arc_test(kin, record=True)
    out["arc_base"] = {k: v for k, v in base.items() if k != "trace"}
    out["arc_base"]["settings"] = {"ramp_C_per_min": 1.0, "wait_min": 30.0, "seek_min": 10.0, "step_C": 5.0}
    out["acceptance"] = {"band_C": [169.0, 198.0], "T_in_C": base["T_in_C"],
                         "pass": base["T_in_C"] is not None and 169.0 <= base["T_in_C"] <= 198.0}
    if a.sensitivity:
        sens = []
        for ramp in (0.5, 1.0, 2.0):
            for seek in (5.0, 10.0, 20.0):
                rr = arc_test(kin, ramp_C_per_min=ramp, seek_min=seek)
                sens.append({"ramp": ramp, "seek_min": seek, "T_in_C": rr["T_in_C"], "T_on_C": rr.get("T_on_C"),
                             "T_at_1_C_per_s_C": rr.get("T_at_1_C_per_s_C")})
        out["arc_sensitivity"] = sens
        # the anode-electrolyte mass read as the anode alone (100.58 g) instead of D4's 208.58 g
        mg = dict(bcrnn.MASS_G); mg["an_ele"] = bcrnn.M_ANODE
        rr = arc_test(bcrnn.Kinetics(mass_g=mg))
        out["arc_an_ele_mass_anode_only"] = {"T_in_C": rr["T_in_C"], "T_on_C": rr.get("T_on_C"), "T_at_1_C_per_s_C": rr.get("T_at_1_C_per_s_C")}
    os.makedirs(a.out, exist_ok=True)
    json.dump(out, open(os.path.join(a.out, "v1_arc_check.json"), "w"), indent=1)
    if base.get("trace"):
        np.savetxt(os.path.join(a.out, "v1_arc_trace.csv"), np.array([(x[1], x[2] - 273.15) for x in base["trace"]]),
                   delimiter=",", header="t_s,T_bat_C (heating phases only)", comments="")
    print(json.dumps({k: v for k, v in out.items() if not k.startswith("isothermal")}, indent=1))
    print("\nisothermal, M50 neighbour (cp 950 J/kgK), fresh reactants:")
    for row in out["isothermal_m50"]:
        print(f"{row['T_C']:6.1f} C: initial {row['initial_K_per_min']:.4g} K/min, peak {row['peak_K_per_min']:.4g}, "
              f"first 0.15 K/min at {row['first_0.15_s']} s, SEI conversion in 1 h {row['sei_conversion_1h']:.3f}")
