#!/usr/bin/env python3
"""Local EICU-style window-length artefact analysis (parameterized).

Expects a long MAP table and a cohort index table you prepare from your
own credentialed extract. This repository does NOT ship identifiable
local EICU data.

Input long MAP CSV columns (configurable via flags):
  id_col, hour_col, map_col
  — hours are relative to index (ICU/admit time), already filtered preferably to [0, 72).

Input cohort CSV: one row per patient with id_col (and optional index timestamp).

Outputs (written under --out-dir):
  summary_WE_v1.csv-style window positivity tables
  length_curve_0h_v1.csv / length_curve_24h_v1.csv
  perm_null_v1.csv (within-patient value permutation null)

Manuscript numbers for the primary n=148 analysis are also shipped as
aggregate CSVs under data/summary/ (no patient rows).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from window_metrics_core import (  # noqa: E402
    CAP_H,
    WIN_ALL,
    WIN_EQUAL_END,
    WIN_UNEQUAL,
    length_curve,
    permute_values,
    rates_any_pct,
    summarize_window,
    window_metrics,
)


def load_series(
    map_csv: Path,
    cohort_csv: Path | None,
    id_col: str,
    hour_col: str,
    map_col: str,
) -> dict:
    m = pd.read_csv(map_csv, dtype={id_col: str})
    if cohort_csv is not None:
        coh = pd.read_csv(cohort_csv, dtype={id_col: str})
        ids = set(coh[id_col].astype(str))
        m = m[m[id_col].astype(str).isin(ids)].copy()
    m = m.sort_values([id_col, hour_col])
    series = {
        k: (g[hour_col].to_numpy(dtype=float), g[map_col].to_numpy(dtype=float))
        for k, g in m.groupby(id_col)
    }
    return series


def build_window_table(series: dict, windows: dict, design: str) -> pd.DataFrame:
    rows = []
    for label, (a, b) in windows.items():
        s = summarize_window(series, a, b, label)
        if not s:
            continue
        rows.append(
            dict(
                design=design,
                window=label,
                n_evaluable=s["n_burden_ok"],
                n_pos=s["n_pos"],
                pos_pct_among_evaluable=s["any_pct"],
                mean_burden_evaluable=s["mean_burden"],
                mean_hypo_h=s["mean_hypo_h"],
                mean_auc=s["mean_auc"],
                mean_twa=s["mean_twa"],
                median_sd=s["median_sd"],
                median_arv=s["median_arv"],
            )
        )
    return pd.DataFrame(rows)


def permutation_null(
    series: dict,
    windows: dict,
    n_perm: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    obs = rates_any_pct(series, windows)
    perm_rows = []
    for _ in range(n_perm):
        Q = permute_values(series, rng)
        perm_rows.append(rates_any_pct(Q, windows))
    perm = pd.DataFrame(perm_rows)
    rows = []
    for w in windows:
        o = obs[w]
        col = perm[w]
        # Laplace-smoothed one-sided p = (b+1)/(m+1)
        b_ge = int((col >= o).sum())
        b_le = int((col <= o).sum())
        m = n_perm
        rows.append(
            dict(
                window=w,
                n_with_points=sum(
                    1
                    for h, v in series.values()
                    if window_metrics(h, v, *windows[w]) is not None
                ),
                observed_pos_pct=round(o, 1),
                perm_mean=round(float(col.mean()), 1),
                perm_2_5=round(float(col.quantile(0.025)), 1),
                perm_97_5=round(float(col.quantile(0.975)), 1),
                p_obs_ge_perm_laplace=(b_ge + 1) / (m + 1),
                p_obs_le_perm_laplace=(b_le + 1) / (m + 1),
                p_obs_ge_perm_raw=b_ge / m,
                p_obs_le_perm_raw=b_le / m,
            )
        )
    return pd.DataFrame(rows)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--map-csv", type=Path, required=True, help="Long MAP CSV (id, hour, map)")
    p.add_argument("--cohort-csv", type=Path, default=None, help="Optional patient id list")
    p.add_argument("--id-col", default="hosp_id")
    p.add_argument("--hour-col", default="h")
    p.add_argument("--map-col", default="map")
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--n-perm", type=int, default=500)
    p.add_argument("--seed", type=int, default=20261105)
    p.add_argument("--cap-h", type=float, default=CAP_H)
    args = p.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    series = load_series(
        args.map_csv, args.cohort_csv, args.id_col, args.hour_col, args.map_col
    )
    print(f"n patients with MAP series: {len(series)}")

    we = pd.concat(
        [
            build_window_table(series, WIN_UNEQUAL, "original_unequal"),
            build_window_table(series, WIN_EQUAL_END, "equal6h_end_of_parent"),
        ],
        ignore_index=True,
    )
    we.to_csv(args.out_dir / "summary_WE_recomputed.csv", index=False)
    print(we[["design", "window", "n_evaluable", "pos_pct_among_evaluable"]].to_string(index=False))

    lc0 = pd.DataFrame(
        length_curve(series, 0.0, [1, 2, 3, 6, 12, 18, 24, 36, 48, 72], cap_h=args.cap_h)
    )
    lc24 = pd.DataFrame(
        length_curve(series, 24.0, [1, 2, 3, 6, 12, 18, 24, 36, 48], cap_h=args.cap_h)
    )
    lc0.to_csv(args.out_dir / "length_curve_0h_recomputed.csv", index=False)
    lc24.to_csv(args.out_dir / "length_curve_24h_recomputed.csv", index=False)

    null = permutation_null(series, WIN_ALL, args.n_perm, args.seed)
    null.to_csv(args.out_dir / "perm_null_recomputed.csv", index=False)
    print(null[["window", "observed_pos_pct", "perm_mean", "p_obs_le_perm_laplace"]].to_string(index=False))
    print(f"Wrote outputs under {args.out_dir}")


if __name__ == "__main__":
    main()
