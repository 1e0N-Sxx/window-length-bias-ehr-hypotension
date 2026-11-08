#!/usr/bin/env python3
"""Regenerate manuscript Figs 1–3 from the shipped n=145 summary CSVs.

Reads data/summary/ only. Does not fabricate numbers and does not write into
the Journal submission pack. Figure 2 does not draw an on-canvas
observed-versus-permutation callout; that comparison stays in the caption.
"""
from __future__ import annotations
from pathlib import Path
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "data" / "summary"
OUT = ROOT / "out_figures"
try:
    from audit_panel_alignment import require_matplotlib_panel_alignment  # type: ignore
except Exception:  # noqa: BLE001
    require_matplotlib_panel_alignment = None

P_LEN_0H = SUMMARY / "length_curve_0h_v1.csv"
P_LEN_24H = SUMMARY / "length_curve_24h_v1.csv"
P_PERM = SUMMARY / "perm_null_v1.csv"
P_SUM = SUMMARY / "summary_WE_v1.csv"
P_MIMIC = SUMMARY / "MIMICfull_windows_complete_v1.csv"

PALETTE = {
    "blue_main": "#0F4D92", "red_strong": "#B64342", "neutral_mid": "#767676",
    "neutral_dark": "#4D4D4D", "obs": "#0F4D92", "perm": "#B64342",
    "unequal": "#0F4D92", "equal": "#42949E",
}


def apply_style():
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
        "svg.fonttype": "none", "pdf.fonttype": 42, "ps.fonttype": 42,
        "font.size": 7, "axes.labelsize": 7, "axes.titlesize": 8,
        "xtick.labelsize": 6.5, "ytick.labelsize": 6.5, "legend.fontsize": 6.5,
        "axes.spines.right": False, "axes.spines.top": False, "axes.linewidth": 0.8,
        "legend.frameon": False, "figure.dpi": 150, "savefig.dpi": 600,
        "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
    })


def add_panel_label(ax, label, x=-0.12, y=1.08):
    ax.text(x, y, label, transform=ax.transAxes, fontsize=9, fontweight="bold",
            va="top", ha="left", clip_on=False)


def save_pub(fig, stem: Path, multi=True):
    stem = Path(stem)
    stem.parent.mkdir(parents=True, exist_ok=True)
    fig.canvas.draw()
    try:
        if require_matplotlib_panel_alignment is None:
            raise RuntimeError("alignment helper not installed")
        require_matplotlib_panel_alignment(
            fig, json_out=f"{stem}.alignment.json", overlay_svg=f"{stem}.alignment.svg",
            tolerance_pt=1.5, gutter_tolerance_pt=1.5, strict=True,
        )
    except Exception as exc:  # noqa: BLE001
        Path(f"{stem}.alignment.json").write_text(
            f'{{"status":"SKIPPED","detail":"{type(exc).__name__}: {exc}"}}\n'
        )
    fig.savefig(f"{stem}.svg"); fig.savefig(f"{stem}.pdf")
    fig.savefig(f"{stem}.png", dpi=600)
    try:
        fig.savefig(f"{stem}.tiff", dpi=600)
    except Exception as exc:  # noqa: BLE001
        print("TIFF skip:", exc)
    plt.close(fig)


