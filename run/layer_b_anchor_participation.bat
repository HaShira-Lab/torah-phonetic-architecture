@echo off
setlocal

echo === layer b anchor participation ===

set SCRIPT=src\analyses\layer_b\layer_b_anchor_participation.py
set OUTDIR=results\layer_b_anchor_participation

python %SCRIPT% ^
  data\data_processed\torah\genesis_phonetic.txt data\data_processed\torah\exodus_phonetic.txt data\data_processed\torah\leviticus_phonetic.txt data\data_processed\torah\numbers_phonetic.txt data\data_processed\torah\deuteronomy_phonetic.txt data\data_processed\modern\hagamad_phonetic.txt --out_dir %OUTDIR% --tag baseline --mode exact --block 80 --perm 1000 --seed 1

if errorlevel 1 (
  echo FAILED
  pause
  exit /b 1
)

echo DONE
pause