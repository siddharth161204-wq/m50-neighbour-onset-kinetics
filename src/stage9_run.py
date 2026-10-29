#!/usr/bin/env python3
"""Stage 9 runs: the delivered fraction read from each test's time and peak (predictions_stage9.md; DECISIONS.md D90
to D96).

Every run is one test of Fransson et al. with its Stage 7 trigger (D65), the central contact, the central tabs, 25 C,
the posterior-mean kinetics and the reaction heat fed back one-way (D40), and a fraction f of the test's ejected
energy E_e = r E_b (D77) delivered to the neighbour from t = 0 through the half of its can facing the trigger: Stage
8's triangular pulse over 21.39 s (Part A, C3), or a constant power over 120, 240 or 360 s (Part B, conditional).
The SEI is fresh, or aged (C3). A run holds the resolved and the lumped neighbour ("both"), the lumped one alone
("lumped") or the resolved one alone ("resolved", V3); each stops when it reaches 255.7 C (D35), or goes on to 900 s
where its search reads a peak (the stop lifted, "_ns" in its id, D92 (2)).

The searches are chains (D91 to D95), each a function of the records already made:
  A1_<C>_<test>        A1, the induction curve: the grid above Stage 8's f*_hi (nine propagated tests, C1 and C2);
  A2_<C>_<test>        A2, f_t: the grid, then the bisection (after every A1 chain has ended and V1 is written);
  A3_<test>            A3, f_max of the thermocouple node (the five low-maximum tests; the two high ones exploratory);
  A3L_<test>           the lumped neighbour's f_max with the 21.39 s delivery, B2's reference (exploratory);
  B_fs_<C>_<tau>_<test>, B_ft_<C>_<tau>_<test>, B_fm_<tau>_<test>, B_fmL_<tau>_<test>
                       Part B: f* by D78's search, then f_t (propagated) or f_max (not propagated), all sixteen tests;
  C3_fs_<C>_<test>, C3_ft_<C>_<test>   C3, the aged SEI for the three tests of P8;
  V3                   V3 on M50_PP_Exp3 under 240 s at f*_lo(C1) (D95 (3));
  S_<delivery>_<test>  the thermocouple's history at f_t(C2), exploratory (D94 (3)).
Records reused, not rerun: Stage 7's pertest and aged runs at the central contact (f = 0, no delivery) and Stage 8's
Part A runs (sets first, c1, c2, refA_c1, refA_c2: the 21.39 s delivery, fresh SEI), wherever a chain's fraction and
configuration coincide with theirs (D90 (3)).
Records go to results/stage9_runs/<id>.json and series to results/stage9_series/<id>.npz; the laptop-against-cloud
check of three Stage 8 runs to results/stage9_xcheck/ (D96 (2)).

Usage:
  python3 stage9_run.py list | chains | status | reset-claims
  python3 stage9_run.py work --worker K --label NAME [--wall-min M] [--sets ...]
"""
import os as _os
for _k in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "NUMBA_NUM_THREADS"):
    _os.environ.setdefault(_k, "1")      # D43 (4): one thread per library; set before numpy and numba load
import argparse, glob, hashlib, json, os, signal, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v12_model as V                    # noqa: E402  (unchanged)
import v12_run as RUN                    # noqa: E402  (unchanged)
import reactive as RX                    # noqa: E402
import stage8_run as R8                  # noqa: E402  (unchanged)
import stage8_search as SR8              # noqa: E402  (unchanged)
import stage9_inputs as IN               # noqa: E402
import stage9_model as M9                # noqa: E402
import stage9_search as S9               # noqa: E402

RES = os.path.join(HERE, "..", "results")
TAG = os.environ.get("STAGE9_RUNS_TAG", "")
RUNS = os.path.join(RES, "stage9_runs" + TAG)
SERIES = os.path.join(RES, "stage9_series" + TAG)
XCHK = os.path.join(RES, "stage9_xcheck" + TAG)
V1_FILE = os.path.join(RES, "stage9_v1" + TAG + ".json")
S7RUNS = os.path.join(RES, "stage7_runs")
S8RUNS = os.path.join(RES, "stage8_runs")
STOP_FILE = os.path.join(RES, "stage9_STOP")      # if this file exists, no worker starts another run
MAX_SUB = 4096                                   # D68 (3), from the sources' start (t = 0)
RUN_LIMIT_MIN = {1.0: 1440.0, 2.0: 2880.0}       # D96 (1): a run that takes longer is recorded as failed
START_MARGIN_MIN = 5.0
K0 = 273.15
S8_SETS = ("first", "c1", "c2", "refA_c1", "refA_c2")


# ------------------------------------------------------------------------------------------------ the inputs
_CACHE = {}


def _get(name, fn):
    if name not in _CACHE:
        _CACHE[name] = fn()
    return _CACHE[name]


def tests():
    return _get("tests", IN.tests)


def by_test():
    return {t["test"]: t for t in tests()}


def ratios():
    return _get("ratios", IN.ratios)


