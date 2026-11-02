"""Stage 11 (DECISIONS.md D111 to D117): the constants of its rules and the inputs it takes from Part A0 (D111) and from
the earlier stages' records, each checked against the file it rests on when the module is loaded."""
import csv, json, math, os
import stage9_inputs as IN9                  # noqa: E402  (unchanged)
import stage10_inputs as IN10                # noqa: E402  (unchanged)

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")

# ------------------------------------------------------------------------------------------- A0.1, the kinetic draws
HEADLINE_CASE = "two_E33223_tau30_G0.5"     # 33.2 kJ over 30 s, 500 mW/K: Stage 3's registered case (D111 (1))
KIN_RANKS = (5, 50, 151, 196)               # the brief's ranks, earliest onset first
KIN_DRAWS = {5: 188, 50: 83, 151: 40, 196: 184}     # rank -> Stage 3's joint draw (D111 (1))
KIN_COLUMNS = {188: (71, 52, 3), 83: (6, 15, 254), 40: (37, 44, 366), 184: (20, 70, 145)}   # An_Ele, Separator, NCM811

# ------------------------------------------------------------------------------------------- A0.2, the thermal draws
THERMAL_DRAWS = {"kr_min": 2, "kr_max": 1, "c_min": 20, "c_max": 27}   # Stage 3's Latin hypercube draws (D111 (2))
M_ROLL_KG = 0.056
C_CAN_J_K = 4.5                              # the two-cell study's 9 g can at 500 J/(kg K), held fixed (D27)

# ------------------------------------------------------------------------------------------- A0.3, the tests
A_TESTS = ("M50_PT_Exp1", "M50_PP_Exp3", "M50_ST_Exp2", "M50_SP_Exp3")   # Parts A, B and E (D111 (3))
C_TESTS = IN9.REGISTERED_FMAX               # the five low-maximum tests (Part C)
FMAX_TEST = "M50_PT_Exp1"                    # C2
FMAX_CASES = (("kr_min", "central"), ("central", "low"))   # C2: the smallest radial conductivity; the low contact

# ------------------------------------------------------------------------------------------- the rules
WIDEN = 0.05                                 # A1: the step by which a threshold that leaves Stage 8's bracket is followed
WIDTH = 0.02                                 # Stage 8's interval (D78 (2))
F_END = 1.0
PEAK_TOL_K = IN9.PEAK_TOL_K                  # 5 K (Stage 9's f_max)
WIDTH_M = IN9.WIDTH_M                        # 0.005
T_END_S = 900.0
D_WITHIN_S = (10.0, 60.0)                    # D2
P1_FACTOR = 2.0
P1_ZERO_TOL = 0.025

# ------------------------------------------------------------------------------------------- Part D's inputs (D111 (5))
# the nine propagated tests: Stage 9's f_t(C2) with the 21.39 s delivery; for the three that ended at the threshold,
# the upper end of their bracket; for M50_SP_Exp3, the fraction of Stage 9's run at its interpolated f_t
D_FRACTIONS = {"M50_PT_Exp4": 0.040625, "M50_PP_Exp1": 0.01875, "M50_PP_Exp2": 0.046875, "M50_PP_Exp4": 0.0125,
               "M50_ST_Exp3": 0.234375, "M50_ST_Exp4": 0.009375, "M50_SP_Exp1": 0.01875, "M50_SP_Exp2": 0.025,
               "M50_SP_Exp3": 0.001575}
D_STATUS9 = {"M50_PT_Exp4": "threshold", "M50_ST_Exp3": "threshold", "M50_ST_Exp4": "threshold",
             "M50_SP_Exp3": "bracketed"}
FT_MIN = 0.0015754800756108784               # M50_SP_Exp3's interpolated f_t(C2), the smallest (Stage 9, E3)

# the probes: Stage 10's five (D102 (4))
NODES = IN10.NODES
EXTRA_PROBES = IN10.EXTRA_PROBES
PROBES = {k: d["node"] for k, d in list(NODES.items()) + list(EXTRA_PROBES.items())}


def thermal_draws():
    """{label: {"thermal_draw", "k_radial", "k_axial", "c_roll", "C_cell"}} from Stage 3's file."""
    rows = {int(r["thermal_draw"]): r for r in csv.DictReader(open(os.path.join(RES, "stage3_thermal_draws.csv")))}
    out = {}
    for lab, d in THERMAL_DRAWS.items():
        r = rows[d]
        c_roll = float(r["c_roll_J_per_kgK"])
        out[lab] = {"thermal_draw": d, "k_radial": float(r["k_radial_W_per_mK"]), "k_axial": float(r["k_axial_W_per_mK"]),
                    "c_roll": c_roll, "C_cell": C_CAN_J_K + M_ROLL_KG * c_roll}
        assert abs(out[lab]["C_cell"] - float(r["C_cell_J_per_K"])) < 1e-9, (lab, r)
    return out


def _check():
    # A0.1: the ranks, from Stage 3a's per-draw file
    per = list(csv.DictReader(open(os.path.join(RES, "stage3a_per_draw.csv"))))
    order = sorted(per, key=lambda r: (float(r["headline_hottest_onset_s"]), int(r["draw"])))
    for rank, d in KIN_DRAWS.items():
        assert int(order[rank - 1]["draw"]) == d, (rank, order[rank - 1]["draw"], d)
    idx = {int(r["draw"]): r for r in csv.DictReader(open(os.path.join(RES, "stage3_draw_indices.csv")))}
    for d, cols in KIN_COLUMNS.items():
        r = idx[d]
        assert (int(r["an_ele_column"]), int(r["separator_column"]), int(r["ncm811_column"])) == cols, (d, r)
    # A0.2: the smallest and largest conductivity across the layers and specific heat, no draw twice
    rows = list(csv.DictReader(open(os.path.join(RES, "stage3_thermal_draws.csv"))))
    by = lambda col: sorted(rows, key=lambda r: (float(r[col]), int(r["thermal_draw"])))
    kr, cr = by("k_radial_W_per_mK"), by("c_roll_J_per_kgK")
    assert [int(kr[0]["thermal_draw"]), int(kr[-1]["thermal_draw"]), int(cr[0]["thermal_draw"]),
            int(cr[-1]["thermal_draw"])] == [THERMAL_DRAWS[k] for k in ("kr_min", "kr_max", "c_min", "c_max")]
    assert len(set(THERMAL_DRAWS.values())) == 4
    thermal_draws()
    # Part D: the fractions against Stage 9's file
    fr = {r["test"]: r for r in csv.DictReader(open(os.path.join(RES, "stage9_fractions.csv")))}
    prop = [t for t, r in fr.items() if r["propagated"] in ("yes", "True", "1")]
    assert sorted(prop) == sorted(D_FRACTIONS), (prop, D_FRACTIONS)
    for t, f in D_FRACTIONS.items():
        r = fr[t]
        if r["ft_C2_status"] == "matched":
            assert abs(float(r["ft_C2"]) - f) < 1e-12, (t, r["ft_C2"], f)
        elif r["ft_C2_status"] == "threshold":
            assert abs(float(r["ft_C2_hi"]) - f) < 1e-12 and D_STATUS9[t] == "threshold", t
        else:
            assert r["ft_C2_status"] == "bracketed" and abs(round(float(r["ft_C2"]), 6) - f) < 1e-12, t
            assert abs(float(r["ft_C2"]) - FT_MIN) < 1e-15
    assert min(float(r["ft_C2"]) for r in fr.values() if r["ft_C2"] not in ("", "None")) == FT_MIN
    for t in A_TESTS + tuple(C_TESTS):
        assert t in fr, t


_check()
