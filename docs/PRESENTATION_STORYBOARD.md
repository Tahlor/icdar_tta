# ICDAR TTA text-only presentation storyboard

Status: **design/storyboard draft only**. This file is intentionally text-first: it describes exactly what each slide should contain before another visual deck is made. Do not treat it as slide artwork. Do not insert schematic/fake charts into the real deck; every chart must be generated from the committed `outputs/derived/*.csv` tables or from an explicitly named future derived table.

Latest evidence incorporated: ground-truth lineage has been resolved to the six paper-era fields plus the recovered historical `Self*` exclusion rule; the two executable modern Gemini 3.5 screens are complete; the requested Gemini 3.7 and Qwen screens remain route-blocked; the modern 95% accepted-field precision target was not reached.

## Global rules for the next deck

- Placeholder deck only: every slide should contain editable text boxes describing the intended visual, chart axes, data series, image/crop needs, and speaker intent.
- No rasterized screenshots of charts in the placeholder deck.
- No fake data art. If a chart is not ready, write the exact placeholder specification and the blocker.
- For the final visual deck, use real repository charts only. If the current chart is visually confusing, redesign it from the same real source table rather than drawing a schematic.
- Use `local_agent/MODERN_FULL_RECEIPT.md`, `docs/GT_LINEAGE.md`, and `local_agent/CHART_RECEIPT.md` as the current evidence sources.

## Main deck storyboard, 15 minutes + 5 minutes Q&A

### Slide 1 — Title / thesis

**Purpose:** Frame the talk as a story about turning instability into useful evidence.

**On-slide text placeholder:**

- Title: `Test-Time Augmentation for Black-Box MLLM Document Transcription`
- Subtitle: `Using visual disagreement to improve consensus and estimate when to trust an answer`
- Footer placeholders: authors, venue, date.

**Image placeholder:** Full-slide archival document background or a clean crop of a Pennsylvania death certificate, faded behind the title. Must be real/release-safe or generated only as a decorative non-data background. If real, record source/release status.

**Speaker intent:** One sentence: “The same model can read the same record differently when we shift or warp the pixels; instead of hiding that, we exploit it.”

---

### Slide 2 — Hook: same information, different answer

**Purpose:** Open with surprise, not literature review.

**Visual placeholder:** One real historical name/field crop, then 3–4 visually near-equivalent rendered views beside it: original/unchanged, shifted/padded, grid-warped, maybe blurred/resized. Each view needs a real model transcription from the historical or modern run. Do not use toy strings unless the real example cannot be released; if unreleasable, use redacted boxes but preserve the structure.

**Exact content needed:**

- Crop/source ID or redacted example ID.
- View IDs: e.g. `U0`, `P1`, `G0`, `G2`.
- Model ID and run ID.
- Prediction text or redacted error category.
- Ground truth only if release-safe.

**On-slide chart/image spec:** No chart. Four editable labels under image placeholders: `same record`, `small visual change`, `different transcription`.

**Speaker intent:** Ask: “Why should a label-preserving pixel shift change the answer?” Then transition: “That sounds like a bug, but it creates a signal.”

**Blocker/status:** Need a release-safe real example. Current `C9` does not provide crops or predictions.

---

### Slide 3 — Problem: accuracy is not enough

**Purpose:** Explain the production motivation: manual review and trust, not just leaderboard CER.

**Visual placeholder:** Simple editable flow diagram: `record image -> MLLM transcription -> accept automatically? -> human review?` with a large question mark over the decision step.

**On-slide text:**

- MLLMs can transcribe historical documents without task-specific training.
- But errors remain costly and confidence is opaque.
- Deployment question: `which fields can we accept without review?`

**Chart spec:** None.

**Speaker intent:** Make the practical objective explicit: reduce manual review subject to a quality target.

---

### Slide 4 — Method in one picture

**Purpose:** Give the entire method before details.

**Visual placeholder:** Editable pipeline diagram, not a chart:

`source record` → branches to `U: unchanged repeats`, `P: pad/shift`, `G: grid warp`, optionally `other historical augmentations` → same MLLM → multiple strings → `Needleman–Wunsch alignment + character vote` → `consensus transcription + agreement score`.

**Required labels:**

- `same model`
- `no retraining`
- `black-box API`
- `test-time only`
- `agreement is raw consistency, not calibrated probability`

**Speaker intent:** The audience should understand the method in 60 seconds.

---

### Slide 5 — What was perturbed?

**Purpose:** Show that visual perturbations are the experimental lever; temperature is just a control.

