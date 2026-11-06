# MIMIC-IV 3.1 extraction (external replication)

**Purpose.** Reproduce the manuscript’s MIMIC-IV full external check of the
window-length artefact (unequal-window any-positivity climb vs equal-end plateau;
fixed-start length curves). This document describes the **protocol**. Identifiable
MIMIC rows are **not** included in this repository.

**Citation.** Johnson AEW, et al. MIMIC-IV (version 3.1). PhysioNet.
https://doi.org/10.13026/kpb9-mt58 — credentialed access required.

## Analysis rules (frozen with manuscript S6)

| Item | Value |
|---|---|
| MAP itemids | **220052**, **225312**, **220181** |
| Prefer-invasive | same charttime: 220052 > 225312 > 220181 |
| Analytic MAP range | 20 ≤ MAP ≤ 200 mmHg |
| Hypotension | MAP < 65 mmHg |
| TWA burden | finite-persistence cap = **60 min** |
| Windows | half-open `[a, b)` |
| Positivity | burden > 0 among burden-computable stays |
| Cohort | adult age ≥ 18; **first** ICU stay; LOS ≥ 72 h |

## Suggested extract layout (user-local)

Place credentialed files under a path you choose, for example:

```text
<path-to-mimic-iv-3.1>/
  icu/icustays.csv.gz
  icu/chartevents.csv.gz   # or a pre-filtered MAP-only extract
```

Or prepare two analysis CSVs and call `scripts/mimic_iv_windows.py`:

1. **stays CSV** — columns: `stay_id`, `subject_id`, `intime`, `outtime` (or `los_h` / `los` in days), optional `age`
2. **maps CSV** — columns: `stay_id`, `charttime`, `itemid`, `valuenum` (itemids restricted to the three MAP codes above)

Do **not** commit those CSVs to a public repository.

## Cohort flow (manuscript frozen counts)

| Step | n |
|---|---:|
| Stays table rows | 94,458 |
| Adult age ≥ 18 | 94,458 |
| Adult first ICU stay | 65,366 |
| First ICU LOS ≥ 72 h | 20,696 |
| Prefer-invasive MAP in 0–72 h | 20,649 |
| Complete W1–W3 burden | 20,168 |
| Complete E1–E3 burden | 19,952 |

Source table in this deposit: `data/summary/MIMICfull_cohort_flow_v1.csv`.

## Main frozen direction (complete-case)

- Unequal W any%: **43.7 / 60.8 / 70.5** (n=20,168)
- Equal-end E any%: **43.8 / 39.2 / 31.2** (n=19,952)
- Fixed 24 h-start length scan L=1→48: any% **16.9 → 70.8**; mean TWA burden **0.154 → 0.132**

Aggregate CSVs: `data/summary/MIMICfull_windows_*.csv`, `MIMICfull_length_curve_*.csv`.

## How to recompute

```bash
python scripts/mimic_iv_windows.py \
  --stays /path/to/stays.csv \
  --maps /path/to/map_long.csv \
  --out-dir ./out_mimic
```

Full recompute needs your own PhysioNet-credentialed extract. The shipped summary
CSVs already reproduce the manuscript aggregate numbers without patient rows.

## Notes on earlier internal pipelines

Internal work used a materialized DuckDB layer for speed. The public deposit
intentionally ships a **CSV-only** script so no database file, Mac absolute path,
or patient-level cache is required or distributed.
