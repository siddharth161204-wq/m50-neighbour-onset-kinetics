#!/usr/bin/env python3
"""Stage 8 runs: how much of the ejected energy the outcomes require (predictions_stage8.md; DECISIONS.md D77 to D84).

Every run is one test of Fransson et al. with its Stage 7 trigger (D65), the central contact, the central tabs, 25 C,
the posterior-mean kinetics, the fresh SEI and the reaction heat fed back one-way (D40), and a fraction f of the
test's ejected energy E_e = r E_b delivered to the neighbour from the start of the trigger's release (D77). A run
holds the resolved and the lumped neighbour (`both`), or the lumped one alone (`lumped`, for the searches of C2), or
the resolved split cell of Part D alone (`split`). Each resolved neighbour stops when its hot spot reaches 255.7 C,
each lumped one when it does, or at 900 s (D35).

Sets (D78 to D83):
  first     Part A's first round: the sixteen tests at f = 0.1, 0.2 and 0.3, both (48 runs); Part C reads them;
  c1, c2    Part A's searches of C1 (both) and C2 (lumped) beyond the first round, one chain per test;
  dur10_c1, dur10_c2, dur60_c1, dur60_c2, capend_c1   A4: the chains restarted from Part A's results with the
            delivery over 10 or 60 s (conditional), or on the cap-end quarter (C1 only: the lumped neighbour has no
            geometry, so C2 is unchanged by construction), for the five A4 tests;
  ratiolow_c1, ratiolow_c2, ratiohigh_c1, ratiohigh_c2   A4: the Databank ratio's bracket, from Part A's points
            rescaled (the model sees only f r E_b), with runs only where the rescaled bracket is wider than 0.02;
  elec05_c1, elec20_c1   Part B: the C1 chains with f_e = 0.05 and 0.2 of the stored energy as Joule heat in the
            roll, for the eight parallel tests, f = 0 first, then restarted from Part A's bracket;
  gas, gasctl   Part D: the three median tests at f = 0.2 on the split cell, with the gas layer and without it
            (the control);
  v3mesh, v3step   V3: the first-round run of M50_PT_Exp1 at f = 0.1 with every mesh spacing, or every step limit,
            halved.
A chain's next run is made only once its previous runs are recorded, so the list grows as the records come in.
Records go to results/stage8_runs/<id>.json and series to results/stage8_series/<id>.npz.

Usage:
  python3 stage8_run.py ejected          results/stage8_ejected.csv (A1)
  python3 stage8_run.py list | chains | status | reset-claims
  python3 stage8_run.py work --queue --label NAME [--wall-min M]
"""
import os as _os
for _k in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "NUMBA_NUM_THREADS"):
    _os.environ.setdefault(_k, "1")      # D43 (4): one thread per library; set before numpy and numba load
import argparse, csv, hashlib, json, os, signal, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v12_model as V                    # noqa: E402  (unchanged)
import v12_run as RUN                    # noqa: E402  (unchanged)
import reactive as RX                    # noqa: E402
import stage6_crossings as CR            # noqa: E402  (unchanged)
import stage7_criteria as CQ             # noqa: E402  (unchanged)
import stage7_model as M7                # noqa: E402  (unchanged)
import stage8_inputs as IN               # noqa: E402
import stage8_model as M8                # noqa: E402
import stage8_search as SR               # noqa: E402

RES = os.path.join(HERE, "..", "results")
TAG = os.environ.get("STAGE8_RUNS_TAG", "")
RUNS = os.path.join(RES, "stage8_runs" + TAG)
SERIES = os.path.join(RES, "stage8_series" + TAG)
S7RUNS = os.path.join(RES, "stage7_runs")
S7SERIES = os.path.join(RES, "stage7_series")
EJECTED = os.path.join(RES, "stage8_ejected.csv")
STOP_FILE = os.path.join(RES, "stage8_STOP")      # if this file exists, no worker starts another run
MAX_SUB = 4096                                   # D68 (3), from the sources' start (t = 0)
RUN_LIMIT_MIN = {1.0: 105.0, 2.0: 105.0}         # D83 (6): a run that takes longer is recorded as failed
START_MARGIN_MIN = {1.0: 5.0, 2.0: 80.0}         # D83 (6): the time a worker must have left to start a run
START_MARGIN_SET_MIN = {}
CKPT = os.path.join(RES, "stage8_ckpt" + TAG)     # D83 (6): Part D's runs keep their state here while they go
SPLIT_WALL_CAP_MIN = 600.0                       # D83 (6): a split run's wall time over all its attempts
V3_TEST, V3_F = "M50_PT_Exp1", 0.1               # D83 (3)
K0 = 273.15


# ------------------------------------------------------------------------------------------------ the inputs
_CACHE = {}


