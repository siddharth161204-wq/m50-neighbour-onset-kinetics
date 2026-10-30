#!/usr/bin/env python3
"""Stage 10 checks (DECISIONS.md D106 (2)): V2, V3, V4 and X; V1 is `stage10_v1.py` (it needs the supplement's PDF).
  V2  the probes' nodes in every record are those of D102 (4), with their distances from the line of contact;
  V3  Part C recomputed by separate code: Firth's logistic by root finding on the penalised score (scipy), Spearman's
      rho by scipy, the permutations with another seed; acceptance 1e-10 in the scores, and every p-value within
      four standard errors of the Monte Carlo plus 1/N of the scoring's;
  V4  the energy accounts and deliveries of every Stage 10 record (Stage 9's V4, `stage9_checks.v4`);
  X   where a Stage 10 run holds a point that a Stage 7 or Stage 9 record holds (the same test, delivery, fraction
      and contact), the histories they share (the hottest node, the toward and away probes, the lumped neighbour)
      agree up to the shorter run's end (acceptance 1e-6 K).
Writes results/stage10_checks.json."""
import glob, json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage9_checks as C9               # noqa: E402  (unchanged)
import stage10_inputs as IN              # noqa: E402
import stage10_run as R10                # noqa: E402
import stage10_partc as PC               # noqa: E402

RES = os.path.join(HERE, "..", "results")


def v2(recs):
    bad = []
    for r in recs.values():
        if r.get("failed"):
            continue
        for name, d in list(IN.NODES.items()) + list(IN.EXTRA_PROBES.items()):
            w = r["probe_where"][name]
            if abs(w["theta_deg"] - d["theta_deg"]) > 1e-5 or abs(w["z_mm"] - 35.05) > 1e-9 or abs(w["r_mm"] - 10.55) > 1e-9:
                bad.append((r["id"], name, w))
    dist = {n: {"theta_deg": d["theta_deg"], "arc_mm": IN.arc_mm(d["theta_deg"]),
                "chord_mm": 2 * 10.55 * math.sin(math.radians(d["theta_deg"]) / 2)} for n, d in
            list(IN.NODES.items()) + list(IN.EXTRA_PROBES.items())}
    return {"pass": not bad, "records": sum(1 for r in recs.values() if not r.get("failed")), "bad": bad,
            "distances_from_line": dist}


# ------------------------------------------------------------------------------------------------ V3
def firth_root(x, y):
    from scipy.optimize import root
    y = np.asarray(y, float)
    if x is None or np.std(x) == 0.0:
        return None
    x = np.asarray(x, float)
    X = np.column_stack([np.ones(len(y)), x])

    def score(b):
        p = 1.0 / (1.0 + np.exp(-(X @ b)))
        W = p * (1 - p)
        I = X.T @ (W[:, None] * X)
        A = np.sqrt(W)[:, None] * X
        h = np.einsum("ij,jk,ik->i", A, np.linalg.inv(I), A)
        return X.T @ (y - p + h * (0.5 - p))
    s = root(score, np.zeros(2), method="hybr", tol=1e-14)
    return s.x


def v3(scored_held, scored_rank, n_perm=IN.N_PERM, seed=IN.SEED + 100):
    from scipy.stats import spearmanr
    rows = scored_held["table"]
    y = np.array([r["y"] for r in rows], float)
    ser = np.array([r["connection"] == "series" for r in rows])
    worst = 0.0
    pv = []
    rng = np.random.default_rng(seed)
    perms = np.array([rng.permutation(y) for _ in range(n_perm)])

    def d_log(x, yy, tr, te):
        k, n = yy[tr].sum(), tr.sum()
        pc = (k + 0.5) / (n + 1.0)
        b = firth_root(x[tr], yy[tr])
        if b is None:
            pg = np.full(te.sum(), pc)
        else:
            pg = 1.0 / (1.0 + np.exp(-(b[0] + b[1] * x[te])))
        ls = lambda p: float(np.mean(yy[te] * np.log(p) + (1 - yy[te]) * np.log(1 - p)))
        return ls(pg) - ls(np.full(te.sum(), pc)), float(np.mean((pg - yy[te]) ** 2) - np.mean((pc - yy[te]) ** 2))
    for name in PC.PREDICTORS:
        x = np.array([r[name] for r in rows], float)
        for d, (tr, te) in {"series_to_parallel": (ser, ~ser), "parallel_to_series": (~ser, ser)}.items():
            o = scored_held["predictors"][name][d]
            dl, db = d_log(x, y, tr, te)
            worst = max(worst, abs(dl - o["observed"]["d_log"]), abs(db - o["observed"]["d_brier"]))
            sl = np.array([d_log(x, perms[k], tr, te)[0] for k in range(n_perm)])
            p = (1 + np.sum(sl >= dl - 1e-12)) / (1 + n_perm)
            se = math.sqrt(max(p * (1 - p), 1.0 / n_perm) / n_perm)
            pv.append({"what": f"{name} {d} log", "p": p, "p_scoring": o["p_log"], "ok": abs(p - o["p_log"]) <= 4 * se + 1.0 / n_perm})
    rho_worst = 0.0
    big = lambda v: [1e30 if a is None else a for a in v]
    prop = [r for r in rows if r["y"]]
    for q, dd in scored_rank["quantities"].items():
        if "outcome" not in dd:
            continue
        v = big([r[q] for r in rows])
        for what, a, b in (("outcome", v, [r["y"] for r in rows]),
                           ("time", big([r[q] for r in prop]), [r["time_s"] for r in prop]),
                           ("E_b", v, [r["E_b_J"] for r in rows])):
            rho = spearmanr(a, b)[0]
            rho_worst = max(rho_worst, abs(rho - dd[what]["rho"]))
    ok = worst < 1e-10 and rho_worst < 1e-10 and all(x["ok"] for x in pv)
    return {"pass": ok, "largest_score_difference": worst, "largest_rho_difference": rho_worst, "p_values": pv,
            "seed": seed}


