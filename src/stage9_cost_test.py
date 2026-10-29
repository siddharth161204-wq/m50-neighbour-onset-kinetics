#!/usr/bin/env python3
"""Sizing of the Stage 9 runs (DECISIONS.md D96 (5)), made before the predictions were public.

Every case has cell 1 held at the ambient temperature, 25 C (no trigger), so it lies outside every Stage 9
configuration: the neighbour at the central contact, central tabs, parallel, the posterior-mean kinetics, the fresh SEI,
the reaction heat fed back, receiving a made-up delivered energy from t = 0 through the facing half of its can, with the
sub-step limit of D68 (3) from t = 0, and not stopped at 255.7 C (the runs of the thermocouple's peak go on, D92):
  con20_240     20 kJ at constant power over 240 s, base mesh, resolved and lumped, to 900 s;
  con135_360    135 kJ at constant power over 360 s, base mesh, resolved and lumped, to 900 s;
  tri135        135 kJ as Stage 8's triangular pulse over 21.39 s, base mesh, resolved and lumped, to 900 s.
Writes provenance/stage9_cost_test_<case>.json.
Usage: python3 stage9_cost_test.py CASE
"""
import os as _os
for _k in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "NUMBA_NUM_THREADS"):
    _os.environ.setdefault(_k, "1")
import json, os, resource, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v12_model as V                    # noqa: E402
import stage8_inputs as IN8              # noqa: E402
import stage9_model as M9                # noqa: E402

OUT = os.path.join(HERE, "..", "provenance")
CASES = {"con20_240": (20000.0, "constant", 240.0), "con135_360": (135000.0, "constant", 360.0),
         "tri135": (135000.0, "triangular", None)}


def main(case):
    E, shape, tau = CASES[case]
    tau = IN8.tau_median_s() if tau is None else tau
    t0 = time.time()
    model = V.Cell2Contact(V.H_CONTACT["central"], refine=1.0)
    sh = M9.share_surface(model, "half")
    g_pos, g_neg = V.tabs("parallel", V.G_TAB["central"])
    Ta = V.LP.T_AMB
    t1 = lambda t: Ta
    pulse = (M9.Constant if shape == "constant" else M9.Triangular)
    prog, last = [], [time.time()]

    def progress(t, Tmax, Tmean, dt):
        if time.time() - last[0] >= 30.0:
            last[0] = time.time()
            prog.append({"t_s": round(t, 4), "Tmax_C": round(Tmax - 273.15, 2), "Tmean_C": round(Tmean - 273.15, 2),
                         "dt_s": dt, "wall_s": round(time.time() - t0, 1)})
            print(json.dumps(prog[-1]), flush=True)

    out = {"case": case, "E_J": E, "shape": shape, "tau_s": tau, "geometry": "half", "t_end_s": 900.0,
           "n_nodes": int(model.C.size), "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    r = M9.run_resolved(model, t1, g_pos, g_neg, t_end=900.0, probes=model.probes, stop_level=None,
                        sources=[M9.Source("delivery", pulse(E, tau, 0.0), sh)], max_sub=4096, progress=progress)
    out["resolved"] = {"wall_s": time.time() - t0, "t_end_s": r["t_end_s"], "steps": r["steps"],
                       "rejected": r["rejected"], "cross_s": r["cross_s"], "peak": r["peak"],
                       "energy_residual_rel": r["energy_residual_rel"], "delivered_J": r["sources"]["delivery"]["delivered_J"],
                       "max_implicit_nodes": r["max_implicit_nodes"], "in_rxn_J": r["energy_J"]["in_rxn"],
                       "probe_peak": r.get("probe_peak"), "progress": prog}
    t2 = time.time()
    lr = M9.run_lumped(t1, g_pos + g_neg, g_link=V.g_contact(V.H_CONTACT["central"]), f_view=V.F_TOUCH, t_end=900.0,
                       stop_level=None, sources=[M9.Source("delivery", pulse(E, tau, 0.0))], max_sub=4096)
    out["lumped"] = {"wall_s": time.time() - t2, "cross_s": lr["cross_s"], "peak": lr["peak"],
                     "energy_residual_rel": lr["energy_residual_rel"],
                     "delivered_J": lr["sources"]["delivery"]["delivered_J"], "reaction_heat_J": lr["reaction_heat_J"]}
    out["largest_memory_MB"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    out["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    json.dump(out, open(os.path.join(OUT, f"stage9_cost_test_{case}.json"), "w"), indent=1, default=float)
    print(json.dumps({k: v for k, v in out.items() if k != "resolved"}, default=float))
    print(json.dumps({k: v for k, v in out["resolved"].items() if k != "progress"}, default=float))


if __name__ == "__main__":
    main(sys.argv[1])
