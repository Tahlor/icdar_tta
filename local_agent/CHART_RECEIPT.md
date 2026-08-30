# Modern chart update addendum — 2026-08-30

The chart set has been regenerated from the completed modern analysis. All 18
required stable basenames (C1–C9, SVG and PNG) exist under `outputs/figures/`.
The modern rows are included in C1, C2, C3, C4, C6, and C8; C5, C7, and C9
retain their historical/blocked semantics where the modern screen does not
provide a corresponding shift or release-safe failure-example artifact.

The modern source-table snapshots used for this regeneration are:

| Table | Rows | SHA-256 |
|---|---:|---|
| `strategy_summary.csv` | 43 | `3b91626ffd22e05bcd215b8d76377b416433a356710b4a8aeccc364cde6c5798` |
| `precision_coverage.csv` | 2,499 | `1a6f8a21d2f7b51ebb03b38cf86fc22ee6f4ea07fbcb7b2bd7db03c06ee8dbc9` |
| `error_correlation_summary.csv` | 22 | `b85036eb073f98c21cb43ec2b941829665a63808207313888b82ee968cb92255` |
| `cost_by_run.csv` | 5 | `6fd9c434cb75ccf946f779c5d20e82677f1b778139d860b47d8346078d1cafb5` |
| `cross_model_operating_points.csv` | 18 | `e460f75784d305ff9aeeea311e3921d295054927a221bfead9eb7aef01080f48` |
| `ensemble_size.csv` | 65 | `6a8c25f610abd99bfe80a71a811287f8940446f659f8e2beb3459568d1e0c673` |

The exact command remains `python3 scripts/generate_charts.py
--derived-dir outputs/derived --figure-dir outputs/figures`. This is an
offline deterministic rendering step; raw images and response bodies are not
required. The full modern execution receipt and request accounting are in
`local_agent/MODERN_FULL_RECEIPT.md`.

# Historical C1-C9 chart receipt (preserved pre-modern snapshot)

## GT-lineage addendum — 2026-08-30

The chart source tables in this receipt are legacy/public v7 products. C3 uses
the v7 3,682-row reliability tables, and C8 uses the approximately 4,920-row
historical WARP aggregate; neither is a paper-v9/v10 3,684-row recomputation.
The six-field selector and 24-record historical exclusion are now recovered,
but the v9/v10 3,684-row artifacts retain one blank row. The precise lineage
and reporting rule are in [`docs/GT_LINEAGE.md`](../docs/GT_LINEAGE.md).

Historical snapshot status: **all 18 required files rendered offline; evidence limitations are shown rather than filled with unsupported values**. Receipt regenerated 2026-08-29 (16:59 local) after fixing the C4 row-label overlap identified in the prior visual QA pass in `scripts/generate_charts.py`, from repository HEAD `cebf7778cea92692da9837f8914ae0b61a29c399` and the working-tree inputs listed below. The modern execution-resolution addendum above supersedes its pre-modern “no provider” and blocked-modern-cell descriptions.

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
| C1 `01_useful_diversity` | `strategy_summary.csv` | Rendered historical and modern measured coordinates with source labels. Selected v7 category rows remain visibly separated as consensus-only; they have no correlation coordinate and are not called individual CER. |
| C2 `02_effective_sample_size` | `error_correlation_summary.csv` | Rendered the theoretical N=10 curve plus 20 measured historical/modern correlations. Family-level historical Grid Warp and Resize correlations remain visibly blocked; prose values were not promoted. |
| C3 `03_precision_coverage` | `precision_coverage.csv` | Rendered all 2,499 raw-agreement threshold rows: 1,750 legacy/public-v7 rows plus 749 modern rows. Historical and modern denominator statuses remain explicit; the score is labeled raw/not calibrated. |
| C4 `04_cost_review_frontier` | `cost_by_run.csv`; `review_frontier.csv` | Rendered the numeric review-burden coordinate. The five cost rows include measured modern usage but no pricing, so the cost axis and Pad/Resize target coordinates remain visibly blocked. No dollars were invented. |
| C5 `05_shift_periodicity` | `shift_agreement.csv` | Rendered all 130 reported horizontal/vertical points and 16-pixel guides. Periodicity is labeled observational, not architecture proof. |
| C6 `06_cross_model_coverage` | `cross_model_operating_points.csv` | Rendered one measured historical Grid Warp point, one historical Pad target-not-met row, eight measured modern target-not-met rows, and eight explicit route-blocked rows for 3.7/Qwen. Empty modern coverage is a measured failure to reach the target, not a fabricated zero. |
| C7 `07_augmentation_contribution` | `augmentation_contribution.csv` | Rendered all five family selection counts and source descriptors. Selection frequency is explicitly descriptive, not causal contribution. |
| C8 `08_ensemble_size` | `ensemble_size.csv` | Rendered 53 historical source-reported rows plus 12 modern measured strategy points. The approximately 4,920-field source aggregate is labeled historical WARP lineage; modern points use the raw 3,718-cell denominator and are not the paper-v9/v10 3,684-row population. |
| C9 `09_failure_examples` | `failure_examples.csv` | Rendered a blocked evidence panel from three count-only rows. No prediction, ground truth, crop, or private path was copied; stable redacted lineage and crop authorization remain unavailable. |

