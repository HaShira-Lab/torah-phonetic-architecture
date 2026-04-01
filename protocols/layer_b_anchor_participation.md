\# Layer B — Anchor Participation Test



\## 1. Objective



To test whether consonant anchors participate in recurring bidirectional phonetic contexts.



Hypothesis:



> the same consonant functions as a structural anchor linking left and right phonetic environments, and these anchor-context patterns recur more strongly than expected under a block-shuffle null.



\---



\## 2. Input



Same fixed phonetic corpora as Layer B:



\- whitespace-separated tokens

\- boundary marker `|` removed

\- digraphs `sh`, `kh`, `ts` treated as atomic phonemes



\---



\## 3. Preprocessing



Identical to Layer B:



\- tokenize into phoneme atoms

\- remove `|`

\- build one continuous phoneme stream



Vowels:



\- `a e i o u`



Anchors:



\- all non-vowel phonemes



\---



\## 4. Anchor-centered units



For each consonant anchor at position `i`, with `1 <= i <= N-2`:



\- left context = `p\[i-1]`

\- anchor = `p\[i]`

\- right context = `p\[i+1]`



Unit:



`(anchor, left, right)`



This is not treated as an ordinary k-gram stream.

It is treated as an anchor-participation event.



\---



\## 5. Metrics



\### 5.1 Token Repeat Fraction



Proportion of anchor-events belonging to repeated anchor-context types.



\### 5.2 Type Repeat Fraction



Proportion of unique anchor-context types that recur.



\### 5.3 Mean Gap



For each repeated anchor-context type, compute distances between successive occurrences in the anchor-event sequence.



Negative `z\_mean\_gap` indicates tighter clustering than expected.



\---



\## 6. Null model



Block-shuffle null on the full phoneme stream:



1\. split stream into non-overlapping blocks

2\. shuffle blocks

3\. preserve internal order within each block

4\. rebuild anchor-events after shuffle



Baseline:



\- `block = 80`

\- `perm = 1000`

\- `seed = 1`



Stress:



\- `block = 40`

\- `block = 120`



\---



\## 7. Statistical evaluation



For each metric:



`Z = (obs - mean\_null) / sd\_null`



Reported:



\- `z\_token\_repeat`

\- `z\_type\_repeat`

\- `z\_mean\_gap`



\---



\## 8. Baseline



\- exact mode

\- block = 80

\- perm = 1000

\- seed = 1



\---



\## 9. Stress



\- equivalence mode

\- block = 40

\- block = 120



Equivalence mode uses the same conservative normalization as Layer B:



\- `d -> t`

\- `z -> s`

\- `q -> k`

\- `v -> b`



\---



\## 10. Interpretation



If strong signal is observed:



\- consonants act as anchors of recurring bidirectional context

\- phonetic organization is not only sequential, but anchor-centered



If results closely match ordinary Layer B:



\- anchor participation may be largely reducible to sequential chain recurrence



\---



\## 11. Role in architecture



This test evaluates whether Layer B can be refined from:



\- sequence recurrence



to:



\- anchor-centered recurrence



It is intended as a comparison layer, not a replacement for Layer B unless it proves clearly more explanatory.

