#!/usr/bin/env python3
"""Derive privacy-safe aggregate tables from the modern PA screen.

The provider runner preserves raw responses and parsed values outside Git.
This script joins those results to the private WARP ground-truth CSV, computes
field-level consensus in the frozen view order, and writes only aggregate
tables to ``outputs/derived``. The raw six-name nonblank population is used by
this implementation because it has not yet applied the recovered historical
record-level exclusion rule. Every modern table labels that denominator as
non-paper-lineage; see ``docs/GT_LINEAGE.md`` for the six-field contract, the
24-record exclusion rule, and the v9/v10 one-blank-row caveat.

No model, transform, threshold, or ensemble is selected from modern labels by
this script.  The 95% precision row is a descriptive operating point on the
predeclared raw-agreement curve, while the complete curve remains available.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

from icdar_tta.agreement import pairwise_error_correlation_summary
from icdar_tta.consensus import progressive_consensus
from icdar_tta.metrics import precision_coverage_curve
from icdar_tta.normalize import character_error_rate, is_exact_match, levenshtein_distance, normalize_field
from icdar_tta.parser import EVALUATED_NAME_FIELDS, parse_response_json
from icdar_tta.request_ledger import read_ledger, request_fingerprint


MODEL_ORDER = (
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
)
VIEW_ORDER = ("U0", "U1", "U2", "P0", "P1", "P2", "G0", "G1", "G2")
STRATEGIES = {
    "single": ("U0",),
    "unchanged_3": ("U0", "U1", "U2"),
    "Pad": ("P0", "P1", "P2"),
    "Grid Warp": ("G0", "G1", "G2"),
    "visual_mixed_6": ("P0", "P1", "P2", "G0", "G1", "G2"),
    "all_views_9": VIEW_ORDER,
}
STRATEGY_FAMILY = {
    "single": "unchanged",
    "unchanged_3": "unchanged",
    "Pad": "pad",
    "Grid Warp": "grid_warp",
    "visual_mixed_6": "mixed_visual",
    "all_views_9": "mixed_visual",
}
GT_FIELDS = {field_name: f"{field_name}_edt" for field_name in EVALUATED_NAME_FIELDS}
TARGET_PRECISION = 0.95
EVIDENCE_STATUS = "measured_modern_raw_noncanonical_denominator"
RUN_ID = "modern_screen_v1"
PARSER_VERSION = "pa_v149_json_repair_v0"
TERMINAL_RESULT_STATUSES = {"ok", "ok_projected", "parse_fail_kept"}
FIELD_BEARING_RESULT_STATUSES = {"ok", "ok_projected"}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fmt(value: float | None) -> str:
    return "" if value is None or not math.isfinite(value) else repr(float(value))


def safe_prediction(value: Any) -> str | None:
    """Map provider missing sentinels to explicit missing values."""
    if value is None or isinstance(value, (list, dict)):
        return None
    text = str(value).strip()
    if not text or text == "N/A":
        return None
    return text


def safe_ground_truth(value: Any) -> str | None:
    """Return a ground-truth value without applying provider sentinels.

    A label literally equal to ``NA`` is data, not a provider missing-value
    marker. Ground-truth scope is determined only by blankness.
    """
    if value is None or isinstance(value, (list, dict)):
        return None
    text = str(value).strip()
    return text or None


def load_ground_truth(path: Path) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 622:
        raise ValueError(f"expected 622 ground-truth rows, found {len(rows)}")
    required = {"ImageFileName", *GT_FIELDS.values()}
    if not required.issubset(rows[0]):
        raise ValueError(f"ground truth is missing columns: {sorted(required - set(rows[0]))}")
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        key = row["ImageFileName"]
        if not key or key in result:
            raise ValueError("ground truth has a blank or duplicate ImageFileName")
        result[key] = row
    return result


def load_results(results_root: Path) -> tuple[dict[str, dict[str, dict[str, dict[str, Any]]]], list[Path]]:
    """Load the latest normalized response row by model/document/view."""
    paths = sorted((results_root / "normalized").glob("*/results.jsonl"))
    if not paths:
        raise FileNotFoundError(f"no normalized result files under {results_root / 'normalized'}")
    latest: dict[tuple[str, str, str], dict[str, Any]] = {}
    seen_paths: dict[tuple[str, str, str], Path] = {}
    for path in paths:
        expected_model_id = path.parent.name
        seen_in_file: set[tuple[str, str, str]] = set()
        with path.open("r", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, start=1):
                if not line.strip():
                    continue
                row = json.loads(line)
                for key in ("doc_id", "model_id", "view_id", "status"):
                    if key not in row:
                        raise ValueError(f"{path}:{line_number} missing {key}")
                if str(row["model_id"]) != expected_model_id:
                    raise ValueError(
                        f"{path}:{line_number} model_id {row['model_id']!r} does not match parent directory {expected_model_id!r}"
                    )
                key = (str(row["model_id"]), str(row["doc_id"]), str(row["view_id"]))
                if key in seen_in_file:
                    raise ValueError(f"{path}:{line_number} contains a duplicate normalized result key: {key}")
                if key in seen_paths:
                    raise ValueError(
                        f"{path}:{line_number} duplicates normalized result key {key}; first seen in {seen_paths[key]}"
                    )
                seen_in_file.add(key)
                seen_paths[key] = path
                latest[key] = row
    nested: dict[str, dict[str, dict[str, dict[str, Any]]]] = defaultdict(lambda: defaultdict(dict))
    for (model_id, doc_id, view_id), row in latest.items():
        nested[model_id][doc_id][view_id] = row
    return nested, paths


RESULT_LINEAGE_FIELDS = (
    "transform_id",
    "sample_index",
    "source_relative_filename",
    "source_image_sha256",
    "mask_relative_filename",
    "mask_sha256",
    "transform_spec_json",
    "transform_spec_sha256",
    "seed",
    "rendered_relative_filename",
    "rendered_image_sha256",
    "width",
    "height",
    "channels",
    "codec",
    "codec_options",
    "renderer_sha256",
    "external_grid_renderer_sha256",
    "external_pad_renderer_sha256",
)


def validate_result_lineage(
    responses: dict[str, dict[str, dict[str, dict[str, Any]]]],
    model_ids: tuple[str, ...],
    results_root: Path,
    render_manifest: Path | None,
    *,
    expected_prompt_hash: str | None,
    expected_schema_hash: str | None,
    expected_run_id: str,
    expected_route_version: str | None,
) -> list[Path]:
    """Fail closed when normalized rows do not match the frozen render/run."""
    if render_manifest is None:
        return []
    with render_manifest.open("r", encoding="utf-8", newline="") as stream:
        render_rows = list(csv.DictReader(stream))
    required = {"doc_id", "view_id", *RESULT_LINEAGE_FIELDS}
    if not render_rows or not required.issubset(render_rows[0]):
        raise ValueError(f"render manifest missing lineage columns: {sorted(required - set(render_rows[0] if render_rows else {}))}")
    render_by_key: dict[tuple[str, str], dict[str, str]] = {}
    for row in render_rows:
        key = (row["doc_id"], row["view_id"])
        if key in render_by_key:
            raise ValueError(f"render manifest contains duplicate document-view key: {key}")
        render_by_key[key] = row

    raw_paths: list[Path] = []
    root = results_root.resolve()
    errors: list[str] = []
    for model_id in model_ids:
        for doc_id, views in responses[model_id].items():
            for view_id, row in views.items():
                key = (doc_id, view_id)
                expected = render_by_key.get(key)
                if expected is None:
                    errors.append(f"{model_id}/{doc_id}/{view_id}: missing render-manifest row")
                    continue
                for field_name in RESULT_LINEAGE_FIELDS:
                    if str(row.get(field_name, "")) != str(expected.get(field_name, "")):
                        errors.append(
                            f"{model_id}/{doc_id}/{view_id}: {field_name} mismatch "
                            f"{row.get(field_name)!r} != {expected.get(field_name)!r}"
                        )
                        break
                if row.get("screen_run_id") != expected_run_id:
                    errors.append(f"{model_id}/{doc_id}/{view_id}: screen_run_id mismatch")
                for name, expected_value in (
                    ("prompt_hash", expected_prompt_hash),
                    ("schema_hash", expected_schema_hash),
                    ("route_transport_version", expected_route_version),
                ):
                    if expected_value is not None and row.get(name) != expected_value:
                        errors.append(f"{model_id}/{doc_id}/{view_id}: {name} mismatch")
                returned_model = str(row.get("returned_model_id") or "")
                for prefix in ("models/", "publishers/google/models/"):
                    if returned_model.startswith(prefix):
                        returned_model = returned_model[len(prefix):]
                if returned_model and returned_model != model_id:
                    errors.append(f"{model_id}/{doc_id}/{view_id}: returned_model_id mismatch")
                try:
                    descriptor = {
                        "model_id": row["model_id"],
                        "prompt_hash": row["prompt_hash"],
                        "schema_hash": row["schema_hash"],
                        "source_image_hash": row["source_image_hash"],
                        "rendered_image_hash": row["rendered_image_hash"],
                        "payload_hash": row["payload_hash"],
                        "transform_id": row["transform_id"],
                        "sample_index": int(row["sample_index"]),
                        "generation_params": row["generation_params"],
                        "route_transport_version": row["route_transport_version"],
                        "gemini_key_env": row.get("gemini_key_env"),
                    }
                    if request_fingerprint(descriptor) != row.get("request_fingerprint"):
                        errors.append(f"{model_id}/{doc_id}/{view_id}: request_fingerprint mismatch")
                except (KeyError, TypeError, ValueError):
                    errors.append(f"{model_id}/{doc_id}/{view_id}: incomplete request fingerprint fields")
                raw_ref = row.get("raw_response_ref")
                raw_path = (results_root / str(raw_ref)).resolve() if raw_ref else None
                if raw_path is None or root not in raw_path.parents or not raw_path.is_file():
                    errors.append(f"{model_id}/{doc_id}/{view_id}: missing or escaping raw response")
                else:
                    raw_paths.append(raw_path)
                if not row.get("payload_hash"):
                    errors.append(f"{model_id}/{doc_id}/{view_id}: missing payload_hash")
    expected_keys = {(str(row["doc_id"]), str(row["view_id"])) for row in render_rows}
    actual_keys = {
        (doc_id, view_id)
        for model_id in model_ids
        for doc_id, views in responses[model_id].items()
        for view_id in views
    }
    if len(render_rows) != len(expected_keys) or expected_keys != actual_keys:
        errors.append(
            f"render/result key-set mismatch: render_rows={len(render_rows)} unique_render={len(expected_keys)} "
            f"actual_per_model={len(actual_keys)}"
        )
    if errors:
        preview = "; ".join(errors[:8])
        suffix = f" (+{len(errors) - 8} more)" if len(errors) > 8 else ""
        raise ValueError(f"modern result lineage validation failed: {preview}{suffix}")
    return sorted(set(raw_paths))


def validate_ledger_evidence(
    responses: dict[str, dict[str, dict[str, dict[str, Any]]]],
    model_ids: tuple[str, ...],
    ledger_paths: list[Path],
) -> dict[str, int]:
    """Reconcile every normalized row to a terminal ledger event when given."""
    if not ledger_paths:
        return {}
    terminal: set[tuple[str, str, str, int, str, str, str]] = set()
    submitted_by_model: dict[str, int] = defaultdict(int)
    for ledger_path in ledger_paths:
        for record in read_ledger(ledger_path):
            model_id = str(record["model_id"])
            if model_id not in model_ids:
                continue
            if record["status"] == "submitted":
                submitted_by_model[model_id] += 1
            if record["status"] in {"ok", "parse_fail_kept"}:
                terminal.add(
                    (
                        str(record["doc_id"]),
                        model_id,
                        str(record["transform_id"]),
                        int(record["sample_index"]),
                        str(record["request_fingerprint"]),
                        str(record.get("raw_response_ref") or ""),
                        str(record["status"]),
                    )
                )
    missing: list[str] = []
    for model_id in model_ids:
        for doc_id, views in responses[model_id].items():
            for view_id, row in views.items():
                strict_status = str(row.get("strict_status") or row.get("status"))
                if strict_status == "ok_projected":
                    strict_status = "parse_fail_kept"
                key = (
                    doc_id,
                    model_id,
                    str(row.get("transform_id")),
                    int(row.get("sample_index")),
                    str(row.get("request_fingerprint")),
                    str(row.get("raw_response_ref") or ""),
                    strict_status,
                )
                if key not in terminal:
                    missing.append(f"{model_id}/{doc_id}/{view_id}")
    if missing:
        preview = ", ".join(missing[:8])
        suffix = f" (+{len(missing) - 8} more)" if len(missing) > 8 else ""
        raise ValueError(f"normalized rows missing matching terminal ledger events: {preview}{suffix}")
    return dict(submitted_by_model)


def _model_text_from_raw_body(body: dict[str, Any], model_id: str) -> str:
    """Extract model text from a preserved Gemini/Qwen provider body."""
    if model_id.startswith("gemini-"):
        candidates = body.get("candidates") or []
        parts = ((candidates[0] if candidates else {}).get("content") or {}).get("parts") or []
        return "".join(part.get("text", "") for part in parts if isinstance(part, dict))
    choices = body.get("choices") or []
    message = (choices[0] if choices else {}).get("message") or {}
    content = message.get("content", "")
    if isinstance(content, list):
        return "".join(item.get("text", "") for item in content if isinstance(item, dict))
    return str(content)


def _project_model_text(text: str) -> Any:
    """Validate only the six evaluated fields after a strict-schema failure.

    The provider response remains a strict-parser failure for the full 44
    fields. This explicit, auditable projection recovers name fields when an
    unrelated field (for example, the age array) is malformed, without
    changing the raw response or silently treating the original parse as a
    full-schema success.
    """
    candidate = str(text).strip()
    think = re.match(r"^<think>.*?</think>\s*(.*)$", candidate, flags=re.DOTALL)
    if think:
        candidate = think.group(1).strip()
    fence = re.match(r"^```(?:json)?[ \t]*\r?\n(?P<body>.*)\r?\n```[ \t]*$", candidate, flags=re.IGNORECASE | re.DOTALL)
    if fence:
        candidate = fence.group("body").strip()
    try:
        payload = json.loads(candidate)
    except json.JSONDecodeError:
        first_open, last_close = candidate.find("{"), candidate.rfind("}")
        if first_open < 0 or last_close <= first_open:
            return None
        try:
            payload = json.loads(candidate[first_open:last_close + 1])
        except json.JSONDecodeError:
            return None
    if not isinstance(payload, dict) or any(field not in payload for field in EVALUATED_NAME_FIELDS):
        return None
    projected = {field: payload[field] for field in EVALUATED_NAME_FIELDS}
    parsed = parse_response_json(
        json.dumps(projected, ensure_ascii=False),
        allowed_fields=EVALUATED_NAME_FIELDS,
        api_status="200",
    )
    return parsed if hasattr(parsed, "values") else None


def project_strict_parse_failures(
    responses: dict[str, dict[str, dict[str, dict[str, Any]]]],
    results_root: Path,
) -> int:
    """Recover evaluated-field projections from preserved raw failures."""
    root = results_root.resolve()
    recovered = 0
    for model_rows in responses.values():
        for document_rows in model_rows.values():
            for row in document_rows.values():
                if row.get("status") != "parse_fail_kept" or not row.get("raw_response_ref"):
                    continue
                raw_path = (results_root / str(row["raw_response_ref"])).resolve()
                if root not in raw_path.parents or not raw_path.is_file():
                    continue
                try:
                    body = json.loads(raw_path.read_text(encoding="utf-8"))
                    parsed = _project_model_text(_model_text_from_raw_body(body, str(row["model_id"])))
                except (OSError, UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError):
                    continue
                if parsed is None:
                    continue
                row["strict_status"] = row["status"]
                row["status"] = "ok_projected"
                row["parsed"] = {
                    "values": parsed.values,
                    "confidences": parsed.confidences,
                    "repair_path": list(parsed.repair_path) + ["project_evaluated_six_fields"],
                }
                row["parser_version"] = f"{PARSER_VERSION}+evaluated_six_projection_v1"
                row["parser_failure"] = None
                recovered += 1
    return recovered


def value_from_response(row: dict[str, Any] | None, field_name: str) -> str | None:
    if not row or row.get("status") not in FIELD_BEARING_RESULT_STATUSES:
        return None
    parsed = row.get("parsed") or {}
    values = parsed.get("values") or {}
    return safe_prediction(values.get(field_name))


def confidence_from_response(row: dict[str, Any] | None, field_name: str) -> int | None:
    if not row or row.get("status") not in FIELD_BEARING_RESULT_STATUSES:
        return None
    confidences = ((row.get("parsed") or {}).get("confidences") or {})
    value = confidences.get(field_name)
    return int(value) if isinstance(value, int) else None


def source_hash(
    paths: Iterable[Path],
    ground_truth: Path,
    *,
    results_root: Path | None = None,
    raw_paths: Iterable[Path] = (),
) -> str:
    root = results_root.resolve() if results_root is not None else None
    raw_entries = []
    for path in sorted(set(raw_paths)):
        name = str(path.relative_to(root)) if root is not None else path.name
        raw_entries.append({"path_name": name, "sha256": sha256_file(path)})
    payload = {
        "ground_truth": {"path_name": ground_truth.name, "sha256": sha256_file(ground_truth)},
        "results": [{"path_name": path.name, "sha256": sha256_file(path)} for path in paths],
        "raw_responses": raw_entries,
    }
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="raise", lineterminator="\n")
        writer.writeheader()
        writer.writerows({name: row.get(name, "") for name in fieldnames} for row in rows)
    os.replace(temp, path)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def replace_models(path: Path, rows: list[dict[str, Any]], model_ids: set[str]) -> None:
    """Preserve historical rows while making modern reruns idempotent."""
    prior = read_csv(path)
    kept = [row for row in prior if row.get("model_id") not in model_ids]
    fieldnames = list(prior[0]) if prior else list(rows[0])
    write_csv(path, kept + rows, fieldnames)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-root", type=Path, required=True)
    parser.add_argument("--ground-truth", type=Path, required=True)
    parser.add_argument("--derived-dir", type=Path, default=Path("outputs/derived"))
    parser.add_argument("--field-level-output", type=Path, required=True)
    parser.add_argument("--models", default=",".join(MODEL_ORDER))
    parser.add_argument("--render-manifest", type=Path)
    parser.add_argument("--expected-prompt-hash")
    parser.add_argument("--expected-schema-hash")
    parser.add_argument("--expected-run-id", default=RUN_ID)
    parser.add_argument("--expected-route-version")
    parser.add_argument("--ledger", action="append", type=Path, default=[])
    args = parser.parse_args()

    model_ids = tuple(value.strip() for value in args.models.split(",") if value.strip())
    if not model_ids:
        raise ValueError("at least one model is required")
    responses, result_paths = load_results(args.results_root)
    projected_parse_failures_recovered = project_strict_parse_failures(responses, args.results_root)
    projected_by_model = {
        model_id: sum(1 for rows in responses[model_id].values() for row in rows.values() if row.get("status") == "ok_projected")
        for model_id in model_ids
    }
    unrecovered_parse_failures_by_model = {
        model_id: sum(1 for rows in responses[model_id].values() for row in rows.values() if row.get("status") == "parse_fail_kept")
        for model_id in model_ids
    }
    raw_paths = validate_result_lineage(
        responses,
        model_ids,
        args.results_root,
        args.render_manifest,
        expected_prompt_hash=args.expected_prompt_hash,
        expected_schema_hash=args.expected_schema_hash,
        expected_run_id=args.expected_run_id,
        expected_route_version=args.expected_route_version,
    )
    submitted_by_model = validate_ledger_evidence(responses, model_ids, args.ledger)
    ground_truth = load_ground_truth(args.ground_truth)
    raw_nonblank_evaluated_fields = sum(
        1
        for row in ground_truth.values()
        for gt_column in GT_FIELDS.values()
        if safe_ground_truth(row.get(gt_column)) is not None
    )
    denominator_status = (
        f"raw_six_name_nonblank_{raw_nonblank_evaluated_fields}_historical_3684_rule_not_applied"
    )
    missing_models = [model for model in model_ids if model not in responses]
    if missing_models:
        raise ValueError(f"no normalized results for requested model(s): {missing_models}")

    docs_by_model: dict[str, list[str]] = {}
    for model_id in model_ids:
        docs = sorted(responses[model_id])
        if len(docs) != 622:
            raise ValueError(f"{model_id} has {len(docs)} result documents, expected 622")
        if set(docs) != set(ground_truth):
            raise ValueError(f"{model_id} result document IDs do not match the 622-row ground truth")
        incomplete = [
            (doc_id, view_id)
            for doc_id in docs
            for view_id in VIEW_ORDER
            if responses[model_id][doc_id].get(view_id, {}).get("status") not in TERMINAL_RESULT_STATUSES
        ]
        if incomplete:
            raise ValueError(
                f"{model_id} has {len(incomplete)} incomplete/non-ok document-view responses; "
                "complete the full screen with terminal ok/parse_fail_kept results before deriving modern metrics"
            )
        docs_by_model[model_id] = docs

    input_hash = source_hash(
        [path for path in result_paths if path.parent.name in model_ids],
        args.ground_truth,
        results_root=args.results_root,
        raw_paths=raw_paths,
    )
    field_level_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    correlation_rows: list[dict[str, Any]] = []
    precision_rows: list[dict[str, Any]] = []
    cross_rows: list[dict[str, Any]] = []
    cost_rows: list[dict[str, Any]] = []
    frontier_rows: list[dict[str, Any]] = []
    ensemble_rows: list[dict[str, Any]] = []
    failure_rows: list[dict[str, Any]] = []
    model_summaries: dict[str, Any] = {}

    for model_id in model_ids:
        docs = docs_by_model[model_id]
        model_responses = responses[model_id]
        by_strategy: dict[str, list[dict[str, Any]]] = {}
        model_failure_count = 0
        total_usage = 0
        total_latency = 0.0
        usage_rows = 0
        for doc_id in docs:
            for view_id in VIEW_ORDER:
                row = model_responses[doc_id].get(view_id)
                if not row or row.get("status") not in FIELD_BEARING_RESULT_STATUSES:
                    model_failure_count += 1
                usage = (row or {}).get("usage") or {}
                if isinstance(usage.get("totalTokenCount"), (int, float)):
                    total_usage += int(usage["totalTokenCount"])
                    usage_rows += 1
                if isinstance((row or {}).get("latency_seconds"), (int, float)):
                    total_latency += float(row["latency_seconds"])

        model_strategy_stats: dict[str, dict[str, Any]] = {}
        for strategy, views in STRATEGIES.items():
            member_distances = [0 for _ in views]
            member_gt_chars = [0 for _ in views]
            member_correct: list[list[bool]] = [[] for _ in views]
            member_errors: list[list[bool]] = [[] for _ in views]
            consensus_distance = 0
            consensus_gt_chars = 0
            consensus_correct: list[bool] = []
            scores: list[float] = []
            for doc_id in docs:
                gt_row = ground_truth[doc_id]
                for field_name, gt_column in GT_FIELDS.items():
                    gt = safe_ground_truth(gt_row.get(gt_column))
                    if gt is None:
                        continue
                    gt_normalized = normalize_field(gt)
                    if gt_normalized is None:
                        raise AssertionError("nonblank ground truth normalized to blank")
                    values = [value_from_response(model_responses[doc_id].get(view), field_name) for view in views]
                    normalized_values = [normalize_field(value) for value in values]
                    if len(views) == 1:
                        consensus_value = normalized_values[0]
                        score = 1.0 if consensus_value is not None else 0.0
                        n_valid = int(consensus_value is not None)
                        n_missing = int(consensus_value is None)
                        field_confidence = score
                        valid_fraction = float(n_valid)
                    else:
                        result = progressive_consensus(normalized_values)
                        consensus_value = result.consensus_text or None
                        n_valid = result.n_valid_samples
                        n_missing = result.n_missing_samples
                        field_confidence = result.field_confidence
                        valid_fraction = n_valid / len(views)
                        # Availability is part of the acceptance score: a
                        # single successful member cannot look unanimous when
                        # the other requested views are missing.
                        score = field_confidence * valid_fraction if n_valid else 0.0
                    exact = is_exact_match(consensus_value, gt)
                    cer = character_error_rate(consensus_value, gt)
                    if exact is None or cer is None:
                        raise AssertionError("nonblank ground truth unexpectedly produced an undefined metric")
                    consensus_correct.append(bool(exact))
                    consensus_distance += levenshtein_distance(normalize_field(consensus_value) or "", gt_normalized)
                    consensus_gt_chars += len(gt_normalized)
                    scores.append(score)
                    for index, value in enumerate(values):
                        individual_exact = is_exact_match(value, gt)
                        individual_cer = character_error_rate(value, gt)
                        member_correct[index].append(bool(individual_exact))
                        member_errors[index].append(not bool(individual_exact))
                        member_distances[index] += levenshtein_distance(normalize_field(value) or "", gt_normalized)
                        member_gt_chars[index] += len(gt_normalized)
                    field_level_rows.append(
                        {
                            "doc_id": doc_id,
                            "model_id": model_id,
                            "field_name": field_name,
                            "strategy": strategy,
                            "views": "+".join(views),
                            "n_valid_samples": n_valid,
                            "n_missing_samples": n_missing,
                            "agreement_score": score,
                            "field_confidence": field_confidence,
                            "valid_fraction": valid_fraction,
                            "score_definition": "raw_consensus_character_agreement_times_view_availability",
                            "is_exact_correct": bool(exact),
                            "cer": cer,
                        }
                    )

            correlation = pairwise_error_correlation_summary(member_errors)
            total = len(consensus_correct)
            individual_cer = (
                sum(member_distances) / sum(member_gt_chars)
                if sum(member_gt_chars)
                else None
            )
            individual_accuracy = sum(sum(values) / len(values) for values in member_correct) / len(member_correct)
            consensus_cer = consensus_distance / consensus_gt_chars if consensus_gt_chars else None
            consensus_accuracy = sum(consensus_correct) / total if total else None
            stats = {
                "total": total,
                "scores": scores,
                "correct": consensus_correct,
                "individual_cer": individual_cer,
                "individual_accuracy": individual_accuracy,
                "consensus_cer": consensus_cer,
                "consensus_accuracy": consensus_accuracy,
                "correlation": correlation.mean_correlation,
                "correlation_pairs_used": correlation.n_pairs_used,
                "correlation_pairs_undefined": correlation.n_pairs_undefined,
                "n_samples": len(views),
                "family": STRATEGY_FAMILY[strategy],
            }
            model_strategy_stats[strategy] = stats
            notes = (
                "Modern PA screen measured on the raw six-name nonblank population; "
                "the recovered historical 3,684-row exclusion rule is not applied by this script. "
                "Raw agreement is not calibrated. See docs/GT_LINEAGE.md."
            )
            summary_rows.append(
                {
                    "model_id": model_id,
                    "strategy": strategy,
                    "family": stats["family"],
                    "n_samples": stats["n_samples"],
                    "individual_cer": fmt(stats["individual_cer"]),
                    "individual_field_accuracy": fmt(stats["individual_accuracy"]),
                    "error_correlation": fmt(stats["correlation"]),
                    "consensus_cer": fmt(stats["consensus_cer"]),
                    "consensus_field_accuracy": fmt(stats["consensus_accuracy"]),
                    "total_evaluated_fields": total,
                    "denominator_status": denominator_status,
                    "evidence_status": EVIDENCE_STATUS,
                    "source_artifact": "external modern normalized results + PA_DEATH/WARP/5164_gts.csv",
                    "source_sha256": input_hash,
                    "notes": notes,
                }
            )
            if stats["correlation"] is not None:
                correlation_rows.append(
                    {
                        "model_id": model_id,
                        "strategy": strategy,
                        "family": stats["family"],
                        "n_samples": stats["n_samples"],
                        "error_correlation": fmt(stats["correlation"]),
                        "stylized_effective_sample_size": fmt(stats["n_samples"] / (1 + (stats["n_samples"] - 1) * stats["correlation"])),
                        "correlation_scope": "mean_pairwise_field_error_indicator",
                        "total_evaluated_fields": total,
                        "denominator_status": denominator_status,
                        "evidence_status": EVIDENCE_STATUS,
                        "source_artifact": "external modern normalized results + PA_DEATH/WARP/5164_gts.csv",
                        "source_sha256": input_hash,
                        "notes": f"Pairwise correlations used={stats['correlation_pairs_used']}; undefined={stats['correlation_pairs_undefined']}. N_eff is stylized theory, not a measured count.",
                    }
                )

            thresholds = sorted({0.0, 1.0, *scores})
            curve = precision_coverage_curve(scores, [bool(value) for value in consensus_correct], thresholds)
            for point in curve:
                precision_rows.append(
                    {
                        "model_id": model_id,
                        "strategy": strategy,
                        "n_samples": stats["n_samples"],
                        "score_definition": "raw_consensus_character_agreement_times_view_availability",
                        "confidence_threshold": fmt(point.threshold),
                        "total_evaluated_fields": point.total_evaluated_fields,
                        "accepted_fields": point.accepted_fields,
                        "coverage": fmt(point.coverage),
                        "accepted_correct": point.accepted_correct,
                        "precision": fmt(point.precision),
                        "precision_ci_low": fmt(point.precision_ci_low),
                        "precision_ci_high": fmt(point.precision_ci_high),
                        "review_fields": point.review_fields,
                        "denominator_status": denominator_status,
                        "evidence_status": EVIDENCE_STATUS,
                        "source_artifact": "external modern normalized results + PA_DEATH/WARP/5164_gts.csv",
                        "source_sha256": input_hash,
                        "notes": "Descriptive held-out curve; threshold was not tuned to select a transform. Raw agreement is not calibrated probability.",
                    }
                )

            target_points = [point for point in curve if point.precision is not None and point.precision >= TARGET_PRECISION]
            best = max(target_points, key=lambda point: (point.coverage, -point.threshold)) if target_points else None
            for display_strategy in ("unchanged_3", "Pad", "Grid Warp", "visual_mixed_6"):
                if display_strategy != strategy:
                    continue
                cross_rows.append(
                    {
                        "model_id": model_id,
                        "strategy": strategy,
                        "n_samples": stats["n_samples"],
                        "target_precision": TARGET_PRECISION,
                        "confidence_threshold": fmt(best.threshold if best else None),
                        "total_evaluated_fields": total,
                        "accepted_fields": best.accepted_fields if best else "",
                        "coverage": fmt(best.coverage if best else None),
                        "observed_precision": fmt(best.precision if best else None),
                        "review_fields": best.review_fields if best else "",
                        "denominator_status": denominator_status,
                        "evidence_status": EVIDENCE_STATUS if best else "modern_measured_target_not_met",
                        "source_artifact": "outputs/derived/precision_coverage.csv",
                        "source_sha256": input_hash,
                        "notes": "Operating point maximizes descriptive coverage among observed points meeting the predeclared 95% target; it is not a calibrated threshold.",
                    }
                )
            ensemble_rows.append(
                {
                    "model_id": model_id,
                    "strategy": strategy,
                    "family": stats["family"],
                    "n_samples": stats["n_samples"],
                    "consensus_cer": fmt(stats["consensus_cer"]),
                    "consensus_field_accuracy": fmt(stats["consensus_accuracy"]),
                    "average_raw_confidence": fmt(sum(scores) / len(scores) if scores else None),
                    "total_evaluated_fields": total,
                    "total_sample_records": total * len(views),
                    "denominator_status": denominator_status,
                    "evidence_status": EVIDENCE_STATUS,
                    "source_artifact": "external modern normalized results + PA_DEATH/WARP/5164_gts.csv",
                    "source_sha256": input_hash,
                    "notes": "Modern screen consensus in canonical view order; no additional provider calls.",
                }
            )

        all_results = [
            row
            for view_rows in model_responses.values()
            for row in view_rows.values()
            if row.get("status") in TERMINAL_RESULT_STATUSES
        ]
        cost_rows.append(
            {
                "model_id": model_id,
                "run_id": RUN_ID,
                "strategy": "all_views_9",
                "n_samples": 9,
                "request_count": submitted_by_model.get(model_id, len(all_results)),
                "usage_unit": "provider_total_tokens",
                "usage_amount": total_usage,
                "currency": "",
                "cost_amount": "",
                "pricing_snapshot_id": "",
                "cost_status": "blocked_pricing_not_located",
                "evidence_status": "measured_usage_no_price",
                "source_artifact": "external modern normalized results",
                "source_sha256": input_hash,
                "notes": f"Ledger submitted attempts={submitted_by_model.get(model_id, 'not_supplied')}; terminal response rows={len(all_results)}; field-bearing rows={len(all_results) - sum(1 for view_rows in model_responses.values() for row in view_rows.values() if row.get('status') == 'parse_fail_kept')}; usage rows with totalTokenCount={usage_rows}; aggregate latency_seconds={total_latency:.2f}.",
            }
        )
        model_summaries[model_id] = {
            "documents": len(docs),
            "expected_views": len(VIEW_ORDER),
            "response_rows": len(all_results),
            "field_bearing_response_rows": len(all_results) - sum(
                1
                for view_rows in model_responses.values()
                for row in view_rows.values()
                if row.get("status") == "parse_fail_kept"
            ),
            "failed_or_non_field_bearing_view_rows": model_failure_count,
            "total_usage_tokens": total_usage,
            "usage_rows": usage_rows,
            "total_latency_seconds": total_latency,
            "provider_submitted_attempts": submitted_by_model.get(model_id),
            "projected_parse_failures_recovered": projected_by_model[model_id],
            "unrecovered_parse_failures": unrecovered_parse_failures_by_model[model_id],
            "strategies": {
                strategy: {
                    key: value
                    for key, value in stats.items()
                    if key not in {"scores", "correct"}
                }
                for strategy, stats in model_strategy_stats.items()
            },
        }

    for row in cross_rows:
        if row["coverage"] != "":
            frontier_rows.append(
                {
                    "model_id": row["model_id"],
                    "strategy": row["strategy"],
                    "n_samples": row["n_samples"],
                    "target_precision": row["target_precision"],
                    "observed_precision": row["observed_precision"],
                    "coverage": row["coverage"],
                    "review_fields_per_1000": fmt(1000 * int(row["review_fields"]) / int(row["total_evaluated_fields"])),
                    "cost_per_1000_fields": "",
                    "currency": "",
                    "cost_status": "blocked_pricing_not_located",
                    "denominator_status": denominator_status,
                    "evidence_status": EVIDENCE_STATUS,
                    "source_artifact": "outputs/derived/cross_model_operating_points.csv",
                    "source_sha256": input_hash,
                    "notes": "Review burden is descriptive at the observed point meeting the predeclared target; no dollar cost fabricated.",
                }
            )

    args.field_level_output.parent.mkdir(parents=True, exist_ok=True)
    field_level_temp = args.field_level_output.with_suffix(args.field_level_output.suffix + ".tmp")
    with field_level_temp.open("w", encoding="utf-8", newline="") as stream:
        for row in field_level_rows:
            stream.write(canonical_json(row) + "\n")
    os.replace(field_level_temp, args.field_level_output)

    model_set = set(model_ids)
    derived = args.derived_dir
    replace_models(
        derived / "strategy_summary.csv",
        summary_rows,
        model_set,
    )
    replace_models(derived / "error_correlation_summary.csv", correlation_rows, model_set)
    replace_models(derived / "precision_coverage.csv", precision_rows, model_set)
    replace_models(derived / "cross_model_operating_points.csv", cross_rows, model_set)
    replace_models(derived / "cost_by_run.csv", cost_rows, model_set)
    replace_models(derived / "review_frontier.csv", frontier_rows, model_set)
    replace_models(derived / "ensemble_size.csv", ensemble_rows, model_set)

    failure_prior = read_csv(derived / "failure_examples.csv")
    failure_prior = [row for row in failure_prior if row.get("model_id") not in model_set]
    for model_id in model_ids:
        wrong = sum(
            1
            for row in field_level_rows
            if row["model_id"] == model_id and row["strategy"] == "Grid Warp" and not row["is_exact_correct"] and row["agreement_score"] >= 0.999
        )
        if wrong:
            failure_rows.append(
                {
                    "example_id": f"private_high_agreement_wrong_{hashlib.sha256(model_id.encode()).hexdigest()[:12]}",
                    "model_id": model_id,
                    "run_id": RUN_ID,
                    "strategy": "Grid Warp",
                    "transform_id": "private_aggregate_only",
                    "agreement": "0.999_or_higher",
                    "prediction": "",
                    "ground_truth": "",
                    "error_type": "high_agreement_wrong_private_values_not_exported",
                    "crop_reference": "",
                    "release_status": "private_not_exported",
                    "denominator_status": denominator_status,
                    "evidence_status": "measured_private_example_count_only",
                    "source_artifact": "external modern field-level table",
                    "source_sha256": input_hash,
                    "notes": f"Aggregate count={wrong}; raw values/crops remain outside Git and are not release-authorized.",
                }
            )
    failure_output = failure_prior + failure_rows
    if failure_output:
        write_csv(
            derived / "failure_examples.csv",
            failure_output,
            list(failure_output[0]),
        )

    receipt = {
        "schema_version": 1,
        "status": "complete",
        "run_id": RUN_ID,
        "models": list(model_ids),
        "documents": 622,
        "views_per_document": len(VIEW_ORDER),
        "target_fields": list(GT_FIELDS),
        "raw_nonblank_evaluated_fields": raw_nonblank_evaluated_fields,
        "canonical_regression_target": 3684,
        "denominator_status": denominator_status,
        "source_hash": input_hash,
        "raw_response_files_hashed": len(raw_paths),
        "ground_truth": {"path": str(args.ground_truth), "sha256": sha256_file(args.ground_truth)},
        "results_root": str(args.results_root),
        "field_level_output": str(args.field_level_output),
        "parser_version": PARSER_VERSION,
        "projected_parse_failures_recovered": projected_parse_failures_recovered,
        "projected_parse_failures_by_model": projected_by_model,
        "unrecovered_parse_failures_by_model": unrecovered_parse_failures_by_model,
        "ledger_submitted_attempts": submitted_by_model,
        "target_precision": TARGET_PRECISION,
        "provider_calls": 0,
        "model_summaries": model_summaries,
        "derived_tables": [
            "strategy_summary.csv",
            "error_correlation_summary.csv",
            "precision_coverage.csv",
            "cross_model_operating_points.csv",
            "cost_by_run.csv",
            "review_frontier.csv",
            "ensemble_size.csv",
            "failure_examples.csv",
        ],
    }
    receipt_path = Path("local_agent/runtime/modern_analysis_receipt.json")
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(canonical_json(receipt) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
