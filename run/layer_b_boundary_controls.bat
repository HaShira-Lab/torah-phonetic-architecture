@echo off
setlocal

echo === layer b boundary controls ===

set SCRIPT=src\analyses\layer_b\layer_b_boundary_controls.py
set OUT=results\layer_b_boundary_controls

python %SCRIPT% data\data_processed\torah\genesis_phonetic.txt data\data_processed\torah\exodus_phonetic.txt data\data_processed\torah\leviticus_phonetic.txt data\data_processed\torah\numbers_phonetic.txt data\data_processed\torah\deuteronomy_phonetic.txt data\data_processed\modern\hagamad_phonetic.txt --out_dir %OUT% --tag baseline --k 3 --perm 1000 --seed 1

pause