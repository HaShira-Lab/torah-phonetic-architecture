@echo off
cd /d D:\HaShira-Lab\torah-phonetic-architecture

echo === layer_c_window_density_stress (analysis) ===

set PY=python
set SCRIPT=src\analyses\layer_c\layer_c_window_density.py

echo === --L 40 --W 1000 --step 500 ===
%PY% %SCRIPT% data\data_processed\torah\Genesis_phonetic.txt data\data_processed\torah\Exodus_phonetic.txt data\data_processed\torah\Leviticus_phonetic.txt data\data_processed\torah\Numbers_phonetic.txt data\data_processed\torah\Deuteronomy_phonetic.txt data\data_processed\modern\HaGamad_phonetic.txt --L 40 --W 1000 --step 500 --out_root results\layer_c_window_density --tag stress_L40

echo === --L 120 --W 1000 --step 500 ===
%PY% %SCRIPT% data\data_processed\torah\Genesis_phonetic.txt data\data_processed\torah\Exodus_phonetic.txt data\data_processed\torah\Leviticus_phonetic.txt data\data_processed\torah\Numbers_phonetic.txt data\data_processed\torah\Deuteronomy_phonetic.txt data\data_processed\modern\HaGamad_phonetic.txt --L 120 --W 1000 --step 500 --out_root results\layer_c_window_density --tag stress_L120

echo === --L 80 --W 800 --step 400 ===
%PY% %SCRIPT% data\data_processed\torah\Genesis_phonetic.txt data\data_processed\torah\Exodus_phonetic.txt data\data_processed\torah\Leviticus_phonetic.txt data\data_processed\torah\Numbers_phonetic.txt data\data_processed\torah\Deuteronomy_phonetic.txt data\data_processed\modern\HaGamad_phonetic.txt --L 80 --W 800 --step 400 --out_root results\layer_c_window_density --tag stress_W800

echo === --L 80 --W 1500 --step 750 ===
%PY% %SCRIPT% data\data_processed\torah\Genesis_phonetic.txt data\data_processed\torah\Exodus_phonetic.txt data\data_processed\torah\Leviticus_phonetic.txt data\data_processed\torah\Numbers_phonetic.txt data\data_processed\torah\Deuteronomy_phonetic.txt data\data_processed\modern\HaGamad_phonetic.txt --L 80 --W 1500 --step 750 --out_root results\layer_c_window_density --tag stress_W1500


pause