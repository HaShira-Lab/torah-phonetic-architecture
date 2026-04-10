# Layer B — Boundary & Segment Controls (B′)

## 1. Objective

This analysis tests whether the phonetic-chain clustering observed in Layer B:

- is confined within phrase boundaries  
- depends on segment ordering  
- or reflects a continuous cross-boundary structure  

It serves as a control layer validating the structural interpretation of Layer B.

---

## 2. Input

Input files are the project’s fixed transliterated phonetic corpora.

Expected alphabet:

- vowels: a, e, i, o, u  
- consonants: b, g, d, h, v, z, kh, t, y, k, l, m, n, s, p, ts, q, r, sh  
- boundary marker: `|`  

Input is whitespace-separated text.

---

## 3. Preprocessing

### 3.1 Tokenization

Words are converted into phoneme sequences using greedy left-to-right matching:

- digraphs (sh, kh, ts) are treated as atomic phonemes  
- otherwise single characters are used  

---

### 3.2 Segmentation

The corpus is split into segments by the boundary marker `|`.

Two representations are used:

- segments: list of phoneme sequences (structure preserved)  
- stream: flattened phoneme sequence (boundaries removed)  

---

## 4. k-gram Construction

For a given k, contiguous k-grams are extracted from any stream:

g_i = (p_i, p_{i+1}, ..., p_{i+k-1})

---

## 5. Metric

Only one metric is used.

### 5.1 Mean Gap

For each repeated k-gram with occurrence positions:

[i1, i2, i3, ...]

gaps are defined as:

gap_j = i_{j+1} − i_j

(i.e., distance between starting indices)

Mean gap is computed across all gaps.

Interpretation:

- lower gap → stronger clustering  
- negative Z-score → stronger clustering than null  

---

## 6. Tests

### 6.1 Baseline (continuous stream)

- compute gap on the flattened stream  
- ignores all boundaries  

---

### 6.2 Boundary-aware (within-segment)

- compute k-gram gaps inside each segment  
- collect all within-segment gaps  
- compute a single global mean across all segments  

Important:

- segments are not averaged equally  
- all gaps are pooled before averaging  

This avoids bias from segment length differences.

---

### 6.3 Full shuffle null

- randomly shuffle the entire phoneme stream  

Purpose:

- destroys all structure  
- preserves only phoneme frequencies  

---

### 6.4 Segment-order shuffle null

- shuffle segments as blocks  
- preserve internal segment structure  

Purpose:

- tests whether clustering depends on segment ordering  

---

## 7. Statistical Evaluation

Z-scores are computed as:

Z = (observed − mean_null) / sd_null

Population standard deviation is used.

Null values:

- computed across permutations  
- filtered for valid (non-None) values only  

Reported:

- z_full (vs full shuffle)  
- z_segment (vs segment shuffle)  

---

## 8. Output

Outputs are written to a user-specified directory.

Recommended root:

results/layer_b_boundary_controls/

### 8.1 Summary output

- layer_b_boundary_controls_summary.csv  

Contains per corpus:

- gap_baseline  
- gap_boundary  
- z_full  
- z_segment  

---

## 9. Stdout

For each corpus:

- book name  
- k  
- permutations  
- baseline gap  
- boundary gap  
- Z_full  
- Z_segment  

---

## 10. Frozen Run Configurations

### Baseline

- k = 3  
- perm = 1000  
- seed = 1  

---

### Stress Tests

Chain length:

- k = 2  
- k = 4  

Permutation stability:

- perm = 200  

All stress runs use:

- seed = 1  

---

## 11. Execution

All runs are executed via batch scripts.

- baseline: single configuration (k=3, perm=1000)  
- stress: separate runs per configuration using distinct tags  

Each run produces an independent output directory:

results/layer_b_boundary_controls/<tag>/

---

## 12. Interpretation

Compare:

- gap_baseline vs gap_boundary  
- z_full vs z_segment  

Interpretation:

- if gap_boundary ≈ gap_baseline → clustering is mostly intra-segment  
- if gap_boundary > gap_baseline → clustering extends across boundaries  
- if z_full remains strong → effect is not reducible to frequency  
- if z_segment decreases → structure depends on segment ordering  

---

## 13. Role in Architecture

This analysis verifies that Layer B clustering:

- is not reducible to phoneme frequencies  
- is not confined to segment boundaries  
- partially depends on segment ordering  

It is a validation/control layer, not a primary structural layer.