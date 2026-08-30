# Modern-model route audit

Status: read-only local evidence audit; **no route was called or live-verified for this PA matrix**. Paths below are portable logical paths rooted in the named evidence repositories. Credential values, endpoint URLs, signed object URLs, and raw response bodies are intentionally omitted.

## Exact planning-name mapping

| Planning name | Exact locally evidenced executable ID | Evidence quality | Mapping decision |
|---|---|---|---|
| Flash 3.7 | `gemini-3.7-flash` | 10-row provider output; every returned `modelVersion` is the exact ID | Mapped; fresh PA smoke still pending |
| Flash-Lite 3.5 | `gemini-3.5-flash-lite` | Vertex global job model plus 36/36, 20/20, and 500/500 returned-model records | Mapped; fresh PA smoke still pending |
| Qwen vision used by Vermont | `sagemaker-qwen3-vl-8b-instruct-fp8` | Runner constant and raw JSONL `model` metadata | Mapped; fresh PA smoke/capacity check still pending |

Earlier direct-route evidence also proves `gemini-3.5-flash` and `gemini-3.1-flash-lite`; they are not substitutions for the requested matrix.

## Candidate route comparison

| Route | Local evidence | Image transport | Accounting and resumability | Decision/blocker |
|---|---|---|---|---|
| Gemini synchronous native `generateContent` through L1 gateway | `vermont/.../scripts/run_gemini_cells.py`; 500-row JSONL metadata under `data/raw_responses/` for `gemini-3.5-flash` and `gemini-3.1-flash-lite` | Local JPEG bytes encoded as inline base64; no object-store staging | One provider POST per view; append-only per-cell JSONL; completed stems with `ok`/`parse_fail_kept` are skipped; max two attempts; five-consecutive-error stop | **Preferred operational shape** for transformed local PA images because identity/accounting are one-to-one and no polling is needed. **Blocked** until three-image smokes prove both requested IDs (`gemini-3.7-flash`, `gemini-3.5-flash-lite`) work on this route and return the exact ID. Existing evidence covers only older IDs. |
| Gemini 3.7 Milan L3 LiteLLM batch | `vermont/.../ANALYSIS/l3_gemini37_canary10_20260828/` receipts and provider input/output metadata | Batch JSONL with JPEG media references staged through cloud storage | Durable plan/ledger artifacts exist; 10 outputs recovered. The initial create outcome was ambiguous and required reconciliation/manual recovery before collection. | Exact ID is proven, but this is **not the simplest route** for 5,598 TTA views. Use only as fallback after a clean dry-run of arm-before-submit, identity keys, transformed-image staging, and reconcile-only resume. Never auto-resubmit an armed/ambiguous batch. |
| Gemini Vertex global batch for Flash-Lite 3.5 | `vermont/.../PRODUCTION/FLASH_35_LITE_CURRENT_STATE.md`; `PRODUCTION/scripts/flash35_lite_full_run.py` | Original/padded objects are staged in object storage and submitted to Vertex batch at `location=global` | Strong arm-before-submit shard ledger; retries disabled at submission; completed output is collect-only; armed incomplete shard is reconcile-only. Completed returned-ID evidence exists. | Strongest proven route for the exact Lite ID, but operationally heavier than inline direct calls and currently specialized to Vermont object manifests/prompts. Use as fallback if direct smoke fails, after a PA-specific transform/identity manifest and request ledger are implemented. |
| Gemini native batch helper | `vermont/.../scripts/batch_lib.py` | S3 object keys exposed through a redirector into batch request items | Maximum 5,000 requests per provider batch, so 5,598 scored views/model require at least two chunks; run dirs and stems aid resume, but parsed response mapping is positional. | **Not recommended as-is.** PA transformed-image upload/authorization is unproven; positional-only mapping is weaker than explicit request identity; and the inspected helper contains a hard-coded credential-like value that must be removed/rotated and externally configured before reuse. The value is not reproduced here. |
| Qwen SageMaker L3 OpenAI-compatible chat | `vermont/.../scripts/qwen_warmup_and_smoke.py`, `run_qwen_cells.py`, `smoke_qwen*.py`; Qwen raw JSONL metadata | Longest side capped at 1,280 via Lanczos; RGB conversion; JPEG quality 85; inline base64 `data:image/jpeg` URL | One POST per scored view; 180-second timeout; max two attempts; append-only JSONL resume by image stem/status; stop at five consecutive errors; capacity error forces stop. Warmup is 20–22 minutes with 15-second pings. | **Recommended Qwen route after fixes.** Disable the always-on keepalive thread during active scored calls, cap warmup at 81 calls, correct prompt-ID lineage, and pass a three-image PA smoke/capacity test. Without those changes it is budget-incompatible. |

## Qwen prompt/schema/parser and operational details

- Existing Vermont Qwen request: user content contains inline image plus text; thinking-off appends `/no_think` and sends `chat_template_kwargs.enable_thinking=false`; temperature 0; 2,048 max tokens.
- Existing parser: strip complete `<think>` blocks, strip one outer Markdown fence, direct `json.loads`, then outermost `{...}` fallback. This behavior informs the frozen common parser, but Vermont's prompt/schema is not the PA schema.
- Existing warmup: initial request, then a ping every 15 seconds for at most 20 minutes in `qwen_warmup_and_smoke.py`; `run_qwen_cells.py` allows 22 minutes. Scored timeout is 180 seconds. Warmup ping timeout is 30 seconds.
- Existing retry/stop: `MAX_RETRIES=2` means at most two total attempts (one retry); linear 3-second attempt backoff; stop after five consecutive errors. A response body containing capacity failure immediately forces the stop limit.
- Existing resume: `ok` and `parse_fail_kept` stems count as processed. Raw files have 503 rows for a nominal 500-image cell because three capacity/error rows were retained before resume; terminal lineage must therefore key by stem/status rather than line count.
- Located metadata issue: both Qwen `prompt_b` raw files report `prompt_id=prompt_a`, caused by the runner's text heuristic. A PA runner must bind a frozen prompt ID/hash directly, never infer it from prompt contents.

## Request accounting for the 622 × 9 screen

- Per exact model: 622 × 9 = **5,598 scored provider calls**.
- Three models: **16,794 scored calls**.
- Derived ensembles: **0 calls**.
- Reserve: 9 smoke + 81 Qwen warmup/keepalive + 3,000 shared retry/capacity + 100 ambiguous-reconciliation contingency = **3,190**.
- Worst case: **19,984**; hard-cap remainder **16**.
- Direct synchronous routes avoid batch polling/control accounting. If a batch fallback is selected, the budget must be re-frozen to count every scheduled operational call that consumes the cap; no assumption is made that polling is free.

## Recommendation

1. Build one PA-specific, provider-neutral request/response ledger and common parser; pre-render and hash all nine views locally.
2. Prefer synchronous inline direct calls for both Gemini models **only if** exact-ID three-image smokes pass; this is the simplest identity-preserving route and avoids transformed-image object staging.
3. If a requested Gemini ID fails direct smoke, use its locally proven batch route: Milan L3 for `gemini-3.7-flash`, Vertex global for `gemini-3.5-flash-lite`. Re-freeze transport and operational-call accounting first.
4. Use the SageMaker L3 chat route for Qwen only after disabling redundant active-traffic keepalive and fixing prompt lineage.
5. Do not call `models/gemini-2.0-flash`; its existing outputs are reference-only.

The matrix must continue to say **live verification pending**. Local evidence proves prior route/model execution, not that the requested PA TTA payload will work now.
