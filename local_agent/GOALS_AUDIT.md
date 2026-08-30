# Targeted follow-up resolution — 2026-08-29

This section supersedes the provisional shortlist statements below but preserves them as an audit trail. The follow-up made no provider/network/inference calls.

## Frozen historical decision

- **Grid-Warp shortlist:** `dont_warp_text_and_lines_d003_r30_s10_std15`, `warp_all_d003_r30_s10_std15`, and `warp_hw_only_dont_warp_text_and_lines_d003_r30_s10_std15`. They rank 1–3 by descending `ensemble_score_v4` at `0.47780345508520516`, `0.47756675375973734`, and `0.4711461894218484`. Suffix `std15` is exactly `noise_std=1.5`, the mildest active value; it is not 15. Grid rows tie at zero under v1–v3 and expected improvement, so this is a named historical v4 rule, not a validation-selection claim.
- **Pad shortlist:** `shift_only.variant_00`, `.variant_01`, `.variant_02`, with exact dictionaries recorded in `SHORTLIST_EVIDENCE.md`. Only the five-member `shift_only` aggregate is scored; the deterministic rule is first three in source order, fixed without modern labels. No per-pad score is claimed.
- **Implementation:** active WARP rows use registry type `handwriting_kernel_warp`, not `gridwarp.py` or `gridwarp2.py`. The registry and implementation hashes are recorded in `SHORTLIST_EVIDENCE.md`. Historical grid rows also cycled the five Pad variants; the deadline matrix freezes a disjoint pure-warp projection and gates it on project-owner acceptance.
- **Commented variants:** 18 `r60`/`d005` definitions remain non-active evidence. Three active `warp_hw_*` rows have no row in the 10-row ranking TSV.

## Ground truth correction

The recurring CSV basenames are not one interchangeable file. Nine candidates split into two 622-row groups: SHA-256 `14219f17eeaaf45ffa4cec49f624de1edb3a739b40a87f0f838355a7fa414ccd` (20 columns, includes SelfBirthPlace) and `cf24e896875280560023f6c8976ca6ab32de5d0bc8426c59c00b4d58b235810d` (18 columns, omits SelfBirthPlace). Both contain 3,718 nonblank cells across the six edited name fields. The 3,684 evaluation denominator therefore depends on an unrecovered 34-field exclusion/filter rule; it must not be reconstructed by silently merging or dropping schema columns.

## Exact modern IDs and route state

- Flash 3.7 → `gemini-3.7-flash` (10/10 returned `modelVersion` rows in local Milan L3 batch evidence).
- Flash-Lite 3.5 → `gemini-3.5-flash-lite` (Vertex global completed evidence, including 500/500 returned-model records).
- Vermont Qwen → `sagemaker-qwen3-vl-8b-instruct-fp8` (SageMaker L3 chat runner and raw metadata).

The IDs are mapped, but live PA verification remains pending. Direct inline Gemini is the simplest proposed transport but is locally proven only for earlier `gemini-3.5-flash` and `gemini-3.1-flash-lite`; the requested IDs require fresh three-image smokes. Exact-ID batch fallbacks are evidenced but operationally heavier. Qwen requires a budget-safe change that disables its redundant 15-second keepalive during active scored traffic and fixes prompt-ID lineage.

## Gate decision

`EXPERIMENT_MATRIX.md`, `request_budget.json`, `ROUTE_AUDIT.md`, and `SHORTLIST_EVIDENCE.md` now exist. The three-model scored formula is 16,794; reserve is 3,190; worst case is 19,984; spent is zero. **No paid call is authorized** until the canonical cohort/filter, rendered-image lineage, shared parser hash/tests, route smokes, exact returned IDs, and independent budget approval all pass.

---

---

> **Everything below this line is the original bounded-inventory pass.**
> It is retained as an audit trail. Where a statement is contradicted by
> the frozen decision above, it is marked **SUPERSEDED** inline rather
> than deleted, per `AGENTS.md`'s source-of-truth and audit-trail rules.
> Statements not marked superseded are still active/unresolved.

# Goals audit: historical Flash 2 evidence and transform shortlist

One page. Decision record for outcome 1 of `local_agent/TASK.md`. Based on bounded,
read-only inspection of the six named roots; no new inference was run.

## What was found

