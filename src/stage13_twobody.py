"""Stage 13, Part B2: the two-body model of the whole-cell threshold (DECISIONS.md D133).

Two temperatures joined by the link, each with its losses, the trigger's release and the delivery as the archive
defines them, and no integration of the kinetics:
  - the trigger T1(t) is the archive's: the two-cell pair of v12_model.lumped_pair (the trigger releasing E_b over a
    triangular pulse of 21.39 s, the neighbour inert and undelivered, the link and the radiation between them, each
    with its room losses), tabulated every 0.1 s and interpolated as every archived run reads it (stage5_t1). As in
    every archived run the delivered neighbour does not act back on the trigger;
  - the neighbour T2(t) is the lumped neighbour of stage9_model.run_lumped with the reaction switched off:
        C dT2/dt = G (T1 - T2) + eps^2 sigma F A_lat (T1^4 - Ta^4) - h A_conv (T2 - Ta) - eps sigma A_cell (T2^4 - Ta^4)
                   + P(t)
    with P(t) the delivery (triangular from t = 0 over tau_d with peak 2E/tau_d, or constant E/tau_d);
  - along this inert path the first cathode reaction's remaining fraction c(t) is the closed form of its own rate
    law, dc/dt = -k(T2) c^n, c(0) = 1:  c = (1 + (n - 1) I)^(-1/(n-1)),  I(t) = int_0^t k(T2) ds.

The crossing rule, fixed before the predictions (D133 (3)). Write Q(T, c) for the cell's reaction heat with the
separator's melting complete and every other reactant fresh (B1), L(T, T1) for the neighbour's loss (B1), and
M = Q - L. The neighbour is at or above its ignition temperature when M >= 0 and dM/dT > 0 (it is past the balance
point where the reaction heat overtakes the loss, with the trigger at its temperature of the moment). At such a time
the first cathode reaction's heat still left is Q_left = M_cell h_cat1 c, and the heat needed to carry the neighbour
to the level T_L against its losses is
        need = C (T_L - T2) + C Q / (dQ/dT)
the sensible heat to the level plus the loss during one adiabatic induction time at the balance point (the loss there
equals Q, and the induction time is C / (dQ/dT), so the product is C Q/(dQ/dT) = C R T^2 / E_eff). The neighbour
crosses if Q_left >= need at some such time, or if the inert path itself reaches T_L. The threshold E* is the least
delivered energy for which it crosses.

Two implementations (V1): `trajectory_rk4` (classical Runge-Kutta, 16 steps per 0.1 s) and `trajectory_dp5` (the
fifth-order Dormand-Prince weights, 10 steps per 0.1 s, written separately with its own interpolation and search).
Both locate the largest margin with the cubic Hermite interpolant of each step.
"""
import math
import os
import sys

import numba as nb
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bcrnn                               # noqa: E402  (unchanged)
import v12_model as V                      # noqa: E402  (unchanged)
import stage13_inputs as IN                # noqa: E402
import stage13_tign as B1                  # noqa: E402

LP = V.LP
RG = bcrnn.R_GAS
DT_TAB = 0.1


# ------------------------------------------------------------------------------------------------ inputs of one case
_HIST = {}


def trigger(test, h="central", g="central", dE_body=0.0, h_c=None):
    """The archive's trigger history for a test (stage5_t1), cached; h_c (W/(m2 K)) overrides the contact level."""
    t = IN.tests()[test]
    hc = V.H_CONTACT[h] if h_c is None else float(h_c)
    key = (test, hc, g, float(dE_body))
    if key not in _HIST:
        f, data, T1max, tmax = V.stage5_t1(t["connection"], hc, V.G_TAB[g], IN.TAU_TRIGGER,
                                           float(t["E_b_J"]) + dE_body, IN.T_AMB)
        tt = data[:, 0]
        assert np.allclose(tt, np.arange(len(tt)) * DT_TAB, atol=1e-9)
        _HIST[key] = {"T1_K": data[:, 1] + 273.15, "T1max_C": T1max, "t_T1max_s": tmax, "f": f}
    return _HIST[key]


def kinetic_arrays(kin=None):
    """The rate law's constants for the reactions active in the molten fresh state (B1): ln A, b, E_a, the heat per
    unit rate for the 65 g cell (M h, J), the fixed reactants' log-concentration term, the order in cat1."""
    kin = bcrnn.Kinetics() if kin is None else kin
    c = B1.state_molten(1.0)
    lnA, b, Ea, hM, fixed, ncat, act = [], [], [], [], [], [], []
    for j in range(bcrnn.NR):
        reac = kin.reactants[j]
        ok = all(c[s] > 0 for s in reac if s != B1.I_CAT1)
        lnA.append(float(kin.lnA[j])); b.append(float(kin.b[j])); Ea.append(float(kin.Ea[j]))
        hM.append(float(LP.M_CELL * kin.h_mass[j]))
        fixed.append(float(sum(kin.order[s, j] * math.log(c[s]) for s in reac if s != B1.I_CAT1 and c[s] > 0)))
        ncat.append(float(kin.order[B1.I_CAT1, j]))
        act.append(1.0 if ok else 0.0)
    j = B1.J_CAT1
    return {"lnA": np.array(lnA), "b": np.array(b), "Ea": np.array(Ea), "hM": np.array(hM),
            "fixed": np.array(fixed), "ncat": np.array(ncat), "act": np.array(act),
            "cat": np.array([kin.lnA[j], kin.b[j], kin.Ea[j], kin.order[B1.I_CAT1, j], LP.M_CELL * kin.h_mass[j]])}


