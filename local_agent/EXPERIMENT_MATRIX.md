# Frozen pre-call experiment matrix

Status: **conditions frozen; live execution BLOCKED**
Freeze date: 2026-08-29
Scope: deadline screen only, 622 documents × 9 views × 3 requested modern models. No provider, network, or inference call was made in this audit.

This remains the pre-call freeze. A later six-request, label-blind `U0`
Gemini smoke is recorded separately in `MODERN_SMOKE_RECEIPT.md`; it does not
change the three-model/full-nine-view matrix or make a label-based result
claim.

## Cohort and evaluation roles

- Cohort: the fixed Pennsylvania death-record cohort of 622 source documents. A provider call is blocked until a portable `doc_id`/source-image SHA-256 manifest proves exactly 622 unique inputs.
- Ground truth: the candidate CSVs all have 622 rows but are not interchangeable. The two schemas/hashes and the unresolved 3,684-field filter are documented in `SHORTLIST_EVIDENCE.md`; the exact historical per-field database was reached but its safe aggregate audits did not recover the inclusion artifact (`CANONICAL_FILTER_RAW_PROBE_AUDIT.md`, `CANONICAL_FILTER_STATUS_AGGREGATE_AUDIT.md`). No score may be computed until the canonical schema/filter is recovered and frozen.
- Primary evaluated fields: the six edited name fields for self, father, and mother, after the historical canonical nonblank/evaluability filter. The raw CSV count is 3,718, not 3,684; 3,684 remains a blocked regression target rather than an assumed denominator.
- Primary deployment comparison: accepted-field precision/risk versus automatic coverage/manual review at targets frozen before labels are revealed. Raw agreement is not called a calibrated probability.
- Comparability metrics: exact field accuracy and CER; extraction precision/recall only if the recovered canonical event definition makes false positives/negatives meaningful.
- Modern labels must remain hidden while routes are smoked and while image/prompt/parser lineage is checked. No transform, prompt, threshold, model, or ensemble may be selected from modern test-label performance.

## Exact model matrix

| Requested planning family | Exact executable ID evidenced locally | Local evidence | Screen status |
|---|---|---|---|
| Flash 3.7 | `gemini-3.7-flash` | A 10-request Milan L3 batch canary returned `modelVersion=gemini-3.7-flash` in all 10 provider-output rows | **Pending PA route smoke and returned-ID check** |
| Flash-Lite 3.5 | `gemini-3.5-flash-lite` | Vertex global batch evidence records `publishers/google/models/gemini-3.5-flash-lite`; completed 20/20, 36/36, and 500/500 returned-model checks are recorded; a three-document PA `U0` smoke returned the exact ID | **U0 smoke passed; full nine-view screen still pending** |
| Vermont Qwen vision | `sagemaker-qwen3-vl-8b-instruct-fp8` | Exact model field occurs in Vermont runner and raw JSONL metadata; SageMaker L3 OpenAI-compatible chat route | **Pending PA smoke, capacity check, and budget-safe keepalive change** |

Related but **not substitutes**: `gemini-3.5-flash` and `gemini-3.1-flash-lite` have 500-row local raw-response evidence and direct L1 runner evidence. They do not replace either requested Gemini model. `models/gemini-2.0-flash` is historical reuse-only and is excluded from every new-call row.

## Frozen prompt, schema, parser, and generation contract

