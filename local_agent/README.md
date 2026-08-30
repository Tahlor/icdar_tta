# Local project-manager area

This directory is the control plane for the local data/compute work due by **2026-08-30 23:59 America/Denver**. The project manager owns the deadline, Kiro worker coordination, budget, evidence integration, and verified handoff to the cloud integration agent.

Start with [`TASK.md`](TASK.md). Its priority is the modern-model transfer question: reuse existing Flash 2 evidence to freeze the most promising historical offset and mild Grid Warp settings, run that focused subset on the requested newer Flash, Flash-Lite, and Qwen models, and test whether ensemble agreement predicts correctness or improves quality. No new Flash 2 inference is planned.

Completion also requires the exact C1–C9 chart set defined in [`docs/CHART_PLAN.md`](../docs/CHART_PLAN.md), with every required SVG/PNG generated from its named table and verified. A partial chart set is not done.

## Tracked artifacts

Keep concise, portable goal/route decisions, the work board, approved experiment matrix and request budget, redacted receipts, and final evidence/presentation recommendation here. Put reusable code, safe derived tables, and figures in the locations defined by [`docs/REPRODUCIBILITY.md`](../docs/REPRODUCIBILITY.md) and [`outputs/README.md`](../outputs/README.md).

## Local-only artifacts

The repository ignores `local_agent/runtime/`, `work/`, `raw/`, `logs/`, and `*.local.*`. Use them for Kiro session ledgers/transcripts, raw responses, temporary images, and execution logs. Never add private images, credentials, signed URLs, or large raw-response trees to Git.

Machine paths belong in ignored `config/data_manifest.local.yaml`. Portable `config/data_manifest.yaml` must use logical IDs, counts, checksums, and storage/provenance notes.

## Operating rule

Delegate bounded work to Kiro CLI where practical, record exact session IDs, check each session within 2 minutes and then every 10–15 minutes, and resume or reassign incomplete work when a worker stops early. Independently verify every artifact before marking its task complete.
