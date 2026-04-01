\# Layer C2 — Word-Final Rhyme Concentration



\## 1. Goal



Test whether phonetic rhyme recurrence concentrates at word-final positions.



\---



\## 2. Input



Files: `\*\_phonetic.txt`



Format:



\* words separated by spaces

\* phrase boundary marker `|`



For this analysis:



\* words are the analytical units

\* `|` is ignored



\---



\## 3. Phonetic Rules



\### 3.1 Vowels



`a, e, i, o, u`



\### 3.2 Consonants



All other phoneme tokens



\### 3.3 Digraphs (atomic)



`sh, kh, ts`



\### 3.4 Other conventions



\* `y` is treated as a consonant

\* `o ≠ u`



\---



\## 4. Word-Final Rhyme Tail



For each word:



1\. tokenize the word into phoneme atoms

2\. find the last vowel

3\. define the rhyme tail as the sequence from that vowel to the end of the word

4\. require tail length ≥ 2



Examples:



\* `shamar` → `ar`

\* `zamar` → `ar`

\* `ruah` → `ah`



Words with no vowel, or with a tail of length 1, are excluded from matching.



\---



\## 5. Normalization



Applied to rhyme tails only:



\* `d → t` (always)

\* `kh → k` (optional flag)

\* `ts → s` (optional flag)



`sh` is preserved.



\---



\## 6. Metric



For each word `i`, search all words:



`j ∈ \[i+1, i+L]`



Only words with valid tails are compared.



Count:



\* `comparisons` = number of valid tail-pairs examined

\* `matches` = number of pairs such that `tail\_i == tail\_j`



Score:



`rate = matches / comparisons`



This is a local concentration measure, not a nearest-neighbor measure.



\---



\## 7. Null Model



Block shuffle over the word sequence.



\* preserves word identities and local packing within blocks

\* disrupts larger-scale ordering



Baseline:



\* `L = 40`

\* `block = 50`

\* `perm = 200`

\* `seed = 1`



Stress:



\* `block = 80`

\* optional equivalence stress:



&#x20; \* `eq\_kh\_k = 1`

&#x20; \* `eq\_ts\_s = 1`



\---



\## 8. Z-score



`Z = (obs − mean(null)) / sd(null)`



Reported:



\* `matches`

\* `comparisons`

\* `rate`

\* `null\_mean`

\* `null\_sd`

\* `Z`



\---



\## 9. Interpretation



High positive `Z` indicates that identical word-final rhyme tails are locally concentrated more strongly than expected under the block-shuffle null.



This test captures word-final rhyme concentration only.

It does not test syllabic flow across word boundaries or phrase-final structure.



\---



\## 10. Output



Per book:



\* per-book summary CSV

\* per-book run manifest JSON



Per run:



\* `summary\_all.csv`

\* run manifest JSON



Console:



\* top-line results for quick inspection



