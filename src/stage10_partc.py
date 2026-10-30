#!/usr/bin/env python3
"""Stage 10, Part C (DECISIONS.md D105): what the sixteen tests can tell a model, by arithmetic on the per-test
quantities Stages 7 to 9 already hold (and the six no-delivery runs of D104 (4)).

C1, held out: for each predictor (Stage 8's f*(C1) and f*(C2), and Stage 9's fraction read from the test, f_t(C2) or
f_max), fit on the eight series tests one probability for every test and a logistic in the predictor, score the
eight parallel tests by the mean log score (the mean of ln p of the outcome) and the Brier score, then the other way
round; both models are fitted by Firth's penalised likelihood (the Jeffreys prior), which keeps a logistic finite
where the predictor separates the training half, and gives the constant (k + 0.5) / (n + 1). The difference is the
logistic's score less the constant's; its permutation distribution comes from 10,000 relabellings of the sixteen
outcomes (seed 20261030), the predictors and the split held, and its p-value is the share of relabellings at least as
favourable to the logistic as the outcomes themselves, counted with the observed one.
C2, ranking: the Spearman correlation (average ranks for ties) of each per-test model quantity with the outcome, the
measured time (the nine propagated tests) and the trigger's body energy, with a two-sided permutation p-value (10,000
relabellings of the second variable); the connection as a two-group test on the same quantities (the difference of
the groups' mean ranks, the labels relabelled).
C3, the spread: for each criterion and delivery, the ratio of the largest to the smallest non-zero fraction read from
the tests, and the share of the sixteen whose fraction is zero; the same for the thresholds f*.

Usage: python3 stage10_partc.py   (writes results/stage10_heldout.json and results/stage10_rank.json)"""
import csv, glob, json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage9_run as R9                  # noqa: E402  (unchanged)
import stage10_inputs as IN              # noqa: E402

RES = os.path.join(HERE, "..", "results")
PREDICTORS = ("fC1", "fC2", "f9")
QUANTITIES = ("fC1", "fC2", "f9", "peak_away_f0", "t_c1_f0")
DELIVERIES = ("tri21", "120", "240", "360")


# ------------------------------------------------------------------------------------------------ the table
def _mid(fs):
    if fs["status"] == "zero":
        return 0.0, 0.0, 0.0
    return 0.5 * (fs["lo"] + fs["hi"]), fs["lo"], fs["hi"]


def _f9(states, test, propagated):
    """Stage 9's fraction read from the test: f_t(C2) for a propagated test (a matched or bracketed value; a threshold
    bracket's midpoint), f_max at the thermocouple node for the others (the two high maxima exploratory)."""
    if propagated:
        s = states[f"A2_C2_{test}"]
        if s["status"] in ("matched", "bracketed"):
            return s["f_t"], s.get("lo", s["f_t"]), s.get("hi", s["f_t"]), s["status"]
        assert s["status"] == "threshold", (test, s["status"])
        return 0.5 * (s["lo"] + s["hi"]), s["lo"], s["hi"], "threshold"
    s = states[f"A3_{test}"]
    assert s["status"] in ("zero", "matched", "bracketed"), (test, s["status"])
    return s["f_max"], s["f_max"], s["f_max"], s["status"]


def _no_delivery(test):
    """The thermocouple node's peak with no delivery over 900 s, and the hot spot's crossing at f = 0 (Stage 7's run at
    the central contact; where it stopped at the crossing, Stage 9's or Stage 10's run with the stop lifted)."""
    p = [x for x in glob.glob(os.path.join(RES, "stage7_runs", f"pertest_{test}_*_hcentral_gcentral_tau21.39_*.json"))
         if "aged" not in x]
    assert len(p) == 1, p
    r7 = json.load(open(p[0]))["resolved"]
    t_c = r7["t_prop_s"] if r7["propagated"] else None
    if r7["t_end_s"] >= 900.0 - 1e-9:
        return r7["probe_peak"]["away"]["T_C"], t_c, "stage7"
    for src, pat in (("stage9", os.path.join(RES, "stage9_runs", f"s9_none_fresh_both_ns_{test}_f0.000000000.json")),
                     ("stage10", os.path.join(RES, "stage10_runs", f"s10_none_fresh_hcentral_{test}_f0.000000000_t900.json"))):
        if os.path.exists(pat):
            r = json.load(open(pat))["resolved"]
            assert r["t_end_s"] >= 900.0 - 1e-9
            return r["probe_peak"]["away"]["T_C"], t_c, src
    return None, t_c, None


