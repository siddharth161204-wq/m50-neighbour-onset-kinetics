"""Stage 13, Part A1: the closed form of the local threshold (DECISIONS.md D131 (1)).

A half-space x > 0 (the roll across its layers: conductivity k_r = 1.3 W/(m K), volumetric heat capacity
rho c = 2.336e6 J/(m3 K), effusivity e = sqrt(k_r rho c) = 1,743 J/(m2 K s^0.5)) whose surface x = 0 carries the
can as a layer of heat capacity C_s = 841.7 J/(m2 K) and no resistance, receives the triangular flux q(t) (energy
E'' per unit area over tau, peak 2E''/tau at tau/2) and loses heat linearly, h (T_s - T_b), with h the surface's
loss coefficient to first order (the local contact or convection coefficient plus radiation linearised as the secant
from T_b to the level). In Laplace variables the surface temperature rise is u(s) = q(s) / (C_s s + e sqrt(s) + h).
With C_s p^2 + e p + h = C_s (p + a)(p + b) (a + b = e/C_s, a b = h/C_s) and phi_x(t) = exp(x^2 t) erfc(x sqrt t):
    impulse  g(t)  = [a phi_a - b phi_b] / (C_s (a - b))
    step     G1(t) = [(phi_a - 1)/a - (phi_b - 1)/b] / (C_s (a - b))
    ramp     G2(t) = [(I_a - t)/a - (I_b - t)/b] / (C_s (a - b)),  I_x(t) = [phi_x(t) - 1 + 2 x sqrt(t/pi)] / x^2
    triangle u(t)  = (4 E''/tau^2) [G2(t) - 2 G2(t - tau/2) + G2(t - tau)]      (G2 = 0 for negative arguments)
The peak rise is u_pk = Phi(gamma, beta) E'' / (e sqrt(tau)) with gamma = C_s / (e sqrt(tau)) and
beta = h sqrt(tau) / e; Phi(0, 0) = 1.2284 at t = 2 tau / 3 (D130 (3)). The threshold is
    f*_A1 = (T_L - T_b) A_region e sqrt(tau) / (E_e Phi(gamma, beta)).

Two implementations (V1): `peak_closed` (the erfc forms above) and `peak_laplace` (mpmath's Talbot inversion of
1/(s^2 (C_s s + e sqrt(s) + h)) for the ramp, at 30 digits).
"""
import math
import os
import sys

import numpy as np
from scipy.optimize import brentq
from scipy.special import erfcx, wofz

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage13_inputs as IN                # noqa: E402


def roots(h, e=IN.E_ROLL, Cs=IN.C_S):
    """a, b with a + b = e/C_s and a b = h/C_s (b written in the form free of cancellation); complex conjugates when
    4 C_s h > e^2 (a loss coefficient above about 900 W/(m2 K), within the contact band)."""
    disc = e * e - 4.0 * Cs * h
    d = math.sqrt(disc) if disc >= 0 else 1j * math.sqrt(-disc)
    return (e + d) / (2 * Cs), 2.0 * h / (e + d)


def _phi(x, t):
    if isinstance(x, complex):
        return wofz(1j * x * math.sqrt(t))         # erfcx(z) = w(i z), the Faddeeva function
    return erfcx(x * math.sqrt(t))


def G1(t, h, e=IN.E_ROLL, Cs=IN.C_S):
    if t <= 0:
        return 0.0
    a, b = roots(h, e, Cs)
    if b == 0.0:
        return ((_phi(a, t) - 1) / a + 2 * math.sqrt(t / math.pi)) / (Cs * a)
    return float(np.real(((_phi(a, t) - 1) / a - (_phi(b, t) - 1) / b) / (Cs * (a - b))))


def _Ix_minus_t_over_x(x, t):
    """(I_x(t) - t) / x with I_x = [phi_x - 1 + 2 x sqrt(t/pi)] / x^2; a series for small x sqrt(t)."""
    z = x * math.sqrt(t)
    if abs(z) < 1e-3:
        # phi = 1 - 2z/sqrt(pi) + z^2 - 4 z^3/(3 sqrt(pi)) + z^4/2 - 8 z^5/(15 sqrt(pi)) ...
        sp = math.sqrt(math.pi)
        return t ** 1.5 * (-4.0 / (3 * sp) + z / 2.0 - 8.0 * z * z / (15 * sp) + z ** 3 / 6.0)
    return ((_phi(x, t) - 1 + 2 * z / math.sqrt(math.pi)) / x ** 2 - t) / x


def G2(t, h, e=IN.E_ROLL, Cs=IN.C_S):
    if t <= 0:
        return 0.0
    a, b = roots(h, e, Cs)
    if b == 0.0:
        return (_Ix_minus_t_over_x(a, t) + 4.0 / (3 * math.sqrt(math.pi)) * t ** 1.5) / (Cs * a)
    return float(np.real((_Ix_minus_t_over_x(a, t) - _Ix_minus_t_over_x(b, t)) / (Cs * (a - b))))


def rise_closed(t, tau, Epp, h, e=IN.E_ROLL, Cs=IN.C_S):
    return 4.0 * Epp / tau ** 2 * (G2(t, h, e, Cs) - 2 * G2(t - tau / 2, h, e, Cs) + G2(t - tau, h, e, Cs))


def _slope_closed(t, tau, h, e, Cs):
    return G1(t, h, e, Cs) - 2 * G1(t - tau / 2, h, e, Cs) + G1(t - tau, h, e, Cs)


