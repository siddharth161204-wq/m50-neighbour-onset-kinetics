#!/usr/bin/env python3
"""Stage 10, Part A0.2 (DECISIONS.md D102): the measured histories of Fransson et al. (2024), supplementary Figure 10
(Appendix A, p. 29): (a) M50_PT_Exp4, which propagated, and (b) M50_PP_Exp3, which did not, each with the trigger
cell (solid curve) and the propagation cell, the neighbour (dashed curve).

The figure is a vector drawing: every curve is a stroked path of 7,359 to 8,307 points, so the histories are read out
of the paths themselves, not off pixels. They are read twice, by separate code and separate calibrations:
  first:  pdfplumber's path objects, with each panel's axes fitted by least squares to its major grid lines, whose
          values are the tick labels set beside them (read as text);
  second: the page's form XObject parsed operator by operator with pypdf (its own transformation matrices), with the
          axes taken from the panel's frame, the plot area's white rectangle, as 0 to 500 s and 0 to 700 C.
Both are resampled every half second from 0 to 500 s by linear interpolation between the path's points. The
digitisation's uncertainty is the larger difference between the two readings; the figure's resolution is half the
curves' stroke width, in seconds and in kelvin. The section boundaries the figure draws (dash-dot lines) are read as
well: the boundary between Sections II and III of panel (a) is the instant the paper marks as the neighbour's onset.

Usage: python3 extract_fig10.py PATH/1-s2.0-S0378775324008681-mmc1.pdf
Writes pt_exp4_history.csv, pp_exp3_history.csv and fig10_extraction.json next to this script."""
import hashlib, json, math, os, re, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SHA256 = "e96713ef58e8dc13df8810034c7ee8b47fb3e2fdcdb398a5095ecdfb64dfc0ef"
SIZE = 10240301
URL = "https://ars.els-cdn.com/content/image/1-s2.0-S0378775324008681-mmc1.pdf"
PAGE = 1                                   # 0-based: the PDF's second page, the journal's p. 29
T_AXIS = (0.0, 500.0)                      # the axes' limits as the tick labels give them (checked in first())
Y_AXIS = (0.0, 700.0)
GRID_W = 0.1786                            # the major grid lines' width (pt) in the page
PANELS = {"a": "M50_PT_Exp4", "b": "M50_PP_Exp3"}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# ------------------------------------------------------------------------------------------- the first reading
def _numbers(chars, axis):
    """Tick labels as (value, position): characters on one row (x labels) or one line (y labels) joined into numbers."""
    out = []
    if axis == "x":
        rows = {}
        for c in chars:
            rows.setdefault(round(c["top"], 1), []).append(c)
        for top, cs in rows.items():
            cs.sort(key=lambda c: c["x0"])
            groups, cur = [], [cs[0]]
            for c in cs[1:]:
                if c["x0"] - cur[-1]["x1"] < 1.0:
                    cur.append(c)
                else:
                    groups.append(cur)
                    cur = [c]
            groups.append(cur)
            for g in groups:
                s = "".join(c["text"] for c in g)
                if re.fullmatch(r"\d+", s):
                    out.append((float(s), 0.5 * (g[0]["x0"] + g[-1]["x1"]), top))
    else:
        rows = {}
        for c in chars:
            rows.setdefault(round(0.5 * (c["top"] + c["bottom"]), 1), []).append(c)
        for yc, cs in rows.items():
            cs.sort(key=lambda c: c["x0"])
            s = "".join(c["text"] for c in cs)
            if re.fullmatch(r"\d+", s):
                out.append((float(s), yc, cs[-1]["x1"]))
    return out


