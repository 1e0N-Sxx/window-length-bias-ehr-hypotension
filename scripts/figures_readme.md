# Figures

Manuscript Figures 1–3 (dual-panel length curves, permutation null, narrative-reversal bars)
are produced for the Journal of Clinical Epidemiology submission pack and are **not**
duplicated in this code deposit.

- Figure source PDFs/SVGs live with the separate JCE submission materials.
- Aggregate inputs that underlie the figures are in `data/summary/`:
  - `length_curve_0h_v1.csv`, `length_curve_24h_v1.csv` → Figure 1
  - `perm_null_v1.csv` → Figure 2
  - `local_common_WE_positivity_v1.csv`, `MIMICfull_windows_complete_v1.csv` → Figure 3
  - `paper2_12x6h_trajectory_v1.csv` → 12×6 h plateau companion numbers

To redraw locally, load those CSVs with any plotting library; no patient-level series
are required for the published figure numbers.
