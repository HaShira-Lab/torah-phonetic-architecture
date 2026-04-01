\# Layer B — Local Phonetic Chains



\## Organized reproducible version



\### 1. Objective



This analysis quantifies local phonetic regularity in the transliterated phonetic stream by measuring:



\- density of repeated short phoneme chains (k-grams)

\- spatial clustering of their repetitions



It is a full-phoneme-stream analysis and does not rely on syllabification.



\---



\### 2. Input



Input files are the project’s fixed transliterated phonetic corpora.



Expected alphabet:



\- vowels: `a e i o u`

\- consonants: `b g d h v z kh t y k l m n s p ts q r sh`

\- boundary marker: `|`



Input is whitespace-separated text.



Baseline input set:



\- `genesis\_phonetic.txt`

\- `exodus\_phonetic.txt`

\- `leviticus\_phonetic.txt`

\- `numbers\_phonetic.txt`

\- `deuteronomy\_phonetic.txt`

\- `hagamad\_phonetic.txt`



This analysis uses the default phonetic preprocessing variant:



\- qamats = `a`



\---



\### 3. Preprocessing



\#### 3.1 Boundary handling



Phrase-boundary markers `|` are removed before analysis.



The analysis is performed on one continuous phoneme stream.



\#### 3.2 Phoneme tokenization



Words are tokenized phonemically, not character-by-character.



Tokenization is left-to-right, prioritizing digraph matches before single-character atoms.



The following digraphs are treated as atomic phonemes:



\- `sh`

\- `kh`

\- `ts`



Example:



\- `bereshit -> b e r e sh i t`

\- `tsedek -> ts e d e k`



\#### 3.3 Stream construction



All phonemes are concatenated into a single sequence:



`\[p1, p2, p3, ..., pN]`



This stream includes all transition types:



\- C→V

\- V→C

\- C→C

\- V→V



\#### 3.4 Special commitments



\- `y` is treated as a consonantal phoneme.

\- No syllabification is used.

\- No lexical or morphological adjustment is applied.



\---



\### 4. Matching modes



\#### 4.1 Exact mode (primary)



Two k-grams match only if all phonemes are identical.



Examples:



\- `(e,t) = (e,t)`

\- `(e,t) != (e,d)`



\#### 4.2 Equivalence mode (robustness only)



A conservative normalization is applied before k-gram construction:



\- `d -> t`

\- `z -> s`

\- `q -> k`

\- `v -> b`



Digraphs remain unchanged:



\- `sh -> sh`

\- `kh -> kh`

\- `ts -> ts`



Equivalence mode is used strictly as a robustness check, not as the primary analysis.



\---



\### 5. k-gram construction



For a chosen k, all contiguous k-grams are extracted:



`g\_i = (p\_i, p\_{i+1}, ..., p\_{i+k-1})`



Frozen settings:



\- baseline: `k = 3`

\- support: `k = 2`

\- support: `k = 4`



Appendix-level diagnostic only:



\- `k = 5`



\---



\### 6. Metrics



\#### 6.1 Token Repeat Fraction



Proportion of all k-gram tokens that belong to repeated types:



`token\_repeat\_fraction = (# occurrences of k-grams with frequency > 1) / (total # of k-grams)`



\#### 6.2 Type Repeat Fraction



Proportion of unique k-gram types that recur:



`type\_repeat\_fraction = (# unique k-grams with frequency > 1) / (total # of unique k-grams)`



\#### 6.3 Hapax Fraction



Proportion of unique k-gram types occurring only once:



`hapax\_fraction = (# unique k-grams with frequency = 1) / (total # of unique k-grams)`



This is descriptive and not a primary inferential metric.



\#### 6.4 Gap metrics



For each repeated k-gram with positions `\[i1, i2, i3, ...]`, inter-occurrence distances are:



`gap\_j = i\_{j+1} - i\_j`



Reported:



\- mean gap

\- median gap

\- number of gaps



Interpretation:



\- negative `z\_mean\_gap` means stronger clustering than expected



Median gap is descriptive only.



\---



\### 7. Null model



A block-shuffle null model is used.



Procedure:



1\. split the phoneme stream into non-overlapping blocks of size `B`

2\. randomly permute blocks

3\. preserve internal order within each block



Frozen baseline settings:



\- `block = 80`

\- `perm = 1000`

\- `seed = 1`



Stress settings:



\- `block = 40`

\- `block = 120`



\---



\### 8. Statistical evaluation



For each metric:



`Z = (observed - mean\_null) / sd\_null`



Primary reported Z-scores:



\- `z\_token\_repeat`

\- `z\_type\_repeat`

\- `z\_mean\_gap`



Interpretation:



\- `z\_token\_repeat > 0` -> more repeated k-gram mass than expected

\- `z\_type\_repeat > 0` -> more recurring k-gram types than expected

\- `z\_mean\_gap < 0` -> repeated k-grams are more tightly clustered than expected



Population SD is used.



If null SD = 0:



\- Z is reported as `NA`



\---



\### 9. Output files



All outputs are written under a user-specified output directory.



Recommended root:



`results/layer\_b\_local\_phonetic\_chains/`



\#### 9.1 Per-book outputs



For each corpus:



\- `books/<corpus>/layer\_b\_<tag>\_metrics.csv`



\#### 9.2 Combined outputs



At output root:



\- `layer\_b\_<tag>\_summary\_all.csv`

\- `layer\_b\_<tag>\_important\_summary.csv`

\- `layer\_b\_<tag>\_run\_manifest.json`



\---



\### 10. Stdout



For each corpus the script prints:



\- book

\- mode

\- k

\- block size

\- permutations

\- stream length

\- total k-grams

\- total types

\- token-repeat result

\- type-repeat result

\- mean-gap result



At the end it prints a compact top-line summary across corpora.



These values are intended for direct copying into discussion logs.



\---



\### 11. Frozen main settings



Primary result:



\- `k = 3`

\- `mode = exact`

\- `block = 80`

\- `perm = 1000`

\- `seed = 1`



Support:



\- `k = 2`

\- `mode = exact`



Support:



\- `k = 4`

\- `mode = exact`



Robustness:



\- `k = 3`

\- `mode = equiv`



Stress:



\- `k = 3`

\- `block = 40`

\- `block = 120`



Appendix diagnostic:



\- `k = 5`

\- Genesis and HaGamad only



\---



\### 12. Role in the architecture



This layer establishes a dense local phonetic texture in the continuous phoneme stream.



It does not by itself establish:



\- syllabic structure

\- rhyme structure

\- directionality

\- large-scale intentional architecture



It is a foundational phonetic-textural layer.

