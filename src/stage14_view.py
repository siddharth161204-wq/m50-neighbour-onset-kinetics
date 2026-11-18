"""Stage 14: ray tracing for the radiation path (A1) and the rate bounds (A1, A2).

Geometry (DECISIONS D150, D152): two cylinders of radius R and length L, axes along z from 0 to L.
The neighbour's axis passes through (0, 0), the trigger's through (0, 2R): they touch along the line
x = 0, y = R. The facing half is the neighbour's lateral surface with y >= 0 (within 90 degrees of
the line of contact). Every surface is opaque and black for these counts: a ray ends at the first
surface it meets (lateral surfaces and end discs of both cells).

Functions
  first_hit(o, d, cells)        index of the first surface each ray meets (or -1) and its point
  point_fraction(p, n, rng)     the share of an isotropic emitter's directions at p whose first hit
                                is the facing half (w in D152)
  facing_view(n, rng)           cosine-weighted view from the facing half: the shares that end on
                                the trigger, that leave beyond z = L, beyond z = 0, and the rest
Everything is plain numpy; the random generator is passed in so that every run can be repeated.
"""
import math

import numpy as np

R = 0.01055
L = 0.0701

# Surface codes
NONE = -1
NB_LAT, NB_END0, NB_ENDL = 0, 1, 2
TR_LAT, TR_END0, TR_ENDL = 3, 4, 5


def cells_default(trigger=True, length=L, radius=R):
    """List of (cx, cy, codes) for the cells present."""
    cs = [(0.0, 0.0, (NB_LAT, NB_END0, NB_ENDL))]
    if trigger:
        cs.append((0.0, 2.0 * radius, (TR_LAT, TR_END0, TR_ENDL)))
    return cs, length, radius


def _lateral(o, d, cx, cy, radius, length, eps):
    ox, oy, oz = o[:, 0] - cx, o[:, 1] - cy, o[:, 2]
    dx, dy, dz = d[:, 0], d[:, 1], d[:, 2]
    a = dx * dx + dy * dy
    b = 2.0 * (ox * dx + oy * dy)
    c = ox * ox + oy * oy - radius * radius
    disc = b * b - 4.0 * a * c
    t = np.full(o.shape[0], np.inf)
    ok = (a > 1e-300) & (disc >= 0.0)
    sq = np.sqrt(np.where(ok, disc, 0.0))
    with np.errstate(divide="ignore", invalid="ignore"):
        t1 = np.where(ok, (-b - sq) / (2.0 * a), np.inf)
        t2 = np.where(ok, (-b + sq) / (2.0 * a), np.inf)
    for tt in (t1, t2):
        z = oz + tt * dz
        good = ok & (tt > eps) & (z >= 0.0) & (z <= length) & (tt < t)
        t = np.where(good, tt, t)
    return t


def _disc(o, d, cx, cy, radius, z0, eps):
    dz = d[:, 2]
    with np.errstate(divide="ignore", invalid="ignore"):
        tt = np.where(np.abs(dz) > 1e-300, (z0 - o[:, 2]) / dz, np.inf)
    x = o[:, 0] + tt * d[:, 0] - cx
    y = o[:, 1] + tt * d[:, 1] - cy
    good = (tt > eps) & (x * x + y * y <= radius * radius)
    return np.where(good, tt, np.inf)


def first_hit(o, d, cells=None, eps=1e-12):
    """For rays o + t d (t > eps), the code of the first surface met and the hit points."""
    if cells is None:
        cells = cells_default()
    cs, length, radius = cells
    n = o.shape[0]
    best = np.full(n, np.inf)
    code = np.full(n, NONE, dtype=int)
    for cx, cy, (c_lat, c_e0, c_eL) in cs:
        for c, t in ((c_lat, _lateral(o, d, cx, cy, radius, length, eps)),
                     (c_e0, _disc(o, d, cx, cy, radius, 0.0, eps)),
                     (c_eL, _disc(o, d, cx, cy, radius, length, eps))):
            take = t < best
            best = np.where(take, t, best)
            code = np.where(take, c, code)
    pts = o + np.where(np.isfinite(best), best, 0.0)[:, None] * d
    return code, pts


def sphere_dirs(n, rng):
    v = rng.normal(size=(n, 3))
    return v / np.linalg.norm(v, axis=1)[:, None]


def point_fraction(p, n, rng, cells=None, facing_only=True):
    """Share of isotropic directions from point p whose first hit is the neighbour's lateral surface
    (with y >= 0 when facing_only)."""
    d = sphere_dirs(n, rng)
    o = np.repeat(np.asarray(p, float)[None, :], n, axis=0)
    code, pts = first_hit(o, d, cells)
    hit = code == NB_LAT
    if facing_only:
        hit &= pts[:, 1] >= 0.0
    return hit.mean()


def facing_points(n, rng, radius=R, length=L):
    """Points uniform on the facing half (theta in [-90, 90] degrees from +y), with outward normals."""
    th = rng.uniform(-0.5 * math.pi, 0.5 * math.pi, n)
    z = rng.uniform(0.0, length, n)
    nrm = np.stack([np.sin(th), np.cos(th), np.zeros(n)], axis=1)
    pts = nrm * radius
    pts[:, 2] = z
    return pts, nrm


def cosine_dirs(nrm, rng):
    """Cosine-weighted directions about each normal."""
    n = nrm.shape[0]
    u1, u2 = rng.random(n), rng.random(n)
    r = np.sqrt(u1)
    phi = 2.0 * math.pi * u2
    lx, ly, lz = r * np.cos(phi), r * np.sin(phi), np.sqrt(1.0 - u1)
    # orthonormal frame (t1, t2, nrm)
    a = np.where(np.abs(nrm[:, 2:3]) < 0.9, np.array([[0.0, 0.0, 1.0]]), np.array([[1.0, 0.0, 0.0]]))
    t1 = np.cross(nrm, a)
    t1 /= np.linalg.norm(t1, axis=1)[:, None]
    t2 = np.cross(nrm, t1)
    return lx[:, None] * t1 + ly[:, None] * t2 + lz[:, None] * nrm


def facing_view(n, rng, cells=None):
    """Cosine-weighted view from the facing half: shares ending on the trigger, leaving with z > L,
    leaving with z < 0, and ending elsewhere (the neighbour itself cannot be met: it is convex)."""
    if cells is None:
        cells = cells_default()
    _, length, radius = cells
    pts, nrm = facing_points(n, rng, radius, length)
    d = cosine_dirs(nrm, rng)
    code, _ = first_hit(pts, d, cells, eps=1e-9)
    trig = np.isin(code, (TR_LAT, TR_END0, TR_ENDL))
    free = code == NONE
    beyond_L = free & (d[:, 2] > 0.0)
    beyond_0 = free & (d[:, 2] < 0.0)
    other = ~(trig | free)
    return dict(trigger=trig.mean(), beyond_L=beyond_L.mean(), beyond_0=beyond_0.mean(),
                free_sideways=(free & (d[:, 2] == 0.0)).mean(), other=other.mean(), n=n)
