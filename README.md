# Cross-Arithmetic Reliability of Fully Fuzzy Linear Systems

Reproducibility repository for the conference paper:

**Cross-Arithmetic Reliability of Fully Fuzzy Linear Systems in Photovoltaic and Production Computing Applications**

This repository contains deterministic analysis scripts, derived reproducibility data, and provenance/verification records supporting the reported cross-arithmetic FFLS results.

## Scope

The repository supports the paper's family-relative cross-arithmetic reliability analysis. It does **not** claim universal arithmetic superiority, improved photovoltaic performance, improved cluster scheduling, or prospective downstream validation.

## Reproducibility contents

- `code/` - primary Alibaba PAI replay, crossed 5x7 sensitivity analysis, spread-scale verification, and independent-benchmark verification.
- `data/` - the primary weekly balance output, full 35-case PAI sensitivity table and summary, weekday alignment results, spread-scale thresholds, full primary PAI replay results, and independent-benchmark output.
- `provenance/` - official PAI source-file hash lock, clean-run parity record, and source/literature audit.

## Data availability boundary

The GitHub repository contains **code and derived reproducibility data supporting the reported results**. Raw third-party source datasets are not redistributed here. The Alibaba PAI archives remain available from the official Alibaba Cluster Trace source, and the PVDAQ source remains available from NREL/OEDI. The replay code checks the official Alibaba archive and member SHA-256 values before processing.

## Primary PAI replay

```bash
python code/run_pai_v3_gate.py pai_group_tag_table.tar.gz pai_task_table.tar.gz pai_job_table.tar.gz --out pai_v3_gate_output
```

The numerical scripts use Python, NumPy, and the Python standard library.

## Repository status

Release state: conference submission reproducibility snapshot, 11 September 2026.

Repository: https://github.com/shaikhamalkawi-ux/cac-ffls-cross-arithmetic-reliability
