"""Stage 5 (version 1.2.0) mesh of the neighbour cell: the two-cell study's half cylinder, graded toward the line of
contact with the trigger cell (DECISIONS.md D42).

The generator is the published one (external/m50-two-cell-pilot/src/mesh_cell2.py): rings in the cross-section,
a zipper triangulation between consecutive rings, extrusion through axial layers into prisms, and the conforming
three-tetrahedra split of every prism. Three things differ, all in where the nodes sit:
  1. the rings with r >= 8.9 mm share one azimuthal distribution that is fine at the line of contact (theta = 0)
     and coarser away from it, with nodes exactly at 45 degrees (the edge of the wedge sector) and 180 degrees;
  2. the inner rings are uniform but coarser (0.9 mm against 0.55 mm), with fewer rings inside 8.2 mm;
  3. the axial layers are graded from 0.3 mm at both ends to at most 3 mm (0.2 mm and 2.5 mm before).
The outer rings are the published ones (9.0 to 10.55 mm), and the 4.0 mm ring carries the tab discs.

Cell 2 is centred on the z axis, 0 <= z <= L (z = 0 is the negative base, z = L the positive cap). Cell 1 lies
along +x and touches cell 2 along the line x = R, y = 0; the plane y = 0 is a plane of symmetry, so only y >= 0
is meshed. `refine` > 1 shrinks every spacing by that factor (V3).
"""
import math
import numpy as np
from skfem import MeshTet

R_DISC = 0.004            # m, tab weld patch: disc of 8 mm diameter at the centre of the cap and of the base (D37)
SECTOR = math.pi / 4      # half-angle of the wedge sector facing cell 1 (as the two-cell study's gap sector)
R_OUTER_FROM = 0.0089     # m, rings at or beyond this radius share the graded azimuthal distribution

INNER_RINGS_MM = [1.0, 2.0, 3.0, 4.0, 5.1, 6.2, 7.2, 8.2]
OUTER_RINGS_MM = [9.0, 9.4, 9.73, 10.0, 10.2, 10.35, 10.46, 10.55]      # the published outer rings

# azimuthal grading on the outer rings, as arc lengths on the can radius
DS_CONTACT = 0.06e-3      # m, first spacing at the line of contact
GROW_CONTACT = 1.2        # growth from the line of contact
DS_SECTOR = 0.5e-3        # m, largest spacing inside the 45 degree sector (the published spacing)
GROW_FAR = 1.1            # growth beyond 45 degrees
DS_FAR = 1.2e-3           # m, largest spacing on the far side
DS_INNER = 0.9e-3         # m, uniform spacing on the inner rings
# axial layers
DZ_FIRST, DZ_GROW, DZ_MAX = 0.3e-3, 1.3, 3.0e-3


def radial_rings(R, refine=1.0):
    base = [0.0] + [x * 1e-3 for x in INNER_RINGS_MM + OUTER_RINGS_MM]
    base[-1] = R
    n = max(1, int(math.ceil(refine - 1e-9)))
    out = []
    for a, b in zip(base[:-1], base[1:]):
        for k in range(1, n + 1):
            out.append(a + (b - a) * k / n)
    return np.array(out)


def _graded(length, ds0, grow, dsmax):
    """Spacings that start at ds0, grow geometrically to dsmax and then stay uniform, summing exactly to length."""
    sp = []
    d = ds0
    while sum(sp) + d < length and d < dsmax:
        sp.append(d)
        d *= grow
    rest = length - sum(sp)
    n = max(1, int(math.ceil(rest / dsmax - 1e-9)))
    sp += [rest / n] * n
    return np.array(sp)


def outer_angles(R, refine=1.0):
    """The azimuthal node angles shared by every outer ring: 0 at the line of contact to pi, with nodes at pi/4."""
    g1 = _graded(R * SECTOR, DS_CONTACT / refine, GROW_CONTACT ** (1.0 / refine), DS_SECTOR / refine)
    g2 = _graded(R * (math.pi - SECTOR), DS_SECTOR / refine, GROW_FAR ** (1.0 / refine), DS_FAR / refine)
    th = np.concatenate([[0.0], np.cumsum(g1) / R, SECTOR + np.cumsum(g2) / R])
    th[np.argmin(np.abs(th - SECTOR))] = SECTOR
    th[-1] = math.pi
    return th


def inner_angles(r, refine=1.0):
    n = 4 * int(math.ceil(math.pi * r / (4 * DS_INNER / refine)))
    return np.linspace(0.0, math.pi, max(4, n) + 1)


