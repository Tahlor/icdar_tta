"""Strict offline parser for the frozen PA v1.49 confidence prompt.

By default :func:`parse_response_json` requires the exact 44-field response
schema in ``prompt_v1.49_confidence.txt``.  The six historically evaluated
name fields are a downstream projection, not the model-response schema; their
source lineage and record-level exclusion are documented in
``docs/GT_LINEAGE.md``.
Callers may explicitly pass ``allowed_fields`` for a legacy/custom closed
schema; that opt-in never changes the strict default.

Repairs are intentionally limited and audited on successful results: remove a
complete leading ``<think>...</think>`` block, remove at most one complete
outer Markdown JSON fence, try direct JSON decoding, then try exactly one
outermost-braced-object extraction.  Raw failures are always preserved.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Sequence


class ParseFailureReason(str, Enum):
    """Closed reason set used for reproducible parser-failure reporting."""

    EMPTY_RESPONSE = "empty_response"
    NOT_JSON = "not_json"
    NOT_JSON_OBJECT = "not_json_object"
    MISSING_REQUIRED_FIELD = "missing_required_field"
    UNKNOWN_FIELD_NAME = "unknown_field_name"
    WRONG_TYPE = "wrong_type"
    INVALID_CONFIDENCE = "invalid_confidence"
    INVALID_SELF_DEATH_AGE = "invalid_self_death_age"
    TRUNCATED = "truncated"
    PROVIDER_ERROR_STATUS = "provider_error_status"


class ParseError(ValueError):
    """Programmer-error input, such as an invalid ``allowed_fields`` value."""


@dataclass(frozen=True)
class ParseFailure:
    """Explicit, non-exceptional malformed-response record."""

    reason: ParseFailureReason
    detail: str
    raw_response: Any = field(repr=False, default=None)


@dataclass(frozen=True)
class ParsedFields:
    """Validated field values, confidences, and the auditable repair path."""

    values: dict
    confidences: dict
    repair_path: tuple


# Exact Required Fields order in PA_DEATH/prompts/prompt_v1.49_confidence.txt.
PA_V149_REQUIRED_FIELDS = (
    "SelfNamePrefix",
    "SelfGivenName",
    "SelfSurname",
    "SelfNameSuffix",
    "SelfGender",
    "SelfRace",
    "SelfMaritalStatus",
    "SelfDeathDay",
    "SelfDeathMonth",
    "SelfDeathYear",
    "SelfDeathAge",
    "SelfDeathCity",
    "SelfDeathCounty",
    "SelfBurialDay",
    "SelfBurialMonth",
    "SelfBurialYear",
    "SelfBurialCity",
    "SelfBurialCounty",
    "SelfBurialState",
    "SelfBurialCountry",
    "SelfBurialCemetery",
    "SelfBirthDay",
    "SelfBirthMonth",
    "SelfBirthYear",
    "SelfBirthCity",
    "SelfBirthCounty",
    "SelfBirthState",
    "SelfBirthCountry",
    "SpouseNamePrefix",
    "SpouseGivenName",
    "SpouseSurname",
    "SpouseNameSuffix",
    "FatherNamePrefix",
    "FatherGivenName",
    "FatherSurname",
    "FatherNameSuffix",
    "FatherBirthPlace",
    "MotherNamePrefix",
    "MotherGivenName",
    "MotherSurname",
    "MotherNameSuffix",
    "MotherBirthPlace",
    "CauseOfDeath",
    "FormRevision",
)

# Historical evaluation projection.  It is deliberately not the parser default.
EVALUATED_NAME_FIELDS = (
    "SelfGivenName",
    "SelfSurname",
    "FatherGivenName",
    "FatherSurname",
    "MotherGivenName",
    "MotherSurname",
)

# Backwards-compatible import name; callers must pass it explicitly if they
# intentionally want the six-field projection schema.
CANONICAL_NAME_FIELDS = EVALUATED_NAME_FIELDS

_OK_API_STATUSES = ("ok", "success", "200")
_THINK_BLOCK_RE = re.compile(r"^<think>.*?</think>\s*(.*)$", re.DOTALL)
_JSON_FENCE_RE = re.compile(
    r"^```(?:json)?[ \t]*\r?\n(?P<body>.*)\r?\n```[ \t]*$",
    re.IGNORECASE | re.DOTALL,
)


def parse_response_json(
    raw_response: str,
    *,
    allowed_fields: Optional[Sequence[str]] = None,
    api_status: Optional[str] = None,
) -> "ParsedFields | ParseFailure":
    """Parse and validate one frozen PA v1.49 model response.

    With the default ``allowed_fields=None``, the top-level object must contain
    exactly :data:`PA_V149_REQUIRED_FIELDS`.  Every field must be an object
    containing exactly ``value`` and ``confidence``.  Confidence is an integer
    from 1 through 10 (``bool`` is rejected).  Values are strings, except
    ``SelfDeathAge``, whose value is exactly three strings.

    Passing ``allowed_fields`` is an explicit compatibility opt-in to another
    exact closed top-level field set.  Inner object, confidence, and value rules
    remain strict, including the age exception when ``SelfDeathAge`` is present.
    """
    fields = _resolve_allowed_fields(allowed_fields)

    if api_status is not None and api_status not in _OK_API_STATUSES:
        return ParseFailure(
            ParseFailureReason.PROVIDER_ERROR_STATUS,
            detail=f"api_status={api_status!r}",
            raw_response=raw_response,
        )

    if raw_response is None or str(raw_response).strip() == "":
        return ParseFailure(
            ParseFailureReason.EMPTY_RESPONSE,
            detail="empty or whitespace-only response",
            raw_response=raw_response,
        )

    text, repair_steps = _remove_documented_wrappers(str(raw_response))
    payload, decode_step, decode_failure = _decode_payload(text)
    if decode_failure is not None:
        reason, detail = decode_failure
        return ParseFailure(reason, detail=detail, raw_response=raw_response)
    repair_steps.append(decode_step)

    if not isinstance(payload, dict):
        return ParseFailure(
            ParseFailureReason.NOT_JSON_OBJECT,
            detail=f"top-level JSON type is {type(payload).__name__}; expected object",
            raw_response=raw_response,
        )

    expected = set(fields)
    actual = set(payload)
    unknown = sorted(actual - expected)
    if unknown:
        return ParseFailure(
            ParseFailureReason.UNKNOWN_FIELD_NAME,
            detail=f"top-level object has unrecognized field name(s): {unknown}",
            raw_response=raw_response,
        )
    missing = [name for name in fields if name not in actual]
    if missing:
        return ParseFailure(
            ParseFailureReason.MISSING_REQUIRED_FIELD,
            detail=f"top-level object is missing required field(s): {missing}",
            raw_response=raw_response,
        )

    values = {}
    confidences = {}
    for name in fields:
        field_payload = payload[name]
        if not isinstance(field_payload, dict):
            return ParseFailure(
                ParseFailureReason.WRONG_TYPE,
                detail=(
                    f"field {name!r} must be an object with exactly 'value' and "
                    f"'confidence'; got {type(field_payload).__name__}"
                ),
                raw_response=raw_response,
            )

        inner_keys = set(field_payload)
        unknown_inner = sorted(inner_keys - {"value", "confidence"})
        if unknown_inner:
            return ParseFailure(
                ParseFailureReason.UNKNOWN_FIELD_NAME,
                detail=f"field {name!r} has unrecognized member(s): {unknown_inner}",
                raw_response=raw_response,
            )
        missing_inner = [key for key in ("value", "confidence") if key not in inner_keys]
        if missing_inner:
            return ParseFailure(
                ParseFailureReason.MISSING_REQUIRED_FIELD,
                detail=f"field {name!r} is missing required member(s): {missing_inner}",
                raw_response=raw_response,
            )

        confidence = field_payload["confidence"]
        if isinstance(confidence, bool) or not isinstance(confidence, int) or not 1 <= confidence <= 10:
            return ParseFailure(
                ParseFailureReason.INVALID_CONFIDENCE,
                detail=(
                    f"field {name!r} confidence must be an integer from 1 through 10 "
                    f"(bool is invalid); got {confidence!r} ({type(confidence).__name__})"
                ),
                raw_response=raw_response,
            )

        value = field_payload["value"]
        if name == "SelfDeathAge":
            if not (
                isinstance(value, list)
                and len(value) == 3
                and all(isinstance(part, str) for part in value)
            ):
                return ParseFailure(
                    ParseFailureReason.INVALID_SELF_DEATH_AGE,
                    detail=(
                        "field 'SelfDeathAge' value must be an array of exactly three "
                        f"strings [years, months, days]; got {value!r}"
                    ),
                    raw_response=raw_response,
                )
        elif not isinstance(value, str):
            return ParseFailure(
                ParseFailureReason.WRONG_TYPE,
                detail=f"field {name!r} value must be a string; got {type(value).__name__}",
                raw_response=raw_response,
            )

        values[name] = value
        confidences[name] = confidence

    return ParsedFields(
        values=values,
        confidences=confidences,
        repair_path=tuple(repair_steps),
    )


def _resolve_allowed_fields(allowed_fields: Optional[Sequence[str]]) -> tuple:
    if allowed_fields is None:
        return PA_V149_REQUIRED_FIELDS
    if isinstance(allowed_fields, (str, bytes)):
        raise ParseError("allowed_fields must be a sequence of field-name strings, not a string")
    try:
        fields = tuple(allowed_fields)
    except TypeError as exc:
        raise ParseError("allowed_fields must be an iterable of field-name strings") from exc
    if any(not isinstance(name, str) or not name for name in fields):
        raise ParseError("allowed_fields entries must be nonempty strings")
    if len(set(fields)) != len(fields):
        raise ParseError("allowed_fields must not contain duplicate field names")
    return fields


def _remove_documented_wrappers(text: str) -> "tuple[str, list[str]]":
    stripped = text.strip()
    steps = []

    think_match = _THINK_BLOCK_RE.fullmatch(stripped)
    if think_match is not None:
        stripped = think_match.group(1).strip()
        steps.append("remove_complete_think_block")

    fence_match = _JSON_FENCE_RE.fullmatch(stripped)
    if fence_match is not None:
        stripped = fence_match.group("body").strip()
        steps.append("remove_outer_markdown_json_fence")

    return stripped, steps


def _decode_payload(text: str) -> "tuple[Any, str, Optional[tuple[ParseFailureReason, str]]]":
    try:
        return json.loads(text), "direct_json", None
    except json.JSONDecodeError as direct_exc:
        direct_detail = f"direct JSON decode failed: {direct_exc}"

    first_open = text.find("{")
    last_close = text.rfind("}")
    if first_open >= 0 and last_close > first_open:
        candidate = text[first_open : last_close + 1]
        # Avoid retrying the identical text under a misleading repair label.
        if candidate != text:
            try:
                return json.loads(candidate), "extract_outermost_braced_object", None
            except json.JSONDecodeError as extraction_exc:
                detail = (
                    f"{direct_detail}; outermost-braced-object decode failed: "
                    f"{extraction_exc}"
                )
                reason = ParseFailureReason.TRUNCATED if _looks_truncated(candidate) else ParseFailureReason.NOT_JSON
                return None, "", (reason, detail)

    reason = ParseFailureReason.TRUNCATED if _looks_truncated(text) else ParseFailureReason.NOT_JSON
    extraction_detail = (
        "no complete outermost braced object was available"
        if first_open < 0 or last_close <= first_open
        else "outermost braced object was identical to the direct payload"
    )
    return None, "", (reason, f"{direct_detail}; {extraction_detail}")


def _looks_truncated(text: str) -> bool:
    """Detect unfinished strings/containers without treating syntax errors as truncation."""
    stack = []
    in_string = False
    escaped = False
    pairs = {"}": "{", "]": "["}

    for char in text:
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char in "{[":
            stack.append(char)
        elif char in "}]":
            if not stack or stack[-1] != pairs[char]:
                return False
            stack.pop()

    return in_string or bool(stack)