def _get(name, fn):
    if name not in _CACHE:
        _CACHE[name] = fn()
    return _CACHE[name]


def ratios():
    return _get("ratios", IN.ratios)


def tests():
    return _get("tests", IN.tests)


def by_test():
    return {t["test"]: t for t in tests()}


def sens_tests():
    s = _get("sens", IN.sensitivity_tests)
    return s["nearest"] + s["extremes"]


def tau_median():
    return _get("tau", IN.tau_median_s)


def ejected_rows():
    r = ratios()
    out = []
    for t in tests():
        out.append({"test": t["test"], "connection": t["connection"], "E_b_J": t["E_b_J"],
                    "r_central": r["central"], "r_low": r["low"], "r_high": r["high"],
                    "E_e_J": r["central"] * t["E_b_J"], "E_e_low_J": r["low"] * t["E_b_J"],
                    "E_e_high_J": r["high"] * t["E_b_J"]})
    return out


def write_ejected(path=EJECTED):
    """A1: results/stage8_ejected.csv: the sixteen ejected energies at the central ratio and the bracket's ends,
    then the ten Databank rows and their ratios."""
    r = ratios()
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["kind", "id", "connection", "E_b_J", "ratio_central", "ratio_low", "ratio_high", "E_e_J",
                    "E_e_low_J", "E_e_high_J", "databank_row", "body_kJ", "positive_ejecta_kJ", "negative_ejecta_kJ",
                    "total_kJ", "ratio"])
        for x in ejected_rows():
            w.writerow(["test", x["test"], x["connection"], repr(x["E_b_J"]), repr(x["r_central"]), repr(x["r_low"]),
                        repr(x["r_high"]), repr(x["E_e_J"]), repr(x["E_e_low_J"]), repr(x["E_e_high_J"]),
                        "", "", "", "", "", ""])
        for d in r["rows"]:
            w.writerow(["databank", d["test_id"], "", "", "", "", "", "", "", "", d["row"], repr(d["body_kJ"]),
                        repr(d["positive_ejecta_kJ"]), repr(d["negative_ejecta_kJ"]), repr(d["total_kJ"]),
                        repr(d["ratio"])])
    return path


# ------------------------------------------------------------------------------------------------ Stage 7 at f = 0
def stage7_zero():
    """For each test, Stage 7's pertest run at the central contact (f = 0), read and not rerun: C1, C2 and C3, and
    the lumped neighbour's peak (A5)."""
    def load():
        out = {}
        for t in tests():
            rid = f"pertest_{t['test']}_{t['connection']}_hcentral_gcentral_tau{tau_median():.2f}_E{t['E_b_J'] / 1e3:.2f}"
            rec = json.load(open(os.path.join(S7RUNS, rid + ".json")))
            q = rec["stage7"]
            out[t["test"]] = {"id": rid, "C1": bool(rec["resolved"]["propagated"]),
                              "C2": bool(rec["lumped"]["propagated"]),
                              "C3": q["clocks"]["lumped"]["t_150_s"] is not None,
                              "t_C1_s": rec["resolved"].get("t_prop_s"), "t_C2_s": rec["lumped"].get("t_prop_s"),
                              "t_C3_s": q["clocks"]["lumped"]["t_150_s"], "lumped_peak_C": rec["lumped"]["peak_C"],
                              "hot_peak_C": rec["resolved"]["peak_hottest_C"]}
        return out
    return _get("s7zero", load)


# ------------------------------------------------------------------------------------------------ the run specifications
SETS_FIXED = ("first", "gas", "gasctl", "v3mesh", "v3step")
VARIANTS = {   # set: (criterion, delivery duration, geometry, f_e, ratio, models)
    "c1": ("C1", None, "half", 0.0, "central", "both"),
    "c2": ("C2", None, "half", 0.0, "central", "lumped"),
    "dur10_c1": ("C1", 10.0, "half", 0.0, "central", "both"),
    "dur10_c2": ("C2", 10.0, "half", 0.0, "central", "lumped"),
    "dur60_c1": ("C1", 60.0, "half", 0.0, "central", "both"),
    "dur60_c2": ("C2", 60.0, "half", 0.0, "central", "lumped"),
    "capend_c1": ("C1", None, "capend", 0.0, "central", "both"),
    "ratiolow_c1": ("C1", None, "half", 0.0, "low", "both"),
    "ratiolow_c2": ("C2", None, "half", 0.0, "low", "lumped"),
    "ratiohigh_c1": ("C1", None, "half", 0.0, "high", "both"),
    "ratiohigh_c2": ("C2", None, "half", 0.0, "high", "lumped"),
    "elec05_c1": ("C1", None, "half", 0.05, "central", "both"),
    "elec20_c1": ("C1", None, "half", 0.2, "central", "both"),
}
REFINE_SETS = ("dur10_c1", "dur10_c2", "dur60_c1", "dur60_c2", "capend_c1")   # D79 (3)
REFINE_FACTOR = 8
VARIANTS.update({"refA_c1": VARIANTS["c1"], "refA_c2": VARIANTS["c2"]})
VARIANTS.update({f"ref_{s}": VARIANTS[s] for s in REFINE_SETS})