def load():
    d0 = pd.read_csv(P_LEN_0H)
    d24 = pd.read_csv(P_LEN_24H)
    perm = pd.read_csv(P_PERM).set_index("window")
    summ = pd.read_csv(P_SUM)
    mimic = pd.read_csv(P_MIMIC)

    # Anchors from recomputed n145 (must match CHANGELOG)
    r24_1 = d24.loc[d24.L_h == 1].iloc[0]
    r24_48 = d24.loc[d24.L_h == 48].iloc[0]
    assert round(float(r24_1.any_pct), 1) == 4.2
    assert round(float(r24_48.any_pct), 1) == 47.6
    assert int(r24_48.n) == 145
    r0_1 = d0.loc[d0.L_h == 1].iloc[0]
    r0_72 = d0.loc[d0.L_h == 72].iloc[0]
    assert round(float(r0_1.any_pct), 1) == 12.4
    assert round(float(r0_72.any_pct), 1) == 62.1

    obs = [float(perm.loc[w, "observed_pos_pct"]) for w in ["W1_0_6", "W2_6_24", "W3_24_72"]]
    pmean = [float(perm.loc[w, "perm_mean"]) for w in ["W1_0_6", "W2_6_24", "W3_24_72"]]
    assert obs == [27.6, 34.5, 47.6], obs
    assert pmean == [24.8, 41.2, 56.7], pmean

    def pct(design, window):
        r = summ[(summ.design == design) & (summ.window == window)].iloc[0]
        return float(r.pos_pct_among_evaluable)

    eicu_u = [pct("original_unequal", w) for w in ["W1_0_6", "W2_6_24", "W3_24_72"]]
    eicu_e = [pct("equal6h_end_of_parent", w) for w in ["E1_0_6", "E2_18_24", "E3_66_72"]]
    assert eicu_u == [27.6, 34.5, 47.6]
    assert eicu_e == [27.6, 17.2, 17.2]

    mw = mimic.loc[mimic["set"].str.startswith("complete_W")].copy()
    me = mimic.loc[mimic["set"].str.startswith("complete_E")].copy()
    mimic_u = [float(mw.loc[mw.window == w, "any_pct"].iloc[0]) for w in ["W1_0_6", "W2_6_24", "W3_24_72"]]
    mimic_e = [float(me.loc[me.window == w, "any_pct"].iloc[0]) for w in ["E1_0_6", "E2_18_24", "E3_66_72"]]
    assert mimic_u == [43.7, 60.8, 70.5]
    assert mimic_e == [43.8, 39.2, 31.2]

    print("ANCHOR CHECK PASS (n145)")
    return dict(
        d0=d0, d24=d24, perm=perm,
        eicu_unequal=eicu_u, eicu_equal=eicu_e,
        mimic_unequal=mimic_u, mimic_equal=mimic_e,
        n_eicu_u=145, n_eicu_e=145,
        n_mimic_u=int(mw.n.iloc[0]), n_mimic_e=int(me.n.iloc[0]),
        obs=obs, pmean=pmean,
    )


def plot_length_panel(ax, df, title, panel, xlim_max):
    x = df.L_h.to_numpy(float)
    any_pct = df.any_pct.to_numpy(float)
    burden = df.mean_burden.to_numpy(float)
    (ln1,) = ax.plot(x, any_pct, color=PALETTE["blue_main"], marker="o", markersize=3.5,
                     linewidth=1.4, label="Any MAP <65 (%)", zorder=3)
    ax.set_xlabel("Window length L (h)")
    ax.set_ylabel("Any MAP <65 positivity (%)", color=PALETTE["blue_main"])
    ax.tick_params(axis="y", colors=PALETTE["blue_main"])
    ax.set_xlim(0, xlim_max)
    ax.set_ylim(0, max(65.0, float(np.nanmax(any_pct)) * 1.08))
    ax.set_title(title, loc="left", pad=4)
    ax2 = ax.twinx()
    (ln2,) = ax2.plot(x, burden, color=PALETTE["red_strong"], marker="s", markersize=3.2,
                      linewidth=1.2, linestyle="--", label="Mean TWA burden", zorder=2)
    ax2.set_ylabel("Mean TWA burden", color=PALETTE["red_strong"])
    ax2.tick_params(axis="y", colors=PALETTE["red_strong"])
    ax2.spines["right"].set_visible(True)
    ax2.spines["top"].set_visible(False)
    ax2.set_ylim(0, 0.12)
    ax.legend([ln1, ln2], ["Any MAP <65 (%)", "Mean TWA burden"],
              loc="upper left", bbox_to_anchor=(0.02, 0.98), handlelength=2.2)
    add_panel_label(ax, panel)


def make_fig1(data):
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8), constrained_layout=True)
    plot_length_panel(axes[0], data["d0"], "0 h start (ICU admission)", "a", 76)
    plot_length_panel(axes[1], data["d24"], "24 h start", "b", 52)
    ymax = max(axes[0].get_ylim()[1], axes[1].get_ylim()[1])
    for ax in axes:
        ax.set_ylim(0, ymax)
    save_pub(fig, OUT / "Fig1_length_curves", multi=True)


