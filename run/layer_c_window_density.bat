@echo off
echo === Layer C6 window density ===

python src\analyses\layer_c\layer_c_window_density.py data\data_processed\torah\genesis_phonetic.txt data\data_processed\torah\exodus_phonetic.txt data\data_processed\torah\leviticus_phonetic.txt data\data_processed\torah\numbers_phonetic.txt data\data_processed\torah\deuteronomy_phonetic.txt data\data_processed\modern\hagamad_phonetic.txt --L 20 --W 800 --step 200 --block 50 --perm 200 --seed 1 --mode permissive --threshold 0.15 --smooth 5 --out_root results\layer_c_window_density --tag baseline

pause