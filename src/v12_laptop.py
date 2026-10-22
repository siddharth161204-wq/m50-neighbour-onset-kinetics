#!/usr/bin/env python3
"""Stage 5 on the author's laptop (DECISIONS.md D45), started by run_stage5_windows.cmd.

1. The environment check, once: the kernel check and the five reactive Stage 2 cases of V2 (d), all at the same time,
   into results/v12_checks_laptop/. Accepted when, in every case, every band entry agrees with Stage 2's record within
   0.01 s and every peak (hottest node, mean and lumped) within 0.01 K, the precision Stage 2 reported, and the sparse
   solver is PARDISO, as on the machine that registered the predictions. No Stage 5 run starts otherwise.
2. One worker per core (fewer if the memory is short, 1 GB each) on the shared run list (v12_run.py work --queue), at
   below-normal priority and detached, so they go on if this window closes. While it is open, this window keeps the
   computer awake and shows the progress; at the end it zips the records for the repository.
To stop: create the file results/v12_STOP (each worker finishes its current run). To go on later: run the .cmd again;
recorded runs are skipped.
"""
import ctypes, glob, json, os, subprocess, sys, time, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, ".."))
RES = os.path.join(REPO, "results")
CHECKS = os.path.join(RES, "v12_checks_laptop")
LOGS = os.path.join(RES, "v12_logs")
LOCK = os.path.join(RES, "v12_laptop_workers.json")
ZIP = os.path.normpath(os.path.join(REPO, "..", "results_v12_laptop.zip"))
STAGE2_CASES = ("max:10:0.5", "max:30:0.5", "max:10:0.2", "max:30:0.2", "median:30:0.5")
ENV = dict(os.environ, OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", OMP_NUM_THREADS="1", NUMBA_NUM_THREADS="1",
           PYTHONUTF8="1", V12_CHECKS_DIR="v12_checks_laptop")
WIN = os.name == "nt"
BELOW = getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0)
DETACHED = (0x00000008 | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)) if WIN else 0
GB_PER_WORKER = 1.0
TOL_S, TOL_K = 0.01, 0.01


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def mem_gb():
    if WIN:
        class MS(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        m = MS()
        m.dwLength = ctypes.sizeof(MS)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        return m.ullTotalPhys / 2 ** 30, m.ullAvailPhys / 2 ** 30
    ps = os.sysconf("SC_PAGE_SIZE")
    return os.sysconf("SC_PHYS_PAGES") * ps / 2 ** 30, os.sysconf("SC_AVPHYS_PAGES") * ps / 2 ** 30


def keep_awake():
    if WIN:                                            # ES_CONTINUOUS | ES_SYSTEM_REQUIRED, for as long as this runs
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)


def started_epoch(pid):
    """When the process now holding this pid was created (Windows), so that a reused pid is not taken for a worker."""
    if not WIN:
        return None
    h = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
    if not h:
        return None
    c, e, k, u = (ctypes.c_ulonglong() for _ in range(4))
    ok = ctypes.windll.kernel32.GetProcessTimes(h, ctypes.byref(c), ctypes.byref(e), ctypes.byref(k), ctypes.byref(u))
    ctypes.windll.kernel32.CloseHandle(h)
    return (c.value - 116444736000000000) / 1e7 if ok else None


def worker_start_limits(lock):
    """For each worker of a lock file, the latest creation time its process can have (its start plus 10 minutes)."""
    import calendar
    ep = lambda s: calendar.timegm(time.strptime(s, "%Y-%m-%dT%H:%M:%SZ"))
    lim = {p: ep(lock["started_utc"]) + 600 for p in lock.get("pids", [])}
    for add in lock.get("added", []):
        for p in add.get("pids", []):
            lim[p] = ep(add["utc"]) + 600
    return lim


def terminate(pid):
    """Ends a worker that did not stop (Windows): its run in progress is unrecorded and is made again."""
    if not WIN:
        try:
            os.kill(pid, 9)
            return True
        except OSError:
            return False
    h = ctypes.windll.kernel32.OpenProcess(0x0001 | 0x1000, False, pid)
    if not h:
        return False
    ok = ctypes.windll.kernel32.TerminateProcess(h, 1)
    ctypes.windll.kernel32.CloseHandle(h)
    return bool(ok)


def alive(pid, not_after=None):
    if WIN:
        h = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
        if not h:
            return False
        code = ctypes.c_ulong()
        ok = ctypes.windll.kernel32.GetExitCodeProcess(h, ctypes.byref(code))
        ctypes.windll.kernel32.CloseHandle(h)
        if not (bool(ok) and code.value == 259):       # STILL_ACTIVE
            return False
        if not_after is not None:
            t0 = started_epoch(pid)
            if t0 is not None and t0 > not_after:      # the pid now belongs to a later process
                return False
        return True
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def py(args, log, flags=0):
    return subprocess.Popen([sys.executable] + args, cwd=HERE, env=ENV, stdout=open(log, "w"),
                            stderr=subprocess.STDOUT, creationflags=flags)


def machine():
    out = subprocess.run([sys.executable, "-c", "import json, v12_run; print(json.dumps(v12_run.machine_info('author-laptop')))"],
                         cwd=HERE, env=ENV, capture_output=True, text=True)
    return json.loads(out.stdout.strip().splitlines()[-1])


def _diff(a, b):
    if a is None and b is None:
        return 0.0
    if a is None or b is None:
        return float("inf")
    return abs(a - b)


