\# Layer C1.2 — Syllabic Rhyme Distance Spectrum



\## 1. Goal



Measure the distribution of recurrence distances of syllabic rhyme units in a continuous phonetic stream.



\---



\## 2. Input



Files: \*\_phonetic.txt

Format:



\* words separated by space

\* phrase boundary marker: "|"

&#x20; All boundaries are ignored.



\---



\## 3. Phonetic Units



Vowels: {a, e, i, o, u}

Digraphs: sh, ts, kh (atomic)



\---



\## 4. Syllable Extraction



(optional C) + V + (C\* until next V)



\---



\## 5. Rhyme Units



\### Strict



\* Closed syllable: VC, VCC, ...

\* Open: discarded



\### Permissive



\* Closed: same

\* Open V → converted to CV using previous consonant (can cross boundaries)



\---



\## 6. Stream



S = \[r1, r2, ..., rN], len(r) ≥ 2



\---



\## 7. Metric



\### Global (as C1)



Nearest recurrence within L:

match\_rate



\### Distance spectrum



For each d ∈ \[1..Dmax]:

rate(d) = P(ri = r(i+d))



\---



\## 8. Null Model



Block shuffle (preserving local frequencies)



block ∈ {50, 80}

perm ≥ 200



\---



\## 9. Z-score



For each d:

Z(d) = (obs(d) − mean\_null(d)) / sd\_null(d)



Global Z computed same as C1.



\---



\## 10. Output



Per book:



\* summary (global Z)

\* distance\_profile.csv (d, Z(d))



Run-level:



\* summary\_all.csv



\---



\## 11. Expected



Torah:



\* strong global Z

\* structured peaks in Z(d)



Modern:



\* weak / flatter spectrum



