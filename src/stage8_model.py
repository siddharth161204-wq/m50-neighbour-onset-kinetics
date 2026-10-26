"""Stage 8 (version 1.4.0): the Stage 7 loops with sources from the start of the trigger's release, and the gas layer
of Part D (DECISIONS.md D77 (4), D80 and D82).

  - Sources. Each is an energy released as a triangular pulse (stage7_model.Event, the trigger's shape, D38) and a
    share of it per node of the resolved neighbour; the lumped neighbour receives the same pulse into its one node.
    The delivery of Part A enters through the can, as a uniform flux over a part of the lateral surface (`share_
    surface`): the half facing the trigger (within 90 degrees of the line of contact), or the quarter of that half
    nearest the cap. The Joule heat of Part B is released in the roll by volume (`share_volume`, the weights of the
    roll's heat capacity, as the event of D68 (3)). Each step receives each pulse's exact integral over the step, so
    the energy delivered is the source's energy to rounding; each source's largest local heating rate counts in the
    choice of the step as the reaction's does (D13's rule, D68 (3)), and each enters the energy account as `in_<name>`.
    From the first source's start on, a node is integrated with explicit sub-steps if it needs at most `max_sub` of
    them (stage7_kernel.FastKineticsMax, D68 (3)).
  - The gas layer (Part D): `SplitCell` gives the lateral wall of the can its own nodes, joined to the roll's outer
    nodes through Hoelle et al.'s resistance (Eq. 28), which depends on the interface's temperature; the ends of the
    can (the cap and the base, with the tab discs) stay as they are. `run_resolved_split` integrates it.
With no source, `run_resolved` and `run_lumped` are `v12_model.run_resolved` and `v12_model.run_lumped` operation for
operation, and with one volumetric source named "event" they are `stage7_model.run_resolved` and `run_lumped` with that
event; src/test_stage8.py checks both bitwise on synthetic histories.
"""
import math
import os
import sys
import numpy as np
import scipy.sparse as sp

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import v12_model as V                             # noqa: E402  (unchanged)
import stage7_model as M7                         # noqa: E402  (unchanged)
import stage8_inputs as IN                        # noqa: E402

LP, bcrnn, RX = V.LP, V.bcrnn, V.RX
Pulse = M7.Event                                  # E_J released from t0_s as a triangular pulse of length tau_s
K0 = 273.15


class Source:
    """A pulse and its share per node of the resolved half model (summing to 1/2: the half model holds half of the
    cell, D10); the lumped neighbour receives the whole pulse."""

    def __init__(self, name, pulse, share=None):
        self.name, self.pulse, self.share = name, pulse, share

    def as_dict(self):
        return dict(self.pulse.as_dict(), name=self.name)


# ------------------------------------------------------------------------------------------------ the shares
def share_volume(model):
    """The roll by volume (D68 (3)): w_vol over twice its sum."""
    return model.w_vol / (2.0 * model.w_vol.sum())


def surface_weights(model, geometry="half", intorder=6):
    """The node weights of a uniform flux over the lateral surface where theta <= 90 degrees ("half"), and also
    z >= 0.75 L ("capend"): the integral of each node's hat function times the region's indicator over the lateral
    facets of the half model. Returns (weights, the region's area in the half model)."""
    from skfem import FacetBasis, ElementTetP1, LinearForm, asm
    lz = V.LZ

    @LinearForm
    def region(v, w):
        th = np.arctan2(w.x[1], w.x[0])
        ind = th <= math.pi / 2
        if geometry == "capend":
            ind = ind & (w.x[2] >= IN.CAPEND_FROM * lz)
        elif geometry != "half":
            raise ValueError(geometry)
        return ind * v

    fb = FacetBasis(model.mesh, ElementTetP1(), facets=model.groups["lateral"], intorder=intorder)
    w = asm(region, fb)
    w[np.hypot(model.mesh.p[0], model.mesh.p[1]) < V.R - 1e-9] = 0.0     # round-off (below 1e-17) off the surface
    return w, float(w.sum())


def share_surface(model, geometry="half"):
    w, _ = surface_weights(model, geometry)
    return w / (2.0 * w.sum())


