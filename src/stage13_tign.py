"""Stage 13, Part B1: the whole-cell ignition temperature T_ign of the lumped neighbour (DECISIONS.md D132).

T_ign is where the cell's heat release equals the lumped neighbour's loss, with the trigger at a stated temperature:

    Q(T) = M sum_j h_j r_j(T, c)                     the reaction heat of the 65 g cell (W), the archive's rate law
    L(T; T1) = G (T - T1) + h_conv A_conv (T - Ta) + eps sigma A_cell (T^4 - Ta^4) - eps^2 sigma F A_lat (T1^4 - Ta^4)

L is the loss exactly as the lumped neighbour holds it (stage9_model.run_lumped): the link G (contact and wedge plus
tabs) to the trigger at T1, room convection outside the 90 degree sector, radiation to the room from the whole can,
and the radiation received from the trigger. The state c is the fresh state with the separator's melting complete
(sep = 0): every other reactant at its initial amount (ele_liq, li_an, binder and cat1 at 1, sei at 0.15, the
intermediates at 0). T_ign is the last temperature below the level T_L = 255.68 C at which Q - L changes sign from
negative to positive, so that above it, up to T_L, the reaction heat exceeds the loss. Two trigger states are used:
the trigger at 25 C (the largest loss) and at the neighbour's own temperature (no loss through the link).

Usage: python3 stage13_tign.py [--draws]     writes results/stage13_tign.csv (posterior mean, and the 200 draws)
"""
import argparse
import csv
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bcrnn                               # noqa: E402  (unchanged)
import v12_model as V                      # noqa: E402  (unchanged)
import stage13_inputs as IN                # noqa: E402

LP = V.LP
I_SEP = bcrnn.SPECIES.index("sep")
I_CAT1 = bcrnn.SPECIES.index("cat1")
J_CAT1 = bcrnn.REACTIONS.index("cat1")
T_SCAN_LO = IN.T_AMB + 75.0             # 100 C: below the separator's melting, where no balance point is sought
T_SCAN_STEP = 0.05


def state_molten(c_cat1=1.0):
    """The fresh state with the separator's melting complete and cat1 at c_cat1."""
    c = bcrnn.C0.astype(float).copy()
    c[I_SEP] = 0.0
    c[I_CAT1] = c_cat1
    return c


def heat_by_reaction(kin, T, c=None):
    """W per reaction for the 65 g cell at temperature T (K)."""
    c = state_molten() if c is None else c
    r = kin.rates(np.array([T]), c.reshape(-1, 1))[:, 0]
    return LP.M_CELL * kin.h_mass * r


def q_gen(kin, T, c=None):
    return float(heat_by_reaction(kin, T, c).sum())


def g_link(connection, h="central", g="central"):
    """The lumped neighbour's link: contact and wedge plus the tabs (W/K)."""
    gp, gn = V.tabs(connection, V.G_TAB[g])
    return V.g_contact(V.H_CONTACT[h]) + gp + gn


def loss(T, T1, G):
    """The lumped neighbour's net loss (W) at temperature T with the trigger at T1, as run_lumped holds it."""
    Ta = IN.T_AMB
    return (G * (T - T1) + LP.H_CONV * LP.A_CONV * (T - Ta) + LP.EPS * LP.SIGMA * LP.A_CELL * (T ** 4 - Ta ** 4)
            - LP.EPS ** 2 * LP.SIGMA * V.F_TOUCH * LP.A_LAT * (T1 ** 4 - Ta ** 4))


def balance(kin, T, T1_mode, G, c=None):
    T1 = IN.T_AMB if T1_mode == "ambient" else (T if T1_mode == "own" else float(T1_mode))
    return q_gen(kin, T, c) - loss(T, T1, G)


def _balance_grid(kin, Ts, T1_mode, G, c=None):
    """Q - L on a grid of temperatures in one call of the rate law (the scan of t_ign)."""
    c = state_molten() if c is None else c
    r = kin.rates(Ts, np.repeat(c.reshape(-1, 1), len(Ts), axis=1))
    q = LP.M_CELL * (kin.h_mass[:, None] * r).sum(axis=0)
    T1 = np.full_like(Ts, IN.T_AMB) if T1_mode == "ambient" else (Ts if T1_mode == "own" else
                                                                     np.full_like(Ts, float(T1_mode)))
    return q - loss(Ts, T1, G)


