#!/usr/bin/env python3
"""V3 for Stage 2 (DECISIONS.md D15): with the roll's conductivity raised to 1e4 W/mK the reactive resolved cell must
match the reactive lumped node, as the published study's two-way check did; the energy account of every Stage 2 run
must close to 1e-9 of the heat taken in.

Usage: python3 v3_stage2.py --out ../results --cases max:30:0.5 max:30:0.2
"""
import argparse, glob, json, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "external", "m50-two-cell-pilot", "src"))
import lumped_two_cell as LP               # noqa: E402

LP.K_RADIAL = LP.K_AXIAL = 1.0e4          # before the resolved model is built
import reactive as RX                       # noqa: E402
from run_stage2 import E, PUB, case_name   # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="../results")
    ap.add_argument("--cases", nargs="+", default=["max:30:0.5", "max:30:0.2"])
    a = ap.parse_args()
    from resolved_cell2 import Cell2Model, t1_interpolator
    model = Cell2Model(1.0)
    path = os.path.join(a.out, "v3_stage2.json")
    out = json.load(open(path)) if os.path.exists(path) else {}
    for spec in a.cases:
        en, tau, g = spec.split(":"); tau, g = float(tau), float(g)
        name = case_name(en, tau, g)
        t1f, _ = t1_interpolator(os.path.join(PUB, "results", "t1_series", LP.series_name(E[en], tau, g)))
        rr = RX.run_resolved(model, t1f, g / 2, g / 2)
        lr = RX.run_lumped(t1f, g)
        s, l = rr["series"], lr["series"]
        Tm = np.interp(l[:, 0], s[:, 0], s[:, 3])
        Tx = np.interp(l[:, 0], s[:, 0], s[:, 2])
        out[name] = {"k_roll_W_per_mK": 1.0e4, "max_abs_Tmean_minus_lumped_K": float(np.abs(Tm - l[:, 1]).max()),
                     "max_abs_Tmax_minus_lumped_K": float(np.abs(Tx - l[:, 1]).max()),
                     "max_Tmax_minus_Tmean_K": float((s[:, 2] - s[:, 3]).max()),
                     "resolved_peak_C": rr["peak"]["Tmax_C"], "lumped_peak_C": lr["peak"]["T_C"],
                     "resolved_band_entry_s": rr["cross_s"], "lumped_band_entry_s": lr["cross_s"],
                     "energy_residual_rel": rr["energy_residual_rel"], "pass_1K": bool(np.abs(Tm - l[:, 1]).max() < 1.0)}
        print(name, json.dumps(out[name], default=float), flush=True)
        json.dump(out, open(path, "w"), indent=1, default=float)
    # energy closure over every Stage 2 run
    res = {}
    for f in sorted(glob.glob(os.path.join(a.out, "stage2", "*.json"))):
        d = json.load(open(f))
        res[d["case"]] = d["resolved"]["energy_residual_rel"]
    out["energy_residual_rel_stage2_runs"] = res
    out["energy_residual_max_abs"] = max((abs(v) for v in res.values()), default=None)
    json.dump(out, open(path, "w"), indent=1, default=float)
    print("energy residuals", res)


if __name__ == "__main__":
    main()
