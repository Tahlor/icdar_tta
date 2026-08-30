# Modern screen completion addendum — 2026-08-30 America/Denver

The deadline transfer screen is complete for the two executable Gemini models:
`gemini-3.5-flash` (the available Flash substitute after the PA 3.7 route
returned HTTP 403) and `gemini-3.5-flash-lite`. Each has 5,598 terminal rows
(622 documents × 9 frozen views), with 11,307 submitted ledger events across
the complete ledger chain. The full redacted receipt, route blockers, exact
metrics, parse accounting, and QA evidence are in
[`MODERN_FULL_RECEIPT.md`](MODERN_FULL_RECEIPT.md).

The requested `gemini-3.7-flash` route remained blocked by HTTP 403, the
Vermont Qwen route remained blocked by HTTP 500 endpoint-not-found, and a
`gemini-3.6-flash` PA probe also returned HTTP 403. No full-screen claim is
made for those model IDs. The temporary EC2 instance was stopped and verified
stopped. The earlier “live gate closed/no provider calls” entries below are
historical pre-run records and are superseded by this addendum.

| Deliverable | State | Evidence |
|---|---|---|
| Historical Flash 2 reference and fixed shortlist | VERIFIED / FROZEN | `GOALS_AUDIT.md`, `SHORTLIST_EVIDENCE.md`, and `GT_LINEAGE.md` |
| Modern Gemini transfer screen | COMPLETE for Flash 3.5 and Flash-Lite 3.5 | 11,196 terminal raw responses; strict analyzer PASS |
| Cross-model metrics and deployment analysis | COMPLETE with 95% target unmet | `outputs/derived/*.csv`; no modern operating point fabricated |
| C1–C9 figures | COMPLETE | 18 generated SVG/PNG files under `outputs/figures/` |
| Reproducible QA and receipt | COMPLETE | 210 tests PASS, validator PASS, analyzer rerun identical |
| 3.7 and Qwen full screens | BLOCKED / NARROWED | Model-specific route failures documented in `MODERN_FULL_RECEIPT.md` |

---

# GT-lineage resolution addendum — 2026-08-30 America/Denver

The ground-truth investigation is no longer blocked at the field-selector or
historical-exclusion level. The paper-era selector is the six name fields
listed in [`docs/GT_LINEAGE.md`](../docs/GT_LINEAGE.md). The historical
`chat2rec/processing/common.py::_add_flags` logic is recovered, including its
wider scan scope, five substring terms, and `Self*` row removal. On the newer
paper-lineage processed GT it flags 24 records, yielding
`622 × 6 − 24 × 2 = 3,684` historical row slots.

The v9/v10 consensus artifacts contain 3,683 rows with `f_gt_missing=0` plus
one retained blank row, even though their analysis config requests
`f_gt_missing: 0`. That blank-row reconciliation is now an explicit caveat,
not an unknown 34-row filter. The raw `_edt` six-name count of 3,718 is a
different pre-filter statistic. The older `f1b978...` processed GT remains the
public-release/v7 lineage and produces the separate 3,682-row products.

Current documentation consequence: existing `icdar_tta` derived tables and
charts remain labeled as legacy/public v7 evidence; no historical metric is
silently relabeled as a paper-v9/v10 recomputation. The remaining closed-gate
wording in the historical records below describes the state before the modern
screen authorization and execution; the completion addendum at the top is the
current result. No provider call was made by this documentation update.

---

# Modern label-blind smoke addendum — 2026-08-29 America/Denver (2026-08-30 UTC)

A subsequent bounded smoke ran after the offline handoff. It used three
predeclared source documents, the `U0` unchanged-repeat view, and two Gemini
IDs: `gemini-3.5-flash` and `gemini-3.5-flash-lite`. All six provider requests
returned `ok`, with six exact returned-model IDs, zero retries, and zero
recorded failures. The six-row redacted metadata table is
`outputs/derived/modern_smoke_metadata.csv`; the receipt is
`local_agent/MODERN_SMOKE_RECEIPT.md`.

This is route/parser/usage evidence only. It does not expose model
transcription values, source/rendered image bytes, or private response bodies;
those remain outside Git. It does not test `gemini-3.7-flash` or Qwen, does
not open ground-truth labels, and does not make an accuracy/CER/precision/
coverage claim at that checkpoint. The full scored transfer was subsequently
completed for the two executable Gemini 3.5 models; the completion addendum at
the top supersedes this pre-call gate status.

