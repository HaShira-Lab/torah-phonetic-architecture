\# Project I/O Standard



This document defines the unified input/output and execution conventions for all scripts in the project.



\---



\## 1. General Principle



All scripts must be:



\- deterministic (given fixed seed and inputs)

\- reproducible

\- explicit in inputs and outputs



No script should rely on implicit paths or hidden defaults.



\---



\## 2. Input Specification



All scripts (except web download scripts) must receive:



\### Required:



\- explicit list of input files  

\- output root directory  



\### Example:



```bash

python script.py file1.txt file2.txt --outdir results/C1/L20

