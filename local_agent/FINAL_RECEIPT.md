# Historical offline handoff receipt — superseded only by the separate smoke addendum

This receipt records the offline preparation state as of 2026-08-29. A later
small label-blind Gemini smoke is documented in
`local_agent/MODERN_SMOKE_RECEIPT.md`; its metadata is separate and does not
alter the historical claims or the closed full-transfer gate below.

---

# Raw per-field database probe — 2026-08-29

Sol 5.6 Max Kiro completed a resumed, bounded metadata pass over the exact
historical per-field database. The file is 23,014,921 bytes,
SHA-256 `34cce8d33ce772af0fce762549b2d89b2c166e8c7e55cc21bdcfb332949ffb96`,
and contains 68,880 data rows across eight schema field names. Safe aggregate
flags were `f_gt_missing`: 68,866 zero / 14 one, and
`f_flag_for_human_review`: 68,880 zero. The immediate directory contained 30
entries and no filename matching `canonical`, `filter`, or `generator`.

This probe does not establish the exact canonical 3,684 `doc_id`/`field_name`
filter. No filter was synthesized, no row values or private data were emitted,
and no provider/network/inference call occurred. Evidence and literal offline
checks are recorded in
`local_agent/CANONICAL_FILTER_RAW_PROBE_AUDIT.md`; the exact Kiro interruption
and resume are retained in ignored `local_agent/runtime/` state.

A final canary-verified Sol aggregate pass counted all `f_` columns and safe
experiment/category controls. It found zero malformed rows, no reported group
with 3,684 rows, and no directly named filter/generator in the immediate
directory. It did not compute distinct document/field pairs or combine flags;
the negative/partial result is recorded in
`local_agent/CANONICAL_FILTER_STATUS_AGGREGATE_AUDIT.md`.

Independent post-probe QA passed: `compileall` exited 0; the full suite ran 207
tests with `OK`; both manifests validated with `Overall: PASS (0 hard
failure(s))`; both YAML documents parsed; report redaction/marker checks passed;
the Kiro ledger contained 33 rows with zero active sessions; the source
manifest check found 622 unique IDs and hashes; the frozen budget remained
16,794 scheduled + 3,190 reserved = 19,984 worst-case requests; and
`git diff --check` exited 0.

---

# Offline gate follow-up — 2026-08-29

This follow-up records the final offline implementation and recovery checks
after the earlier receipt. No provider/API/network call, inference, credential
access, raw-response read, private-image copy, commit, clean, reset, or checkout
occurred. Repository HEAD remains `cebf7778cea92692da9837f8914ae0b61a29c399`
on `master`.

Completed offline gates:

- Source identity: 622 unique JPEG documents, source manifest SHA-256
  `7ad5e7a065bf8bd262953d8faf8e34344e861333c4655eff72bf80aee90f25ee`, source
  collection SHA-256
  `c1c1bd78585d34da500d94cb4c838cdcd664f9d2f19615158d4e312c29afd769`.
- Parser: `pa_v149_json_repair_v0`, implementation SHA-256
  `656366a6215d008dd443abae45603e1a628513b5331a4752928e35fbb3ff9fde`.
- Retry policy: `provider_neutral_retry_v1`, implementation SHA-256
  `b35f840a7cd0d8969e250fa62f89fef5a31ee7afc99232c03130e8b5ac4f7f0d`.
- Request ledger: implementation SHA-256
  `6c727ee40ccada307f185d6c6ad56c2b5c608d7d2dc20a66ead9c76460929479`.
- Offline verification: 207 unittest cases, compileall, both-manifest
  validator, YAML parse, redaction, exact-byte hash, and `git diff --check`
  all pass. The 18 C1–C9 SVG/PNG files also pass an independent deterministic
  regeneration comparison.

The canonical-filter search was run twice: first over the bounded historical
scope and then over a fixed expanded shortlist of named non-raw code/config/
report artifacts. Neither found a named artifact or generator producing exactly
3,684 `doc_id`/`field_name` pairs; no filter or checksum sidecar was fabricated.
The render-lineage audit likewise remains BLOCKED because the historical Pad
adapter, deterministic Grid-Warp seed/render hashes, and executable transport
rule are not recoverable from the inspected evidence.

