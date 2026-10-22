"""Stage 5 (version 1.2.0): the resolved and the lumped neighbour in the configuration of Fransson et al. (2024),
two LG M50 cells in direct contact joined by welded tabs (DECISIONS.md D33 to D44; predictions_v12.md).

What changes from the two-cell study (external/m50-two-cell-pilot), each from a source or a declared bracket:
  - the 2 mm air gap becomes a line contact: within the 45 degree sector facing the trigger cell, the local
    conductance per unit area is h(theta) = k_air / (delta(theta) + k_air / h_c), with delta = 2 R (1 - cos theta)
    the gap between the two cans along the line of centres and h_c a published steel-on-steel contact conductance
    (low, central, high; D36). At theta = 0 it equals h_c; away from the line it is the air in the wedge;
  - radiation as before, with the view factor of two cylinders in contact (D38);
  - welded tabs instead of busbars: series, one tab at the neighbour's base; parallel, one at the cap and one at the
    base, each a conductance from the two-cell study's archived nickel-strip values (D37);
  - room convection and radiation as before (D6, D5), the trigger as before (33.2 kJ, triangular over 10 or 30 s);
  - the neighbour's reaction heat fed back as in Stage 2 (src/reactive.py, D13), one-way.
With the two-cell configuration switched back (`Cell2Contact(geometry="two_cell")`, the two-cell paths in
`lumped_pair` and `run_lumped`), the loops below reproduce Stage 1 and Stage 2 (V2, src/v12_checks.py).
"""
import math
import os
import sys
import numpy as np
import scipy.sparse as sp

HERE = os.path.dirname(os.path.abspath(__file__))
EXT = os.path.join(HERE, "..", "external", "m50-two-cell-pilot", "src")
if EXT not in sys.path:
    sys.path.insert(0, EXT)
import lumped_two_cell as LP                      # noqa: E402
import bcrnn                                      # noqa: E402
import reactive as RX                             # noqa: E402
import v12_mesh as MS                             # noqa: E402

R = LP.D_CELL / 2
LZ = LP.L_CELL

# ------------------------------------------------------------------------------------------------ inputs (D36 to D38)
H_CONTACT = {"low": 200.0, "central": 2000.0, "high": 3700.0}      # W/(m2 K), Lienhard and Lienhard, A Heat Transfer Textbook, 6th ed., Table 2.1 (D36)
G_TAB = {"low": 0.005, "central": 0.0068, "high": 0.010}          # W/K per tab (D37)
CONNECTIONS = ("series", "parallel")
X_TOUCH = 1.0                                                     # centre distance over diameter, cans in contact
F_TOUCH = (math.sqrt(X_TOUCH ** 2 - 1.0) + math.asin(1.0 / X_TOUCH) - X_TOUCH) / math.pi   # D38: 0.18169
A_FACE = LP.A_FACE                                                # the 90 degree sector, as the two-cell study
A_CONV = LP.A_CONV                                                # D6: no room convection in the sector
A_RAD_TOUCH = LP.A_CELL - LP.EPS * F_TOUCH * LP.A_LAT              # D5's radiosity form, lumped pair
E_BODY = max(LP.E_BODY_LIST)                                       # 33.2 kJ, Databank maximum at 100 % SOC (D38)
LEVEL_PROP = LP.T_ONSET_BAND[0]                                    # 255.7 C in K, the model's propagation
T_WINDOW = 900.0


def tabs(connection, g_tab):
    """(g_pos, g_neg) in W/K at the neighbour's cap and base: D37."""
    if connection == "series":
        return 0.0, g_tab
    if connection == "parallel":
        return g_tab, g_tab
    raise ValueError(connection)


def contact_gap_m(theta):
    return 2.0 * R * (1.0 - np.cos(theta))


def h_local(theta, h_c, k_air=LP.K_AIR):
    """Local conductance per unit area (W/(m2 K)) between the cans at angle theta within the sector (D36)."""
    return k_air / (contact_gap_m(theta) + k_air / h_c)


