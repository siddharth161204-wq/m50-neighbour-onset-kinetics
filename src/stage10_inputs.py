"""Stage 10 (DECISIONS.md D102 to D107): the constants of its rules and the inputs it takes from Part A0 and from Stage 9's
records, each checked against the file it rests on when the module is loaded."""
import csv, json, math, os
import stage9_inputs as IN9                  # noqa: E402  (unchanged)

HERE = os.path.dirname(os.path.abspath(__file__))
INP = os.path.join(HERE, "..", "inputs", "fransson2024")
RES = os.path.join(HERE, "..", "results")

# ------------------------------------------------------------------------------------------- Part A0 (D102)
HIST_A = os.path.join(INP, "pt_exp4_history.csv")
HIST_B = os.path.join(INP, "pp_exp3_history.csv")
EXTRACTION = os.path.join(INP, "fig10_extraction.json")
TEST_A = "M50_PT_Exp4"
TEST_B = "M50_PP_Exp3"
T_PROP_S = 271.50                 # the figure's boundary between Sections II and III of M50_PT_Exp4 (D102 (2))
T_TABLE_S = 272.0                 # Table 3's time to propagation of M50_PT_Exp4
T_SECTION_I_END_S = 24.16         # the end of Section I of M50_PT_Exp4 (the trigger's maximum)
T_SECTION_II_END_B_S = 309.72     # the end of Section II of M50_PP_Exp3 (its neighbour's maximum)
UNC_K = 2.47                      # the recorded uncertainty of M50_PT_Exp4's record (D102 (2))
UNC_S = 0.45
RECORD_END_S = 500.0              # the figure's time axis

# the three thermocouple nodes at mid-length (A0.3, D102 (4)), and two more probes recorded beside them
NODES = {"away": {"node": 9953, "theta_deg": 180.0}, "side": {"node": 9938, "theta_deg": 88.277117},
         "facing": {"node": 9905, "theta_deg": 0.325853}}
EXTRA_PROBES = {"toward": {"node": 9904, "theta_deg": 0.0}, "side_out": {"node": 9939, "theta_deg": 94.391976}}
REGISTERED_NODE = "away"          # the Stage 9 node (D89 (6))

# ------------------------------------------------------------------------------------------- Part A (D103)
WINDOW = (0.0, T_PROP_S)          # from the start of the release (the paper's time zero, D34) to the onset
LAST_S = 60.0                     # the rise over the last 60 s before the onset
LEVELS_C = (100.0, 150.0)         # the times at which the histories first pass 100 and 150 C
T_END_A_S = T_TABLE_S + 60.0      # every Part A run goes to 332 s with the stop lifted
CONTACTS = ("low", "central", "high")
# the readings of M50_PT_Exp4 Stage 9 found (results/stage9_states.json), checked below
READINGS = {
    "none": {"cfg": "none", "f": 0.0, "registered": True},
    "tri21_C2_lo": {"cfg": "tri21", "f": 0.0375, "registered": True, "chain": "A2_C2_M50_PT_Exp4", "end": "lo"},
    "tri21_C2_hi": {"cfg": "tri21", "f": 0.040625, "registered": True, "chain": "A2_C2_M50_PT_Exp4", "end": "hi"},
    "con240_C2": {"cfg": "con240", "f": 0.028125, "registered": True, "chain": "B_ft_C2_240_M50_PT_Exp4", "end": "f_t"},
    "con360_C2": {"cfg": "con360", "f": 0.040625, "registered": True, "chain": "B_ft_C2_360_M50_PT_Exp4", "end": "f_t"},
    "con360_C1": {"cfg": "con360", "f": 0.071875, "registered": True, "chain": "B_ft_C1_360_M50_PT_Exp4", "end": "f_t"},
    "tri21_C1_lo": {"cfg": "tri21", "f": 0.009375, "registered": False, "chain": "A2_C1_M50_PT_Exp4", "end": "lo"},
    "tri21_C1_hi": {"cfg": "tri21", "f": 0.0125, "registered": False, "chain": "A2_C1_M50_PT_Exp4", "end": "hi"},
    "con120_C2_lo": {"cfg": "con120", "f": 0.028125, "registered": False, "chain": "B_ft_C2_120_M50_PT_Exp4", "end": "lo"},
    "con120_C2_hi": {"cfg": "con120", "f": 0.03125, "registered": False, "chain": "B_ft_C2_120_M50_PT_Exp4", "end": "hi"},
    "con240_C1_lo": {"cfg": "con240", "f": 0.05, "registered": False, "chain": "B_ft_C1_240_M50_PT_Exp4", "end": "lo"},
    "con240_C1_hi": {"cfg": "con240", "f": 0.053125, "registered": False, "chain": "B_ft_C1_240_M50_PT_Exp4", "end": "hi"},
}
SHORT = ("tri21_C2_lo", "tri21_C2_hi")
LONG = ("con240_C2", "con360_C2", "con360_C1")
CONTACT_BRACKET = SHORT                  # the low and high contacts are run for the short delivery's two ends only

