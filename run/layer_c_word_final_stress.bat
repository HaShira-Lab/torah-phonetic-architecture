@echo off
echo === Layer C3 stress ===

for %%L in (20 40) do (
  for %%B in (50 80) do (

    python src\analyses\layer_c\layer_c_word_final.py data\data_processed\torah\genesis_phonetic.txt data\data_processed\torah\exodus_phonetic.txt data\data_processed\torah\leviticus_phonetic.txt data\data_processed\torah\numbers_phonetic.txt data\data_processed\torah\deuteronomy_phonetic.txt data\data_processed\modern\hagamad_phonetic.txt --L %%L --block %%B --perm 200 --seed 1 --out_root results\layer_c_word_final --tag stress_L%%L_B%%B

  )
)

pause