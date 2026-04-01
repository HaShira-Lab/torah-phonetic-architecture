@echo off
echo === Layer C2 baseline ===

python src\analyses\layer_c\layer_c_word_final.py data\data_processed\torah\genesis_phonetic.txt data\data_processed\torah\exodus_phonetic.txt data\data_processed\torah\leviticus_phonetic.txt data\data_processed\torah\numbers_phonetic.txt data\data_processed\torah\deuteronomy_phonetic.txt data\data_processed\modern\hagamad_phonetic.txt --L 40 --block 50 --perm 200 --seed 1 --out_root results\layer_c_word_final --tag baseline

pause