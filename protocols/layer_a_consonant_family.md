# Layer A — Dominant Consonant-Unit Recurrence

## 1. Objective

This layer measures persistence of locally dominant consonant units across neighboring sliding windows.

Signal:

> stability of top-N consonant units across local windows

---

## 2. Input

Phonetic corpora (`*_phonetic.txt`)

- whitespace-separated tokens  
- boundary marker: `|`  

Baseline set:

- genesis_phonetic.txt  
- exodus_phonetic.txt  
- leviticus_phonetic.txt  
- numbers_phonetic.txt  
- deuteronomy_phonetic.txt  
- hagamad_phonetic.txt  

---

## 3. Representation

### Atomic units

- single consonants  
- digraphs: sh, kh, ts (atomic)  

Tokenization:

- left-to-right  
- digraph priority  

Vowels removed:

- a e i o u  

---

## 4. Consonant stream

Each corpus becomes:

t1, t2, ..., tn

---

## 5. Boundary handling

Baseline:

- respect_boundaries = 0  
- `|` removed  
- one continuous stream  

---

## 6. Windowing

Baseline:

- W = 150  
- step = 25  

Windows shorter than W are ignored.

---

## 7. Local profile

Per window:

- count frequencies  
- rank by:  
  1. descending frequency  
  2. alphabetical tie-break  
- keep top_n atoms  

Baseline:

- top_n = 3  

---

## 8. Recurrence metric

overlap(wi, wj) = |topN(wi) ∩ topN(wj)|

Range:

0 .. top_n

---

## 9. Aggregated metrics

### Global recurrence (weighted)

- lags 1..max_lag  
- weighted by number of pairs  

### Short-lag recurrence (weighted)

- lags 1..short_lag_to  

### Lag profile (unweighted)

- mean overlap per lag  

### Best lag

- maximal observed overlap (descriptive)  

---

## 10. Null model

Block permutation:

- split into blocks of size `block`  
- shuffle blocks  
- preserve order inside each block  
- trailing remainder is kept in place  

If respect_boundaries = 0:

- whole corpus = one segment  

Baseline:

- block = 80  
- perm = 1000  
- seed = 1  

---

## 11. Statistics

Z = (obs − mean_null) / sd_null

Population SD.

---

## 12. Baseline run

Parameters:

- W = 150  
- step = 25  
- top_n = 3  
- max_lag = 20  
- short_lag_to = 5  
- block = 80  
- perm = 1000  
- seed = 1  
- respect_boundaries = 0  

---

## 13. Stress tests

Run independently (same file set):

### Window size

- W = 100 (tag: w100)  
- W = 200 (tag: w200)  

### Top-N

- top_n = 2 (tag: top2)  
- top_n = 4 (tag: top4)  

### Null block size

- block = 50 (tag: block50)  
- block = 120 (tag: block120)  

All other parameters unchanged.

---

## 14. Outputs

Per corpus:

- books/<corpus>/layer_a_<tag>_summary.csv  
- books/<corpus>/layer_a_<tag>_lag_profile.csv  

Combined:

- layer_a_<tag>_summary_all.csv  
- layer_a_<tag>_lag_profile_all.csv  
- layer_a_<tag>_important_summary.csv  
- layer_a_<tag>_run_manifest.json  

---

## 15. Interpretation

Positive Z indicates persistence of dominant consonant units beyond local block structure.

---

## 16. Limitations

Does not detect:

- unordered consonant clusters  
- phonetic chains  
- equivalence classes  
- long-range compositional structures  