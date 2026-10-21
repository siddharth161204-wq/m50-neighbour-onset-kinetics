@echo off
rem Stage 5 on Windows: adds workers to the running pass and lets every worker use the fast cores
rem (DECISIONS.md D46). This repository sits in <folder>\repo, with Python unpacked in <folder>\python.
setlocal
cd /d "%~dp0src"
set PYTHONUTF8=1
"%~dp0..\python\python.exe" v12_laptop_more.py
echo.
pause
