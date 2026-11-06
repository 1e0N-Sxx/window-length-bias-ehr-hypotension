"""Shared time-weighted MAP hypotension window metrics.

Half-open windows [a, b); MAP < 65; finite-persistence cap (default 60 min).
Positive = TWA burden > 0 among burden-computable windows.
No patient identifiers required — callers pass hour arrays and MAP values.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping, Optional, Sequence, Tuple

import numpy as np

CAP_H = 1.0  # 60 minutes
MAP_LO, MAP_HI = 20.0, 200.0
HYPO_THRESHOLD = 65.0

# Unequal-length design (W) and equal-end 6 h design (E)
WIN_UNEQUAL = {
    "W1_0_6": (0.0, 6.0),
    "W2_6_24": (6.0, 24.0),
    "W3_24_72": (24.0, 72.0),
}
WIN_EQUAL_END = {
    "E1_0_6": (0.0, 6.0),
    "E2_18_24": (18.0, 24.0),
    "E3_66_72": (66.0, 72.0),
}
WIN_ALL = {**WIN_UNEQUAL, **WIN_EQUAL_END}


def window_metrics(
    hours: np.ndarray,
    values: np.ndarray,
    a: float,
    b: float,
    cap_h: float = CAP_H,
    hypo: float = HYPO_THRESHOLD,
) -> Optional[Dict[str, Any]]:
    """Compute metrics on half-open [a, b).

    Returns None if no MAP points fall in the window (not burden-computable).
    """
    hours = np.asarray(hours, dtype=float)
    values = np.asarray(values, dtype=float)
    mask = (hours >= a) & (hours < b)
    hh, vv = hours[mask], values[mask]
    if len(hh) == 0:
        return None
    nxt = np.append(hh[1:], b)
    delta = np.clip(np.minimum(np.minimum(nxt, hh + cap_h), b) - hh, 0, None)
    supported = float(delta.sum())
    if supported <= 0:
        return None
    low = vv < hypo
    hypo_h = float((delta * low).sum())
    burden = hypo_h / supported
    out: Dict[str, Any] = {
        "any": float(bool(low.any())),
        "burden": burden,
        "hypo_h": hypo_h,
        "auc": float((delta * np.clip(hypo - vv, 0, None)).sum()),
        "twa": float((delta * vv).sum() / supported),
        "arv": float(np.abs(np.diff(vv)).mean()) if len(vv) > 1 else np.nan,
        "sd": float(vv.std(ddof=1)) if len(vv) > 1 else np.nan,
        "cov": supported / (b - a),
        "npts": int(len(vv)),
    }
    return out


def rates_any_pct(
    series: Mapping[Any, Tuple[np.ndarray, np.ndarray]],
    windows: Mapping[str, Tuple[float, float]] = WIN_ALL,
    cap_h: float = CAP_H,
) -> Dict[str, float]:
    """Percent any-positivity per window among patients with ≥1 point in window."""
    out: Dict[str, float] = {}
    for name, (a, b) in windows.items():
        rows = [window_metrics(h, v, a, b, cap_h=cap_h) for h, v in series.values()]
        rows = [r for r in rows if r is not None]
        out[name] = float(np.mean([r["any"] for r in rows]) * 100.0) if rows else np.nan
    return out


def summarize_window(
    series: Mapping[Any, Tuple[np.ndarray, np.ndarray]],
    a: float,
    b: float,
    label: str,
    cap_h: float = CAP_H,
) -> Optional[Dict[str, Any]]:
    rows = []
    for sid, (h, v) in series.items():
        r = window_metrics(h, v, a, b, cap_h=cap_h)
        if r is None:
            continue
        rows.append(r)
    if not rows:
        return None
    any_arr = np.array([r["any"] for r in rows])
    n = len(rows)
    pos_n = int((any_arr > 0).sum())
    return dict(
        window=label,
        a=a,
        b=b,
        len_h=b - a,
        n_burden_ok=n,
        n_pos=pos_n,
        any_pct=round(100.0 * pos_n / n, 1) if n else np.nan,
        mean_burden=round(float(np.nanmean([r["burden"] for r in rows])), 4),
        median_burden=round(float(np.nanmedian([r["burden"] for r in rows])), 4),
        mean_hypo_h=round(float(np.nanmean([r["hypo_h"] for r in rows])), 4),
        mean_auc=round(float(np.nanmean([r["auc"] for r in rows])), 4),
        mean_twa=round(float(np.nanmean([r["twa"] for r in rows])), 2),
        median_sd=round(float(np.nanmedian([r["sd"] for r in rows])), 3),
        median_arv=round(float(np.nanmedian([r["arv"] for r in rows])), 3),
        median_cov=round(float(np.nanmedian([r["cov"] for r in rows])), 3),
        median_npts=int(np.nanmedian([r["npts"] for r in rows])),
        n_var_ok=int(np.sum(~np.isnan([r["sd"] for r in rows]))),
    )


def length_curve(
    series: Mapping[Any, Tuple[np.ndarray, np.ndarray]],
    start: float,
    lengths: Sequence[float],
    cap_h: float = CAP_H,
) -> list:
    rows = []
    for L in lengths:
        s = summarize_window(series, start, start + float(L), f"L{L}", cap_h=cap_h)
        if not s:
            continue
        rows.append(
            dict(
                start_h=start,
                L_h=float(L),
                n=s["n_burden_ok"],
                n_pos=s["n_pos"],
                any_pct=s["any_pct"],
                mean_burden=s["mean_burden"],
                mean_hypo_h=s["mean_hypo_h"],
                mean_auc=s["mean_auc"],
                mean_twa=s["mean_twa"],
                median_sd=s["median_sd"],
                median_arv=s["median_arv"],
                median_cov=s["median_cov"],
            )
        )
    return rows


def permute_values(
    series: Mapping[Any, Tuple[np.ndarray, np.ndarray]],
    rng: np.random.Generator,
) -> Dict[Any, Tuple[np.ndarray, np.ndarray]]:
    """Within-patient permutation of MAP values; hours stay fixed."""
    return {k: (h, rng.permutation(v)) for k, (h, v) in series.items()}
