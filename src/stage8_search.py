"""Stage 8: the search for the threshold fraction f* of one test, criterion and configuration (DECISIONS.md D78).

A chain holds the fractions already tried, each with whether the criterion was met there (the delivered heat is
assumed never to undo a crossing, so the fractions that meet it lie above those that do not). Its bracket is (lo, hi]:
lo the largest fraction tried that does not meet the criterion, hi the smallest that does. The next fraction is the
first of the chain's probes that lies inside the bracket and has not been tried, else the bracket's midpoint, until
the bracket is at most WIDTH wide. The chain ends with:
  zero     the criterion is met at f = 0 (f* = 0);
  bracket  f* in (lo, hi], hi - lo <= WIDTH;
  above    the criterion is not met at F_MAX = 1 (f* above 1);
  broken   a fraction that meets the criterion lies below one that does not (reported; no further point).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import stage8_inputs as IN                        # noqa: E402

ND = 12                                           # fractions are kept rounded to 12 decimals


def key(f):
    return round(float(f), ND)


def bracket(points):
    """points: {f: met}. Returns (lo, hi), either None where no such fraction was tried."""
    no = [f for f, m in points.items() if not m]
    yes = [f for f, m in points.items() if m]
    return (max(no) if no else None), (min(yes) if yes else None)


def state(points, probes=(), width=IN.WIDTH, f_max=IN.F_MAX):
    """The chain's state: {"status", "lo", "hi", "next"}; "next" is the fraction to try next, or None at the end."""
    pts = {key(f): bool(m) for f, m in points.items()}
    lo, hi = bracket(pts)
    out = {"lo": lo, "hi": hi, "n_points": len(pts)}
    if lo is not None and hi is not None and lo > hi:
        return dict(out, status="broken", next=None)
    if hi is not None and hi == 0.0:
        return dict(out, status="zero", next=None)
    if lo is not None and lo >= f_max:
        return dict(out, status="above", next=None)
    for p in probes:
        p = key(p)
        if p in pts:
            continue
        if (lo is None or p > lo) and (hi is None or p < hi):
            return dict(out, status="searching", next=p)
    if hi is None:
        if key(f_max) not in pts:
            return dict(out, status="searching", next=key(f_max))
        return dict(out, status="above", next=None)
    if lo is None:
        raise ValueError("a chain must hold f = 0 or probe it first")
    if hi - lo <= width + 1e-12:
        return dict(out, status="bracket", next=None)
    return dict(out, status="searching", next=key(0.5 * (lo + hi)))


def restart_probes(lo_a, hi_a, status_a):
    """The probes of a chain restarted from Part A's result (A4, Part B): Part A's upper end, then its lower end, then
    the grid's points (0.1, 0.2, 0.3, 0.5 and 1.0) in order, of which `state` tries those the bracket holds, below
    Part A's lower end as well as above its upper end (D88 (2), which corrects D79 (1) and D80's "points above")."""
    out = []
    if status_a == "bracket":
        out = [hi_a] + ([lo_a] if lo_a and lo_a > 0 else [])
    elif status_a == "above":
        out = [IN.F_MAX]
    return out + [p for p in IN.PROBES_A if p not in out]


def f_star(st):
    """The reported value: 0 for zero, the bracket's two ends, or above 1."""
    if st["status"] == "zero":
        return {"status": "zero", "lo": 0.0, "hi": 0.0}
    if st["status"] == "above":
        return {"status": "above", "lo": st["lo"], "hi": None}
    if st["status"] == "bracket":
        return {"status": "bracket", "lo": st["lo"], "hi": st["hi"]}
    return {"status": st["status"], "lo": st.get("lo"), "hi": st.get("hi")}


def below(fs, x):
    """Whether f* lies below x: True if the criterion is met at a fraction at or below x (hi <= x), False if it is
    not met at x or above (lo >= x), None if the bracket straddles x."""
    if fs["status"] == "zero":
        return True
    if fs["status"] == "above":
        return False if x <= 1.0 else None
    if fs["hi"] is not None and fs["hi"] <= x + 1e-12:
        return True
    if fs["lo"] is not None and fs["lo"] >= x - 1e-12:
        return False
    return None
