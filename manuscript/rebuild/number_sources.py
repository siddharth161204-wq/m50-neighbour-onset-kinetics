"""Where each number of the rebuilt manuscript comes from (Brief 29, rule 4).

Each entry ties a number as written, in a context (a regular expression that must match the text around it, written
against the LaTeX source; the check normalises thin spaces, ties, degree and per-cent signs on both sides), to a value
read from a results, inputs or predictions file of the archive, or from the code for a setting of the model, by a named
selector. The numbers check (manuscript/numbers_check.py --rebuild) applies the entry's unit change to the value, and
the value, rounded to the number's written precision, must equal the number. A number of the manuscript's text, the
highlights, the cover letter, the enquiry or the graphical abstract with no entry is a failure.

Selectors read files only. `J` reads one value of a JSON file by its key path; `C` the values of a CSV column in the rows
that match filters; `MD` a number written in a text file (a results text file, a predictions file, the code) by a
regular expression; `F` any other reading, named in words (the smallest or largest of values a file holds, or a value
picked out by a condition on its row); `count` the rows of the registry with a verdict. None computes a new quantity:
the only operations are picking a value, its smallest or largest over named rows, and the unit changes J to kJ,
fraction to per cent, and the magnitude of a value whose sign the text states in words.
"""
import csv
import glob
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
RES = os.path.join(ROOT, "results")
_cache = {}


def _json(f):
    p = os.path.join(ROOT, f)
    if p not in _cache:
        _cache[p] = json.load(open(p))
    return _cache[p]


def _csv(f):
    p = os.path.join(ROOT, f)
    if p not in _cache:
        with open(p) as fh:
            _cache[p] = list(csv.DictReader(fh))
    return _cache[p]


def _get(o, path):
    parts = path if isinstance(path, (list, tuple)) else re.findall(r"[^.\[\]]+|\[\d+\]", path)
    for part in parts:
        if isinstance(part, int):
            o = o[part]
        elif isinstance(part, str) and part.startswith("[") and part.endswith("]"):
            o = o[int(part[1:-1])]
        else:
            o = o[part]
    return o


def J(f, path):
    """One value of a JSON file by its key path ('a.b[1].c', or a list of keys where a key holds a dot)."""
    def get():
        return [float(_get(_json(f), path))]
    get.where = f"{f}: {path if isinstance(path, str) else '/'.join(map(str, path))}"
    return get


def C(f, col, **filt):
    """The values of a CSV column in the rows whose columns equal the filters."""
    def get():
        rows = [r for r in _csv(f) if all(r.get(k) == v for k, v in filt.items())]
        return [float(r[col]) for r in rows if r.get(col) not in (None, "")]
    get.where = f"{f}: {col}" + (f" where {filt}" if filt else "")
    return get


def MD(f, rx):
    """A number written in a text file (a results text file, a predictions file, the code)."""
    def get():
        m = re.search(rx, open(os.path.join(ROOT, f)).read())
        return [float(m.group(1).replace(",", ""))]
    get.where = f"{f}: /{rx}/"
    return get


def F(where, fn):
    def get():
        return [float(x) for x in fn()]
    get.where = where
    return get


def lo_hi(where, gen):
    """The smallest and the largest of the values a reading gives (an entry matches either)."""
    def fn():
        v = [float(x) for x in gen() if x not in (None, "")]
        return [min(v), max(v)]
    return F("smallest and largest of " + where, fn)


def count(verdict=None):
    def get():
        rows = _csv("manuscript/rebuild/data/predictions_registry.csv")
        return [float(sum(1 for r in rows if verdict is None or r["verdict"] == verdict))]
    get.where = "manuscript/rebuild/data/predictions_registry.csv: rows" + (f" with verdict {verdict}" if verdict else "")
    return get


def LIT(key, quantity):
    """A value a cited source states, as recorded with its place in the source in manuscript/data/comparators.csv."""
    return C("manuscript/data/comparators.csv", "value", key=key, quantity=quantity)


S15 = "results/stage15_paper_numbers.json"
S13 = "results/stage13_paper_numbers.json"
S12 = "results/stage12_paper_numbers.json"
S10 = "results/stage10_paper_numbers.json"
S8 = "results/stage8_paper_numbers.json"
CONST = "results/manuscript_numbers.json"
NEEDS = "results/stage14_needs.csv"
BOUNDS = "results/stage14_bounds_corrected.csv"
INP14 = "results/stage14_inputs.csv"
READ = "results/stage15_readings.json"
XS = "results/stage15_cross_section.json"
SKIN = "results/stage13_skin.csv"
TIGN = "results/stage13_tign.csv"
TAB15 = "results/stage15_table.csv"
TESTS = "inputs/fransson2024/m50_tests.csv"
TRIG = "results/stage7_triggers.csv"
CAP = "results/stage12_capped.csv"
PARAMS = "manuscript/data/parameters.csv"   # the parameters table, each row with the line of code it is read from
B1 = "B1.M50_"
STRONG = ("PT_Exp4", "PP_Exp2", "SP_Exp3")


def b1_runs(tests=STRONG):
    for t in tests:
        for r in _json(S15)["B1"]["M50_" + t]["runs"]:
            yield r


def trig_E():
    return [r["E_J"] for r in _csv(TRIG) if r["kind"] == "test"]


def trig_by_test():
    return {r["test"]: float(r["E_J"]) for r in _csv(TRIG) if r["kind"] == "test"}


def xs_lo():
    return {r["test"]: r["lo_J"] for r in _json(XS)["A2"] if r["shape"] == "tri"}


def lumped_hi():
    import sys as _s
    _s.path.insert(0, os.path.join(ROOT, "src"))
    import rebuild_brackets as RBK
    return {r["test"]: RBK.brackets(r)[1][1] for r in _csv(NEEDS)}


def strong_rows():
    """Every case of the eight propagated tests other than ST_Exp3 (strong triggers), each shape: matched or within
    the search's resolution of the threshold."""
    return [r for r in _csv(TAB15) if r["test"] != "M50_ST_Exp3" and r["C8_xs_status"] in ("matched", "threshold")]


def st3_rows():
    return [r for r in _csv(TAB15) if r["test"] == "M50_ST_Exp3"]


def ratio_span(test):
    """The ratio of the three-dimensional resolved bracket to the lumped bracket, at its two extremes."""
    import sys as _s
    _s.path.insert(0, os.path.join(ROOT, "src"))
    import rebuild_brackets as RBK
    b = _json(S15)["B1"]["M50_" + test]["bracket"]
    nd = {r["test"]: r for r in _csv(NEEDS)}
    lo2, hi2 = RBK.brackets(nd["M50_" + test])[1]
    return [b["lo_J"] / hi2, b["hi_J"] / lo2]


def archived_6209():
    return [r for r in _json(XS)["A1_rows"] if r["id"] == "s10_con240_fresh_hcentral_M50_PT_Exp4_f0.050000000_t332"]


def exploratory_both():
    return [r for r in _json(XS)["A1_rows"] if r["test"] in ("M50_PT_Exp2", "M50_SP_Exp4") and r["C8_3d"] and r["C8_xs"]]


def cat1_dh():
    import sys as _s
    _s.path.insert(0, os.path.join(ROOT, "src"))
    import bcrnn
    k = bcrnn.Kinetics()
    return [float(k.dH[bcrnn.REACTIONS.index("cat1")])]


def section_cells():
    import sys as _s
    _s.path.insert(0, os.path.join(ROOT, "src"))
    import stage13_section as S
    sec = S.Section()
    return [float(sec.nr * sec.nt)]


def twobody_central():
    return [r for r in _csv("results/stage13_twobody.csv") if r["h"] == "central" and r["lum_source"] == "new search"
            and r["tau_d_s"][:3] in ("120", "360")]


def matched_rows():
    """The 21.4 s, 120 s, 240 s and 360 s cases outside ST_Exp3 in which the reactive cross-section's need is matched."""
    return [r for r in _csv(TAB15) if r["test"] != "M50_ST_Exp3" and r["C8_xs_status"] == "matched"]


def skin_short():
    """How far the hottest point without the reaction falls short, over the searches up to a Fourier number of 0.6."""
    return [abs(float(r["inert_peak_minus_level_K"])) for r in _csv(SKIN)
            if r["inert_peak_minus_level_K"] and float(r["fourier"]) < 0.61 and float(r["inert_peak_minus_level_K"]) < 0]


def wall_xs():
    return [json.load(open(f))["wall_s"] for f in glob.glob(os.path.join(RES, "stage15_xs", "*.json"))]


def held_out_p():
    ho = _json(S10)["part_c"]["held_out"]
    return [v["p_log"] for crit in ho.values() for v in crit.values() if isinstance(v, dict) and "p_log" in v]


def overshoot():
    return [v["overshoot_K"] for v in _json("results/stage9_paper_numbers.json")["part_a"]["A3"].values()
            if isinstance(v, dict) and v.get("overshoot_K") is not None]


def acc250():
    return [r["lumped_less_resolved"]["contact_and_wedge"] for v in _json("results/stage15_accounts.json")["accounts"].values()
            for r in v["rows"] if r["t_s"] == 250.0]


def shift_run(K, key):
    return F(f"{S15}: B4.shift_runs, the run shifted by {K} K: {key}",
             lambda: [r[key] for r in _json(S15)["B4"]["shift_runs"] if r["shift_K"] == K])


