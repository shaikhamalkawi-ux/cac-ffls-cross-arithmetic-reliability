# PV derived source and stored-precision record

This record supports the PVDAQ-derived FFLS arithmetic checks reported in the paper and Supplement S3. It does **not** redistribute the raw PVDAQ dataset and does not recreate the upstream raw-to-2,447-day processing chain.

## Public source

- Source: NREL/OEDI Photovoltaic Data Acquisition (PVDAQ) public datasets.
- Dataset DOI: `10.25984/1846021`.
- Application record used in the paper: PVDAQ system 2107, described as an 893-kW fixed ground-mount photovoltaic facility in California.

## Prespecified day census reported in the paper

- Processed paired days in the retained source record: 2,447.
- 2017 provenance observations retained but excluded from fitting/evaluation: 2.
- Model-construction days (2018-2022): 1,616.
- Chronological evaluation days (2023-2025): 829.
- Check: `2 + 1616 + 829 = 2447`.

## Stored-precision FFLS quantities used for the arithmetic recheck

Center solution:

`x = (0.942882448, 0.974760760)^T`

Center-spread vectors:

`y_M = (0.002399454446, 0.000115589172)^T`

`z_M = (0.002667352702, 0)^T`

Right-hand-side spread vectors:

`h = (0.003015371068, 0.002625966344)^T`

`g = (0.003122817983, 0.002642280566)^T`

Reconstructed center matrix:

`A = [[0.582918133264814, 0.417081866735186], [0.341356522125083, 0.658643477874917]]`

Direct-TA spread vectors obtained from the shift relation:

`y_TA = (0.013462613923642, 0.006342656662640)^T`

`z_TA = (0.014524903846198, 0.005889664756132)^T`

These quantities reproduce the supports reported in Table III and show two distinct admissible singleton fuzzy solutions, so the tested pairwise common core is empty.

## Boundary

This is a derived verification/provenance record. It supports arithmetic reproduction from the stored precision quantities; it is not a replacement for the official PVDAQ dataset and is not evidence that the full upstream preprocessing chain was rerun in this conference analysis.
