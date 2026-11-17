"""Stage 15 (Brief 26): the inputs every Stage 15 module shares, all read from the archive (DECISIONS.md D170 onward).

Stage 15 asks what the resolved neighbour itself does after its hot spot crosses: whether the whole cell runs away.
Nothing here is new physics. The constants are the resolved and the lumped neighbour's own (`v12_model`, the two-cell
study's `lumped_two_cell`), the tests, their triggers and the ejected-energy ratio are Stage 8's, the measured times,
maxima and M50_PT_Exp4's history are those of Stages 7, 9 and 10, the kinetic draws Stage 11's and the aged SEI
Stage 7's.

Symbols used across Stage 15 (each also defined where it is used):
  T_L       the level, 255.68 C (528.83 K), the lower end of the two-cell study's onset band (D35)
  Tmean     the resolved neighbour's mean temperature: sum(C_i T_i) / sum(C_i) over its mesh nodes, C_i each node's
            heat capacity (the roll's volumetric heat capacity times the node's volume weight, plus its share of the
            can's heat capacity on the outer surface); the stored heat over the heat capacity, so the quantity the
            lumped neighbour's single temperature stands for (v12_model.Cell2Contact.C, run_resolved's Tmean)
  C8        the neighbour's own runaway: the first time within 900 s at which Tmean reaches T_L
  E*(C8)    the least delivered energy for which C8 happens, for a stated delivery
  C1, C2    the hot spot of the resolved neighbour, and the lumped neighbour, reaching T_L (the manuscript's two)
  far face  the resolved neighbour's surface node at mid-length opposite the line of contact (theta = 180 degrees,
            the Stage 9 thermocouple node, "away")
  E_b       a test's trigger energy (its fitted body energy, Stage 7); E_e = r E_b its ejected energy, r = 3.105
  f         a delivered fraction of E_e; E = f E_e the delivered energy in J
"""
import csv
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import v12_model as V                    # noqa: E402  (unchanged)
import stage8_inputs as IN8              # noqa: E402  (unchanged)
import stage9_run as R9                  # noqa: E402  (unchanged)
import stage10_inputs as IN10            # noqa: E402  (unchanged)
import stage11_inputs as IN11            # noqa: E402  (unchanged)
import stage13_inputs as IN13            # noqa: E402  (unchanged)

LP = V.LP
ROOT = os.path.abspath(os.path.join(HERE, ".."))
RES = os.path.join(ROOT, "results")
RUNS = os.path.join(RES, "stage15_runs")
SERIES = os.path.join(RES, "stage15_series")
K0 = 273.15

# ------------------------------------------------------------------------------------------------ the levels
T_AMB = LP.T_AMB                                   # 298.15 K
T_LEVEL = V.LEVEL_PROP                             # 528.83 K
T_LEVEL_C = T_LEVEL - K0                           # 255.68 C
T_END = 900.0                                      # C8 is read within 900 s
HALF_RXN_J = 11.3e3          # half of what the lumped neighbour releases when it runs away (22.5 to 22.8 kJ, reading 1)
TAU_TRIGGER = IN13.TAU_TRIGGER                     # 21.3865 s: the trigger's release and the archive's short pulse
TAUS_LONG = (120.0, 240.0, 360.0)                  # Stage 9's constant powers (D93)
R_CENTRAL = IN13.R_CENTRAL                         # 3.1053

# the far face's jump (A0.2, reading 5 of the brief): rates over centred 2 s differences on the 0.5 s grid of the
# measured record (the form that reproduces the brief's reading 5, D171)
DIFF_S = 2.0
GRID_S = 0.5
RISE_SLOW = 0.5                                    # K/s: the rise first slows below this
RISE_JUMP = 1.0                                    # K/s: the jump begins where the rise next passes this
BEFORE_S = 20.0                                    # where the rise never slows: the reading 20 s before C8

# the measured history of M50_PT_Exp4 (Stage 10, D102 (2)) and its scoring (D103 (2))
HIST_TEST = IN10.TEST_A                            # M50_PT_Exp4
T_PROP_FIG_S = IN10.T_PROP_S                       # 271.50 s, the figure's onset
JUMP_FROM_C = 197.3                                # the measured neighbour's reading at 271.50 s, before its jump
FAR_NODE = "away"

# ------------------------------------------------------------------------------------------------ the tests
TEST_ORDER = list(IN13.TEST_ORDER)


def tests():
    """The sixteen tests (Stage 8's file): connection, outcome, measured time, maxima and E_b."""
    return {t["test"]: t for t in IN8.tests()}


def propagated():
    return [t for t in TEST_ORDER if tests()[t]["propagated"]]


def e_e(test):
    return IN13.e_e(test)


def measured_history():
    """M50_PT_Exp4's neighbour record (t s, T C), the first reading, every 0.5 s (inputs/fransson2024)."""
    rows = list(csv.DictReader(open(IN10.HIST_A)))
    return [float(r["t_s"]) for r in rows], [float(r["T_neighbour_C"]) for r in rows]


# ------------------------------------------------------------------------------------------------ the kinetics
KIN_DRAWS = dict(IN11.KIN_DRAWS)                   # rank -> Stage 3's joint draw: 5: 188, 50: 83, 151: 40, 196: 184
SEI_AGED = 0.0                                     # the aged SEI: the SEI's initial amount 0 in every node (D66)
SHIFT_STEP_K = (5.0, 2.5)                          # B4's shift of the rate laws: steps of 5 K, then 2.5 K

# ------------------------------------------------------------------------------------------------ Part B (the list)
B1_TESTS = ("M50_PT_Exp4", "M50_PP_Exp2", "M50_SP_Exp3", "M50_ST_Exp3")
B1_FIRST = (-0.05, +0.05)                          # A2's E*(C8) less and plus 5 %
B1_STEP = 0.10                                     # then steps of 10 % on the side needed
B2_RUNS = ((240.0, 6209.0), (240.0, 5821.0))       # M50_PT_Exp4, constant power over 240 s, to 900 s
B3_PULSE_J = 5045.0                                # the delivery that follows the history best (Stage 10)
B3_STEP_W = 2.5                                    # the hold's power searched in steps of 2.5 W
B3_TOL_S = 10.0                                    # until C8 falls within 10 s of 271.5 s
B4_ENERGY_J = 5045.0


def key(x, nd=6):
    return round(float(x), nd)


def sha256_text(text):
    return hashlib.sha256(text.encode()).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()
