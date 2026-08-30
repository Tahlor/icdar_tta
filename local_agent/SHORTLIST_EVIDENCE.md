# Historical transform shortlist evidence

Status: frozen pre-call evidence record. No new inference was run. Evidence paths are portable logical paths, not workstation paths.

## Sources and implementation wiring

- Active config: `PA_DEATH/WARP/PA_DEATH_WARP.yaml`, SHA-256 `bb5b5a8fe53381f3139a413d148d8aa5bd74ebde51a4854d91679007ed95164c`.
- Ranking table: `PA_DEATH/WARP/metrics_no_punc/ensemble_selection_analysis.tsv` (10 rows).
- Shift evidence: `PA_DEATH/SHIFT/metrics_no_punc/run_settings.csv` and adjacent summary tables/raw experiment directories.
- Paper cross-check: `chat2rec_analysis/.../analysis - v7/paper/transform_metrics_table.tex` and `best_consensus_CER/cv_rank_metrics_summary.tsv`.
- Registry: `chat2rec_v1/chat2rec/degradations/pipeline.py`, SHA-256 `74a1860489bbb42baf0a5e18ace5cea904c8c1445fc4b47c8ba740a40f36483c`, maps `handwriting_kernel_warp` to `HandwritingKernelWarpDegradation` and `shift`/`deterministic_shift` to their implementations.
- Warp implementation: `.../effects/handwriting_kernel_warp.py`, SHA-256 `089dd75ba3b203a18dd347d08885851215fe64f842e9c1c52da5cddff39bbfc8`. It scales parameters against default `target_scale=1200`, uses pixel-based kernels unless `full_image_mode=true`, samples displacement magnitude from `Normal(0, noise_std)` clipped to `warp_strength`, and applies channel include/exclude masks.
- Shift implementation inspected: `.../effects/shift.py`, SHA-256 `ffd94284ff4c302c51852b03b425c7794079a138882e17a4ac10353b092781d5`. Historical WARP uses a separately registered `granular_shift` pipeline effect; its exact implementation was not in the four requested effect files, so Pad rendering remains a lineage gate.

## Every active WARP variant

All variants use dataset `pa_death_records622`, temperature 0, candidate count 1, common resize `{"resize_mode":"max_dimension","max_dimension":1504}`. `baseline` has 3 samples; every other active variant has 5. Warp rows use `type=handwriting_kernel_warp` followed historically by the five `shift_only` granular-pad variants.

Shared warp dictionary: `{"prob":1.0,"point_density":0.003,"base_radius":30.0,"boundary_safety":1.0,"min_radius":5.0,"warp_strength":10.0,"falloff_type":"gaussian","region_based":true,"region_margin":20,"min_influence":0.01,"min_region_area":100,"dilate_radius":3,"min_component_size":50,"mask_suffix":".tif","visualize":false,"random_state":null}`. Omitted implementation defaults include `target_scale=1200`, `auto_scale_params=true`, and `full_image_mode=false`.

| Active experiment_name | Exact differentiating params | Ranking-table row |
|---|---|---|
| `baseline` | Pad `[16,16,16,16]`; no warp | absent |
| `shift_only` | five pads listed below; no warp | present |
| `dont_warp_text_and_lines_d003_r30_s10_std2` | `noise_std=2.0`, `do_not_warp_channels=[0,1]` | present |
| `warp_hw_only_dont_warp_text_and_lines_d003_r30_s10_std2` | `noise_std=2.0`, `do_warp_channels=[2]`, `do_not_warp_channels=[0,1]` | present |
| `warp_all_d003_r30_s10_std2` | `noise_std=2.0`, no channel lists | present |
| `warp_all_d003_r30_s10_std15` | `noise_std=1.5`, no channel lists | present |
| `dont_warp_text_and_lines_d003_r30_s10_std15` | `noise_std=1.5`, `do_not_warp_channels=[0,1]` | present |
| `warp_hw_only_dont_warp_text_and_lines_d003_r30_s10_std15` | `noise_std=1.5`, `do_warp_channels=[2]`, `do_not_warp_channels=[0,1]` | present |
| `warp_all_d003_r30_s10_std3` | `noise_std=3.0`, no channel lists | present |
| `dont_warp_text_and_lines_d003_r30_s10_std3` | `noise_std=3.0`, `do_not_warp_channels=[0,1]` | present |
| `warp_hw_only_dont_warp_text_and_lines_d003_r30_s10_std3` | `noise_std=3.0`, `do_warp_channels=[2]`, `do_not_warp_channels=[0,1]` | present |
| `warp_hw_d003_r30_s10_std2` | `noise_std=2.0`, `do_warp_channels=[2]` | absent |
| `warp_hw_d003_r30_s10_std15` | `noise_std=1.5`, `do_warp_channels=[2]` | absent |
| `warp_hw_d003_r30_s10_std3` | `noise_std=3.0`, `do_warp_channels=[2]` | absent |

