#!/usr/bin/env python3
"""Stage 3a metrics and the scoring of P1, P2, P3 and P6 (predictions_stage3.md; DECISIONS.md D26).

Reads results/stage3a_onsets.csv (stage3a.py --merge), the V4 classes (results/stage3_v4_arc_draws.csv) and Stage 1's
posterior-mean records (results/onset_results.csv) for reference. Every draw stays in every metric; the V4 classes
are reported beside the metrics, not used to drop draws.

Writes results/stage3a_metrics.json, results/stage3a_per_draw.csv, results/stage3a_p3_by_draw.csv and the 3a part of
results/stage3_scorecard.json.

Usage: python3 stage3a_score.py --out ../results
"""
import argparse, csv, json, os
import numpy as np

NINE = ["two_E33223_tau10_G0.5", "two_E33223_tau10_G0.2", "two_E33223_tau10_G0.1", "two_E33223_tau10_G0.05",
        "two_E33223_tau30_G0.5", "two_E33223_tau30_G0.2", "two_E33223_tau30_G0.1", "two_E33223_tau30_G0.05",
        "two_E21495_tau30_G0.5"]
HEADLINE = "two_E33223_tau30_G0.5"
N = 200
LV = "0.15Kpm"


def num(v):
    return None if v in ("", "None", None) else float(v)


def load(out):
    on = {}
    for r in csv.DictReader(open(os.path.join(out, "stage3a_onsets.csv"))):
        on[(int(r["draw"]), r["case"], r["history"])] = r
    cls = {int(r["draw"]): r["class"] for r in csv.DictReader(open(os.path.join(out, "stage3_v4_arc_draws.csv")))}
    s1 = {r["case"]: r for r in csv.DictReader(open(os.path.join(out, "onset_results.csv")))}
    return on, cls, s1


def pct(values, qs=(2.5, 50, 97.5)):
    """Percentiles over all draws with None ranked after every value (+inf); a percentile among them is None."""
    v = np.array([np.inf if x is None else x for x in values], float)
    out = {}
    for q in qs:
        p = float(np.percentile(v, q)) if v.size else None
        out[f"p{q:g}"] = p if p is not None and np.isfinite(p) else None
    return out


def lead_pct(hot, lump, qs=(2.5, 50, 97.5)):
    """D26: over draws whose hottest node starts; a lumped node that does not start ranks as the longest lead."""
    v = np.array([np.inf if l is None else l - h for h, l in zip(hot, lump) if h is not None], float)
    out = {"n": int(v.size), "n_lumped_not_started": int(np.isinf(v).sum())}
    for q in qs:
        p = float(np.percentile(v, q)) if v.size else None
        out[f"p{q:g}"] = p if p is not None and np.isfinite(p) else None
    both = np.array([l - h for h, l in zip(hot, lump) if h is not None and l is not None], float)
    out["both_started"] = {"n": int(both.size), **({f"p{q:g}": float(np.percentile(both, q)) for q in qs} if both.size else {}),
                           **({"mean": float(both.mean()), "sd": float(both.std(ddof=1))} if both.size > 1 else {})}
    return out


def sd(values):
    v = np.array([x for x in values if x is not None], float)
    return {"n": int(v.size), "n_without": int(sum(x is None for x in values)),
            "mean": float(v.mean()) if v.size else None, "sd": float(v.std(ddof=1)) if v.size > 1 else None}


