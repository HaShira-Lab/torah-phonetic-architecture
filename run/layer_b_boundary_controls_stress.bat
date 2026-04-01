@echo off
setlocal

echo === layer b boundary controls / stress ===

set SCRIPT=src\analyses\layer_b\layer_b_boundary_controls.py
set BASE=results\layer_b_boundary_controls\stress

set FILES=data\data_processed\torah\genesis_phonetic.txt data\data_processed\torah\exodus_phonetic.txt data\data_processed\torah\leviticus_phonetic.txt data\data_processed\torah\numbers_phonetic.txt data\data_processed\torah\deuteronomy_phonetic.txt data\data_processed\modern\hagamad_phonetic.txt

REM --- k=2 (short chains)
python %SCRIPT% %FILES% --out_dir %BASE% --tag k2 --k 2 --perm 1000 --seed 1
if errorlevel 1 exit /b 1

REM --- k=4 (longer chains)
python %SCRIPT% %FILES% --out_dir %BASE% --tag k4 --k 4 --perm 1000 --seed 1
if errorlevel 1 exit /b 1

REM --- fewer permutations (stability check)
python %SCRIPT% %FILES% --out_dir %BASE% --tag perm200 --k 3 --perm 200 --seed 1
if errorlevel 1 exit /b 1

echo DONE
pause