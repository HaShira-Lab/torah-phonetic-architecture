\# layer a — dominant consonant-unit recurrence



version: v1.0  

status: locked  

script: `layer\_a\_consonant\_family.py`



\---



\## 1. objective



This layer tests whether the locally dominant consonant units remain stable across neighboring sliding windows more strongly than expected under a block-permutation null model.



The signal measured here is:



> persistence of top-N consonant units across local windows.



\---



\## 2. input



Input files are preprocessed phonetic corpora:



\- `\*\_phonetic.txt`



Format:



\- whitespace-separated tokens

\- boundary marker: `|`



Baseline input set:



\- `genesis\_phonetic.txt`

\- `exodus\_phonetic.txt`

\- `leviticus\_phonetic.txt`

\- `numbers\_phonetic.txt`

\- `deuteronomy\_phonetic.txt`

\- `hagamad\_phonetic.txt`



This baseline uses the default phonetic preprocessing variant:



\- qamats = `a`



\---



\## 3. representation



\### 3.1 atomic units



Each transliterated token is decomposed into phonetic atoms.



Single-character atoms:

\- `b d g h k l m n p q r s t v y z ...`



Multi-character atoms treated as single units:

\- `sh`

\- `kh`

\- `ts`



Tokenization is left-to-right, prioritizing digraph matches (sh, kh, ts) before single-character atoms.

Vowel removal is applied after tokenization and before any further transformations.



Important:



In this script, the historical term `family` means only:



> atomic consonant unit in the locked phonetic representation



No extra grouping, equivalence collapsing, or consonant-class merging is applied.



\---



\## 4. consonant stream construction



For each token:



1\. tokenize into phonetic atoms

2\. remove vowels:

&#x20;  - `a e i o u`

3\. keep only consonant atoms



Thus each corpus becomes a consonant stream:



`t1, t2, t3, ..., tn`



\---



\## 5. boundary handling



\### baseline mode

`--respect\_boundaries 0`



\- boundary marker `|` is removed

\- the full corpus becomes one continuous consonant stream



\### boundary-aware variant

`--respect\_boundaries 1`



\- the corpus is split into segments by `|`

\- windows are built independently inside each segment

\- windows do not cross boundaries



\---



\## 6. windowing



Baseline parameters:



\- `W = 150`

\- `step = 25`



Sliding windows are built over the consonant stream.



For continuous mode:



\- one stream

\- one sliding-window series



For boundary-aware mode:



\- windows are built separately inside each segment



Windows shorter than `W` are ignored.



\---



\## 7. local profile



For each window:



1\. count consonant-atom frequencies

2\. rank by:

&#x20;  - descending frequency

&#x20;  - alphabetical order as deterministic tie-break

3\. keep the top `N` atoms



Baseline:



\- `top\_n = 3`



This defines the window profile:



`profile(w) = {c1, c2, c3}`



\---



\## 8. recurrence metric



For two windows:



`overlap(wi, wj) = |topN(wi) ∩ topN(wj)|`



Range:



`0 <= overlap <= top\_n`



No weighting is applied inside overlap itself.



\---



\## 9. aggregated metrics



\### 9.1 global recurrence



Mean overlap across all pairs:



\- lags `1..max\_lag`



Weighted by number of contributing pairs.



Baseline:



\- `max\_lag = 20`



\### 9.2 short-lag recurrence



Mean overlap across:



\- lags `1..short\_lag\_to`



Baseline:



\- `short\_lag\_to = 5`



\### 9.3 lag profile



For each lag:



\- observed mean overlap

\- null mean overlap

\- null sd

\- z-score



\### 9.4 best lag



Descriptive only:



\- lag with maximal observed mean overlap



\---



\## 10. null model



Primary null:



\- block permutation



Procedure:



1\. split each segment into non-overlapping blocks of size `block`

2\. shuffle the blocks

3\. preserve the internal order within each block



If `respect\_boundaries = 0`:



\- the whole corpus is one segment



If `respect\_boundaries = 1`:



\- each boundary-defined segment is shuffled independently



Baseline null parameters:



\- `block = 80`

\- `perm = 1000`

\- `seed = 1`



\---



\## 11. statistics



For each metric:



\- observed value

\- null distribution

\- null mean

\- null sd

\- z-score



Formula:



`Z = (obs - mean\_null) / sd\_null`



If null sd = 0:



\- `Z = NaN`



Population SD is used (`pstdev`).



\---



\## 12. baseline run



Baseline parameters:



\- `W = 150`

\- `step = 25`

\- `top\_n = 3`

\- `max\_lag = 20`

\- `short\_lag\_to = 5`

\- `block = 80`

\- `perm = 1000`

\- `seed = 1`

\- `respect\_boundaries = 0`



This is the main reportable run.



\---



\## 13. stress tests



Stress tests are run independently relative to baseline.



\### window size

\- `W = 100`

\- `W = 200`



\### top\_n

\- `top\_n = 2`

\- `top\_n = 4`



\### null block size

\- `block = 50`

\- `block = 120`



\### boundary-aware variant

The boundary-aware configuration (`respect_boundaries = 1`) was tested.

At the baseline window scale (`W = 150`), no valid windows were formed due to short segment lengths.

Therefore, this variant is not applicable at this scale and is not included in the reported stress results.


No full combinatorial grid is required.



\---



\## 14. outputs



All outputs are written under a user-specified output directory.



\### per-book outputs

For each corpus:



\- `books/<corpus>/layer\_a\_<tag>\_summary.csv`

\- `books/<corpus>/layer\_a\_<tag>\_lag\_profile.csv`



\### combined outputs

At output root:



\- `layer\_a\_<tag>\_summary\_all.csv`

\- `layer\_a\_<tag>\_lag\_profile\_all.csv`

\- `layer\_a\_<tag>\_important\_summary.csv`

\- `layer\_a\_<tag>\_run\_manifest.json`



\---



\## 15. stdout



For each corpus the script prints:



\- corpus

\- stream length

\- number of segments

\- number of windows

\- parameters

\- global overlap

\- short overlap

\- z-scores

\- best lag



At the end it prints a compact top-line summary for all corpora.



These values are intended for direct copying into discussion logs.



\---



\## 16. interpretation



A positive `z\_global\_overlap` or `z\_short\_overlap` indicates that the dominant consonant units remain stable across neighboring windows more strongly than expected under locally constrained block shuffling.



Because the null preserves:



\- local composition inside blocks

\- overall atom inventory

\- local chunk order within each block



while disrupting broader coordination, a significant positive effect is interpreted as structured local recurrence beyond trivial local texture.



\---



\## 17. limitations



This layer detects:



\- persistence of locally dominant consonant units



It does not detect:



\- unordered consonant-group dominance

\- phonetic chains

\- consonant equivalence classes

\- larger compositional motifs



Those belong to later or separate analyses.



\---



\## 18. reproducibility



Each run records:



\- explicit input file paths

\- parameter values

\- seed

\- tag

\- output file paths



Seed is fixed by default:



\- `seed = 1`



Any change in logic or parameter interpretation requires a new version.

