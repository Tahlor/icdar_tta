# Local project-manager brief

**Deadline:** 2026-08-30 23:59 America/Denver
**Workspace:** repository root (use the local checkout path for the active environment)

## Mission

Deliver a focused transfer study for the ICDAR 2026 talk. On the requested newer Gemini Flash, Gemini Flash-Lite, and Qwen models, determine whether combining predictions from unchanged repeats, image offsets, or mild Grid Warp:

1. produces an agreement score that meaningfully predicts correctness;
2. improves consensus accuracy/CER and, where the task definition supports them, extraction precision/recall;
3. improves accepted-field precision and automatic coverage, reducing manual review; and
4. preserves the relative value of the historically promising offset and Grid Warp parameters.

The existing Gemini 2.0 Flash data is the historical reference and parameter-selection source. **Do not run new Gemini 2.0 Flash inference.** Locate and validate enough existing evidence to freeze the modern test conditions, then spend execution effort on the requested modern models.

The modern experiment tests transfer of fixed historical perturbations; it must not retune transforms or thresholds on modern test labels. Accepted-field precision/coverage is the deployment metric, while exact field accuracy and CER provide paper comparability.

When sources disagree, follow the source-of-truth order in `AGENTS.md`: raw images/labels/responses, generating code/configuration, recomputed metrics, paper text, then presentation notes. Paper values are regression targets, not ground truth.

The project manager owns the deadline, dependency order, Kiro delegation, request ledger, integration, verification, and final handoff. Audits are gates to results, not the end product.

## Current state (2026-08-30)

The historical reference is frozen: the six-field evaluation contract and the paper/v9/v10 GT lineage are documented, while the packaged public/v7 lineage is kept separate. The focused modern screen is complete for `gemini-3.5-flash` and `gemini-3.5-flash-lite` using the fixed nine-view design; the requested `gemini-3.7-flash` route returned HTTP 403 and the Qwen route returned HTTP 500, so those model families remain blocked. Derived tables, C1–C9 figures, and the modern completion receipt are available. No tested strategy reached the 95% observed raw-agreement precision target. The original execution brief below is retained as the historical scope; it is not a statement that these completed items are still pending. See `local_agent/MODERN_FULL_RECEIPT.md`, `docs/GT_LINEAGE.md`, and `local_agent/STATUS.md` for the current handoff.

## Required outcomes, in priority order

### 1. Freeze the historical reference—without new Flash 2 runs

- Locate the existing Gemini 2.0 Flash responses, labels, folds, prompt/parser, augmentation definitions, and analysis code for the 622-image cohort.
- Recover the exact historically selected offset/Pad and mild Grid Warp parameter IDs and the validation logic that selected them. Do not pick modern transforms using modern test performance.
- Reuse existing Flash 2 tables to establish the single-run, unchanged-repeat, offset, Grid Warp, mixed-ensemble, confidence, and accuracy reference values.
- Populate ignored `config/data_manifest.local.yaml` with machine paths and portable `config/data_manifest.yaml` with safe provenance.

This is a bounded prerequisite, not a new Flash 2 replication project. Explain material discrepancies, but do not let nonessential historical cleanup delay the modern-model screen.

### 2. Run the focused modern-model screen

Requested candidates are “Flash 3.7,” “Flash-Lite 3.5,” and the Qwen vision model used in the Vermont workflow. These are planning names: verify and record the exact provider model IDs and capabilities at execution time.

Run the same predeclared image cohort, prompt/schema, parser, normalization, and fixed transform IDs for every available model. The provisional budget-fitting screen is:

- 3 unchanged calls per image, with one serving as the single-run baseline;
- 3 historically promising offset/Pad configurations;
- 3 historically promising mild Grid Warp configurations;
- unchanged, offset, Grid Warp, and mixed ensembles derived from those nine responses with no extra calls.

At 622 images, nine views across three models require 16,794 scored requests. Use all three requested model families when their exact endpoints are available and the operational reserve fits under the hard cap. Any model substitution or omission requires an explicit evidence-backed decision in the experiment matrix.

The full 10-per-strategy design in `docs/EXPERIMENT_PLAN.md` remains the stronger follow-up. This nine-view design is the deadline/budget transfer screen and must be labeled as such. Do not add a broad augmentation sweep, prompt sweep, per-model tuning, full thinking-on/off comparison, or compound-transform search before this screen is complete.

### 3. Answer the confidence, quality, and transfer questions

For every model and strategy, compare against both the single run and repeated-unchanged control:

- individual and consensus exact field accuracy and CER;
- extraction precision/recall when the canonical evaluation defines meaningful false-positive and false-negative events;
- raw agreement versus correctness, with uncertainty and a risk/precision-versus-coverage curve;
- accepted-field precision, automatic coverage, and manual-review count at predeclared operating targets;
- pairwise error correlation and ensemble gain;
- the rank and contribution of each tested historical transform ID.

