"""Stage 5 (version 1.2.0): a compiled form of the Stage 2 reaction sub-step (DECISIONS.md D41).

`reactive.LocalKinetics.step` (Stage 2, D13) is vectorised numpy: for every node it evaluates the B-CRNN rates at the
start of the step, picks a number of explicit Heun sub-steps (1 to 64, a power of two) from how fast the node's
amounts, temperature-driven rates and temperature change, and integrates the nodes that would need more than 64
sub-steps with BDF. This module does the same per node in numba, with the same rules and the same limits:

  - rates: r_j = exp(min(ln A_j + b_j ln T - Ea_j / (R T) + sum_s n_sj ln c_s, 700)), zero once a reactant is spent;
  - heating: dT/dt = (sum_j dH_j' r_j) m_i / C_i;
  - sub-step count: 2^ceil(log2(max(cons / 2e-3, sens / 2e-3, |H| dt / 0.02 K, 1)));
  - Heun sub-steps with the amounts clipped at zero after each stage;
  - nodes needing more than 64 sub-steps are flagged and integrated by `reactive.LocalKinetics._implicit`, unchanged.

The only difference is arithmetic order: numpy forms the sums over species with BLAS, this module in species
order, and the libraries' exp and log differ in the last bit. `src/v12_checks.py` measures the effect against the
numpy path (V2 and D41).
"""
import math
import os
import numpy as np
import numba as nb

import bcrnn
import reactive as RX

R_GAS = bcrnn.R_GAS
SLOW_FRAC, DT_EXPLICIT, MAX_SUB, C_FLOOR = RX.SLOW_FRAC, RX.DT_EXPLICIT, RX.MAX_SUB, RX.C_FLOOR
NS, NR = bcrnn.NS, bcrnn.NR


def pack(kin):
    """The arrays the kernel needs from a bcrnn.Kinetics object."""
    order = np.asarray(kin.order, float)
    n_react = np.zeros(NR, np.int64)
    react_idx = np.zeros((NR, NS), np.int64)
    react_ord = np.zeros((NR, NS))
    for j in range(NR):
        s_list = np.where(order[:, j] != 0)[0]          # the species order of bcrnn.Kinetics.reactants
        n_react[j] = s_list.size
        react_idx[j, :s_list.size] = s_list
        react_ord[j, :s_list.size] = order[s_list, j]
    return (np.ascontiguousarray(kin.lnA, float), np.ascontiguousarray(kin.b, float),
            np.ascontiguousarray(kin.Ea, float), n_react, react_idx, react_ord,
            np.ascontiguousarray(kin.stoich, float), np.ascontiguousarray(kin.h_mass, float))


@nb.njit(cache=True, inline="always")
def _rates_node(T, c, i, lnA, b, Ea, n_react, react_idx, react_ord, out):
    lnT = math.log(T)
    RT = R_GAS * T
    for j in range(NR):
        e = lnA[j] + b[j] * lnT
        e = e - Ea[j] / RT
        ok = True
        acc = 0.0
        for k in range(n_react[j]):
            cs = c[react_idx[j, k], i]
            if cs <= 0.0:
                ok = False
                break
            acc += react_ord[j, k] * math.log(cs)
        if ok:
            e = e + acc
            if e > 700.0:
                e = 700.0
            out[j] = math.exp(e)
        else:
            out[j] = 0.0


@nb.njit(cache=True, inline="always")
def _heat(r, hm, mi, Ci):
    q = 0.0
    for j in range(NR):
        q += hm[j] * r[j]
    return q * mi / Ci


@nb.njit(cache=True)
def heat0(T, c, m, C, lnA, b, Ea, n_react, react_idx, react_ord, S, hm):
    """Rates (NR, N) and reaction heating (N,) at the start of a step, for every node."""
    N = T.size
    R0 = np.empty((NR, N))
    H0 = np.empty(N)
    r = np.empty(NR)
    for i in range(N):
        _rates_node(T[i], c, i, lnA, b, Ea, n_react, react_idx, react_ord, r)
        for j in range(NR):
            R0[j, i] = r[j]
        H0[i] = _heat(r, hm, m[i], C[i])
    return R0, H0


