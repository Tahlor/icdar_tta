"""Offline validation CLI: ``python3 -m icdar_tta.validate``.

Per ``docs/VALIDATION_TESTS.md``: "one end-to-end validation command
such as ``python -m icdar_tta.validate --manifest
config/data_manifest.local.yaml``." This module implements that entry
point.

This CLI performs **no network I/O and no provider calls**. It checks:

1. that the two manifest files described in ``docs/DATA_CONTRACT.md``
   exist and pass their shape/secret/absolute-path gate checks;
2. that the core offline modules (normalize/parser/alignment/consensus/
   metrics/lineage) import and pass an internal self-check;
3. if a field-level table path is supplied and exists, that it passes
   :func:`icdar_tta.schema.validate_table_schema`.

Any missing data source, missing manifest, or unmet data-gate condition
is reported as a structured, documented result -- never an unhandled
exception -- per the "make it report documented data-gate errors rather
than crash" requirement. The process exit code is 0 only if there are
zero hard errors; missing-but-expected local data is a reported gate
condition (exit code 2), and unexpected internal errors are exit code 1.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

from icdar_tta import manifest as manifest_mod
from icdar_tta import normalize
from icdar_tta.consensus import progressive_consensus
from icdar_tta.parser import ParsedFields, parse_response_json


@dataclass
class GateReport:
    name: str
    passed: bool
    detail: str


@dataclass
class ValidationReport:
    gates: list = field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        return all(g.passed for g in self.gates)

    @property
    def hard_failures(self) -> list:
        return [g for g in self.gates if not g.passed]

    def add(self, name: str, passed: bool, detail: str) -> None:
        self.gates.append(GateReport(name=name, passed=passed, detail=detail))

    def to_dict(self) -> dict:
        return {
            "all_passed": self.all_passed,
            "gates": [asdict(g) for g in self.gates],
        }


def _self_check_normalize(report: ValidationReport) -> None:
    try:
        assert normalize.normalize_field("  O'Brien. ") == "o'brien"
        assert normalize.is_exact_match("Mary", "mary") is True
        assert normalize.is_exact_match("Mary", None) is None
        assert normalize.character_error_rate("Mary", "Mary") == 0.0
        report.add("self_check.normalize", True, "normalize_field/is_exact_match/character_error_rate OK")
    except Exception as exc:  # noqa: BLE001 - deliberately broad: this is a health check, not app logic
        report.add("self_check.normalize", False, f"unexpected exception: {exc!r}")


def _self_check_parser(report: ValidationReport) -> None:
    try:
        from icdar_tta.parser import PA_V149_REQUIRED_FIELDS

        payload = {
            name: {"value": "N/A", "confidence": 10}
            for name in PA_V149_REQUIRED_FIELDS
        }
        payload["SelfGivenName"] = {"value": "Mary", "confidence": 9}
        payload["SelfDeathAge"] = {"value": ["72", "", "4"], "confidence": 8}
        ok = parse_response_json(json.dumps(payload))
        assert isinstance(ok, ParsedFields)
        assert len(ok.values) == 44
        assert ok.values["SelfGivenName"] == "Mary"
        assert ok.values["SelfDeathAge"] == ["72", "", "4"]
        assert ok.repair_path == ("direct_json",)

        bad = parse_response_json("not json at all")
        assert bad.reason.value == "not_json"
        report.add(
            "self_check.parser",
            True,
            "strict PA v1.49 44-field success, age exception, repair audit, and failure paths OK",
        )
    except Exception as exc:  # noqa: BLE001
        report.add("self_check.parser", False, f"unexpected exception: {exc!r}")


def _self_check_consensus(report: ValidationReport) -> None:
    try:
        result = progressive_consensus(["Mary", "Mary", "Mray"])
        assert result.n_valid_samples == 3
        assert result.n_missing_samples == 0
        assert 0.0 <= result.field_confidence <= 1.0
        report.add("self_check.consensus", True, f"progressive_consensus deterministic OK ({result.consensus_text!r})")
    except Exception as exc:  # noqa: BLE001
        report.add("self_check.consensus", False, f"unexpected exception: {exc!r}")


def _check_manifests(report: ValidationReport, portable_path: Path, local_path: Path) -> None:
    portable_result, local_result = manifest_mod.run_manifest_gate(portable_path, local_path)

    if portable_result.exists:
        report.add(
            "manifest.portable.secrets_and_shape",
            portable_result.ok,
            f"path={portable_result.path} errors={list(portable_result.errors)} "
            f"warnings={list(portable_result.warnings)}",
        )
    else:
        # A missing portable manifest is a documented data gate, not a
        # crash: report it as an informational (non-fatal) gate.
        report.add(
            "manifest.portable.exists",
            True,
            f"portable manifest not found at {portable_result.path} (informational; "
            f"see docs/DATA_CONTRACT.md); not treated as a hard failure in this offline check",
        )

    if local_path is not None:
        if local_result.exists:
            report.add(
                "manifest.local.shape",
                local_result.ok,
                f"path={local_result.path} errors={list(local_result.errors)}",
            )
        else:
            report.add(
                "manifest.local.exists",
                True,
                f"local manifest not found at {local_result.path} (expected in an offline "
                f"environment without machine-specific data mounted; documented data gate, "
                f"not a failure)",
            )


def _check_field_table(report: ValidationReport, table_path: Optional[Path]) -> None:
    if table_path is None:
        report.add(
            "field_table.provided",
            True,
            "no --field-table path given; skipping schema validation (documented data gate)",
        )
        return
    if not table_path.exists():
        report.add(
            "field_table.exists",
            True,
            f"field table not found at {table_path}; documented data gate, not a failure "
            f"in this offline environment",
        )
        return
    try:
        from icdar_tta.schema import validate_table_schema

        rows = json.loads(table_path.read_text(encoding="utf-8"))
        if not isinstance(rows, list):
            report.add("field_table.shape", False, "field table JSON must be a top-level list of row objects")
            return
        validate_table_schema(rows)
        report.add("field_table.schema", True, f"{len(rows)} row(s) validated against required schema columns")
    except Exception as exc:  # noqa: BLE001 - report, do not crash the CLI
        report.add("field_table.schema", False, f"schema validation failed: {exc!r}")


def run_validation(
    *,
    portable_manifest: Path,
    local_manifest: Path,
    field_table: Optional[Path],
) -> ValidationReport:
    report = ValidationReport()
    _self_check_normalize(report)
    _self_check_parser(report)
    _self_check_consensus(report)
    _check_manifests(report, portable_manifest, local_manifest)
    _check_field_table(report, field_table)
    return report


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="icdar_tta.validate",
        description=(
            "Offline data-gate and self-check validation for the icdar_tta analysis core. "
            "Performs no network I/O and no provider calls."
        ),
    )
    parser.add_argument(
        "--manifest",
        dest="local_manifest",
        default="config/data_manifest.local.yaml",
        help="Path to the machine-specific local manifest (default: config/data_manifest.local.yaml)",
    )
    parser.add_argument(
        "--portable-manifest",
        dest="portable_manifest",
        default="config/data_manifest.yaml",
        help="Path to the portable/committed manifest (default: config/data_manifest.yaml)",
    )
    parser.add_argument(
        "--field-table",
        dest="field_table",
        default=None,
        help="Optional path to a JSON field-level table to validate against the schema.",
    )
    parser.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Print the full report as JSON instead of a human-readable summary.",
    )
    return parser


def main(argv: Optional[list] = None) -> int:
    args = build_arg_parser().parse_args(argv)

    try:
        report = run_validation(
            portable_manifest=Path(args.portable_manifest),
            local_manifest=Path(args.local_manifest),
            field_table=Path(args.field_table) if args.field_table else None,
        )
    except Exception as exc:  # noqa: BLE001 - last-resort guard; must report, not crash
        print(f"INTERNAL ERROR (unexpected, please report): {exc!r}", file=sys.stderr)
        return 1

    if args.as_json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        for gate in report.gates:
            status = "PASS" if gate.passed else "FAIL"
            print(f"[{status}] {gate.name}: {gate.detail}")
        print()
        print(f"Overall: {'PASS' if report.all_passed else 'FAIL'} ({len(report.hard_failures)} hard failure(s))")

    if report.hard_failures:
        return 1
    if not Path(args.local_manifest).exists() or not Path(args.portable_manifest).exists():
        # Distinguish "everything checkable passed, but real data isn't
        # mounted here" from full success, without treating it as an error.
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
