#!/usr/bin/env python3
"""Stage 6 checks V1 and V2 (DECISIONS.md D56), written apart from the code they check.

V1  The Part A crossings of three runs, fixed before the predictions, recomputed by hand from the archived series:
    each history is scanned sample by sample in a plain loop, the two samples that bracket 150 C are printed, and the
    crossing is interpolated with the formula written out here; the peaks are taken as the largest stored sample.
    Compared with results/stage6_crossings.csv.
V2  The matched trigger re-derived by separate code: the Databank's energies read again from
    inputs/databank/databank_m50_used.csv with the csv module alone; the release durations from the table values
    recorded in DECISIONS.md D52, typed here; and cell 1's peak from an implementation of the lumped pair written
    here from the equations of D38 (the contact conductance by numerical quadrature of D36's local conductance, the
    view factor from its formula), with the same explicit Euler step and, as a reference for the time step, a
    fourth-order Runge-Kutta step ten times smaller. The selection and the peak-matched energy are then made again
    and compared with results/stage6_trigger.json.
Usage: python3 stage6_checks.py v1 | v2 [--res DIR]
"""
import argparse, csv, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXT = os.path.join(HERE, "..", "external", "m50-two-cell-pilot", "src")
V1_RUNS = ("grid_mean_series_hcentral_gcentral_tau10", "grid_mean_parallel_hhigh_ghigh_tau30",
           "grid_mean_series_hlow_glow_tau30")
LEVEL_K = 150.0 + 273.15


# ------------------------------------------------------------------------------------------------ V1
def by_hand(t, y):
    """First sample at or above 150 C, the one before it, and the crossing between them."""
    for i in range(len(y)):
        if y[i] >= LEVEL_K:
            if i == 0:
                return {"i": 0, "t_cross_s": float(t[0])}
            t0, t1, y0, y1 = float(t[i - 1]), float(t[i]), float(y[i - 1]), float(y[i])
            tc = t0 + (LEVEL_K - y0) * (t1 - t0) / (y1 - y0)
            return {"i": i, "before": [t0, y0 - 273.15], "after": [t1, y1 - 273.15], "t_cross_s": tc}
    return None


def v1(res):
    import numpy as np
    rows = {r["id"]: r for r in csv.DictReader(open(os.path.join(res, "stage6_crossings.csv")))}
    out, worst = {}, 0.0
    for rid in V1_RUNS:
        z = np.load(os.path.join(res, "v12_series", rid + ".npz"))
        rec = json.load(open(os.path.join(res, "v12_runs", rid + ".json")))
        hist = {"hot": (z["t"], z["Tmax"]), "mean": (z["t"], z["Tmean"]), "away": (z["probe_t"], z["probe_away"]),
                "toward": (z["probe_t"], z["probe_toward"]), "lumped": (z["t_lumped"], z["T_lumped"])}
        d = {}
        for c, (t, y) in hist.items():
            h = by_hand(list(t), list(y))
            big = max(range(len(y)), key=lambda i: y[i])
            mine = None if h is None else h["t_cross_s"]
            theirs = rows[rid][f"{c}_t_cross_s"]
            theirs = None if theirs in ("", "None") else float(theirs)
            diff = None if (mine is None or theirs is None) else abs(mine - theirs)
            agree = (mine is None and theirs is None) or (diff is not None and diff < 1e-9)
            worst = max(worst, diff or 0.0) if agree else float("inf")
            d[c] = {"by_hand": h, "csv_t_cross_s": theirs, "agree": agree, "abs_diff_s": diff,
                    "largest_stored_C": float(y[big]) - 273.15, "at_s": float(t[big]),
                    "csv_peak_C": float(rows[rid][f"{c}_peak_C"])}
        d["record_peaks_C"] = {"hot": rec["resolved"]["peak_hottest_C"], "mean": rec["resolved"]["peak_mean_C"],
                               "away": rec["resolved"]["probe_peak"]["away"]["T_C"],
                               "toward": rec["resolved"]["probe_peak"]["toward"]["T_C"],
                               "lumped": rec["lumped"]["peak_C"]}
        out[rid] = d
    ok = all(v["agree"] for d in out.values() for k, v in d.items() if k != "record_peaks_C")
    res_ = {"runs": out, "pass": ok, "largest_difference_s": worst}
    json.dump(res_, open(os.path.join(res, "stage6_v1.json"), "w"), indent=1, default=float)
    print("V1", "pass" if ok else "FAIL", "largest difference", worst)
    return res_