The suffixes mean exactly `std15 → noise_std 1.5`, `std2 → 2.0`, and `std3 → 3.0`. The 18 `r60`/`d005` experiment definitions are commented out at source lines 850–1879 and are not active-run evidence.

## Complete active grid ranking

All nine tabled grid rows have `baseline_cer=0.07983547969380106`, `sample_count=4920`, `ensemble_score_v1=v2=v3=0.0`, and `expected_ensemble_improvement=0.0`. Therefore v1–v3 and expected improvement do not rank these rows; no source statement establishes validation selection.

| ID (abbreviated only in this table) | avg CER (rank asc) | CER improvement (rank desc) | char error corr. (rank asc) | field error corr. (rank asc) | ensemble v4 (rank desc) | baseline error coverage |
|---|---:|---:|---:|---:|---:|---:|
| `dont...std15` | 0.08378498973594023 (1) | -0.0039495100421391705 (1) | 0.8424147402405657 (8) | 0.7483235853601342 (8) | 0.47780345508520516 (1) | 0.17278797996661102 |
| `warp_all...std15` | 0.08625353753133524 (3) | -0.006418057837534186 (3) | 0.8208506657974413 (5) | 0.7245475291277046 (6) | 0.47756675375973734 (2) | 0.19031719532554256 |
| `warp_hw_only_dont...std15` | 0.08465326126881603 (2) | -0.004817781575014973 (2) | 0.8465126951137221 (9) | 0.7554732810494599 (9) | 0.4711461894218484 (3) | 0.169449081803005 |
| `warp_hw_only_dont...std2` | 0.08808170485836675 (4) | -0.00824622516456569 (4) | 0.8244528011600872 (6) | 0.7194705336022215 (5) | 0.46663233625946965 (4) | 0.18864774624373956 |
| `warp_all...std2` | 0.09027907493360153 (6) | -0.010443595239800471 (6) | 0.8134476291238948 (4) | 0.6958293619502486 (4) | 0.46136047290193527 (5) | 0.19532554257095158 |
| `dont...std2` | 0.08958469772075701 (5) | -0.009749218026955955 (5) | 0.8258333067799184 (7) | 0.7288877226901269 (7) | 0.45571161985980746 (6) | 0.17445742904841402 |
| `warp_hw_only_dont...std3` | 0.09868939149307393 (7) | -0.01885391179927287 (7) | 0.7898375361572497 (3) | 0.6594524268002262 (2) | 0.43066960873703786 (7) | 0.20534223706176963 |
| `dont...std3` | 0.09923937739510431 (8) | -0.019403897701303255 (8) | 0.7893669977497686 (2) | 0.6770099246346705 (3) | 0.4244294397153585 (8) | 0.18697829716193656 |
| `warp_all...std3` | 0.10347315600977126 (9) | -0.023637676315970205 (9) | 0.7649706024536344 (1) | 0.6332651459671222 (1) | 0.4193193876495547 (9) | 0.21869782971619364 |

The full names for `dont...` and `warp_hw_only_dont...` are the exact active names in the prior table. Lower-correlation `std3` rows are more diverse but have materially worse individual CER; v4's top three select the milder 1.5 trade-off.

### Frozen Grid-Warp shortlist

1. `dont_warp_text_and_lines_d003_r30_s10_std15` — v4 rank 1, `0.47780345508520516`.
2. `warp_all_d003_r30_s10_std15` — v4 rank 2, `0.47756675375973734`.
3. `warp_hw_only_dont_warp_text_and_lines_d003_r30_s10_std15` — v4 rank 3, `0.4711461894218484`.

This is a fixed historical `ensemble_score_v4` shortlist, not a validation-selected claim. Each historical score came from a five-sample pipeline that also cycled Pad variants, so pure-warp transfer remains an explicit caveat.

## Pad/offset evidence and frozen subset

`shift_only` contains these exact zero-based source-order variants:

| Transfer ID | Exact dictionary |
|---|---|
| `shift_only.variant_00` | `{"pad_left":16,"pad_right":16,"pad_top":16,"pad_bottom":16}` |
| `shift_only.variant_01` | `{"pad_left":8,"pad_right":24,"pad_top":8,"pad_bottom":24}` |
| `shift_only.variant_02` | `{"pad_left":28,"pad_right":4,"pad_top":28,"pad_bottom":4}` |
| `shift_only.variant_03` | `{"pad_left":24,"pad_right":8,"pad_top":8,"pad_bottom":24}` |
| `shift_only.variant_04` | `{"pad_left":4,"pad_right":28,"pad_top":28,"pad_bottom":4}` |

Only their five-member aggregate is present in the WARP ranking table: `avg_cer=0.07930349022888478`, `baseline_cer=0.07983547969380106`, `cer_improvement_over_baseline=0.0005319894649162826`, `char_error_correlation=0.9804324686260179`, `field_error_correlation=0.9673924064602234`, `ensemble_score_v1=0.00013038965363898987`, `v2=0.00021728304640950636`, `v3=0.009941606490249449`, `v4=0.016001623308630843`, `expected_ensemble_improvement=0.0000053482328845406935`, `baseline_error_coverage=0.027545909849749584`, `baseline_error_count=1198`, `sample_count=4920`.

The adjacent SHIFT sweep separately proves exact 20-member diagonal, 33-member horizontal, and 32-member vertical granular-pad lists at maximum dimension 2,240. Its experiment-level weighted CERs are 0.09329832717612387, 0.09350656538403, and 0.0931695495848084 respectively. These are family/sweep aggregates, not scores for the five WARP pads, and the v7 CV table concerns a different pixel-shift sweep. They cannot justify inventing per-pad ranks.

Frozen Pad subset: `shift_only.variant_00`, `.variant_01`, `.variant_02`. Rule: first three variants in historical source order, predeclared without modern labels. No individual-score claim is made.

## v7 cross-check

`analysis - v7/paper/transform_metrics_table.tex` reports family-level 5/10-sample values: Grid Warp CER `0.0933/0.0855`, field accuracy `0.7171/0.7331`; Pad CER `0.0840/0.0810`, field accuracy `0.7369/0.7388`. This supports family relevance only. It does not identify the WARP YAML parameter shortlist or prove that the v4 table is a validation selection.

## Ground-truth identity/provenance

Nine located `5164_gts.csv` candidates form two byte-identical groups, each with 622 rows:

- SHA-256 `14219f17eeaaf45ffa4cec49f624de1edb3a739b40a87f0f838355a7fa414ccd`, 159,892 bytes, 20 columns: includes `SelfBirthPlace_orig` and `SelfBirthPlace_edt` (BIG_SHIFT, CONSISTENCY, ROTATE, SHIFT).
- SHA-256 `cf24e896875280560023f6c8976ca6ab32de5d0bc8426c59c00b4d58b235810d`, 142,892 bytes, 18 columns: omits those two columns (LINE_THICKNESS, MONOTONIC_DEGRADATION, MONOTONIC_DEGRADATION2, PROMPT_VARIATION, WARP).

Within WARP and SHIFT, `5164_gts.csv` and `5164_gts_no_post_processing.csv` are byte-identical to their local schema group. Across either schema, the six edited name columns contain 3,718 nonblank cells: 609 SelfGivenName, 622 SelfSurname, 622 FatherGivenName, 622 FatherSurname, 622 MotherGivenName, 621 MotherSurname. Therefore the claimed 3,684 evaluated nonblank name fields requires 34 additional exclusions from a canonical filter that was not recovered in the bounded v7 tables. The schemas are **not interchangeable**, and neither dropping `SelfBirthPlace` nor silently merging files reconciles 3,684. This remains a provenance/evaluation gate.

## Unresolved caveats

- Recover and hash the exact canonical 3,684-field filtering/normalization code and fold assignments.
- Locate or implement the exact `granular_shift` renderer and produce source-to-render hashes.
- Pre-render/harden random-state-null warp outputs before calls; otherwise an experiment name alone does not identify image bytes.
- Confirm segmentation channel semantics and complete mask coverage for all 622 documents.
- Project-owner acceptance is needed for the matrix's disjoint pure-warp projection because historical v4 rows include the shared five-Pad pipeline.