def b1_crossing(test, key):
    """The B1 run of a test at the upper end of its bracket (the least energy with the mean's runaway)."""
    def fn():
        b = _json(S15)["B1"]["M50_" + test]
        return [r[key] for r in b["runs"] if r["C8"] and abs(r["E_J"] - b["bracket"]["hi_J"]) < 1e-6]
    return F(f"{S15}: B1.M50_{test}, the run at the bracket's upper end: {key}", fn)


def b3b(P, key, sub=None):
    def fn():
        r = [x for x in _json(S15)["B3b"]["runs"] if x["id"] == f"s15_B3_PT_Exp4_hold{P}W"][0]
        return [r[key][sub] if sub else r[key]]
    return F(f"{S15}: B3b run s15_B3_PT_Exp4_hold{P}W: {key}{'.' + sub if sub else ''}", fn)


def sector_deg():
    m = re.search(r"SECTOR = math\.pi / (\d+)", open(os.path.join(ROOT, "src/v12_mesh.py")).read())
    return [180.0 / float(m.group(1))]


def side_probes():
    return [float(x) for x in re.findall(r"side(?:_out)? (\d{3}\.\d+) C", open(os.path.join(RES, "stage15_independent_read.md")).read())]


# (context regex, numbers as written, selector, unit change)
# unit change: None; "kJ" (J to kJ); "pct" (a fraction to per cent); "pctabs" (its magnitude); "abs" (the magnitude of a
# value whose sign the text gives in words, "earlier", "lower", "short", "below").
E = [
    # ---------------------------------------------------------------- the model's settings (read from the code)
    (r".", ["255.7"], J(CONST, "constants.level_propagation_C"), None),
    (r"900~s", ["900"], J(CONST, "constants.run_end_s"), None),
    (r"C=61\.75", ["61.75"], J(CONST, "constants.C_cell_J_K"), None),
    (r"0\.25~mm", ["0.25"], J(CONST, "constants.can_thickness_mm"), None),
    (r"1\.3~W", ["1.3"], J(CONST, "constants.k_radial_W_mK"), None),
    (r"and 25~W", ["25"], J(CONST, "constants.k_axial_W_mK"), None),
    (r"T_a=25|trigger at 25", ["25"], J(CONST, "constants.T_amb_C"), None),
    (r"200, 2,000,? or 3,700|200, 2,000, 3,700", ["200"], J(CONST, "constants.h_contact_W_m2K.low"), None),
    (r"200, 2,000,? or 3,700|200, 2,000, 3,700", ["2,000"], J(CONST, "constants.h_contact_W_m2K.central"), None),
    (r"200, 2,000,? or 3,700|200, 2,000, 3,700", ["3,700"], J(CONST, "constants.h_contact_W_m2K.high"), None),
    (r"a=10\.55", ["10.55"], J(CONST, "constants.cell_radius_mm"), None),
    (r"720~g", ["720"], J(CONST, "constants.M_ref_g"), None),
    (r"19,355 nodes", ["19,355"], J(S8, "v3.base.n_nodes"), None),
    (r"(within|Beyond|spans) 45", ["45"], F("src/v12_mesh.py: SECTOR = math.pi / 4, the wedge sector's half-angle, in degrees", sector_deg), None),
    (r"within 1~K a step", ["1"], MD("src/reactive.py", r"DT_TARGET = (1\.0)"), None),
    (r"21\.39~s", ["21.39"], C(SKIN, "tau_d_s", test="M50_PT_Exp1", region="half"), None),
    (r"21\.4~s|21\.4\\,s|21\.4 s", ["21.4"], C(SKIN, "tau_d_s", test="M50_PT_Exp1", region="half"), None),
    (r"120, 240 or 360", ["120", "240", "360"], C(TAB15, "tau_s", test="M50_PT_Exp4"), None),
    (r"deliveries of 5 to 120", ["5", "120"], C(SKIN, "tau_d_s", test="M50_PT_Exp1", region="half"), None),
    (r"at 10 and 60~s", ["10", "60"], C(SKIN, "tau_d_s", test="M50_ST_Exp3", region="half"), None),
    (r"Over 360~s", ["360"], C(SKIN, "tau_d_s", test="M50_PT_Exp1", region="half"), None),
    (r"\(within 10~s", ["10"], MD("predictions_stage9.md", r"crossing lies within (10) s of the measured time"), None),
    (r"\(within 5~K\)", ["5"], MD("predictions_stage9.md", r"within (5) K of it"), None),
    (r"200 (joint|kinetic) draws|the 200 kinetic|over the 200", ["200"], J(S13, "scorecard.P7.n_draws"), None),
    (r"larger of 10\\,\\% and 300~J", ["10"], MD("predictions_stage13.md", r"within the larger of (10) % and 300 J"), None),
    (r"larger of 10\\,\\% and 300~J", ["300"], MD("predictions_stage13.md", r"within the larger of 10 % and (300) J"), None),
    (r"margin of 0\.1", ["0.1"], MD("predictions_stage10.md", r"by more than (0\.1) in the mean log score"), None),
    (r"5\\,\\% either side", ["5"], MD("predictions_stage15.md", r"less (5) % and plus 5 %"), None),
    (r"central 95", ["95"], MD("predictions_stage13.md", r"the central (95) % of the 200 draws"), None),
    (r"shifted by 2~kJ", ["2"], MD("src/stage13_inputs.py", r"for d in \(-2000\.0, (2000\.0)\)"), "kJ"),
    (r"within 3\\,\\%", ["3"], MD("src/stage13_inputs.py", r"FIRST_STEP = (0\.03)"), "pct"),
    # ---------------------------------------------------------------- the tests and the trigger
    (r"147 to 342", ["147", "342"], lo_hi(f"{TESTS}: time_to_propagation_s", lambda: [r["time_to_propagation_s"] for r in _csv(TESTS)]), None),
    (r"71 to 133", ["71", "133"], lo_hi(f"{TESTS}: neighbour_max_C of the tests that did not propagate, without the two exploratory maxima",
                                        lambda: [r["neighbour_max_C"] for r in _csv(TESTS) if r["propagated"] == "No" and float(r["neighbour_max_C"]) < 600]), None),
    (r"626 and 808", ["626", "808"], C(TESTS, "neighbour_max_C", propagated="No"), None),
    (r"2\.47~K and 0\.45", ["2.47"], J(S10, "measured.uncertainty_K"), None),
    (r"2\.47~K and 0\.45", ["0.45"], J(S10, "measured.uncertainty_s"), None),
    (r"9\.0 to 54\.3|to 54\.3", ["9.0", "54.3"], lo_hi(f"{TRIG}: E_J of the sixteen tests", trig_E), "kJ"),
    (r"46\.5 to 54\.3", ["46.5", "54.3"], lo_hi(f"{CAP}: E_b_fitted_J", lambda: [r["E_b_fitted_J"] for r in _csv(CAP)]), "kJ"),
    (r"31\.6 to 54\.3", ["31.6"], F(f"{TRIG}: the smallest E_J of the tests whose body energy exceeds 30 kJ",
                                    lambda: [min(float(x) for x in trig_E() if float(x) > 30000)]), "kJ"),
    (r"weak trigger \(16\.6", ["16.6"], C(TRIG, "E_J", kind="test", test="M50_ST_Exp3"), "kJ"),
    (r"33\.2~kJ", ["33.2"], J(CONST, "constants.E_body_stage5_J"), "kJ"),
    (r"76\.74", ["76.74"], C(INP14, "value", key="db_Eej_median"), "kJ"),
    (r"89\.34", ["89.34"], C(INP14, "value", key="db_Eej_max"), "kJ"),
    # ---------------------------------------------------------------- conduction and radiation are not enough
    (r"5,248 runs", ["5,248"], J("results/v12_numbers.json", "runs.all"), None),
    (r"at most at 226\.7", ["226.7"], J("results/v12_numbers.json", "all_runs.res_peak_hottest_C.max"), None),
    (r"lumped neighbour at 180\.6", ["180.6"], J("results/v12_numbers.json", "all_runs.lum_peak_C.max"), None),
    (r"within 21\.7~s", ["21.7"], J(S12, "part_a.central.fitted_C1_at_f0_s[1]"), None),
    (r"191\.9 (to|and) 192\.2", ["191.9"], J(S12, "part_a.central.hot_spot_peak_C[0]"), None),
    (r"191\.9 (to|and) 192\.2", ["192.2"], J(S12, "part_a.central.hot_spot_peak_C[1]"), None),
    (r"226\.4 (to|and) 226\.7", ["226.4"], J(S12, "part_a.high.hot_spot_peak_C[0]"), None),
    (r"226\.4 (to|and) 226\.7", ["226.7"], J(S12, "part_a.high.hot_spot_peak_C[1]"), None),
    (r"63\.5 to 63\.8", ["63.5"], J(S12, "part_a.central.shortfall_hot_spot_K[0]"), None),
    (r"63\.5 to 63\.8", ["63.8"], J(S12, "part_a.central.shortfall_hot_spot_K[1]"), None),
    (r"29\.0 to 29\.3", ["29.0"], J(S12, "part_a.high.shortfall_hot_spot_K[0]"), None),
    (r"29\.0 to 29\.3", ["29.3"], J(S12, "part_a.high.shortfall_hot_spot_K[1]"), None),
    (r"at least 29~K|29~K short", ["29"], J(S12, "part_a.high.shortfall_hot_spot_K[0]"), None),
    (r"159\.8 (to|and) 161\.8", ["159.8"], J(S12, "part_a.central.lumped_peak_C[0]"), None),
    (r"159\.8 (to|and) 161\.8", ["161.8"], J(S12, "part_a.central.lumped_peak_C[1]"), None),
    (r"175\.9 (to|and) 177\.4", ["175.9"], J(S12, "part_a.high.lumped_peak_C[0]"), None),
    (r"175\.9 (to|and) 177\.4", ["177.4"], J(S12, "part_a.high.lumped_peak_C[1]"), None),
    # ---------------------------------------------------------------- what a neighbour needs
    (r"at most 4\.53~kJ", ["4.53"], C(NEEDS, "threshold_C1_hi_J", test="M50_PT_Exp1"), "kJ"),
    (r"at most 12\.89~kJ", ["12.89"], C(NEEDS, "threshold_C2_hi_J", test="M50_PT_Exp1"), "kJ"),
    (r"3\.5 to 10\.8", ["3.5", "10.8"], lo_hi(f"{XS}: A2, the 21.39 s pulse, E_star_J", lambda: [r["E_star_J"] for r in _json(XS)["A2"] if r["shape"] == "tri"]), "kJ"),
    (r"4\.5 and 3\.5", ["4.5", "3.5"], F(f"{XS}: A2, the 21.39 s pulse, E_star_J of the two tests whose lumped neighbour needs no delivery",
                                         lambda: [r["E_star_J"] for r in _json(XS)["A2"] if r["shape"] == "tri" and r["test"] in ("M50_PP_Exp1", "M50_SP_Exp3")]), "kJ"),
    (r"above 7\.06~kJ|midpoint 7\.06", ["7.06"], J(S15, B1 + "PT_Exp4.bracket.mid_J"), "kJ"),
    (r"6\.71 (to|and) 7\.42", ["6.71"], J(S15, B1 + "PT_Exp4.bracket.lo_J"), "kJ"),
    (r"6\.71 (to|and) 7\.42|At 7\.42~kJ|of the 7\.42~kJ run", ["7.42"], J(S15, B1 + "PT_Exp4.bracket.hi_J"), "kJ"),
    (r"6\.85~kJ in PP|PP-Exp2 \(6\.85~kJ\)", ["6.85"], J(S15, B1 + "PP_Exp2.bracket.mid_J"), "kJ"),
    (r"6\.51 (to|and) 7\.20", ["6.51"], J(S15, B1 + "PP_Exp2.bracket.lo_J"), "kJ"),
    (r"6\.51 (to|and) 7\.20", ["7.20"], J(S15, B1 + "PP_Exp2.bracket.hi_J"), "kJ"),
    (r"1\.49 and 1\.72|1\.49 to 1\.72", ["1.49"], J(S15, B1 + "PT_Exp4.ratio_to_C2"), None),
    (r"1\.49 and 1\.72|1\.49 to 1\.72", ["1.72"], J(S15, B1 + "PP_Exp2.ratio_to_C2"), None),
    (r"4\.75 and 3\.97", ["4.75"], J(S15, B1 + "PT_Exp4.E_C2_J"), "kJ"),
    (r"4\.75 and 3\.97", ["3.97"], J(S15, B1 + "PP_Exp2.E_C2_J"), "kJ"),
    (r"above 3\.88~kJ|4\.06~kJ \(3\.88~kJ\)", ["3.88"], J(S15, B1 + "SP_Exp3.bracket.mid_J"), "kJ"),
    (r"3\.70 (to|and) 4\.06", ["3.70"], J(S15, B1 + "SP_Exp3.bracket.lo_J"), "kJ"),
    (r"3\.70 (to|and) 4\.06", ["4.06"], J(S15, B1 + "SP_Exp3.bracket.hi_J"), "kJ"),
    (r"106 to 128", ["106", "128"], lo_hi(f"{S15}: B1 runs of PT_Exp4, PP_Exp2, SP_Exp3: lumped_C2_t_s", lambda: [r["lumped_C2_t_s"] for r in b1_runs()]), None),
    (r"22\.4 to 22\.6", ["22.4", "22.6"], lo_hi(f"{S15}: B1 runs of PT_Exp4, PP_Exp2, SP_Exp3: lumped_rxn_J", lambda: [r["lumped_rxn_J"] for r in b1_runs()]), "kJ"),
    (r"4\.1 to 4\.8~kJ", ["4.1", "4.8"], lo_hi(f"{S15}: B1 runs of PT_Exp4, PP_Exp2, SP_Exp3 with the mean's runaway: rxn_J", lambda: [r["rxn_J"] for r in b1_runs() if r["C8"]]), "kJ"),
    (r"needs 10\.28|10\.80~kJ \(10\.28~kJ\)", ["10.28"], J(S15, B1 + "ST_Exp3.bracket.mid_J"), "kJ"),
    (r"9\.77 (to|and) 10\.80", ["9.77"], J(S15, B1 + "ST_Exp3.bracket.lo_J"), "kJ"),
    (r"9\.77 (to|and) 10\.80|at 10\.80~kJ", ["10.80"], J(S15, B1 + "ST_Exp3.bracket.hi_J"), "kJ"),
    (r"0\.85 times", ["0.85"], J(S15, B1 + "ST_Exp3.ratio_to_C2"), None),
    (r"12\.03~kJ", ["12.03"], J(S15, B1 + "ST_Exp3.E_C2_J"), "kJ"),
    (r"runs away at 61\.5", ["61.5"], b1_crossing("ST_Exp3", "t_C8_s"), None),
    # ---------------------------------------------------------------- why
    (r"0\.025 to 0\.60", ["0.025"], C(SKIN, "fourier", test="M50_PT_Exp1", region="half", tau_d_s="5.0"), None),
    (r"0\.025 to 0\.60|at 0\.60", ["0.60"], C(SKIN, "fourier", test="M50_PT_Exp1", region="half", tau_d_s="120.0"), None),
    (r"alpha=5\.565", ["5.565\\times10^{-7}"], MD("results/stage13_sentences.md", r"\(([\d.]+e-7) m2/s\)"), None),
    (r"at most 1\.1~K", ["1.1"], F(f"{SKIN}: the largest shortfall of inert_peak_minus_level_K up to a Fourier number of 0.6", lambda: [max(skin_short())]), None),
    (r"Fourier number 1\.80|at 1\.80", ["1.80"], C(SKIN, "fourier", test="M50_PT_Exp1", region="half", tau_d_s="360.0"), None),
    (r"18\.9~K short", ["18.9"], C(SKIN, "inert_peak_minus_level_K", test="M50_PT_Exp1", region="half", tau_d_s="360.0"), "abs"),
    (r"316\.5~s", ["316.5"], C(SKIN, "res_t_cross_hi_s", test="M50_PT_Exp1", region="half", tau_d_s="360.0"), None),
    (r"mean at 240\.1", ["240.1"], C(SKIN, "res_mean_at_cross_hi_C", test="M50_PT_Exp1", region="half", tau_d_s="360.0"), None),
    (r"from 2\.90", ["2.90"], J(S13, ["scorecard", "P9", "ratio", "21.39"]), None),
    (r"Fourier number of 0\.11", ["0.11"], C(SKIN, "fourier", test="M50_PT_Exp1", region="half", tau_d_s="21.38651984299561"), None),
    (r"to 1\.16 at", ["1.16"], J(S13, ["scorecard", "P9", "ratio", "120"]), None),
    (r"0\.94 at 1\.80", ["0.94"], J(S13, ["scorecard", "P9", "ratio", "360"]), None),
    (r"218\.5", ["218.5"], J(S13, "scorecard.P7.mean_C"), None),
    (r"230\.4", ["230.4"], C(TIGN, "T_ign_C", kinetics="mean", connection="parallel", trigger="ambient"), None),
    (r"215\.3 to 221\.4", ["215.3"], J(S13, ["scorecard", "P7", "p2.5_C"]), None),
    (r"215\.3 to 221\.4", ["221.4"], J(S13, ["scorecard", "P7", "p97.5_C"]), None),
    (r"6\.1~K", ["6.1"], J(S13, "scorecard.P7.span_K"), None),
    (r"73\.3", ["73.3"], C(TIGN, "carrying_share", kinetics="mean", connection="parallel", trigger="own"), "pct"),
    (r"2,667~J", ["2,667"], C(TIGN, "cat1_heat_total_J", kinetics="mean", connection="parallel", trigger="own"), None),
    (r"all 32 searches", ["32"], J(S13, "scorecard.P8.n_within"), None),
    (r"393 to 456", ["393", "456"], lo_hi(f"{S13}: scorecard.P10.cases: slope_J_per_kJ", lambda: [c["slope_J_per_kJ"] for c in _json(S13)["scorecard"]["P10"]["cases"]]), None),
    (r"By 250~s", ["250"], F("results/stage15_accounts.json: accounts rows: t_s", lambda: [r["t_s"] for r in _json("results/stage15_accounts.json")["accounts"]["acc_PT_Exp4"]["rows"]]), None),
    (r"2\.1 to 2\.3", ["2.1", "2.3"], lo_hi("results/stage15_accounts.json: lumped_less_resolved.contact_and_wedge at 250 s", acc250), "kJ"),
    (r"5\.04~kJ|4\.66 and 5\.04|4\.66 to 5\.04", ["5.04"], J(S15, "B4.draws.5.E_J"), "kJ"),
    (r"runs away at 215\.6", ["215.6"], J(READ, "1.PT_Exp4.lumped_cross_s"), None),
    (r"191\.2 to 192\.4", ["191.2", "192.4"], lo_hi(f"{S15}: B4.draws: peak_mean_C", lambda: [v["peak_mean_C"] for v in _json(S15)["B4"]["draws"].values()]), None),
    (r"aged SEI \(188\.3", ["188.3"], J(S15, "B4.aged.peak_mean_C"), None),
    (r"17\.5~K", ["17.5"], F(f"{S15}: B4.shift_runs: the largest shift_K without the mean's runaway",
                             lambda: [max(r["shift_K"] for r in _json(S15)["B4"]["shift_runs"] if not r["C8"])]), None),
    (r"221\.1", ["221.1"], shift_run(17.5, "peak_mean_C"), None),
    (r"at 20~K|the first with one \(20~K\)", ["20"], J(S15, "B4.shift.least_shift_K"), None),
    (r"270\.3~s", ["270.3"], J(S15, "B4.shift.t_C8_s"), None),
    # ---------------------------------------------------------------- what the tests say
    (r"0\.26 to 5\.96", ["0.26", "5.96"], lo_hi(f"{NEEDS}: need_21s_lo_J of the propagated tests read at the measured time",
                                                 lambda: [r["need_21s_lo_J"] for r in _csv(NEEDS) if r["propagated"] == "yes" and "threshold" not in r["reading_21s"] and r["need_21s_lo_J"]]), "kJ"),
    (r"4\.66 to 4\.85|4\.66 and 5\.04|4\.66 to 5\.04|The 4\.66~kJ run", ["4.66"], C(NEEDS, "need_21s_lo_J", test="M50_PT_Exp4"), "kJ"),
    (r"4\.66 to 4\.85", ["4.85"], C(NEEDS, "need_21s_hi_J", test="M50_PT_Exp4"), "kJ"),
    (r"11\.95 to 12\.11", ["11.95"], C(NEEDS, "need_21s_lo_J", test="M50_ST_Exp3"), "kJ"),
    (r"11\.95 to 12\.11", ["12.11"], C(NEEDS, "need_21s_hi_J", test="M50_ST_Exp3"), "kJ"),
    (r"13\.8 to 56\.3", ["13.8", "56.3"], lo_hi("results/stage9_paper_numbers.json: part_a.A3: overshoot_K", overshoot), None),
    (r"needs 2\.09~kJ", ["2.09"], C(NEEDS, "need_21s_lo_J", test="M50_PT_Exp1"), "kJ"),
    (r"7\.9 times", ["7.9"], J(S12, "P4.ratio"), None),
    (r"22- to 64-fold", ["22"], J(S12, "part_c.stage10_energy_ratio_range[0]"), None),
    (r"22- to 64-fold", ["64"], J(S12, "part_c.stage10_energy_ratio_range[1]"), None),
    (r"gain is 0\.062", ["0.062"], J(S10, "part_c.largest_d_log"), None),
    (r"0\.23 to 0\.75", ["0.23", "0.75"], lo_hi(f"{S10}: part_c.held_out: p_log", held_out_p), None),
    (r"rho=-0\.92|-0\.92", ["-0.92"], J(S10, "part_c.rho_E_b.fC1"), None),
    (r"-0\.97", ["-0.97"], J(S10, "part_c.rho_E_b.fC2"), None),
    (r"4\.1 to 8\.1", ["4.1", "8.1"], lo_hi(f"{TAB15}: C8_xs_E_by_t_J, every case outside ST_Exp3 (matched, or within the search's resolution of the threshold)", lambda: [r["C8_xs_E_by_t_J"] for r in strong_rows()]), "kJ"),
    (r"0\.2 to 6\.0", ["0.2", "6.0"], lo_hi(f"{TAB15}: C2_E_by_t_J of the same thirty-two cases", lambda: [r["C2_E_by_t_J"] for r in strong_rows()]), "kJ"),
    (r"4\.58 against 0\.26", ["4.58"], C(TAB15, "C8_xs_E_by_t_J", test="M50_SP_Exp3", delivery="21.39 s pulse"), "kJ"),
    (r"4\.58 against 0\.26", ["0.26"], C(TAB15, "C2_E_by_t_J", test="M50_SP_Exp3", delivery="21.39 s pulse"), "kJ"),
    (r"114\.0~s", ["114.0"], C(TAB15, "C8_xs_t_at_E_star_hi_s", test="M50_ST_Exp3", delivery="21.39 s pulse"), None),
    (r"measured 177~s", ["177"], C(TAB15, "t_measured_s", test="M50_ST_Exp3", delivery="21.39 s pulse"), None),
    (r"141\.0", ["141.0"], J(S10, "measured.at_45_s_C"), None),
    (r"by 45~s", ["45"], MD(S10, r'"at_(45)_s_C"'), None),
    (r"197\.3", ["197.3"], J(S10, "measured.at_onset_C"), None),
    (r"271\.5", ["271.5"], J(S10, "measured.onset_figure_s"), None),
    (r"16\.3 and 16\.8|16\.3 to 16\.8", ["16.3"], J(S10, "part_a.tri21_C2_lo_hcentral.nodes.away.window.rms_K"), None),
    (r"16\.3 and 16\.8|16\.3 to 16\.8", ["16.8"], J(S10, "part_a.tri21_C2_hi_hcentral.nodes.away.window.rms_K"), None),
    (r"190\.6", ["190.6"], J(READ, "1.PT_Exp4.mean_peak_C"), None),
    (r"181\.9", ["181.9"], b1_crossing("PT_Exp4", "t_C8_s"), None),
    (r"234\.1", ["234.1"], J(S15, "B3a.run.far_jump.T_C"), None),
    (r"36\.8~K", ["36.8"], J("results/stage15_scorecard.json", ["scorecard", "predictions", "P5", "above_197.3_K"]), None),
    (r"51\.4~K", ["51.4"], J(S15, "B3a.history.rms_K"), None),
    (r"255\.9", ["255.9"], b3b("12.5", "t_C8_s"), None),
    (r"369\.3", ["369.3"], b3b("10.0", "t_C8_s"), None),
    (r"constant 12\.5~W|with 12\.5~W|followed by 12\.5~W", ["12.5"], J(S15, "B3b.result.P_hi_W"), None),
    (r"by 10~W", ["10"], J(S15, "B3b.result.P_lo_W"), None),
    (r"added 2\.9 and 3\.5", ["2.9"], b3b("12.5", "delivered_J", "delivery2"), "kJ"),
    (r"added 2\.9 and 3\.5", ["3.5"], b3b("10.0", "delivered_J", "delivery2"), "kJ"),
    (r"233\.6", ["233.6"], b3b("12.5", "far_jump", "T_C"), None),
    (r"33\.1~K", ["33.1"], J(S15, "B3b.history.rms_K"), None),
    (r"235\.5 and 235\.8", ["235.5", "235.8"], F("results/stage15_independent_read.md: the two side probes' readings at the far face's jump", side_probes), None),
    (r"37~K", ["37"], J("results/stage15_scorecard.json", ["scorecard", "predictions", "P5", "above_197.3_K"]), None),
    # ---------------------------------------------------------------- paths
    (r"225\.8", ["225.8"], J("results/stage14_corrections.json", "E_avail_J"), "kJ"),
    (r"27\.9~kJ|jet or flame & 27\.9", ["27.9"], C(BOUNDS, "upper_J", path="A1", window_s="21.39"), "kJ"),
    (r"1500", ["1500"], C(INP14, "value", key="T_flame_max"), None),
    (r"about 0\.38\\,\\%", ["0.38"], MD("results/stage14_independent_read.md", r"gives (0\.003759) \+- 0\.000022 at 0\.85 R"), "pct"),
    (r"0\.85~kJ", ["0.85"], MD("results/stage14_independent_read.md", r"at most about (\d+) J \(1\.11 %\)"), "kJ"),
    (r"195\.5", ["195.5"], C(BOUNDS, "upper_J", path="A2", window_s="21.39"), "kJ"),
    (r"65\.5~kJ|parallel tests\) & 65\.5 & 65\.5", ["65.5"], C(BOUNDS, "upper_J", path="A6", window_s="21.39"), "kJ"),
    (r"32\.7 and 75\.8", ["32.7"], C(NEEDS, "need_21s_lo_J", test="M50_SP_Exp4"), "kJ"),
    (r"32\.7 and 75\.8", ["75.8"], C(NEEDS, "need_21s_lo_J", test="M50_PT_Exp2"), "kJ"),
    (r"5\.3 to 25\.4", ["5.3", "25.4"], lo_hi(f"{TAB15}: C8_xs_share_of_76.74kJ", lambda: [r["C8_xs_share_of_76.74kJ"] for r in _csv(TAB15)]), "pct"),
    # ---------------------------------------------------------------- the reactive cross-section
    (r"(all|the|Against the) 151\b|151 (runs|three-dimensional|central)", ["151"], J(XS, "A1_summary.runs"), None),
    (r"In the 92 runs", ["92"], J(XS, "A1_summary.dt_C8_s.n"), None),
    (r"1\.0~s later", ["1.0"], J(XS, "A1_summary.dt_C8_s.mean"), None),
    (r"\(5\.5~s earlier", ["5.5"], J(XS, "A1_summary.dt_C8_s.min"), "abs"),
    (r"34\.5~s later", ["34.5"], J(XS, "A1_summary.dt_C8_s.max"), None),
    (r"in the 59 in which", ["59"], J(XS, "A1_summary.d_mean_peak_K.n"), None),
    (r"1\.9~K lower", ["1.9"], J(XS, "A1_summary.d_mean_peak_K.mean"), "abs"),
    (r"20\.7~K lower", ["20.7"], J(XS, "A1_summary.d_mean_peak_K.min"), "abs"),
    (r"9\.1\\,\\%", ["9.1"], J(S15, B1 + "SP_Exp3.rel_diff_xs"), "pctabs"),
    (r"17 to 71~s", ["17", "71"], lo_hi("results/stage15_xs/*.json: wall_s", wall_xs), None),
    (r"240 to 2,762", ["240", "2,762"], lo_hi(f"{S15}: runs.wall_s min and max", lambda: [_json(S15)["runs"]["wall_s"]["min"], _json(S15)["runs"]["wall_s"]["max"]]), None),
    # ---------------------------------------------------------------- pre-registration, checks, discussion, appendix
    (r"Of 98 predictions|42 of 98|98 predictions", ["98"], count(), None),
    (r"56 held", ["56"], count("held"), None),
    (r"42 failed|42 of 98", ["42"], count("failed"), None),
    (r"2\\times10\^\{-11\}", ["2\\times10^{-11}"], J(S8, "checks.V4.largest_relative.resolved"), None),
    (r"0\.52\\,\\%", ["0.52"], J(S8, "checks.V3.v3mesh.relative_change"), "pct"),
    (r"by 1\.5\\,\\%|by at most 1\.5\\,\\%", ["1.5"], J("results/stage15_checks.json", ["V4", "s15_B1_PT_Exp4_s+1_r1.5", "rel_change"]), "pct"),
    (r"opening 8\.5~s", ["8.5"], J(S10, "measured.dip_after_spike_t_s"), None),
    (r"spike to 102", ["102"], J(S10, "measured.spike_on_the_samples_C"), None),
    (r"2\.0~kJ on average", ["2.0"], LIT("torrescastro2020passive", "energy the next cell absorbs before it fails, mean"), None),
    (r"20 to 30", ["20"], LIT("walker2019decoupling", "share of the total energy released through the casing, low"), None),
    (r"20 to 30", ["30"], LIT("walker2019decoupling", "share of the total energy released through the casing, high"), None),
    (r"e=1,743", ["1,743"], J("results/stage13_readings.json", "reading_1.e_roll_as_resolved"), None),
    (r"1\.2284", ["1.2284"], J("results/stage13_checks.json", "V5.Phi00"), None),
    (r"841\.7", ["841.7"], J("results/stage13_readings.json", "reading_1.C_s_J_m2K"), None),
    # ---------------------------------------------------------------- figure captions
    (r"at 8~s", ["8"], b1_crossing("PT_Exp4", "C1_t_s"), None),
    (r"at 107~s", ["107"], b1_crossing("PT_Exp4", "lumped_C2_t_s"), None),
    (r"at 182~s", ["182"], b1_crossing("PT_Exp4", "t_C8_s"), None),
    (r"7\.4~kJ delivered", ["7.4"], b1_crossing("PT_Exp4", "E_J"), "kJ"),
    (r"5\.0~kJ over 21\.4~s", ["5.0"], J(READ, "1.PT_Exp4.E_J"), "kJ"),
    (r"carried to 332|held to 332", ["332"], J(READ, "1.PT_Exp4.t_end_s"), None),
    (r"[Aa]bout 7~kJ", ["7"], J(S15, B1 + "PT_Exp4.bracket.mid_J"), "kJ"),
    (r"1\.5 (and|to) 1\.7 times", ["1.5"], J(S15, B1 + "PT_Exp4.ratio_to_C2"), None),
    (r"1\.5 (and|to) 1\.7 times", ["1.7"], J(S15, B1 + "PP_Exp2.ratio_to_C2"), None),
    # ---------------------------------------------------------------- Table 2, the parameters (read from the code)
    (r"21\.1 and 70\.1", ["21.1"], J(CONST, "constants.cell_diameter_mm"), None),
    (r"21\.1 and 70\.1", ["70.1"], J(CONST, "constants.cell_length_mm"), None),
    (r"0\.25 mm, 15 W", ["15"], J(CONST, "constants.can_conductivity_W_mK"), None),
    (r"; 9 g, 500 J", ["9"], MD(PARAMS, r"m_can; c_can,(9); 500"), None),
    (r"9 g, 500 J", ["500"], MD(PARAMS, r"m_can; c_can,9; (500)"), None),
    (r"1\.3 and 25 W", ["1.3"], J(CONST, "constants.k_radial_W_mK"), None),
    (r"1\.3 and 25 W", ["25"], J(CONST, "constants.k_axial_W_mK"), None),
    (r"61\.75 J", ["61.75"], J(CONST, "constants.C_cell_J_K"), None),
    (r"\(65 g at 950", ["65"], J(CONST, "constants.m_cell_kg"), "g"),
    (r"65 g at 950", ["950"], J(CONST, "constants.cp_cell_J_kgK"), None),
    (r"half model, 19,355", ["19,355"], J(S8, "v3.base.n_nodes"), None),
    (r"wedge beside the contact & 0\.03", ["0.03"], J(CONST, "constants.k_air_W_mK"), None),
    (r"6\.8 mW", ["6.8"], J(CONST, "constants.g_tab_mW_K.central"), None),
    (r"\(5 and 10 as brackets", ["5"], J(CONST, "constants.g_tab_mW_K.low"), None),
    (r"5 and 10 as brackets", ["10"], J(CONST, "constants.g_tab_mW_K.high"), None),
    (r"0\.1817; 0\.8", ["0.1817"], J(CONST, "constants.view_factor_cans_in_contact"), None),
    (r"0\.1817; 0\.8", ["0.8"], J(CONST, "constants.emissivity"), None),
    (r"Room convection; ambient & 10", ["10"], J(CONST, "constants.h_conv_W_m2K"), None),
    (r"K\$\^\{-1\}\$; 25|; 25\\textdegree", ["25"], J(CONST, "constants.T_amb_C"), None),
    (r"triangular over 21\.39", ["21.39"], C(SKIN, "tau_d_s", test="M50_PT_Exp1", region="half"), None),
    (r"0\.15 \(fresh\)|0\.15 of the source's normalised amount", ["0.15"], J(CONST, "constants.sei_initial_amount"), None),
    (r"0 \(aged\)", ["0"], MD("src/stage15_inputs.py", r"SEI_AGED = (0\.0)"), None),
    (r"constant power over 120, 240 or 360", ["120", "240", "360"], C(TAB15, "tau_s", test="M50_PT_Exp4"), None),
    (r"failure category: 1, the trigger|; 2, failure in the propagating|; 4, sidewall rupture", ["1", "2", "4"],
     F(f"{TESTS}: the failure categories the tests report (Fransson et al.'s codes)",
       lambda: [float(r["failure_category"]) for r in _csv(TESTS) if r["failure_category"].isdigit()]), None),
    # ---------------------------------------------------------------- the graphical abstract (manuscript/rebuild/ga_text.txt)
    (r"PT-Exp4, the lumped neighbour's threshold", ["4.75"], J(S15, B1 + "PT_Exp4.E_C2_J"), "kJ"),
    (r"PP-Exp2, the lumped neighbour's threshold", ["3.97"], J(S15, B1 + "PP_Exp2.E_C2_J"), "kJ"),
    (r"PT-Exp4, the resolved neighbour's threshold", ["7.06"], J(S15, B1 + "PT_Exp4.bracket.mid_J"), "kJ"),
    (r"PP-Exp2, the resolved neighbour's threshold", ["6.85"], J(S15, B1 + "PP_Exp2.bracket.mid_J"), "kJ"),
    (r"1\.5 times \| PT-Exp4", ["1.5"], J(S15, B1 + "PT_Exp4.ratio_to_C2"), None),
    (r"1\.7 times \| PP-Exp2", ["1.7"], J(S15, B1 + "PP_Exp2.ratio_to_C2"), None),
    # ---------------------------------------------------------------- Table 3, the bounds
    (r"at most 136\.5", ["136.5"], C(INP14, "value", key="vendra_Qt_max"), "kJ"),
    (r"398\.5", ["398.5"], C(INP14, "value", key="u_vent_max"), None),
    (r"247\.3~kJ", ["247.3"], J("results/stage14_corrections.json", "E_global_J"), "kJ"),
    (r"15\.6~kJ within", ["15.6"], J("results/stage14_bounds.json", ["A6", "conditional_25C_J", "21.39"]), "kJ"),
    (r"at its 25\\textdegree C value|at its 25", ["25"], MD(INP14, r"0\.5 C for 30 s, (25) C"), None),
    # ---------------------------------------------------------------- added with the independent read's fixes (20 November)
    (r"\(17\.53 and 25\.24", ["17.53"], J("results/stage7_paper_numbers.json", "triggers.levels.tau_s[0]"), None),
    (r"\(17\.53 and 25\.24", ["25.24"], J("results/stage7_paper_numbers.json", "triggers.levels.tau_s[2]"), None),
    (r"rise from 25 ?°C, taken as its start", ["25"], MD(PARAMS, r"the (25) C start of Section I is this study's choice"), None),
    (r"9\.0 and 16\.6", ["16.6"], C(TRIG, "E_J", kind="test", test="M50_ST_Exp3"), "kJ"),
    (r"2,000 or 3,700", ["2,000"], J(CONST, "constants.h_contact_W_m2K.central"), None),
    (r"2,000 or 3,700", ["3,700"], J(CONST, "constants.h_contact_W_m2K.high"), None),
    (r"and 200 W m\^\{-2\} ?K\^\{-1\} for the low", ["200"], J(CONST, "constants.h_contact_W_m2K.low"), None),
    (r"(pulses of|triangular over) 5 to 360", ["5", "360"], C(SKIN, "tau_d_s", test="M50_PT_Exp1", region="half"), None),
    (r"PT-Exp1 at 5, 40 and 120", ["5", "40", "120"], C(SKIN, "tau_d_s", test="M50_PT_Exp1", region="half"), None),
    (r"(Up to|To|up to|pulses of|brackets up to) 120 ?s", ["120"], C(SKIN, "tau_d_s", test="M50_PT_Exp1", region="half"), None),
    (r"over a can at 25|the model's 25", ["25"], J(CONST, "constants.T_amb_C"), None),
    (r"hydrogen's (properties )?at 1000", ["1000"], MD(INP14, r"Table A\.6, 50 to (1000) K"), None),
    (r"within 30 ?°", ["30"], J("results/stage14_corrections.json", "A3.narrow_jet_strikes_for_phi_below_deg"), None),
    (r"10,000 permutations", ["10,000"], J("results/stage10_heldout.json", "n_perm"), None),
    (r"over 10 or 30 ?s", ["10"], MD(PARAMS, r'Release durations, Stage 5",tau,(10) and 30'), None),
    (r"over 10 or 30 ?s", ["30"], MD(PARAMS, r'Release durations, Stage 5",tau,10 and (30)'), None),
    (r"3\.18 to 4\.77", ["3.18"], C(NEEDS, "threshold_C2_lo_J", test="M50_PP_Exp2"), "kJ"),
    (r"3\.18 to 4\.77", ["4.77"], C(NEEDS, "threshold_C2_hi_J", test="M50_PP_Exp2"), "kJ"),
    (r"threshold is 10\.28", ["10.28"], J(S15, B1 + "ST_Exp3.bracket.mid_J"), "kJ"),
    (r"150 to 300 ?J per kJ", ["150"], MD("predictions_stage13.md", r"falls by (150) to 300 J per kJ"), None),
    (r"150 to 300 ?J per kJ", ["300"], MD("predictions_stage13.md", r"falls by 150 to (300) J per kJ"), None),
    (r"by 250 ?s the lumped", ["250"], F("results/stage15_accounts.json: the accounts' rows at t_s 250",
                                         lambda: sorted({r["t_s"] for v in _json("results/stage15_accounts.json")["accounts"].values()
                                                         for r in v["rows"] if r["t_s"] == 250.0})), None),
    (r"rank 5, 50, 151 and 196", ["5", "50", "151", "196"], F(f"{CONST}: constants.kin_ranks", lambda: _json(CONST)["constants"]["kin_ranks"]), None),
    (r"196 of 200", ["200"], J(S13, "scorecard.P7.n_draws"), None),
    (r"the 0\.26 ?kJ with which SP-Exp3", ["0.26"], C(TAB15, "C2_E_by_t_J", test="M50_SP_Exp3", delivery="21.39 s pulse"), "kJ"),
    (r"5\.96 ?kJ in PP-Exp2", ["5.96"], C(NEEDS, "need_21s_lo_J", test="M50_PP_Exp2"), "kJ"),
    (r"about 23( times|-fold)", ["23"], J(S12, "part_c.ratio"), None),
    (r"time within 10 ?s", ["10"], MD("predictions_stage9.md", r"crossing lies within (10) s of the measured time"), None),
    (r"starts at 32\.2", ["32.2"], C("inputs/fransson2024/pt_exp4_history.csv", "T_neighbour_C", t_s="0.0"), None),
    (r"begins at 173 ?s", ["173"], F(f"{S15}: B1.M50_PT_Exp4, the run at the bracket's upper end: far_jump.t_s",
                                     lambda: [r["far_jump"]["t_s"] for r in _json(S15)["B1"]["M50_PT_Exp4"]["runs"] if r["C8"]]), None),
    (r"6\.2 ?kJ (at constant power )?over 240|332~s, 6\.2~kJ, 5", ["6.2"], J(S15, ["B2", "0.05", "E_J"]), "kJ"),
    (r"6\.2 ?kJ (at constant power )?over 240|energy, at constant power over 240", ["240"], C(TAB15, "tau_s", test="M50_PT_Exp4"), None),
    (r"peaking at 241\.4", ["241.4"], J(S15, ["B2", "0.05", "peak_mean_C"]), None),
    (r"mean (peaking )?at 220\.5", ["220.5"], MD("predictions_stage15.md", r"6,209 J no C8 \(mean peak (220\.5) C\)"), None),
    (r"carries 4\.1 to 19\.5", ["4.1", "19.5"], lo_hi(f"{TAB15}: C8_xs_E_J, every delivery with which the cross-section runs away",
                                                      lambda: [r["C8_xs_E_J"] for r in _csv(TAB15)]), "kJ"),
    (r"in twelve, to 332", ["332"], F(f"{XS}: A1_rows, the earliest end of a run", lambda: [min(r["t_end_s"] for r in _json(XS)["A1_rows"])]), None),
    (r"shifted by 20 ?K bring", ["20"], J(S15, "B4.shift.least_shift_K"), None),
    (r"jump at 240\.4|jump beginning at 240\.4", ["240.4"], F(f"{S15}: B4.shift_runs, the run shifted by 20 K: far_jump.T_C",
                                     lambda: [r["far_jump"]["T_C"] for r in _json(S15)["B4"]["shift_runs"] if r["shift_K"] == 20.0]), None),
    (r"=1,743", ["1,743"], J("results/stage13_readings.json", "reading_1.e_roll_as_resolved"), None),
    (r"(can's|its) 4\.5 ?J", ["4.5"], MD(PARAMS, r"9; 500 \((4\.5) J/K\)"), None),
    (r"heat & 15 W", ["15"], J(CONST, "constants.can_conductivity_W_mK"), None),
    (r"ambient and start & 10 W", ["10"], J(CONST, "constants.h_conv_W_m2K"), None),
    (r"\(110\.8 ?kJ", ["110.8"], C(INP14, "value", key="db_Etotal_max"), "kJ"),
    (r"comparison\) & 65\.5 & 65\.5", ["65.5"], C(BOUNDS, "upper_J", path="A6", window_s="21.39"), "kJ"),
    (r"stored energy, 18\.2 ?Wh", ["18.2"], MD(INP14, r"Cell-Energy-Wh \((18\.2)\)"), None),
    (r"15\.6 ?kJ at 731|731 ?W or 15\.6|dissipate 15\.6", ["15.6"], J("results/stage14_bounds.json", ["A6", "conditional_25C_J", "21.39"]), "kJ"),
    (r"at 731 ?W|C, 731 ?W", ["731"], J("results/stage14_bounds.json", "A6.rate_25C_W"), None),
    (r"4\.189 ?V", ["4.189"], J("results/stage14_bounds.json", "inputs.V_oc_V"), None),
    (r"across 24 ?m", ["24"], J("results/stage14_bounds.json", "inputs.R_dc_min_ohm"), "milli"),
    (r"Omega\s+at 25", ["25"], MD(INP14, r"0\.5 C for 30 s, (25) C"), None),
]


