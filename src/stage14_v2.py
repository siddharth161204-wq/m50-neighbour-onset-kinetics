"""Stage 14, check V2 (DECISIONS D156): every bound recomputed by separate code from the inputs table alone.

Imports nothing of the study's. It reads results/stage14_inputs.csv, traces its own rays with its own
intersection code, direction samplers and seeds, recomputes every bound, and compares with
results/stage14_bounds.csv and results/stage14_raytrace.json. Writes results/stage14_v2.json.
"""
import csv
import json
import math
import os

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def inputs():
    with open(os.path.join(ROOT, "results", "stage14_inputs.csv"), newline="") as fh:
        rows = {r["key"]: r for r in csv.DictReader(fh)}
    return lambda k, f="value": float(rows[k][f])


class Scene:
    """Two cylinders of radius a and length ell along z; neighbour at (0, 0), trigger at (0, 2a)."""

    def __init__(self, a, ell, trigger=True):
        self.a, self.ell = a, ell
        self.axes = [(0.0, 0.0)] + ([(0.0, 2.0 * a)] if trigger else [])

    def trace(self, o, d):
        """Returns (cell index or -1, kind 0 lateral / 1 end, hit y) of the first surface met."""
        n = len(o)
        tbest = np.full(n, np.inf)
        cell = np.full(n, -1)
        kind = np.full(n, -1)
        a, ell = self.a, self.ell
        for ci, (cx, cy) in enumerate(self.axes):
            px, py = o[:, 0] - cx, o[:, 1] - cy
            # lateral: |p_perp + t d_perp| = a, written with the projection of p on d_perp
            dd = d[:, 0] ** 2 + d[:, 1] ** 2
            pd = px * d[:, 0] + py * d[:, 1]
            pp = px * px + py * py
            with np.errstate(divide="ignore", invalid="ignore"):
                tc = -pd / dd                              # closest approach in projection
                m2 = pp - pd * pd / dd                     # squared distance of closest approach
                half = np.sqrt(np.maximum(a * a - m2, 0.0) / dd)
            ok = (dd > 0) & (m2 <= a * a)
            for t in (tc - half, tc + half):
                z = o[:, 2] + t * d[:, 2]
                good = ok & (t > 1e-12) & (z >= 0) & (z <= ell) & (t < tbest)
                tbest = np.where(good, t, tbest)
                cell = np.where(good, ci, cell)
                kind = np.where(good, 0, kind)
            for z0 in (0.0, ell):
                with np.errstate(divide="ignore", invalid="ignore"):
                    t = (z0 - o[:, 2]) / d[:, 2]
                hx, hy = px + t * d[:, 0], py + t * d[:, 1]
                good = np.isfinite(t) & (t > 1e-12) & (hx * hx + hy * hy <= a * a) & (t < tbest)
                tbest = np.where(good, t, tbest)
                cell = np.where(good, ci, cell)
                kind = np.where(good, 1, kind)
        hy = o[:, 1] + np.where(np.isfinite(tbest), tbest, 0.0) * d[:, 1]
        return cell, kind, hy


def iso(n, rng):
    mu = rng.uniform(-1.0, 1.0, n)
    ph = rng.uniform(0.0, 2.0 * math.pi, n)
    s = np.sqrt(1.0 - mu * mu)
    return np.stack([s * np.cos(ph), s * np.sin(ph), mu], axis=1)


def w_point(scene, p, n, rng):
    d = iso(n, rng)
    o = np.repeat(np.asarray(p, float)[None, :], n, axis=0)
    cell, kind, hy = scene.trace(o, d)
    return float(((cell == 0) & (kind == 0) & (hy >= 0.0)).mean())


def facing(scene, n, rng):
    a, ell = scene.a, scene.ell
    th = rng.uniform(-math.pi / 2, math.pi / 2, n)
    z = rng.uniform(0, ell, n)
    nr = np.stack([np.sin(th), np.cos(th), np.zeros(n)], axis=1)
    o = nr * a
    o[:, 2] = z
    # cosine-weighted about the normal: local frame (tangent along theta, axis z, normal)
    u, ph = rng.random(n), rng.uniform(0, 2 * math.pi, n)
    sr = np.sqrt(u)
    tang = np.stack([np.cos(th), -np.sin(th), np.zeros(n)], axis=1)
    ez = np.array([0.0, 0.0, 1.0])
    d = (sr * np.cos(ph))[:, None] * tang + (sr * np.sin(ph))[:, None] * ez + np.sqrt(1 - u)[:, None] * nr
    cell, kind, hy = scene.trace(o + 1e-10 * nr, d)
    trig = (cell == 1).mean()
    free = cell == -1
    return float(trig), float((free & (d[:, 2] > 0)).mean())


