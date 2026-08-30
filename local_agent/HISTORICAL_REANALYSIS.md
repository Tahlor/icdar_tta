# Historical Gemini 2.0 Flash re-analysis

## GT-lineage addendum — 2026-08-30

The tables in this report were generated from the legacy/public v7 evidence and
therefore intentionally remain 3,682-row products. The earlier wording that
the 3,684 filter was “unresolved” is superseded at the rule level: the six
metric fields and the historical 24-record `Self*` exclusion are recovered.
The paper/v9/v10 row target is `622 × 6 − 24 × 2 = 3,684`, but those artifacts
retain one blank row despite the configured `f_gt_missing: 0`. This report has
not silently converted its v7 tables to the paper-lineage population. See
[`docs/GT_LINEAGE.md`](../docs/GT_LINEAGE.md).

Status: **offline legacy-v7 products generated; paper-lineage recomputation and modern screen remain pending**. This report records only aggregate, portable evidence. No provider call, network request, inference run, external-root write, raw response copy, or private field-value copy was performed.

## Scope and evidence semantics

- `reported_historical_aggregate`: a numeric value already present in a machine-readable historical aggregate table, possibly joined to another aggregate by exact experiment ID.
- `recomputed_historical_noncanonical`: a statistic recomputed from a historical field-level aggregate without exporting predictions, labels, image paths, or record IDs.
- `recomputed_from_reported_cv_summary`: a family aggregation computed from the v7 CV-rank summary.
- `blocked_*`: the requested coordinate cannot be supported by available evidence; numeric result cells are left empty.
- No paper prose value is promoted to a measured row. In particular, v7 Grid Warp/Resize correlation rows are blocked because the inspected machine-readable v7 table does not encode those correlations.

The six edited name columns in the fixed-v2 source contain **3,718 raw
nonblank cells** (Self given 609, Self surname 622, Father given 622, Father
surname 622, Mother given 622, Mother surname 621). That raw count is not the
paper row population. The legacy/public v7 reliability tables contain 3,682
rows; the newer paper-lineage v9/v10 tables contain the separate 3,684-row
population described in `docs/GT_LINEAGE.md`.

## Source inventory

Paths below are logical paths relative to the two explicitly supplied evidence roots. `rows` excludes the header.

| Logical source | Bytes | Rows | SHA-256 |
|---|---:|---:|---|
| `PA_DEATH/WARP/PA_DEATH_WARP.yaml` | 54,848 | n/a; 14 active experiment declarations | `bb5b5a8fe53381f3139a413d148d8aa5bd74ebde51a4854d91679007ed95164c` |
| `PA_DEATH/WARP/metrics_no_punc/ensemble_selection_analysis.tsv` | 2,407 | 10 | `3224861466c073bb8c21e5944268a910f437a178c76a335260389dc0f19eea39` |
| `PA_DEATH/WARP/metrics_no_punc/experiment_level_consensus_summary_by_k.tsv` | 10,654 | 53 | `ff5a00eaa22390f0a0abf4b0ee23479aae21dfa35d06b2896cf1fb894104c565` |
| `PA_DEATH/WARP/metrics_no_punc/weighted_cer_by_experiment.tsv` | 1,204 | 14 | `ddd370b91ae47dd081e30f34c2b494b64449d3f0d07e9bc95dd913dbaf8a3e0a` |
| `PA_DEATH/WARP/5164_gts.csv` | 142,892 | 622; 18 columns | `cf24e896875280560023f6c8976ca6ab32de5d0bc8426c59c00b4d58b235810d` |
| `PA_DEATH/SHIFT/metrics_no_punc/run_settings.csv` | 19,093 | 3; 53 columns | `b2a145aad1d2d394217b3f1e8a6625161b9a0f279705d672a7136654b28a06e8` |
| `PA_DEATH/SHIFT/metrics_no_punc/weighted_cer_by_experiment.tsv` | 305 | 3 | `9aa5f5b5ce5046ce325cda9b10a11dfe0ddceb36126f3e3c321526eb6340e686` |
| `PA_DEATH/SHIFT/5164_gts.csv` | 159,892 | 622; 20 columns | `14219f17eeaaf45ffa4cec49f624de1edb3a739b40a87f0f838355a7fa414ccd` |
| `PA_DEATH/CVPR_ANALYSIS/small_shift_horizontal_signal_data.csv` | 1,655 | 65 | `e5e33c9a1b15f4eac26160d4b753f30eaa28a378a1330da74441073d8f6fc7b2` |
| `PA_DEATH/CVPR_ANALYSIS/small_shift_vertical_signal_data.csv` | 1,647 | 65 | `17ec7d9a8981693efce9b35f6982636ff01231c9082c8aae1dfbbf92d1f532ad` |
| `PA_DEATH/CVPR_ANALYSIS/small_shift_horizontal_fft_peaks.csv` | 221 | 5 | `5eab02ab9e9bbc7f120b469a65fa54e0fc1d3fecac7321c3fe8412e530f1f21a` |
| `PA_DEATH/CVPR_ANALYSIS/small_shift_vertical_fft_peaks.csv` | 240 | 5 | `360bc2a79d04718f216735cc6e0379e93dc50aa8034bb6142e3abe6a05d794e6` |
| `chat2rec_analysis/analysis - v7/paper/transform_metrics_table.csv` | 1,100 | 11 | `1661070745d508cb396479a88239ae2905beb1b3920f6fd763309baadb28d5ce` |
| `chat2rec_analysis/analysis - v7/paper/ensemble_methods_table.csv` | 467 | 4 | `3ce70dee90528da02f9c3fe541f01bc14dd36600b3aba45bca8343a32e270100` |
| `chat2rec_analysis/analysis - v7/best_consensus_CER/cv_rank_metrics_summary.tsv` | 13,381 | 55 | `e4502daed441dd29608684b905289a72bfe683ca93bafb8762f626f2e34c8315` |
| `chat2rec_analysis/analysis - v7/outputs/consensus_reliability_analysis/consensus_gw_data.csv` | 1,438,281 | 3,682 | `eaee8bb37329e5e5c32177bbe5287ce0a884148d5819e60bc2c38d44deb0d623` |
| `chat2rec_analysis/analysis - v7/outputs/consensus_reliability_analysis/consensus_shift_data.csv` | 1,334,405 | 3,682 | `e562e96ed5dede565e0f88746be37367ae9c21e0dde84fc9f18a394182bf804f` |
| `chat2rec_analysis/analysis - v7/outputs/consensus_reliability_analysis/consensus_resize_data.csv` | 1,334,492 | 3,682 | `e494e0c27070908185754afacddaa05ab6f1c47a29c96f3cd8b2134564179f2d` |