# ---------------------------------------------------------------- counts written in words in the main text
def _n_tests(cond):
    return lambda: [float(sum(1 for r in _csv(TESTS) if cond(r)))]


def _n_needs(cond):
    return lambda: [float(sum(1 for r in _csv(NEEDS) if cond(r)))]


def _nz21(r):
    return bool(r["need_21s_lo_J"]) and float(r["need_21s_lo_J"]) > 0


def _need21(r):
    return float(r["need_21s_hi_J"] or r["need_21s_lo_J"])


def _bound(path):
    return [float(r["upper_J"]) for r in _csv(BOUNDS) if r["path"] == path and r["window_s"] == "21.39"][0]


# (phrase as written, the count it states, a selector giving that count from the files)
E += [
    (r"exotherm onset of 179\.3", ["179.3"], J("results/note_numbers.json", "V1.T_in_C"), None),
    (r"main cluster, 169\.0 to 198\.0|169\.0 to 198\.0", ["169.0"], MD("DECISIONS.md", r"main-cluster mean, (169\.0) to 198\.0"), None),
    (r"main cluster, 169\.0 to 198\.0|169\.0 to 198\.0", ["198.0"], MD("DECISIONS.md", r"main-cluster mean, 169\.0 to (198\.0)"), None),
    (r"next lower run, 0\.5\\,\\% of the test's ejected energy", ["0.5"], J(XS, "settings.width_ft"), "pct"),
    (r"least resistance at 25\\degC|4\.189~V and 25", ["25"], MD(INP14, r"0\.5 C for 30 s, (25) C"), None),
    (r"failed, 24 of the failures", ["24"], F("manuscript/rebuild/data/predictions_registry.csv: rows foreseen",
                                                lambda: [float(sum(1 for r in _csv("manuscript/rebuild/data/predictions_registry.csv") if r["foreseen"] == "yes"))]), None),
    (r"by a factor of 1\.5", ["1.5"], MD("predictions_stage15.md", r"the mesh refined by (1\.5)"), None),
    (r"at most at 199\.2", ["199.2"], lo_hi("results/stage15_nodelivery.csv: mean_peak_xs_C, high contact, outcome from the cross-section",
                                             lambda: [r["mean_peak_xs_C"] for r in _csv("results/stage15_nodelivery.csv") if r["h"] == "high" and r["C8_source"] == "cross-section"]), None),
    (r"1\.38 to 1\.59", ["1.38", "1.59"], F(f"{S15} B1 against the lumped bracket (rebuild_brackets): PT_Exp4", lambda: ratio_span("PT_Exp4")), None),
    (r"1\.37 to 2\.26|at least 1\.37 times", ["1.37", "2.26"], F(f"{S15} B1 against the lumped bracket (rebuild_brackets): PP_Exp2", lambda: ratio_span("PP_Exp2")), None),
    (r"0\.81 to 0\.90|at most 0\.90", ["0.81", "0.90"], F(f"{S15} B1 against the lumped bracket (rebuild_brackets): ST_Exp3", lambda: ratio_span("ST_Exp3")), None),
    (r"in 29 of the 32 searches over 120 and 360", ["29"], F("results/stage13_twobody.csv: central-contact searches over 120 and 360 s within the larger of 10 % and 300 J",
                                                           lambda: [float(sum(1 for r in twobody_central() if abs(float(r["B2_minus_mid_J"])) <= max(0.1 * float(r["lum_mid_J"]), 300.0)))]), None),
    (r"in 29 of the 32 searches over 120 and 360", ["32"], F("results/stage13_twobody.csv: central-contact searches over 120 and 360 s", lambda: [float(len(twobody_central()))]), None),
    (r"in 29 of the 32 searches over 120 and 360", ["120", "360"], F("results/stage13_twobody.csv: tau_d_s of those searches", lambda: [float(r["tau_d_s"]) for r in twobody_central()]), None),
    (r"\(3\.75 to 4\.06\\,\\%", ["3.75"], F("results/stage10_heldout.json: table, M50_PT_Exp4, f9_lo", lambda: [next(r["f9_lo"] for r in _json("results/stage10_heldout.json")["table"] if r["test"] == "M50_PT_Exp4")]), "pct"),
    (r"\(3\.75 to 4\.06\\,\\%", ["4.06"], F("results/stage10_heldout.json: table, M50_PT_Exp4, f9_hi", lambda: [next(r["f9_hi"] for r in _json("results/stage10_heldout.json")["table"] if r["test"] == "M50_PT_Exp4")]), "pct"),
    (r"by 1\.7 to 4\.3|within the 1\.7 to 4\.3", ["1.7", "4.3"], lo_hi(f"{TAB15}: the pulse, C8_xs_E_by_t_J less C2_E_by_t_J outside ST_Exp3",
                                                                       lambda: [float(r["C8_xs_E_by_t_J"]) - float(r["C2_E_by_t_J"]) for r in strong_rows() if r["delivery"].startswith("21.39")]), "kJ"),
    (r"needs 10\.3 to 13\.8|at 10\.3 to 13\.8|and 10\.3 to 13\.8", ["10.3", "13.8"], lo_hi(f"{TAB15}: ST_Exp3, C8_xs_E_by_t_J", lambda: [r["C8_xs_E_by_t_J"] for r in st3_rows()]), "kJ"),
    (r"11\.5 to 12\.3", ["11.5", "12.3"], lo_hi(f"{TAB15}: ST_Exp3, C2_E_by_t_J", lambda: [r["C2_E_by_t_J"] for r in st3_rows()]), "kJ"),
    (r"they are 12\.1 and", ["12.1"], C(TAB15, "C2_E_by_t_J", test="M50_ST_Exp3", delivery="21.39 s pulse"), "kJ"),
    (r"only with the 240~s delivery|with the 360~s delivery", ["240", "360"], C(TAB15, "tau_s", test="M50_ST_Exp3"), None),
    (r"6\.2~kJ, 5\\,\\% of the test's ejected energy", ["5"], MD("predictions_stage15.md", r"at f = (0\.05) \(6,209 J"), "pct"),
    (r"archive's 241\.2", ["241.2"], F(f"{XS}: A1_rows, the archived 6,209 J run over 240 s: mean_peak_3d_C", lambda: [r["mean_peak_3d_C"] for r in archived_6209()]), None),
    (r"archive's 241\.2.{0,12}at 332", ["332"], F(f"{XS}: A1_rows, the archived 6,209 J run: t_end_s", lambda: [r["t_end_s"] for r in archived_6209()]), None),
    (r"Table~S2, step~15, P8", ["15"], C("manuscript/rebuild/data/predictions_registry.csv", "stage", prediction="P8"), None),
    (r"under five deliveries|; 6\.7 and 7\.4~kJ", ["6.7"], J(S15, B1 + "PT_Exp4.bracket.lo_J"), "kJ"),
    (r"6\.7 and 7\.4~kJ", ["7.4"], J(S15, B1 + "PT_Exp4.bracket.hi_J"), "kJ"),
    (r"deliveries: 5\.0~kJ|the 5\.0~kJ pulse|of 5\.0~kJ over", ["5.0"], J(S15, "B4.draws.5.E_J"), "kJ"),
    (r"82 of them in the two exploratory tests", ["82"], F(f"{XS}: A1_rows of PT_Exp2 and SP_Exp4 in which both run away", lambda: [float(len(exploratory_both()))]), None),
    (r"deliveries of 15 to 135", ["15", "135"], lo_hi(f"{XS}: A1_rows of PT_Exp2 and SP_Exp4 in which both run away, E_J", lambda: [r["E_J"] for r in exploratory_both()]), "kJ"),
    (r"164\.9~J per gram", ["164.9"], F("inputs: the posterior-mean kinetics (src/bcrnn.py): dH of cat1, J/g", cat1_dh), None),
    (r"the cathode's 179\.12", ["179.12"], MD("src/bcrnn.py", r"M_IVV = (179\.12)"), None),
    (r"this cell's 65~g", ["65"], MD("src/stage13_tign.py", r"the reaction heat of the (65) g cell"), None),
    (r"solved on 3,034 cells", ["3,034"], F("src/stage13_section.py: Section(): nr x nt", section_cells), None),
]