The pre-call material below remains a historical record of the earlier freeze.

---

# Git publication handoff addendum — 2026-08-29

The portable handoff is prepared for Git publication. It includes the
offline analysis package, ten derived historical tables, all 18 required chart
files, source/hash manifests, receipts, tests, and the code-only modern view
renderer/request runner. The modern runner requires the optional `modern`
dependencies and private render/prompt inputs; gateway bases and credentials
are environment-provided, and raw responses remain outside Git. No provider
call or inference was made during preparation. The six-field historical rule
is recovered; the v9/v10 blank-row convention, exact historical render lineage,
and modern execution gates remain open as documented below.

---

# Raw per-field database probe — 2026-08-29

The exact historical per-field database was reached through a resumed Sol 5.6
Max Kiro task using one bounded, non-RTK streaming pass. No provider/API/
network/inference call, credential access, raw response read, image read, or
row-value export occurred.

The historical per-field database (logical alias
`HISTORICAL_WARP_METRICS_DB`; its machine-specific path is retained only in
ignored `config/data_manifest.local.yaml`) is 23,014,921 bytes with SHA-256
`34cce8d33ce772af0fce762549b2d89b2c166e8c7e55cc21bdcfb332949ffb96` and
68,880 data rows. It has eight schema `field_name` tokens; aggregate flags are
`f_gt_missing`: 68,866 zero / 14 one, and
`f_flag_for_human_review`: 68,880 zero. The immediate directory had 30
entries, with no name matching `canonical`, `filter`, or `generator`.

This is useful raw metadata but does not define a standalone paper-lineage
3,684 `doc_id`/`field_name` list. `config/canonical_field_filter.csv` remains
uncreated because no label-bearing filter file is needed for, or fabricated
from, this metadata probe. The recovered code-level rule and its row semantics
are in
`local_agent/CANONICAL_FILTER_RAW_PROBE_AUDIT.md`; the Kiro runtime ledger
records the interrupted PTY and exact-session resume.

A final canary-verified Sol aggregate pass counted all `f_` columns and safe
experiment/category controls in the same CSV. It found zero malformed rows,
no reported group with 3,684 rows, and no directly named filter/generator in
the immediate directory. It did not compute or export distinct document/field
pairs, combine flags, or inspect row values. The negative/partial evidence is
in `local_agent/CANONICAL_FILTER_STATUS_AGGREGATE_AUDIT.md`; that audit remains
negative only for a standalone filter artifact in the legacy database.

---

# Source-manifest follow-up — 2026-08-29

Scope: later bounded source-candidate audit after the final-QA pass. No provider/API/network call, inference, staging, commit, clean, or reset occurred.

The exact source candidate is now verified: 623 direct files, consisting of 622
JPEG source documents and one unextracted `622.zip` sidecar; 622 unique document
IDs and per-file hashes; zero filename-stem differences against the verified
622-mask set. The source collection hash is
`c1c1bd78585d34da500d94cb4c838cdcd664f9d2f19615158d4e312c29afd769`.

`config/source_image_manifest.csv` contains 622 deterministic rows and
`config/source_image_manifest.sha256` records the manifest hash
`7ad5e7a065bf8bd262953d8faf8e34344e861333c4655eff72bf80aee90f25ee`.
The portable manifest contains no machine-specific paths, image bytes, or label
text. This supersedes only the source-identity wording in the earlier addendum;
the v9/v10 blank-row convention, exact-render, route, and authorization
blockers remain active. The shared parser/retry gate was subsequently closed
offline; see
local_agent/PARSER_RETRY_AUDIT.md.

A second expanded, fixed-shortlist search also found no standalone artifact or
generator for an exported 3,684-pair key list; see
local_agent/CANONICAL_FILTER_EXPANDED_AUDIT.md. This does not reopen the
recovered code-level rule; the remaining paper-lineage task is to recompute and
freeze the blank-row reporting convention.