def first(path):
    import pdfplumber
    pg = pdfplumber.open(path).pages[PAGE]
    lines = pg.objects["line"]
    grid = [o for o in lines if abs(o["linewidth"] - GRID_W) < 0.01]
    frames = sorted((o for o in pg.objects["rect"] if o.get("fill") and o.get("non_stroking_color") in (1, 1.0, [1], (1,))
                     and (o["x1"] - o["x0"]) > 300), key=lambda o: o["top"])
    assert len(frames) == 2, len(frames)
    curves = sorted(pg.objects["curve"], key=lambda o: -len(o["pts"]))[:4]
    out = {}
    for key, fr in zip("ab", frames):
        x0, x1, top, bot = fr["x0"], fr["x1"], fr["top"], fr["bottom"]
        vert = sorted({round(o["x0"], 4) for o in grid if abs(o["x0"] - o["x1"]) < 1e-6
                       and abs(o["top"] - top) < 0.01 and abs(o["bottom"] - bot) < 0.01})
        hor = sorted({round(o["top"], 4) for o in grid if abs(o["top"] - o["bottom"]) < 1e-6
                      and abs(o["x0"] - x0) < 0.01 and abs(o["x1"] - x1) < 0.01})
        # tick labels: the x labels on the row just below the frame, the y labels just left of it
        below = [c for c in pg.chars if bot < c["top"] < bot + 8 and x0 - 8 < c["x0"] < x1 + 8]
        left = [c for c in pg.chars if top - 4 < c["top"] < bot + 4 and x0 - 20 < c["x0"] and c["x1"] < x0 - 0.5]
        xl = _numbers(below, "x")
        yl = _numbers(left, "y")
        xs, tv = [], []
        for v, xc, _ in xl:
            g = min(vert, key=lambda g: abs(g - xc))
            assert abs(g - xc) < 3.0, (key, v, xc, g)
            xs.append(g)
            tv.append(v)
        ys, Tv = [], []
        for v, yc, _ in yl:
            g = min(hor, key=lambda g: abs(g - yc))
            assert abs(g - yc) < 3.0, (key, v, yc, g)
            ys.append(g)
            Tv.append(v)
        bt, at = np.polyfit(xs, tv, 1)
        bT, aT = np.polyfit(ys, Tv, 1)
        res_t = max(abs(at + bt * x - v) for x, v in zip(xs, tv))
        res_T = max(abs(aT + bT * y - v) for y, v in zip(ys, Tv))
        assert min(tv) == T_AXIS[0] and max(tv) == T_AXIS[1] and min(Tv) == Y_AXIS[0] and max(Tv) == Y_AXIS[1]
        mine = [c for c in curves if top - 1 < c["top"] and c["bottom"] < bot + 1]
        assert len(mine) == 2, (key, len(mine))
        legend = sorted((o for o in lines if abs(o["linewidth"] - 0.5714) < 0.01 and top < o["top"] < bot
                         and abs(o["top"] - o["bottom"]) < 1e-6), key=lambda o: o["top"])
        legend_text = []
        for o in legend:
            row = sorted((c for c in pg.chars if abs(0.5 * (c["top"] + c["bottom"]) - o["top"]) < 2.5
                          and o["x1"] < c["x0"] < o["x1"] + 40), key=lambda c: c["x0"])
            legend_text.append(("dashed" if o["dash"][0] else "solid", "".join(c["text"] for c in row).strip()))
        style = dict(legend_text)
        assert style["solid"].startswith("Trigger") and style["dashed"].startswith("Propagation"), legend_text
        cur = {}
        for c in mine:
            name = "neighbour" if c["dash"][0] else "trigger"
            p = np.array(c["pts"], float)
            cur[name] = {"t": at + bt * p[:, 0], "T": aT + bT * p[:, 1], "n": len(p), "dash": list(c["dash"][0]),
                         "linewidth_pt": c["linewidth"]}
        bounds = sorted(at + bt * o["x0"] for o in lines if o["dash"][0] == [8, 2, 4, 2] and abs(o["top"] - top) < 0.01)
        out[key] = {"curves": cur, "bounds_s": bounds, "cal": {"t_per_pt": bt, "T_per_pt": bT, "t0": at, "T0": aT,
                    "grid_x_pt": xs, "grid_t": tv, "grid_y_pt": ys, "grid_T": Tv, "max_residual_s": res_t,
                    "max_residual_K": res_T, "frame_pt": [x0, x1, top, bot]}, "legend": legend_text}
    return out


# ------------------------------------------------------------------------------------------ the second reading
def _mul(a, b):
    """The product of two PDF matrices [a b c d e f] (a applied first)."""
    return [a[0] * b[0] + a[1] * b[2], a[0] * b[1] + a[1] * b[3], a[2] * b[0] + a[3] * b[2],
            a[2] * b[1] + a[3] * b[3], a[4] * b[0] + a[5] * b[2] + b[4], a[4] * b[1] + a[5] * b[3] + b[5]]


def _apply(m, x, y):
    return m[0] * x + m[2] * y + m[4], m[1] * x + m[3] * y + m[5]


