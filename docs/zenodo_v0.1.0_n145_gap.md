# Zenodo v0.1.0 is not the n=145 deposit

Checked 2026-11-08. This environment cannot publish or edit Zenodo.

| Field | Value |
|---|---|
| Version DOI | [10.5281/zenodo.24014471](https://doi.org/10.5281/zenodo.24014471) |
| Concept DOI | [10.5281/zenodo.24014470](https://doi.org/10.5281/zenodo.24014470) |
| Version on that record | **v0.1.0**, published 2026-11-06 |
| Zip | `1e0N-Sxx/window-length-bias-ehr-hypotension-v0.1.0.zip` |
| md5 | `11cae10c0da728a4e4a1c71f36299e29` (25,711 bytes) |
| Git tree inside the zip | commit `59fc66f`, tag `v0.1.0` |
| Description | “Public analysis scripts and aggregate summary tables (no patient-level data).” It does not state n=145. |

That snapshot is the pre-complete-case deposit (primary **n=148**). This repository’s tables are complete-case **n=145** (unequal any-positivity 27.6 / 34.5 / 47.6; equal-end 27.6 / 17.2 / 17.2; death 11/145; permutation means 24.8 / 41.2 / 56.7). **Do not treat 10.5281/zenodo.24014471 as already matching this tree.**

MIMIC summary files in the v0.1.0 zip match `data/summary/MIMIC*.csv` here. Leave those unchanged in the next archive.

## After the git tag

1. Sign in as an owner of record 24014471.
2. Open the record and choose **New version**. Leave v0.1.0 in place. Version DOIs are not overwritten.
3. Upload an archive of the tagged n=145 tree. Keep patient-level rows out of the zip.
4. State in the description that the primary set is complete-case n=145 and that v0.1.0 remains the earlier snapshot.
5. Publish and copy the **new version DOI**.
6. The concept DOI `10.5281/zenodo.24014470` stays and will resolve to that latest version. `10.5281/zenodo.24014471` will keep resolving to v0.1.0. Point the README badge and the manuscript Data availability line at the new version DOI after it exists.
