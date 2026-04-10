# Layer B — Local Phonetic Chains

## 1. Objective

This analysis quantifies local phonetic regularity in the continuous phoneme stream by measuring:

- density of repeated short phoneme chains (k-grams)  
- spatial clustering of their repetitions  

This is a full-phoneme-stream analysis and does not rely on syllabification.

---

## 2. Input

Input files are the project’s fixed transliterated phonetic corpora.

Expected alphabet:

- vowels: a, e, i, o, u  
- consonants: b, g, d, h, v, z, kh, t, y, k, l, m, n, s, p, ts, q, r, sh  
- boundary marker: `|`  

Input is whitespace-separated text.

Baseline input set:

- genesis_phonetic.txt  
- exodus_phonetic.txt  
- leviticus_phonetic.txt  
- numbers_phonetic.txt  
- deuteronomy_phonetic.txt  
- hagamad_phonetic.txt  

Phonetic preprocessing (fixed):

- qamats = a  
- digraphs are atomic: sh, kh, ts  
- y is treated as a consonant  

---

## 3. Preprocessing

### 3.1 Boundary handling

Phrase-boundary marker `|` is removed before analysis.

The analysis is performed on a single continuous phoneme stream.

---

### 3.2 Phoneme tokenization

Words are tokenized phonemically (not character-wise).

Left-to-right greedy matching:

- first match digraphs (sh, kh, ts)  
- otherwise single-character phonemes  

Examples:

- bereshit → b e r e sh i t  
- tsedek → ts e d e k  

---

### 3.3 Stream construction

All phonemes are concatenated:

p1, p2, ..., pN

The stream includes all transitions:

- C→V  
- V→C  
- C→C  
- V→V  

No segmentation is preserved.

---

### 3.4 Special commitments

- no syllabification  
- no morphological normalization  
- no lexical filtering  

---

## 4. Matching Modes

### 4.1 Exact mode (primary)

Two k-grams match only if all phonemes are identical.

---

### 4.2 Equivalence mode (robustness only)

Normalization is applied at the phoneme level before k-gram construction:

- d → t  
- z → s  
- q → k  
- v → b  

Digraphs remain unchanged:

- sh, kh, ts are not affected  

This mode is used only for robustness testing.

---

## 5. k-gram Construction

For a chosen k, all contiguous k-grams are extracted:

g_i = (p_i, p_{i+1}, ..., p_{i+k-1})

---

## 6. Metrics

### 6.1 Token Repeat Fraction

Proportion of all k-gram tokens that belong to repeated types:

token_repeat_fraction =  
(# occurrences of k-grams with frequency > 1) / (total # of k-grams)

---

### 6.2 Type Repeat Fraction

Proportion of unique k-gram types that recur:

type_repeat_fraction =  
(# unique k-grams with frequency > 1) / (total # of unique k-grams)

---

### 6.3 Hapax Fraction (descriptive)

hapax_fraction =  
(# unique k-grams with frequency = 1) / (total # of unique k-grams)

---

### 6.4 Gap Metrics

For each repeated k-gram with occurrences at positions:

[i1, i2, i3, ...]

gaps are defined as:

gap_j = i_{j+1} − i_j

(i.e., distance between starting indices)

Reported:

- mean gap  
- median gap  
- number of gaps  

Interpretation:

- z_mean_gap < 0 → stronger clustering than expected  

Median gap is descriptive only.

---

## 7. Null Model

Block-shuffle null model:

- split stream into non-overlapping blocks of size B  
- randomly permute blocks  
- preserve internal order within blocks  

Notes:

- the last block may be shorter than B  
- the stream remains continuous (no boundary constraints)  

---

## 8. Statistical Evaluation

For each metric:

Z = (observed − mean_null) / sd_null

Computed using population standard deviation.

Null statistics are computed over valid (non-NaN) values only.

Primary reported Z-scores:

- z_token_repeat  
- z_type_repeat  
- z_mean_gap  

Interpretation:

- z_token_repeat > 0 → higher repetition mass  
- z_type_repeat > 0 → more recurring types  
- z_mean_gap < 0 → stronger clustering  

If null SD = 0:

- Z is reported as NA  

---

## 9. Output

Outputs are written to a user-specified directory.

Recommended root:

results/layer_b_local_phonetic_chains/

### 9.1 Per-book outputs

- books/<corpus>/layer_b_<tag>_metrics.csv  

### 9.2 Combined outputs

- layer_b_<tag>_summary_all.csv  
- layer_b_<tag>_important_summary.csv  
- layer_b_<tag>_run_manifest.json  

---

## 10. Stdout

For each corpus:

- book name  
- mode  
- k  
- block size  
- permutations  
- stream length  
- total k-grams  
- total types  
- token-repeat result  
- type-repeat result  
- mean-gap result  

Final section:

- compact top-line summary across corpora  

---

## 11. Frozen Run Configurations

### Baseline

- k = 3  
- mode = exact  
- block = 80  
- perm = 1000  
- seed = 1  

Applied to all corpora.

---

### Stress Tests

Parameter robustness:

- k = 2, exact, block = 80  
- k = 4, exact, block = 80  

Equivalence robustness:

- k = 3, equiv, block = 80  

Null-model robustness:

- k = 3, exact, block = 40  
- k = 3, exact, block = 120  

Appendix diagnostic:

- k = 5, exact, block = 80  
- corpora: Genesis + HaGamad only  

---

## 12. Execution

All runs are executed via batch scripts.

- baseline: single configuration (k=3, exact, block=80)  
- stress: separate runs per configuration using distinct tags  

Each run produces an independent output directory:

results/layer_b_local_phonetic_chains/<tag>/

---

## 13. Role in the Architecture

This layer establishes a dense local phonetic texture in the continuous phoneme stream.

It does not by itself establish:

- syllabic structure  
- rhyme structure  
- directionality  
- global architecture  

It functions as a foundational phonetic-textural layer.