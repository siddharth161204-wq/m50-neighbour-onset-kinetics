"""Stage 13 runs: the resolved searches of Part A4 (with A5's reaction-off runs and V2) and the lumped searches of
Part B4 (with V3), each a function of the records already made (DECISIONS.md D134, D135, D136).

Every run is one test of Fransson et al. with its archived trigger (stage5_t1: the triangular release of the test's
body energy E_b over 21.39 s, shifted by dE_body for B4's six cases), the contact at the search's level (central
unless stated), the central tabs, 25 C, the posterior-mean kinetics, the fresh SEI, the neighbour's reaction heat fed
back one-way, and a delivered energy E from t = 0 through the search's region (the facing half, the whole lateral
surface or the eighth nearest the cap) with the archive's triangular pulse over tau_d. The resolved runs stop at
255.68 C or go to 900 s; the lumped runs likewise. A5's and V2's runs switch the reaction off and do not stop.

A search's next run is read from its records: from the reduced model's value (stage13_reduced.json, registered with
the predictions), a first step of 3 %, doubled until the threshold is bracketed, then halving until the bracket is
no wider than 4 % of its midpoint (resolved) or 2 % of it or 20 J (lumped). An archived reference is halved from its
archived bracket. Records go to results/stage13_runs/<id>.json and series to results/stage13_series/<id>.npz.

Usage:
  python3 stage13_run.py list | status
  python3 stage13_run.py work --worker K [--models resolved|lumped|all]
"""
import os as _os
for _k in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "NUMBA_NUM_THREADS"):
    _os.environ.setdefault(_k, "1")
import argparse
import glob
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v12_model as V                    # noqa: E402  (unchanged)
import v12_run as RUN                    # noqa: E402  (unchanged)
import reactive as RX                    # noqa: E402  (unchanged)
import stage9_model as M9                # noqa: E402  (unchanged)
import stage9_run as R9                  # noqa: E402  (unchanged)
import stage13_inputs as IN              # noqa: E402

RUNS, SERIES = IN.RUNS, IN.SERIES
STOP_FILE = os.path.join(IN.RES, "stage13_STOP")
REDUCED = os.path.join(IN.RES, "stage13_reduced.json")
MAX_SUB = 4096


# ------------------------------------------------------------------------------------------------ specifications
def _reduced():
    return json.load(open(REDUCED))


def start_value(s, red=None):
    """The reduced model's value a search starts from: A2's f* (resolved) or B2's E* in J (lumped)."""
    red = _reduced() if red is None else red
    if s["model"] == "resolved":
        if s["geometry"] == "eighth":
            half = red[f"A2_M50_PT_Exp1_half_tau{IN.TAU_TRIGGER:.4f}_r1_dt1"]["f_star"]
            return IN.key(half * (IN.A_EIGHTH / IN.A_HALF) * 1.25)      # the half's flux per area plus 25 %
        k = f"A2_{s['test']}_{s['geometry']}_tau{s['tau_d_s']:.4f}_r1_dt1"
        return IN.key(red[k]["f_star"])
    k = f"B2_{s['test']}_tau{s['tau_d_s']:.4f}_{s['h']}_dEb{s['dE_body_J']:+.0f}"
    return round(red[k]["E_star_J"], 6)


def spec(s, x, reaction=True, stop=True, t_end=900.0, tag=""):
    """One run of search s at x (f for resolved searches, E in J for lumped ones)."""
    t = IN.tests()[s["test"]]
    E_e = IN.e_e(s["test"])
    if s["model"] == "resolved":
        f = IN.key(x)
        E = f * E_e
        xs = f"f{f:.9f}"
    else:
        E = round(float(x), 6)
        f = E / E_e
        xs = f"E{E:.6f}"
    rid = f"s13_{s['name']}_{xs}{'' if reaction else '_inert'}{'' if stop else '_ns'}{tag}"
    return {"id": rid, "stage": 13, "search": s["name"], "kind": s["kind"], "test": s["test"], "kin": "mean",
            "connection": t["connection"], "h": s["h"], "g": "central", "tau": IN.TAU_TRIGGER,
            "E_body_J": float(t["E_b_J"]) + s["dE_body_J"], "dE_body_J": s["dE_body_J"], "T_amb_K": IN.T_AMB,
            "refine": 1.0, "dt_scale": 1.0, "f": f, "ratio": "central", "r": IN.R_CENTRAL, "E_e_J": E_e,
            "E_delivered_J": E, "shape": s["shape"], "tau_d_s": s["tau_d_s"], "geometry": s["geometry"],
            "f_e": 0.0, "sei": "fresh", "sei0": None, "models": s["model"], "reaction": reaction, "stop": stop,
            "t_end_s": t_end, "max_sub": MAX_SUB}


