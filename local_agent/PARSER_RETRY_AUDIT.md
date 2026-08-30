# Parser/retry gate audit

## Current modern-screen completion addendum — 2026-08-30

The offline parser/retry implementation passed its focused and full tests and
was used by the completed two-model screen. The screen produced 5,598
terminal rows for each of `gemini-3.5-flash` and `gemini-3.5-flash-lite`;
parse repairs and unrecovered failures are counted in
`local_agent/MODERN_FULL_RECEIPT.md`. The 3.7 Gemini route (HTTP 403) and
Qwen route (HTTP 500 endpoint-not-found) remain blocked, so this addendum
does not claim a full screen for those IDs.

The status below is the 2026-08-29 offline/pre-call audit scope. Its claims
about the implementation remain valid; its blanket statement that no provider
smoke or screen existed is historical and superseded by this addendum.

Status: **offline implementation PASS; two-model modern screen reconciled; 3.7/Qwen routes blocked**. Historical exact-render and paper-lineage recomputation remain separate gates.

Audit date: 2026-08-29
Scope: offline implementation and tests only; no network access, provider call, inference, credential inspection, private image access, or raw-response access.

## Frozen implementation evidence

| Evidence | Result |
|---|---|
| Parser specification | `pa_v149_json_repair_v0` |
| Parser implementation | `src/icdar_tta/parser.py` |
| `parser_implementation_sha256` | `656366a6215d008dd443abae45603e1a628513b5331a4752928e35fbb3ff9fde` |
| Parser status | **PASS**, implementation unchanged; test coverage expanded |
| Retry policy | `provider_neutral_retry_v1` |
| Retry implementation | `src/icdar_tta/retry.py` |
| `retry_policy_implementation_sha256` | `b35f840a7cd0d8969e250fa62f89fef5a31ee7afc99232c03130e8b5ac4f7f0d` |
| Retry status | **PASS**, new provider-neutral deterministic policy |

Both hashes are SHA-256 over the exact implementation file bytes as stored. Serialization is the raw file byte sequence only: no text decoding, newline conversion, path prefix, byte-order mark insertion, prefix, or suffix. The primary check used `sha256sum`; the acceptance check repeated hashing independently with Python `hashlib.sha256(Path(path).read_bytes())`.

## Parser conformance findings

The existing implementation conforms to the frozen specification; no parser rewrite or implementation edit was justified.

- The default closed schema contains exactly 44 unique PA v1.49 fields in frozen order. A custom closed field set requires explicit caller opt-in.
- A complete leading multiline `<think>...</think>` block is removed, followed by at most one outer Markdown JSON-fence removal pass.
- Decode order is direct `json.loads`, then at most one outermost-braced-object candidate. A failed candidate is retained as a failure; the parser does not search for another object.
- The top-level value must be an object with exactly the required field names. Every field must contain exactly `value` and `confidence`.
- Confidence must be an integer from 1 through 10; booleans, floats, strings, and out-of-range integers fail.
- Every ordinary value must be a string. `SelfDeathAge` alone must be a list of exactly three strings.
- Empty, malformed, truncated, non-object, schema-invalid, and provider-error responses produce an explicit `ParseFailure` carrying the original raw response.
- `ParseFailure` is structurally distinct from `ParsedFields` and exposes no `values` or `confidences`; a failed response therefore supplies no parser-level vote or agreement value. Downstream code must retain that explicit failure rather than fabricate a prediction.

Exact parser-only test count is 40: `TestFrozenParserContract` 19, `TestParserRepairsAndFailures` 15, and `TestExplicitAllowedFieldsCompatibility` 6. The complete `tests.test_schema_and_parser` target contains 53 tests including schema/table checks.

## Retry-policy findings

No retry implementation existed in `src/` or `tests/`, so the minimal offline policy was added. It performs no I/O and has a closed status enum; unknown statuses raise `RetryPolicyError` rather than inheriting behavior.

- `retries_already_attempted=0` permits one retry; one or more already-attempted retries keep the failure and permit no second retry.
- Network failures one through four may use that one retry. The fifth consecutive network failure stops. The counter is defined to include the current failure.
- Any capacity failure stops immediately, independent of retry count or consecutive-failure count.
- `ambiguous_submission` and `reconciling` are reconcile-only and never automatically retried.
- Terminal `ok` and `parse_fail_kept` are skippable only when current and stored request fingerprints are both nonempty and exactly equal. Missing or mismatched fingerprints stop resume.
- `reserved`, `submitted`, generic `failed`, and `non_retryable_failure` each have explicit outcomes.

