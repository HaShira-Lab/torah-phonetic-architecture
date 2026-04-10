# Layer C — Word-Final Rhyme Recurrence

## 1. Objective

This analysis tests whether rhyme recurrence is concentrated at word-final positions.

It evaluates recurrence of word-final rhyme units across nearby words.

---

## 2. Input

Input files are transliterated phonetic corpora.

- words separated by spaces  
- `|` removed  

---

## 3. Rhyme Unit (Word Final)

Each word is mapped to a rhyme tail.

### Closed syllable

- (V, C)

### Open final syllable

- (C, V)

Only units of length ≥ 2 are used.

### Scope Note

This analysis operates on word-final positions.

Unlike stream-based analyses:

- word boundaries are explicitly used  
- open final syllables are represented as (C, V)  

This allows inclusion of open syllables in rhyme comparison.

---

## 4. Metric

For each word i:

find j such that:

i < j ≤ i + L  
tail_i == tail_j  

Each pair contributes to:

- matches  
- comparisons  

Rate:

rate = matches / comparisons

---

## 5. Parameters

### Baseline

- L = 40  
- block = 50  
- perm = 200  
- seed = 1  

### Stress

- L ∈ {20, 40}  
- block ∈ {50, 80}  

---

## 6. Null Model

Block shuffle over words:

- words grouped into blocks  
- blocks permuted  
- order within blocks preserved  

---

## 7. Statistical Evaluation

Z = (obs − mean_null) / sd_null  

If sd = 0:

- Z = NA  

---

## 8. Output

Per book:

- rate  
- null_mean  
- Z  

---

## 9. Interpretation

- higher Z → stronger recurrence of word-final rhyme  
- comparison with modern text tests specificity  

---

## 10. Role in Architecture

This analysis tests end-position bias of rhyme.

It complements Layer C1 (stream flow) by focusing on word boundaries.

A strong effect indicates structured rhyme placement at word endings.