def params(test, h="central", g="central", dE_body=0.0, C=None, t_level=None, dT_ign=0.0, h_c=None, dT_kin=0.0):
    t = IN.tests()[test]
    gp, gn = V.tabs(t["connection"], V.G_TAB[g])
    G = V.g_contact(V.H_CONTACT[h] if h_c is None else float(h_c)) + gp + gn
    C = LP.C_CELL if C is None else C
    return np.array([C, G, LP.H_CONV * LP.A_CONV, IN.T_AMB, LP.EPS * LP.SIGMA * LP.A_CELL,
                     LP.EPS ** 2 * LP.SIGMA * V.F_TOUCH * LP.A_LAT, IN.T_LEVEL if t_level is None else t_level,
                     900.0, dT_ign, dT_kin])


# ------------------------------------------------------------------------------------------------ implementation 1
_GLX = np.array([-0.8611363115940526, -0.3399810435848563, 0.3399810435848563, 0.8611363115940526])
_GLW = np.array([0.3478548451374538, 0.6521451548625461, 0.6521451548625461, 0.3478548451374538])


@nb.njit(cache=True)
def _t1a(t, tab):
    x = t / 0.1
    i = int(math.floor(x + 1e-12))
    if i >= tab.size - 1:
        return tab[tab.size - 1]
    if i < 0:
        return tab[0]
    w = x - i
    return tab[i] + (tab[i + 1] - tab[i]) * w


@nb.njit(cache=True)
def _pa(t, E, tau, shape):
    if t <= 0.0 or t >= tau or E == 0.0:
        return 0.0
    if shape == 1:
        return E / tau
    pk = 2.0 * E / tau
    if t <= 0.5 * tau:
        return pk * t / (0.5 * tau)
    return pk * (tau - t) / (0.5 * tau)


@nb.njit(cache=True)
def _qa(T, c, kA, kb, kE, khM, kfix, kn, kact, jcat):
    """Reaction heat (W), its temperature derivative and the first cathode reaction's part, at T with cat1 at c."""
    q = 0.0
    dq = 0.0
    qc = 0.0
    for j in range(kA.size):
        if kact[j] == 0.0:
            continue
        lr = kA[j] + kb[j] * math.log(T) - kE[j] / (8.314462618 * T) + kfix[j]
        if kn[j] != 0.0:
            if c <= 0.0:
                continue
            lr += kn[j] * math.log(c)
        r = khM[j] * math.exp(min(lr, 700.0))
        q += r
        dq += r * (kb[j] / T + kE[j] / (8.314462618 * T * T))
        if j == jcat:
            qc = r
    return q, dq, qc


@nb.njit(cache=True)
def _fa(t, Ti, I, th, P, tab, E, tau, shape, cat, kA, kb, kE, khM, kfix, kn, kact, jcat):
    """The inert neighbour, the cathode reaction's integral along it, and the first-order self-heating."""
    C, G, hA, Ta, wr, gi = P[0], P[1], P[2], P[3], P[4], P[5]
    T1 = _t1a(t, tab)
    dT = (G * (T1 - Ti) + gi * (T1 ** 4 - Ta ** 4) - hA * (Ti - Ta) - wr * (Ti ** 4 - Ta ** 4)
          + _pa(t, E, tau, shape)) / C
    Tk = Ti - P[9]                     # the rate law shifted in temperature (C2), zero otherwise
    dI = math.exp(cat[0] + cat[1] * math.log(Tk) - cat[2] / (8.314462618 * Tk))
    n = cat[3]
    c = (1.0 + (n - 1.0) * I) ** (-1.0 / (n - 1.0))
    q = _qa(Tk, c, kA, kb, kE, khM, kfix, kn, kact, jcat)[0]
    dth = (q - (G + hA + 4.0 * wr * Ti ** 3) * th) / C
    return dT, dI, dth


@nb.njit(cache=True)
def _marga(t, Ti, I, th, P, tab, cat, kA, kb, kE, khM, kfix, kn, kact, jcat):
    """(admissible, margin g, M, dM/dT) at one point, with the first-order temperature Tc = Ti + th."""
    C, G, hA, Ta, wr, gi, TL, dTi = P[0], P[1], P[2], P[3], P[4], P[5], P[6], P[8]
    n = cat[3]
    c = (1.0 + (n - 1.0) * I) ** (-1.0 / (n - 1.0))
    Tc = Ti + th
    Te = Tc - dTi
    T1 = _t1a(t, tab)
    q, dq, qc = _qa(Te - P[9], c, kA, kb, kE, khM, kfix, kn, kact, jcat)
    L = G * (Te - T1) + hA * (Te - Ta) + wr * (Te ** 4 - Ta ** 4) - gi * (T1 ** 4 - Ta ** 4)
    dL = G + hA + 4.0 * wr * Te ** 3
    M = q - L
    dM = dq - dL
    if not (M >= 0.0 and dM > 0.0):
        return False, -1e300, M, dM
    # the cathode reaction's share of the climb to T_L: the mean share over [Tc, T_L] for the sensible heat, the
    # share at Tc for the loss during the induction time
    sbar = 0.0
    if TL > Tc:
        for k in range(4):
            Tk = 0.5 * (TL + Tc) + 0.5 * (TL - Tc) * _GLX[k]
            qk, dqk, qck = _qa(Tk - P[9], c, kA, kb, kE, khM, kfix, kn, kact, jcat)
            sbar += 0.5 * _GLW[k] * qck / qk
    q0, dq0, qc0 = _qa(Tc - P[9], c, kA, kb, kE, khM, kfix, kn, kact, jcat)
    need = sbar * C * max(TL - Tc, 0.0) + (qc0 / q0) * C * q0 / dq0
    return True, cat[4] * c - need, M, dM