Each SVG contains a machine-readable `<metadata>` object with chart ID, 1,200 x 675 dimensions, numeric input filenames, renderer, one-sentence takeaway, and limitations. The same takeaway is visible as a subtitle. Measured, theoretical, reported, recomputed, and blocked roles are distinguished in chart text and styling.

## Source CSV provenance

Rows exclude the header.

| Source table | Rows | Bytes | SHA-256 |
|---|---:|---:|---|
| `outputs/derived/augmentation_contribution.csv` | 5 | 2,427 | `6d6e2c4be232d77e94ee31560bbc327c04e9596721a79e34c456e78b6f1ceab6` |
| `outputs/derived/cost_by_run.csv` | 5 | 1,615 | `6fd9c434cb75ccf946f779c5d20e82677f1b778139d860b47d8346078d1cafb5` |
| `outputs/derived/cross_model_operating_points.csv` | 18 | 6,350 | `e460f75784d305ff9aeeea311e3921d295054927a221bfead9eb7aef01080f48` |
| `outputs/derived/ensemble_size.csv` | 65 | 33,507 | `6a8c25f610abd99bfe80a71a811287f8940446f659f8e2beb3459568d1e0c673` |
| `outputs/derived/error_correlation_summary.csv` | 22 | 9,850 | `b85036eb073f98c21cb43ec2b941829665a63808207313888b82ee968cb92255` |
| `outputs/derived/failure_examples.csv` | 3 | 1,464 | `30f027e10639a469db528f87db33f6d3ea91d2deba59e1e650ee82ea28938aec` |
| `outputs/derived/precision_coverage.csv` | 2,499 | 1,452,340 | `1a6f8a21d2f7b51ebb03b38cf86fc22ee6f4ea07fbcb7b2bd7db03c06ee8dbc9` |
| `outputs/derived/review_frontier.csv` | 3 | 1,667 | `3192b4c711a30e15ffb3febd8c6cd8f3c0ecf203ba5c61456787157c7c03f4de` |
| `outputs/derived/shift_agreement.csv` | 130 | 54,974 | `3e18fa536faf11992ae55ed8b5901f5a0d4c6b7ac1e394f07851d86158e77e96` |
| `outputs/derived/strategy_summary.csv` | 43 | 23,292 | `3b91626ffd22e05bcd215b8d76377b416433a356710b4a8aeccc364cde6c5798` |

## Output provenance

| Output | Bytes | Dimensions | SHA-256 |
|---|---:|---:|---|
| `outputs/figures/01_useful_diversity.png` | 16,249 | 1200x675 | `e60ceb390392196a6280fefa33b0bb21908127913bb1f396f7628e36f1b6c47f` |
| `outputs/figures/01_useful_diversity.svg` | 10,068 | 1200x675 | `3a9cb70cb234f704fbf42ba661b83407f7c3cd6ec8f0f1267b9ddd7fb2b07e48` |
| `outputs/figures/02_effective_sample_size.png` | 14,604 | 1200x675 | `8e74c225364f66d3ae8a0f92ad840e08e56cf3307b6dffa4cb123a85b41cadcd` |
| `outputs/figures/02_effective_sample_size.svg` | 10,140 | 1200x675 | `75b066c931b400b65976f56fbb523e8f14e5bf9db6903da407479720d7e6aa29` |
| `outputs/figures/03_precision_coverage.png` | 17,801 | 1200x675 | `845e9c951e2eedc09414b8667f3d4318dfb8b105c7fe686ef65b4c874bff4068` |
| `outputs/figures/03_precision_coverage.svg` | 127,676 | 1200x675 | `da650840315f45d0567859abcd7134f662f2642041a62c6eeb4c05cd057cb5b1` |
| `outputs/figures/04_cost_review_frontier.png` | 12,999 | 1200x675 | `aa0b2721ea4f38b122fabeda5a5a9ce6b4abddd9ddfbc974a8cbd87fba5b3fc3` |
| `outputs/figures/04_cost_review_frontier.svg` | 6,259 | 1200x675 | `b701c90f46391d38c4f88f615cd3f23cb417f47f988646fa598b96be22efb67d` |
| `outputs/figures/05_shift_periodicity.png` | 16,359 | 1200x675 | `50d12e231c7665364f401d71ef016ce7aaa659f15e4964616b4b91b074a17a48` |
| `outputs/figures/05_shift_periodicity.svg` | 11,912 | 1200x675 | `9a10c3507a7f890f5439302abb389274328de1a41ff62fd05aaed560a1e3d24b` |
| `outputs/figures/06_cross_model_coverage.png` | 10,744 | 1200x675 | `a4bd595aca4bc0a79230b454ec77615415e735f12db019ae7dd8678d57b677da` |
| `outputs/figures/06_cross_model_coverage.svg` | 9,152 | 1200x675 | `bfecbe6a7aefc4f3ba723689224677a1790cbcfeb5c98485bf191de099621665` |
| `outputs/figures/07_augmentation_contribution.png` | 9,639 | 1200x675 | `b2b5f644420a87e9ef7a71b4b7fb58be9fad7c964c69039f249e73a2fe7d29ab` |
| `outputs/figures/07_augmentation_contribution.svg` | 5,632 | 1200x675 | `d617be5e1772d1238178982a4e58c0e554917b13cd1bd33468b866474614b575` |
| `outputs/figures/08_ensemble_size.png` | 17,145 | 1200x675 | `5bf0cfbb1e3a1f950106acd00caf91fbd7dde906cb5a7518a6a84d7b264bc007` |
| `outputs/figures/08_ensemble_size.svg` | 12,151 | 1200x675 | `ff389bc07067323c3bdd4af64c2d575ef1aface0bbd8f82e36dec46f55287c86` |
| `outputs/figures/09_failure_examples.png` | 11,194 | 1200x675 | `22b74fc1c500f421b8f270ed0fccfbc52c4fa8638aab0b72a5b02fd21eebf00f` |
| `outputs/figures/09_failure_examples.svg` | 4,005 | 1200x675 | `e7a0687d203010419600105ccccb4443f693b51f07372ae7e64a9f426b1148bb` |