def g_per_length(h_c, k_air=LP.K_AIR, theta_max=MS.SECTOR):
    """Exact integral of h_local over -theta_max..theta_max on the can radius: W/(m K)."""
    Y = k_air / h_c
    a = math.sqrt((4 * R + Y) / Y)
    return 4 * k_air * R / math.sqrt(Y * (4 * R + Y)) * math.atan(math.tan(theta_max / 2) * a)


def g_contact(h_c, k_air=LP.K_AIR):
    """Contact plus wedge conductance of the whole cell, W/K."""
    return LZ * g_per_length(h_c, k_air)


def contact_split(h_c, k_air=LP.K_AIR):
    """For the record: the part within the band where the wedge gap is below k_air/h_c (the contact) and the rest."""
    Y = k_air / h_c
    th_y = math.acos(1.0 - Y / (2 * R))
    total = g_per_length(h_c, k_air)
    band = g_per_length(h_c, k_air, theta_max=th_y)
    return {"theta_band_deg": math.degrees(th_y), "band_width_mm": 2e3 * R * th_y, "contact_band_W_per_mK": band,
            "wedge_W_per_mK": total - band, "total_W_per_mK": total, "total_W_per_K": LZ * total}


def f_local_touch(theta):
    """resolved_cell2.f_local with the cans in contact (centre distance 2R)."""
    th = np.asarray(theta, dtype=float)
    px, py = R * np.cos(th), R * np.sin(th)
    vx, vy = 2 * R - px, -py
    d = np.hypot(vx, vy)
    alpha = np.arcsin(np.clip(R / np.maximum(d, 1e-300), -1, 1))
    cos_psi = (np.cos(th) * vx + np.sin(th) * vy) / np.maximum(d, 1e-300)
    psi = np.arccos(np.clip(cos_psi, -1, 1))
    lo = np.maximum(psi - alpha, -math.pi / 2)
    hi = np.minimum(psi + alpha, math.pi / 2)
    return np.where(hi > lo, 0.5 * (np.sin(hi) - np.sin(lo)), 0.0)


# ------------------------------------------------------------------------------------------------ the lumped pair
def lumped_pair(e_body, tau, g_bus, g_link, f_view, a_rad, t_amb=LP.T_AMB, t_end=LP.T_END, dt=LP.DT,
                dt_series=LP.DT_SERIES):
    """lumped_two_cell.run with the paths as arguments: the cell-1 history that drives the neighbour (one-way).
    With g_link = G_GAP, f_view = F_VIEW and a_rad = A_RAD it is the published run, operation for operation (V2).
    Returns (series [(t, T1_C, T2_C)], T1max_C, t_T1max_s)."""
    def q_release(t):
        if t < 0 or t > tau:
            return 0.0
        peak = 2.0 * e_body / tau
        return peak * (t / (tau / 2)) if t <= tau / 2 else peak * ((tau - t) / (tau / 2))

    def loss(T):
        return LP.H_CONV * A_CONV * (T - t_amb) + LP.EPS * LP.SIGMA * a_rad * (T ** 4 - t_amb ** 4)

    def coupling(T1, T2):
        cond = (g_bus + g_link) * (T1 - T2)
        rad = LP.EPS ** 2 * LP.SIGMA * f_view * LP.A_LAT * (T1 ** 4 - T2 ** 4)
        return cond + rad

    T1 = T2 = t_amb
    n_steps = int(round(t_end / dt))
    every = int(round(dt_series / dt))
    series = [(0.0, T1 - 273.15, T2 - 273.15)]
    T1max, tmax = T1, 0.0
    for n in range(n_steps):
        t = n * dt
        q12 = coupling(T1, T2)
        dT1 = (q_release(t) - loss(T1) - q12) / LP.C_CELL
        dT2 = (q12 - loss(T2)) / LP.C_CELL
        T1 += dT1 * dt
        T2 += dT2 * dt
        t_new = (n + 1) * dt
        if T1 > T1max:
            T1max, tmax = T1, t_new
        if (n + 1) % every == 0:
            series.append((round(t_new, 3), T1 - 273.15, T2 - 273.15))
    return series, T1max - 273.15, tmax