# ------------------------------------------------------------------------------------------------ the records
def load_records():
    recs = {}
    for fn in glob.glob(os.path.join(RUNS, "*.json")):
        try:
            r = json.load(open(fn))
        except Exception:
            continue
        recs[r["id"]] = r
    return recs


def crossed(rec):
    if rec.get("failed"):
        return None
    part = rec["resolved"] if rec["models"] == "resolved" else rec["lumped"]
    return bool(part["propagated"])


def search_state(s, recs, red=None):
    """(status, next x or None, bracket (lo, hi) or None, the search's runs)."""
    mine = sorted([r for r in recs.values() if r.get("search") == s["name"] and r.get("reaction", True)
                   and r.get("stop", True)], key=lambda r: r["f"] if s["model"] == "resolved" else r["E_delivered_J"])
    xval = (lambda r: r["f"]) if s["model"] == "resolved" else (lambda r: round(r["E_delivered_J"], 6))
    done = {xval(r): crossed(r) for r in mine}
    if any(v is None for v in done.values()):
        return "failed", None, None, mine
    lo = max([x for x, c in done.items() if not c], default=None)
    hi = min([x for x, c in done.items() if c], default=None)
    resolved = s["model"] == "resolved"

    def narrow(lo, hi):
        mid = 0.5 * (lo + hi)
        if resolved:
            return hi - lo <= IN.RES_WIDTH * mid + 1e-15
        return hi - lo <= max(IN.LUM_WIDTH * mid, IN.LUM_WIDTH_J) + 1e-9

    if len(mine) >= IN.MAX_RUNS[s["model"]]:
        return "stopped (run limit)", None, (lo, hi), mine
    if s["kind"] == "refine":
        lo0, hi0 = s["ref"]
        lo = max(lo0, lo) if lo is not None else lo0
        hi = min(hi0, hi) if hi is not None else hi0
        if narrow(lo, hi):
            return "done", None, (lo, hi), mine
        return "running", IN.key(0.5 * (lo + hi)), (lo, hi), mine
    if not mine:
        x0 = start_value(s, red)
        if not resolved and x0 < IN.LUM_WIDTH_J:
            x0 = 0.0
        return "running", x0, None, mine
    if not resolved and 0.0 in done and done[0.0]:
        return "done", None, (0.0, 0.0), mine           # crosses with no delivery
    if lo is not None and hi is not None:
        if narrow(lo, hi):
            return "done", None, (lo, hi), mine
        mid = 0.5 * (lo + hi)
        return "running", (IN.key(mid) if resolved else round(mid, 6)), (lo, hi), mine
    # not yet bracketed: step away from the start, the step doubling each time
    first = min(mine, key=lambda r: r.get("started_utc", ""))
    x0 = xval(first)
    k = len(mine)                                        # steps made so far: 3 %, 6 %, 12 %, ...
    step = IN.FIRST_STEP * 2 ** (k - 1)
    if hi is not None:                                   # every run crossed: go down
        x = x0 * (1.0 - step) if step < 1.0 else 0.0
        if x <= 0.0 or (not resolved and x < IN.LUM_WIDTH_J):
            x = 0.0
        if resolved and x <= 0.0:
            x = IN.key(min(done) / 2)
    else:                                                # none crossed: go up
        x = x0 * (1.0 + step) if x0 > 0.0 else (0.005 if resolved else 50.0) * 2 ** (k - 1)
    return "running", (IN.key(x) if resolved else round(x, 6)), (lo, hi), mine


def extra_runs(recs, red=None):
    """A5 (reaction off at each new resolved search's upper end), V2 and V3, once their searches allow."""
    out = []
    lists = IN.run_lists()
    for s in lists["resolved"]:
        if s["kind"] != "search":
            continue
        st, _, br, _ = search_state(s, recs, red)
        if st == "done" and br and br[1] is not None:
            out.append(spec(s, br[1], reaction=False, stop=False, t_end=min(900.0, 2 * s["tau_d_s"] + 150.0)))
    ref = [s for s in lists["resolved"] if s["name"] == "A4ref_PT_Exp1_tri21"][0]
    out.append(spec(ref, 0.15625, reaction=False, stop=False, t_end=900.0, tag="_V2"))
    red = _reduced() if red is None else red
    for test in ("M50_PT_Exp1", "M50_ST_Exp3", "M50_PP_Exp3"):
        s = {"name": f"V3_{test[4:]}", "model": "lumped", "test": test, "shape": "tri", "tau_d_s": IN.TAU_TRIGGER,
             "geometry": "half", "h": "central", "dE_body_J": 0.0, "kind": "check", "ref": None}
        E = red[f"B2_{test}_tau{IN.TAU_TRIGGER:.4f}_central_dEb+0"]["E_star_J"]
        out.append(spec(s, E, reaction=False, stop=False, t_end=900.0))
    return out


