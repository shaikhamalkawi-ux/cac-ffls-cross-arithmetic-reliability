# Cross-Arithmetic Reliability Gate for Fully Fuzzy Linear Systems

Reproducibility repository for the conference paper:

**A Cross-Arithmetic Reliability Gate for Fully Fuzzy Linear Systems: Photovoltaic and Production-Computing Applications**

This repository contains deterministic analysis scripts, derived reproducibility data, and provenance/verification records supporting the reported FFLS results.

## Core idea

The paper introduces the **Cross-Arithmetic Reliability Gate (CARG)** as a pre-use reliability protocol for fully fuzzy linear systems. CARG asks whether an FFLS output remains admissible and identical across a predeclared family of fuzzy-arithmetic conventions before that output is carried into engineering, calibration, planning, or decision-support use.

Its mathematical decision object is the cross-arithmetic common core. A shared core supports family-relative stability; disjoint admissible solutions indicate identity fragility; loss of admissibility indicates admissibility fragility. The framework is a reporting/use gate, not a new FFLS solver.

## Scope

The repository supports the paper's family-relative cross-arithmetic reliability analysis. It does **not** claim universal arithmetic superiority, improved photovoltaic performance, improved cluster scheduling, or prospective downstream validation.

## Reproducibility contents

- `code/` - primary Alibaba PAI replay, crossed 5x7 sensitivity analysis, spread-scale verification, and independent-benchmark verification.
- `data/` - the primary weekly balance output, full 35-case PAI sensitivity table and summary, weekday alignment results, spread-scale thresholds, full primary PAI replay results, independent-benchmark output, and the row-1 alpha=1/2 Reserve/PV-BESS-EV anchor membership checks reported in Supplement S1.
- `provenance/` - official PAI source-file hash lock, clean-run parity record, source/literature audit, and a derived PVDAQ stored-precision/source record supporting the arithmetic recheck in Supplement S3.

## Data availability boundary

The GitHub repository contains **code and derived reproducibility data supporting the reported results**. Raw third-party source datasets are not redistributed here. The Alibaba PAI archives remain available from the official Alibaba Cluster Trace source, and the PVDAQ source remains available from NREL/OEDI. The replay code checks the official Alibaba archive and member SHA-256 values before processing.

The supplementary Reserve and PV-BESS-EV file contains the exact pairwise row-1 alpha=1/2 membership checks reported in the paper; it does not assert that the full extension-principle solution sets are empty. The PV provenance file records the stored-precision quantities needed to reproduce the reported arithmetic comparison and does not claim a rerun of the full upstream PVDAQ preprocessing chain.

## Primary PAI replay

```bash
python code/run_pai_v3_gate.py pai_group_tag_table.tar.gz pai_task_table.tar.gz pai_job_table.tar.gz --out pai_v3_gate_output
```

The numerical scripts use Python, NumPy, and the Python standard library.

## Repository status

Release state: conference submission reproducibility snapshot, updated 11 September 2026.

Repository: https://github.com/shaikhamalkawi-ux/cac-ffls-cross-arithmetic-reliability
