"""Stage 13 checks V1 to V6 (DECISIONS.md D136). Writes results/stage13_checks.json.

V1  A1, A2 and B2 each by their two implementations: the thresholds agree to 1e-8.
V2  A2 against the resolved neighbour with the reaction off (PT_Exp1, facing half, 21.39 s, f = 0.15625): the hot
    spot's temperature within 2 % of the resolved rise at every 0.1 s from 1 s to 3 tau_d; the whole window reported.
V3  B2's inert temperature against the lumped neighbour with the reaction off, three tests, within 0.5 K over 900 s.
V4  every new run's energy account to 1e-6 of the heat taken in, and its delivery exact to 1e-9.
V5  the hand cases (recomputed here from their formulas).
V6  the new regions' weights against their areas, within 0.1 % (results/stage13_v6.json).
Usage: python3 stage13_checks.py [v1|v2|v3|v4|v5|v6|all]
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage13_inputs as IN                # noqa: E402

OUT = os.path.join(IN.RES, "stage13_checks.json")
T21 = IN.TAU_TRIGGER


def _load():
    return json.load(open(OUT)) if os.path.exists(OUT) else {}


def _save(d):
    json.dump(d, open(OUT, "w"), indent=1, default=float)


def v1():
    import stage13_section as A2
    import stage13_twobody as B2
    red = json.load(open(os.path.join(IN.RES, "stage13_reduced.json")))
    out = {"A1": [], "A2": [], "B2": []}
    for k, r in red.items():
        if k.startswith("A2_") and "A1" in r:
            a, b = r["A1"]["f_star"], r["A1_laplace_f_star"]
            out["A1"].append({"case": k, "closed": a, "laplace": b, "rel": abs(a - b) / a})
    for test, tau in (("M50_PT_Exp1", T21), ("M50_ST_Exp3", 60.0)):
        a = red[f"A2_{test}_half_tau{tau:.4f}_r1_dt1"]["f_star"]
        b = A2.threshold(test, tau, impl="banded")["f_star"]
        out["A2"].append({"case": f"{test} {tau:g} s", "sparse": a, "banded": b, "rel": abs(a - b) / a})
    for test, h in (("M50_PT_Exp1", "central"), ("M50_PP_Exp3", "central"), ("M50_ST_Exp3", "central"),
                    ("M50_SP_Exp3", "central"), ("M50_PT_Exp1", "low")):
        a = red[f"B2_{test}_tau{T21:.4f}_{h}_dEb+0"]["E_star_J"]
        b = B2.Case(test, h=h, impl="dp5").threshold()
        out["B2"].append({"case": f"{test} {h}", "rk4": a, "dp5": b, "rel": abs(a - b) / max(a, 1e-300) if a else
                          abs(b)})
    worst = max(x["rel"] for v in out.values() for x in v)
    out.update({"worst_rel": worst, "pass": bool(worst <= 1e-8)})
    return out


def _rec(rid):
    return json.load(open(os.path.join(IN.RUNS, rid + ".json")))


def v2():
    import stage13_section as A2
    import v12_model as V
    import glob
    fn = glob.glob(os.path.join(IN.RUNS, "*_V2.json"))
    if not fn:
        return {"pass": None, "note": "the V2 run is not recorded yet"}
    rec = json.load(open(fn[0]))
    ser = np.load(os.path.join(IN.SERIES, rec["id"] + ".npz"))
    f = rec["f"]
    t = IN.tests()["M50_PT_Exp1"]
    f1, data, _, _ = V.stage5_t1(t["connection"], V.H_CONTACT["central"], V.G_TAB["central"], T21, float(t["E_b_J"]),
                                 IN.T_AMB)
    sec = A2.Section()
    F = A2.tri_cumulative(T21)
    tt, Ts, inner = sec.run(f1, F, f * IN.e_e("M50_PT_Exp1"), 900.0, 0.01, 0.0214)
    a2max = np.maximum(Ts.max(axis=1), inner)
    tr, Tr = ser["t"], ser["Tmax"]
    a2_at = np.interp(tr, tt, a2max)
    rise = Tr - IN.T_AMB
    dev = np.abs(a2_at - Tr) / np.maximum(rise, 1e-9)
    win = (tr >= 1.0 - 1e-9) & (tr <= 3 * T21 + 1e-9)
    out = {"run": rec["id"], "f": f, "window_s": [1.0, 3 * T21], "max_rel_dev_window": float(dev[win].max()),
           "t_at_max_window_s": float(tr[win][np.argmax(dev[win])]), "max_rel_dev_all": float(dev[tr >= 1.0].max()),
           "t_at_max_all_s": float(tr[tr >= 1.0][np.argmax(dev[tr >= 1.0])]),
           "resolved_peak_C": float(Tr.max() - IN.K0), "A2_peak_C": float(a2max.max() - IN.K0),
           "resolved_t_peak_s": float(tr[np.argmax(Tr)]), "A2_t_peak_s": float(tt[np.argmax(a2max)])}
    out["pass"] = bool(out["max_rel_dev_window"] <= 0.02)
    return out


def v3():
    import glob
    import stage13_twobody as B2
    out = []
    for test in ("M50_PT_Exp1", "M50_ST_Exp3", "M50_PP_Exp3"):
        fn = glob.glob(os.path.join(IN.RUNS, f"s13_V3_{test[4:]}_*_inert_ns.json"))
        if not fn:
            out.append({"test": test, "pass": None})
            continue
        rec = json.load(open(fn[0]))
        ser = np.load(os.path.join(IN.SERIES, rec["id"] + ".npz"))
        c = B2.Case(test)
        c.path(rec["E_delivered_J"])
        tb = np.arange(len(c.out)) * 0.1
        tl, Tl = ser["t_lumped"], ser["T_lumped"]
        d = np.abs(np.interp(tl, tb, c.out) - Tl)
        out.append({"test": test, "E_J": rec["E_delivered_J"], "max_abs_K": float(d.max()),
                    "t_at_max_s": float(tl[np.argmax(d)]), "pass": bool(d.max() <= 0.5)})
    return {"cases": out, "pass": (all(x["pass"] for x in out) if all(x["pass"] is not None for x in out) else None)}


def v4():
    import glob
    worst_e, worst_d, n, bad = 0.0, 0.0, 0, []
    for fn in glob.glob(os.path.join(IN.RUNS, "*.json")):
        r = json.load(open(fn))
        if r.get("failed"):
            bad.append(r["id"])
            continue
        p = r["resolved"] or r["lumped"]
        n += 1
        e = abs(p["energy_residual_rel"]) if p["energy_residual_rel"] is not None else 0.0
        worst_e = max(worst_e, e)
        if r["E_delivered_J"] > 0:
            dlv = p["sources"]["delivery"]["delivered_J"]
            # a run that stops before the delivery has ended has delivered only the part released by then
            if not p["stopped"]:
                worst_d = max(worst_d, abs(dlv - r["E_delivered_J"]) / r["E_delivered_J"])
    return {"runs": n, "failed": bad, "worst_energy_residual_rel": worst_e, "worst_delivery_rel": worst_d,
            "pass": bool(not bad and worst_e <= 1e-6 and worst_d <= 1e-9)}


def v5():
    import stage13_skin as A1
    import stage13_tign as B1
    import bcrnn
    Phi00 = A1.Phi(0.0, 0.0)
    exact = 16 / (3 * math.sqrt(math.pi)) * ((2 / 3) ** 1.5 - 2 * (1 / 6) ** 1.5)
    kin = bcrnn.Kinetics()
    T = B1.t_ign(kin, "own", B1.g_link("parallel"))
    return {"Phi00": Phi00, "Phi00_exact": exact, "T_ign_own_C": T - IN.K0,
            "balance_at_T_ign_W": B1.balance(kin, T, "own", B1.g_link("parallel")),
            "pass": bool(abs(Phi00 - exact) < 1e-9)}


def v6():
    d = json.load(open(os.path.join(IN.RES, "stage13_v6.json")))
    worst = max(abs(d[g]["rel_diff"]) for g in ("half", "whole", "eighth"))
    return {"regions": {g: d[g] for g in ("half", "whole", "eighth")}, "worst": worst, "pass": bool(worst <= 1e-3)}


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    d = _load()
    for name, fn in (("V1", v1), ("V2", v2), ("V3", v3), ("V4", v4), ("V5", v5), ("V6", v6)):
        if which in ("all", name.lower()):
            d[name] = fn()
            print(name, json.dumps(d[name], default=float)[:600])
            _save(d)