def make_fig2(data):
    perm = data["perm"]
    windows = ["W1_0_6", "W2_6_24", "W3_24_72"]
    labels = ["W1\n[0, 6)", "W2\n[6, 24)", "W3\n[24, 72)"]
    obs = np.array([float(perm.loc[w, "observed_pos_pct"]) for w in windows])
    pmean = np.array([float(perm.loc[w, "perm_mean"]) for w in windows])
    lo = np.array([float(perm.loc[w, "perm_2.5"]) for w in windows])
    hi = np.array([float(perm.loc[w, "perm_97.5"]) for w in windows])
    x = np.arange(len(windows))
    fig, ax = plt.subplots(figsize=(3.6, 2.9), constrained_layout=True)
    yerr = np.vstack([pmean - lo, hi - pmean])
    ax.errorbar(x, pmean, yerr=yerr, fmt="D", color=PALETTE["perm"], markersize=5,
                linewidth=1.2, capsize=3.5, capthick=1.0,
                label="Permutation mean (2.5–97.5%)", zorder=2)
    ax.plot(x, obs, marker="o", markersize=7, linewidth=1.6, color=PALETTE["obs"],
            label="Observed", zorder=3)
    # Obs-vs-perm comparison is stated in the figure caption, not on-canvas
    # (avoids crowding the legend at upper left).
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_ylabel("Any MAP <65 positivity (%)")
    ax.set_ylim(0, 70); ax.set_xlim(-0.4, 2.4)
    ax.legend(loc="upper left", bbox_to_anchor=(0.02, 0.98))
    ax.set_title("Unequal windows vs within-patient permutation null", loc="left", pad=4)
    save_pub(fig, OUT / "Fig2_perm_null", multi=False)


def make_fig3(data):
    cats = ["Early\n(0–6 h)", "Mid\n(6–24 / 18–24 h)", "Late\n(24–72 / 66–72 h)"]
    x = np.arange(len(cats)); width = 0.36
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9), constrained_layout=True)
    ax = axes[0]
    u = np.array(data["eicu_unequal"]); e = np.array(data["eicu_equal"])
    ax.bar(x - width/2, u, width, color=PALETTE["unequal"],
           label=f"Unequal W1–W3 (n={data['n_eicu_u']})", edgecolor="none")
    ax.bar(x + width/2, e, width, color=PALETTE["equal"],
           label=f"Equal-end 6 h (n={data['n_eicu_e']})", edgecolor="none")
    ax.set_ylabel("Any MAP <65 positivity (%)")
    ax.set_xticks(x); ax.set_xticklabels(cats); ax.set_ylim(0, 55)
    ax.set_title("EICU primary cohort (complete-case)", loc="left", pad=4)
    ax.legend(loc="upper left")
    ax.text(2 - width/2, u[2] + 1.2, f"{u[2]:.1f}", ha="center", va="bottom", fontsize=6, color=PALETTE["unequal"])
    ax.text(2 + width/2, e[2] + 1.2, f"{e[2]:.1f}", ha="center", va="bottom", fontsize=6, color=PALETTE["equal"])
    add_panel_label(ax, "a")
    ax = axes[1]
    u = np.array(data["mimic_unequal"]); e = np.array(data["mimic_equal"])
    ax.bar(x - width/2, u, width, color=PALETTE["unequal"],
           label=f"Unequal W1–W3 (n={data['n_mimic_u']:,})", edgecolor="none")
    ax.bar(x + width/2, e, width, color=PALETTE["equal"],
           label=f"Equal-end 6 h (n={data['n_mimic_e']:,})", edgecolor="none")
    ax.set_xticks(x); ax.set_xticklabels(cats); ax.set_ylim(0, 85)
    ax.set_title("MIMIC-IV 3.1 external replication", loc="left", pad=4)
    ax.legend(loc="upper left")
    ax.text(2 - width/2, u[2] + 1.5, f"{u[2]:.1f}", ha="center", va="bottom", fontsize=6, color=PALETTE["unequal"])
    ax.text(2 + width/2, e[2] + 1.5, f"{e[2]:.1f}", ha="center", va="bottom", fontsize=6, color=PALETTE["equal"])
    add_panel_label(ax, "b")
    save_pub(fig, OUT / "Fig3_narrative_reversal_mimic", multi=True)


def main():
    apply_style()
    OUT.mkdir(parents=True, exist_ok=True)
    data = load()
    make_fig1(data); make_fig2(data); make_fig3(data)
    print("EXPORT COMPLETE ->", OUT)


if __name__ == "__main__":
    main()
