"""Stage 13, Part C2: the conditioning of the whole-cell threshold, from B2 (DECISIONS.md D138 (2)).

For each of the sixteen tests at the central contact with the 21.39 s triangle: B2's E* and its derivatives by
central differences in the trigger's body energy (plus and minus 500 J), the contact conductance h_c (plus and minus
5 %, in the trigger's pair and in the neighbour), the neighbour's heat capacity C (plus and minus 1 %, the trigger's
history held) and the ignition temperature (the balance taken 1 K higher and lower); the error each implies with the
archive's bracket (the f*(C2) bracket's width in energy divided by the derivative). Also B2's spread of f* over the
sixteen tests with the 21.39 s triangle and with constant powers of 120, 240 and 360 s, and at Stage 12's one
ejected energy. Writes results/stage13_conditioning.csv and results/stage13_spread.json.
Usage: python3 stage13_conditioning.py [--workers 2]
"""
import argparse
import csv
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage13_inputs as IN                # noqa: E402

T21 = IN.TAU_TRIGGER
OUT = os.path.join(IN.RES, "stage13_conditioning.csv")
CACHE = os.path.join(IN.RES, "stage13_conditioning_cases.json")


def _cases():
    out = []
    for t in IN.TEST_ORDER:
        for name, kw in (("base", {}), ("Eb+", {"dE_body": 500.0}), ("Eb-", {"dE_body": -500.0}),
                         ("hc+", {"h_c": 2000.0 * 1.05}), ("hc-", {"h_c": 2000.0 * 0.95}),
                         ("C+", {"C": 61.75 * 1.01}), ("C-", {"C": 61.75 * 0.99}),
                         ("Ti+", {"dT_ign": 1.0}), ("Ti-", {"dT_ign": -1.0})):
            out.append((t, name, "tri", T21, kw))
        for tau in (120.0, 240.0, 360.0):
            out.append((t, f"con{tau:g}", "con", tau, {}))
    return out


def _do(case):
    import stage13_twobody as B2
    t, name, shape, tau, kw = case
    c = B2.Case(t, tau_d=tau, shape=shape, **kw)
    return f"{t}|{name}", c.threshold()


def main(workers=2):
    done = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    todo = [c for c in _cases() if f"{c[0]}|{c[1]}" not in done]
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for k, E in ex.map(_do, todo):
            done[k] = E
            json.dump(done, open(CACHE, "w"), indent=1)
            print(k, round(E, 3), flush=True)
    br = {r["test"]: r for r in csv.DictReader(open(os.path.join(IN.RES, "stage8_thresholds.csv")))}
    rows = []
    for t in IN.TEST_ORDER:
        g = lambda n: done[f"{t}|{n}"]
        Ee = IN.e_e(t)
        width = 0.0125 * Ee
        d = {"dE*/dE_b": (g("Eb+") - g("Eb-")) / 1000.0, "dE*/dln h_c": (g("hc+") - g("hc-")) / 0.10,
             "dE*/dln C": (g("C+") - g("C-")) / 0.02, "dE*/dT_ign": (g("Ti+") - g("Ti-")) / 2.0}
        one_sided = any(g(n) == 0.0 for n in ("Eb+", "Eb-", "hc+", "hc-", "C+", "C-", "Ti+", "Ti-")) and g("base") > 0
        row = {"test": t, "connection": IN.tests()[t]["connection"], "E_b_J": float(IN.tests()[t]["E_b_J"]),
               "E_e_J": Ee, "B2_E_star_J": g("base"), "B2_f_star": g("base") / Ee,
               "archived_fC2": br[t]["fC2"], "bracket_width_J": width,
               "dEstar_dEb_J_per_J": d["dE*/dE_b"], "dEstar_dlnhc_J": d["dE*/dln h_c"],
               "dEstar_dlnC_J": d["dE*/dln C"], "dEstar_dTign_J_per_K": d["dE*/dT_ign"],
               "bracket_as_E_b_J": width / abs(d["dE*/dE_b"]) if d["dE*/dE_b"] else None,
               "bracket_as_h_c_pct": 100 * width / abs(d["dE*/dln h_c"]) if d["dE*/dln h_c"] else None,
               "bracket_as_C_pct": 100 * width / abs(d["dE*/dln C"]) if d["dE*/dln C"] else None,
               "bracket_as_T_ign_K": width / abs(d["dE*/dT_ign"]) if d["dE*/dT_ign"] else None,
               "near_zero": bool(one_sided or g("base") == 0.0)}
        for tau in (120.0, 240.0, 360.0):
            row[f"B2_f_star_con{tau:g}"] = g(f"con{tau:g}") / Ee
        rows.append(row)
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    import stage12_inputs as S12
    e_fixed = float(S12.fixed_ejecta()[0])

    def ratio(vals):
        nz = [v for v in vals if v > 0]
        return (max(nz) / min(nz)) if nz else None, (len(vals) - len(nz))

    sp = {"tri21": ratio([r["B2_f_star"] for r in rows])}
    for tau in (120, 240, 360):
        sp[f"con{tau}"] = ratio([r[f"B2_f_star_con{tau}"] for r in rows])
    sp["fixed_ejecta_J"] = e_fixed
    sp["fixed_tri21"] = ratio([r["B2_E_star_J"] / e_fixed for r in rows])
    sp["archived"] = {"tri21": 73.0, "con120": 79.0, "con240": 91.25, "con360": 108.75, "fixed_midpoints": 14.0}
    json.dump(sp, open(os.path.join(IN.RES, "stage13_spread.json"), "w"), indent=1)
    return rows, sp


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    rows, sp = main(a.workers)
    print(json.dumps(sp, indent=1))
