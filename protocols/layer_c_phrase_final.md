# Layer C — Phrase-Final Rhyme Recurrence

## 1. Objective

This analysis tests whether phrase-final words form a locally recurrent rhyme network.

It uses phrase-final words only.

It does not test rhyme participation of all words inside each phrase.

---

## 2. Input

Input files are transliterated phonetic corpora.

Format:

- words separated by spaces  
- phrase boundary marker: `|`  

For this analysis:

- `|` defines phrase boundaries  
- the last word of each phrase is the analytical unit  

---

## 3. Phonetic Rules

### 3.1 Vowels

- a, e, i, o, u  

### 3.2 Consonants

- All other phoneme tokens  

### 3.3 Digraphs (atomic)

- sh, kh, ts  

### 3.4 Other conventions

- y is treated as a consonant  
- o ≠ u  

---

## 4. Phrase-Final Rhyme Tail

For each phrase:

1. take the final word of the phrase  
2. tokenize it into phoneme atoms  
3. find the last vowel  
4. define the rhyme tail as follows  

### Closed final syllable

- (V, C)  

### Open final syllable

- (C, V)  

If no valid tail exists, the phrase is excluded from scoring.

### Scope Note

This analysis operates on phrase-final words.

Unlike stream-based analyses:

- phrase boundaries are explicitly used  
- open final syllables are represented as (C, V)  

This allows inclusion of open syllables in rhyme comparison.

---

## 5. Local Phrase Window

For each phrase i, search within a symmetric local phrase window:

j ∈ [i−R, i+R], j ≠ i  

Only phrases with valid tails are compared.

---

## 6. Metric

For each valid phrase i:

matches_i = number of phrases in the local window whose final rhyme tail equals tail_i  

Global score:

score = mean(matches_i)  

This is a local network-density measure over phrase-final rhyme links.

---

## 7. Null Model

Block shuffle over the phrase sequence.

- preserves phrase integrity  
- preserves local packing within blocks  
- destroys larger-scale cross-phrase ordering  

### Baseline

- R = 10  
- block = 20  
- perm = 200  
- seed = 1  

### Stress

- block = 50  

---

## 8. Statistical Evaluation

Z = (obs − mean(null)) / sd(null)  

- population standard deviation is used  

If sd = 0:

- Z is reported as NA  

Reported:

- n_phrases  
- n_valid_final_tails  
- score  
- null_mean  
- null_sd  
- Z  

---

## 9. Output

Per book:

- summary CSV  
- phrase-final tails CSV  
- run manifest JSON  

Per run:

- c4_<tag>_summary_all.csv  
- c4_<tag>_important_summary.csv  
- c4_<tag>_run_manifest.json  

Console:

- top-line results  

---

## 10. Interpretation

High positive Z indicates that phrase-final rhyme tails form a denser local recurrence network than expected under the phrase-block null.

This is a dedicated phrase-final test and can be compared directly between Torah and modern prose.

It does not claim that every phrase contains internal rhyme support; that requires a separate whole-phrase participation analysis.

---

## 11. Role in Architecture

Layer C4 tests phrase-final organization of rhyme.

It complements:

- C1: continuous rhyme flow  
- C1.2: distance structure  
- C2: word-final recurrence  

A strong C4 effect indicates that rhyme organization extends to phrase boundaries and participates in larger compositional structuring.