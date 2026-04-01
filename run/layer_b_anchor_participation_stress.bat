@echo off
setlocal

echo === layer b anchor participation / stress ===

set SCRIPT=src\analyses\layer_b\layer_b_anchor_participation.py
set BASE=results\layer_b_anchor_participation\stress

set FILES=data\data_processed\torah\genesis_phonetic.txt data\data_processed\torah\exodus_phonetic.txt data\data_processed\torah\leviticus_phonetic.txt data\data_processed\torah\numbers_phonetic.txt data\data_processed\torah\deuteronomy_phonetic.txt data\data_processed\modern\hagamad_phonetic.txt

python %SCRIPT% %FILES% --out_dir %BASE% --tag equiv --mode equiv --block 80 --perm 1000 --seed 1
if errorlevel 1 exit /b 1

python %SCRIPT% %FILES% --out_dir %BASE% --tag block40 --mode exact --block 40 --perm 1000 --seed 1
if errorlevel 1 exit /b 1

python %SCRIPT% %FILES% --out_dir %BASE% --tag block120 --mode exact --block 120 --perm 1000 --seed 1
if errorlevel 1 exit /b 1

echo DONE
pause