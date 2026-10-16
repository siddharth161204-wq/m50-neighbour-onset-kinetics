#!/usr/bin/env python3
"""Stage 4 scoring (predictions_v11.md; DECISIONS.md D29): main-effect shares of the three kinetic submodels, the
rank-based repeat, early SEI starts by submodel, the central-half restriction, and P1 to P5.

Reads results/v11_onsets.csv (v11_sensitivity.py merge), the joint draws of Stage 3a (results/stage3a_onsets.csv,
unchanged), the draw indices (results/stage3_draw_indices.csv) and the publisher's particle files (for the distances;
inputs/kinetics/supplementary, not redistributed). Every draw stays in every metric.

Writes results/v11_sensitivity.csv (one row per case, run type and draw), results/v11_sensitivity.json (every metric)
and results/v11_scorecard.json.

Usage: python3 v11_score.py --out ../results
"""
import argparse, csv, json, os
import numpy as np
import bcrnn
import stage3_draws as S

CASES = {"500 mW/K": "two_E33223_tau30_G0.5", "100 mW/K": "two_E33223_tau30_G0.1"}
HEADLINE = "two_E33223_tau30_G0.5"
GROUPS = {"an_ele": "An_Ele.csv", "ncm811": "NCM811.csv", "separator": "Separator.csv"}
LABEL = {"an_ele": "anode-electrolyte (SEI)", "ncm811": "NCM811 cathode", "separator": "separator"}
OUTPUTS = ("hottest_onset_s", "lumped_onset_s", "lead_s", "hottest_onset_T_C")
N, LV, TIE, B, SEED = 200, "0.15Kpm", 0.01, 2000, 20261016
PREDICTIONS_COMMIT = "a975f20c63cd823d932983ddf285b5782b0ca31c"
AN_ELE_REACTIONS = {"elec_evap": 0, "elec_decomp": 1, "an_ele": 2, "an_bin": 3, "sei_decomp": 4, "IV": 6, "V": 8}


def num(v):
    return None if v in ("", "None", None) else float(v)


# ------------------------------------------------------------------ loading

def load_runs(out):
    """runs[(source, case, draw)] = dict of the four outputs and the onset reactions; source is a group or 'joint'."""
    raw = {}
    for r in csv.DictReader(open(os.path.join(out, "v11_onsets.csv"))):
        raw[(r["group"], r["case"], int(r["draw"]), r["history"])] = r
    for r in csv.DictReader(open(os.path.join(out, "stage3a_onsets.csv"))):
        if r["case"] in CASES.values() and r["history"] in ("hottest_node", "lumped"):
            raw[("joint", r["case"], int(r["draw"]), r["history"])] = r
    runs = {}
    for src in list(GROUPS) + ["joint"]:
        for case in CASES.values():
            for d in range(1, N + 1):
                h, l = raw[(src, case, d, "hottest_node")], raw[(src, case, d, "lumped")]
                th, tl = num(h[f"t_{LV}_s"]), num(l[f"t_{LV}_s"])
                runs[(src, case, d)] = {
                    "hottest_onset_s": th, "lumped_onset_s": tl,
                    "lead_s": None if th is None or tl is None else tl - th,
                    "lead_rank_value": None if th is None else (np.inf if tl is None else tl - th),
                    "hottest_onset_T_C": num(h[f"T_at_{LV}_C"]),
                    "hottest_onset_reaction": h[f"rxn_at_{LV}"] or None, "lumped_onset_reaction": l[f"rxn_at_{LV}"] or None}
    return runs


def draw_columns(out):
    cols = {}
    for r in csv.DictReader(open(os.path.join(out, "stage3_draw_indices.csv"))):
        cols[int(r["draw"])] = {"An_Ele.csv": int(r["an_ele_column"]), "NCM811.csv": int(r["ncm811_column"]),
                                "Separator.csv": int(r["separator_column"])}
    return cols


def mean_rows():
    rec = json.load(open(bcrnn.MODEL_JSON))
    return {"An_Ele.csv": np.array(rec["an_ele_rows_mean"], float), "NCM811.csv": np.array(rec["ncm811_rows_mean"], float),
            "Separator.csv": np.array(rec["separator_rows_mean"], float)}


# ------------------------------------------------------------------ distances and the central half

