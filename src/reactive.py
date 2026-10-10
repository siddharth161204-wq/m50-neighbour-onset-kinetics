"""Stage 2: the B-CRNN reaction heat as a source in the resolved cell 2 and in the lumped node of the published study.

One-way coupling, as in the published study: cell 1's temperature history is the archived one and does not respond.
The published solver (external/m50-two-cell-pilot/src/resolved_cell2.py, v1.0.0) supplies the mesh, the conduction
and capacity matrices, every boundary path and its energy account; nothing in its physics is changed.

Scheme (DECISIONS.md D13): first-order (Lie) splitting in each step of length dt.
 1. Reaction: every node integrates its own adiabatic kinetics over dt, dc/dt = S r(T, c), dT/dt = Q(T, c) / C_i,
    with Q the node's reaction heat (its share of the cell's reactant inventory, which sits in the jelly roll only,
    D14) and C_i its heat capacity (roll plus can shell on the surface). Nodes whose reactants and temperature change
    by less than 1e-4 of themselves in the step take one explicit Heun step; the others are integrated with BDF on a
    block-diagonal analytic Jacobian.
 2. Conduction: the published backward-Euler step with lumped capacity and lagged room radiation, from the
    post-reaction temperatures.
The step adapts: dt = 0.1 s / 2^k, the largest such that the largest local reaction heating in the step stays below
DT_TARGET kelvin; a step whose reaction sub-step raises any node by more than DT_ACCEPT is repeated at half the step.
The reaction heat enters the energy account as the sum over nodes of C_i (T_after_reaction - T_before), so the
account closes exactly as the published one does.
"""
import math
import os
import sys
import numpy as np
import scipy.sparse as sp
from scipy.integrate import solve_ivp

HERE = os.path.dirname(os.path.abspath(__file__))
EXT = os.path.join(HERE, "..", "external", "m50-two-cell-pilot", "src")
if EXT not in sys.path:
    sys.path.insert(0, EXT)
import lumped_two_cell as LP                      # noqa: E402
import bcrnn                                      # noqa: E402


def _solver_class():
    from resolved_cell2 import _Solver           # imported late so that a caller may change LP's conductivities first
    return _Solver

DT_BASE = 0.1          # s, the published step
DT_TARGET = 1.0        # K, largest local reaction heating aimed for in one step
DT_ACCEPT = 4.0        # K, a step whose reaction sub-step heats any node more than this is repeated at half the step
K_MAX = 16             # smallest step 0.1 / 2^16 s
SLOW_FRAC = 2e-3       # largest relative change of an amount, or of a rate through temperature, in one explicit sub-step
DT_EXPLICIT = 0.02     # K, largest temperature change in one explicit sub-step
MAX_SUB = 64           # points needing more explicit sub-steps than this are integrated implicitly
C_FLOOR = 1e-3         # amounts below this are measured against it when judging a step slow (dimensionless)
NV = bcrnn.NS + 1      # unknowns per node: T and 13 species


