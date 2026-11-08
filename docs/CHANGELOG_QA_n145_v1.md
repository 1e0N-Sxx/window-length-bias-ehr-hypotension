# P2 JCE v2.5 — n=145 complete-case CHANGELOG / QA

Generated: 2026-11-08 23:45:39 CST (Asia/Shanghai)
Scope: recalculate analyses affected by primary 148→145. No manuscript rewrite in this script. Chinese MD untouched.

**Public-repo status:** the English pack number pass is v2.5.1 and is not in this repository. Current shipped rates are the n=145 column below. The old column is the audit trail only.

## Locked decisions

- Primary = W1–W3 ∩ E1–E3 all computable (**n=145**).
- Three stays lacked a computable E3 burden and are outside the complete-case set; all three survived. Hospitalization IDs are not listed in this public deposit.
- Deaths remain **11/145 (7.6%)**.
- Study period unify: April 27, 2025, to October 20, 2026.
- Other sets keep own denominators (early 252, full 257, MIMIC own N).

## QC vs expected common-case positivity

| | W1 | W2 | W3 | E1 | E2 | E3 |
|---|---:|---:|---:|---:|---:|---:|
| Expected | 27.6 | 34.5 | 47.6 | 27.6 | 17.2 | 17.2 |
| Recomputed | 27.6 | 34.5 | 47.6 | 27.6 | 17.2 | 17.2 |

**PASS** — exact match.

## Core metrics old(n=148) → new(n=145)

| metric | old n148 | new n145 | note |
|---|---|---|---|
| primary_n | 148 | 145 | complete-case W∪E; drop 3 E3-missing (all alive) |
| W1_pos_pct | 27.0 | 27.6 | among primary (=145) |
| W2_pos_pct | 33.8 | 34.5 |  |
| W3_pos_pct | 46.6 | 47.6 |  |
| W_cochran_p | 0.0001339815814698729 | 0.0001339815814698729 | complete n=145 |
| W_friedman_burden_p | 0.6699038274547535 | 0.6699038274547763 |  |
| E1_pos_pct | 27.0 | 27.6 | E3 was already among-145 in v2.4 |
| E2_pos_pct | 16.9 | 17.2 |  |
| E3_pos_pct | 17.2 | 17.2 | unchanged vs prior E3-evaluable |
| E_cochran_p | 0.015503853599009307 | 0.015503853599009307 | identical complete-case E triad |
| E_friedman_burden_p | 0.02867515708310316 | 0.02867515708310316 |  |
| S_pos_pct | 27.0/18.2/14.9 | 27.6/18.6/15.2 | complete n=145 |
| M_pos_pct | 27.6/19.3/14.5 | 27.8/19.4/14.6 | complete n=144 |
| early+_death | 5/40 (12.5%) | 5/40 (12.5%) | early+ unchanged |
| early−_death | 6/108 (5.6%) | 6/105 (5.7%) | denom 108→105 (3 alive early− dropped) |
| total_death | 11/148 (7.4%) | 11/145 (7.6%) | 11 deaths confirmed |
| early_fisher_p | 0.1682 | 0.1763 | two-sided |
| L1_any_pct_from24 | 4.138 | 4.225 | recomputed on n=145 |
| L48_any_pct_from24 | 46.622 | 47.586 |  |
| perm_means_W | 23.9/40.3/55.8 | 24.8/41.2/56.7 | seed=20261105 m=500 |
| table1_age_median_IQR | 70 (51.75–80) | 70 (52–80) |  |
| table1_male_pct | 66.2 | 66.2 |  |

## Tests (n=145)

- W Cochran Q=17.8356, p=0.0001; Friedman burden p=0.6699
- E Cochran Q=8.3333, p=0.0155; Friedman burden p=0.0287
- S complete n=145: 27.6/18.6/15.2; Cochran p=0.0090
- M complete n=144: 27.8/19.4/14.6; Cochran p=0.0084

## Early ± death

| Arm | n | Deaths | % |
|---|---:|---:|---:|
| early+ | 40 | 5 | 12.5 |
| early− | 105 | 6 | 5.7 |
| total | 145 | 11 | 7.6 |

- Fisher OR=2.3571, p=0.1763

## Length curves (24 h start) headline

