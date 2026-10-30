#!/usr/bin/env python3
"""Stage 10, V1 (DECISIONS.md D102 (5)): the measured histories of `inputs/fransson2024/pt_exp4_history.csv` and
`pp_exp3_history.csv`, read from the figure's vector paths (`inputs/fransson2024/extract_fig10.py`), read a second
time by separate means: the page rendered as pixels (pdftoppm, 1200 dpi, no anti-aliasing), the axes calibrated on the
grid lines found in the pixels, and the neighbour's dashed curve traced column by column. No vector data is used.

At each whole second from 5 s to the end of the window (the propagation instant of panel (a), 271.50 s; the end of
Section II of panel (b), 309.72 s) where a dash of the curve crosses the column, the pixel reading is compared with the
vector reading at the same instant. Acceptance: within the recorded uncertainty in kelvin plus one pixel, plus the
curve's local slope times the uncertainty in seconds plus one pixel's width. The first 5 s, where the two curves rise
together within a few pixels of each other, are left out. The vector reading is used only for the comparison.

Usage: python3 stage10_v1.py PATH/1-s2.0-S0378775324008681-mmc1.pdf   (writes results/stage10_v1.json)"""
import csv, json, os, subprocess, sys, tempfile
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
INP = os.path.join(HERE, "..", "inputs", "fransson2024")
RES = os.path.join(HERE, "..", "results")
DPI = 1200
PX_PER_PT = DPI / 72.0
# generous crops (pt) around each panel's plot area, from the page's layout; the axes come from the pixels
CROPS = {"a": (130.0, 226.0, 456.0, 326.0), "b": (130.0, 328.0, 456.0, 428.0)}
WINDOW = {"a": 271.50, "b": 309.72}
FILES = {"a": "pt_exp4_history.csv", "b": "pp_exp3_history.csv"}


def render(pdf, crop):
    from PIL import Image
    x0, y0, x1, y1 = crop
    with tempfile.TemporaryDirectory() as d:
        base = os.path.join(d, "p")
        subprocess.run(["pdftoppm", "-f", "2", "-l", "2", "-r", str(DPI), "-aa", "no", "-aaVector", "no",
                        "-x", str(int(x0 * PX_PER_PT)), "-y", str(int(y0 * PX_PER_PT)),
                        "-W", str(int((x1 - x0) * PX_PER_PT)), "-H", str(int((y1 - y0) * PX_PER_PT)), "-png", pdf, base],
                       check=True)
        f = [n for n in os.listdir(d) if n.endswith(".png")][0]
        return np.array(Image.open(os.path.join(d, f)).convert("RGB")).astype(int)


def lines_in(mask, axis, frac):
    """Centres of the runs of columns (axis 0) or rows (axis 1) in which at least frac of the pixels are set."""
    cnt = mask.sum(axis=axis)
    n = mask.shape[axis]
    on = cnt >= frac * n
    out, i = [], 0
    while i < len(on):
        if on[i]:
            j = i
            while j + 1 < len(on) and on[j + 1]:
                j += 1
            out.append(0.5 * (i + j))
            i = j + 1
        else:
            i += 1
    return out


def calibrate(im):
    L = im.mean(axis=2)
    grey = (L > 175) & (L < 233) & (np.ptp(im, axis=2) < 40)              # the grid lines, blended over the fills
    frame = (L >= 30) & (L < 70) & (np.ptp(im, axis=2) < 25)             # the axes' frame, on the outer grid lines
    # the inner grid lines and the frame's edges: the rows and columns that hold such pixels in long runs
    cols = sorted(lines_in(grey, 0, 0.5) + lines_in(frame, 0, 0.5))
    rows = sorted(lines_in(grey, 1, 0.5) + lines_in(frame, 1, 0.5))
    assert len(cols) == 21 and len(rows) == 8, (len(cols), len(rows))
    bt, at = np.polyfit(cols, np.linspace(0.0, 500.0, 21), 1)
    bT, aT = np.polyfit(rows, np.linspace(700.0, 0.0, 8), 1)
    return {"t0": at, "t_per_px": bt, "T0": aT, "T_per_px": bT, "cols": cols, "rows": rows,
            "max_residual_s": float(np.max(np.abs(at + bt * np.array(cols) - np.linspace(0, 500, 21)))),
            "max_residual_K": float(np.max(np.abs(aT + bT * np.array(rows) - np.linspace(700, 0, 8))))}