# ------------------------------------------------------------------------------------------------ X
def _key9(test, cfg, f):
    return f"s9_{cfg}_both_ns_{test}_f{f:.9f}", f"s9_{cfg}_both_{test}_f{f:.9f}"


def same_points(recs):
    out, worst = [], 0.0
    for rid, r in recs.items():
        if r.get("failed") or r["h"] != "central":
            continue
        cand = []
        for k in _key9(r["test"], r["cfg"], r["f"]):
            p = os.path.join(RES, "stage9_series", k + ".npz")
            if os.path.exists(p):
                cand.append(("stage9", k, p))
        if r["f"] == 0.0:
            for p in glob.glob(os.path.join(RES, "stage7_series", f"pertest_{r['test']}_*_hcentral_gcentral_tau21.39_*.npz")):
                if "aged" not in p:
                    cand.append(("stage7", os.path.basename(p)[:-4], p))
        if not cand:
            continue
        s10 = np.load(os.path.join(RES, "stage10_series", rid + ".npz"))
        for src, k, p in cand:
            z = np.load(p)
            d = {}
            for a, b in (("Tmax", "Tmax"), ("probe_away", "probe_away"), ("probe_toward", "probe_toward"), ("T_lumped", "T_lumped")):
                ta = s10["t_lumped"] if a == "T_lumped" else (s10["probe_t"] if a.startswith("probe") else s10["t"])
                tb = z["t_lumped"] if b == "T_lumped" else (z["probe_t"] if b.startswith("probe") else z["t"])
                n = min(len(ta), len(tb))
                if n < 2 or not np.allclose(ta[:n], tb[:n], atol=1e-9):
                    d[a] = None
                    continue
                d[a] = float(np.max(np.abs(s10[a][:n] - z[b][:n])))
            vals = [v for v in d.values() if v is not None]
            m = max(vals) if vals else None
            if m is not None:
                worst = max(worst, m)
            out.append({"stage10": rid, "other": k, "source": src, "largest_K": m, "by_series": d})
    return {"pass": all(o["largest_K"] is not None and o["largest_K"] <= 1e-6 for o in out), "pairs": len(out),
            "largest_K": worst, "pairs_list": out}


def main():
    recs = R10.load_records()
    out = {"V2": v2(recs), "V4": C9.v4(recs), "X": same_points(recs)}
    hp, rp = os.path.join(RES, "stage10_heldout.json"), os.path.join(RES, "stage10_rank.json")
    if os.path.exists(hp) and os.path.exists(rp):
        out["V3"] = v3(json.load(open(hp)), json.load(open(rp)))
    v1 = os.path.join(RES, "stage10_v1.json")
    if os.path.exists(v1):
        j = json.load(open(v1))
        out["V1"] = {"pass": j["pass"], "panels": {k: {kk: p[kk] for kk in ("seconds_read", "seconds_in_window",
                                                                          "largest_difference_K", "pass")}
                                                  for k, p in j["panels"].items()}}
    json.dump(out, open(os.path.join(RES, "stage10_checks.json"), "w"), indent=1, default=float)
    print(json.dumps({k: v.get("pass") for k, v in out.items()}))


if __name__ == "__main__":
    main()