class LocalKinetics:
    """Adiabatic kinetics of many independent material points with reacting mass m (kg) and heat capacity C (J/K)."""

    def __init__(self, kin, m, C):
        self.kin, self.m, self.C = kin, np.asarray(m, float), np.asarray(C, float)
        self.h = kin.h_mass                       # J/kg per unit rate
        self.S = kin.stoich

    def heating(self, T, c, idx=None):
        m = self.m if idx is None else self.m[idx]
        C = self.C if idx is None else self.C[idx]
        r = self.kin.rates(T, c)
        return r, (self.h @ r) * m / C

    def step(self, T, c, dt, rtol=1e-7):
        """Integrate every point over dt. Points whose relative change in the step is small take explicit Heun steps,
        sub-cycled in powers of two so that each sub-step changes every amount, the temperature-driven rate and the
        temperature by less than SLOW_FRAC, SLOW_FRAC and DT_EXPLICIT; points that would need more than MAX_SUB
        sub-steps are integrated implicitly. Returns new T, c, and the number of points integrated implicitly."""
        T = T.copy(); c = c.copy()
        r0, H0 = self.heating(T, c)
        dc0 = self.S @ r0
        cons = np.where(dc0 < 0, -dc0 * dt / np.maximum(c, C_FLOOR), 0.0).max(axis=0)
        sens = np.abs(H0) * dt * (self.kin.Ea[:, None] * (r0 > 0)).max(axis=0) / (bcrnn.R_GAS * T ** 2)
        need = np.maximum.reduce([cons / SLOW_FRAC, sens / SLOW_FRAC, np.abs(H0) * dt / DT_EXPLICIT, np.ones_like(T)])
        nsub = (2 ** np.ceil(np.log2(need))).astype(np.int64)
        for b in np.unique(nsub[nsub <= MAX_SUB]):
            s = np.where(nsub == b)[0]
            h = dt / b
            Ts, cs = T[s], c[:, s]
            for _ in range(int(b)):
                r_a, H_a = self.heating(Ts, cs, s)
                dca = self.S @ r_a
                T1 = Ts + h * H_a
                c1 = np.clip(cs + h * dca, 0.0, None)
                r_b, H_b = self.heating(T1, c1, s)
                Ts = Ts + 0.5 * h * (H_a + H_b)
                cs = np.clip(cs + 0.5 * h * (dca + self.S @ r_b), 0.0, None)
            T[s], c[:, s] = Ts, cs
        f = np.where(nsub > MAX_SUB)[0]
        if f.size:
            T[f], c[:, f] = self._implicit(T[f], c[:, f], dt, f, rtol)
        return T, c, int(f.size)

    def _implicit(self, T, c, dt, idx, rtol):
        n = T.size
        m, C = self.m[idx], self.C[idx]
        S, h, kin = self.S, self.h, self.kin

        def fun(t, y):
            Y = y.reshape(n, NV)
            cc = np.clip(Y[:, 1:].T, 0.0, None)
            r = kin.rates(Y[:, 0], cc)
            out = np.empty((n, NV))
            out[:, 0] = (h @ r) * m / C
            out[:, 1:] = (S @ r).T
            return out.ravel()

        rows = (np.arange(n)[:, None, None] * NV + np.arange(NV)[None, :, None]) * np.ones((1, 1, NV), int)
        cols = (np.arange(n)[:, None, None] * NV + np.arange(NV)[None, None, :]) * np.ones((1, NV, 1), int)
        rows, cols = rows.ravel(), cols.ravel()

        def jac(t, y):
            Y = y.reshape(n, NV)
            TT = Y[:, 0]
            cc = np.clip(Y[:, 1:].T, 0.0, None)
            r = kin.rates(TT, cc)
            drdc, drdT = kin.jacobian(TT, cc, r)
            B = np.empty((n, NV, NV))
            B[:, 0, 0] = (h @ drdT) * m / C
            B[:, 0, 1:] = (np.einsum("j,jkn->kn", h, drdc) * (m / C)).T
            B[:, 1:, 0] = (S @ drdT).T
            B[:, 1:, 1:] = np.einsum("sj,jkn->nsk", S, drdc)
            return sp.csc_matrix((B.ravel(), (rows, cols)), shape=(n * NV, n * NV))

        y0 = np.empty((n, NV)); y0[:, 0] = T; y0[:, 1:] = c.T
        atol = np.tile(np.r_[1e-6, np.full(bcrnn.NS, 1e-11)], n)
        sol = solve_ivp(fun, (0.0, dt), y0.ravel(), method="BDF", jac=jac, rtol=rtol, atol=atol, t_eval=[dt])
        if not sol.success:
            raise RuntimeError("reaction sub-step failed: " + sol.message)
        Y = sol.y[:, -1].reshape(n, NV)
        return Y[:, 0], np.clip(Y[:, 1:].T, 0.0, None)


def choose_level(t, H_max, k_prev):
    """Step level k (dt = DT_BASE / 2^k): fine enough that H_max dt <= DT_TARGET, at most one level coarser than the
    previous step, and aligned so that t is a whole multiple of dt (the step then lands on the coarser grids)."""
    k_need = 0 if H_max * DT_BASE <= DT_TARGET else int(math.ceil(math.log2(H_max * DT_BASE / DT_TARGET)))
    k = max(k_need, k_prev - 1, 0)
    while k < K_MAX:
        x = t / (DT_BASE / 2 ** k)
        if abs(x - round(x)) < 1e-6:
            break
        k += 1
    return min(k, K_MAX)


