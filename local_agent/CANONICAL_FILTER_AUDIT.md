# Canonical Field Filter Audit — Negative Result

Status: **NEGATIVE**. No exact 3,684 doc_id/field_name inclusion/exclusion artifact
or generator was found within the bounded search scope. No filter file was created.

## Objective

Determine whether an exact historical inclusion/exclusion list or deterministic
generator reproduces a target of exactly **3,684** evaluated doc_id/field_name
pairs, starting from fixed-v2's six edited-name nonblank field set (reported
elsewhere as 3,718 nonblank rows before any filtering).

## Scope actually searched (single bounded, read-only Python probe)

One Python program was run once, in read-only mode, restricted to:

- `analysis - v1/paper` through `analysis - v7/paper` (including `v2 - seam carving`
  and `v6a`), direct files only.
- `best_consensus_CER` and `best_consensus_oracle` directories at depth 1 under
  each of the above analysis versions.
- `analysis - v7/outputs/consensus_reliability_analysis` at depth 1.
- Five named historical files under `WARP` and `SHIFT` (logical roots below).
- Direct files (not recursive) under `WARP`, `SHIFT/metrics_no_punc`,
  `BIG_SHIFT/CONSISTENCY`, `CVPR_ANALYSIS` whose filenames contain one of:
  label, ground, truth, valid, eval, field, filter, exclude, fold, consensus.

Logical roots (no machine-specific paths retained below this point):
- `OFFICIAL_ROOT` = official analysis checkout, `pa_death_records622_official` project,
  containing `analysis - v1` .. `analysis - v7`/`v6a`.
- `HIST_ROOT` = historical `PA_DEATH` project root, containing `WARP`, `SHIFT`,
  `BIG_SHIFT`, `CVPR_ANALYSIS`.

Exclusions enforced by the probe: files >2MB skipped; any file/dir name containing
`prediction`, `response`, `gemini`, `master`, `database`, `raw`, `image`, `.png`,
`.jpg`, `.jsonl` skipped (one narrow exception: `master_first_sample_database.csv`
was read for header + aggregate row count only, per explicit task instruction, with
no per-row content printed). `BIG_SHIFT/CONSISTENCY` does not exist under `HIST_ROOT`
(confirmed missing, not a scope violation). `WARP/metrics_no_punc/experiment_level_consensus.tsv`
does not exist at the specified path (confirmed missing).

The probe printed only filenames, sha256 hashes, headers, row counts, and lines
containing: `3684`, `3,684`, `3718`, `3,718`, `canonical`, `exclude`, `exclusion`,
`valid`, `evaluable`, `f_gt_missing`, `field`, `sample_count`.

## Result: token search

Across the entire bounded scope, **zero lines contained** `3684`, `3,684`, `3718`,
`3,718`, `canonical`, `exclusion`, or `evaluable`. All `field`/`sample_count` hits
were column-header tokens (e.g. `Field_Accuracy_5_Samples`, `sample_count`), not
filter definitions. No script, config, or summary file anywhere in scope names or
implements a "canonical" filter concept.

## Result: candidate row/pair counts (source-grounded)

| Count (data rows) | Source file (logical name) | Hash (sha256) | Notes |
|---|---|---|---|
| 622 | `WARP/5164_gts.csv` | `cf24e896875280560023f6c8976ca6ab32de5d0bc8426c59c00b4d58b235810d` | Source labels, 18 columns, doc-level not field-level. |
| 622 | `SHIFT/5164_gts.csv` | `14219f17eeaaf45ffa4cec49f624de1edb3a739b40a87f0f838355a7fa414ccd` | Source labels, 20 columns (adds SelfBirthPlace), doc-level not field-level. |
| 68,892 | `WARP/metrics_no_punc/master_first_sample_database.csv` | `34cce8d33ce772af0fce762549b2d89b2c166e8c7e55cc21bdcfb332949ffb96` | Raw per-sample rows (unaggregated); headers + aggregate count only inspected per instruction. Contains `f_gt_missing` and `f_flag_for_human_review` columns but no standalone canonical-filter artifact. |
| 3,682 | `analysis - v7/outputs/consensus_reliability_analysis/consensus_shift_data.csv` | `e562e96ed5dede565e0f88746be37367ae9c21e0dde84fc9f18a394182bf804f` | Has `f_gt_missing` column (per-row flag, not a separate filter list). Matches current repo historical denominator. |
| 3,682 | `.../consensus_T05_data.csv` | `f38eb3a38fb3dd959bced05a4cc241883840690ce6bad07b5d8d8f32b48be8d2` | Same shape/columns as above. |
| 3,682 | `.../consensus_T1_data.csv` | `e4c3b5cbdef5477684cdd62f475f7e6b58f4ebea26e70bcb52bc408f9dd12932` | Same shape/columns as above. |
| 3,682 | `.../consensus_T2_data.csv` | `6033e4c9bc1db7f78d29ff890295e5304c22f7ba2d598b6b5ac20e28c8b93932` | Same shape/columns as above. |
| 3,677 | `SHIFT/metrics_no_punc/name_fields_consensus_by_category.csv` | `78b4ac5a720a915a2d8ebd48725c1457ab7fe24b8f7ccb21e84244db02336582` | Per-record-per-field consensus rows for the `shift` category only; no explicit "canonical" label on this file or its generator. |
| 10 | `WARP/metrics_no_punc/ensemble_selection_analysis.tsv` | `3224861466c073bb8c21e5944268a910f437a178c76a335260389dc0f19eea39` | Per-experiment summary, not per-field; irrelevant to pair-count question. |
| 3 | `SHIFT/metrics_no_punc/experiment_level_consensus_summary.tsv` | `ef7ae7006d178fcafebfbbfb3188a98168b7abf79754936aac4611fe91da1531` | Per-experiment summary, not per-field. |
| 1 | `SHIFT/metrics_no_punc/name_fields_category_summary.csv` | `55aa736605b4d32072c62491b1adca1cd3d3bcc33452b430279a2d0aca7670a0` | Single aggregate row across all name fields; not a pair list. |
| n/a | `WARP/metrics_no_punc/experiment_level_consensus.tsv` | — | **File missing** at the specified path; not found anywhere else in bounded scope. |
| n/a | `BIG_SHIFT/CONSISTENCY` | — | **Directory missing**; not found. |