**Visual placeholder:** A real visual montage of the same record thumbnail rendered as: unchanged, pad/shift, grid warp, blur/resize, noise/resize. Add a separate small text-only tile for `temperature/repeated sampling` to emphasize it is not visual.

**Chart spec:** None.

**Important limitation text:** `We varied perturbation families across ensemble members; we did not systematically search arbitrary compound transforms inside a single image. Blur+resize and standard resize preprocessing are specific exceptions.`

**Speaker intent:** Avoid parameter-grid detail. Say the conceptual point: different views can expose different model failure modes.

---

### Slide 6 — Consensus and agreement

**Purpose:** Explain Needleman–Wunsch alignment and confidence without equations.

**Visual placeholder:** Editable string-alignment example, preferably from a real field if release-safe; otherwise synthetic but clearly marked as illustrative.

Example structure:

- Prediction 1: `ALBERT`
- Prediction 2: `ALBERT`
- Prediction 3: `ALBRT`
- Alignment inserts gaps.
- Character vote returns `ALBERT`.
- Agreement score highlights weak characters.

**Chart spec:** None.

**Speaker intent:** One sentence: “We align strings despite insertions/deletions, then vote character by character; agreement becomes an external confidence signal.”

---

### Slide 7 — Evaluation population and lineage

**Purpose:** Cleanly separate paper-era, legacy/public, and modern denominators so the talk does not overclaim.

**Visual placeholder:** Three-row editable table:

1. `Paper-era v9/v10 lineage`: 622 records × 6 fields − 24 Self-record exclusions × 2 = 3,684 row slots; one blank-row caveat.
2. `Legacy/public v7 reliability tables`: 3,682 rows; used by current historical C3 precision/coverage chart.
3. `Modern screen`: 3,718 raw six-name nonblank fields; used for modern metrics.

**Chart spec:** None, but table must be editable.

**Speaker intent:** “The headline paper number is still the headline, but our repository now keeps the lineages honest.”

**Evidence update:** The earlier unknown 34-row discrepancy is resolved: it was the six-field selector plus historical `Self*` exclusion behavior, not an arbitrary missing filter.

---

### Slide 8 — Historical headline result

**Purpose:** Establish that the paper-era method worked before getting into the deeper diversity story.

**Visual placeholder:** Two large editable number callouts, not a chart:

- `Exact field accuracy: 71.2% → 75.2%`
- `CER: 9.0% → 7.2%`

Add small caption: `Historical Gemini 2.0 Flash paper-era result; detailed lineage caveats in notes.`

**Chart spec:** None. Do not make a bar chart unless using recomputed paper-lineage data; number callouts are enough.

**Speaker intent:** Spend under one minute. This is proof of usefulness, not the main intellectual contribution.

---

### Slide 9 — C1 chart: useful diversity scatter

**Purpose:** Show why repeated inference helps only when errors are not too correlated.

**Real chart source:** `outputs/derived/strategy_summary.csv`; current generated figure `outputs/figures/01_useful_diversity.svg/png` includes historical and modern rows.

**Final chart axes:**

- x-axis: `mean pairwise error correlation` or equivalent source column. Lower is more diverse.
- y-axis: `mean individual CER` or field error rate. Lower is better. Ensure the y-axis direction is visually obvious; do not accidentally invert the interpretation.

**Series/points:**

- Historical controls: resize, temperature/repeated sampling controls, pad, grid warp where source data supports both axes.
- Modern points: Flash and Flash-Lite strategies: `single`, `unchanged_3`, `pad_3`, `grid_3`, `visual_mixed_6`, `all_views_9` where correlation is defined.
- Highlight only 4–6 points in the main view; relegate full labels to backup or hover/notes.

**Annotation to include:** `Useful diversity = informative members + different mistakes.`

**Speaker intent:** Contrast repeated unchanged inference with visual perturbations. Temperature/randomness is a negative/control result, not a section.

---

### Slide 10 — C2 chart: slightly mathy effective sample size

**Purpose:** Make correlation intuitive.

**Real chart source:** `outputs/derived/error_correlation_summary.csv` plus theoretical curve generated by chart script.

**Final chart axes:**

- x-axis: pairwise error correlation `rho`, from 0 to 1.
- y-axis: stylized effective sample size for `N=10`.
- Formula displayed: `N_eff = N / (1 + (N - 1) rho)`.

**Series:**

- One theoretical curve for N=10.
- Empirical markers for historical/modern strategy correlations.

**Required wording:** `Stylized intuition, not a complete theory of structured MLLM errors.`