def surface_info(model, geometry="half"):
    """The region's area: on the mesh (both halves) and exact (pi R L for the facing half, a quarter of it for the
    cap end)."""
    _, a = surface_weights(model, geometry)
    exact = math.pi * V.R * V.LZ * (1.0 if geometry == "half" else 1.0 - IN.CAPEND_FROM)
    return {"geometry": geometry, "A_mesh_m2": 2.0 * a, "A_exact_m2": exact}


# ------------------------------------------------------------------------------------------------ the resolved cell
def run_resolved(model, t1_of_t, g_pos, g_neg, kin=None, kernel="numba", t_amb=None, t_end=900.0, record_dt=0.1,
                 reaction=True, levels=None, stop_level=None, probes=None, keep_series=True, progress=None,
                 max_facts=6, sources=(), max_sub=None):
    """stage7_model.run_resolved (fresh SEI) with any number of sources in place of the one event."""
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
    c = bcrnn.fresh_state(N)
    sei_ref = 0.15
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
    return _resolved_out(model, T, c, E0, energy, sources, cross, peak, t_cat1_consumed, n_steps, n_rejected,
                         max_implicit, max_rate, t, stop, series, keep_series, max_sub, n_steps_after, n_imp_after,
                         pr_names, pr_t, pr_T, pr_peak)


def _resolved_out(model, T, c, E0, energy, sources, cross, peak, t_cat1_consumed, n_steps, n_rejected, max_implicit,
                  max_rate, t, stop, series, keep_series, max_sub, n_steps_after, n_imp_after, pr_names, pr_t, pr_T,
                  pr_peak, w_vol=None, extra=None):
    w_vol = model.w_vol if w_vol is None else w_vol
    stored = 2 * (float(model.C @ T) - E0)
    energy = {k: 2 * v for k, v in energy.items()}
    net = energy["in_bus"] + energy["in_gap"] + energy["in_rad"] + energy["in_rxn"] - energy["out_conv"] - energy["out_rad"]
    taken_in = energy["in_bus"] + energy["in_gap"] + energy["in_rad"] + max(energy["in_rxn"], 0.0)
    for s in sources:
        net += energy["in_" + s.name]
        taken_in += energy["in_" + s.name]
    c0n = bcrnn.C0.copy()
    conv = {}
    for s in ("sei", "li_an", "ele_liq", "cat1", "sep"):
        i = bcrnn.SPECIES.index(s)
        conv[s] = (float((1 - c[i] / c0n[i]) @ w_vol / w_vol.sum()) if c0n[i] > 0 else None)
    out = {"cross_s": cross, "peak": peak, "t_cat1_consumed_at_a_node_s": t_cat1_consumed,
           "conversion_volume_mean_end": conv, "energy_J": energy, "stored_J": stored, "net_in_J": net,
           "energy_residual_rel": (stored - net) / taken_in, "steps": n_steps, "rejected": n_rejected,
           "max_implicit_nodes": max_implicit, "max_local_reaction_heating_K_per_s": max_rate, "t_end_s": t,
           "stop": stop, "series": np.array(series) if keep_series else None, "T_final": T, "c_final": c,
           "sources": {s.name: dict(s.as_dict(), delivered_J=energy["in_" + s.name]) for s in sources},
           "max_sub": max_sub, "steps_with_max_sub": n_steps_after, "implicit_node_steps_with_max_sub": n_imp_after}
    if pr_names:
        pt, pT = np.array(pr_t), np.array(pr_T)
        out["probe_t"] = pt
        out["probe_T"] = {k: pT[:, j] for j, k in enumerate(pr_names)}
        out["probe_peak"] = {k: {"T_C": v[0], "t_s": v[1]} for k, v in pr_peak.items()}
    if extra:
        out.update(extra)
    return out


# ------------------------------------------------------------------------------------------------ the lumped cell
def run_lumped(t1_of_t, g_bus, g_link=None, f_view=None, kin=None, kernel="numba", t_amb=None, t_end=900.0,
               record_dt=0.1, reaction=True, levels=None, stop_level=None, sources=(), max_sub=None):
    """stage7_model.run_lumped (fresh SEI) with any number of sources in place of the one event."""
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
    T = np.array([Ta]); c = bcrnn.fresh_state(1)
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
    c0n = bcrnn.C0.copy()
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
            "max_sub": max_sub}