def table():
    states = json.load(open(os.path.join(RES, "stage9_states.json")))
    f8 = R9.fstar8()
    rows = []
    for t in R9.tests():
        x = t["test"]
        prop = bool(t["propagated"])
        fc1, fc2 = _mid(f8[x]["C1"]), _mid(f8[x]["C2"])
        f9, f9lo, f9hi, f9s = _f9(states, x, prop)
        peak, t_c, src = _no_delivery(x)
        rows.append({"test": x, "connection": t["connection"], "y": int(prop), "time_s": t["time_s"] if prop else None,
                     "E_b_J": float(t["E_b_J"]), "fC1": fc1[0], "fC1_lo": fc1[1], "fC1_hi": fc1[2], "fC2": fc2[0],
                     "fC2_lo": fc2[1], "fC2_hi": fc2[2], "f9": f9, "f9_lo": f9lo, "f9_hi": f9hi, "f9_status": f9s,
                     "f9_exploratory": x in IN.IN9.EXPLORATORY_FMAX, "peak_away_f0": peak, "peak_source": src,
                     "t_c1_f0": t_c})
    return rows


# ------------------------------------------------------------------------------------------------ C1
def firth(x, y, iters=200, tol=1e-13):
    """Firth's penalised maximum likelihood for p = 1 / (1 + exp(-(a + b x))), by Newton steps on the modified score
    X'(y - p + h (1/2 - p)), h the hat matrix's diagonal, with step halving on the penalised log-likelihood. The
    predictor is standardised for the iteration and the coefficients returned on its own scale. x None: the constant."""
    y = np.asarray(y, float)
    n = len(y)
    if x is None:
        p = (y.sum() + 0.5) / (n + 1.0)
        return {"a": math.log(p / (1.0 - p)), "b": 0.0, "p": p}
    x = np.asarray(x, float)
    mu, sd = x.mean(), x.std()
    if sd == 0.0:                                   # a predictor constant over the training half: the constant
        c = firth(None, y)
        return {"a": c["a"], "b": 0.0, "p": c["p"], "degenerate": True, "converged": True}
    z = (x - mu) / sd
    X = np.column_stack([np.ones(n), z])
    beta = np.zeros(2)

    def pll(b):
        eta = X @ b
        p = 1.0 / (1.0 + np.exp(-eta))
        W = p * (1 - p)
        info = X.T @ (W[:, None] * X)
        sign, logdet = np.linalg.slogdet(info)
        ll = np.sum(y * eta - np.logaddexp(0.0, eta))
        return ll + 0.5 * logdet, p, W, info

    cur, p, W, info = pll(beta)
    for _ in range(iters):
        inv = np.linalg.inv(info)
        Wh = np.sqrt(W)
        A = Wh[:, None] * X
        h = np.einsum("ij,jk,ik->i", A, inv, A)
        U = X.T @ (y - p + h * (0.5 - p))
        step = inv @ U
        lam = 1.0
        while True:
            nb = beta + lam * step
            new, p2, W2, info2 = pll(nb)
            if new >= cur - 1e-15 or lam < 1e-8:
                break
            lam *= 0.5
        beta, cur, p, W, info = nb, new, p2, W2, info2
        if np.max(np.abs(lam * step)) < tol:
            break
    b = beta[1] / sd
    a = beta[0] - b * mu
    return {"a": float(a), "b": float(b), "converged": bool(np.max(np.abs(lam * step)) < 1e-9)}


def prob(fit, x):
    if fit["b"] == 0.0 and "p" in fit:
        return np.full(len(x), fit["p"])
    return 1.0 / (1.0 + np.exp(-(fit["a"] + fit["b"] * np.asarray(x, float))))


def scores(p, y):
    p = np.clip(np.asarray(p, float), 1e-300, 1 - 1e-16)
    y = np.asarray(y, float)
    return {"log": float(np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))), "brier": float(np.mean((p - y) ** 2))}


