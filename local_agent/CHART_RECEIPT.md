# C1-C9 chart receipt

Status: **all 18 required files rendered offline; evidence limitations are shown rather than filled with unsupported values**. Receipt regenerated 2026-08-29 (16:59 local) after fixing the C4 row-label overlap identified in the prior visual QA pass in `scripts/generate_charts.py`, from repository HEAD `cebf7778cea92692da9837f8914ae0b61a29c399` and the working-tree inputs listed below. No provider, network, cloud, inference, credential, or external/private image access was used.

## Exact generation command

```bash
python3 scripts/generate_charts.py --derived-dir outputs/derived --figure-dir outputs/figures
```

The command printed:

```text
Generated 18 deterministic chart files in outputs/figures
```

Renderer: `scripts/generate_charts.py`; canvas: 1,200 x 675 pixels; numeric inputs: committed CSV files under `outputs/derived/` only. Runtime dependencies are Python standard-library modules (`argparse`, `csv`, `html`, `json`, `math`, `pathlib`, `struct`, and `zlib`). SVGs use native text and vector primitives. PNGs use the script's deterministic RGB bitmap text/primitives layer and PNG encoder. No matplotlib, Pillow, reportlab, numpy, fonts, images, or private roots are required.

## Chart/table mapping and evidence status

| ID / basename | Numeric input table(s) | Render status and limitation |
|---|---|---|
| C1 `01_useful_diversity` | `strategy_summary.csv` | Rendered 10 measured WARP per-condition coordinates. Selected v7 category rows are visibly separated as consensus-only; they have no correlation coordinate and are not called individual CER. |
| C2 `02_effective_sample_size` | `error_correlation_summary.csv` | Rendered the code-generated theoretical N=10 curve plus 10 measured WARP correlations projected onto it. Family-level Grid Warp and Resize correlations remain visibly blocked; prose values were not promoted. |
| C3 `03_precision_coverage` | `precision_coverage.csv` | Rendered all 1,750 raw-agreement threshold rows for Grid Warp, Pad, and Resize, including supplied 95% Wilson bounds. The 3,682-row denominator is labeled noncanonical and the score is labeled raw/not calibrated. |
| C4 `04_cost_review_frontier` | `cost_by_run.csv`; `review_frontier.csv` | Rendered the one numeric review-burden coordinate. All four cost rows lack observed usage/pricing; the cost axis and Pad/Resize target coordinates remain visibly blocked. No dollars were invented. |
| C5 `05_shift_periodicity` | `shift_agreement.csv` | Rendered all 130 reported horizontal/vertical points and 16-pixel guides. Periodicity is labeled observational, not architecture proof. |
| C6 `06_cross_model_coverage` | `cross_model_operating_points.csv` | Rendered one measured historical Grid Warp point, one historical Pad target-not-met row, and explicit blocked cells for all 12 rows across the three exact modern IDs. No modern result is implied. |
| C7 `07_augmentation_contribution` | `augmentation_contribution.csv` | Rendered all five family selection counts and source descriptors. Selection frequency is explicitly descriptive, not causal contribution. |
| C8 `08_ensemble_size` | `ensemble_size.csv` | Rendered 23 key rows across five source-reported series from the 53-row table. The approximately 4,920-field denominator is labeled noncanonical. |
| C9 `09_failure_examples` | `failure_examples.csv` | Rendered a blocked evidence panel from the single source row. No prediction, ground truth, crop, or private path was copied; stable redacted lineage and crop authorization remain unavailable. |

Each SVG contains a machine-readable `<metadata>` object with chart ID, 1,200 x 675 dimensions, numeric input filenames, renderer, one-sentence takeaway, and limitations. The same takeaway is visible as a subtitle. Measured, theoretical, reported, recomputed, and blocked roles are distinguished in chart text and styling.

## Source CSV provenance

Rows exclude the header.