**Speaker intent:** “Ten calls on the invoice are not ten independent opinions if they make the same mistake.”

---

### Slide 11 — C3 chart: precision versus automatic coverage

**Purpose:** Show the deployment goal directly: accepted-field precision versus review burden.

**Real chart source:** `outputs/derived/precision_coverage.csv`; current generated C3 includes 1,750 legacy/public-v7 rows plus 749 modern rows.

**Final chart axes:**

- x-axis: automatic coverage = accepted fields / total evaluated fields.
- y-axis: accepted-field precision = accepted correct / accepted.
- Confidence/agreement threshold is swept along each curve.

**Series:**

- Historical legacy/public-v7: Grid Warp, Pad, Resize if visually legible.
- Modern Flash strategies and Flash-Lite strategies only if not cluttered; otherwise use a separate modern slide.
- Add target line at 95% only if clearly labeled as predeclared target and if not overclaiming.

**Current evidence message:** Historical legacy/public-v7 Grid Warp has a useful 95% operating point, but no modern strategy reaches the predeclared 95% target. The slide must not imply a modern 95% auto-accept result.

**Speaker intent:** This is where we explain why confidence/selectivity matters more than raw accuracy.

---

### Slide 12 — C5 chart: shift periodicity, redesigned from real data

**Purpose:** Explain why padding/shift might work.

**Real chart source:** `outputs/derived/shift_agreement.csv`; current generated C5 uses all 130 horizontal/vertical historical points but is visually hard to read because the trivial zero-shift peak dominates.

**Final chart design:** Redesign from the same real table, not a fake sine wave.

**Chart axes:**

- x-axis: absolute relative shift in pixels, preferably excluding or separately insetting `0 px`.
- y-axis: mean pairwise transcription agreement.

**Series:**

- Horizontal shift line.
- Vertical shift line, lighter or secondary.
- Optional average line if computed and clearly labeled.

**Annotations:**

- Highlight multiples of 16: 16, 32, 48, 64 px.
- Add small annotation: `FFT peak: 16 px` only if sourced from the existing FFT tables or added derived table.
- Caption: `consistent with patch/grid alignment sensitivity; not proof of proprietary internals.`

**Speaker intent:** “The interesting thing is not the 0-pixel self-agreement spike. It is the recurring recovery of agreement at 16-pixel phases.”

---

### Slide 13 — Modern transfer result: what actually happened

**Purpose:** Incorporate agent updates honestly.

**Visual placeholder:** Editable results table with six rows per model or a compact two-model summary.

**Required numbers:**

- Flash single accuracy/CER: `0.8335 / 0.0537`.
- Flash visual_mixed_6 consensus accuracy/CER: `0.8421 / 0.0496`.
- Flash-Lite single accuracy/CER: `0.7856 / 0.0750`.
- Flash-Lite all_views_9 consensus accuracy/CER: `0.8098 / 0.0632`.
- Mention visual variants reduce error correlation relative to unchanged repetition for both models.

**Route status text:**

- `gemini-3.5-flash`: executed as available Flash substitute after 3.7 PA route returned HTTP 403.
- `gemini-3.5-flash-lite`: executed as requested.
- `gemini-3.7-flash`: blocked by HTTP 403.
- Qwen: blocked by HTTP 500 endpoint-not-found.

**Speaker intent:** Mixed but useful replication: consensus and diversity transfer; 95% auto-accept does not.

---

### Slide 14 — C6 chart: cross-model target coverage

**Purpose:** Make the modern limitation visible instead of hiding it.

**Real chart source:** `outputs/derived/cross_model_operating_points.csv`.

**Final chart axes:**

- x-axis: model and strategy groups.
- y-axis: automatic coverage at the predeclared precision target.

**Series:**

- Historical legacy Grid Warp point at 95% target.
- Historical Pad target-not-met row.
- Modern Flash and Flash-Lite target-not-met rows.
- Route-blocked rows for 3.7 and Qwen.

**Required visual semantics:** Distinguish `measured target not met` from `route blocked` from `measured coverage point`. Do not render target-not-met as if it were zero coverage.

**Speaker intent:** “This is the honest replication slide: visual TTA helped consensus, but our auto-accept precision target is not solved by raw agreement on these modern runs.”

---

### Slide 15 — C8 chart: ensemble size / diminishing returns

**Purpose:** Show how many calls we need before returns flatten.

**Real chart source:** `outputs/derived/ensemble_size.csv`; current chart includes historical rows and 12 modern measured strategy points.

