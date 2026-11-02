#!/usr/bin/env python3
"""Stage 11 runs (predictions_stage11.md; DECISIONS.md D111 to D117).

Every run is a Stage 10 run (`stage9_model`'s loops, Stage 9's inputs, Stage 10's five probes): one test of Fransson et
al. with its Stage 7 trigger, the central tabs, 25 C, the fresh SEI with the reaction heat fed back one-way, and a
fraction f of the test's ejected energy delivered through the facing half of the can as Stage 8's triangular pulse over
21.39 s. What Stage 11 adds, by the brief:
  - the kinetics of one of Stage 3's joint posterior draws in place of the posterior mean ("kin": the draw's number;
    D111 (1)), in both neighbours;
  - the neighbour's roll at one of Stage 3's thermal draws in place of the central properties ("thermal": the draw's
    label; D111 (2)): its conductivity across and along the layers in the resolved neighbour, and its heat capacity in
    both neighbours, the trigger's history held at the central properties as Stage 3b held cell 1's (D27 (g), D112 (2)).

  Part A: f*(C1) and f*(C2) of the four tests under each kinetic draw; Part B: the same under each thermal draw
  (`threshold_state`, D113). Part C1: the far face's peak at f = 0 of the five low-maximum tests under each thermal
  draw, and at the high contact where Stage 7's run stopped (D114 (1)); C2: M50_PT_Exp1's f_max under the smallest
  radial conductivity and at the low contact (Stage 9's search); E3's decisive runs at the smallest f_t (D114 (3)).
  Part D: the whole-cell crossing of the nine propagated tests at their f_t(C2) under each kinetic draw (D115). V4:
  three earlier records repeated at the posterior mean (D116 (4)).

Records go to results/stage11_runs/<id>.json and series to results/stage11_series/<id>.npz.

Usage:
  python3 stage11_run.py list | chains | status | reset-claims
  python3 stage11_run.py work --worker K --label NAME
"""
import os as _os
for _k in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "NUMBA_NUM_THREADS"):
    _os.environ.setdefault(_k, "1")      # D43 (4): one thread per library; set before numpy and numba load
import argparse, contextlib, glob, hashlib, json, os, signal, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v12_model as V                    # noqa: E402  (unchanged)
import v12_run as RUN                    # noqa: E402  (unchanged)
import reactive as RX                    # noqa: E402  (unchanged)
import stage9_run as R9                  # noqa: E402  (unchanged)
import stage9_model as M9                # noqa: E402  (unchanged)
import stage9_search as S9               # noqa: E402  (unchanged)
import stage8_search as SR8              # noqa: E402  (unchanged)
import stage10_inputs as IN10            # noqa: E402  (unchanged)
import stage11_inputs as IN              # noqa: E402

LP = V.LP
RES = os.path.join(HERE, "..", "results")
TAG = os.environ.get("STAGE11_RUNS_TAG", "")
RUNS = os.path.join(RES, "stage11_runs" + TAG)
SERIES = os.path.join(RES, "stage11_series" + TAG)
STOP_FILE = os.path.join(RES, "stage11_STOP")
RUN_LIMIT_MIN = 1440.0                   # as D96 (1): a run that takes longer is recorded as failed
CENTRAL = {"k_radial": LP.K_RADIAL, "k_axial": LP.K_AXIAL, "C_cell": LP.C_CELL}
key = SR8.key


def thermal_params(label):
    return dict(CENTRAL) if label == "central" else IN.thermal_draws()[label]


@contextlib.contextmanager
def heat_capacity(C):
    """The neighbour's heat capacity for the lumped neighbour's loop and the resolved cell's construction (D112 (2)):
    LP.C_CELL is set for the duration and restored after, whatever happens."""
    old = LP.C_CELL
    LP.C_CELL = float(C)
    try:
        yield
    finally:
        LP.C_CELL = old


