#!/usr/bin/env python3
"""MIMIC-IV window-length bias external replication (parameterized; no DuckDB).

Reads user-supplied CSV extracts (credentialed MIMIC-IV access required).
Does NOT include MIMIC patient data. Aggregate summary tables that match the
manuscript are under data/summary/MIMICfull_*.csv.

Default MAP itemids (prefer-invasive at same charttime):
  220052 (Arterial Blood Pressure mean) >
  225312 (ART BP Mean) >
  220181 (Non Invasive Blood Pressure mean)

Rules aligned with manuscript / S6:
  - adult (age >= 18), first ICU stay, LOS >= 72 h
  - analytic MAP range 20–200 mmHg
  - hypotension MAP < 65; TWA cap 60 min; half-open windows
  - positivity = burden > 0

Example (after you extract icustays + chartevents MAP rows locally):

  python scripts/mimic_iv_windows.py \\
    --stays path/to/icustays_or_stays.csv \\
    --maps path/to/map_long.csv \\
    --out-dir ./out_mimic

Expected columns (override with flags):
  stays: stay_id, subject_id, intime, outtime OR los_h, age (optional)
  maps:  stay_id, charttime, itemid, valuenum
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from window_metrics_core import (  # noqa: E402
    CAP_H,
    MAP_HI,
    MAP_LO,
    WIN_ALL,
    length_curve,
    summarize_window,
)

INV = {"220052", "225312"}
NIBP = {"220181"}
ITEM_PRIORITY = {"220052": 3, "225312": 2, "220181": 1}


def load_stays(path: Path, age_min: float, los_min_h: float) -> pd.DataFrame:
    st = pd.read_csv(path)
    # normalize column names lightly
    cols = {c.lower(): c for c in st.columns}
    def col(*names):
        for n in names:
            if n in st.columns:
                return n
            if n.lower() in cols:
                return cols[n.lower()]
        raise KeyError(f"Need one of {names} in {path}")

    stay_id = col("stay_id", "icustay_id")
    subject_id = col("subject_id")
    intime = col("intime")
    st[intime] = pd.to_datetime(st[intime])
    if "outtime" in st.columns or "outtime" in cols:
        out_c = col("outtime")
        st[out_c] = pd.to_datetime(st[out_c])
        st["los_h"] = (st[out_c] - st[intime]).dt.total_seconds() / 3600.0
    elif "los_h" in st.columns:
        pass
    elif "los" in st.columns:
        # MIMIC demo los is in days
        st["los_h"] = st["los"].astype(float) * 24.0
    else:
        raise KeyError("Need outtime, los_h, or los (days)")

    age_c = None
    for cand in ("age", "anchor_age"):
        if cand in st.columns:
            age_c = cand
            break
    if age_c is not None:
        st = st[st[age_c].astype(float) >= age_min].copy()
    st = st.sort_values([subject_id, intime, stay_id]).groupby(subject_id, as_index=False).head(1)
    st = st[st["los_h"] >= los_min_h].copy()
    st = st.rename(columns={stay_id: "stay_id", subject_id: "subject_id", intime: "intime"})
    return st


def prefer_invasive_maps(
    maps: pd.DataFrame,
    stays: pd.DataFrame,
    itemids: set[str],
    map_lo: float,
    map_hi: float,
) -> dict:
    m = maps.copy()
    m["itemid"] = m["itemid"].astype(str)
    m = m[m["itemid"].isin(itemids)].copy()
    m["valuenum"] = pd.to_numeric(m["valuenum"], errors="coerce")
    m = m[m["valuenum"].between(map_lo, map_hi)].copy()
    m["charttime"] = pd.to_datetime(m["charttime"])
    m["stay_id"] = m["stay_id"].astype(str)
    stays = stays.copy()
    stays["stay_id"] = stays["stay_id"].astype(str)
    m = m.merge(stays[["stay_id", "intime", "los_h"]], on="stay_id", how="inner")
    m["pri"] = m["itemid"].map(ITEM_PRIORITY).fillna(0).astype(int)
    m = m.sort_values(["stay_id", "charttime", "pri"], ascending=[True, True, False])
    m = m.drop_duplicates(["stay_id", "charttime"], keep="first")
    m["h"] = (m["charttime"] - m["intime"]).dt.total_seconds() / 3600.0
    m = m[(m["h"] >= 0) & (m["h"] < 72)].sort_values(["stay_id", "h"])
    series = {
        k: (g["h"].to_numpy(dtype=float), g["valuenum"].to_numpy(dtype=float))
        for k, g in m.groupby("stay_id")
    }
    return series


def complete_rates(series: dict, keys: list[str]) -> tuple[pd.DataFrame, list]:
    # build per-window patient any flags
    win_patient = {}
    for k in keys:
        a, b = WIN_ALL[k]
        rows = []
        for sid, (h, v) in series.items():
            r = summarize_window({sid: (h, v)}, a, b, k)
            # need per-patient any — recompute via core window_metrics
            from window_metrics_core import window_metrics

            wm = window_metrics(h, v, a, b)
            if wm is None:
                continue
            rows.append(dict(stay_id=sid, any=wm["any"], burden=wm["burden"], hypo_h=wm["hypo_h"],
                             auc=wm["auc"], twa=wm["twa"], sd=wm["sd"], arv=wm["arv"]))
        win_patient[k] = pd.DataFrame(rows)

    ids = None
    for k in keys:
        sids = set(win_patient[k]["stay_id"])
        ids = sids if ids is None else ids & sids
    ids = sorted(ids)
    rows = []
    for k in keys:
        df = win_patient[k][win_patient[k].stay_id.isin(ids)]
        pos = int((df["any"] > 0).sum())
        n = len(df)
        rows.append(
            dict(
                set="complete_" + "-".join(keys),
                window=k,
                n=n,
                n_pos=pos,
                any_pct=round(100.0 * pos / n, 1) if n else np.nan,
                mean_burden=round(float(df.burden.mean()), 4) if n else np.nan,
                mean_hypo_h=round(float(df.hypo_h.mean()), 4) if n else np.nan,
                mean_auc=round(float(df.auc.mean()), 4) if n else np.nan,
                mean_twa=round(float(df.twa.mean()), 2) if n else np.nan,
                median_sd=round(float(df.sd.median(skipna=True)), 3) if n else np.nan,
                median_arv=round(float(df.arv.median(skipna=True)), 3) if n else np.nan,
            )
        )
    return pd.DataFrame(rows), ids


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--stays", type=Path, required=True, help="ICU stays CSV")
    p.add_argument("--maps", type=Path, required=True, help="MAP long CSV from chartevents")
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--age-min", type=float, default=18.0)
    p.add_argument("--los-min-h", type=float, default=72.0)
    p.add_argument("--map-lo", type=float, default=MAP_LO)
    p.add_argument("--map-hi", type=float, default=MAP_HI)
    p.add_argument("--cap-h", type=float, default=CAP_H)
    p.add_argument(
        "--itemids",
        default="220052,225312,220181",
        help="Comma-separated MAP itemids (prefer order handled in code)",
    )
    args = p.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    itemids = {x.strip() for x in args.itemids.split(",") if x.strip()}
    stays = load_stays(args.stays, args.age_min, args.los_min_h)
    print(f"first ICU LOS>={args.los_min_h}h: {len(stays)}")
    maps = pd.read_csv(args.maps)
    series = prefer_invasive_maps(maps, stays, itemids, args.map_lo, args.map_hi)
    print(f"with MAP in 0-72h prefer-invasive: {len(series)}")

    win_rows = []
    for label, (a, b) in WIN_ALL.items():
        s = summarize_window(series, a, b, label, cap_h=args.cap_h)
        if s:
            win_rows.append(s)
            print(label, s["any_pct"], s["n_burden_ok"])
    pd.DataFrame(win_rows).to_csv(args.out_dir / "MIMICfull_windows_recomputed.csv", index=False)

    cc_w, ids_w = complete_rates(series, ["W1_0_6", "W2_6_24", "W3_24_72"])
    cc_e, ids_e = complete_rates(series, ["E1_0_6", "E2_18_24", "E3_66_72"])
    cc = pd.concat([cc_w, cc_e], ignore_index=True)
    cc.to_csv(args.out_dir / "MIMICfull_windows_complete_recomputed.csv", index=False)
    print("complete W n", len(ids_w), "E n", len(ids_e))

    lc24 = pd.DataFrame(length_curve(series, 24, [1, 2, 3, 6, 12, 18, 24, 36, 48], cap_h=args.cap_h))
    lc0 = pd.DataFrame(length_curve(series, 0, [1, 2, 3, 6, 12, 18, 24, 36, 48, 72], cap_h=args.cap_h))
    lc24.to_csv(args.out_dir / "MIMICfull_length_curve_24h_start_recomputed.csv", index=False)
    lc0.to_csv(args.out_dir / "MIMICfull_length_curve_0h_start_recomputed.csv", index=False)

    flow = pd.DataFrame(
        [
            dict(step="first_ICU_los_ge72h", n=len(stays)),
            dict(step="with_MAP_0_72h_prefer_invasive", n=len(series)),
            dict(step="complete_W1W2W3_burden_ok", n=len(ids_w)),
            dict(step="complete_E1E2E3_burden_ok", n=len(ids_e)),
        ]
    )
    flow.to_csv(args.out_dir / "MIMICfull_cohort_flow_recomputed.csv", index=False)

    meta = dict(
        map_itemids=sorted(itemids),
        prefer_invasive="220052 > 225312 > 220181 at same charttime",
        value_filter=f"{args.map_lo}<=MAP<={args.map_hi}",
        threshold_hypo=65,
        tw_cap_h=args.cap_h,
        note="Patient-level outputs not written; aggregates only.",
    )
    (args.out_dir / "run_meta.json").write_text(json.dumps(meta, indent=2))
    print(f"Wrote aggregates under {args.out_dir}")


if __name__ == "__main__":
    main()
