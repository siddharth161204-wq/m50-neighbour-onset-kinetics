#!/usr/bin/env python3
"""Stage 12 checks (brief of 3 November 2026; DECISIONS.md D123 (6)), by code separate from the inputs, the runner and
the scoring: none of stage12_inputs, stage12_run or stage12_score is imported, and the files are read directly.

V1  The cap and the fixed ejected energy from the Databank's rows: the largest cell-body energy of the LG M50 tests (all
    seventeen rows, and the ten nail tests) and the median of the ten nail tests' ejected energies (positive plus
    negative ejecta), each found by its columns' names, against the values every Stage 12 record holds.
V2  Energy accounts: every record's lumped and resolved accounts close (relative residual at most 1e-9); every delivery
    is exact (the integrated delivery equals f E_e, and f E_e / 76,741.25 J equals the record's fraction of the fixed
    energy); Part A delivers nothing and holds the capped trigger.
V3  Part C and P3, P4 recomputed from the records: f_t(C2) of each propagated test (Stage 9's when it matched there; a
    Stage 12 run within 10 s of the measured time; otherwise no fraction), the registered f_max from Stage 9's table,
    each test's ejected energy from Stage 8's table; Stage 10's spreads from its rank file; the tightest bracket of
    f*(C2) of each test from Stage 8's table and the Stage 12 runs; all against the scorecard.
X   Part A's central-contact runs against Stage 6's records at the same energy and release: every peak within 1e-6 K.

Writes results/stage12_checks.json. Usage: python3 stage12_checks.py
"""
import csv, glob, json, os, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
RES = os.path.join(ROOT, "results")
E_FIX_STATED = 76741.25365663527         # predictions_stage12.md
E_CAP_STATED = 33222.9
TOL_T = 10.0
OUT = {}


def rows(path):
    with open(path) as fh:
        return list(csv.DictReader(fh))


def record(name, ok, **detail):
    OUT[name] = dict(ok=bool(ok), **detail)
    print(("pass " if ok else "FAIL ") + name, {k: v for k, v in detail.items() if not isinstance(v, (list, dict))})


def stage12_records():
    return [json.load(open(p)) for p in sorted(glob.glob(os.path.join(RES, "stage12_runs", "s12_*.json")))]


# ------------------------------------------------------------------------------------------------ V1
def v1(recs):
    db = rows(os.path.join(ROOT, "inputs", "databank", "databank_m50_used.csv"))
    body = [(float(r["Energy-Fraction-Cell-Body-kJ"]) * 1e3, r["Test-ID"]) for r in db]
    nail = [r for r in db if r["Trigger-Mechanism"].strip().lower() == "nail"]
    body_nail = [(float(r["Energy-Fraction-Cell-Body-kJ"]) * 1e3, r["Test-ID"]) for r in nail]
    ej = [(float(r["Energy-Fraction-Positive-Ejecta-kJ"]) + float(r["Energy-Fraction-Negative-Ejecta-kJ"])) * 1e3
          for r in nail]
    cap, cap_id = max(body)
    med = statistics.median(ej)
    ok_cap = round(cap, 1) == E_CAP_STATED and max(body_nail) == (cap, cap_id) and cap_id.endswith("RUN195")
    ok_med = len(nail) == 10 and abs(med - E_FIX_STATED) < 1e-6
    a = [r for r in recs if r["kind"] == "A"]
    b = [r for r in recs if r["kind"] in ("B1", "B2")]
    ok_rec = all(r["E_body_J"] == E_CAP_STATED for r in a) and all(abs(r["E_fix_J"] - med) < 1e-6 for r in b)
    record("V1", ok_cap and ok_med and ok_rec, cap_J=cap, cap_test=cap_id, n_rows=len(db), n_nail=len(nail),
           median_ejected_J=med, ejected_J=sorted(ej), part_a_records=len(a), part_b_records=len(b))


