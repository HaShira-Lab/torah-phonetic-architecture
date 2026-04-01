@echo off
echo === Layer C4 stress ===

python src\analyses\layer_c\layer_c_phrase_final.py data\data_processed\torah\genesis_phonetic.txt data\data_processed\modern\hagamad_phonetic.txt --R 10 --block 50 --perm 200 --seed 1 --out_root results\layer_c_phrase_final --tag stress_block50

python src\analyses\layer_c\layer_c_phrase_final.py data\data_processed\torah\genesis_phonetic.txt data\data_processed\modern\hagamad_phonetic.txt --R 10 --block 20 --perm 200 --seed 1 --eq_kh_k 1 --eq_ts_s 1 --out_root results\layer_c_phrase_final --tag stress_equiv

pause