def trace(im, cal, t_end, vec_t, vec_T):
    dark = im.max(axis=2) < 32                                   # the curves; the frame and ticks are lighter greys
    row_of = lambda T: (T - cal["T0"]) / cal["T_per_px"]
    col_of = lambda t: (t - cal["t0"]) / cal["t_per_px"]
    r_top = int(row_of(350.0))                                 # the neighbour stays below 350 C in the windows
    dark[int(row_of(0.0)) - 20:, :] = False                    # the bottom frame and its ticks (the curves stay above 25 C)
    out = []
    prev = None
    for t in np.arange(5.0, np.floor(t_end) + 1e-9, 1.0):
        c = int(round(col_of(t)))
        sub = dark[r_top:, c - 2:c + 3].any(axis=1)
        idx = np.where(sub)[0]
        if not len(idx):
            continue
        runs, start = [], idx[0]
        for a, b in zip(idx[:-1], idx[1:]):
            if b != a + 1:
                runs.append((start, a))
                start = b
        runs.append((start, idx[-1]))
        temps = [cal["T0"] + cal["T_per_px"] * (r_top + 0.5 * (a + b)) for a, b in runs]
        cand = sorted(temps)                                     # the neighbour is the lowest curve in the windows
        T = cand[0]
        if prev is not None and abs(T - prev) > 15.0:            # a dash gap with only the trigger in the column
            continue
        prev = T
        tv = cal["t0"] + cal["t_per_px"] * c
        out.append((float(t), float(tv), float(T), float(np.interp(tv, vec_t, vec_T))))
    return out


def main(pdf):
    rec = {"what": "V1 (D102 (5)): the measured histories read a second time from pixels", "dpi": DPI, "panels": {}}
    ok = True
    for key in ("a", "b"):
        rows = list(csv.DictReader(open(os.path.join(INP, FILES[key]))))
        vt = np.array([float(r["t_s"]) for r in rows])
        vT = np.array([float(r["T_neighbour_C"]) for r in rows])
        uK, us = float(rows[0]["uncertainty_K"]), float(rows[0]["uncertainty_s"])
        im = render(pdf, CROPS[key])
        cal = calibrate(im)
        pts = trace(im, cal, WINDOW[key], vt, vT)
        slope = np.gradient(vT, vt)
        px_K, px_s = abs(cal["T_per_px"]), abs(cal["t_per_px"])
        worst, fails = 0.0, []
        for t, tv, T, Tv in pts:
            s = abs(float(np.interp(tv, vt, slope)))
            tol = uK + px_K + s * (us + px_s)
            d = T - Tv
            worst = max(worst, abs(d))
            if abs(d) > tol:
                fails.append({"t_s": t, "pixel_C": T, "vector_C": Tv, "tolerance_K": tol})
        n_win = int(np.floor(WINDOW[key])) - 5 + 1
        rec["panels"][key] = {"file": FILES[key], "calibration": {k: v for k, v in cal.items() if k not in ("cols", "rows")},
                              "pixel_K": px_K, "pixel_s": px_s, "seconds_read": len(pts), "seconds_in_window": n_win,
                              "largest_difference_K": worst, "outside_tolerance": fails, "pass": not fails and len(pts) >= 0.5 * n_win}
        ok = ok and rec["panels"][key]["pass"]
    rec["pass"] = ok
    json.dump(rec, open(os.path.join(RES, "stage10_v1.json"), "w"), indent=1, default=float)
    print(json.dumps({k: {kk: vv for kk, vv in p.items() if kk in ("seconds_read", "seconds_in_window", "largest_difference_K", "pass")}
                      for k, p in rec["panels"].items()}), "pass" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
