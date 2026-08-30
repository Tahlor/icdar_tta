# Focused presentation chart status

Status: **real-data presentation charts implemented; two evidence gaps remain**.

The audit-oriented C1-C9 figures remain useful for provenance, but the timed talk needs cleaner charts with one argumentative job each. `scripts/generate_presentation_charts.py` now regenerates the focused chart set from committed numeric evidence. SVG is the primary editable artifact; PNG is a convenience render. The cloud workflow runs the generator and uploads both formats.

## Main chart candidates

| ID | Output | Real source | Intended slide job |
|---|---|---|---|
| P1 | `outputs/presentation_charts/01_historical_useful_diversity.svg` | `outputs/derived/presentation_historical_table1.csv` | Historical scatter: x = pairwise error correlation; y = mean individual CER. Shows Resize, Pad, Grid Warp, and temperature controls. Key labels also show 10-sample consensus CER. |
| P2 | `outputs/presentation_charts/02_effective_sample_size.svg` | published Table 1 correlations + stated theoretical formula | Math slide: x = rho; y = stylized N_eff for N=10; empirical markers for Grid Warp, Pad, Resize, Temperature 2.0. |
| P3 | `outputs/presentation_charts/03_historical_precision_coverage.svg` | `precision_coverage.csv` | Historical selective-confidence result: x = automatic coverage; y = accepted-field precision; series Grid Warp, Pad, Resize; 95% guide; annotate Grid Warp 40.4% coverage at 95.23% precision. Explicitly legacy/public v7 3,682-row lineage. |
| P4 | `outputs/presentation_charts/04_shift_periodicity_zoomed.svg` | `shift_agreement.csv` | Mechanism result: x = absolute relative shift 2-64 px; y = mean pairwise transcription agreement; horizontal + vertical series; 0 px omitted; markers/guides at 16/32/48/64. |
| P5 | `outputs/presentation_charts/05_historical_ensemble_gain.svg` | `presentation_historical_table1.csv` | Compact augmentation contribution chart: CER gain from individual predictions to 10-sample consensus. Makes the Grid-Warp counterexample and temperature negative result obvious. Candidate backup or alternative to P1. |
| P6 | `outputs/presentation_charts/06_modern_transfer_diversity.svg` | modern rows in `strategy_summary.csv` | Modern replication: x = error correlation; y = percentage CER reduction vs the single-call baseline. Series = Gemini 3.5 Flash and Flash-Lite. Shows visual variants reduce correlation and improve consensus. |
| P7 | `outputs/presentation_charts/07_modern_precision_coverage_flash.svg` | modern `precision_coverage.csv` | Gemini 3.5 Flash descriptive precision/coverage: Pad, Grid Warp, all-views; predeclared 95% guide. Best all-views observed precision is ~91.5%, so target is visibly not met. |
| P8 | `outputs/presentation_charts/08_modern_precision_coverage_flash_lite.svg` | modern `precision_coverage.csv` | Gemini 3.5 Flash-Lite descriptive precision/coverage: Pad, Grid Warp, all-views; predeclared 95% guide. Best all-views observed precision is ~93.4%, so target is visibly not met. |
| P9 | `outputs/presentation_charts/09_modern_measured_token_budget.svg` | `cost_by_run.csv` | Interim cost evidence only: provider-reported total tokens per document for the complete nine-view screen. This is **not** a dollar-cost chart. |

## Recommended main-deck use

Use P1 (or P5 if P1 is too abstract), P2, P3, P4, and P6. P7/P8 are useful as a combined modern-limitations slide or backup. P9 is backup until proper pricing can be computed.

The historical and modern precision/coverage results must not be merged into one unlabeled curve family: they use different denominators and answer different questions. P3 is the historical deployment story; P7/P8 are the honest modern replication result.

## Remaining evidence gaps

### A. Dollar cost / manual-review frontier

The modern run records total provider tokens and requests, but the portable derived table does not contain **input-token versus output/thinking-token totals by model and strategy**. Gemini prices those categories differently, so applying a single dollar rate to total tokens would be fabricated.

Required local-agent extraction:

1. From the preserved modern raw response metadata, sum provider-reported input/prompt tokens and output/candidate/thinking tokens separately.
2. Produce totals by exact model and by view/strategy (`U`, `P`, `G`, and derived ensemble membership), plus retry/failure accounting.
3. Commit only aggregate token totals; no raw response text or credentials.
4. Add a dated provider pricing snapshot and compute measured/estimated USD per 1,000 documents and per 1,000 evaluated fields.
5. Do not fabricate a modern 95%-precision review frontier: no modern raw-agreement strategy met that predeclared target. If lower precision targets are shown descriptively, label them post-hoc/descriptive rather than predeclared deployment targets.

Official pricing snapshot to verify/record at execution time (2026-08-30 Google Gemini Developer API page): Gemini 3.5 Flash standard lists separate input and output rates; Gemini 3.5 Flash-Lite likewise lists separate lower input/output rates. The repository needs the dated snapshot plus the real token split before dollar plotting.

### B. Release-safe qualitative example

The public/release-authorized fixture already contains two real Pennsylvania death-record images under `examples/samples/`. What remains unavailable in Git is a release-safe mapping from one of those images to real per-view model predictions. The local agent should extract a small release-safe example table for `U0`, one Pad view, and one Grid-Warp view, including model/run/view IDs and prediction strings only if those outputs are approved for release. This is needed for the opening hook, not for a numeric chart.

## Integrity rules

- No chart may use invented points, schematic curves, or visually inferred values.
- P1/P2/P5 use the published paper Table 1 values now committed in machine-readable form.
- P3 is explicitly legacy/public v7 evidence, not a new 3,684-row paper-lineage recomputation.
- P4 omits the trivial 0-pixel self-agreement point only for readability; all non-zero source points are retained after symmetric ± displacement is averaged by absolute shift.
- P6-P8 use the measured modern 3,718-field screen and remain labeled as that denominator.
- Raw agreement is never called a calibrated probability.