# ------------------------------------------------------------------------------------------------ Part D: the gas layer
class SplitCell:
    """The resolved neighbour with its can on nodes of its own wherever the roll meets the can (Part D, D82).

    Every outer node of the base model (`v12_model.Cell2Contact`: the lateral wall, the cap and the base) but those
    of the two tab discs gets a second node, the can's, at the same place: the can's heat capacity there (the shell's
    share, D10) and its conduction along itself move to it, and so does every path through the surface (the contact
    with the trigger, convection, radiation in and out) and the delivered flux; the roll's node keeps the roll's heat
    capacity, its conduction and the kinetics. The tab discs (the welds of the tabs to the cap and the base, D37)
    stay joined, with their tab paths. Each pair is joined by its area over Hoelle et al.'s resistance (Eq. 28) at
    the interface's temperature, the mean of the two nodes: on the half of the wall facing the trigger (theta <= 90
    degrees) at most 0.03077 m2 K/W, their heated side, and on every other part of the boundary (the far half of the
    wall, the cap and the base) at most 0.00962 m2 K/W, their "cold" side (Table VI, cell 2); a node whose area
    straddles 90 degrees has the two in parallel, by area. Below 91 C the resistance is 0, taken as R_FLOOR so that
    the two nodes stay one in effect. Node indices: the base model's first (the roll, with the tab discs), then the
    can's."""

    def __init__(self, base, r_max_heated=IN.R_MAX_HEATED, r_max_cold=IN.R_MAX_COLD, r_floor=IN.R_FLOOR,
                 n_bands=IN.N_BANDS):
        self.base = base
        mesh = base.mesh
        outer = np.unique(mesh.facets[:, base.groups["outer"]])
        discs = np.unique(np.concatenate([mesh.facets[:, base.groups["top_disc"]].ravel(),
                                          mesh.facets[:, base.groups["bottom_disc"]].ravel()]))
        split = np.setdiff1d(outer, discs)
        Nr, Nc = base.C.size, split.size
        N = Nr + Nc
        self.n_roll, self.n_can, self.interior = Nr, Nc, split
        mp = np.arange(Nr)
        mp[split] = Nr + np.arange(Nc)
        self.map = mp
        Ks = base.K_shell.tocoo()
        Kr = base.K_roll.tocoo()
        self.K = (sp.coo_matrix((Kr.data, (Kr.row, Kr.col)), shape=(N, N))
                  + sp.coo_matrix((Ks.data, (mp[Ks.row], mp[Ks.col])), shape=(N, N))).tocsr()
        full_outer = 2 * base.w["outer"].sum()
        c_shell = LP.M_CAN * LP.CP_CAN * base.w["outer"] / full_outer
        C = np.zeros(N)
        C[:Nr] = base.C
        C[split] = base.rho_cp_roll * base.w_vol[split]
        C[Nr:] = c_shell[split]
        self.C = C
        self.C_total = float(C.sum())
        self.rho_cp_roll = base.rho_cp_roll
        for name in ("d_conv_unit", "d_gap_unit", "d_pos_unit", "d_neg_unit", "g_rad", "w_rad"):
            setattr(self, name, self.move(getattr(base, name)))
        assert not base.d_pos_unit[split].any() and not base.d_neg_unit[split].any()
        self.w_vol = np.concatenate([base.w_vol, np.zeros(Nc)])
        self.geom = dict(base.geom)
        self.mesh, self.groups = base.mesh, base.groups
        self.probes = {"toward": int(mp[base.probes["toward"]]), "away": int(mp[base.probes["away"]]),
                       "toward_roll": int(base.probes["toward"]), "away_roll": int(base.probes["away"])}
        # the interface: each pair's area facing the trigger and the rest
        w_heated, _ = surface_weights(base, "half")
        self.a_heated = w_heated[split]
        self.a_cold = np.clip(base.w["outer"][split] - self.a_heated, 0.0, None)
        self.a_if = self.a_heated + self.a_cold
        self.r_floor = float(r_floor)
        self.n_bands = int(n_bands)
        self.dT_band = (IN.T_VAP_EC_C - IN.T_VAP_DMC_C) / n_bands
        mids = IN.T_VAP_DMC_C + (np.arange(n_bands) + 0.5) * self.dT_band
        tab = {}
        for side, rmax in (("heated", r_max_heated), ("cold", r_max_cold)):
            tab[side] = np.array([r_floor] + [IN.r_vap(x, rmax) for x in mids] + [rmax])   # band -1, 0..n-1, n
        self.R_tab = tab
        self.R_max = {"heated": r_max_heated, "cold": r_max_cold}
        self.geom.update({"split_nodes": int(Nc), "tab_disc_nodes": int(discs.size),
                          "A_interface_m2": float(2 * self.a_if.sum()),
                          "A_interface_heated_m2": float(2 * self.a_heated.sum()),
                          "A_interface_cold_m2": float(2 * self.a_cold.sum()),
                          "A_outer_mesh_m2": float(2 * base.w["outer"].sum())})
        rows = np.concatenate([split, Nr + np.arange(Nc), split, Nr + np.arange(Nc)])
        cols = np.concatenate([split, Nr + np.arange(Nc), Nr + np.arange(Nc), split])
        self._if_rows, self._if_cols = rows, cols
        self.r_node = np.concatenate([base.r_node, base.r_node[split]])
        self.th_node = np.concatenate([base.th_node, base.th_node[split]])
        self.z_node = np.concatenate([base.z_node, base.z_node[split]])

    def move(self, v):
        """A vector on the base nodes with the split nodes' entries moved to the can's nodes."""
        out = np.zeros(self.n_roll + self.n_can)
        out[:self.n_roll] = v
        out[self.n_roll:] = v[self.interior]
        out[self.interior] = 0.0
        return out

    def bands(self, T):
        """Each interface's band of temperature: -1 below 91 C, 0 to n-1 between, n at or above 248 C."""
        t_if = 0.5 * (T[self.interior] + T[self.n_roll:]) - K0
        b = np.floor((t_if - IN.T_VAP_DMC_C) / self.dT_band).astype(np.int64)
        b = np.where(t_if < IN.T_VAP_DMC_C, -1, b)
        b = np.where(t_if >= IN.T_VAP_EC_C, self.n_bands, b)
        return np.clip(b, -1, self.n_bands)

    def conductance(self, b):
        """Each pair's conductance (W/K, half model): its two areas over their resistances in the band, in parallel."""
        return self.a_heated / self.R_tab["heated"][b + 1] + self.a_cold / self.R_tab["cold"][b + 1]

    def interface_matrix(self, G):
        N = self.n_roll + self.n_can
        data = np.concatenate([G, G, -G, -G])
        return sp.coo_matrix((data, (self._if_rows, self._if_cols)), shape=(N, N)).tocsr()

    def where(self, i):
        i = int(i)
        part = "can" if i >= self.n_roll else "roll"
        j = int(self.interior[i - self.n_roll]) if i >= self.n_roll else i
        d = self.base.where(j)
        d["part"] = part
        return d


