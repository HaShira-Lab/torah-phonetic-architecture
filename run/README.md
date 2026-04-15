# Run scripts

This directory contains execution scripts for analyses and figures.

All scripts must be run from the repository root:

Typical workflow:

1. Run analysis scripts to generate data:
   run\layer_*.bat

2. Run figure scripts:
   run\fig*.bat

Figure scripts depend on existing results and will fail if data is not generated.

Each script:

\- defines input paths

\- defines output directories

\- runs a specific analysis pipeline