# ------------------------------------------------------------------------------------------------ one run
def spec(kind, test, f, kin="mean", thermal="central", h="central", models="both", stop=True, t_end=IN.T_END_S,
         chain=None):
    """One run: Stage 9's specification (`stage9_run.spec`, the 21.39 s delivery, none at f = 0) with the kinetic and
    thermal draw, the contact, the probes and the run's end. The id names every input that differs between runs, so
    that two parts that need the same run share it."""
    sp = R9.spec(R9.TRI21(), test, f, models, stop, kind=kind)
    f = sp["f"]
    th = thermal_params(thermal)
    sp.update({"stage": 11, "kin": kin, "thermal": thermal, "k_radial_W_mK": th["k_radial"],
               "k_axial_W_mK": th["k_axial"], "C_cell_J_K": th["C_cell"], "h": h, "t_end_s": float(t_end),
               "probes": dict(IN.PROBES) if models != "lumped" else {}, "chain": chain})
    kl = "mean" if kin == "mean" else f"d{int(kin)}"
    mtag = {"both": "both", "lumped": "lum", "resolved": "res"}[models]
    sp["id"] = (f"s11_{kl}_{thermal}_h{h}_{mtag}{'' if stop else '_ns'}_{test}_f{f:.9f}"
                f"{'' if abs(t_end - IN.T_END_S) < 1e-9 else '_t%d' % round(t_end)}")
    return sp


class Context(R9.Context):
    """Stage 9's context with one resolved model per (contact, mesh, thermal draw)."""

    def model(self, h, refine, thermal="central"):
        k = (h, refine, thermal)
        if k not in self.models:
            if len(self.models) >= 3:
                self.models.pop(next(iter(self.models)))
            th = thermal_params(thermal)
            with heat_capacity(th["C_cell"]):
                self.models[k] = V.Cell2Contact(V.H_CONTACT[h], refine=refine, k_radial=th["k_radial"],
                                                k_axial=th["k_axial"])
        return self.models[k]

    def share(self, h, refine):
        """The delivery's weights depend on the mesh alone (`stage8_model.share_surface`), so the central model's."""
        key_ = (h, refine)
        if key_ not in self.shares:
            self.shares[key_] = M9.share_surface(self.model(h, refine, "central"), "half")
        return self.shares[key_]