def t1_history(series_rows):
    """The published t1_interpolator, from rows of (t, T1_C, T2_C) written as the published CSV writes them."""
    data = np.array([(float(f"{a:.1f}"), float(f"{b:.4f}"), float(f"{c:.4f}")) for a, b, c in series_rows])
    t, T1 = data[:, 0], data[:, 1] + 273.15

    def f(tt):
        return float(np.interp(tt, t, T1))
    return f, data


def stage5_t1(connection, h_c, g_tab, tau, e_body=E_BODY, t_amb=LP.T_AMB):
    g_pos, g_neg = tabs(connection, g_tab)
    rows, T1max, tmax = lumped_pair(e_body, tau, g_pos + g_neg, g_contact(h_c), F_TOUCH, A_RAD_TOUCH, t_amb)
    f, data = t1_history(rows)
    return f, data, T1max, tmax


# ------------------------------------------------------------------------------------------------ the resolved cell
class Cell2Contact:
    """The resolved neighbour of resolved_cell2.Cell2Model on the Stage 5 mesh, with the contact, tab and radiation
    paths of this stage. Attribute names follow Cell2Model so that one loop serves both; `d_gap_unit` here holds the
    contact and wedge path, the one that takes the place of the two-cell gap.

    geometry="two_cell" switches the configuration back: the published mesh, the uniform 2 mm gap over the sector,
    the negative strip on the bottom annulus and the 2 mm view factor. V2 checks that every array then equals the
    published Cell2Model's."""

    def __init__(self, h_c=None, refine=1.0, k_radial=None, k_axial=None, intorder=6, geometry="stage5"):
        from skfem import Basis, FacetBasis, ElementTetP1, BilinearForm, LinearForm, asm
        self.geometry = geometry
        two = geometry == "two_cell"
        if two:
            import mesh_cell2 as MC
            self.mesh, self.mesh_info = MC.build_mesh(R, LZ, refine)
            self.groups = MC.classify_facets(self.mesh, R, LZ)
        else:
            self.mesh, self.mesh_info = MS.build_mesh(R, LZ, refine)
            self.groups = MS.classify_facets(self.mesh, R, LZ)
        m = self.mesh
        e = ElementTetP1()
        self.vb = Basis(m, e)
        fb = {k: FacetBasis(m, e, facets=v) for k, v in self.groups.items() if k != "symmetry" and len(v)}
        kr = LP.K_RADIAL if k_radial is None else k_radial
        kz = LP.K_AXIAL if k_axial is None else k_axial

        @BilinearForm
        def conduction(u, v, w):
            x, y = w.x[0], w.x[1]
            r = np.sqrt(x ** 2 + y ** 2) + 1e-15
            ex, ey = x / r, y / r
            gu, gv = u.grad, v.grad
            ur = ex * gu[0] + ey * gu[1]
            vr = ex * gv[0] + ey * gv[1]
            return kz * (gu[0] * gv[0] + gu[1] * gv[1] + gu[2] * gv[2]) + (kr - kz) * ur * vr

        kt = LP.K_CAN * LP.T_CAN

        @BilinearForm
        def shell(u, v, w):
            n = w.n
            gu, gv = u.grad, v.grad
            un = gu[0] * n[0] + gu[1] * n[1] + gu[2] * n[2]
            vn = gv[0] * n[0] + gv[1] * n[1] + gv[2] * n[2]
            return kt * sum((gu[i] - un * n[i]) * (gv[i] - vn * n[i]) for i in range(3))

        @LinearForm
        def one(v, w):
            return v

        if two:
            from resolved_cell2 import f_local as f_view_fn
            f_view_total = LP.F_VIEW
        else:
            f_view_fn, f_view_total = f_local_touch, F_TOUCH

        @LinearForm
        def view(v, w):
            th = np.arctan2(w.x[1], w.x[0])
            return f_view_fn(th) * v

        hc = h_c

        @LinearForm
        def contact(v, w):
            return h_local(np.abs(np.arctan2(w.x[1], w.x[0])), hc) * v

        self.h_c = h_c
        self.K_roll = asm(conduction, self.vb).tocsr()
        self.K_shell = asm(shell, fb["outer"]).tocsr()
        self.K = (self.K_roll + self.K_shell).tocsr()
        w_vol = asm(one, self.vb)
        self.w_vol = w_vol
        self.w = {k: asm(one, b) for k, b in fb.items()}
        if two:
            g_view = asm(view, fb["lateral"])
        else:
            g_view = asm(view, FacetBasis(m, e, facets=self.groups["lateral"], intorder=intorder))
        full = lambda k: 2 * self.w[k].sum()
        self.geom = {
            "volume_mesh": 2 * w_vol.sum(), "volume_exact": math.pi * R ** 2 * LZ,
            "A_outer_mesh": full("outer"), "A_outer_exact": LP.A_CELL,
            "A_face_mesh": full("sector"), "A_face_exact": A_FACE,
            "A_conv_mesh": full("conv"), "A_conv_exact": A_CONV,
            "FA_lat_mesh": 2 * g_view.sum(), "FA_lat_exact": f_view_total * LP.A_LAT,
        }
        c_shell_total = LP.M_CAN * LP.CP_CAN
        c_shell = c_shell_total * self.w["outer"] / full("outer")
        self.rho_cp_roll = (LP.C_CELL - c_shell_total) / self.geom["volume_mesh"]
        self.C = self.rho_cp_roll * w_vol + c_shell
        self.C_total = self.C.sum()
        # boundary weights normalised so that a uniform field reproduces the lumped totals exactly (V0, V1)
        self.d_conv_unit = LP.H_CONV * LP.A_CONV * self.w["conv"] / full("conv")
        if two:
            self.d_gap_unit = LP.G_GAP * self.w["sector"] / full("sector")
            self.d_pos_unit = self.w["top_disc"] / full("top_disc")
            self.d_neg_unit = self.w["bottom_annulus"] / full("bottom_annulus")
        else:
            w_contact = asm(contact, FacetBasis(m, e, facets=self.groups["sector"], intorder=intorder))
            G_exact = g_contact(h_c)
            self.geom.update({"G_contact_mesh": 2 * w_contact.sum(), "G_contact_exact": G_exact,
                              "A_disc_top_mesh": full("top_disc"), "A_disc_bottom_mesh": full("bottom_disc"),
                              "A_disc_exact": math.pi * MS.R_DISC ** 2})
            self.d_gap_unit = G_exact * w_contact / (2 * w_contact.sum())                 # contact and wedge
            self.d_pos_unit = self.w["top_disc"] / full("top_disc")
            self.d_neg_unit = self.w["bottom_disc"] / full("bottom_disc")
        self.g_rad = LP.EPS ** 2 * LP.SIGMA * f_view_total * LP.A_LAT * g_view / (2 * g_view.sum())
        self.w_rad = LP.EPS * LP.SIGMA * LP.A_CELL * self.w["outer"] / full("outer")
        p = self.mesh.p
        self.r_node = np.hypot(p[0], p[1])
        self.th_node = np.arctan2(p[1], p[0])
        self.z_node = p[2]
        self.probes = {"toward": self.node_at(R, 0.0, LZ / 2), "away": self.node_at(R, math.pi, LZ / 2)}

    def node_at(self, r, th, z):
        p = self.mesh.p
        x, y = r * math.cos(th), r * math.sin(th)
        d = (p[0] - x) ** 2 + (p[1] - y) ** 2 + (p[2] - z) ** 2
        i = int(np.argmin(d))
        assert d[i] < 1e-16, ("no node at", r, th, z)
        return i

    def where(self, i):
        return {"r_mm": 1e3 * float(self.r_node[i]), "theta_deg": math.degrees(float(self.th_node[i])),
                "z_mm": 1e3 * float(self.z_node[i])}


