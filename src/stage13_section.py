"""Stage 13, Part A2: the cross-section conduction model of the local threshold (DECISIONS.md D131 (2)).

Linear conduction in r and theta at mid-height, with no reaction and no axial direction, in the half cross-section
0 <= theta <= pi (theta from the line of contact; the planes theta = 0 and pi are planes of symmetry), per unit length:
  - the roll: conductivity 1.3 W/(m K) across the layers (r) and 25 W/(m K) along them (theta), volumetric heat
    capacity rho c = (C_cell - m_can c_can) / (pi R^2 L) = 2.336e6 J/(m3 K), as the resolved neighbour holds them;
  - the can: a surface layer with heat capacity C_s = m_can c_can / A_cell = 841.7 J/(m2 K) and in-plane
    conductance k_can t_can = 3.75e-3 W/K, its nodes on r = R (v12_model's shell term and can mass);
  - at r = R: the contact and the air wedge to the trigger, h(theta) = k_air / (2R(1 - cos theta) + k_air/h_c) for
    theta < 45 degrees (integrated exactly over each face), room convection 10 W/(m2 K) beyond 45 degrees, radiation
    to the room eps sigma (T^4 - Ta^4) over the whole circumference, and the radiation received from the trigger,
    eps^2 sigma F (T1^4 - Ta^4) shared over theta as the view factor's local value (v12_model.f_local_touch);
  - the delivery: a uniform flux q(t) = E p(t) / A_region over the region's faces (theta <= 90 degrees for the facing
    half, every theta for the whole surface), p the archive's triangular pulse.
Time stepping as the resolved code's: implicit in conduction and the contact (the trigger's temperature at the end of
the step), explicit in radiation, the delivery's energy exact over each step.

The trigger's conduction enters by superposition (D131 (2)): T = T_cond + f T_unit, where T_cond is the run with
the trigger and no delivery (radiation as the code holds it) and T_unit the response to the whole ejected energy
(f = 1) with the trigger's terms removed. The perturbation's radiation is the exact secant of the code's radiation
along the threshold's own solution, eps sigma [(T_cond + f T_unit)^4 - T_cond^4] / (f T_unit), found by fixed-point
iteration on f, so that at convergence T_cond + f* T_unit is the nonlinear model's solution at f*. The threshold is
f* = min over surface nodes and steps of (T_L - T_cond) / T_unit, which also gives the hot spot's place and time.

Two implementations (V1): `Section(impl="sparse")` (vectorised assembly, r-major order, SuperLU) and
`Section(impl="banded")` (loop assembly, theta-major order, banded Cholesky).
"""
import math
import os
import sys

import numpy as np
import scipy.sparse as sps
import scipy.sparse.linalg as spla
import scipy.linalg as sla

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v12_model as V                      # noqa: E402  (unchanged)
import stage13_inputs as IN                # noqa: E402

LP = V.LP
R = IN.R


def _graded(length, ds0, grow, dsmax):
    out = []
    s = ds0
    while sum(out) + s < length - 1e-15:
        out.append(s)
        s = min(s * grow, dsmax)
    rest = length - sum(out)
    if rest < 0.5 * out[-1]:
        out[-1] += rest
    else:
        out.append(rest)
    return np.array(out)


def grid(refine=1.0):
    """Radial faces (from the axis to R) and azimuthal faces (0 to pi) with faces exactly at 45 and 90 degrees."""
    dr = _graded(R, 0.02e-3 / refine, 1.15 ** (1 / refine), 0.4e-3 / refine)[::-1]      # from the axis outward
    rho = np.concatenate([[0.0], np.cumsum(dr)])
    rho[-1] = R
    s1 = _graded(R * math.pi / 4, 0.03e-3 / refine, 1.15 ** (1 / refine), 0.4e-3 / refine)
    s2 = np.full(int(math.ceil(R * math.pi / 4 / (0.4e-3 / refine))), R * math.pi / 4 / math.ceil(R * math.pi / 4 / (0.4e-3 / refine)))
    s3 = _graded(R * math.pi / 2, 0.4e-3 / refine, 1.1 ** (1 / refine), 1.0e-3 / refine)
    th = np.concatenate([[0.0], np.cumsum(np.concatenate([s1, s2, s3])) / R])
    th[len(s1)] = math.pi / 4
    th[len(s1) + len(s2)] = math.pi / 2
    th[-1] = math.pi
    return rho, th