def cone(axis, beta, n, rng):
    if beta == 0:
        return np.repeat(np.asarray(axis, float)[None, :], n, axis=0)
    c = rng.uniform(math.cos(math.radians(beta)), 1.0, n)
    s = np.sqrt(1 - c * c)
    ph = rng.uniform(0, 2 * math.pi, n)
    ax = np.asarray(axis, float)
    e1 = np.array([0.0, 0.0, 1.0])                 # the axis lies in the x-y plane for a breach
    e2 = np.cross(ax, e1)
    return (s * np.cos(ph))[:, None] * e1 + (s * np.sin(ph))[:, None] * e2 + c[:, None] * ax


def cb(Re, Pr):
    g = 0.62 * math.sqrt(Re) * Pr ** (1 / 3) / (1 + (0.4 / Pr) ** (2 / 3)) ** 0.25
    a = 0.3 + g * (1 + (Re / 2.82e5) ** 0.625) ** 0.8
    if 4.0e4 < Re < 4.0e5:
        return max(1.2 * a, 0.3 + g * (1 + math.sqrt(Re / 2.82e5)))
    return a


def main():
    q = inputs()
    a, ell = q("R_cell"), q("L_cell")
    Af = math.pi * a * ell
    E_avail = q("db_Eej_max") + q("vendra_Qt_max")
    E_glob = q("db_Etotal_max") + q("vendra_Qt_max")
    sig, Tf, T0 = q("sigma"), q("T_flame_max") + 273.15, q("T0") + 273.15
    scene = Scene(a, ell)

    # w over the same grid of positions, own seed and sampler
    rng = np.random.default_rng(1401)
    N = 1_000_000
    pts = []
    for k in (0.0, 0.5, 1.0, 2.0, 5.0, 10.0):
        pts.append(("axis", (0.0, 2 * a, ell + max(k * a, 1e-6 * a))))
    for h in (0.01, 0.1, 1.0):
        for r in (0.0, 0.25, 0.5, 0.75, 1.0):
            for psi in ((0,) if r == 0 else range(0, 360, 30)):
                s = math.radians(psi)
                pts.append(("column", (r * a * math.sin(s), 2 * a - r * a * math.cos(s), ell + h * a)))
    for th in range(0, 91, 15):
        for dl in (0.3, 0.1, 0.03, 0.01):
            t = math.radians(th)
            pts.append(("edge", ((a + dl * a) * math.sin(t), (a + dl * a) * math.cos(t), ell + 1e-6 * a)))
    ws = [(part, w_point(scene, p, N, rng)) for part, p in pts]
    wmax = {part: max(w for pp, w in ws if pp == part) for part in ("axis", "column", "edge")}
    w_sup = max(0.25, max(w for _, w in ws))

    rng = np.random.default_rng(1402)
    F_trig, F_end = facing(scene, 2_000_000, rng)

    # breach shares
    rng = np.random.default_rng(1403)
    s_by_phi = {}
    for phi in range(0, 181, 5):
        if phi == 0:
            s_by_phi[phi] = 1.0
            continue
        ph = math.radians(phi)
        nr = np.array([math.sin(ph), -math.cos(ph), 0.0])
        sp = np.array([a * math.sin(ph), 2 * a - a * math.cos(ph), 0.5 * ell]) + 1e-9 * nr
        best = 0.0
        for b in (0, 5, 10, 15, 30, 45, 60, 90):
            n = 1 if b == 0 else 200_000
            d = cone(nr, b, n, rng)
            cell, kind, hy = scene.trace(np.repeat(sp[None, :], n, axis=0), d)
            best = max(best, float(((cell == 0) & (kind == 0) & (hy >= 0)).mean()))
        s_by_phi[phi] = best

    # convection
    Tfilm = 0.5 * (Tf + T0)
    fr = (Tfilm - 1000.0) / 100.0
    air = {k: q(f"air_1000K_{k}") * (1 - fr) + q(f"air_1100K_{k}") * fr for k in ("nu", "k", "Pr")}
    h2 = {k: q(f"h2_1000K_{k}") for k in ("nu", "k", "Pr")}
    D = 2 * a
    hs = {nm: cb(q("u_vent_max") * D / p["nu"], p["Pr"]) * p["k"] / D for nm, p in (("air", air), ("hydrogen", h2))}
    hmax = max(hs.values())

    tmax = q("t_flame_max")
    P1 = sig * Tf ** 4 * Af * F_end
    P2 = (hmax * (Tf - T0) + sig * Tf ** 4 * (1 - F_trig)) * Af
    mine = {}
    for win in (21.39, 120.0, 240.0, 360.0, "total"):
        t = tmax if win == "total" else win
        mine[("A1", win)] = min(w_sup * E_avail, P1 * t)
        mine[("A2", win)] = min(E_avail, P2 * t)
        mine[("A3", win)] = max(s_by_phi.values()) * E_avail
        mine[("A4", win)] = E_avail
        mine[("A6", win)] = q("db_stored_energy")

    # compare
    with open(os.path.join(ROOT, "results", "stage14_bounds.csv"), newline="") as fh:
        theirs = {(r["path"], (float(r["window_s"]) if r["window_s"] != "total" else "total")): r for r in csv.DictReader(fh)}
    rt = json.load(open(os.path.join(ROOT, "results", "stage14_raytrace.json")))
    comp = []
    ok_all = True
    se_end = math.sqrt(F_end * (1 - F_end) / 2e6) + math.sqrt(rt["facing_view"]["beyond_L"] * (1 - rt["facing_view"]["beyond_L"]) / 4e6)
    se_trig = math.sqrt(F_trig * (1 - F_trig) / 2e6) + math.sqrt(rt["facing_view"]["trigger"] * (1 - rt["facing_view"]["trigger"]) / 4e6)
    for key, mv in mine.items():
        r = theirs[key]
        tv = float(r["upper_J"])
        t = tmax if key[1] == "total" else key[1]
        tol = 1e-9 * max(abs(tv), 1.0)
        if key[0] == "A1" and min(mv, tv) < w_sup * E_avail * (1 - 1e-12):
            # the rate term binds in at least one of the two: its share F_end carries the ray tracing's error
            tol += 4 * se_end * sig * Tf ** 4 * Af * t
        if key[0] == "A2" and min(mv, tv) < E_avail * (1 - 1e-12):
            tol += 4 * se_trig * sig * Tf ** 4 * Af * t
        ok = abs(mv - tv) <= tol
        ok_all &= ok
        comp.append(dict(path=key[0], window=str(key[1]), study_J=tv, v2_J=mv, tolerance_J=tol, agree=ok))
    shares = dict(
        w_sup=dict(study=rt["w_sup"], v2=w_sup),
        w_max_axis=dict(study=rt["w_max_axis"]["w"], v2=wmax["axis"]),
        w_max_column=dict(study=rt["w_max_column"]["w"], v2=wmax["column"]),
        w_max_edge=dict(study=rt["w_max_edge"]["w"], v2=wmax["edge"]),
        F_end=dict(study=rt["facing_view"]["beyond_L"], v2=F_end),
        F_trig=dict(study=rt["facing_view"]["trigger"], v2=F_trig),
        h_max=dict(v2=hmax, by_gas=hs),
        breach_s_max=dict(v2={str(k): v for k, v in s_by_phi.items()},
                          study={str(r["phi_deg"]): r["s_max"] for r in rt["breach"]}),
        A5=dict(v2="not determinable", cap_J=E_glob),
    )
    # breach shares: agree within four standard errors of the two estimates
    br_ok = True
    for r in rt["breach"]:
        a1, b1 = r["s_max"], s_by_phi[r["phi_deg"]]
        tol = 4 * (math.sqrt(a1 * (1 - a1) / 1e6) + math.sqrt(b1 * (1 - b1) / 2e5)) + 1e-12
        if abs(a1 - b1) > tol:
            br_ok = False
    out = dict(all_bounds_agree=ok_all, breach_shares_agree=br_ok, comparisons=comp, shares=shares)
    with open(os.path.join(ROOT, "results", "stage14_v2.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps(dict(all_bounds_agree=ok_all, breach_shares_agree=br_ok,
                          shares={k: v for k, v in shares.items() if k not in ("breach_s_max",)}), indent=1, default=str)[:2500])


if __name__ == "__main__":
    main()
