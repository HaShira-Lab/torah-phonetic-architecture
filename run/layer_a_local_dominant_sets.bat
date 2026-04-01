@echo off
setlocal

echo === layer a+ dominant sets / baseline ===

set SCRIPT=src\analyses\layer_a\layer_a_local_dominant_sets.py
set OUTDIR=results\layer_a_local_dominant_sets

python %SCRIPT% data\data_processed\torah\genesis_phonetic.txt data\data_processed\torah\exodus_phonetic.txt data\data_processed\torah\leviticus_phonetic.txt data\data_processed\torah\numbers_phonetic.txt data\data_processed\torah\deuteronomy_phonetic.txt data\data_processed\modern\hagamad_phonetic.txt --out_dir %OUTDIR% --tag baseline --L 150 --mode topk --k 3 --max_lag 10 --R 5 --min_jaccard 0.5 --block 80 --perm 1000 --seed 1

if errorlevel 1 (
  echo FAILED
  pause
  exit /b 1
)

echo DONE
pause