- Prompt ID: `prompt_v1.49_confidence`.
- Prompt evidence: `PA_DEATH/prompts/prompt_v1.49_confidence.txt`.
- Prompt SHA-256: `fd119108d3ef4dbf2f88984511d9f903b7d4c98b032a95c327a21f713335e48e` (4,823 bytes).
- Embedded output schema: one JSON object with exactly 44 named fields; each field is an object containing `value` and integer `confidence` from 1–10. Missing is `"N/A"`, present-but-blank is `""`; `SelfDeathAge.value` is the prompt's documented three-element array exception.
- Parser specification ID: `pa_v149_json_repair_v0`. Preserve raw text; remove a complete Qwen `<think>...</think>` block if present; remove at most one outer Markdown JSON fence; try direct JSON decoding, then one outermost-braced-object decode; record the repair path; require an object and structurally validate the 44-field contract; never turn a failed/missing response into agreement.
- Parser implementation SHA-256: `656366a6215d008dd443abae45603e1a628513b5331a4752928e35fbb3ff9fde`.
- Parser hash serialization: SHA-256 over the exact bytes of `src/icdar_tta/parser.py` as stored; no text decoding, newline conversion, prefix, or suffix.
- Parser evidence: **offline PASS** for `pa_v149_json_repair_v0`; 40 parser-focused `unittest` cases (53 in the parser/schema target module) cover the exact field contract, strict values/confidences, three-string `SelfDeathAge`, think/fence handling, the single outermost-object fallback, raw failures, and structural separation of failures from parsed fields.
- Retry policy ID: `provider_neutral_retry_v1`; implementation SHA-256 `b35f840a7cd0d8969e250fa62f89fef5a31ee7afc99232c03130e8b5ac4f7f0d` over the exact bytes of `src/icdar_tta/retry.py` under the same byte-hash serialization.
- Retry evidence: **offline PASS** in 21 focused `unittest` cases for one-retry maximum, fifth-consecutive-network stop, immediate capacity stop, reconcile-only ambiguity, fingerprint-guarded terminal resume, and explicit remaining statuses. This is policy evidence only and does not authorize or perform provider calls.
- Request-ledger implementation: `src/icdar_tta/request_ledger.py`; exact-byte SHA-256 `6c727ee40ccada307f185d6c6ad56c2b5c608d7d2dc20a66ead9c76460929479`. Serialization is append-only canonical JSONL (sorted keys, compact separators, UTF-8, one object and terminal LF per appended event); request fingerprints are SHA-256 over canonical UTF-8 JSON containing the closed model, prompt/schema, source-image, transform, sample-index, generation-parameter, and route/transport dimensions.
- Request-ledger evidence: **offline PASS** in 24 focused `unittest` cases for deterministic/distinct fingerprints, record/history validation, append/read and malformed-JSONL behavior, raw metadata preservation, exact terminal matching, reconcile-only ambiguity, capacity/fifth-network stops, and retry delegation. This does not claim a live ledger, provider route, render lineage, or authorization gate passed.
- Generation: temperature `0`, candidate count `1`, maximum output tokens `2048`; no prompt sweep, reasoning sweep, or per-model sampling tuning. Qwen additionally uses `/no_think` and `enable_thinking=false`. For Gemini, exact supported thinking-control serialization is a smoke-test item; unsupported controls must be recorded rather than silently substituted.

## Frozen nine views per document

Common source identity and route-required encoding are not transforms. Each rendered view must be linked to the source SHA-256 and receive its own rendered-image SHA-256 before submission.

| View | Strategy | Frozen transform ID | Exact parameters / definition |
|---|---|---|---|
| U0 | unchanged | `unchanged_repeat.0` | Canonical source pixels after only the single frozen route transport conversion; serves as single-run baseline |
| U1 | unchanged | `unchanged_repeat.1` | Byte-identical image payload to U0; a separate model call |
| U2 | unchanged | `unchanged_repeat.2` | Byte-identical image payload to U0; a separate model call |
| P0 | Pad | `shift_only.variant_00` | `{"pad_left":16,"pad_right":16,"pad_top":16,"pad_bottom":16}` |
| P1 | Pad | `shift_only.variant_01` | `{"pad_left":8,"pad_right":24,"pad_top":8,"pad_bottom":24}` |
| P2 | Pad | `shift_only.variant_02` | `{"pad_left":28,"pad_right":4,"pad_top":28,"pad_bottom":4}` |
| G0 | Grid Warp | `dont_warp_text_and_lines_d003_r30_s10_std15` | `handwriting_kernel_warp`; shared params below; `do_not_warp_channels=[0,1]`; `noise_std=1.5` |
| G1 | Grid Warp | `warp_all_d003_r30_s10_std15` | same shared params; no channel include/exclude lists; `noise_std=1.5` |
| G2 | Grid Warp | `warp_hw_only_dont_warp_text_and_lines_d003_r30_s10_std15` | same shared params; `do_warp_channels=[2]`, `do_not_warp_channels=[0,1]`; `noise_std=1.5` |

Grid shared historical parameters: `prob=1.0`, `point_density=0.003`, `base_radius=30.0`, `boundary_safety=1.0`, `min_radius=5.0`, `warp_strength=10.0`, `falloff_type="gaussian"`, `region_based=true`, `region_margin=20`, `min_influence=0.01`, `min_region_area=100`, `dilate_radius=3`, `min_component_size=50`, `mask_suffix=".tif"`, `visualize=false`, `random_state=null`; implementation defaults also make `target_scale=1200`, `auto_scale_params=true`, and `full_image_mode=false`. The historical WARP pipeline first resized to maximum dimension 1,504 and also cycled the five granular pads. For this nine-view strategy comparison, G0–G2 transfer the exact warp parameter dictionaries but do **not** add a second Pad view; this avoids double-counting a compound Pad+Warp view. That projection is frozen here and requires project-owner acceptance because its historical ranking was measured in the five-sample WARP pipeline, not as a pure-warp ablation.