def tau_median():
    return _get("tau", IN.tau_median_s)


def fstar8():
    return _get("fstar8", IN.stage8_fstar)


def t_meas(test):
    return float(by_test()[test]["time_s"])


def max_meas(test):
    return float(by_test()[test]["neighbour_max_C"])


# ------------------------------------------------------------------------------------------------ configurations
def cfg(shape, tau_d=0.0, sei="fresh", refine=1.0, dt_scale=1.0):
    return {"shape": shape, "tau_d": float(tau_d), "sei": sei, "refine": float(refine), "dt_scale": float(dt_scale)}


def cfg_key(c):
    if c["shape"] == "none":
        k = "none"
    elif c["shape"] == "tri":
        k = f"tri{c['tau_d']:.0f}" if abs(c["tau_d"] - tau_median()) > 1e-9 else "tri21"
    else:
        k = f"con{c['tau_d']:.0f}"
    k += "_" + c["sei"]
    if c["refine"] != 1.0:
        k += f"_r{c['refine']:g}"
    if c["dt_scale"] != 1.0:
        k += f"_dt{c['dt_scale']:g}".replace(".", "")
    return k


def TRI21(sei="fresh"):
    return cfg("tri", tau_median(), sei)


def CON(tau, sei="fresh"):
    return cfg("con", tau, sei)


def at(c, f):
    """The configuration a fraction is looked up in: f = 0 has no delivery, so every delivery shares it (D90 (3))."""
    if SR8.key(f) == 0.0:
        return dict(c, shape="none", tau_d=0.0)
    return c


def spec(c, test, f, models, stop, kind=""):
    t = by_test()[test]
    r = ratios()["central"]
    f = SR8.key(f)
    cc = at(c, f)
    mtag = {"both": "both", "lumped": "lum", "resolved": "res"}[models]
    rid = f"s9_{cfg_key(cc)}_{mtag}{'' if stop else '_ns'}_{test}_f{f:.9f}"
    return {"id": rid, "stage": 9, "kind": kind, "test": test, "kin": "mean", "connection": t["connection"],
            "h": "central", "g": "central", "tau": float(tau_median()), "E_body_J": float(t["E_b_J"]),
            "T_amb_K": float(V.LP.T_AMB), "refine": cc["refine"], "dt_scale": cc["dt_scale"], "f": f,
            "ratio": "central", "r": float(r), "E_e_J": float(r * t["E_b_J"]), "E_delivered_J": float(f * r * t["E_b_J"]),
            "shape": cc["shape"], "tau_d_s": cc["tau_d"], "geometry": "half", "f_e": 0.0, "sei": cc["sei"],
            "sei0": 0.0 if cc["sei"] == "aged" else None, "models": models, "stop": bool(stop), "t_end_s": 900.0,
            "max_sub": MAX_SUB, "cfg": cfg_key(cc)}


# ------------------------------------------------------------------------------------------------ the records' points
def _entry_res(rr, rid):
    t_c = rr.get("t_prop_s") if rr.get("propagated") else None
    pa = rr.get("probe_peak", {}).get("away", {})
    return {"t_c": t_c, "full": rr["t_end_s"] >= 900.0 - 1e-9, "peak_away": pa.get("T_C"),
            "t_peak_away": pa.get("t_s"), "peak_hot": rr.get("peak_hottest_C"), "t_end": rr["t_end_s"], "id": rid}


def _entry_lum(ll, rid):
    t_c = ll.get("t_prop_s") if ll.get("propagated") else None
    return {"t_c": t_c, "full": ll["t_end_s"] >= 900.0 - 1e-9, "peak": ll.get("peak_C"), "t_peak": ll.get("t_peak_s"),
            "t_end": ll["t_end_s"], "id": rid}


class Points:
    """Every point a chain can read: (configuration key, test, f) -> the resolved and the lumped entries, from Stage 7's
    and Stage 8's records (read-only) and Stage 9's. Where two records hold the same point, a run that went to its
    end is preferred, and the crossing times must agree (checked by the scoring, D95 (4))."""

    def __init__(self):
        self.res, self.lum, self.dups = {}, {}, []
        self.idx = {"res": {}, "lum": {}}

    def _put(self, part, k, e):
        d = self.res if part == "res" else self.lum
        old = d.get(k)
        if old is None:
            d[k] = e
            self.idx[part].setdefault((k[0], k[1]), set()).add(k)
            return
        self.dups.append((part, k, old["id"], e["id"], old["t_c"], e["t_c"]))
        if e["full"] and not old["full"]:
            d[k] = e

    def add(self, cfgk, test, f, rec):
        k = (cfgk, test, SR8.key(f))
        if rec.get("resolved"):
            self._put("res", k, _entry_res(rec["resolved"], rec["id"]))
        if rec.get("lumped"):
            self._put("lum", k, _entry_lum(rec["lumped"], rec["id"]))

    def _keys(self, part, c, test):
        ks = set(self.idx[part].get((cfg_key(c), test), ()))
        z = (cfg_key(at(c, 0.0)), test, 0.0)
        if z in (self.res if part == "res" else self.lum):
            ks.add(z)
        return ks

    def tc(self, c, test, crit):
        """{f: t_c} of a test, criterion and configuration, f = 0 included (D90 (3))."""
        part = "res" if crit == "C1" else "lum"
        d = self.res if part == "res" else self.lum
        return {k[2]: d[k]["t_c"] for k in self._keys(part, c, test)}

    def met(self, c, test, crit):
        return {f: (t is not None) for f, t in self.tc(c, test, crit).items()}

    def peaks(self, c, test, node):
        """{f: peak (C)} of the full runs: the thermocouple node ("away") or the lumped neighbour ("lumped")."""
        part = "res" if node == "away" else "lum"
        d = self.res if part == "res" else self.lum
        out = {}
        for k in self._keys(part, c, test):
            e = d[k]
            if e["full"]:
                out[k[2]] = e["peak_away"] if node == "away" else e["peak"]
        return out

    def entry(self, c, test, f, part):
        d = self.res if part == "res" else self.lum
        return d.get((cfg_key(at(c, f)), test, SR8.key(f)))


