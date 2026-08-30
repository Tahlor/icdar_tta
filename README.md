# ICDAR TTA presentation and replication workspace

Planning, analysis, replication, and figure-generation workspace for the ICDAR 2026 presentation of **Improving MLLM Historical Record Extraction with Test-Time Image Augmentation**.

The goal is not to reproduce the paper slide-by-slide. The presentation should tell a compact systems/research story:

> Repeated inference is useful not mainly because it squeezes out a few extra points of transcription accuracy, but because carefully chosen visual perturbations create useful disagreement. Useful disagreement enables a black-box confidence signal that can reduce manual review.

## Presentation target

- **15 minutes talk + 5 minutes Q&A**
- Target **13.5–14 minutes of rehearsed content** to leave timing margin.
- Prefer new presentation-specific figures over copied paper tables/figures.
- Main result framing: **manual review avoided at a fixed quality/precision target**, not maximum benchmark accuracy.

## Core claims to test and communicate

1. Visual perturbations can generate more useful diversity than repeated sampling of an unchanged image.
2. Ensemble value depends on both member accuracy and **error correlation**; ten copies of the same mistake are effectively one opinion.
3. Grid warp is especially interesting because relatively weak individual predictions can produce diverse errors and strong high-precision agreement signals.
4. Pixel shifting/padding exposes model sensitivity to visual patch/tile alignment; the 16-pixel periodicity is a memorable mechanistic result.
5. Repeated cheap inference can be economically useful even when aggregate accuracy barely improves, if agreement lets us confidently auto-accept more fields and reduce human review.
6. We should test whether these behaviors persist on newer MLLMs rather than presenting a Gemini 2.0 Flash result as timeless.

## Repository organization

- [`AGENTS.md`](AGENTS.md): steering and coordination rules for cloud/local agents.
- [`docs/PRESENTATION_OUTLINE.md`](docs/PRESENTATION_OUTLINE.md): current 15-minute narrative.
- [`docs/CHART_PLAN.md`](docs/CHART_PLAN.md): planned new figures and acceptance criteria.
- [`docs/EXPERIMENT_PLAN.md`](docs/EXPERIMENT_PLAN.md): baseline re-analysis and modern-model replication matrix.
- [`docs/DATA_CONTRACT.md`](docs/DATA_CONTRACT.md): path/manifest contract for data that lives outside Git.
- [`docs/GT_LINEAGE.md`](docs/GT_LINEAGE.md): authoritative six-field selector, historical exclusion rule, and public-v7 versus paper-v9/v10 GT lineage.
- [`docs/VALIDATION_TESTS.md`](docs/VALIDATION_TESTS.md): integrity, regression, leakage, cost, and figure-reproducibility checks.
- [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md): local-first chart generation with a cloud fallback.
- [`data/README.md`](data/README.md): what belongs in Git versus external storage.
- [`examples/README.md`](examples/README.md): two release-authorized sample images and matching labels for smoke/visual checks.
- [`config/data_manifest.example.yaml`](config/data_manifest.example.yaml): machine-readable path manifest template.
- [`outputs/README.md`](outputs/README.md): expected derived tables and chart artifacts.
- [`local_agent/TASK.md`](local_agent/TASK.md): deadline-driven project-manager brief for reusing Flash 2 evidence and testing historically promising offset/Grid-Warp ensembles on newer Flash, Flash-Lite, and Qwen models.

## Current evidence status — 2026-08-30

- Ground-truth lineage is resolved: the historical metric selector is six
  name fields, the newer paper/v9/v10 rule yields `622 × 6 − 24 × 2 = 3,684`
  row slots with one retained blank row, and the public/v7 release is a
  separate 3,682-row lineage. See [`docs/GT_LINEAGE.md`](docs/GT_LINEAGE.md).
- The nine-view modern screen is complete for `gemini-3.5-flash` and
  `gemini-3.5-flash-lite` (5,598 terminal rows per model). The analyzer used
  3,718 raw six-name nonblank cells and did not apply the historical 3,684-row
  exclusion; this is explicit in the derived-table metadata.
- The predeclared 95% accepted-field precision target was not reached. The
  `gemini-3.7-flash` route returned HTTP 403 and the Qwen route returned HTTP
  500 endpoint-not-found, so neither has a full scored PA screen.
- All C1–C9 chart files are generated from the current derived tables. The
  complete run, model metrics, route failures, ledger accounting, and private
  artifact locations are recorded in
  [`local_agent/MODERN_FULL_RECEIPT.md`](local_agent/MODERN_FULL_RECEIPT.md).

