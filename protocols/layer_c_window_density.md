\# Layer C6 — Windowed Rhyme Density Distribution



\## 1. Goal



Measure the distribution of rhyme density across the text.



\---



\## 2. Phonetic Basis



Identical to Layer C1:



\* vowels: a e i o u

\* digraphs: sh, ts, kh

\* units:



&#x20; \* closed: V + C\*

&#x20; \* open (permissive): previous C + V

\* minimum length: ≥ 2

\* o ≠ u



\---



\## 3. Stream Construction



Phonetic stream is built identically to C1.



Modes:



\* permissive (default)

\* strict (optional)



\---



\## 4. Matching Rule



For each unit:



\* search forward within distance L

\* match = exact unit equality



\---



\## 5. Windowing



Sliding windows over stream:



\* W = window size

\* step = step size



In each window:



```text

rhyme\_rate = (#units with ≥1 match) / window size

```



\---



\## 6. Metrics



\* mean\_rate

\* variance (key)

\* minimum window value (key)

\* fraction of windows below threshold τ



\---



\## 7. Null Model



Block shuffle of stream:



\* preserves local phonetic statistics

\* destroys structure



\---



\## 8. Z-scores



Computed for:



\* mean

\* variance

\* minimum



\---



\## 9. Visualization



Plot:



\* x = normalized position (0–1)

\* y = rhyme\_rate



Optional:



\* smoothed curve (moving average)



\---



\## 10. Interpretation



Torah:



\* higher mean

\* lower variance

\* higher minimum

\* no low-density gaps



Modern:



\* lower mean

\* higher variance

\* deep local drops



