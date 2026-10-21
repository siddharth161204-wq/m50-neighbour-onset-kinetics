@echo off
rem Stage 5 on Windows (DECISIONS.md D45). This repository sits in <folder>\repo, with <folder>\wheels and the
rem Python archive <folder>\cpython-3.13.16-windows.tar.gz beside it.
setlocal
cd /d "%~dp0"
set "BUNDLE=%~dp0.."
set PYTHONUTF8=1
if not exist "%BUNDLE%\python\python.exe" (
  echo Unpacking Python 3.13.16 ...
  tar -xzf "%BUNDLE%\cpython-3.13.16-windows.tar.gz" -C "%BUNDLE%" || goto :fail
)
if not exist "%BUNDLE%\python\stage5_packages.txt" (
  echo Installing the pinned packages from the wheels folder ...
  "%BUNDLE%\python\python.exe" -m pip --version >nul 2>&1 || "%BUNDLE%\python\python.exe" -m ensurepip || goto :fail
  "%BUNDLE%\python\python.exe" -m pip install --no-index --find-links "%BUNDLE%\wheels" -r requirements_windows.txt || goto :fail
  "%BUNDLE%\python\python.exe" -m pip freeze > "%BUNDLE%\python\stage5_packages.txt"
)
cd src
"%BUNDLE%\python\python.exe" v12_laptop.py
echo.
pause
exit /b 0
:fail
echo Setup failed. Leave this window open and tell Claude.
pause
exit /b 1