| Deliverable | State | Evidence / remaining limitation |
|---|---|---|
| Exact 622 source-image identity and hash manifest | VERIFIED | Source candidate has 622 unique JPEGs, zero mask-stem differences, and a deterministic portable manifest plus sidecar. |
| Offline parser, retry policy, and request ledger | VERIFIED / TESTED | Exact implementation hashes and 40/21/24 focused tests are recorded in `PARSER_RETRY_AUDIT.md` and `REQUEST_LEDGER_AUDIT.md`; this closes only the offline sub-gates. |
| Paper-lineage six-field/3,684-row contract | VERIFIED WITH CAVEAT | Selector and 24-record historical `Self*` exclusion are recovered; v9/v10 retain one blank row and a dedicated paper-lineage recomputation still needs to freeze its strict-nonblank reporting convention. See `docs/GT_LINEAGE.md`. |
| Nine-view render/source/mask/payload lineage | BLOCKED | Source identity and mask coverage are verified, but the historical Pad adapter, deterministic Grid seeds/render hashes, and executable transport rule remain missing; see `RENDER_LINEAGE_AUDIT.md`. |
| Modern Flash 3.7, Flash-Lite 3.5, and Qwen transfer | BLOCKED / GATED | Source identity, offline parser/retry gate, and offline request-ledger gate are resolved; paper-lineage row convention, exact nine rendered views, route smokes, Qwen keepalive change, budget review, and live authorization remain unresolved. |

---

# Final-QA addendum — 2026-08-29

Scope: final-QA verification pass over repository HEAD
`cebf7778cea92692da9837f8914ae0b61a29c399`. No provider/API/network call,
inference, staging, commit, clean, or reset occurred. No file was edited other
than this addendum and the new `local_agent/FINAL_RECEIPT.md`. Full detail,
including all ten source CSV row counts/SHA-256 values, the nine chart
basenames with the C4 label-overlap repair and the C6/C9 blocked-evidence
semantics, exact model/prompt/transform IDs, the request budget ledger, and
the precise closed-gate blockers, is recorded in `local_agent/FINAL_RECEIPT.md`.

## Final deliverable state

| Deliverable | State | Evidence / remaining limitation |
|---|---|---|
| Historical Flash 2 inventory and transform shortlist | VERIFIED / FROZEN | Existing evidence is reuse-only; the three Pad IDs and three mild Grid-Warp IDs are recorded with provenance. |
| Offline PA parser, retry policy, lineage, consensus, and metrics | IMPLEMENTED / TESTED | Strict PA v1.49 parser and deterministic retry policy pass offline; exact hashes are frozen in `EXPERIMENT_MATRIX.md` and `PARSER_RETRY_AUDIT.md`; live route/render lineage remains gated. |
| Historical reanalysis tables | VERIFIED | Ten deterministic CSVs are present with independent row-count and SHA-256 checks in `local_agent/FINAL_RECEIPT.md`. |
| Presentation evidence | VERIFIED | All nine required C1–C9 basenames exist as SVG and PNG; C4 is repaired; C6/C9 explicitly show blocked evidence. |
| Modern Flash 3.7, Flash-Lite 3.5, and Qwen transfer | BLOCKED / GATED | No provider calls or modern labels were used; source identity, the six-field rule, and parser/retry evidence are verified, while paper-row/render/mask/route/authorization prerequisites remain unresolved. |
| Final receipt and handoff | VERIFIED | `local_agent/FINAL_RECEIPT.md` records commands, IDs, counts, budget, blockers, and the narrowed claim. |

Checks reconfirmed in this pass:

- `git rev-parse HEAD` / `git status --porcelain=v2 --branch` — HEAD matches,
  working tree unchanged apart from the pre-existing dirty/untracked state
  already on record below.
- `python3 -m compileall -q scripts tests src` — exit 0, no output.
- `PYTHONPATH=src python3 -m unittest discover -s tests` — `Ran 158 tests`,
  `OK` (includes `tests/test_validate_cli.py`).
- `PYTHONPATH=src python3 -m icdar_tta.validate --manifest config/data_manifest.local.yaml` — exit 0,
  `Overall: PASS (0 hard failure(s))`, with the documented no-field-table gate skipped.
- All 10 files in `outputs/derived/*.csv` independently re-hashed
  (`sha256sum`) and re-counted (`wc -l`, `stat -c%s`); all values match
  `local_agent/CHART_RECEIPT.md` exactly.
- Chart regeneration and the 18-file byte-identical temporary-directory
  comparison were independently rerun by the project manager after this
  addendum was written; all 18 files matched and the exact temporary directory
  was removed. The C4 row-label-overlap fix remains recorded in
  `local_agent/CHART_RECEIPT.md`.
- Modern-provider live-request gate confirmed **still closed**; no paid call
  was made or authorized. See `local_agent/FINAL_RECEIPT.md` for the full
  closed-gate blocker list.

Deliverable added in this pass: `local_agent/FINAL_RECEIPT.md`.

---

# Current targeted follow-up status — 2026-08-29

