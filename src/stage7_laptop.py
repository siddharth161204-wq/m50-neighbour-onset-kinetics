#!/usr/bin/env python3
"""Stage 7 on the author's laptop (DECISIONS.md D69 (4)), started by run_stage7_windows.cmd.

The laptop, its Python and its packages are those of Stages 5 and 6 (D45, D55 (4)); their environment check passed on
21 October (results/v12_checks_laptop/acceptance.json) and is not repeated, since neither the packages nor the Stage 5
model changed. One worker per logical processor (fewer if the memory is short, 0.6 GB each, D47 (4)) on the shared
run list (stage7_run.py work --queue), at below-normal priority, detached and out of efficiency mode (D46 (1)). The
workers make Part A, then write Part C's list from Part A's records and make Part C, in one start. While this window
is open it keeps the computer awake and shows the progress; at the end it zips the records.
To stop: create the file results/stage7_STOP (each worker finishes its current run). To go on later: run the .cmd
again; recorded runs are skipped.
"""
import glob, json, os, subprocess, sys, time, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v12_laptop as L5                         # memory, keep-awake and process helpers of Stage 5 (unchanged)

REPO = os.path.normpath(os.path.join(HERE, ".."))
RES = os.path.join(REPO, "results")
LOGS = os.path.join(RES, "stage7_logs")
LOCK = os.path.join(RES, "stage7_laptop_workers.json")
ZIP = os.path.normpath(os.path.join(REPO, "..", "results_stage7_laptop.zip"))
ACCEPTANCE = os.path.join(RES, "v12_checks_laptop", "acceptance.json")


def launch(n):
    subprocess.run([sys.executable, "stage7_run.py", "reset-claims"], cwd=HERE, env=L5.ENV)
    os.makedirs(LOGS, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    pids = []
    for k in range(n):
        p = L5.py(["stage7_run.py", "work", "--queue", "--label", "author-laptop", "--worker", str(k), "--of", str(n)],
                  os.path.join(LOGS, f"laptop_{stamp}_w{k:02d}.log"), L5.BELOW | L5.DETACHED)
        pids.append(p.pid)
    off = 0
    if L5.WIN:
        time.sleep(2)
        import v12_laptop_more
        off = sum(v12_laptop_more.no_ecoqos(p) for p in pids)
    json.dump({"started_utc": L5.utc(), "workers": n, "pids": pids, "ecoqos_off": off}, open(LOCK, "w"), indent=1)
    print(f"{L5.utc()} {n} workers started (below-normal priority, efficiency mode off for {off}).")
    return pids


def total_runs():
    import stage7_run
    return len(stage7_run.build_runs()), os.path.exists(stage7_run.EVENTLIST)


def monitor(pids, limits=None):
    limits = limits or {}
    while True:
        L5.keep_awake()
        done = len(glob.glob(os.path.join(RES, "stage7_runs", "*.json")))
        total, part_c = total_runs()
        live = sum(L5.alive(p, limits.get(p)) for p in pids)
        what = "Parts A and C" if part_c else "Part A (Part C's list comes after it)"
        print(f"\r{time.strftime('%H:%M')}  {done} of {total} runs recorded ({what}), {live} workers running.   ",
              end="", flush=True)
        if live == 0:
            print()
            return done, total
        time.sleep(60)


def make_zip():
    files = []
    for sub in ("stage7_runs", "stage7_series", "stage7_logs"):
        files += [f for f in glob.glob(os.path.join(RES, sub, "*")) if not f.endswith(".claim") and ".tmp" not in f]
    files += [f for f in (LOCK, os.path.join(RES, "stage7_eventlist.json"), os.path.join(RES, "stage7_eventlist.lock"))
              if os.path.exists(f)]
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(f, os.path.relpath(f, REPO))
    print(f"{L5.utc()} {len(files)} files zipped into {ZIP}")


def main():
    import stage7_run
    tot, avail = L5.mem_gb()
    total, part_c = total_runs()
    print(f"Stage 7 on this computer: {os.cpu_count()} logical processors, {tot:.1f} GB memory ({avail:.1f} GB free); "
          f"{total} runs in the list so far.")
    if not (os.path.exists(ACCEPTANCE) and json.load(open(ACCEPTANCE)).get("pass")):
        print("The Stage 5 environment check has not passed on this computer; no run is started.")
        return 1
    if not os.path.exists(stage7_run.TRIGGERS):
        print("results/stage7_triggers.json is missing; no run is started.")
        return 1
    if os.path.exists(LOCK):
        old = json.load(open(LOCK))
        lim = L5.worker_start_limits(old)
        if any(L5.alive(p, lim.get(p)) for p in old["pids"]):
            print("Workers from an earlier start are still running; showing their progress.")
            monitor(old["pids"], lim)
            make_zip()
            return 0
    want = int(os.environ.get("V12_WORKERS", os.cpu_count() or 1))
    per = float(os.environ.get("V12_GB_PER_WORKER", 0.6))
    n = max(1, min(want, int((avail - 2.0) / per)))
    print(f"{n} workers ({want} asked for; {per:.2f} GB allowed each, {avail:.1f} GB free).")
    if os.path.exists(stage7_run.STOP_FILE):
        os.remove(stage7_run.STOP_FILE)
    pids = launch(n)
    done, total = monitor(pids)
    make_zip()
    print(f"{done} of {total} runs recorded. Tell Claude the runs have finished.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
