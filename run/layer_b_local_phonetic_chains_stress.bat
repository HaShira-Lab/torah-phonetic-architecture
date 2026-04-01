@echo off
setlocal

echo === layer b local phonetic chains / stress ===

set SCRIPT=src\analyses\layer_b\layer_b_local_phonetic_chains.py
set BASE=results\layer_b_local_phonetic_chains\stress

set FILES=data\data_processed\torah\genesis_phonetic.txt data\data_processed\torah\exodus_phonetic.txt data\data_processed\torah\leviticus_phonetic.txt data\data_processed\torah\numbers_phonetic.txt data\data_processed\torah\deuteronomy_phonetic.txt data\data_processed\modern\hagamad_phonetic.txt

python %SCRIPT% %FILES% --out_dir %BASE% --tag k2 --k 2 --mode exact --block 80 --perm 1000 --seed 1
if errorlevel 1 exit /b 1

python %SCRIPT% %FILES% --out_dir %BASE% --tag k4 --k 4 --mode exact --block 80 --perm 1000 --seed 1
if errorlevel 1 exit /b 1

python %SCRIPT% %FILES% --out_dir %BASE% --tag equiv_k3 --k 3 --mode equiv --block 80 --perm 1000 --seed 1
if errorlevel 1 exit /b 1

python %SCRIPT% %FILES% --out_dir %BASE% --tag block40 --k 3 --mode exact --block 40 --perm 1000 --seed 1
if errorlevel 1 exit /b 1

python %SCRIPT% %FILES% --out_dir %BASE% --tag block120 --k 3 --mode exact --block 120 --perm 1000 --seed 1
if errorlevel 1 exit /b 1

python %SCRIPT% data\data_processed\torah\genesis_phonetic.txt data\data_processed\modern\hagamad_phonetic.txt --out_dir %BASE% --tag k5_appendix --k 5 --mode exact --block 80 --perm 1000 --seed 1
if errorlevel 1 exit /b 1

echo DONE
pause