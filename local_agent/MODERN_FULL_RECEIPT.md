# Modern two-model transfer-screen receipt

Date: 2026-08-30 America/Denver
Run ID: `modern_screen_v1`
Status: **complete for the two executable Gemini models; requested 3.7 and Qwen routes remain model-specific blockers**

## Scope and provenance

The frozen PA cohort contains 622 documents and nine predeclared views per
document: three unchanged repeats, three Pad/offset views, and three mild Grid
Warp views. No new Gemini 2.0 Flash calls were made. Modern transforms and the
95% accepted-field precision target were frozen before the label-based
analysis.

| Item | Value |
|---|---|
| Executed model IDs | `gemini-3.5-flash`, `gemini-3.5-flash-lite` |
| Per-model terminal rows | 5,598 = 622 × 9 |
| Total terminal rows | 11,196 |
| Render manifest rows | 5,598; SHA-256 `ED3C80E0554B670C17FF649C99C318E807E74B9D7C6267BC2E570A2D267DC301` |
| Prompt SHA-256 | `fd119108d3ef4dbf2f88984511d9f903b7d4c98b032a95c327a21f713335e48e` |
| Schema SHA-256 | `9bfcb9bf8ba73ee6d73a827bf7ec6de6907589e4832601104081c75781019585` |
| Parser | `pa_v149_json_repair_v0` |
| Transport | `gemini_l1_native_inline_jpeg95_minimal4096_v2` |
| Evaluated field population | 3,718 raw six-name nonblank fields; historical 3,684 exclusion rule not applied by this modern analyzer |

Private source images, raw response bodies, and field-level output remain
outside Git. The committed tables refer to the external response artifact by
logical name and SHA-256 only.

Project-manager live-call authorization was recorded at
`2026-08-30T09:46:56.518223+00:00` for the two-model executable scope. The
final request accounting is the append-only ledger chain described below;
the authorization record itself remains in ignored runtime state.

## Request accounting

The append-only ledger chain records 11,307 `submitted` events. A separate
early direct route probe was not written to that ledger, so the conservative
provider-boundary total is 11,308, leaving 8,692 attempts under the 20,000
hard cap. The 11,307 ledger events include retries, capacity failures, route
repairs, and the 13-call Qwen warmup attempt; they are not all unique scored
cells.

The two executed model totals are 5,649 submitted events for Flash and 5,642
for Flash-Lite. Terminal result rows are exactly 5,598 per model. All derived
ensembles use those rows and add zero provider calls.

## Model-specific route outcome

- `gemini-3.5-flash`: executed as the available modern Flash substitute after
  the requested 3.7 PA route returned HTTP 403. All 5,598 views completed.
- `gemini-3.5-flash-lite`: executed as requested. All 5,598 views completed.
- `gemini-3.7-flash`: PA route probe returned HTTP 403; no full screen was
  attempted.
- `gemini-3.6-flash`: an available Vermont-era alternative also returned HTTP
  403 on the PA probe; it was not substituted after the working 3.5 route was
  established.
- `sagemaker-qwen3-vl-8b-instruct-fp8`: Vermont L3 warmup/route attempts
  returned HTTP 500 endpoint-not-found responses. No PA scored Qwen matrix was
  claimed.

The successful Gemini continuation used the native L1 route with the stable
ledger key-environment label `AI_GATEWAY_KEY_PROD`; process-local route repairs
used only redacted environment aliases. No credential value is recorded.

## Response quality and consensus

Values below are exact field accuracy and character error rate over the raw
3,718-field modern denominator. Agreement is a raw consistency score, not a
calibrated probability.

| Model | Strategy | Samples | Individual accuracy | Consensus accuracy | Individual CER | Consensus CER | Mean error correlation |
|---|---|---:|---:|---:|---:|---:|---:|
| Flash | single | 1 | 0.8335 | 0.8335 | 0.0537 | 0.0537 | — |
| Flash | unchanged_3 | 3 | 0.8341 | 0.8346 | 0.0532 | 0.0527 | 0.9806 |
| Flash | Pad | 3 | 0.8372 | 0.8405 | 0.0529 | 0.0500 | 0.8461 |
| Flash | Grid Warp | 3 | 0.8316 | 0.8370 | 0.0545 | 0.0519 | 0.8633 |
| Flash | visual_mixed_6 | 6 | 0.8344 | 0.8421 | 0.0537 | 0.0496 | 0.8426 |
| Flash | all_views_9 | 9 | 0.8343 | 0.8408 | 0.0535 | 0.0497 | 0.8697 |
| Flash-Lite | single | 1 | 0.7856 | 0.7856 | 0.0750 | 0.0750 | — |
| Flash-Lite | unchanged_3 | 3 | 0.7829 | 0.7948 | 0.0782 | 0.0693 | 0.8088 |
| Flash-Lite | Pad | 3 | 0.7835 | 0.8082 | 0.0798 | 0.0645 | 0.7159 |
| Flash-Lite | Grid Warp | 3 | 0.7734 | 0.7964 | 0.0868 | 0.0697 | 0.7434 |
| Flash-Lite | visual_mixed_6 | 6 | 0.7785 | 0.8096 | 0.0833 | 0.0642 | 0.7212 |
| Flash-Lite | all_views_9 | 9 | 0.7800 | 0.8098 | 0.0816 | 0.0632 | 0.7415 |

Interpretation: both models show lower error correlation for visual variants
than unchanged repetition, and both improve consensus CER over the single
view. Pad is the strongest individual tested family on consensus accuracy for
both models; Grid Warp remains beneficial but is not the best individual family
under this screen. The modern data therefore support useful visual diversity,
but not a universal claim that Grid Warp is the top accuracy transform.

## Accepted-field precision target

The predeclared target was 95% accepted-field precision. No modern strategy
reached that target at an observed raw-agreement threshold, so the operating
point table intentionally contains no fabricated modern acceptance coordinate.
The maximum observed precision was approximately 91.5% for Flash all-views and
93.4% for Flash-Lite all-views. This means the screen does not yet justify a
95%-precision automatic-acceptance claim; it does not mean that agreement is
useless or that a calibrated follow-up could not improve the operating point.

## Parse and raw-evidence accounting

- Flash: 5,598 normalized rows; 5,597 field-bearing after strict projection;
  410 parse-failure bodies recovered in memory; 1 remained unrecovered.
- Flash-Lite: 5,598 normalized rows; 5,574 field-bearing after strict
  projection; 302 parse-failure bodies recovered in memory; 24 remained
  unrecovered.
- The analyzer hashed 11,196 terminal raw response files and matched every
  normalized row to a rendered-view lineage row and a terminal ledger event.

## Reproducibility and cleanup checks

| Check | Result |
|---|---|
| Modern analyzer | PASS; full lineage, fingerprint, raw-file, and ledger reconciliation |
| Analyzer rerun | PASS; zero changed derived CSV or field-level hashes |
| Chart generation | PASS; all nine required basenames in SVG and PNG (18 files) |
| Repository tests | PASS; 210 tests, 0 failures |
| Python compilation | PASS; 18 files |
| Local manifest validator | PASS; 0 hard failures |
| Temporary EC2 instance `cp` | Stopped and verified stopped |

Primary artifacts are `outputs/derived/*.csv`, `outputs/figures/`,
`local_agent/request_budget.json`, and this receipt. The timed presentation
should use the modern result as a mixed replication slide/backup: quality and
diversity effects transfer to both executable Gemini 3.5 models, while the 95%
accepted-field target and requested 3.7/Qwen full-screen claims remain
unsupported.