@nb.njit(cache=True)
def _herm(s, h, y0, y1, d0, d1):
    s2 = s * s
    s3 = s2 * s
    return ((2 * s3 - 3 * s2 + 1) * y0 + (s3 - 2 * s2 + s) * h * d0 + (-2 * s3 + 3 * s2) * y1
            + (s3 - s2) * h * d1)


@nb.njit(cache=True)
def _ev(s, ta, h, st, P, tab, cat, kA, kb, kE, khM, kfix, kn, kact, jcat):
    """_marga on the step's interpolant at fraction s; st holds (T, Tn, dT0, dT1, I, In, dI0, dI1, th, thn, dth0,
    dth1)."""
    Ti = _herm(s, h, st[0], st[1], st[2], st[3])
    I = _herm(s, h, st[4], st[5], st[6], st[7])
    th = _herm(s, h, st[8], st[9], st[10], st[11])
    return _marga(ta + s * h, Ti, I, th, P, tab, cat, kA, kb, kE, khM, kfix, kn, kact, jcat)


@nb.njit(cache=True)
def _scan_a(ta, h, st, P, tab, cat, kA, kb, kE, khM, kfix, kn, kact, jcat, running, full):
    """The largest margin on one step (ends, the largest M, the admissible set's edges, the largest g inside it).
    Returns (g, s_best, s_first) with g = -1e300 when no point of the step is admissible."""
    a0, g0, M0, d0 = _ev(0.0, ta, h, st, P, tab, cat, kA, kb, kE, khM, kfix, kn, kact, jcat)
    a1, g1, M1, d1 = _ev(1.0, ta, h, st, P, tab, cat, kA, kb, kE, khM, kfix, kn, kact, jcat)
    if not (a0 or a1 or max(M0, M1) > -0.5):
        return -1e300, -1.0, -1.0
    if a0 and a1 and not full and not (g1 < g0 and g0 >= running - 1e-9):
        if g1 >= g0:
            return g1, 1.0, 0.0
        return g0, 0.0, 0.0
    gr = 0.6180339887498949
    lo, hi = 0.0, 1.0
    x1, x2 = hi - gr * (hi - lo), lo + gr * (hi - lo)
    m1 = _ev(x1, ta, h, st, P, tab, cat, kA, kb, kE, khM, kfix, kn, kact, jcat)[2]
    m2 = _ev(x2, ta, h, st, P, tab, cat, kA, kb, kE, khM, kfix, kn, kact, jcat)[2]
    for _ in range(70):
        if m1 > m2:
            hi, x2, m2 = x2, x1, m1
            x1 = hi - gr * (hi - lo)
            m1 = _ev(x1, ta, h, st, P, tab, cat, kA, kb, kE, khM, kfix, kn, kact, jcat)[2]
        else:
            lo, x1, m1 = x1, x2, m2
            x2 = lo + gr * (hi - lo)
            m2 = _ev(x2, ta, h, st, P, tab, cat, kA, kb, kE, khM, kfix, kn, kact, jcat)[2]
    sm = 0.5 * (lo + hi)
    am = _ev(sm, ta, h, st, P, tab, cat, kA, kb, kE, khM, kfix, kn, kact, jcat)[0]
    pts = np.array([0.0, sm, 1.0])
    adm = np.array([a0, am, a1])
    cand = np.empty(8)
    nc = 0
    for q in range(3):
        if adm[q]:
            cand[nc] = pts[q]
            nc += 1
    for q in range(2):
        if adm[q] != adm[q + 1]:
            lo, hi = pts[q], pts[q + 1]
            for _ in range(90):
                mid = 0.5 * (lo + hi)
                if _ev(mid, ta, h, st, P, tab, cat, kA, kb, kE, khM, kfix, kn, kact, jcat)[0] == adm[q]:
                    lo = mid
                else:
                    hi = mid
            cand[nc] = lo if adm[q] else hi
            nc += 1
    if nc == 0:
        return -1e300, -1.0, -1.0
    slo, shi = 2.0, -1.0
    for q in range(nc):
        slo = min(slo, cand[q])
        shi = max(shi, cand[q])
    lo, hi = slo, shi
    if hi - lo > 1e-12:
        x1, x2 = hi - gr * (hi - lo), lo + gr * (hi - lo)
        r1 = _ev(x1, ta, h, st, P, tab, cat, kA, kb, kE, khM, kfix, kn, kact, jcat)
        r2 = _ev(x2, ta, h, st, P, tab, cat, kA, kb, kE, khM, kfix, kn, kact, jcat)
        v1 = r1[1] if r1[0] else -1e300
        v2 = r2[1] if r2[0] else -1e300
        for _ in range(70):
            if v1 > v2:
                hi, x2, v2 = x2, x1, v1
                x1 = hi - gr * (hi - lo)
                r1 = _ev(x1, ta, h, st, P, tab, cat, kA, kb, kE, khM, kfix, kn, kact, jcat)
                v1 = r1[1] if r1[0] else -1e300
            else:
                lo, x1, v1 = x1, x2, v2
                x2 = lo + gr * (hi - lo)
                r2 = _ev(x2, ta, h, st, P, tab, cat, kA, kb, kE, khM, kfix, kn, kact, jcat)
                v2 = r2[1] if r2[0] else -1e300
        cand[nc] = 0.5 * (lo + hi)
        nc += 1
    best, sb, sfirst = -1e300, -1.0, 2.0
    for q in range(nc):
        r = _ev(cand[q], ta, h, st, P, tab, cat, kA, kb, kE, khM, kfix, kn, kact, jcat)
        if r[0]:
            sfirst = min(sfirst, cand[q])
            if r[1] > best:
                best, sb = r[1], cand[q]
    if sb < 0.0:
        return -1e300, -1.0, -1.0
    return best, sb, sfirst


