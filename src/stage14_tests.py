"""Stage 14, Parts B and C (DECISIONS D154): the bounds against the sixteen tests, and the module table.

Arithmetic only. Reads results/stage14_bounds.csv, results/stage14_bounds.json and results/stage14_needs.csv.
Writes results/stage14_tests.csv (B1), results/stage14_partb.json (B1 counts, B2, B3) and
results/stage14_module_table.csv (Part C).
"""
import csv
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATHS = ("A1", "A2", "A3", "A4", "A5", "A6")
WINDOWS = ("21.39", "120.0", "240.0", "360.0")
NEED_COLS = {"21.39": ("need_21s_lo_J", "need_21s_hi_J", "reading_21s"),
             "120.0": ("need_120s_lo_J", "need_120s_hi_J", "need_120s_reading"),
             "240.0": ("need_240s_lo_J", "need_240s_hi_J", "need_240s_reading"),
             "360.0": ("need_360s_lo_J", "need_360s_hi_J", "need_360s_reading")}


def read(path):
    with open(os.path.join(ROOT, path), newline="") as fh:
        return list(csv.DictReader(fh))


def fnum(x):
    x = (x or "").strip()
    return None if x == "" else float(x)


def verdict(U, lo, hi):
    if hi == 0.0:
        return "needs nothing"
    if U >= hi:
        return "reaches"
    if U >= lo:
        return "reaches part"
    return "does not reach"


