@echo off
echo === Layer C2 stress ===

python src\analyses\layer_c\layer_c_word_final.py data\data_processed\torah\genesis_phonetic.txt data\data_processed\modern\hagamad_phonetic.txt --L 40 --block 80 --perm 200 --seed 1 --out_root results\layer_c_word_final --tag stress_block80

python src\analyses\layer_c\layer_c_word_final.py data\data_processed\torah\genesis_phonetic.txt data\data_processed\modern\hagamad_phonetic.txt --L 40 --block 50 --perm 200 --seed 1 --eq_kh_k 1 --eq_ts_s 1 --out_root results\layer_c_word_final --tag stress_equiv

pause