def run_one(sp, ctx, keep_series=True):
    """Stage 10's run (`stage10_run.run_one`) with the models and the stop of the specification, a kinetic draw and a
    thermal draw. The trigger's history is computed first, at the central properties (D112 (2))."""
    t_start = time.time()
    t1f, t1data, T1max_C, tT1max = ctx.history(sp)
    kin, draw = ctx.kinetics(sp["kin"])
    g_pos, g_neg = V.tabs(sp["connection"], V.G_TAB[sp["g"]])
    stop = V.LEVEL_PROP if sp["stop"] else None
    th = thermal_params(sp["thermal"])
    r = lr = model = None
    where = None
    if sp["models"] in ("both", "resolved"):
        model = ctx.model(sp["h"], sp["refine"], sp["thermal"])
        where = IN10.theta_ok(model)                                 # V2 of Stage 10: the probes' nodes
        src_r = [M9.Source("delivery", R9._pulse(sp), ctx.share(sp["h"], sp["refine"]))] if sp["E_delivered_J"] > 0 else []
        r = M9.run_resolved(model, t1f, g_pos, g_neg, kin=kin, t_amb=sp["T_amb_K"], t_end=sp["t_end_s"],
                            stop_level=stop, probes=sp["probes"], keep_series=keep_series, max_facts=6, sources=src_r,
                            max_sub=sp["max_sub"], sei0=sp["sei0"])
    if sp["models"] in ("both", "lumped"):
        src_l = [M9.Source("delivery", R9._pulse(sp))] if sp["E_delivered_J"] > 0 else []
        with heat_capacity(th["C_cell"]):
            lr = M9.run_lumped(t1f, g_pos + g_neg, g_link=V.g_contact(V.H_CONTACT[sp["h"]]), f_view=V.F_TOUCH,
                               kin=kin, t_amb=sp["T_amb_K"], t_end=sp["t_end_s"], stop_level=stop, sources=src_l,
                               max_sub=sp["max_sub"], sei0=sp["sei0"])
    rec = dict(sp)
    rec.update({"draw": draw, "h_c_W_m2K": V.H_CONTACT[sp["h"]], "G_tab_W_K": V.G_TAB[sp["g"]],
                "G_contact_W_K": V.g_contact(V.H_CONTACT[sp["h"]]), "g_pos_W_K": g_pos, "g_neg_W_K": g_neg,
                "T1max_C": T1max_C, "t_T1max_s": tT1max, "resolved": None, "lumped": None})
    series = {"t1_t": t1data[:, 0], "t1_T1_C": t1data[:, 1], "t1_T2_C": t1data[:, 2]}
    if r is not None:
        t_x = r["cross_s"]["T_onset_low"]
        rec.update({"n_nodes": int(model.C.size), "C_total_J_K": float(model.C_total) * 2.0, "probe_where": where})
        rec["resolved"] = {"propagated": t_x is not None, "t_prop_s": t_x, "stopped": r["stop"] is not None,
                           "t_end_s": r["t_end_s"], "steps": r["steps"], "rejected": r["rejected"],
                           "max_implicit_nodes": r["max_implicit_nodes"], "energy_residual_rel": r["energy_residual_rel"],
                           "peak_hottest_C": r["peak"]["Tmax_C"], "t_peak_hottest_s": r["peak"]["t_s"],
                           "where_peak": model.where(r["peak"]["imax"]), "peak_mean_C": r["peak"]["Tmean_C"],
                           "probe_peak": r["probe_peak"], "cross_s": r["cross_s"], "energy_J": r["energy_J"],
                           "stored_J": r["stored_J"], "net_in_J": r["net_in_J"], "sources": r["sources"],
                           "max_sub": r["max_sub"], "steps_with_max_sub": r["steps_with_max_sub"],
                           "conversion_volume_mean_end": r["conversion_volume_mean_end"]}
        s = r["series"]
        series.update({"t": s[:, 0], "T1": s[:, 1], "Tmax": s[:, 2], "Tmean": s[:, 3], "imax": s[:, 4].astype(int),
                       "probe_t": r["probe_t"]})
        for k in sp["probes"]:
            series["probe_" + k] = r["probe_T"][k]
    if lr is not None:
        t_xl = lr["cross_s"]["T_onset_low"]
        rec["lumped"] = {"propagated": t_xl is not None, "t_prop_s": t_xl, "stopped": lr["stop"] is not None,
                         "peak_C": lr["peak"]["T_C"], "t_peak_s": lr["peak"]["t_s"],
                         "reaction_heat_J": lr["reaction_heat_J"], "t_end_s": lr["t_end_s"], "energy_J": lr["energy_J"],
                         "energy_residual_rel": lr["energy_residual_rel"], "cross_s": lr["cross_s"],
                         "sources": lr["sources"], "stored_J": lr["stored_J"], "net_in_J": lr["net_in_J"],
                         "C_J_K": th["C_cell"]}
        series.update({"t_lumped": lr["series"][:, 0], "T_lumped": lr["series"][:, 1]})
    rec["wall_s"] = time.time() - t_start
    return rec, (series if keep_series else None)


# ------------------------------------------------------------------------------------------------ the records' points
def load_records(runs_dir=None):
    d = runs_dir or RUNS
    out = {}
    for p in glob.glob(os.path.join(d, "s11_*.json")):
        r = json.load(open(p))
        out[r["id"]] = r
    return out


def pkey(kin, thermal, h, test, f):
    return (str(kin), thermal, h, test, key(f))