def spec(set_, test, f, tau_d=None, geometry="half", f_e=0.0, ratio="central", models="both", gas=None, refine=1.0,
         dt_scale=1.0):
    t = by_test()[test]
    r = ratios()[ratio]
    tau_d = tau_median() if tau_d is None else float(tau_d)
    f = SR.key(f)
    return {"id": f"{set_}_{test}_f{f:.9f}", "set": set_, "test": test, "kin": "mean", "connection": t["connection"],
            "h": "central", "g": "central", "tau": float(tau_median()), "E_body_J": float(t["E_b_J"]),
            "T_amb_K": float(V.LP.T_AMB), "refine": float(refine), "dt_scale": float(dt_scale), "f": f,
            "ratio": ratio, "r": float(r), "E_e_J": float(r * t["E_b_J"]), "E_delivered_J": float(f * r * t["E_b_J"]),
            "tau_d_s": tau_d, "geometry": geometry, "f_e": float(f_e), "E_joule_J": float(f_e * IN.E_STORED_J),
            "models": models, "gas": gas, "t_end_s": 900.0, "max_sub": MAX_SUB}


def variant_spec(set_, test, f):
    crit, tau_d, geom, f_e, ratio, models = VARIANTS[set_]
    return spec(set_, test, f, tau_d=tau_d, geometry=geom, f_e=f_e, ratio=ratio, models=models)


def fixed_runs():
    out = []
    for t in tests():
        for f in IN.COMMON_F:
            out.append(spec("first", t["test"], f))
    for test in IN.median_tests():
        out.append(spec("gas", test, 0.2, models="split", gas="layer"))
        out.append(spec("gasctl", test, 0.2, models="split", gas="control"))
    out.append(spec("v3mesh", V3_TEST, V3_F, refine=2.0, models="resolved"))
    out.append(spec("v3step", V3_TEST, V3_F, dt_scale=0.5, models="resolved"))
    return out


# ------------------------------------------------------------------------------------------------ the chains
def chain_defs():
    """Every chain: its name, set, test, criterion, its known points' source, its probes' source and what it waits
    for."""
    out = []
    for t in tests():
        for crit, set_ in (("C1", "c1"), ("C2", "c2")):
            out.append({"name": f"A_{crit}_{t['test']}", "set": set_, "test": t["test"], "criterion": crit,
                        "kind": "partA"})
    for test in sens_tests():
        for set_ in ("dur10_c1", "dur10_c2", "dur60_c1", "dur60_c2", "capend_c1"):
            crit = VARIANTS[set_][0]
            out.append({"name": f"{set_}_{test}", "set": set_, "test": test, "criterion": crit, "kind": "restart",
                        "after": f"A_{crit}_{test}"})
        for set_ in ("ratiolow_c1", "ratiolow_c2", "ratiohigh_c1", "ratiohigh_c2"):
            crit = VARIANTS[set_][0]
            out.append({"name": f"{set_}_{test}", "set": set_, "test": test, "criterion": crit, "kind": "ratio",
                        "after": f"A_{crit}_{test}"})
    for t in tests():
        if t["connection"] == "parallel":
            for set_ in ("elec05_c1", "elec20_c1"):
                out.append({"name": f"{set_}_{t['test']}", "set": set_, "test": t["test"], "criterion": "C1",
                            "kind": "elec", "after": f"A_C1_{t['test']}"})
    for test in sens_tests():                    # D79 (3): a variant that ends in Part A's own bracket
        for set_ in REFINE_SETS:
            crit = VARIANTS[set_][0]
            out.append({"name": f"ref_{set_}_{test}", "set": f"ref_{set_}", "test": test, "criterion": crit,
                        "kind": "refV", "after": f"{set_}_{test}", "partA": f"A_{crit}_{test}"})
        for crit in ("C1", "C2"):
            out.append({"name": f"refA_{crit}_{test}", "set": f"refA_{crit.lower()}", "test": test, "criterion": crit,
                        "kind": "refA", "after": f"A_{crit}_{test}",
                        "variants": [f"ref_{s}_{test}" for s in REFINE_SETS if VARIANTS[s][0] == crit]})
    return out