V12 = "results/v12_numbers.json"
E += [
    (r"central case, the central contact and tab with the posterior-mean kinetics, the hottest point peaked at 191\.5 to 192\.3", ["191.5"], J(V12, "central_case.span.res_peak_hottest_C.min"), None),
    (r"hottest point peaked at 191\.5 to 192\.3", ["192.3"], J(V12, "central_case.span.res_peak_hottest_C.max"), None),
    (r"lumped neighbour at 159\.4 to 162\.1", ["159.4"], J(V12, "central_case.span.lum_peak_C.min"), None),
    (r"lumped neighbour at 159\.4 to 162\.1", ["162.1"], J(V12, "central_case.span.lum_peak_C.max"), None),
    (r"they are 8\.7~s apart", ["8.7"], F(f"{TESTS}: mean time_to_propagation_s in series less in parallel",
                                          lambda: [(lambda rr: sum(float(r["time_to_propagation_s"]) for r in rr if r["connection"] == "series") / sum(1 for r in rr if r["connection"] == "series")
                                                   - sum(float(r["time_to_propagation_s"]) for r in rr if r["connection"] == "parallel") / sum(1 for r in rr if r["connection"] == "parallel"))(
                                                   [r for r in _csv(TESTS) if r["propagated"] == "Yes"])]), None),
    (r"as 8~s apart", ["8"], MD("predictions_v12.md", r"the measured means differ by (8) s"), None),
    (r"about 0\.4~K", ["0.4"], MD("predictions_v12.md", r"average heat rate for propagation to occur was (0\.4)"), None),
    (r"it lies within the same tolerance in 29", ["29"], F("results/stage13_twobody.csv: central searches over 120 and 360 s within the tolerance",
                                                         lambda: [float(sum(1 for r in twobody_central() if abs(float(r["B2_minus_mid_J"])) <= max(0.1 * float(r["lum_mid_J"]), 300.0)))]), None),
    (r"with the 32 searches made there over 120 and 360", ["32"], F("results/stage13_twobody.csv: central searches over 120 and 360 s", lambda: [float(len(twobody_central()))]), None),
    (r"with the 32 searches made there over 120 and 360|SP-Exp2 over 120", ["120", "360"], F("results/stage13_twobody.csv: tau_d_s of those searches", lambda: [float(r["tau_d_s"]) for r in twobody_central()]), None),
    (r"7 to 46~J beyond it", ["7", "46"], lo_hi("results/stage13_twobody.csv: central searches outside the tolerance, by how much",
                                               lambda: [abs(float(r["B2_minus_mid_J"])) - max(0.1 * float(r["lum_mid_J"]), 300.0) for r in twobody_central()
                                                        if abs(float(r["B2_minus_mid_J"])) > max(0.1 * float(r["lum_mid_J"]), 300.0)]), None),
    (r"Of the 92 in which both models run away, 82", ["92"], F(f"{XS}: A1_rows in which both run away", lambda: [float(sum(1 for r in _json(XS)["A1_rows"] if r["C8_3d"] and r["C8_xs"]))]), None),
    (r"Of the 92 in which both models run away, 82", ["82"], F(f"{XS}: A1_rows of PT_Exp2 and SP_Exp4 in which both run away", lambda: [float(len(exploratory_both()))]), None),
    (r"lists, by test and delivery, the 151", ["151"], J(XS, "A1_summary.runs"), None),
    (r"Nine of the 32 are zero in both", ["32"], F("results/stage13_twobody.csv: low and high searches", lambda: [float(sum(1 for r in _csv("results/stage13_twobody.csv") if r["h"] in ("low", "high")))]), None),
]

