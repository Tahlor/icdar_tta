"""Offline, provider-neutral append-only request/response JSONL ledger.

The ledger performs no network I/O.  Each JSON object is one immutable state
observation for a request key ``(doc_id, model_id, transform_id,
sample_index)``.  Repeated keys are retained as history and validated as
transitions; no record is updated or silently replaced.

Request fingerprints are SHA-256 over canonical UTF-8 JSON with sorted keys,
compact separators, and no NaN/Infinity values.  Callers must describe every
request dimension that can change provider behavior, including the model,
prompt/schema, source image, transform, sample index, generation parameters,
and route/transport version.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Sequence, Tuple

from icdar_tta.retry import RequestStatus, RetryDecision, decide_retry


LEDGER_SCHEMA_VERSION = 1
REQUEST_DESCRIPTOR_FIELDS = (
    "model_id",
    "prompt_hash",
    "schema_hash",
    "source_image_hash",
    "transform_id",
    "sample_index",
    "generation_params",
    "route_transport_version",
)
REQUIRED_RECORD_FIELDS = (
    "schema_version",
    "doc_id",
    "model_id",
    "transform_id",
    "sample_index",
    "request_fingerprint",
    "prompt_hash",
    "status",
    "attempt_count",
    "retry_count",
)
IDENTITY_METADATA_FIELDS = (
    "source_image_hash",
    "rendered_image_hash",
    "payload_hash",
)

_FINGERPRINT_RE = re.compile(r"^[0-9a-f]{64}$")
_FORBIDDEN_KEYS = {
    "api_key",
    "authorization",
    "access_token",
    "auth_token",
    "bearer_token",
    "refresh_token",
    "session_token",
    "password",
    "secret",
    "credential",
    "credentials",
    "image_bytes",
    "image_data",
    "payload_bytes",
}

# Same-state observations are permitted so metadata returned later can be
# appended without rewriting the submission event.  Terminal states stay
# terminal.  An ambiguous submission must pass through reconciling before a
# terminal result can be recorded.
_ALLOWED_TRANSITIONS = {
    RequestStatus.RESERVED: {
        RequestStatus.RESERVED,
        RequestStatus.SUBMITTED,
        RequestStatus.NETWORK_FAILURE,
        RequestStatus.CAPACITY_FAILURE,
        RequestStatus.AMBIGUOUS_SUBMISSION,
        RequestStatus.FAILED,
        RequestStatus.NON_RETRYABLE_FAILURE,
    },
    RequestStatus.SUBMITTED: {
        RequestStatus.SUBMITTED,
        RequestStatus.RECONCILING,
        RequestStatus.OK,
        RequestStatus.PARSE_FAIL_KEPT,
        RequestStatus.NETWORK_FAILURE,
        RequestStatus.CAPACITY_FAILURE,
        RequestStatus.AMBIGUOUS_SUBMISSION,
        RequestStatus.FAILED,
        RequestStatus.NON_RETRYABLE_FAILURE,
    },
    RequestStatus.AMBIGUOUS_SUBMISSION: {
        RequestStatus.AMBIGUOUS_SUBMISSION,
        RequestStatus.RECONCILING,
    },
    RequestStatus.RECONCILING: {
        RequestStatus.RECONCILING,
        RequestStatus.OK,
        RequestStatus.PARSE_FAIL_KEPT,
        RequestStatus.NETWORK_FAILURE,
        RequestStatus.CAPACITY_FAILURE,
        RequestStatus.FAILED,
        RequestStatus.NON_RETRYABLE_FAILURE,
    },
    RequestStatus.NETWORK_FAILURE: {
        RequestStatus.NETWORK_FAILURE,
        RequestStatus.RESERVED,
        RequestStatus.SUBMITTED,
        RequestStatus.CAPACITY_FAILURE,
        RequestStatus.FAILED,
        RequestStatus.NON_RETRYABLE_FAILURE,
    },
    RequestStatus.FAILED: {
        RequestStatus.FAILED,
        RequestStatus.RESERVED,
        RequestStatus.SUBMITTED,
        RequestStatus.NON_RETRYABLE_FAILURE,
    },
    RequestStatus.OK: {RequestStatus.OK},
    RequestStatus.PARSE_FAIL_KEPT: {RequestStatus.PARSE_FAIL_KEPT},
    RequestStatus.CAPACITY_FAILURE: {RequestStatus.CAPACITY_FAILURE},
    RequestStatus.NON_RETRYABLE_FAILURE: {RequestStatus.NON_RETRYABLE_FAILURE},
}

LedgerKey = Tuple[str, str, str, int]


class RequestLedgerError(ValueError):
    """Base class for explicit ledger validation/read failures."""


class RequestDescriptorError(RequestLedgerError):
    """Raised when a request descriptor cannot be safely fingerprinted."""


class LedgerRecordError(RequestLedgerError):
    """Raised when a ledger record or its history is invalid."""


class MalformedLedgerError(RequestLedgerError):
    """Raised with path and line evidence when JSONL cannot be read exactly."""


def canonical_request_json(descriptor: Mapping[str, Any]) -> str:
    """Return the canonical JSON serialization used for fingerprinting.

    The closed minimum field set prevents accidental row-position-only or
    partial fingerprints.  Additional JSON-serializable provider-neutral
    fields are retained in the fingerprint.
    """
    if not isinstance(descriptor, Mapping):
        raise RequestDescriptorError("request descriptor must be a mapping")
    missing = [name for name in REQUEST_DESCRIPTOR_FIELDS if name not in descriptor]
    if missing:
        raise RequestDescriptorError(
            f"request descriptor missing fingerprint dimension(s): {missing}"
        )

    for name in ("model_id", "prompt_hash", "schema_hash", "source_image_hash", "transform_id", "route_transport_version"):
        value = descriptor[name]
        if not isinstance(value, str) or not value:
            raise RequestDescriptorError(f"request descriptor field {name!r} must be a nonempty string")
    _validate_nonnegative_int("sample_index", descriptor["sample_index"], RequestDescriptorError)
    if not isinstance(descriptor["generation_params"], Mapping):
        raise RequestDescriptorError("request descriptor field 'generation_params' must be a mapping")
    _reject_forbidden_content(descriptor, RequestDescriptorError, "request descriptor")

    try:
        return json.dumps(
            descriptor,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise RequestDescriptorError(
            f"request descriptor must be finite JSON-serializable data: {exc}"
        ) from exc


def request_fingerprint(descriptor: Mapping[str, Any]) -> str:
    """Return lowercase SHA-256 for the canonical request descriptor."""
    canonical = canonical_request_json(descriptor).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def record_key(record: Mapping[str, Any]) -> LedgerKey:
    """Return the explicit four-part request key after validating the record."""
    validate_record(record)
    return (
        record["doc_id"],
        record["model_id"],
        record["transform_id"],
        record["sample_index"],
    )


def validate_record(record: Mapping[str, Any]) -> None:
    """Validate one self-contained ledger event without modifying it."""
    if not isinstance(record, Mapping):
        raise LedgerRecordError("ledger record must be a mapping")
    missing = [name for name in REQUIRED_RECORD_FIELDS if name not in record]
    if missing:
        raise LedgerRecordError(f"ledger record missing required field(s): {missing}")
    if record["schema_version"] != LEDGER_SCHEMA_VERSION:
        raise LedgerRecordError(
            f"unsupported ledger schema_version {record['schema_version']!r}; expected {LEDGER_SCHEMA_VERSION}"
        )
    for name in ("doc_id", "model_id", "transform_id", "prompt_hash"):
        if not isinstance(record[name], str) or not record[name]:
            raise LedgerRecordError(f"ledger record field {name!r} must be a nonempty string")
    _validate_nonnegative_int("sample_index", record["sample_index"], LedgerRecordError)
    _validate_nonnegative_int("attempt_count", record["attempt_count"], LedgerRecordError)
    _validate_nonnegative_int("retry_count", record["retry_count"], LedgerRecordError)

    fingerprint = record["request_fingerprint"]
    if not isinstance(fingerprint, str) or not _FINGERPRINT_RE.fullmatch(fingerprint):
        raise LedgerRecordError(
            "ledger record field 'request_fingerprint' must be a lowercase 64-character SHA-256 hex string"
        )
    try:
        RequestStatus(record["status"])
    except (TypeError, ValueError) as exc:
        raise LedgerRecordError(f"unknown ledger record status: {record['status']!r}") from exc

    for name in IDENTITY_METADATA_FIELDS:
        if name in record and (
            not isinstance(record[name], str) or not record[name]
        ):
            raise LedgerRecordError(
                f"optional identity field {name!r} must be a nonempty string when supplied"
            )
    for name in (
        "request_timestamp_utc",
        "response_timestamp_utc",
        "updated_timestamp_utc",
        "raw_response_ref",
        "provider",
        "returned_model_id",
        "parser_version",
        "pricing_snapshot_id",
    ):
        if name in record and (
            not isinstance(record[name], str) or not record[name]
        ):
            raise LedgerRecordError(
                f"optional metadata field {name!r} must be a nonempty string when supplied"
            )
    if "raw_response_text" in record and not isinstance(record["raw_response_text"], str):
        raise LedgerRecordError("optional field 'raw_response_text' must be a string when supplied")
    if "usage" in record and not isinstance(record["usage"], Mapping):
        raise LedgerRecordError("optional field 'usage' must be a mapping when supplied")
    if "latency_seconds" in record:
        latency = record["latency_seconds"]
        if isinstance(latency, bool) or not isinstance(latency, (int, float)) or latency < 0:
            raise LedgerRecordError("optional field 'latency_seconds' must be a nonnegative number")

    _reject_forbidden_content(record, LedgerRecordError, "ledger record")
    try:
        json.dumps(record, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise LedgerRecordError(f"ledger record must be finite JSON-serializable data: {exc}") from exc


def validate_history(records: Sequence[Mapping[str, Any]]) -> None:
    """Validate records and every repeated-key transition in append order."""
    previous_by_key = {}
    for index, record in enumerate(records):
        try:
            validate_record(record)
        except LedgerRecordError as exc:
            raise LedgerRecordError(f"record {index}: {exc}") from exc
        key = (
            record["doc_id"],
            record["model_id"],
            record["transform_id"],
            record["sample_index"],
        )
        previous = previous_by_key.get(key)
        if previous is not None:
            if record["request_fingerprint"] != previous["request_fingerprint"]:
                raise LedgerRecordError(
                    f"record {index} changes request_fingerprint for key {key!r}"
                )
            if record["prompt_hash"] != previous["prompt_hash"]:
                raise LedgerRecordError(f"record {index} changes prompt_hash for key {key!r}")
            for count_name in ("attempt_count", "retry_count"):
                if record[count_name] < previous[count_name]:
                    raise LedgerRecordError(
                        f"record {index} decreases {count_name} for key {key!r}"
                    )
            old_status = RequestStatus(previous["status"])
            new_status = RequestStatus(record["status"])
            if new_status not in _ALLOWED_TRANSITIONS[old_status]:
                raise LedgerRecordError(
                    f"record {index} has invalid status transition for key {key!r}: "
                    f"{old_status.value!r} -> {new_status.value!r}"
                )
        previous_by_key[key] = record


def read_ledger(path: "str | Path") -> list:
    """Read and validate every JSONL event; malformed input always fails."""
    ledger_path = Path(path)
    if not ledger_path.exists():
        return []
    records = []
    try:
        with ledger_path.open("rb") as stream:
            for line_number, raw_line in enumerate(stream, start=1):
                if not raw_line.strip():
                    raise MalformedLedgerError(
                        f"{ledger_path}: line {line_number}: blank JSONL records are not allowed"
                    )
                try:
                    text = raw_line.decode("utf-8")
                except UnicodeDecodeError as exc:
                    raise MalformedLedgerError(
                        f"{ledger_path}: line {line_number}: invalid UTF-8: {exc}"
                    ) from exc
                try:
                    record = json.loads(text)
                except json.JSONDecodeError as exc:
                    raise MalformedLedgerError(
                        f"{ledger_path}: line {line_number}: malformed JSON: {exc.msg} "
                        f"at column {exc.colno}"
                    ) from exc
                if not isinstance(record, dict):
                    raise MalformedLedgerError(
                        f"{ledger_path}: line {line_number}: JSONL record must be an object"
                    )
                records.append(record)
    except OSError as exc:
        raise MalformedLedgerError(f"cannot read ledger {ledger_path}: {exc}") from exc

    try:
        validate_history(records)
    except LedgerRecordError as exc:
        raise MalformedLedgerError(f"{ledger_path}: invalid ledger history: {exc}") from exc
    return records


def append_record(path: "str | Path", record: Mapping[str, Any]) -> None:
    """Validate and append one canonical JSON line while preserving prior bytes.

    Existing bytes are read and validated first.  A missing terminal newline is
    repaired only by appending a delimiter before the new record; existing
    bytes remain an exact prefix of the resulting file.
    """
    ledger_path = Path(path)
    existing = read_ledger(ledger_path)
    candidate = dict(record)
    validate_history([*existing, candidate])
    encoded = json.dumps(
        candidate,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")

    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    prefix = b""
    try:
        if ledger_path.exists() and ledger_path.stat().st_size:
            with ledger_path.open("rb") as stream:
                stream.seek(-1, os.SEEK_END)
                if stream.read(1) != b"\n":
                    prefix = b"\n"
        with ledger_path.open("ab") as stream:
            stream.write(prefix + encoded + b"\n")
            stream.flush()
            os.fsync(stream.fileno())
    except OSError as exc:
        raise RequestLedgerError(f"cannot append ledger {ledger_path}: {exc}") from exc


def latest_record(
    records: Sequence[Mapping[str, Any]], key: LedgerKey
) -> Optional[Mapping[str, Any]]:
    """Return the latest event for a key without discarding earlier events."""
    validate_history(records)
    _validate_key(key)
    result = None
    for record in records:
        if (
            record["doc_id"],
            record["model_id"],
            record["transform_id"],
            record["sample_index"],
        ) == key:
            result = record
    return result


def decide_ledger_action(
    records: Sequence[Mapping[str, Any]],
    key: LedgerKey,
    *,
    request_fingerprint: str,
    consecutive_network_or_capacity_failures: int = 0,
) -> RetryDecision:
    """Delegate the latest durable state to :func:`retry.decide_retry`.

    No provider action is performed.  With no prior event, a valid nonempty
    fingerprint yields ``PROCEED_INITIAL_ATTEMPT``.  Terminal rows skip only
    on an exact fingerprint match; ambiguous/reconciling rows remain
    reconcile-only, and capacity/network stop decisions remain those frozen in
    ``retry.py``.
    """
    stored = latest_record(records, key)
    if stored is None:
        if not isinstance(request_fingerprint, str) or not _FINGERPRINT_RE.fullmatch(request_fingerprint):
            raise LedgerRecordError(
                "a new request requires a lowercase 64-character SHA-256 request_fingerprint"
            )
        return decide_retry(RequestStatus.RESERVED)
    return decide_retry(
        stored["status"],
        retries_already_attempted=stored["retry_count"],
        consecutive_network_or_capacity_failures=consecutive_network_or_capacity_failures,
        request_fingerprint=request_fingerprint,
        stored_request_fingerprint=stored["request_fingerprint"],
    )


def _validate_key(key: LedgerKey) -> None:
    if not isinstance(key, tuple) or len(key) != 4:
        raise LedgerRecordError("ledger key must be a four-item tuple")
    for name, value in zip(("doc_id", "model_id", "transform_id"), key[:3]):
        if not isinstance(value, str) or not value:
            raise LedgerRecordError(f"ledger key field {name!r} must be a nonempty string")
    _validate_nonnegative_int("sample_index", key[3], LedgerRecordError)


def _validate_nonnegative_int(name: str, value: Any, error_type) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise error_type(f"{name} must be a nonnegative integer, got {value!r}")


def _reject_forbidden_content(value: Any, error_type, location: str, path: str = "") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).strip().lower().replace("-", "_")
            child_path = f"{path}.{key}" if path else str(key)
            if normalized in _FORBIDDEN_KEYS:
                raise error_type(
                    f"{location} contains forbidden credential/image-byte field {child_path!r}"
                )
            _reject_forbidden_content(child, error_type, location, child_path)
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_forbidden_content(child, error_type, location, f"{path}[{index}]")
    elif isinstance(value, (bytes, bytearray, memoryview)):
        raise error_type(f"{location} contains raw bytes at {path!r}; store only an identity/reference")