def outcome(rec, crit):
    """Whether a record meets C1 (the resolved stop) or C2 (the lumped stop)."""
    if crit == "C1":
        return bool(rec["resolved"]["propagated"])
    if crit == "C2":
        return bool(rec["lumped"]["propagated"])
    raise ValueError(crit)


def own_points(ch, recs):
    pts = {}
    for r in recs.values():
        if r.get("failed") or r["test"] != ch["test"]:
            continue
        if r["set"] == ch["set"] or (ch["kind"] == "partA" and r["set"] == "first"):
            pts[SR.key(r["f"])] = outcome(r, ch["criterion"])
    return pts


def chain_state(ch, recs, states=None):
    """The chain's points, probes and state (stage8_search.state); "waiting" if it waits for another chain."""
    s7 = stage7_zero()[ch["test"]]
    states = {} if states is None else states
    if ch["kind"] == "partA":
        pts = {0.0: s7[ch["criterion"]]}
        pts.update(own_points(ch, recs))
        st = SR.state(pts, IN.PROBES_A)
        return dict(st, points=pts, probes=list(IN.PROBES_A))
    a = states.get(ch["after"]) or chain_state(next(c for c in chain_defs() if c["name"] == ch["after"]), recs)
    if a["status"] in ("searching", "waiting", "broken"):
        return {"status": "waiting", "next": None, "points": {}, "probes": [], "lo": None, "hi": None}
    if ch["kind"] in ("refV", "refA"):
        return refine_state(ch, recs, states, a)
    if ch["kind"] == "restart":
        pts = {0.0: s7[ch["criterion"]]}           # no delivery at f = 0: Stage 7's run, whatever the delivery's form
        probes = SR.restart_probes(a["lo"], a["hi"], a["status"])
    elif ch["kind"] == "elec":
        pts = {}
        probes = [0.0] + SR.restart_probes(a["lo"], a["hi"], a["status"])
    elif ch["kind"] == "ratio":
        rr = ratios()
        sc = rr["central"] / rr[VARIANTS[ch["set"]][4]]
        pts = {SR.key(f * sc): m for f, m in a["points"].items()}
        probes = []
    else:
        raise ValueError(ch["kind"])
    pts.update(own_points(ch, recs))
    st = SR.state(pts, probes)
    return dict(st, points=pts, probes=probes)


def refine_state(ch, recs, states, a):
    """D79 (3): a variant chain that ends in Part A's own bracket, and Part A's chain with it, are halved on, each in
    its own configuration, until the bracket is an eighth as wide; otherwise "not needed"."""
    idle = {"status": "not needed", "next": None, "points": {}, "probes": [], "lo": None, "hi": None}
    if ch["kind"] == "refV":
        pa = states[ch["partA"]]
        if pa["status"] in ("searching", "waiting", "broken"):
            return dict(idle, status="waiting")
        need = a["status"] == "bracket" and pa["status"] == "bracket" and (a["lo"], a["hi"]) == (pa["lo"], pa["hi"])
    else:
        vs = [states[v] for v in ch["variants"]]
        if any(v["status"] == "waiting" for v in vs):
            return dict(idle, status="waiting")
        need = any(v["status"] not in ("not needed",) for v in vs) and a["status"] == "bracket"
    if not need:
        return idle
    pts = {SR.key(a["lo"]): False, SR.key(a["hi"]): True}
    pts.update(own_points(ch, recs))
    st = SR.state(pts, (), width=(a["hi"] - a["lo"]) / REFINE_FACTOR)
    return dict(st, points=pts, probes=[], refined_from=[a["lo"], a["hi"]])


def all_states(recs):
    states = {}
    for ch in chain_defs():                      # Part A's chains come first, so the others find them
        states[ch["name"]] = chain_state(ch, recs, states)
    return states


def chain_runs(recs, states=None):
    """The runs the chains need now: for each chain still searching, its next fraction (a first-round run for Part
    A's chains at the common fractions, which are in the fixed list)."""
    states = all_states(recs) if states is None else states
    out = []
    for ch in chain_defs():
        st = states[ch["name"]]
        if st["status"] != "searching" or st["next"] is None:
            continue
        f = st["next"]
        if ch["kind"] == "partA" and f in [SR.key(x) for x in IN.COMMON_F]:
            continue                             # the first-round run, in the fixed list
        out.append(variant_spec(ch["set"], ch["test"], f))
    return out


def build_runs(recs):
    """The run list as it stands: the first round, then the chains' runs, then Part D, then V3's."""
    fx = fixed_runs()
    first = [r for r in fx if r["set"] == "first"]
    rest = [r for r in fx if r["set"] != "first"]
    seen, out = set(), []
    for r in first + chain_runs(recs) + rest:
        if r["id"] not in seen:
            seen.add(r["id"])
            out.append(r)
    return out