def stage7_records():
    """Stage 7's pertest (fresh) and aged runs at the central contact: f = 0 of every delivery."""
    def load():
        out = {}
        for t in tests():
            for sei, pre in (("fresh", "pertest"), ("aged", "aged")):
                suf = "_aged" if sei == "aged" else ""
                rid = (f"{pre}_{t['test']}_{t['connection']}_hcentral_gcentral_tau{tau_median():.2f}"
                       f"_E{t['E_b_J'] / 1e3:.2f}{suf}")
                out[(sei, t["test"])] = json.load(open(os.path.join(S7RUNS, rid + ".json")))
        return out
    return _get("s7", load)


def stage8_records():
    def load():
        out = []
        for p in glob.glob(os.path.join(S8RUNS, "*.json")):
            r = json.load(open(p))
            if r.get("failed") or r["set"] not in S8_SETS:
                continue
            assert r["geometry"] == "half" and r["ratio"] == "central" and r["f_e"] == 0.0
            assert r["refine"] == 1.0 and r["dt_scale"] == 1.0 and abs(r["tau_d_s"] - tau_median()) < 1e-9
            out.append(r)
        return out
    return _get("s8", load)


def stage7_zero():
    """For each test, whether C1 and C2 are met at f = 0 (Stage 7's pertest run, fresh SEI)."""
    s7 = stage7_records()
    return {t["test"]: {"C1": bool(s7[("fresh", t["test"])]["resolved"]["propagated"]),
                        "C2": bool(s7[("fresh", t["test"])]["lumped"]["propagated"])} for t in tests()}


_RECS = {}


def load_records(runs_dir=None):
    """Stage 9's records, read incrementally: a file already read is not read again."""
    runs_dir = RUNS if runs_dir is None else runs_dir
    cache = _RECS.setdefault(runs_dir, {})
    if os.path.isdir(runs_dir):
        for f in os.listdir(runs_dir):
            if not f.endswith(".json") or f in cache:
                continue
            try:
                cache[f] = json.load(open(os.path.join(runs_dir, f)))
            except (OSError, ValueError):
                continue
    return {r["id"]: r for r in cache.values()}


def points(recs):
    P = Points()
    for (sei, test), r in stage7_records().items():
        P.add(cfg_key(cfg("none", 0.0, sei)), test, 0.0, r)
    for r in stage8_records():
        P.add(cfg_key(TRI21()), r["test"], r["f"], r)
    for r in recs.values():
        if r.get("failed") or r.get("kind") == "xcheck":
            continue
        P.add(r["cfg"], r["test"], r["f"], r)
    return P