# ------------------------------------------------------------------------------------------- Part B (D104)
PART_B_TESTS = IN9.REGISTERED_FMAX       # the five low-maximum tests
PART_B_NODES = ("side", "facing")         # the Stage 9 node's f_max is Stage 9's (A3)
PEAK_TOL_K = IN9.PEAK_TOL_K               # 5 K
WIDTH_M = IN9.WIDTH_M                     # 0.005
F_MAX = IN9.F_MAX                         # 1
SMALLEST_FT_C2 = ("M50_SP_Exp3", 0.00157548)  # Stage 9's smallest f_t(C2), checked below

# ------------------------------------------------------------------------------------------- Part C (D105)
# the six tests whose no-delivery run (Stage 7's) stopped at the hot spot's crossing and that have no Stage 9 run with
# the stop lifted: their thermocouple node's peak over 900 s with no delivery is run in Stage 10 (D104 (4))
PART_C_ZERO_TESTS = ("M50_PP_Exp1", "M50_PP_Exp4", "M50_ST_Exp4", "M50_SP_Exp1", "M50_SP_Exp2", "M50_SP_Exp3")
N_PERM = 10000
SEED = 20261030
P_LEVEL = 0.05
LOG_MARGIN = 0.1                          # P6: by more than 0.1 in the mean log score


def _check():
    ex = json.load(open(EXTRACTION))
    a = ex["panels"]["a"]
    assert a["test"] == TEST_A and abs(a["section_bounds_s"][1] - T_PROP_S) < 0.01, a["section_bounds_s"]
    assert abs(a["section_bounds_s"][0] - T_SECTION_I_END_S) < 0.01
    assert abs(ex["panels"]["b"]["section_bounds_s"][1] - T_SECTION_II_END_B_S) < 0.01
    assert abs(a["uncertainty_K"] - UNC_K) < 0.005 and abs(a["uncertainty_s"] - UNC_S) < 0.005
    st = json.load(open(os.path.join(RES, "stage9_states.json")))
    for name, r in READINGS.items():
        if "chain" not in r:
            continue
        s = st[r["chain"]]
        want = s["f_t"] if r["end"] == "f_t" else s[r["end"]]
        assert abs(want - r["f"]) < 1e-12, (name, want, r["f"])
    import glob
    for test in [r["test"] for r in csv.DictReader(open(os.path.join(INP, "m50_tests_stage7.csv")))]:
        p = [x for x in glob.glob(os.path.join(RES, "stage7_runs", f"pertest_{test}_*_hcentral_gcentral_tau21.39_*.json"))
             if "aged" not in x]
        full = json.load(open(p[0]))["resolved"]["t_end_s"] >= 900.0 - 1e-9
        ns = os.path.exists(os.path.join(RES, "stage9_runs", f"s9_none_fresh_both_ns_{test}_f0.000000000.json"))
        assert (test in PART_C_ZERO_TESTS) == (not full and not ns), test
    rows = list(csv.DictReader(open(os.path.join(RES, "stage9_fractions.csv"))))
    ft = {r["test"]: float(r["ft_C2"]) for r in rows if r["ft_C2"] not in ("", "None")}
    k = min(ft, key=ft.get)
    assert k == SMALLEST_FT_C2[0] and abs(ft[k] - SMALLEST_FT_C2[1]) < 5e-8, (k, ft[k])


_check()


def history(which="a"):
    """The measured record: t (s), the neighbour's and the trigger's temperatures (C), from the first reading."""
    rows = list(csv.DictReader(open(HIST_A if which == "a" else HIST_B)))
    t = [float(r["t_s"]) for r in rows]
    return t, [float(r["T_neighbour_C"]) for r in rows], [float(r["T_trigger_C"]) for r in rows]


def theta_ok(model):
    """The probes' nodes on the base mesh are those of D102 (4): the right angle, mid-length, on the can (V2)."""
    out = {}
    for name, d in list(NODES.items()) + list(EXTRA_PROBES.items()):
        i = d["node"]
        w = model.where(i)
        out[name] = w
        assert abs(w["r_mm"] - 1e3 * model_R(model)) < 1e-9 and abs(w["z_mm"] - 35.05) < 1e-9, (name, w)
        assert abs(w["theta_deg"] - d["theta_deg"]) < 1e-5, (name, w)
    return out


def model_R(model):
    import numpy as np
    return float(np.max(np.hypot(model.mesh.p[0], model.mesh.p[1])))


def arc_mm(theta_deg, R_mm=10.55):
    return R_mm * math.radians(theta_deg)
