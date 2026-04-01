@echo off
setlocal

echo === PHONETIC PREPROCESSING (LOCKED MODEL) ===

set SCRIPT=src\preprocessing\preprocessing_phonetic.py

set TORAH_IN=data\data_raw\torah
set MODERN_IN=data\data_raw\modern

set TORAH_OUT=data\data_processed\torah
set MODERN_OUT=data\data_processed\modern

if not exist %TORAH_OUT% mkdir %TORAH_OUT%
if not exist %MODERN_OUT% mkdir %MODERN_OUT%

REM ===== Torah =====
for %%f in (%TORAH_IN%\*.txt) do (
    set "name=%%~nf"
    setlocal enabledelayedexpansion
    set "base=!name:_raw=!"
    python %SCRIPT% "%%f" "%TORAH_OUT%\!base!_phonetic.txt" torah
    endlocal
)

REM ===== Modern =====
for %%f in (%MODERN_IN%\*.txt) do (
    set "name=%%~nf"
    setlocal enabledelayedexpansion
    set "base=!name:_raw=!"
    python %SCRIPT% "%%f" "%MODERN_OUT%\!base!_phonetic.txt" modern
    endlocal
)

echo DONE
pause