## Issue roadmap

1. [#1 — Inventory historical data/code/run artifacts](https://github.com/Tahlor/icdar_tta/issues/1): local-agent first task; recover paths and provenance before new inference.
2. [#2 — Reconstruct canonical field-level dataset and paper-era metrics](https://github.com/Tahlor/icdar_tta/issues/2): normalized data, consensus/evaluation code, and regression tests.
3. [#3 — Build precision/coverage and manual-review analysis](https://github.com/Tahlor/icdar_tta/issues/3): the primary deployment-oriented analysis.
4. [#4 — Build inference-cost vs human-review frontier](https://github.com/Tahlor/icdar_tta/issues/4): measured/estimated cost accounting tied to fixed-quality operating points.
5. [#5 — Replicate fixed TTA conditions on current Gemini and Qwen-family MLLMs](https://github.com/Tahlor/icdar_tta/issues/5): modern-model transfer test without per-model retuning.
6. [#6 — Recompute and simplify pixel-shift periodicity analysis](https://github.com/Tahlor/icdar_tta/issues/6): new presentation-specific shifting figure.
7. [#7 — Implement reproducible presentation chart pipeline and cloud fallback](https://github.com/Tahlor/icdar_tta/issues/7): local + generic/cloud chart generation.
8. [#8 — Assemble and rehearse the 15-minute ICDAR presentation](https://github.com/Tahlor/icdar_tta/issues/8): final deck and Q&A backup.
9. [#9 — Optional compound-transform/adaptive-sampling extensions](https://github.com/Tahlor/icdar_tta/issues/9): backlog only; do not block the core work.

## Immediate workflow

1. **Local data inventory:** locate original images, labels, augmentation outputs, model responses, paper-era scripts, and any token/cost logs; populate `config/data_manifest.local.yaml` locally and commit only a redacted/portable manifest if paths are machine-specific.
2. **Baseline reconstruction:** regenerate a normalized field-level table from existing Gemini 2.0 Flash outputs and verify the paper headline metrics before making new figures. Use the paper/v9/v10 GT lineage for that comparison; the currently committed v7 tables are a separately labeled public/legacy 3,682-row product. Do not run new Flash 2 inference.
3. **New analyses:** derive agreement/precision/coverage, error-correlation, ensemble-size, augmentation-contribution, and cost/review tables from the baseline outputs.
4. **Modern-model replication:** run the historically promising offset/Pad and mild Grid Warp parameters, plus an unchanged-repeat control, on newer Gemini Flash, Gemini Flash-Lite, and Qwen-class models. Test agreement as a confidence signal and compare accuracy plus precision/coverage without per-model retuning.
5. **Charts:** generate publication-quality SVG/PDF/PNG from committed derived tables. Local execution is primary; cloud generation must be possible from the same scripts and manifests.
6. **Deck:** finalize slides only after the new result figures stabilize.

## Ground rules

- Do not commit private/raw archival data unless it is already intentionally public and licensing permits it.
- Do not commit API keys, credentials, or machine-specific absolute paths.
- Preserve raw model responses. Derived tables should be reproducible from raw responses + labels.
- Keep the GT lineage explicit: the paper-era target is 3,684 six-field evaluation rows under the recovered historical exclusion rule; the public/v7 products use a distinct 3,682-row processed lineage. See [`docs/GT_LINEAGE.md`](docs/GT_LINEAGE.md).
- Every figure should be generated by code and have an accompanying machine-readable input table.
- Completion requires the exact C1–C9 SVG/PNG chart set and source tables in `docs/CHART_PLAN.md`; a partial or substituted chart set is not done without explicit project-owner approval.
- Separate **measured results** from **illustrative/theoretical curves**.
- Do not selectively present only models for which TTA works. If a replication differs, report the difference and adjust the claim.
- For the talk, spend little time on the full augmentation sweep; emphasize grid warp, shifting/padding, confidence, correlation, and the human-review objective.

## Paper-era reference numbers to verify from source outputs

These are useful checks, not substitutes for recomputation:

- Single-pass field accuracy: **71.2%**
- Best 10-sample validation-consensus field accuracy: **75.2%**
- Single-pass CER: **9.0%**
- Best 10-sample validation-consensus CER: **7.2%**
- Pad 10-sample field accuracy: **74.8%**
- Grid-warp error correlation: **0.575**
- Resize error correlation: **0.973**
- Grid-warp raw confidence/accuracy correlation reported in the paper: **0.642**

All presentation numbers should ultimately be regenerated from repository-linked data products rather than copied manually from the paper.