# ------------------------------------------------------------------------------------------------ V2
def released(E, tau, t):
    """The energy a symmetric triangular pulse of E over tau, from t = 0, has released by t (this check's statement)."""
    if t <= 0.0:
        return 0.0
    if t >= tau:
        return E
    x = t / tau
    return 2.0 * E * x * x if x <= 0.5 else E * (1.0 - 2.0 * (1.0 - x) ** 2)


def v2(recs):
    """A run that stops at its crossing before the pulse ends (C1's runs stop at the hot spot's) has released only the
    pulse's share up to its end; the check compares with that share, and counts the deliveries that ran whole."""
    bad, worst = [], {"lumped": 0.0, "resolved": 0.0, "delivery": 0.0, "fixed": 0.0}
    n = {"deliveries": 0, "whole": 0, "cut_at_stop": 0}
    for r in recs:
        for m in ("lumped", "resolved"):
            x = r.get(m)
            if x:
                res = abs(x["energy_residual_rel"])
                worst[m] = max(worst[m], res)
                if res > 1e-9:
                    bad.append((r["id"], m, "residual", res))
                dsrc = (x.get("sources") or {}).get("delivery")
                if r["kind"] == "A":
                    if dsrc or x["energy_J"].get("in_delivery", 0.0) != 0.0:
                        bad.append((r["id"], m, "delivery in Part A"))
                else:
                    E = r["f"] * r["E_e_J"]
                    if abs(r["E_delivered_J"] - E) > 1e-12 * E or abs(dsrc["E_J"] - E) > 1e-12 * E:
                        bad.append((r["id"], m, "requested", r["E_delivered_J"], dsrc["E_J"], E))
                    want = released(E, r["tau_d_s"], x["t_end_s"])
                    n["deliveries"] += 1
                    n["whole" if x["t_end_s"] >= r["tau_d_s"] else "cut_at_stop"] += 1
                    for got in (dsrc["delivered_J"], x["energy_J"]["in_delivery"]):
                        d = abs(got - want) / want
                        worst["delivery"] = max(worst["delivery"], d)
                        if d > 1e-9:
                            bad.append((r["id"], m, "delivery", got, want))
        if r["kind"] == "A":
            if r["E_delivered_J"] != 0.0 or r["f"] != 0.0 or r["E_body_J"] != E_CAP_STATED:
                bad.append((r["id"], "Part A inputs"))
        else:
            d = abs(r["f_fixed"] * E_FIX_STATED - r["E_delivered_J"]) / r["E_delivered_J"]
            worst["fixed"] = max(worst["fixed"], d)
            if d > 1e-12:
                bad.append((r["id"], "fixed fraction", d))
    record("V2", not bad, records=len(recs), worst_relative=worst, counts=n, problems=bad)