The retry target contains 21 tests.

## Literal offline acceptance outcomes

All commands ran from the repository root with Python source resolution set to `PYTHONPATH=src` where needed.

1. Parser/schema target:
   - Command: `PYTHONPATH=src python3 -m unittest tests.test_schema_and_parser -v`
   - Literal outcome: `Ran 53 tests in 0.005s` and `OK`.
2. Retry target:
   - Command: `PYTHONPATH=src python3 -m unittest tests.test_retry_policy -v`
   - Literal outcome: `Ran 21 tests in 0.001s` and `OK`.
3. Compile check:
   - Command: `python3 -m compileall -q src tests`
   - Literal outcome: exit status `0`; stdout empty; stderr empty.
4. Complete unittest suite:
   - Command: `PYTHONPATH=src python3 -m unittest discover -s tests -v`
   - Literal outcome: `Ran 183 tests in 2.255s` and `OK`.
5. Both-manifest validator:
   - Command: `PYTHONPATH=src python3 -m icdar_tta.validate --manifest config/data_manifest.local.yaml --portable-manifest config/data_manifest.yaml`
   - Literal outcome: six `[PASS]` gates, including `manifest.portable.secrets_and_shape` with `errors=[] warnings=[]` and `manifest.local.shape` with `errors=[]`; `Overall: PASS (0 hard failure(s))`; exit status `0`.
6. Independent YAML parse:
   - Command: `python3 -c "from pathlib import Path; import yaml; ... yaml.safe_load(...)"` over both manifest paths.
   - Literal outcome: `YAML_PARSE_OK files=2 config/data_manifest.yaml:top=dict config/data_manifest.local.yaml:top=dict`; exit status `0`.
7. Portable-artifact redaction scan:
   - Scanned: `local_agent/PARSER_RETRY_AUDIT.md`, `local_agent/EXPERIMENT_MATRIX.md`, and `config/data_manifest.yaml`.
   - Literal outcome: `REDACTION_SCAN_OK files=3 findings=0`; exit status `0`.
8. Whitespace/error check:
   - Command: `git diff --check`
   - Literal outcome: exit status `0`; stdout empty; stderr empty.
9. Primary exact-byte hashes:
   - Command: `sha256sum src/icdar_tta/parser.py src/icdar_tta/retry.py`
   - Literal output:
     - `656366a6215d008dd443abae45603e1a628513b5331a4752928e35fbb3ff9fde  src/icdar_tta/parser.py`
     - `b35f840a7cd0d8969e250fa62f89fef5a31ee7afc99232c03130e8b5ac4f7f0d  src/icdar_tta/retry.py`
10. Second independent exact-byte hash check:
    - Implementation: Python `hashlib.sha256(Path(path).read_bytes()).hexdigest()`.
    - Literal output:
      - `INDEPENDENT_SHA256 src/icdar_tta/parser.py 656366a6215d008dd443abae45603e1a628513b5331a4752928e35fbb3ff9fde`
      - `INDEPENDENT_SHA256 src/icdar_tta/retry.py b35f840a7cd0d8969e250fa62f89fef5a31ee7afc99232c03130e8b5ac4f7f0d`

## Remaining live gates

The matrix remains `BLOCKED`. The project manager still owns and must independently verify or approve:

- application/hash freeze of the recovered paper-lineage six-field/24-record
  exclusion rule, including the v9/v10 one-blank-row reporting convention
  (`docs/GT_LINEAGE.md`);
- deterministic render/source/mask lineage for all nine views, including unresolved Pad renderer details and Grid-Warp seeds/render hashes;
- route selection and image transport for each model;
- exact three-image, label-blind provider smoke and returned-model checks for all three exact IDs;
- Qwen capacity behavior and disabling/capping redundant keepalive traffic;
- independent review of the frozen request budget and durable live request ledger;
- explicit live-call authorization.

No model, transform, cohort, generation, request-budget, route-authorization, or live-call value was changed. No route gate or render gate was exercised or passed by this audit.
