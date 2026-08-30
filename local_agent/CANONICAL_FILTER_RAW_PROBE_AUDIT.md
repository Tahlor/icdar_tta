# Canonical Filter Raw Probe Audit

## Status

- Probe status: resumed single-file probe after interruption.
- Scope: one bounded streaming metadata pass over the exact named CSV and one immediate-directory listing only.
- Target under audit: the canonical 3,684 `(doc_id, field_name)` evaluation population.
- Privacy constraints: no row values, document identifiers, ground truth, predictions, personal names, response bodies, credentials, or image bytes will be printed or saved.
- Canonical-filter status: not established; this recovery will not create `config/canonical_field_filter.csv` or infer that an exact filter exists from a count alone.

## Bounded probe result

- Recovery request timestamp: `2026-08-29T19:15:29.570-06:00`.
- Input artifact: logical alias `HISTORICAL_WARP_METRICS_DB`; the machine-specific path is retained only in ignored `config/data_manifest.local.yaml`.
- Execution: one non-RTK `timeout 120s python3` streaming pass; exit status `0`; stderr was empty.
- Immediate-directory inspection: `30` entries; `0` entry names matched the case-insensitive terms `canonical`, `filter`, or `generator`. Entry names were not saved in this audit.
- File byte size: `23,014,921`.
- SHA-256: `34cce8d33ce772af0fce762549b2d89b2c166e8c7e55cc21bdcfb332949ffb96`.
- Total data rows (header excluded): `68,880`.
- Header names (`34`): `record_id`, `degradation_suffix`, `experiment_name`, `sample_id`, `experiment_name_with_suffix`, `source_experiment`, `field_name`, `prediction_value_orig`, `prediction_value`, `logprob`, `prob_from_logprob`, `logprob_min`, `prob_from_logprob_min`, `value_avg_logprob`, `value_min_logprob`, `gt_value`, `f_prediction_missing`, `f_gt_missing`, `f_experiment_missing_record_id`, `pred_model_self_conf_norm`, `preds_model_designated_ambig`, `cer`, `edit_distance`, `unique_experiment_id`, `f_fold`, `f_split`, `exp_category`, `exp_category_2`, `exp_category_warp_type`, `exp_category_warp_params`, `f_is_correct`, `f_ambiguous_markers`, `f_confident_markers`, `f_flag_for_human_review`.
- Distinct `field_name` schema-token count: `8`.
- `field_name` schema tokens: `FatherBirthPlace`, `FatherGivenName`, `FatherSurname`, `MotherBirthPlace`, `MotherGivenName`, `MotherSurname`, `SelfGivenName`, `SelfSurname`.
- `f_gt_missing` aggregate counts: value `0` = `68,866`; value `1` = `14`.
- `f_flag_for_human_review` aggregate counts: value `0` = `68,880`.

## Interpretation and limitations

- The pass completed within the bound, so no partial-result limitation applies.
- The immediate directory listing did not expose a pre-existing artifact or generator whose name directly identifies a canonical filter.
- This metadata does not define or independently verify an exact canonical population. In particular, no row-count coincidence is treated as evidence for a filter.
- `config/canonical_field_filter.csv` was not created. No broader search, recursive scan, additional worker, network/provider call, inference call, credential inspection, file copy, or raw-record export was performed.
- No CSV row values, document identifiers, ground-truth values, prediction values, personal names, response bodies, credentials, or image bytes were printed or saved.