# ------------------------------------------------------------------------------------------------ the chains
def chain_defs():
    """Every chain, in the order its runs are listed (D96 (1))."""
    out = []
    prop = [t["test"] for t in tests() if t["propagated"]]
    nprop = [t["test"] for t in tests() if not t["propagated"]]
    for x in prop:
        for c in IN.CRITERIA:
            out.append({"name": f"A1_{c}_{x}", "kind": "grid", "test": x, "crit": c, "cfg": TRI21(), "part": "A"})
    for x in prop:
        for c in IN.CRITERIA:
            out.append({"name": f"A2_{c}_{x}", "kind": "ft", "test": x, "crit": c, "cfg": TRI21(), "part": "A",
                        "fs": ("stage8", c), "after_v1": True})
    for x in nprop:
        expl = x in IN.EXPLORATORY_FMAX
        out.append({"name": f"A3_{x}", "kind": "fmax", "test": x, "cfg": TRI21(), "part": "A", "node": "away",
                    "up": None if expl else ("stage8", "C1"), "exploratory": expl})
        out.append({"name": f"A3L_{x}", "kind": "fmax", "test": x, "cfg": TRI21(), "part": "A", "node": "lumped",
                    "up": None if expl else ("stage8", "C2"), "exploratory": True})
    for tau in IN.TAUS_B:
        for t in tests():
            x = t["test"]
            for c in IN.CRITERIA:
                out.append({"name": f"B_fs_{c}_{tau:.0f}_{x}", "kind": "fstar", "test": x, "crit": c, "cfg": CON(tau),
                            "part": "B"})
            if t["propagated"]:
                for c in IN.CRITERIA:
                    out.append({"name": f"B_ft_{c}_{tau:.0f}_{x}", "kind": "ft", "test": x, "crit": c, "cfg": CON(tau),
                                "part": "B", "fs": ("chain", f"B_fs_{c}_{tau:.0f}_{x}")})
            else:
                expl = x in IN.EXPLORATORY_FMAX
                out.append({"name": f"B_fm_{tau:.0f}_{x}", "kind": "fmax", "test": x, "cfg": CON(tau), "part": "B",
                            "node": "away", "up": None if expl else ("chain", f"B_fs_C1_{tau:.0f}_{x}"),
                            "exploratory": expl})
                out.append({"name": f"B_fmL_{tau:.0f}_{x}", "kind": "fmax", "test": x, "cfg": CON(tau), "part": "B",
                            "node": "lumped", "up": None if expl else ("chain", f"B_fs_C2_{tau:.0f}_{x}"),
                            "exploratory": expl})
    for x in IN.P8_TESTS:
        for c in IN.CRITERIA:
            out.append({"name": f"C3_fs_{c}_{x}", "kind": "fstar", "test": x, "crit": c, "cfg": TRI21("aged"),
                        "part": "C3"})
        for c in IN.CRITERIA:
            out.append({"name": f"C3_ft_{c}_{x}", "kind": "ft", "test": x, "crit": c, "cfg": TRI21("aged"), "part": "C3",
                        "fs": ("chain", f"C3_fs_{c}_{x}")})
    v = IN.V3_CASE
    out.append({"name": "V3", "kind": "v3", "test": v["test"], "cfg": CON(v["tau_s"]), "part": "V3",
                "fs": ("chain", f"B_fs_{v['criterion']}_{v['tau_s']:.0f}_{v['test']}")})
    for x in prop:
        for d in ["tri21"] + [f"{tau:.0f}" for tau in IN.TAUS_B]:
            c = TRI21() if d == "tri21" else CON(float(d))
            src = f"A2_C2_{x}" if d == "tri21" else f"B_ft_C2_{d}_{x}"
            out.append({"name": f"S_{d}_{x}", "kind": "story", "test": x, "cfg": c, "part": "story", "after": src})
    return out


def _fs_of(ch, states):
    kind, what = ch["fs"]
    if kind == "stage8":
        return fstar8()[ch["test"]][what]
    st = states.get(what)
    if st is None or st["status"] in ("searching", "waiting"):
        return {"status": "waiting", "lo": None, "hi": None}
    return SR8.f_star(st)


def _run_for(ch, c, f, crit=None, node=None, stop=True):
    if crit == "C2" or node == "lumped":
        return spec(c, ch["test"], f, "lumped", stop, kind=ch["kind"])
    return spec(c, ch["test"], f, "both", stop, kind=ch["kind"])


def fstar_replay(met_all):
    """D78's search replayed along its own path: from f = 0, each next fraction of stage8_search.state is read from
    the records if it is there and is the next run otherwise. Fractions that other chains ran in the same
    configuration are read only where the path reaches them, so f* does not move as they accumulate (D93 (2))."""
    pts = {}
    if 0.0 not in met_all:
        return {"status": "searching", "next": 0.0, "lo": None, "hi": None, "points": pts}
    pts[0.0] = met_all[0.0]
    while True:
        st = SR8.state(pts, IN.PROBES_FSTAR, width=IN.WIDTH_FSTAR, f_max=IN.F_MAX)
        if st["status"] != "searching" or st["next"] not in met_all:
            return dict(st, points=dict(pts))
        pts[st["next"]] = met_all[st["next"]]


