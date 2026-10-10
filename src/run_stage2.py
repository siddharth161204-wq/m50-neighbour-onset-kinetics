#!/usr/bin/env python3
"""Stage 2: reactive resolved cell 2 and reactive lumped node for the registered cases (DECISIONS.md D12 to D15).

Usage: python3 run_stage2.py --out ../results --cases max:10:0.5 max:30:0.5 max:10:0.2 max:30:0.2 median:30:0.5
Each case writes results/stage2/<case>.json and results/stage2/<case>.npz. Several processes may run at once with
different --cases. Options for the checks: --tag (file suffix), --dt-scale (DT_TARGET and DT_ACCEPT multiplied),
--no-reaction (the same loops without the source, which must reproduce the archived passive series).
"""
import argparse, json, os, time
import numpy as np
import reactive as RX
import lumped_two_cell as LP

PUB = os.path.join(RX.EXT, "..")
E = dict(zip(("min", "median", "max"), sorted(LP.E_BODY_LIST)))


def case_name(en, tau, g):
    return f"two_E{int(round(E[en]))}_tau{int(tau)}_G{g:g}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="../results")
    ap.add_argument("--cases", nargs="+", required=True)
    ap.add_argument("--tag", default="")
    ap.add_argument("--dt-scale", type=float, default=1.0)
    ap.add_argument("--no-reaction", action="store_true")
    ap.add_argument("--t-end", type=float, default=900.0)
    a = ap.parse_args()
    RX.DT_TARGET *= a.dt_scale
    RX.DT_ACCEPT *= a.dt_scale
    from resolved_cell2 import Cell2Model, t1_interpolator
    outdir = os.path.join(a.out, "stage2"); os.makedirs(outdir, exist_ok=True)
    model = Cell2Model(1.0)
    for spec in a.cases:
        en, tau, g = spec.split(":"); tau, g = float(tau), float(g)
        name = case_name(en, tau, g) + a.tag
        t1f, _ = t1_interpolator(os.path.join(PUB, "results", "t1_series", LP.series_name(E[en], tau, g)))
        t0 = time.time()
        last = [0.0]

        def prog(t, Tmax, Tmean, dt):
            if t - last[0] >= 10.0 - 1e-9:
                last[0] = t
                print(f"  {name} t={t:6.1f} s Tmax={Tmax - 273.15:7.2f} C Tmean={Tmean - 273.15:7.2f} C dt={dt:.2e} s "
                      f"wall={time.time() - t0:.0f} s", flush=True)
        reaction = not a.no_reaction
        rr = RX.run_resolved(model, t1f, g / 2, g / 2, t_end=a.t_end, reaction=reaction, progress=prog)
        lr = RX.run_lumped(t1f, g, t_end=a.t_end, reaction=reaction)
        lp = RX.run_lumped(t1f, g, t_end=a.t_end, reaction=False)
        arch = np.load(os.path.join(PUB, "results", "resolved_series", case_name(en, tau, g) + ".npz"))
        rec = {"case": name, "E_body_J": E[en], "tau_rel_s": tau, "G_bus_WK": g, "reaction": reaction,
               "dt_target_K": RX.DT_TARGET, "dt_accept_K": RX.DT_ACCEPT,
               "resolved": {k: v for k, v in rr.items() if k not in ("series", "T_final", "c_final")},
               "lumped_reactive": {k: v for k, v in lr.items() if k != "series"},
               "lumped_passive": {k: v for k, v in lp.items() if k != "series"},
               "passive_archived": {"Tmax_peak_C": float(arch["Tmax"].max() - 273.15), "Tmean_peak_C": float(arch["Tmean"].max() - 273.15),
                                    "T2_be_peak_C": float(arch["T2_be"].max() - 273.15)},
               "runtime_s": time.time() - t0}
        s = rr["series"]
        # the loops of this study, run without the source, must reproduce the archived passive series
        ta = arch["t_be"]
        rec["lumped_passive_vs_archived_T2_be_max_abs_K"] = float(np.abs(np.interp(ta, lp["series"][:, 0], lp["series"][:, 1]) - arch["T2_be"]).max())
        if not reaction:
            rec["resolved_passive_vs_archived_max_abs_K"] = {
                "Tmax": float(np.abs(np.interp(arch["t"], s[:, 0], s[:, 2]) - arch["Tmax"]).max()),
                "Tmean": float(np.abs(np.interp(arch["t"], s[:, 0], s[:, 3]) - arch["Tmean"]).max())}
        np.savez_compressed(os.path.join(outdir, name + ".npz"), t=s[:, 0], T1=s[:, 1], Tmax=s[:, 2], Tmean=s[:, 3],
                            imax=s[:, 4].astype(int), cat1_conv_hottest=s[:, 5], sei_conv_hottest=s[:, 6],
                            vol_frac_above_255p7=s[:, 7], t_lumped=lr["series"][:, 0], T_lumped=lr["series"][:, 1],
                            t_lumped_passive=lp["series"][:, 0], T_lumped_passive=lp["series"][:, 1])
        json.dump(rec, open(os.path.join(outdir, name + ".json"), "w"), indent=1, default=float)
        print(name, "resolved band entry", rr["cross_s"], "peak", round(rr["peak"]["Tmax_C"], 2), "| lumped band entry",
              lr["cross_s"], "peak", round(lr["peak"]["T_C"], 2), "| residual", f"{rr['energy_residual_rel']:.2e}",
              "| runtime", round(rec["runtime_s"]), "s", flush=True)


if __name__ == "__main__":
    main()
