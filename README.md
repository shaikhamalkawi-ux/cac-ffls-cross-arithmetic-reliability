# Cross-Arithmetic Reliability of Fully Fuzzy Linear Systems

Reproducibility repository for the conference paper:

**Cross-Arithmetic Reliability of Fully Fuzzy Linear Systems in Photovoltaic and Production Computing Applications**

This repository contains the deterministic analysis scripts, locked derived outputs, provenance records, and manuscript source used to support the reported cross-arithmetic FFLS results.

## Scope

The repository supports the paper's family-relative cross-arithmetic reliability analysis. It does **not** claim universal arithmetic superiority, improved photovoltaic performance, improved cluster scheduling, or prospective downstream validation.

## Reproducibility contents

- `code/` - deterministic PAI replay, sensitivity analysis, spread-scale verification, and independent-benchmark verification.
- `data/` - locked derived outputs reported or summarized in the paper and supplementary material.
- `provenance/` - source-lock and clean-run parity records.
- `source/` - LaTeX manuscript source and bibliography.

The raw Alibaba PAI archives are not redistributed here. The replay script verifies the official archive and member SHA-256 values before processing. See `provenance/PAI_SOURCE_LOCK.json`.

## Primary PAI replay

```bash
python code/run_pai_v3_gate.py pai_group_tag_table.tar.gz pai_task_table.tar.gz pai_job_table.tar.gz --out pai_v3_gate_output
```

Python dependencies used by the numerical scripts include `numpy` and the Python standard library.

## Repository status

Release state: conference submission reproducibility snapshot, 11 September 2026.

Repository: https://github.com/shaikhamalkawi-ux/cac-ffls-cross-arithmetic-reliability