def _contact_integral(t_a, t_b, h_c):
    """R times the integral of h(theta) over [t_a, t_b] within the sector (the exact antiderivative, v12_model)."""
    Y = LP.K_AIR / h_c
    a = math.sqrt((4 * R + Y) / Y)
    F = lambda t: 2 * LP.K_AIR * R / math.sqrt(Y * (4 * R + Y)) * math.atan(math.tan(t / 2) * a)
    return F(min(t_b, math.pi / 4)) - F(min(t_a, math.pi / 4))


def _view_integral(t_a, t_b, n=64):
    x, w = np.polynomial.legendre.leggauss(n)
    tt = 0.5 * (t_a + t_b) + 0.5 * (t_b - t_a) * x
    return 0.5 * (t_b - t_a) * float(np.sum(w * V.f_local_touch(tt)))


class Section:
    def __init__(self, h_c=2000.0, refine=1.0, impl="sparse", region="half"):
        self.impl, self.region, self.h_c = impl, region, h_c
        self.rho, self.th = grid(refine)
        nr, nt = len(self.rho) - 1, len(self.th) - 1
        self.nr, self.nt = nr, nt
        rho, th = self.rho, self.th
        rc = 0.5 * (rho[:-1] + rho[1:])
        tc = 0.5 * (th[:-1] + th[1:])
        dth = np.diff(th)
        self.tc, self.dth = tc, dth
        kr, kt = IN.K_R, IN.K_Z
        # boundary terms per can node (per unit length of the half section)
        self.g_contact = np.array([R * 0.0 + _contact_integral(th[j], th[j + 1], h_c) for j in range(nt)])
        self.h_conv = np.where(tc > math.pi / 4, IN.H_CONV * R * dth, 0.0)
        self.w_rad = IN.EPS * IN.SIGMA * R * dth
        vi = np.array([_view_integral(th[j], th[j + 1]) for j in range(nt)])
        self.g_rad = IN.EPS ** 2 * IN.SIGMA * V.F_TOUCH * math.pi * R * vi / vi.sum()
        if region == "half":
            ind = (tc < math.pi / 2).astype(float)
        elif region == "whole":
            ind = np.ones(nt)
        else:
            raise ValueError(region)
        self.q_share = ind * R * dth / IN.A_REGION[region]          # W per unit length per W of delivered power
        self.cap_roll = IN.RHO_CP * 0.5 * (rho[1:, None] ** 2 - rho[:-1, None] ** 2) * dth[None, :]
        self.cap_can = IN.C_S * R * dth
        # conductances
        self.g_r = kr * rho[1:-1, None] * dth[None, :] / np.diff(rc)[:, None]            # (nr-1, nt)
        self.g_t = kt * np.diff(rho)[:, None] / (rc[:, None] * np.diff(tc)[None, :])       # (nr, nt-1)
        self.g_rc = kr * R * dth / (R - rc[-1])                                            # outer roll to can
        self.g_cc = IN.KT_CAN / (R * np.diff(tc))                                          # can to can
        self.n = nr * nt + nt
        self._facts = {}

    # -------------------------------------------------------------------------------------------- matrix assembly
    def _idx_roll(self, i, j):
        return i * self.nt + j if self.impl == "sparse" else j * (self.nr + 1) + i

    def _idx_can(self, j):
        return self.nr * self.nt + j if self.impl == "sparse" else j * (self.nr + 1) + self.nr

    def capacity(self):
        c = np.zeros(self.n)
        for i in range(self.nr):
            for j in range(self.nt):
                c[self._idx_roll(i, j)] = self.cap_roll[i, j]
        for j in range(self.nt):
            c[self._idx_can(j)] = self.cap_can[j]
        return c

    def _edges(self):
        """(a, b, g) for every conductance between two unknowns."""
        nr, nt = self.nr, self.nt
        if self.impl == "sparse":
            I, J = np.meshgrid(np.arange(nr - 1), np.arange(nt), indexing="ij")
            a1, b1, g1 = (I * nt + J).ravel(), ((I + 1) * nt + J).ravel(), self.g_r.ravel()
            I, J = np.meshgrid(np.arange(nr), np.arange(nt - 1), indexing="ij")
            a2, b2, g2 = (I * nt + J).ravel(), (I * nt + J + 1).ravel(), self.g_t.ravel()
            j = np.arange(nt)
            a3, b3, g3 = (nr - 1) * nt + j, nr * nt + j, self.g_rc
            j = np.arange(nt - 1)
            a4, b4, g4 = nr * nt + j, nr * nt + j + 1, self.g_cc
            return np.concatenate([a1, a2, a3, a4]), np.concatenate([b1, b2, b3, b4]), np.concatenate([g1, g2, g3, g4])
        out = []
        for j in range(nt):
            for i in range(nr - 1):
                out.append((self._idx_roll(i, j), self._idx_roll(i + 1, j), self.g_r[i, j]))
            out.append((self._idx_roll(nr - 1, j), self._idx_can(j), self.g_rc[j]))
            if j < nt - 1:
                for i in range(nr):
                    out.append((self._idx_roll(i, j), self._idx_roll(i, j + 1), self.g_t[i, j]))
                out.append((self._idx_can(j), self._idx_can(j + 1), self.g_cc[j]))
        a, b, g = zip(*out)
        return np.array(a), np.array(b), np.array(g)

    def can_index(self):
        return np.array([self._idx_can(j) for j in range(self.nt)])

    def factor(self, dt):
        key = round(dt, 12)
        if key in self._facts:
            return self._facts[key]
        C = self.capacity()
        a, b, g = self._edges()
        ci = self.can_index()
        diag = C / dt
        diag[ci] += self.g_contact + self.h_conv
        if self.impl == "sparse":
            rows = np.concatenate([a, b, a, b])
            cols = np.concatenate([b, a, a, b])
            vals = np.concatenate([-g, -g, g, g])
            A = sps.coo_matrix((vals, (rows, cols)), shape=(self.n, self.n)).tocsc() + sps.diags(diag).tocsc()
            lu = spla.splu(A.tocsc())
            solve = lu.solve
        else:
            bw = self.nr + 1
            ab = np.zeros((bw + 1, self.n))            # upper form for cholesky_banded: ab[bw + i - j, j] = A[i, j]
            ab[bw] = diag
            for x, y, gg in zip(a, b, g):
                i, j = (x, y) if x < y else (y, x)
                ab[bw + i - j, j] -= gg
                ab[bw, i] += gg
                ab[bw, j] += gg
            cf = sla.cholesky_banded(ab, lower=False)
            solve = lambda r, cf=cf: sla.cho_solve_banded((cf, False), r)
        self._facts[key] = (C, solve)
        return self._facts[key]

    # -------------------------------------------------------------------------------------------- one run
    def run(self, T1_of_t, pulse, E, t_end, dt_early=0.01, dt_late=0.05, t_switch=60.0, nonlinear=True, h_sec=None,
            Ta=None):
        """Integrate. With T1_of_t (K, a function) the trigger's terms are on; with pulse/E the delivery is on;
        nonlinear radiation (T^4) or, for the perturbation, the explicit secant coefficients h_sec[n, j] times the
        surface temperature. Returns (times, surface temperatures [steps, nt], interior max per step)."""
        Ta = IN.T_AMB if Ta is None else Ta
        ci = self.can_index()
        T = np.full(self.n, Ta if nonlinear else 0.0)
        t = 0.0
        times, surf, inner = [0.0], [T[ci].copy()], [T.max()]
        n = 0
        while t < t_end - 1e-9:
            dt = dt_early if t < t_switch - 1e-9 else dt_late
            dt = min(dt, t_end - t)
            C, solve = self.factor(dt)
            t_new = round(t + dt, 10)
            rhs = C / dt * T
            Ts = T[ci]
            r = np.zeros(self.nt)
            if nonlinear:
                r += self.h_conv * Ta - self.w_rad * (Ts ** 4 - Ta ** 4)
                if T1_of_t is not None:
                    T1 = T1_of_t(t_new)
                    r += self.g_contact * T1 + self.g_rad * (T1 ** 4 - Ta ** 4)
                else:
                    r += self.g_contact * Ta
            else:
                r -= h_sec[n] * Ts
            if pulse is not None and E > 0.0:
                dQ = E * (pulse(t_new) - pulse(t))
                r += self.q_share * dQ / dt
            rhs[ci] += r
            T = solve(rhs)
            t = t_new
            n += 1
            times.append(t)
            surf.append(T[ci].copy())
            inner.append(np.delete(T, ci).max())
        return np.array(times), np.array(surf), np.array(inner)


