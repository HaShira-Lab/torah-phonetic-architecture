\# Layer A+ — Local Dominant Consonant Sets (LDCS)



\## 1. Objective



To detect and quantify:



> local stability of dominant consonant sets in non-overlapping segments



Hypothesis:



> the Torah exhibits locally stable sets of co-dominant consonants beyond block-permutation expectations.



\---



\## 2. Input Data



\* Preprocessed phonetic corpora: \*\_phonetic.txt



\* Same pipeline as Layer A



\* Tokens: whitespace-separated



\* Boundary marker "|" removed



Baseline input set:



\* genesis\_phonetic.txt



\* exodus\_phonetic.txt



\* leviticus\_phonetic.txt



\* numbers\_phonetic.txt



\* deuteronomy\_phonetic.txt



\* hagamad\_phonetic.txt



\---



\## 3. Phonetic Processing



\* Digraphs treated as atomic: sh, kh, ts



\* Tokenization is left-to-right, prioritizing digraph matches (sh, kh, ts)



\* Vowels removed: a, e, i, o, u



\* Vowel removal is applied after tokenization



\* Result: consonant stream



\---



\## 4. Segmentation



\* Non-overlapping segments



Parameters:



\* segment length L ∈ {100, 150, 200}



Procedure:



\* stream → segments of size L



\* remainder discarded



\---



\## 5. Dominant Set Construction



Mode: topk (baseline and reportable)



\* Count frequencies per segment



\* Rank by:



&#x20; \* descending frequency



&#x20; \* alphabetical order (deterministic tie-break)



\* Select top-k consonants



\* Sort alphabetically



Parameters:



\* k ∈ {2, 3, 4}



Result:



\* dominant\_set(segment) = unordered set (stored as sorted tuple)



\---



\## 6. Metrics



\### 6.1 Adjacent Jaccard (primary)



J(Sᵢ, Sᵢ₊₁)



Primary metric:



\* mean adjacent Jaccard



\---



\### 6.2 Lag Profile



Jaccard similarity computed across segment lags:



\* lags 1..max\_lag



Baseline:



\* max\_lag = 10



For each lag:



\* observed mean Jaccard



\* null mean



\* null sd



\* Z-score



\* number of pairs



\---



\### 6.3 Dominance Mass



Fraction of segment covered by dominant set



Metric:



\* mean dominance mass



\---



\### 6.4 Recurrence (secondary)



Whether similar set appears within R segments



Parameters:



\* R = 5



\* min\_jaccard = 0.5



Metric:



\* fraction of segments with recurrence



\---



\## 7. Null Model



Block permutation



Procedure:



\* split stream into blocks



\* shuffle blocks



\* preserve internal order within each block



\* rebuild segments AFTER shuffle



Parameters:



\* block ∈ {50, 80, 120}



\* perm = 1000



\* seed = 1



\---



\## 8. Statistics



For each metric:



Z = (obs − mean\_null) / sd\_null



If null sd = 0:



\* Z = NaN



Population SD is used.



\---



\## 9. Baseline Run



Baseline parameters:



\* L = 150



\* mode = topk



\* k = 3



\* max\_lag = 10



\* R = 5



\* min\_jaccard = 0.5



\* block = 80



\* perm = 1000



\* seed = 1



This is the main reportable configuration.



\---



\## 10. Stress Tests



Stress tests are run independently relative to baseline.



\### Segment size



\* L = 100



\* L = 200



\### Set size



\* k = 2



\* k = 4



\### Null



\* block = 50



\* block = 120



No full combinatorial grid is required.



\---



\## 11. Output



All outputs are written under a user-specified output directory.



\### Per-book outputs



For each corpus:



\* books/<corpus>/layer\_a\_plus\_<tag>\_summary.csv



\### Combined outputs



At output root:



\* layer\_a\_plus\_<tag>\_summary\_all.csv



\* layer\_a\_plus\_<tag>\_lag\_profile\_all.csv



\* layer\_a\_plus\_<tag>\_important\_summary.csv



\* layer\_a\_plus\_<tag>\_run\_manifest.json



\---



\## 12. Stdout



For each corpus the script prints:



\* corpus



\* stream length



\* number of segments



\* parameters



\* adjacent Jaccard



\* recurrence rate



\* dominance mass



\* Z-scores



At the end it prints a compact top-line summary for all corpora.



\---



\## 13. Interpretation



Positive Z indicates:



> stability of dominant consonant sets beyond local frequency structure



The null preserves:



\* local composition inside blocks



\* overall atom inventory



\* local order within blocks



while disrupting broader coordination.



Important:



\* no overlapping windows



\* no ordering assumption in set comparison



\* ties in ranking are resolved alphabetically



\---



\## 14. Limitations



This layer detects:



\* stability of unordered dominant consonant sets



It does not detect:



\* ordered phonetic chains



\* syllabic structure



\* rhyme



\* phonetic equivalence classes



\* larger compositional motifs



\---



\## 15. Position in Project



Layer A+ extends Layer A:



\* Layer A: repetition of dominant elements



\* Layer A+: stability of unordered dominant sets



Together:



> local phonetic regimes