def check():
    acc = os.path.join(CHECKS, "acceptance.json")
    if os.path.exists(acc) and json.load(open(acc)).get("pass"):
        print("The environment check passed before:", acc)
        return True
    os.makedirs(CHECKS, exist_ok=True)
    info = machine()
    print("Machine:", json.dumps(info))
    print(f"{utc()} Environment check: the compiled step and the five reactive Stage 2 cases, at the same time.")
    procs = [py(["v12_checks.py", "kernel"], os.path.join(CHECKS, "kernel.log"), BELOW)]
    for c in STAGE2_CASES:
        procs.append(py(["v12_checks.py", "v2-reactive", "--cases", c],
                        os.path.join(CHECKS, "v2_" + c.replace(":", "-") + ".log"), BELOW))
    while any(p.poll() is None for p in procs):
        keep_awake()
        time.sleep(20)
        print(".", end="", flush=True)
    print()
    rec = evaluate(info, [p.returncode for p in procs])
    json.dump(rec, open(acc, "w"), indent=1, default=float)
    print(json.dumps(rec, indent=1, default=float))
    print("PASSED" if rec["pass"] else "FAILED: no Stage 5 run is started on this machine.")
    return rec["pass"]


def evaluate(info, codes, checks=CHECKS):
    rec = {"checked_utc": utc(), "machine": info, "tolerance": {"band_entry_s": TOL_S, "peak_K": TOL_K},
           "exit_codes": codes, "cases": {}}
    ok = all(c == 0 for c in codes) and info.get("sparse_solver") == "pardiso"
    for f in sorted(glob.glob(os.path.join(checks, "v2_reactive_numba_*.json"))):
        for name, d in json.load(open(f)).items():
            ds = max(_diff(a, b) for a, b in d["cross_s"].values())
            lc = d["lumped_cross_s"]
            if isinstance(lc[0], dict) or isinstance(lc[1], dict):
                a, b = lc[0] or {}, lc[1] or {}
                ds = max([ds] + [_diff(a.get(k), b.get(k)) for k in set(a) | set(b)])
            else:
                ds = max(ds, _diff(lc[0], lc[1]))
            dk = max(_diff(*d["peak_Tmax_C"]), _diff(*d["peak_Tmean_C"]), _diff(*d["lumped_peak_C"]))
            rec["cases"][name] = {"band_entry_max_diff_s": ds, "peak_max_diff_K": dk,
                                  "steps": d["steps"], "identical": d["identical"]}
            ok = ok and ds <= TOL_S and dk <= TOL_K
    ok = ok and len(rec["cases"]) == len(STAGE2_CASES)
    rec["pass"] = bool(ok)
    return rec


def launch(n):
    subprocess.run([sys.executable, "v12_run.py", "reset-claims"], cwd=HERE, env=ENV)
    os.makedirs(LOGS, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    pids = []
    for k in range(n):
        p = py(["v12_run.py", "work", "--queue", "--label", "author-laptop", "--worker", str(k), "--of", str(n),
                "--budget-min", "1e9", "--wall-min", "1e9"], os.path.join(LOGS, f"laptop_{stamp}_w{k:02d}.log"),
               BELOW | DETACHED)
        pids.append(p.pid)
    off = 0
    if WIN:                                            # D46 (1): let them use the fast cores
        time.sleep(2)
        import v12_laptop_more
        off = sum(v12_laptop_more.no_ecoqos(p) for p in pids)
    json.dump({"started_utc": utc(), "workers": n, "pids": pids, "ecoqos_off": off}, open(LOCK, "w"), indent=1)
    print(f"{utc()} {n} workers started (below-normal priority, efficiency mode off for {off}).")
    return pids


def monitor(pids, total):
    while True:
        keep_awake()
        done = len(glob.glob(os.path.join(RES, "v12_runs", "*.json")))
        live = sum(alive(p) for p in pids)
        print(f"\r{time.strftime('%H:%M')}  {done} of {total} runs recorded, {live} workers running.   ", end="", flush=True)
        if live == 0:
            print()
            return done
        time.sleep(60)


def make_zip():
    files = []
    for sub in ("v12_runs", "v12_series", "v12_logs", "v12_checks_laptop"):
        files += [f for f in glob.glob(os.path.join(RES, sub, "*")) if not f.endswith(".claim") and ".tmp" not in f]
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(f, os.path.relpath(f, REPO))
    print(f"{utc()} {len(files)} files zipped into {ZIP}")


def main():
    sys.path.insert(0, HERE)
    import v12_run
    total = len(v12_run.build_runs())
    tot, avail = mem_gb()
    print(f"Stage 5 on this computer: {os.cpu_count()} logical processors, {tot:.1f} GB memory ({avail:.1f} GB free).")
    if os.path.exists(LOCK):
        old = json.load(open(LOCK))
        lim = worker_start_limits(old)
        if any(alive(p, lim.get(p)) for p in old["pids"]):
            print("Workers from an earlier start are still running; showing their progress.")
            monitor(old["pids"], total)
            make_zip()
            return 0
    if not check():
        return 1
    want = int(os.environ.get("V12_WORKERS", os.cpu_count() or 1))            # D47 (4): the restart asks for 24
    per = float(os.environ.get("V12_GB_PER_WORKER", GB_PER_WORKER))
    n = max(1, min(want, int((avail - 2.0) / per)))
    print(f"{n} workers ({want} asked for; {per:.2f} GB allowed each, {avail:.1f} GB free).")
    if os.path.exists(v12_run.STOP_FILE):
        os.remove(v12_run.STOP_FILE)
    pids = launch(n)
    done = monitor(pids, total)
    make_zip()
    print(f"{done} of {total} runs recorded. Tell Claude the runs have finished.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
