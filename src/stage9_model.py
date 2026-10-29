"""Stage 9 (version 1.5.0): the Stage 8 loops with two additions (DECISIONS.md D90 and D93).

  - The delivery of Part B as a constant power from the start of the trigger's release (`Constant`): E_J at E / tau
    from t0 over tau, the brief's bracket of long deliveries (120, 240 and 360 s, conditional). Each step receives the
    pulse's exact integral over the step, as with the triangular pulse of Stage 8 (`stage8_model.Pulse`), so the energy
    delivered is the source's energy to rounding, and the pulse's power enters the choice of the step as Stage 8's
    does (its largest local heating rate added to the reaction's, D13's rule).
  - The kinetics' initial state as an argument (`sei0`), as Stage 7 has it (`stage7_model.initial_state`): the aged
    SEI of C3 sets the SEI's initial amount to 0 in every node and in the lumped node (D66, D57 (1)).
`run_resolved` and `run_lumped` are `stage8_model.run_resolved` and `stage8_model.run_lumped` with `sei0`: with the
fresh state (sei0=None) they are Stage 8's operation for operation, and with sei0 given and no source they are
`stage7_model.run_resolved` and `run_lumped` with that sei0 and no event; src/test_stage9.py checks both bitwise on
synthetic histories. A run with `stop_level=None` is not stopped at the hot spot's (or the lumped neighbour's) 255.7 C
and goes on to its end; the crossing is still recorded in `cross_s` (the level T_onset_low is 255.68 C, D35).
"""
import os
import sys
import numpy as np
import scipy.sparse as sp

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import v12_model as V                             # noqa: E402  (unchanged)
import stage7_model as M7                         # noqa: E402  (unchanged)
import stage8_model as M8                         # noqa: E402  (unchanged)

LP, bcrnn, RX = V.LP, V.bcrnn, V.RX
I_SEI = bcrnn.SPECIES.index("sei")
Triangular = M8.Pulse                             # Stage 8's delivery: a triangular pulse (stage7_model.Event)
Source = M8.Source
share_surface = M8.share_surface
share_volume = M8.share_volume
surface_info = M8.surface_info


class Constant:
    """E_J released at the constant power E / tau from t0_s over tau_s (Part B's delivery, D93)."""

    shape = "constant"

    def __init__(self, E_J, tau_s, t0_s):
        self.E, self.tau, self.t0 = float(E_J), float(tau_s), float(t0_s)

    def cumulative(self, t):
        s = t - self.t0
        if s <= 0.0:
            return 0.0
        if s >= self.tau:
            return self.E
        return self.E * s / self.tau

    def power(self, t):
        s = t - self.t0
        return self.E / self.tau if 0.0 < s < self.tau else 0.0

    def max_power(self, t_a, t_b):
        """The largest power over [t_a, t_b]: E / tau where the interval overlaps the delivery, else 0."""
        return self.E / self.tau if (t_b > self.t0 and t_a < self.t0 + self.tau) else 0.0

    def as_dict(self):
        return {"E_J": self.E, "tau_s": self.tau, "t0_s": self.t0, "shape": self.shape}


def initial_state(n, sei0=None):
    """The fresh state (bcrnn.fresh_state), or Stage 7's with the SEI's initial amount set to sei0."""
    return bcrnn.fresh_state(n) if sei0 is None else M7.initial_state(n, sei0)


def _c0(sei0):
    c0n = bcrnn.C0.copy()
    if sei0 is not None:
        c0n[I_SEI] = float(sei0)
    return c0n