CSV/TSV parsing is header-aware and quote-aware. The SHIFT configuration dictionaries are parsed with `ast.literal_eval`, not `eval`. Their exact variant counts agree with `num_samples`: diagonal 20, horizontal 33, vertical 32. The corresponding sweep-level weighted CER values are 0.09329832717612387, 0.09350656538403, and 0.0931695495848084. These are not per-offset CER values. Both fine-shift FFT peak tables rank period 16 px first; the agreement inputs contain 65 symmetric points per direction from relative shift -64 through +64 in 2-pixel increments.

Raw historical JSON was not needed because the available aggregate and v7 consensus tables contain every scalar used here; opening/copying raw responses would add private content without improving these products. Pickles were not used because equivalent CSV/TSV products exist and unpickling untrusted historical files can execute code. No claimed metric depends on a pickle-only field.

## Computations

1. **Useful diversity and error correlation.** WARP rows join exact `experiment_name` values between the 10-row ranking table and the maximum available `k` in the 53-row by-k table. `individual_cer` is ranking-table `avg_cer`; `consensus_cer` is by-k `weighted_CER`. Category-level v7 consensus CER is stored only in `consensus_cer`, never `individual_cer`. The stylized quantity is `N_eff = N / (1 + (N - 1) * rho)` and is explicitly not a measured sample count.
2. **Precision/coverage.** For each of Grid Warp, Pad, and Resize, the legacy/public v7 source has 3,682 20-member consensus rows. At every distinct `consensus_confidence` threshold `t`, accept when `confidence >= t`; correctness is source `cer == 0`; `coverage = accepted / 3682`; `precision = accepted_correct / accepted`; `review = 3682 - accepted`. Intervals are two-sided 95% Wilson score intervals. The score is labeled raw character agreement, not calibrated probability. These are not v9/v10 3,684-row metrics.
3. **Descriptive operating point.** The offline table uses a clearly labeled descriptive target of 0.95 and chooses maximum empirical coverage among thresholds meeting it. Grid Warp reaches 0.95225285810356419 precision at threshold 0.96666666666666679, accepting 1,487/3,682 fields (coverage 0.40385659967409016). Pad has no empirical threshold meeting 0.95, so its row is an explicit negative result with no fabricated coordinates. This target is not presented as the frozen modern-test target.
4. **Shift series.** The horizontal and vertical aggregate series are copied with direction, signed/absolute displacement, and a computed multiple-of-16 flag. The evidence is observational and does not prove model architecture.
5. **Contribution.** The 55 CV-rank rows are grouped by transform family; `selection_count` sums source `frequency`, and `mean_mrr` averages source `MRR`. This is descriptive selection frequency, not a causal leave-one-family-out result.
6. **Ensemble size.** The 53 by-k rows preserve source weighted CER, field accuracy, confidence, evaluated-record count, and sample-record count for baseline, Pad, and ranked WARP variants.

