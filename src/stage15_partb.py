"""Stage 15, Part B: the registered list of three-dimensional runs and its rules (DECISIONS.md D175, D177), each
next run read from the records already made (`stage15_run.run_one` makes them).

  B1  For M50_PT_Exp4, PP_Exp2, SP_Exp3 and ST_Exp3, the 21.39 s triangular delivery: runs at A2's E*(C8) (the
      reactive cross-section's, results/stage15_cross_section.json, registered with the predictions) less 5 % and
      plus 5 %; then, while both have C8 or neither has, one further step of 10 % of A2's value on the side needed
      (down from the lowest with C8, or up from the highest without), until a run with C8 lies above one without.
      The bracket is (highest without C8, lowest with C8]; its midpoint is the run's E*(C8).
  B2  M50_PT_Exp4 with constant power over 240 s at f = 0.05 (6,209 J, the archived run that ended at 332 s) and at
      f = 0.046875 (5,821 J), each to C8 or 900 s.
  B3  (a) B1's M50_PT_Exp4 run at the upper end of its bracket, scored against the measured history by Stage 10's
      rule (the far-face node, 0 to 271.5 s, or to C8 where C8 comes first). (b) The pulse and the hold: f = 0.040625
      (5,045 J) over 21.39 s, then a constant power P from 21.39 s until the run ends; P from the cross-section's
      value on the 2.5 W grid (results/stage15_cross_section.json), then steps of 2.5 W (down while C8 comes more than
      10 s before 271.5 s, up while it comes more than 10 s after it or not at all) until C8 lies within 10 s of
      271.5 s, or the two neighbouring powers bracket 271.5 s (C8 earlier than 261.5 s at one, later than 281.5 s or
      absent at the other), or 16 runs are made.
  B4  M50_PT_Exp4 at f = 0.040625 over 21.39 s under Stage 11's kinetic draws by rank 5, 50, 151 and 196 (Stage 3's
      draws 188, 83, 40 and 184) and with the aged SEI; then, at the posterior mean, the rate laws evaluated at
      T + s: s = 5, 10, 15, ... K until C8 happens (at most 60 K), then the shift 2.5 K below the first with C8.
  V4  B1's M50_PT_Exp4 runs at the two ends of its bracket, each again with the mesh refined by 1.5 and with every
      step limit halved (`dt_scale` 0.5).
  A run that fails is made again at once; a run that fails twice is recorded as failed and stops its chain, which is
      then reported as stopped.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage15_inputs as IN              # noqa: E402
import stage15_run as R                  # noqa: E402

XS_OUT = os.path.join(IN.RES, "stage15_cross_section.json")
B3_MAX_RUNS = 16
B4_SHIFT_MAX = 60.0
F_B4 = 0.040625                          # 5,045 J for M50_PT_Exp4 (Stage 10's tri21_C2_hi)
B2_F = (0.05, 0.046875)


def _xs():
    return json.load(open(XS_OUT))


def a2_value(test, xs=None):
    xs = _xs() if xs is None else xs
    for r in xs["A2"]:
        if r["test"] == test and r["shape"] == "tri":
            return r["E_star_J"]
    raise KeyError(test)


def b3_start(xs=None):
    xs = _xs() if xs is None else xs
    return xs["B3_hold"]["P_start_W"]


def tri_f(test, E):
    return {"shape": "tri", "f": E / IN.e_e(test), "tau_s": IN.TAU_TRIGGER, "t0_s": 0.0}


# ------------------------------------------------------------------------------------------------ the specs
def b1_spec(test, step):
    """step: the run's position in units of 5 % of A2's value: -1 and +1 first, then -3, -5, ... or +3, +5, ..."""
    E = a2_value(test) * (1.0 + 0.05 * step)
    return R.spec(f"B1_{test[4:]}_s{step:+d}", test, [tri_f(test, E)], "B1", search=f"B1_{test}")


def b2_spec(f):
    return R.spec(f"B2_PT_Exp4_con240_f{f:.6f}", "M50_PT_Exp4",
                  [{"shape": "con", "f": f, "tau_s": 240.0, "t0_s": 0.0}], "B2")


def b3_spec(P):
    return R.spec(f"B3_PT_Exp4_hold{P:.1f}W", "M50_PT_Exp4",
                  [{"shape": "tri", "f": F_B4, "tau_s": IN.TAU_TRIGGER, "t0_s": 0.0},
                   {"shape": "hold", "P_W": float(P), "t0_s": IN.TAU_TRIGGER}], "B3", search="B3")


def b4_spec(kin=None, sei0=None, shift=0.0):
    tag = (f"draw{kin}" if kin is not None else "") + ("aged" if sei0 is not None else "") + \
          (f"shift{shift:.1f}K" if shift else "")
    return R.spec(f"B4_PT_Exp4_{tag}", "M50_PT_Exp4",
                  [{"shape": "tri", "f": F_B4, "tau_s": IN.TAU_TRIGGER, "t0_s": 0.0}], "B4",
                  kin=kin if kin is not None else "mean", sei0=sei0, shift_K=shift,
                  search="B4_shift" if shift else None)


def v4_spec(base, variant):
    s = dict(base)
    if variant == "refine":
        s.update({"id": base["id"] + "_r1.5", "refine": 1.5, "kind": "V4"})
    else:
        s.update({"id": base["id"] + "_dt0.5", "dt_scale": 0.5, "kind": "V4"})
    return s


# ------------------------------------------------------------------------------------------------ the records
def load(recs_dir=IN.RUNS):
    out = {}
    if not os.path.isdir(recs_dir):
        return out
    for fn in os.listdir(recs_dir):
        if fn.endswith(".json"):
            try:
                r = json.load(open(os.path.join(recs_dir, fn)))
            except Exception:
                continue
            out[r["id"]] = r
    return out


def c8(rec):
    return bool(rec and not rec.get("failed") and rec["resolved"]["C8"])


def failed(rec):
    """A record whose run failed at both attempts (`stage15_run.work_list`): its chain stops there and is reported."""
    return bool(rec and rec.get("failed"))


def b1_state(test, recs):
    """(status, pending specs, bracket)."""
    have = {}
    for step in range(-19, 40, 2):
        sp = b1_spec(test, step)
        if sp["id"] in recs:
            have[step] = recs[sp["id"]]
    if any(failed(r) for r in have.values()):
        return "failed", [], None
    need = [s for s in (-1, +1) if s not in have]
    if need:
        return "running", [b1_spec(test, s) for s in need], None
    yes = sorted(s for s, r in have.items() if c8(r))
    no = sorted(s for s, r in have.items() if not c8(r))
    if yes and no and max(no) < min(yes) and min(yes) - max(no) == 2:
        lo, hi = max(no), min(yes)
        return "done", [], {"lo_step": lo, "hi_step": hi, "lo_id": have[lo]["id"], "hi_id": have[hi]["id"],
                            "lo_J": have[lo]["E_delivered_J"], "hi_J": have[hi]["E_delivered_J"]}
    if not no:
        nxt = min(yes) - 2
    elif not yes:
        nxt = max(no) + 2
    else:
        return "not monotone", [], None
    if nxt < -19 or nxt > 39:
        return "out of range", [], None
    return "running", [b1_spec(test, nxt)], None


def b3_state(recs, P0=None):
    P0 = b3_start() if P0 is None else P0
    runs = {}
    for k in range(-60, 61):
        P = P0 + IN.B3_STEP_W * k
        if P <= 0:
            continue
        sp = b3_spec(P)
        if sp["id"] in recs:
            runs[round(P, 6)] = recs[sp["id"]]
    tgt, tol = IN.T_PROP_FIG_S, IN.B3_TOL_S
    if not runs:
        return "running", [b3_spec(P0)], None
    if any(failed(r) for r in runs.values()):
        return "failed", [], None

    def cls(r):
        if not c8(r):
            return "late"
        t = r["resolved"]["t_C8_s"]
        return "early" if t < tgt - tol else ("late" if t > tgt + tol else "hit")

    for P, r in sorted(runs.items()):
        if cls(r) == "hit":
            return "matched", [], {"P_W": P, "t_C8_s": r["resolved"]["t_C8_s"], "id": r["id"]}
    Ps = sorted(runs)
    for a, b in zip(Ps[:-1], Ps[1:]):
        if abs(b - a - IN.B3_STEP_W) < 1e-9 and cls(runs[a]) == "late" and cls(runs[b]) == "early":
            return "bracketed", [], {"P_lo_W": a, "P_hi_W": b, "id_lo": runs[a]["id"], "id_hi": runs[b]["id"]}
    if len(runs) >= B3_MAX_RUNS:
        return "limit", [], None
    last = runs[Ps[-1]] if cls(runs[Ps[-1]]) == "late" else runs[Ps[0]]
    if all(cls(r) == "late" for r in runs.values()):
        return "running", [b3_spec(Ps[-1] + IN.B3_STEP_W)], None
    if all(cls(r) == "early" for r in runs.values()):
        if Ps[0] - IN.B3_STEP_W <= 0:
            return "below zero", [], None
        return "running", [b3_spec(Ps[0] - IN.B3_STEP_W)], None
    return "not monotone", [], None


def b4_state(recs):
    pend = []
    for rank in (5, 50, 151, 196):
        sp = b4_spec(kin=IN.KIN_DRAWS[rank])
        if sp["id"] not in recs:
            pend.append(sp)
    sp = b4_spec(sei0=IN.SEI_AGED)
    if sp["id"] not in recs:
        pend.append(sp)
    # the shift: 5, 10, 15 ... K, then 2.5 K below the first with C8
    s = 5.0
    first = None
    while s <= B4_SHIFT_MAX + 1e-9:
        sp = b4_spec(shift=s)
        if sp["id"] not in recs:
            pend.append(sp)
            return pend, None
        if failed(recs[sp["id"]]):
            return pend, {"status": "failed"}
        if c8(recs[sp["id"]]):
            first = s
            break
        s += 5.0
    if first is None:
        return pend, {"status": "no C8 up to %.0f K" % B4_SHIFT_MAX}
    half = first - 2.5
    sp = b4_spec(shift=half)
    if sp["id"] not in recs:
        pend.append(sp)
        return pend, None
    if failed(recs[sp["id"]]):
        return pend, {"status": "failed"}
    least = half if c8(recs[sp["id"]]) else first
    return pend, {"status": "found", "least_shift_K": least,
                  "t_C8_s": recs[b4_spec(shift=least)["id"]]["resolved"]["t_C8_s"]}


def pending(recs):
    out = []
    states = {}
    for t in IN.B1_TESTS:
        st, p, br = b1_state(t, recs)
        states[t] = (st, br)
        out += p
    for f in B2_F:
        sp = b2_spec(f)
        if sp["id"] not in recs:
            out.append(sp)
    st, p, res = b3_state(recs)
    out += p
    p4, res4 = b4_state(recs)
    out += p4
    st1, br = states["M50_PT_Exp4"]
    v4 = []
    if st1 == "done":
        for side in ("lo_id", "hi_id"):
            base = recs[br[side]]
            for v in ("refine", "dt"):
                sp = v4_spec({k: base[k] for k in R.spec("x", "M50_PT_Exp4", [], "x")}, v)
                if sp["id"] not in recs:
                    v4.append(sp)
    return v4 + out          # the longest runs (V4's refined mesh) first, once they are due: an order, not a result


def registered_list():
    """The list before any record (the first runs of every chain), with the rules' parameters, as hashed."""
    first = []
    for t in IN.B1_TESTS:
        first += [b1_spec(t, -1), b1_spec(t, +1)]
    first += [b2_spec(f) for f in B2_F]
    first.append(b3_spec(b3_start()))
    first += [b4_spec(kin=IN.KIN_DRAWS[r]) for r in (5, 50, 151, 196)]
    first += [b4_spec(sei0=IN.SEI_AGED), b4_spec(shift=5.0)]
    rules = {"B1": {"first": [-0.05, 0.05], "step": 0.10, "of": "A2's E*(C8)"},
             "B3": {"step_W": IN.B3_STEP_W, "tol_s": IN.B3_TOL_S, "target_s": IN.T_PROP_FIG_S, "max_runs": B3_MAX_RUNS},
             "B4": {"shift_steps_K": [5.0, 2.5], "max_K": B4_SHIFT_MAX},
             "V4": {"refine": 1.5, "dt_scale": 0.5, "on": "B1 M50_PT_Exp4, both ends"},
             "stop": "C8 (mean 255.68 C) or 900 s", "lumped": "to 900 s, no stop",
             "failure": "a failed run is made again at once; a second failure stops its chain"}
    keep = ("id", "test", "deliveries", "kin", "sei0", "shift_K", "h", "refine", "dt_scale", "t_end_s",
            "stop_mean", "max_sub")
    return {"first": [{k: s[k] for k in keep} for s in first], "rules": rules}


def list_hash():
    text = json.dumps(registered_list(), sort_keys=True, default=float)
    return hashlib.sha256(text.encode()).hexdigest(), text


def main(a):
    import time
    if a.cmd == "list":
        h, text = list_hash()
        print(h)
        print(text[:2000])
        return
    if a.cmd == "status":
        recs = load()
        print(len(recs), "records")
        for sp in pending(recs):
            print("pending", sp["id"])
        return
    if a.cmd == "work":
        t0 = time.time()
        while True:
            if os.path.exists(R.STOP_FILE):
                return
            if a.max_minutes is not None and time.time() - t0 > 60.0 * a.max_minutes:
                return
            recs = load()
            pend = [sp for sp in pending(recs) if not os.path.exists(os.path.join(IN.RUNS, sp["id"] + ".claim"))]
            if not pend:
                if [f for f in os.listdir(IN.RUNS) if f.endswith(".claim")]:
                    time.sleep(10)
                    continue
                print("nothing left", flush=True)
                return
            R.work_list(pend[:1], IN.RUNS, a.worker, f"stage15-{a.worker}", None)
