"""Stage 10, D110 (2): the held-out fit's global maximum checked against a dense profile of the penalised likelihood.

For each predictor of Part C (f*(C1), f*(C2), Stage 9's fraction) and each training half (the eight series tests,
the eight parallel ones), and for every one of the 256 outcome patterns of the half, the 255 that the relabellings
can give and the one with no propagation: Firth's penalised log-likelihood on the standardised predictor is profiled
over the slope every 0.1 from -80 to 80, the intercept maximised at each slope, and the simplex is run from the
profile's best point; the fit of `stage10_partc.firth` is set against the larger of the two. The largest shortfall
of the fit below that maximum is reported, with the number of patterns in which the start at 0 alone finds a lower
maximum. Writes results/stage10_profile_check.json (about 20 minutes on one core)."""
import itertools, json, os, sys
import numpy as np
from scipy.optimize import minimize_scalar, minimize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage10_partc as PC               # noqa: E402

RES = os.path.join(HERE, "..", "results")


def main():
    rows = json.load(open(os.path.join(RES, "stage10_heldout.json")))["table"]
    ser = np.array([r["connection"] == "series" for r in rows])
    grid = np.arange(-80.0, 80.0 + 1e-9, 0.1)
    out = {"grid": [-80.0, 80.0, 0.1], "halves": {}}
    worst, n, lower = 0.0, 0, 0
    for name in ("fC1", "fC2", "f9"):
        xall = np.array([r[name] for r in rows], float)
        for d, tr in (("series", ser), ("parallel", ~ser)):
            x = xall[tr]
            mu, sd = x.mean(), x.std()
            z = (x - mu) / sd
            X = np.column_stack([np.ones(len(z)), z])
            h_worst, h_n, h_lower = 0.0, 0, 0
            for bits in itertools.product((0.0, 1.0), repeat=len(z)):
                y = np.array(bits)

                def pll(a, b):
                    eta = a + b * z
                    p = 1.0 / (1.0 + np.exp(-eta))
                    W = p * (1 - p)
                    return float(np.sum(y * eta - np.logaddexp(0.0, eta))
                                 + 0.5 * np.linalg.slogdet(X.T @ (W[:, None] * X))[1])
                prof = []
                for b in grid:
                    r = minimize_scalar(lambda a: -pll(a, b), bounds=(-60, 60), method="bounded",
                                        options={"xatol": 1e-8})
                    prof.append((-r.fun, r.x, b))
                v0, a0, b0 = max(prof)
                m = minimize(lambda q: -pll(q[0], q[1]), [a0, b0], method="Nelder-Mead",
                             options={"xatol": 1e-11, "fatol": 1e-14, "maxiter": 20000})
                vbest = max(v0, -m.fun)
                f = PC.firth(x, y)
                vf = pll(f["a"] + f["b"] * mu, f["b"] * sd)       # the fit on the standardised scale
                h_worst = max(h_worst, vbest - vf)
                h_n += 1
                h_lower += bool(f.get("lower_maximum_from_zero"))
            out["halves"][f"{name}/{d}"] = {"patterns": h_n, "largest_shortfall": h_worst,
                                            "with_lower_maximum_from_zero": h_lower}
            worst, n, lower = max(worst, h_worst), n + h_n, lower + h_lower
    out.update({"patterns": n, "largest_shortfall": worst, "with_lower_maximum_from_zero": lower})
    json.dump(out, open(os.path.join(RES, "stage10_profile_check.json"), "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("patterns", "largest_shortfall", "with_lower_maximum_from_zero")}))


if __name__ == "__main__":
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        main()
