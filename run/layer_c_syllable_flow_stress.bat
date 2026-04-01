@echo off
echo === Layer C1 stress ===

for %%L in (10 20 40) do (
  for %%B in (50 80) do (

    python src\analyses\layer_c\layer_c_syllable_flow.py data\data_processed\torah\genesis_phonetic.txt data\data_processed\modern\hagamad_phonetic.txt --mode permissive --L %%L --block %%B --perm 200 --seed 1 --out_root results\layer_c_syllable_flow --tag stress_L%%L_B%%B

  )
)

pause