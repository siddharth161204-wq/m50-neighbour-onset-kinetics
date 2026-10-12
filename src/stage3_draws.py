#!/usr/bin/env python3
"""Stage 3 kinetic draws (DECISIONS.md D22).

A draw is one particle (one column) taken from each of the three supplementary files of Koenig, Zhao and Deng
(2025): An_Ele.csv (220 rows x 100 particles), NCM811.csv (17 x 500) and Separator.csv (6 x 100). The three column
indices are sampled independently and uniformly, with replacement, because the three submodels were inferred from
separate DSC datasets and the paper samples "the randomly sampled uncertain effects of all kinetic models". Column j
of one file has nothing to do with column j of another.

Each draw's parameters are built by bcrnn.rows_to_model, the conversion the posterior-mean model goes through (ln A,
Ea times 1e5, b, dH, orders and stoichiometry from the same rows), with the same masses, initial amounts and
separator sign (D3, D4, D5). No particle is scaled, trimmed, reweighted or corrected.

Usage:
  python3 stage3_draws.py --out ../results          writes results/stage3_draw_indices.csv and the parameter vectors
  python3 stage3_draws.py --check                    the unit test: particle means equal bcrnn_mean_model.json

The parameter vectors (results/stage3_kinetic_draw_parameters.csv) reproduce the publisher's supplementary data, which
this repository does not redistribute, so that file is not committed; its SHA-256 is (results/stage3_draws.json), and
the indices with the publisher's files regenerate it exactly.
"""
import argparse, csv, hashlib, json, os
import numpy as np
import bcrnn

HERE = os.path.dirname(os.path.abspath(__file__))
SUPP = os.path.join(HERE, "..", "inputs", "kinetics", "supplementary")
N_DRAWS, SEED = 200, 20261012
SHAPES = {"An_Ele.csv": (220, 100), "NCM811.csv": (17, 500), "Separator.csv": (6, 100)}


def load_particles(src=SUPP):
    """The three particle matrices, rows = parameters, columns = SVGD particles, exactly as stored."""
    out = {}
    for f, shape in SHAPES.items():
        M = np.loadtxt(os.path.join(src, f), delimiter=",", ndmin=2)
        assert M.shape == shape, (f, M.shape)
        out[f] = M
    return out


def draw_indices(n=N_DRAWS, seed=SEED):
    """1-based column indices, drawn in this order from one generator: anode-electrolyte, separator, cathode."""
    rng = np.random.default_rng(seed)
    ae = rng.integers(1, 101, size=n)
    sep = rng.integers(1, 101, size=n)
    cat = rng.integers(1, 501, size=n)
    return ae, sep, cat


def draw_rows(P, ae, sep, cat):
    """The 220, 17 and 6 raw rows of one draw (1-based column indices)."""
    return P["An_Ele.csv"][:, ae - 1], P["NCM811.csv"][:, cat - 1], P["Separator.csv"][:, sep - 1]


def draw_model(P, ae, sep, cat):
    return bcrnn.rows_to_model(*draw_rows(P, ae, sep, cat))


def draw_kinetics(P, ae, sep, cat):
    return bcrnn.Kinetics(model=draw_model(P, ae, sep, cat))


def all_draws(P=None, n=N_DRAWS, seed=SEED):
    P = load_particles() if P is None else P
    ae, sep, cat = draw_indices(n, seed)
    return [(i + 1, int(ae[i]), int(sep[i]), int(cat[i])) for i in range(n)], P


def check_means(P=None, tol=1e-12):
    """Unit test (brief, Stage 3a step 1): the means over all particles, recomputed through this loader, equal the
    recorded posterior-mean rows to 1e-12 of each value, and the model built from them equals the mean model."""
    P = load_particles() if P is None else P
    rec = json.load(open(bcrnn.MODEL_JSON))
    worst = 0.0
    for f, key in (("An_Ele.csv", "an_ele_rows_mean"), ("NCM811.csv", "ncm811_rows_mean"), ("Separator.csv", "separator_rows_mean")):
        m, r = P[f].mean(axis=1), np.array(rec[key])
        rel = np.abs(m - r) / np.maximum(np.abs(r), 1e-300)
        rel[(r == 0) & (m == 0)] = 0.0
        worst = max(worst, float(rel.max()))
    mm = bcrnn.rows_to_model(P["An_Ele.csv"].mean(axis=1), P["NCM811.csv"].mean(axis=1), P["Separator.csv"].mean(axis=1))
    ref = bcrnn.load_mean_model()
    model_worst = 0.0
    for k in ("order", "stoich", "lnA", "Ea", "b", "dH"):
        a, b = np.asarray(mm[k]), np.asarray(ref[k])
        d = np.abs(a - b) / np.maximum(np.abs(b), 1e-300)
        d[(a == 0) & (b == 0)] = 0.0
        model_worst = max(model_worst, float(d.max()))
    ok = worst < tol and model_worst < tol
    return {"rows_max_relative_difference": worst, "model_max_relative_difference": model_worst, "tolerance": tol, "pass": ok}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "..", "results"))
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    P = load_particles()
    chk = check_means(P)
    print("unit test:", json.dumps(chk))
    if a.check:
        raise SystemExit(0 if chk["pass"] else 1)
    assert chk["pass"]
    draws, _ = all_draws(P)
    with open(os.path.join(a.out, "stage3_draw_indices.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["draw", "an_ele_column", "separator_column", "ncm811_column"])
        w.writerows(draws)
    par = os.path.join(a.out, "stage3_kinetic_draw_parameters.csv")
    with open(par, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["draw"] + [f"an_ele_row_{i + 1}" for i in range(220)] + [f"ncm811_row_{i + 1}" for i in range(17)]
                   + [f"separator_row_{i + 1}" for i in range(6)])
        for d, ae, sep, cat in draws:
            ra, rc, rs = draw_rows(P, ae, sep, cat)
            w.writerow([d] + [repr(float(x)) for x in np.concatenate([ra, rc, rs])])
    sha = hashlib.sha256(open(par, "rb").read()).hexdigest()
    ae, sep, cat = (np.array([x[k] for x in draws]) for k in (1, 2, 3))
    info = {"n_draws": len(draws), "seed": SEED, "generator": "numpy.random.default_rng(seed); integers for an_ele, then separator, then ncm811",
            "unique_columns": {"an_ele": int(np.unique(ae).size), "separator": int(np.unique(sep).size), "ncm811": int(np.unique(cat).size)},
            "parameter_vectors_file": "results/stage3_kinetic_draw_parameters.csv (not committed; regenerate with this script)",
            "parameter_vectors_sha256": sha, "unit_test": chk}
    json.dump(info, open(os.path.join(a.out, "stage3_draws.json"), "w"), indent=1)
    print(json.dumps(info, indent=1))
