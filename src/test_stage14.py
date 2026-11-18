"""Stage 14 tests of the ray tracing on configurations whose answers are known (V4, D157).

Run: python3 src/test_stage14.py  (prints each case, its exact value, the Monte Carlo value and the
allowance of four standard errors, and fails if any case lies outside it). Written and run before the
predictions were pushed: it tests the code on known configurations and computes nothing for the rig.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stage14_view as v  # noqa: E402

N = 2_000_000


def se(p, n):
    return math.sqrt(max(p * (1 - p), 1e-12) / n)


def case_disc(rng):
    """A point on the axis of a disc of radius R at height h sees it in (1 - h/sqrt(h^2+R^2))/2 of
    all directions (the solid angle of a disc over 4 pi)."""
    out = []
    for h in (0.2 * v.R, v.R, 3.0 * v.R):
        cells = v.cells_default(trigger=False)
        o = np.repeat(np.array([[0.0, 0.0, v.L + h]]), N, axis=0)
        d = v.sphere_dirs(N, rng)
        code, _ = v.first_hit(o, d, cells)
        mc = (code == v.NB_ENDL).mean()
        exact = 0.5 * (1.0 - h / math.sqrt(h * h + v.R * v.R))
        out.append((f"disc seen from its axis, h = {h / v.R:.1f} R", exact, mc, 4 * se(exact, N)))
    return out


def case_semi_infinite(rng):
    """A point in the end plane of a long cylinder, at a distance rho from its axis, sees its lateral
    surface in arcsin(R/rho)/(2 pi) of all directions (half the infinite cylinder's 4 arcsin(R/rho))."""
    out = []
    length = 2000.0 * v.R
    for rho in (1.05 * v.R, 2.0 * v.R, 5.0 * v.R):
        cells = v.cells_default(trigger=False, length=length)
        o = np.repeat(np.array([[rho, 0.0, length]]), N, axis=0)
        d = v.sphere_dirs(N, rng)
        code, _ = v.first_hit(o, d, cells)
        mc = (code == v.NB_LAT).mean()
        exact = math.asin(v.R / rho) / (2.0 * math.pi)
        # the finite length L' = 2000 R removes about rho/(2 L') of it; allowance includes that
        tol = 4 * se(exact, N) + exact * rho / length
        out.append((f"long cylinder from its end plane, rho = {rho / v.R:.2f} R", exact, mc, tol))
    return out


def case_two_cylinders(rng):
    """Two touching cylinders, long: the view factor from one whole lateral surface to the other is
    (pi/2 - 1)/pi = 0.1817 (crossed strings), so from the facing half it is twice that, 0.3634."""
    length = 400.0 * v.R
    cells = v.cells_default(trigger=True, length=length)
    res = v.facing_view(N, rng, cells)
    exact = 2.0 * (math.pi / 2.0 - 1.0) / math.pi
    tol = 4 * se(exact, N) + exact * 4.0 * v.R / length
    return [("touching cylinders, facing half to the other's lateral surface", exact, res["trigger"], tol)]


def main():
    rng = np.random.default_rng(14)
    rows = case_disc(rng) + case_semi_infinite(rng) + case_two_cylinders(rng)
    bad = 0
    for name, exact, mc, tol in rows:
        ok = abs(mc - exact) <= tol
        bad += not ok
        print(f"{'ok  ' if ok else 'FAIL'} {name}: exact {exact:.6f}, ray tracing {mc:.6f}, allowance {tol:.6f}")
    if bad:
        raise SystemExit(f"{bad} case(s) outside the allowance")
    print("all cases within the allowance")


if __name__ == "__main__":
    main()
