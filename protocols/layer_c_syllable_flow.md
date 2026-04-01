\# Layer C1 — Syllabic / Rhyme Flow (Stream-Based)



\## 1. Goal



Test local recurrence of syllabic rhyme units in a continuous phonetic stream,

independent of word and phrase boundaries.



\---



\## 2. Input



Files: \*\_phonetic.txt



Format:

\- words separated by space

\- phrase boundary marker: "|"



All boundaries are ignored in this analysis.



\---



\## 3. Phonetic Units



\### 3.1 Vowels



V = {a, e, i, o, u}



\### 3.2 Consonants



All non-vowels



\### 3.3 Digraphs (atomic)



sh, ts, kh



\---



\## 4. Syllable Extraction



Rule:



(optional C) + V + (C\* until next V)



Example:



yisrael → yi-sra-el  

mitsrayim → mi-tsra-yim  

ruah → ru-ah  



\---



\## 5. Rhyme Unit Definition



\### Strict mode



\- Closed syllable → take from vowel to end (VC, VCC, ...)

\- Open syllable (V only) → discard



\---



\### Permissive mode



\- Closed → same as strict

\- Open (V only) →



&#x20; convert to CV using previous consonant



&#x20; previous consonant may come across word boundary



Example:



mare → re  

qore → re  



\---



\## 6. Stream Construction



Construct sequence:



S = \[r1, r2, ..., rN]



Constraints:

\- ignore word boundaries

\- ignore "|"

\- keep only units with length ≥ 2



\---



\## 7. Normalization (optional flags)



\- kh → k

\- ts → s

\- sh preserved

\- o ≠ u



\---



\## 8. Metric — Nearest Recurrence



For each i:



find smallest j such that:

i < j ≤ i + L

and ri == rj



match\_rate = matches / total



\---



\## 9. Parameters



L ∈ {10, 20, 40}



\---



\## 10. Null Model



Block shuffle of stream



block ∈ {50, 80}



perm ≥ 200



\---



\## 11. Z-score



Z = (obs − mean\_null) / sd\_null



\---



\## 12. Window Profile



Sliding window:



W ∈ {1000}

step ∈ {500}



\---



\## 13. Expected Outcome



Torah:

\- strong positive Z

\- structured profile



Modern:

\- weaker / flatter