class _SplitSolver:
    """The split cell's matrix at one step length: K + diag(C/dt + the boundary paths) + the interface at the current
    bands. Its sparsity pattern does not change with the bands, so PARDISO's ordering and symbolic analysis (phase 11)
    are made once, and each change of the bands costs a numerical factorisation only (phase 22), which gives the same
    solution, bit for bit, as a factorisation from the start (src/test_stage8.py)."""

    def __init__(self, model, dt, d_conv, d_gap, d_bus, counter):
        import pypardiso
        self.model, self.counter = model, counter
        self.A0 = (model.K + sp.diags(model.C / dt + d_conv + d_gap + d_bus)).tocsr()
        self.ps = pypardiso.PyPardisoSolver(mtype=2)
        self.sig = None
        self.A = None

    def _matrix(self, b):
        A = sp.triu(self.A0 + self.model.interface_matrix(self.model.conductance(b)), format="csr")
        A.sort_indices()
        return A

    def set_bands(self, b):
        sig = b.tobytes()
        if sig == self.sig:
            return
        A = self._matrix(b)
        if self.A is None:
            self.ps._check_A(A)
            self.ps.set_phase(11)
            self.ps._call_pardiso(A, np.zeros(A.shape[0]))
        else:
            assert np.array_equal(A.indptr, self.A.indptr) and np.array_equal(A.indices, self.A.indices)
        self.ps.set_phase(22)
        self.ps._call_pardiso(A, np.zeros(A.shape[0]))
        self.A, self.sig = A, sig
        self.counter[0] += 1

    def solve(self, rhs):
        self.ps.set_phase(33)
        return self.ps._call_pardiso(self.A, np.ascontiguousarray(rhs, dtype=np.float64))

    def free(self):
        self.ps.free_memory(everything=True)