# ------------------------------------------------------------------------------------------------ the resolved cell
def run_resolved(model, t1_of_t, g_pos, g_neg, kin=None, kernel="numba", t_amb=None, t_end=900.0, record_dt=0.1,
                 reaction=True, levels=None, stop_level=None, probes=None, keep_series=True, progress=None,
                 max_facts=6, sources=(), max_sub=None, sei0=None):
    """stage8_model.run_resolved with the kinetics' initial state (`sei0`, D93 (6))."""
    Ta = LP.T_AMB if t_amb is None else t_amb
    kin = bcrnn.Kinetics() if kin is None else kin
    V_full = model.geom["volume_mesh"]
    m_node = LP.M_CELL * model.w_vol / V_full
    if kernel == "numpy":
        loc = RX.LocalKinetics(kin, m_node, model.C)
    else:
        import v12_kernel as KN
        loc = KN.FastKinetics(kin, m_node, model.C)
    sources = list(sources)
    t_src = min(s.pulse.t0 for s in sources) if sources else None
    loc_src = None
    if sources and max_sub is not None and kernel != "numpy":
        import stage7_kernel as K7
        loc_src = K7.FastKineticsMax(kin, m_node, model.C, max_sub)
    n_steps_after = n_imp_after = 0
    N = model.C.size
    T = np.full(N, Ta)
    c = initial_state(N, sei0)
    sei_ref = 0.15 if sei0 is None else float(sei0)
    d_bus = g_pos * model.d_pos_unit + g_neg * model.d_neg_unit
    d_gap, d_conv = model.d_gap_unit, model.d_conv_unit
    facts = {}
    rates = [float(np.max(s.share / model.C)) for s in sources]      # K/s per W of the whole cell's power

    def solver(dt):
        key = round(dt, 12)
        if key not in facts:
            if len(facts) >= max_facts:
                old = facts.pop(max(facts))
                if getattr(old, "kind", "") == "pardiso":
                    old.ps.free_memory(everything=True)
            A = (model.K + sp.diags(model.C / dt + d_conv + d_gap + d_bus)).tocsr()
            facts[key] = RX._solver_class()(A)
        return facts[key]

    levels = levels if levels is not None else {"T_onset_low": LP.T_ONSET_BAND[0], "T_onset_mean": LP.T_ONSET_MEAN,
                                                "T_onset_high": LP.T_ONSET_BAND[1]}
    cross = {k: None for k in levels}
    energy = {k: 0.0 for k in ("in_bus", "in_gap", "in_rad", "out_conv", "out_rad", "in_rxn")}
    for s in sources:
        energy["in_" + s.name] = 0.0
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
    pr_names = list(probes) if probes else []
    pr_idx = np.array([probes[k] for k in pr_names], dtype=int) if probes else np.zeros(0, int)
    pr_t, pr_T = [0.0], [T[pr_idx].copy()]
    pr_peak = {k: (float(T[pr_idx[j]] - 273.15), 0.0) for j, k in enumerate(pr_names)}
    stop = None
    while t < t_end - 1e-12:
        if reaction:
            if kernel == "numpy":
                r0, H0 = loc.heating(T, c)
            else:
                R0, H0 = loc.start(T, c)
            H_max = float(np.abs(H0).max())
            max_rate = max(max_rate, H_max)
        else:
            H_max = 0.0
        for s, rate in zip(sources, rates):
            H_max = H_max + rate * s.pulse.max_power(t, t + RX.DT_BASE)
        k = RX.choose_level(t, H_max, k_prev)
        use = loc_src if (loc_src is not None and t >= t_src) else loc
        while True:
            dt = RX.DT_BASE / 2 ** k
            if reaction:
                if kernel == "numpy":
                    Ts, cs, n_imp = loc.step(T, c, dt)
                else:
                    Ts, cs, n_imp = use.step(T, c, R0, H0, dt)
                if np.abs(Ts - T).max() > RX.DT_ACCEPT and k < RX.K_MAX:
                    k += 1; n_rejected += 1
                    continue
            else:
                Ts, cs, n_imp = T, c, 0
            break
        max_implicit = max(max_implicit, n_imp)
        if use is not loc:
            n_steps_after += 1
            n_imp_after += n_imp
        t_new = round(t + dt, 12)
        T1 = t1_of_t(t_new)
        q_rad_gain = T1 ** 4 - Ta ** 4
        rad_loss = model.w_rad * (T ** 4 - Ta ** 4)
        rhs = model.C / dt * Ts + d_conv * Ta + (d_gap + d_bus) * T1 + model.g_rad * q_rad_gain - rad_loss
        for s in sources:
            dQ = s.pulse.cumulative(t_new) - s.pulse.cumulative(t)
            if dQ != 0.0:
                rhs = rhs + (dQ / dt) * s.share
            energy["in_" + s.name] += 0.5 * dQ
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
        if pr_names:
            pr_t.append(t); pr_T.append(T[pr_idx].copy())
            for j, kname in enumerate(pr_names):
                if T[pr_idx[j]] - 273.15 > pr_peak[kname][0]:
                    pr_peak[kname] = (float(T[pr_idx[j]] - 273.15), t)
        if stop_level is not None and stop is None and Tmax >= stop_level:
            frac = (stop_level - Tmax_prev) / (Tmax - Tmax_prev) if Tmax > Tmax_prev else 1.0
            stop = {"t_s": t - dt + dt * frac, "frac": frac, "imax": imax, "Tmean_C": Tmean - 273.15,
                    "where": model.where(imax) if hasattr(model, "where") else None}
        Tmax_prev = Tmax
        if t >= rec_next - 1e-9:
            rec_next = round(rec_next + record_dt, 12)
            sei_conv = float(1 - c[i_sei, imax] / sei_ref) if sei_ref > 0 else 0.0
            series.append((t, T1, Tmax, Tmean, imax, float(1 - c[i_cat1, imax]), sei_conv,
                           float(model.w_vol[T >= LP.T_ONSET_BAND[0]].sum() / model.w_vol.sum())))
            if progress:
                progress(t, Tmax, Tmean, dt)
        if stop is not None:
            break
    for f in facts.values():
        if getattr(f, "kind", "") == "pardiso":
            f.ps.free_memory(everything=True)
    facts.clear()
    out = M8._resolved_out(model, T, c, E0, energy, sources, cross, peak, t_cat1_consumed, n_steps, n_rejected,
                           max_implicit, max_rate, t, stop, series, keep_series, max_sub, n_steps_after, n_imp_after,
                           pr_names, pr_t, pr_T, pr_peak)
    if sei0 is not None:                         # the conversions against the run's own initial amounts (Stage 7)
        c0n = _c0(sei0)
        conv = {}
        for s in ("sei", "li_an", "ele_liq", "cat1", "sep"):
            i = bcrnn.SPECIES.index(s)
            conv[s] = (float((1 - c[i] / c0n[i]) @ model.w_vol / model.w_vol.sum()) if c0n[i] > 0 else None)
        out["conversion_volume_mean_end"] = conv
    out["sei0"] = sei0
    return out


