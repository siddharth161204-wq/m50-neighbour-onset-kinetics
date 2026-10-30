@echo off
rem Stage 10 on Windows (DECISIONS.md D106 (1)). This repository sits in <folder>\repo9 (or repo), with Python unpacked
rem in <folder>\python, as for Stages 5 to 9. It asks for 24 workers at 0.6 GB each (D47 (4)).
setlocal
cd /d "%~dp0src"
set PYTHONUTF8=1
set STAGE10_WORKERS=24
set STAGE10_GB_PER_WORKER=0.6
"%~dp0..\python\python.exe" stage10_laptop.py
echo.
pause