def chain_state(ch, P, states, v1_ready):
    k = ch["kind"]
    x = ch["test"]
    if k == "grid":
        fs = fstar8()[x][ch["crit"]]
        g = IN.grid(fs["hi"])
        tc = P.tc(ch["cfg"], x, ch["crit"])
        need = [f for f in g if f not in tc]
        st = {"status": "searching" if need else "done", "grid": g, "fs": fs,
              "tc": {f: tc[f] for f in g if f in tc}}
        st["runs"] = [_run_for(ch, ch["cfg"], f, ch["crit"]) for f in need]
        return st
    if k == "ft":
        if ch.get("after_v1") and not v1_ready:
            return {"status": "waiting", "runs": []}
        fs = _fs_of(ch, states)
        if fs["status"] == "waiting":
            return {"status": "waiting", "runs": []}
        if fs["status"] == "broken":
            return {"status": "broken", "runs": [], "fs": fs}
        g = IN.grid(fs["hi"]) if fs["status"] in ("zero", "bracket") else []
        tc = P.tc(ch["cfg"], x, ch["crit"])
        st = S9.ft_state(t_meas(x), fs, g, tc, tol_s=IN.T_TOL_S, width=IN.WIDTH_T)
        st["runs"] = [_run_for(ch, ch["cfg"], st["next"], ch["crit"])] if st["status"] == "searching" else []
        st["tc"] = tc
        return st
    if k == "fstar":
        st = fstar_replay(P.met(ch["cfg"], x, ch["crit"]))
        st["runs"] = [_run_for(ch, ch["cfg"], st["next"], ch["crit"])] if st["status"] == "searching" else []
        return st
    if k == "fmax":
        node = ch["node"]
        if ch["up"] is None:
            f_up = 0.0                           # the exploratory search: from 0 to 1 (D92 (3))
        else:
            kind, what = ch["up"]
            if kind == "stage8":
                fs = fstar8()[x][what]
            else:
                stf = states.get(what)
                if stf is None or stf["status"] in ("searching", "waiting"):
                    return {"status": "waiting", "runs": []}
                fs = SR8.f_star(stf)
            if fs["status"] not in ("zero", "bracket"):
                f_up = IN.F_MAX if fs["status"] == "above" else None
                if f_up is None:
                    return {"status": "broken", "runs": [], "fs": fs}
            else:
                f_up = fs["lo"]
        pk = P.peaks(ch["cfg"], x, node)
        st = S9.fmax_state(max_meas(x), f_up, pk, tol_k=IN.PEAK_TOL_K, width=IN.WIDTH_M, f_end=IN.F_MAX)
        st["pk"] = pk
        st["runs"] = ([_run_for(ch, ch["cfg"], st["next"], node=node, stop=False)]
                      if st["status"] == "searching" else [])
        if st["status"] == "searching" and ch.get("exploratory") and node == "away":
            st["speculative_runs"] = [dict(_run_for(ch, ch["cfg"], q, node=node, stop=False), speculative=True)
                                      for q in st.get("speculative", [])]
        return st
    if k == "v3":
        stf = states.get(ch["fs"][1])
        if stf is None or stf["status"] in ("searching", "waiting"):
            return {"status": "waiting", "runs": []}
        fs = SR8.f_star(stf)
        if fs["status"] != "bracket":
            return {"status": "not applicable", "runs": [], "fs": fs}
        f = fs["lo"] if fs["lo"] > 0 else fs["hi"]
        base = P.entry(ch["cfg"], x, f, "res")
        runs = []
        if base is None or not base["full"]:
            runs.append(spec(ch["cfg"], x, f, "both", False, kind="v3"))
        for c in (dict(ch["cfg"], refine=2.0), dict(ch["cfg"], dt_scale=0.5)):
            e = P.entry(c, x, f, "res")
            if e is None:
                runs.append(spec(c, x, f, "resolved", False, kind="v3"))
        return {"status": "searching" if runs else "done", "f": f, "fs": fs, "runs": runs}
    if k == "story":
        src = states.get(ch["after"])
        if src is None or src["status"] in ("searching", "waiting"):
            return {"status": "waiting", "runs": []}
        if src.get("f_t") is None:
            return {"status": "not applicable", "runs": []}
        f = SR8.key(round(src["f_t"], 6))
        e = P.entry(ch["cfg"], x, f, "res")
        if e is not None and e["full"]:
            return {"status": "done", "f": f, "runs": []}
        return {"status": "searching", "f": f, "runs": [spec(ch["cfg"], x, f, "both", False, kind="story")]}
    raise ValueError(k)


def all_states(P, v1_ready=None):
    if v1_ready is None:
        v1_ready = os.path.exists(V1_FILE)
    states = {}
    for ch in chain_defs():
        states[ch["name"]] = chain_state(ch, P, states, v1_ready)
    return states


def v1_payload(states):
    """V1 (D95 (1)): t_c against f on every A1 grid, with each pair in which the crossing comes later at the larger
    fraction (or not at all)."""
    out = {}
    for name, st in states.items():
        if not name.startswith("A1_"):
            continue
        g = st["grid"]
        tc = st["tc"]
        _, pairs = S9.monotone_part(g, tc)
        out[name] = {"grid": g, "t_c": [tc.get(f) for f in g], "non_monotone_pairs": pairs}
    return {"written_utc": RUN._utc(), "chains": out,
            "flagged": sorted(k for k, v in out.items() if v["non_monotone_pairs"])}


def maybe_write_v1(states):
    """Once every A1 chain has ended, V1 is written before any A2 run is listed (the brief)."""
    if os.path.exists(V1_FILE):
        return True
    if not all(st["status"] == "done" for n, st in states.items() if n.startswith("A1_")):
        return False
    tmp = V1_FILE + f".tmp{os.getpid()}"
    json.dump(v1_payload(states), open(tmp, "w"), indent=1, default=float)
    try:
        os.replace(tmp, V1_FILE)
    except OSError:
        pass
    return True