The table above is the current 2026-08-30 chart-set provenance after
regenerating from the merged historical-plus-modern derived tables. An
independent temporary rerun into a fresh directory confirmed that all 18
files are byte-identical (`cmp -s`) to the corresponding files in
`outputs/figures/`.

## Verification and portability notes

`tests/test_chart_generation.py` uses `unittest` and only standard-library modules. It verifies required table existence, all exact basenames and formats, nonempty SVG metadata/vector marks, PNG signature/IHDR/1,200 x 675 dimensions/nontrivial bytes, two byte-identical temporary reruns, equality to the checked working-tree outputs, and absence of absolute paths, URLs, or credential tokens in SVG metadata. A targeted run of this module after the C4 row-label-overlap fix completed with `Ran 6 tests in 3.119s` and `OK`.

`python3 -m compileall -q scripts tests` completed with no output (all `.py` files under both directories compile cleanly).

The complete suite was also rerun with `PYTHONPATH=src`: `Ran 210 tests` and
`OK`. `tests/test_chart_generation.py` passes independently and the chart
renderer remains standard-library-only. A bare discovery without the
`src`-layout path is not the supported invocation; use the documented
`PYTHONPATH=src` command.

An explicit temporary rerun (`python3 scripts/generate_charts.py --derived-dir outputs/derived --figure-dir <mktemp -d>`) followed by `cmp -s` against every one of the 18 files in `outputs/figures/` showed 18/18 byte-identical, 0 mismatches. The temporary directory was removed after comparison.

All paths in this receipt and chart metadata are repository-relative. C4 and
C9 remain partial/blocked because pricing and release-authorized qualitative
examples are unavailable. C6 contains measured modern target failures plus
explicit route blockers; it does not imply a modern 95% operating point. The
chart set does not resolve the separate paper-lineage recomputation or
historical exact-render limitations.

## Visual inspection (post C4 row-label-overlap fix)

All nine PNGs were rendered and visually inspected directly (not inferred from code):

- C1–C3, C5, C7–C9: headings, subtitles, axis labels, legends, and side panels render without clipping or overlap.
- C4 (`04_cost_review_frontier`): **fixed**. The prior pass's per-row strategy label (e.g. "GRID WARP (N=...") was drawn at x=90 immediately left of a bar container starting at x=250, and the label bled behind the bar rectangle. `chart_4` in `scripts/generate_charts.py` now places the strategy label ("GRID WARP (N=20)") on its own text line above the bar, at the container's full left margin (x=90), and widens the bar/track to span the full container width (x=90 to x=670) instead of starting at x=250. The label no longer shares a horizontal row with the bar it describes, so it cannot run behind the bar container regardless of strategy-name or n-sample length; the coverage/precision caption line and the two blocked-row panels (Pad, Resize) below are unaffected and still render without overlap. Verified visually in the regenerated PNG: the label sits cleanly above the fully visible blue/gray bar with no clipping.
- C6 (`06_cross_model_coverage`): the single numeric cell (Gemini-2.0-Flash / Grid Warp) renders as a green dot with "40.4%" and "P=95.23%" beneath it. Modern 3.5 rows render as red "TARGET NOT MET" cells, while the 3.7/Qwen rows render as red "ROUTE BLOCKED" cells; no overlap observed.
- No SVG/PNG shows placeholder text, invented numbers, or unlabeled provider data.
