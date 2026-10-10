#!/usr/bin/env python3
"""Recompute the posterior-mean B-CRNN model from the supplementary CSV files and compare it with bcrnn_mean_model.json.

Usage: python3 extract_mean_model.py [--src supplementary]      (after fetch_supplementary.py)

Each CSV holds one parameter per row and one SVGD particle per column (CSV_model_key.docx). The mean model is the
arithmetic mean of every row over its particles (DECISIONS.md D3). The recorded values were computed from the same
files (same SHA-256) in a browser session, because the cloud machine of this study could not reach the publisher's
file server; this script is the reproducible route and must agree with them to 1e-12 of each value.
"""
import argparse, json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def row_means(path):
    M = np.loadtxt(path, delimiter=",", ndmin=2)
    return M.mean(axis=1), M.shape


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--src", default=os.path.join(HERE, "supplementary")); a = ap.parse_args()
    rec = json.load(open(os.path.join(HERE, "bcrnn_mean_model.json")))
    worst = 0.0
    for fname, key, shape in (("An_Ele.csv", "an_ele_rows_mean", (220, 100)), ("NCM811.csv", "ncm811_rows_mean", (17, 500)),
                              ("Separator.csv", "separator_rows_mean", (6, 100))):
        m, sh = row_means(os.path.join(a.src, fname))
        assert sh == shape, (fname, sh)
        r = np.array(rec[key])
        rel = np.abs(m - r) / np.maximum(np.abs(r), 1e-300)
        rel[(r == 0) & (m == 0)] = 0.0
        worst = max(worst, float(rel.max()))
        print(f"{fname}: shape {sh}, largest relative difference from the recorded means {rel.max():.2e}")
    print("PASS" if worst < 1e-12 else "FAIL", f"(worst {worst:.2e})")


if __name__ == "__main__":
    main()
