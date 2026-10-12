"""Posterior-mean B-CRNN decomposition kinetics of Koenig, Zhao and Deng (2025), and their use in a cell.

Source: B.C. Koenig, P. Zhao, S. Deng, Chemical Engineering Journal 507 (2025) 160402, supplementary material
(An_Ele.csv, NCM811.csv, Separator.csv and CSV_model_key.docx). The model used here is the arithmetic mean of each
parameter over the SVGD particles (inputs/kinetics/bcrnn_mean_model.json), which is what the paper's Fig. A.1(a)
calls the "mean kinetic parameters" (DECISIONS.md D3).

Rate of reaction j (paper Eq. 2):  r_j = exp( sum_s n_sj ln c_s + ln A_j + b_j ln T - Ea_j / (R T) )   [1/s]
Species (paper Eq. 3):            dc_s/dt = sum_j v_sj r_j
Heat (paper Eq. 4 and Eq. 20):    Q = sum_j dH_j r_j m_j            [W], dH_j in J/g, m_j in g

Cathode (Eq. 10): c1 -> v1 c2 -> v2 c3 -> rock salt, each step consuming its reactant with coefficient -1.
Separator (Eq. 11): one endothermic melting reaction; the sign of its heat is fixed in DECISIONS.md D5.

Species order (13): the nine of the anode-electrolyte-SEI-binder network in the supplementary order, then the
three cathode phases and the separator.
"""
import json
import math
import os
import numpy as np

R_GAS = 8.314462618
HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_JSON = os.path.join(HERE, "..", "inputs", "kinetics", "bcrnn_mean_model.json")

SPECIES = ["ele_liq", "ele_gas", "li_an", "binder", "sei", "p_ele_d", "p_an_ele", "p_an_bin", "p_sei_d",
           "cat1", "cat2", "cat3", "sep"]
NS = len(SPECIES)
# initial dimensionless amounts: paper Fig. 2 (anode-electrolyte network), Eq. (10) and (11) (cathode, separator)
C0 = np.array([1.0, 0.0, 1.0, 1.0, 0.15, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0])

# the seven anode-electrolyte reactions used in the paper, by their column in the supplementary legend
AN_ELE_COLUMNS = {"elec_evap": 0, "elec_decomp": 1, "an_ele": 2, "an_bin": 3, "sei_decomp": 4, "IV": 6, "V": 8}
REACTIONS = list(AN_ELE_COLUMNS) + ["cat1", "cat2", "cat3", "sep_melt"]
NR = len(REACTIONS)

# Component masses of the paper's ARC cell (Table 1, values from Feng et al. 2015), in g, and the reaction each
# multiplies (Eq. 20). The anode-electrolyte reaction is not listed in Table 1; DECISIONS.md D4 fixes it at the anode
# plus electrolyte mass from the paper's own Fig. A.1(a).
M_REF_G = 720.0
CP_REF = 1100.0        # J/(kg K), the paper's cell, used only to reproduce its ARC test (V1)
M_CATHODE, M_ANODE, M_ELECTROLYTE, M_SEI, M_SEPARATOR, M_IVV = 179.12, 100.58, 108.0, 100.58, 17.6, 104.3
MASS_G = {"elec_evap": M_ELECTROLYTE, "elec_decomp": M_ELECTROLYTE, "an_ele": M_ANODE + M_ELECTROLYTE,
          "an_bin": M_ANODE, "sei_decomp": M_SEI, "IV": M_IVV, "V": M_IVV,
          "cat1": M_CATHODE, "cat2": M_CATHODE, "cat3": M_CATHODE, "sep_melt": M_SEPARATOR}

SEPARATOR_HEAT_SIGN = -1.0     # D5: the supplementary file stores the magnitude; melting absorbs heat (paper Fig. 3e)


def load_mean_model(path=MODEL_JSON):
    d = json.load(open(path))
    m = rows_to_model(d["an_ele_rows_mean"], d["ncm811_rows_mean"], d["separator_rows_mean"])
    m["raw"] = d
    return m


