@echo off
setlocal

echo === layer a consonant family / stress ===

set SCRIPT=src\analyses\layer_a\layer_a_consonant_family.py
set BASE=results\layer_a_consonant_family\stress

set FILES=data\data_processed\torah\genesis_phonetic.txt data\data_processed\torah\exodus_phonetic.txt data\data_processed\torah\leviticus_phonetic.txt data\data_processed\torah\numbers_phonetic.txt data\data_processed\torah\deuteronomy_phonetic.txt data\data_processed\modern\hagamad_phonetic.txt

python %SCRIPT% %FILES% --out_dir %BASE% --tag w100 --W 100 --step 25 --top_n 3 --max_lag 20 --short_lag_to 5 --block 80 --perm 1000 --seed 1 --respect_boundaries 0
if errorlevel 1 exit /b 1

python %SCRIPT% %FILES% --out_dir %BASE% --tag w200 --W 200 --step 25 --top_n 3 --max_lag 20 --short_lag_to 5 --block 80 --perm 1000 --seed 1 --respect_boundaries 0
if errorlevel 1 exit /b 1

python %SCRIPT% %FILES% --out_dir %BASE% --tag top2 --W 150 --step 25 --top_n 2 --max_lag 20 --short_lag_to 5 --block 80 --perm 1000 --seed 1 --respect_boundaries 0
if errorlevel 1 exit /b 1

python %SCRIPT% %FILES% --out_dir %BASE% --tag top4 --W 150 --step 25 --top_n 4 --max_lag 20 --short_lag_to 5 --block 80 --perm 1000 --seed 1 --respect_boundaries 0
if errorlevel 1 exit /b 1

python %SCRIPT% %FILES% --out_dir %BASE% --tag block50 --W 150 --step 25 --top_n 3 --max_lag 20 --short_lag_to 5 --block 50 --perm 1000 --seed 1 --respect_boundaries 0
if errorlevel 1 exit /b 1

python %SCRIPT% %FILES% --out_dir %BASE% --tag block120 --W 150 --step 25 --top_n 3 --max_lag 20 --short_lag_to 5 --block 120 --perm 1000 --seed 1 --respect_boundaries 0
if errorlevel 1 exit /b 1

echo.
echo done
pause