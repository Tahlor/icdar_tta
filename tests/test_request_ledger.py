"""Dependency-light tests for the offline append-only request ledger."""

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from icdar_tta.request_ledger import (
    LedgerRecordError,
    MalformedLedgerError,
    RequestDescriptorError,
    append_record,
    canonical_request_json,
    decide_ledger_action,
    latest_record,
    read_ledger,
    request_fingerprint,
    validate_history,
    validate_record,
)
from icdar_tta.retry import RetryDecision


class LedgerFixtures:
    def descriptor(self, **overrides):
        value = {
            "model_id": "model-exact-v1",
            "prompt_hash": "prompt-sha256",
            "schema_hash": "schema-sha256",
            "source_image_hash": "source-sha256",
            "transform_id": "shift_only.variant_00",
            "sample_index": 0,
            "generation_params": {"temperature": 0, "max_output_tokens": 2048},
            "route_transport_version": "direct-json-image-v1",
        }
        value.update(overrides)
        return value

    def record(self, **overrides):
        descriptor = self.descriptor()
        value = {
            "schema_version": 1,
            "doc_id": "doc-001",
            "model_id": descriptor["model_id"],
            "transform_id": descriptor["transform_id"],
            "sample_index": descriptor["sample_index"],
            "request_fingerprint": request_fingerprint(descriptor),
            "prompt_hash": descriptor["prompt_hash"],
            "status": "reserved",
            "attempt_count": 0,
            "retry_count": 0,
        }
        value.update(overrides)
        return value


class TestCanonicalFingerprint(unittest.TestCase, LedgerFixtures):
    def test_canonical_stability_ignores_mapping_insertion_order(self):
        descriptor = self.descriptor()
        reversed_descriptor = dict(reversed(list(descriptor.items())))
        reversed_descriptor["generation_params"] = {
            "max_output_tokens": 2048,
            "temperature": 0,
        }
        self.assertEqual(request_fingerprint(descriptor), request_fingerprint(reversed_descriptor))
        canonical = canonical_request_json(descriptor)
        expected = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        self.assertEqual(request_fingerprint(descriptor), expected)
        self.assertNotIn(" ", canonical)

    def test_every_closed_request_dimension_changes_fingerprint(self):
        base = self.descriptor()
        mutations = {
            "model_id": "model-exact-v2",
            "prompt_hash": "other-prompt",
            "schema_hash": "other-schema",
            "source_image_hash": "other-source",
            "transform_id": "grid.variant_01",
            "sample_index": 1,
            "generation_params": {"temperature": 1, "max_output_tokens": 2048},
            "route_transport_version": "batch-jsonl-v2",
        }
        base_fingerprint = request_fingerprint(base)
        for field, changed_value in mutations.items():
            with self.subTest(field=field):
                changed = copy.deepcopy(base)
                changed[field] = changed_value
                self.assertNotEqual(base_fingerprint, request_fingerprint(changed))

    def test_distinct_explicit_keys_are_not_row_position_fingerprints(self):
        first = self.descriptor(sample_index=0)
        second = self.descriptor(sample_index=1)
        self.assertNotEqual(request_fingerprint(first), request_fingerprint(second))

    def test_missing_dimension_and_nonfinite_json_fail_explicitly(self):
        descriptor = self.descriptor()
        del descriptor["source_image_hash"]
        with self.assertRaisesRegex(RequestDescriptorError, "source_image_hash"):
            request_fingerprint(descriptor)
        with self.assertRaisesRegex(RequestDescriptorError, "finite JSON"):
            request_fingerprint(self.descriptor(generation_params={"temperature": float("nan")}))