@nb.njit(cache=True)
def trajectory_rk4(P, tab, E, tau, shape, cat, kA, kb, kE, khM, kfix, kn, kact, jcat, nsub, out_T, out_th):
    """Integrate the inert neighbour, the cathode integral and the self-heating; return (g_max, t_g, Tc_max,
    t_Tc_max, t_first_admissible, c_at_g, Tc_at_g, th_at_g, Ti_max). out_T and out_th receive Ti and th every 0.1 s."""
    T = P[3]
    I = 0.0
    th = 0.0
    n = cat[3]
    TL = P[6]
    gmax, tg, cg, Tg, thg = -1e300, -1.0, -1.0, -1.0, 0.0
    Tcmax, tTc, Timax, tfirst = T, 0.0, T, -1.0
    nint = int(round(P[7] / 0.1))
    out_T[0] = T
    out_th[0] = 0.0
    st = np.zeros(12)
    pst = np.zeros(12)
    pta, ph = 0.0, 0.0
    have_prev = False
    pg = -1e300
    for k in range(nint):
        t0 = k * 0.1
        t1 = t0 + 0.1
        pts = np.empty(nsub + 3)
        npt = 0
        for m in range(nsub + 1):
            pts[npt] = t0 + 0.1 * m / nsub
            npt += 1
        for kk in (0.5 * tau, tau):
            if kk > t0 + 1e-12 and kk < t1 - 1e-12:
                pts[npt] = kk
                npt += 1
        pp = np.sort(pts[:npt])
        for m in range(npt - 1):
            ta, tb = pp[m], pp[m + 1]
            h = tb - ta
            if h <= 1e-14:
                continue
            a1, b1, c1 = _fa(ta, T, I, th, P, tab, E, tau, shape, cat, kA, kb, kE, khM, kfix, kn, kact, jcat)
            a2, b2, c2 = _fa(ta + 0.5 * h, T + 0.5 * h * a1, I + 0.5 * h * b1, th + 0.5 * h * c1, P, tab, E, tau,
                             shape, cat, kA, kb, kE, khM, kfix, kn, kact, jcat)
            a3, b3, c3 = _fa(ta + 0.5 * h, T + 0.5 * h * a2, I + 0.5 * h * b2, th + 0.5 * h * c2, P, tab, E, tau,
                             shape, cat, kA, kb, kE, khM, kfix, kn, kact, jcat)
            a4, b4, c4 = _fa(tb, T + h * a3, I + h * b3, th + h * c3, P, tab, E, tau, shape, cat, kA, kb, kE, khM,
                             kfix, kn, kact, jcat)
            Tn = T + h * (a1 + 2 * a2 + 2 * a3 + a4) / 6.0
            In = I + h * (b1 + 2 * b2 + 2 * b3 + b4) / 6.0
            thn = th + h * (c1 + 2 * c2 + 2 * c3 + c4) / 6.0
            e1, f1, g1_ = _fa(tb, Tn, In, thn, P, tab, E, tau, shape, cat, kA, kb, kE, khM, kfix, kn, kact, jcat)
            st[0], st[1], st[2], st[3] = T, Tn, a1, e1
            st[4], st[5], st[6], st[7] = I, In, b1, f1
            st[8], st[9], st[10], st[11] = th, thn, c1, g1_
            # the largest first-order temperature, refined on the interpolant
            d0 = a1 + c1
            d1 = e1 + g1_
            if d0 > 0.0 and d1 <= 0.0:
                lo, hi = 0.0, 1.0
                for _ in range(80):
                    s = 0.5 * (lo + hi)
                    dd = ((6 * s * s - 6 * s) * (T + th) + (3 * s * s - 4 * s + 1) * h * d0
                          + (-6 * s * s + 6 * s) * (Tn + thn) + (3 * s * s - 2 * s) * h * d1)
                    if dd > 0:
                        lo = s
                    else:
                        hi = s
                s = 0.5 * (lo + hi)
                v = _herm(s, h, T + th, Tn + thn, d0, d1)
                if v > Tcmax:
                    Tcmax, tTc = v, ta + s * h
            if Tn + thn > Tcmax:
                Tcmax, tTc = Tn + thn, tb
            if Tn > Timax:
                Timax = Tn
            gs, sb, sf = _scan_a(ta, h, st, P, tab, cat, kA, kb, kE, khM, kfix, kn, kact, jcat, gmax, False)
            if sf >= 0.0 and tfirst < 0.0:
                tfirst = ta + sf * h
            if gs > gmax:
                gmax, tg = gs, ta + sb * h
                Ib = _herm(sb, h, st[4], st[5], st[6], st[7])
                thg = _herm(sb, h, st[8], st[9], st[10], st[11])
                Tg = _herm(sb, h, st[0], st[1], st[2], st[3]) + thg
                cg = (1.0 + (n - 1.0) * Ib) ** (-1.0 / (n - 1.0))
            if have_prev and gs < gmax and gs > -1e299 and pg >= gmax - 1e-9:
                gq, sq, sfq = _scan_a(pta, ph, pst, P, tab, cat, kA, kb, kE, khM, kfix, kn, kact, jcat, 1e300, True)
                if gq > gmax:
                    gmax, tg = gq, pta + sq * ph
                    Ib = _herm(sq, ph, pst[4], pst[5], pst[6], pst[7])
                    thg = _herm(sq, ph, pst[8], pst[9], pst[10], pst[11])
                    Tg = _herm(sq, ph, pst[0], pst[1], pst[2], pst[3]) + thg
                    cg = (1.0 + (n - 1.0) * Ib) ** (-1.0 / (n - 1.0))
            pst[:] = st
            pta, ph = ta, h
            have_prev = True
            pg = gs
            T, I, th = Tn, In, thn
        out_T[k + 1] = T
        out_th[k + 1] = th
    return gmax, tg, Tcmax, tTc, tfirst, cg, Tg, thg, Timax


