"""Stage 15, Part A: the reactive cross-section (DECISIONS.md D173).

Stage 13's cross-section conduction model of the mid-height section (`stage13_section.Section`: conduction in r and
theta with the roll's across- and along-layer conductivities, the can as a surface layer, the contact and air wedge
to the trigger, convection and radiation, the radiation received from the trigger, the delivery as a uniform flux over
the facing half), with the archive's kinetics integrated in every cell of the roll and their heat fed back. Nothing
else is new:
  - each roll cell carries the three-dimensional model's reacting mass per unit volume, M_cell / V_cell (v12_model's
    m_node = M_cell w_vol / V), and its own heat capacity; the can's nodes carry no reacting mass, as the can's
    capacity carries none in the three-dimensional model;
  - the reaction step is the three-dimensional model's own (`stage9_model.run_resolved`): the compiled sub-steps of
    `v12_kernel.FastKinetics` (up to 64 explicit sub-steps, then the implicit integrator) or, from the delivery's
    start, `stage7_kernel.FastKineticsMax` with 4,096; the step level k chosen by `reactive.choose_level`'s rule
    (the largest local reaction heating times the step at most DT_TARGET = 1 K, at most one level coarser than the
    previous step, aligned to the grid), and a step repeated at half its length while the reaction sub-step heats any
    cell by more than DT_ACCEPT = 4 K, down to 2^-16 of the base step;
  - the base step is Stage 13's (`Section.run`): dt_early to t_switch, then dt_late; the level halves it. With the
    reaction off the level is always 0 and the run is `Section.run` step for step (V3).
The section is per unit length of the half section 0 <= theta <= pi; the whole cell's energies are 2 L times its own
(L = 70.1 mm), and its mean temperature is the heat-capacity-weighted mean over the roll's cells and the can's nodes,
the section's stand-in for the cell's Tmean. It has neither the ends (the caps, their convection and radiation) nor
the tabs.
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v12_model as V                      # noqa: E402  (unchanged)
import stage13_inputs as IN13              # noqa: E402  (unchanged)
import stage13_section as S13              # noqa: E402  (unchanged)
import stage15_model as M15                # noqa: E402

LP, bcrnn, RX = V.LP, V.bcrnn, V.RX
K0 = 273.15
LENGTH_FACTOR = 2.0 * IN13.LZ              # half section per unit length -> whole cell


class ReactiveSection(S13.Section):
    def __init__(self, h_c=2000.0, refine=1.0, region="half"):
        super().__init__(h_c, refine, "sparse", region)
        nr, nt = self.nr, self.nt
        self.n_roll = nr * nt                           # the sparse ordering: roll cells first (i * nt + j), then can
        self.C_all = self.capacity()
        self.C_roll = self.C_all[:self.n_roll].copy()
        rho_m = LP.M_CELL / IN13.V_CELL                 # kg/m3, the three-dimensional model's reacting mass density
        self.m_roll = rho_m * self.C_roll / IN13.RHO_CP
        self.ci = self.can_index()
        self.far = int(self.ci[-1])                     # the can node nearest theta = pi, the far face
        self.C_total = float(self.C_all.sum())

    def run(self, T1_of_t, sources, t_end, dt_early=0.01, dt_late=0.1, t_switch=60.0, reaction=True, kin=None,
            stop_mean=None, shift_K=0.0, sei0=None, max_sub=4096, Ta=None, record_dt=0.5):
        """Integrate from the ambient temperature. sources: objects with cumulative(t) in J and max_power(t_a, t_b)
        (stage9_model's Triangular, Constant, stage15_model.Hold), each delivered over the region as a uniform flux.
        Stops at C8 (the mean at stop_mean, K) if given. Returns the histories every record_dt s and at the end."""
        Ta = IN13.T_AMB if Ta is None else Ta
        kin = bcrnn.Kinetics() if kin is None else kin
        import v12_kernel as KN
        import stage7_kernel as K7
        loc = KN.FastKinetics(kin, self.m_roll, self.C_roll)
        loc_src = K7.FastKineticsMax(kin, self.m_roll, self.C_roll, max_sub) if (sources and max_sub) else None
        if shift_K:
            loc = M15.Shifted(loc, shift_K)
            loc_src = M15.Shifted(loc_src, shift_K) if loc_src is not None else None
        t_src = min(s.t0 for s in sources) if sources else None
        nroll, ci = self.n_roll, self.ci
        C = self.C_all
        T = np.full(self.n, Ta)
        c = M15.initial_state(nroll, sei0)
        t = 0.0
        e_rxn = e_src = 0.0
        rec_t, rec_mean, rec_far, rec_max, rec_rxn = [0.0], [Ta], [Ta], [Ta], [0.0]
        surf_hist = [T[ci].copy()]
        next_rec = record_dt
        Tmean_prev = Tmax_prev = Ta
        t_c8 = t_c1 = None
        peak_mean, t_peak_mean = Ta, 0.0
        peak_max, t_peak_max = Ta, 0.0
        peak_far, t_peak_far = Ta, 0.0
        n_steps = n_sub = n_rej = max_imp = 0
        k_prev = 0
        UNIT = 2 ** RX.K_MAX
        while t < t_end - 1e-9:
            dt_b = dt_early if t < t_switch - 1e-9 else dt_late
            dt_b = min(dt_b, t_end - t)
            t_base = t
            off = 0                                      # position within the base step, in units of dt_b / 2^K_MAX
            while off < UNIT:
                if reaction:
                    R0, H0 = loc.start(T[:nroll], c)
                    H_max = float(np.abs(H0).max())
                else:
                    H_max = 0.0
                k_need = 0 if H_max * dt_b <= RX.DT_TARGET else int(math.ceil(math.log2(H_max * dt_b / RX.DT_TARGET)))
                k = max(k_need, k_prev - 1, 0)
                while k < RX.K_MAX and off % (UNIT >> k) != 0:
                    k += 1
                k = min(k, RX.K_MAX)
                use = loc_src if (loc_src is not None and t >= t_src) else loc
                while True:
                    dt = dt_b / 2 ** k
                    if reaction:
                        Ts_r, cs, n_imp = use.step(T[:nroll], c, R0, H0, dt)
                        if np.abs(Ts_r - T[:nroll]).max() > RX.DT_ACCEPT and k < RX.K_MAX:
                            k += 1; n_rej += 1
                            continue
                    else:
                        Ts_r, cs, n_imp = T[:nroll], c, 0
                    break
                max_imp = max(max_imp, n_imp)
                off_new = off + (UNIT >> k)
                t_new = round(t + dt, 10) if (k == 0 and off == 0) else round(t_base + off_new * (dt_b / UNIT), 12)
                Cf, solve = self.factor(dt)
                Ts = T.copy() if reaction else T
                if reaction:
                    Ts[:nroll] = Ts_r
                rhs = Cf / dt * Ts
                Tsurf = T[ci]
                r = self.h_conv * Ta - self.w_rad * (Tsurf ** 4 - Ta ** 4)
                if T1_of_t is not None:
                    T1 = T1_of_t(t_new)
                    r = r + self.g_contact * T1 + self.g_rad * (T1 ** 4 - Ta ** 4)
                else:
                    r = r + self.g_contact * Ta
                for s in sources:
                    dQ = s.cumulative(t_new) - s.cumulative(t)
                    if dQ != 0.0:
                        r = r + self.q_share * dQ / dt
                        e_src += dQ
                rhs[ci] += r
                if reaction:
                    e_rxn += float(self.C_roll @ (Ts_r - T[:nroll]))
                    c = cs
                T = solve(rhs)
                t = t_new
                off = off_new
                k_prev = k
                n_sub += 1
                Tmean = float(C @ T) / self.C_total
                imax = int(np.argmax(T))
                Tmax = float(T[imax])
                if t_c1 is None and Tmax >= IN13.T_LEVEL:
                    t_c1 = t - dt + dt * (IN13.T_LEVEL - Tmax_prev) / (Tmax - Tmax_prev) if Tmax > Tmax_prev else t
                if Tmean > peak_mean:
                    peak_mean, t_peak_mean = Tmean, t
                if Tmax > peak_max:
                    peak_max, t_peak_max = Tmax, t
                if T[self.far] > peak_far:
                    peak_far, t_peak_far = float(T[self.far]), t
                if stop_mean is not None and t_c8 is None and Tmean >= stop_mean:
                    t_c8 = t - dt + dt * (stop_mean - Tmean_prev) / (Tmean - Tmean_prev) if Tmean > Tmean_prev else t
                Tmean_prev, Tmax_prev = Tmean, Tmax
                if t >= next_rec - 1e-9 or t_c8 is not None:
                    next_rec = round(next_rec + record_dt, 10)
                    rec_t.append(t); rec_mean.append(Tmean); rec_far.append(float(T[self.far]))
                    rec_max.append(Tmax); rec_rxn.append(e_rxn * LENGTH_FACTOR)
                if t_c8 is not None:
                    break
            n_steps += 1
            surf_hist.append(T[ci].copy())
            if t_c8 is not None:
                break
        return {"t_c8_s": t_c8, "t_c1_s": t_c1, "t_end_s": t, "peak_mean_C": peak_mean - K0,
                "t_peak_mean_s": t_peak_mean, "peak_max_C": peak_max - K0, "t_peak_max_s": t_peak_max,
                "peak_far_C": peak_far - K0, "t_peak_far_s": t_peak_far, "mean_end_C": Tmean_prev - K0,
                "rxn_J": e_rxn * LENGTH_FACTOR, "delivered_J": e_src, "base_steps": n_steps, "steps": n_sub,
                "rejected": n_rej, "max_implicit_nodes": max_imp,
                "t": np.array(rec_t), "mean_C": np.array(rec_mean) - K0, "far_C": np.array(rec_far) - K0,
                "max_C": np.array(rec_max) - K0, "rxn_cum_J": np.array(rec_rxn),
                "surface_history": np.array(surf_hist), "T_final": T, "c_final": c}