def split_scores(x, y, train, test):
    c = firth(None, y[train])
    g = firth(x[train], y[train])
    sc, sg = scores(prob(c, x[test]), y[test]), scores(prob(g, x[test]), y[test])
    return {"constant": sc, "logistic": sg, "fit_constant": c, "fit_logistic": g,
            "d_log": sg["log"] - sc["log"], "d_brier": sg["brier"] - sc["brier"]}


def heldout(rows, n_perm=IN.N_PERM, seed=IN.SEED):
    y = np.array([r["y"] for r in rows])
    ser = np.array([r["connection"] == "series" for r in rows])
    dirs = {"series_to_parallel": (ser, ~ser), "parallel_to_series": (~ser, ser)}
    rng = np.random.default_rng(seed)
    perms = np.array([rng.permutation(y) for _ in range(n_perm)])
    out = {"n_perm": n_perm, "seed": seed, "n_series": int(ser.sum()), "n_parallel": int((~ser).sum()),
           "propagated_series": int(y[ser].sum()), "propagated_parallel": int(y[~ser].sum()), "predictors": {}}
    for name in PREDICTORS:
        x = np.array([r[name] for r in rows], float)
        pr = {}
        for d, (tr, te) in dirs.items():
            obs = split_scores(x, y, tr, te)
            dl, db = np.empty(n_perm), np.empty(n_perm)
            for k in range(n_perm):
                s = split_scores(x, perms[k], tr, te)
                dl[k], db[k] = s["d_log"], s["d_brier"]
            pr[d] = {"observed": obs,
                     "p_log": float((1 + np.sum(dl >= obs["d_log"] - 1e-12)) / (1 + n_perm)),
                     "p_brier": float((1 + np.sum(db <= obs["d_brier"] + 1e-12)) / (1 + n_perm)),
                     "band_log_2.5_97.5": [float(np.percentile(dl, 2.5)), float(np.percentile(dl, 97.5))],
                     "band_brier_2.5_97.5": [float(np.percentile(db, 2.5)), float(np.percentile(db, 97.5))],
                     "perm_d_log_mean": float(dl.mean())}
        out["predictors"][name] = pr
    return out