Scope: second bounded historical-selection and modern-route pass. Required canary passed. No provider/API/network call, inference, staging, commit, clean, or reset occurred. Protected pre-existing edits were not touched.

## Deliverables now present

| Artifact | State | Key result |
|---|---|---|
| `local_agent/EXPERIMENT_MATRIX.md` | Created; conditions frozen, live gate closed | All three requested exact IDs; 622×9 roles; three Pad and three Grid IDs; prompt/schema/parser contract; no-label-tuning and no-Flash-2 rules |
| `local_agent/request_budget.json` | Created | 16,794 scored; 3,190 reserve; 0 spent; 19,984 worst case; 16 remaining |
| `local_agent/ROUTE_AUDIT.md` | Created | Direct Gemini recommended only after requested-ID smoke; exact-ID batch fallbacks documented; Qwen keepalive/prompt-lineage blockers explicit |
| `local_agent/SHORTLIST_EVIDENCE.md` | Created | Full active WARP inventory/ranks; first-three Pad rule; implementation wiring; GT schema/hash discrepancy |
| `local_agent/GOALS_AUDIT.md` | Refined | Provisional shortlist superseded by exact v4/fixed-source-order rules |
| `local_agent/HISTORICAL_INVENTORY.md` | Refined | Exact counts, hashes, route IDs, and remaining provenance caveats added |

## Gate and next checkpoint

**Next gate remains closed.** The exact 622-image/hash manifest, six-field historical rule, shared offline parser/retry gate, and offline request-ledger gate are now verified. Before any paid call: freeze the paper-lineage blank-row convention; render/hash all nine views and prove mask coverage; obtain project-owner acceptance of the pure-warp projection; independently approve the 19,984 worst-case ledger; then run exactly three label-blind lineage smokes per exact model and verify returned IDs. Qwen must disable redundant keepalive during active scored traffic and bind prompt ID/hash directly.

Historical Gemini 2.0 Flash remains reuse-only. Modern labels remain unopened for transform/threshold selection.

---

> **Everything below this line is the original bounded-inventory-pass
> status report.** It is retained as an audit trail per `AGENTS.md`. Where
> a row or statement is contradicted by the resolution above, it is marked
> **SUPERSEDED** inline rather than deleted. Rows not marked superseded
> reflect state that had not changed as of this file's last update.

# Local agent status

Last updated: 2026-08-29 (WSL session, bounded-root inventory pass)

Scope of this pass: bounded, read-only inventory of six named evidence roots per
project-manager instruction. No provider/API calls, no inference, no staging,
commit, clean, or reset were performed. The earlier unbounded recursive scan of
`the user profile root` was not resumed.

## Roots inspected

| Root | Status | Notes |
|---|---|---|
| `repository pa-death-records-622` | Available | Public-release-style repo: `LICENSE.md`, `RELEASE_NOTES.md`, `DATA_DICTIONARY.md`, `examples/` with 2 sample images + `example_labels.csv`, `scripts/verify_release.py`. Small (11 files). |
| `PA_DEATH historical root` | Available | Large historical run tree (396 files at depth 3, more below). Contains `BIG_SHIFT/`, `CONSISTENCY/`, `CVPR_ANALYSIS/`, `LINE_THICKNESS/`, `MONOTONIC_DEGRADATION[2]/`, `PROMPT_VARIATION[_GPT]/`, `ROTATE/`, `SHIFT/`, `WARP/`, `prompts/`, `temp_downloads/`. |
| `repository chat2rec_analysis/projects/pa_death_records622_official` | Available | Very large (13,835 files at depth 3). Multiple `analysis - v1..v7` + `v6a` snapshots, each with `best_consensus_CER/` and `paper/` subfolders; `gemini/` (raw responses, 12,499 files); `gemini - confidence_analysis/` (1,250 files); `backup/`, `metrics_no_punc/`, `paper/`. |
| `repository ancestry/chat2rec_v1/chat2rec/degradations` | Available | Transform implementation source (42 files). `effects/gridwarp.py`, `gridwarp2.py`, `handwriting_aware_gridwarp*.py`, `shift.py`, `blur.py`, `resize.py`, `seamcarve*.py`, `composite.py`, plus `apps/*_gui.py` visual debug tools. |
| `repository ancestry/vermont` | Available | Modern-model execution repo (215 files at depth 3). `deploy/` (dispatcher, worker, S3/SQS/ECS infra under `deploy/infra/*.tf`), `models/example/`, and — one level deeper — `63129.IDX.003_field_extraction/scripts/{qwen_warmup_and_smoke,run_qwen_cells,smoke_qwen*}.py`. |
| `repository ancestry/ds-content-raptor` | Available | Framework/tickets repo (321 files at depth 3). `.tickets/TICKET-001..020`, `63129.IDX.003_field_extraction/{AGENTS.md,BATCH_PIPELINE.md,RESULTS_SUMMARY.md,BROWN_BAG_2026_08_19/*}`. Note: this path and the Vermont repo both contain a `63129.IDX.003_field_extraction` subtree — see Goals Audit for the discrepancy. |

