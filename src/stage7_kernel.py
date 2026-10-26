"""Stage 7 (version 1.3.0): the Stage 5 compiled reaction sub-step (src/v12_kernel.py, D41) with the largest number
of explicit sub-steps as an argument (DECISIONS.md D68 (3)).

`v12_kernel.substeps` integrates each node with explicit Heun sub-steps, 1 to 64 of them (a power of two), chosen so
that in each sub-step every amount and every temperature-driven rate changes by less than 2e-3 and the temperature by
less than 0.02 K (D13), and leaves a node that would need more than 64 to the implicit integrator
(`reactive.LocalKinetics._implicit`, BDF). `substeps_max` is the same function, operation for operation, with that
limit, 64, as an argument; with 64 it returns what `v12_kernel.substeps` returns (src/test_stage7.py checks it
bitwise). A Part C run uses it with a larger limit from its event's time on (D68 (3)): the explicit sub-steps keep
D13's accuracy limits, so only the share of nodes left to the implicit integrator, and so the cost, changes.
"""
import math
import numpy as np
import numba as nb

import v12_kernel as KN                         # the Stage 5 kernel, unchanged
from v12_kernel import _rates_node, _heat, R_GAS, SLOW_FRAC, DT_EXPLICIT, C_FLOOR, NS, NR


@nb.njit(cache=True)
def substeps_max(T, c, R0, H0, dt, m, C, lnA, b, Ea, n_react, react_idx, react_ord, S, hm, max_sub):
    """v12_kernel.substeps with MAX_SUB as the argument max_sub."""
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
        if nsub > max_sub:
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


class FastKineticsMax(KN.FastKinetics):
    """v12_kernel.FastKinetics (one thread) with the explicit sub-step limit max_sub; the start-of-step rates and the
    implicit integrator are Stage 5's, unchanged."""

    def __init__(self, kin, m, C, max_sub):
        super().__init__(kin, m, C, threads=1)
        self.max_sub = int(max_sub)

    def step(self, T, c, R0, H0, dt, rtol=1e-7):
        Tn, cn, imp = substeps_max(T, np.ascontiguousarray(c), R0, H0, dt, self.m, self.C, *self.p, self.max_sub)
        f = np.where(imp)[0]
        if f.size:
            Tn[f], cn[:, f] = self.loc._implicit(T[f], c[:, f], dt, f, rtol)
        return Tn, cn, int(f.size)