Pad selection rule: the first three `shift_only` variants in source order, fixed before modern labels. Only the aggregate five-member `shift_only` row is scored historically; P0–P2 have no invented individual score.

Grid selection rule: top three active grid IDs by descending historical `ensemble_score_v4` in `WARP/metrics_no_punc/ensemble_selection_analysis.tsv`. This is a named historical ranking rule, **not** a claim of validation selection. All three use the mildest tested `noise_std`, 1.5; suffix `std15` does not mean 15.

## Ensemble construction (zero additional calls)

- `single`: U0 only.
- `unchanged_3`: U0+U1+U2.
- `pad_3`: P0+P1+P2.
- `grid_3`: G0+G1+G2.
- `visual_mixed_6`: P0+P1+P2+G0+G1+G2.
- `all_views_9` (secondary): all nine responses.
- Consensus member order is exactly the order above. Missing/failed members remain explicit and are never treated as votes. Any progressive alignment must preserve this canonical order.
- Derived consensus, agreement, correlation, and mixed ensembles are computations over existing responses and cost zero provider calls.

## Planned smoke and lineage checks

1. Offline: prove 622 unique `doc_id`s; source hashes; transform specs; segmentation-mask coverage; deterministic transformed-image manifests; and byte identity of U0/U1/U2 payloads.
2. Offline: fixture-test parser success, fence/think repair, malformed JSON, truncation, absent fields, `SelfDeathAge`, and failed-response handling; freeze parser and schema hashes.
3. Live, only after approval: exactly three predeclared, label-blind smoke images per exact model (9 reserved calls). Require HTTP/provider success, parse status, usage metadata, source/transform/request IDs, and returned exact model/version where supplied.
4. Route lineage: write a durable request ledger before each submission; key every response by `(doc_id, model_id, transform_id, sample_index)`; never rely only on response position; preserve raw responses byte-for-byte.
5. Resume: skip only a terminal response with matching request fingerprint. An armed/ambiguous batch is reconcile-only, never blindly resubmitted.
6. Stop after five consecutive network/capacity failures, any ambiguous submission outcome, returned-model mismatch, parser/schema drift, or exhaustion of the reserved ledger.

## Paid-call gate — currently FAIL/CLOSED

**No paid/provider call is authorized until every item below passes and the project manager records the approval timestamp.**

- [x] Exact 622-image source manifest is recovered and hashed (`config/source_image_manifest.csv`; source gate PASS).
- [ ] Canonical 3,684-field evaluation filter is recovered and hashed (raw database and status-aggregate audits negative/partial; filter gate remains BLOCKED).
- [ ] All nine view definitions render correctly; source/mask/render lineage manifests and hashes exist.
- [x] Shared PA parser/schema implementation and fixture tests pass; the exact 44-field schema is embedded in the hashed parser implementation and the parser hash is frozen above.
- [ ] A route is selected per model; credentials are external to artifacts; direct/batch image transport is verified without signed URLs in portable files.
- [ ] The two requested Gemini IDs and Qwen ID pass the exact three-image lineage smoke and returned-ID checks.
- [ ] Qwen's redundant concurrent keepalive is disabled during active scored traffic; the warmup/keepalive count is ledgered and capped at 81.
- [ ] `request_budget.json` is independently reviewed: scheduled 16,794, reserved 3,190, spent 0, worst case 19,984, remaining 16.
- [x] Retry, capacity-stop, ambiguous-submit, and resumability behavior is tested offline (21 focused `unittest` cases; no provider calls).
- [x] Provider-neutral request-ledger serialization, history, malformed-input, fingerprint, metadata, and retry-integration behavior is tested offline (24 focused `unittest` cases; implementation SHA-256 `6c727ee40ccada307f185d6c6ad56c2b5c608d7d2dc20a66ead9c76460929479`; no provider calls or live records).
- [ ] Project manager records explicit live-call authorization. Until then, matrix state remains `BLOCKED`.
- [x] No new Gemini 2.0 Flash inference is present or planned.
- [x] Transform/model/threshold selection is frozen without modern-label access.