# ------------------------------------------------------------------------------------------------ implementation 2
# Dormand-Prince fifth-order weights (the 5th-order solution of DOPRI5), written out separately.
_DP_C = np.array([0.0, 1 / 5, 3 / 10, 4 / 5, 8 / 9, 1.0])
_DP_A = np.array([[0, 0, 0, 0, 0], [1 / 5, 0, 0, 0, 0], [3 / 40, 9 / 40, 0, 0, 0], [44 / 45, -56 / 15, 32 / 9, 0, 0],
                  [19372 / 6561, -25360 / 2187, 64448 / 6561, -212 / 729, 0],
                  [9017 / 3168, -355 / 33, 46732 / 5247, 49 / 176, -5103 / 18656]])
_DP_B = np.array([35 / 384, 0.0, 500 / 1113, 125 / 192, -2187 / 6784, 11 / 84])
_GL = np.array([[0.8611363115940526, 0.3478548451374538], [0.3399810435848563, 0.6521451548625461]])


@nb.njit(cache=True)
def _t1b(t, tab):
    i = int(t * 10.0 + 1e-9)
    if i < 0:
        i = 0
    if i > tab.size - 2:
        return tab[tab.size - 1]
    frac = (t - 0.1 * i) / 0.1
    return (1.0 - frac) * tab[i] + frac * tab[i + 1]


@nb.njit(cache=True)
def _pb(t, E, tau, shape):
    if E == 0.0 or not (0.0 < t < tau):
        return 0.0
    if shape == 1:
        return E / tau
    return 4.0 * E / tau ** 2 * min(t, tau - t)


@nb.njit(cache=True)
def _heat_b(T, c, K):
    """K rows: lnA, b, Ea, M h, fixed term, order in cat1, active, is-cat1. Returns (Q, dQ/dT, Q_cat1)."""
    lnT = math.log(T)
    inv = 1.0 / (8.314462618 * T)
    out = np.zeros(3)
    for j in range(K.shape[1]):
        if K[6, j] < 0.5:
            continue
        if K[5, j] != 0.0 and c <= 0.0:
            continue
        e = K[0, j] + K[1, j] * lnT - K[2, j] * inv + K[4, j]
        if K[5, j] != 0.0:
            e += K[5, j] * math.log(c)
        r = K[3, j] * math.exp(e if e < 700.0 else 700.0)
        out[0] += r
        out[1] += r * (K[1, j] + K[2, j] * inv) / T
        if K[7, j] > 0.5:
            out[2] += r
    return out


