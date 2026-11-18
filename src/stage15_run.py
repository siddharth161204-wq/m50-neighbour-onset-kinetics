"""Stage 15 runs of the three-dimensional model (DECISIONS.md D172, D177): the archive repeats made before the
predictions (A0.4's accounts and the sizing, kind "repeat"; their configurations and outcomes are archived records)
and Part B's registered list (B1 to B4 and V4), each run a function of the records already made.

Every run is one test of Fransson et al. with its archived trigger (stage5_t1: the triangular release of the test's
body energy E_b over 21.39 s), the central contact and tabs unless stated, 25 C, the posterior-mean kinetics unless
stated, the fresh SEI unless stated, the neighbour's reaction heat fed back one-way, both neighbours, Stage 10's five
probes of the resolved neighbour at mid-length, and a delivered energy from t = 0 through the facing half: the
archive's triangular pulse over 21.39 s, Stage 9's constant power, or B3's pulse followed by a constant power (the
hold) from the pulse's end until the run ends. The resolved neighbour's run stops at C8, the first step at which its
mean temperature reaches 255.68 C, or goes to 900 s; its hot spot's crossing (C1) is recorded and does not stop it.
The lumped twin runs to 900 s without a stop. Records go to results/stage15_runs/<id>.json (repeats to
results/stage15_repeats/) and series to results/stage15_series/<id>.npz.

Usage:
  python3 stage15_run.py repeats --worker K        # A0.4 and sizing, before the predictions
  python3 stage15_run.py list | status
  python3 stage15_run.py work --worker K [--max-minutes M]
"""
import os as _os
for _k in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "NUMBA_NUM_THREADS"):
    _os.environ.setdefault(_k, "1")

import argparse
import glob
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v12_model as V                    # noqa: E402  (unchanged)
import v12_run as RUN                    # noqa: E402  (unchanged)
import stage9_run as R9                  # noqa: E402  (unchanged)
import stage10_run as R10                # noqa: E402  (unchanged)
import stage15_inputs as IN              # noqa: E402
import stage15_model as M15              # noqa: E402
import stage15_archive as AR             # noqa: E402

RX, LP = V.RX, V.LP
RUNS = IN.RUNS
SERIES = IN.SERIES
REPEATS = os.path.join(IN.RES, "stage15_repeats")
STOP_FILE = os.path.join(IN.RES, "stage15_STOP")
MAX_SUB = 4096
PROBES = dict(R10.PROBES)                # away, side, facing, toward, side_out (Stage 10's nodes on the base mesh)


# ------------------------------------------------------------------------------------------------ specifications
def spec(name, test, deliveries, kind, h="central", kin="mean", sei0=None, shift_K=0.0, t_end=IN.T_END, refine=1.0,
         dt_scale=1.0, accounts_dt=None, stop_mean=True, search=None):
    """One run. deliveries: dicts {"shape": "tri" | "con" | "hold", "f": fraction of E_e (tri, con), "tau_s", "P_W"
    (hold), "t0_s"}; the energies are f E_e, so that a run names the same point as any archived record there."""
    t = IN.tests()[test]
    E_e = IN.e_e(test)
    dl = []
    for d in deliveries:
        d = dict(d)
        if d["shape"] in ("tri", "con"):
            d["f"] = IN.key(d["f"], 9)
            d["E_J"] = d["f"] * E_e
        dl.append(d)
    rid = f"s15_{name}"
    return {"id": rid, "stage": 15, "kind": kind, "search": search, "test": test, "kin": kin,
            "connection": t["connection"], "h": h, "g": "central", "tau": IN.TAU_TRIGGER, "E_body_J": float(t["E_b_J"]),
            "T_amb_K": IN.T_AMB, "refine": refine, "dt_scale": dt_scale, "ratio": "central", "r": IN.R_CENTRAL,
            "E_e_J": E_e, "deliveries": dl, "E_delivered_J": sum(d.get("E_J", 0.0) for d in dl), "geometry": "half",
            "sei": "aged" if sei0 is not None else "fresh", "sei0": sei0, "shift_K": float(shift_K), "models": "both",
            "stop_mean": bool(stop_mean), "t_end_s": float(t_end), "max_sub": MAX_SUB, "accounts_dt": accounts_dt}