- **Model and run config**: `PA_DEATH/WARP/PA_DEATH_WARP.yaml` and
  `PA_DEATH/*/metrics_no_punc/run_settings.csv` both confirm `model_name:
  models/gemini-2.0-flash`, `temperature: 0`, prompt file
  `PA_DEATH/prompts/prompt_v1.49_confidence.txt`, `max_output_tokens:
  2048`, `request_logprobs: true`, `logprobs: 2`. This matches the paper's
  Gemini 2.0 Flash single-run baseline described in `README.md`.
- **Raw responses**: `chat2rec_analysis/.../pa_death_records622_official/gemini/`
  holds 12,499 files, largely per-image JSON responses named
  `{film}_{roll?}_{frame}.json`, under a subdirectory named
  `gemini-20-flash_blur_11/` (visible at this depth) — i.e. raw responses are
  organized per-experiment-condition subdirectory. `gemini - confidence_analysis/`
  (1,250 files) appears to be a parallel/derived confidence-scored response set.
- **Ground truth**: `5164_gts.csv` / `5164_gts.pkl` (and a
  `_no_post_processing` variant) recur identically across `BIG_SHIFT/`,
  `CONSISTENCY/`, `SHIFT/`, and `WARP/` — strong evidence of one canonical
  label set reused across experiment families, consistent with the 622-image
  cohort (the `_no_post_processing` variant suggests a raw vs. normalized label
  distinction worth preserving downstream).
- **Grid-warp transform parameter IDs** (from the *uncommented*, i.e. actually
  run, variants in `PA_DEATH/WARP/PA_DEATH_WARP.yaml`):
  - `baseline`
  - `shift_only`
  - `warp_all_d003_r30_s10_std{2,3,15}`
  - `dont_warp_text_and_lines_d003_r30_s10_std{2,3,15}`
  - `warp_hw_only_dont_warp_text_and_lines_d003_r30_s10_std{2,3,15}`
  - `warp_hw_d003_r30_s10_std{2,15,3}`

  A large second block of `r60`/`d005` variants exists in the same file but is
  fully commented out (`#`-prefixed), i.e. planned but not executed historically.
  Do not treat commented variants as run evidence.