@nb.njit(cache=True)
def _fb(t, y, P, tab, E, tau, shape, cat, K):
    Ti = y[0]
    T1 = _t1b(t, tab)
    Ta = P[3]
    net = (P[1] * (T1 - Ti) + P[5] * (T1 * T1 * T1 * T1 - Ta * Ta * Ta * Ta) - P[2] * (Ti - Ta)
           - P[4] * (Ti * Ti * Ti * Ti - Ta * Ta * Ta * Ta) + _pb(t, E, tau, shape))
    c = math.exp(-math.log(1.0 + (cat[3] - 1.0) * y[1]) / (cat[3] - 1.0))
    out = np.empty(3)
    out[0] = net / P[0]
    Tk = Ti - P[9]
    out[1] = math.exp(cat[0] + cat[1] * math.log(Tk) - cat[2] / (8.314462618 * Tk))
    out[2] = (_heat_b(Tk, c, K)[0] - (P[1] + P[2] + 4.0 * P[4] * Ti * Ti * Ti) * y[2]) / P[0]
    return out


@nb.njit(cache=True)
def _mb(t, y, P, tab, cat, K):
    """(admissible, g, c, M) at a point y = (Ti, I, th)."""
    c = math.exp(-math.log(1.0 + (cat[3] - 1.0) * y[1]) / (cat[3] - 1.0))
    Ta = P[3]
    Tc = y[0] + y[2]
    Te = Tc - P[8]
    T1 = _t1b(t, tab)
    hq = _heat_b(Te - P[9], c, K)
    M = hq[0] - (P[1] * (Te - T1) + P[2] * (Te - Ta) + P[4] * (Te ** 4 - Ta ** 4) - P[5] * (T1 ** 4 - Ta ** 4))
    dM = hq[1] - (P[1] + P[2] + 4.0 * P[4] * Te ** 3)
    if M < 0.0 or dM <= 0.0:
        return False, -1e300, c, M
    TL = P[6]
    mean_share = 0.0
    if TL > Tc:
        mid, half = 0.5 * (TL + Tc), 0.5 * (TL - Tc)
        for r in range(2):
            for sgn in (-1.0, 1.0):
                hk = _heat_b(mid + sgn * half * _GL[r, 0] - P[9], c, K)
                mean_share += 0.5 * _GL[r, 1] * hk[2] / hk[0]
    h0 = _heat_b(Tc - P[9], c, K)
    need = mean_share * P[0] * (TL - Tc if TL > Tc else 0.0) + P[0] * h0[2] / h0[1]
    return True, cat[4] * c - need, c, M


@nb.njit(cache=True)
def _hb(s, h, a, b, da, db):
    return (a * (1 + 2 * s) * (1 - s) ** 2 + h * da * s * (1 - s) ** 2 + b * s * s * (3 - 2 * s)
            - h * db * s * s * (1 - s))


@nb.njit(cache=True)
def _yb(s, h, y0, y1, d0, d1):
    out = np.empty(3)
    for i in range(3):
        out[i] = _hb(s, h, y0[i], y1[i], d0[i], d1[i])
    return out


@nb.njit(cache=True)
def _fine_b(ta, h, y0, y1, d0, d1, P, tab, cat, K):
    """Largest admissible margin on one step: 33 grid points, the largest M by ternary search, the edges of the
    admissible set by bisection, then a ternary search near the best point. Returns (g, s, s_first)."""
    best, sb, sfirst = -1e300, -1.0, 2.0
    prev = _mb(ta, y0, P, tab, cat, K)[0]
    for q in range(33):
        s = q / 32
        r = _mb(ta + s * h, _yb(s, h, y0, y1, d0, d1), P, tab, cat, K)
        if r[0] != prev and q > 0:
            a, b = (q - 1) / 32, s
            for _ in range(100):
                mm = 0.5 * (a + b)
                if _mb(ta + mm * h, _yb(mm, h, y0, y1, d0, d1), P, tab, cat, K)[0] == prev:
                    a = mm
                else:
                    b = mm
            se = b if not prev else a
            re = _mb(ta + se * h, _yb(se, h, y0, y1, d0, d1), P, tab, cat, K)
            if re[0]:
                sfirst = min(sfirst, se)
                if re[1] > best:
                    best, sb = re[1], se
        prev = r[0]
        if r[0]:
            sfirst = min(sfirst, s)
            if r[1] > best:
                best, sb = r[1], s
    a, b = 0.0, 1.0
    for _ in range(120):
        m1 = a + (b - a) / 3
        m2 = b - (b - a) / 3
        if _mb(ta + m1 * h, _yb(m1, h, y0, y1, d0, d1), P, tab, cat, K)[3] < \
                _mb(ta + m2 * h, _yb(m2, h, y0, y1, d0, d1), P, tab, cat, K)[3]:
            a = m1
        else:
            b = m2
    smx = 0.5 * (a + b)
    r = _mb(ta + smx * h, _yb(smx, h, y0, y1, d0, d1), P, tab, cat, K)
    if r[0]:
        sfirst = min(sfirst, smx)
        if r[1] > best:
            best, sb = r[1], smx
    if sb < 0.0:
        return best, -1.0, -1.0
    a = max(0.0, sb - 1.0 / 32)
    b = min(1.0, sb + 1.0 / 32)
    for _ in range(120):
        m1 = a + (b - a) / 3
        m2 = b - (b - a) / 3
        r1 = _mb(ta + m1 * h, _yb(m1, h, y0, y1, d0, d1), P, tab, cat, K)
        r2 = _mb(ta + m2 * h, _yb(m2, h, y0, y1, d0, d1), P, tab, cat, K)
        v1 = r1[1] if r1[0] else -1e300
        v2 = r2[1] if r2[0] else -1e300
        if v1 < v2:
            a = m1
        else:
            b = m2
    s = 0.5 * (a + b)
    r = _mb(ta + s * h, _yb(s, h, y0, y1, d0, d1), P, tab, cat, K)
    if r[0] and r[1] > best:
        best, sb = r[1], s
    return best, sb, (sfirst if sfirst <= 1.0 else -1.0)