def rows_to_model(an_ele_rows, ncm811_rows, separator_rows):
    """One parameter vector per file (the 220, 17 and 6 rows of the supplementary CSVs, in their order) to the model
    arrays. The mean model passes the row means; a Stage 3 draw passes one particle's column of each file (D22)."""
    a = np.array(an_ele_rows, dtype=float)
    n_ae = a[0:90].reshape(9, 10)            # [species, column]
    v_ae = a[90:180].reshape(9, 10)
    lnA_ae, Ea_ae, b_ae, dH_ae = a[180:190], a[190:200] * 1e5, a[200:210], a[210:220]
    cat = np.array(ncm811_rows, dtype=float)
    sep = np.array(separator_rows, dtype=float)

    order = np.zeros((NS, NR))      # reaction orders n_sj
    stoich = np.zeros((NS, NR))     # stoichiometric coefficients v_sj
    lnA, Ea, b, dH = (np.zeros(NR) for _ in range(4))
    for j, name in enumerate(AN_ELE_COLUMNS):
        col = AN_ELE_COLUMNS[name]
        order[:9, j] = n_ae[:, col]
        stoich[:9, j] = v_ae[:, col]
        lnA[j], Ea[j], b[j], dH[j] = lnA_ae[col], Ea_ae[col], b_ae[col], dH_ae[col]
    # cathode, three sequential reactions
    lnA_c, Ea_c, b_c, dH_c, n_c, v_c = cat[0:3], cat[3:6] * 1e5, cat[6:9], cat[9:12], cat[12:15], cat[15:17]
    for k in range(3):
        j = 7 + k
        s = 9 + k
        order[s, j] = n_c[k]
        stoich[s, j] = -1.0
        if k < 2:
            stoich[s + 1, j] = v_c[k]
        lnA[j], Ea[j], b[j], dH[j] = lnA_c[k], Ea_c[k], b_c[k], dH_c[k]
    # separator: rows A, v, n, Ea/1e5, b, dH
    j = 10
    lnA[j], stoich[12, j], order[12, j], Ea[j], b[j] = sep[0], sep[1], sep[2], sep[3] * 1e5, sep[4]
    dH[j] = SEPARATOR_HEAT_SIGN * sep[5]
    return {"order": order, "stoich": stoich, "lnA": lnA, "Ea": Ea, "b": b, "dH": dH}


class Kinetics:
    """Vectorised over nodes: T has shape (N,), c has shape (NS, N)."""

    def __init__(self, model=None, mass_g=None, m_ref_g=M_REF_G):
        self.m = model if model is not None else load_mean_model()
        self.order, self.stoich = self.m["order"], self.m["stoich"]
        self.lnA, self.Ea, self.b, self.dH = self.m["lnA"], self.m["Ea"], self.m["b"], self.m["dH"]
        mg = dict(MASS_G if mass_g is None else mass_g)
        self.mass_g = np.array([mg[r] for r in REACTIONS])
        self.w = self.mass_g / m_ref_g                     # reactant mass fractions of the paper's cell
        # heat per unit cell mass and per unit rate: J/kg  (dH in J/g, times 1000 g/kg, times mass fraction)
        self.h_mass = self.dH * 1e3 * self.w
        self.reactants = [np.where(self.order[:, j] != 0)[0] for j in range(NR)]
        self._lnA, self._b, self._Ea = [float(x) for x in self.lnA], [float(x) for x in self.b], [float(x) for x in self.Ea]
        self._react = [[(int(s), float(self.order[s, j])) for s in self.reactants[j]] for j in range(NR)]
        self._rmask = (self.order.T != 0).astype(float)          # (NR, NS): which species each reaction consumes

    def rates(self, T, c):
        """r_j for every reaction and node, shape (NR, N). A reaction stops when any of its reactants is exhausted."""
        T = np.atleast_1d(np.asarray(T, dtype=float))
        c = np.asarray(c, dtype=float).reshape(NS, -1)
        pos = c > 0
        lnc = np.log(np.where(pos, c, 1.0))
        e = (self.lnA[:, None] + self.b[:, None] * np.log(T)[None, :] - self.Ea[:, None] / (R_GAS * T)[None, :]
             + self.order.T @ lnc)
        ok = (self._rmask @ (~pos).astype(float)) == 0.0
        return np.where(ok, np.exp(np.minimum(e, 700.0)), 0.0)

    def rates_scalar(self, T, c):
        """Same as rates() for one node, in plain floats (the passive integration calls this many thousand times)."""
        lnT, invRT = math.log(T), 1.0 / (R_GAS * T)
        out = np.zeros(NR)
        for j in range(NR):
            e = self._lnA[j] + self._b[j] * lnT - self._Ea[j] * invRT
            for s, n in self._react[j]:
                cs = c[s]
                if cs <= 0.0:
                    break
                e += n * math.log(cs)
            else:
                out[j] = math.exp(min(e, 700.0))
        return out

    def dcdt(self, r):
        return self.stoich @ r

    def q_mass(self, r):
        """Reaction heat per unit cell mass, W/kg, shape (N,)."""
        return self.h_mass @ r

    def q_mass_by_reaction(self, r):
        return self.h_mass[:, None] * r

    def jacobian(self, T, c, r):
        """d r_j / d c_s (NR, NS, N) and d r_j / d T (NR, N) for the local adiabatic system of Stage 2."""
        T = np.atleast_1d(T)
        drdc = np.zeros((NR, NS, T.size))
        for j in range(NR):
            for s in self.reactants[j]:
                cs = c[s]
                drdc[j, s] = np.where(cs > 0, self.order[s, j] * r[j] / np.where(cs > 0, cs, 1.0), 0.0)
        drdT = r * (self.b[:, None] / T + self.Ea[:, None] / (R_GAS * T ** 2))
        return drdc, drdT


def fresh_state(n=1):
    return np.repeat(C0[:, None], n, axis=1)
