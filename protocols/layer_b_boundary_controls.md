\# Layer B — Boundary \& Segment Controls (B′)



\## 1. Objective



To test whether the phonetic-chain clustering observed in Layer B:



\* is confined within phrase boundaries,

\* depends on segment ordering,

\* or reflects a continuous cross-boundary structure.



\---



\## 2. Input



Same phonetic corpus as Layer B:



\* whitespace-separated tokens

\* boundary marker: `|`

\* digraphs: `sh, kh, ts` treated as atomic phonemes



\---



\## 3. Preprocessing



\### 3.1 Tokenization



Words are converted into phoneme sequences with atomic digraph handling.



\### 3.2 Segmentation



The corpus is split into segments by `|`.



Two representations:



\* continuous stream (boundaries removed)

\* segment list (structure preserved)



\---



\## 4. Metrics



Only one metric is used:



\### Mean Gap



Mean distance between repeated k-gram occurrences.



Interpretation:



\* lower gap → stronger clustering



\---



\## 5. Tests



\### B′1. Baseline (continuous stream)



\* compute gap on full flattened stream



\---



\### B′2. Boundary-aware



\* compute gap separately inside each segment

\* average across segments



Purpose:



\* tests whether clustering exists within segments only



\---



\### B′3. Full shuffle



\* randomly shuffle entire phoneme stream



Purpose:



\* destroys all structure

\* tests frequency-only explanation



\---



\### B′4. Segment-order shuffle



\* shuffle segments as blocks

\* preserve internal segment structure



Purpose:



\* tests dependence on segment ordering



\---



\## 6. Statistical evaluation



Z-scores computed:



Z = (observed − mean\_null) / sd\_null



Reported:



\* Z\_full (vs full shuffle)

\* Z\_segment (vs segment shuffle)



\---



\## 7. Baseline parameters



\* k = 3

\* mode = exact

\* perm = 1000

\* seed = 1



\---



\## 8. Interpretation



\* If boundary gap ≈ baseline → clustering is intra-segment

\* If boundary gap << baseline → cross-boundary structure exists

\* If Z\_segment drops → structure depends on segment order

\* If Z\_full remains strong → effect is non-trivial



\---



\## 9. Role



This analysis verifies that Layer B clustering:



\* is not reducible to phoneme frequencies

\* is not confined to boundaries

\* partially depends on segment ordering



It is a control layer, not a primary result.



