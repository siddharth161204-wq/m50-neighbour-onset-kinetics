#!/usr/bin/env python3
"""Restarts the Stage 5 workers on Windows with the corrected code (DECISIONS.md D47), started by
restart_stage5_windows.cmd beside the repository.

1. Stops the running workers through the stop file; each finishes its current run first.
2. Sets aside the records of runs that failed for want of memory (MemoryError, or PARDISO error -2) in
   results/v12_failed_memory/, listed in results/v12_failed_memory.json, so that the runs are made again.
3. Starts the pass again (v12_laptop.py): the environment check is skipped once passed, the cloud machine's claims
   are kept, and the new workers make every run not yet recorded.
"""
import glob, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v12_laptop as L
import v12_run as RUN


def main():
    lock = json.load(open(L.LOCK)) if os.path.exists(L.LOCK) else {"pids": []}
    lim = L.worker_start_limits(lock) if lock.get("started_utc") else {}
    live = [p for p in lock["pids"] if L.alive(p, lim.get(p))]
    if live:
        with open(RUN.STOP_FILE, "w") as fh:
            fh.write("restart, D47\n")
        print(f"{L.utc()} Stopping {len(live)} running workers; each finishes its current run first.")
        t0 = time.time()
        while live and time.time() - t0 < 3600:
            L.keep_awake()
            time.sleep(15)
            live = [p for p in live if L.alive(p, lim.get(p))]
            print(f"\r{time.strftime('%H:%M')}  {len(live)} still running.   ", end="", flush=True)
        print()
        if live:
            print("Some workers did not stop within an hour; nothing else was done. Tell Claude.")
            return 1
    aside = os.path.join(L.RES, "v12_failed_memory")
    os.makedirs(aside, exist_ok=True)
    moved = []
    for f in sorted(glob.glob(os.path.join(RUN.RUNS, "*.json"))):
        r = json.load(open(f))
        if r.get("failed") and RUN.is_memory_failure(r.get("error", "")):
            os.replace(f, os.path.join(aside, os.path.basename(f)))
            moved.append({"id": r["id"], "error": r["error"][:120], "finished_utc": r.get("finished_utc")})
    man = os.path.join(L.RES, "v12_failed_memory.json")
    old = json.load(open(man)) if os.path.exists(man) else []
    json.dump(old + [{"set_aside_utc": L.utc(), "runs": moved}], open(man, "w"), indent=1)
    print(f"{L.utc()} {len(moved)} records of runs that failed for want of memory set aside; they will be run again.")
    if os.path.exists(RUN.STOP_FILE):
        os.remove(RUN.STOP_FILE)
    return L.main()


if __name__ == "__main__":
    sys.exit(main())