def pending_runs(recs, models="all"):
    red = _reduced()
    lists = IN.run_lists()
    out = []
    for kind in ("resolved", "lumped"):
        if models not in ("all", kind):
            continue
        for s in lists[kind]:
            st, x, br, mine = search_state(s, recs, red)
            if st == "running":
                sp = spec(s, x)
                if sp["id"] not in recs:
                    out.append(sp)
    for sp in extra_runs(recs, red):
        if sp["id"] not in recs and models in ("all", sp["models"]):
            out.append(sp)
    return out


# ------------------------------------------------------------------------------------------------ one run
class Context(R9.Context):
    def share13(self, h, geometry):
        key = ("s13", h, geometry)
        if key not in self.shares:
            self.shares[key] = IN.share_surface(self.model(h, 1.0), geometry)
        return self.shares[key]


def _pulse(sp):
    return M9.Triangular(sp["E_delivered_J"], sp["tau_d_s"], 0.0)


def run_one(sp, ctx, keep_series=True):
    t_start = time.time()
    t1f, t1data, T1max_C, tT1max = ctx.history(sp)
    kin, draw = ctx.kinetics(sp["kin"])
    g_pos, g_neg = V.tabs(sp["connection"], V.G_TAB[sp["g"]])
    stop = V.LEVEL_PROP if sp["stop"] else None
    rec = dict(sp)
    rec.update({"h_c_W_m2K": V.H_CONTACT[sp["h"]], "G_contact_W_K": V.g_contact(V.H_CONTACT[sp["h"]]),
                "g_pos_W_K": g_pos, "g_neg_W_K": g_neg, "T1max_C": T1max_C, "t_T1max_s": tT1max,
                "resolved": None, "lumped": None})
    series = {"t1_t": t1data[:, 0], "t1_T1_C": t1data[:, 1]}
    if sp["models"] == "resolved":
        model = ctx.model(sp["h"], 1.0)
        src = [M9.Source("delivery", _pulse(sp), ctx.share13(sp["h"], sp["geometry"]))] \
            if sp["E_delivered_J"] > 0.0 else []
        r = M9.run_resolved(model, t1f, g_pos, g_neg, kin=kin, t_amb=sp["T_amb_K"], t_end=sp["t_end_s"],
                            reaction=sp["reaction"], stop_level=stop, probes=model.probes, keep_series=keep_series,
                            max_facts=6, sources=src, max_sub=sp["max_sub"], sei0=sp["sei0"])
        t_x = r["cross_s"]["T_onset_low"]
        res = {"propagated": t_x is not None, "t_prop_s": t_x, "stopped": r["stop"] is not None,
               "t_end_s": r["t_end_s"], "steps": r["steps"], "energy_residual_rel": r["energy_residual_rel"],
               "peak_hottest_C": r["peak"]["Tmax_C"], "t_peak_hottest_s": r["peak"]["t_s"],
               "where_peak": model.where(r["peak"]["imax"]), "peak_mean_C": r["peak"]["Tmean_C"],
               "probe_peak": r["probe_peak"], "in_rxn_J": r["energy_J"]["in_rxn"], "cross_s": r["cross_s"],
               "energy_J": r["energy_J"], "stored_J": r["stored_J"], "net_in_J": r["net_in_J"],
               "sources": r["sources"], "max_local_reaction_heating_K_per_s": r.get("max_local_reaction_heating_K_per_s"),
               "conversion_volume_mean_end": r.get("conversion_volume_mean_end"), "n_nodes": int(model.C.size)}
        if r["stop"] is not None:
            res.update({"where": r["stop"]["where"], "mean_at_prop_C": r["stop"]["Tmean_C"]})
        rec["resolved"] = res
        s = r["series"]
        series.update({"t": s[:, 0], "T1": s[:, 1], "Tmax": s[:, 2], "Tmean": s[:, 3], "imax": s[:, 4].astype(int)})
    else:
        src = [M9.Source("delivery", _pulse(sp))] if sp["E_delivered_J"] > 0.0 else []
        lr = M9.run_lumped(t1f, g_pos + g_neg, g_link=V.g_contact(V.H_CONTACT[sp["h"]]), f_view=V.F_TOUCH, kin=kin,
                           t_amb=sp["T_amb_K"], t_end=sp["t_end_s"], reaction=sp["reaction"], stop_level=stop,
                           sources=src, max_sub=sp["max_sub"], sei0=sp["sei0"])
        t_xl = lr["cross_s"]["T_onset_low"]
        rec["lumped"] = {"propagated": t_xl is not None, "t_prop_s": t_xl, "stopped": lr["stop"] is not None,
                         "peak_C": lr["peak"]["T_C"], "t_peak_s": lr["peak"]["t_s"],
                         "reaction_heat_J": lr["reaction_heat_J"], "t_end_s": lr["t_end_s"],
                         "energy_J": lr["energy_J"], "energy_residual_rel": lr["energy_residual_rel"],
                         "conversion_end": lr["conversion_end"], "cross_s": lr["cross_s"], "sources": lr["sources"],
                         "stored_J": lr["stored_J"], "net_in_J": lr["net_in_J"]}
        series.update({"t_lumped": lr["series"][:, 0], "T_lumped": lr["series"][:, 1]})
    rec["wall_s"] = time.time() - t_start
    return rec, series