@nb.njit(cache=True)
def substeps(T, c, R0, H0, dt, m, C, lnA, b, Ea, n_react, react_idx, react_ord, S, hm):
    """Explicit Heun sub-steps over dt for every node that needs at most MAX_SUB of them. Returns the new
    temperatures and amounts, and a flag for the nodes left to the implicit integrator (their values unchanged)."""
    N = T.size
    Tn = T.copy()
    cn = c.copy()
    implicit = np.zeros(N, np.bool_)
    ra = np.empty(NR)
    rb = np.empty(NR)
    dca = np.empty(NS)
    dcb = np.empty(NS)
    cs = np.empty((NS, 1))
    c1 = np.empty((NS, 1))
    for i in range(N):
        # sub-step count, as reactive.LocalKinetics.step
        cons = 0.0
        for s in range(NS):
            d = 0.0
            for j in range(NR):
                d += S[s, j] * R0[j, i]
            if d < 0.0:
                v = -d * dt / max(c[s, i], C_FLOOR)
                if v > cons:
                    cons = v
        maxEa = 0.0
        for j in range(NR):
            v = Ea[j] if R0[j, i] > 0.0 else 0.0
            if v > maxEa:
                maxEa = v
        aH = abs(H0[i])
        sens = aH * dt * maxEa / (R_GAS * T[i] ** 2)
        need = max(max(max(cons / SLOW_FRAC, sens / SLOW_FRAC), aH * dt / DT_EXPLICIT), 1.0)
        nsub = int(2.0 ** math.ceil(math.log2(need)))
        if nsub > MAX_SUB:
            implicit[i] = True
            continue
        h = dt / nsub
        Ts = T[i]
        for s in range(NS):
            cs[s, 0] = c[s, i]
        for k in range(nsub):
            if k == 0:
                for j in range(NR):
                    ra[j] = R0[j, i]
                Ha = H0[i]
            else:
                _rates_node(Ts, cs, 0, lnA, b, Ea, n_react, react_idx, react_ord, ra)
                Ha = _heat(ra, hm, m[i], C[i])
            for s in range(NS):
                d = 0.0
                for j in range(NR):
                    d += S[s, j] * ra[j]
                dca[s] = d
            T1 = Ts + h * Ha
            for s in range(NS):
                v = cs[s, 0] + h * dca[s]
                c1[s, 0] = v if v > 0.0 else 0.0
            _rates_node(T1, c1, 0, lnA, b, Ea, n_react, react_idx, react_ord, rb)
            Hb = _heat(rb, hm, m[i], C[i])
            Ts = Ts + 0.5 * h * (Ha + Hb)
            for s in range(NS):
                d = 0.0
                for j in range(NR):
                    d += S[s, j] * rb[j]
                dcb[s] = d
            for s in range(NS):
                v = cs[s, 0] + 0.5 * h * (dca[s] + dcb[s])
                cs[s, 0] = v if v > 0.0 else 0.0
        Tn[i] = Ts
        for s in range(NS):
            cn[s, i] = cs[s, 0]
    return Tn, cn, implicit


@nb.njit(cache=True, parallel=True)
def heat0_par(T, c, m, C, lnA, b, Ea, n_react, react_idx, react_ord, S, hm, nchunk):
    """heat0 with the nodes split into chunks run on several threads; every node's arithmetic is unchanged."""
    N = T.size
    R0 = np.empty((NR, N))
    H0 = np.empty(N)
    size = (N + nchunk - 1) // nchunk
    for ch in nb.prange(nchunk):
        r = np.empty(NR)
        for i in range(ch * size, min(N, (ch + 1) * size)):
            _rates_node(T[i], c, i, lnA, b, Ea, n_react, react_idx, react_ord, r)
            for j in range(NR):
                R0[j, i] = r[j]
            H0[i] = _heat(r, hm, m[i], C[i])
    return R0, H0