No file in this table equals 3,684. No file is accompanied by a script or config
in scope that transforms one of these counts into 3,684 via a named, evidenced
predicate (e.g., an explicit "canonical" mask, an exclusion list, or a documented
fold/valid/evaluable join). The closest population (3,682, from the four
`consensus_*_data.csv` tables) is 2 rows short of 3,684 in the *wrong* direction
(fewer, not more), and the task's own framing starts from 3,718 nonblank pairs
going down to 3,684 (34-row exclusion), not from 3,682 going up.

## Predicates tested and rejected

Per the task's requirement to test only predicates evidenced by a named artifact
or generator (not to search for an arbitrary 34-row exclusion that happens to
land on 3,684):

- **`f_gt_missing` mask** — present as a column in the `consensus_*_data.csv`
  files and in `master_first_sample_database.csv`, but it flags rows already
  excluded to reach 3,682, not a 3,684-row set. Applying/removing this mask does
  not reach 3,684 from any candidate table inspected.
- **Explicit valid/evaluable column** — no column literally named `valid`,
  `evaluable`, or `canonical` was found in any header in scope.
  `name_fields_consensus_by_category.csv` has an `accuracy`/`TP`/`FP`/`TN`/`FN`
  set but no inclusion mask column.
  `master_first_sample_database.csv` has `f_is_correct`, `f_ambiguous_markers`,
  `f_confident_markers`, `f_flag_for_human_review` — none of these are a
  documented canonical-inclusion filter, and applying any single one of them
  was not attempted without a named generator script defining how, since none
  references a target count or "canonical" concept in-scope.
- **Fold join** — `f_fold`/`f_split` columns exist in the raw and consensus
  tables, but no fold-based row count in scope equals 3,684, and no script in
  scope documents a fold-based canonical selection.
- **Row-inclusion list / generator script** — no script, notebook, or config
  file was found anywhere in the bounded scope (including `paper/` directories
  across v1–v7/v6a) that emits, references, or is named after 3,684 or
  "canonical."

## Blocker

**No named artifact or generator producing exactly 3,684 doc_id/field_name pairs
exists within the bounded search scope defined for this session.** The only
candidate counts found are 3,682 (four `consensus_*_data.csv` tables, `f_gt_missing`
already applied — this matches the repository's current historical denominator),
3,677 (`name_fields_consensus_by_category.csv`, `shift` category only), and the
unfiltered 622 source rows / 68,892 raw per-sample rows. None of these is 3,684,
and no in-scope script or config bridges any of them to 3,684 via a documented
predicate.

Widening the search (e.g., recursively into raw response trees, `BIG_SHIFT`
subdirectories beyond `CONSISTENCY`, `CVPR_ANALYSIS` beyond direct-file scope, or
`projects2`/v8–v10 outside the task's named version list) was explicitly out of
scope for this session and was not performed. If the 3,684 target originates from
one of those excluded locations, or from a script/notebook not committed to disk
under the inspected roots, that is outside what this bounded audit can confirm or
deny.

## Disposition

- No filter file created. `config/canonical_field_filter.csv` and
  `config/canonical_field_filter.sha256` are **not** created by this session.
- `config/data_manifest.yaml` / `config/data_manifest.local.yaml`: **not modified**
  — the evidence does not change canonical-filter status (still absent).
- Historical derived tables: **left unchanged** at the existing 3,682 noncanonical
  denominator, as instructed.
- `local_agent/request_budget.json`: **not touched**.
- Live inference/provider gate: **left closed**. No provider, network, model, or
  inference calls were made.

## Commands run

- One bounded read-only Python probe script (temporary, not committed; deleted
  after use) performing directory-scoped `os.walk` at `max_depth<=2`, per-file
  size check (skip >2MB), per-file/dir name forbidden-substring check, sha256 of
  each inspected file, and regex line-matching against the allowed token list.
- `sha256sum` verification of `config/source_image_manifest.csv` against
  `config/source_image_manifest.sha256` (confirms 622 data rows, hash
  `7ad5e7a065bf8bd262953d8faf8e34344e861333c4655eff72bf80aee90f25ee` — unchanged,
  consistent with the sidecar's own serialization note of header + 622 rows).
- `git status --short` / `git log --oneline -5` to confirm current working tree
  state before making any writes.

No provider/model calls, network access, inference, raw-image copy, archive
extraction, external-repository edits, commits, `git clean`, `git reset`, or
deletions were performed.

## Files owned/written by this session

- `local_agent/CANONICAL_FILTER_AUDIT.md` (this file) — created.

No other files were created or modified by this session.

CANONICAL_FILTER_AUDIT_DONE