The modern live-call gate therefore remains **CLOSED**. Remaining blockers are
the canonical filter, nine-view render/payload lineage, route and transport
smokes, Qwen keepalive change, independent budget approval, and explicit live
authorization. See `local_agent/CANONICAL_FILTER_EXPANDED_AUDIT.md`,
`local_agent/RENDER_LINEAGE_AUDIT.md`, `local_agent/PARSER_RETRY_AUDIT.md`, and
`local_agent/REQUEST_LEDGER_AUDIT.md` for evidence.

---

# Source-manifest follow-up addendum — 2026-08-29

The exact source-input candidate identified by the historical run settings was
audited in a later bounded, offline pass. No provider/API/network call,
inference, staging, commit, clean, reset, or raw-image copy occurred.

- Direct source-candidate inventory: 623 files = 622 JPEGs plus one unextracted
  `622.zip` sidecar.
- Stable identity: 622 unique document IDs, 622 unique per-file SHA-256 values,
  and zero source/mask filename-stem differences.
- Source collection SHA-256 (sorted relative-name, byte-size, file-hash lines):
  `c1c1bd78585d34da500d94cb4c838cdcd664f9d2f19615158d4e312c29afd769`.
- Portable manifest: `config/source_image_manifest.csv`, 622 data rows, with
  SHA-256 `7ad5e7a065bf8bd262953d8faf8e34344e861333c4655eff72bf80aee90f25ee`;
  sidecar: `config/source_image_manifest.sha256`.
- Independent checks: manifest rebuilt from the runtime TSV, compared byte for
  byte, and cross-checked with `sha256sum`; all matched. Portable files contain
  no machine-specific paths, image bytes, label text, or credentials.

The source-document identity/hash gate is therefore **PASS**. The canonical
3,684-field filter, exact nine-view render lineage, route smokes, Qwen keepalive
change, budget approval, and project-manager live
authorization remain **BLOCKED**. No modern call is authorized by this
addendum.

The shared parser/retry gate and the provider-neutral request-ledger gate are
offline-PASS. Canonical fingerprints, append-only JSONL history, explicit
malformed/transition handling, and fingerprint-guarded resume behavior are
implemented and tested in `src/icdar_tta/request_ledger.py`; a real
provider-backed ledger and live reconciliation still require the blocked route,
render, and authorization gates.

The canonical-filter search was independently expanded to the fixed historical
shortlist and named non-raw code/config/report artifacts. It still found no
evidenced 3,684-pair artifact or generator; the negative result is recorded in
`local_agent/CANONICAL_FILTER_EXPANDED_AUDIT.md` and no filter was fabricated.

---

# Final QA receipt — 2026-08-29

Status: **final-QA pass complete for the artifacts owned by this receipt.** This
document records the checks performed in this session against repository HEAD
`cebf7778cea92692da9837f8914ae0b61a29c399` (branch `master`, tracking
`origin/master`, `+0 -0`). No provider/API/network/inference call was made. No
`git add`, `commit`, `clean`, or `reset` was run. No file other than this one and
`local_agent/STATUS.md` (addendum only) was written.

## Pre-existing working-tree state (observed, not caused by this pass)

Modified but not staged (pre-existing, left untouched):
`.gitignore`, `README.md`, `docs/CHART_PLAN.md`, `docs/EXPERIMENT_PLAN.md`,
`outputs/README.md`.

Untracked (pre-existing, left untouched except the two files this receipt owns):
`config/data_manifest.yaml`, `local_agent/`, `outputs/derived/`,
`outputs/figures/`, `pyproject.toml`, `scripts/`, `src/`, `tests/`.

## Checks performed and reconfirmed in this session

