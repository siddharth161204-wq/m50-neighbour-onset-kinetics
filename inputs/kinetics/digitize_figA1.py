#!/usr/bin/env python3
"""Read the mass that multiplies each reaction in the paper's own ARC simulation from its Fig. A.1(a) (DECISIONS.md D4).

Usage: python3 digitize_figA1.py <path to the paper PDF> [--out figA1a_mass_basis.json]

Fig. A.1(a) of Koenig, Zhao and Deng (2025) plots, for the mean kinetic model in the paper's ARC test, the
self-heating rate dT/dt (C/s, log axis) of the SEI decomposition (green) and of the anode-electrolyte reaction
(orange) against the battery temperature. Below 168 C the anode-electrolyte reactants are essentially unconsumed, and
the SEI curve below 60 C is too, so each curve divided by the fresh-reactant rate of the posterior-mean model gives the
mass m in dT/dt = dH r m / (M cp), with M cp = 792 J/K (Table 1). The SEI's mass is given in Table 1 (100.58 g), so
its reading measures the digitisation bias, which is then removed from the anode-electrolyte reading.

The figure is extracted with pdfimages (poppler) from page 16. The axes are calibrated from the tick marks: x ticks
at 50, 100, ..., 300 C; major y ticks at 1e0 down to 1e-5.
"""
import argparse, json, os, subprocess, sys, tempfile
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src"))
import bcrnn  # noqa: E402


def groups(idx):
    out = []
    for x in idx:
        if out and x - out[-1][-1] <= 1:
            out[-1].append(x)
        else:
            out.append([x])
    return [float(np.mean(g)) for g in out]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("pdf"); ap.add_argument("--out", default="figA1a_mass_basis.json")
    a = ap.parse_args()
    tmp = tempfile.mkdtemp()
    subprocess.run(["pdfimages", "-f", "16", "-l", "16", "-png", a.pdf, os.path.join(tmp, "fig")], check=True)
    im = np.asarray(Image.open(os.path.join(tmp, "fig-000.png")).convert("RGB")).astype(int)[:720]
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    dark = (r + g + b) < 150
    spine_x = max(range(0, 250), key=lambda x: dark[:, x].sum())
    bottom_y = max(range(500, 720), key=lambda y: dark[y, :].sum())
    xt = [x for x in groups(np.where(dark[bottom_y + 4, :])[0]) if x > spine_x + 50]      # 50, 100, ..., 300 C
    yt = groups(np.where(dark[:, spine_x - 5])[0])
    px_per_C = (xt[-1] - xt[0]) / 250.0
    x0 = xt[0] - 50.0 * px_per_C
    y_dec = sorted(yt)
    y_top, y_bot = y_dec[0], y_dec[-1]                      # 1e0 and 1e-5
    px_per_dec = (y_bot - y_top) / 5.0
    T_of_x = lambda x: (x - x0) / px_per_C
    rate_of_y = lambda y: 10 ** (-(y - y_top) / px_per_dec)
    legend = np.zeros(r.shape, bool); legend[20:245, 160:880] = True
    masks = {"an_ele": (r > 220) & (g > 110) & (g < 190) & (b < 90) & ~legend,
             "sei": (r < 90) & (g > 110) & (g < 170) & (b > 60) & (b < 130) & ~legend}
    pts = {}
    for k, m in masks.items():
        pts[k] = []
        for x in range(spine_x + 6, im.shape[1] - 10):
            ys = np.where(m[:, x])[0]
            ys = ys[(ys > y_top + 1) & (ys < y_bot - 1)]
            if ys.size:
                pts[k].append((T_of_x(x), rate_of_y(ys.mean())))
    kin = bcrnn.Kinetics()
    MCP = 0.720 * 1100.0
    c = bcrnn.C0[:, None]
    j_sei, j_ae = bcrnn.REACTIONS.index("sei_decomp"), bcrnn.REACTIONS.index("an_ele")

    def fresh(j, TC):
        rr = kin.rates(np.array([TC + 273.15]), c)[j, 0]
        return kin.dH[j] * rr / MCP            # C/s per gram of reacting mass
    sei = np.array([rt / fresh(j_sei, T) for T, rt in pts["sei"] if 25.0 <= T <= 60.0])
    ae = np.array([rt / fresh(j_ae, T) for T, rt in pts["an_ele"] if 133.0 <= T <= 168.0])
    bias = bcrnn.M_SEI / np.median(sei)
    res = {"calibration": {"x_ticks_px": xt, "y_ticks_px_major": [y_top, y_bot], "px_per_C": px_per_C, "px_per_decade": px_per_dec},
           "sei_implied_mass_g": {"median": float(np.median(sei)), "n": int(sei.size), "table1_value": bcrnn.M_SEI},
           "digitisation_bias_factor": float(bias),
           "an_ele_implied_mass_g_raw": {"median": float(np.median(ae)), "q25": float(np.percentile(ae, 25)),
                                         "q75": float(np.percentile(ae, 75)), "n": int(ae.size)},
           "an_ele_implied_mass_g_corrected": float(np.median(ae) * bias),
           "candidates_g": {"anode": bcrnn.M_ANODE, "electrolyte": bcrnn.M_ELECTROLYTE,
                            "anode_plus_electrolyte": bcrnn.M_ANODE + bcrnn.M_ELECTROLYTE}}
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