# ------------------------------------------------------------------------------------------------ reactive loops
def run_resolved(model, t1_of_t, g_pos, g_neg, kin=None, kernel="numba", t_amb=None, t_end=900.0, record_dt=0.1,
                 reaction=True, levels=None, stop_level=None, probes=None, keep_series=True, progress=None,
                 max_facts=6):
    """reactive.run_resolved (Stage 2), operation for operation, with these additions: the kinetics as an argument
    (a posterior draw), the ambient temperature, the compiled reaction sub-step (`kernel="numba"`, D41) or the
    published numpy one (`kernel="numpy"`), an optional stop once the hottest node reaches `stop_level` (the model's
    propagation, D35), and probe nodes recorded at every step (the mid-surface thermocouple, D39). `max_facts`, the
    number of factorisations kept, changes memory use only."""
    Ta = LP.T_AMB if t_amb is None else t_amb
    kin = bcrnn.Kinetics() if kin is None else kin
    V_full = model.geom["volume_mesh"]
    m_node = LP.M_CELL * model.w_vol / V_full
    if kernel == "numpy":
        loc = RX.LocalKinetics(kin, m_node, model.C)
    else:
        import v12_kernel as KN
        loc = KN.FastKinetics(kin, m_node, model.C)
    N = model.C.size
    T = np.full(N, Ta)
    c = bcrnn.fresh_state(N)
    d_bus = g_pos * model.d_pos_unit + g_neg * model.d_neg_unit
    d_gap, d_conv = model.d_gap_unit, model.d_conv_unit
    facts = {}

    def solver(dt):
        key = round(dt, 12)
        if key not in facts:
            if len(facts) >= max_facts:                  # memory only: Stage 2 keeps 6, the refined mesh fewer
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
        k = RX.choose_level(t, H_max, k_prev)
        while True:
            dt = RX.DT_BASE / 2 ** k
            if reaction:
                if kernel == "numpy":
                    Ts, cs, n_imp = loc.step(T, c, dt)
                else:
                    Ts, cs, n_imp = loc.step(T, c, R0, H0, dt)
                if np.abs(Ts - T).max() > RX.DT_ACCEPT and k < RX.K_MAX:
                    k += 1; n_rejected += 1
                    continue
            else:
                Ts, cs, n_imp = T, c, 0
            break
        max_implicit = max(max_implicit, n_imp)
        t_new = round(t + dt, 12)
        T1 = t1_of_t(t_new)
        q_rad_gain = T1 ** 4 - Ta ** 4
        rad_loss = model.w_rad * (T ** 4 - Ta ** 4)
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
            series.append((t, T1, Tmax, Tmean, imax, float(1 - c[i_cat1, imax]), float(1 - c[i_sei, imax] / 0.15),
                           float(model.w_vol[T >= LP.T_ONSET_BAND[0]].sum() / model.w_vol.sum())))
            if progress:
                progress(t, Tmax, Tmean, dt)
        if stop is not None:
            break
    for f in facts.values():                           # D47: PARDISO keeps a factorisation's memory until freed
        if getattr(f, "kind", "") == "pardiso":
            f.ps.free_memory(everything=True)
    facts.clear()
    stored = 2 * (float(model.C @ T) - E0)
    energy = {k: 2 * v for k, v in energy.items()}
    net = energy["in_bus"] + energy["in_gap"] + energy["in_rad"] + energy["in_rxn"] - energy["out_conv"] - energy["out_rad"]
    taken_in = energy["in_bus"] + energy["in_gap"] + energy["in_rad"] + max(energy["in_rxn"], 0.0)
    conv = {s: float((1 - c[bcrnn.SPECIES.index(s)] / bcrnn.C0[bcrnn.SPECIES.index(s)]) @ model.w_vol / model.w_vol.sum())
            for s in ("sei", "li_an", "ele_liq", "cat1", "sep")}
    out = {"cross_s": cross, "peak": peak, "t_cat1_consumed_at_a_node_s": t_cat1_consumed,
           "conversion_volume_mean_end": conv, "energy_J": energy, "stored_J": stored, "net_in_J": net,
           "energy_residual_rel": (stored - net) / taken_in, "steps": n_steps, "rejected": n_rejected,
           "max_implicit_nodes": max_implicit, "max_local_reaction_heating_K_per_s": max_rate, "t_end_s": t,
           "stop": stop, "series": np.array(series) if keep_series else None, "T_final": T, "c_final": c}
    if pr_names:
        pt, pT = np.array(pr_t), np.array(pr_T)
        out["probe_t"] = pt
        out["probe_T"] = {k: pT[:, j] for j, k in enumerate(pr_names)}
        out["probe_peak"] = {k: {"T_C": v[0], "t_s": v[1]} for k, v in pr_peak.items()}
    return out