def t_ign(kin, T1_mode="own", G=None, c=None, hi=None):
    """T_ign (K): the last upward zero of Q - L below T_L (None if Q > L throughout or nowhere)."""
    from scipy.optimize import brentq
    G = g_link("parallel") if G is None else G
    hi = IN.T_LEVEL if hi is None else hi
    Ts = np.arange(T_SCAN_LO, hi + 1e-9, T_SCAN_STEP)
    f = _balance_grid(kin, Ts, T1_mode, G, c)
    up = np.where((f[:-1] <= 0) & (f[1:] > 0))[0]
    if len(up) == 0 or f[-1] <= 0:
        return None
    k = up[-1]
    return brentq(lambda T: balance(kin, T, T1_mode, G, c), Ts[k], Ts[k + 1], xtol=1e-12, rtol=1e-15, maxiter=200)


def describe(kin, T, T1_mode, G, c=None):
    """The carrying reaction, the effective activation temperature T^2 dlnQ/dT, the shares and the loss at T."""
    q = heat_by_reaction(kin, T, c)
    dT = 1e-3
    lnq = lambda x: math.log(q_gen(kin, x, c))
    t_act = T ** 2 * (lnq(T + dT) - lnq(T - dT)) / (2 * dT)
    j = int(np.argmax(q))
    T1 = IN.T_AMB if T1_mode == "ambient" else (T if T1_mode == "own" else float(T1_mode))
    return {"T_ign_C": T - IN.K0, "Q_W": float(q.sum()), "loss_W": loss(T, T1, G), "carrying": bcrnn.REACTIONS[j],
            "carrying_share": float(q[j] / q.sum()), "T_act_eff_K": t_act, "RT2_over_E_K": T ** 2 / t_act,
            "shares": {bcrnn.REACTIONS[i]: float(q[i]) for i in range(len(q)) if abs(q[i]) > 1e-6},
            "cat1_heat_total_J": float(LP.M_CELL * kin.h_mass[J_CAT1])}


def table(kin, temps_C=(200, 210, 220, 225, 230, 240, 250)):
    out = []
    for TC in temps_C:
        q = heat_by_reaction(kin, TC + IN.K0)
        out.append({"T_C": TC, "Q_W": float(q.sum()), "cat1_W": float(q[J_CAT1])})
    return out


def run(draws=False):
    """The posterior mean (and the 200 draws): T_ign with the trigger at 25 C and at the neighbour's own temperature,
    for the parallel and the series link at the central contact."""
    rows = []
    kins = [("mean", bcrnn.Kinetics())]
    if draws:
        import stage3_draws as S
        d_all, particles = S.all_draws()
        for d, ae, sep, cat in d_all:
            kins.append((d, S.draw_kinetics(particles, ae, sep, cat)))
    for name, kin in kins:
        for conn in ("parallel", "series"):
            G = g_link(conn)
            for mode in ("own", "ambient"):
                T = t_ign(kin, mode, G)
                row = {"kinetics": name, "connection": conn, "trigger": mode, "G_W_K": G,
                       "T_ign_C": None if T is None else T - IN.K0}
                if T is not None:
                    dsc = describe(kin, T, mode, G)
                    row.update({k: dsc[k] for k in ("Q_W", "loss_W", "carrying", "carrying_share", "T_act_eff_K",
                                                    "RT2_over_E_K", "cat1_heat_total_J")})
                rows.append(row)
            if conn == "series" and name != "mean":
                pass
    return rows


def write(rows, path=os.path.join(IN.RES, "stage13_tign.csv")):
    keys = ["kinetics", "connection", "trigger", "G_W_K", "T_ign_C", "Q_W", "loss_W", "carrying", "carrying_share",
            "T_act_eff_K", "RT2_over_E_K", "cat1_heat_total_J"]
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in keys})
    return path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", action="store_true")
    a = ap.parse_args()
    rows = run(draws=a.draws)
    print(write(rows))
    for r in rows[:4]:
        print(r)
