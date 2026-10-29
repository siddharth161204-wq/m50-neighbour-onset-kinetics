"""Stage 9: the searches for f_t and f_max of one test, criterion and configuration (DECISIONS.md D91 and D92).

Points are fractions already run, each with what the search reads from its run: the crossing time t_c (None where
the criterion is not met within 900 s) for f_t, the peak (C) of the thermocouple node, or of the lumped neighbour,
over the whole run for f_max. Every function here is pure: it returns the search's state, with the next fraction to
run ("searching") or its result. Fractions are kept rounded to 12 decimals (stage8_search.key).

f_t (A2, D91): the fraction at which the crossing comes at the measured time t_m.
  1. The grid (A1's fractions above f*_hi, in order) is read up to its first fraction whose crossing comes before
     t_m (hi0), on the grid's monotone part: the fractions from the first up to the last before a pair in which the
     crossing comes later at the larger fraction (or not at all), D91 (2).
  2. Bisection between f*_lo and hi0 on whether the crossing comes before t_m, until the bracket is at most 0.005
     wide or a run's crossing (hi0's, then each midpoint's) lies within 10 s of t_m.
  Results: "matched" (a run within 10 s; f_t is its fraction), "bracketed" (the width reached with both ends
  crossing, one at or after t_m and one before; f_t interpolated linearly in t_c between them), "threshold" (the
  width reached with the lower end not crossing at all: the bracket holds the threshold, and no run reproduces t_m),
  "early" (f* is 0 and the crossing at f = 0 already comes before t_m by more than 10 s: no fraction reproduces it),
  "above grid" (no grid fraction crosses before t_m), "not monotone" (the grid's monotone part holds none that does),
  "no crossing" (f* lies above 1).
f_max (A3, D92): the fraction at which the node's peak equals the measured maximum M.
  From f = 0: "zero" if the peak there is at least M (the overshoot recorded); "matched" if it is within 5 K below M;
  otherwise bisection between 0 and the range's end f_up (f*_lo of the configuration's criterion) until the bracket
  is at most 0.005 wide or a peak lies within 5 K of M; "bracketed" (f_max interpolated linearly in the peak). If the
  peak at f_up is still more than 5 K below M, the search goes on by bisection on (f_up, 1], its runs not stopped at
  255.7 C (the extension, D92 (4)), and its result is flagged as extended; the exploratory search is that bisection
  from 0 (f_up = 0). Its upper end, 1, is run only if every midpoint falls short: "above 1" if its peak is short too.
  Where a run takes hours, the midpoints of the bracket's two halves are listed beside the next one ("speculative",
  D96 (1)): they do not change the bisection's path, only how soon its next point is at hand.
"""
import math

KEYND = 12


def key(f):
    return round(float(f), KEYND)


def _mid(lo, hi):
    return key(0.5 * (lo + hi))


def monotone_part(grid, tc):
    """The grid's fractions up to the last before the first pair in which the crossing does not come earlier or at the
    same time at the larger fraction (a crossing lost counts as later), and every such pair. tc: {f: t_c or None}."""
    pairs = []
    end = len(grid)
    for k in range(len(grid) - 1):
        a, b = grid[k], grid[k + 1]
        if a not in tc or b not in tc:
            break
        ta, tb = tc[a], tc[b]
        late = (tb is None and ta is not None) or (ta is not None and tb is not None and tb > ta + 1e-9)
        if late:
            pairs.append((a, b))
            if end == len(grid):
                end = k + 1
    return grid[:end], pairs


def interp_t(lo, t_lo, hi, t_hi, t_m):
    """The fraction at which the crossing comes at t_m, linear in t_c between (lo, t_lo) and (hi, t_hi)."""
    if t_hi == t_lo:
        return hi
    return lo + (t_m - t_lo) * (hi - lo) / (t_hi - t_lo)


def sensitivity(tc, f0):
    """dt_c/df (s per unit f) from the two crossing runs nearest f0 (D91 (4)), with the two fractions."""
    xs = sorted((abs(f - f0), f) for f, t in tc.items() if t is not None)
    if len(xs) < 2:
        return None
    a, b = sorted([xs[0][1], xs[1][1]])
    return {"f_a": a, "f_b": b, "dtc_df_s": (tc[b] - tc[a]) / (b - a)}