def points(recs):
    """(kin, thermal, contact, test, f) -> {"C1": crossing or None, "C2": ..., "away": peak if the run went to 900 s,
    "id": ...}, from every Stage 11 record that is not failed; Stage 7's pertest runs at the low and high contact (f = 0,
    the posterior mean and the central properties) are added where they went to 900 s (D111 (4))."""
    out = {}
    for r in recs.values():
        if r.get("failed"):
            continue
        k = pkey(r["kin"], r["thermal"], r["h"], r["test"], r["f"])
        e = out.setdefault(k, {"ids": []})
        e["ids"].append(r["id"])
        if r.get("resolved"):
            rr = r["resolved"]
            e["C1"] = rr["t_prop_s"] if rr["propagated"] else None
            if rr["t_end_s"] >= IN.T_END_S - 1e-9:
                e["away"] = rr["probe_peak"]["away"]["T_C"]
                e["full_id"] = r["id"]
        if r.get("lumped"):
            ll = r["lumped"]
            e["C2"] = ll["t_prop_s"] if ll["propagated"] else None
    for (test, h), (rid, rr) in stage7_contacts().items():
        k = pkey("mean", "central", h, test, 0.0)
        e = out.setdefault(k, {"ids": []})
        if rr["t_end_s"] >= IN.T_END_S - 1e-9 and "away" not in e:
            e["away"] = rr["probe_peak"]["away"]["T_C"]
            e["full_id"] = rid
            e["ids"].append(rid)
    return out


_S7 = {}


def stage7_contacts():
    """Stage 7's pertest runs (fresh SEI) at the low and high contacts of the five low-maximum tests: {(test, h): (id,
    resolved)}."""
    if not _S7:
        for test in IN.C_TESTS:
            t = R9.by_test()[test]
            for h in ("low", "high"):
                rid = (f"pertest_{test}_{t['connection']}_h{h}_gcentral_tau{R9.tau_median():.2f}"
                       f"_E{t['E_b_J'] / 1e3:.2f}")
                rec = json.load(open(os.path.join(R9.S7RUNS, rid + ".json")))
                _S7[(test, h)] = (rid, rec["resolved"])
    return _S7


# ------------------------------------------------------------------------------------------------ the thresholds (A1, B1)
def threshold_state(pts, s8):
    """The search of D113 for one test, criterion and draw. pts: {f: met}; s8: Stage 8's f* ({"status": "zero" or
    "bracket", "lo", "hi"}). From Stage 8's bracket (its two ends tried first, or f = 0 where Stage 8's f* is 0), the
    threshold is followed by steps of 0.05 at the end it leaves (up to f = 1, down to f = 0), then the bracket is
    halved until it is at most 0.02 wide. Returns {"status": searching | zero | bracket | above | broken, "lo", "hi",
    "next": [fractions to run now]}."""
    p = {key(f): bool(m) for f, m in pts.items()}
    lo, hi = SR8.bracket(p)
    out = {"lo": lo, "hi": hi, "n_points": len(p)}
    if lo is not None and hi is not None and lo > hi:
        return dict(out, status="broken", next=[])
    start = [0.0] if s8["status"] == "zero" else [key(s8["hi"]), key(s8["lo"])]
    missing = [f for f in start if f not in p]
    if hi is not None and hi == 0.0:
        return dict(out, status="zero", next=[])
    if missing:
        return dict(out, status="searching", next=missing)
    if hi is None:                                   # not met anywhere tried: follow it up
        top = max(p)
        if top >= IN.F_END - 1e-12:
            return dict(out, status="above", next=[])
        return dict(out, status="searching", next=[key(min(IN.F_END, top + IN.WIDEN))])
    if lo is None:                                   # met everywhere tried: follow it down
        return dict(out, status="searching", next=[key(max(0.0, min(p) - IN.WIDEN))])
    if hi - lo <= IN.WIDTH + 1e-12:
        return dict(out, status="bracket", next=[])
    return dict(out, status="searching", next=[key(0.5 * (lo + hi))])