class TestRecordValidation(unittest.TestCase, LedgerFixtures):
    def test_required_identity_counts_and_closed_status_validate(self):
        validate_record(self.record())
        for change in (
            {"doc_id": ""},
            {"sample_index": -1},
            {"attempt_count": True},
            {"retry_count": -1},
            {"status": "unknown"},
            {"request_fingerprint": "not-a-sha256"},
        ):
            with self.subTest(change=change):
                with self.assertRaises(LedgerRecordError):
                    validate_record(self.record(**change))

    def test_credentials_and_raw_image_bytes_are_rejected_recursively(self):
        for change in (
            {"metadata": {"authorization": "redacted-but-forbidden"}},
            {"image_bytes": "base64-is-still-forbidden-here"},
            {"metadata": {"blob": b"raw bytes"}},
        ):
            with self.subTest(change=change):
                with self.assertRaisesRegex(LedgerRecordError, "forbidden|raw bytes"):
                    validate_record(self.record(**change))

    def test_optional_raw_response_and_metadata_are_preserved_exactly(self):
        record = self.record(
            status="ok",
            attempt_count=1,
            source_image_hash="source-sha256",
            rendered_image_hash="render-sha256",
            payload_hash="payload-sha256",
            request_timestamp_utc="2026-08-29T20:00:00Z",
            response_timestamp_utc="2026-08-29T20:00:01Z",
            usage={"input_units": 123, "output_units": 45},
            error={"code": None, "message": ""},
            latency_seconds=0.25,
            raw_response_ref="private-store://response-id-1",
            raw_response_text='{"result":"María"}',
        )
        validate_record(record)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            append_record(path, record)
            self.assertEqual(read_ledger(path), [record])

    def test_raw_response_fields_are_absent_unless_caller_supplies_them(self):
        record = self.record()
        validate_record(record)
        self.assertNotIn("raw_response_ref", record)
        self.assertNotIn("raw_response_text", record)


class TestAppendReadAndHistory(unittest.TestCase, LedgerFixtures):
    def test_append_read_round_trip_is_canonical_newline_delimited_jsonl(self):
        first = self.record()
        second = self.record(status="submitted", attempt_count=1)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nested" / "ledger.jsonl"
            append_record(path, first)
            before = path.read_bytes()
            append_record(path, second)
            after = path.read_bytes()
            self.assertTrue(after.startswith(before))
            self.assertTrue(after.endswith(b"\n"))
            self.assertEqual(len(after.splitlines()), 2)
            self.assertEqual(read_ledger(path), [first, second])

    def test_append_preserves_valid_prior_bytes_without_terminal_newline(self):
        first = self.record()
        second = self.record(status="submitted", attempt_count=1)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            original = json.dumps(first, sort_keys=True, separators=(",", ":")).encode("utf-8")
            path.write_bytes(original)
            append_record(path, second)
            self.assertTrue(path.read_bytes().startswith(original))
            self.assertEqual(read_ledger(path), [first, second])

    def test_duplicate_key_history_is_retained_and_latest_is_explicit(self):
        records = [
            self.record(),
            self.record(status="submitted", attempt_count=1),
            self.record(status="ok", attempt_count=1),
        ]
        validate_history(records)
        key = ("doc-001", "model-exact-v1", "shift_only.variant_00", 0)
        self.assertEqual(latest_record(records, key), records[-1])
        self.assertEqual(len(records), 3)

    def test_second_explicit_key_remains_independent(self):
        first = self.record()
        descriptor = self.descriptor(sample_index=1)
        second = self.record(
            sample_index=1,
            request_fingerprint=request_fingerprint(descriptor),
        )
        validate_history([first, second])
        self.assertNotEqual(first["request_fingerprint"], second["request_fingerprint"])

    def test_fingerprint_change_for_duplicate_key_is_rejected_without_append(self):
        first = self.record()
        changed = self.record(request_fingerprint="f" * 64)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            append_record(path, first)
            before = path.read_bytes()
            with self.assertRaisesRegex(LedgerRecordError, "changes request_fingerprint"):
                append_record(path, changed)
            self.assertEqual(path.read_bytes(), before)

    def test_attempt_retry_counts_cannot_decrease(self):
        first = self.record(status="failed", attempt_count=2, retry_count=1)
        for field in ("attempt_count", "retry_count"):
            changed = self.record(status="failed", attempt_count=2, retry_count=1)
            changed[field] = 0
            with self.subTest(field=field):
                with self.assertRaisesRegex(LedgerRecordError, f"decreases {field}"):
                    validate_history([first, changed])

    def test_terminal_and_ambiguous_shortcut_transitions_are_rejected(self):
        with self.assertRaisesRegex(LedgerRecordError, "invalid status transition"):
            validate_history([
                self.record(status="ok", attempt_count=1),
                self.record(status="submitted", attempt_count=2, retry_count=1),
            ])
        with self.assertRaisesRegex(LedgerRecordError, "invalid status transition"):
            validate_history([
                self.record(status="ambiguous_submission", attempt_count=1),
                self.record(status="ok", attempt_count=1),
            ])

    def test_nonexistent_and_empty_ledgers_read_as_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            self.assertEqual(read_ledger(path), [])
            path.write_bytes(b"")
            self.assertEqual(read_ledger(path), [])