def ft_state(t_m, fs, grid, tc, tol_s=10.0, width=0.005):
    """The state of the f_t search (A2). fs: f* of the configuration ({"status", "lo", "hi"}); grid: A1's fractions;
    tc: {f: t_c or None} for the fractions run (f = 0 included where known)."""
    tc = {key(f): v for f, v in tc.items()}
    base = {"t_m": t_m, "fs": fs}
    if fs["status"] == "above":
        return dict(base, status="no crossing", next=None)
    if fs["status"] not in ("zero", "bracket"):
        return dict(base, status="waiting", next=None)
    lo0 = key(fs["lo"])
    # 1. the grid, in order, up to the first fraction whose crossing comes before t_m
    hi0 = None
    seen = []
    for g in grid:
        if g not in tc:
            return dict(base, status="searching", next=g, stage="grid")
        seen.append(g)
        part, pairs = monotone_part(seen, tc)
        if pairs:
            return dict(base, status="not monotone", next=None, pairs=pairs, grid_read=seen)
        if tc[g] is not None and tc[g] < t_m:
            hi0 = g
            break
    if hi0 is None:
        return dict(base, status="above grid", next=None, grid_read=seen)
    if hi0 <= lo0:                               # f* is 0 and the grid's first fraction, 0, already crosses before t_m
        t0 = tc[hi0]
        if abs(t0 - t_m) <= tol_s:
            return dict(base, status="matched", next=None, f_t=hi0, lo=lo0, hi=hi0, t_lo=t0, t_hi=t0, f_run=hi0,
                        t_run=t0, runs=[], grid_read=seen)
        return dict(base, status="early", next=None, lo=lo0, hi=hi0, t_hi=t0, grid_read=seen)
    # 2. the bisection
    lo, hi = lo0, hi0
    runs = []
    if abs(tc[hi] - t_m) <= tol_s:
        return _ft_out(base, "matched", lo, hi, tc, t_m, hi, runs, seen)
    while True:
        if hi - lo <= width + 1e-12:
            st = "bracketed" if tc.get(lo) is not None else "threshold"
            return _ft_out(base, st, lo, hi, tc, t_m, None, runs, seen)
        m = _mid(lo, hi)
        if m not in tc:
            return dict(base, status="searching", next=m, stage="bisection", lo=lo, hi=hi, runs=runs)
        runs.append(m)
        t = tc[m]
        if t is not None and abs(t - t_m) <= tol_s:
            if t < t_m:
                hi = m
            else:
                lo = m
            return _ft_out(base, "matched", lo, hi, tc, t_m, m, runs, seen)
        if t is not None and t < t_m:
            hi = m
        else:
            lo = m


def _ft_out(base, status, lo, hi, tc, t_m, f_run, runs, seen):
    t_lo, t_hi = tc.get(lo), tc.get(hi)
    out = dict(base, status=status, next=None, lo=lo, hi=hi, t_lo=t_lo, t_hi=t_hi, runs=runs, grid_read=seen)
    if status == "matched":
        out.update(f_t=f_run, f_run=f_run, t_run=tc[f_run])
    elif status == "bracketed":
        out.update(f_t=interp_t(lo, t_lo, hi, t_hi, t_m))
    else:
        out.update(f_t=None)
    if out.get("f_t") is not None:
        out["sensitivity"] = sensitivity(tc, out["f_t"])
    else:
        out["sensitivity"] = sensitivity(tc, hi)
    return out


def interp_p(lo, p_lo, hi, p_hi, M):
    if p_hi == p_lo:
        return hi
    return lo + (M - p_lo) * (hi - lo) / (p_hi - p_lo)


