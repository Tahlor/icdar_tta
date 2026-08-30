# Canonical Filter Status — Aggregate Audit

> **Scope clarification — 2026-08-30:** this audit remains a negative result
> for discovering a standalone filter from the 68,880-row legacy database and
> its aggregate flags. It does not test, and must not be read as disproving,
> the historical selector/exclusion code recovered later. See
> [`docs/GT_LINEAGE.md`](../docs/GT_LINEAGE.md) for the current contract.

## Status and verdict

- Status: `COMPLETE_NEGATIVE_PARTIAL_PRIVACY_SAFE`.
- Verdict: **the authorized legacy CSV and its immediate directory listing do not directly evidence a standalone 3,684 `(doc_id, field_name)` key list.** This remains a database-artifact negative result; it does not contradict the recovered code/configuration rule in `docs/GT_LINEAGE.md`.
- Scope: one bounded, offline, streaming aggregate inspection of the single authorized historical metrics CSV, plus the exact immediate-directory listing and the repository-local task contract.
- Interpretation guardrail: a count of 3,684—including any group or flag combination totaling 3,684—would not by itself evidence the canonical filter. No flags were combined, no exclusions were invented, and no filter was inferred.

## Authorized input and execution receipt

- Input artifact: logical alias `HISTORICAL_WARP_METRICS_DB`; the machine-specific path is retained only in ignored `config/data_manifest.local.yaml`.
- Execution: exactly one `rtk timeout 120s python3` standard-library `csv` streaming pass. A hashing reader updated SHA-256 from the same byte stream consumed by the CSV parser; the CSV was not reopened or copied.
- Literal exit status: `0`.
- Literal stderr: empty (`""`).
- File byte size: `23,014,921`.
- SHA-256: `34cce8d33ce772af0fce762549b2d89b2c166e8c7e55cc21bdcfb332949ffb96`.
- Total data rows (header excluded): `68,880`.
- Malformed rows: `0`.

## Header

- Header column count: `34`.
- Header columns, in source order: `record_id`, `degradation_suffix`, `experiment_name`, `sample_id`, `experiment_name_with_suffix`, `source_experiment`, `field_name`, `prediction_value_orig`, `prediction_value`, `logprob`, `prob_from_logprob`, `logprob_min`, `prob_from_logprob_min`, `value_avg_logprob`, `value_min_logprob`, `gt_value`, `f_prediction_missing`, `f_gt_missing`, `f_experiment_missing_record_id`, `pred_model_self_conf_norm`, `preds_model_designated_ambig`, `cer`, `edit_distance`, `unique_experiment_id`, `f_fold`, `f_split`, `exp_category`, `exp_category_2`, `exp_category_warp_type`, `exp_category_warp_params`, `f_is_correct`, `f_ambiguous_markers`, `f_confident_markers`, `f_flag_for_human_review`.

## `field_name` schema-token aggregates

Distinct schema-token count: `8`.

| Schema token | Rows |
|---|---:|
| `FatherBirthPlace` | 8,694 |
| `FatherGivenName` | 8,694 |
| `FatherSurname` | 8,694 |
| `MotherBirthPlace` | 8,694 |
| `MotherGivenName` | 8,694 |
| `MotherSurname` | 8,694 |
| `SelfGivenName` | 8,358 |
| `SelfSurname` | 8,358 |

These are schema identifiers and aggregate counts only; no row-level field content was retained or emitted.

## Flag and explicit-status aggregates

All columns beginning with `f_` were counted. The explicit non-`f_` status column `preds_model_designated_ambig` was also counted. Counts for each column sum to `68,880`.

| Column | Aggregate value counts |
|---|---|
| `f_prediction_missing` | `0`: 68,843; `1`: 37 |
| `f_gt_missing` | `0`: 68,866; `1`: 14 |
| `f_experiment_missing_record_id` | `0`: 68,872; `1`: 8 |
| `preds_model_designated_ambig` | `<empty>`: 68,880 |
| `f_fold` | `0`: 13,804; `1`: 13,776; `2`: 13,748; `3`: 13,832; `4`: 13,720 |
| `f_split` | `test`: 55,076; `train`: 13,804 |
| `f_is_correct` | `0`: 17,890; `1`: 50,990 |
| `f_ambiguous_markers` | `0`: 68,880 |
| `f_confident_markers` | `0`: 68,880 |
| `f_flag_for_human_review` | `0`: 68,880 |

No flag combinations were computed. In particular, these status counts are descriptive properties of database rows, not evidenced canonical-inclusion semantics.

## Experiment/category/transform-control aggregates

To avoid emitting source values, every nonempty grouping value below is represented as `sha256:` followed by the first 12 hexadecimal characters of SHA-256 over its exact UTF-8 value. `<empty>` denotes an empty value. Identical short keys across columns represent identical source strings. No short-key collision occurred within any reported column.

### `degradation_suffix`

