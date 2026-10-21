#!/usr/bin/env python3
"""Adds workers to the running Stage 5 pass on Windows and lets every worker use the fast cores (DECISIONS.md D46).

Windows can run background processes in its efficiency mode (EcoQoS: the efficient cores, at lower clocks). This
turns that mode off for the running workers (results/v12_laptop_workers.json) and starts more, as many as there are
idle logical processors and as the free memory allows (1.3 times the largest running worker's memory each), in the
same queue (v12_run.py work --queue), detached, at below-normal priority. Nothing a run computes changes.
Started by add_workers.cmd beside the repository.
"""
import ctypes, json, os, subprocess, sys, time
from ctypes import wintypes

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.normpath(os.path.join(HERE, "..", "results"))
LOCK = os.path.join(RES, "v12_laptop_workers.json")
LOGS = os.path.join(RES, "v12_logs")
ENV = dict(os.environ, OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", OMP_NUM_THREADS="1", NUMBA_NUM_THREADS="1",
           PYTHONUTF8="1")
K32 = ctypes.windll.kernel32
PSAPI = ctypes.windll.psapi
BELOW = subprocess.BELOW_NORMAL_PRIORITY_CLASS
DETACHED = 0x00000008 | subprocess.CREATE_NEW_PROCESS_GROUP
SET_INFO, QUERY_LIMITED, VM_READ, QUERY = 0x0200, 0x1000, 0x0010, 0x0400


class Throttle(ctypes.Structure):
    _fields_ = [("Version", wintypes.ULONG), ("ControlMask", wintypes.ULONG), ("StateMask", wintypes.ULONG)]


class MemCounters(ctypes.Structure):
    _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD), ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t), ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t), ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t), ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t)]


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def alive(pid):
    h = K32.OpenProcess(QUERY_LIMITED, False, pid)
    if not h:
        return False
    code = wintypes.DWORD()
    ok = K32.GetExitCodeProcess(h, ctypes.byref(code))
    K32.CloseHandle(h)
    return bool(ok) and code.value == 259


def no_ecoqos(pid):
    """PROCESS_POWER_THROTTLING_EXECUTION_SPEED in the control mask and 0 in the state: efficiency mode off."""
    h = K32.OpenProcess(SET_INFO | QUERY_LIMITED, False, pid)
    if not h:
        return False
    s = Throttle(1, 1, 0)
    ok = K32.SetProcessInformation(h, 4, ctypes.byref(s), ctypes.sizeof(s))      # ProcessPowerThrottling
    K32.CloseHandle(h)
    return bool(ok)


def working_set_gb(pid):
    h = K32.OpenProcess(QUERY | VM_READ, False, pid)
    if not h:
        return None
    m = MemCounters()
    m.cb = ctypes.sizeof(MemCounters)
    ok = PSAPI.GetProcessMemoryInfo(h, ctypes.byref(m), m.cb)
    K32.CloseHandle(h)
    return m.PeakWorkingSetSize / 2 ** 30 if ok else None


def free_gb():
    sys.path.insert(0, HERE)
    import v12_laptop
    return v12_laptop.mem_gb()[1]


def main():
    lock = json.load(open(LOCK))
    pids = [p for p in lock["pids"] if alive(p)]
    off = sum(no_ecoqos(p) for p in pids)
    print(f"{utc()} {len(pids)} workers running; efficiency mode turned off for {off}.")
    sizes = [s for s in (working_set_gb(p) for p in pids) if s]
    per = 1.3 * max(sizes) if sizes else 1.0
    avail = free_gb()
    n_new = max(0, min((os.cpu_count() or 1) - len(pids), int((avail - 2.0) / per)))
    print(f"Largest worker {max(sizes) if sizes else float('nan'):.2f} GB; {avail:.1f} GB free; starting {n_new} more.")
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    new = []
    for k in range(n_new):
        w = len(lock["pids"]) + k
        p = subprocess.Popen([sys.executable, "v12_run.py", "work", "--queue", "--label", "author-laptop",
                              "--worker", str(w), "--of", str(w + 1), "--budget-min", "1e9", "--wall-min", "1e9"],
                             cwd=HERE, env=ENV, stdout=open(os.path.join(LOGS, f"laptop_{stamp}_w{w:02d}.log"), "w"),
                             stderr=subprocess.STDOUT, creationflags=BELOW | DETACHED)
        new.append(p.pid)
    time.sleep(2)
    off_new = sum(no_ecoqos(p) for p in new)
    lock["pids"] += new
    lock.setdefault("added", []).append({"utc": utc(), "pids": new, "ecoqos_off": off + off_new,
                                         "per_worker_gb": per, "free_gb": avail})
    json.dump(lock, open(LOCK, "w"), indent=1)
    print(f"{utc()} {len(new)} workers added (efficiency mode off for {off_new}); {len(pids) + len(new)} in all.")
    print("This window can be closed. Leave the first one open: it keeps the laptop awake and shows the progress.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