@nb.njit(cache=True)
def trajectory_dp5(P, tab, E, tau, shape, cat, K, nsub, out_T, out_th, cA, cB, cC):
    y = np.array([P[3], 0.0, 0.0])
    best, tbest, cbest, Tbest, thbest = -1e300, -1.0, -1.0, -1.0, 0.0
    Tcmax, tmax, Timax, tfirst = P[3], 0.0, P[3], -1.0
    Kst = np.empty((6, 3))
    have_prev = False
    pbest_end = -1e300
    py0, py1, pd0, pd1 = np.zeros(3), np.zeros(3), np.zeros(3), np.zeros(3)
    pta, ph = 0.0, 0.0
    nint = int(round(P[7] * 10.0))
    out_T[0] = y[0]
    out_th[0] = 0.0
    for k in range(nint):
        edges = [k * 0.1 + 0.1 * m / nsub for m in range(nsub + 1)]
        for kk in (0.5 * tau, tau):
            if k * 0.1 + 1e-12 < kk < (k + 1) * 0.1 - 1e-12:
                edges.append(kk)
        edges.sort()
        for m in range(len(edges) - 1):
            ta = edges[m]
            h = edges[m + 1] - ta
            if h < 1e-14:
                continue
            for i in range(6):
                yy = y.copy()
                for j in range(i):
                    yy += h * cA[i, j] * Kst[j]
                Kst[i] = _fb(ta + cC[i] * h, yy, P, tab, E, tau, shape, cat, K)
            yn = y.copy()
            for i in range(6):
                yn += h * cB[i] * Kst[i]
            d0 = Kst[0].copy()
            d1 = _fb(ta + h, yn, P, tab, E, tau, shape, cat, K)
            u0, u1 = y[0] + y[2], yn[0] + yn[2]
            e0, e1 = d0[0] + d0[2], d1[0] + d1[2]
            if e0 > 0.0 and e1 <= 0.0:
                a, b = 0.0, 1.0
                for _ in range(100):
                    s = 0.5 * (a + b)
                    ds = (6 * s * s - 6 * s) * (u0 - u1) + h * e0 * (1 - 4 * s + 3 * s * s) + h * e1 * (3 * s * s - 2 * s)
                    if ds > 0:
                        a = s
                    else:
                        b = s
                v = _hb(0.5 * (a + b), h, u0, u1, e0, e1)
                if v > Tcmax:
                    Tcmax, tmax = v, ta + 0.5 * (a + b) * h
            if u1 > Tcmax:
                Tcmax, tmax = u1, ta + h
            if yn[0] > Timax:
                Timax = yn[0]
            r0 = _mb(ta, y, P, tab, cat, K)
            r1 = _mb(ta + h, yn, P, tab, cat, K)
            near = max(r0[3], r1[3]) > -0.5
            inside = r0[0] and r1[0]
            peaked = inside and r1[1] < r0[1] and r0[1] >= best - 1e-9
            gstep = -1e300
            if inside and not peaked:
                gstep = max(r0[1], r1[1])
                if gstep > best:
                    best = gstep
                    sb = 1.0 if r1[1] >= r0[1] else 0.0
                    tbest = ta + sb * h
                    yb_ = yn if sb == 1.0 else y
                    Tbest, thbest = yb_[0] + yb_[2], yb_[2]
                    cbest = r1[2] if sb == 1.0 else r0[2]
                if tfirst < 0.0:
                    tfirst = ta
            elif r0[0] or r1[0] or near:
                gq, sq, sf = _fine_b(ta, h, y, yn, d0, d1, P, tab, cat, K)
                gstep = gq
                if sf >= 0.0 and tfirst < 0.0:
                    tfirst = ta + sf * h
                if gq > best:
                    best, tbest = gq, ta + sq * h
                    yv = _yb(sq, h, y, yn, d0, d1)
                    Tbest, thbest = yv[0] + yv[2], yv[2]
                    cbest = math.exp(-math.log(1.0 + (cat[3] - 1.0) * yv[1]) / (cat[3] - 1.0))
                if peaked and have_prev:
                    gp, sp_, sfp = _fine_b(pta, ph, py0, py1, pd0, pd1, P, tab, cat, K)
                    if gp > best:
                        best, tbest = gp, pta + sp_ * ph
                        yv = _yb(sp_, ph, py0, py1, pd0, pd1)
                        Tbest, thbest = yv[0] + yv[2], yv[2]
                        cbest = math.exp(-math.log(1.0 + (cat[3] - 1.0) * yv[1]) / (cat[3] - 1.0))
            py0[:], py1[:], pd0[:], pd1[:] = y, yn, d0, d1
            pta, ph = ta, h
            have_prev = True
            pbest_end = gstep
            y = yn
        out_T[k + 1] = y[0]
        out_th[k + 1] = y[2]
    return best, tbest, Tcmax, tmax, tfirst, cbest, Tbest, thbest, Timax


