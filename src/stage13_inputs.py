"""Stage 13 (Brief 22): the inputs every Stage 13 module shares, all read from the archive (DECISIONS.md D130 onward).

Nothing here is new physics. The constants are the resolved and the lumped neighbour's own (the two-cell study's
`lumped_two_cell`, `v12_model`), the tests and the ejected-energy ratio are Stage 8's (`stage9_inputs`), and the run
lists are the searches of Parts A4 and B4 of the brief, written out once so that their hash can be registered with
the predictions (predictions_stage13.md).

Symbols used across Stage 13 (each also defined where it is used):
  T_L      the propagation level, 255.68 C (528.83 K), the lower end of the two-cell study's onset band (D35)
  f        the delivered fraction of a test's ejected energy E_e = r E_b (r = 3.105, the Databank median; D77)
  E        the delivered energy, f E_e, in J
  tau_d    the delivery's duration in s (triangular: zero at 0 and tau_d, peak 2E/tau_d at tau_d/2)
  e        the roll's across-layer thermal effusivity, sqrt(k_r rho c), J/(m2 K s^0.5)
  C_s      the can's heat capacity per unit area, J/(m2 K)
"""
import hashlib
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v12_model as V                    # noqa: E402  (unchanged)
import stage9_run as R9                  # noqa: E402  (unchanged)

LP = V.LP
ROOT = os.path.abspath(os.path.join(HERE, ".."))
RES = os.path.join(ROOT, "results")
RUNS = os.path.join(RES, "stage13_runs")
SERIES = os.path.join(RES, "stage13_series")
K0 = 273.15

# ------------------------------------------------------------------------------------------------ the model's facts
T_AMB = LP.T_AMB                                   # 298.15 K
T_LEVEL = V.LEVEL_PROP                             # 528.83 K, 255.68 C
T_LEVEL_C = T_LEVEL - K0
R = V.R                                            # 10.55 mm
LZ = V.LZ                                          # 70.1 mm
K_R, K_Z = LP.K_RADIAL, LP.K_AXIAL                 # 1.3 and 25 W/(m K): across and along the layers
C_CAN = LP.M_CAN * LP.CP_CAN                       # 4.5 J/K, the can
C_S = C_CAN / LP.A_CELL                            # 841.7 J/(m2 K): the can spread over the outer area (v12_model)
KT_CAN = LP.K_CAN * LP.T_CAN                       # 3.75e-3 W/K: the can's in-plane conductance (shell term)
V_CELL = math.pi * R ** 2 * LZ
RHO_CP = (LP.C_CELL - C_CAN) / V_CELL              # 2.336e6 J/(m3 K), the roll (v12_model, exact volume)
E_ROLL = math.sqrt(K_R * RHO_CP)                   # 1,743 J/(m2 K s^0.5)
ALPHA_R = K_R / RHO_CP                             # 5.565e-7 m2/s across the layers
ALPHA_Z = K_Z / RHO_CP                             # 1.070e-5 m2/s along the layers
EPS, SIGMA = LP.EPS, LP.SIGMA
H_CONV = LP.H_CONV
SECTOR = math.pi / 4                               # the 90 degree sector facing the trigger: contact, no convection
A_HALF = math.pi * R * LZ                          # theta <= 90 degrees, the archive's delivery region
A_WHOLE = 2 * math.pi * R * LZ                     # the whole lateral surface
EIGHTH_FROM = 0.875                                # the eighth: theta <= 90 degrees and z >= 0.875 L
A_EIGHTH = A_HALF * (1 - EIGHTH_FROM)
A_REGION = {"half": A_HALF, "whole": A_WHOLE, "eighth": A_EIGHTH, "capend": A_HALF * 0.25}

TAU_TRIGGER = float(R9.tau_median())               # 21.3865 s, the trigger's release and the archive's pulse
R_CENTRAL = float(R9.ratios()["central"])          # 3.1053


def tests():
    return R9.by_test()


TEST_ORDER = [t["test"] for t in R9.tests()]


def e_e(test):
    """The test's ejected energy E_e = r E_b (J), the archive's reference for f."""
    return R_CENTRAL * float(tests()[test]["E_b_J"])


def fourier(tau_s, radius=R):
    """alpha_r tau / a^2 with a the can radius."""
    return ALPHA_R * tau_s / radius ** 2


# ------------------------------------------------------------------------------------------------ the run lists
def _res(name, test, tau_d, geometry="half", kind="search", ref=None):
    return {"name": name, "model": "resolved", "test": test, "shape": "tri", "tau_d_s": float(tau_d),
            "geometry": geometry, "h": "central", "dE_body_J": 0.0, "kind": kind, "ref": ref}


def _lum(name, test, tau_d, h="central", dE_body=0.0):
    return {"name": name, "model": "lumped", "test": test, "shape": "tri", "tau_d_s": float(tau_d), "geometry": "half",
            "h": h, "dE_body_J": float(dE_body), "kind": "search", "ref": None}


