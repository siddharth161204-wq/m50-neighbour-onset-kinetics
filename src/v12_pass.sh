#!/bin/bash
# One pass of the Stage 5 runs (D43): both workers, one thread per library each, for at most 118 minutes.
# Each worker skips recorded runs, so passes are repeated until `python3 v12_run.py status` shows every set done.
# Logs: results/v12_logs/pass_<UTC start>_w<k>.log, one timestamped line per run.
cd "$(dirname "$0")" || exit 1
export OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1
stamp=$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p ../results/v12_logs
python3 v12_run.py work --worker 0 --of 2 --budget-min 117 --wall-min 118 > "../results/v12_logs/pass_${stamp}_w0.log" 2>&1 &
p0=$!
python3 v12_run.py work --worker 1 --of 2 --budget-min 117 --wall-min 118 > "../results/v12_logs/pass_${stamp}_w1.log" 2>&1 &
p1=$!
wait $p0; e0=$?
wait $p1; e1=$?
echo "pass ${stamp}: worker 0 exit ${e0}, worker 1 exit ${e1}, ended $(date -u +%H:%M:%SZ)"
grep -c ': resolved ' "../results/v12_logs/pass_${stamp}_w0.log" "../results/v12_logs/pass_${stamp}_w1.log"
grep -h 'FAILED\|interrupted\|Traceback\|Error' "../results/v12_logs/pass_${stamp}_w0.log" "../results/v12_logs/pass_${stamp}_w1.log" | head -5
tail -n 1 "../results/v12_logs/pass_${stamp}_w0.log" "../results/v12_logs/pass_${stamp}_w1.log"
python3 v12_run.py status