# ------------------------------------------------------------------------------------------------ C2
def ranks(v):
    """Average ranks, 1-based; None ranks above every number (a crossing that did not happen within 900 s)."""
    big = [math.inf if a is None else float(a) for a in v]
    order = sorted(range(len(big)), key=lambda i: big[i])
    r = [0.0] * len(big)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and big[order[j + 1]] == big[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = 0.5 * (i + j) + 1.0
        i = j + 1
    return np.array(r)


def spearman(a, b):
    ra, rb = ranks(a), ranks(b)
    ra, rb = ra - ra.mean(), rb - rb.mean()
    den = math.sqrt(float(np.sum(ra ** 2) * np.sum(rb ** 2)))
    return float(np.sum(ra * rb) / den) if den > 0 else 0.0


def perm_spearman(a, b, rng, n_perm):
    obs = spearman(a, b)
    b = list(b)
    cnt = 0
    for _ in range(n_perm):
        bb = [b[i] for i in rng.permutation(len(b))]
        if abs(spearman(a, bb)) >= abs(obs) - 1e-12:
            cnt += 1
    return obs, (1 + cnt) / (1 + n_perm)


def two_group(v, g, rng, n_perm):
    r = ranks(v)
    g = np.asarray(g, bool)
    obs = float(r[g].mean() - r[~g].mean())
    cnt = 0
    for _ in range(n_perm):
        gg = rng.permutation(g)
        if abs(r[gg].mean() - r[~gg].mean()) >= abs(obs) - 1e-12:
            cnt += 1
    return obs, (1 + cnt) / (1 + n_perm)


def rank(rows, n_perm=IN.N_PERM, seed=IN.SEED):
    rng = np.random.default_rng(seed + 1)
    prop = [r for r in rows if r["y"]]
    out = {"n_perm": n_perm, "seed": seed + 1, "quantities": {}}
    for q in QUANTITIES:
        v = [r[q] for r in rows]
        if any(x is None for x in v) and q != "t_c1_f0":
            out["quantities"][q] = {"missing": [r["test"] for r in rows if r[q] is None]}
            continue
        rho_y, p_y = perm_spearman(v, [r["y"] for r in rows], rng, n_perm)
        vp = [r[q] for r in prop]
        rho_t, p_t = perm_spearman(vp, [r["time_s"] for r in prop], rng, n_perm)
        rho_e, p_e = perm_spearman(v, [r["E_b_J"] for r in rows], rng, n_perm)
        dg, p_g = two_group(v, [r["connection"] == "series" for r in rows], rng, n_perm)
        out["quantities"][q] = {"outcome": {"rho": rho_y, "p": p_y}, "time": {"rho": rho_t, "p": p_t, "n": len(prop)},
                                "E_b": {"rho": rho_e, "p": p_e}, "connection": {"mean_rank_series_less_parallel": dg,
                                                                               "p": p_g}}
    return out


# ------------------------------------------------------------------------------------------------ C3
def spread(rows):
    """For each criterion and delivery: the fractions read from the tests (f_t for a propagated test where its search
    found one and it is not across a jump; f_max for a registered non-propagated test, zero included; the two
    exploratory f_max apart), and the thresholds f*."""
    states = json.load(open(os.path.join(RES, "stage9_states.json")))
    f8 = R9.fstar8()
    out = {}
    for crit in ("C1", "C2"):
        for d in DELIVERIES:
            vals, none, expl = {}, [], {}
            for r in rows:
                x = r["test"]
                if r["y"]:
                    s = states[f"A2_{crit}_{x}"] if d == "tri21" else states[f"B_ft_{crit}_{d}_{x}"]
                    if s["status"] in ("matched", "bracketed") and not s.get("across_jump"):
                        vals[x] = s["f_t"]
                    else:
                        none.append((x, s["status"]))
                else:
                    s = states[f"A3_{x}"] if d == "tri21" else states[f"B_fm_{d}_{x}"]
                    if x in IN.IN9.EXPLORATORY_FMAX:
                        expl[x] = s.get("f_max")
                    elif s["status"] in ("zero", "matched", "bracketed"):
                        vals[x] = s["f_max"]
                    else:
                        none.append((x, s["status"]))
            nz = [v for v in vals.values() if v > 0]
            fs = {}
            for r in rows:
                x = r["test"]
                s = f8[x][crit] if d == "tri21" else states[f"B_fs_{crit}_{d}_{x}"]
                fs[x] = 0.0 if s["status"] == "zero" else (0.5 * (s["lo"] + s["hi"]) if s["status"] == "bracket" else None)
            fnz = [v for v in fs.values() if v]
            out[f"{crit}_{d}"] = {
                "fractions": vals, "no_fraction": none, "exploratory": expl,
                "ratio_largest_to_smallest_nonzero": (max(nz) / min(nz)) if nz else None,
                "largest": max(nz) if nz else None, "smallest_nonzero": min(nz) if nz else None,
                "zero_share_of_16": sum(1 for v in vals.values() if v == 0.0) / 16.0, "n_with_fraction": len(vals),
                "fstar": fs, "fstar_ratio_largest_to_smallest_nonzero": (max(fnz) / min(fnz)) if fnz else None,
                "fstar_zero_share_of_16": sum(1 for v in fs.values() if v == 0.0) / 16.0}
    return out


def main():
    rows = table()
    missing = [r["test"] for r in rows if r["peak_away_f0"] is None]
    ho = heldout(rows)
    ho["table"] = rows
    json.dump(ho, open(os.path.join(RES, "stage10_heldout.json"), "w"), indent=1, default=float)
    rk = rank(rows)
    rk["spread"] = spread(rows)
    rk["missing_no_delivery_peak"] = missing
    json.dump(rk, open(os.path.join(RES, "stage10_rank.json"), "w"), indent=1, default=float)
    print("held out:", {k: {d: (round(v["observed"]["d_log"], 4), round(v["p_log"], 4)) for d, v in p.items()}
                        for k, p in ho["predictors"].items()})
    print("rank:", {q: ({k: (round(v["rho"], 3), round(v["p"], 4)) for k, v in d.items() if "rho" in v}
                        if "outcome" in d else d) for q, d in rk["quantities"].items()})


if __name__ == "__main__":
    main()
