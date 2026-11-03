#!/usr/bin/env python3
"""Tests of the Stage 12 code, run before the Stage 12 predictions (DECISIONS.md D123 (5)). No Stage 12 run is made:
the one run here repeats a Stage 8 record of the lumped neighbour (under a second), with Stage 12's specification.

Usage: python3 test_stage12.py
"""
import os as _os
for _k in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "NUMBA_NUM_THREADS"):
    _os.environ.setdefault(_k, "1")
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage9_run as R9                  # noqa: E402
import stage11_run as S11                # noqa: E402
import stage12_inputs as IN              # noqa: E402
import stage12_run as R12                # noqa: E402

RES = os.path.join(HERE, "..", "results")
N = {"pass": 0}


def ok(cond, what):
    assert cond, what
    N["pass"] += 1
    print("pass:", what)


def test_inputs():
    ok(IN.check(), "the cap (row 15, RUN195, 33,222.9 J) and the fixed ejected energy (median of rows 9 to 18) from the file")
    i, tid, cap = IN.cap_row()
    ok(abs(cap - 33222.9118228995) < 1e-9, "the cap's row value in full")
    med, e = IN.fixed_ejecta()
    ok(len(e) == 10 and abs(med - 0.5 * (e[4] + e[5])) < 1e-9 and abs(e[4] - 76251.25) < 1.0 and abs(e[5] - 77231.26) < 1.0,
       "the median is the mean of the fifth and sixth ejected energies (Run063's and Run067's)")
    pts = IN.a_points()
    ok(sorted(len(v) for v in pts.values()) == [2, 2, 6, 6], "the eight tests fall on two points per contact, 6 series and 2 parallel")
    bt = R9.by_test()
    ok(all(bt[t]["connection"] == c for (c, h), ts in pts.items() for t in ts), "every test on its connection's point")
    ok(min(bt[t]["E_b_J"] for t in IN.a_tests()) > max(bt[t]["E_b_J"] for t in bt if t not in IN.a_tests()),
       "the eight are the eight largest fitted triggers")


def test_spec_a():
    for (c, h) in IN.a_points():
        sp = R12.spec_a(c, h)
        ok(sp["E_body_J"] == IN.E_CAP_J and sp["E_delivered_J"] == 0.0 and sp["f"] == 0.0 and not sp["stop"]
           and sp["models"] == "both" and sp["h"] == h and sp["connection"] == c and sp["kin"] == "mean"
           and sp["thermal"] == "central" and sp["t_end_s"] == 900.0, f"Part A's specification {c} {h}")
    s6 = json.load(open(os.path.join(RES, "stage6_runs", IN.STAGE6_IDS["series"] + ".json")))
    sp = R12.spec_a("series", "central")
    same = all(sp[k] == s6[k] for k in ("connection", "h", "g", "tau", "E_body_J", "T_amb_K", "kin"))
    ok(same, "Part A's central series point has Stage 6's trigger inputs (connection, contact, tabs, release, energy, ambient)")


def test_spec_b():
    sp = R12.spec_b("B1", "M50_PP_Exp3", 0.00625, "both", True)
    ee = IN.e_e("M50_PP_Exp3")
    ok(abs(sp["E_delivered_J"] - 0.00625 * ee) < 1e-9 and abs(sp["f_fixed"] - 0.00625 * ee / IN.E_FIX_J) < 1e-15,
       "Part B's delivered energy and its fraction of the fixed energy")
    ok(sp["E_body_J"] == R9.by_test()["M50_PP_Exp3"]["E_b_J"], "Part B keeps the test's fitted trigger")
    ok(sp["id"] == "s12_B1_mean_central_hcentral_both_M50_PP_Exp3_f0.006250000", "Part B's id")


def test_states():
    pts = {}
    b = R12.b1_state("M50_PP_Exp3", "C1", pts)
    ok(b["status"] == "searching" and b["next"] == 0.00625, "B1 starts from Stage 8's bracket and halves it")
    pts[("M50_PP_Exp3", 0.00625)] = {"C1": 12.0}
    b = R12.b1_state("M50_PP_Exp3", "C1", pts)
    ok(b["status"] == "bracket" and (b["lo"], b["hi"]) == (0.0, 0.00625), "B1 stops at a fixed-energy width of at most 0.02")
    ok(R12.b1_state("M50_PT_Exp1", "C2", {})["status"] == "bracket", "B1: a Stage 8 bracket already narrow enough stands")
    ok(R12.b1_state("M50_SP_Exp3", "C2", {})["status"] == "zero", "B1: a zero stays zero")
    pts = {("M50_SP_Exp3", 0.0015625): {"C2": 209.5}}
    b = R12.b2_state("M50_SP_Exp3", pts)
    ok(b["status"] == "matched" and b["f_t"] == 0.0015625, "B2: a run within 10 s ends the search")
    pts = {("M50_PT_Exp4", 0.0390625): {"C2": 290.0}}
    b = R12.b2_state("M50_PT_Exp4", pts)
    ok(b["status"] == "bracketed" and b["lo"] == 0.0390625 and b["t_lo"] == 290.0 and b["lo"] < b["f_t"] < b["hi"],
       "B2: a late crossing at the midpoint turns a threshold into a bracket, interpolated")
    pts = {("M50_PT_Exp4", 0.0390625): {"C2": None}}
    ok(R12.b2_state("M50_PT_Exp4", pts)["status"] == "threshold", "B2: no crossing at the midpoint keeps the threshold")
    ok(R12.b2_state("M50_ST_Exp3", {})["status"] == "threshold", "B2: a Stage 9 bracket already narrow enough stands")
    ok(R12.b2_state("M50_PP_Exp1", {})["status"] == "matched", "B2: a matched search stays matched")


def test_repeat():
    """Stage 12's specification and Stage 11's run at a Stage 8 point of the lumped neighbour (M50_PT_Exp1 at 0.4625, C2's
    chain) repeat Stage 8's record."""
    sp = R12.spec_b("T", "M50_PT_Exp1", 0.4625, "lumped", True)
    rec, _ = S11.run_one(sp, S11.Context(), keep_series=False)
    s8 = json.load(open(os.path.join(RES, "stage8_runs", "c2_M50_PT_Exp1_f0.462500000.json")))
    a, b = rec["lumped"]["t_prop_s"], s8["lumped"]["t_prop_s"]
    ok(a is not None and b is not None and abs(a - b) <= 1e-9, f"a Stage 12 lumped run repeats Stage 8's crossing ({a} s, {b} s)")


if __name__ == "__main__":
    test_inputs()
    test_spec_a()
    test_spec_b()
    test_states()
    test_repeat()
    print(f"all {N['pass']} checks pass")
