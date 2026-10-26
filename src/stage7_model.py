"""Stage 7 (version 1.3.0): the Stage 5 loops with two additions (DECISIONS.md D66 and D68).

  - The initial state of the kinetics as an argument: the aged SEI of D57 (1) sets the SEI's initial amount to 0 in
    every node and in the lumped node; everything else starts fresh, as in the source paper's Fig. 2 (`bcrnn.C0`).
  - An event: an energy released in the neighbour from a given time, as a triangular pulse of a given length (the
    trigger's shape, D38), over the roll by volume in the resolved cell and into the lumped node (the internal short
    of D57 (2), D68). Each step receives the pulse's exact integral over the step, so the energy delivered is the
    event's energy to rounding; its heating counts in the choice of the step as the reaction's does (D13's rule, with
    the largest local heating rate of the event added to the reaction's), and it enters the energy account as
    `in_event`. The lumped loop keeps an energy account as well.
With the fresh state and no event both loops are `v12_model.run_resolved` and `v12_model.run_lumped`, operation for
operation: src/test_stage7.py checks that every output is bitwise equal on synthetic histories.
"""
import os
import sys
import numpy as np
import scipy.sparse as sp

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import v12_model as V                             # noqa: E402  (the Stage 5 model, unchanged)

LP, bcrnn, RX = V.LP, V.bcrnn, V.RX
I_SEI = bcrnn.SPECIES.index("sei")


def initial_state(n, sei0=None):
    """The kinetics' initial amounts in n nodes: the fresh state (bcrnn.C0), with the SEI's amount set to sei0 if
    given (0 for the aged SEI of D57 (1))."""
    c = bcrnn.fresh_state(n)
    if sei0 is not None:
        c[I_SEI, :] = float(sei0)
    return c


class Event:
    """E_J released from t0_s over a triangular pulse of length tau_s (peak power 2 E / tau at t0 + tau / 2)."""

    def __init__(self, E_J, tau_s, t0_s):
        self.E, self.tau, self.t0 = float(E_J), float(tau_s), float(t0_s)

    def cumulative(self, t):
        s = t - self.t0
        if s <= 0.0:
            return 0.0
        if s >= self.tau:
            return self.E
        if s <= self.tau / 2:
            return 2.0 * self.E * (s / self.tau) ** 2
        return self.E - 2.0 * self.E * ((self.tau - s) / self.tau) ** 2

    def power(self, t):
        s = t - self.t0
        if s <= 0.0 or s >= self.tau:
            return 0.0
        peak = 2.0 * self.E / self.tau
        return peak * (s / (self.tau / 2)) if s <= self.tau / 2 else peak * ((self.tau - s) / (self.tau / 2))

    def max_power(self, t_a, t_b):
        """The largest power over [t_a, t_b]: the pulse is linear on each half, so its ends and its peak suffice."""
        p = max(self.power(t_a), self.power(t_b))
        tp = self.t0 + self.tau / 2
        if t_a <= tp <= t_b:
            p = max(p, 2.0 * self.E / self.tau)
        return p

    def as_dict(self):
        return {"E_J": self.E, "tau_s": self.tau, "t0_s": self.t0}


