"""Acceptance tests for the dependency-free C1-C9 chart renderer."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import struct
import tempfile
import unittest
import xml.etree.ElementTree as ET


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate_charts.py"
DERIVED = ROOT / "outputs" / "derived"
FIGURES = ROOT / "outputs" / "figures"

spec = importlib.util.spec_from_file_location("generate_charts", SCRIPT)
charts = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(charts)


class ChartGenerationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="icdar-charts-")
        base = pathlib.Path(cls.tmp.name)
        cls.first = base / "first"
        cls.second = base / "second"
        charts.generate(DERIVED, cls.first)
        charts.generate(DERIVED, cls.second)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_required_source_tables_exist(self):
        expected = {
            "strategy_summary.csv",
            "error_correlation_summary.csv",
            "precision_coverage.csv",
            "cost_by_run.csv",
            "review_frontier.csv",
            "shift_agreement.csv",
            "cross_model_operating_points.csv",
            "augmentation_contribution.csv",
            "ensemble_size.csv",
            "failure_examples.csv",
        }
        mapped = {name for group in charts.TABLE_MAP.values() for name in group}
        self.assertEqual(expected, mapped)
        for name in sorted(expected):
            path = DERIVED / name
            self.assertTrue(path.is_file(), path)
            self.assertGreater(path.stat().st_size, 0, path)

    def test_all_nine_exact_basenames_and_formats(self):
        self.assertEqual(9, len(charts.BASENAMES))
        self.assertEqual(9, len(set(charts.BASENAMES)))
        expected = {name + ext for name in charts.BASENAMES for ext in (".svg", ".png")}
        for directory in (self.first, self.second, FIGURES):
            actual = {path.name for path in directory.iterdir() if path.suffix in (".svg", ".png")}
            self.assertEqual(expected, actual)

    def test_svg_nonempty_metadata_takeaway_and_primitives(self):
        namespace = "{http://www.w3.org/2000/svg}"
        for basename in charts.BASENAMES:
            with self.subTest(chart=basename):
                path = self.first / (basename + ".svg")
                self.assertGreater(path.stat().st_size, 1000)
                root = ET.parse(path).getroot()
                self.assertEqual(namespace + "svg", root.tag)
                self.assertEqual(str(charts.WIDTH), root.attrib["width"])
                self.assertEqual(str(charts.HEIGHT), root.attrib["height"])
                metadata_node = root.find(namespace + "metadata")
                self.assertIsNotNone(metadata_node)
                metadata = json.loads(metadata_node.text)
                self.assertEqual(basename, metadata["chart_id"])
                self.assertEqual(charts.TAKEAWAYS[basename], metadata["takeaway"])
                self.assertTrue(metadata["takeaway"].endswith("."))
                self.assertEqual(list(charts.TABLE_MAP[basename]), metadata["numeric_inputs"])
                self.assertGreater(len(root.findall(".//" + namespace + "text")), 5)
                marks = sum(len(root.findall(".//" + namespace + tag)) for tag in ("line", "rect", "circle", "polyline", "polygon"))
                self.assertGreater(marks, 3)

    def test_png_signature_dimensions_and_nontrivial_content(self):
        signature = b"\x89PNG\r\n\x1a\n"
        for basename in charts.BASENAMES:
            with self.subTest(chart=basename):
                payload = (self.first / (basename + ".png")).read_bytes()
                self.assertTrue(payload.startswith(signature))
                self.assertGreater(len(payload), 5000)
                self.assertEqual(b"IHDR", payload[12:16])
                width, height = struct.unpack(">II", payload[16:24])
                self.assertEqual((charts.WIDTH, charts.HEIGHT), (width, height))
                self.assertIn(b"IDAT", payload)
                self.assertTrue(payload.endswith(b"IEND\xaeB`\x82"))

    def test_deterministic_rerun_and_committed_outputs(self):
        for basename in charts.BASENAMES:
            for suffix in (".svg", ".png"):
                with self.subTest(chart=basename, suffix=suffix):
                    first = (self.first / (basename + suffix)).read_bytes()
                    second = (self.second / (basename + suffix)).read_bytes()
                    committed = (FIGURES / (basename + suffix)).read_bytes()
                    self.assertEqual(hashlib.sha256(first).digest(), hashlib.sha256(second).digest())
                    self.assertEqual(first, second)
                    self.assertEqual(first, committed)

    def test_metadata_has_no_external_paths_urls_or_credentials(self):
        forbidden = ("c:\\", "/mnt/", "/home/", "file://", "http://", "https://", "api_key", "credential", "signed_url")
        namespace = "{http://www.w3.org/2000/svg}"
        for basename in charts.BASENAMES:
            metadata = ET.parse(self.first / (basename + ".svg")).getroot().find(namespace + "metadata").text.lower()
            for token in forbidden:
                with self.subTest(chart=basename, token=token):
                    self.assertNotIn(token, metadata)


if __name__ == "__main__":
    unittest.main()