| Check | Command | Result |
|---|---|---|
| HEAD / status / diff | `git rev-parse HEAD`; `git status --porcelain=v2 --branch` | HEAD `cebf7778cea92692da9837f8914ae0b61a29c399`; working tree matches the pre-existing state above; no unexpected changes |
| Byte-compile | `python3 -m compileall -q scripts tests src` | Exit 0, no output — all `.py` files under `scripts/`, `tests/`, and `src/` compile cleanly |
| Full test suite | `PYTHONPATH=src python3 -m unittest discover -s tests` | `Ran 158 tests in 2.337s` — `OK` (0 failures, 0 errors) |
| Offline validator | `PYTHONPATH=src python3 -m icdar_tta.validate --manifest config/data_manifest.local.yaml` | Exit 0, `Overall: PASS (0 hard failure(s))`; six PASS/skipped-gate lines (self-check normalize/parser/consensus, portable manifest, local manifest, and the documented no-field-table skip) |
| Validator tests | `tests/test_validate_cli.py` (one module of the 158-test suite above) | Included and passing in the same full-suite run |
| Chart regeneration + independent byte comparison | `python3 scripts/generate_charts.py --derived-dir outputs/derived --figure-dir outputs/figures`, plus independent reruns into fresh temporary directories recorded in `local_agent/CHART_RECEIPT.md` and final project-manager QA | 18/18 output files byte-identical (`cmp -s`) in the final QA rerun; temporary directory removed after comparison; all 10 source CSV hashes independently reconfirmed below |
| Source CSV integrity (independent recomputation) | `wc -l`, `stat -c%s`, `sha256sum` on each file in `outputs/derived/*.csv` | All 10 files match `local_agent/CHART_RECEIPT.md` exactly (see table below) |
| Metadata / temporary-directory checks | Inspection of SVG `<metadata>` blocks and confirmation the `mktemp -d` rerun directory was removed | No absolute paths, URLs, or credential tokens found in SVG metadata; temporary directory not present in working tree |

## Ten source CSV row counts and SHA-256 values (independently recomputed)

Row counts exclude the header row. Paths are repository-relative.

| CSV | Rows | Bytes | SHA-256 |
|---|---:|---:|---|
| `outputs/derived/augmentation_contribution.csv` | 5 | 2,427 | `6d6e2c4be232d77e94ee31560bbc327c04e9596721a79e34c456e78b6f1ceab6` |
| `outputs/derived/cost_by_run.csv` | 4 | 911 | `bad4ed762ddf9761a6ea3b57171f26e3a8086c225d3672e4c023837fba17e665` |
| `outputs/derived/cross_model_operating_points.csv` | 14 | 5,145 | `ee1c9f00ccfa5014ab34c69a1a4c07d2870277f513ee9a5a4e1a5f79b7b4b438` |
| `outputs/derived/ensemble_size.csv` | 53 | 24,457 | `3deecacbf92eb76b17521adbef3e3294cbb4fe49dd96a68f02abd3d09b79d0cf` |
| `outputs/derived/error_correlation_summary.csv` | 12 | 5,368 | `93157ddd6c16b8f928df5f32cc6b29d353b0cea2b921c71d8a158473d90b985b` |
| `outputs/derived/failure_examples.csv` | 1 | 495 | `c4ecf82d3d5e5c0f909d0992cd2b3a3acaf0e3b2d87130b49c22541618b54b55` |
| `outputs/derived/precision_coverage.csv` | 1,750 | 998,692 | `619210cd328762df6b87b8195f18d506bf61dcfa236c44e27c207b31d83bd53a` |
| `outputs/derived/review_frontier.csv` | 3 | 1,667 | `3192b4c711a30e15ffb3febd8c6cd8f3c0ecf203ba5c61456787157c7c03f4de` |
| `outputs/derived/shift_agreement.csv` | 130 | 54,974 | `3e18fa536faf11992ae55ed8b5901f5a0d4c6b7ac1e394f07851d86158e77e96` |
| `outputs/derived/strategy_summary.csv` | 31 | 15,951 | `815c0d66b688f75cb736fe7765979dc14ad67ab370407e1804ff12981977f9c7` |

## Nine chart basenames, C4 repair, and C6/C9 blocked semantics

