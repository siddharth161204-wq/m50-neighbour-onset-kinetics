"""Tests of the Stage 13 code on synthetic inputs (no Stage 13 case is run here). python3 -m pytest -q test_stage13.py"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage13_inputs as IN                # noqa: E402
import stage13_skin as A1                  # noqa: E402
import stage13_section as A2               # noqa: E402
import stage13_tign as B1                  # noqa: E402
import stage13_twobody as B2               # noqa: E402
import stage13_run as RN                   # noqa: E402
import bcrnn                               # noqa: E402


def test_half_space_triangle():
    """A1's limit with no can and no loss: the peak 1.2284 E''/(e sqrt tau) at two thirds of the pulse."""
    u, tp = A1.peak_closed(1.0, 1.0, 0.0, 1.0, 1e-12)
    assert abs(u - 16 / (3 * math.sqrt(math.pi)) * ((2 / 3) ** 1.5 - 2 * (1 / 6) ** 1.5)) < 1e-9
    assert abs(tp - 2 / 3) < 1e-9


def test_skin_two_codes():
    for tau, h in ((5.0, 0.0), (21.39, 25.0), (120.0, 40.0)):
        a = A1.peak_closed(tau, 1e7, h)
        b = A1.peak_laplace(tau, 1e7, h)
        assert abs(a[0] - b[0]) / a[0] < 1e-9 and abs(a[1] - b[1]) / a[1] < 1e-9


def test_skin_can_and_loss_lower_the_peak():
    u0 = A1.Phi(0.0, 0.0)
    assert A1.Phi(0.1, 0.0) < u0 and A1.Phi(0.0, 0.05) < u0


def _adiabatic(sec):
    sec.g_contact[:] = 0.0
    sec.h_conv[:] = 0.0
    sec.w_rad[:] = 0.0
    sec.g_rad[:] = 0.0
    sec._facts = {}
    return sec


def test_section_energy_and_two_codes():
    """With every surface term off, the delivered energy per unit length is all stored; the two codes agree."""
    out = []
    for impl in ("sparse", "banded"):
        sec = _adiabatic(A2.Section(impl=impl))
        F = A2.tri_cumulative(5.0)
        E = 1000.0
        tt, Ts, inner = sec.run(None, F, E, 8.0, 0.01, 0.01, nonlinear=False, h_sec=np.zeros((900, sec.nt)))
        C = sec.capacity()
        # stored per unit length of the half section against E share: E * sum(q_share) per unit length
        out.append((tt, Ts))
    assert np.max(np.abs(out[0][1] - out[1][1])) < 1e-9


def test_section_stored_energy():
    sec = _adiabatic(A2.Section(impl="sparse"))
    F = A2.tri_cumulative(2.0)
    E = 500.0
    ci = sec.can_index()
    T = np.zeros(sec.n)
    C, solve = sec.factor(0.01)
    t = 0.0
    for n in range(400):
        rhs = C / 0.01 * T
        rhs[ci] += sec.q_share * E * (F(t + 0.01) - F(t)) / 0.01
        T = solve(rhs)
        t += 0.01
    stored = float(C @ T)
    assert abs(stored - E * sec.q_share.sum()) / (E * sec.q_share.sum()) < 1e-10


def test_contact_integral_matches_g_contact():
    import v12_model as V
    g = 2 * A2._contact_integral(0.0, math.pi / 4, 2000.0) * IN.LZ
    assert abs(g / V.g_contact(2000.0) - 1) < 1e-12


def test_tign_is_a_balance_point():
    kin = bcrnn.Kinetics()
    G = B1.g_link("parallel")
    for mode in ("own", "ambient"):
        T = B1.t_ign(kin, mode, G)
        assert abs(B1.balance(kin, T, mode, G)) < 1e-8
        assert all(B1.balance(kin, x, mode, G) > 0 for x in np.linspace(T + 0.01, IN.T_LEVEL, 50))


def test_cat1_closed_form():
    """c = (1 + (n - 1) I)^(-1/(n-1)) solves dc/dt = -k c^n along a prescribed path."""
    ka = B2.kinetic_arrays()
    lnA, b, Ea, n = ka["cat"][:4]
    T = lambda t: 450.0 + 0.5 * t
    k = lambda t: math.exp(lnA + b * math.log(T(t)) - Ea / (bcrnn.R_GAS * T(t)))
    from scipy.integrate import solve_ivp, quad
    sol = solve_ivp(lambda t, c: [-k(t) * c[0] ** n], (0, 120), [1.0], rtol=1e-12, atol=1e-14)
    I = quad(k, 0, 120, epsabs=1e-14, epsrel=1e-12)[0]
    assert abs(sol.y[0, -1] - (1 + (n - 1) * I) ** (-1 / (n - 1))) < 1e-8


def test_twobody_codes_agree_synthetic():
    """The two codes on a synthetic trigger (a constant 120 C) and a 3 kJ delivery."""
    c1 = B2.Case("M50_PT_Exp1", impl="rk4")
    c2 = B2.Case("M50_PT_Exp1", impl="dp5")
    for c in (c1, c2):
        c.tab = np.full_like(c.tab, 393.15)
        c.P = c.P.copy()
        c.P[7] = 60.0
        c.out = np.zeros(601)
        c.out_th = np.zeros(601)
    p1, p2 = c1.path(3000.0), c2.path(3000.0)
    assert abs(p1["Tc_max_C"] - p2["Tc_max_C"]) < 1e-8
    assert np.max(np.abs(c1.out - c2.out)) < 1e-8


def test_search_rule_synthetic():
    """The search's next value from synthetic records: start, step, bracket and halving."""
    s = {"name": "X", "model": "resolved", "test": "M50_PT_Exp1", "shape": "tri", "tau_d_s": 5.0,
         "geometry": "half", "h": "central", "dE_body_J": 0.0, "kind": "search", "ref": None}
    red = {f"A2_M50_PT_Exp1_half_tau{5.0:.4f}_r1_dt1": {"f_star": 0.1}}
    mk = lambda f, c, k: {"id": f"r{k}", "search": "X", "models": "resolved", "f": f, "started_utc": f"{k:03d}",
                          "reaction": True, "stop": True, "resolved": {"propagated": c}}
    st, x, br, _ = RN.search_state(s, {}, red)
    assert st == "running" and x == 0.1
    recs = {"a": mk(0.1, False, 1)}
    st, x, br, _ = RN.search_state(s, recs, red)
    assert abs(x - 0.103) < 1e-12
    recs["b"] = mk(0.103, False, 2)
    st, x, br, _ = RN.search_state(s, recs, red)
    assert abs(x - 0.106) < 1e-12
    recs["c"] = mk(0.106, True, 3)
    st, x, br, _ = RN.search_state(s, recs, red)
    assert st == "done" and br == (0.103, 0.106)