def _pulse(d):
    if d["shape"] == "tri":
        return M15.Triangular(d["E_J"], d["tau_s"], d.get("t0_s", 0.0))
    if d["shape"] == "con":
        return M15.Constant(d["E_J"], d["tau_s"], d.get("t0_s", 0.0))
    if d["shape"] == "hold":
        return M15.Hold(d["P_W"], d["t0_s"], d["t_until_s"])
    raise ValueError(d["shape"])


class Context(R9.Context):
    def probes(self, model, refine):
        if refine == 1.0:
            return dict(PROBES)
        return {"away": model.probes["away"], "toward": model.probes["toward"]}


# ------------------------------------------------------------------------------------------------ one run
def run_one(sp, ctx, keep_series=True):
    t_start = time.time()
    t1f, t1data, T1max_C, tT1max = ctx.history(sp)
    kin, draw = ctx.kinetics(sp["kin"])
    g_pos, g_neg = V.tabs(sp["connection"], V.G_TAB[sp["g"]])
    model = ctx.model(sp["h"], sp["refine"])
    share = ctx.share(sp["h"], sp["refine"])
    names = []
    src_r, src_l = [], []
    for j, d in enumerate(sp["deliveries"]):
        nm = "delivery" if j == 0 else f"delivery{j + 1}"
        if d["shape"] == "hold":
            d = dict(d, t_until_s=max(sp["t_end_s"], IN.T_END))      # both neighbours: the lumped twin runs to 900 s
        if d.get("E_J", 1.0) > 0.0 and d.get("P_W", 1.0) > 0.0:
            src_r.append(M15.Source(nm, _pulse(d), share))
            src_l.append(M15.Source(nm, _pulse(d)))
            names.append(nm)
    probes = ctx.probes(model, sp["refine"])
    saved = (RX.DT_BASE, RX.DT_TARGET, RX.DT_ACCEPT)
    if sp["dt_scale"] != 1.0:
        RX.DT_BASE, RX.DT_TARGET, RX.DT_ACCEPT = (x * sp["dt_scale"] for x in saved)
    try:
        r = M15.run_resolved15(model, t1f, g_pos, g_neg, kin=kin, t_amb=sp["T_amb_K"], t_end=sp["t_end_s"],
                               stop_level=None, probes=probes, keep_series=keep_series,
                               max_facts=6 if sp["refine"] == 1.0 else 2, sources=src_r, max_sub=sp["max_sub"],
                               sei0=sp["sei0"], stop_mean=IN.T_LEVEL if sp["stop_mean"] else None,
                               shift_K=sp["shift_K"], accounts_dt=sp["accounts_dt"], rxn_mark_J=IN.HALF_RXN_J)
        lr = M15.run_lumped15(t1f, g_pos + g_neg, g_link=V.g_contact(V.H_CONTACT[sp["h"]]), f_view=V.F_TOUCH,
                              kin=kin, t_amb=sp["T_amb_K"], t_end=IN.T_END, stop_level=None, sources=src_l,
                              max_sub=sp["max_sub"], sei0=sp["sei0"], shift_K=sp["shift_K"],
                              accounts_dt=sp["accounts_dt"])
    finally:
        RX.DT_BASE, RX.DT_TARGET, RX.DT_ACCEPT = saved
    rec = dict(sp)
    rec.update({"draw": draw, "h_c_W_m2K": V.H_CONTACT[sp["h"]], "G_tab_W_K": V.G_TAB[sp["g"]],
                "G_contact_W_K": V.g_contact(V.H_CONTACT[sp["h"]]), "g_pos_W_K": g_pos, "g_neg_W_K": g_neg,
                "T1max_C": T1max_C, "t_T1max_s": tT1max, "n_nodes": int(model.C.size)})
    sm = r["stop_mean"]
    t_c8 = sm["t_s"] if sm else None
    pt = r["probe_t"]
    far = r["probe_T"]["away"] - IN.K0
    fj = AR.far_face_jump(pt, far, t_c8)
    at = lambda x: float(np.interp(x, pt, far)) if x <= pt[-1] + 1e-9 else None
    mt, mT = r["mean_steps"]
    t_x = r["cross_s"]["T_onset_low"]
    res = {"C8": t_c8 is not None, "t_C8_s": t_c8, "stop_mean": sm, "t_end_s": r["t_end_s"],
           "propagated": t_x is not None, "t_prop_s": t_x, "cross_s": r["cross_s"],
           "peak_hottest_C": r["peak"]["Tmax_C"], "t_peak_hottest_s": r["peak"]["t_s"],
           "where_peak": model.where(r["peak"]["imax"]), "peak_mean_C": r["peak"]["Tmean_C"],
           "t_peak_mean_s": float(mt[int(np.argmax(mT))]), "mean_end_C": float(mT[-1] - IN.K0),
           "probe_peak": r["probe_peak"], "in_rxn_J": r["energy_J"]["in_rxn"], "t_rxn_mark_s": r["t_rxn_mark_s"],
           "far_jump": ({"t_s": fj[0], "T_C": fj[1], "rule": fj[2]} if fj else None),
           "far_at_45_C": at(45.0), "far_at_271.5_C": at(IN.T_PROP_FIG_S),
           "energy_J": r["energy_J"], "stored_J": r["stored_J"], "net_in_J": r["net_in_J"],
           "energy_residual_rel": r["energy_residual_rel"], "sources": r["sources"], "steps": r["steps"],
           "rejected": r["rejected"], "max_implicit_nodes": r["max_implicit_nodes"],
           "steps_with_max_sub": r["steps_with_max_sub"],
           "implicit_node_steps_with_max_sub": r["implicit_node_steps_with_max_sub"],
           "max_local_reaction_heating_K_per_s": r["max_local_reaction_heating_K_per_s"],
           "conversion_volume_mean_end": r["conversion_volume_mean_end"], "probe_where":
           {k: model.where(v) for k, v in probes.items()}}
    t_xl = lr["cross_s"]["T_onset_low"]
    rec["resolved"] = res
    rec["lumped"] = {"propagated": t_xl is not None, "t_prop_s": t_xl, "peak_C": lr["peak"]["T_C"],
                     "t_peak_s": lr["peak"]["t_s"], "reaction_heat_J": lr["reaction_heat_J"],
                     "t_end_s": lr["t_end_s"], "energy_J": lr["energy_J"],
                     "energy_residual_rel": lr["energy_residual_rel"], "conversion_end": lr["conversion_end"],
                     "cross_s": lr["cross_s"], "sources": lr["sources"], "stored_J": lr["stored_J"],
                     "net_in_J": lr["net_in_J"]}
    series = {"t1_t": t1data[:, 0], "t1_T1_C": t1data[:, 1], "t1_T2_C": t1data[:, 2]}
    s = r["series"]
    series.update({"t": s[:, 0], "T1": s[:, 1], "Tmax": s[:, 2], "Tmean": s[:, 3], "imax": s[:, 4].astype(int),
                   "mean_step_t": mt, "mean_step_T": mT, "probe_t": pt,
                   "t_lumped": lr["series"][:, 0], "T_lumped": lr["series"][:, 1]})
    for k, v in r["probe_T"].items():
        series["probe_" + k] = v
    if r["accounts"] is not None:
        series["acc_res_keys"] = np.array(r["accounts"]["keys"])
        series["acc_res"] = r["accounts"]["rows"]
        series["acc_lum_keys"] = np.array(lr["accounts"]["keys"])
        series["acc_lum"] = lr["accounts"]["rows"]
    rec["wall_s"] = time.time() - t_start
    return rec, series


