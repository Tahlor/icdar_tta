"""Validation CLI tests: must report data-gate conditions, never crash."""

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from icdar_tta.validate import main, run_validation


class TestRunValidation(unittest.TestCase):
    def test_self_checks_pass_with_missing_manifests(self):
        report = run_validation(
            portable_manifest=Path("/nonexistent/portable.yaml"),
            local_manifest=Path("/nonexistent/local.yaml"),
            field_table=None,
        )
        self_check_gates = [g for g in report.gates if g.name.startswith("self_check.")]
        self.assertTrue(all(g.passed for g in self_check_gates))
        self.assertTrue(len(self_check_gates) >= 3)

    def test_missing_manifest_is_not_a_hard_failure(self):
        report = run_validation(
            portable_manifest=Path("/nonexistent/portable.yaml"),
            local_manifest=Path("/nonexistent/local.yaml"),
            field_table=None,
        )
        # No manifest present in this offline environment: report must
        # still be constructible and must not raise.
        manifest_gates = [g for g in report.gates if g.name.startswith("manifest.")]
        self.assertTrue(len(manifest_gates) >= 2)

    def test_field_table_missing_reports_gate_not_error(self):
        report = run_validation(
            portable_manifest=Path("/nonexistent/portable.yaml"),
            local_manifest=Path("/nonexistent/local.yaml"),
            field_table=Path("/nonexistent/table.json"),
        )
        table_gate = next(g for g in report.gates if g.name == "field_table.exists")
        self.assertTrue(table_gate.passed)

    def test_field_table_bad_schema_reports_failure_not_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            table_path = Path(tmp) / "table.json"
            table_path.write_text(json.dumps([{"doc_id": "x"}]), encoding="utf-8")
            report = run_validation(
                portable_manifest=Path("/nonexistent/portable.yaml"),
                local_manifest=Path("/nonexistent/local.yaml"),
                field_table=table_path,
            )
            table_gate = next(g for g in report.gates if g.name == "field_table.schema")
            self.assertFalse(table_gate.passed)
            self.assertFalse(report.all_passed)

    def test_field_table_valid_schema_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            table_path = Path(tmp) / "table.json"
            row = {
                "doc_id": "doc-1",
                "field_name": "decedent_given_name",
                "ground_truth": "Mary",
                "model_id": "gemini-2.0-flash",
                "run_id": "run-1",
                "strategy": "baseline",
                "transform_id": "none",
                "sample_index": 0,
                "prediction": "Mary",
                "normalized_prediction": "mary",
                "is_exact_correct": True,
                "cer": 0.0,
                "response_path_or_id": "resp-1.json",
                "fold": "0",
            }
            table_path.write_text(json.dumps([row]), encoding="utf-8")
            report = run_validation(
                portable_manifest=Path("/nonexistent/portable.yaml"),
                local_manifest=Path("/nonexistent/local.yaml"),
                field_table=table_path,
            )
            table_gate = next(g for g in report.gates if g.name == "field_table.schema")
            self.assertTrue(table_gate.passed)


class TestMainCliDoesNotCrash(unittest.TestCase):
    def test_main_returns_gate_exit_code_when_no_manifests(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            exit_code = main(
                [
                    "--portable-manifest",
                    "/nonexistent/portable.yaml",
                    "--manifest",
                    "/nonexistent/local.yaml",
                ]
            )
        # 2 == "checkable things passed, but real data is not mounted"
        self.assertEqual(exit_code, 2)
        output = buf.getvalue()
        self.assertIn("PASS", output)
        self.assertNotIn("Traceback", output)

    def test_main_json_output_is_valid_json(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            main(
                [
                    "--portable-manifest",
                    "/nonexistent/portable.yaml",
                    "--manifest",
                    "/nonexistent/local.yaml",
                    "--json",
                ]
            )
        payload = json.loads(buf.getvalue())
        self.assertIn("gates", payload)
        self.assertIn("all_passed", payload)

    def test_main_with_malformed_field_table_reports_failure_exit_code_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            table_path = Path(tmp) / "table.json"
            table_path.write_text("not valid json", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                exit_code = main(
                    [
                        "--portable-manifest",
                        "/nonexistent/portable.yaml",
                        "--manifest",
                        "/nonexistent/local.yaml",
                        "--field-table",
                        str(table_path),
                    ]
                )
            self.assertEqual(exit_code, 1)
            self.assertNotIn("Traceback", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