def case_metrics(on, cls, case):
    hist = ("hottest_node", "resolved_mean", "lumped")
    t = {h: [num(on[(d, case, h)][f"t_{LV}_s"]) for d in range(1, N + 1)] for h in hist}
    T = {h: [num(on[(d, case, h)][f"T_at_{LV}_C"]) for d in range(1, N + 1)] for h in hist}
    rxn_hot = [on[(d, case, "hottest_node")][f"rxn_at_{LV}"] for d in range(1, N + 1)]
    hot, lump, mean = t["hottest_node"], t["lumped"], t["resolved_mean"]
    only_hot = [h is not None and l is None for h, l in zip(hot, lump)]
    none_any = [h is None and l is None and m is None for h, l, m in zip(hot, lump, mean)]
    sei = [r == "sei_decomp" for r in rxn_hot]
    early = [x is not None and x < 100.0 for x in T["hottest_node"]]
    before = [h is not None and (l is None or h < l) for h, l in zip(hot, lump)]
    m = {"case": case,
         "onset_s": {h: {**pct(t[h]), **sd(t[h])} for h in hist},
         "onset_temperature_C": {h: {**pct(T[h]), **sd(T[h])} for h in hist},
         "lead_s": lead_pct(hot, lump),
         "share_hottest_before_lumped": sum(before) / N,
         "share_only_hottest_starts": sum(only_hot) / N,
         "share_hottest_onset_sei": sum(sei) / N,
         "hottest_onset_reactions": {r: sum(x == r for x in rxn_hot) for r in sorted(set(x or "none" for x in rxn_hot))},
         "share_no_onset_anywhere": sum(none_any) / N,
         "share_hottest_onset_below_100C": sum(early) / N,
         "by_V4_class": {}}
    for c in sorted(set(cls.values())):
        idx = [d - 1 for d in range(1, N + 1) if cls[d] == c]
        if not idx:
            continue
        m["by_V4_class"][c] = {"n": len(idx),
                               "hottest_onset_s_median": float(np.median([hot[i] for i in idx if hot[i] is not None])) if any(hot[i] is not None for i in idx) else None,
                               "lumped_onset_s_median": float(np.median([lump[i] for i in idx if lump[i] is not None])) if any(lump[i] is not None for i in idx) else None,
                               "share_only_hottest_starts": sum(only_hot[i] for i in idx) / len(idx),
                               "share_hottest_onset_below_100C": sum(early[i] for i in idx) / len(idx)}
    return m