def main():
    bounds = {}
    for r in read("results/stage14_bounds.csv"):
        bounds[(r["path"], str(float(r["window_s"])) if r["window_s"] != "total" else "total")] = r
    bj = json.load(open(os.path.join(ROOT, "results", "stage14_bounds.json")))
    needs = read("results/stage14_needs.csv")

    def U(path, window):
        r = bounds[(path, window)]
        return None if r["determinable"] == "no" else float(r["upper_J"])

    rows = []
    for t in needs:
        for win, (klo, khi, kread) in NEED_COLS.items():
            lo, hi = fnum(t[klo]), fnum(t[khi])
            if hi is None:
                continue
            for p in PATHS:
                if p == "A5":
                    v = "not determinable"
                    u = ""
                elif p == "A6" and t["connection"] != "parallel":
                    v = "does not act (series)"
                    u = ""
                else:
                    u = U(p, win)
                    v = verdict(u, lo, hi)
                rows.append(dict(test=t["test"], connection=t["connection"], propagated=t["propagated"],
                                 failure_category=t["failure_category"] or "none", window_s=win, reading=t[kread],
                                 need_lo_J=lo, need_hi_J=hi, path=p, upper_J=u, verdict=v))
    with open(os.path.join(ROOT, "results", "stage14_tests.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # B1 counts at 21.39 s
    b1 = {}
    for p in PATHS:
        sel = [r for r in rows if r["path"] == p and r["window_s"] == "21.39"]
        b1[p] = {k: sum(1 for r in sel if r["verdict"] == k) for k in
                 ("reaches", "reaches part", "does not reach", "needs nothing", "not determinable", "does not act (series)")}
        b1[p]["tests_not_reached"] = [r["test"] for r in sel if r["verdict"] in ("does not reach", "reaches part")]

    # B2
    prop = [t for t in needs if t["propagated"] == "yes"]
    ranked = sorted(prop, key=lambda t: -float(t["need_21s_hi_J"]))
    largest = float(ranked[0]["need_21s_hi_J"])
    large_paths = [p for p in PATHS if p != "A5" and U(p, "21.39") is not None and U(p, "21.39") >= largest]
    allows = {"A1": "every test (the trigger vents)", "A2": "every test (the trigger vents)", "A3": "category 4 only (a trigger rupture)",
              "A4": "every test (the trigger ejects)", "A6": "parallel tests only"}
    cat4 = [dict(test=t["test"], propagated=t["propagated"], need_21s_lo_J=float(t["need_21s_lo_J"]), need_21s_hi_J=float(t["need_21s_hi_J"]),
                 reading=t["reading_21s"]) for t in needs if t["failure_category"] == "4"]
    sums = {}
    for win in list(WINDOWS) + ["total"]:
        s = sum(U(p, win) for p in PATHS if p != "A5" and p != "A6")
        s_par = s + U("A6", win)
        over = []
        for t in needs:
            if win == "total":
                continue
            hi = fnum(t[NEED_COLS[win][1]])
            if hi is None:
                continue
            cap = s_par if t["connection"] == "parallel" else s
            if hi > cap:
                over.append(t["test"])
        sums[win] = dict(sum_series_J=s, sum_parallel_J=s_par, tests_needing_more=over)
    b2 = dict(
        ranked=[dict(test=t["test"], need_21s_hi_J=float(t["need_21s_hi_J"]), reading=t["reading_21s"], category=t["failure_category"] or "none")
                for t in ranked],
        top3=[dict(test=t["test"], category=t["failure_category"] or "none") for t in ranked[:3]],
        largest_need_21s_J=largest,
        paths_reaching_largest_need_21s=large_paths,
        where_each_path_acts=allows,
        category4_tests=cat4,
        sums_of_determinable_bounds=sums,
    )

    # B3
    Tf_C = bj["inputs"]["T_flame_K"] - 273.15
    b3 = {}
    for name, reading in (("M50_PT_Exp2", 808.0), ("M50_SP_Exp4", 626.0)):
        t = next(x for x in needs if x["test"] == name)
        cat = t["failure_category"] or "none"
        b3[name] = dict(
            neighbour_max_C=reading, category=cat, connection=t["connection"],
            A1=f"possible: published flame temperatures reach {Tf_C:.0f} C, above {reading:.0f} C, and the radiation lands near the venting end, a patch",
            A2=f"possible: gas or flame beside the neighbour up to {Tf_C:.0f} C can heat a patch (the wedges, or a thermocouple it engulfs)",
            A3="not shown by the category: a breach's jet could, but neither test is in category 4" if cat != "4" else "possible: category 4",
            A4="possible: hot solids or melt resting on the thermocouple (molten copper was seen in most M50 tests, Sharp et al.)",
            A5="not determinable: the holder's temperature is not given",
            A6=("heats the roll by volume, not a surface patch, so it cannot raise one surface reading far above the roll" if t["connection"] == "parallel"
                else "does not act (series)"),
            note="Stated as possibilities and not built on; the paper notes that cells and thermocouples moved during failure (D89 (5)).",
        )
    with open(os.path.join(ROOT, "results", "stage14_partb.json"), "w") as fh:
        json.dump(dict(B1_counts_21s=b1, B2=b2, B3=b3), fh, indent=1)

    # Part C, the module table
    share = {
        "A1": "every calorimetry test vented (10 of 10, this cell); fire reported in the rig without a count",
        "A2": "as A1",
        "A3": "a trigger rupture in 3 of 16 tests in this rig; 0 of 10 in calorimetry; 3 of 3 (35 mm nail) and none (10 mm) in Read et al.; facing the neighbour: 1/6 of the circumference for a narrow jet",
        "A4": "as A1; from a breach, melt falls onto the facing half from 1/2 of the circumference",
        "A5": "the holder always touches; not determinable",
        "A6": "the 8 parallel tests of 16",
    }
    mod = []
    for p in PATHS:
        r = bounds[(p, "total")]
        det = r["determinable"] == "yes"
        row = dict(path=p, path_name=r["path_name"], carrier=r["carrier"], determinable=r["determinable"], lower_J=0.0 if det else "")
        for win in WINDOWS:
            row[f"upper_within_{win}s_J"] = U(p, win) if det else ""
        row["upper_total_J"] = U(p, "total") if det else ""
        row["time_lo_s"], row["time_hi_s"] = r["time_lo_s"], r["time_hi_s"]
        row["where_and_reading"] = r["where_and_reading"]
        row["share_of_events"] = share[p]
        row["note"] = r["note"]
        row["to_narrow_it"] = r["to_narrow_it"]
        mod.append(row)
    with open(os.path.join(ROOT, "results", "stage14_module_table.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(mod[0].keys()))
        w.writeheader()
        w.writerows(mod)
    print(json.dumps(dict(B1_counts_21s=b1, top3=b2["top3"], large=large_paths, sums={k: v_["tests_needing_more"] for k, v_ in sums.items()}), indent=1))


if __name__ == "__main__":
    main()