PRIORITY = {"xcheck": 0, "lumped": 1, "explore": 2, "V3": 2, "B": 3, "C3": 3, "A": 4, "story": 5, "speculative": 8}


def priority(ch, run):
    if run["models"] == "lumped":
        return PRIORITY["lumped"]
    if ch.get("exploratory"):
        return PRIORITY["explore"]
    return PRIORITY.get(ch["part"], 9)


def xcheck_runs():
    out = []
    for rid in IN.XCHECK:
        r = json.load(open(os.path.join(S8RUNS, rid + ".json")))
        sp = {k: r[k] for k in ("id", "set", "test", "kin", "connection", "h", "g", "tau", "E_body_J", "T_amb_K",
                                "refine", "dt_scale", "f", "ratio", "r", "E_e_J", "E_delivered_J", "tau_d_s",
                                "geometry", "f_e", "E_joule_J", "models", "gas", "t_end_s", "max_sub")}
        out.append(dict(sp, id="xcheck_" + rid, kind="xcheck", stage8_id=rid))
    return out


def build_runs(recs, states=None):
    """The run list as it stands: the cross-check, then every chain's next runs by priority (D96 (1))."""
    if states is None:
        P = points(recs)
        ready = os.path.exists(V1_FILE)
        states = all_states(P, ready)
        if not ready and maybe_write_v1(states):
            states = all_states(P, True)
    out, seen = [], set()
    for r in xcheck_runs():
        out.append((0, 0, r))
        seen.add(r["id"])
    for i, ch in enumerate(chain_defs()):
        for r in states[ch["name"]].get("runs", []):
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            out.append((priority(ch, r), i, r))
    for i, ch in enumerate(chain_defs()):
        for r in states[ch["name"]].get("speculative_runs", []):
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            out.append((PRIORITY["speculative"], i, r))
    out.sort(key=lambda x: (x[0], x[1]))
    return [r for _, _, r in out]


def runs_hash(runs):
    return hashlib.sha256(json.dumps(runs, sort_keys=True).encode()).hexdigest()


# ------------------------------------------------------------------------------------------------ one run
class Context(RUN.Context):
    def __init__(self):
        super().__init__()
        self.shares = {}

    def share(self, h, refine):
        key = (h, refine)
        if key not in self.shares:
            self.shares[key] = M9.share_surface(self.model(h, refine), "half")
        return self.shares[key]


def _pulse(sp):
    if sp["shape"] == "tri":
        return M9.Triangular(sp["E_delivered_J"], sp["tau_d_s"], 0.0)
    if sp["shape"] == "con":
        return M9.Constant(sp["E_delivered_J"], sp["tau_d_s"], 0.0)
    raise ValueError(sp["shape"])