# ------------------------------------------------------------------------------------------------ V2
def median(v):
    v = sorted(v)
    n = len(v)
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2


class Pair:
    """The lumped pair of D38 with the Stage 5 paths, written from its equations."""

    def __init__(self, h_c, g_tabs):
        sys.path.insert(0, EXT)
        import lumped_two_cell as LP                  # constants only (inputs): geometry, properties, ambient
        from scipy.integrate import quad
        self.LP = LP
        R = LP.D_CELL / 2
        sector = math.pi / 4                           # the 45 degree half-sector facing cell 1 (D36 (3))
        h = lambda th: LP.K_AIR / (2 * R * (1 - math.cos(th)) + LP.K_AIR / h_c)
        g_len = quad(h, -sector, sector, epsabs=0, epsrel=1e-13, limit=200)[0] * R
        self.G = g_len * LP.L_CELL + g_tabs             # contact and wedge, plus the tabs
        self.F = (math.pi / 2 - 1) / math.pi           # two cylinders in contact
        self.A_lat = math.pi * LP.D_CELL * LP.L_CELL
        self.A_cell = self.A_lat + 2 * math.pi * R ** 2
        self.A_conv = self.A_cell - 0.25 * self.A_lat
        self.A_rad = self.A_cell - LP.EPS * self.F * self.A_lat
        self.C = LP.M_CELL * LP.CP_CELL
        self.Ta = 25.0 + 273.15

    def rhs(self, t, T1, T2, e, tau):
        LP = self.LP
        if 0 <= t <= tau:
            q = (2 * e / tau) * (t / (tau / 2) if t <= tau / 2 else (tau - t) / (tau / 2))
        else:
            q = 0.0
        loss = lambda T: LP.H_CONV * self.A_conv * (T - self.Ta) + LP.EPS * LP.SIGMA * self.A_rad * (T ** 4 - self.Ta ** 4)
        q12 = self.G * (T1 - T2) + LP.EPS ** 2 * LP.SIGMA * self.F * self.A_lat * (T1 ** 4 - T2 ** 4)
        return (q - loss(T1) - q12) / self.C, (q12 - loss(T2)) / self.C

    def peak_euler(self, e, tau, dt=0.01, t_end=None):
        t_end = 3 * tau + 30 if t_end is None else t_end   # cell 1 peaks at the end of its release
        T1 = T2 = self.Ta
        best, t_best = T1, 0.0
        for n in range(int(round(t_end / dt))):
            d1, d2 = self.rhs(n * dt, T1, T2, e, tau)
            T1, T2 = T1 + dt * d1, T2 + dt * d2
            if T1 > best:
                best, t_best = T1, (n + 1) * dt
        return best - 273.15, t_best

    def peak_rk4(self, e, tau, dt=0.001, t_end=None):
        t_end = 3 * tau + 30 if t_end is None else t_end
        T1 = T2 = self.Ta
        best = T1
        for n in range(int(round(t_end / dt))):
            t = n * dt
            a1, a2 = self.rhs(t, T1, T2, e, tau)
            b1, b2 = self.rhs(t + dt / 2, T1 + dt / 2 * a1, T2 + dt / 2 * a2, e, tau)
            c1, c2 = self.rhs(t + dt / 2, T1 + dt / 2 * b1, T2 + dt / 2 * b2, e, tau)
            d1, d2 = self.rhs(t + dt, T1 + dt * c1, T2 + dt * c2, e, tau)
            T1 += dt / 6 * (a1 + 2 * b1 + 2 * c1 + d1)
            T2 += dt / 6 * (a2 + 2 * b2 + 2 * c2 + d2)
            best = max(best, T1)
        return best - 273.15


