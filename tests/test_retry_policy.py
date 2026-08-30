"""Unit tests for the deterministic provider-neutral retry policy."""

import unittest

from icdar_tta.retry import (
    MAX_CONSECUTIVE_NETWORK_OR_CAPACITY_FAILURES,
    MAX_RETRIES_PER_REQUEST,
    RETRY_POLICY_ID,
    RequestStatus,
    RetryDecision,
    RetryPolicyError,
    decide_retry,
)


class TestRetryPolicyConstants(unittest.TestCase):
    def test_frozen_policy_identity_and_limits(self):
        self.assertEqual(RETRY_POLICY_ID, "provider_neutral_retry_v1")
        self.assertEqual(MAX_RETRIES_PER_REQUEST, 1)
        self.assertEqual(MAX_CONSECUTIVE_NETWORK_OR_CAPACITY_FAILURES, 5)


class TestRetryLimitsAndStops(unittest.TestCase):
    def test_first_generic_failure_gets_one_retry(self):
        self.assertEqual(
            decide_retry(RequestStatus.FAILED, retries_already_attempted=0),
            RetryDecision.RETRY_ONCE,
        )

    def test_generic_failure_after_one_retry_is_kept(self):
        self.assertEqual(
            decide_retry(RequestStatus.FAILED, retries_already_attempted=1),
            RetryDecision.KEEP_FAILED,
        )

    def test_first_four_consecutive_network_failures_may_retry(self):
        for count in range(1, 5):
            with self.subTest(count=count):
                self.assertEqual(
                    decide_retry(
                        RequestStatus.NETWORK_FAILURE,
                        retries_already_attempted=0,
                        consecutive_network_or_capacity_failures=count,
                    ),
                    RetryDecision.RETRY_ONCE,
                )

    def test_retry_limit_still_applies_before_network_stop_threshold(self):
        self.assertEqual(
            decide_retry(
                RequestStatus.NETWORK_FAILURE,
                retries_already_attempted=1,
                consecutive_network_or_capacity_failures=4,
            ),
            RetryDecision.KEEP_FAILED,
        )

    def test_fifth_consecutive_network_failure_stops(self):
        self.assertEqual(
            decide_retry(
                RequestStatus.NETWORK_FAILURE,
                retries_already_attempted=0,
                consecutive_network_or_capacity_failures=5,
            ),
            RetryDecision.STOP_FIVE_CONSECUTIVE_FAILURES,
        )

    def test_counts_above_five_also_stop(self):
        self.assertEqual(
            decide_retry(
                RequestStatus.NETWORK_FAILURE,
                consecutive_network_or_capacity_failures=6,
            ),
            RetryDecision.STOP_FIVE_CONSECUTIVE_FAILURES,
        )

    def test_any_capacity_failure_stops_immediately(self):
        for count in (0, 1, 4, 5):
            with self.subTest(count=count):
                self.assertEqual(
                    decide_retry(
                        RequestStatus.CAPACITY_FAILURE,
                        consecutive_network_or_capacity_failures=count,
                    ),
                    RetryDecision.STOP_CAPACITY,
                )

    def test_nonretryable_failure_is_kept_explicitly(self):
        self.assertEqual(
            decide_retry(RequestStatus.NON_RETRYABLE_FAILURE),
            RetryDecision.KEEP_FAILED,
        )


class TestAmbiguityAndResume(unittest.TestCase):
    def test_ambiguous_submission_is_reconcile_only_even_without_retry(self):
        self.assertEqual(
            decide_retry(RequestStatus.AMBIGUOUS_SUBMISSION),
            RetryDecision.RECONCILE_ONLY,
        )

    def test_ambiguous_submission_is_never_retried_after_prior_retry(self):
        self.assertEqual(
            decide_retry(
                RequestStatus.AMBIGUOUS_SUBMISSION,
                retries_already_attempted=1,
            ),
            RetryDecision.RECONCILE_ONLY,
        )

    def test_reconciling_status_remains_reconcile_only(self):
        self.assertEqual(
            decide_retry(RequestStatus.RECONCILING),
            RetryDecision.RECONCILE_ONLY,
        )

    def test_terminal_statuses_skip_only_on_exact_nonempty_fingerprint_match(self):
        for status in (RequestStatus.OK, RequestStatus.PARSE_FAIL_KEPT):
            with self.subTest(status=status):
                self.assertEqual(
                    decide_retry(
                        status,
                        request_fingerprint="sha256:current",
                        stored_request_fingerprint="sha256:current",
                    ),
                    RetryDecision.SKIP_MATCHING_TERMINAL,
                )

    def test_terminal_fingerprint_mismatch_stops(self):
        self.assertEqual(
            decide_retry(
                RequestStatus.OK,
                request_fingerprint="sha256:current",
                stored_request_fingerprint="sha256:other",
            ),
            RetryDecision.STOP_FINGERPRINT_MISMATCH,
        )

    def test_terminal_missing_fingerprint_stops(self):
        for current, stored in ((None, None), ("sha256:current", None), (None, "sha256:stored"), ("", "")):
            with self.subTest(current=current, stored=stored):
                self.assertEqual(
                    decide_retry(
                        RequestStatus.PARSE_FAIL_KEPT,
                        request_fingerprint=current,
                        stored_request_fingerprint=stored,
                    ),
                    RetryDecision.STOP_FINGERPRINT_MISMATCH,
                )


class TestExplicitOtherStatusesAndValidation(unittest.TestCase):
    def test_reserved_proceeds_to_initial_attempt_not_retry(self):
        self.assertEqual(
            decide_retry(RequestStatus.RESERVED),
            RetryDecision.PROCEED_INITIAL_ATTEMPT,
        )

    def test_submitted_waits_for_terminal(self):
        self.assertEqual(
            decide_retry(RequestStatus.SUBMITTED),
            RetryDecision.WAIT_FOR_TERMINAL,
        )

    def test_string_enum_values_are_accepted_deterministically(self):
        self.assertEqual(decide_retry("failed"), RetryDecision.RETRY_ONCE)

    def test_unknown_status_is_rejected(self):
        with self.assertRaisesRegex(RetryPolicyError, "unknown request status"):
            decide_retry("mystery")

    def test_network_counter_must_include_current_failure(self):
        with self.assertRaisesRegex(RetryPolicyError, "at least 1"):
            decide_retry(
                RequestStatus.NETWORK_FAILURE,
                consecutive_network_or_capacity_failures=0,
            )

    def test_counters_reject_negative_noninteger_and_bool(self):
        for value in (-1, 0.5, True):
            with self.subTest(value=value):
                with self.assertRaises(RetryPolicyError):
                    decide_retry(RequestStatus.FAILED, retries_already_attempted=value)


if __name__ == "__main__":
    unittest.main()