def runs_hash(runs):
    return hashlib.sha256(json.dumps(runs, sort_keys=True).encode()).hexdigest()


def load_records(runs_dir=None):
    runs_dir = RUNS if runs_dir is None else runs_dir
    recs = {}
    if os.path.isdir(runs_dir):
        for f in os.listdir(runs_dir):
            if f.endswith(".json"):
                try:
                    r = json.load(open(os.path.join(runs_dir, f)))
                except (OSError, ValueError):
                    continue
                recs[r["id"]] = r
    return recs


# ------------------------------------------------------------------------------------------------ one run
class Context(RUN.Context):
    """v12_run.Context with the split cell and the shares kept as well."""

    def __init__(self):
        super().__init__()
        self.splits, self.shares = {}, {}

    def split(self, h, refine):
        key = (h, refine)
        if key not in self.splits:
            self.splits[key] = M8.SplitCell(self.model(h, refine))
        return self.splits[key]

    def share(self, h, refine, geometry):
        key = (h, refine, geometry)
        if key not in self.shares:
            self.shares[key] = M8.share_surface(self.model(h, refine), geometry)
        return self.shares[key]


def sources_for(spec_, ctx, split=None):
    """The run's sources: the delivery (f E_e over tau_d from 0, through the can) and the Joule heat (f_e of the stored
    energy over the trigger's release from 0, in the roll by volume)."""
    model = ctx.model(spec_["h"], spec_["refine"])
    res, lum = [], []
    if spec_["E_delivered_J"] > 0.0:
        sh = ctx.share(spec_["h"], spec_["refine"], spec_["geometry"])
        if split is not None:
            sh = split.move(sh)
        res.append(M8.Source("delivery", M8.Pulse(spec_["E_delivered_J"], spec_["tau_d_s"], 0.0), sh))
        lum.append(M8.Source("delivery", M8.Pulse(spec_["E_delivered_J"], spec_["tau_d_s"], 0.0)))
    if spec_["E_joule_J"] > 0.0:
        sv = M8.share_volume(split if split is not None else model)
        res.append(M8.Source("joule", M8.Pulse(spec_["E_joule_J"], spec_["tau"], 0.0), sv))
        lum.append(M8.Source("joule", M8.Pulse(spec_["E_joule_J"], spec_["tau"], 0.0)))
    return res, lum


def _at(t_arr, y_arr, t):
    return float(np.interp(t, t_arr, y_arr))