def v2(res):
    trig = json.load(open(os.path.join(res, "stage6_trigger.json")))
    # energies, read again
    rows = [r for r in csv.DictReader(open(os.path.join(HERE, "..", "inputs", "databank", "databank_m50_used.csv")))
            if r["Trigger-Mechanism"] == "Nail"]
    totals = [1e3 * float(r["Corrected-Total-Energy-Yield-kJ"]) for r in rows]
    body = max(1e3 * float(r["Energy-Fraction-Cell-Body-kJ"]) for r in rows)
    E = {"n_rows": len(rows), "body_max_J": body, "total_median_J": median(totals), "total_min_J": min(totals),
         "total_max_J": max(totals)}
    # durations, from the values recorded in D52 (Table 3 maxima; supplementary Figure 10 rates; 25 C start)
    dur = sorted([(630.0 - 25.0) / 23.97, (686.0 - 25.0) / 37.70])
    D = {"durations_s": [dur[0], median(dur), dur[1]]}
    L = trig["levels"]
    cmp_inputs = {"total_median_J": abs(E["total_median_J"] - L["E_total_J"]),
                  "total_min_J": abs(E["total_min_J"] - L["E_bracket_J"][0]),
                  "total_max_J": abs(E["total_max_J"] - L["E_bracket_J"][1]),
                  "body_max_J_vs_stage5": abs(E["body_max_J"] - L["E_body_J"]),
                  "durations_s": max(abs(a - b) for a, b in zip(D["durations_s"], L["tau_s"]))}
    # cell 1's peak: the same rows as the trigger step, recomputed
    pair = {c: Pair(2000.0, 0.0068 * (1 if c == "series" else 2)) for c in ("series", "parallel")}
    lo, hi = 164.0, 832.0
    recomputed, worst_euler, worst_rk4 = [], 0.0, 0.0
    for r in trig["rows"]:
        T1, t1 = pair[r["connection"]].peak_euler(r["E_J"], r["tau_s"])
        T1_rk4 = pair[r["connection"]].peak_rk4(r["E_J"], r["tau_s"])
        recomputed.append({"energy": r["energy"], "tau_s": r["tau_s"], "connection": r["connection"],
                           "T1max_C_trigger_step": r["T1max_C"], "T1max_C_here": T1, "T1max_C_rk4": T1_rk4,
                           "inside_here": lo <= T1 <= hi, "inside_trigger_step": r["inside_measured_range"]})
        worst_euler = max(worst_euler, abs(T1 - r["T1max_C"]))
        worst_rk4 = max(worst_rk4, abs(T1_rk4 - r["T1max_C"]))
    same_selection = all(x["inside_here"] == x["inside_trigger_step"] for x in recomputed)
    # the peak-matched energy (exploratory), by bisection here
    pk = trig["peak_matched_exploratory"]
    e_lo, e_hi = E["body_max_J"], E["total_median_J"]
    for _ in range(100):
        mid = (e_lo + e_hi) / 2
        T1 = pair["series"].peak_euler(mid, D["durations_s"][1])[0]
        if abs(T1 - 704.5) <= 0.01:
            break
        e_lo, e_hi = (mid, e_hi) if T1 < 704.5 else (e_lo, mid)
    peak = {"E_J_here": mid, "T1max_C_here": T1, "E_J_trigger_step": pk.get("E_J"),
            "abs_diff_J": abs(mid - pk["E_J"]) if pk.get("E_J") else None}
    exact = [v for k, v in cmp_inputs.items() if k != "body_max_J_vs_stage5"]
    ok = (max(exact) < 1e-6 and cmp_inputs["body_max_J_vs_stage5"] < 0.05 and same_selection and worst_euler < 1e-6
          and peak["abs_diff_J"] is not None and peak["abs_diff_J"] < 5.0)
    out = {"energies": E, "durations": D, "input_differences": cmp_inputs, "cell1_peaks": recomputed,
           "largest_peak_difference_K_euler": worst_euler, "largest_peak_difference_K_rk4_dt_over_10": worst_rk4,
           "same_selection": same_selection, "peak_matched": peak, "pass": ok,
           "note": "the stage 5 energy is 33,222.9 J, the Databank's 33,222.91 J as the two-cell study recorded it"}
    json.dump(out, open(os.path.join(res, "stage6_v2.json"), "w"), indent=1, default=float)
    print("V2", "pass" if ok else "FAIL", json.dumps({"inputs": cmp_inputs, "euler_K": worst_euler, "rk4_K": worst_rk4,
                                                       "selection": same_selection, "peak": peak}, default=float))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["v1", "v2"])
    ap.add_argument("--res", default=os.path.join(HERE, "..", "results"))
    a = ap.parse_args()
    v1(a.res) if a.cmd == "v1" else v2(a.res)