def run_resolved_split(model, t1_of_t, g_pos, g_neg, kin=None, t_amb=None, t_end=900.0, record_dt=0.1,
                       levels=None, stop_level=None, keep_series=True, max_facts=4, sources=(), max_sub=None,
                       layer=True, progress=None, checkpoint=None, checkpoint_every_s=300.0, wall_cap_s=None):
    """run_resolved on a SplitCell: the kinetics on the roll's nodes only (the can's wall carries none), the hot spot
    the roll's hottest node, and the interface's conductance, from the interface temperatures at the start of each
    step, in its band (64 bands between 91 and 248 C, each at its middle temperature); the matrix is factorised again
    whenever a band changes. With layer=False the resistance stays at R_FLOOR everywhere: the split alone, the
    control. Records the can's hottest node and the number of factorisations.
    With `checkpoint` (a path), the loop's whole state is written there every `checkpoint_every_s` seconds of wall
    time, and a run that finds it starts from it: a run cut off by its worker's end goes on where it stopped, and
    gives what an uninterrupted run gives, bit for bit (src/test_stage8.py). `wall_cap_s` bounds the wall time over
    all its attempts."""
    import pickle
    import time as _time
    import v12_kernel as KN
    t_wall0 = _time.time()
    Ta = LP.T_AMB if t_amb is None else t_amb
    kin = bcrnn.Kinetics() if kin is None else kin
    Nr = model.n_roll
    V_full = model.geom["volume_mesh"]
    m_node = LP.M_CELL * model.w_vol[:Nr] / V_full
    loc = KN.FastKinetics(kin, m_node, model.C[:Nr])
    sources = list(sources)
    t_src = min(s.pulse.t0 for s in sources) if sources else None
    loc_src = None
    if sources and max_sub is not None:
        import stage7_kernel as K7
        loc_src = K7.FastKineticsMax(kin, m_node, model.C[:Nr], max_sub)
    n_steps_after = n_imp_after = 0
    N = model.C.size
    T = np.full(N, Ta)
    c = bcrnn.fresh_state(Nr)
    sei_ref = 0.15
    d_bus = g_pos * model.d_pos_unit + g_neg * model.d_neg_unit
    d_gap, d_conv = model.d_gap_unit, model.d_conv_unit
    facts = {}
    n_fact = [0]
    rates = [float(np.max(s.share / model.C)) for s in sources]

    def band_now(T):
        return model.bands(T) if layer else np.full(model.n_can, -1, np.int64)

    def solver(dt, b):
        key = round(dt, 12)
        if key not in facts:
            while len(facts) >= max_facts:
                facts.pop(next(iter(facts))).free()
            facts[key] = _SplitSolver(model, dt, d_conv, d_gap, d_bus, n_fact)
        f = facts[key]
        f.set_bands(b)
        return f

    levels = levels if levels is not None else {"T_onset_low": LP.T_ONSET_BAND[0], "T_onset_mean": LP.T_ONSET_MEAN,
                                                "T_onset_high": LP.T_ONSET_BAND[1]}
    cross = {k: None for k in levels}
    energy = {k: 0.0 for k in ("in_bus", "in_gap", "in_rad", "out_conv", "out_rad", "in_rxn")}
    for s in sources:
        energy["in_" + s.name] = 0.0
    E0 = float(model.C @ T)
    t, k_prev = 0.0, 0
    Tmax_prev = T[:Nr].max()
    rec_next = record_dt
    series = [(0.0, t1_of_t(0.0), T[:Nr].max(), float(model.C @ T) / model.C_total, int(np.argmax(T[:Nr])), 0.0, 0.0,
               0.0, T[Nr:].max())]
    peak = {"Tmax_C": T[:Nr].max() - 273.15, "t_s": 0.0, "imax": 0, "Tmean_C": T[:Nr].max() - 273.15}
    can_peak = {"T_C": float(T[Nr:].max() - 273.15), "t_s": 0.0}
    i_cat1, i_sei = bcrnn.SPECIES.index("cat1"), bcrnn.SPECIES.index("sei")
    n_steps = n_rejected = max_implicit = 0
    max_rate = 0.0
    pr_names = list(model.probes)
    pr_idx = np.array([model.probes[k] for k in pr_names], dtype=int)
    pr_t, pr_T = [0.0], [T[pr_idx].copy()]
    pr_peak = {k: (float(T[pr_idx[j]] - 273.15), 0.0) for j, k in enumerate(pr_names)}
    band_steps = {"floor": 0, "ramp": 0, "max": 0}
    stop = None
    wall_prev, resumed = 0.0, 0
    if checkpoint is not None and os.path.exists(checkpoint):
        with open(checkpoint, "rb") as fh:
            st = pickle.load(fh)
        T, c, t, k_prev, Tmax_prev, rec_next = st["T"], st["c"], st["t"], st["k_prev"], st["Tmax_prev"], st["rec_next"]
        series, peak, can_peak, cross, energy, E0 = st["series"], st["peak"], st["can_peak"], st["cross"], st["energy"], st["E0"]
        n_steps, n_rejected, max_implicit, max_rate = st["n_steps"], st["n_rejected"], st["max_implicit"], st["max_rate"]
        pr_t, pr_T, pr_peak, band_steps = st["pr_t"], st["pr_T"], st["pr_peak"], st["band_steps"]
        n_steps_after, n_imp_after = st["n_steps_after"], st["n_imp_after"]
        n_fact[0] = st["n_fact"]
        wall_prev, resumed = st["wall_s"], st["resumed"] + 1
    last_save = _time.time()
    while t < t_end - 1e-12:
        if wall_cap_s is not None and wall_prev + (_time.time() - t_wall0) > wall_cap_s:
            raise RuntimeError(f"the run exceeded its wall time over all attempts ({wall_cap_s:.0f} s)")
        Tr = T[:Nr]
        R0, H0 = loc.start(Tr, c)
        H_max = float(np.abs(H0).max())
        max_rate = max(max_rate, H_max)
        for s, rate in zip(sources, rates):
            H_max = H_max + rate * s.pulse.max_power(t, t + RX.DT_BASE)
        k = RX.choose_level(t, H_max, k_prev)
        use = loc_src if (loc_src is not None and t >= t_src) else loc
        while True:
            dt = RX.DT_BASE / 2 ** k
            Tsr, cs, n_imp = use.step(Tr, c, R0, H0, dt)
            if np.abs(Tsr - Tr).max() > RX.DT_ACCEPT and k < RX.K_MAX:
                k += 1; n_rejected += 1
                continue
            break
        Ts = T.copy()
        Ts[:Nr] = Tsr
        max_implicit = max(max_implicit, n_imp)
        if use is not loc:
            n_steps_after += 1
            n_imp_after += n_imp
        b = band_now(T)
        band_steps["floor"] += int((b < 0).sum()); band_steps["max"] += int((b >= model.n_bands).sum())
        band_steps["ramp"] += int(((b >= 0) & (b < model.n_bands)).sum())
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
        Tn = solver(dt, b).solve(rhs)
        energy["in_rxn"] += float(model.C @ (Ts - T))
        energy["in_bus"] += dt * float(d_bus @ (T1 - Tn))
        energy["in_gap"] += dt * float(d_gap @ (T1 - Tn))
        energy["in_rad"] += dt * float(model.g_rad.sum() * q_rad_gain)
        energy["out_conv"] += dt * float(d_conv @ (Tn - Ta))
        energy["out_rad"] += dt * float(np.sum(rad_loss))
        T, c, t = Tn, cs, t_new
        n_steps += 1
        k_prev = k
        imax = int(np.argmax(T[:Nr])); Tmax = float(T[imax])
        jc = int(np.argmax(T[Nr:])); Tcan = float(T[Nr + jc])
        for key, lv in levels.items():
            if cross[key] is None and Tmax >= lv:
                cross[key] = t - dt + dt * (lv - Tmax_prev) / (Tmax - Tmax_prev) if Tmax > Tmax_prev else t
        Tmean = float(model.C @ T) / model.C_total
        if Tmax - 273.15 > peak["Tmax_C"]:
            peak.update(Tmax_C=Tmax - 273.15, t_s=t, imax=imax)
        peak["Tmean_C"] = max(peak["Tmean_C"], Tmean - 273.15)
        if Tcan - 273.15 > can_peak["T_C"]:
            can_peak = {"T_C": Tcan - 273.15, "t_s": t, "where": model.where(Nr + jc)}
        pr_t.append(t); pr_T.append(T[pr_idx].copy())
        for j, kname in enumerate(pr_names):
            if T[pr_idx[j]] - 273.15 > pr_peak[kname][0]:
                pr_peak[kname] = (float(T[pr_idx[j]] - 273.15), t)
        if stop_level is not None and stop is None and Tmax >= stop_level:
            frac = (stop_level - Tmax_prev) / (Tmax - Tmax_prev) if Tmax > Tmax_prev else 1.0
            stop = {"t_s": t - dt + dt * frac, "frac": frac, "imax": imax, "Tmean_C": Tmean - 273.15,
                    "where": model.where(imax), "can_max_C": Tcan - 273.15}
        Tmax_prev = Tmax
        if t >= rec_next - 1e-9:
            rec_next = round(rec_next + record_dt, 12)
            series.append((t, T1, Tmax, Tmean, imax, float(1 - c[i_cat1, imax]), float(1 - c[i_sei, imax] / sei_ref),
                           float(model.w_vol[:Nr][T[:Nr] >= LP.T_ONSET_BAND[0]].sum() / model.w_vol.sum()), Tcan))
            if progress:
                progress(t, Tmax, Tcan, dt, n_fact[0])
        if stop is not None:
            break
        if checkpoint is not None and _time.time() - last_save >= checkpoint_every_s:
            st = {"T": T, "c": c, "t": t, "k_prev": k_prev, "Tmax_prev": Tmax_prev, "rec_next": rec_next,
                  "series": series, "peak": peak, "can_peak": can_peak, "cross": cross, "energy": energy, "E0": E0,
                  "n_steps": n_steps, "n_rejected": n_rejected, "max_implicit": max_implicit, "max_rate": max_rate,
                  "pr_t": pr_t, "pr_T": pr_T, "pr_peak": pr_peak, "band_steps": band_steps,
                  "n_steps_after": n_steps_after, "n_imp_after": n_imp_after, "n_fact": n_fact[0],
                  "wall_s": wall_prev + (_time.time() - t_wall0), "resumed": resumed}
            tmp = checkpoint + f".tmp{os.getpid()}"
            with open(tmp, "wb") as fh:
                pickle.dump(st, fh, protocol=pickle.HIGHEST_PROTOCOL)
            os.replace(tmp, checkpoint)
            last_save = _time.time()
    for f in facts.values():
        f.free()
    facts.clear()
    extra = {"can_peak": can_peak, "factorisations": n_fact[0], "interface_node_steps": band_steps,
             "layer": bool(layer), "resumed": resumed, "wall_all_attempts_s": wall_prev + (_time.time() - t_wall0)}
    return _resolved_out(model, T, c, E0, energy, sources, cross, peak, None, n_steps, n_rejected, max_implicit,
                         max_rate, t, stop, series, keep_series, max_sub, n_steps_after, n_imp_after, pr_names, pr_t,
                         pr_T, pr_peak, w_vol=model.w_vol[:Nr], extra=extra)
