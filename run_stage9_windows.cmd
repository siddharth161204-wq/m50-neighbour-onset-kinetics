@echo off
rem Stage 9 on Windows (DECISIONS.md D96 (1)). This repository sits in <folder>\repo, with Python unpacked in
rem <folder>\python, as for Stages 5 to 7. It asks for 24 workers at 0.6 GB each (D47 (4)).
setlocal
cd /d "%~dp0src"
set PYTHONUTF8=1
set STAGE9_WORKERS=24
set STAGE9_GB_PER_WORKER=0.6
"%~dp0..\python\python.exe" stage9_laptop.py
echo.
pause
