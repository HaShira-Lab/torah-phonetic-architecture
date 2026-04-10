@echo off
cd /d D:\HaShira-Lab\torah-phonetic-architecture

echo === layer_c_window_density (analysis) ===

set PY=python
set SCRIPT=src\analyses\layer_c\layer_c_window_density.py

%PY% %SCRIPT% data\data_processed\torah\Genesis_phonetic.txt data\data_processed\torah\Exodus_phonetic.txt data\data_processed\torah\Leviticus_phonetic.txt data\data_processed\torah\Numbers_phonetic.txt data\data_processed\torah\Deuteronomy_phonetic.txt data\data_processed\modern\HaGamad_phonetic.txt --L 80 --W 1000 --step 500 --out_root results\layer_c_window_density --tag baseline

pause