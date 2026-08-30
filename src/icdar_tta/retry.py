"""Deterministic, provider-neutral retry and resume decisions.

This module performs no I/O.  ``retries_already_attempted`` counts retries,
not the initial attempt, so only zero permits the policy's single retry.
``consecutive_network_or_capacity_failures`` includes the current failure.
Callers remain responsible for durable request ledgers and reconciliation.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional, Union


RETRY_POLICY_ID = "provider_neutral_retry_v1"
MAX_RETRIES_PER_REQUEST = 1
MAX_CONSECUTIVE_NETWORK_OR_CAPACITY_FAILURES = 5


class RetryPolicyError(ValueError):
    """Raised when a status or policy input is not explicit and valid."""


class RequestStatus(str, Enum):
    """Closed request-state set; unknown states are rejected, not guessed."""

    RESERVED = "reserved"
    SUBMITTED = "submitted"
    RECONCILING = "reconciling"
    OK = "ok"
    PARSE_FAIL_KEPT = "parse_fail_kept"
    NETWORK_FAILURE = "network_failure"
    CAPACITY_FAILURE = "capacity_failure"
    AMBIGUOUS_SUBMISSION = "ambiguous_submission"
    FAILED = "failed"
    NON_RETRYABLE_FAILURE = "non_retryable_failure"


class RetryDecision(str, Enum):
    """Exhaustive policy outcomes; none of them performs a provider call."""

    PROCEED_INITIAL_ATTEMPT = "proceed_initial_attempt"
    WAIT_FOR_TERMINAL = "wait_for_terminal"
    RECONCILE_ONLY = "reconcile_only"
    SKIP_MATCHING_TERMINAL = "skip_matching_terminal"
    STOP_FINGERPRINT_MISMATCH = "stop_fingerprint_mismatch"
    RETRY_ONCE = "retry_once"
    KEEP_FAILED = "keep_failed"
    STOP_FIVE_CONSECUTIVE_FAILURES = "stop_five_consecutive_failures"
    STOP_CAPACITY = "stop_capacity"


def decide_retry(
    status: Union[RequestStatus, str],
    *,
    retries_already_attempted: int = 0,
    consecutive_network_or_capacity_failures: int = 0,
    request_fingerprint: Optional[str] = None,
    stored_request_fingerprint: Optional[str] = None,
) -> RetryDecision:
    """Return the sole allowed action for one durable request state.

    Terminal ``ok`` and ``parse_fail_kept`` rows may be resumed/skipped only
    when their nonempty stored fingerprint exactly matches the current request
    fingerprint.  Ambiguous submissions are reconciliation-only.  Capacity
    failure always stops immediately.  A fifth consecutive network failure
    stops the run; earlier network failures and generic retryable failures get
    at most one retry.  Nonterminal and nonretryable statuses remain explicit.
    """
    try:
        explicit_status = status if isinstance(status, RequestStatus) else RequestStatus(status)
    except (TypeError, ValueError) as exc:
        raise RetryPolicyError(f"unknown request status: {status!r}") from exc

    _validate_nonnegative_int("retries_already_attempted", retries_already_attempted)
    _validate_nonnegative_int(
        "consecutive_network_or_capacity_failures",
        consecutive_network_or_capacity_failures,
    )

    if explicit_status in (RequestStatus.OK, RequestStatus.PARSE_FAIL_KEPT):
        if (
            request_fingerprint
            and stored_request_fingerprint
            and request_fingerprint == stored_request_fingerprint
        ):
            return RetryDecision.SKIP_MATCHING_TERMINAL
        return RetryDecision.STOP_FINGERPRINT_MISMATCH

    if explicit_status in (
        RequestStatus.AMBIGUOUS_SUBMISSION,
        RequestStatus.RECONCILING,
    ):
        return RetryDecision.RECONCILE_ONLY

    if explicit_status is RequestStatus.CAPACITY_FAILURE:
        return RetryDecision.STOP_CAPACITY

    if explicit_status is RequestStatus.NETWORK_FAILURE:
        if consecutive_network_or_capacity_failures < 1:
            raise RetryPolicyError(
                "consecutive_network_or_capacity_failures must include the current "
                "network failure and therefore be at least 1"
            )
        if (
            consecutive_network_or_capacity_failures
            >= MAX_CONSECUTIVE_NETWORK_OR_CAPACITY_FAILURES
        ):
            return RetryDecision.STOP_FIVE_CONSECUTIVE_FAILURES
        return _retry_or_keep(retries_already_attempted)

    if explicit_status is RequestStatus.FAILED:
        return _retry_or_keep(retries_already_attempted)

    if explicit_status is RequestStatus.NON_RETRYABLE_FAILURE:
        return RetryDecision.KEEP_FAILED

    if explicit_status is RequestStatus.RESERVED:
        return RetryDecision.PROCEED_INITIAL_ATTEMPT

    if explicit_status is RequestStatus.SUBMITTED:
        return RetryDecision.WAIT_FOR_TERMINAL

    # The closed enum and branches above should make this unreachable.  Keep an
    # explicit guard so a future status cannot silently inherit a decision.
    raise RetryPolicyError(f"request status has no policy decision: {explicit_status.value!r}")


def _retry_or_keep(retries_already_attempted: int) -> RetryDecision:
    if retries_already_attempted < MAX_RETRIES_PER_REQUEST:
        return RetryDecision.RETRY_ONCE
    return RetryDecision.KEEP_FAILED


def _validate_nonnegative_int(name: str, value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise RetryPolicyError(f"{name} must be a nonnegative integer, got {value!r}")