# ------------------------------------------------------------------------------------------------ V3
def v3(recs, card):
    ee = {r["id"]: float(r["E_e_J"]) for r in rows(os.path.join(RES, "stage8_ejected.csv")) if r["kind"] == "test"}
    tests = {r["test"]: r for r in rows(os.path.join(ROOT, "inputs", "fransson2024", "m50_tests.csv"))}
    s9 = json.load(open(os.path.join(RES, "stage9_states.json")))
    fr9 = {r["test"]: r for r in rows(os.path.join(RES, "stage9_fractions.csv"))}
    by_test = {}
    for r in recs:
        if r["kind"] == "B2":
            by_test.setdefault(r["test"], []).append(r)
    # f_t(C2) of the nine propagated tests
    ft, none = {}, {}
    for t, row in tests.items():
        if row["propagated"] != "Yes":
            continue
        st = s9[f"A2_C2_{t}"]
        t_m = float(row["time_to_propagation_s"])
        if st["status"] == "matched":
            ft[t] = st["f_t"]
            continue
        hit = [r for r in by_test.get(t, []) if r["lumped"]["propagated"] and abs(r["lumped"]["t_prop_s"] - t_m) <= TOL_T]
        if hit:
            ft[t] = hit[0]["f"]
        else:
            none[t] = "no run within 10 s"
    energy = {t: f * ee[t] for t, f in ft.items()}
    for t, r in fr9.items():
        if r["propagated"] == "False" and r["fmax_exploratory"] == "False":
            energy[t] = float(r["fmax_E_J"])
    nz = {t: e for t, e in energy.items() if e > 0}
    ratio = max(nz.values()) / min(nz.values())
    zeros = sorted(t for t, e in energy.items() if e == 0)
    pc = card["part_c"]
    ok_c = (abs(ratio - pc["ratio_largest_to_smallest_nonzero"]) < 1e-9 * ratio
            and min(nz, key=nz.get) == pc["smallest"]["test"] and max(nz, key=nz.get) == pc["largest"]["test"]
            and zeros == pc["zero_tests"] and sorted(none) == sorted(t for t, _ in pc["no_fraction"])
            and all(abs(energy[t] - pc["energies_J"][t]) < 1e-6 for t in energy))
    cm = sorted(t for t, r in tests.items() if r["failure_category"] == "cell movement")
    ok_cm = (cm == pc["cell_movement_tests"] and (min(nz, key=nz.get) in cm) == pc["smallest"]["cell_movement"]
             and (max(nz, key=nz.get) in cm) == pc["largest"]["cell_movement"])
    # P3 and P4
    prop_e = {t: energy[t] for t in ft}
    p3 = max(prop_e.values()) / min(prop_e.values())
    fmax_f = max(float(r["fmax_E_J"]) for r in fr9.values() if r["propagated"] == "False" and r["fmax_exploratory"] == "False") / E_FIX_STATED
    ft_f = min(prop_e.values()) / E_FIX_STATED
    P = card["predictions"]
    ok_p = (abs(p3 - P["P3"]["ratio"]) < 1e-9 * p3 and (p3 >= 10) == (P["P3"]["verdict"] == "holds")
            and abs(fmax_f - P["P4"]["largest_registered_f_max"]["f_fixed"]) < 1e-12
            and abs(ft_f - P["P4"]["smallest_f_t"]["f_fixed"]) < 1e-12 and (fmax_f > ft_f) == (P["P4"]["verdict"] == "holds"))
    # Stage 10's spreads, in fraction and in energy
    sp = json.load(open(os.path.join(RES, "stage10_rank.json")))["spread"]
    e10, f10 = [], []
    for d in ("tri21", "120", "240", "360"):
        fr = {t: x for t, x in sp[f"C2_{d}"]["fractions"].items() if x > 0}
        en = [x * ee[t] for t, x in fr.items()]
        e10.append(max(en) / min(en))
        f10.append(max(fr.values()) / min(fr.values()))
    ok_10 = (abs(min(e10) - pc["stage10_energy_ratio_range"][0]) < 1e-9 and abs(max(e10) - pc["stage10_energy_ratio_range"][1]) < 1e-9
             and abs(min(f10) - pc["stage10_fraction_ratio_range"][0]) < 1e-9
             and abs(max(f10) - pc["stage10_fraction_ratio_range"][1]) < 1e-9)
    # f*(C2) as fractions of the fixed energy: the tightest bracket from Stage 8's and every Stage 12 run of the lumped
    # neighbour (B1, with the fraction's run giving C2's crossing or none)
    th = {r["test"]: r for r in rows(os.path.join(RES, "stage8_thresholds.csv"))}
    mids = {}
    for crit, model, col in (("C2", "lumped", "fC2"), ("C1", "resolved", "fC1")):
        for t, r in th.items():
            lo, hi = float(r[col + "_lo"] or 0.0), float(r[col + "_hi"] or 0.0)
            if r[col].strip() not in ("0", "0.0"):
                for x in recs:
                    if x["kind"] == "B1" and x["test"] == t and x.get(model):
                        if x[model]["propagated"] and x["f"] < hi:
                            hi = x["f"]
                        if not x[model]["propagated"] and x["f"] > lo:
                            lo = x["f"]
            else:
                lo = hi = 0.0
            m = 0.5 * (lo + hi) * ee[t] / E_FIX_STATED
            got = pc[f"fstar_{crit}_fixed"][t]
            if (abs(m - got["mid_fixed"]) > 1e-12 or abs(lo * ee[t] / E_FIX_STATED - got["f_fixed"][0]) > 1e-12
                    or abs(hi * ee[t] / E_FIX_STATED - got["f_fixed"][1]) > 1e-12):
                ok_10 = False
            if crit == "C2":
                mids[t] = m
    nzm = {t: v for t, v in mids.items() if v > 0}
    fs_ratio = max(nzm.values()) / min(nzm.values())
    ok_fs = abs(fs_ratio - pc["fstar_C2_fixed_ratio_of_midpoints"]) < 1e-9 * fs_ratio
    record("V3", ok_c and ok_cm and ok_p and ok_10 and ok_fs, ratio=ratio, smallest=min(nz, key=nz.get),
           largest=max(nz, key=nz.get), zeros=zeros, p3_ratio=p3, p4_fmax_fixed=fmax_f, p4_ft_fixed=ft_f,
           stage10_energy=[min(e10), max(e10)], stage10_fraction=[min(f10), max(f10)], fstar_C2_fixed_ratio=fs_ratio,
           parts={"spread": ok_c, "cell_movement": ok_cm, "P3_P4": ok_p, "stage10": ok_10, "fstar": ok_fs})


