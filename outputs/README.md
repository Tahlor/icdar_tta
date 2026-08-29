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
- `augmentation_contribution.csv` — optional compact contribution analysis.

## `outputs/figures/`

Presentation-ready generated assets. Prefer a stable basename with multiple formats, e.g.:

- `01_useful_diversity.svg` / `.png`
- `02_effective_sample_size.svg` / `.png`
- `03_precision_coverage.svg` / `.png`
- `04_cost_review_frontier.svg` / `.png`
- `05_shift_periodicity.svg` / `.png`
- `06_cross_model_coverage.svg` / `.png`

Final filenames can change once the deck order settles.

## Provenance

Each generated figure should have enough build metadata/logging to recover the repository SHA and source-table checksum used to make it.