# ------------------------------------------------------------------------------------------------ the resolved cell
def run_resolved(model, t1_of_t, g_pos, g_neg, kin=None, kernel="numba", t_amb=None, t_end=900.0, record_dt=0.1,
                 reaction=True, levels=None, stop_level=None, probes=None, keep_series=True, progress=None,
                 max_facts=6, sei0=None, event=None, max_sub_event=None):
    """v12_model.run_resolved with the initial SEI (`sei0`) and an `event` (an Event, or None); with `max_sub_event`,
    every step that starts at or after the event's time integrates explicitly the nodes that need up to that many
    sub-steps (stage7_kernel.py, D68 (3)), the steps before it as Stage 5 does. The series column
    that v12_model fills with the SEI converted at the hottest node is computed against the run's own initial SEI
    (and is 0 where that is 0); the record adds the event's energy, the account's `in_event`, and each history's
    peak after the event."""
    Ta = LP.T_AMB if t_amb is None else t_amb
    kin = bcrnn.Kinetics() if kin is None else kin
    V_full = model.geom["volume_mesh"]
    m_node = LP.M_CELL * model.w_vol / V_full
    if kernel == "numpy":
        loc = RX.LocalKinetics(kin, m_node, model.C)
    else:
        import v12_kernel as KN
        loc = KN.FastKinetics(kin, m_node, model.C)
    loc_ev = None
    if event is not None and max_sub_event is not None and kernel != "numpy":
        import stage7_kernel as K7
        loc_ev = K7.FastKineticsMax(kin, m_node, model.C, max_sub_event)
    n_steps_after = n_imp_after = 0
    N = model.C.size
    T = np.full(N, Ta)
    c = bcrnn.fresh_state(N) if sei0 is None else initial_state(N, sei0)
    sei_ref = 0.15 if sei0 is None else float(sei0)
    d_bus = g_pos * model.d_pos_unit + g_neg * model.d_neg_unit
    d_gap, d_conv = model.d_gap_unit, model.d_conv_unit
    facts = {}
    if event is not None:
        ev_share = model.w_vol / (2.0 * model.w_vol.sum())    # the half model holds half the cell (D10)
        ev_rate = float(np.max(ev_share / model.C))           # K/s per W of the whole cell's event power

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
    if event is not None:
        energy["in_event"] = 0.0
    E0 = float(model.C @ T)
    t, k_prev = 0.0, 0
    Tmax_prev = T.max()
    rec_next = record_dt
    series = [(0.0, t1_of_t(0.0), T.max(), float(model.C @ T) / model.C_total, int(np.argmax(T)), 0.0, 0.0, 0.0)]
    peak = {"Tmax_C": T.max() - 273.15, "t_s": 0.0, "imax": 0, "Tmean_C": T.max() - 273.15}
    after = None
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
        if event is not None:
            H_max = H_max + ev_rate * event.max_power(t, t + RX.DT_BASE)
        k = RX.choose_level(t, H_max, k_prev)
        use = loc_ev if (loc_ev is not None and t >= event.t0) else loc
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
        if event is not None:
            dQ = event.cumulative(t_new) - event.cumulative(t)
            if dQ != 0.0:
                rhs = rhs + (dQ / dt) * ev_share
            energy["in_event"] += 0.5 * dQ
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
        if event is not None and t > event.t0:
            if after is None:
                after = {"Tmax_C": -1e9, "t_Tmax_s": None, "Tmean_C": -1e9, "t_Tmean_s": None,
                         "probes": {kk: (-1e9, None) for kk in pr_names}}
            if Tmax - 273.15 > after["Tmax_C"]:
                after.update(Tmax_C=Tmax - 273.15, t_Tmax_s=t, imax=imax)
            if Tmean - 273.15 > after["Tmean_C"]:
                after.update(Tmean_C=Tmean - 273.15, t_Tmean_s=t)
            for j, kname in enumerate(pr_names):
                if T[pr_idx[j]] - 273.15 > after["probes"][kname][0]:
                    after["probes"][kname] = (float(T[pr_idx[j]] - 273.15), t)
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
    stored = 2 * (float(model.C @ T) - E0)
    energy = {k: 2 * v for k, v in energy.items()}
    net = energy["in_bus"] + energy["in_gap"] + energy["in_rad"] + energy["in_rxn"] - energy["out_conv"] - energy["out_rad"]
    taken_in = energy["in_bus"] + energy["in_gap"] + energy["in_rad"] + max(energy["in_rxn"], 0.0)
    if event is not None:
        net += energy["in_event"]
        taken_in += energy["in_event"]
    c0n = bcrnn.C0.copy()
    if sei0 is not None:
        c0n[I_SEI] = float(sei0)
    conv = {}
    for s in ("sei", "li_an", "ele_liq", "cat1", "sep"):
        i = bcrnn.SPECIES.index(s)
        conv[s] = (float((1 - c[i] / c0n[i]) @ model.w_vol / model.w_vol.sum()) if c0n[i] > 0 else None)
    out = {"cross_s": cross, "peak": peak, "t_cat1_consumed_at_a_node_s": t_cat1_consumed,
           "conversion_volume_mean_end": conv, "energy_J": energy, "stored_J": stored, "net_in_J": net,
           "energy_residual_rel": (stored - net) / taken_in, "steps": n_steps, "rejected": n_rejected,
           "max_implicit_nodes": max_implicit, "max_local_reaction_heating_K_per_s": max_rate, "t_end_s": t,
           "stop": stop, "series": np.array(series) if keep_series else None, "T_final": T, "c_final": c}
    if event is not None:
        out["event"] = dict(event.as_dict(), delivered_J=energy["in_event"], max_sub_after=max_sub_event,
                            steps_after=n_steps_after, implicit_node_steps_after=n_imp_after)
        if after is not None:
            after["probes"] = {k: {"T_C": v[0], "t_s": v[1]} for k, v in after["probes"].items()}
        out["after_event"] = after
    if pr_names:
        pt, pT = np.array(pr_t), np.array(pr_T)
        out["probe_t"] = pt
        out["probe_T"] = {k: pT[:, j] for j, k in enumerate(pr_names)}
        out["probe_peak"] = {k: {"T_C": v[0], "t_s": v[1]} for k, v in pr_peak.items()}
    return out


