# A Global Multi-Layer Phonetic Network in the Biblical Pentateuch

## Overview

This repository accompanies the study:

**“A global multi-layer phonetic network in the Biblical Pentateuch”**

The project investigates large-scale phonetic organization in the Biblical Pentateuch using a reproducible computational framework. The analysis models phonetic structure as a multi-layer system consisting of:

- consonantal clustering (Layer A)  
- boundary-aligned phonetic chains (Layer B)  
- syllabic / rhyme-like correspondence (Layer C)  

The study compares the Pentateuch to a modern Hebrew prose corpus and evaluates statistical structure using controlled randomization.

This repository contains all code and data required to reproduce the results reported in the study.

---

## Repository Structure

- paper/
- src/
  - analyses/
  - figures/
  - preprocessing/
- data/
  - data_raw/
  - data_processed/
- results/
- protocols/
- run/

---

## Paper

Preprint available on Zenodo:  
https://doi.org/10.5281/zenodo.19653193

A PDF version is included in this repository:  
paper/multilayer_phonetic_network_pentateuch_v2.pdf

---

## Data Sources

### Primary corpus (Torah)

- Source: Sefaria API  
- Version: *Tanach with Ta'amei HaMikra*  
- Content: Genesis, Exodus, Leviticus, Numbers, Deuteronomy  
- Features: niqqud + cantillation (cantillation removed during preprocessing)

### Comparison corpus (Modern Hebrew)

- Text: *HaGamad Baal HaChotem*  
  (*Dwarf Long-Nose*) 
- Source: Ben Yehuda Project  
- Features: niqqud, no cantillation  

---

## Data

Processed phonetic text files are located in:

data/data_processed/

These were generated from fully vocalized Hebrew sources with standardized preprocessing (see protocols).

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
Outputs are provided in CSV format across analyses; intermediate formats may vary by analysis but all results are reproducible from the provided scripts.

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
- Figure 4-5 → model visualization  

---

## Figure generation

Figures are generated from precomputed analysis outputs.

Before running figure scripts, the corresponding analysis must be executed.

Example (Layer C density figure):

    run\layer_c_window_density.bat
    run\fig4_layer_c_torah_stream.bat

Figure scripts do not perform analysis themselves and require existing data in the `results/` directory.

---

## Running the analyses

All analysis scripts are executed from the repository root directory.  
All paths inside `.bat` files are defined relative to this root.

Example:

    run\layer_a_consonant_family.bat

Running scripts from other directories may result in incorrect path resolution.

---

## Quick start

Clone the repository and run analyses from the root directory.

Example (Layer C density figure):

    run\layer_c_window_density.bat
    run\fig4_layer_c_torah_stream.bat

Figures require precomputed results and will fail if the corresponding analysis has not been executed.

Ensure that all required input data is present before running analysis scripts.

---

## Requirements

- Python 3.x
- Required libraries:
  - numpy
  - pandas
  - matplotlib

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

If you use this repository or the associated dataset, please cite:

Glikshtern E. A global multi-layer phonetic network in the Biblical Pentateuch. 2026. https://doi.org/10.5281/zenodo.19653193

