#!/usr/bin/env python3
"""Stage 10 on the author's laptop (DECISIONS.md D106 (1)), started by run_stage10_windows.cmd.

The laptop, its Python and its packages are those of Stages 5 to 9 (their environment check of 21 October is not
repeated; test_stage10.py's first test checks that a Stage 10 run equals Stage 9's at the probes they share). One
worker per logical processor (fewer if the memory is short, 0.6 GB each, D47 (4)) on the shared run list
(stage10_run.py work), at below-normal priority, detached and out of efficiency mode, as for Stage 9 (D96 (1)). While
this window is open it keeps the computer awake and shows the progress; at the end it zips the records.
To stop: create the file results/stage10_STOP (each worker finishes its current run). To go on later: run the .cmd
again; recorded runs are skipped.
"""
import glob, json, os, subprocess, sys, time, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v12_laptop as L5                         # memory, keep-awake and process helpers of Stage 5 (unchanged)

REPO = os.path.normpath(os.path.join(HERE, ".."))
RES = os.path.join(REPO, "results")
LOGS = os.path.join(RES, "stage10_logs")
LOCK = os.path.join(RES, "stage10_laptop_workers.json")
ZIP = os.path.normpath(os.path.join(REPO, "..", "results_stage10_laptop.zip"))
STOP = os.path.join(RES, "stage10_STOP")


def launch(n):
    subprocess.run([sys.executable, "stage10_run.py", "reset-claims"], cwd=HERE, env=L5.ENV)
    os.makedirs(LOGS, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    pids = []
    for k in range(n):
        p = L5.py(["stage10_run.py", "work", "--label", "author-laptop", "--worker", str(k)],
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


def monitor(pids, limits=None):
    limits = limits or {}
    while True:
        L5.keep_awake()
        done = len(glob.glob(os.path.join(RES, "stage10_runs", "*.json")))
        live = sum(L5.alive(p, limits.get(p)) for p in pids)
        print(f"\r{time.strftime('%H:%M')}  {done} Stage 10 runs recorded, {live} workers running.   ", end="", flush=True)
        if live == 0:
            print()
            return done
        time.sleep(60)


def make_zip():
    files = []
    for sub in ("stage10_runs", "stage10_series", "stage10_logs"):
        files += [f for f in glob.glob(os.path.join(RES, sub, "*")) if not f.endswith(".claim") and ".tmp" not in f]
    files += [f for f in (LOCK,) if os.path.exists(f)]
    tmp = ZIP + f".tmp{os.getpid()}"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(f, os.path.relpath(f, REPO))
    for k in range(120):
        try:
            os.replace(tmp, ZIP)
            break
        except PermissionError:
            time.sleep(1)
    print(f"{L5.utc()} {len(files)} files zipped into {ZIP}")


def main():
    tot, avail = L5.mem_gb()
    print(f"Stage 10 on this computer: {os.cpu_count()} logical processors, {tot:.1f} GB memory ({avail:.1f} GB free).")
    for need in ("stage7_triggers.json", "stage8_thresholds.csv", "stage9_states.json", "stage9_fractions.csv"):
        if not os.path.exists(os.path.join(RES, need)):
            print(f"results/{need} is missing; no run is started.")
            return 1
    if os.path.exists(LOCK):
        old = json.load(open(LOCK))
        lim = L5.worker_start_limits(old)
        if any(L5.alive(p, lim.get(p)) for p in old["pids"]):
            print("Workers from an earlier start are still running; showing their progress.")
            monitor(old["pids"], lim)
            make_zip()
            return 0
    want = int(os.environ.get("STAGE10_WORKERS", os.cpu_count() or 1))
    per = float(os.environ.get("STAGE10_GB_PER_WORKER", 0.6))
    n = max(1, min(want, int((avail - 2.0) / per)))
    print(f"{n} workers ({want} asked for; {per:.2f} GB allowed each, {avail:.1f} GB free).")
    if os.path.exists(STOP):
        os.remove(STOP)
    pids = launch(n)
    done = monitor(pids)
    make_zip()
    print(f"{done} runs recorded. Tell Claude the runs have finished.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