def distances(P, M, f, rows=None):
    """Standardized Euclidean distance of each particle (1-based column) from the posterior mean, over the varying rows
    of the file (or over the given rows, kept only where they vary)."""
    X = P[f]
    sd = X.std(axis=1)
    use = np.where(sd > 0)[0] if rows is None else np.array([r for r in rows if sd[r] > 0], int)
    z = (X[use, :] - M[f][use, None]) / sd[use, None]
    return {j + 1: float(v) for j, v in enumerate(np.sqrt((z ** 2).sum(axis=0)))}, int(use.size)


def central_half(dist):
    """The half of the particles with the smallest distances; ties by column index."""
    order = sorted(dist, key=lambda c: (dist[c], c))
    return set(order[: len(order) // 2])


def reaction_rows(f):
    """Row indices (0-based) of each reaction's parameters in a file."""
    if f == "An_Ele.csv":
        out = {}
        for name, col in AN_ELE_REACTIONS.items():
            out[name] = [10 * s + col for s in range(9)] + [90 + 10 * s + col for s in range(9)] + [180 + col, 190 + col, 200 + col, 210 + col]
        return out
    if f == "NCM811.csv":
        return {f"cat{k + 1}": [k, 3 + k, 6 + k, 9 + k, 12 + k] + ([15 + k] if k < 2 else []) for k in range(3)}
    return {"sep_melt": list(range(6))}


# ------------------------------------------------------------------ statistics

def var1(x):
    x = np.array([v for v in x if v is not None], float)
    return (float(x.var(ddof=1)) if x.size > 1 else None), int(x.size)


def lead_width(leads_rank):
    """D26 (5): leads over draws whose hottest node starts, a lumped node that does not start ranking as the longest."""
    v = np.array([x for x in leads_rank if x is not None], float)
    if v.size == 0:
        return {"n": 0, "p2.5": None, "p97.5": None, "width_s": None}
    p_lo, p_hi = float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))
    fin = lambda p: p if np.isfinite(p) else None
    return {"n": int(v.size), "n_lumped_not_started": int(np.isinf(v).sum()), "p2.5": fin(p_lo), "p97.5": fin(p_hi),
            "width_s": (p_hi - p_lo) if np.isfinite(p_hi) and np.isfinite(p_lo) else None}


def round_sig(x, sig=4):
    if x is None or not np.isfinite(x) or x == 0:
        return x
    return float(f"{x:.{sig - 1}e}")


def rankdata(a):
    """Average ranks (1-based), ties sharing their mean rank; +inf ranks after every finite value."""
    a = np.asarray(a, float)
    order = np.argsort(a, kind="mergesort")
    ranks = np.empty(a.size, float)
    s = a[order]
    i = 0
    while i < a.size:
        j = i
        while j + 1 < a.size and s[j + 1] == s[i]:
            j += 1
        ranks[order[i:j + 1]] = 0.5 * (i + j) + 1.0
        i = j + 1
    return ranks


def spearman_share(g, j):
    """Squared Spearman correlation between paired values (None = left out of the pair, +inf = after every onset),
    each rounded to 4 significant digits first; 0 if the grouped values take one value in every draw."""
    pairs = [(round_sig(a), round_sig(b)) for a, b in zip(g, j) if a is not None and b is not None]
    if len(pairs) < 3:
        return {"n_pairs": len(pairs), "rho": None, "rank_share": None}
    ga, ja = np.array([p[0] for p in pairs], float), np.array([p[1] for p in pairs], float)
    if np.all(ga == ga[0]):
        return {"n_pairs": len(pairs), "rho": None, "rank_share": 0.0, "grouped_constant": True}
    rg, rj = rankdata(ga), rankdata(ja)
    rho = float(np.corrcoef(rg, rj)[0, 1])
    return {"n_pairs": len(pairs), "rho": rho, "rank_share": rho ** 2}


def ordering(shares):
    """Pairwise relations with ties below TIE; and a readable ranking."""
    names = list(shares)
    rel = {}
    for a in range(len(names)):
        for b in range(a + 1, len(names)):
            x, y = names[a], names[b]
            dv = shares[x] - shares[y]
            rel[f"{x}|{y}"] = "tie" if abs(dv) < TIE else (">" if dv > 0 else "<")
    srt = sorted(names, key=lambda n: -shares[n])
    txt = srt[0]
    for p, q in zip(srt, srt[1:]):
        txt += (" = " if abs(shares[p] - shares[q]) < TIE else " > ") + q
    return rel, txt


