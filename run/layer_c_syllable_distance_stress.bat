@echo off
echo === Layer C1.2 stress ===

for %%B in (50 80) do (
  python src\analyses\layer_c\layer_c_syllable_distance.py data\data_processed\torah\genesis_phonetic.txt data\data_processed\modern\hagamad_phonetic.txt --mode permissive --L 20 --Dmax 40 --block %%B --perm 200 --seed 1 --out_root results\layer_c_syllable_distance --tag stress_B%%B
)

pause