def run_one(spec_, ctx, keep_series=True, checkpoint=None):
    """One Stage 8 run. The record has v12_run.run_one's fields (resolved and lumped), with the sources' energies, and
    the Stage 7 quantities of its histories (stage7_criteria.quantities) where it holds both neighbours. A split run
    keeps its state in `checkpoint` as it goes and starts from it if it is there (D83 (6))."""
    t_start = time.time()
    t1f, t1data, T1max_C, tT1max = ctx.history(spec_)
    kin, draw = ctx.kinetics(spec_["kin"])
    g_pos, g_neg = V.tabs(spec_["connection"], V.G_TAB[spec_["g"]])
    models = spec_["models"]
    split = ctx.split(spec_["h"], spec_["refine"]) if models == "split" else None
    model = split if split is not None else ctx.model(spec_["h"], spec_["refine"])
    src_r, src_l = sources_for(spec_, ctx, split)
    saved = (RX.DT_BASE, RX.DT_TARGET, RX.DT_ACCEPT)
    if spec_["dt_scale"] != 1.0:
        RX.DT_BASE, RX.DT_TARGET, RX.DT_ACCEPT = (x * spec_["dt_scale"] for x in saved)
    r = lr = None
    try:
        if models in ("both", "resolved"):
            r = M8.run_resolved(model, t1f, g_pos, g_neg, kin=kin, t_amb=spec_["T_amb_K"], t_end=spec_["t_end_s"],
                                stop_level=V.LEVEL_PROP, probes=model.probes, keep_series=keep_series,
                                max_facts=6 if spec_["refine"] == 1.0 else 2, sources=src_r, max_sub=spec_["max_sub"])
        elif models == "split":
            r = M8.run_resolved_split(model, t1f, g_pos, g_neg, kin=kin, t_amb=spec_["T_amb_K"],
                                      t_end=spec_["t_end_s"], stop_level=V.LEVEL_PROP, keep_series=keep_series,
                                      sources=src_r, max_sub=spec_["max_sub"], layer=spec_["gas"] == "layer",
                                      checkpoint=checkpoint, wall_cap_s=SPLIT_WALL_CAP_MIN * 60.0)
        if models in ("both", "lumped"):
            lr = M8.run_lumped(t1f, g_pos + g_neg, g_link=V.g_contact(V.H_CONTACT[spec_["h"]]), f_view=V.F_TOUCH,
                               kin=kin, t_amb=spec_["T_amb_K"], t_end=spec_["t_end_s"], stop_level=V.LEVEL_PROP,
                               sources=src_l, max_sub=spec_["max_sub"])
    finally:
        RX.DT_BASE, RX.DT_TARGET, RX.DT_ACCEPT = saved
    rec = dict(spec_)
    rec.update({"draw": draw, "h_c_W_m2K": V.H_CONTACT[spec_["h"]], "G_tab_W_K": V.G_TAB[spec_["g"]],
                "G_contact_W_K": V.g_contact(V.H_CONTACT[spec_["h"]]), "g_pos_W_K": g_pos, "g_neg_W_K": g_neg,
                "T1max_C": T1max_C, "t_T1max_s": tT1max, "n_nodes": int(model.C.size), "resolved": None,
                "lumped": None})
    series = {"t1_t": t1data[:, 0], "t1_T1_C": t1data[:, 1], "t1_T2_C": t1data[:, 2]}
    if r is not None:
        res = {"propagated": r["stop"] is not None, "t_end_s": r["t_end_s"], "steps": r["steps"],
               "rejected": r["rejected"], "max_implicit_nodes": r["max_implicit_nodes"],
               "energy_residual_rel": r["energy_residual_rel"], "peak_hottest_C": r["peak"]["Tmax_C"],
               "t_peak_hottest_s": r["peak"]["t_s"], "where_peak": model.where(r["peak"]["imax"]),
               "peak_mean_C": r["peak"]["Tmean_C"], "probe_peak": r["probe_peak"], "in_rxn_J": r["energy_J"]["in_rxn"],
               "cross_s": r["cross_s"], "energy_J": r["energy_J"], "stored_J": r["stored_J"],
               "net_in_J": r["net_in_J"], "sources": r["sources"], "max_sub": r["max_sub"],
               "steps_with_max_sub": r["steps_with_max_sub"],
               "implicit_node_steps_with_max_sub": r["implicit_node_steps_with_max_sub"],
               "conversion_volume_mean_end": r["conversion_volume_mean_end"],
               "max_local_reaction_heating_K_per_s": r["max_local_reaction_heating_K_per_s"]}
        for k in ("can_peak", "factorisations", "interface_node_steps", "layer", "resumed", "wall_all_attempts_s"):
            if k in r:
                res[k] = r[k]
        if split is not None:
            res["geom"] = {k: v for k, v in split.geom.items() if k.startswith(("split", "A_interface", "A_lateral"))}
        pt, pT = r["probe_t"], r["probe_T"]
        if r["stop"] is not None:
            tp = r["stop"]["t_s"]
            res.update({"t_prop_s": tp, "where": r["stop"]["where"], "mean_at_prop_C": r["stop"]["Tmean_C"],
                        "T1_at_prop_C": t1f(tp) - 273.15})
            if "can_max_C" in r["stop"]:
                res["can_at_prop_C"] = r["stop"]["can_max_C"]
        rec["resolved"] = res
        s = r["series"]
        series.update({"t": s[:, 0], "T1": s[:, 1], "Tmax": s[:, 2], "Tmean": s[:, 3], "imax": s[:, 4].astype(int),
                       "probe_t": pt, "probe_toward": pT["toward"], "probe_away": pT["away"]})
        if s.shape[1] > 8:
            series["Tcan_max"] = s[:, 8]
            series["probe_toward_roll"], series["probe_away_roll"] = pT["toward_roll"], pT["away_roll"]
    if lr is not None:
        lres = {"propagated": lr["stop"] is not None, "peak_C": lr["peak"]["T_C"], "t_peak_s": lr["peak"]["t_s"],
                "reaction_heat_J": lr["reaction_heat_J"], "t_end_s": lr["t_end_s"], "energy_J": lr["energy_J"],
                "energy_residual_rel": lr["energy_residual_rel"], "conversion_end": lr["conversion_end"],
                "cross_s": lr["cross_s"], "sources": lr["sources"], "stored_J": lr["stored_J"],
                "net_in_J": lr["net_in_J"]}
        if lr["stop"] is not None:
            lres["t_prop_s"] = lr["stop"]["t_s"]
        rec["lumped"] = lres
        series.update({"t_lumped": lr["series"][:, 0], "T_lumped": lr["series"][:, 1]})
    rec["wall_s"] = time.time() - t_start
    rec["stage8"] = quantities(rec, series)
    return rec, (series if keep_series else None)