All nine required chart IDs are rendered as both `.svg` and `.png` (18 files
total) under `outputs/figures/`, deterministically from the 10 CSVs above via
`scripts/generate_charts.py`. Renderer uses only Python standard-library
modules; no matplotlib, Pillow, numpy, external fonts, images, or private
roots are used.

| ID | Basename | Numeric input(s) | Status / semantics |
|---|---|---|---|
| C1 | `01_useful_diversity` | `strategy_summary.csv` | 10 measured WARP per-condition coordinates rendered; selected v7 category rows shown separated as consensus-only (no correlation coordinate, not individual CER) |
| C2 | `02_effective_sample_size` | `error_correlation_summary.csv` | Code-generated theoretical N=10 curve plus 10 measured WARP correlations projected onto it; family-level Grid Warp/Resize correlations remain visibly blocked, not promoted from prose |
| C3 | `03_precision_coverage` | `precision_coverage.csv` | All 1,750 raw-agreement threshold rows (Grid Warp, Pad, Resize) with supplied 95% Wilson bounds; 3,682-row denominator labeled noncanonical; score labeled raw/not calibrated |
| C4 | `04_cost_review_frontier` | `cost_by_run.csv`; `review_frontier.csv` | **Repaired in this lineage.** Prior pass had the strategy label (e.g. "GRID WARP (N=...") drawn at x=90 immediately left of a bar starting at x=250, bleeding behind the bar. Fix in `chart_4`: the strategy label now sits on its own text line above the bar at the full left margin (x=90), and the bar/track was widened to span x=90–670, so the label cannot overlap the bar regardless of name/sample-size length. One numeric review-burden coordinate is rendered; all four cost rows lack observed usage/pricing, so the cost axis and Pad/Resize target coordinates remain visibly blocked — no dollar figure was invented |
| C5 | `05_shift_periodicity` | `shift_agreement.csv` | All 130 reported horizontal/vertical points plus 16-pixel guides; periodicity labeled observational, not architecture proof |
| C6 | `06_cross_model_coverage` | `cross_model_operating_points.csv` | **Blocked-semantics chart.** One measured historical Grid Warp point (Gemini-2.0-Flash, rendered as a green dot, "40.4%" / "P=95.23%") and one historical Pad target-not-met row are shown; the remaining 12 cells across the three exact modern model IDs are explicit red BLOCKED cells. No modern-model result is implied or invented |
| C7 | `07_augmentation_contribution` | `augmentation_contribution.csv` | All five family selection counts and source descriptors; selection frequency labeled descriptive, not causal contribution |
| C8 | `08_ensemble_size` | `ensemble_size.csv` | 23 key rows across five source-reported series from the 53-row table; ~4,920-field denominator labeled noncanonical |
| C9 | `09_failure_examples` | `failure_examples.csv` | **Blocked-semantics chart.** Renders a blocked evidence panel from the single available source row; no prediction, ground truth, crop, or private path is copied, because stable redacted lineage and crop-release authorization remain unavailable |

Each SVG embeds a machine-readable `<metadata>` object (chart ID, 1,200x675
dimensions, numeric input filenames, renderer, one-sentence takeaway,
limitations); the same takeaway appears as a visible subtitle. Measured,
theoretical, reported, recomputed, and blocked roles are visually and
textually distinguished throughout.

## Model / prompt / transform IDs (from `local_agent/EXPERIMENT_MATRIX.md` and `local_agent/request_budget.json`)

Exact modern-model IDs approved for the (still-gated) replication pass:

- `gemini-3.7-flash`
- `gemini-3.5-flash-lite`
- `sagemaker-qwen3-vl-8b-instruct-fp8`

Prompt: ID `prompt_v1.49_confidence`, SHA-256
`fd119108d3ef4dbf2f88984511d9f903b7d4c98b032a95c327a21f713335e48e`.