def run_lumped(t1_of_t, g_bus, g_link=None, f_view=None, kin=None, kernel="numba", t_amb=None, t_end=900.0,
               record_dt=0.1, reaction=True, levels=None, stop_level=None):
    """reactive.run_lumped (Stage 2), operation for operation, with the path conductance (g_bus + g_link), the view
    factor, the ambient temperature and the kinetics as arguments, the compiled sub-step, and an optional stop."""
    Ta = LP.T_AMB if t_amb is None else t_amb
    g_link = LP.G_GAP if g_link is None else g_link
    f_view = LP.F_VIEW if f_view is None else f_view
    kin = bcrnn.Kinetics() if kin is None else kin
    if kernel == "numpy":
        loc = RX.LocalKinetics(kin, np.array([LP.M_CELL]), np.array([LP.C_CELL]))
    else:
        import v12_kernel as KN
        loc = KN.FastKinetics(kin, np.array([LP.M_CELL]), np.array([LP.C_CELL]))
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
        k = RX.choose_level(t, H_max, k_prev)
        while True:
            dt = RX.DT_BASE / 2 ** k
            if reaction:
                if kernel == "numpy":
                    Ts, cs, _ = loc.step(T, c, dt)
                else:
                    Ts, cs, _ = loc.step(T, c, R0, H0, dt)
                if abs(Ts[0] - T[0]) > RX.DT_ACCEPT and k < RX.K_MAX:
                    k += 1; continue
            else:
                Ts, cs = T, c
            break
        t_new = round(t + dt, 12)
        T1 = t1_of_t(t_new)
        q_in = LP.EPS ** 2 * LP.SIGMA * f_view * LP.A_LAT * (T1 ** 4 - Ta ** 4)
        q_loss_rad = LP.EPS * LP.SIGMA * LP.A_CELL * (T[0] ** 4 - Ta ** 4)
        Tn = (C / dt * Ts[0] + G * T1 + hA * Ta + q_in - q_loss_rad) / (C / dt + G + hA)
        e_rxn += C * (Ts[0] - T[0])
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
    conv = {s: float(1 - c[bcrnn.SPECIES.index(s), 0] / bcrnn.C0[bcrnn.SPECIES.index(s)]) for s in ("sei", "li_an", "ele_liq", "cat1", "sep")}
    return {"cross_s": cross, "peak": peak, "reaction_heat_J": e_rxn, "conversion_end": conv, "series": np.array(out),
            "stop": stop, "t_end_s": t, "steps_t": np.array(steps_t), "steps_T": np.array(steps_T)}
