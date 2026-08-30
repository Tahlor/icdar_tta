# Modern label-blind smoke receipt

Run window: 2026-08-30T04:48:11Z–2026-08-30T04:48:26Z. This is a small
route/parser/usage smoke, not the modern accuracy experiment.

## Scope and outcome

- Three predeclared source documents, one `U0` unchanged-repeat view, and two
  Gemini model IDs were used.
- Six provider requests were attempted: six returned `ok`, with zero retries
  and zero recorded failures.
- Every response returned the exact requested model ID.
- The prompt SHA-256 is
  `fd119108d3ef4dbf2f88984511d9f903b7d4c98b032a95c327a21f713335e48e`.
- The route/generation contract used by this smoke is
  `gemini_l1_native_inline_jpeg95_minimal4096_v2` with temperature `0`, one
  candidate, minimal thinking, and a 4,096-token maximum.

The six-row machine-readable metadata table is
[`outputs/derived/modern_smoke_metadata.csv`](../outputs/derived/modern_smoke_metadata.csv).
It includes source/render/payload hashes, exact returned IDs, latency, token
usage, and raw-response hashes. The raw response bodies, source documents,
and rendered smoke images remain in private local storage and are not copied
to Git.

## Interpretation

- `gemini-3.5-flash-lite` passed this label-blind PA route smoke and is the
  requested Flash-Lite target.
- `gemini-3.5-flash` also passed, but is a related direct-route model and is
  not a substitute for the frozen `gemini-3.7-flash` target.
- `gemini-3.7-flash` and the Qwen model were not tested by this smoke.
- No ground-truth labels were opened, so this receipt makes no accuracy,
  CER, precision, coverage, or deployment-quality claim. The full scored
  transfer gate remains closed pending the documented filter, render-lineage,
  Qwen, budget, and authorization checks.

The smoke metadata is intentionally a redacted derivative. It contains no
model transcription values, prompt contents, credentials, endpoint URLs, or
private filesystem paths. Raw-response hashes can be reconciled against the
local private response archive without placing the archive in Git.