# ------------------------------------------------------------------------------------------------ the lumped cell
def run_lumped(t1_of_t, g_bus, g_link=None, f_view=None, kin=None, kernel="numba", t_amb=None, t_end=900.0,
               record_dt=0.1, reaction=True, levels=None, stop_level=None, sei0=None, event=None, max_sub_event=None):
    """v12_model.run_lumped with the initial SEI (`sei0`), an `event`, an energy account, and `max_sub_event` as in
    run_resolved."""
    Ta = LP.T_AMB if t_amb is None else t_amb
    g_link = LP.G_GAP if g_link is None else g_link
    f_view = LP.F_VIEW if f_view is None else f_view
    kin = bcrnn.Kinetics() if kin is None else kin
    if kernel == "numpy":
        loc = RX.LocalKinetics(kin, np.array([LP.M_CELL]), np.array([LP.C_CELL]))
    else:
        import v12_kernel as KN
        loc = KN.FastKinetics(kin, np.array([LP.M_CELL]), np.array([LP.C_CELL]))
    loc_ev = None
    if event is not None and max_sub_event is not None and kernel != "numpy":
        import stage7_kernel as K7
        loc_ev = K7.FastKineticsMax(kin, np.array([LP.M_CELL]), np.array([LP.C_CELL]), max_sub_event)
    C, G, hA = LP.C_CELL, g_bus + g_link, LP.H_CONV * LP.A_CONV
    T = np.array([Ta]); c = bcrnn.fresh_state(1) if sei0 is None else initial_state(1, sei0)
    levels = levels if levels is not None else {"T_onset_low": LP.T_ONSET_BAND[0], "T_onset_mean": LP.T_ONSET_MEAN,
                                                "T_onset_high": LP.T_ONSET_BAND[1]}
    cross = {k: None for k in levels}
    t, k_prev, Tprev = 0.0, 0, Ta
    rec_next = record_dt
    out = [(0.0, Ta)]
    peak = {"T_C": Ta - 273.15, "t_s": 0.0}
    after = None
    e_rxn = 0.0
    acc = {k: 0.0 for k in ("in_link", "in_rad", "out_conv", "out_rad", "in_event")}
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
        if event is not None:
            H_max = H_max + event.max_power(t, t + RX.DT_BASE) / C
        k = RX.choose_level(t, H_max, k_prev)
        use = loc_ev if (loc_ev is not None and t >= event.t0) else loc
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
        if event is None:
            Tn = (C / dt * Ts[0] + G * T1 + hA * Ta + q_in - q_loss_rad) / (C / dt + G + hA)
        else:
            dQ = event.cumulative(t_new) - event.cumulative(t)
            Tn = (C / dt * Ts[0] + G * T1 + hA * Ta + q_in - q_loss_rad + dQ / dt) / (C / dt + G + hA)
            acc["in_event"] += dQ
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
        if event is not None and t > event.t0:
            if after is None or Tn - 273.15 > after["T_C"]:
                after = {"T_C": Tn - 273.15, "t_s": t}
        steps_t.append(t); steps_T.append(Tn)
        if stop_level is not None and stop is None and Tn >= stop_level:
            stop = {"t_s": t - dt + dt * (stop_level - Tprev) / (Tn - Tprev) if Tn > Tprev else t}
        Tprev = Tn
        if t >= rec_next - 1e-9:
            rec_next = round(rec_next + record_dt, 12)
            out.append((t, Tn))
        if stop is not None:
            break
    c0n = bcrnn.C0.copy()
    if sei0 is not None:
        c0n[I_SEI] = float(sei0)
    conv = {}
    for s in ("sei", "li_an", "ele_liq", "cat1", "sep"):
        i = bcrnn.SPECIES.index(s)
        conv[s] = float(1 - c[i, 0] / c0n[i]) if c0n[i] > 0 else None
    stored = C * (float(T[0]) - Ta)
    net = acc["in_link"] + acc["in_rad"] + e_rxn + acc["in_event"] - acc["out_conv"] - acc["out_rad"]
    taken = max(acc["in_link"], 0.0) + acc["in_rad"] + max(e_rxn, 0.0) + acc["in_event"]
    res = {"cross_s": cross, "peak": peak, "reaction_heat_J": e_rxn, "conversion_end": conv, "series": np.array(out),
           "stop": stop, "t_end_s": t, "steps_t": np.array(steps_t), "steps_T": np.array(steps_T),
           "energy_J": dict(acc, in_rxn=e_rxn), "stored_J": stored, "net_in_J": net,
           "energy_residual_rel": (stored - net) / taken if taken > 0 else None}
    if event is not None:
        res["event"] = dict(event.as_dict(), delivered_J=acc["in_event"], max_sub_after=max_sub_event)
        res["after_event"] = after
    return res
