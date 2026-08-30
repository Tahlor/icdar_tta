# Provider-neutral request-ledger audit

## Current modern-screen accounting addendum — 2026-08-30

The completed modern screen has a private append-only ledger chain with
11,307 submitted events and 11,196 terminal response rows (5,598 per
executed Gemini model). All terminal response files were hashed and reconciled
to the modern analysis receipt; raw ledger/response bodies remain outside
Git. The full accounting, including the conservative 11,308 provider-boundary
count and the 20,000 hard cap, is in `MODERN_FULL_RECEIPT.md`.

The status below is the 2026-08-29 offline/pre-call audit scope. It remains
the implementation contract and test record, but its statement that no live
records existed is historical and does not describe the later private screen.

Status: **offline implementation PASS; modern two-model ledger reconciliation PASS; 3.7/Qwen route attempts blocked**. Historical exact-render and paper-lineage gates remain distinct.

Audit date: 2026-08-29
Scope: offline code, temporary-directory tests, portable hash/test evidence, and local validation only. No network access or provider call was made, and no tracked provider record was created.

## Exact implementation evidence

| Evidence | Result |
|---|---|
| Implementation | `src/icdar_tta/request_ledger.py` |
| Exact-byte implementation SHA-256 | `6c727ee40ccada307f185d6c6ad56c2b5c608d7d2dc20a66ead9c76460929479` |
| Focused tests | `tests/test_request_ledger.py` |
| Exact-byte focused-test SHA-256 | `b2f20acacdb60ee7bc20142db8ba50ca33852f1b8ab91968ebe95cdf82d3c78c` |
| Focused unittest result | **PASS**, 24 tests |
| Complete unittest result | **PASS**, 207 tests |
| Network/provider behavior | None implemented or exercised |

Both hashes are SHA-256 over the exact file bytes as stored. Hash serialization is the raw file byte sequence only: no text decoding, newline conversion, path prefix, byte-order mark insertion, prefix, or suffix. Primary hashes used `sha256sum`; independent checks used `hashlib.sha256(Path(path).read_bytes()).hexdigest()`.

## Serialization and identity contract

### Request fingerprint

`request_fingerprint()` computes SHA-256 over the UTF-8 bytes of canonical JSON produced with `sort_keys=True`, `separators=(",", ":")`, `ensure_ascii=False`, and `allow_nan=False`. There is no prefix, suffix, or row-position input. A descriptor must explicitly contain:

- exact `model_id`;
- `prompt_hash` and `schema_hash`;
- `source_image_hash`;
- structured `transform_id`;
- nonnegative `sample_index`;
- `generation_params` mapping;
- `route_transport_version`.

Additional JSON-serializable request dimensions are retained in the hash. Missing closed dimensions, nonfinite values, credential-shaped fields, image-byte fields, and raw byte values fail explicitly.

### Ledger record and JSONL

Each event is keyed by `(doc_id, model_id, transform_id, sample_index)` and requires schema version, request fingerprint, prompt hash, closed retry status, attempt count, and retry count. Source/render/payload identities, timestamps, usage, error, latency, parser/pricing/provider metadata, and raw-response reference/text are retained only when supplied by the caller. Raw-response fields are not fabricated. Credential fields and image bytes are rejected.

Each append writes one canonical JSON object with sorted keys and compact separators, UTF-8 encoding, and terminal LF. Existing bytes are validated before append and remain an exact prefix afterward. If a valid final JSON object lacks a terminal newline, the delimiter is appended before the new event without changing prior bytes. Reads reject blank lines, invalid UTF-8, malformed JSON, non-object JSON, invalid records, changed fingerprints/prompt hashes for a repeated key, decreasing counters, and invalid transitions with path/line or history context.

Repeated keys are append-only transition history, not uniqueness collisions to overwrite. `latest_record()` selects the final event for a decision without deleting prior events. Terminal and capacity states cannot transition back to submission; an ambiguous submission must enter `reconciling` before a reconciled terminal event.

### Retry-policy integration

`decide_ledger_action()` delegates the latest durable status and stored retry count to `retry.decide_retry()`:

- `ok` and `parse_fail_kept` skip only when current and stored fingerprints are both nonempty and exactly equal;
- a missing or mismatched terminal fingerprint stops with `STOP_FINGERPRINT_MISMATCH`;
- `ambiguous_submission` and `reconciling` are `RECONCILE_ONLY`;
- capacity failure is `STOP_CAPACITY`;
- the fifth consecutive network failure is `STOP_FIVE_CONSECUTIVE_FAILURES`;
- retry exhaustion remains controlled by the frozen one-retry policy.

The component makes no submission, reconciliation, network, or provider call.

## Focused test coverage

The 24 tests cover canonical key-order stability; every closed fingerprint dimension; explicit sample-key differences; missing/nonfinite descriptors; required record fields and statuses; recursive credential/image-byte rejection; optional raw metadata and Unicode text preservation; caller-only raw fields; canonical append/read round trips; prior-byte and missing-final-newline behavior; duplicate-key history; independent keys; fingerprint/counter/transition failures; nonexistent, empty, malformed, blank, non-object, and invalid-record ledgers; new-request decisions; exact terminal matching and mismatch; reconcile-only ambiguity; capacity and fifth-network stops; and retry-count delegation. Every test ledger used `tempfile.TemporaryDirectory()` and was removed by context cleanup.