def run_resolved(model, t1_of_t, g_pos, g_neg, t_end=900.0, record_dt=0.1, reaction=True, levels=None,
                 progress=None):
    """Reactive resolved cell 2 (one-way). Returns crossings, peaks, conversions, an energy account and a series."""
    Ta = LP.T_AMB
    kin = bcrnn.Kinetics()
    V_full = model.geom["volume_mesh"]
    m_node = LP.M_CELL * model.w_vol / V_full                     # kg of cell per node (half model), D14
    loc = LocalKinetics(kin, m_node, model.C)
    N = model.C.size
    T = np.full(N, Ta)
    c = bcrnn.fresh_state(N)
    d_bus = g_pos * model.d_pos_unit + g_neg * model.d_neg_unit
    d_gap, d_conv = model.d_gap_unit, model.d_conv_unit
    facts = {}

    def solver(dt):
        key = round(dt, 12)
        if key not in facts:
            if len(facts) >= 6:
                old = facts.pop(max(facts))   # keep the finer steps, which a runaway needs again
                if getattr(old, "kind", "") == "pardiso":
                    old.ps.free_memory(everything=True)
            A = (model.K + sp.diags(model.C / dt + d_conv + d_gap + d_bus)).tocsr()
            facts[key] = _solver_class()(A)
        return facts[key]

    levels = levels if levels is not None else {"T_onset_low": LP.T_ONSET_BAND[0], "T_onset_mean": LP.T_ONSET_MEAN,
                                                "T_onset_high": LP.T_ONSET_BAND[1]}
    cross = {k: None for k in levels}
    energy = {k: 0.0 for k in ("in_bus", "in_gap", "in_rad", "out_conv", "out_rad", "in_rxn")}
    E0 = float(model.C @ T)
    t, k_prev = 0.0, 0
    Tmax_prev = T.max()
    rec_next = record_dt
    series = [(0.0, t1_of_t(0.0), T.max(), float(model.C @ T) / model.C_total, int(np.argmax(T)), 0.0, 0.0, 0.0)]
    peak = {"Tmax_C": T.max() - 273.15, "t_s": 0.0, "imax": 0, "Tmean_C": T.max() - 273.15}
    i_cat1, i_sei = bcrnn.SPECIES.index("cat1"), bcrnn.SPECIES.index("sei")
    t_cat1_consumed = None
    n_steps = n_rejected = max_implicit = 0
    max_rate = 0.0
    while t < t_end - 1e-12:
        if reaction:
            r0, H0 = loc.heating(T, c)
            H_max = float(np.abs(H0).max())
            max_rate = max(max_rate, H_max)
        else:
            H_max = 0.0
        k = choose_level(t, H_max, k_prev)
        while True:
            dt = DT_BASE / 2 ** k
            if reaction:
                Ts, cs, n_imp = loc.step(T, c, dt)
                if np.abs(Ts - T).max() > DT_ACCEPT and k < K_MAX:
                    k += 1; n_rejected += 1
                    continue
            else:
                Ts, cs, n_imp = T, c, 0
            break
        max_implicit = max(max_implicit, n_imp)
        t_new = round(t + dt, 12)
        T1 = t1_of_t(t_new)
        q_rad_gain = T1 ** 4 - Ta ** 4
        rad_loss = model.w_rad * (T ** 4 - Ta ** 4)              # lagged, as published
        rhs = model.C / dt * Ts + d_conv * Ta + (d_gap + d_bus) * T1 + model.g_rad * q_rad_gain - rad_loss
        Tn = solver(dt).solve(rhs)
        energy["in_rxn"] += float(model.C @ (Ts - T))
        energy["in_bus"] += dt * float(d_bus @ (T1 - Tn))
        energy["in_gap"] += dt * float(d_gap @ (T1 - Tn))
        energy["in_rad"] += dt * float(model.g_rad.sum() * q_rad_gain)
        energy["out_conv"] += dt * float(d_conv @ (Tn - Ta))
        energy["out_rad"] += dt * float(np.sum(rad_loss))
        T, c, t = Tn, cs, t_new
        n_steps += 1
        k_prev = k
        imax = int(np.argmax(T)); Tmax = float(T[imax])
        for key, lv in levels.items():
            if cross[key] is None and Tmax >= lv:
                cross[key] = t - dt + dt * (lv - Tmax_prev) / (Tmax - Tmax_prev) if Tmax > Tmax_prev else t
        Tmean = float(model.C @ T) / model.C_total
        if Tmax - 273.15 > peak["Tmax_C"]:
            peak.update(Tmax_C=Tmax - 273.15, t_s=t, imax=imax)
        peak["Tmean_C"] = max(peak["Tmean_C"], Tmean - 273.15)
        if t_cat1_consumed is None and (1.0 - c[i_cat1]).max() >= 0.99:
            t_cat1_consumed = t
        Tmax_prev = Tmax
        if t >= rec_next - 1e-9:
            rec_next = round(rec_next + record_dt, 12)
            series.append((t, T1, Tmax, Tmean, imax, float(1 - c[i_cat1, imax]), float(1 - c[i_sei, imax] / 0.15),
                           float(model.w_vol[T >= LP.T_ONSET_BAND[0]].sum() / model.w_vol.sum())))
            if progress:
                progress(t, Tmax, Tmean, dt)
    stored = 2 * (float(model.C @ T) - E0)
    energy = {k: 2 * v for k, v in energy.items()}
    net = energy["in_bus"] + energy["in_gap"] + energy["in_rad"] + energy["in_rxn"] - energy["out_conv"] - energy["out_rad"]
    taken_in = energy["in_bus"] + energy["in_gap"] + energy["in_rad"] + max(energy["in_rxn"], 0.0)
    conv = {s: float((1 - c[bcrnn.SPECIES.index(s)] / bcrnn.C0[bcrnn.SPECIES.index(s)]) @ model.w_vol / model.w_vol.sum())
            for s in ("sei", "li_an", "ele_liq", "cat1", "sep")}
    return {"cross_s": cross, "peak": peak, "t_cat1_consumed_at_a_node_s": t_cat1_consumed,
            "conversion_volume_mean_900s": conv, "energy_J": energy, "stored_J": stored, "net_in_J": net,
            "energy_residual_rel": (stored - net) / taken_in, "steps": n_steps, "rejected": n_rejected,
            "max_implicit_nodes": max_implicit, "max_local_reaction_heating_K_per_s": max_rate,
            "series": np.array(series), "T_final": T, "c_final": c}


