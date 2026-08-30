# Outputs

Planned output layout once analysis code is added.

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
- `modern_smoke_metadata.csv` — redacted six-row route/parser/usage metadata for the latest label-blind Gemini smoke; raw response bodies remain outside Git.

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
