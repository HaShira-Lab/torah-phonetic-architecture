\# Phonetic Preprocessing Protocol



Version: v1.0 (LOCKED)  

Matches: preprocessing_phonetic.py (exact implementation)



\---



\## 1. Definition



Deterministic transformation:



RAW TEXT → PHONETIC TOKEN STREAM



No probabilistic elements.



\---



\## 2. Input



\### Torah

\- Hebrew text with niqqud and taamim



\### Modern

\- Hebrew text with punctuation



\---



\## 3. Token Filtering



A token is processed ONLY if:

\- contains Hebrew letters

\- AND contains vocalization marks



Otherwise:

→ discarded



\---



\## 4. Normalization



\- maqaf → space

\- remove:

&#x20; - brackets

&#x20; - parentheses

&#x20; - numbers

\- collapse whitespace



\---



\## 5. Letter Normalization



Final letters:



ך → כ  

ם → מ  

ן → נ  

ף → פ  

ץ → צ  



\---



\## 6. Special Replacements



Before processing:



יהוה → adonai  

אלהים / אלוהים → elohim  



\---



\## 7. Parsing Model



Token → sequence of units:



u = (letter, marks\[])



Marks include:

\- vowels

\- dagesh

\- sheva

\- shin/sin dot

\- (Torah: also cantillation marks retained)



\---



\## 8. Vowel System



Mapping:



ֱ → e  

ֲ → a  

ֳ → a  

ִ → i  

ֵ → e  

ֶ → e  

ַ → a  

ָ → a   (qamats = default)  

ֹ → o  

ֻ → u  



\---



\## 9. Qamats



Fixed:



qamats = a



(No qamats gadol/qatan distinction)



\---



\## 10. Vowel Extraction



Priority:



1\. ו + dagesh + no vowel → u  

2\. vowel mark  

3\. Ø  



\---



\## 11. Consonant Mapping



\### Silent



א → Ø  

ע → Ø  



\### ה



\- final → Ø  

\- else → h  



\### Begadkefat



ב → b / v  

כ → k / kh  

פ → p / f  



\### Shin



שׂ → s  

שׁ → sh  



\### Fixed



צ → ts  

ק → q  

ח → h  

ט → t  

ת → t  



ג → g  

ד → d  

ז → z  

ל → l  

מ → m  

נ → n  

ס → s  

ר → r  



\### ו



\- vowel (o/u) → Ø  

\- else → v  



\### י



context-dependent (see below)



\---



\## 12. Yod Rules



If no vowel:



\- first position OR previous ≠ i → y  

\- else → Ø  



If vowel:



\- i + previous i → i  

\- else → y + vowel  



\---



\## 13. Sheva Rules



\- final → Ø  

\- initial → e  

\- after sheva → e  

\- before guttural+vowel → e  

\- before sheva → Ø  

\- after (o,u) → e  

\- else → Ø  



\---



\## 14. Special Rule



Final ח + vowel a → "ah"



\---



\## 15. Segment Construction



Default:



C + V



Exception:



ו carrying (o/u) → vowel only



\---



\## 16. Boundary System



All boundaries → "|"



\### Torah



Inserted after tokens containing:

\- Sof Pasuq

\- Atnah

\- Zaqef Katan



\### Modern



Converted to "|":

\- . ? ! ; : ,

\- ellipsis (...)



Removed:

\- dashes (– — -)



\---



\## 17. Output Format



\- tokens separated by spaces

\- boundaries = "|"

\- ASCII only



\---



\## 18. Meta Output



For each file:



.meta.json with:



\- mode

\- qamats

\- input SHA256

\- output SHA256

\- timestamp



\---



\## 19. Atomic Units



Multi-character sequences:



kh, ts, sh



→ represent single phonetic units



They MUST be treated as atomic in all analyses.



\---



\## 20. Determinism



Same input → identical output



\---



\## 21. Scope



Model does NOT encode:



\- stress

\- prosody

\- morphology

\- syntax



\---



\## 22. Model Philosophy



Minimal deterministic mapping designed to test:



> emergence of large-scale phonetic structure



\---



\## 23. Status



LOCKED



Any change requires new version.

