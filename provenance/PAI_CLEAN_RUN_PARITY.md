# Clean-run reproducibility parity

The standalone `code/run_pai_v3_gate.py` was executed twice from empty output directories against the same three hash-locked public Alibaba PAI archives.

Both runs returned:

- decision: `PASS_TO_V3`
- selected pair: `bert`, `ctr`
- complete Monday weeks: 9
- `det(A) = -3.708103634587713`
- `cond_2(A) = 16.337376894397448`
- `k_M = 1`
- `k_TA = 0`
- `k_core = 0`
- seven-weekday classification robustness: PASS

Byte-identical output hashes across both runs:

- `results.json`: `14221c014f2d445ba7ec5804b1ff51e64253d839778501c60846d3d8245f7a0d`
- `weekly.csv`: `fef26fb24f575b73338561a670fbf07a1064d427c2109ed7a839c43aacaa0774`
- `alignment.csv`: `551442b1f2290c13a06f1fc0c097eafb5f695f92a96ea259b4d0b4be797d7485`

Decision: **CLEAN-RUN PARITY PASS**.