def run_one(sp, ctx, keep_series=True):
    """One Stage 9 run: its record has Stage 8's fields for each neighbour, with the crossing whether or not the run
    stopped there, the thermocouple node's peak and whether the run went to its end."""
    if sp.get("kind") == "xcheck":
        return R8.run_one(sp, R8.Context())
    t_start = time.time()
    t1f, t1data, T1max_C, tT1max = ctx.history(sp)
    kin, draw = ctx.kinetics(sp["kin"])
    g_pos, g_neg = V.tabs(sp["connection"], V.G_TAB[sp["g"]])
    model = ctx.model(sp["h"], sp["refine"])
    src_r, src_l = [], []
    if sp["E_delivered_J"] > 0.0:
        src_r = [M9.Source("delivery", _pulse(sp), ctx.share(sp["h"], sp["refine"]))]
        src_l = [M9.Source("delivery", _pulse(sp))]
    saved = (RX.DT_BASE, RX.DT_TARGET, RX.DT_ACCEPT)
    if sp["dt_scale"] != 1.0:
        RX.DT_BASE, RX.DT_TARGET, RX.DT_ACCEPT = (x * sp["dt_scale"] for x in saved)
    stop = V.LEVEL_PROP if sp["stop"] else None
    r = lr = None
    try:
        if sp["models"] in ("both", "resolved"):
            r = M9.run_resolved(model, t1f, g_pos, g_neg, kin=kin, t_amb=sp["T_amb_K"], t_end=sp["t_end_s"],
                                stop_level=stop, probes=model.probes, keep_series=keep_series,
                                max_facts=6 if sp["refine"] == 1.0 else 2, sources=src_r, max_sub=sp["max_sub"],
                                sei0=sp["sei0"])
        if sp["models"] in ("both", "lumped"):
            lr = M9.run_lumped(t1f, g_pos + g_neg, g_link=V.g_contact(V.H_CONTACT[sp["h"]]), f_view=V.F_TOUCH,
                               kin=kin, t_amb=sp["T_amb_K"], t_end=sp["t_end_s"], stop_level=stop, sources=src_l,
                               max_sub=sp["max_sub"], sei0=sp["sei0"])
    finally:
        RX.DT_BASE, RX.DT_TARGET, RX.DT_ACCEPT = saved
    rec = dict(sp)
    rec.update({"draw": draw, "h_c_W_m2K": V.H_CONTACT[sp["h"]], "G_tab_W_K": V.G_TAB[sp["g"]],
                "G_contact_W_K": V.g_contact(V.H_CONTACT[sp["h"]]), "g_pos_W_K": g_pos, "g_neg_W_K": g_neg,
                "T1max_C": T1max_C, "t_T1max_s": tT1max, "n_nodes": int(model.C.size), "resolved": None,
                "lumped": None})
    series = {"t1_t": t1data[:, 0], "t1_T1_C": t1data[:, 1], "t1_T2_C": t1data[:, 2]}
    if r is not None:
        t_x = r["cross_s"]["T_onset_low"]
        res = {"propagated": t_x is not None, "t_prop_s": t_x, "stopped": r["stop"] is not None,
               "t_end_s": r["t_end_s"], "steps": r["steps"], "rejected": r["rejected"],
               "max_implicit_nodes": r["max_implicit_nodes"], "energy_residual_rel": r["energy_residual_rel"],
               "peak_hottest_C": r["peak"]["Tmax_C"], "t_peak_hottest_s": r["peak"]["t_s"],
               "where_peak": model.where(r["peak"]["imax"]), "peak_mean_C": r["peak"]["Tmean_C"],
               "probe_peak": r["probe_peak"], "in_rxn_J": r["energy_J"]["in_rxn"], "cross_s": r["cross_s"],
               "energy_J": r["energy_J"], "stored_J": r["stored_J"], "net_in_J": r["net_in_J"],
               "sources": r["sources"], "max_sub": r["max_sub"], "steps_with_max_sub": r["steps_with_max_sub"],
               "implicit_node_steps_with_max_sub": r["implicit_node_steps_with_max_sub"],
               "conversion_volume_mean_end": r["conversion_volume_mean_end"],
               "max_local_reaction_heating_K_per_s": r["max_local_reaction_heating_K_per_s"]}
        if r["stop"] is not None:
            tp = r["stop"]["t_s"]
            res.update({"where": r["stop"]["where"], "mean_at_prop_C": r["stop"]["Tmean_C"],
                        "T1_at_prop_C": t1f(tp) - 273.15})
        rec["resolved"] = res
        s = r["series"]
        series.update({"t": s[:, 0], "T1": s[:, 1], "Tmax": s[:, 2], "Tmean": s[:, 3], "imax": s[:, 4].astype(int),
                       "probe_t": r["probe_t"], "probe_toward": r["probe_T"]["toward"],
                       "probe_away": r["probe_T"]["away"]})
    if lr is not None:
        t_xl = lr["cross_s"]["T_onset_low"]
        lres = {"propagated": t_xl is not None, "t_prop_s": t_xl, "stopped": lr["stop"] is not None,
                "peak_C": lr["peak"]["T_C"], "t_peak_s": lr["peak"]["t_s"], "reaction_heat_J": lr["reaction_heat_J"],
                "t_end_s": lr["t_end_s"], "energy_J": lr["energy_J"], "energy_residual_rel": lr["energy_residual_rel"],
                "conversion_end": lr["conversion_end"], "cross_s": lr["cross_s"], "sources": lr["sources"],
                "stored_J": lr["stored_J"], "net_in_J": lr["net_in_J"]}
        rec["lumped"] = lres
        series.update({"t_lumped": lr["series"][:, 0], "T_lumped": lr["series"][:, 1]})
    rec["wall_s"] = time.time() - t_start
    return rec, (series if keep_series else None)


# ------------------------------------------------------------------------------------------------ the work loop
def peak_memory_mb():
    try:
        import resource
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    except Exception:
        return None


def _paths(sp):
    if sp.get("kind") == "xcheck":
        return os.path.join(XCHK, sp["id"] + ".json"), os.path.join(XCHK, sp["id"] + ".npz")
    return os.path.join(RUNS, sp["id"] + ".json"), os.path.join(SERIES, sp["id"] + ".npz")


def _recorded(sp, recs):
    if sp.get("kind") == "xcheck":
        return os.path.exists(_paths(sp)[0])
    return sp["id"] in recs