E += [
    (r"against 139\\degC\{\} in the kinetic source|against 139", ["139"], MD("DECISIONS.md", r"(139) C in the source paper's Fig\. 3\(e\)"), None),
]

E += [
    (r"internal-short rate, 1~K\\,min\$\^\{-1\}\$ of self-heating, at 199\.8|at 199\.8", ["199.8"], J("results/note_numbers.json", "V1.T_on_1_C_per_min_C"), None),
    (r"internal-short rate|self-heating, at 199", ["1"], MD("DECISIONS.md", r"T_on at the paper's stated trigger \((1) C/min\)"), None),
    (r"band of 255\.7 to 302\.1", ["255.7"], MD("DECISIONS.md", r"below the paper's band of (255\.7) to 302\.1"), None),
    (r"band of 255\.7 to 302\.1", ["302.1"], MD("DECISIONS.md", r"below the paper's band of 255\.7 to (302\.1)"), None),
    (r"runs from 146\.3 to 191\.4", ["146.3"], J("results/stage3_numbers.json", ["V4_registered", "T_in_p2.5_C"]), None),
    (r"runs from 146\.3 to 191\.4", ["191.4"], J("results/stage3_numbers.json", ["V4_registered", "T_in_p97.5_C"]), None),
    (r"191\.4\\degC\{\} \(central 95|\(central 95\\,\\%\)", ["95"], MD("DECISIONS.md", r"(95) %"), None),
    (r"Over the 200 draws below|the 200 draws below", ["200"], J(S13, "scorecard.P7.n_draws"), None),
]

