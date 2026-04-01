@echo off
setlocal

echo === layer a consonant family / baseline ===

set SCRIPT=src\analyses\layer_a\layer_a_consonant_family.py
set OUTDIR=results\layer_a_consonant_family

python %SCRIPT% data\data_processed\torah\genesis_phonetic.txt data\data_processed\torah\exodus_phonetic.txt data\data_processed\torah\leviticus_phonetic.txt data\data_processed\torah\numbers_phonetic.txt data\data_processed\torah\deuteronomy_phonetic.txt data\data_processed\modern\hagamad_phonetic.txt --out_dir %OUTDIR% --tag baseline --W 150 --step 25 --top_n 3 --max_lag 20 --short_lag_to 5 --block 80 --perm 1000 --seed 1 --respect_boundaries 0

if errorlevel 1 (
  echo.
  echo failed
  pause
  exit /b 1
)

echo.
echo done
pause