def resolved_searches():
    """Part A4: ten new searches and the three archived references refined to the same width (D134)."""
    out = []
    for tau in (5.0, 40.0, 120.0, 360.0):
        out.append(_res(f"A4_PT_Exp1_tri{tau:g}", "M50_PT_Exp1", tau))
    for test in ("M50_ST_Exp3", "M50_PT_Exp3"):
        for tau in (10.0, 60.0):
            out.append(_res(f"A4_{test[4:]}_tri{tau:g}", test, tau))
    out.append(_res("A4_PT_Exp1_whole", "M50_PT_Exp1", TAU_TRIGGER, "whole"))
    out.append(_res("A4_PT_Exp1_eighth", "M50_PT_Exp1", TAU_TRIGGER, "eighth"))
    ref = {"M50_PT_Exp1": (0.15, 0.1625), "M50_ST_Exp3": (0.075, 0.0875), "M50_PT_Exp3": (0.025, 0.0375)}
    for test, br in ref.items():
        out.append(_res(f"A4ref_{test[4:]}_tri21", test, TAU_TRIGGER, kind="refine", ref=br))
    return out


def lumped_searches():
    """Part B4: seventy searches with the full lumped neighbour (D135)."""
    out = []
    for h in ("low", "high"):
        for t in TEST_ORDER:
            out.append(_lum(f"B4_{h}_{t[4:]}", t, TAU_TRIGGER, h=h))
    for tau in (120.0, 360.0):
        for t in TEST_ORDER:
            out.append(_lum(f"B4_tri{tau:g}_{t[4:]}", t, tau))
    for t in ("M50_PP_Exp3", "M50_ST_Exp2", "M50_PT_Exp3"):
        for d in (-2000.0, 2000.0):
            out.append(_lum(f"B4_Eb{'m' if d < 0 else 'p'}2_{t[4:]}", t, TAU_TRIGGER, dE_body=d))
    return out


def run_lists():
    return {"resolved": resolved_searches(), "lumped": lumped_searches()}


def run_lists_hash():
    s = json.dumps(run_lists(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(s.encode()).hexdigest()


# ------------------------------------------------------------------------------------------------ search rules (D134)
RES_WIDTH = 0.04          # a resolved bracket ends when hi - lo <= 4 % of its midpoint
LUM_WIDTH = 0.02          # a lumped bracket ends when hi - lo <= 2 % of its midpoint, or <= 20 J
LUM_WIDTH_J = 20.0
FIRST_STEP = 0.03         # the first step from the reduced model's value, doubled until the threshold is bracketed
MAX_RUNS = {"resolved": 12, "lumped": 40}


def key(f):
    """Fractions rounded as the archive rounds them (stage8_search.key), so that ids are stable."""
    return float(f"{float(f):.9f}")


# ------------------------------------------------------------------------------------------------ the new regions
def _clip(poly, n, c):
    """Sutherland-Hodgman: the part of a planar polygon (k x 3) where n . x >= c."""
    out = []
    k = len(poly)
    for i in range(k):
        p, q = poly[i], poly[(i + 1) % k]
        dp, dq = n @ p - c, n @ q - c
        if dp >= 0:
            out.append(p)
        if (dp >= 0) != (dq >= 0):
            out.append(p + (q - p) * dp / (dp - dq))
    return np.array(out)


def surface_weights(model, geometry):
    """Node weights of a uniform flux over a region of the lateral surface of the half model, integrated exactly: each
    lateral facet is clipped by the region's planes (theta <= 90 degrees is x >= 0 on the half model; the eighth adds
    z >= 0.875 L) and each node's hat function integrated over the clipped polygon. "half" is the archive's own rule
    (stage8_model.surface_weights, unchanged); "whole" and "eighth" are new. Returns (weights, area in the half
    model)."""
    if geometry == "half":
        import stage8_model as M8
        return M8.surface_weights(model, "half")
    planes = []
    if geometry == "eighth":
        planes = [(np.array([1.0, 0.0, 0.0]), 0.0), (np.array([0.0, 0.0, 1.0]), EIGHTH_FROM * LZ)]
    elif geometry != "whole":
        raise ValueError(geometry)
    m = model.mesh
    w = np.zeros(m.p.shape[1])
    for f in model.groups["lateral"]:
        nodes = m.facets[:, f]
        P = m.p[:, nodes].T                                   # 3 x 3, the facet's corners
        poly = P.copy()
        for n_, c_ in planes:
            if len(poly) == 0:
                break
            poly = _clip(poly, n_, c_)
        if len(poly) < 3:
            continue
        # barycentric coordinates on the facet: hat functions are linear, so each sub-triangle's integral is its
        # area times the hat functions at its centroid
        e1, e2 = P[1] - P[0], P[2] - P[0]
        M = np.array([[e1 @ e1, e1 @ e2], [e1 @ e2, e2 @ e2]])
        for i in range(1, len(poly) - 1):
            tri = np.array([poly[0], poly[i], poly[i + 1]])
            area = 0.5 * np.linalg.norm(np.cross(tri[1] - tri[0], tri[2] - tri[0]))
            g = tri.mean(axis=0) - P[0]
            l1, l2 = np.linalg.solve(M, np.array([g @ e1, g @ e2]))      # g = l1 e1 + l2 e2 on the facet
            w[nodes] += area * np.array([1.0 - l1 - l2, l1, l2])
    return w, float(w.sum())


def share_surface(model, geometry):
    w, _ = surface_weights(model, geometry)
    return w / (2.0 * w.sum())


def region_check(model, geometry):
    """V6: twice the half model's weights against the region's exact area."""
    _, a = surface_weights(model, geometry)
    exact = A_REGION[geometry]
    return {"geometry": geometry, "A_mesh_m2": 2.0 * a, "A_exact_m2": exact, "rel_diff": 2.0 * a / exact - 1.0}
