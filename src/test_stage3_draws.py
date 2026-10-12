#!/usr/bin/env python3
"""Unit tests of the Stage 3 draw loader (run: python3 test_stage3_draws.py, or with pytest).

1. The means over all particles, recomputed through the loader, equal bcrnn_mean_model.json to 1e-12 (the same
   requirement as inputs/kinetics/extract_mean_model.py), and the model built from them equals the mean model.
2. A draw takes one column per file, by its own index: its rows are exactly those columns of the stored files, and its
   model is rows_to_model of those rows (no scaling, trimming or reweighting).
3. The indices are 1-based, inside each file's range, reproducible from the seed, and independent across files.
Needs the supplementary files in inputs/kinetics/supplementary (fetch_supplementary.py).
"""
import numpy as np
import bcrnn
import stage3_draws as S

P = S.load_particles()


def test_means_equal_recorded_mean_model():
    chk = S.check_means(P)
    assert chk["pass"], chk


def test_draw_is_one_column_per_file():
    draws, _ = S.all_draws(P)
    for d, ae, sep, cat in draws[:20]:
        ra, rc, rs = S.draw_rows(P, ae, sep, cat)
        assert np.array_equal(ra, P["An_Ele.csv"][:, ae - 1])
        assert np.array_equal(rc, P["NCM811.csv"][:, cat - 1])
        assert np.array_equal(rs, P["Separator.csv"][:, sep - 1])
        m = S.draw_model(P, ae, sep, cat)
        ref = bcrnn.rows_to_model(ra, rc, rs)
        for k in ("order", "stoich", "lnA", "Ea", "b", "dH"):
            assert np.array_equal(m[k], ref[k])
        # spot checks of the unit conversions against the raw rows
        assert m["Ea"][7] == rc[3] * 1e5 and m["lnA"][7] == rc[0]                 # cathode reaction 1
        assert m["dH"][10] == bcrnn.SEPARATOR_HEAT_SIGN * rs[5]                   # separator sign (D5)
        assert m["Ea"][4] == ra[190 + 4] * 1e5                                    # SEI decomposition, column 4


def test_indices_ranges_seed_and_independence():
    ae, sep, cat = S.draw_indices()
    assert ae.min() >= 1 and ae.max() <= 100 and sep.min() >= 1 and sep.max() <= 100 and cat.min() >= 1 and cat.max() <= 500
    ae2, sep2, cat2 = S.draw_indices()
    assert np.array_equal(ae, ae2) and np.array_equal(sep, sep2) and np.array_equal(cat, cat2)
    assert not np.array_equal(ae, sep)          # separate streams, not the same column reused across files
    assert len(ae) == S.N_DRAWS


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print("passed:", name)