# ------------------------------------------------------------------------------------------------ X
def x_stage6(recs):
    ids = {"series": "body_mean_series_hcentral_gcentral_tau21.39_E33.22",
           "parallel": "body_mean_parallel_hcentral_gcentral_tau21.39_E33.22"}
    diffs, same_inputs = {}, True
    for c, sid in ids.items():
        s6 = json.load(open(os.path.join(RES, "stage6_runs", sid + ".json")))
        r = [x for x in recs if x["id"] == f"s12_A_cap_{c}_hcentral_both_ns"][0]
        for k in ("connection", "h", "g", "tau", "E_body_J", "T_amb_K", "kin"):
            same_inputs &= r[k] == s6[k]
        pairs = {"hot_spot_peak_C": (r["resolved"]["peak_hottest_C"], s6["resolved"]["peak_hottest_C"]),
                 "mean_peak_C": (r["resolved"]["peak_mean_C"], s6["resolved"]["peak_mean_C"]),
                 "lumped_peak_C": (r["lumped"]["peak_C"], s6["lumped"]["peak_C"]),
                 "trigger_peak_C": (r["T1max_C"], s6["T1max_C"])}
        diffs[c] = {k: abs(a - b) for k, (a, b) in pairs.items()}
        diffs[c]["propagated"] = [r["resolved"]["propagated"], s6["resolved"]["propagated"], r["lumped"]["propagated"],
                                  s6["lumped"]["propagated"]]
        diffs[c]["t_peak_s"] = [r["resolved"]["t_peak_hottest_s"], s6["resolved"]["t_peak_hottest_s"],
                                r["lumped"]["t_peak_s"], s6["lumped"]["t_peak_s"]]
    worst = max(v for d in diffs.values() for k, v in d.items() if k not in ("propagated", "t_peak_s"))
    none = all(x is False for d in diffs.values() for x in d["propagated"])
    same_t = all(d["t_peak_s"][0] == d["t_peak_s"][1] and d["t_peak_s"][2] == d["t_peak_s"][3] for d in diffs.values())
    none = none and same_t
    record("X", same_inputs and worst <= 1e-6 and none, worst_K=worst, differences=diffs)


def main():
    recs = stage12_records()
    card = json.load(open(os.path.join(RES, "stage12_scorecard.json")))
    v1(recs)
    v2(recs)
    v3(recs, card)
    x_stage6(recs)
    OUT["all_pass"] = all(v["ok"] for v in OUT.values() if isinstance(v, dict))
    json.dump(OUT, open(os.path.join(RES, "stage12_checks.json"), "w"), indent=1, default=float)
    print("all pass" if OUT["all_pass"] else "SOME CHECKS FAIL")


if __name__ == "__main__":
    main()
