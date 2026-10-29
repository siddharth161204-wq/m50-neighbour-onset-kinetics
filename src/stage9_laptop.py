#!/usr/bin/env python3
"""Stage 9 on the author's laptop (DECISIONS.md D96 (1)), started by run_stage9_windows.cmd.

The laptop, its Python and its packages are those of Stages 5 to 7 (D45, D55 (4), D69 (4)); their environment check
passed on 21 October (results/v12_checks_laptop/acceptance.json) and is not repeated, since neither the packages nor
the Stage 5 model changed; the three Stage 8 runs made again at the head of the list (stage9_run.py, kind xcheck) check
the Stage 8 code on this machine against its cloud records. One worker per logical processor (fewer if the memory is
short, 0.6 GB each, D47 (4)) on the shared run list (stage9_run.py work), at below-normal priority, detached and out of
efficiency mode (D46 (1)). While this window is open it keeps the computer awake and shows the progress; at the end it
zips the records.
To stop: create the file results/stage9_STOP (each worker finishes its current run). To go on later: run the .cmd
again; recorded runs are skipped. add_stage9_workers_windows.cmd (--add, D98 (2)) replaces workers that stopped with
an error, leaving the running ones as they are.
"""
import glob, json, os, subprocess, sys, time, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v12_laptop as L5                         # memory, keep-awake and process helpers of Stage 5 (unchanged)

REPO = os.path.normpath(os.path.join(HERE, ".."))
RES = os.path.join(REPO, "results")
LOGS = os.path.join(RES, "stage9_logs")
LOCK = os.path.join(RES, "stage9_laptop_workers.json")
ZIP = os.path.normpath(os.path.join(REPO, "..", "results_stage9_laptop.zip"))
ACCEPTANCE = os.path.join(RES, "v12_checks_laptop", "acceptance.json")
STOP = os.path.join(RES, "stage9_STOP")