@nb.njit(cache=True, parallel=True)
def substeps_par(T, c, R0, H0, dt, m, C, lnA, b, Ea, n_react, react_idx, react_ord, S, hm, nchunk):
    """substeps with the nodes split into chunks run on several threads; every node's arithmetic is unchanged."""
    N = T.size
    Tn = T.copy()
    cn = c.copy()
    implicit = np.zeros(N, np.bool_)
    size = (N + nchunk - 1) // nchunk
    for ch in nb.prange(nchunk):
        ra = np.empty(NR)
        rb = np.empty(NR)
        dca = np.empty(NS)
        dcb = np.empty(NS)
        cs = np.empty((NS, 1))
        c1 = np.empty((NS, 1))
        for i in range(ch * size, min(N, (ch + 1) * size)):
            cons = 0.0
            for s in range(NS):
                d = 0.0
                for j in range(NR):
                    d += S[s, j] * R0[j, i]
                if d < 0.0:
                    v = -d * dt / max(c[s, i], C_FLOOR)
                    if v > cons:
                        cons = v
            maxEa = 0.0
            for j in range(NR):
                v = Ea[j] if R0[j, i] > 0.0 else 0.0
                if v > maxEa:
                    maxEa = v
            aH = abs(H0[i])
            sens = aH * dt * maxEa / (R_GAS * T[i] ** 2)
            need = max(max(max(cons / SLOW_FRAC, sens / SLOW_FRAC), aH * dt / DT_EXPLICIT), 1.0)
            nsub = int(2.0 ** math.ceil(math.log2(need)))
            if nsub > MAX_SUB:
                implicit[i] = True
                continue
            h = dt / nsub
            Ts = T[i]
            for s in range(NS):
                cs[s, 0] = c[s, i]
            for k in range(nsub):
                if k == 0:
                    for j in range(NR):
                        ra[j] = R0[j, i]
                    Ha = H0[i]
                else:
                    _rates_node(Ts, cs, 0, lnA, b, Ea, n_react, react_idx, react_ord, ra)
                    Ha = _heat(ra, hm, m[i], C[i])
                for s in range(NS):
                    d = 0.0
                    for j in range(NR):
                        d += S[s, j] * ra[j]
                    dca[s] = d
                T1 = Ts + h * Ha
                for s in range(NS):
                    v = cs[s, 0] + h * dca[s]
                    c1[s, 0] = v if v > 0.0 else 0.0
                _rates_node(T1, c1, 0, lnA, b, Ea, n_react, react_idx, react_ord, rb)
                Hb = _heat(rb, hm, m[i], C[i])
                Ts = Ts + 0.5 * h * (Ha + Hb)
                for s in range(NS):
                    d = 0.0
                    for j in range(NR):
                        d += S[s, j] * rb[j]
                    dcb[s] = d
                for s in range(NS):
                    v = cs[s, 0] + 0.5 * h * (dca[s] + dcb[s])
                    cs[s, 0] = v if v > 0.0 else 0.0
            Tn[i] = Ts
            for s in range(NS):
                cn[s, i] = cs[s, 0]
    return Tn, cn, implicit


class FastKinetics:
    """Drop-in for the reaction part of the Stage 2 loop: start-of-step rates once, then sub-steps for a given dt."""

    def __init__(self, kin, m, C, threads=None):
        self.kin = kin
        self.loc = RX.LocalKinetics(kin, m, C)          # its _implicit integrates the flagged nodes, unchanged
        self.m, self.C = np.ascontiguousarray(m, float), np.ascontiguousarray(C, float)
        self.p = pack(kin)
        self.threads = int(os.environ.get("V12_KERNEL_THREADS", "1")) if threads is None else threads
        self.nchunk = 8 * self.threads

    def start(self, T, c):
        if self.threads > 1 and T.size > 1:
            return heat0_par(T, np.ascontiguousarray(c), self.m, self.C, *self.p, self.nchunk)
        return heat0(T, np.ascontiguousarray(c), self.m, self.C, *self.p)

    def step(self, T, c, R0, H0, dt, rtol=1e-7):
        if self.threads > 1 and T.size > 1:
            Tn, cn, imp = substeps_par(T, np.ascontiguousarray(c), R0, H0, dt, self.m, self.C, *self.p, self.nchunk)
        else:
            Tn, cn, imp = substeps(T, np.ascontiguousarray(c), R0, H0, dt, self.m, self.C, *self.p)
        f = np.where(imp)[0]
        if f.size:
            Tn[f], cn[:, f] = self.loc._implicit(T[f], c[:, f], dt, f, rtol)
        return Tn, cn, int(f.size)