Do not call raw agreement a calibrated probability. If calibration is evaluated, fit it without modern test-label leakage and report it separately. Report all tested models and transforms, including negative results.

Before revealing modern test labels, freeze the accepted-field precision target(s), transform shortlist, ensemble construction, and primary comparisons. Judge “meaningful confidence” by the risk/precision-versus-coverage curve and coverage achieved at those targets relative to repeated unchanged runs. Judge accuracy improvement with paired field-level deltas and uncertainty. Judge parameter transfer by comparing the historical and per-model ranks of the predeclared transform IDs; “best” always means best among the tested shortlist under the named metric.

If a provider or evidence blocker prevents a defensible modern run by the deadline, complete every unaffected deliverable, write a precise failure receipt, and narrow the presentation claim. The task remains blocked—not complete—while that blocker prevents any required chart. Saying a route “should work” is not completion.

### 4. Deliver presentation-ready evidence

- Generate all nine required C1–C9 figures by code from the exact tables and stable basenames in `docs/CHART_PLAN.md`.
- Produce both SVG and PNG for every chart. C1–C6 cover the main narrative and modern comparison; C7–C9 provide the specified contribution, ensemble-size, and failure-example backup evidence.
- Record which claims are supported, model-dependent, contradicted, or omitted.
- Keep historical Gemini evidence distinct from new Qwen/Gemini results.
- Track the cloud integration agent through final deck/outline integration, a 13.5–14 minute timing pass, and Q&A backup preparation. The project manager remains accountable until the integrated artifacts are verified on `master`.

Alternate charts, renamed files, prose summaries, or copied paper figures do not satisfy this requirement without explicit project-owner approval. Missing evidence is a blocker to resolve, not a reason to silently skip a chart.

### 5. Close with reproducible QA

- Run the relevant integrity, metric, leakage, cost, and figure checks in `docs/VALIDATION_TESTS.md`.
- Record exact commands, repository SHAs, model IDs, prompt/transform hashes, row counts, failures, request counts, costs, and artifact paths.
- Hand verified tables, figures, receipts, and the claim recommendation to the cloud integration agent, then verify the integrated `master` result rather than stopping at handoff.

## Immediate execution order

1. Read the repository contracts listed in `README.md`; capture Git status here and read-only status for external repositories.
2. Create `local_agent/STATUS.md` with each required outcome, owner/worker label, artifact path, state, blocker, and next checkpoint. Keep exact Kiro session IDs in ignored runtime state.
3. Locate the existing Flash 2 evidence and freeze the historically promising offset and Grid Warp transform IDs; document the decision in a one-page `local_agent/GOALS_AUDIT.md`.
4. Delegate bounded Kiro tasks for provider/model verification, runner/transform preparation, metric implementation, chart generation, and independent QA.
5. Freeze `local_agent/EXPERIMENT_MATRIX.md` and `local_agent/request_budget.json`, including exact modern model IDs and the same transform IDs for every model.
6. Run parser/lineage smoke tests, then the approved Flash, Flash-Lite, and Qwen cells if every live-request gate passes. Do not schedule new Flash 2 calls.
7. Generate cross-model confidence, precision/coverage, correlation, and accuracy results; determine whether the historical transform shortlist transfers.
8. Generate and verify the exact C1–C9 chart set, integrate it into the talk/backup material, run final QA, verify `master`, and write `local_agent/FINAL_RECEIPT.md` before the deadline.

Optional compound transforms, adaptive sampling, extra models, and decorative chart variants wait until all required outcomes above are complete.

## How the project manager must use Kiro CLI

Use Kiro CLI for work that is bounded and independently verifiable, especially source inventory, read-only route audits, normalization/metric implementation, chart generation, and independent QA. The project manager retains ownership of scope, live-call approval, integration, and verification.

Every Kiro task must specify:

- exact working directory and owned files;
- required inputs and output artifact path;
- acceptance checks and time box;
- dirty worktrees that must not be cleaned or reset;
- whether edits are allowed;
- “no live provider calls” unless an explicit request reservation is attached.

For every launched session, the project manager must:

1. Run a small read/tool canary first so permission, model, and path failures appear immediately.
2. Record the exact session ID, actual model/engine, start time, log/artifact path, and next check in ignored local runtime state.
3. Check once within 2 minutes, then every 10–15 minutes while active. Monitor the exact workspace and session ID; never select an arbitrary newest session.
4. Treat five minutes without new session or execution-stream activity as a stall heuristic, while allowing for known long-running commands.
5. If a session stops before its acceptance checks pass, inspect partial artifacts and resume that exact session with the specific remaining work. Never start a competing process while its live lock exists.
6. After a second premature stop or repeated permission failure, split the task, correct the invocation, or reassign the remainder. Do not keep sending a vague “continue” prompt.
7. Mark work complete only after the artifact exists and the project manager independently runs its acceptance check.

