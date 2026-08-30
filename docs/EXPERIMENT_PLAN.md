# Experiment plan

## Goals

The new work has two purposes:

1. Re-analyze the paper-era outputs around the presentation's deployment story: useful diversity, selective confidence, and manual-review reduction.
2. Test whether the qualitative findings persist on newer multimodal models without turning the project into a full new paper.

## Current deadline focus

The new-inference deliverable is the modern-model transfer test: apply a frozen shortlist of the historically promising offset/Pad and mild Grid Warp parameters to the requested newer Gemini Flash, Gemini Flash-Lite, and Qwen models, then test whether combining their outputs predicts correctness or improves accuracy and selective precision/coverage. Existing Gemini 2.0 Flash responses are reuse-only reference evidence; do not generate new Flash 2 responses.

The full design below remains the stronger follow-up. For the 2026-08-30 deadline and 20,000-request cap, `local_agent/TASK.md` defines a smaller predeclared screen with three unchanged, three offset/Pad, and three mild Grid Warp views per available modern model.

## Phase 0 — inventory before inference

Do not spend API money until the local data inventory is complete.

Locate and identify:

- 622 source images and release/provenance information;
- ground-truth name fields and the exact filtering/normalization used in the paper;
- fold assignments / validation split logic;
- Gemini 2.0 Flash baseline responses;
- all existing blur/resize, noise, resize, pad/shift, grid-warp, and temperature/repeat responses;
- augmentation configuration files and seeds;
- fine/coarse shift experiment outputs;
- consensus/alignment implementation;
- prompt(s), schema/parser, model configuration, and any retries;
- token/usage/cost logs if present;
- paper-era scripts/notebooks and environment information.

Deliverables: populated manifest, inventory report, checksums/row counts, and a mapping from historical files to normalized logical datasets.

## Phase 1 — paper-era baseline reconstruction

Build a normalized **field-level prediction table**. One logical row should identify a document field and one model response/augmentation sample.

Minimum columns:

- `doc_id`
- `field_name`
- `ground_truth`
- `model_id`
- `run_id`
- `strategy`
- `transform_id`
- `sample_index`
- `prediction`
- `normalized_prediction`
- `is_exact_correct`
- `cer`
- `response_path_or_id`
- `fold`

Where available also include usage, latency, API status/retry, prompt hash, transform parameters, and image hash.

### Regression checks

Recompute and reconcile the paper reference values, including:

- 622 images;
- 3,684 nonblank evaluated name fields;
- baseline 71.2% field accuracy and 9.0% CER;
- best validation-consensus 10-sample 75.2% field accuracy and 7.2% CER;
- Pad 10-sample 74.8% field accuracy;
- historical family-level error correlations (especially Grid Warp 0.575 and Resize 0.973).

A mismatch is not automatically a bug in the new code: trace filtering, parser versions, response revisions, and fold selection until the discrepancy is explained.

## Phase 2 — new analysis on existing outputs

### A. Useful-diversity summary

For every historical strategy and relevant sample count compute:

- mean individual CER;
- mean individual exact field accuracy;
- mean pairwise field-error correlation;
- consensus CER;
- consensus field accuracy;
- consensus gain over a one-sample baseline.

Include temperature/repeated-output controls as context, but do not make them the presentation focus.

### B. Agreement -> precision/coverage

For each strategy and sample count:

1. Generate the consensus and field/word confidence under the canonical alignment implementation.
2. Sweep agreement/confidence thresholds.
3. For each threshold compute accepted count, accepted-field precision, coverage, and review count.
4. Add uncertainty intervals appropriate to the accepted-field binomial count. Do not select a headline threshold solely because it looks favorable; define candidate operating targets before cross-model comparisons.

Evaluate raw agreement and, separately if useful, a cross-validated calibrated mapping. Do not mix the two labels in charts.

### C. Cost/review frontier

From actual usage logs when available, compute cost by call/run. If historical exact usage is unavailable, retain a clearly labeled estimate with pricing source/date outside the figure data.

For each strategy/sample count, combine cost with precision/coverage to derive:

- review fields per 1,000 fields at target precision;
- incremental inference cost per 1,000 fields/documents;
- manual reviews avoided vs one-sample baseline;
- incremental inference cost per review avoided.

No dollar value for human labor is required for the primary chart.

### D. Augmentation contribution

Use one compact, validation-respecting analysis to answer which families matter most in the ensemble. Candidate methods: leave-one-family-out, validation-set marginal gain, or selection frequency across CV folds. Avoid a broad new hyperparameter search unless results reveal a specific unresolved question.

## Phase 3 — modern-model replication

### Principle

The first modern-model experiment should test **transfer**, not retune TTA separately for every model.

Candidate model families requested for evaluation include newer Gemini Flash / Flash-Lite generations and a current Qwen multimodal model. **Exact provider model IDs must be verified at execution time and recorded in the run manifest**; colloquial names such as "Flash 3.7" are not sufficient provenance.

### Fixed first-pass conditions

For each model:

1. **Single baseline**: one unchanged image call.
2. **Repeated unchanged image**: 10 calls using the provider's normal/default supported generation controls. This is the modern stochasticity control.
3. **Pad/shift TTA**: the fixed set of 10 historical pad configurations selected without using this model's test labels.
4. **Grid Warp TTA**: the fixed set of 10 historical grid-warp configurations selected without using this model's test labels.
5. **Mixed practical ensemble**: derive a 10-member ensemble from 5 Pad + 5 Grid Warp outputs already generated above; no extra model calls.

If an API still exposes historical temperature-like sampling controls and a temperature replication is scientifically useful, treat it as a **secondary control**, not a requirement for cross-model comparability.

### Staged execution

**Stage A — smoke/pilot**

- Use a fixed, predeclared subset of documents only to validate API/schema/parser/latency/cost and confirm transforms render correctly.
- Do not use pilot labels to tune transformation strength.

**Stage B — full benchmark**

- Run all 622 images once the pipeline is stable and budget is acceptable.
- Preserve failures/timeouts as explicit statuses; retry policy must be deterministic and logged.

### Replication success criteria

Do **not** define replication as "another +4 percentage points." A newer model may have less headroom.

The important questions are:

- Does visual TTA reduce error correlation relative to repeated unchanged-image sampling?
- Does consensus/agreement improve accepted-field precision?
- At a fixed precision target, does visual TTA increase automatic coverage / reduce review?
- Does Grid Warp remain more selective/high-precision than more accuracy-oriented transforms?
- Does Pad/shift still show useful behavior?
- Are qualitative effects consistent across model families, or clearly model-dependent?

All tested models remain in repository results even if only selected models are shown on the main slide.

## Phase 4 — optional extensions only after the core work

### Mixed/compound transforms within one image

The historical paper did not systematically explore arbitrary compound transforms. After the fixed replication, a small experiment may test whether combining e.g. padding + mild grid warp in the **same image** creates better diversity/cost tradeoffs. This must be labeled new exploratory work, not part of the original paper method.

### Adaptive sampling / early stopping

Evaluate sequential sampling policies that stop when agreement is already sufficient for the target precision. This is directly aligned with the manual-review/cost objective and may be more valuable than pushing 10-sample aggregate accuracy.

A simple first policy can examine confidence after 2/3/5/... samples and stop when a cross-validated threshold is met; evaluation must avoid using the current test label to decide when to stop.
