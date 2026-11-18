"""Stage 14, Part A: the lower and upper bounds of the six paths (DECISIONS D153).

Run only after predictions_stage14.md has been pushed. Reads results/stage14_inputs.csv (every number
by its key) and traces rays with src/stage14_view.py, with the counts and seeds of D153 (11).

Writes
  results/stage14_raytrace.json   every ray-tracing share with its standard error and point
  results/stage14_bounds.csv      one row per path and window: lower and upper bound of the energy
                                  delivered to the facing half, the bounds of the time, and notes
  results/stage14_bounds.json     the same numbers with the terms they come from
"""
import csv
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import stage14_view as v  # noqa: E402

WINDOWS = (21.39, 120.0, 240.0, 360.0)
N_POINT = 2_000_000
N_VIEW = 4_000_000
N_BREACH = 1_000_000


def load_inputs():
    with open(os.path.join(ROOT, "results", "stage14_inputs.csv"), newline="") as fh:
        rows = {r["key"]: r for r in csv.DictReader(fh)}

    def num(key, field="value"):
        return float(rows[key][field])
    return rows, num


def se(p, n):
    return math.sqrt(max(p * (1.0 - p), 0.0) / n)


def cone_dirs(axis, beta_deg, n, rng):
    """Directions uniform over the solid angle of a cone of half-angle beta about a unit axis."""
    axis = np.asarray(axis, float)
    if beta_deg == 0.0:
        return np.repeat(axis[None, :], n, axis=0)
    cb = math.cos(math.radians(beta_deg))
    ct = 1.0 - rng.random(n) * (1.0 - cb)          # cos of the angle from the axis, uniform in [cb, 1]
    st = np.sqrt(np.maximum(0.0, 1.0 - ct * ct))
    ph = 2.0 * math.pi * rng.random(n)
    a = np.array([0.0, 0.0, 1.0]) if abs(axis[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    t1 = np.cross(axis, a)
    t1 /= np.linalg.norm(t1)
    t2 = np.cross(axis, t1)
    return (st * np.cos(ph))[:, None] * t1 + (st * np.sin(ph))[:, None] * t2 + ct[:, None] * axis


def raytrace(Rc, Lc):
    v.R, v.L = Rc, Lc
    cells = v.cells_default(trigger=True, length=Lc, radius=Rc)
    out = {"geometry": {"R_m": Rc, "L_m": Lc}}

    # (1) The share w of an isotropic emitter's directions whose first surface is the facing half.
    rng = np.random.default_rng(14)
    lift = 1e-6 * Rc
    grid = []

    def w_at(part, label, p):
        w = v.point_fraction(np.array(p), N_POINT, rng, cells=cells, facing_only=True)
        grid.append(dict(part=part, label=label, x_m=p[0], y_m=p[1], z_m=p[2], w=w, se=se(w, N_POINT)))

    for k in (0.0, 0.5, 1.0, 2.0, 5.0, 10.0):
        w_at("axis", f"trigger's axis, {k} R beyond the end", (0.0, 2.0 * Rc, Lc + max(k * Rc, lift)))
    for h in (0.01, 0.1, 1.0):
        for r in (0.0, 0.25, 0.5, 0.75, 1.0):
            angles = (0.0,) if r == 0.0 else tuple(range(0, 360, 30))
            for psi in angles:
                ps = math.radians(psi)              # psi = 0 points down, toward the neighbour
                p = (r * Rc * math.sin(ps), 2.0 * Rc - r * Rc * math.cos(ps), Lc + h * Rc)
                w_at("column", f"in front of the trigger's end, r = {r} R, psi = {psi} deg, {h} R beyond", p)
    for th in range(0, 91, 15):
        for dlt in (0.3, 0.1, 0.03, 0.01):
            t = math.radians(th)
            p = ((Rc + dlt * Rc) * math.sin(t), (Rc + dlt * Rc) * math.cos(t), Lc + lift)
            w_at("edge", f"theta = {th} deg, {dlt} R outside the can, at the end plane", p)
    out["w_grid"] = grid
    for part in ("axis", "column", "edge"):
        best = max((g for g in grid if g["part"] == part), key=lambda g: g["w"])
        out[f"w_max_{part}"] = best
    w_grid_max = max(g["w"] for g in grid)
    out["w_sup"] = max(0.25, w_grid_max)
    out["w_sup_rule"] = "the larger of 1/4 (the share an emitter approaches at the facing half's end edge) and the largest grid value"

    # (2) The facing half's view: shares ending on the trigger and leaving through each end plane.
    rng = np.random.default_rng(15)
    fv = v.facing_view(N_VIEW, rng, cells)
    out["facing_view"] = {k: (float(x) if k != "n" else int(x)) for k, x in fv.items()}
    out["facing_view"]["se_trigger"] = se(fv["trigger"], N_VIEW)
    out["facing_view"]["se_beyond_L"] = se(fv["beyond_L"], N_VIEW)

    # (3) Breach jets: the share of a cone about the outward normal whose first surface is the facing half.
    rng = np.random.default_rng(16)
    betas = (0.0, 5.0, 10.0, 15.0, 30.0, 45.0, 60.0, 90.0)
    breach = []
    for phi in range(0, 181, 5):
        ph = math.radians(phi)                     # phi = 0 faces the neighbour (straight down)
        s_pt = np.array([Rc * math.sin(ph), 2.0 * Rc - Rc * math.cos(ph), 0.5 * Lc])
        nrm = np.array([math.sin(ph), -math.cos(ph), 0.0])
        row = dict(phi_deg=phi)
        if phi == 0:
            # The breach sits on the line of contact: every direction of a cone about the normal enters
            # the neighbour at once, through the facing half (its tangent plane there is y = R).
            for b in betas:
                row[f"s_beta{int(b)}"] = 1.0
            row["s_max"], row["beta_at_max"] = 1.0, 0.0
            breach.append(row)
            continue
        for b in betas:
            n = 1 if b == 0.0 else N_BREACH
            d = cone_dirs(nrm, b, n, rng)
            o = np.repeat(s_pt[None, :] + 1e-9 * nrm[None, :], n, axis=0)
            code, pts = v.first_hit(o, d, cells, eps=1e-12)
            hit = (code == v.NB_LAT) & (pts[:, 1] >= 0.0)
            row[f"s_beta{int(b)}"] = float(hit.mean())
        row["s_max"] = max(row[f"s_beta{int(b)}"] for b in betas)
        row["beta_at_max"] = max(betas, key=lambda b: row[f"s_beta{int(b)}"])
        breach.append(row)
    out["breach"] = breach
    narrow = [r["phi_deg"] for r in breach if r["s_beta0"] == 1.0]
    out["breach_narrow_strike_phi_max_deg"] = max(narrow) if narrow else None
    out["breach_narrow_share_of_circumference_analytic"] = 60.0 / 360.0
    return out


def churchill_bernstein(Re, Pr):
    base = 0.62 * Re ** 0.5 * Pr ** (1.0 / 3.0) / (1.0 + (0.4 / Pr) ** (2.0 / 3.0)) ** 0.25
    nu765 = 0.3 + base * (1.0 + (Re / 282000.0) ** 0.625) ** 0.8
    if 40000.0 < Re < 400000.0:
        nu768 = 0.3 + base * (1.0 + (Re / 282000.0) ** 0.5)
        return max(1.2 * nu765, nu768), dict(eqn765=nu765, eqn768=nu768, rule="max(1.2 x (7.65), (7.68))")
    return nu765, dict(eqn765=nu765, rule="(7.65)")


def main():
    rows, num = load_inputs()
    Rc, Lc = num("R_cell"), num("L_cell")
    D = 2.0 * Rc
    A_f = num("A_facing")
    E_ej_max = num("db_Eej_max")
    Q_air_max = num("vendra_Qt_max")
    E_avail = E_ej_max + Q_air_max
    E_global = num("db_Etotal_max") + Q_air_max
    sigma = num("sigma")
    Tf = num("T_flame_max") + 273.15
    T0 = num("T0") + 273.15
    t_min, t_max = num("t_vent_min", "range_lo"), num("t_flame_max")   # the time bounds take the widest ends
    t_breach_min = num("fr2023_breach_time")
    u_max = num("u_vent_max")
    E_s = num("db_stored_energy")
    V_oc = num("db_ocv")
    R_min = num("R_dc", "range_lo")
    E_fix = num("db_Eej_median")

    rt = raytrace(Rc, Lc)
    with open(os.path.join(ROOT, "results", "stage14_raytrace.json"), "w") as fh:
        json.dump(rt, fh, indent=1)

    F_end = rt["facing_view"]["beyond_L"]
    F_trig = rt["facing_view"]["trigger"]
    w_sup = rt["w_sup"]

    # A1
    U1E = 1.0 * 1.0 * w_sup * E_avail
    P1R = 1.0 * sigma * Tf ** 4 * A_f * F_end
    A1 = {tau: min(U1E, P1R * tau) for tau in WINDOWS}
    A1["total"] = min(U1E, P1R * t_max)
    A1_both = {tau: min(U1E, 2.0 * P1R * tau) for tau in WINDOWS}
    A1_both["total"] = min(U1E, 2.0 * P1R * t_max)
    cond_axis = rt["w_max_axis"]["w"] * E_avail
    cond_column = rt["w_max_column"]["w"] * E_avail

    # A2
    Tfilm = 0.5 * (Tf + T0)
    f = (Tfilm - 1000.0) / 100.0
    air = {q: num(f"air_1000K_{q}") + f * (num(f"air_1100K_{q}") - num(f"air_1000K_{q}")) for q in ("nu", "k", "Pr")}
    h2 = {q: num(f"h2_1000K_{q}") for q in ("nu", "k", "Pr")}
    conv = {}
    for name, p in (("air", air), ("hydrogen", h2)):
        Re = u_max * D / p["nu"]
        Nu, how = churchill_bernstein(Re, p["Pr"])
        conv[name] = dict(Re=Re, Pr=p["Pr"], k=p["k"], nu=p["nu"], Nu=Nu, h=Nu * p["k"] / D, **how)
    h_max = max(c["h"] for c in conv.values())
    q_conv = h_max * (Tf - T0)
    q_rad = sigma * Tf ** 4 * (1.0 - F_trig)
    P2R = (q_conv + q_rad) * A_f
    U2E = E_avail
    A2 = {tau: min(U2E, P2R * tau) for tau in WINDOWS}
    A2["total"] = min(U2E, P2R * t_max)

    # A3
    s_face = max(r["s_max"] for r in rt["breach"])
    U3_face = s_face * E_avail
    A3 = {tau: U3_face for tau in WINDOWS}
    A3["total"] = U3_face
    A3_phi = [dict(phi_deg=r["phi_deg"], s_max=r["s_max"], beta_at_max=r["beta_at_max"], U_J=r["s_max"] * E_avail) for r in rt["breach"]]

    # A4
    A4 = {tau: E_avail for tau in WINDOWS}
    A4["total"] = E_avail

    # A6
    P6R = V_oc ** 2 / R_min
    A6 = {tau: E_s for tau in WINDOWS}
    A6["total"] = E_s
    A6_cond25 = {tau: min(E_s, P6R * tau) for tau in WINDOWS}

    paths = [
        ("A1", "radiation from the jet or flame of a cap-end vent", "the ejecta (gas and flame beyond the end plane)", True, A1,
         (t_min, t_max), "near the venting end of the facing half; C1 and the long deliveries",
         f"min(energy {U1E:.1f} J, rate {P1R:.2f} W x t); w_sup {w_sup:.4f}, F_end {F_end:.5f}"),
        ("A2", "heat from vented gas that passes the neighbour", "the ejecta (gas beside the neighbour)", True, A2,
         (t_min, t_max), "anywhere on the facing half; C2 for the whole half, C1 for the wedges",
         f"min(energy {U2E:.1f} J, rate {P2R:.2f} W x t); h_max {h_max:.1f} W/(m2 K), F_trig {F_trig:.5f}"),
        ("A3", "the jet of a sidewall breach facing the neighbour", "the ejecta (through a breach)", True, A3,
         (t_breach_min, t_max), "a patch around the point struck; C1",
         f"s_max {s_face:.4f} x E_avail; narrow jets strike for |phi| < 30 degrees"),
        ("A4", "solids and melt on or against the facing half", "the ejecta (solids and melt)", True, A4,
         (t_min, t_max), "patches; C1", "share at most 1 x E_avail; no rate term"),
        ("A5", "conduction through the holder and fixtures", "the holder", False, None,
         (None, None), "the neighbour's ends", f"not determinable; energy conservation alone caps it at {E_global:.1f} J"),
        ("A6", "the neighbour's own discharge into the shorted trigger (parallel tests)", "the neighbour's stored charge", True, A6,
         (None, None), "in the roll, by volume; Stage 8 Part B",
         f"stored energy; at 25 C the rate term V^2/R = {P6R:.1f} W gives {A6_cond25[21.39]:.1f} J within 21.39 s (conditional)"),
    ]
    narrow = {
        "A1": "the flame's position and extent beside the cells during venting, its temperature or a radiometer at the facing half's place, and the radiant fraction of such flames",
        "A2": "the gas's temperature and velocity in the wedges beside the line of contact during venting, or the share of the vent gas that passes",
        "A3": "where breaches face, how much of the ejecta leaves through them, and the jet's velocity and opening",
        "A4": "the mass and temperature of the debris and melt found on the facing half after a test, or a heat-flux gauge there",
        "A5": "the inserts' material and contact, or a thermocouple on the holder at the neighbour's ends",
        "A6": "the current between the cells in a parallel test, and the neighbour's resistance at its temperature",
    }
    out_rows = []
    for key, name, carrier, det, U, (tlo, thi), where, note in paths:
        for tau in list(WINDOWS) + ["total"]:
            out_rows.append(dict(path=key, path_name=name, carrier=carrier, determinable="yes" if det else "no",
                                 window_s=tau, lower_J=0.0 if det else "", upper_J=(round(U[tau], 3) if det else ""),
                                 time_lo_s=("" if tlo is None else tlo), time_hi_s=("" if thi is None else thi),
                                 where_and_reading=where, note=note, to_narrow_it=narrow[key]))
    with open(os.path.join(ROOT, "results", "stage14_bounds.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)

    res = dict(
        inputs=dict(R_m=Rc, L_m=Lc, A_f_m2=A_f, E_ej_max_J=E_ej_max, Q_air_max_J=Q_air_max, E_avail_J=E_avail,
                    E_global_J=E_global, E_fix_J=E_fix, sigma=sigma, T_flame_K=Tf, T0_K=T0, t_min_s=t_min, t_max_s=t_max,
                    u_max_m_s=u_max, E_stored_J=E_s, V_oc_V=V_oc, R_dc_min_ohm=R_min),
        A1=dict(w_sup=w_sup, w_max_axis=rt["w_max_axis"], w_max_column=rt["w_max_column"], w_max_edge=rt["w_max_edge"],
                F_end=F_end, energy_term_J=U1E, rate_term_W=P1R, both_ends_rate_W=2 * P1R,
                bounds_J={str(k): x for k, x in A1.items()}, both_ends_J={str(k): x for k, x in A1_both.items()},
                shortest_arrival_s=U1E / P1R, conditional_axis_J=cond_axis, conditional_column_J=cond_column,
                conditional_axis_fraction_of_Efix=cond_axis / E_fix, conditional_column_fraction_of_Efix=cond_column / E_fix),
        A2=dict(T_film_K=Tfilm, convection=conv, h_max=h_max, q_conv_W_m2=q_conv, q_rad_W_m2=q_rad, F_trig=F_trig,
                energy_term_J=U2E, rate_term_W=P2R, bounds_J={str(k): x for k, x in A2.items()}, shortest_arrival_s=U2E / P2R),
        A3=dict(s_face=s_face, U_face_J=U3_face, per_phi=A3_phi, bounds_J={str(k): x for k, x in A3.items()},
                narrow_strike_phi_max_deg=rt["breach_narrow_strike_phi_max_deg"],
                narrow_share_of_circumference=rt["breach_narrow_share_of_circumference_analytic"]),
        A4=dict(bounds_J={str(k): x for k, x in A4.items()}, melt_share_of_circumference=0.5),
        A5=dict(determinable=False, cap_J=E_global),
        A6=dict(bounds_J={str(k): x for k, x in A6.items()}, rate_25C_W=P6R, conditional_25C_J={str(k): x for k, x in A6_cond25.items()},
                stage8_bracket_J=[0.05 * E_s, 0.2 * E_s]),
    )
    with open(os.path.join(ROOT, "results", "stage14_bounds.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps({k: (v_["bounds_J"] if isinstance(v_, dict) and "bounds_J" in v_ else v_) for k, v_ in res.items() if k != "inputs"}, indent=1, default=str)[:3000])


if __name__ == "__main__":
    main()