class TestMalformedLedger(unittest.TestCase, LedgerFixtures):
    def test_malformed_json_reports_path_and_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            path.write_text(json.dumps(self.record()) + "\n{not json}\n", encoding="utf-8")
            with self.assertRaisesRegex(MalformedLedgerError, r"ledger\.jsonl: line 2: malformed JSON"):
                read_ledger(path)

    def test_blank_line_and_nonobject_fail_explicitly(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name, content, message in (
                ("blank.jsonl", "\n", "blank JSONL"),
                ("array.jsonl", "[]\n", "must be an object"),
            ):
                with self.subTest(name=name):
                    path = Path(tmp) / name
                    path.write_text(content, encoding="utf-8")
                    with self.assertRaisesRegex(MalformedLedgerError, message):
                        read_ledger(path)

    def test_valid_json_with_invalid_record_is_malformed_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            path.write_text('{"doc_id":"only-one-field"}\n', encoding="utf-8")
            with self.assertRaisesRegex(MalformedLedgerError, "missing required field"):
                read_ledger(path)


class TestRetryIntegration(unittest.TestCase, LedgerFixtures):
    def test_new_key_proceeds_only_with_valid_fingerprint(self):
        fingerprint = request_fingerprint(self.descriptor())
        self.assertEqual(
            decide_ledger_action([], ("doc-001", "model-exact-v1", "shift_only.variant_00", 0), request_fingerprint=fingerprint),
            RetryDecision.PROCEED_INITIAL_ATTEMPT,
        )
        with self.assertRaisesRegex(LedgerRecordError, "new request requires"):
            decide_ledger_action([], ("doc-001", "model-exact-v1", "shift_only.variant_00", 0), request_fingerprint="")

    def test_terminal_ok_and_parse_fail_skip_only_on_exact_nonempty_match(self):
        for status in ("ok", "parse_fail_kept"):
            record = self.record(status=status, attempt_count=1)
            key = ("doc-001", "model-exact-v1", "shift_only.variant_00", 0)
            with self.subTest(status=status, case="matching"):
                self.assertEqual(
                    decide_ledger_action([record], key, request_fingerprint=record["request_fingerprint"]),
                    RetryDecision.SKIP_MATCHING_TERMINAL,
                )
            for fingerprint in ("e" * 64, ""):
                with self.subTest(status=status, fingerprint=fingerprint):
                    self.assertEqual(
                        decide_ledger_action([record], key, request_fingerprint=fingerprint),
                        RetryDecision.STOP_FINGERPRINT_MISMATCH,
                    )

    def test_ambiguous_and_reconciling_are_reconcile_only(self):
        key = ("doc-001", "model-exact-v1", "shift_only.variant_00", 0)
        for status in ("ambiguous_submission", "reconciling"):
            record = self.record(status=status, attempt_count=1)
            with self.subTest(status=status):
                self.assertEqual(
                    decide_ledger_action([record], key, request_fingerprint=record["request_fingerprint"]),
                    RetryDecision.RECONCILE_ONLY,
                )

    def test_capacity_and_fifth_network_stops_remain_explicit(self):
        key = ("doc-001", "model-exact-v1", "shift_only.variant_00", 0)
        capacity = self.record(status="capacity_failure", attempt_count=1)
        self.assertEqual(
            decide_ledger_action([capacity], key, request_fingerprint=capacity["request_fingerprint"]),
            RetryDecision.STOP_CAPACITY,
        )
        network = self.record(status="network_failure", attempt_count=1)
        self.assertEqual(
            decide_ledger_action(
                [network],
                key,
                request_fingerprint=network["request_fingerprint"],
                consecutive_network_or_capacity_failures=5,
            ),
            RetryDecision.STOP_FIVE_CONSECUTIVE_FAILURES,
        )

    def test_retry_count_is_delegated_to_frozen_retry_policy(self):
        key = ("doc-001", "model-exact-v1", "shift_only.variant_00", 0)
        first_failure = self.record(status="failed", attempt_count=1, retry_count=0)
        exhausted = self.record(status="failed", attempt_count=2, retry_count=1)
        self.assertEqual(
            decide_ledger_action([first_failure], key, request_fingerprint=first_failure["request_fingerprint"]),
            RetryDecision.RETRY_ONCE,
        )
        self.assertEqual(
            decide_ledger_action([exhausted], key, request_fingerprint=exhausted["request_fingerprint"]),
            RetryDecision.KEEP_FAILED,
        )


if __name__ == "__main__":
    unittest.main()