def _walk(reader, ops, ctm, resources, sink):
    from pypdf.generic import ContentStream
    stack, path, dash, gray_fill, lw = [], [], [], None, 1.0
    for args, op in ops:
        if op == b"q":
            stack.append((ctm, dash, gray_fill, lw))
        elif op == b"Q":
            ctm, dash, gray_fill, lw = stack.pop()
        elif op == b"cm":
            ctm = _mul([float(a) for a in args], ctm)
        elif op == b"d":
            dash = [float(a) for a in args[0]]
        elif op == b"w":
            lw = float(args[0])
        elif op == b"g":
            gray_fill = float(args[0])
        elif op == b"rg":
            gray_fill = None
        elif op == b"m":
            path.append([_apply(ctm, float(args[0]), float(args[1]))])
        elif op == b"l":
            path[-1].append(_apply(ctm, float(args[0]), float(args[1])))
        elif op == b"c":
            path[-1].append(_apply(ctm, float(args[4]), float(args[5])))
        elif op in (b"v", b"y"):
            path[-1].append(_apply(ctm, float(args[2]), float(args[3])))
        elif op == b"re":
            x, y, w, h = (float(a) for a in args)
            path.append([_apply(ctm, x, y), _apply(ctm, x + w, y), _apply(ctm, x + w, y + h), _apply(ctm, x, y + h)])
            path[-1].append(("rect",))
        elif op in (b"S", b"s"):
            scale = math.hypot(ctm[0], ctm[1])
            for sp in path:
                pts = [p for p in sp if not (isinstance(p, tuple) and p and p[0] == "rect")]
                sink.append({"kind": "stroke", "pts": pts, "dash": [d * scale for d in dash], "lw": lw * scale})
            path = []
        elif op in (b"f", b"F", b"f*", b"B", b"b", b"B*", b"b*"):
            for sp in path:                    # a rectangle drawn by re, or by m, l, l, l (and h)
                pts = [p for p in sp if not (isinstance(p, tuple) and p and p[0] == "rect")]
                if len(pts) in (4, 5):
                    sink.append({"kind": "fill_rect", "pts": pts[:4], "gray": gray_fill})
            path = []
        elif op == b"n":
            path = []
        elif op == b"Do":
            xo = resources["/XObject"][args[0]].get_object()
            if xo.get("/Subtype") == "/Form":
                m = [float(a) for a in xo.get("/Matrix", [1, 0, 0, 1, 0, 0])]
                _walk(reader, ContentStream(xo, reader).operations, _mul(m, ctm), xo.get("/Resources", resources), sink)


def second(path):
    import pypdf
    from pypdf.generic import ContentStream
    r = pypdf.PdfReader(path)
    pg = r.pages[PAGE]
    sink = []
    _walk(r, ContentStream(pg.get_contents(), r).operations, [1, 0, 0, 1, 0, 0], pg["/Resources"], sink)
    frames = []
    for s in sink:
        if s["kind"] == "fill_rect" and s["gray"] == 1.0:
            xs = [p[0] for p in s["pts"]]
            ys = [p[1] for p in s["pts"]]
            if max(xs) - min(xs) > 300:
                frames.append((min(xs), max(xs), min(ys), max(ys)))
    frames = sorted({tuple(round(v, 6) for v in f) for f in frames}, key=lambda f: -f[3])   # top panel first
    assert len(frames) == 2, frames
    long_paths = [s for s in sink if s["kind"] == "stroke" and len(s["pts"]) > 1000]
    assert len(long_paths) == 4, len(long_paths)
    out = {}
    for key, (x0, x1, y0, y1) in zip("ab", frames):
        bt = (T_AXIS[1] - T_AXIS[0]) / (x1 - x0)
        bT = (Y_AXIS[1] - Y_AXIS[0]) / (y1 - y0)
        cur = {}
        for s in long_paths:
            ys = [p[1] for p in s["pts"]]
            if min(ys) > y0 - 1 and max(ys) < y1 + 1:
                p = np.array(s["pts"], float)
                name = "neighbour" if s["dash"] else "trigger"
                cur[name] = {"t": T_AXIS[0] + bt * (p[:, 0] - x0), "T": Y_AXIS[0] + bT * (p[:, 1] - y0), "n": len(p)}
        assert set(cur) == {"neighbour", "trigger"}, (key, list(cur))
        out[key] = {"curves": cur, "frame_pt_pdf": [x0, x1, y0, y1]}
    return out


# ------------------------------------------------------------------------------------------------ the records
def resample(c, grid):
    """Linear between the path's points; the paths begin at -0.06 s and end 2e-5 s short of 500 s, so the last sample
    takes the path's last point."""
    t, T = c["t"], c["T"]
    assert np.all(np.diff(t) > 0) and t[0] <= grid[0] and grid[-1] - t[-1] < 0.01
    return np.interp(grid, t, T)