| Key | Rows |
|---|---:|
| `<empty>` | 68,880 |

### `experiment_name`

| Key | Rows |
|---|---:|
| `sha256:0f0d47d08055` | 4,920 |
| `sha256:11ec4e5abfb6` | 4,920 |
| `sha256:2e7d36c67213` | 4,920 |
| `sha256:49e921d2659c` | 4,920 |
| `sha256:571fb44b4be0` | 4,920 |
| `sha256:597667d0c96e` | 4,920 |
| `sha256:8ba8496a2525` | 4,920 |
| `sha256:8bb7d48063ac` | 4,920 |
| `sha256:916e4df8ad26` | 4,920 |
| `sha256:9a769947cd84` | 4,920 |
| `sha256:9a82cee62aa9` | 4,920 |
| `sha256:b84ab8dfa34e` | 4,920 |
| `sha256:f074e218ed9d` | 4,920 |
| `sha256:f6e59d2222cf` | 4,920 |

### `source_experiment`

| Key | Rows |
|---|---:|
| `<empty>` | 8 |
| `sha256:0f0d47d08055` | 4,912 |
| `sha256:11ec4e5abfb6` | 4,920 |
| `sha256:2e7d36c67213` | 4,920 |
| `sha256:49e921d2659c` | 4,920 |
| `sha256:571fb44b4be0` | 4,920 |
| `sha256:597667d0c96e` | 4,920 |
| `sha256:8ba8496a2525` | 4,920 |
| `sha256:8bb7d48063ac` | 4,920 |
| `sha256:916e4df8ad26` | 4,920 |
| `sha256:9a769947cd84` | 4,920 |
| `sha256:9a82cee62aa9` | 4,920 |
| `sha256:b84ab8dfa34e` | 4,920 |
| `sha256:f074e218ed9d` | 4,920 |
| `sha256:f6e59d2222cf` | 4,920 |

### `exp_category`

| Key | Rows |
|---|---:|
| `sha256:8ba8496a2525` | 4,920 |
| `sha256:d9298a10d1b0` | 59,040 |
| `sha256:ecd3fad7a4d3` | 4,920 |

### `exp_category_2`

| Key | Rows |
|---|---:|
| `sha256:d9298a10d1b0` | 68,880 |

### `exp_category_warp_type`

| Key | Rows |
|---|---:|
| `sha256:2944717df707` | 9,840 |
| `sha256:8ba8496a2525` | 4,920 |
| `sha256:94cecdead857` | 14,760 |
| `sha256:bc43f9010770` | 19,680 |
| `sha256:d9298a10d1b0` | 14,760 |
| `sha256:f074e218ed9d` | 4,920 |

### `exp_category_warp_params`

| Key | Rows |
|---|---:|
| `sha256:17a2c0470633` | 19,680 |
| `sha256:869284160205` | 4,920 |
| `sha256:8ba8496a2525` | 4,920 |
| `sha256:ce329c72470e` | 19,680 |
| `sha256:d9298a10d1b0` | 14,760 |
| `sha256:f074e218ed9d` | 4,920 |

Every reported grouping column sums to `68,880`. No individual reported group count is `3,684`.

## Immediate-directory evidence

- Immediate entries: `30`.
- Immediate entry names matching case-insensitive `canonical`, `filter`, or `generator`: `0`.
- The listing contains derived database/consensus/metrics artifacts and transform-named directories, but no immediate entry directly names a canonical-filter artifact or generator.
- A filename/listing alone cannot establish inclusion semantics. Because no directly named artifact/generator was present, no filter semantics could be independently evidenced within this task's exact listing-only scope.

## Interpretation and limitations

1. The `68,880` rows are experiment/sample/field database rows. Their field, flag, fold, split, experiment, category, and transform-control aggregates are not a deduplicated canonical `(doc_id, field_name)` population.
2. Neither an aggregate count nor a count coincidence can establish the historical inclusion/exclusion rule. No group equals 3,684 here, but even one that did would remain insufficient without a named artifact/generator and independently evidenced semantics.
3. The pass did not derive document IDs, count distinct document/field pairs, combine flags, test candidate exclusions, or inspect prediction, ground-truth, response, or row-level label values.
4. The immediate-directory inspection was listing-only. It did not recursively inspect transform directories or open other external artifacts, scripts, notebooks, pickles, responses, images, or credentials.
5. No broader filesystem/repository search for a generator was performed as part of this audit. Repository-local documents were consulted only to interpret the assigned contract and avoid repeating unsafe or semantically unsupported inference.
6. No network/provider call, inference, image-byte access, raw-response output, file copy, row-level extract, or canonical-filter file creation occurred.
7. `config/canonical_field_filter.csv` remains uncreated. This audit did not export a label-bearing key list; the historical selector/exclusion rule is documented separately in `docs/GT_LINEAGE.md`, with the v9/v10 blank-row convention still requiring explicit treatment in a paper-lineage recomputation.
