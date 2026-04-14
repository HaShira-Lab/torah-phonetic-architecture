# A Global Multi-Layer Phonetic Network Underlying the Biblical Pentateuch

## Overview

This repository accompanies the study:

**“A global multi-layer phonetic network underlying the Biblical Pentateuch”**

The project investigates large-scale phonetic organization in the Biblical Pentateuch using a reproducible computational framework. The analysis models phonetic structure as a multi-layer system consisting of:

- consonantal clustering (Layer A)  
- boundary-aligned phonetic chains (Layer B)  
- syllabic / rhyme-like correspondence (Layer C)  

The study compares the Pentateuch to a modern Hebrew prose corpus and evaluates statistical structure using controlled randomization.

---

## Repository Structure
torah-phonetic-architecture/
│
├── src/
│ ├── analyses/
│ │ ├── layer_a/
│ │ ├── layer_b/
│ │ └── layer_c/
│ ├── figures/
│ └── preprocessing/
│
├── data/
│ ├── data_raw/
│ │ ├── torah/
│ │ └── modern/
│ └── data_processed/
│ ├── torah/
│ └── modern/
│
├── results/
│ ├── layer_a/
│ ├── layer_b/
│ └── layer_c/
│
├── protocols/
│
├── run/
│
└── README.md


---

## Data Sources

### Primary corpus (Torah)

- Source: Sefaria API  
- Version: *Tanach with Ta'amei HaMikra*  
- Content: Genesis, Exodus, Leviticus, Numbers, Deuteronomy  
- Features: niqqud + cantillation (cantillation removed during preprocessing)

### Comparison corpus (Modern Hebrew)

- Text: *HaGamad Baal HaChotem*  
  (*The Dwarf with the Nose Ring*, Haim Nahman Bialik)  
- Source: Ben Yehuda Project  
- Features: niqqud, no cantillation  

---

## Preprocessing

The preprocessing pipeline:

- retains consonants and niqqud  
- removes cantillation marks  
- normalizes punctuation and boundaries  
- separates maqaf-linked forms  
- encodes phrase boundaries using a dedicated delimiter  

The output is a continuous phonetic stream preserving word and phrase structure.

---

## Phonetic Representation

- vowels mapped to {a, e, i, o, u}  
- consonants encoded with preserved phonemic contrasts  
- digraphs (sh, kh, ts) treated as atomic units  
- yod treated as a consonant  

The encoding is deterministic and applied identically across corpora.

---

## Analytical Framework

### Layer A — Consonantal structure
- recurrence of k-sequences (k = 2–4)  
- clustering and dominant sets  
- metrics: recurrence density, gap, overlap  

### Layer B — Phonetic chain structure
- recurrence across the stream  
- sensitivity to segmentation  
- boundary-aware vs shuffled controls  

### Layer C — Syllabic / rhyme structure
- syllabic correspondence units  
- distance-selective recurrence  
- positional concentration (word-final, phrase-final)  
- window-based density  

---

## Null Models

- block-randomized shuffling (preserves local distributions)  
- segment-level controls (boundary-sensitive)  
- permutation-based significance testing (Z-scores)  

---

## Reproducibility

All analyses are reproducible from the repository.

Typical workflow:

1. preprocess data  
2. run analysis scripts via `/run/*.bat`  
3. outputs written to `/results/`  
4. figures generated from results  

All parameters (block size, k, L, window size, permutations) are defined in scripts and protocols.

---

## Protocols

Detailed analysis protocols are provided in:


/protocols/


Each document describes:
- input format  
- parameters  
- metrics  
- null models  
- expected outputs  

---

## Figures

Figures are generated from analysis outputs using scripts in:


src/figures/


Mapping:

- Figure 1 → Layer A (consonantal structure)  
- Figure 2 → Layer B (boundary alignment)  
- Figure 3 → Layer C (syllabic correspondence)  
- Figure 4/5 → model visualization  

---

## License

MIT License

---

## Notes

- The study is computational and observational  
- No human subjects are involved  
- The phonetic representation is a controlled analytic encoding, not a full phonological reconstruction

---

## Citation

If you use this repository, please cite:
[preprint link]
