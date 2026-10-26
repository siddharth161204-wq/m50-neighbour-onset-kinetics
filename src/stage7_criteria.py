"""Stage 7, Part B: the ignition conditions read from a run's own histories (DECISIONS.md D67); no new physics.

For each run, the five clocks of Stage 6 (stage6_crossings.histories, unchanged): the hottest node (the hot spot), the
resolved mean, the face away from the trigger at mid-height (the thermocouple's position), the line of contact at
mid-height (reported apart) and the lumped neighbour. For each: its peak and the time of its peak (the record's, taken
at every step; the mean's time from the series), and its first crossing of 138.5, 150 and 255.7 C, interpolated
linearly between the two stored samples that bracket it (Stage 6's convention, D51 (3)). A resolved run stops at its
hottest node's 255.7 C crossing and a lumped run at its own (D35), each interpolated within the step: C1, C2 and C6
take those, the runs' own; their series may end before a stored sample reaches 255.7 C.

The criteria (the brief's Part B), each a predicted outcome (the clock reaches the level within 900 s) and a predicted
time (the crossing):
  C1  the hot spot reaches 255.7 C (Stage 5's condition), fresh SEI;
  C2  the lumped neighbour reaches 255.7 C, fresh SEI;
  C3  the lumped neighbour reaches 150 C (the paper's criterion), fresh SEI;
  C4  the hot spot reaches 138.5 C (the separator melts locally), fresh SEI;
  C5  the lumped neighbour reaches 138.5 C (the separator melts in the whole-cell model), fresh SEI;
  C6  C1 under the aged SEI;  C7  C4 under the aged SEI.
"""
import os
import sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage6_crossings as CR                # noqa: E402  (unchanged)
import stage7_inputs as IN                   # noqa: E402

K0 = 273.15
CLOCKS = ("hot", "mean", "away", "toward", "lumped")
LEVELS_C = {"sep": IN.LEVEL_SEP_C, "150": IN.LEVEL_150_C, "prop": IN.LEVEL_PROP_C}
CRITERIA = {                                  # set of the Part A run, clock, level, source of the crossing
    "C1": ("pertest", "hot", "prop", "stop"),
    "C2": ("pertest", "lumped", "prop", "stop"),
    "C3": ("pertest", "lumped", "150", "series"),
    "C4": ("pertest", "hot", "sep", "series"),
    "C5": ("pertest", "lumped", "sep", "series"),
    "C6": ("aged", "hot", "prop", "stop"),
    "C7": ("aged", "hot", "sep", "series"),
}
CRITERIA_TEXT = {
    "C1": "hot spot reaches 255.7 C", "C2": "lumped neighbour reaches 255.7 C", "C3": "lumped neighbour reaches 150 C",
    "C4": "hot spot reaches 138.5 C", "C5": "lumped neighbour reaches 138.5 C",
    "C6": "hot spot reaches 255.7 C, aged SEI", "C7": "hot spot reaches 138.5 C, aged SEI"}


def quantities(rec, series):
    """Every clock's peak and time and its first crossing of each level, the runs' own stop crossings, and, for an
    event run, each clock's peak after the event."""
    pk = CR.record_peaks(rec)
    hs = CR.histories(series) if series is not None else None
    clocks = {}
    for c in CLOCKS:
        T, tp = pk[c]
        d = {"peak_C": float(T), "t_peak_s": None if tp is None else float(tp)}
        if hs is not None:
            t, y = hs[c]
            if c == "mean":
                d["t_peak_s"] = float(t[int(np.argmax(y))])
            for name, lv in LEVELS_C.items():
                d[f"t_{name}_s"] = CR.first_crossing(t, y, lv + K0)
        clocks[c] = d
    rr, ll = rec["resolved"], rec["lumped"]
    out = {"levels_C": dict(LEVELS_C), "clocks": clocks,
           "stop": {"hot_t_s": rr.get("t_prop_s"), "lumped_t_s": ll.get("t_prop_s"),
                    "resolved_t_end_s": rr["t_end_s"], "lumped_t_end_s": ll["t_end_s"]}}
    if rr.get("after_event") is not None:
        ae, la = rr["after_event"], ll["after_event"]
        t0 = rr["event"]["t0_s"]
        aft = {"t_event_s": t0, "hot_C": ae["Tmax_C"], "t_hot_s": ae["t_Tmax_s"], "mean_C": ae["Tmean_C"],
               "t_mean_s": ae["t_Tmean_s"], "away_C": ae["probes"]["away"]["T_C"],
               "t_away_s": ae["probes"]["away"]["t_s"], "toward_C": ae["probes"]["toward"]["T_C"],
               "t_toward_s": ae["probes"]["toward"]["t_s"], "lumped_C": la["T_C"] if la else None,
               "t_lumped_s": la["t_s"] if la else None,
               "delivered_resolved_J": rr["event"]["delivered_J"], "delivered_lumped_J": ll["event"]["delivered_J"]}
        if hs is not None:
            for c in CLOCKS:
                t, y = hs[c]
                m = np.asarray(t) >= t0
                aft[f"{c}_t_prop_after_event_s"] = (CR.first_crossing(np.asarray(t)[m], np.asarray(y)[m],
                                                                      LEVELS_C["prop"] + K0) if m.any() else None)
        out["after_event"] = aft
    return out


def crossing(rec, criterion):
    """The predicted outcome (True if the clock reaches the level) and time of one criterion from a record."""
    set_, clock, level, source = CRITERIA[criterion]
    q = rec["stage7"]
    if source == "stop":
        t = q["stop"]["hot_t_s"] if clock == "hot" else q["stop"]["lumped_t_s"]
    else:
        t = q["clocks"][clock][f"t_{level}_s"]
    return (t is not None), t


def first_self_heating(series, sei0=None, level_K_per_min=0.15):
    """P5: the hot spot's first self-heating, Stage 1's quantity (src/onset_kinetics.py, unchanged): the kinetics
    integrated along the run's stored hottest-node history from the run's own initial state (fresh, or with the SEI's
    amount sei0), and the temperature of that history when the self-heating rate first reaches 0.15 K/min.
    Returns (time, temperature in C, the reaction then dominant) or (None, None, None)."""
    import onset_kinetics as OK
    import stage7_model as M
    c0 = None if sei0 is None else M.initial_state(1, sei0)[:, 0]
    tt, sh, Y, Tg, nsteps = OK.integrate_along(series["t"], series["Tmax"], c0=c0)
    tc = OK.first_crossing(tt, sh, level_K_per_min)
    if tc is None:
        return None, None, None
    k = int(np.searchsorted(tt, tc))
    return float(tc), float(np.interp(tc, tt, Tg) - K0), OK.dominant_reaction(Tg[min(k, Tg.size - 1)],
                                                                                Y[:, min(k, Tg.size - 1)])
