# Window-length bias in EHR-derived MAP hypotension metrics

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24014471.svg)](https://doi.org/10.5281/zenodo.24014471)

Analysis code companion for a methods manuscript on **window-length bias** in
time-window summaries of mean arterial pressure (MAP) hypotension
(Journal of Clinical Epidemiology submission materials are separate).

**Public repository:** https://github.com/1e0N-Sxx/window-length-bias-ehr-hypotension

**Zenodo archive:** https://doi.org/10.5281/zenodo.24014471

That version DOI is still Zenodo **v0.1.0** (published 2026-11-06; primary **n=148** snapshot). It does not match the tables in this tree. A new Zenodo version is needed after the git tag. The concept DOI `10.5281/zenodo.24014470` stays and will track the latest version. Details: `docs/zenodo_v0.1.0_n145_gap.md`.

**Primary analysis set (v2.5 / n145):** complete-case **n=145** (W1–W3 and E1–E3 all computable).
Unequal any-MAP<65 positivity **27.6 / 34.5 / 47.6%**; equal-end **27.6 / 17.2 / 17.2%**.
Permutation means (W) **24.8 → 41.2 → 56.7%** (m=500, seed 20261105). Observed W3 47.6% below the null.

## What is included

- Parameterized Python scripts for:
  - local-style window positivity, length curves, and within-patient permutation nulls
  - MIMIC-IV prefer-invasive MAP window replication (CSV inputs; no DuckDB)
  - APACHE/SOFA OLS on a ready analysis frame (Table S3 style)
- **Aggregate / summary CSVs only** under `data/summary/` that reproduce manuscript
  table numbers (positivity %, length curves, permutation null, MIMIC full summaries,
  cohort flow counts).
- Extraction protocol note: `docs/MIMIC_IV_3.1_extraction.md`
- n=145 QA note: `docs/CHANGELOG_QA_n145_v1.md` (old-versus-new audit; current rates are the n=145 column)
- `scripts/make_figs_n145.py` redraws Figures 1–3 from these CSVs. Figure 2 keeps the observed-versus-permutation comparison in the caption only.

## What is NOT included

- **No local EICU / hospital identifiable patient data**
- No hospitalization IDs, raw MAP time series, DuckDB files, or patient-level pickles
- No manuscript DOCX / submission pack (those stay with the journal materials)

## MIMIC-IV access

Full MIMIC-IV recompute requires **PhysioNet credentialed access**:

- Johnson AEW, et al. MIMIC-IV (v3.1). PhysioNet. doi:[10.13026/kpb9-mt58](https://doi.org/10.13026/kpb9-mt58)

The open PhysioNet **demo** can be used to smoke-test `scripts/mimic_iv_windows.py`,
but the manuscript’s external evidence is the **full** v3.1 extract summarized in
`data/summary/MIMICfull_*.csv`.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Inspect shipped aggregates (no PHI)
python -c "import pandas as pd; print(pd.read_csv('data/summary/local_common_WE_positivity_v1.csv'))"
```

### Recompute on your own extracts

```bash
# Local long MAP table (you supply; columns configurable)
python scripts/eicu_window_metrics.py \
  --map-csv /path/to/your_map_long.csv \
  --cohort-csv /path/to/your_cohort_ids.csv \
  --id-col hosp_id --hour-col h --map-col map \
  --out-dir ./out_local

# MIMIC-IV (credentialed CSVs you extract)
python scripts/mimic_iv_windows.py \
  --stays /path/to/stays.csv \
  --maps /path/to/map_long.csv \
  --out-dir ./out_mimic

# Severity OLS on a de-identified analysis frame you build
python scripts/severity_ols.py \
  --input /path/to/analysis_frame.csv \
  --out-dir ./out_ols
```

Shared metric definitions live in `scripts/window_metrics_core.py`
(half-open windows, MAP&lt;65, 60 min TWA cap, positivity = burden &gt; 0;
MIMIC prefer-invasive itemids 220052 &gt; 225312 &gt; 220181).

## Summary tables ↔ manuscript (n=145 complete-case)

| File | Role |
|---|---|
| `summary_WE_v1.csv` | Local unequal / equal-end window summaries (**n=145**) |
| `local_common_WE_positivity_v1.csv` | Locked positivity (**27.6/34.5/47.6** vs **27.6/17.2/17.2**) |
| `length_curve_0h_v1.csv`, `length_curve_24h_v1.csv` | Figure 1 inputs |
| `perm_null_v1.csv` | Figure 2 permutation null (m=500, seed 20261105; means 24.8/41.2/56.7) |
| `paper2_12x6h_trajectory_v1.csv` | 12×6 h trajectory (same rows as `trajectory_12x6h_v1.csv`) |
| `early_death_v1.csv` | In-hospital death 11/145 (7.6%); early+ 5/40 vs early− 6/105 |
| `table1_summary_v1.json` | Table 1 aggregates (age, sex, diagnosis category, occupancy) |
| `length_curve_perm_v1.csv` | Permuted any-positivity by length (24 h start) |
| `MIMICfull_*.csv` | External full MIMIC aggregates (own N; unchanged) |
| `MIMICdemo_windows_v1.csv` | Demo smoke-check only (not main external evidence) |
| `key_numbers_v1.json` | Frozen n145 key-number card (no hospitalization IDs) |

## License

MIT — see `LICENSE`.

## Citation

Please cite the published article (or preprint) when available, and MIMIC-IV as above. The badge is version DOI 10.5281/zenodo.24014471 (v0.1.0 only). Cite the new version DOI after that version is published.
This code deposit is offered to support methods review and reproducibility of
**aggregate** results; it is not a substitute for credentialed database access.