def orders_agree(r1, r2):
    return all(not (a != "tie" and b != "tie" and a != b) for a, b in ((r1[k], r2[k]) for k in r1))


def pct_interval(x):
    x = np.array([v for v in x if v is not None and np.isfinite(v)], float)
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))] if x.size else None


# ------------------------------------------------------------------ main

def main(out):
    runs = load_runs(out)
    cols = draw_columns(out)
    P, M = S.load_particles(), mean_rows()
    D = list(range(1, N + 1))
    boot = np.random.default_rng(SEED).integers(0, N, size=(B, N))     # paired resamples of the draw numbers (0-based)

    def series(src, case, y):
        return [runs[(src, case, d)][y] for d in D]

    res = {"predictions_commit": PREDICTIONS_COMMIT, "n_draws": N, "cases": CASES, "groups": LABEL,
           "definitions": "predictions_v11.md; DECISIONS.md D29", "shares": {}, "rank_shares": {}, "early_sei": {},
           "onset_reactions": {}, "orderings": {}, "restriction": {},
           "failed_runs": "none: all 600 grouped draws completed in one pass (results/v11_run.log); the harness would have stopped on a failure (DECISIONS.md D32)"}

    # main-effect shares, with paired bootstrap intervals
    for cl, case in CASES.items():
        res["shares"][cl], res["rank_shares"][cl], res["orderings"][cl] = {}, {}, {}
        for y in OUTPUTS:
            vj, nj = var1(series("joint", case, y))
            entry = {"joint_variance": vj, "joint_n": nj, "joint_n_without": N - nj, "by_group": {}}
            boot_shares = {g: [] for g in GROUPS}
            for g in GROUPS:
                vg, ng = var1(series(g, case, y))
                entry["by_group"][g] = {"variance": vg, "n": ng, "n_without": N - ng, "share": vg / vj}
            sums = []
            yj = np.array([np.nan if v is None else v for v in series("joint", case, y)], float)
            yg = {g: np.array([np.nan if v is None else v for v in series(g, case, y)], float) for g in GROUPS}
            for b in range(B):
                idx = boot[b]
                jj = yj[idx]; jj = jj[~np.isnan(jj)]
                vjb = jj.var(ddof=1)
                s_b = 0.0
                for g in GROUPS:
                    gg = yg[g][idx]; gg = gg[~np.isnan(gg)]
                    sh = gg.var(ddof=1) / vjb
                    boot_shares[g].append(sh); s_b += sh
                sums.append(s_b)
            for g in GROUPS:
                entry["by_group"][g]["share_95_bootstrap"] = pct_interval(boot_shares[g])
            entry["sum"] = sum(entry["by_group"][g]["share"] for g in GROUPS)
            entry["sum_95_bootstrap"] = pct_interval(sums)
            res["shares"][cl][y] = entry
            # rank-based repeat
            rk = {}
            for g in GROUPS:
                if y == "lead_s":
                    gv, jv = series(g, case, "lead_rank_value"), series("joint", case, "lead_rank_value")
                elif y in ("hottest_onset_s", "lumped_onset_s"):
                    gv = [np.inf if v is None else v for v in series(g, case, y)]
                    jv = [np.inf if v is None else v for v in series("joint", case, y)]
                else:
                    gv, jv = series(g, case, y), series("joint", case, y)
                rk[g] = spearman_share(gv, jv)
            res["rank_shares"][cl][y] = {**rk, "sum": sum(rk[g]["rank_share"] for g in GROUPS if rk[g]["rank_share"] is not None)}
            rel_v, txt_v = ordering({g: entry["by_group"][g]["share"] for g in GROUPS})
            rel_r, txt_r = ordering({g: rk[g]["rank_share"] for g in GROUPS})
            res["orderings"][cl][y] = {"by_variance_share": txt_v, "by_rank_share": txt_r, "pairs_variance": rel_v,
                                       "pairs_rank": rel_r, "rank_agrees_with_variance": orders_agree(rel_v, rel_r)}
        # early SEI starts and onset reactions
        res["early_sei"][cl], res["onset_reactions"][cl] = {}, {}
        for src in list(GROUPS) + ["joint"]:
            early = [runs[(src, case, d)]["hottest_onset_T_C"] is not None and runs[(src, case, d)]["hottest_onset_T_C"] < 100.0
                     and runs[(src, case, d)]["hottest_onset_reaction"] == "sei_decomp" for d in D]
            res["early_sei"][cl][src] = {"n": int(sum(early)), "share": sum(early) / N}
            rx = [runs[(src, case, d)]["hottest_onset_reaction"] or "none" for d in D]
            rl = [runs[(src, case, d)]["lumped_onset_reaction"] or "none" for d in D]
            res["onset_reactions"][cl][src] = {"hottest_node": {r: rx.count(r) for r in sorted(set(rx))},
                                               "lumped": {r: rl.count(r) for r in sorted(set(rl))}}

    # dominant submodel and the central-half restriction
    sh_lead = {g: res["shares"]["500 mW/K"]["lead_s"]["by_group"][g]["share"] for g in GROUPS}
    dom = max(sh_lead, key=sh_lead.get)
    res["dominant_submodel"] = dom
    dist_all = {}
    for g, f in GROUPS.items():
        dist, nrows = distances(P, M, f)
        dist_all[f] = dist
        half = central_half(dist)
        entry = {"file": f, "rows_used": nrows, "n_particles": len(dist), "central_half_size": len(half), "by_case": {}}
        for cl, case in CASES.items():
            lead_j = series("joint", case, "lead_rank_value")
            inside = [cols[d][f] in half for d in D]
            full = lead_width(lead_j)
            restr = lead_width([v for v, k in zip(lead_j, inside) if k])
            e = {"full": full, "restricted": restr, "n_restricted_draws": int(sum(inside)),
                 "narrowing": (1.0 - restr["width_s"] / full["width_s"]) if (full["width_s"] and restr["width_s"] is not None) else None}
            # paired bootstrap of the narrowing
            lj = np.array([np.nan if v is None else v for v in lead_j], float)
            ins = np.array(inside)
            nb = []
            for b in range(B):
                idx = boot[b]
                v = lj[idx]; k = ins[idx]
                ok = ~np.isnan(v)
                fw = lead_width(list(v[ok])); rw = lead_width(list(v[ok & k]))
                nb.append(None if not fw["width_s"] or rw["width_s"] is None else 1.0 - rw["width_s"] / fw["width_s"])
            e["narrowing_95_bootstrap"] = pct_interval(nb)
            e["bootstrap_resamples_unbounded"] = int(sum(x is None for x in nb))
            if e["bootstrap_resamples_unbounded"]:
                e["narrowing_95_bootstrap_note"] = "conditional: over the resamples in which both widths are bounded only (DECISIONS.md D32)"
            if g == dom:
                lead_g = series(g, case, "lead_rank_value")
                fg, rg = lead_width(lead_g), lead_width([v for v, k in zip(lead_g, inside) if k])
                e["within_own_grouped_runs"] = {"full": fg, "restricted": rg,
                                                "narrowing": (1.0 - rg["width_s"] / fg["width_s"]) if (fg["width_s"] and rg["width_s"] is not None) else None}
                per_rx, boot_rx = {}, {}
                for rxn, rws in reaction_rows(f).items():
                    dr, nr = distances(P, M, f, rws)
                    hr = central_half(dr)
                    ins_r = [cols[d][f] in hr for d in D]
                    rw = lead_width([v for v, k in zip(lead_j, ins_r) if k])
                    per_rx[rxn] = {"rows_used": nr, "n_restricted_draws": int(sum(ins_r)), "restricted": rw,
                                   "narrowing": (1.0 - rw["width_s"] / full["width_s"]) if (full["width_s"] and rw["width_s"] is not None) else None}
                    # paired bootstrap, the same resamples as above (reported, not scored)
                    ir = np.array(ins_r)
                    nbr = []
                    for b in range(B):
                        idx = boot[b]
                        v = lj[idx]; k = ir[idx]; ok = ~np.isnan(v)
                        fw = lead_width(list(v[ok])); rw_b = lead_width(list(v[ok & k]))
                        nbr.append(None if not fw["width_s"] or rw_b["width_s"] is None else 1.0 - rw_b["width_s"] / fw["width_s"])
                    per_rx[rxn]["narrowing_95_bootstrap"] = pct_interval(nbr)
                    boot_rx[rxn] = nbr
                # how often each reaction's half gives the largest narrowing over the resamples
                if cl == "500 mW/K":
                    names_rx = list(boot_rx)
                    wins = {n: 0 for n in names_rx}
                    for b in range(B):
                        vals = {n: boot_rx[n][b] for n in names_rx if boot_rx[n][b] is not None}
                        if vals:
                            wins[max(vals, key=vals.get)] += 1
                    e["per_reaction_share_of_resamples_largest"] = {n: wins[n] / B for n in names_rx}
                e["per_reaction_restriction"] = per_rx
            entry["by_case"][cl] = e
        res["restriction"][g] = entry

    # exploratory, not pre-registered (DECISIONS.md D30, written after the results): why the restriction narrows the width
    # so little. The joint leads at the headline case split into two modes at the largest gap of their sorted values
    # (as Stage 3 reported them, src/stage3_numbers.py); for each restricted set, the share of its draws in the long-lead
    # mode and the 2.5 to 97.5 % width within the short-lead mode alone.
    lead_h = np.array(series("joint", HEADLINE, "lead_s"), float)
    srt = np.sort(lead_h); kgap = int(np.argmax(np.diff(srt))); cut = 0.5 * (srt[kgap] + srt[kgap + 1])
    T_h = np.array(series("joint", HEADLINE, "hottest_onset_T_C"), float)
    rx_h = [runs[("joint", HEADLINE, d)]["hottest_onset_reaction"] for d in D]

    def mode_summary(mask):
        v, m2 = lead_h[mask], lead_h[mask] > cut
        return {"n": int(mask.sum()), "n_long_lead": int(m2.sum()), "share_long_lead": float(m2.mean()),
                "n_cathode_starts": int(sum(1 for i in np.where(mask)[0] if rx_h[i] == "cat1")),
                "p2.5_s": float(np.percentile(v, 2.5)), "p97.5_s": float(np.percentile(v, 97.5)),
                "short_mode_width_s": float(np.ptp(np.percentile(v[~m2], [2.5, 97.5])))}
    expl = {"note": "exploratory, not pre-registered; written after the Stage 4 results (DECISIONS.md D30)",
            "mode_cut_s": cut, "gap_s": [float(srt[kgap]), float(srt[kgap + 1])],
            "short_mode_max_onset_T_C": float(T_h[lead_h < cut].max()), "long_mode_min_onset_T_C": float(T_h[lead_h > cut].min()),
            "sets": {"all joint draws": mode_summary(np.ones(N, bool))}}
    for g, f in GROUPS.items():
        hf = central_half(dist_all[f]) if f in dist_all else None
        expl["sets"][f"central half, {g}"] = mode_summary(np.array([cols[d][f] in hf for d in D]))
    for rxn, rws in reaction_rows(GROUPS[dom]).items():
        hr = central_half(distances(P, M, GROUPS[dom], rws)[0])
        expl["sets"][f"central half, {dom}, {rxn} rows"] = mode_summary(np.array([cols[d][GROUPS[dom]] in hr for d in D]))
    # the half of the anode-electrolyte particles whose fresh-SEI heat release at 108.4 C (the posterior-mean model's onset
    # temperature in every Stage 1 history) lies closest to the posterior mean's: ln(dH w k(T) 0.15^n)
    T_ref, c_sei = 108.4 + 273.15, bcrnn.C0[bcrnn.SPECIES.index("sei")]
    Aw = P["An_Ele.csv"]; col = AN_ELE_REACTIONS["sei_decomp"]

    def lnq_sei(rows):
        lnA, Ea, b, dH, n = rows[180 + col], rows[190 + col] * 1e5, rows[200 + col], rows[210 + col], rows[10 * 4 + col]
        return (np.log(abs(dH) * 1e3 * bcrnn.M_SEI / bcrnn.M_REF_G) + lnA + b * np.log(T_ref) - Ea / (bcrnn.R_GAS * T_ref)
                + n * np.log(c_sei))
    lq = {j + 1: float(lnq_sei(Aw[:, j])) for j in range(Aw.shape[1])}
    lq0 = float(lnq_sei(M["An_Ele.csv"]))
    hq = set(sorted(lq, key=lambda c: (abs(lq[c] - lq0), c))[: len(lq) // 2])
    mq = np.array([cols[d]["An_Ele.csv"] in hq for d in D])
    wq = lead_width([v for v, k in zip(series("joint", HEADLINE, "lead_rank_value"), mq) if k])
    full_h = res["restriction"]["an_ele"]["by_case"]["500 mW/K"]["full"]
    lq_draw = np.array([lq[cols[d]["An_Ele.csv"]] for d in D])
    expl["sei_heat_release_half"] = {"definition": "half of the anode-electrolyte particles whose ln of the fresh SEI's heat release per unit cell mass at 108.4 C lies closest to the posterior-mean model's",
                                     "posterior_mean_lnq": lq0, "restricted": wq, "narrowing": 1.0 - wq["width_s"] / full_h["width_s"],
                                     "mode": mode_summary(mq),
                                     "spearman_lnq_vs_hottest_onset_T": float(np.corrcoef(rankdata(lq_draw), rankdata(T_h))[0, 1]),
                                     "spearman_lnq_vs_lead": float(np.corrcoef(rankdata(lq_draw), rankdata(lead_h))[0, 1])}
    # draw by draw: how each joint draw's mode and starting reaction compare with the dominant submodel's run of the
    # same draw (the other two submodels at their posterior mean)
    lead_dom = np.array(series(dom, HEADLINE, "lead_s"), float)
    rx_dom = [runs[(dom, HEADLINE, d)]["hottest_onset_reaction"] for d in D]
    trans = {}
    for i in range(N):
        k = (f"joint {rx_h[i]}, {'long' if lead_h[i] > cut else 'short'} lead -> {dom} run {rx_dom[i]}, "
             f"{'long' if lead_dom[i] > cut else 'short'} lead")
        trans[k] = trans.get(k, 0) + 1
    expl["joint_against_dominant_runs"] = {
        "transitions": dict(sorted(trans.items())),
        "n_long_to_short": int(sum((lead_h > cut) & (lead_dom <= cut))), "n_short_to_long": int(sum((lead_h <= cut) & (lead_dom > cut))),
        "n_long_joint": int((lead_h > cut).sum()), "n_long_dominant_runs": int((lead_dom > cut).sum()),
        "n_lead_within_0.01_s": int((np.abs(lead_dom - lead_h) < 0.01).sum()),
        "dominant_runs_cathode_start_T_C": [float(min(T for T, r in zip(series(dom, HEADLINE, "hottest_onset_T_C"), rx_dom) if r == "cat1")),
                                            float(max(T for T, r in zip(series(dom, HEADLINE, "hottest_onset_T_C"), rx_dom) if r == "cat1"))] if "cat1" in rx_dom else None,
        "joint_cathode_start_T_C": [float(T_h[[i for i in range(N) if rx_h[i] == "cat1"]].min()), float(T_h[[i for i in range(N) if rx_h[i] == "cat1"]].max())]}
    # the cathode and separator runs: how far they move the onsets from the posterior-mean model's
    expl["minor_runs_onset_ranges"] = {
        cl: {g: {y: [float(min(v for v in series(g, case, y) if v is not None)), float(max(v for v in series(g, case, y) if v is not None))]
                 for y in ("hottest_onset_s", "lumped_onset_s", "hottest_onset_T_C")} for g in GROUPS if g != dom}
        for cl, case in CASES.items()}
    res["exploratory"] = expl

    # scorecard
    H = "500 mW/K"
    s1 = res["shares"][H]["lead_s"]["by_group"]["an_ele"]["share"]
    s2 = res["shares"][H]["lead_s"]["sum"]
    p3c, p3s = res["early_sei"][H]["ncm811"]["share"], res["early_sei"][H]["separator"]["share"]
    p4 = res["restriction"][dom]["by_case"][H]["narrowing"]
    rel500, txt500 = ordering({g: res["shares"]["500 mW/K"]["lead_s"]["by_group"][g]["share"] for g in GROUPS})
    rel100, txt100 = ordering({g: res["shares"]["100 mW/K"]["lead_s"]["by_group"][g]["share"] for g in GROUPS})
    score = {
        "predictions_commit": PREDICTIONS_COMMIT,
        "P1": {"an_ele_share_of_lead_variance": s1, "threshold": "> 0.5", "brief_central": 0.65,
               "study_expectation": "held, by a wide margin", "held": s1 > 0.5},
        "P2": {"sum_of_shares_of_lead": s2, "threshold": "0.8 to 1.1", "study_expectation": "uncertain, no number",
               "held": 0.8 <= s2 <= 1.1},
        "P3": {"early_sei_share_ncm811_runs": p3c, "early_sei_share_separator_runs": p3s, "threshold": "each < 0.05",
               "an_ele_runs_share": res["early_sei"][H]["an_ele"]["share"], "joint_share": res["early_sei"][H]["joint"]["share"],
               "study_expectation": "held", "held": p3c < 0.05 and p3s < 0.05},
        "P4": {"dominant_submodel": dom, "narrowing": p4, "threshold": "> 0.40",
               "full_width_s": res["restriction"][dom]["by_case"][H]["full"]["width_s"],
               "restricted_width_s": res["restriction"][dom]["by_case"][H]["restricted"]["width_s"],
               "study_expectation": "may fail", "held": p4 is not None and p4 > 0.40},
        "P5": {"ordering_500": txt500, "ordering_100": txt100, "pairs_500": rel500, "pairs_100": rel100,
               "tie_rule": "shares closer than 0.01 are tied", "study_expectation": "held, if the anode-electrolyte file leads at 500 mW/K",
               "held": orders_agree(rel500, rel100)},
    }
    json.dump(res, open(os.path.join(out, "v11_sensitivity.json"), "w"), indent=1)
    json.dump(score, open(os.path.join(out, "v11_scorecard.json"), "w"), indent=1)

    # per-draw table; the per-reaction halves of the dominant file are added as columns (secondary, reported)
    rx_halves = {rxn: central_half(distances(P, M, GROUPS[dom], rws)[0]) for rxn, rws in reaction_rows(GROUPS[dom]).items()}
    with open(os.path.join(out, "v11_sensitivity.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["case", "run", "draw", "varied_file", "varied_column", "an_ele_column", "ncm811_column", "separator_column",
                    "hottest_onset_s", "lumped_onset_s", "lead_s", "hottest_onset_T_C", "hottest_onset_reaction",
                    "lumped_onset_reaction", "early_sei_start", "an_ele_distance", "ncm811_distance", "separator_distance",
                    "an_ele_in_central_half", "ncm811_in_central_half", "separator_in_central_half"]
                   + [f"{dom}_{rxn}_rows_in_central_half" for rxn in rx_halves])
        halves = {f: central_half(dist_all[f]) for f in dist_all}
        for cl, case in CASES.items():
            for src in ["joint"] + list(GROUPS):
                for d in D:
                    r = runs[(src, case, d)]
                    c = cols[d]
                    early = r["hottest_onset_T_C"] is not None and r["hottest_onset_T_C"] < 100.0 and r["hottest_onset_reaction"] == "sei_decomp"
                    w.writerow([case, src, d, "" if src == "joint" else GROUPS[src], "" if src == "joint" else c[GROUPS[src]],
                                c["An_Ele.csv"], c["NCM811.csv"], c["Separator.csv"],
                                r["hottest_onset_s"], r["lumped_onset_s"], r["lead_s"], r["hottest_onset_T_C"],
                                r["hottest_onset_reaction"], r["lumped_onset_reaction"], early,
                                dist_all["An_Ele.csv"][c["An_Ele.csv"]], dist_all["NCM811.csv"][c["NCM811.csv"]],
                                dist_all["Separator.csv"][c["Separator.csv"]],
                                c["An_Ele.csv"] in halves["An_Ele.csv"], c["NCM811.csv"] in halves["NCM811.csv"],
                                c["Separator.csv"] in halves["Separator.csv"]]
                               + [c[GROUPS[dom]] in rx_halves[rxn] for rxn in rx_halves])
    return res, score


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="../results")
    a = ap.parse_args()
    res, score = main(a.out)
    print(json.dumps(score, indent=1))
