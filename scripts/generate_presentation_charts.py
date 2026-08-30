#!/usr/bin/env python3
"""Generate focused presentation charts from real committed evidence.

These are deliberately separate from the audit-oriented C1-C9 figures.  The
presentation charts simplify the visual story without changing or inventing
numeric evidence.  SVG is the primary editable artifact; PNG is a convenience
render.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def finish(fig, out: Path, stem: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / f"{stem}.svg", bbox_inches="tight")
    fig.savefig(out / f"{stem}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def load_modern_strategy(path: Path) -> pd.DataFrame:
    # strategy_summary.csv contains a small set of legacy rows whose notes make
    # them awkward for generic dataframe parsing.  The modern rows themselves
    # are closed 15-column records, so select them with csv.reader first.
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = []
        for row in reader:
            if len(row) == len(header) and row[0] in {
                "gemini-3.5-flash", "gemini-3.5-flash-lite"
            }:
                rows.append(dict(zip(header, row)))
    df = pd.DataFrame(rows)
    for col in (
        "n_samples", "individual_cer", "individual_field_accuracy",
        "error_correlation", "consensus_cer", "consensus_field_accuracy",
    ):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def chart_historical_diversity(paper: pd.DataFrame, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(paper.error_correlation, paper.individual_cer_pct, s=70)
    offsets = {
        "Temperature 0.5": (5, 8), "Temperature 1.0": (5, 8),
        "Temperature 2.0": (5, -20), "Blur + Resize": (-88, -18),
        "Gaussian Noise": (6, 8), "Grid Warp": (7, 5),
        "Resize": (-46, 8), "Pad": (-25, -22),
    }
    emphasized = {"Grid Warp", "Pad", "Resize", "Temperature 2.0"}
    for _, r in paper.iterrows():
        label = r.strategy
        if r.strategy in emphasized:
            label += f"\n{r.individual_cer_pct:.1f}→{r.consensus_cer_10_pct:.1f}% CER"
        ax.annotate(label, (r.error_correlation, r.individual_cer_pct),
                    xytext=offsets[r.strategy], textcoords="offset points", fontsize=9)
    ax.set_xlabel("Mean pairwise error correlation ρ  (lower = more diverse)")
    ax.set_ylabel("Mean individual CER (%)  (lower = better)")
    ax.set_title("Useful diversity requires both accurate members and different mistakes")
    ax.grid(True, alpha=.25)
    ax.text(.01, -.16,
            "Published paper Table 1. Arrow labels show individual CER → 10-sample consensus CER.",
            transform=ax.transAxes, fontsize=9)
    finish(fig, out, "01_historical_useful_diversity")


def chart_effective_sample_size(paper: pd.DataFrame, out: Path) -> None:
    rho = np.linspace(0, 1, 401)
    n = 10
    neff = n / (1 + (n - 1) * rho)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(rho, neff, linewidth=2.5, label="Stylized N=10 curve")
    for _, r in paper[paper.strategy.isin(["Grid Warp", "Pad", "Resize", "Temperature 2.0"])].iterrows():
        y = n / (1 + (n - 1) * r.error_correlation)
        ax.scatter([r.error_correlation], [y], s=65)
        ax.annotate(f"{r.strategy}\nρ={r.error_correlation:.3f}, Nₑff≈{y:.2f}",
                    (r.error_correlation, y), xytext=(6, 7),
                    textcoords="offset points", fontsize=9)
    ax.set_xlim(0, 1)
    ax.set_ylim(1, 10.2)
    ax.set_xlabel("Pairwise error correlation ρ")
    ax.set_ylabel("Stylized effective sample size Nₑff")
    ax.set_title("Ten correlated calls can contain barely more than one independent opinion")
    ax.text(.02, .92, r"$N_{\mathrm{eff}}=\frac{N}{1+(N-1)\rho}$",
            transform=ax.transAxes, fontsize=16)
    ax.grid(True, alpha=.25)
    ax.text(.01, -.15,
            "Intuition model, not a measured effective-sample count; markers use published empirical correlations.",
            transform=ax.transAxes, fontsize=9)
    finish(fig, out, "02_effective_sample_size")


def chart_historical_precision(pc: pd.DataFrame, out: Path) -> None:
    hist = pc[pc.model_id == "models/gemini-2.0-flash"].copy()
    fig, ax = plt.subplots(figsize=(10, 6))
    for strategy in ("Grid Warp", "Pad", "Resize"):
        g = hist[hist.strategy == strategy].sort_values("coverage")
        ax.plot(g.coverage * 100, g.precision * 100, linewidth=2, label=strategy)
    ax.axhline(95, linestyle="--", linewidth=1.5, label="95% precision target")
    op = hist[(hist.strategy == "Grid Warp") & (hist.precision >= .95)]
    op = op.loc[op.coverage.idxmax()]
    ax.scatter([op.coverage * 100], [op.precision * 100], s=90, zorder=5)
    ax.annotate(f"Grid Warp: {op.coverage*100:.1f}% auto-accepted\nat {op.precision*100:.2f}% precision",
                (op.coverage*100, op.precision*100), xytext=(18, -50),
                textcoords="offset points", fontsize=10,
                arrowprops={"arrowstyle": "->"})
    ax.set_xlim(25, 100)
    ax.set_ylim(65, 100)
    ax.set_xlabel("Automatic coverage (%)")
    ax.set_ylabel("Precision among auto-accepted fields (%)")
    ax.set_title("Grid Warp creates the strongest high-precision selection signal")
    ax.legend()
    ax.grid(True, alpha=.25)
    ax.text(.01, -.16,
            "Legacy/public v7 reliability tables, 3,682-row lineage; not a paper-v9/v10 3,684-row recomputation.",
            transform=ax.transAxes, fontsize=9)
    finish(fig, out, "03_historical_precision_coverage")


def chart_shift(shift: pd.DataFrame, out: Path) -> None:
    agg = (shift[shift.absolute_shift_px > 0]
           .groupby(["direction", "absolute_shift_px"], as_index=False).agreement.mean())
    fig, ax = plt.subplots(figsize=(10, 6))
    for direction in ("horizontal", "vertical"):
        g = agg[agg.direction == direction].sort_values("absolute_shift_px")
        ax.plot(g.absolute_shift_px, g.agreement * 100, marker="o", markersize=3,
                linewidth=1.8, label=direction.title())
        m = g[g.absolute_shift_px.isin([16, 32, 48, 64])]
        ax.scatter(m.absolute_shift_px, m.agreement * 100, s=65, zorder=5)
    for x in (16, 32, 48, 64):
        ax.axvline(x, linestyle=":", linewidth=1)
    ax.set_xlim(2, 64)
    ax.set_ylim(75, 79.5)
    ax.set_xlabel("Absolute relative shift (pixels); 0 px intentionally omitted")
    ax.set_ylabel("Mean pairwise transcription agreement (%)")
    ax.set_title("Transcription agreement repeatedly recovers at ~16-pixel phases")
    ax.legend()
    ax.grid(True, alpha=.25)
    ax.text(.01, -.16,
            "All non-zero historical shift points; ± shifts averaged by absolute displacement. Observational, not proof of internals.",
            transform=ax.transAxes, fontsize=9)
    finish(fig, out, "04_shift_periodicity_zoomed")


def chart_ensemble_gain(paper: pd.DataFrame, out: Path) -> None:
    g = paper.sort_values("ensemble_cer_gain_pp")
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(g.strategy, g.ensemble_cer_gain_pp)
    ax.set_xlabel("CER improvement from ensembling (percentage points)\nmean individual CER − 10-sample consensus CER")
    ax.set_title("Grid Warp benefits most from consensus—even though its members are worst individually")
    for bar, (_, r) in zip(bars, g.iterrows()):
        ax.text(bar.get_width() + .06, bar.get_y() + bar.get_height()/2,
                f"{r.ensemble_cer_gain_pp:.1f} pp  (final {r.consensus_cer_10_pct:.1f}%)",
                va="center", fontsize=9)
    ax.grid(True, axis="x", alpha=.25)
    ax.text(.01, -.16,
            "Published Table 1. Large ensemble gain does not imply best final accuracy; Temperature 2.0 is the counterexample.",
            transform=ax.transAxes, fontsize=9)
    finish(fig, out, "05_historical_ensemble_gain")


def chart_modern_transfer(modern: pd.DataFrame, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    for model, g in modern.groupby("model_id"):
        single = float(g.loc[g.strategy == "single", "consensus_cer"].iloc[0])
        h = g[g.strategy.isin(["unchanged_3", "Pad", "Grid Warp", "visual_mixed_6", "all_views_9"])].copy()
        h["reduction"] = (single - h.consensus_cer) / single * 100
        label = "Gemini 3.5 Flash-Lite" if model.endswith("flash-lite") else "Gemini 3.5 Flash"
        ax.scatter(h.error_correlation, h.reduction, s=75, label=label)
        for _, r in h.iterrows():
            short = {"unchanged_3": "unchanged ×3", "visual_mixed_6": "mixed ×6", "all_views_9": "all ×9"}.get(r.strategy, r.strategy)
            ax.annotate(short, (r.error_correlation, r.reduction),
                        xytext=(5, 5), textcoords="offset points", fontsize=8)
    ax.set_xlabel("Mean pairwise error correlation ρ  (lower = more diverse)")
    ax.set_ylabel("Consensus CER reduction vs single call (%)  (higher = better)")
    ax.set_title("Visual diversity still helps on modern Gemini 3.5 models")
    ax.legend()
    ax.grid(True, alpha=.25)
    ax.text(.01, -.16,
            "Measured 622-document modern screen; 3,718 raw six-name nonblank fields; fixed views, no per-model retuning.",
            transform=ax.transAxes, fontsize=9)
    finish(fig, out, "06_modern_transfer_diversity")


def chart_modern_precision(pc: pd.DataFrame, out: Path, model: str, stem: str, title_model: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    gm = pc[pc.model_id == model]
    for strategy in ("Pad", "Grid Warp", "all_views_9"):
        g = gm[gm.strategy == strategy].sort_values("coverage")
        ax.plot(g.coverage * 100, g.precision * 100, linewidth=2,
                label="All views ×9" if strategy == "all_views_9" else strategy)
        if strategy == "all_views_9":
            best = g.loc[g.precision.idxmax()]
            ax.scatter([best.coverage*100], [best.precision*100], s=90, zorder=5)
            ax.annotate(f"best observed: {best.precision*100:.1f}% precision\nat {best.coverage*100:.1f}% coverage",
                        (best.coverage*100, best.precision*100), xytext=(-145, -48),
                        textcoords="offset points", fontsize=9,
                        arrowprops={"arrowstyle": "->"})
    ax.axhline(95, linestyle="--", linewidth=1.5, label="Predeclared 95% target")
    ax.set_xlim(0, 100)
    ax.set_ylim(70 if model.endswith("flash-lite") else 78, 97)
    ax.set_xlabel("Automatic coverage (%)")
    ax.set_ylabel("Precision among auto-accepted fields (%)")
    ax.set_title(f"{title_model}: raw agreement improves selectivity but misses 95%")
    ax.legend()
    ax.grid(True, alpha=.25)
    ax.text(.01, -.16,
            "Modern measured raw agreement; not calibrated. The 95% line was predeclared before labels were opened.",
            transform=ax.transAxes, fontsize=9)
    finish(fig, out, stem)


def chart_token_budget(cost: pd.DataFrame, out: Path) -> None:
    c = cost[cost.model_id.isin(["gemini-3.5-flash", "gemini-3.5-flash-lite"])].copy()
    c["usage_amount"] = pd.to_numeric(c.usage_amount, errors="coerce")
    c["tokens_per_document"] = c.usage_amount / 622
    fig, ax = plt.subplots(figsize=(8, 5.5))
    bars = ax.bar(["Gemini 3.5 Flash", "Gemini 3.5 Flash-Lite"], c.tokens_per_document)
    for bar, (_, r) in zip(bars, c.iterrows()):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+250,
                f"{r.tokens_per_document:,.0f}\nprovider tokens/doc",
                ha="center", va="bottom", fontsize=9)
    ax.set_ylabel("Provider-reported total tokens per document")
    ax.set_title("Measured inference budget for the complete 9-view modern screen")
    ax.grid(True, axis="y", alpha=.25)
    ax.text(.01, -.18,
            "Measured usage, not dollar cost. Dollar pricing requires input/output token split, absent from the portable receipt.",
            transform=ax.transAxes, fontsize=9)
    finish(fig, out, "09_modern_measured_token_budget")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--derived-dir", default="outputs/derived")
    p.add_argument("--output-dir", default="outputs/presentation_charts")
    args = p.parse_args()
    d = Path(args.derived_dir)
    out = Path(args.output_dir)
    paper = pd.read_csv(d / "presentation_historical_table1.csv")
    pc = pd.read_csv(d / "precision_coverage.csv")
    shift = pd.read_csv(d / "shift_agreement.csv")
    modern = load_modern_strategy(d / "strategy_summary.csv")
    cost = pd.read_csv(d / "cost_by_run.csv")
    chart_historical_diversity(paper, out)
    chart_effective_sample_size(paper, out)
    chart_historical_precision(pc, out)
    chart_shift(shift, out)
    chart_ensemble_gain(paper, out)
    chart_modern_transfer(modern, out)
    chart_modern_precision(pc, out, "gemini-3.5-flash", "07_modern_precision_coverage_flash", "Gemini 3.5 Flash")
    chart_modern_precision(pc, out, "gemini-3.5-flash-lite", "08_modern_precision_coverage_flash_lite", "Gemini 3.5 Flash-Lite")
    chart_token_budget(cost, out)
    print(f"Generated focused presentation charts in {out}")


if __name__ == "__main__":
    main()