def fstar_value(st):
    """f* as a number: 0, the bracket's midpoint, or None (above 1, broken or unfinished)."""
    if st["status"] == "zero":
        return 0.0
    if st["status"] == "bracket":
        return 0.5 * (st["lo"] + st["hi"])
    return None


def chain_list():
    """Every threshold chain: (part, criterion, test, kin, thermal)."""
    out = []
    for kin in IN.KIN_DRAWS.values():
        for test in IN.A_TESTS:
            for crit in ("C1", "C2"):
                out.append(("A", crit, test, kin, "central"))
    for lab in IN.THERMAL_DRAWS:
        for test in IN.A_TESTS:
            for crit in ("C1", "C2"):
                out.append(("B", crit, test, "mean", lab))
    return out


def chain_name(part, crit, test, kin, thermal):
    return f"{part}_{crit}_{test}_{'d%d' % kin if kin != 'mean' else thermal}"


def threshold_chains(recs, pts=None):
    pts = points(recs) if pts is None else pts
    out = {}
    for part, crit, test, kin, thermal in chain_list():
        met = {}
        for (k, th, h, t, f), e in pts.items():
            if k == str(kin) and th == thermal and h == "central" and t == test and crit in e:
                met[f] = e[crit] is not None
        st = threshold_state(met, R9.fstar8()[test][crit])
        st.update({"part": part, "crit": crit, "test": test, "kin": kin, "thermal": thermal})
        out[chain_name(part, crit, test, kin, thermal)] = st
    return out


def threshold_spec(st, f):
    """C1's runs hold both neighbours and stop at their crossings; C2's hold the lumped neighbour alone. Where a C1
    point at f = 0 is also a run of Part C1 (a low-maximum test under a thermal draw at the central contact), Part C1's
    run, to 900 s with the stop lifted, is listed, so that the two share it (D113 (3))."""
    test, kin, thermal = st["test"], st["kin"], st["thermal"]
    if st["crit"] == "C2":
        return spec(st["part"], test, f, kin, thermal, "central", "lumped", True, chain=None)
    if key(f) == 0.0 and kin == "mean" and thermal != "central" and test in IN.C_TESTS:
        return spec("C1", test, 0.0, kin, thermal, "central", "both", False)
    return spec(st["part"], test, f, kin, thermal, "central", "both", True)


# ------------------------------------------------------------------------------------------------ Part C
def part_c1_specs():
    out = [spec("C1", t, 0.0, "mean", lab, "central", "both", False) for lab in IN.THERMAL_DRAWS for t in IN.C_TESTS]
    for (t, h), (rid, rr) in stage7_contacts().items():
        if h == "high" and rr["t_end_s"] < IN.T_END_S - 1e-9:      # Stage 7's run stopped at the hot spot (D111 (4))
            out.append(spec("C1", t, 0.0, "mean", "central", "high", "both", False))
    return out


def fmax_chains(recs, pts=None):
    """C2: M50_PT_Exp1's f_max at the far face by Stage 9's search (`stage9_search.fmax_state`) from f = 0 to Stage 8's
    f*_lo(C1), under the smallest radial conductivity (central contact) and at the low contact (central properties)."""
    pts = points(recs) if pts is None else pts
    test = IN.FMAX_TEST
    M = R9.max_meas(test)
    f_up = float(R9.fstar8()[test]["C1"]["lo"])
    out = {}
    for thermal, h in IN.FMAX_CASES:
        pk = {k[4]: e["away"] for k, e in pts.items()
              if k[0] == "mean" and k[1] == thermal and k[2] == h and k[3] == test and "away" in e}
        st = S9.fmax_state(M, f_up, pk, tol_k=IN.PEAK_TOL_K, width=IN.WIDTH_M, f_end=IN.F_END)
        nxt = [] if st.get("next") is None else [st["next"]]
        if st["status"] == "searching" and st.get("stage") == "range end":    # D114 (2): the first midpoints too
            m = key(0.5 * f_up)
            nxt += [m, key(0.5 * m), key(0.5 * (m + f_up))]
        if st["status"] == "searching" and st.get("stage") == "bisection":    # D114 (2): the next two midpoints
            m, lo, hi = st["next"], st["lo"], st["hi"]
            nxt += [key(0.5 * (lo + m)), key(0.5 * (m + hi))]
        nxt += [q for q in st.get("speculative", [])]
        st.update({"test": test, "thermal": thermal, "h": h, "list": [q for q in nxt if q not in pk]})
        out[f"C2_{test}_{thermal}_h{h}"] = st
    return out