def twobody_low(strong):
    trig = trig_by_test()
    return [float(r["B2_minus_mid_J"]) for r in _csv("results/stage13_twobody.csv") if r["h"] == "low" and ((trig[r["test"]] > 30000) == strong)]


E += [
    (r"after every strong trigger, by 0\.25 to 0\.48", ["0.25", "0.48"], lo_hi("results/stage13_twobody.csv: low contact, strong triggers, B2 less the midpoint", lambda: twobody_low(True)), "kJ"),
    (r"after the two weak ones, by 0\.28 and 0\.44", ["0.28", "0.44"], F("results/stage13_twobody.csv: low contact, weak triggers, the midpoint less B2", lambda: [-x for x in twobody_low(False)]), "kJ"),
    (r"differences run from -0\.43 to 0\.19", ["-0.43", "0.19"], lo_hi("results/stage13_twobody.csv: high contact, B2 less the midpoint", lambda: [r["B2_minus_mid_J"] for r in _csv("results/stage13_twobody.csv") if r["h"] == "high"]), "kJ"),
]

WORDS = [
    (r"thirteen of the fourteen with strong triggers", 13, F("stage15_cross_section.json A2 against rebuild_brackets: strong-trigger tests whose cross-section bracket lies above the lumped bracket",
                                                       lambda: [float(sum(1 for t, lo in xs_lo().items() if trig_by_test()[t] > 30000 and lo > lumped_hi()[t]))])),
    (r"After the eight strong triggers among the tests that propagated", 8, F(f"{TAB15}: tests other than ST_Exp3", lambda: [float(len({r["test"] for r in strong_rows()}))])),
    (r"under three of the shapes", 3, F(f"{TAB15}: ST_Exp3 shapes with a cross-section need", lambda: [float(sum(1 for r in st3_rows() if r["C8_xs_E_by_t_J"]))])),
    (r"nine of them with both zero", 9, F("results/stage13_twobody.csv: low and high searches with both zero",
                                         lambda: [float(sum(1 for r in _csv("results/stage13_twobody.csv") if r["h"] in ("low", "high") and float(r["B2_E_J"] or 0) == 0 and float(r["lum_mid_J"] or 0) == 0))])),
    (r"four of the holds recorded there as fixed", 4, F("manuscript/rebuild/data/predictions_registry.csv: held rows whose expectation records them as fixed",
                                                        lambda: [float(sum(1 for r in _csv("manuscript/rebuild/data/predictions_registry.csv") if r["verdict"] == "held" and "fixed" in r["expectation"]))])),
    (r"Nine propagated", 9, F(f"{TESTS}: tests with propagated Yes", _n_tests(lambda r: r["propagated"] == "Yes"))),
    (r"thirteen of the sixteen tests", 13, F(f"{TRIG}: tests whose E_J exceeds the calorimetry's 33,222.9 J",
                                               lambda: [float(sum(1 for x in trig_E() if float(x) > 33222.9))])),
    (r"the fourteen with strong triggers", 14, F(f"{TRIG}: tests whose E_J exceeds 30 kJ",
                                                      lambda: [float(sum(1 for x in trig_E() if float(x) > 30000))])),
    (r"the two with weak triggers", 2, F(f"{TRIG}: tests whose E_J is below 30 kJ",
                                         lambda: [float(sum(1 for x in trig_E() if float(x) < 30000))])),
    (r"zero in the eight tests", 8, F(f"{NEEDS}: tests whose local threshold is zero",
                                      _n_needs(lambda r: r["threshold_C1_hi_J"] and float(r["threshold_C1_hi_J"]) == 0))),
    (r"in the eight tests with the largest fitted triggers", 8, F(f"{CAP}: tests run with their fitted trigger",
                                                                  lambda: [float(len({r['test'] for r in _csv(CAP)}))])),
    (r"zero in two tests", 2, F(f"{NEEDS}: tests whose lumped threshold is zero",
                                _n_needs(lambda r: r["threshold_C2_hi_J"] and float(r["threshold_C2_hi_J"]) == 0))),
    (r"in seven propagated tests", 7, F(f"{NEEDS}: propagated tests read at the measured time",
                                        _n_needs(lambda r: r["propagated"] == "yes" and "matched" in r["reading_21s"]))),
    (r"Of the five tests that did not propagate and report low maxima", 5, F(f"{TESTS}: tests that did not propagate, below 600 C",
                                                                              _n_tests(lambda r: r["propagated"] == "No" and float(r["neighbour_max_C"]) < 600))),
    (r"four need none", 4, F("results/stage9_paper_numbers.json: part_a.A3 tests with an overshoot", lambda: [float(len(overshoot()))])),
    (r"In twenty-five of them a run reproduces", 25, F(f"{TAB15}: matched cases outside ST_Exp3", lambda: [float(len(matched_rows()))])),
    (r"in the same thirty-two cases", 32, F(f"{TAB15}: cases outside ST_Exp3",
                                                     lambda: [float(sum(1 for r in _csv(TAB15) if r["test"] != "M50_ST_Exp3"))])),
    (r"in the other seven, shorter deliveries", 7, F(f"{TAB15}: cases outside ST_Exp3 whose cross-section need is a threshold",
                                                              lambda: [float(sum(1 for r in _csv(TAB15) if r["test"] != "M50_ST_Exp3"
                                                                                 and r["C8_xs_status"] == "threshold"))])),
    (r"or, in twelve, to 332", 12, F(f"{XS}: A1_rows that end at 332 s", lambda: [float(sum(1 for r in _json(XS)["A1_rows"] if r["t_end_s"] < 400))])),
    (r"rests in ten tests, PT-Exp2|ten of the high-contact outcomes", 10,
     F("results/stage15_nodelivery.csv: high-contact rows whose whole-cell outcome comes from the cross-section",
       lambda: [float(sum(1 for r in _csv("results/stage15_nodelivery.csv") if r["h"] == "high" and r["C8_source"] == "cross-section"))])),
    (r"the twelve tests not searched in three dimensions|twelve of the sixteen resolved thresholds", 12,
     F(f"{S15}: the sixteen tests less those searched in three dimensions (B1)", lambda: [16.0 - len(_json(S15)["B1"])])),
    (r"at least four delivery paths", 4, F(f"{TAB15}: the fewest of the paths A1 to A4 whose bound reaches a need at the measured time",
                                           lambda: [float(min(len(set(r[k].split()) & {"A1", "A2", "A3", "A4"}) for r in _csv(TAB15)
                                                              for k in ("C2_stage14_paths", "C8_xs_stage14_paths") if r[k]))])),
    (r"none of the three quantities", 3, F("results/stage10_heldout.json: predictors", lambda: [float(len(_json("results/stage10_heldout.json")["predictors"]))])),
    (r"all twelve of the needs with the pulse", 12, F(f"{NEEDS}: non-zero needs over 21.39 s", _n_needs(_nz21))),
    (r"radiation reaches ten", 10, F(f"{NEEDS} against {BOUNDS} A1: non-zero needs at or below the radiation bound",
                                     _n_needs(lambda r: _nz21(r) and _need21(r) <= _bound("A1")))),
    (r"five of the six parallel needs", 5, F(f"{NEEDS} against {BOUNDS} A6: parallel non-zero needs at or below the discharge bound",
                                             _n_needs(lambda r: r["connection"] == "parallel" and _nz21(r) and _need21(r) <= _bound("A6")))),
    (r"of the six parallel needs", 6, F(f"{NEEDS}: parallel non-zero needs", _n_needs(lambda r: r["connection"] == "parallel" and _nz21(r)))),
    (r"in the four tests it searched", 4, F(f"{S15}: B1 tests", lambda: [float(len(_json(S15)["B1"]))])),
]
