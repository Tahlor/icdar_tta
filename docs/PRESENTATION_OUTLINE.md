# 15-minute presentation outline

Status: working narrative. The deck should be rehearsed to roughly **13.5–14 minutes**, leaving margin inside the 15-minute speaking slot and preserving the separate 5-minute Q&A.

## Narrative thesis

**MLLM document transcription is surprisingly sensitive to irrelevant visual changes. Instead of treating that instability only as a bug, we can use carefully chosen perturbations to create useful disagreement, improve consensus, and estimate confidence without model internals. The practical objective is to reduce manual review at a fixed quality target.**

## Proposed sequence

### 1. Hook — same document, different answer (0:00–0:45)

Show one historical name/record crop and several visually near-equivalent views that produce different transcriptions.

Question: **Why does moving or slightly warping the same information change the answer?**

Do not open with related work or a taxonomy of OCR/HTR methods.

### 2. Problem — accuracy is not enough (0:45–2:00)

Three points:

- MLLMs are strong zero/few-shot document transcribers.
- Historical documents still produce errors/hallucinations.
- Closed/proprietary models often do not expose a confidence signal we trust enough for automation.

Research question: **Can the model's instability become an external confidence signal?**

### 3. Method in one picture (2:00–3:00)

Original image -> several label-preserving visual variants -> same MLLM -> several strings -> Needleman–Wunsch-style alignment and character voting -> consensus + agreement confidence.

Message: **same model, no retraining, black-box API, multiple views.**

### 4. What was perturbed? (3:00–3:45)

One compact visual showing blur/resize, noise, padding/shift, grid warp, resize, and the non-visual sampling/temperature control.

Do not spend time on the full parameter grid.

Explicit limitation: **we varied perturbation families across ensemble members; we did not systematically search arbitrary compound transforms inside a single image.** Blur+resize and common resize preprocessing are specific exceptions.

### 5. Consensus and confidence (3:45–4:45)

Use a tiny aligned-string example. Explain Needleman–Wunsch in one sentence and show that per-character vote fractions create a black-box agreement score.

Avoid a dense formal derivation here.

### 6. Experimental context + headline result (4:45–5:45)

Very short setup:

- 622 Pennsylvania death certificates
- 3,684 paper-era six-field evaluation rows (the v9/v10 artifact retains one blank row; see [`GT_LINEAGE.md`](GT_LINEAGE.md))
- historical paper-era model: Gemini 2.0 Flash
- cross-validated augmentation selection

Keep the current repository chart package labeled as legacy/public v7 when it
uses the 3,682-row tables; do not present those tables as a paper/v9/v10
3,684-row recomputation until the dedicated paper-lineage rerun is complete.

Show the headline accuracy/CER improvement as large numbers, not as a full table. This establishes that the method works, then move on.

### 7. Where does useful diversity come from? (5:45–7:15)

New chart: individual error vs pairwise error correlation, including temperature/repeated-sampling controls and visual transforms.

Key contrast:

- unchanged/repeated or resize-like predictions can remain highly correlated;
- increasing sampling randomness can create diversity but may damage individual accuracy;
- padding and grid warp create more useful visual diversity.

Message: **randomness is not automatically useful diversity.**

### 8. Slightly mathy slide — ten copies of the same mistake (7:15–8:30)

Show

`N_eff = N / (1 + (N - 1) rho)`

for a stylized correlated-error model, with a curve for `N=10` and empirical augmentation-family correlations annotated.

Message: **ensemble size on the invoice is not the same as effective independent evidence.**

State explicitly that this is an intuition/model, not a complete theory of structured MLLM errors.

### 9. Grid warp is valuable for confidence (8:30–10:00)

New precision-vs-auto-acceptance/coverage curve.

The key deployment story is not that grid warp is the most accurate single transformation. It is that its less-correlated mistakes can make high agreement more selective, giving strong precision when we auto-accept only the fields the ensemble strongly agrees on.

Compare at least Pad, Grid Warp, and a practical mixed ensemble if supported by the recomputed data.

### 10. Why does shifting work? (10:00–11:15)

New simplified shift-periodicity plot: agreement vs pixel displacement, with 16-pixel markers/reveal. Keep the FFT and coarse diagnostic detail in backup unless needed.

Interpret carefully as evidence consistent with sensitivity to patch/tile alignment, not proof of undocumented model internals.

### 11. Cost vs manual review (11:15–12:45)

New cost/review frontier.

Frame the objective as:

**How much inexpensive inference do we buy to avoid one human review while holding accepted-field precision fixed?**

Show ensemble size/adaptive-sampling points and the measured modern-model
alternatives where they clarify the review tradeoff. The current modern run
has provider-reported token usage but no portable pricing snapshot, so do not
invent dollar costs; label the comparison by request/token budget instead.

### 12. Measured modern-model replication (12:45–13:30)

Show the completed nine-view PA screen for `gemini-3.5-flash` and
`gemini-3.5-flash-lite` (622 documents per model). The exact metrics and
lineage are in `local_agent/MODERN_FULL_RECEIPT.md` and the derived tables.

The measured message is deliberately mixed:

- Visual variants reduce error correlation relative to unchanged repetition,
  and consensus CER improves for both models.
- Pad is the strongest individual tested family on consensus accuracy in this
  screen; Grid Warp is useful but is not the top-accuracy family.
- The predeclared 95% accepted-field precision target is not reached by any
  modern strategy, so there is no claimed modern auto-accept operating point.
- `gemini-3.5-flash` is the allowed substitute after the 3.7 PA route returned
  HTTP 403; Qwen's route returned HTTP 500 endpoint-not-found. These are
  honest route limitations, not silently omitted models.

Success is **not** defined as reproducing a fixed accuracy gain. The useful
replication result is that perturbation diversity and consensus effects can be
measured on modern models, while the deployment precision target remains an
open limitation.

### 13. Takeaways (13:30–14:00)

1. Small visual perturbations can improve consensus without retraining.
2. **Error diversity matters as much as member accuracy.**
3. The practical payoff is a black-box confidence signal that can reduce manual review.

Closing line concept: **Do not just ask the model again; ask it a meaningfully different visual version of the same question and measure whether the answers agree.**

## Likely backup slides

- Full augmentation-family table.
- Temperature sweep details.
- Full calibration metrics (ECE/ACE/Brier/isotonic).
- Fine + coarse shift plots and FFT.
- Consensus algorithm details.
- Failure examples/unanimous errors.
- Full modern-model results, including models that do not follow the main pattern.
- Exact cost assumptions/pricing snapshot.
- Compound-transform limitation/future search space.
