"""Focused tests for the standard-library historical derivation CLI."""

from __future__ import annotations

import csv
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from scripts import recompute_historical as historical


class HistoricalFixture:
    def __init__(self, root: Path):
        self.pa = root / "PA_DEATH"
        self.analysis = root / "analysis_root"
        self._create()

    @staticmethod
    def _write(path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def _create(self) -> None:
        self._write(
            self.pa / "WARP/PA_DEATH_WARP.yaml",
            "experiments:\n  - experiment_name: shift_only\n    mask_root: /private/masks\n",
        )
        self._write(
            self.pa / "WARP/metrics_no_punc/ensemble_selection_analysis.tsv",
            "experiment_name\tavg_cer\tbaseline_cer\tcer_improvement_over_baseline\tchar_error_correlation\tfield_error_correlation\tensemble_score_v1\tensemble_score_v2\tensemble_score_v3\tensemble_score_v4\texpected_ensemble_improvement\tbaseline_error_coverage\tbaseline_error_count\tsample_count\n"
            "shift_only\t0.1\t0.11\t0.01\t0.8\t0.75\t0\t0\t0\t0.2\t0\t0.1\t1\t3\n",
        )
        self._write(
            self.pa / "WARP/metrics_no_punc/experiment_level_consensus_summary_by_k.tsv",
            "k_samples_used\texperiment_name\texp_category\ttotal_edit_distance\ttotal_gt_chars\tunweighted_CER\tconsensus_missing\tconsensus_worse_than_median_count\ttotal_consensus_records\tTP\tFP\tFN\tTN\ttotal_samples\tavg_confidence\tweighted_CER\tconsensus_worse_than_median_pct\tfield_accuracy\tf1_score\n"
            "1\tshift_only\tshift\t1\t10\t0.1\t0\t0\t3\t0\t0\t1\t2\t3\t1\t0.1\t0\t0.6666666666666666\t0\n"
            "2\tshift_only\tshift\t0\t10\t0\t0\t0\t3\t1\t0\t0\t2\t6\t0.9\t0\t0\t1\t1\n",
        )
        self._write(
            self.pa / "WARP/metrics_no_punc/weighted_cer_by_experiment.tsv",
            "experiment_name\texp_category\tedit_distance\tgt_length\tweighted_cer\tsample_count\nshift_only\tshift\t1\t10\t0.1\t3\n",
        )
        gt_header = ["ImageFileName"] + list(historical.RAW_NAME_FIELDS)
        gt_row = ["doc-1.jpg", "a", "b", "c", "d", "e", "f"]
        for family in ("WARP", "SHIFT"):
            self._write(
                self.pa / f"{family}/5164_gts.csv",
                ",".join(gt_header) + "\n" + ",".join(gt_row) + "\n",
            )
        config = {
            "transformations": [
                {"type": "resize", "params": {"max_dimension": 2240}},
                {"type": "granular_shift", "params": {"variants": [{"pad_left": 1, "pad_right": 1, "pad_top": 1, "pad_bottom": 1}]}},
            ]
        }
        self._write(
            self.pa / "SHIFT/metrics_no_punc/run_settings.csv",
            "experiment_name,num_samples,transformation_config\n"
            f"SHIFT_TEST,1,\"{str(config).replace(chr(34), chr(34) * 2)}\"\n",
        )
        self._write(
            self.pa / "SHIFT/metrics_no_punc/weighted_cer_by_experiment.tsv",
            "experiment_name\texp_category\tedit_distance\tgt_length\tweighted_cer\tsample_count\nSHIFT_TEST\tshift\t1\t10\t0.1\t3\n",
        )
        for direction in ("horizontal", "vertical"):
            self._write(
                self.pa / f"CVPR_ANALYSIS/small_shift_{direction}_signal_data.csv",
                "relative_shift,agreement\n-16,0.8\n0,1.0\n16,0.8\n",
            )
            self._write(
                self.pa / f"CVPR_ANALYSIS/small_shift_{direction}_fft_peaks.csv",
                "Frequency,Period (px),Amplitude\n0.0625,16,0.01\n",
            )
        paper = self.analysis / "analysis - v7/paper"
        self._write(
            paper / "transform_metrics_table.csv",
            "Transform,CER_5_Samples,CER_10_Samples,Field_Accuracy_5_Samples,Field_Accuracy_10_Samples\n"
            "Baseline*,0.1 (1-sample),0.1 (1-sample),0.7 (1-sample),0.7 (1-sample)\n"
            "Grid Warp,0.09,0.08,0.72,0.74\n",
        )
        self._write(
            paper / "ensemble_methods_table.csv",
            "Method,CER_5_Samples,CER_10_Samples,Field_Accuracy_5_Samples,Field_Accuracy_10_Samples\nBaseline,0.1,0.1,0.7,0.7\n",
        )
        self._write(
            self.analysis / "analysis - v7/best_consensus_CER/cv_rank_metrics_summary.tsv",
            "last_added_experiment\tfrequency\tMRR\ttotal_folds\n"
            "gemini-20-flash_ns20_gw_sweep_1\t2\t0.5\t2\n",
        )
        consensus_header = "consensus_confidence,cer,sample_count\n"
        consensus_body = "0.5,1.0,2\n0.8,0.0,2\n1.0,0.0,2\n"
        reliability = self.analysis / "analysis - v7/outputs/consensus_reliability_analysis"
        for name in ("consensus_gw_data.csv", "consensus_shift_data.csv", "consensus_resize_data.csv"):
            self._write(reliability / name, consensus_header + consensus_body)


class TestHistoricalDerivation(unittest.TestCase):
    def _run(self, fixture: HistoricalFixture, output: Path, manifest: Path | None = None) -> None:
        args = [
            "--pa-root", str(fixture.pa),
            "--analysis-root", str(fixture.analysis),
            "--output-dir", str(output),
        ]
        if manifest is not None:
            args += ["--local-manifest", str(manifest)]
        with redirect_stdout(io.StringIO()):
            self.assertEqual(historical.main(args), 0)

    def test_deterministic_rerun_and_required_headers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = HistoricalFixture(root)
            first, second = root / "out-a", root / "out-b"
            self._run(fixture, first)
            self._run(fixture, second)
            self.assertEqual(set(historical.REQUIRED_OUTPUTS), {path.name for path in first.glob("*.csv")})
            for filename in historical.REQUIRED_OUTPUTS:
                self.assertEqual((first / filename).read_bytes(), (second / filename).read_bytes())
                with (first / filename).open(newline="", encoding="utf-8") as stream:
                    reader = csv.reader(stream)
                    self.assertEqual(tuple(next(reader)), historical.TABLE_HEADERS[filename])
                    self.assertGreaterEqual(sum(1 for _ in reader), 1)

    def test_tracked_outputs_have_no_absolute_paths_or_secret_like_strings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = HistoricalFixture(root)
            output = root / "derived"
            self._run(fixture, output)
            combined = "\n".join(path.read_text(encoding="utf-8") for path in output.glob("*.csv"))
            report = Path("local_agent/HISTORICAL_REANALYSIS.md")
            if report.exists():
                combined += "\n" + report.read_text(encoding="utf-8")
            self.assertNotIn(str(root), combined)
            self.assertNotRegex(combined, r"(?:/mnt/|[A-Za-z]:[\\/])")
            self.assertNotRegex(combined.lower(), r"api[_-]?key|access[_-]?token|password|credential")

    def test_blocked_rows_are_truthful_and_manifest_is_explicit_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = HistoricalFixture(root)
            output = root / "derived"
            manifest = root / "data_manifest.local.yaml"
            self._run(fixture, output, manifest)
            with (output / "cross_model_operating_points.csv").open(newline="", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
            modern = [row for row in rows if row["model_id"] in historical.MODERN_MODEL_IDS]
            self.assertEqual(len(modern), 12)
            self.assertTrue(all(row["evidence_status"] == "blocked_unavailable" for row in modern))
            self.assertTrue(all(row["accepted_fields"] == "" for row in modern))
            with (output / "failure_examples.csv").open(newline="", encoding="utf-8") as stream:
                failure = next(csv.DictReader(stream))
            self.assertEqual(failure["evidence_status"], "blocked_unavailable")
            self.assertEqual(failure["prediction"], "")
            self.assertEqual(failure["ground_truth"], "")
            self.assertIn(str(fixture.pa), manifest.read_text(encoding="utf-8"))

    def test_cli_paths_have_no_workstation_defaults(self):
        parser = historical.build_parser()
        for action in parser._actions:
            if action.dest in {"pa_root", "analysis_root", "output_dir"}:
                self.assertTrue(action.required)
                self.assertIsNone(action.default)


if __name__ == "__main__":
    unittest.main()
