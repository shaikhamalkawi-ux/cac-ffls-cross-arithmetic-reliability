# V5 source and literature audit

Date: 1 September 2026

## Primary arithmetic/source checks

- Malkawi, Ahmad & Ibrahim (2014), *Applied Mathematics & Information Sciences*, DOI `10.12785/amis/080309`: primary positive-FFLS source rechecked. The positive LR/triangular multiplication is an approximate declared arithmetic and leads to the associated equations `Ax=b`, `Ay+Mx=h`, `Az+Nx=g`. V5 does not describe it as exact extension-principle multiplication.
- Abbasi & Allahviranloo (2022), *Information Sciences*, DOI `10.1016/j.ins.2022.01.004`: TA-based FFLS is explicit prior art. V5 claims neither TA operations nor arithmetic-dependent FFLS solutions as new.
- Ibrahim (2020; repository issue 2021), *Fully Fuzzy Linear Systems Via Alpha-cuts*: retained as the alpha-cut associated-system source for the Energy-Hub stress test. V5 now prints the exact associated equations used there so they cannot be confused with the 2014 center-spread equations.
- Nasseri et al. (2012), *International Journal of Applied Mathematics*: source text rechecked. Eq. (2.10) has the ordering `Ax=b`, `Ay+Mx=h`, `Az+Nx=g`; later Eq. (3.3) visibly interchanges `h` and `g`. The published Example 4.2 numerical solution follows the Eq. (2.10) ordering. V5 recomputes the benchmark from Eq. (2.10) and the published inputs.

## Fuzzification / sensitivity positioning

- Guo & Zhuo (2023), DOI `10.3233/JIFS-222392`: fixed-arithmetic FFLS perturbation analysis is positioned as related sensitivity work, not the same problem as cross-arithmetic certification.
- Guerra, Sorini & Stefanini (2020), DOI `10.1016/j.ijar.2020.06.012`: empirical-quantile membership construction is cited as methodological context for data-derived fuzzy membership/envelope choices. V5 does not claim that its PAI operating-envelope construction is the same method.

## Current 2026 FFLS positioning

- Zheng (2026), *Fuzzy Sets and Systems* 531, 109772, DOI `10.1016/j.fss.2026.109772`: solves fuzzy linear systems in a Gaussian-PDMF algebraic space. This is a representation-space comparator, not a common-domain cross-arithmetic certificate.
- Kemwal & Kumar (2026), *Soft Computing*, DOI `10.1007/s00500-026-11412-w`: iterative acceleration/bounded spread evolution under a selected formulation.
- Parappathiyil (2026), FUZZ-IEEE/WCCI, DOI `10.1109/FUZZ69877.2026.11626434`: pentagonal fuzzy-number FFLS solution machinery.
- Alazzam et al. (2026), *IEEE Access*, DOI `10.1109/ACCESS.2026.3660925`: optimization-based fully fuzzy matrix-equation/FFLS work.

## Data-source checks

- Alibaba PAI v2020 official trace documentation confirms a production MLaaS trace with >6,500 GPUs, training and inference workloads, task fields including `inst_num`, `plan_cpu`, `plan_gpu`, and semantic workload tags including `bert` and `ctr`. The uploaded archives and decompressed CSV members were hash-verified against Alibaba's published checksums. The V5 raw pipeline and the crossed 5x7 sensitivity audit were rerun from those raw archives.
- NREL/OEDI PVDAQ public data record DOI `10.25984/1846021` confirms the public PV time-series source. System 2107 metadata identifies a fixed ground-mount California PV system. The originating PV source certificate records the processed 2,447-day input and SHA-256 `780e29106c768b8a5ecd1abb6fd05aa6713c818f7821254819de12bb27204a90`. CAC V5 rechecks the frozen FFLS arithmetic but does not duplicate the upstream raw-PVDAQ-to-daily preprocessing pipeline.

## Hostile novelty search

Fresh targeted searches on 1 September 2026 used combinations of:

- `cross-arithmetic fully fuzzy linear system`
- `fully fuzzy linear system solution-set intersection arithmetic`
- `arithmetic invariant fully fuzzy linear system`
- `common solution set fuzzy arithmetic FFLS`
- current 2026 FFLS solver/representation terms

The search located multiple arithmetic-specific solvers, perturbation analyses, solution semantics, iterative methods, optimization methods, and representation-space extensions. It did **not** locate a direct FFLS framework combining all of the following: (i) one frozen common fuzzy input/domain/admissibility declaration, (ii) explicit intersection of convention-specific admissible solution sets across a declared arithmetic family, and (iii) finite-anchor cross-convention certification after anchor completeness. This is an **absence-of-match finding, not proof of universal novelty**.

## Final submission reference closure - 2026-09-11

- Alibaba Cluster Trace v2020 remains supported by the official Alibaba ClusterData repository. The final bibliography entry contains only standard resource metadata; archive checksum verification remains a study method/provenance statement.
- The AAUP thesis PDF title page states **November/2020** for S. A. H. Ibrahim, *Fully Fuzzy Linear Systems Via Alpha-cuts*. The repository metadata lists issue date 2021, but the final IEEE reference uses the thesis title-page date (Nov. 2020) and omits the repository issue-date note.
- The PV source provenance was cross-checked against the originating PV FFLS report: 2,447 paired days include two 2017 observations retained in the released data for provenance but excluded from fitting/testing, plus 1,616 model-construction days (2018-2022) and 829 chronological evaluation days (2023-2025).