def work(worker, budget_min=1e9, wall_min=1e9, label="unlabelled", wait_s=10.0, sets=None, once=False):
    """Stage 8's loop with Stage 9's list, which grows as the chains advance: each pass rebuilds the list from the
    records, takes the first run that is neither recorded nor claimed, and runs it. Claims as D43 (3); a run
    interrupted at the wall time is not recorded; a failed run is recorded as failed (D96 (1))."""
    for d in (RUNS, SERIES, XCHK):
        os.makedirs(d, exist_ok=True)
    ctx = Context()
    machine = RUN.machine_info(label)
    t0 = time.time()
    done = 0
    if hasattr(signal, "SIGALRM"):
        signal.signal(signal.SIGALRM, RUN._alarm)
    while True:
        recs = load_records()
        runs = build_runs(recs)
        if sets is not None:
            runs = [r for r in runs if r.get("kind") in sets]
        pending = [r for r in runs if not _recorded(r, recs)]
        if not pending:
            claims = [f for f in os.listdir(RUNS) if f.endswith(".claim")]
            if claims:
                time.sleep(wait_s)               # another worker's run will extend the list
                continue
            print(f"{RUN._utc()} worker {worker}: nothing left to run ({done} this pass)", flush=True)
            return done
        started = False
        for sp in pending:
            elapsed = (time.time() - t0) / 60.0
            left = wall_min - elapsed
            if elapsed > budget_min or left < START_MARGIN_MIN or os.path.exists(STOP_FILE):
                print(f"{RUN._utc()} worker {worker}: stopping after {done} runs (budget, wall time or stop file)",
                      flush=True)
                return done
            claim = os.path.join(RUNS, sp["id"] + ".claim")
            if not RUN._claim(claim, worker):
                continue
            started = True
            path, spath = _paths(sp)
            wall_s = int(left * 60) - RUN.WALL_MARGIN_S
            limit_s = int(RUN_LIMIT_MIN[sp["refine"]] * 60)
            st_utc = RUN._utc()
            try:
                try:
                    RUN._arm(min(limit_s, wall_s), "wall" if wall_s < limit_s else "limit")
                    rec, series = run_one(sp, ctx)
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
                print(f"{RUN._utc()} worker {worker}: {sp['id']} interrupted at the wall time and not recorded; "
                      f"stopping after {done} runs", flush=True)
                return done
            except Exception as exc:
                import traceback
                RX.DT_BASE, RX.DT_TARGET, RX.DT_ACCEPT = 0.1, 1.0, 4.0
                rec, series = dict(sp), None
                rec.update({"failed": True, "error": repr(exc), "traceback": traceback.format_exc()})
            finally:
                RUN._disarm()
            rec["worker_peak_memory_MB"] = peak_memory_mb()
            rec["started_utc"], rec["finished_utc"] = st_utc, RUN._utc()
            rec["machine"] = machine
            rec["worker"] = worker
            if series is not None:
                np.savez_compressed(spath, **series)
            tmp = path + f".tmp{os.getpid()}"
            with open(tmp, "w") as fh:
                json.dump(rec, fh, indent=1, default=float)
            os.replace(tmp, path)
            RUN._unclaim(claim)
            done += 1
            print(f"{RUN._utc()} {summary(rec)}", flush=True)
            break                                # re-read the list: the chains may have moved
        if once:
            return done
        if not started:
            time.sleep(wait_s)                   # every pending run is claimed by another worker


def summary(rec):
    if rec.get("failed"):
        return f"{rec['id']}: FAILED {rec['error']}"
    parts = [rec["id"]]
    rr, ll = rec.get("resolved"), rec.get("lumped")
    if rr:
        parts.append(f"hot spot {'%.1f s' % rr['t_prop_s'] if rr['propagated'] else 'none'} "
                     f"(peak {rr['peak_hottest_C']:.1f} C, away {rr['probe_peak']['away']['T_C']:.1f} C)")
    if ll:
        parts.append(f"lumped {'%.1f s' % ll['t_prop_s'] if ll['propagated'] else 'none'} (peak {ll['peak_C']:.1f} C)")
    parts.append(f"{rec['wall_s']:.0f} s")
    return "; ".join(parts)


def status():
    recs = load_records()
    P = points(recs)
    states = all_states(P)
    by = {}
    for s in states.values():
        by[s["status"]] = by.get(s["status"], 0) + 1
    runs = build_runs(recs, states)
    pend = [r for r in runs if not _recorded(r, recs)]
    print(json.dumps({"records": len(recs), "failed": sum(1 for r in recs.values() if r.get("failed")),
                      "pending_now": len(pend), "pending_resolved": sum(r["models"] != "lumped" for r in pend),
                      "chains": by, "v1_written": os.path.exists(V1_FILE),
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
    ap.add_argument("--budget-min", type=float, default=1e9)
    ap.add_argument("--wall-min", type=float, default=1e9)
    ap.add_argument("--label", default="unlabelled")
    ap.add_argument("--sets", nargs="*", default=None)
    a = ap.parse_args()
    if a.cmd == "list":
        recs = load_records()
        runs = build_runs(recs)
        print(len(runs), "runs listed now; sha256", runs_hash(runs))
        print(len(chain_defs()), "chains", {k: sum(c["kind"] == k for c in chain_defs())
                                            for k in ("grid", "ft", "fmax", "fstar", "v3", "story")})
    elif a.cmd == "chains":
        recs = load_records()
        for name, st in all_states(points(recs)).items():
            print(name, st["status"], st.get("lo"), st.get("hi"), st.get("next"), st.get("f_t"), st.get("f_max"))
    elif a.cmd == "work":
        work(a.worker, a.budget_min, a.wall_min, label=a.label, sets=set(a.sets) if a.sets else None)
    elif a.cmd == "reset-claims":
        reset_claims()
    else:
        status()