def summary(rec):
    if rec.get("failed"):
        return f"{rec['id']}: FAILED {rec['error']}"
    p = rec["resolved"]
    c8 = "C8 %.1f s" % p["t_C8_s"] if p["C8"] else "no C8 (mean peak %.1f C)" % p["peak_mean_C"]
    return f"{rec['id']}: {c8}; hot spot peak {p['peak_hottest_C']:.1f} C; {rec['wall_s']:.0f} s"


# ------------------------------------------------------------------------------------------------ the repeats
ARCHIVE_REPEATS = (
    # A0.4: both neighbours' accounts against time with no delivery (Stage 10's records, run to the same end)
    ("acc_PT_Exp4", "s10_none_fresh_hcentral_M50_PT_Exp4_f0.000000000_t332", "M50_PT_Exp4", [], 332.0, False),
    ("acc_PP_Exp3", "s10_none_fresh_hcentral_M50_PP_Exp3_f0.000000000_t900", "M50_PP_Exp3", [], 900.0, False),
    ("acc_ST_Exp2", "s10_none_fresh_hcentral_M50_ST_Exp2_f0.000000000_t900", "M50_ST_Exp2", [], 900.0, False),
    # sizing: an archived run that runs away (C8 at 263.2 s), repeated with the stop at C8
    ("size_PT_Exp4_con240", "s10_con240_fresh_hcentral_M50_PT_Exp4_f0.053125000_t332", "M50_PT_Exp4",
     [{"shape": "con", "f": 0.053125, "tau_s": 240.0, "t0_s": 0.0}], 332.0, True),
    # sizing and reading 5's run: the 21.39 s delivery of 5,045 J, to its archived end
    ("size_PT_Exp4_tri21", "s10_tri21_fresh_hcentral_M50_PT_Exp4_f0.040625000_t332", "M50_PT_Exp4",
     [{"shape": "tri", "f": 0.040625, "tau_s": IN.TAU_TRIGGER, "t0_s": 0.0}], 332.0, True),
)