**Final chart axes:**

- x-axis: number of samples/views in ensemble.
- y-axis: consensus CER or exact field accuracy.

**Series:**

- Historical selected series if valid for the denominator shown.
- Modern Flash strategies.
- Modern Flash-Lite strategies.

**Desired annotation:** `More views help, but returns depend on correlation and model quality.`

**Speaker intent:** This can be backup unless it clarifies the cost/review slide.

---

### Slide 16 — C4 chart: cost/review frontier

**Purpose:** Reframe the production objective, even if exact dollars are not ready.

**Real chart source:** `outputs/derived/cost_by_run.csv` and `outputs/derived/review_frontier.csv`.

**Current evidence limitation:** Modern usage is measured, but no portable pricing snapshot is committed; C4 should not invent dollars. It can show request/token budget and review burden. Pricing can be added later from a dated provider snapshot.

**Final chart axes, preferred final form:**

- x-axis: inference cost per 1,000 fields or documents, once pricing is sourced.
- interim x-axis: requests or token usage per 1,000 fields.
- y-axis: fields requiring manual review per 1,000 fields at fixed accepted-field precision.

**Series:**

- Single call.
- Unchanged repeats.
- Pad.
- Grid Warp.
- Visual mixed/all views.
- Optional adaptive early-stop if implemented.

**Speaker intent:** “Accuracy is not the deployed objective. The deployed objective is fewer human reviews for a known risk and budget.”

---

### Slide 17 — What we can and cannot claim

**Purpose:** Preempt Q&A and avoid overclaiming.

**Visual placeholder:** Two-column editable table: `Supported` vs `Not yet supported`.

**Supported:**

- Historical paper reports accuracy/CER gains.
- Visual TTA reduces error correlation relative to unchanged repetition in the modern Gemini 3.5 screens.
- Modern consensus improves CER over single view for both executed models.
- Shift data show 16-pixel periodic sensitivity, observationally.

**Not yet supported:**

- A universal claim that Grid Warp is always the best transform.
- A modern 95% precision auto-accept operating point from raw agreement.
- Full Gemini 3.7 or Qwen results.
- Exact production cost savings in dollars.
- Proof of proprietary model internals.

**Speaker intent:** Turn limitations into credibility.

---

### Slide 18 — Takeaways

**Purpose:** Close cleanly.

**On-slide text:**

1. `Small visual changes expose real MLLM instability.`
2. `Useful ensembles need uncorrelated errors, not just more calls.`
3. `Consensus improves transcription; confidence/selectivity is promising but must be validated against the target.`

**Closing line:** `Do not just ask the model again; ask a meaningfully different visual version of the same question and measure whether it agrees with itself.`

**Speaker intent:** End at 13.5–14 minutes.

## Backup / Q&A storyboard

### Backup A — Full ground-truth lineage

Show the exact six fields, the 24-record Self exclusion, the one blank-row caveat, and the distinction among 3,684 paper row slots, 3,682 v7 legacy rows, and 3,718 modern raw nonblank fields.

### Backup B — Full modern run accounting

Show 11,196 terminal rows, 11,307 submitted ledger events, two completed Gemini models, 3.7 HTTP 403, Qwen HTTP 500, parse-failure accounting, and 210 tests passing.

### Backup C — C7 augmentation contribution

Use `outputs/derived/augmentation_contribution.csv`. Label it descriptive selection frequency only, not causal contribution.

### Backup D — C9 failure examples

Current C9 is blocked because no release-safe crops/predictions are available. The desired final backup slide needs 3–4 examples of high-agreement wrong cases with redacted crop, model/view lineage, agreement score, prediction, ground truth, and error type.

### Backup E — Temperature / sampling controls

Use as supporting detail for the C1 useful-diversity slide. Message: autoregressive randomness alone is not equivalent to useful visual diversity.

### Backup F — FFT / shift diagnostics

Show FFT/periodogram and the full horizontal/vertical shift series only if asked. Main talk should use the simplified C5 redesign.

## Immediate follow-up tasks

1. Build the next Google Slides draft from this storyboard only: editable text placeholders, no charts/images.
2. Redesign C5 from `shift_agreement.csv` so the real 16-pixel pattern is interpretable without the zero-shift spike dominating.
3. Identify one release-safe real example for Slide 2 or make a redacted example protocol.
4. Decide whether C11/C14 should be split into historical confidence and modern target-failure slides in the final visual deck.
5. Add dated pricing snapshot only when ready; until then C4 stays token/request-based.