def quantities(rec, series):
    """The Stage 7 quantities (stage7_criteria.quantities) where the record holds both neighbours; for a lumped run
    the lumped neighbour's alone (its peak, and its crossings of 138.5, 150 and 255.7 C read from its stored series
    as D67 (1) reads them); for a split run the resolved clocks alone."""
    if rec["resolved"] is not None and rec["lumped"] is not None:
        return CQ.quantities(rec, series)
    out = {"levels_C": dict(CQ.LEVELS_C), "clocks": {}, "stop": {}}
    if rec["lumped"] is not None:
        ll = rec["lumped"]
        d = {"peak_C": float(ll["peak_C"]), "t_peak_s": float(ll["t_peak_s"])}
        for name, lv in CQ.LEVELS_C.items():
            d[f"t_{name}_s"] = CR.first_crossing(series["t_lumped"], series["T_lumped"], lv + K0)
        out["clocks"]["lumped"] = d
        out["stop"].update({"lumped_t_s": ll.get("t_prop_s"), "lumped_t_end_s": ll["t_end_s"]})
    if rec["resolved"] is not None:
        rr = rec["resolved"]
        d = {"peak_C": float(rr["peak_hottest_C"]), "t_peak_s": float(rr["t_peak_hottest_s"])}
        for name, lv in CQ.LEVELS_C.items():
            d[f"t_{name}_s"] = CR.first_crossing(series["t"], series["Tmax"], lv + K0)
        out["clocks"]["hot"] = d
        out["stop"].update({"hot_t_s": rr.get("t_prop_s"), "resolved_t_end_s": rr["t_end_s"]})
    return out


# ------------------------------------------------------------------------------------------------ the work loop
def peak_memory_mb():
    try:
        import resource
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    except Exception:
        return None


def order_key(sp_, prefer):
    """Within the list, the first round first; a worker labelled for the long runs takes V3's refined run first."""
    if prefer and sp_["set"] == prefer:
        return -1
    return 0


def work(worker, budget_min, wall_min=1e9, label="unlabelled", prefer=None, wait_s=20.0, sets=None):
    """v12_run.work's loop with the Stage 8 list, which grows as the chains advance: each pass rebuilds the list from
    the records, takes the first run that is neither recorded nor claimed, and runs it. Every rule of D43 (3), D47 (3)
    and D55 (3) is kept (claims, a run interrupted at the wall time is not recorded, a failed run is recorded as
    failed)."""
    os.makedirs(RUNS, exist_ok=True)
    os.makedirs(SERIES, exist_ok=True)
    ctx = Context()
    machine = RUN.machine_info(label)
    t0 = time.time()
    done = 0
    if hasattr(signal, "SIGALRM"):
        signal.signal(signal.SIGALRM, RUN._alarm)
    while True:
        recs = load_records()
        runs = [r for r in build_runs(recs) if sets is None or r["set"] in sets]
        runs.sort(key=lambda s: order_key(s, prefer))
        pending = [r for r in runs if r["id"] not in recs]
        if not pending:
            if any(st["status"] in ("searching", "waiting") for st in all_states(recs).values()) and \
                    any(f.endswith(".claim") for f in os.listdir(RUNS)):
                time.sleep(wait_s)                 # another worker's run will extend the list
                continue
            print(f"{RUN._utc()} worker {worker}: nothing left to run ({done} this pass)", flush=True)
            return
        started = False
        for sp_ in pending:
            elapsed = (time.time() - t0) / 60.0
            left = wall_min - elapsed
            margin = max(START_MARGIN_MIN[sp_["refine"]], START_MARGIN_SET_MIN.get(sp_["set"], 0.0))
            if elapsed > budget_min or left < margin or os.path.exists(STOP_FILE):
                print(f"{RUN._utc()} worker {worker}: stopping after {done} runs (budget, wall time or stop file)",
                      flush=True)
                return
            claim = os.path.join(RUNS, sp_["id"] + ".claim")
            if not RUN._claim(claim, worker):
                continue
            started = True
            path = os.path.join(RUNS, sp_["id"] + ".json")
            split = sp_["models"] == "split"
            ck = os.path.join(CKPT, sp_["id"] + ".pkl") if split else None
            if split:
                os.makedirs(CKPT, exist_ok=True)
            wall_s = int(left * 60) - RUN.WALL_MARGIN_S
            limit_s = wall_s + 60 if split else int(RUN_LIMIT_MIN[sp_["refine"]] * 60)
            st_utc = RUN._utc()
            try:
                try:
                    RUN._arm(min(limit_s, wall_s), "wall" if wall_s < limit_s else "limit")
                    rec, series = run_one(sp_, ctx, checkpoint=ck)
                except KeyboardInterrupt:
                    if not RUN._DEADLINE["fired"]:
                        raise
                    if RUN._DEADLINE["kind"] == "wall":
                        raise RUN.WallTime("the hosting shell's time ran out") from None
                    raise RUN.RunTimeLimit("the run exceeded its time limit") from None
            except RUN.WallTime:
                RUN._disarm()
                RX.DT_BASE, RX.DT_TARGET, RX.DT_ACCEPT = 0.1, 1.0, 4.0
                RUN._unclaim(claim)
                print(f"{RUN._utc()} worker {worker}: {sp_['id']} interrupted at the wall time and not recorded; "
                      f"stopping after {done} runs", flush=True)
                return
            except Exception as exc:
                import traceback
                RX.DT_BASE, RX.DT_TARGET, RX.DT_ACCEPT = 0.1, 1.0, 4.0
                rec, series = dict(sp_), None
                rec.update({"failed": True, "error": repr(exc), "traceback": traceback.format_exc()})
            finally:
                RUN._disarm()
            rec["worker_peak_memory_MB"] = peak_memory_mb()
            rec["started_utc"], rec["finished_utc"] = st_utc, RUN._utc()
            rec["machine"] = machine
            rec["worker"] = worker
            if series is not None:
                np.savez_compressed(os.path.join(SERIES, sp_["id"] + ".npz"), **series)
            tmp = path + f".tmp{os.getpid()}"
            with open(tmp, "w") as fh:
                json.dump(rec, fh, indent=1, default=float)
            os.replace(tmp, path)
            if ck is not None and os.path.exists(ck):
                os.remove(ck)
            RUN._unclaim(claim)
            done += 1
            print(f"{RUN._utc()} {summary(rec)}", flush=True)
            break                                    # re-read the list: the chains may have moved
        if not started:
            time.sleep(wait_s)                       # every pending run is claimed by another worker