def axial_layers(Lz, refine=1.0):
    first, dmax, growth = DZ_FIRST / refine, DZ_MAX / refine, DZ_GROW ** (1.0 / refine)
    half = Lz / 2
    z = [0.0]
    d = first
    while z[-1] + d < half - 0.5 * min(d, dmax):
        z.append(z[-1] + d)
        d = min(d * growth, dmax)
    z = np.array(z + [half])
    upper = Lz - z[::-1][1:]
    return np.concatenate([z, upper])


def build_mesh(R, Lz, refine=1.0):
    rings = radial_rings(R, refine)
    th_out = outer_angles(R, refine)
    pts2 = [(0.0, 0.0)]
    ring_nodes = []
    for r in rings:
        th = th_out if r >= R_OUTER_FROM - 1e-12 else inner_angles(r, refine)
        idx = list(range(len(pts2), len(pts2) + len(th)))
        pts2 += [(r * math.cos(t), r * math.sin(t)) for t in th]
        ring_nodes.append((idx, th))
    pts2 = np.array(pts2)
    tris = []
    idx0, _ = ring_nodes[0]
    for j in range(len(idx0) - 1):
        tris.append((0, idx0[j], idx0[j + 1]))
    for (ia, ta), (ib, tb) in zip(ring_nodes[:-1], ring_nodes[1:]):
        i = j = 0
        m, n = len(ia) - 1, len(ib) - 1
        while i < m or j < n:
            if i == m:
                tris.append((ia[i], ib[j], ib[j + 1])); j += 1
            elif j == n:
                tris.append((ia[i], ib[j], ia[i + 1])); i += 1
            elif ta[i + 1] < tb[j + 1] - 1e-12:
                tris.append((ia[i], ib[j], ia[i + 1])); i += 1
            else:
                tris.append((ia[i], ib[j], ib[j + 1])); j += 1
    tris = np.array(tris)
    z = axial_layers(Lz, refine)
    n2, nz = len(pts2), len(z)
    p = np.zeros((3, n2 * nz))
    for k in range(nz):
        p[0, k * n2:(k + 1) * n2] = pts2[:, 0]
        p[1, k * n2:(k + 1) * n2] = pts2[:, 1]
        p[2, k * n2:(k + 1) * n2] = z[k]
    tets = []
    for tri in tris:
        a, b, c = sorted(tri)
        for k in range(nz - 1):
            A0, B0, C0 = a + k * n2, b + k * n2, c + k * n2
            A1, B1, C1 = A0 + n2, B0 + n2, C0 + n2
            tets += [(A0, B0, C0, C1), (A0, B0, B1, C1), (A0, A1, B1, C1)]
    t = np.array(tets).T
    P = p[:, t]
    vol = np.einsum("ij,ij->j", np.cross((P[:, 1] - P[:, 0]).T, (P[:, 2] - P[:, 0]).T).T, P[:, 3] - P[:, 0])
    neg = vol < 0
    t[[1, 2]] = np.where(neg, t[[2, 1]], t[[1, 2]])
    mesh = MeshTet(p, t)
    info = {"n_rings": len(rings), "n_layers": nz, "n_nodes_2d": n2, "n_tris_2d": len(tris),
            "n_outer_segments": len(th_out) - 1, "smallest_outer_spacing_mm": float(1e3 * R * np.diff(th_out).min()),
            "min_abs_vol": float(np.abs(vol).min()), "n_nodes": int(p.shape[1])}
    return mesh, info


def classify_facets(mesh, R, Lz):
    """Boundary facet groups of the half model (indices into mesh.facets)."""
    bf = mesh.boundary_facets()
    mid = mesh.p[:, mesh.facets[:, bf]].mean(axis=1)
    x, y, z = mid
    r = np.hypot(x, y)
    th = np.arctan2(y, x)
    tol = 1e-9
    top = np.abs(z - Lz) < tol
    bottom = np.abs(z) < tol
    sym = (np.abs(y) < tol) & ~top & ~bottom
    lateral = ~top & ~bottom & ~sym
    groups = {
        "top": bf[top], "bottom": bf[bottom], "symmetry": bf[sym], "lateral": bf[lateral],
        "top_disc": bf[top & (r < R_DISC)],
        "bottom_disc": bf[bottom & (r < R_DISC)],
        "sector": bf[lateral & (th < SECTOR)],
        "lateral_nonsector": bf[lateral & (th >= SECTOR)],
    }
    groups["outer"] = np.concatenate([groups["top"], groups["bottom"], groups["lateral"]])
    groups["conv"] = np.concatenate([groups["top"], groups["bottom"], groups["lateral_nonsector"]])
    return groups