| Source table | Rows | Bytes | SHA-256 |
|---|---:|---:|---|
| `outputs/derived/augmentation_contribution.csv` | 5 | 2,427 | `6d6e2c4be232d77e94ee31560bbc327c04e9596721a79e34c456e78b6f1ceab6` |
| `outputs/derived/cost_by_run.csv` | 4 | 911 | `bad4ed762ddf9761a6ea3b57171f26e3a8086c225d3672e4c023837fba17e665` |
| `outputs/derived/cross_model_operating_points.csv` | 14 | 5,145 | `ee1c9f00ccfa5014ab34c69a1a4c07d2870277f513ee9a5a4e1a5f79b7b4b438` |
| `outputs/derived/ensemble_size.csv` | 53 | 24,457 | `3deecacbf92eb76b17521adbef3e3294cbb4fe49dd96a68f02abd3d09b79d0cf` |
| `outputs/derived/error_correlation_summary.csv` | 12 | 5,368 | `93157ddd6c16b8f928df5f32cc6b29d353b0cea2b921c71d8a158473d90b985b` |
| `outputs/derived/failure_examples.csv` | 1 | 495 | `c4ecf82d3d5e5c0f909d0992cd2b3a3acaf0e3b2d87130b49c22541618b54b55` |
| `outputs/derived/precision_coverage.csv` | 1,750 | 998,692 | `619210cd328762df6b87b8195f18d506bf61dcfa236c44e27c207b31d83bd53a` |
| `outputs/derived/review_frontier.csv` | 3 | 1,667 | `3192b4c711a30e15ffb3febd8c6cd8f3c0ecf203ba5c61456787157c7c03f4de` |
| `outputs/derived/shift_agreement.csv` | 130 | 54,974 | `3e18fa536faf11992ae55ed8b5901f5a0d4c6b7ac1e394f07851d86158e77e96` |
| `outputs/derived/strategy_summary.csv` | 31 | 15,951 | `815c0d66b688f75cb736fe7765979dc14ad67ab370407e1804ff12981977f9c7` |

## Output provenance

| Output | Bytes | Dimensions | SHA-256 |
|---|---:|---:|---|
| `outputs/figures/01_useful_diversity.png` | 15,166 | 1200x675 | `133c6ddd6180f1e9b72c3539503c75ba47eddde99ca16b9445ad04f0d8391138` |
| `outputs/figures/01_useful_diversity.svg` | 8,589 | 1200x675 | `b9a60565fa1b64ce0ac65275298592fad66539cced29e6393596ea04374e2a9a` |
| `outputs/figures/02_effective_sample_size.png` | 14,403 | 1200x675 | `5f65a6fc2fa5728b9c832bba8d31c5018dc274f1926535957f40965ebdb2752f` |
| `outputs/figures/02_effective_sample_size.svg` | 9,246 | 1200x675 | `ca41c9316b788f493792ebf5a8799438948e6b68086b2f155ce802d773d7b7b0` |
| `outputs/figures/03_precision_coverage.png` | 14,941 | 1200x675 | `2039ec6aa7e713de94dd814925e367f86dfb25b4663efd30b1bac7b87024b0a7` |
| `outputs/figures/03_precision_coverage.svg` | 89,231 | 1200x675 | `77e103f790bab436e2e4ee2befd3806bdd1d5a77ff640b43557feec3feb1d5ec` |
| `outputs/figures/04_cost_review_frontier.png` | 12,429 | 1200x675 | `c149623cb2d1b7121e27a4e978a06861dd7a54779b7a0b0fb71519b5aa8e2705` |
| `outputs/figures/04_cost_review_frontier.svg` | 5,862 | 1200x675 | `70f2053cc9c86b2fe5e52c2d075cc9492548856b7357c7d199514d23a243a43b` |
| `outputs/figures/05_shift_periodicity.png` | 16,359 | 1200x675 | `50d12e231c7665364f401d71ef016ce7aaa659f15e4964616b4b91b074a17a48` |
| `outputs/figures/05_shift_periodicity.svg` | 11,912 | 1200x675 | `9a10c3507a7f890f5439302abb389274328de1a41ff62fd05aaed560a1e3d24b` |
| `outputs/figures/06_cross_model_coverage.png` | 10,024 | 1200x675 | `8fd911f5dffcdac45443e1321da750eded86b2887359e72a82321de483ad1c2f` |
| `outputs/figures/06_cross_model_coverage.svg` | 7,774 | 1200x675 | `d03c8f08ad9ecf454030deaaa34b0c31ecf71fe74d8b12670fb0db5576781e63` |
| `outputs/figures/07_augmentation_contribution.png` | 9,639 | 1200x675 | `b2b5f644420a87e9ef7a71b4b7fb58be9fad7c964c69039f249e73a2fe7d29ab` |
| `outputs/figures/07_augmentation_contribution.svg` | 5,632 | 1200x675 | `d617be5e1772d1238178982a4e58c0e554917b13cd1bd33468b866474614b575` |
| `outputs/figures/08_ensemble_size.png` | 14,625 | 1200x675 | `60f2a16a30aeaccd1152a06fe049ba30b9c7c18fe5b14901ba84d3819872f23a` |
| `outputs/figures/08_ensemble_size.svg` | 9,251 | 1200x675 | `fcbae1f29311d9c3074b7deb2107d7906902d0129df5d41b4eec50df6e982798` |
| `outputs/figures/09_failure_examples.png` | 11,194 | 1200x675 | `22b74fc1c500f421b8f270ed0fccfbc52c4fa8638aab0b72a5b02fd21eebf00f` |
| `outputs/figures/09_failure_examples.svg` | 4,005 | 1200x675 | `e7a0687d203010419600105ccccb4443f693b51f07372ae7e64a9f426b1148bb` |