# ------------------------------------------------------------------------------------------------ one case, a threshold
class Case:
    """One case of B2: a test, contact and tab levels, the body energy's shift, the delivery's shape and duration."""

    def __init__(self, test, tau_d=None, shape="tri", h="central", g="central", dE_body=0.0, kin=None, C=None,
                 t_level=None, dT_ign=0.0, impl="rk4", h_c=None, dT_kin=0.0):
        self.test, self.h, self.g, self.dE_body = test, h, g, float(dE_body)
        self.tau_d = IN.TAU_TRIGGER if tau_d is None else float(tau_d)
        self.shape = 0 if shape == "tri" else 1
        self.tab = trigger(test, h, g, dE_body, h_c)["T1_K"]
        self.P = params(test, h, g, dE_body, C=C, t_level=t_level, dT_ign=dT_ign, h_c=h_c, dT_kin=dT_kin)
        ka = kinetic_arrays(kin)
        self.k = (ka["cat"], ka["lnA"], ka["b"], ka["Ea"], ka["hM"], ka["fixed"], ka["ncat"], ka["act"])
        iscat = np.zeros(len(ka["lnA"]))
        iscat[B1.J_CAT1] = 1.0
        self.K = np.vstack([ka["lnA"], ka["b"], ka["Ea"], ka["hM"], ka["fixed"], ka["ncat"], ka["act"], iscat])
        self.impl = impl
        self.out = np.zeros(int(round(self.P[7] / DT_TAB)) + 1)
        self.out_th = np.zeros_like(self.out)

    def path(self, E):
        cat, kA, kb, kE, khM, kfix, kn, kact = self.k
        if self.impl == "rk4":
            r = trajectory_rk4(self.P, self.tab, float(E), self.tau_d, self.shape, cat, kA, kb, kE, khM, kfix, kn,
                               kact, B1.J_CAT1, 16, self.out, self.out_th)
        else:
            r = trajectory_dp5(self.P, self.tab, float(E), self.tau_d, self.shape, cat, self.K, 10, self.out,
                               self.out_th, _DP_A, _DP_B, _DP_C)
        gmax, tg, Tcmax, tTc, tfirst, cg, Tg, thg, Timax = r
        return {"E_J": float(E), "g_max_J": gmax, "t_g_s": tg, "Tc_max_C": Tcmax - IN.K0, "t_Tc_max_s": tTc,
                "Ti_max_C": Timax - IN.K0, "t_first_admissible_s": tfirst, "c_cat1_at_g": cg,
                "Tc_at_g_C": Tg - IN.K0 if tg >= 0 else None, "theta_at_g_K": thg,
                "crossed": bool(gmax >= 0.0 or Tcmax >= self.P[6]),
                "by": "reaction" if gmax >= 0.0 else ("first-order path" if Tcmax >= self.P[6] else None)}

    def margin(self, E):
        p = self.path(E)
        return max(p["g_max_J"], self.P[0] * (p["Tc_max_C"] + IN.K0 - self.P[6]))

    def threshold(self, E_hi=None, rtol=1e-13):
        """E* by bisection on the crossing; 0 if the case crosses with no delivery."""
        if self.margin(0.0) >= 0.0:
            return 0.0
        hi = 2.0 * IN.e_e(self.test) if E_hi is None else E_hi
        k = 0
        while self.margin(hi) < 0.0:
            hi *= 2.0
            k += 1
            if k > 20:
                return float("nan")
        lo = 0.0
        while hi - lo > rtol * hi:
            mid = 0.5 * (lo + hi)
            if self.margin(mid) >= 0.0:
                hi = mid
            else:
                lo = mid
        return 0.5 * (lo + hi)


    def summary(self, E_star):
        """What sets the threshold: "reaching T_ign" (just below E* the inert path never reaches the balance point),
        "the heat left" (it reaches it, without enough of the cathode reaction's heat), or "the inert path"."""
        if E_star == 0.0:
            return {"E_star_J": 0.0, "binding": "no delivery needed", "above": self.path(0.0)}
        below = self.path(E_star * (1 - 1e-9))
        above = self.path(E_star * (1 + 1e-9))
        if above["by"] == "first-order path":
            b = "the first-order path reaches T_L"
        elif below["t_first_admissible_s"] >= 0.0:
            b = "the heat left"
        else:
            b = "reaching T_ign"
        return {"E_star_J": E_star, "binding": b, "above": above, "below": below}


def threshold(test, tau_d=None, shape="tri", h="central", g="central", dE_body=0.0, impl="rk4", **kw):
    return Case(test, tau_d, shape, h, g, dE_body, impl=impl, **kw).threshold()


if __name__ == "__main__":
    import time
    t0 = time.time()
    for impl in ("rk4", "dp5"):
        c = Case("M50_PT_Exp1", impl=impl)
        E = c.threshold()
        print(impl, "E* =", E, "f* =", E / IN.e_e("M50_PT_Exp1"), c.path(E), time.time() - t0)