def repeat_specs():
    out = []
    for name, arch, test, dl, t_end, stop in ARCHIVE_REPEATS:
        sp = spec("rep_" + name, test, dl, "repeat", t_end=t_end, stop_mean=stop,
                  accounts_dt=0.5 if name.startswith("acc") else None)
        sp["archived_id"] = arch
        out.append(sp)
    return out


def _write(path_dir, rec, series):
    os.makedirs(path_dir, exist_ok=True)
    os.makedirs(SERIES, exist_ok=True)
    if series is not None:
        np.savez_compressed(os.path.join(SERIES, rec["id"] + ".npz"), **series)
    path = os.path.join(path_dir, rec["id"] + ".json")
    tmp = path + f".tmp{os.getpid()}"
    with open(tmp, "w") as fh:
        json.dump(rec, fh, indent=1, default=float)
    os.replace(tmp, path)


def work_list(specs, out_dir, worker, label, max_minutes=None, wait_s=5.0):
    os.makedirs(out_dir, exist_ok=True)
    ctx = Context()
    machine = RUN.machine_info(label)
    done = 0
    t0 = time.time()
    for sp in specs:
        if os.path.exists(STOP_FILE):
            break
        if max_minutes is not None and time.time() - t0 > 60.0 * max_minutes:
            break
        path = os.path.join(out_dir, sp["id"] + ".json")
        claim = path[:-5] + ".claim"
        if os.path.exists(path) or not RUN._claim(claim, worker):
            continue
        st = RUN._utc()
        rec = series = None
        errors = []
        for attempt in (1, 2):                   # a step that fails twice stops its chain (D176 (4))
            try:
                rec, series = run_one(sp, ctx)
                break
            except Exception as exc:
                import traceback
                RX.DT_BASE, RX.DT_TARGET, RX.DT_ACCEPT = 0.1, 1.0, 4.0
                errors.append({"attempt": attempt, "error": repr(exc), "traceback": traceback.format_exc()})
                print(f"{RUN._utc()} {sp['id']}: attempt {attempt} failed: {exc!r}", flush=True)
        if rec is None:
            rec, series = dict(sp), None
            rec.update({"failed": True, "error": errors[-1]["error"], "attempts": errors})
        elif errors:
            rec["failed_attempts"] = errors
        rec.update({"started_utc": st, "finished_utc": RUN._utc(), "machine": machine, "worker": worker})
        _write(out_dir, rec, series)
        RUN._unclaim(claim)
        done += 1
        print(f"{RUN._utc()} {summary(rec)}", flush=True)
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--worker", type=int, default=0)
    ap.add_argument("--max-minutes", type=float, default=None)
    a = ap.parse_args()
    if a.cmd == "repeats":
        work_list(repeat_specs(), REPEATS, a.worker, f"stage15-{a.worker}", a.max_minutes)
    else:
        import stage15_partb as PB
        PB.main(a)


if __name__ == "__main__":
    main()