def peak_closed(tau, Epp, h, e=IN.E_ROLL, Cs=IN.C_S):
    """(peak rise K, time of the peak s) of the closed form: the zero of du/dt after tau/2."""
    f = lambda t: _slope_closed(t, tau, h, e, Cs)
    lo, hi = 0.5 * tau, tau
    while f(hi) > 0:
        hi *= 1.5
    tp = brentq(f, lo, hi, xtol=1e-14 * tau, rtol=1e-15, maxiter=500)
    return rise_closed(tp, tau, Epp, h, e, Cs), tp


def peak_laplace(tau, Epp, h, e=IN.E_ROLL, Cs=IN.C_S, dps=30):
    import mpmath as mp
    mp.mp.dps = dps
    e_, C_, h_ = mp.mpf(e), mp.mpf(Cs), mp.mpf(h)
    ramp = lambda t: mp.invertlaplace(lambda s: 1 / (s ** 2 * (C_ * s + e_ * mp.sqrt(s) + h_)), t, method="talbot") \
        if t > 0 else mp.mpf(0)
    step = lambda t: mp.invertlaplace(lambda s: 1 / (s * (C_ * s + e_ * mp.sqrt(s) + h_)), t, method="talbot") \
        if t > 0 else mp.mpf(0)
    tau_ = mp.mpf(tau)
    slope = lambda t: step(t) - 2 * step(t - tau_ / 2) + step(t - tau_)
    # bisection on the slope's sign (it falls through zero once after tau/2)
    lo, hi = tau_ / 2, tau_
    while slope(hi) > 0:
        hi *= mp.mpf(1.5)
    for _ in range(60):
        mid = (lo + hi) / 2
        if slope(mid) > 0:
            lo = mid
        else:
            hi = mid
    tp = (lo + hi) / 2
    u = 4 * mp.mpf(Epp) / tau_ ** 2 * (ramp(tp) - 2 * ramp(tp - tau_ / 2) + ramp(tp - tau_))
    return float(u), float(tp)


def Phi(gamma, beta):
    """The dimensionless peak: u_pk e sqrt(tau) / E'' for gamma = C_s/(e sqrt tau), beta = h sqrt(tau)/e (tau = 1)."""
    e = 1.0
    return peak_closed(1.0, 1.0, beta * e, e, max(gamma, 1e-12) * e)[0]


def h_loss(theta_deg, T_b_K, h_c=2000.0):
    """The surface's loss coefficient to first order at the hot spot: the local contact (theta < 45 degrees) or room
    convection, plus radiation as the secant from T_b to the level."""
    import v12_model as V
    th = math.radians(theta_deg)
    local = float(V.h_local(th, h_c)) if th < math.pi / 4 else IN.H_CONV
    TL = IN.T_LEVEL
    rad = IN.EPS * IN.SIGMA * (TL ** 2 + T_b_K ** 2) * (TL + T_b_K)
    return local + rad, local, rad


def threshold(test, tau_d, theta_deg, T_b_of_t, region="half", h_c=2000.0, impl="closed"):
    """f*_A1 with the place and the no-delivery temperature T_b taken from A2 (T_b_of_t: K at time t)."""
    Ee = IN.e_e(test)
    Epp = Ee / IN.A_REGION[region]                  # J/m2 per unit f
    T_b = T_b_of_t(2 * tau_d / 3)
    for _ in range(3):                              # T_b at the peak's time, the loss from T_b
        h, local, rad = h_loss(theta_deg, T_b, h_c)
        u, tp = (peak_closed if impl == "closed" else peak_laplace)(tau_d, Epp, h)
        T_b = T_b_of_t(tp)
    h, local, rad = h_loss(theta_deg, T_b, h_c)
    u, tp = (peak_closed if impl == "closed" else peak_laplace)(tau_d, Epp, h)
    f = (IN.T_LEVEL - T_b) / u
    gamma = IN.C_S / (IN.E_ROLL * math.sqrt(tau_d))
    beta = h * math.sqrt(tau_d) / IN.E_ROLL
    u0, tp0 = peak_closed(tau_d, Epp, 0.0)
    return {"f_star": f, "E_star_J": f * Ee, "t_peak_s": tp, "T_b_C": T_b - IN.K0, "h_W_m2K": h, "h_local": local,
            "h_rad": rad, "gamma": gamma, "beta": beta, "Phi": u * IN.E_ROLL * math.sqrt(tau_d) / Epp,
            "rise_per_f_K": u, "pure_skin_f_star": (IN.T_LEVEL - IN.T_AMB) / u0, "pure_skin_t_peak_s": tp0,
            "pure_skin_Phi": u0 * IN.E_ROLL * math.sqrt(tau_d) / Epp}


if __name__ == "__main__":
    print("Phi(0,0) =", Phi(0.0, 0.0), "t_pk/tau =", peak_closed(1.0, 1.0, 0.0, 1.0, 1e-12)[1],
          "exact 16 (2/3)^1.5 ... =", 16.0 / (3 * math.sqrt(math.pi)) * ((2 / 3) ** 1.5 - 2 * (1 / 6) ** 1.5))
    for tau in (5.0, 21.38651984299561):
        Epp = IN.e_e("M50_PT_Exp1") / IN.A_HALF
        a = peak_closed(tau, Epp, 25.0)
        b = peak_laplace(tau, Epp, 25.0)
        print(tau, a, b, abs(a[0] - b[0]) / a[0])
