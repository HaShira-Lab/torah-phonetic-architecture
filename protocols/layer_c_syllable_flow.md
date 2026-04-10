# Layer C — Syllabic / Rhyme Flow (Stream-Based, Strict)

## 1. Objective

This analysis tests local recurrence of syllabic rhyme units in a continuous phonetic stream, independent of word and phrase boundaries.

It measures how frequently a rhyme unit reappears within a short forward window.

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

### 3.4 Rhyme Unit Definition — Scope Note

Two distinct rhyme-unit definitions are used in Layer C:

1. Stream-based analyses (C1, C2, window density)

- units are defined as V + following consonants
- extraction is continuous and ignores word boundaries
- open final vowels are not treated as rhyme units

2. Boundary-based analyses (word-final, phrase-final)

- units are defined relative to word endings
- closed syllables: V + following consonants
- open syllables: preceding consonant + final vowel (CV)

This distinction is required because:

- stream-based extraction cannot reliably detect word-final open syllables
- boundary-based analyses explicitly depend on word/phrase structure

---

## 4. Tokenization

The text is processed left-to-right:

- whitespace and `|` are ignored  
- digraphs are matched first  
- otherwise single-character phonemes are used  

Result:

p1, p2, ..., pN

---

## 5. Syllable / Rhyme Unit Extraction

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

### 5.1 Inclusion rule

Only closed units are retained:

- length ≥ 2  

Open vowel-only units are discarded.

###  5.2 Scope Note

This analysis operates on a continuous phonetic stream.

- units are defined as V + following consonants  
- word boundaries are ignored  
- open final vowels are not treated as standalone rhyme units  

Example:

- rua → ru (final 'a' is discarded as length < 2)

---

## 6. Stream Construction

Construct continuous sequence:

S = [r1, r2, ..., rN]

Constraints:

- no word boundaries  
- no phrase boundaries  
- only units with length ≥ 2  

---

## 7. Metric — Nearest Recurrence

For each position i, find the first match within a forward window:

find j such that:

i < j ≤ i + L  
and r_i == r_j  

Each position contributes at most one match.

### 7.1 Match rate

match_rate = (# matched positions) / N

---

## 8. Parameters

### 8.1 Window length

- L ∈ {10, 20, 40}  

Baseline:

- L = 20  

### 8.2 Null model

Block shuffle of the stream:

- block ∈ {50, 80}  
- perm = 200  

Baseline:

- block = 50  
- perm = 200  
- seed = 1  

### 8.3 Window profile

Sliding window over the stream:

- W = 1000  
- step = 500  

---

## 9. Statistical Evaluation

Z-score:

Z = (obs − mean_null) / sd_null  

- population standard deviation is used  
- null values are computed over all permutations  

If sd_null = 0:

- Z is reported as NA  

---

## 10. Output

Outputs are written to:

results/layer_c_syllable_flow/<tag>/

### 10.1 Per-book outputs

- books/<book>/c1_<tag>_summary.csv  
- books/<book>/c1_<tag>_profile.csv  
- books/<book>/c1_<tag>_run_manifest.json  

Summary fields:

- book  
- L  
- block  
- perm  
- seed  
- stream_len  
- obs  
- null_mean  
- null_sd  
- z  

### 10.2 Combined summary

- c1_<tag>_summary_all.csv  

Contains full per-book metrics.

---

## 11. Execution

All runs are executed via batch scripts.

### 11.1 Baseline

- L = 20  
- block = 50  
- perm = 200  
- seed = 1  

### 11.2 Stress

- L ∈ {10, 20, 40}  
- block ∈ {50, 80}  
- perm = 200  
- seed = 1  

Each configuration is executed with a separate tag:

- stress_L{L}_B{block}  

---

## 12. Interpretation

- positive Z → rhyme units recur more often than expected  
- higher Z → stronger local rhyme flow  

Window profile reveals distribution of flow across the text.

---

## 13. Role in Architecture

This is the first analysis of Layer C.

It establishes:

- existence of local rhyme flow  
- independence from word and phrase boundaries  
- continuous operation across the entire stream  

It serves as the entry point to the syllabic/rhyme layer.