## Generated tables

| Output | Rows | Bytes | SHA-256 | Status |
|---|---:|---:|---|---|
| `outputs/derived/strategy_summary.csv` | 31 | 15,951 | `815c0d66b688f75cb736fe7765979dc14ad67ab370407e1804ff12981977f9c7` | reported aggregates; denominator explicit |
| `outputs/derived/error_correlation_summary.csv` | 12 | 5,368 | `93157ddd6c16b8f928df5f32cc6b29d353b0cea2b921c71d8a158473d90b985b` | 10 WARP rows plus 2 blocked v7 family rows |
| `outputs/derived/precision_coverage.csv` | 1,750 | 998,692 | `619210cd328762df6b87b8195f18d506bf61dcfa236c44e27c207b31d83bd53a` | recomputed on legacy/public v7 3,682-row sources |
| `outputs/derived/cost_by_run.csv` | 4 | 911 | `bad4ed762ddf9761a6ea3b57171f26e3a8086c225d3672e4c023837fba17e665` | blocked: no observed historical usage; no modern runs |
| `outputs/derived/review_frontier.csv` | 3 | 1,667 | `3192b4c711a30e15ffb3febd8c6cd8f3c0ecf203ba5c61456787157c7c03f4de` | review burden partial; cost axis blocked |
| `outputs/derived/shift_agreement.csv` | 130 | 54,974 | `3e18fa536faf11992ae55ed8b5901f5a0d4c6b7ac1e394f07851d86158e77e96` | reported aggregate series |
| `outputs/derived/cross_model_operating_points.csv` | 14 | 5,145 | `ee1c9f00ccfa5014ab34c69a1a4c07d2870277f513ee9a5a4e1a5f79b7b4b438` | 2 historical rows; 12 modern blocked rows |
| `outputs/derived/augmentation_contribution.csv` | 5 | 2,427 | `6d6e2c4be232d77e94ee31560bbc327c04e9596721a79e34c456e78b6f1ceab6` | recomputed family selection frequency |
| `outputs/derived/ensemble_size.csv` | 53 | 24,457 | `3deecacbf92eb76b17521adbef3e3294cbb4fe49dd96a68f02abd3d09b79d0cf` | reported by-k aggregates |
| `outputs/derived/failure_examples.csv` | 1 | 495 | `c4ecf82d3d5e5c0f909d0992cd2b3a3acaf0e3b2d87130b49c22541618b54b55` | blocked: no release-authorized crop lineage |

## Blockers and nonclaims

- **Paper-lineage evaluation:** the six-field selector and 24-record historical exclusion are recovered, but this report's tables remain legacy/public v7 at 3,682 rows. The v9/v10 emitted 3,684-row population retains one blank row, so a dedicated paper-lineage recomputation still needs to freeze its strict-nonblank reporting convention. All existing table rows carry `denominator_status`.
- **Modern transfer:** exact IDs are recorded for `gemini-3.7-flash`, `gemini-3.5-flash-lite`, and `sagemaker-qwen3-vl-8b-instruct-fp8`, but no modern scored responses exist. The exact 622-image/hash manifest, paper-lineage row convention, shared parser hash, source/mask/render lineage, route smoke, and explicit live-call authorization remain closed gates.
- **Cost:** run settings do not provide observed token/usage/billing records or a pricing snapshot. No dollar estimate is invented.
- **Qualitative examples:** no stable redacted high-agreement-wrong IDs with authorized crop references were found. Predictions, labels, image paths, and crops are left empty.
- **Correlation cross-check:** the v7 transform table contains family CER and field accuracy but not family error correlation. Prose regression targets remain targets, not measured output rows.

## Reproduction

Set the two local roots without committing their values, then run:

```bash
python3 scripts/recompute_historical.py \
  --pa-root "$PA_ROOT" \
  --analysis-root "$ANALYSIS_ROOT" \
  --output-dir outputs/derived \
  --local-manifest config/data_manifest.local.yaml
python3 -m compileall -q scripts src tests
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m icdar_tta.validate
```

Omit `--local-manifest` to guarantee the CLI writes only beneath `--output-dir`. The local manifest is ignored and is the only permitted output outside that directory.