- **Grid-warp parameter selection evidence**:
  `PA_DEATH/WARP/metrics_no_punc/ensemble_selection_analysis.tsv` scores
  experiments by `avg_cer`, `baseline_cer`, `cer_improvement_over_baseline`,
  `char_error_correlation`, `field_error_correlation`, four `ensemble_score_v{1..4}`
  variants, and `expected_ensemble_improvement`. First two rows sampled:
  `dont_warp_text_and_lines_d003_r30_s10_std15` and `warp_all_d003_r30_s10_std15`,
  both with `ensemble_score_v1..v3 = 0.0` and nonzero `ensemble_score_v4`
  (~0.478 for both), `sample_count = 4920` (i.e. 622 images × ~8 fields, matching
  the paper's field-level cohort). This TSV is the strongest located candidate
  for "the validation logic that selected [historical parameters]," but only two
  of the many candidate rows were previewed in this pass — full ranking not yet
  extracted.
- **Offset/shift periodicity evidence**: `PA_DEATH/CVPR_ANALYSIS/README.md`
  documents the exact 16px-periodicity analysis referenced in the top-level
  `README.md` ("Small Shift": ±32px step 2; "Big Shift": ±384px step 64; FFT
  peak at k=4 → 16px for the small-shift signal). This is presentation-relevant
  primary evidence, not a paper-table copy.
- **Modern model IDs located**:
  - Qwen: `sagemaker-qwen3-vl-8b-instruct-fp8`, hardcoded as `MODEL` in
    `vermont/63129.IDX.003_field_extraction/scripts/qwen_warmup_and_smoke.py`
    line 17. This is a SageMaker-hosted endpoint identifier, not a
    provider-hosted Qwen API — matters for the route-selection decision in
    `TASK.md` ("do not force Vertex/GCS... without evidence").
  - Gemini Flash 3.7 / Flash-Lite 3.5: **SUPERSEDED** — at the time of this
    pass, not yet located in any of the six roots. The addendum at the top
    of this file now records the exact resolved IDs
    (`gemini-3.7-flash`, `gemini-3.5-flash-lite`), found in `vermont`
    Milan L3 batch evidence and Vertex global batch evidence respectively.
    The paragraph below is preserved verbatim as the original (now
    resolved) open question:

    > not yet located in any of the six roots during this pass. These are
    > planning names per `TASK.md` ("verify and record the exact provider
    > model IDs... at execution time") — no exact modern Gemini endpoint ID
    > was found in `vermont` or `ds-content-raptor` scripts inspected so far.
    > Needs targeted follow-up search (not performed in this bounded pass)
    > rather than assumption.

## Discrepancy to flag

`vermont` and `ds-content-raptor` both contain a `63129.IDX.003_field_extraction/`
subtree with overlapping filenames (`AGENTS.md`, `RESULTS_SUMMARY.md`,
`.tickets/`, `scripts/`). This is either (a) a shared ticket/project namespace
intentionally duplicated across two repos, or (b) one is a stale copy/clone of
the other. `TASK.md` explicitly says "Do not add PA/Vermont-specific code or
artifacts to the Raptor framework repository" — this implies Raptor
(`ds-content-raptor`) is meant to be generic infrastructure and `vermont` is
the project-specific repo, so the presence of `63129.IDX.003_field_extraction`
content inside `ds-content-raptor` may itself be the violation the task is
warning against, or simply an artifact of directory listing overlap that needs
a direct diff to resolve. Not resolved in this pass — flagged for the project
manager rather than silently assumed.

## Decision (provisional, pending full ranking extraction) — SUPERSEDED

> **This entire section is superseded by the frozen decision in the
> addendum at the top of this file.** It is retained verbatim below for
> audit trail only; do not use it as the active shortlist. In particular:
> the frozen decision does **not** include a `std2`/`std3` "mild" member —
> the actual frozen Grid-Warp shortlist is three `std15` variants, and
> `std15` was later confirmed to mean `noise_std=1.5` (the *mildest*
> active value), contradicting this section's guess that `std15` was
> "likely the strongest/most-warped setting." The Pad shortlist was later
> resolved to `shift_only.variant_00/01/02` with the exact dictionaries in
> `SHORTLIST_EVIDENCE.md`, not the "two specific pixel offsets... not yet
> fully extracted" described below.

Freeze the following as the historically promising shortlist to carry into the
modern-model screen, pending confirmation from the full
`ensemble_selection_analysis.tsv` ranking and the chat2rec `analysis - v7`
transform tables (not yet cross-checked in this pass):

- **Grid Warp (3 configs)**: `warp_all_d003_r30_s10_std15`,
  `dont_warp_text_and_lines_d003_r30_s10_std15`, and one of the `std2`/`std3`
  variants (weaker distortion) as the "mild" member requested by `TASK.md`
  ("mild Grid Warp"). `std15` is likely the strongest/most-warped setting given
  naming convention (higher std = more distortion) and appears in the scored
  TSV; `std2` is the mildest. Exact std-to-severity mapping not yet confirmed
  from `gridwarp.py` source — recommend reading
  `chat2rec_v1/chat2rec/degradations/effects/gridwarp.py` before finalizing.
- **Offset/Pad (3 configs)**: `shift_only` plus two specific pixel offsets to
  be pulled from `PA_DEATH/SHIFT/metrics_no_punc/run_settings.csv` (confirmed
  to exist; experiment names not yet fully extracted in this pass — sampled
  columns showed `PA_DEATH_FFT_SHIFT_DIAGONAL` and `PA_DEATH_FFT_SHIFT_HORIZONTAL`
  as experiment-name-adjacent tokens from a CSV whose header wrapped a long
  prompt field, so parsing needs `csv`-aware extraction, not a raw grep).
- **Unchanged-repeat control**: `baseline` (temperature 0, so "unchanged
  repeat" here tests non-determinism at fixed temperature, per the `TASK.md`
  distinction between repeats and sampling controls).

This is not yet the final frozen shortlist — it is the evidence-backed
provisional set. Finalizing requires: (1) parsing the full
`ensemble_selection_analysis.tsv` ranking rather than a 2-row preview, (2)
cross-checking against chat2rec `analysis - v7/paper/transform_metrics_table.tex`,
and (3) confirming the shift-offset parameter values from `SHIFT/metrics_no_punc/run_settings.csv`. None of this required a provider call and all remain available for a follow-up bounded pass.
