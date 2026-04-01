@echo off
echo === Layer C1 baseline ===

python src\analyses\layer_c\layer_c_syllable_flow.py data\data_processed\torah\genesis_phonetic.txt data\data_processed\torah\exodus_phonetic.txt data\data_processed\torah\leviticus_phonetic.txt data\data_processed\torah\numbers_phonetic.txt data\data_processed\torah\deuteronomy_phonetic.txt data\data_processed\modern\hagamad_phonetic.txt --mode permissive --L 20 --block 50 --perm 200 --seed 1 --out_root results\layer_c_syllable_flow --tag baseline

pause