def launch(n):
    subprocess.run([sys.executable, "stage9_run.py", "reset-claims"], cwd=HERE, env=L5.ENV)
    os.makedirs(LOGS, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    pids = []
    for k in range(n):
        p = L5.py(["stage9_run.py", "work", "--label", "author-laptop", "--worker", str(k)],
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
        done = len(glob.glob(os.path.join(RES, "stage9_runs", "*.json")))
        xc = len(glob.glob(os.path.join(RES, "stage9_xcheck", "*.json")))
        live = sum(L5.alive(p, limits.get(p)) for p in pids)
        print(f"\r{time.strftime('%H:%M')}  {done} Stage 9 runs and {xc} of 3 cross-checks recorded, "
              f"{live} workers running.   ", end="", flush=True)
        if live == 0:
            print()
            return done
        time.sleep(60)


def make_zip():
    files = []
    for sub in ("stage9_runs", "stage9_series", "stage9_xcheck", "stage9_logs"):
        files += [f for f in glob.glob(os.path.join(RES, sub, "*")) if not f.endswith(".claim") and ".tmp" not in f]
    files += [f for f in (LOCK, os.path.join(RES, "stage9_v1.json")) if os.path.exists(f)]
    tmp = ZIP + f".tmp{os.getpid()}"               # D98 (2): another window may be zipping at the same time
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(f, os.path.relpath(f, REPO))
    for k in range(120):
        try:
            os.replace(tmp, ZIP)
            break
        except PermissionError:
            time.sleep(1)
    else:
        print(f"{ZIP} is held by another program; the records are zipped in {tmp}")
        return
    print(f"{L5.utc()} {len(files)} files zipped into {ZIP}")


def _start(first, n):
    """launch's workers, numbered on from the earlier ones, without clearing the claims (D98 (2))."""
    os.makedirs(LOGS, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    pids, logs = [], []
    for k in range(first, first + n):
        log = os.path.join(LOGS, f"laptop_{stamp}_w{k:02d}.log")
        p = L5.py(["stage9_run.py", "work", "--label", "author-laptop", "--worker", str(k)], log, L5.BELOW | L5.DETACHED)
        pids.append(p.pid)
        logs.append(log)
    off = 0
    if L5.WIN and pids:
        time.sleep(2)
        import v12_laptop_more
        off = sum(v12_laptop_more.no_ecoqos(p) for p in pids)
    return pids, logs, off


def _logs(lock):
    """Each worker's log: the first start's by the worker's number (the latest log of that number made before the
    start was recorded), the added ones' as recorded."""
    out = {}
    first = lock["started_utc"].replace("-", "").replace(":", "")
    for k, p in enumerate(lock["pids"][:lock["workers"]]):
        logs = [f for f in sorted(glob.glob(os.path.join(LOGS, f"laptop_*_w{k:02d}.log")))
                if os.path.basename(f)[7:23] <= first]
        if logs:
            out[p] = logs[-1]
    for add in lock.get("added", []):
        out.update(zip(add["pids"], add.get("logs", [])))
    return out


def _ended_well(log):
    """A worker's normal ends (stage9_run.work): nothing left to run, or the stop file (or a budget, unused here)."""
    try:
        text = open(log, errors="replace").read()
    except (OSError, TypeError):
        return True                                # no log to read: not taken for a worker that failed
    return "nothing left to run" in text or "stopping after" in text


def _free_claims():
    """Removes each claim whose worker is no longer running: at the end of the list such a claim would keep the
    others waiting, and its run, if unrecorded, is made again (D98 (2))."""
    import calendar
    n = 0
    for f in glob.glob(os.path.join(RES, "stage9_runs", "*.claim")):
        try:
            _, pid, at = open(f).read().split()[:3]
            pid, t = int(pid), calendar.timegm(time.strptime(at, "%Y-%m-%dT%H:%M:%SZ"))
        except (OSError, ValueError):
            continue                               # being written
        if not L5.alive(pid, t + 60):              # the claim's time is to the second; a later process with the pid
            try:                                   # is not taken for its worker
                os.remove(f)
                n += 1
            except OSError:
                pass
    return n


def _save(lock):
    for k in range(20):
        try:
            with open(LOCK + f".tmp{os.getpid()}", "w") as fh:
                json.dump(lock, fh, indent=1)
            os.replace(LOCK + f".tmp{os.getpid()}", LOCK)
            return
        except PermissionError:
            time.sleep(0.5)
    raise RuntimeError(f"could not write {LOCK}")


def add():
    """D98 (2): leaves the running workers as they are; for each worker that has stopped without its normal end,
    starts one with the code as it now stands (at most as many in all as the first start had), and while this window
    is open does the same for any later one and removes the claims of workers no longer running."""
    if not os.path.exists(LOCK):
        print("No earlier start is recorded; starting afresh.")
        return main()
    lock = json.load(open(LOCK))
    target = int(lock["workers"])
    print(f"Stage 9 on this computer: the start of {lock['started_utc']} ({target} workers); this window replaces "
          f"workers that stop with an error and keeps the computer awake.")
    while True:
        L5.keep_awake()
        lock = json.load(open(LOCK))
        lim, logs = L5.worker_start_limits(lock), _logs(lock)
        live = [p for p in lock["pids"] if L5.alive(p, lim.get(p))]
        done_before = set(lock.get("replaced", []))
        failed = [p for p in lock["pids"] if p not in live and p not in done_before and not _ended_well(logs.get(p))]
        freed = _free_claims()
        room = target - len(done_before)
        if failed and room > 0 and not os.path.exists(STOP):
            per = float(os.environ.get("STAGE9_GB_PER_WORKER", 0.6))
            n = max(0, min(len(failed), room, target - len(live), int((L5.mem_gb()[1] - 2.0) / per)))
            if n:
                pids, new_logs, off = _start(len(lock["pids"]), n)
                lock["pids"] += pids
                lock.setdefault("added", []).append({"utc": L5.utc(), "pids": pids, "logs": new_logs,
                                                     "replacing": failed[:n], "ecoqos_off": off,
                                                     "claims_freed": freed})
                lock["replaced"] = sorted(done_before | set(failed[:n]))
                _save(lock)
                print(f"\n{L5.utc()} {n} workers started with the code as it now stands, in place of "
                      f"{', '.join(str(lock['pids'].index(p)) for p in failed[:n])}; {freed} claims freed.")
                live += pids
        elif freed:
            print(f"\n{L5.utc()} {freed} claims of workers no longer running freed.")
        done = len(glob.glob(os.path.join(RES, "stage9_runs", "*.json")))
        xc = len(glob.glob(os.path.join(RES, "stage9_xcheck", "*.json")))
        print(f"\r{time.strftime('%H:%M')}  {done} Stage 9 runs and {xc} of 3 cross-checks recorded, "
              f"{len(live)} workers running, {len(lock.get('replaced', []))} replaced.   ", end="", flush=True)
        if not live:
            print()
            break
        time.sleep(60)
    lock = json.load(open(LOCK))
    logs = _logs(lock)
    bad = [p for p in lock["pids"] if not _ended_well(logs.get(p))]
    make_zip()
    print(f"{done} runs recorded" + (f"; {len(bad)} workers stopped with an error (results/stage9_logs)" if bad else "")
          + ". Tell Claude the runs have finished.")
    return 0


def main():
    tot, avail = L5.mem_gb()
    print(f"Stage 9 on this computer: {os.cpu_count()} logical processors, {tot:.1f} GB memory ({avail:.1f} GB free).")
    if not (os.path.exists(ACCEPTANCE) and json.load(open(ACCEPTANCE)).get("pass")):
        print("The Stage 5 environment check has not passed on this computer; no run is started.")
        return 1
    for need in ("stage7_triggers.json", "stage8_thresholds.csv"):
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
    want = int(os.environ.get("STAGE9_WORKERS", os.cpu_count() or 1))
    per = float(os.environ.get("STAGE9_GB_PER_WORKER", 0.6))
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
    sys.exit(add() if "--add" in sys.argv else main())