E3_CASES = [(lab, "central") for lab in IN.THERMAL_DRAWS] + [("central", "low"), ("central", "high")]


def e3_cases(recs, pts=None):
    """E3, per thermal draw at the central contact and per contact at the central properties: each low-maximum test's
    f_max against the smallest f_t(C2), 0.0015755 (M50_SP_Exp3's, Stage 9). A test is "zero" where its far face at f = 0
    peaks within 5 K below its maximum or above it (f_max = 0); "above" where its f_max is known to exceed the smallest
    f_t (C2's search, or its far face at that fraction still more than 5 K short); "at or below" where its far face at that
    fraction comes within 5 K or above; "unknown" otherwise. The case separates the groups if every test is "zero" or "at
    or below", and does not if any is "above"; while undecided, the next unknown test in the brief's order gets a run at the
    smallest f_t (D114 (3))."""
    pts = points(recs) if pts is None else pts
    fm = fmax_chains(recs, pts)
    out = {}
    for thermal, h in E3_CASES:
        per = {}
        for test in IN.C_TESTS:
            M = R9.max_meas(test)
            e0 = pts.get(pkey("mean", thermal, h, test, 0.0), {})
            et = pts.get(pkey("mean", thermal, h, test, IN.FT_MIN), {})
            c2 = fm.get(f"C2_{test}_{thermal}_h{h}")
            if "away" not in e0:
                per[test] = "waiting"
            elif e0["away"] >= M - IN.PEAK_TOL_K:
                per[test] = "zero"
            elif c2 is not None and c2["status"] in ("matched", "bracketed", "above 1"):
                fmx = c2.get("f_max")
                per[test] = "above" if (fmx is not None and fmx > IN.FT_MIN) or c2["status"] == "above 1" else "at or below"
            elif "away" in et:
                per[test] = "above" if et["away"] < M - IN.PEAK_TOL_K else "at or below"
            else:
                per[test] = "unknown"
        vals = list(per.values())
        if "above" in vals:
            verdict = "no separation"
        elif all(v in ("zero", "at or below") for v in vals):
            verdict = "separation"
        else:
            verdict = "undecided"
        nxt = None
        if verdict == "undecided" and "waiting" not in vals:
            for test in IN.C_TESTS:
                if per[test] == "unknown":
                    c2 = fm.get(f"C2_{test}_{thermal}_h{h}")
                    if c2 is None:                       # C2's own search answers its two cases
                        nxt = test
                    break
        out[f"E3_{thermal}_h{h}"] = {"thermal": thermal, "h": h, "per_test": per, "verdict": verdict, "next": nxt}
    return out


# ------------------------------------------------------------------------------------------------ Part D and V4
def part_d_specs():
    return [spec("D", t, f, kin, "central", "central", "lumped", True)
            for t, f in IN.D_FRACTIONS.items() for kin in IN.KIN_DRAWS.values()]


V4_REPEATS = (  # (test, f, models, stop, the record repeated)
    ("M50_PP_Exp3", 0.0125, "both", True, ("stage8_runs", "c1_M50_PP_Exp3_f0.012500000")),
    ("M50_PT_Exp1", 0.4625, "lumped", True, ("stage8_runs", "c2_M50_PT_Exp1_f0.462500000")),
    ("M50_SP_Exp3", 0.001575, "both", False, ("stage9_runs", "s9_tri21_fresh_both_ns_M50_SP_Exp3_f0.001575000")),
)