def tri_cumulative(tau):
    """The archive's triangular pulse as a cumulative fraction of its energy (stage7_model.Event)."""
    def F(t):
        if t <= 0.0:
            return 0.0
        if t >= tau:
            return 1.0
        if t <= tau / 2:
            return 2.0 * (t / tau) ** 2
        return 1.0 - 2.0 * ((tau - t) / tau) ** 2
    return F


def threshold(test, tau_d, region="half", h="central", impl="sparse", refine=1.0, dt_early=0.01, dt_late=None,
              t_end=None, tol=1e-12, max_iter=60, sec=None, history=None, trigger_on=True):
    """A2's f* for one case, with the hot spot's place and time. trigger_on=False drops the trigger's terms (the
    delivery alone, for the record)."""
    tests = IN.tests()
    t = tests[test]
    if history is None:
        f1, data, _, _ = V.stage5_t1(t["connection"], V.H_CONTACT[h], V.G_TAB["central"], IN.TAU_TRIGGER,
                                     float(t["E_b_J"]), IN.T_AMB)
    else:
        f1 = history
    sec = Section(V.H_CONTACT[h], refine, impl, region) if sec is None else sec
    dt_late = (max(0.01, min(0.1, tau_d / 1000.0)) if dt_late is None else dt_late)
    t_end = min(900.0, 2.0 * tau_d + 150.0) if t_end is None else t_end
    Ee = IN.e_e(test)
    F = tri_cumulative(tau_d)
    if trigger_on:
        tt, Tc, inner_c = sec.run(f1, None, 0.0, t_end, dt_early, dt_late)
    else:
        tt, Tc, inner_c = sec.run(None, None, 0.0, t_end, dt_early, dt_late)
    Ta = IN.T_AMB
    TL = IN.T_LEVEL
    if Tc.max() >= TL:
        n, j = np.unravel_index(np.argmax(Tc >= TL), Tc.shape)
        return {"f_star": 0.0, "trigger_alone": True, "theta_deg": math.degrees(sec.tc[j]), "t_s": float(tt[n]),
                "n_iter": 0, "T_cond_C": float(Tc[n, j] - IN.K0)}
    w = sec.w_rad[None, :]
    h_sec = 4.0 * w * Tc ** 3                       # the tangent, to start
    f_prev = None
    hist = []
    for it in range(max_iter):
        _, Tu, inner_u = sec.run(None, F, Ee, t_end, dt_early, dt_late, nonlinear=False, h_sec=h_sec)
        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = np.where(Tu > 1e-9, (TL - Tc) / Tu, np.inf)
        k = np.argmin(ratio)
        n, j = np.unravel_index(k, ratio.shape)
        f = float(ratio[n, j])
        hist.append(f)
        if f_prev is not None and abs(f - f_prev) <= tol * f:
            break
        f_prev = f
        d = f * Tu
        with np.errstate(divide="ignore", invalid="ignore"):
            h_sec = np.where(d > 1e-9, w * ((Tc + d) ** 4 - Tc ** 4) / np.where(d > 1e-9, d, 1.0), 4.0 * w * Tc ** 3)
    # the check of the fixed point: the nonlinear model run directly at f*, its surface and interior maxima
    if trigger_on:
        _, Ts_chk, inner_chk = sec.run(f1, F, f * Ee, t_end, dt_early, dt_late)
    else:
        _, Ts_chk, inner_chk = sec.run(None, F, f * Ee, t_end, dt_early, dt_late)
    return {"f_star": f, "E_star_J": f * Ee, "trigger_alone": False, "theta_deg": math.degrees(sec.tc[j]),
            "t_s": float(tt[n]), "n_iter": len(hist), "f_iter": hist, "T_cond_C": float(Tc[n, j] - IN.K0),
            "T_cond_at_hot_spot": (tt, Tc[:, j]), "rise_unit_K": float(Tu[n, j]),
            "direct_surface_max_C": float(Ts_chk.max() - IN.K0), "direct_inner_max_C": float(inner_chk.max() - IN.K0),
            "surface_max_C": float((Tc + f * Tu).max() - IN.K0),
            "t_end_s": t_end, "peak_before_end": bool(tt[n] < t_end - 30.0), "nr": sec.nr, "nt": sec.nt,
            "dt_early": dt_early, "dt_late": dt_late, "region": region, "tau_d_s": tau_d, "test": test, "h": h}


if __name__ == "__main__":
    import time
    t0 = time.time()
    r = threshold("M50_PT_Exp1", IN.TAU_TRIGGER)
    print({k: v for k, v in r.items() if k != "T_cond_at_hot_spot"}, time.time() - t0)
