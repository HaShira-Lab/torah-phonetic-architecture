# Layer A+ — Local Dominant Consonant Sets (LDCS)

## 1. Objective

This layer measures:

> stability of locally dominant consonant sets in non-overlapping segments

Hypothesis:

> the text exhibits stable local phonetic regimes beyond block-permutation expectations.

---

## 2. Input

Phonetic corpora (`*_phonetic.txt`)

- whitespace-separated tokens  
- boundary marker `|` removed  

Baseline corpus set:

- genesis_phonetic.txt  
- exodus_phonetic.txt  
- leviticus_phonetic.txt  
- numbers_phonetic.txt  
- deuteronomy_phonetic.txt  
- hagamad_phonetic.txt  

---

## 3. Phonetic Representation

- digraphs treated as atomic: sh, kh, ts  
- tokenization is left-to-right with digraph priority  
- vowels removed: a, e, i, o, u  

Result:

- continuous consonant stream  

---

## 4. Segmentation

- non-overlapping segments  

Procedure:

- stream → segments of size L  
- trailing remainder is discarded  

---

## 5. Dominant Set Construction

Mode: `topk` (baseline)

Per segment:

- count consonant frequencies  
- rank by:  
  1. descending frequency  
  2. alphabetical tie-break  
- select top-k consonants  
- sort alphabetically  

Result:

dominant_set(segment) = unordered set

Baseline:

- k = 3  

---

## 6. Metrics

### 6.1 Adjacent Jaccard (primary)

J(Sᵢ, Sᵢ₊₁)

Metric:

- mean adjacent Jaccard  

---

### 6.2 Lag Profile

For lags 1..max_lag:

- mean Jaccard  
- null mean  
- null sd  
- Z-score  
- number of pairs  

Baseline:

- max_lag = 10  

---

### 6.3 Dominance Mass

Fraction of segment covered by dominant set:

- mean over segments  

---

### 6.4 Recurrence

For each segment i:

- check if a similar dominant set appears within next R segments  

Condition:

- Jaccard ≥ min_jaccard  

Metric:

- fraction of segments with recurrence  

Baseline:

- R = 5  
- min_jaccard = 0.5  

---

## 7. Null Model

Block permutation:

- split stream into blocks of size `block`  
- shuffle full blocks  
- preserve order inside each block  
- trailing remainder is kept in place  
- segments are rebuilt AFTER shuffle  

Baseline:

- block = 80  
- perm = 1000  
- seed = 1  

---

## 8. Statistics

Z = (obs − mean_null) / sd_null

Population SD.

If sd = 0 → Z = NaN

---

## 9. Baseline Run

Parameters:

- L = 150  
- mode = topk  
- k = 3  
- max_lag = 10  
- R = 5  
- min_jaccard = 0.5  
- block = 80  
- perm = 1000  
- seed = 1  

---

## 10. Stress Tests

Each run independent (same corpus set)

### Segment size

- L = 100 (tag: L100)  
- L = 200 (tag: L200)  

### Set size

- k = 2 (tag: k2)  
- k = 4 (tag: k4)  

### Null block size

- block = 50 (tag: block50)  
- block = 120 (tag: block120)  

All other parameters unchanged.

---

## 11. Outputs

Per corpus:

- books/<corpus>/layer_a_plus_<tag>_summary.csv  

Combined:

- layer_a_plus_<tag>_summary_all.csv  
- layer_a_plus_<tag>_lag_profile_all.csv  
- layer_a_plus_<tag>_important_summary.csv  
- layer_a_plus_<tag>_run_manifest.json  

---

## 12. Stdout

Per corpus:

- corpus name  
- stream length  
- number of segments  
- parameters  
- adjacent Jaccard  
- recurrence rate  
- dominance mass  
- Z-scores  

End:

- compact top-line summary  

---

## 13. Interpretation

Positive Z indicates:

> stability of dominant consonant sets beyond locally preserved block structure

Null preserves:

- local composition within blocks  
- overall inventory  
- intra-block order  

but disrupts larger coordination.

---

## 14. Limitations

This layer detects:

- stability of unordered dominant consonant sets  

It does not detect:

- ordered phonetic chains  
- syllabic structure  
- rhyme  
- equivalence classes  
- long-range motifs  

---

## 15. Position in Project

Layer A+ extends Layer A:

- Layer A → persistence of dominant units  
- Layer A+ → stability of unordered dominant sets  

Together:

> local phonetic regimes