def run_lumped(t1_of_t, g_bus, t_end=900.0, record_dt=0.1, reaction=True, levels=None):
    """Reactive lumped node: the published lumped_one_way scheme (backward Euler, lagged room radiation) plus the
    reaction sub-step for its whole cell mass, with the same adaptive step."""
    Ta = LP.T_AMB
    kin = bcrnn.Kinetics()
    loc = LocalKinetics(kin, np.array([LP.M_CELL]), np.array([LP.C_CELL]))
    C, G, hA = LP.C_CELL, g_bus + LP.G_GAP, LP.H_CONV * LP.A_CONV
    T = np.array([Ta]); c = bcrnn.fresh_state(1)
    levels = levels if levels is not None else {"T_onset_low": LP.T_ONSET_BAND[0], "T_onset_mean": LP.T_ONSET_MEAN,
                                                "T_onset_high": LP.T_ONSET_BAND[1]}
    cross = {k: None for k in levels}
    t, k_prev, Tprev = 0.0, 0, Ta
    rec_next = record_dt
    out = [(0.0, Ta)]
    peak = {"T_C": Ta - 273.15, "t_s": 0.0}
    e_rxn = 0.0
    while t < t_end - 1e-12:
        H_max = float(np.abs(loc.heating(T, c)[1]).max()) if reaction else 0.0
        k = choose_level(t, H_max, k_prev)
        while True:
            dt = DT_BASE / 2 ** k
            if reaction:
                Ts, cs, _ = loc.step(T, c, dt)
                if abs(Ts[0] - T[0]) > DT_ACCEPT and k < K_MAX:
                    k += 1; continue
            else:
                Ts, cs = T, c
            break
        t_new = round(t + dt, 12)
        T1 = t1_of_t(t_new)
        q_in = LP.EPS ** 2 * LP.SIGMA * LP.F_VIEW * LP.A_LAT * (T1 ** 4 - Ta ** 4)
        q_loss_rad = LP.EPS * LP.SIGMA * LP.A_CELL * (T[0] ** 4 - Ta ** 4)
        Tn = (C / dt * Ts[0] + G * T1 + hA * Ta + q_in - q_loss_rad) / (C / dt + G + hA)
        e_rxn += C * (Ts[0] - T[0])
        T, c, t, k_prev = np.array([Tn]), cs, t_new, k
        for key, lv in levels.items():
            if cross[key] is None and Tn >= lv:
                cross[key] = t - dt + dt * (lv - Tprev) / (Tn - Tprev) if Tn > Tprev else t
        if Tn - 273.15 > peak["T_C"]:
            peak.update(T_C=Tn - 273.15, t_s=t)
        Tprev = Tn
        if t >= rec_next - 1e-9:
            rec_next = round(rec_next + record_dt, 12)
            out.append((t, Tn))
    conv = {s: float(1 - c[bcrnn.SPECIES.index(s), 0] / bcrnn.C0[bcrnn.SPECIES.index(s)]) for s in ("sei", "li_an", "ele_liq", "cat1", "sep")}
    return {"cross_s": cross, "peak": peak, "reaction_heat_J": e_rxn, "conversion_900s": conv, "series": np.array(out)}
