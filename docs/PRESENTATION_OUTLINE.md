# 15-minute presentation outline

Status: **storyboard-first revision**. The authoritative next-deck plan is now [`PRESENTATION_STORYBOARD.md`](PRESENTATION_STORYBOARD.md). Do not build another visual deck until the text-only storyboard is reviewed and approved.

The next draft deck should contain **editable placeholder text only**: every slide should describe the intended visual, chart axes, series, image/crop requirements, evidence status, and speaker intent. Do not insert fake charts or schematic data art. When real visuals are eventually added, they must come from committed derived tables or explicitly released image/crop assets.

## Current evidence to respect

- Ground-truth lineage is resolved in [`GT_LINEAGE.md`](GT_LINEAGE.md): the paper-era selector is six name fields, and the historical `Self*` exclusion rule yields `622 × 6 − 24 × 2 = 3,684` paper-era row slots, with one blank-row caveat in v9/v10 artifacts.
- Existing historical precision/coverage charts that use the v7 reliability tables remain labeled as legacy/public 3,682-row products, not paper-v9/v10 recomputations.
- The modern transfer screen is complete for `gemini-3.5-flash` and `gemini-3.5-flash-lite`: 622 documents × 9 frozen views = 5,598 terminal rows per model.
- The requested `gemini-3.7-flash` PA route returned HTTP 403; Qwen returned HTTP 500 endpoint-not-found. Do not silently omit those limitations.
- Modern visual TTA reduces error correlation relative to unchanged repetition and improves consensus CER for both executed models.
- The predeclared 95% accepted-field precision target was not reached by any modern strategy. Do not claim a modern 95% auto-accept operating point.
- The regenerated C1–C9 chart set now includes modern rows in C1, C2, C3, C4, C6, and C8. C5 remains historical shift evidence; C7 remains descriptive historical selection evidence; C9 remains blocked for release-safe qualitative examples.

## Narrative thesis

MLLM document transcription is sensitive to seemingly irrelevant visual changes. Rather than treating that instability only as a bug, we can use carefully chosen perturbations to create useful disagreement, improve consensus, and obtain a black-box agreement signal. The practical objective is not maximum benchmark accuracy alone; it is reducing manual review at a validated quality target.

## Main sequence

1. **Hook:** same document, visually near-equivalent views, different transcription.
2. **Problem:** accuracy is not enough; deployment needs a trusted accept/review decision.
3. **Method:** source image → visual variants → same MLLM → aligned strings → consensus + raw agreement.
4. **Perturbation palette:** unchanged repeats, pad/shift, grid warp, blur/resize/noise, and non-visual sampling controls; explicitly note limited compound-transform search.
5. **Consensus mechanics:** small alignment/voting example; avoid dense equations.
6. **Evaluation lineage:** paper 3,684 row slots, v7 legacy 3,682 rows, modern 3,718 raw nonblank fields.
7. **Historical headline:** paper-era Gemini 2.0 Flash improves exact field accuracy and CER.
8. **Useful diversity (C1):** individual error versus error correlation; temperature/repetition is a control, visual perturbation is the interesting lever.
9. **Correlation intuition (C2):** `N_eff = N / (1 + (N - 1) rho)`; ten calls are not ten independent opinions if errors correlate.
10. **Precision/coverage (C3):** accepted-field precision versus automatic coverage; historical confidence signal is promising, modern 95% target is not met.
11. **Shift periodicity (C5 redesign):** real measured agreement versus shift, preferably excluding/insetting zero; highlight 16 px multiples and avoid proprietary-internals overclaim.
12. **Modern transfer:** two executable Gemini 3.5 models show consensus/CER gains and lower visual-error correlation; 3.7/Qwen remain route-blocked.
13. **Cost/review frontier (C4):** request/token-based placeholder until a dated pricing snapshot exists; do not invent dollars.
14. **Takeaways:** visual perturbations expose useful instability; error diversity matters; confidence/selectivity is promising but must be validated.

## Backup sequence

- Ground-truth lineage and blank-row caveat.
- Modern run accounting, route blockers, and parse accounting.
- Full chart catalog C1–C9 with evidence status.
- Augmentation contribution C7, explicitly descriptive not causal.
- Failure examples C9, currently blocked pending release-safe crops/predictions.
- Temperature/sampling details.
- FFT/shift diagnostic details.
- Cost/pricing assumptions once sourced.

## Immediate tasks

1. Use [`PRESENTATION_STORYBOARD.md`](PRESENTATION_STORYBOARD.md) to create a text-only Google Slides placeholder deck.
2. Redesign C5 from real `shift_agreement.csv` data so the 16-pixel story is understandable.
3. Find or define a release-safe example protocol for the opening hook and failure-example backup.
4. Decide whether historical confidence and modern target failure need separate visual slides in the final deck.
5. Add pricing only after a dated source/usage snapshot is committed.
