@echo off
rem Stage 5 on Windows: restarts the workers with the corrected code (DECISIONS.md D47). This repository sits
rem in <folder>\repo, with Python unpacked in <folder>\python. It asks for 24 workers at 0.6 GB each (D47 (4)).
setlocal
cd /d "%~dp0src"
set PYTHONUTF8=1
set V12_WORKERS=24
set V12_GB_PER_WORKER=0.6
"%~dp0..\python\python.exe" v12_laptop_restart.py
echo.
pause