## Literal offline validation outcomes

All commands ran from the repository root. RTK-filtered test output is reproduced literally as returned.

1. Focused ledger target:
   - Command: `rtk test env PYTHONPATH=src python3 -m unittest tests.test_request_ledger -v`
   - Literal outcome: `Ran 24 tests in 0.029s` and `OK`; exit status `0`.
2. Compile check:
   - Command: `rtk python3 -m compileall -q src tests`
   - Literal outcome: exit status `0`; stdout empty; stderr empty.
3. Complete unittest suite:
   - Command: `rtk test env PYTHONPATH=src python3 -m unittest discover -s tests -v`
   - Literal outcome: `Ran 207 tests in 2.464s` and `OK`; exit status `0`.
4. Both-manifest validator:
   - Command: `rtk env PYTHONPATH=src python3 -m icdar_tta.validate --manifest config/data_manifest.local.yaml --portable-manifest config/data_manifest.yaml`
   - Literal outcome: six `[PASS]` gates, including `manifest.portable.secrets_and_shape: ... errors=[] warnings=[]` and `manifest.local.shape: ... errors=[]`; `Overall: PASS (0 hard failure(s))`; exit status `0`.
5. Independent YAML parse:
   - Implementation: `yaml.safe_load` over `config/data_manifest.yaml` and `config/data_manifest.local.yaml`, asserting both top levels are mappings without printing contents.
   - Literal output: `YAML_PARSE_OK files=2 config/data_manifest.yaml:top=dict config/data_manifest.local.yaml:top=dict`; exit status `0`.
6. Portable-artifact redaction scan:
   - Scanned: `local_agent/REQUEST_LEDGER_AUDIT.md`, `local_agent/EXPERIMENT_MATRIX.md`, and `config/data_manifest.yaml` for private-key headers, machine-specific absolute paths, and credential assignments.
   - Literal output: `REDACTION_SCAN_OK files=3 findings=0`; exit status `0`.
7. Whitespace/error check:
   - Command: `rtk git diff --check`
   - Literal outcome: exit status `0`; no findings.
8. Primary exact-byte hashes:
   - Command: `rtk sha256sum src/icdar_tta/request_ledger.py tests/test_request_ledger.py`
   - Literal output:
     - `6c727ee40ccada307f185d6c6ad56c2b5c608d7d2dc20a66ead9c76460929479  src/icdar_tta/request_ledger.py`
     - `b2f20acacdb60ee7bc20142db8ba50ca33852f1b8ab91968ebe95cdf82d3c78c  tests/test_request_ledger.py`
9. Independent exact-byte hash check:
   - Implementation: Python `hashlib.sha256(Path(path).read_bytes()).hexdigest()`.
   - Literal output:
     - `INDEPENDENT_SHA256 src/icdar_tta/request_ledger.py 6c727ee40ccada307f185d6c6ad56c2b5c608d7d2dc20a66ead9c76460929479`
     - `INDEPENDENT_SHA256 tests/test_request_ledger.py b2f20acacdb60ee7bc20142db8ba50ca33852f1b8ab91968ebe95cdf82d3c78c`
10. Independent evidence/budget assertion:
    - Implementation: Python exact-byte hashing, AST focused-test count, parsed YAML evidence checks, and parsed JSON assertions over the existing frozen budget totals.
    - Literal output: `INDEPENDENT_EVIDENCE_OK source_sha256=6c727ee40ccada307f185d6c6ad56c2b5c608d7d2dc20a66ead9c76460929479 test_sha256=b2f20acacdb60ee7bc20142db8ba50ca33852f1b8ab91968ebe95cdf82d3c78c focused_tests=24 budget_scheduled=16794 budget_reserved=3190 budget_spent=0 budget_worst_case=19984 budget_remaining=16`; exit status `0`.

The first RTK-wrapped redaction one-liner did not execute: it exited `1` with Python `SyntaxError: closing parenthesis ']' does not match opening parenthesis '('`. Per instruction, it was rerun plainly with corrected quoting and returned `REDACTION_SCAN_OK files=2 findings=0`; the final three-file scan including this audit is recorded above after final validation.

## Remaining live gates

The matrix remains `BLOCKED`. The project manager still owns and must independently verify or approve:

- deterministic source/mask/render/payload lineage for every frozen view, including unresolved Pad renderer details and Grid-Warp seeds/render hashes;
- selection and validation of each provider route and image transport;
- exact three-image, label-blind provider smoke and returned-model checks for all three exact model IDs;
- creation, durability, concurrency/locking policy, storage permissions, backup, and reconciliation operation of the real live ledger;
- raw-response storage locations and byte-preservation behavior in the authorized environment;
- provider usage/error/latency metadata behavior and any pricing provenance;
- Qwen capacity behavior and disabling/capping redundant keepalive traffic;
- independent review of `request_budget.json` and any future budget change;
- credential provisioning outside portable artifacts;
- explicit live-call authorization and approval timestamp.

No model, transform, cohort, generation, request-budget, provider-route, or authorization value was changed. No provider records were created in tracked output directories. This offline PASS does not close any live gate.
