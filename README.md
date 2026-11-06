# Window-length bias in EHR-derived MAP hypotension metrics

Analysis code companion for a methods manuscript on **window-length bias** in
time-window summaries of mean arterial pressure (MAP) hypotension
(Journal of Clinical Epidemiology submission materials are separate).

**Public repository:** https://github.com/1e0N-Sxx/window-length-bias-ehr-hypotension

## What is included

- Parameterized Python scripts for:
  - local-style window positivity, length curves, and within-patient permutation nulls
  - MIMIC-IV prefer-invasive MAP window replication (CSV inputs; no DuckDB)
  - APACHE/SOFA OLS on a ready analysis frame (Table S3 style)
- **Aggregate / summary CSVs only** under `data/summary/` that reproduce manuscript
  table numbers (positivity %, length curves, permutation null, MIMIC full summaries,
  cohort flow counts).
- Extraction protocol note: `docs/MIMIC_IV_3.1_extraction.md`

## What is NOT included

- **No local EICU / hospital identifiable patient data**
- No hospitalization IDs, raw MAP time series, DuckDB files, or patient-level pickles
- No manuscript DOCX / submission pack (those stay with the journal materials)
- No Zenodo DOI yet (archive after the public GitHub tag; placeholder in paper Declarations)

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

## Summary tables ↔ manuscript

| File | Role |
|---|---|
| `summary_WE_v1.csv` | Local unequal / equal-end window summaries (n=148) |
| `local_common_WE_positivity_v1.csv` | Locked positivity denominators (27.0/33.8/46.6 vs 27.0/16.9/17.2) |
| `length_curve_0h_v1.csv`, `length_curve_24h_v1.csv` | Figure 1 inputs |
| `perm_null_v1.csv` | Figure 2 permutation null (m=500, seed 20261105) |
| `paper2_12x6h_trajectory_v1.csv` | 12×6 h trajectory |
| `MIMICfull_*.csv` | External full MIMIC aggregates (Table 4 / S6) |
| `MIMICdemo_windows_v1.csv` | Demo smoke-check only (not main external evidence) |

## License

MIT — see `LICENSE`.

## Citation

Please cite the published article (or preprint) when available, and MIMIC-IV as above.
This code deposit is offered to support methods review and reproducibility of
**aggregate** results; it is not a substitute for credentialed database access.
