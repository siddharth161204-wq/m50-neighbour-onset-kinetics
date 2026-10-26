#!/usr/bin/env python3
"""Sizing of the Stage 8 runs (DECISIONS.md D83 (5)), made before the predictions were public.

Every case has cell 1 held at the ambient temperature, 25 C (no trigger), so it lies outside every Stage 8
configuration: the neighbour at the central contact, central tabs, parallel, the posterior-mean kinetics, the fresh SEI,
the reaction heat fed back, receiving a made-up delivered energy over 21.39 s from t = 0 through the facing half of its
can, with the sub-step limit of D68 (3) from t = 0, and stopped at 255.7 C (D35) or at its end.
  base3    3 kJ, base mesh, resolved and lumped, to 900 s;
  base20   20 kJ, base mesh, resolved and lumped, to 900 s;
  split20  20 kJ, the split cell of Part D with the gas layer, resolved only, to 60 s;
  fine3    3 kJ, every mesh spacing halved, resolved only, to 5 s (the cost per step of V3's refined run).
Writes provenance/stage8_cost_test_<case>.json.
Usage: python3 stage8_cost_test.py CASE
"""
import os as _os
for _k in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "NUMBA_NUM_THREADS"):
    _os.environ.setdefault(_k, "1")
import json, os, resource, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v12_model as V                    # noqa: E402
import stage7_model as M7                # noqa: E402
import stage8_model as M8                # noqa: E402
import stage8_inputs as IN               # noqa: E402

OUT = os.path.join(HERE, "..", "provenance")
CASES = {"base3": (3000.0, "base", 1.0, 900.0), "base20": (20000.0, "base", 1.0, 900.0),
         "split20": (20000.0, "split", 1.0, 60.0), "fine3": (3000.0, "base", 2.0, 5.0)}


def main(case):
    E, kind, refine, t_end = CASES[case]
    t0 = time.time()
    model = V.Cell2Contact(V.H_CONTACT["central"], refine=refine)
    tau = IN.tau_median_s()
    sh = M8.share_surface(model, "half")
    g_pos, g_neg = V.tabs("parallel", V.G_TAB["central"])
    Ta = V.LP.T_AMB
    t1 = lambda t: Ta
    prog = []
    last = [time.time()]

    def progress(t, Tmax, Tmean, dt):
        if time.time() - last[0] >= 30.0:
            last[0] = time.time()
            prog.append({"t_s": round(t, 4), "Tmax_C": round(Tmax - 273.15, 2), "Tmean_C": round(Tmean - 273.15, 2),
                         "dt_s": dt, "wall_s": round(time.time() - t0, 1)})
            print(json.dumps(prog[-1]), flush=True)

    out = {"case": case, "E_J": E, "tau_s": tau, "geometry": "half", "refine": refine, "t_end_s": t_end,
           "model": kind, "n_nodes": int(model.C.size), "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if kind == "base":
        src = [M8.Source("delivery", M7.Event(E, tau, 0.0), sh)]
        r = M8.run_resolved(model, t1, g_pos, g_neg, t_end=t_end, probes=model.probes, stop_level=V.LEVEL_PROP,
                            sources=src, max_sub=4096, progress=progress, max_facts=6 if refine == 1.0 else 2)
    else:
        S = M8.SplitCell(model)
        out["n_nodes"] = int(S.C.size)
        src = [M8.Source("delivery", M7.Event(E, tau, 0.0), S.move(sh))]
        def progress_split(t, Tmax, Tcan, dt, nf):
            if time.time() - last[0] >= 30.0:
                last[0] = time.time()
                prog.append({"t_s": round(t, 4), "Tmax_roll_C": round(Tmax - 273.15, 2), "Tcan_max_C": round(Tcan - 273.15, 2),
                             "dt_s": dt, "factorisations": nf, "wall_s": round(time.time() - t0, 1)})
                print(json.dumps(prog[-1]), flush=True)

        r = M8.run_resolved_split(S, t1, g_pos, g_neg, t_end=t_end, stop_level=V.LEVEL_PROP, sources=src,
                                  max_sub=4096, layer=True, progress=progress_split)
    out["resolved"] = {"wall_s": time.time() - t0, "t_end_s": r["t_end_s"], "steps": r["steps"],
                       "rejected": r["rejected"], "stop": r["stop"], "peak": r["peak"],
                       "energy_residual_rel": r["energy_residual_rel"], "delivered_J": r["sources"]["delivery"]["delivered_J"],
                       "max_implicit_nodes": r["max_implicit_nodes"], "in_rxn_J": r["energy_J"]["in_rxn"],
                       "probe_peak": r.get("probe_peak"), "progress": prog}
    for k in ("can_peak", "factorisations", "interface_node_steps"):
        if k in r:
            out["resolved"][k] = r[k]
    if kind == "base" and refine == 1.0:
        t2 = time.time()
        lr = M8.run_lumped(t1, g_pos + g_neg, g_link=V.g_contact(V.H_CONTACT["central"]), f_view=V.F_TOUCH,
                           t_end=t_end, stop_level=V.LEVEL_PROP, sources=[M8.Source("delivery", M7.Event(E, tau, 0.0))],
                           max_sub=4096)
        out["lumped"] = {"wall_s": time.time() - t2, "stop": lr["stop"], "peak": lr["peak"],
                         "energy_residual_rel": lr["energy_residual_rel"],
                         "delivered_J": lr["sources"]["delivery"]["delivered_J"], "reaction_heat_J": lr["reaction_heat_J"]}
    out["largest_memory_MB"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    out["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    json.dump(out, open(os.path.join(OUT, f"stage8_cost_test_{case}.json"), "w"), indent=1, default=float)
    print(json.dumps({k: v for k, v in out.items() if k != "resolved"}, default=float))
    print(json.dumps({k: v for k, v in out["resolved"].items() if k != "progress"}, default=float))


if __name__ == "__main__":
    main(sys.argv[1])