def summary(rec):
    if rec.get("failed"):
        return f"{rec['id']}: FAILED {rec['error']}"
    parts = [rec["id"]]
    rr, ll = rec.get("resolved"), rec.get("lumped")
    if rr:
        parts.append(f"hot spot {'%.1f s' % rr['t_prop_s'] if rr['propagated'] else 'none'} "
                     f"(peak {rr['peak_hottest_C']:.1f} C)" + (f", can {rr['can_peak']['T_C']:.0f} C"
                                                               if rr.get("can_peak") else ""))
    if ll:
        parts.append(f"lumped {'%.1f s' % ll['t_prop_s'] if ll['propagated'] else 'none'} (peak {ll['peak_C']:.1f} C)")
    parts.append(f"{rec['wall_s']:.0f} s")
    return "; ".join(parts)


def status():
    recs = load_records()
    states = all_states(recs)
    by = {}
    for s in states.values():
        by[s["status"]] = by.get(s["status"], 0) + 1
    fx = fixed_runs()
    print(json.dumps({"records": len(recs), "failed": sum(1 for r in recs.values() if r.get("failed")),
                      "fixed_done": sum(1 for r in fx if r["id"] in recs), "fixed_total": len(fx),
                      "chains": by, "claims": [f for f in os.listdir(RUNS) if f.endswith(".claim")]
                      if os.path.isdir(RUNS) else []}))


def reset_claims():
    n = 0
    for f in os.listdir(RUNS) if os.path.isdir(RUNS) else []:
        if f.endswith(".claim"):
            RUN._unclaim(os.path.join(RUNS, f))
            n += 1
    print(f"{n} claims removed")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["ejected", "list", "chains", "work", "status", "reset-claims"])
    ap.add_argument("--worker", type=int, default=0)
    ap.add_argument("--budget-min", type=float, default=1e9)
    ap.add_argument("--wall-min", type=float, default=1e9)
    ap.add_argument("--label", default="unlabelled")
    ap.add_argument("--prefer", default=None)
    ap.add_argument("--sets", nargs="*", default=None)
    a = ap.parse_args()
    if a.cmd == "ejected":
        print(write_ejected())
    elif a.cmd == "list":
        fx = fixed_runs()
        print(len(fx), "fixed runs; sha256 of the list", runs_hash(fx))
        print({s: sum(r["set"] == s for r in fx) for s in SETS_FIXED})
        print(len(chain_defs()), "chains", {k: sum(c["kind"] == k for c in chain_defs())
                                            for k in ("partA", "restart", "ratio", "elec", "refV", "refA")})
    elif a.cmd == "chains":
        recs = load_records()
        for name, st in all_states(recs).items():
            print(name, st["status"], st.get("lo"), st.get("hi"), st.get("next"))
    elif a.cmd == "work":
        work(a.worker, a.budget_min, a.wall_min, label=a.label, prefer=a.prefer,
             sets=set(a.sets) if a.sets else None)
    elif a.cmd == "reset-claims":
        reset_claims()
    else:
        status()
