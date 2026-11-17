"""Stage 13: the numbers the texts quote, gathered from the Stage 13 results files into
results/stage13_paper_numbers.json (every quoted number has one source here)."""
import csv
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage13_inputs as IN                # noqa: E402

R = IN.RES


def _csv(name):
    return list(csv.DictReader(open(os.path.join(R, name))))


def _f(x):
    return None if x in (None, "", "None") else float(x)


def main():
    sc = json.load(open(os.path.join(R, "stage13_scorecard.json")))
    red = json.load(open(os.path.join(R, "stage13_reduced.json")))
    chk = json.load(open(os.path.join(R, "stage13_checks.json")))
    rd = json.load(open(os.path.join(R, "stage13_readings.json")))
    skin = _csv("stage13_skin.csv")
    tb = _csv("stage13_twobody.csv")
    mp = _csv("stage13_map.csv")
    tign = _csv("stage13_tign.csv")
    cond = _csv("stage13_conditioning.csv") if os.path.exists(os.path.join(R, "stage13_conditioning.csv")) else []
    spread = json.load(open(os.path.join(R, "stage13_spread.json"))) if os.path.exists(
        os.path.join(R, "stage13_spread.json")) else {}
    held = [k for k, v in sc.items() if v["holds"]]
    failed = [k for k, v in sc.items() if not v["holds"]]
    out = {"registration": {"commit": "fe1011554f1963b902d4fb614c089410281eed72",
                            "pushed_utc": "2026-11-16T12:52:23Z",
                            "run_lists_sha256": IN.run_lists_hash()},
           "verdicts": {"held": held, "failed": failed, "n": len(sc)},
           "scorecard": sc}
    # A3: the reduced models against the archived local brackets
    a3 = []
    for r in skin:
        if r.get("res_source") == "archived (Stage 8)" and r.get("res_lo") not in (None, ""):
            lo, hi, a2 = float(r["res_lo"]), float(r["res_hi"]), _f(r["A2_f"])
            a3.append({"test": r["test"], "tau_d_s": float(r["tau_d_s"]), "A2": a2, "bracket": [lo, hi],
                       "inside": bool(a2 is not None and (lo < a2 <= hi or (lo == hi == 0.0 and a2 == 0.0)))})
    out["A3"] = {"cases": a3, "inside": sum(c["inside"] for c in a3), "of": len(a3)}
    b3 = [r for r in tb if r.get("lum_source", "").startswith("archived")]
    out["B3"] = {"cases": [{"test": r["test"], "B2_J": _f(r["B2_E_J"]), "lo_J": _f(r["lum_lo_J"]),
                            "hi_J": _f(r["lum_hi_J"]), "archived_t_cross_s": _f(r.get("archived_t_cross_s")),
                            "B2_t_ignition_s": _f(r.get("B2_t_ignition_s"))} for r in b3]}
    out["B3"]["inside"] = sum(1 for c in out["B3"]["cases"]
                              if (c["lo_J"] < c["B2_J"] <= c["hi_J"]) or (c["hi_J"] == 0.0 and c["B2_J"] == 0.0))
    own = np.array([float(r["T_ign_C"]) for r in tign if r["kinetics"] != "mean" and r["trigger"] == "own"
                    and r["connection"] == "parallel"])
    amb = np.array([float(r["T_ign_C"]) for r in tign if r["kinetics"] != "mean" and r["trigger"] == "ambient"
                    and r["connection"] == "parallel"])
    out["B1"] = {"mean_own_C": float([r for r in tign if r["kinetics"] == "mean" and r["trigger"] == "own"][0]["T_ign_C"]),
                 "mean_ambient_parallel_C": float([r for r in tign if r["kinetics"] == "mean" and
                                                   r["trigger"] == "ambient" and r["connection"] == "parallel"][0]["T_ign_C"]),
                 "draws_own_p2.5_p97.5_C": list(np.percentile(own, [2.5, 97.5])),
                 "draws_own_min_max_C": [float(own.min()), float(own.max())],
                 "draws_ambient_p2.5_p97.5_C": list(np.percentile(amb, [2.5, 97.5])),
                 "carrying_all_draws": sorted(set(r["carrying"] for r in tign if r["kinetics"] != "mean"))}
    out["map"] = mp
    out["conditioning"] = cond
    out["spread"] = spread
    out["checks"] = {k: v.get("pass") for k, v in chk.items()}
    out["readings"] = {k: v.get("reproduced") for k, v in rd.items() if isinstance(v, dict)}
    json.dump(out, open(os.path.join(R, "stage13_paper_numbers.json"), "w"), indent=1, default=float)
    return out


if __name__ == "__main__":
    o = main()
    print(json.dumps({k: o[k] for k in ("verdicts", "A3", "checks")}, indent=1, default=float)[:3000])
