# Layer C — Windowed Rhyme Density (Global Distribution, Strict)

## 1. Objective

This analysis evaluates how rhyme relations are distributed across the entire phonetic stream.

It measures whether rhyme activity is:

- globally sustained (Torah)  
- locally sporadic (modern prose)  

This is a descriptive, window-based analysis intended to visualize the spatial distribution of rhyme density.

---

## 2. Input

Input files are the project’s standardized phonetic corpora.

- words separated by spaces  
- phrase boundary marker: `|`  
- `|` is removed before analysis  

Phonetic conventions follow the global project standard.

---

## 3. Phonetic Units

### 3.1 Vowels

- V = {a, e, i, o, u}

### 3.2 Consonants

- All non-vowel phonemes  

### 3.3 Digraphs (atomic)

- sh, kh, ts  

These are treated as single phonetic units during tokenization.

---

## 4. Tokenization

Words are processed left-to-right:

- digraphs are matched first  
- otherwise single-character phonemes are used  

Result:

p1, p2, ..., pN

---

## 5. Rhyme Unit Definition (C1-compatible)

Rhyme units are defined identically to Layer C1.

Each vowel generates a unit.

### 5.1 Closed syllable

If a vowel is followed by one or more consonants:

- V + (all following consonants until next vowel)

Examples:

- tsra → tsra  
- yim → yim  

(If multiple consonants occur, all are included.)

### 5.2 Filtering

- only units of length ≥ 2 are retained  
- single vowels are excluded    

---

## 6. Stream Construction

All rhyme units are concatenated into a continuous stream:

stream = [u1, u2, u3, ...]

Constraints:

- no word boundaries  
- no phrase boundaries  
- units follow the strict C1 definition  

---

## 7. Windowed Density Analysis

A sliding window is applied over the stream.

### 7.1 Parameters

- W — window size (e.g., 1000 units)  
- step — step size (e.g., 500)  
- L — forward search radius (e.g., 80)  

### 7.2 Procedure (per window)

For each position i in the window:

for j in [i+1, i+L]:

    if unit[i] == unit[j]:
        matches += 1

    total_pairs += 1

### 7.3 Metric

density = matches / total_pairs  

Interpretation:

- probability that two nearby units rhyme within the local window  

---

## 8. Output

### 8.1 Per-book outputs

- books/<book>/windows.csv  
- books/<book>/summary.csv  
- books/<book>/run_manifest.json  

### 8.2 windows.csv

- window index  
- density value  

### 8.3 summary.csv

- mean density  
- variance  
- min  
- max  
- number of windows  

---

## 9. Parameters

### 9.1 Baseline

- L = 80  
- W = 1000  
- step = 500  

### 9.2 Stress

- L ∈ {40, 80, 120}  
- W ∈ {800, 1000, 1500}  
- step = W / 2  

---

## 10. Important Note

This analysis:

- does not use a null model  
- does not compute Z-scores  
- is descriptive only  

Its purpose is to visualize global distribution of rhyme activity.

---

## 11. Interpretation

Expected pattern:

### Torah

- higher mean density  
- broader variance across windows  
- sustained density across entire stream  

### Modern prose

- lower mean density  
- lower variance  
- isolated local peaks  

---

## 12. Role in Architecture

This analysis complements Layer C1:

- C1 establishes existence of rhyme flow  
- window density shows its distribution across the entire text  

It answers the question:

Is rhyme present everywhere, or only in isolated regions?

---

## 13. Conceptual Position

This is not a statistical test of structure.

It is a global distribution diagnostic supporting interpretation of the syllabic/rhyme layer.

---

## 14. Summary

- uses strict phonetic rules consistent with C1  
- includes open syllables  
- measures local density across sliding windows  
- demonstrates global vs local organization of rhyme  