def v4_specs():
    return [spec("V4", t, f, "mean", "central", "central", m, s) for t, f, m, s, _ in V4_REPEATS]


# ------------------------------------------------------------------------------------------------ the list
def build_runs(recs):
    """The list, in this order (D116 (5)): C2's f_max searches (the longest chains), the lumped-only runs (the
    threshold chains of C2 and Part D, under a second each), the threshold chains of C1, Part C1's runs to 900 s, E3's
    decisive runs and V4's repeats. It grows as the chains advance."""
    pts = points(recs)
    runs = []
    for st in fmax_chains(recs, pts).values():
        runs += [spec("C2", st["test"], f, "mean", st["thermal"], st["h"], "both", False) for f in st["list"]]
    chains = threshold_chains(recs, pts)
    for st in chains.values():
        if st["crit"] == "C2":
            runs += [threshold_spec(st, f) for f in st["next"]]
    runs += part_d_specs()
    for st in chains.values():
        if st["crit"] == "C1":
            runs += [threshold_spec(st, f) for f in st["next"]]
    runs += part_c1_specs()
    for c in e3_cases(recs, pts).values():
        if c["next"] is not None:
            runs.append(spec("E3", c["next"], IN.FT_MIN, "mean", c["thermal"], c["h"], "both", False))
    runs += v4_specs()
    seen, out = set(), []
    for r in runs:
        if r["id"] not in seen:
            seen.add(r["id"])
            out.append(r)
    return out


def runs_hash(runs):
    keys = sorted(json.dumps({k: v for k, v in r.items() if k not in ("kind", "chain")}, sort_keys=True,
                             default=float) for r in runs)
    return hashlib.sha256("\n".join(keys).encode()).hexdigest()


# ------------------------------------------------------------------------------------------------ the work loop
def _paths(sp):
    return os.path.join(RUNS, sp["id"] + ".json"), os.path.join(SERIES, sp["id"] + ".npz")


def work(worker, label="unlabelled", wait_s=10.0, once=False, run_fn=None):
    """Stage 10's loop (claims, a run recorded since the list was read let go, a failed run recorded as failed) on
    Stage 11's list, which grows as the chains advance. `run_fn` replaces the model in the tests."""
    for d in (RUNS, SERIES):
        os.makedirs(d, exist_ok=True)
    ctx = Context()
    machine = RUN.machine_info(label)
    run_fn = run_fn or run_one
    done = 0
    if hasattr(signal, "SIGALRM"):
        signal.signal(signal.SIGALRM, RUN._alarm)
    while True:
        recs = load_records()
        pending = [r for r in build_runs(recs) if r["id"] not in recs]
        if not pending:
            if [f for f in os.listdir(RUNS) if f.endswith(".claim")]:
                time.sleep(wait_s)                   # another worker's run may extend the list
                continue
            print(f"{RUN._utc()} worker {worker}: nothing left to run ({done} this pass)", flush=True)
            return done
        started = False
        for sp in pending:
            if os.path.exists(STOP_FILE):
                print(f"{RUN._utc()} worker {worker}: stop file; stopping after {done} runs", flush=True)
                return done
            claim = os.path.join(RUNS, sp["id"] + ".claim")
            if not RUN._claim(claim, worker):
                continue
            path, spath = _paths(sp)
            if os.path.exists(path):
                RUN._unclaim(claim)
                continue
            started = True
            st_utc = RUN._utc()
            try:
                try:
                    RUN._arm(int(RUN_LIMIT_MIN * 60), "limit")
                    rec, series = run_fn(sp, ctx)
                except KeyboardInterrupt:
                    if not RUN._DEADLINE["fired"]:
                        raise
                    raise RUN.RunTimeLimit("the run exceeded its time limit") from None
            except Exception as exc:
                import traceback
                RX.DT_BASE, RX.DT_TARGET, RX.DT_ACCEPT = 0.1, 1.0, 4.0
                LP.C_CELL = CENTRAL["C_cell"]
                rec, series = dict(sp), None
                rec.update({"failed": True, "error": repr(exc), "traceback": traceback.format_exc()})
            finally:
                RUN._disarm()
            rec["worker_peak_memory_MB"] = R9.peak_memory_mb()
            rec["started_utc"], rec["finished_utc"] = st_utc, RUN._utc()
            rec["machine"], rec["worker"] = machine, worker
            if series is not None:
                np.savez_compressed(spath, **series)
            tmp = path + f".tmp{os.getpid()}"
            with open(tmp, "w") as fh:
                json.dump(rec, fh, indent=1, default=float)
            R9._put(tmp, path)
            RUN._unclaim(claim)
            done += 1
            print(f"{RUN._utc()} {summary(rec)}", flush=True)
            break
        if once:
            return done
        if not started:
            time.sleep(wait_s)