Parser: specification ID `pa_v149_json_repair_v0`; implementation SHA-256
`656366a6215d008dd443abae45603e1a628513b5331a4752928e35fbb3ff9fde`.
Provider-neutral retry policy: ID `provider_neutral_retry_v1`; implementation
SHA-256 `b35f840a7cd0d8969e250fa62f89fef5a31ee7afc99232c03130e8b5ac4f7f0d`.
Both are offline-tested; see `local_agent/PARSER_RETRY_AUDIT.md`.

Transform scope: three unchanged-repeat calls, three Pad calls, three Grid-Warp
calls per image (9 views), fixed from the historical shortlist in
`local_agent/GOALS_AUDIT.md` / `local_agent/SHORTLIST_EVIDENCE.md` — three Pad
IDs and three Grid-Warp IDs, chosen without opening modern labels. Historical
reference model remains `Gemini 2.0 Flash` (reuse-only; no new calls to it are
authorized).

Frozen view transform IDs (all nine, exact):

- `U0` = `unchanged_repeat.0`
- `U1` = `unchanged_repeat.1`
- `U2` = `unchanged_repeat.2`
- `P0` = `shift_only.variant_00`
- `P1` = `shift_only.variant_01`
- `P2` = `shift_only.variant_02`
- `G0` = `dont_warp_text_and_lines_d003_r30_s10_std15`
- `G1` = `warp_all_d003_r30_s10_std15`
- `G2` = `warp_hw_only_dont_warp_text_and_lines_d003_r30_s10_std15`

## Budget (from `local_agent/request_budget.json`)

| Field | Value |
|---|---:|
| Hard cap | 20,000 |
| Cohort images | 622 |
| Views per image | 9 |
| Scored requests (3 models × 622 × 9) | 16,794 |
| Reserve (smoke + Qwen keepalive + retries + reconciliation) | 3,190 |
| Spent | 0 |
| Worst-case total (spent + scheduled + reserved) | 19,984 |
| Remaining after worst case | 16 |

Reserve breakdown: 9 smoke calls (3 predeclared images × 3 models); 81 Qwen
warmup/keepalive calls (1 initial + up to 80 pings at 15s intervals in a
20-minute window, disabled during active scored traffic); 3,000 shared
retry/capacity-failure reserve (stop after 5 consecutive network/capacity
failures); 100 ambiguous-submission reconciliation contingency (no blind
resubmission).

## Closed modern-provider gate and precise blockers

**The live-request gate remains closed. No paid provider call has been made or
is authorized by this receipt.** Per `local_agent/STATUS.md` and
`local_agent/EXPERIMENT_MATRIX.md`, all of the following must be satisfied
before any scored/smoke call:

1. Recover and verify the canonical 3,684-field filter (the exact 622-image/hash
   manifest is now verified; current derived tables use a 3,682-row denominator,
   explicitly labeled noncanonical in C3/C8 pending this reconciliation).
2. Render and hash all nine per-image views (3 unchanged, 3 Pad, 3 Grid-Warp)
   and prove mask coverage against the source images.
3. Obtain project-owner acceptance of the pure-warp projection used in the
   historical shortlist.
4. Independently approve the 19,984 worst-case request ledger above.
5. Run exactly three label-blind lineage smokes per exact model ID and verify
   the returned IDs match the requested IDs.
6. Qwen-specific: disable the runner's always-on 15-second keepalive thread
   during active scored traffic; bind prompt ID/hash directly to each request.

Additional standing constraints: historical Gemini 2.0 Flash responses are
reuse-only (zero new calls); modern labels remain unopened for
transform/threshold selection (no per-model retuning); no blind resubmission
on ambiguous provider responses.

## Explicit non-actions in this pass

- No provider/API/model call was made; no network request was issued.
- No `git add`, `commit`, `clean`, `reset`, or file deletion was performed.
- No file was edited other than this new file and a prepended addendum to
  `local_agent/STATUS.md`.
- The chart-generation/byte-comparison procedure was independently rerun by
  the project manager after this receipt was created: all 18 files matched a
  fresh deterministic rerun, and the exact temporary directory was removed.
- All paths in this receipt are repository-relative. No absolute
  machine-specific path, credential, token, or secret is recorded here.
