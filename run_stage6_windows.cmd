@echo off
rem Stage 6, Part B on Windows (DECISIONS.md D55 (5)). This repository sits in <folder>\repo, with Python
rem unpacked in <folder>\python, as for Stage 5. It asks for 24 workers at 0.6 GB each (D47 (4)).
setlocal
cd /d "%~dp0src"
set PYTHONUTF8=1
set V12_WORKERS=24
set V12_GB_PER_WORKER=0.6
"%~dp0..\python\python.exe" stage6_laptop.py
echo.
pause
