#!/usr/bin/env python3
"""Stage 8, exploratory, written after Part A's results (the brief's pitfalls; DECISIONS.md D84, D87): the probability
that a test propagates, fitted from the sixteen outcomes and the f* values. Not a registered result.

Method. If each test delivered a fraction f of its ejected energy to the neighbour, drawn afresh for every test from
one distribution, and a test propagated when f reached that test's f*, then a test with threshold f* propagates with
probability P(f >= f*). With f log-normal (median m, spread s of ln f), P = 1 - Phi((ln f* - ln m) / s), and a test
with f* = 0 propagates for any f. (m, s) are fitted by maximum likelihood to the sixteen outcomes, each test's f* taken
at the middle of its bracket (and, to show the bracket's weight, at its lower and upper ends). The fit is compared with
the one-parameter model in which every test propagates with the same probability (9/16), by the likelihood ratio, and
with a logistic model in the trigger energy alone. C1 cannot be fitted this way: two tests whose hot spot reached
255.7 C with no delivery (f*(C1) = 0) did not propagate, which has probability 0 under the model.
Writes results/stage8_explore.json.
"""
import json, math, os, sys
import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RES = os.path.join(HERE, "..", "results")


def point(fs, where):
    if fs["status"] == "zero":
        return 0.0
    if fs["status"] == "above":
        return None
    lo, hi = fs["lo"], fs["hi"]
    return {"mid": 0.5 * (lo + hi), "lo": lo, "hi": hi}[where]


def fit_lognormal(f, y):
    f, y = np.asarray(f, float), np.asarray(y, bool)
    if np.any((f <= 0) & ~y):
        return None                                   # a test at f* = 0 that did not propagate: probability 0
    use = f > 0

    def nll(p):
        mu, ls = p
        s = math.exp(ls)
        z = (np.log(f[use]) - mu) / s
        pr = norm.sf(z)                               # P(f >= f*)
        pr = np.clip(pr, 1e-300, 1 - 1e-16)
        return -(np.sum(np.log(pr[y[use]])) + np.sum(np.log(1 - pr[~y[use]])))
    best = None
    for mu0 in np.log([0.005, 0.02, 0.05, 0.2]):
        for ls0 in (math.log(0.5), 0.0, math.log(2.0)):
            r = minimize(nll, [mu0, ls0], method="Nelder-Mead", options={"xatol": 1e-10, "fatol": 1e-12, "maxiter": 20000})
            if best is None or r.fun < best.fun:
                best = r
    mu, s = best.x[0], math.exp(best.x[1])
    probs = [1.0 if fi <= 0 else float(norm.sf((math.log(fi) - mu) / s)) for fi in f]
    return {"median_f": math.exp(mu), "s": s, "loglik": -best.fun, "p_by_test": probs}


def fit_logistic(e, y):
    e, y = np.asarray(e, float) / 1e3, np.asarray(y, float)

    def nll(p):
        a, b = p
        z = a + b * e
        return float(np.sum(np.logaddexp(0, z) - y * z))
    r = minimize(nll, [0.0, 0.0], method="Nelder-Mead", options={"xatol": 1e-10, "fatol": 1e-12, "maxiter": 20000})
    a, b = r.x
    return {"intercept": a, "slope_per_kJ": b, "E50_kJ": (-a / b) if b != 0 else None, "loglik": -r.fun}


def main():
    v = json.load(open(os.path.join(RES, "stage8_verdicts.json")))
    rows = v["thresholds"]
    y = [r["propagated"] for r in rows]
    n1 = sum(y)
    ll0 = n1 * math.log(n1 / len(y)) + (len(y) - n1) * math.log(1 - n1 / len(y))
    out = {"what": "exploratory, written after Part A's results; not registered (D87)",
           "n": len(y), "propagated": n1, "constant_model_loglik": ll0, "C2": {}, "C1": {}}
    for crit, key in (("C2", "fC2"), ("C1", "fC1")):
        for where in ("mid", "lo", "hi"):
            f = [point(r[key], where) for r in rows]
            if any(x is None for x in f):
                out[crit][where] = {"fitted": False, "why": "a test above 1"}
                continue
            res = fit_lognormal(f, y)
            if res is None:
                out[crit][where] = {"fitted": False,
                                    "why": "tests at f* = 0 that did not propagate: " +
                                           ", ".join(r["test"] for r, fi, yi in zip(rows, f, y) if fi <= 0 and not yi)}
                continue
            lr = 2 * (res["loglik"] - ll0)
            res.update({"fitted": True, "likelihood_ratio_vs_constant": lr,
                        "p_value_chi2_1": float(1 - __import__("scipy.stats", fromlist=["chi2"]).chi2.cdf(lr, 1)),
                        "p_by_test": dict(zip([r["test"] for r in rows], res["p_by_test"]))})
            out[crit][where] = res
    lg = fit_logistic([r["E_b_J"] for r in rows], y)
    lr = 2 * (lg["loglik"] - ll0)
    lg.update({"likelihood_ratio_vs_constant": lr,
               "p_value_chi2_1": float(1 - __import__("scipy.stats", fromlist=["chi2"]).chi2.cdf(lr, 1))})
    out["logistic_in_trigger_energy"] = lg
    json.dump(out, open(os.path.join(RES, "stage8_explore.json"), "w"), indent=1, default=float)
    return out


if __name__ == "__main__":
    o = main()
    c = o["C2"]["mid"]
    print(json.dumps({"C2_mid": {k: c[k] for k in ("median_f", "s", "loglik", "likelihood_ratio_vs_constant",
                                                   "p_value_chi2_1")} if c.get("fitted") else c,
                      "C1": o["C1"]["mid"], "logistic": o["logistic_in_trigger_energy"],
                      "constant_loglik": o["constant_model_loglik"]}, indent=1, default=float))
