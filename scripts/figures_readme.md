# Figures

`scripts/make_figs_n145.py` redraws manuscript Figures 1–3 from `data/summary/`
(complete-case n=145). Image files are written under `out_figures/` and are
not part of this deposit. The Journal submission pack holds the upload PDFs.

## Figure 2

In-plot series: observed curve, permutation mean, and the 2.5–97.5% band.
The legend names those series.

The comparison of observed W3 (47.6%) with the permutation mean (56.7%) is
caption text. The script does not draw `Obs 47.6% < perm 56.7%` on the axes.

Caption used with the v2.5 manuscript:

> Observed W1/W2/W3 positivity versus permutation mean with 2.5–97.5% bands.
> Permutation means were 24.8 → 41.2 → 56.7%; observed W3 (47.6%) sat below
> the permutation mean (m=500, seed 20261105, b=0, one-sided
> p=(b+1)/(m+1)=1/501≈0.002).

## Inputs

- `length_curve_0h_v1.csv`, `length_curve_24h_v1.csv` → Figure 1
- `perm_null_v1.csv` → Figure 2
- `local_common_WE_positivity_v1.csv`, `summary_WE_v1.csv`, `MIMICfull_windows_complete_v1.csv` → Figure 3
- `paper2_12x6h_trajectory_v1.csv` → 12×6 h plateau companion numbers