def main(pdf_path):
    assert os.path.getsize(pdf_path) == SIZE and sha256(pdf_path) == SHA256, "not the file of D52 and D102"
    A, B = first(pdf_path), second(pdf_path)
    grid = np.arange(0.0, 500.0 + 1e-9, 0.5)               # every half second: 271.5 s, the onset, is a sample
    rec = {"source": {"file": os.path.basename(pdf_path), "url": URL, "bytes": SIZE, "sha256": SHA256,
                      "page": "the PDF's page 2, the journal's p. 29, Figure 10",
                      "citation": "M. Fransson et al., Journal of Power Sources 617 (2024) 234916, Appendix A "
                                  "(CC BY 4.0)"},
           "method": "the curves' vector paths, read twice by separate code and calibration (see the docstring)",
           "panels": {}}
    for key, test in PANELS.items():
        a, b = A[key], B[key]
        cal = a["cal"]
        rows = {}
        pr = {"test": test, "legend": a["legend"], "calibration_first": cal, "frame_second_pdf_pt": b["frame_pt_pdf"],
              "section_bounds_s": a["bounds_s"], "curves": {}}
        for name in ("neighbour", "trigger"):
            c1, c2 = a["curves"][name], b["curves"][name]
            r1, r2 = resample(c1, grid), resample(c2, grid)
            d = np.abs(r1 - r2)
            dt = np.diff(c1["t"])
            half_w_pt = 0.5 * c1["linewidth_pt"]
            pr["curves"][name] = {
                "points": c1["n"], "points_second": c2["n"], "t_first_s": float(c1["t"][0]),
                "t_last_s": float(c1["t"][-1]), "median_spacing_s": float(np.median(dt)), "max_spacing_s": float(dt.max()),
                "dash": c1["dash"], "stroke_width_pt": c1["linewidth_pt"],
                "digitisation_uncertainty_K": float(np.nanmax(d)),
                "figure_resolution_K": float(half_w_pt * abs(cal["T_per_pt"])),
                "figure_resolution_s": float(half_w_pt * abs(cal["t_per_pt"])),
                "max_T_C": float(np.max(c1["T"])), "t_of_max_s": float(c1["t"][int(np.argmax(c1["T"]))])}
            rows[name] = (r1, r2)
        unc_K = max(max(pr["curves"][n]["digitisation_uncertainty_K"], pr["curves"][n]["figure_resolution_K"])
                    for n in pr["curves"])
        unc_s = max(pr["curves"][n]["figure_resolution_s"] for n in pr["curves"])
        pr["uncertainty_K"] = unc_K
        pr["uncertainty_s"] = unc_s
        rec["panels"][key] = pr
        fn = {"a": "pt_exp4_history.csv", "b": "pp_exp3_history.csv"}[key]
        with open(os.path.join(HERE, fn), "w") as f:
            f.write("t_s,T_neighbour_C,T_trigger_C,T_neighbour_C_second,T_trigger_C_second,uncertainty_K,uncertainty_s\n")
            for i, t in enumerate(grid):
                n1, n2 = rows["neighbour"][0][i], rows["neighbour"][1][i]
                g1, g2 = rows["trigger"][0][i], rows["trigger"][1][i]
                f.write(f"{t:.1f},{n1:.4f},{g1:.4f},{n2:.4f},{g2:.4f},{unc_K:.2f},{unc_s:.2f}\n")
    json.dump(rec, open(os.path.join(HERE, "fig10_extraction.json"), "w"), indent=1,
              default=lambda o: o.tolist() if hasattr(o, "tolist") else float(o))
    open(os.path.join(HERE, "fig10_extraction.json"), "a").write("\n")
    for key in "ab":
        p = rec["panels"][key]
        print(key, p["test"], "bounds", [round(x, 2) for x in p["section_bounds_s"]],
              {n: {k: (round(v, 4) if isinstance(v, float) else v) for k, v in c.items()
                   if k in ("points", "digitisation_uncertainty_K", "figure_resolution_K", "max_T_C", "t_of_max_s",
                            "median_spacing_s")} for n, c in p["curves"].items()},
              "cal residuals", round(p["calibration_first"]["max_residual_s"], 6), round(p["calibration_first"]["max_residual_K"], 6))


if __name__ == "__main__":
    main(sys.argv[1])