Prefer the requested Sol 5.6/max-effort profile only when the installed Kiro catalog and session evidence verify it. Record the model actually used; do not rely on a command-line model flag that may be ignored. Keep Kiro transcripts and session ledgers under ignored `local_agent/runtime/` or `local_agent/logs/`.

## Live-request gate and budget

No paid/provider call may begin until all of the following exist:

- existing Flash 2 evidence status and the frozen historical transform shortlist;
- a predeclared experiment matrix with exact model, prompt, transform, cohort, and evaluation role;
- a request ledger with `reserved`, `scheduled`, `spent`, and `remaining` counts;
- a passing parse/lineage smoke plan and deterministic retry policy;
- a selected route justified by reliability, request accounting, image transport, and reproducibility.

The project manager records its gate decision, timestamp, and independent budget-review evidence in the matrix.

The hard cap is **20,000 provider requests total**. Count warmups, keepalives, smoke calls, extraction calls, retries, capacity failures, polling calls that consume the same budget, and accidental duplicates at the provider boundary. Historical responses cost zero new requests. Derived mixed ensembles must not trigger extra calls.

At 622 images, the provisional three-model matrix schedules 16,794 scored calls, leaving at most 3,206 calls for smoke, warmup/keepalive, failures, and retries. Allocate that reserve explicitly and recompute the worst case if the cohort, views, or available models change.

Stop and write a redacted failure receipt after five consecutive network/capacity failures or any ambiguous submission outcome. Never blindly resubmit an ambiguous job.

## Evidence roots and route policy

Start with these known evidence roots, verifying exact paths and provenance rather than copying assumptions:

- official PA release: `C:\Users\tarchibald\github\pa-death-records-622`;
- historical PA runs: `D:\Projects\PA_DEATH`;
- Chat2Rec PA outputs: `C:\Users\tarchibald\github\chat2rec_analysis\projects\pa_death_records622_official`;
- transform implementations: `C:\Users\tarchibald\github\ancestry\chat2rec_v1\chat2rec\degradations`;
- Vermont/Qwen execution evidence: `C:\Users\tarchibald\github\ancestry\vermont`;
- Raptor framework examples: `C:\Users\tarchibald\github\ancestry\ds-content-raptor`;
- paper/chart sources under the known Ancestry OneDrive papers directory.

Raptor is optional infrastructure, not a scientific requirement. Choose the simplest auditable route that preserves image/response identity and respects the budget; do not force Vertex/GCS, S3/Lambda, Batch, or synchronous execution without evidence. Do not add PA/Vermont-specific code or artifacts to the Raptor framework repository.

If Qwen is selected, recover and follow the verified Vermont resize, warmup, keepalive, parse-smoke, retry, and resume rules instead of copying historical values from memory. Count every operational call in the request ledger.

## Hard boundaries

- Keep private images and raw responses outside Git. Commit only safe portable code, manifests, checksums, compact derived tables, figures, and documentation.
- Never place credentials, keys, signed URLs, or machine-specific private paths in prompts, Git, issue comments, or presentation artifacts.
- Do not clean, reset, or overwrite unrelated changes in the Vermont or Raptor worktrees.
- Preserve raw responses byte-for-byte when feasible and link every derived row to stable document, field, run, transform, and response identifiers.
- Do not tune modern transforms or acceptance thresholds on modern test labels.
- Do not selectively omit tested models or perturbations because they weaken the narrative.
- Do not claim a test, metric, model, or route succeeded without the underlying artifact and receipt.

## Definition of done

The task is complete only when the deadline package contains:

1. verified reuse of existing Flash 2 evidence and a frozen, provenance-linked shortlist of historical offset and Grid Warp parameters;
2. the approved Flash, Flash-Lite, and Qwen transfer results, or a precise model-specific blocker and appropriately narrowed claim;
3. reproducible cross-model confidence, precision/coverage, correlation, precision/recall where defined, and accuracy/CER tables;
4. an explicit determination of whether the historically promising transforms remain the best among the tested subset;
5. all required C1–C9 charts under their specified basenames, each in SVG and PNG, passing `docs/CHART_PLAN.md` and integrated into the timed talk/backup material;
6. a final redacted receipt with commands, IDs, counts, failures, budget, checks, source-table checksums, chart paths, and final `master` SHA.

Planning documents, partial chart sets, or blocker receipts alone do not satisfy the task.
