# Layer C — Syllabic Rhyme Distance Spectrum (Strict)

## 1. Objective

This analysis measures the distance distribution of recurring syllabic rhyme units in a continuous phonetic stream.

It extends Layer C1 by asking not only whether rhyme units recur locally, but also at which exact distances recurrence is strongest.

---

## 2. Input

Input files are the project’s fixed transliterated phonetic corpora.

Format:

- words separated by spaces  
- phrase boundary marker: `|`  

All boundaries are ignored in this analysis.

---

## 3. Phonetic Units

### 3.1 Vowels

- V = {a, e, i, o, u}

### 3.2 Consonants

- All non-vowel phonemes

### 3.3 Digraphs (atomic)

- sh, ts, kh  

These are treated as single phonetic units during tokenization.

---

## 4. Tokenization

The text is processed left-to-right:

- whitespace and `|` are ignored  
- digraphs are matched first  
- otherwise single-character phonemes are used  

Result:

p1, p2, ..., pN

---

## 5. Syllable / Rhyme Unit Extraction (Strict Mode)

Each vowel defines a candidate unit.

Rule:

V + (C* until next V)

That is:

- start at vowel  
- include all following consonants until the next vowel  

Examples:

- mitsrayim → mi, tsra, yim  
- yisrael → yi, sra, el  
- ruah → ru, ah  

Only closed units are retained:

- length ≥ 2  

Open vowel-only units are discarded.

### 5.1  Scope Note

This analysis follows the same unit definition as Layer C1.

- extraction is continuous  
- word boundaries are ignored  
- open final vowels are not treated as standalone rhyme units  

Example:

- rua → ru

---

## 6. Stream Construction

Construct continuous sequence:

S = [r1, r2, ..., rN]

Constraints:

- no word boundaries  
- no phrase boundaries  
- only units with length ≥ 2  

---

## 7. Metrics

### 7.1 Global metric (same as C1)

For each position i, find the first match within a forward window:

find j such that:

i < j ≤ i + L  
and r_i == r_j  

Each position contributes at most one match.

Global match rate:

match_rate = (# matched positions) / N

---

### 7.2 Distance spectrum

For each distance d in 1..Dmax:

rate(d) = P(r_i = r_{i+d})

Operationally:

- compare all valid pairs (i, i+d)  
- count exact matches  
- divide by the number of valid comparisons at that distance  

Reported per distance:

- hits  
- denom  
- obs_rate  
- null_mean  
- null_sd  
- z  

---

## 8. Parameters

### 8.1 Baseline

- L = 20  
- Dmax = 40  
- block = 50  
- perm = 200  
- seed = 1  

### 8.2 Stress

Recommended stress grid:

- L ∈ {10, 20, 40}  
- block ∈ {50, 80}  
- Dmax = 40  
- perm = 200  
- seed = 1  

---

## 9. Null Model

Block shuffle of the stream:

- split the stream into contiguous blocks of size `block`  
- randomly permute blocks  
- preserve internal order within each block  

This preserves local frequencies while disrupting larger structure.

---

## 10. Statistical Evaluation

For the global metric:

Z_global = (obs_global − mean_null_global) / sd_null_global  

For each distance:

Z(d) = (obs_rate(d) − mean_null(d)) / sd_null(d)  

- population standard deviation is used  

If null SD = 0:

- Z is reported as NA  

---

## 11. Output

Outputs are written to:

results/layer_c_syllable_distance/<tag>/

### 11.1 Per-book outputs

- books/<book>/c1_2_<tag>_summary.csv  
- books/<book>/c1_2_<tag>_distance.csv  
- books/<book>/c1_2_<tag>_run_manifest.json  

### 11.2 Run-level outputs

- c1_2_<tag>_summary_all.csv  
- c1_2_<tag>_run_manifest.json  

---

## 12. Stdout

For each book, the script prints:

- book name  
- L, Dmax, block, perm, seed  
- stream length  
- global observed rate  
- global null mean  
- Z_global  
- top five distance peaks by Z(d)  

---

## 13. Interpretation

Expected pattern in Torah:

- strong positive Z_global  
- structured non-flat distance spectrum  
- clear local and medium-range peaks  

Expected pattern in modern prose:

- weaker Z_global  
- flatter and less structured distance spectrum  

---

## 14. Role in Architecture

Layer C1.2 refines Layer C1 by showing the geometry of rhyme recurrence.

It addresses not only whether syllabic rhyme units recur, but also how recurrence is distributed across distances.

This makes it a key structural analysis within the syllabic / rhyme layer.