def fmax_state(M, f_up, pk, tol_k=5.0, width=0.005, f_end=1.0):
    """The state of the f_max search (A3). M: the measured maximum (C); f_up: the registered range's end, f*_lo of
    the configuration's criterion (0 for the exploratory search, which starts above 0 at once; None while unknown);
    pk: {f: the node's peak (C) over the whole run} for the fractions run.
    Within (0, f_up] the bisection has both ends run; above it (the extension, and the exploratory search) it is a
    bisection on (f_up, 1] whose upper end, 1, is run only if every midpoint falls short (D92 (3) and (4))."""
    pk = {key(f): v for f, v in pk.items()}
    base = {"M": M, "f_up": f_up}
    if 0.0 not in pk:
        return dict(base, status="searching", next=0.0, stage="zero")
    p0 = pk[0.0]
    if p0 >= M:
        return dict(base, status="zero", next=None, f_max=0.0, lo=0.0, hi=0.0, overshoot_K=p0 - M, runs=[],
                    extended=False)
    if M - p0 <= tol_k:
        return dict(base, status="matched", next=None, f_max=0.0, lo=0.0, hi=0.0, f_run=0.0, p_run=p0, runs=[],
                    extended=False)
    if f_up is None:
        return dict(base, status="waiting", next=None)
    f_up = key(f_up)
    runs = []
    if f_up > 0.0:
        if f_up not in pk:
            return dict(base, status="searching", next=f_up, stage="range end", extended=False)
        if pk[f_up] >= M - tol_k:
            return _bisect_closed(base, M, 0.0, f_up, pk, tol_k, width, runs)
    # the extension (or the exploratory search): bisection on (f_up, f_end]
    lo, hi = f_up, key(f_end)
    while True:
        if hi - lo <= width + 1e-12:
            if hi not in pk:
                return dict(base, status="searching", next=hi, stage="extension end", lo=lo, hi=hi, runs=runs,
                            extended=True)
            if pk[hi] < M - tol_k:
                return dict(base, status="above 1", next=None, lo=lo, hi=hi, peak_at_end=pk[hi], runs=runs,
                            extended=True)
            if abs(pk[hi] - M) <= tol_k:
                return dict(base, status="matched", next=None, f_max=hi, lo=lo, hi=hi, f_run=hi, p_run=pk[hi],
                            runs=runs, extended=True)
            return dict(base, status="bracketed", next=None, f_max=interp_p(lo, pk[lo], hi, pk[hi], M), lo=lo, hi=hi,
                        p_lo=pk[lo], p_hi=pk[hi], runs=runs, extended=True)
        m = _mid(lo, hi)
        if m not in pk:
            spec = [q for q in (_mid(lo, m), _mid(m, hi)) if q not in pk]
            return dict(base, status="searching", next=m, stage="extension", lo=lo, hi=hi, runs=runs, extended=True,
                        speculative=spec)
        runs.append(m)
        p = pk[m]
        if abs(p - M) <= tol_k:
            if p >= M:
                hi = m
            else:
                lo = m
            return dict(base, status="matched", next=None, f_max=m, lo=lo, hi=hi, f_run=m, p_run=p, runs=runs,
                        extended=True)
        if p >= M:
            hi = m
        else:
            lo = m


def _bisect_closed(base, M, lo, hi, pk, tol_k, width, runs):
    if abs(pk[hi] - M) <= tol_k:
        return dict(base, status="matched", next=None, f_max=hi, lo=lo, hi=hi, f_run=hi, p_run=pk[hi], runs=runs,
                    extended=False)
    while True:
        if hi - lo <= width + 1e-12:
            return dict(base, status="bracketed", next=None, f_max=interp_p(lo, pk[lo], hi, pk[hi], M), lo=lo, hi=hi,
                        p_lo=pk[lo], p_hi=pk[hi], runs=runs, extended=False)
        m = _mid(lo, hi)
        if m not in pk:
            return dict(base, status="searching", next=m, stage="bisection", lo=lo, hi=hi, runs=runs, extended=False)
        runs.append(m)
        p = pk[m]
        if abs(p - M) <= tol_k:
            if p >= M:
                hi = m
            else:
                lo = m
            return dict(base, status="matched", next=None, f_max=m, lo=lo, hi=hi, f_run=m, p_run=p, runs=runs,
                        extended=False)
        if p >= M:
            hi = m
        else:
            lo = m


def upper(r):
    """The largest value a result's bracket allows: 0 for zero, else its bracket's upper end."""
    return 0.0 if r["status"] == "zero" else r.get("hi")


def lower(r):
    return 0.0 if r["status"] == "zero" else r.get("lo")


def below(fm, fs):
    """Whether f_max lies below f* (D92 (5)): True when the criterion is not met at f_max's upper end, f*_lo being at
    least that end and f* not 0; False when f_max's lower end is at least f*_hi (or f* is 0); None if they overlap."""
    if fm.get("f_max") is None:
        return None
    if fs["status"] == "zero":
        return False
    if fs["status"] == "above":
        return True if (upper(fm) is not None and upper(fm) <= 1.0) else None
    hi = upper(fm)
    if hi is not None and fs["lo"] >= hi - 1e-12:
        return True
    lo = lower(fm)
    if lo is not None and lo >= fs["hi"] - 1e-12:
        return False
    return None


def finite(x):
    return x is not None and not (isinstance(x, float) and math.isnan(x))