Byte sizes/hashes for `04_cost_review_frontier.png/.svg` changed from the prior receipt because of the C4 row-label-overlap fix described below; all other 16 files (including `03_precision_coverage.png/.svg`, whose bytes/hashes had changed in the prior heading-layout pass and are unchanged by this pass) are identical to the prior receipt. Confirmed via an independent temporary rerun into a fresh `mktemp -d` directory: all 18 files in that rerun are byte-identical (`cmp -s`) to the corresponding files in `outputs/figures/`.

## Verification and portability notes

`tests/test_chart_generation.py` uses `unittest` and only standard-library modules. It verifies required table existence, all exact basenames and formats, nonempty SVG metadata/vector marks, PNG signature/IHDR/1,200 x 675 dimensions/nontrivial bytes, two byte-identical temporary reruns, equality to the checked working-tree outputs, and absence of absolute paths, URLs, or credential tokens in SVG metadata. A targeted run of this module after the C4 row-label-overlap fix completed with `Ran 6 tests in 3.119s` and `OK`.

`python3 -m compileall -q scripts tests` completed with no output (all `.py` files under both directories compile cleanly).

Full-repository `python3 -m unittest discover -s tests` currently reports `Ran 16 tests in 2.360s` with 6 import errors (`ModuleNotFoundError: No module named 'icdar_tta'`) because `src/icdar_tta` is a `src`-layout package (`pyproject.toml`, `[tool.setuptools.packages.find] where = ["src"]`) that is not installed or on `PYTHONPATH` in this environment; this affects `tests/test_metrics_agreement.py`, `tests/test_normalize.py`, `tests/test_schema_and_parser.py`, `tests/test_validate_cli.py`, `tests/test_consensus_alignment.py`, and `tests/test_lineage_manifest.py`, none of which are chart-generation files. This is a pre-existing environment condition unrelated to the chart task and outside the files owned by this receipt. Running the identical discovery with `PYTHONPATH=src` set (no file changes) passes fully: `Ran 158 tests in 2.375s`, `OK`, confirming the full suite is correct given a normal editable/installed environment. `tests/test_chart_generation.py` itself has no `icdar_tta` dependency and passes under both invocations.

An explicit temporary rerun (`python3 scripts/generate_charts.py --derived-dir outputs/derived --figure-dir <mktemp -d>`) followed by `cmp -s` against every one of the 18 files in `outputs/figures/` showed 18/18 byte-identical, 0 mismatches. The temporary directory was removed after comparison.

All paths in this receipt and chart metadata are repository-relative. C4, C6, and C9 are truthful blocked/partial evidence artifacts; their existence does not resolve the missing usage/pricing, modern inference, canonical denominator, or release-authorization blockers.

## Visual inspection (post C4 row-label-overlap fix)

All nine PNGs were rendered and visually inspected directly (not inferred from code):

- C1–C3, C5, C7–C9: headings, subtitles, axis labels, legends, and side panels render without clipping or overlap.
- C4 (`04_cost_review_frontier`): **fixed**. The prior pass's per-row strategy label (e.g. "GRID WARP (N=...") was drawn at x=90 immediately left of a bar container starting at x=250, and the label bled behind the bar rectangle. `chart_4` in `scripts/generate_charts.py` now places the strategy label ("GRID WARP (N=20)") on its own text line above the bar, at the container's full left margin (x=90), and widens the bar/track to span the full container width (x=90 to x=670) instead of starting at x=250. The label no longer shares a horizontal row with the bar it describes, so it cannot run behind the bar container regardless of strategy-name or n-sample length; the coverage/precision caption line and the two blocked-row panels (Pad, Resize) below are unaffected and still render without overlap. Verified visually in the regenerated PNG: the label sits cleanly above the fully visible blue/gray bar with no clipping.
- C6 (`06_cross_model_coverage`): the single measured cell (Gemini-2.0-Flash / Grid Warp) renders as a green dot with "40.4%" and "P=95.23%" beneath it, clearly distinguished from the red BLOCKED cells; no overlap observed.
- No SVG/PNG shows placeholder text, invented numbers, or unlabeled provider data.
