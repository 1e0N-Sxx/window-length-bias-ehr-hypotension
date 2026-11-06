#!/usr/bin/env python3
"""APACHE / norepinephrine-adjusted SOFA OLS (Table S3 style).

Expects a *ready analysis frame* (one row per patient) with columns — not raw EHR:
  early_positive  (0/1; 0–6 h MAP<65 any-positivity / burden>0)
  apache24        (APACHE II within ~24 h of index)
  sofa_24_72      (max SOFA in [24, 72) h)
  ne6             (optional; 1 if norepinephrine started within 6 h)

This script does not extract scores from hospital systems. Prepare the frame
from your own credentialed data; identifiable extracts are not shipped here.

Example:
  python scripts/severity_ols.py --input analysis_frame.csv --out-dir ./out_ols
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf


def fit_models(df: pd.DataFrame) -> list[dict]:
    rows = []
    d = df.dropna(subset=["sofa_24_72", "apache24", "early_positive"]).copy()
    d["early_positive"] = d["early_positive"].astype(int)
    r1 = smf.ols("sofa_24_72 ~ early_positive + apache24", d).fit()
    rows.append(
        dict(
            model="sofa_24_72 ~ early_positive + apache24",
            n=int(r1.nobs),
            term="early_positive",
            coef=float(r1.params["early_positive"]),
            ci_low=float(r1.conf_int().loc["early_positive", 0]),
            ci_high=float(r1.conf_int().loc["early_positive", 1]),
            p=float(r1.pvalues["early_positive"]),
            r2=float(r1.rsquared),
        )
    )
    if "ne6" in d.columns:
        d2 = d.dropna(subset=["ne6"]).copy()
        d2["ne6"] = d2["ne6"].astype(int)
        r2 = smf.ols("sofa_24_72 ~ early_positive + apache24 + ne6", d2).fit()
        for term in ("early_positive", "apache24", "ne6"):
            rows.append(
                dict(
                    model="sofa_24_72 ~ early_positive + apache24 + ne6",
                    n=int(r2.nobs),
                    term=term,
                    coef=float(r2.params[term]),
                    ci_low=float(r2.conf_int().loc[term, 0]),
                    ci_high=float(r2.conf_int().loc[term, 1]),
                    p=float(r2.pvalues[term]),
                    r2=float(r2.rsquared),
                )
            )
    return rows


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, required=True, help="Analysis-frame CSV")
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--early-col", default="early_positive")
    p.add_argument("--apache-col", default="apache24")
    p.add_argument("--sofa-col", default="sofa_24_72")
    p.add_argument("--ne-col", default="ne6")
    args = p.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.input)
    rename = {
        args.early_col: "early_positive",
        args.apache_col: "apache24",
        args.sofa_col: "sofa_24_72",
    }
    if args.ne_col in df.columns:
        rename[args.ne_col] = "ne6"
    df = df.rename(columns=rename)

    rows = fit_models(df)
    out = pd.DataFrame(rows)
    out.to_csv(args.out_dir / "ols_severity_summary.csv", index=False)
    print(out.to_string(index=False))
    print(
        "Note: manuscript Table S3 used n=120 complete cases "
        "(early-positive 30 / early-negative 90). Your n depends on your frame."
    )


if __name__ == "__main__":
    main()