No root was unavailable, permission-denied, or timed out during this pass. All six were listed successfully within the time-boxed commands (≤20s each).

## Required outcomes tracker (from `local_agent/TASK.md`)

| # | Outcome | Owner | Artifact | State | Blocker | Next checkpoint |
|---|---|---|---|---|---|---|
| 1 | Freeze historical Flash 2 reference (evidence + transform shortlist) | local agent | `local_agent/GOALS_AUDIT.md`, `config/data_manifest.yaml`, `config/data_manifest.local.yaml` | **SUPERSEDED — now Frozen.** (Original row, kept for audit trail: "In progress — evidence located, shortlist drafted from `PA_DEATH/WARP/PA_DEATH_WARP.yaml` and `PA_DEATH/WARP/metrics_no_punc/ensemble_selection_analysis.tsv`; not yet independently re-verified against `analysis - v7` (chat2rec side) for consistency.") See the "Frozen historical decision" section at the top of this file's `GOALS_AUDIT.md`/`HISTORICAL_INVENTORY.md` addenda for the exact resolved shortlist and IDs. The `analysis - v7` cross-check against chat2rec remains explicitly **not yet performed** — that specific follow-up is still open. | Cross-check against chat2rec `analysis - v7/paper/transform_metrics_table.tex` still open | Perform the `analysis - v7` cross-check before treating the shortlist as independently corroborated from a second source |
| 2 | Modern-model screen (Flash 3.7 / Flash-Lite 3.5 / Qwen) | project manager + Kiro | `local_agent/EXPERIMENT_MATRIX.md`, `local_agent/request_budget.json` | **SUPERSEDED — now Gated, not Not-started.** (Original row: "Not started — No live-request gate artifacts exist yet.") `EXPERIMENT_MATRIX.md`, `request_budget.json`, `ROUTE_AUDIT.md`, and `SHORTLIST_EVIDENCE.md` now exist with exact model IDs, transform IDs, and a 16,794/3,190/0/19,984 scored/reserve/spent/worst-case ledger. **No paid call is authorized yet** — the live-request gate remains closed pending the paper-row convention, render, parser, and route-smoke prerequisites listed at the top of this file. | Live-request gate closed (see top-of-file "Gate and next checkpoint") | Freeze paper-lineage row convention; run label-blind lineage smokes per model |
| 3 | Confidence/quality/transfer analysis | local agent / Kiro | tables under `outputs/` | **Not started** (unchanged) | Depends on outcome 2, which remains gated | — |
| 4 | Presentation charts C1–C9 | Kiro (chart generation) | `docs/CHART_PLAN.md` targets | **Not started** (unchanged) | Depends on outcomes 1–3 | — |
| 5 | Reproducible QA / final receipt | local agent | `local_agent/FINAL_RECEIPT.md` | **Not started** (unchanged) | Depends on all above | — |

## This session's deliverables

- `local_agent/STATUS.md` (this file)
- `local_agent/GOALS_AUDIT.md` — one-page historical transform shortlist decision
- `local_agent/HISTORICAL_INVENTORY.md` — detailed per-root file/evidence inventory
- `config/data_manifest.yaml` — portable, redacted manifest (safe to commit)
- `config/data_manifest.local.yaml` — machine-specific manifest (gitignored, not committed)

## Explicit non-actions in this pass

- No `git add`, `commit`, `clean`, or `reset` was run.
- No files under `docs/`, `README.md`, or `outputs/README.md` were edited.
- No provider/API/model calls were made.
- No files were copied out of the external roots into this repository; only paths, counts, and metadata were recorded.
- Pre-existing dirty files (`.gitignore`, `README.md`, `docs/CHART_PLAN.md`, `docs/EXPERIMENT_PLAN.md`, `outputs/README.md`, untracked `local_agent/`) were left untouched by this pass except for the new files listed above under `local_agent/` and `config/`.
