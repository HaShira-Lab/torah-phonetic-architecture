@echo off
echo === Layer C6 stress ===

python src\analyses\layer_c\layer_c_window_density.py data\data_processed\torah\genesis_phonetic.txt data\data_processed\modern\hagamad_phonetic.txt --L 20 --W 1000 --step 200 --block 80 --perm 200 --seed 1 --mode permissive --threshold 0.15 --smooth 5 --out_root results\layer_c_window_density --tag stress

pause