def summary(rec):
    if rec.get("failed"):
        return f"{rec['id']}: FAILED {rec['error']}"
    parts = [rec["id"]]
    if rec.get("resolved"):
        rr = rec["resolved"]
        parts.append(f"hot spot {'%.1f s' % rr['t_prop_s'] if rr['propagated'] else 'none'} "
                     f"(peak {rr['peak_hottest_C']:.1f} C), away {rr['probe_peak']['away']['T_C']:.1f} C to "
                     f"{rr['t_end_s']:.0f} s")
    if rec.get("lumped"):
        ll = rec["lumped"]
        parts.append(f"lumped {'%.1f s' % ll['t_prop_s'] if ll['propagated'] else 'none'}")
    parts.append(f"{rec['wall_s']:.0f} s")
    return "; ".join(parts)


def status():
    recs = load_records()
    runs = build_runs(recs)
    pend = [r for r in runs if r["id"] not in recs]
    ch = threshold_chains(recs)
    print(json.dumps({"records": len(recs), "failed": sum(1 for r in recs.values() if r.get("failed")),
                      "pending_now": len(pend),
                      "threshold_chains": {s: sum(1 for c in ch.values() if c["status"] == s)
                                           for s in ("searching", "zero", "bracket", "above", "broken")},
                      "fmax": {k: (s["status"], s.get("f_max")) for k, s in fmax_chains(recs).items()},
                      "e3": {k: c["verdict"] for k, c in e3_cases(recs).items()},
                      "claims": [f for f in os.listdir(RUNS) if f.endswith(".claim")] if os.path.isdir(RUNS) else []}))


def reset_claims():
    n = 0
    for f in os.listdir(RUNS) if os.path.isdir(RUNS) else []:
        if f.endswith(".claim"):
            RUN._unclaim(os.path.join(RUNS, f))
            n += 1
    print(f"{n} claims removed")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["list", "chains", "work", "status", "reset-claims"])
    ap.add_argument("--worker", type=int, default=0)
    ap.add_argument("--label", default="unlabelled")
    a = ap.parse_args()
    if a.cmd == "list":
        runs = build_runs(load_records())
        print(len(runs), "runs listed now; sha256", runs_hash(runs))
        for r in runs:
            print(r["id"])
    elif a.cmd == "chains":
        recs = load_records()
        for name, st in threshold_chains(recs).items():
            print(name, st["status"], st.get("lo"), st.get("hi"), st.get("next"))
        for name, st in fmax_chains(recs).items():
            print(name, st["status"], st.get("lo"), st.get("hi"), st.get("next"), st.get("f_max"))
        for name, c in e3_cases(recs).items():
            print(name, c["verdict"], c["per_test"], c["next"])
    elif a.cmd == "work":
        work(a.worker, label=a.label)
    elif a.cmd == "reset-claims":
        reset_claims()
    else:
        status()
