"""Lineage and manifest gate unit tests."""

import tempfile
import unittest
from pathlib import Path

from icdar_tta.lineage import (
    LineageError,
    LineageRecord,
    validate_lineage_dict,
)
from icdar_tta.manifest import (
    ManifestError,
    check_portable_manifest,
    load_manifest_text,
    run_manifest_gate,
)


class TestLineageRecord(unittest.TestCase):
    def _valid_kwargs(self, **overrides):
        defaults = dict(
            provider="google",
            model_id="gemini-3.7-flash",
            request_timestamp_utc="2026-08-29T00:00:00Z",
            prompt_hash="abc123",
            source_image_hash="def456",
            transform_id="grid_warp_v4_std15",
            parser_version="1.0.0",
            status="ok",
        )
        defaults.update(overrides)
        return defaults

    def test_valid_record_constructs(self):
        record = LineageRecord(**self._valid_kwargs())
        self.assertEqual(record.provider, "google")

    def test_missing_required_field_raises(self):
        kwargs = self._valid_kwargs()
        kwargs["prompt_hash"] = ""
        with self.assertRaises(LineageError):
            LineageRecord(**kwargs)

    def test_missing_recommended_fields_reported(self):
        record = LineageRecord(**self._valid_kwargs())
        missing = record.missing_recommended_fields()
        self.assertIn("usage", missing)
        self.assertIn("pricing_snapshot_id", missing)

    def test_has_cost_provenance_false_without_pricing(self):
        record = LineageRecord(**self._valid_kwargs())
        self.assertFalse(record.has_cost_provenance())

    def test_has_cost_provenance_true_with_usage_and_pricing(self):
        record = LineageRecord(
            **self._valid_kwargs(usage={"prompt_tokens": 10}, pricing_snapshot_id="2026-08-29-snapshot")
        )
        self.assertTrue(record.has_cost_provenance())

    def test_validate_lineage_dict_reports_exact_missing_fields(self):
        data = {"provider": "google", "model_id": "gemini-3.7-flash"}
        with self.assertRaises(LineageError) as ctx:
            validate_lineage_dict(data)
        message = str(ctx.exception)
        self.assertIn("request_timestamp_utc", message)
        self.assertIn("prompt_hash", message)

    def test_validate_lineage_dict_success(self):
        data = self._valid_kwargs()
        record = validate_lineage_dict(data)
        self.assertEqual(record.model_id, "gemini-3.7-flash")


class TestManifestParsing(unittest.TestCase):
    def test_fallback_parser_handles_nested_mapping(self):
        text = (
            "schema_version: 1\n"
            "project: icdar_tta\n"
            "sources:\n"
            "  source_images:\n"
            "    path: /ABSOLUTE/PATH\n"
            "    expected_count: 622\n"
        )
        data = load_manifest_text(text)
        self.assertEqual(data["schema_version"], 1)
        self.assertEqual(data["sources"]["source_images"]["expected_count"], 622)

    def test_fallback_parser_handles_null_value(self):
        text = "sources:\n  ground_truth:\n    path: null\n"
        data = load_manifest_text(text)
        self.assertIsNone(data["sources"]["ground_truth"]["path"])


class TestPortableManifestGate(unittest.TestCase):
    def test_flags_secret_like_key(self):
        data = {"sources": {}, "api_key": "should-not-be-here"}
        result = check_portable_manifest(data)
        self.assertFalse(result.ok)
        self.assertTrue(any("secret-like" in e for e in result.errors))

    def test_flags_auth_token_key(self):
        data = {"sources": {}, "access_token": "should-not-be-here"}
        result = check_portable_manifest(data)
        self.assertFalse(result.ok)

    def test_flags_bare_token_key(self):
        data = {"sources": {}, "token": "should-not-be-here"}
        result = check_portable_manifest(data)
        self.assertFalse(result.ok)

    def test_does_not_flag_max_output_tokens(self):
        # Regression: a legitimate generation parameter, not a credential.
        data = {"sources": {}, "generation_params": {"max_output_tokens": 2048}}
        result = check_portable_manifest(data)
        self.assertEqual(result.errors, tuple())

    def test_does_not_flag_usage_tokens_field(self):
        data = {"sources": {}, "usage_tokens_prompt": 100, "usage_tokens_completion": 50}
        result = check_portable_manifest(data)
        self.assertEqual(result.errors, tuple())

    def test_warns_on_missing_source_keys(self):
        data = {"sources": {"source_images": {"path": None}}}
        result = check_portable_manifest(data)
        self.assertTrue(any("missing documented logical source key" in w for w in result.warnings))

    def test_warns_on_absolute_path_in_portable_manifest(self):
        data = {"sources": {"source_images": {"path": "/home/user/data"}}}
        result = check_portable_manifest(data)
        self.assertTrue(any("absolute path" in w for w in result.warnings))

    def test_clean_manifest_with_all_keys_and_null_paths_passes(self):
        from icdar_tta.manifest import REQUIRED_SOURCE_KEYS

        data = {"sources": {key: {"path": None} for key in REQUIRED_SOURCE_KEYS}}
        result = check_portable_manifest(data)
        self.assertTrue(result.ok)
        self.assertEqual(result.errors, tuple())


class TestManifestGateFileHandling(unittest.TestCase):
    def test_missing_files_report_gate_not_crash(self):
        portable, local = run_manifest_gate(
            "/nonexistent/portable.yaml", "/nonexistent/local.yaml"
        )
        self.assertFalse(portable.exists)
        self.assertFalse(local.exists)
        # Missing files must not raise; ok is False only because exists is False,
        # not because of a hard error list.
        self.assertEqual(portable.errors, tuple())
        self.assertEqual(local.errors, tuple())

    def test_existing_valid_files_pass_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            portable_path = Path(tmp) / "portable.yaml"
            local_path = Path(tmp) / "local.yaml"
            portable_path.write_text(
                "sources:\n"
                + "\n".join(
                    f"  {key}:\n    path: null"
                    for key in __import__("icdar_tta.manifest", fromlist=["REQUIRED_SOURCE_KEYS"]).REQUIRED_SOURCE_KEYS
                )
                + "\n",
                encoding="utf-8",
            )
            local_path.write_text("sources:\n  source_images:\n    path: /machine/specific/path\n", encoding="utf-8")

            portable, local = run_manifest_gate(portable_path, local_path)
            self.assertTrue(portable.exists)
            self.assertTrue(portable.ok)
            self.assertTrue(local.exists)
            self.assertTrue(local.ok)


if __name__ == "__main__":
    unittest.main()
