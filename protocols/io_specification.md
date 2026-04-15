# Project I/O and Execution Specification

This document defines the unified input/output and execution conventions for all scripts in the project.

---

## 1. General Principles

All analyses in this project are designed to be:

- deterministic (given fixed seeds and inputs)
- reproducible
- explicit in their data flow
- consistent across all layers (A, B, C)

All paths, parameters, and outputs are defined in a transparent and structured manner.

---

## 2. Execution Model

All analyses are executed via wrapper scripts (`.bat` files) located in the `/run/` directory.

These scripts:

- define input file paths  
- define output directories  
- specify analysis parameters  
- invoke the corresponding Python scripts  

All scripts are intended to be executed from the repository root directory.

### Example

```bash
run\layer_a_consonant_family.bat

Running scripts from other directories may result in incorrect path resolution.

## 3. Input Specification

Input files are not passed directly via command-line arguments in most cases.
Instead, they are defined within the .bat wrapper scripts.

Typical inputs include:

processed phonetic text files (data/data_processed/...)
configuration parameters (defined in .bat or script defaults)

All input data is explicitly referenced through the execution layer.

## 4. Output Specification

All outputs are written under the results/ directory.

Each analysis follows a consistent structure:

layer-specific subdirectory (layer_a/, layer_b/, layer_c/)
run-specific subdirectories (e.g., baseline/, stress/)
optional per-book outputs (books/)
summary CSV files
console summary output
Example structure
results/
  layer_c/
    baseline/
      summary.csv
      books/
        genesis.csv
        exodus.csv

All outputs are reproducible and derived solely from the specified inputs and parameters.

## 5. Figures and Visualization

Figures are generated separately from analysis outputs using scripts in:

src/figures/

These scripts:

read precomputed results (CSV files)
generate publication-ready figures
do not perform primary analysis

All figure generation is deterministic given fixed inputs.

## 6. Determinism and Randomization

Randomized procedures (e.g., null models) follow strict rules:

fixed random seeds
explicitly defined parameters (block size, permutations, etc.)
reproducible outputs across runs

All randomization settings are documented in the corresponding analysis protocols.

## 7. Consistency Across Analyses

All layers (A, B, C) follow a unified design:

shared preprocessing assumptions
consistent directory structure
consistent output formats
consistent statistical framework

This ensures comparability across analytical layers.

## 8. Relationship to Protocols

Detailed methodological descriptions are provided in:

/protocols/

These documents define:

analytical logic
parameter choices
metric definitions
statistical tests

This specification complements those documents by defining execution and data flow.

## 9. Scope

This specification applies to:

all analysis scripts in /src/analyses/
all execution scripts in /run/
all figure scripts in /src/figures/

It does not define theoretical or statistical methodology, which is described separately in the analysis protocols.