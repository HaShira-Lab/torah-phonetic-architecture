\# Layer C4 — Phrase-Final Rhyme Recurrence



\## 1. Goal



Test whether phrase-final words form a locally recurrent rhyme network.



This analysis uses phrase-final words only.

It does not test rhyme participation of all words inside each phrase.



\---



\## 2. Input



Files: `\*\_phonetic.txt`



Format:



\* words separated by spaces

\* phrase boundary marker: `|`



For this analysis:



\* `|` defines phrase boundaries

\* the last word of each phrase is the analytical unit



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



\## 4. Phrase-Final Rhyme Tail



For each phrase:



1\. take the final word of the phrase

2\. tokenize it into phoneme atoms

3\. find the last vowel

4\. define the rhyme tail as the sequence from that vowel to the end of the word

5\. require tail length ≥ 2



If no valid tail exists, the phrase is excluded from scoring.



\---



\## 5. Normalization



Applied to phrase-final tails only:



\* `d → t` (always)

\* `kh → k` (optional flag)

\* `ts → s` (optional flag)



`sh` is preserved.



\---



\## 6. Local Phrase Window



For each phrase `i`, search within a symmetric local phrase window:



`j ∈ \[i-R, i+R], j ≠ i`



Only phrases with valid tails are compared.



\---



\## 7. Metric



For each valid phrase `i`:



`matches\_i = number of phrases in the local window whose final rhyme tail equals tail\_i`



Global score:



`score = mean(matches\_i)`



This is a local network-density measure over phrase-final rhyme links.



\---



\## 8. Null Model



Block shuffle over the phrase sequence.



\* preserves phrase integrity

\* preserves local packing within blocks

\* destroys larger-scale cross-phrase ordering



Baseline:



\* `R = 10`

\* `block = 20`

\* `perm = 200`

\* `seed = 1`



Stress:



\* `block = 50`

\* optional equivalence stress:



&#x20; \* `eq\_kh\_k = 1`

&#x20; \* `eq\_ts\_s = 1`



\---



\## 9. Z-score



`Z = (obs − mean(null)) / sd(null)`



Reported:



\* `n\_phrases`

\* `n\_valid\_final\_tails`

\* `score`

\* `null\_mean`

\* `null\_sd`

\* `Z`



\---



\## 10. Interpretation



High positive `Z` indicates that phrase-final rhyme tails form a denser local recurrence network than expected under the phrase-block null.



This analysis is legitimate as a dedicated phrase-final test and can be compared directly between Torah and modern prose.



It does not claim that every phrase contains internal rhyme support; that requires a separate whole-phrase participation analysis.



\---



\## 11. Output



Per book:



\* summary CSV

\* phrase-final tails CSV

\* run manifest JSON



Per run:



\* `summary\_all.csv`

\* `important\_summary.csv`

\* run manifest JSON



Console:



\* top-line results



