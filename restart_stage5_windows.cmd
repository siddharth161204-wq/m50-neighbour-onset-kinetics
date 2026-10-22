@echo off
rem Stage 5 on Windows: restarts the workers with the corrected code (DECISIONS.md D47). This repository sits
rem in <folder>\repo, with Python unpacked in <folder>\python.
setlocal
cd /d "%~dp0src"
set PYTHONUTF8=1
"%~dp0..\python\python.exe" v12_laptop_restart.py
echo.
pause