def p3_by_draw(on, cases):
    """Smallest conductance among the 42 two-strip cases with an onset at the hottest node and none at the lumped node."""
    out = {}
    for d in range(1, N + 1):
        gs = [float(c.split("_G")[1]) for c in cases
              if num(on[(d, c, "hottest_node")][f"t_{LV}_s"]) is not None and num(on[(d, c, "lumped")][f"t_{LV}_s"]) is None]
        out[d] = (min(gs) if gs else None, sorted(set(gs)))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="../results")
    a = ap.parse_args()
    on, cls, s1 = load(a.out)
    cases = sorted({k[1] for k in on})
    assert len(cases) == 42 and all(c in cases for c in NINE)
    assert len({k[0] for k in on}) == N
    metrics = {c: case_metrics(on, cls, c) for c in NINE}
    p3 = p3_by_draw(on, cases)
    p3_vals = [p3[d][0] for d in range(1, N + 1)]
    gvals = sorted(set(v for v in p3_vals if v is not None))
    p3_dist = {**{f"{int(round(g * 1000))} mW/K": sum(v == g for v in p3_vals) / N for g in gvals},
               "none": sum(v is None for v in p3_vals) / N}
    H = metrics[HEADLINE]
    w_hot = (H["onset_s"]["hottest_node"]["p97.5"] - H["onset_s"]["hottest_node"]["p2.5"]) if H["onset_s"]["hottest_node"]["p97.5"] is not None else None
    w_lump = (H["onset_s"]["lumped"]["p97.5"] - H["onset_s"]["lumped"]["p2.5"]) if H["onset_s"]["lumped"]["p97.5"] is not None else None
    share100 = sum(v == 0.1 for v in p3_vals) / N
    n_above = sum(v is not None and v > 0.2 for v in p3_vals)
    score = {
        "P1": {"share_hottest_before_lumped": H["share_hottest_before_lumped"], "threshold": "> 0.95",
               "held": H["share_hottest_before_lumped"] > 0.95, "brief_central": 0.99, "study_central": 1.0},
        "P2": {"hottest_width_s": w_hot, "lumped_width_s": w_lump,
               "hottest_interval_s": [H["onset_s"]["hottest_node"]["p2.5"], H["onset_s"]["hottest_node"]["p97.5"]],
               "lumped_interval_s": [H["onset_s"]["lumped"]["p2.5"], H["onset_s"]["lumped"]["p97.5"]],
               "threshold": "hottest < 20 s and lumped > 20 s (an interval reaching beyond 900 s counts as wider)",
               "held": (w_hot is not None and w_hot < 20.0) and (w_lump is None or w_lump > 20.0),
               "brief_central_s": [8, 40], "study_central_s": [9.2, 64.2]},
        "P3": {"distribution": p3_dist, "share_100mW_per_K": share100, "n_above_200mW_per_K": n_above,
               "threshold": "share at 100 mW/K > 0.5 and none above 200 mW/K",
               "held": share100 > 0.5 and n_above == 0, "parts": {"a_share_above_half": share100 > 0.5, "b_never_above_200": n_above == 0},
               "brief_central": 0.70, "study_central": 0.185},
        "P6": {"share_hottest_onset_below_100C": H["share_hottest_onset_below_100C"], "threshold": "< 0.10",
               "held": H["share_hottest_onset_below_100C"] < 0.10, "study_central": 0.365,
               "other_cases": {c: metrics[c]["share_hottest_onset_below_100C"] for c in NINE if c != HEADLINE}},
        "P4": "scored in Stage 3b", "P5": "scored in Stage 3b"}
    ref = {c: {h: num(s1[c][f"{h}_t_{LV}_s"]) for h in ("hottest_node", "resolved_mean", "lumped")} for c in NINE}
    outliers = {c: sum(v == c for v in cls.values()) / N for c in ("main_cluster", "delayed_short", "no_short")}
    json.dump({"n_draws": N, "cases": NINE, "headline": HEADLINE, "mean_model_stage1_onsets_s": ref,
               "V4_class_fractions": outliers, "metrics": metrics,
               "P3_distribution_42_cases": p3_dist}, open(os.path.join(a.out, "stage3a_metrics.json"), "w"), indent=1)
    with open(os.path.join(a.out, "stage3a_p3_by_draw.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["draw", "smallest_only_local_G_W_per_K", "all_only_local_G_W_per_K", "V4_class"])
        for d in range(1, N + 1):
            w.writerow([d, "" if p3[d][0] is None else p3[d][0], " ".join(f"{g:g}" for g in p3[d][1]), cls[d]])
    with open(os.path.join(a.out, "stage3a_per_draw.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["draw", "V4_class", "headline_hottest_onset_s", "headline_lumped_onset_s", "headline_resolved_mean_onset_s",
                    "headline_lead_s", "headline_hottest_onset_T_C", "headline_hottest_onset_reaction", "early_sei_below_100C",
                    "p3_smallest_only_local_G_W_per_K"])
        for d in range(1, N + 1):
            h = num(on[(d, HEADLINE, "hottest_node")][f"t_{LV}_s"]); l = num(on[(d, HEADLINE, "lumped")][f"t_{LV}_s"])
            m_ = num(on[(d, HEADLINE, "resolved_mean")][f"t_{LV}_s"]); Th = num(on[(d, HEADLINE, "hottest_node")][f"T_at_{LV}_C"])
            w.writerow([d, cls[d], h, l, m_, None if (h is None or l is None) else l - h, Th,
                        on[(d, HEADLINE, "hottest_node")][f"rxn_at_{LV}"], Th is not None and Th < 100.0,
                        "" if p3[d][0] is None else p3[d][0]])
    sc_path = os.path.join(a.out, "stage3_scorecard.json")
    sc = json.load(open(sc_path)) if os.path.exists(sc_path) else {}
    sc.update({k: v for k, v in score.items() if k in ("P1", "P2", "P3", "P6")})
    sc.setdefault("P4", "scored in Stage 3b"); sc.setdefault("P5", "scored in Stage 3b")
    sc["predictions_commit"] = "2657aeece0c2137af47aaae4abd9319bdd24ab40"
    json.dump(sc, open(sc_path, "w"), indent=1)
    print(json.dumps({k: sc[k] for k in ("P1", "P2", "P3", "P6")}, indent=1))
    print(json.dumps({"lead_headline": H["lead_s"], "only_hot": H["share_only_hottest_starts"], "sei": H["share_hottest_onset_sei"],
                      "no_onset": H["share_no_onset_anywhere"], "V4": outliers}, indent=1))
