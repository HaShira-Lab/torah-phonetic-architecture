@echo off
setlocal

echo === layer a+ dominant sets / stress ===

set SCRIPT=src\analyses\layer_a\layer_a_local_dominant_sets.py
set BASE=results\layer_a_local_dominant_sets\stress

set FILES=data\data_processed\torah\genesis_phonetic.txt data\data_processed\torah\exodus_phonetic.txt data\data_processed\torah\leviticus_phonetic.txt data\data_processed\torah\numbers_phonetic.txt data\data_processed\torah\deuteronomy_phonetic.txt data\data_processed\modern\hagamad_phonetic.txt

:: segment size
python %SCRIPT% %FILES% --out_dir %BASE% --tag L100 --L 100 --mode topk --k 3 --max_lag 10 --R 5 --min_jaccard 0.5 --block 80 --perm 1000 --seed 1
if errorlevel 1 exit /b 1

python %SCRIPT% %FILES% --out_dir %BASE% --tag L200 --L 200 --mode topk --k 3 --max_lag 10 --R 5 --min_jaccard 0.5 --block 80 --perm 1000 --seed 1
if errorlevel 1 exit /b 1

:: k
python %SCRIPT% %FILES% --out_dir %BASE% --tag k2 --L 150 --mode topk --k 2 --max_lag 10 --R 5 --min_jaccard 0.5 --block 80 --perm 1000 --seed 1
if errorlevel 1 exit /b 1

python %SCRIPT% %FILES% --out_dir %BASE% --tag k4 --L 150 --mode topk --k 4 --max_lag 10 --R 5 --min_jaccard 0.5 --block 80 --perm 1000 --seed 1
if errorlevel 1 exit /b 1

:: block
python %SCRIPT% %FILES% --out_dir %BASE% --tag block50 --L 150 --mode topk --k 3 --max_lag 10 --R 5 --min_jaccard 0.5 --block 50 --perm 1000 --seed 1
if errorlevel 1 exit /b 1

python %SCRIPT% %FILES% --out_dir %BASE% --tag block120 --L 150 --mode topk --k 3 --max_lag 10 --R 5 --min_jaccard 0.5 --block 120 --perm 1000 --seed 1
if errorlevel 1 exit /b 1

echo DONE
pause