# Outputs

Output layout for compact, release-safe analysis products. Historical tables
already present in this directory are generated from the legacy/public v7
lineage; they are not silently interchangeable with the paper-v9/v10
3,684-row population. See [`docs/GT_LINEAGE.md`](../docs/GT_LINEAGE.md).

## Modern transfer-screen outputs

The current derived tables include a complete nine-view PA screen for
`gemini-3.5-flash` and `gemini-3.5-flash-lite`: 622 documents × nine views per
model, with consensus and precision/coverage analysis derived offline from
the stored terminal rows. The full execution, route blockers, parser repair
counts, request ledger accounting, and exact model-specific metrics are in
[`local_agent/MODERN_FULL_RECEIPT.md`](../local_agent/MODERN_FULL_RECEIPT.md).

The predeclared 0.95 accepted-field precision target was not reached by the
modern strategies, so `cross_model_operating_points.csv` contains no invented
modern operating point. The 3.5 Flash model is the allowed substitute for the
unavailable 3.7 route; Qwen and 3.7 remain explicit blockers. Raw source
images and response bodies stay outside Git. The chart generator uses only
the committed machine-readable tables and emits all 18 required SVG/PNG
files.

## `outputs/derived/`

Machine-readable chart/analysis inputs. Candidate files:

- `field_predictions.parquet` — normalized field-level prediction table if release-safe;
- `strategy_summary.csv` — individual/consensus accuracy, CER, and correlation by strategy/sample count;
- `error_correlation_summary.csv` — empirical correlation values for the math/diversity slide;
- `precision_coverage.csv` — threshold sweep with accepted counts/precision/coverage/review;
- `shift_agreement.csv` — shift amount/direction and agreement series;
- `cost_by_run.csv` — normalized measured/estimated API usage and provenance;
- `review_frontier.csv` — cost vs human-review operating points;
- `cross_model_operating_points.csv` — fixed-precision cross-model comparison;
- `augmentation_contribution.csv` — compact contribution analysis for C7;
- `ensemble_size.csv` — ensemble size, strategy, quality, and coverage series for C8;
- `failure_examples.csv` — stable qualitative-example lineage and release metadata for C9.
- `modern_smoke_metadata.csv` — redacted six-row route/parser/usage metadata for the initial U0 smoke. The complete two-model screen is represented by the modern rows in the aggregate tables and documented in `local_agent/MODERN_FULL_RECEIPT.md`; raw response bodies remain outside Git.

Denominator rule: every table carrying `total_evaluated_fields` or an
equivalent count must identify its GT lineage. Use “legacy/public v7, 3,682
rows” for the existing historical tables; use “paper v9/v10, 3,684 row slots
(3,683 strict nonblank plus one retained blank)” only after a dedicated
paper-lineage recomputation.

## `outputs/figures/`

Presentation-ready generated assets. The chart completion contract requires these stable basenames in both SVG and PNG:

- `01_useful_diversity.svg` / `.png`
- `02_effective_sample_size.svg` / `.png`
- `03_precision_coverage.svg` / `.png`
- `04_cost_review_frontier.svg` / `.png`
- `05_shift_periodicity.svg` / `.png`
- `06_cross_model_coverage.svg` / `.png`
- `07_augmentation_contribution.svg` / `.png`
- `08_ensemble_size.svg` / `.png`
- `09_failure_examples.svg` / `.png`

These filenames and chart roles may change only with explicit project-owner approval and a matching update to `docs/CHART_PLAN.md`.

## Provenance

Each generated figure should have enough build metadata/logging to recover the repository SHA and source-table checksum used to make it.