# ------------------------------------------------------------------------------------------------ the lumped cell
def run_lumped(t1_of_t, g_bus, g_link=None, f_view=None, kin=None, kernel="numba", t_amb=None, t_end=900.0,
               record_dt=0.1, reaction=True, levels=None, stop_level=None, sources=(), max_sub=None, sei0=None):
    """stage8_model.run_lumped with the kinetics' initial state (`sei0`, D93 (6))."""
    Ta = LP.T_AMB if t_amb is None else t_amb
    g_link = LP.G_GAP if g_link is None else g_link
    f_view = LP.F_VIEW if f_view is None else f_view
    kin = bcrnn.Kinetics() if kin is None else kin
    if kernel == "numpy":
        loc = RX.LocalKinetics(kin, np.array([LP.M_CELL]), np.array([LP.C_CELL]))
    else:
        import v12_kernel as KN
        loc = KN.FastKinetics(kin, np.array([LP.M_CELL]), np.array([LP.C_CELL]))
    sources = list(sources)
    t_src = min(s.pulse.t0 for s in sources) if sources else None
    loc_src = None
    if sources and max_sub is not None and kernel != "numpy":
        import stage7_kernel as K7
        loc_src = K7.FastKineticsMax(kin, np.array([LP.M_CELL]), np.array([LP.C_CELL]), max_sub)
    C, G, hA = LP.C_CELL, g_bus + g_link, LP.H_CONV * LP.A_CONV
    T = np.array([Ta]); c = initial_state(1, sei0)
    levels = levels if levels is not None else {"T_onset_low": LP.T_ONSET_BAND[0], "T_onset_mean": LP.T_ONSET_MEAN,
                                                "T_onset_high": LP.T_ONSET_BAND[1]}
    cross = {k: None for k in levels}
    t, k_prev, Tprev = 0.0, 0, Ta
    rec_next = record_dt
    out = [(0.0, Ta)]
    peak = {"T_C": Ta - 273.15, "t_s": 0.0}
    e_rxn = 0.0
    acc = {k: 0.0 for k in ("in_link", "in_rad", "out_conv", "out_rad")}
    for s in sources:
        acc["in_" + s.name] = 0.0
    stop = None
    steps_t, steps_T = [0.0], [Ta]
    while t < t_end - 1e-12:
        if reaction:
            if kernel == "numpy":
                H_max = float(np.abs(loc.heating(T, c)[1]).max())
            else:
                R0, H0 = loc.start(T, c)
                H_max = float(np.abs(H0).max())
        else:
            H_max = 0.0
        for s in sources:
            H_max = H_max + s.pulse.max_power(t, t + RX.DT_BASE) / C
        k = RX.choose_level(t, H_max, k_prev)
        use = loc_src if (loc_src is not None and t >= t_src) else loc
        while True:
            dt = RX.DT_BASE / 2 ** k
            if reaction:
                if kernel == "numpy":
                    Ts, cs, _ = loc.step(T, c, dt)
                else:
                    Ts, cs, _ = use.step(T, c, R0, H0, dt)
                if abs(Ts[0] - T[0]) > RX.DT_ACCEPT and k < RX.K_MAX:
                    k += 1; continue
            else:
                Ts, cs = T, c
            break
        t_new = round(t + dt, 12)
        T1 = t1_of_t(t_new)
        q_in = LP.EPS ** 2 * LP.SIGMA * f_view * LP.A_LAT * (T1 ** 4 - Ta ** 4)
        q_loss_rad = LP.EPS * LP.SIGMA * LP.A_CELL * (T[0] ** 4 - Ta ** 4)
        if not sources:
            Tn = (C / dt * Ts[0] + G * T1 + hA * Ta + q_in - q_loss_rad) / (C / dt + G + hA)
        else:
            q_src = 0.0
            for s in sources:
                dQ = s.pulse.cumulative(t_new) - s.pulse.cumulative(t)
                q_src += dQ / dt
                acc["in_" + s.name] += dQ
            Tn = (C / dt * Ts[0] + G * T1 + hA * Ta + q_in - q_loss_rad + q_src) / (C / dt + G + hA)
        e_rxn += C * (Ts[0] - T[0])
        acc["in_link"] += dt * G * (T1 - Tn)
        acc["in_rad"] += dt * q_in
        acc["out_conv"] += dt * hA * (Tn - Ta)
        acc["out_rad"] += dt * q_loss_rad
        T, c, t, k_prev = np.array([Tn]), cs, t_new, k
        for key, lv in levels.items():
            if cross[key] is None and Tn >= lv:
                cross[key] = t - dt + dt * (lv - Tprev) / (Tn - Tprev) if Tn > Tprev else t
        if Tn - 273.15 > peak["T_C"]:
            peak.update(T_C=Tn - 273.15, t_s=t)
        steps_t.append(t); steps_T.append(Tn)
        if stop_level is not None and stop is None and Tn >= stop_level:
            stop = {"t_s": t - dt + dt * (stop_level - Tprev) / (Tn - Tprev) if Tn > Tprev else t}
        Tprev = Tn
        if t >= rec_next - 1e-9:
            rec_next = round(rec_next + record_dt, 12)
            out.append((t, Tn))
        if stop is not None:
            break
    c0n = _c0(sei0)
    conv = {}
    for s in ("sei", "li_an", "ele_liq", "cat1", "sep"):
        i = bcrnn.SPECIES.index(s)
        conv[s] = float(1 - c[i, 0] / c0n[i]) if c0n[i] > 0 else None
    stored = C * (float(T[0]) - Ta)
    src = sum(acc["in_" + s.name] for s in sources)
    net = acc["in_link"] + acc["in_rad"] + e_rxn + src - acc["out_conv"] - acc["out_rad"]
    taken = max(acc["in_link"], 0.0) + acc["in_rad"] + max(e_rxn, 0.0) + src
    return {"cross_s": cross, "peak": peak, "reaction_heat_J": e_rxn, "conversion_end": conv, "series": np.array(out),
            "stop": stop, "t_end_s": t, "steps_t": np.array(steps_t), "steps_T": np.array(steps_T),
            "energy_J": dict(acc, in_rxn=e_rxn), "stored_J": stored, "net_in_J": net,
            "energy_residual_rel": (stored - net) / taken if taken > 0 else None,
            "sources": {s.name: dict(s.as_dict(), delivered_J=acc["in_" + s.name]) for s in sources},
            "max_sub": max_sub, "sei0": sei0, "T_final": T, "c_final": c}
