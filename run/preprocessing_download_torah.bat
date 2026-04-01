@echo off
setlocal

echo === PREPROCESSING: DOWNLOAD TORAH RAW ===

set SCRIPT=src\preprocessing\download_torah.py
set OUTDIR=data\data_raw\torah

python %SCRIPT% ^
  --books Genesis Exodus Leviticus Numbers Deuteronomy ^
  --outdir %OUTDIR%

if errorlevel 1 (
  echo.
  echo FAILED
  pause
  exit /b 1
)

echo.
echo DONE
pause