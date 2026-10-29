@echo off
rem Stage 9 on Windows (DECISIONS.md D98 (2)): leaves the running workers as they are and, for each worker that has
rem stopped with an error, starts one with the code as it now stands; while this window is open it does the same for
rem any later one, frees the claims of workers no longer running and keeps the computer awake. This repository sits
rem in <folder>\repo, with Python unpacked in <folder>\python, as for Stages 5 to 7.
setlocal
cd /d "%~dp0src"
set PYTHONUTF8=1
set STAGE9_GB_PER_WORKER=0.6
"%~dp0..\python\python.exe" stage9_laptop.py --add
echo.
pause