| L_h | n | any% | mean TWA | mean hypo_h | median SD | median ARV |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 142 | 4.225 | 0.036 | 0.022 | 1.732 | 1.6 |
| 2 | 144 | 7.639 | 0.04 | 0.059 | 4.243 | 6.0 |
| 3 | 145 | 9.655 | 0.035 | 0.082 | 4.983 | 6.0 |
| 6 | 145 | 15.172 | 0.035 | 0.19 | 6.432 | 6.2 |
| 12 | 145 | 24.138 | 0.042 | 0.484 | 8.152 | 6.444 |
| 18 | 145 | 30.345 | 0.043 | 0.754 | 8.455 | 6.765 |
| 24 | 145 | 35.862 | 0.043 | 1.003 | 9.183 | 7.167 |
| 36 | 145 | 45.517 | 0.043 | 1.529 | 9.735 | 7.114 |
| 48 | 145 | 47.586 | 0.044 | 2.095 | 9.632 | 7.286 |

## Permutation null (W/E)

| window | n | obs% | perm mean [2.5–97.5] | p_obs≤perm (Laplace) |
|---|---:|---:|---|---:|
| W1_0_6 | 145 | 27.6 | 24.8 [19.3–30.3] | 0.8663 |
| W2_6_24 | 145 | 34.5 | 41.2 [35.9–46.2] | 0.0100 |
| W3_24_72 | 145 | 47.6 | 56.7 [53.1–59.7] | 0.0020 |
| E1_0_6 | 145 | 27.6 | 24.8 [19.3–30.3] | 0.8663 |
| E2_18_24 | 145 | 17.2 | 22.4 [17.2–27.6] | 0.0399 |
| E3_66_72 | 145 | 17.2 | 21.9 [17.2–26.9] | 0.0499 |

## 12×6 h trajectory (among evaluable)

| segment | n_eval | n_miss | n_pos | % eval | % /145 |
|---|---:|---:|---:|---:|---:|
| 0-6 | 145 | 0 | 40 | 27.6 | 27.6 |
| 6-12 | 145 | 0 | 27 | 18.6 | 18.6 |
| 12-18 | 144 | 1 | 28 | 19.4 | 19.3 |
| 18-24 | 145 | 0 | 25 | 17.2 | 17.2 |
| 24-30 | 145 | 0 | 22 | 15.2 | 15.2 |
| 30-36 | 144 | 1 | 26 | 18.1 | 17.9 |
| 36-42 | 144 | 1 | 25 | 17.4 | 17.2 |
| 42-48 | 145 | 0 | 22 | 15.2 | 15.2 |
| 48-54 | 145 | 0 | 24 | 16.6 | 16.6 |
| 54-60 | 144 | 1 | 20 | 13.9 | 13.8 |
| 60-66 | 144 | 1 | 19 | 13.2 | 13.1 |
| 66-72 | 145 | 0 | 25 | 17.2 | 17.2 |

## Material-change flags

- No material direction/significance change vs n=148 narrative.

## Unfinished / next-pass TODOs

- Regenerate pack figures that embed n=148 numbers: Fig1 length curves, Fig2 perm null, Fig3 unequal vs equal (local panel).
- Update English pack files listed in `ENGLISH_FILES_INVENTORY_v2.5.md` (numbers + complete-case framing + study period + mortality wording + trim nested-window repetition + one early-warning outlook).
- Flowchart: analysis-set box 148→145; keep early 252 / full 257.
- Cover letter / STROBE / RECORD: n=148→145 where analysis set is cited.
- MIMIC: keep own N (not forced to complete-case this pass).
- Continuous burden vs LOS / CRRT / ventilation full tables: only death MW/Spearman for W1/W3 recomputed here (`exploratory_burden_death_v1.csv`); fuller v3-style table optional next pass.
- Phenotype×death table: not re-run this pass (interpretation freeze); numbers if cited on primary set need check.

## Outputs

- `/workspace/eicu-onboarding/derived/n145_v1/`
- `paper2-window-metrics-n145-v1.md`
- Script: `scripts/n145_window_metrics_v1/run.py`

## Figures (this pass)

Regenerated from n145 CSVs into `derived/n145_v1/figures/`:

- Fig1_length_curves.{png,pdf,svg,tiff}
- Fig2_perm_null.{png,pdf,svg,tiff}
- Fig3_narrative_reversal_mimic.{png,pdf,svg,tiff} (local panel n=145; MIMIC panel unchanged)

Script: `scripts/n145_window_metrics_v1/make_figs_n145.py`  
Pack `paper2-jce-submission-pack-v2.4/figures/` not overwritten (next pass copies into v2.5 pack).

## English inventory

See `derived/n145_v1/ENGLISH_FILES_INVENTORY_v2.5.md`.

## Readiness for VET manuscript edit

READY for number/text pass on English files. Core metrics QC PASS vs expected 27.6/34.5/47.6 & 27.6/17.2/17.2. No material direction/significance change. Death 11/145 confirmed. Chinese MD untouched. No journal submit.
