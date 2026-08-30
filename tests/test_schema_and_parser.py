"""Field-table schema and frozen PA v1.49 parser contract tests."""

import json
import unittest

from icdar_tta.parser import (
    EVALUATED_NAME_FIELDS,
    PA_V149_REQUIRED_FIELDS,
    ParseError,
    ParseFailure,
    ParseFailureReason,
    ParsedFields,
    parse_response_json,
)
from icdar_tta.schema import (
    FieldRecord,
    SchemaError,
    count_distinct_documents,
    count_nonblank_ground_truth_fields,
    validate_table_schema,
)


EXPECTED_PA_V149_FIELDS = (
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


def make_pa_payload():
    payload = {
        name: {"value": "N/A", "confidence": 10}
        for name in PA_V149_REQUIRED_FIELDS
    }
    payload["SelfGivenName"] = {"value": "Mary", "confidence": 9}
    payload["SelfDeathAge"] = {"value": ["72", "", "4"], "confidence": 8}
    return payload


def dump_pa_payload(payload=None):
    return json.dumps(make_pa_payload() if payload is None else payload, separators=(",", ":"))


def make_record(**overrides):
    defaults = dict(
        doc_id="doc-1",
        field_name="SelfGivenName",
        ground_truth="Mary",
        model_id="gemini-2.0-flash",
        run_id="run-1",
        strategy="baseline",
        transform_id="none",
        sample_index=0,
        prediction="Mary",
        normalized_prediction="mary",
        is_exact_correct=True,
        cer=0.0,
        response_path_or_id="resp-1.json",
        fold="0",
    )
    defaults.update(overrides)
    return FieldRecord(**defaults)


class TestFieldRecord(unittest.TestCase):
    def test_valid_record_constructs(self):
        record = make_record()
        self.assertEqual(record.doc_id, "doc-1")

    def test_missing_identity_field_raises(self):
        with self.assertRaises(SchemaError):
            make_record(doc_id="")

    def test_negative_sample_index_raises(self):
        with self.assertRaises(SchemaError):
            make_record(sample_index=-1)

    def test_observation_key(self):
        record = make_record()
        self.assertEqual(
            record.observation_key,
            ("doc-1", "SelfGivenName", "gemini-2.0-flash", "run-1", "baseline", "none", 0),
        )

    def test_to_dict_round_trip(self):
        record = make_record()
        data = record.to_dict()
        self.assertEqual(data["doc_id"], "doc-1")
        self.assertEqual(data["cer"], 0.0)


class TestValidateTableSchema(unittest.TestCase):
    def test_valid_table_passes(self):
        validate_table_schema([make_record(), make_record(sample_index=1)])

    def test_missing_required_column_raises(self):
        with self.assertRaises(SchemaError):
            validate_table_schema([{"doc_id": "doc-1"}])

    def test_duplicate_observation_key_raises(self):
        with self.assertRaises(SchemaError):
            validate_table_schema([make_record(), make_record()])

    def test_conflicting_ground_truth_raises(self):
        rows = [
            make_record(sample_index=0, ground_truth="Mary"),
            make_record(sample_index=1, ground_truth="Marie"),
        ]
        with self.assertRaises(SchemaError):
            validate_table_schema(rows)

    def test_same_ground_truth_across_samples_ok(self):
        validate_table_schema(
            [make_record(sample_index=0), make_record(sample_index=1)]
        )


class TestDocumentAndFieldCounts(unittest.TestCase):
    def test_count_distinct_documents(self):
        rows = [
            make_record(doc_id="a"),
            make_record(doc_id="a", sample_index=1),
            make_record(doc_id="b"),
        ]
        self.assertEqual(count_distinct_documents(rows), 2)

    def test_count_nonblank_ground_truth_fields_excludes_blank(self):
        rows = [
            make_record(doc_id="a", field_name="f1", ground_truth="Mary"),
            make_record(doc_id="a", field_name="f2", ground_truth=None, sample_index=1),
            make_record(doc_id="a", field_name="f3", ground_truth="", sample_index=2),
        ]
        self.assertEqual(count_nonblank_ground_truth_fields(rows), 1)

    def test_count_nonblank_ground_truth_fields_dedupes_by_field(self):
        rows = [
            make_record(doc_id="a", field_name="f1", sample_index=0),
            make_record(doc_id="a", field_name="f1", sample_index=1),
        ]
        self.assertEqual(count_nonblank_ground_truth_fields(rows), 1)


class TestFrozenParserContract(unittest.TestCase):
    def test_required_field_names_and_order_match_frozen_prompt(self):
        self.assertEqual(PA_V149_REQUIRED_FIELDS, EXPECTED_PA_V149_FIELDS)
        self.assertEqual(len(PA_V149_REQUIRED_FIELDS), 44)
        self.assertEqual(len(set(PA_V149_REQUIRED_FIELDS)), 44)

    def test_evaluated_six_fields_are_only_a_downstream_projection(self):
        self.assertEqual(
            EVALUATED_NAME_FIELDS,
            (
                "SelfGivenName",
                "SelfSurname",
                "FatherGivenName",
                "FatherSurname",
                "MotherGivenName",
                "MotherSurname",
            ),
        )
        self.assertNotEqual(EVALUATED_NAME_FIELDS, PA_V149_REQUIRED_FIELDS)

    def test_complete_44_field_response_succeeds(self):
        result = parse_response_json(dump_pa_payload())
        self.assertIsInstance(result, ParsedFields)
        self.assertEqual(tuple(result.values), PA_V149_REQUIRED_FIELDS)
        self.assertEqual(result.values["SelfGivenName"], "Mary")
        self.assertEqual(result.confidences["SelfGivenName"], 9)
        self.assertEqual(result.repair_path, ("direct_json",))

    def test_self_death_age_three_string_array_succeeds(self):
        result = parse_response_json(dump_pa_payload())
        self.assertIsInstance(result, ParsedFields)
        self.assertEqual(result.values["SelfDeathAge"], ["72", "", "4"])

    def test_missing_top_level_field_fails_and_preserves_raw(self):
        payload = make_pa_payload()
        del payload["FormRevision"]
        raw = dump_pa_payload(payload)
        result = parse_response_json(raw)
        self.assertIsInstance(result, ParseFailure)
        self.assertEqual(result.reason, ParseFailureReason.MISSING_REQUIRED_FIELD)
        self.assertIn("FormRevision", result.detail)
        self.assertEqual(result.raw_response, raw)

    def test_unknown_top_level_field_fails(self):
        payload = make_pa_payload()
        payload["InventedField"] = {"value": "x", "confidence": 5}
        result = parse_response_json(dump_pa_payload(payload))
        self.assertEqual(result.reason, ParseFailureReason.UNKNOWN_FIELD_NAME)
        self.assertIn("InventedField", result.detail)

    def test_plain_string_field_instead_of_object_fails(self):
        payload = make_pa_payload()
        payload["SelfGivenName"] = "Mary"
        result = parse_response_json(dump_pa_payload(payload))
        self.assertEqual(result.reason, ParseFailureReason.WRONG_TYPE)
        self.assertIn("must be an object", result.detail)

    def test_missing_value_member_fails(self):
        payload = make_pa_payload()
        payload["SelfGivenName"] = {"confidence": 9}
        result = parse_response_json(dump_pa_payload(payload))
        self.assertEqual(result.reason, ParseFailureReason.MISSING_REQUIRED_FIELD)
        self.assertIn("value", result.detail)

    def test_missing_confidence_member_fails(self):
        payload = make_pa_payload()
        payload["SelfGivenName"] = {"value": "Mary"}
        result = parse_response_json(dump_pa_payload(payload))
        self.assertEqual(result.reason, ParseFailureReason.MISSING_REQUIRED_FIELD)
        self.assertIn("confidence", result.detail)

    def test_unknown_inner_member_fails(self):
        payload = make_pa_payload()
        payload["SelfGivenName"]["explanation"] = "clear"
        result = parse_response_json(dump_pa_payload(payload))
        self.assertEqual(result.reason, ParseFailureReason.UNKNOWN_FIELD_NAME)
        self.assertIn("explanation", result.detail)

    def test_non_age_value_must_be_string(self):
        payload = make_pa_payload()
        payload["SelfGivenName"]["value"] = None
        result = parse_response_json(dump_pa_payload(payload))
        self.assertEqual(result.reason, ParseFailureReason.WRONG_TYPE)
        self.assertIn("must be a string", result.detail)

    def test_confidence_zero_fails(self):
        payload = make_pa_payload()
        payload["SelfGivenName"]["confidence"] = 0
        result = parse_response_json(dump_pa_payload(payload))
        self.assertEqual(result.reason, ParseFailureReason.INVALID_CONFIDENCE)
        self.assertIn("1 through 10", result.detail)

    def test_confidence_above_ten_fails(self):
        payload = make_pa_payload()
        payload["SelfGivenName"]["confidence"] = 11
        result = parse_response_json(dump_pa_payload(payload))
        self.assertEqual(result.reason, ParseFailureReason.INVALID_CONFIDENCE)

    def test_confidence_bool_fails_even_though_bool_is_an_int_subclass(self):
        payload = make_pa_payload()
        payload["SelfGivenName"]["confidence"] = True
        result = parse_response_json(dump_pa_payload(payload))
        self.assertEqual(result.reason, ParseFailureReason.INVALID_CONFIDENCE)
        self.assertIn("bool is invalid", result.detail)

    def test_confidence_float_fails(self):
        payload = make_pa_payload()
        payload["SelfGivenName"]["confidence"] = 9.0
        result = parse_response_json(dump_pa_payload(payload))
        self.assertEqual(result.reason, ParseFailureReason.INVALID_CONFIDENCE)

    def test_confidence_string_fails(self):
        payload = make_pa_payload()
        payload["SelfGivenName"]["confidence"] = "9"
        result = parse_response_json(dump_pa_payload(payload))
        self.assertEqual(result.reason, ParseFailureReason.INVALID_CONFIDENCE)

    def test_self_death_age_string_fails(self):
        payload = make_pa_payload()
        payload["SelfDeathAge"]["value"] = "72"
        result = parse_response_json(dump_pa_payload(payload))
        self.assertEqual(result.reason, ParseFailureReason.INVALID_SELF_DEATH_AGE)

    def test_self_death_age_wrong_length_fails(self):
        payload = make_pa_payload()
        payload["SelfDeathAge"]["value"] = ["72", ""]
        result = parse_response_json(dump_pa_payload(payload))
        self.assertEqual(result.reason, ParseFailureReason.INVALID_SELF_DEATH_AGE)
        self.assertIn("exactly three", result.detail)

    def test_self_death_age_non_string_part_fails(self):
        payload = make_pa_payload()
        payload["SelfDeathAge"]["value"] = [72, "", "4"]
        result = parse_response_json(dump_pa_payload(payload))
        self.assertEqual(result.reason, ParseFailureReason.INVALID_SELF_DEATH_AGE)


class TestParserRepairsAndFailures(unittest.TestCase):
    def test_complete_think_block_is_removed(self):
        raw = "<think>private reasoning without output</think>\n" + dump_pa_payload()
        result = parse_response_json(raw)
        self.assertIsInstance(result, ParsedFields)
        self.assertEqual(
            result.repair_path,
            ("remove_complete_think_block", "direct_json"),
        )

    def test_outer_markdown_json_fence_is_removed(self):
        raw = "```json\n" + dump_pa_payload() + "\n```"
        result = parse_response_json(raw)
        self.assertIsInstance(result, ParsedFields)
        self.assertEqual(
            result.repair_path,
            ("remove_outer_markdown_json_fence", "direct_json"),
        )

    def test_think_then_fence_repairs_are_ordered_and_auditable(self):
        raw = "<think>done</think>\n```JSON\n" + dump_pa_payload() + "\n```"
        result = parse_response_json(raw)
        self.assertIsInstance(result, ParsedFields)
        self.assertEqual(
            result.repair_path,
            (
                "remove_complete_think_block",
                "remove_outer_markdown_json_fence",
                "direct_json",
            ),
        )

    def test_multiline_think_block_is_removed_completely(self):
        raw = (
            "<think>\nconsider {intermediate: braces}\nthen finish\n</think>\n"
            + dump_pa_payload()
        )
        result = parse_response_json(raw)
        self.assertIsInstance(result, ParsedFields)
        self.assertEqual(
            result.repair_path,
            ("remove_complete_think_block", "direct_json"),
        )

    def test_fenced_preamble_uses_only_the_documented_single_fallback(self):
        raw = "```json\nprovider preamble\n" + dump_pa_payload() + "\n```"
        result = parse_response_json(raw)
        self.assertIsInstance(result, ParsedFields)
        self.assertEqual(
            result.repair_path,
            (
                "remove_outer_markdown_json_fence",
                "extract_outermost_braced_object",
            ),
        )

    def test_outermost_braced_object_extraction(self):
        raw = "provider preamble\n" + dump_pa_payload() + "\nprovider suffix"
        result = parse_response_json(raw)
        self.assertIsInstance(result, ParsedFields)
        self.assertEqual(result.repair_path, ("extract_outermost_braced_object",))

    def test_empty_response(self):
        result = parse_response_json("  \n")
        self.assertEqual(result.reason, ParseFailureReason.EMPTY_RESPONSE)

    def test_none_response(self):
        result = parse_response_json(None)
        self.assertEqual(result.reason, ParseFailureReason.EMPTY_RESPONSE)
        self.assertIsNone(result.raw_response)

    def test_malformed_json_is_not_json(self):
        raw = '{"SelfNamePrefix": }'
        result = parse_response_json(raw)
        self.assertEqual(result.reason, ParseFailureReason.NOT_JSON)
        self.assertIn("direct JSON decode failed", result.detail)
        self.assertEqual(result.raw_response, raw)

    def test_outermost_fallback_is_not_repeated_after_decode_failure(self):
        raw = 'prefix {"broken": } suffix {"second": "object"}'
        result = parse_response_json(raw)
        self.assertIsInstance(result, ParseFailure)
        self.assertEqual(result.reason, ParseFailureReason.NOT_JSON)
        self.assertIn("outermost-braced-object decode failed", result.detail)
        self.assertEqual(result.raw_response, raw)

    def test_parse_failure_cannot_be_consumed_as_parsed_fields(self):
        raw = "not a response"
        result = parse_response_json(raw)
        self.assertIsInstance(result, ParseFailure)
        self.assertNotIsInstance(result, ParsedFields)
        self.assertFalse(hasattr(result, "values"))
        self.assertFalse(hasattr(result, "confidences"))
        self.assertEqual(result.raw_response, raw)

    def test_truncated_complete_contract_is_truncated(self):
        raw = dump_pa_payload()[:-1]
        result = parse_response_json(raw)
        self.assertEqual(result.reason, ParseFailureReason.TRUNCATED)
        self.assertIn("decode failed", result.detail)
        self.assertEqual(result.raw_response, raw)

    def test_json_array_is_not_top_level_object(self):
        result = parse_response_json("[1,2,3]")
        self.assertEqual(result.reason, ParseFailureReason.NOT_JSON_OBJECT)
        self.assertIn("list", result.detail)

    def test_provider_error_status_short_circuits_and_preserves_raw(self):
        raw = dump_pa_payload()
        result = parse_response_json(raw, api_status="rate_limited")
        self.assertEqual(result.reason, ParseFailureReason.PROVIDER_ERROR_STATUS)
        self.assertEqual(result.raw_response, raw)

    def test_deterministic_result_and_repair_path(self):
        raw = "prefix " + dump_pa_payload() + " suffix"
        first = parse_response_json(raw)
        for _ in range(10):
            self.assertEqual(parse_response_json(raw), first)


class TestExplicitAllowedFieldsCompatibility(unittest.TestCase):
    def test_explicit_custom_closed_schema_succeeds(self):
        raw = json.dumps({"legacy_name": {"value": "Mary", "confidence": 7}})
        result = parse_response_json(raw, allowed_fields=("legacy_name",))
        self.assertIsInstance(result, ParsedFields)
        self.assertEqual(result.values, {"legacy_name": "Mary"})
        self.assertEqual(result.confidences, {"legacy_name": 7})

    def test_custom_schema_still_requires_every_allowed_field(self):
        raw = json.dumps({"first": {"value": "Mary", "confidence": 7}})
        result = parse_response_json(raw, allowed_fields=("first", "last"))
        self.assertEqual(result.reason, ParseFailureReason.MISSING_REQUIRED_FIELD)
        self.assertIn("last", result.detail)

    def test_custom_schema_still_rejects_unknown_fields(self):
        raw = json.dumps(
            {
                "first": {"value": "Mary", "confidence": 7},
                "extra": {"value": "x", "confidence": 7},
            }
        )
        result = parse_response_json(raw, allowed_fields=("first",))
        self.assertEqual(result.reason, ParseFailureReason.UNKNOWN_FIELD_NAME)

    def test_six_field_projection_requires_explicit_opt_in(self):
        payload = {
            name: {"value": "N/A", "confidence": 10}
            for name in EVALUATED_NAME_FIELDS
        }
        strict = parse_response_json(json.dumps(payload))
        projected = parse_response_json(
            json.dumps(payload), allowed_fields=EVALUATED_NAME_FIELDS
        )
        self.assertIsInstance(strict, ParseFailure)
        self.assertIsInstance(projected, ParsedFields)

    def test_self_death_age_exception_applies_to_custom_schema(self):
        raw = json.dumps(
            {"SelfDeathAge": {"value": ["1", "2", "3"], "confidence": 5}}
        )
        result = parse_response_json(raw, allowed_fields=("SelfDeathAge",))
        self.assertIsInstance(result, ParsedFields)

    def test_invalid_allowed_fields_are_programmer_errors(self):
        with self.assertRaises(ParseError):
            parse_response_json("{}", allowed_fields="field")
        with self.assertRaises(ParseError):
            parse_response_json("{}", allowed_fields=("field", "field"))
        with self.assertRaises(ParseError):
            parse_response_json("{}", allowed_fields=("",))


if __name__ == "__main__":
    unittest.main()