def summary(rec):
    if rec.get("failed"):
        return f"{rec['id']}: FAILED {rec['error']}"
    p = rec["resolved"] or rec["lumped"]
    pk = p.get("peak_hottest_C", p.get("peak_C"))
    return (f"{rec['id']}: {'crossed %.1f s' % p['t_prop_s'] if p['propagated'] else 'no crossing'} "
            f"(peak {pk:.2f} C); {rec['wall_s']:.0f} s")


def work(worker, models="all", wait_s=10.0, max_minutes=None):
    """Make runs until none is left; with max_minutes, start no new run after that many minutes (so that a worker
    held by a time limit ends between runs, never inside one)."""
    os.makedirs(RUNS, exist_ok=True)
    os.makedirs(SERIES, exist_ok=True)
    ctx = Context()
    machine = RUN.machine_info(f"stage13-{worker}")
    done = 0
    t_start = time.time()
    while True:
        if os.path.exists(STOP_FILE):
            print(f"{RUN._utc()} worker {worker}: stop file, {done} runs", flush=True)
            return done
        if max_minutes is not None and time.time() - t_start > 60.0 * max_minutes:
            print(f"{RUN._utc()} worker {worker}: {max_minutes} minutes, ending between runs ({done} runs)",
                  flush=True)
            return done
        recs = load_records()
        pend = pending_runs(recs, models)
        if not pend:
            if [f for f in os.listdir(RUNS) if f.endswith(".claim")]:
                time.sleep(wait_s)
                continue
            print(f"{RUN._utc()} worker {worker}: nothing left ({done} runs)", flush=True)
            return done
        started = False
        for sp in pend:
            claim = os.path.join(RUNS, sp["id"] + ".claim")
            if not RUN._claim(claim, worker):
                continue
            path = os.path.join(RUNS, sp["id"] + ".json")
            if os.path.exists(path):
                RUN._unclaim(claim)
                continue
            started = True
            st = RUN._utc()
            try:
                rec, series = run_one(sp, ctx)
            except Exception as exc:
                import traceback
                RX.DT_BASE, RX.DT_TARGET, RX.DT_ACCEPT = 0.1, 1.0, 4.0
                rec, series = dict(sp), None
                rec.update({"failed": True, "error": repr(exc), "traceback": traceback.format_exc()})
            rec.update({"started_utc": st, "finished_utc": RUN._utc(), "machine": machine, "worker": worker})
            if series is not None:
                np.savez_compressed(os.path.join(SERIES, sp["id"] + ".npz"), **series)
            tmp = path + f".tmp{os.getpid()}"
            with open(tmp, "w") as fh:
                json.dump(rec, fh, indent=1, default=float)
            os.replace(tmp, path)
            RUN._unclaim(claim)
            done += 1
            print(f"{RUN._utc()} {summary(rec)}", flush=True)
            break
        if not started:
            time.sleep(wait_s)


def status():
    recs = load_records()
    red = _reduced()
    for kind, lst in IN.run_lists().items():
        for s in lst:
            st, x, br, mine = search_state(s, recs, red)
            print(f"{s['name']:32s} {st:22s} runs {len(mine):2d} bracket {br} next {x}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--worker", type=int, default=1)
    ap.add_argument("--models", default="all")
    ap.add_argument("--max-minutes", type=float, default=None)
    a = ap.parse_args()
    if a.cmd == "work":
        work(a.worker, a.models, max_minutes=a.max_minutes)
    elif a.cmd == "status":
        status()
    elif a.cmd == "list":
        for sp in pending_runs(load_records(), a.models):
            print(sp["id"])
