# Layer B — Anchor Participation

## 1. Objective

This analysis tests whether consonant phonemes act as structural anchors that participate in recurring bidirectional phonetic contexts.

Hypothesis:

- a consonant serves as a central anchor linking its left and right phonetic environment  
- these anchor-centered configurations recur more frequently and more tightly than expected under a block-shuffle null  

This analysis is not a standard sequential k-gram test; it operates on anchor-centered events.

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

Preprocessing conventions:

- qamats = a  
- digraphs are atomic: sh, kh, ts  
- y is treated as a consonant  

---

## 3. Preprocessing

### 3.1 Boundary handling

All `|` markers are removed.

The analysis is performed on a continuous phoneme stream.

---

### 3.2 Phoneme tokenization

Words are tokenized into phoneme atoms using greedy left-to-right matching:

- digraphs (sh, kh, ts) are matched first  
- otherwise single characters are used  

---

### 3.3 Stream construction

The full phoneme stream is constructed:

p1, p2, ..., pN

No segmentation is preserved.

---

### 3.4 Anchor definition

Anchors are defined as all non-vowel phonemes:

anchor = phoneme ∉ {a, e, i, o, u}

Events are defined only at positions where the central phoneme is a consonant.

---

## 4. Anchor-Centered Events

For each position i such that:

1 ≤ i ≤ N − 2  

and p[i] is a consonant:

- left context = p[i−1]  
- anchor = p[i]  
- right context = p[i+1]  

Event:

(anchor, left, right)

---

## 5. Event Sequence

All anchor-centered events are collected into a sequence:

E = [e1, e2, ..., eM]

Important:

- this is a derived sequence  
- its length M is smaller than the original phoneme stream  
- indexing for all metrics is performed on this event sequence, not on the original stream  

---

## 6. Metrics

### 6.1 Token Repeat Fraction

Proportion of all event tokens belonging to repeated event types:

token_repeat_fraction =  
(# occurrences of events with frequency > 1) / (total # of events)

---

### 6.2 Type Repeat Fraction

Proportion of unique event types that recur:

type_repeat_fraction =  
(# unique events with frequency > 1) / (total # of unique events)

---

### 6.3 Mean Gap

For each repeated event type with positions:

[i1, i2, i3, ...]

gaps are defined as:

gap_j = i_{j+1} − i_j

Important:

- indices refer to positions in the event sequence  
- not the original phoneme stream  

Reported:

- mean gap  
- median gap  
- number of gaps  

Interpretation:

- z_mean_gap < 0 → stronger clustering of anchor-context patterns  

Median gap is descriptive only.

---

## 7. Null Model

Block-shuffle null applied to the full phoneme stream:

- split stream into non-overlapping blocks of size B  
- randomly permute blocks  
- preserve internal order within blocks  
- rebuild anchor-event sequence from shuffled stream  

Notes:

- the last block may be shorter than B  
- anchor events are recomputed after shuffling  

---

## 8. Statistical Evaluation

For each metric:

Z = (observed − mean_null) / sd_null

Population standard deviation is used.

Null statistics are computed over valid (non-NaN) values only.

Primary reported metrics:

- z_token_repeat  
- z_type_repeat  
- z_mean_gap  

Interpretation:

- z_token_repeat > 0 → more anchor-event mass than expected  
- z_type_repeat > 0 → more recurring anchor types  
- z_mean_gap < 0 → tighter clustering of anchor patterns  

If null SD = 0:

- Z is reported as NA  

---

## 9. Output

Outputs are written to a user-specified directory.

Recommended root:

results/layer_b_anchor_participation/

### 9.1 Per-book outputs

- books/<corpus>/layer_b_anchor_<tag>_metrics.csv  

### 9.2 Combined outputs

- layer_b_anchor_<tag>_summary_all.csv  
- layer_b_anchor_<tag>_important_summary.csv  
- layer_b_anchor_<tag>_run_manifest.json  

---

## 10. Stdout

For each corpus:

- book name  
- mode  
- block size  
- permutations  
- stream length  
- total events  
- total types  
- token-repeat result  
- type-repeat result  
- mean-gap result  

Final section:

- compact top-line summary across corpora  

---

## 11. Frozen Run Configurations

### Baseline

- mode = exact  
- block = 80  
- perm = 1000  
- seed = 1  

Applied to all corpora.

---

### Stress Tests

Equivalence robustness:

- mode = equiv  
- block = 80  

Null-model robustness:

- mode = exact  
- block = 40  
- mode = exact  
- block = 120  

All stress runs use:

- perm = 1000  
- seed = 1  

---

## 12. Execution

All runs are executed via batch scripts.

- baseline: single configuration (exact, block=80)  
- stress: separate runs per configuration with distinct tags  

Each run produces an independent output directory:

results/layer_b_anchor_participation/<tag>/

---

## 13. Role in the Architecture

This analysis tests whether Layer B structure can be interpreted as:

- purely sequential phonetic recurrence  
or  
- anchor-centered bidirectional organization  

It is a refinement test of Layer B, not a replacement.

If strong signal is observed:

- consonants function as structural anchors linking phonetic environments  

If results closely match standard Layer B:

- anchor participation may be reducible to sequential recurrence structure  