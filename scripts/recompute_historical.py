#!/usr/bin/env python3
"""Recompute compact historical ICDAR TTA chart tables from local evidence.

This command is offline and standard-library-only. It reads explicitly supplied
historical roots and writes only ``--output-dir`` plus an optional, explicitly
requested ``--local-manifest``. Raw field values and machine paths are never
copied into chart tables.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence

MODEL_HISTORICAL = "models/gemini-2.0-flash"
MODERN_MODEL_IDS = (
    "gemini-3.7-flash",
    "gemini-3.5-flash-lite",
    "sagemaker-qwen3-vl-8b-instruct-fp8",
)
# Paper-era six-field row-population target. See docs/GT_LINEAGE.md for the
# recovered historical exclusion rule and the v9/v10 one-blank-row caveat.
PAPER_DENOMINATOR_TARGET = 3684
RAW_NAME_FIELDS = (
    "SelfGivenName_edt",
    "SelfSurname_edt",
    "FatherGivenName_edt",
    "FatherSurname_edt",
    "MotherGivenName_edt",
    "MotherSurname_edt",
)

REQUIRED_OUTPUTS = (
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
)

TABLE_HEADERS = {
    "strategy_summary.csv": (
        "model_id", "strategy", "family", "n_samples", "individual_cer",
        "individual_field_accuracy", "error_correlation", "consensus_cer",
        "consensus_field_accuracy", "total_evaluated_fields",
        "denominator_status", "evidence_status", "source_artifact",
        "source_sha256", "notes",
    ),
    "error_correlation_summary.csv": (
        "model_id", "strategy", "family", "n_samples", "error_correlation",
        "stylized_effective_sample_size", "correlation_scope",
        "total_evaluated_fields", "denominator_status", "evidence_status",
        "source_artifact", "source_sha256", "notes",
    ),
    "precision_coverage.csv": (
        "model_id", "strategy", "n_samples", "score_definition",
        "confidence_threshold", "total_evaluated_fields", "accepted_fields",
        "coverage", "accepted_correct", "precision", "precision_ci_low",
        "precision_ci_high", "review_fields", "denominator_status",
        "evidence_status", "source_artifact", "source_sha256", "notes",
    ),
    "cost_by_run.csv": (
        "model_id", "run_id", "strategy", "n_samples", "request_count",
        "usage_unit", "usage_amount", "currency", "cost_amount",
        "pricing_snapshot_id", "cost_status", "evidence_status",
        "source_artifact", "source_sha256", "notes",
    ),
    "review_frontier.csv": (
        "model_id", "strategy", "n_samples", "target_precision",
        "observed_precision", "coverage", "review_fields_per_1000",
        "cost_per_1000_fields", "currency", "cost_status",
        "denominator_status", "evidence_status", "source_artifact",
        "source_sha256", "notes",
    ),
    "shift_agreement.csv": (
        "model_id", "direction", "relative_shift_px", "absolute_shift_px",
        "agreement", "is_multiple_of_16", "score_definition",
        "evidence_status", "source_artifact", "source_sha256", "notes",
    ),
    "cross_model_operating_points.csv": (
        "model_id", "strategy", "n_samples", "target_precision",
        "confidence_threshold", "total_evaluated_fields", "accepted_fields",
        "coverage", "observed_precision", "review_fields",
        "denominator_status", "evidence_status", "source_artifact",
        "source_sha256", "notes",
    ),
    "augmentation_contribution.csv": (
        "model_id", "family", "contribution_metric", "selection_count",
        "candidate_transform_count", "mean_mrr", "cv_fold_count",
        "denominator_status", "evidence_status", "source_artifact",
        "source_sha256", "notes",
    ),
    "ensemble_size.csv": (
        "model_id", "strategy", "family", "n_samples", "consensus_cer",
        "consensus_field_accuracy", "average_raw_confidence",
        "total_evaluated_fields", "total_sample_records", "denominator_status",
        "evidence_status", "source_artifact", "source_sha256", "notes",
    ),
    "failure_examples.csv": (
        "example_id", "model_id", "run_id", "strategy", "transform_id",
        "agreement", "prediction", "ground_truth", "error_type",
        "crop_reference", "release_status", "denominator_status",
        "evidence_status", "source_artifact", "source_sha256", "notes",
    ),
}


class DerivationError(RuntimeError):
    """Raised when a required historical source cannot be parsed safely."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_record(path: Path, logical_path: str, *, rows: int | None = None) -> dict:
    return {
        "logical_path": logical_path,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "rows": rows,
    }


def read_delimited(path: Path, delimiter: str | None = None) -> list[dict[str, str]]:
    if not path.is_file():
        raise DerivationError(f"required source file not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        if delimiter is None:
            sample = stream.read(8192)
            stream.seek(0)
            try:
                delimiter = csv.Sniffer().sniff(sample, delimiters=",\t").delimiter
            except csv.Error as exc:
                raise DerivationError(f"could not determine CSV/TSV delimiter for {path}: {exc}") from exc
        reader = csv.DictReader(stream, delimiter=delimiter)
        if reader.fieldnames is None:
            raise DerivationError(f"source has no header: {path}")
        rows = [dict(row) for row in reader]
    return rows


def require_columns(rows: Sequence[Mapping[str, str]], columns: Iterable[str], logical_path: str) -> None:
    if not rows:
        raise DerivationError(f"required source has no data rows: {logical_path}")
    missing = [name for name in columns if name not in rows[0]]
    if missing:
        raise DerivationError(f"source {logical_path} is missing columns: {missing}")


def float_value(value: str) -> float:
    match = re.search(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?", str(value))
    if not match:
        raise DerivationError(f"expected numeric value, got {value!r}")
    return float(match.group(0))


def int_value(value: str) -> int:
    return int(round(float_value(value)))


def fmt_float(value: float | None) -> str:
    if value is None:
        return ""
    if math.isnan(value) or math.isinf(value):
        raise DerivationError(f"refusing to write non-finite value: {value}")
    return format(value, ".17g")


def blank_row(filename: str) -> dict[str, str]:
    return {name: "" for name in TABLE_HEADERS[filename]}


def write_table(output_dir: Path, filename: str, rows: Sequence[Mapping[str, object]]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / filename
    header = TABLE_HEADERS[filename]
    with destination.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=header, extrasaction="raise", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in header})


def family_for_experiment(name: str) -> str:
    lower = name.lower()
    if "shift" in lower or "pad" in lower:
        return "pad"
    if "grid warp" in lower or "_gw_" in lower or lower.startswith("gw") or "warp" in lower:
        return "grid_warp"
    if "gnoise" in lower or "gaussian noise" in lower:
        return "gaussian_noise"
    if "blur" in lower:
        return "blur_and_resize"
    if "resize" in lower:
        return "resize"
    if "seam" in lower:
        return "seam_carving"
    if "temperature" in lower or re.search(r"(?:^|_)t(?:05|1|2)(?:_|$)", lower):
        return "temperature"
    if "baseline" in lower:
        return "unchanged"
    if "all" in lower:
        return "mixed"
    return "other"


def logical_join(*items: str) -> str:
    return ";".join(items)


def hash_join(*items: str) -> str:
    return ";".join(items)


def wilson_interval(successes: int, total: int) -> tuple[float | None, float | None]:
    if total == 0:
        return None, None
    z = 1.959963984540054
    p_hat = successes / total
    denom = 1 + z * z / total
    center = p_hat + z * z / (2 * total)
    margin = z * math.sqrt((p_hat * (1 - p_hat) + z * z / (4 * total)) / total)
    return max(0.0, (center - margin) / denom), min(1.0, (center + margin) / denom)


def derive_precision_rows(
    rows: Sequence[Mapping[str, str]], strategy: str, logical: str, source_hash: str
) -> tuple[list[dict[str, str]], list[dict[str, object]]]:
    require_columns(rows, ("consensus_confidence", "cer", "sample_count"), logical)
    scored: list[tuple[float, bool]] = []
    sample_counts: set[int] = set()
    for row in rows:
        score = float_value(row["consensus_confidence"])
        cer = float_value(row["cer"])
        if not 0.0 <= score <= 1.0:
            raise DerivationError(f"raw agreement outside [0,1] in {logical}: {score}")
        scored.append((score, cer == 0.0))
        sample_counts.add(int_value(row["sample_count"]))
    if len(sample_counts) != 1:
        raise DerivationError(f"mixed sample_count values in {logical}: {sorted(sample_counts)}")
    n_samples = next(iter(sample_counts))
    thresholds = sorted({score for score, _ in scored})
    output: list[dict[str, str]] = []
    points: list[dict[str, object]] = []
    total = len(scored)
    denom_status = f"historical_v7_{total}_rows_legacy_public_lineage_paper_target_{PAPER_DENOMINATOR_TARGET}"
    for threshold in thresholds:
        accepted = [correct for score, correct in scored if score >= threshold]
        accepted_count = len(accepted)
        correct_count = sum(accepted)
        precision = correct_count / accepted_count if accepted_count else None
        coverage = accepted_count / total if total else 0.0
        ci_low, ci_high = wilson_interval(correct_count, accepted_count)
        row = blank_row("precision_coverage.csv")
        row.update({
            "model_id": MODEL_HISTORICAL,
            "strategy": strategy,
            "n_samples": str(n_samples),
            "score_definition": "raw_consensus_character_agreement",
            "confidence_threshold": fmt_float(threshold),
            "total_evaluated_fields": str(total),
            "accepted_fields": str(accepted_count),
            "coverage": fmt_float(coverage),
            "accepted_correct": str(correct_count),
            "precision": fmt_float(precision),
            "precision_ci_low": fmt_float(ci_low),
            "precision_ci_high": fmt_float(ci_high),
            "review_fields": str(total - accepted_count),
            "denominator_status": denom_status,
            "evidence_status": "recomputed_historical_noncanonical",
            "source_artifact": logical,
            "source_sha256": source_hash,
            "notes": "Correct means source CER equals zero. Raw agreement is not a calibrated probability; this table uses the legacy/public v7 row population, while the paper-lineage target is the separate 3684-row contract in docs/GT_LINEAGE.md.",
        })
        output.append(row)
        points.append({
            "threshold": threshold,
            "total": total,
            "accepted": accepted_count,
            "correct": correct_count,
            "precision": precision,
            "coverage": coverage,
            "review": total - accepted_count,
            "n_samples": n_samples,
            "denominator_status": denom_status,
            "logical": logical,
            "source_hash": source_hash,
        })
    return output, points


def select_operating_point(points: Sequence[Mapping[str, object]], target: float) -> Mapping[str, object] | None:
    eligible = [p for p in points if p["precision"] is not None and float(p["precision"]) >= target]
    if not eligible:
        return None
    return max(eligible, key=lambda p: (int(p["accepted"]), -float(p["threshold"])))


def parse_shift_variant_counts(rows: Sequence[Mapping[str, str]]) -> dict[str, int]:
    require_columns(rows, ("experiment_name", "transformation_config", "num_samples"), "PA_DEATH/SHIFT/metrics_no_punc/run_settings.csv")
    counts: dict[str, int] = {}
    for row in rows:
        try:
            config = ast.literal_eval(row["transformation_config"])
            transforms = config["transformations"]
            granular = next(item for item in transforms if item.get("type") == "granular_shift")
            variants = granular["params"]["variants"]
        except (ValueError, SyntaxError, KeyError, StopIteration, TypeError) as exc:
            raise DerivationError(f"could not safely parse SHIFT transformation_config for {row['experiment_name']}: {exc}") from exc
        expected = int_value(row["num_samples"])
        if len(variants) != expected:
            raise DerivationError(
                f"SHIFT variant count mismatch for {row['experiment_name']}: config={len(variants)} num_samples={expected}"
            )
        counts[row["experiment_name"]] = len(variants)
    return counts


def count_ground_truth(path: Path) -> dict[str, object]:
    rows = read_delimited(path, ",")
    require_columns(rows, RAW_NAME_FIELDS, path.name)
    nonblank = {field: sum(str(row[field]).strip() != "" for row in rows) for field in RAW_NAME_FIELDS}
    return {
        "rows": len(rows),
        "columns": len(rows[0]),
        "nonblank_by_field": nonblank,
        "raw_six_name_nonblank": sum(nonblank.values()),
    }


def active_experiment_count(yaml_path: Path) -> int:
    count = 0
    for line in yaml_path.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("#"):
            continue
        if re.match(r"^\s*-?\s*experiment_name\s*:", line):
            count += 1
    return count


def derive_all(pa_root: Path, analysis_root: Path) -> tuple[dict[str, list[dict[str, str]]], list[dict[str, object]], dict[str, object]]:
    paths = {
        "warp_yaml": (pa_root / "WARP/PA_DEATH_WARP.yaml", "PA_DEATH/WARP/PA_DEATH_WARP.yaml"),
        "warp_rank": (pa_root / "WARP/metrics_no_punc/ensemble_selection_analysis.tsv", "PA_DEATH/WARP/metrics_no_punc/ensemble_selection_analysis.tsv"),
        "warp_by_k": (pa_root / "WARP/metrics_no_punc/experiment_level_consensus_summary_by_k.tsv", "PA_DEATH/WARP/metrics_no_punc/experiment_level_consensus_summary_by_k.tsv"),
        "warp_weighted": (pa_root / "WARP/metrics_no_punc/weighted_cer_by_experiment.tsv", "PA_DEATH/WARP/metrics_no_punc/weighted_cer_by_experiment.tsv"),
        "warp_gt": (pa_root / "WARP/5164_gts.csv", "PA_DEATH/WARP/5164_gts.csv"),
        "shift_settings": (pa_root / "SHIFT/metrics_no_punc/run_settings.csv", "PA_DEATH/SHIFT/metrics_no_punc/run_settings.csv"),
        "shift_weighted": (pa_root / "SHIFT/metrics_no_punc/weighted_cer_by_experiment.tsv", "PA_DEATH/SHIFT/metrics_no_punc/weighted_cer_by_experiment.tsv"),
        "shift_gt": (pa_root / "SHIFT/5164_gts.csv", "PA_DEATH/SHIFT/5164_gts.csv"),
        "shift_h": (pa_root / "CVPR_ANALYSIS/small_shift_horizontal_signal_data.csv", "PA_DEATH/CVPR_ANALYSIS/small_shift_horizontal_signal_data.csv"),
        "shift_v": (pa_root / "CVPR_ANALYSIS/small_shift_vertical_signal_data.csv", "PA_DEATH/CVPR_ANALYSIS/small_shift_vertical_signal_data.csv"),
        "fft_h": (pa_root / "CVPR_ANALYSIS/small_shift_horizontal_fft_peaks.csv", "PA_DEATH/CVPR_ANALYSIS/small_shift_horizontal_fft_peaks.csv"),
        "fft_v": (pa_root / "CVPR_ANALYSIS/small_shift_vertical_fft_peaks.csv", "PA_DEATH/CVPR_ANALYSIS/small_shift_vertical_fft_peaks.csv"),
        "transform_table": (analysis_root / "analysis - v7/paper/transform_metrics_table.csv", "chat2rec_analysis/analysis - v7/paper/transform_metrics_table.csv"),
        "ensemble_table": (analysis_root / "analysis - v7/paper/ensemble_methods_table.csv", "chat2rec_analysis/analysis - v7/paper/ensemble_methods_table.csv"),
        "cv_rank": (analysis_root / "analysis - v7/best_consensus_CER/cv_rank_metrics_summary.tsv", "chat2rec_analysis/analysis - v7/best_consensus_CER/cv_rank_metrics_summary.tsv"),
        "consensus_gw": (analysis_root / "analysis - v7/outputs/consensus_reliability_analysis/consensus_gw_data.csv", "chat2rec_analysis/analysis - v7/outputs/consensus_reliability_analysis/consensus_gw_data.csv"),
        "consensus_shift": (analysis_root / "analysis - v7/outputs/consensus_reliability_analysis/consensus_shift_data.csv", "chat2rec_analysis/analysis - v7/outputs/consensus_reliability_analysis/consensus_shift_data.csv"),
        "consensus_resize": (analysis_root / "analysis - v7/outputs/consensus_reliability_analysis/consensus_resize_data.csv", "chat2rec_analysis/analysis - v7/outputs/consensus_reliability_analysis/consensus_resize_data.csv"),
    }
    for path, _ in paths.values():
        if not path.is_file():
            raise DerivationError(f"required source file not found: {path}")

    parsed = {
        "warp_rank": read_delimited(paths["warp_rank"][0], "\t"),
        "warp_by_k": read_delimited(paths["warp_by_k"][0], "\t"),
        "warp_weighted": read_delimited(paths["warp_weighted"][0], "\t"),
        "shift_settings": read_delimited(paths["shift_settings"][0], ","),
        "shift_weighted": read_delimited(paths["shift_weighted"][0], "\t"),
        "shift_h": read_delimited(paths["shift_h"][0], ","),
        "shift_v": read_delimited(paths["shift_v"][0], ","),
        "fft_h": read_delimited(paths["fft_h"][0], ","),
        "fft_v": read_delimited(paths["fft_v"][0], ","),
        "transform_table": read_delimited(paths["transform_table"][0], ","),
        "ensemble_table": read_delimited(paths["ensemble_table"][0], ","),
        "cv_rank": read_delimited(paths["cv_rank"][0], "\t"),
        "consensus_gw": read_delimited(paths["consensus_gw"][0], ","),
        "consensus_shift": read_delimited(paths["consensus_shift"][0], ","),
        "consensus_resize": read_delimited(paths["consensus_resize"][0], ","),
    }

    source_rows = {
        key: len(value) for key, value in parsed.items()
    }
    source_rows.update({"warp_gt": 622, "shift_gt": 622})
    sources = [
        source_record(path, logical, rows=source_rows.get(key))
        for key, (path, logical) in paths.items()
    ]
    source_by_key = {key: source_record(path, logical, rows=source_rows.get(key)) for key, (path, logical) in paths.items()}

    require_columns(parsed["warp_rank"], (
        "experiment_name", "avg_cer", "field_error_correlation", "sample_count"
    ), paths["warp_rank"][1])
    require_columns(parsed["warp_by_k"], (
        "experiment_name", "k_samples_used", "weighted_CER", "field_accuracy",
        "total_consensus_records", "total_samples", "avg_confidence"
    ), paths["warp_by_k"][1])

    by_k_index: dict[tuple[str, int], dict[str, str]] = {}
    max_k: dict[str, int] = defaultdict(int)
    for row in parsed["warp_by_k"]:
        key = (row["experiment_name"], int_value(row["k_samples_used"]))
        by_k_index[key] = row
        max_k[row["experiment_name"]] = max(max_k[row["experiment_name"]], key[1])

    strategy_rows: list[dict[str, str]] = []
    correlation_rows: list[dict[str, str]] = []
    rank_names = {row["experiment_name"] for row in parsed["warp_rank"]}
    for rank in sorted(parsed["warp_rank"], key=lambda row: row["experiment_name"]):
        name = rank["experiment_name"]
        k = max_k.get(name)
        if not k or (name, k) not in by_k_index:
            raise DerivationError(f"no ensemble-size summary found for WARP ranking row {name}")
        consensus = by_k_index[(name, k)]
        family = family_for_experiment(name)
        logical = logical_join(paths["warp_rank"][1], paths["warp_by_k"][1])
        hashes = hash_join(source_by_key["warp_rank"]["sha256"], source_by_key["warp_by_k"]["sha256"])
        row = blank_row("strategy_summary.csv")
        row.update({
            "model_id": MODEL_HISTORICAL, "strategy": name, "family": family,
            "n_samples": str(k), "individual_cer": fmt_float(float_value(rank["avg_cer"])),
            "error_correlation": fmt_float(float_value(rank["field_error_correlation"])),
            "consensus_cer": fmt_float(float_value(consensus["weighted_CER"])),
            "consensus_field_accuracy": fmt_float(float_value(consensus["field_accuracy"])),
            "total_evaluated_fields": consensus["total_consensus_records"],
            "denominator_status": "historical_warp_about_4920_noncanonical",
            "evidence_status": "reported_historical_aggregate",
            "source_artifact": logical, "source_sha256": hashes,
            "notes": "individual_cer is WARP avg_cer; consensus_cer is weighted_CER at the maximum available k. This is a legacy/public v7 aggregate and is not a paper-lineage 3684-row recomputation.",
        })
        strategy_rows.append(row)

        rho = float_value(rank["field_error_correlation"])
        neff = k / (1 + (k - 1) * rho)
        corr = blank_row("error_correlation_summary.csv")
        corr.update({
            "model_id": MODEL_HISTORICAL, "strategy": name, "family": family,
            "n_samples": str(k), "error_correlation": fmt_float(rho),
            "stylized_effective_sample_size": fmt_float(neff),
            "correlation_scope": "mean_pairwise_field_error_indicator",
            "total_evaluated_fields": rank["sample_count"],
            "denominator_status": "historical_warp_4920_noncanonical",
            "evidence_status": "reported_historical_aggregate",
            "source_artifact": paths["warp_rank"][1],
            "source_sha256": source_by_key["warp_rank"]["sha256"],
            "notes": "N_eff=N/(1+(N-1)rho) is stylized theoretical intuition, not a measured effective sample count.",
        })
        correlation_rows.append(corr)

    require_columns(parsed["transform_table"], (
        "Transform", "CER_5_Samples", "CER_10_Samples",
        "Field_Accuracy_5_Samples", "Field_Accuracy_10_Samples"
    ), paths["transform_table"][1])
    for source in parsed["transform_table"]:
        label = source["Transform"].rstrip("*")
        sample_sizes = (1,) if label == "Baseline" else (5, 10)
        for k in sample_sizes:
            suffix = "5" if k == 5 else "10"
            cer_key = f"CER_{suffix}_Samples"
            acc_key = f"Field_Accuracy_{suffix}_Samples"
            row = blank_row("strategy_summary.csv")
            row.update({
                "model_id": MODEL_HISTORICAL,
                "strategy": label,
                "family": family_for_experiment(label),
                "n_samples": str(k),
                "consensus_cer": fmt_float(float_value(source[cer_key])),
                "consensus_field_accuracy": fmt_float(float_value(source[acc_key])),
                "denominator_status": "historical_v7_aggregate_denominator_not_encoded",
                "evidence_status": "reported_historical_aggregate",
                "source_artifact": paths["transform_table"][1],
                "source_sha256": source_by_key["transform_table"]["sha256"],
                "notes": "Category-level v7 consensus CER/accuracy. Deliberately not labeled as individual CER; underlying denominator is absent from this table.",
            })
            strategy_rows.append(row)

    for family in ("Grid Warp", "Resize"):
        row = blank_row("error_correlation_summary.csv")
        row.update({
            "model_id": MODEL_HISTORICAL, "strategy": family,
            "family": family_for_experiment(family), "n_samples": "10",
            "denominator_status": "unavailable",
            "evidence_status": "blocked_unavailable",
            "source_artifact": paths["transform_table"][1],
            "source_sha256": source_by_key["transform_table"]["sha256"],
            "notes": "The inspected v7 machine-readable table contains CER and field accuracy but no error-correlation value; prose regression targets are not promoted to measured rows.",
        })
        correlation_rows.append(row)

    precision_rows: list[dict[str, str]] = []
    point_sets: dict[str, list[dict[str, object]]] = {}
    for key, strategy in (("consensus_gw", "Grid Warp"), ("consensus_shift", "Pad"), ("consensus_resize", "Resize")):
        rows, points = derive_precision_rows(parsed[key], strategy, paths[key][1], source_by_key[key]["sha256"])
        precision_rows.extend(rows)
        point_sets[strategy] = points

    shift_rows: list[dict[str, str]] = []
    for key, direction in (("shift_h", "horizontal"), ("shift_v", "vertical")):
        require_columns(parsed[key], ("relative_shift", "agreement"), paths[key][1])
        for source in sorted(parsed[key], key=lambda row: float_value(row["relative_shift"])):
            shift = float_value(source["relative_shift"])
            row = blank_row("shift_agreement.csv")
            row.update({
                "model_id": MODEL_HISTORICAL, "direction": direction,
                "relative_shift_px": fmt_float(shift), "absolute_shift_px": fmt_float(abs(shift)),
                "agreement": fmt_float(float_value(source["agreement"])),
                "is_multiple_of_16": "true" if shift % 16 == 0 else "false",
                "score_definition": "mean_pairwise_transcription_agreement_by_relative_shift",
                "evidence_status": "reported_historical_aggregate",
                "source_artifact": paths[key][1], "source_sha256": source_by_key[key]["sha256"],
                "notes": "Symmetric source series; shift zero is self/identical-view agreement. Periodicity is observational and does not prove proprietary architecture.",
            })
            shift_rows.append(row)

    cross_rows: list[dict[str, str]] = []
    target = 0.95
    target_text = "0.95"
    historical_ops: dict[str, Mapping[str, object]] = {}
    for strategy in ("Pad", "Grid Warp"):
        point = select_operating_point(point_sets[strategy], target)
        if point is None:
            source_point = point_sets[strategy][0]
            row = blank_row("cross_model_operating_points.csv")
            row.update({
                "model_id": MODEL_HISTORICAL, "strategy": strategy,
                "n_samples": str(source_point["n_samples"]), "target_precision": target_text,
                "total_evaluated_fields": str(source_point["total"]),
                "denominator_status": str(source_point["denominator_status"]),
                "evidence_status": "recomputed_historical_target_not_met",
                "source_artifact": str(source_point["logical"]),
                "source_sha256": str(source_point["source_hash"]),
                "notes": "No empirical raw-agreement threshold in this historical v7 source achieves the descriptive 95% precision target; no operating point is fabricated.",
            })
            cross_rows.append(row)
            continue
        historical_ops[strategy] = point
        row = blank_row("cross_model_operating_points.csv")
        row.update({
            "model_id": MODEL_HISTORICAL, "strategy": strategy,
            "n_samples": str(point["n_samples"]), "target_precision": target_text,
            "confidence_threshold": fmt_float(float(point["threshold"])),
            "total_evaluated_fields": str(point["total"]), "accepted_fields": str(point["accepted"]),
            "coverage": fmt_float(float(point["coverage"])),
            "observed_precision": fmt_float(float(point["precision"])),
            "review_fields": str(point["review"]), "denominator_status": str(point["denominator_status"]),
            "evidence_status": "recomputed_historical_noncanonical",
            "source_artifact": str(point["logical"]), "source_sha256": str(point["source_hash"]),
            "notes": "Descriptive 95% target for this offline table, not a frozen modern-test target; maximum historical coverage among empirical thresholds meeting the target.",
        })
        cross_rows.append(row)
    for model_id in MODERN_MODEL_IDS:
        for strategy in ("unchanged_3", "Pad", "Grid Warp", "visual_mixed_6"):
            row = blank_row("cross_model_operating_points.csv")
            row.update({
                "model_id": model_id, "strategy": strategy,
                "n_samples": "3" if strategy != "visual_mixed_6" else "6",
                "target_precision": target_text, "denominator_status": "unavailable_modern_screen_blocked",
                "evidence_status": "blocked_unavailable", "source_artifact": "local_agent/EXPERIMENT_MATRIX.md",
                "notes": "This historical-only recomputation does not ingest modern responses; the separate two-model screen and model-specific route blockers are documented in local_agent/MODERN_FULL_RECEIPT.md.",
            })
            cross_rows.append(row)

    cost_rows: list[dict[str, str]] = []
    for model_id, run_id in ((MODEL_HISTORICAL, "historical_flash2"),) + tuple((m, "modern_screen") for m in MODERN_MODEL_IDS):
        row = blank_row("cost_by_run.csv")
        row.update({
            "model_id": model_id, "run_id": run_id, "strategy": "all_available",
            "cost_status": "blocked_no_observed_usage" if model_id == MODEL_HISTORICAL else "blocked_no_run",
            "evidence_status": "blocked_unavailable", "source_artifact": "",
            "notes": "Historical generation settings are available but observed usage/pricing logs were not located." if model_id == MODEL_HISTORICAL else "This historical-only recomputation does not include the separate modern screen; see local_agent/MODERN_FULL_RECEIPT.md for its measured usage and route blockers.",
        })
        cost_rows.append(row)

    review_rows: list[dict[str, str]] = []
    for strategy, point in historical_ops.items():
        row = blank_row("review_frontier.csv")
        row.update({
            "model_id": MODEL_HISTORICAL, "strategy": strategy, "n_samples": str(point["n_samples"]),
            "target_precision": target_text, "observed_precision": fmt_float(float(point["precision"])),
            "coverage": fmt_float(float(point["coverage"])),
            "review_fields_per_1000": fmt_float(1000.0 * int(point["review"]) / int(point["total"])),
            "cost_status": "blocked_no_observed_usage", "denominator_status": str(point["denominator_status"]),
            "evidence_status": "blocked_cost_axis", "source_artifact": str(point["logical"]),
            "source_sha256": str(point["source_hash"]),
            "notes": "Review burden is recomputed, but no inference-cost frontier can be claimed because observed historical usage/pricing logs are absent.",
        })
        review_rows.append(row)

    require_columns(parsed["cv_rank"], ("last_added_experiment", "frequency", "MRR", "total_folds"), paths["cv_rank"][1])
    for strategy in sorted(set(point_sets) - set(historical_ops)):
        source_point = point_sets[strategy][0]
        row = blank_row("review_frontier.csv")
        row.update({
            "model_id": MODEL_HISTORICAL, "strategy": strategy,
            "n_samples": str(source_point["n_samples"]), "target_precision": target_text,
            "cost_status": "blocked_target_not_met_and_no_observed_usage",
            "denominator_status": str(source_point["denominator_status"]),
            "evidence_status": "blocked_target_and_cost_axis",
            "source_artifact": str(source_point["logical"]),
            "source_sha256": str(source_point["source_hash"]),
            "notes": "No empirical threshold meets the descriptive precision target, and observed usage/pricing logs are absent; review and cost coordinates are not fabricated.",
        })
        review_rows.append(row)

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in parsed["cv_rank"]:
        grouped[family_for_experiment(row["last_added_experiment"])].append(row)
    contribution_rows: list[dict[str, str]] = []
    for family in sorted(grouped):
        rows = grouped[family]
        frequencies = [int_value(row["frequency"]) for row in rows]
        mrr = [float_value(row["MRR"]) for row in rows]
        row = blank_row("augmentation_contribution.csv")
        row.update({
            "model_id": MODEL_HISTORICAL, "family": family,
            "contribution_metric": "selection_frequency_across_cv_folds",
            "selection_count": str(sum(frequencies)), "candidate_transform_count": str(len(rows)),
            "mean_mrr": fmt_float(sum(mrr) / len(mrr)), "cv_fold_count": "5",
            "denominator_status": "55_cv_rank_summary_rows",
            "evidence_status": "recomputed_from_reported_cv_summary",
            "source_artifact": paths["cv_rank"][1], "source_sha256": source_by_key["cv_rank"]["sha256"],
            "notes": "Family classification and sums are recomputed from v7 summary rows. Selection frequency is descriptive, not a causal leave-one-family-out effect.",
        })
        contribution_rows.append(row)

    ensemble_rows: list[dict[str, str]] = []
    allowed = rank_names | {"baseline"}
    for source in sorted(parsed["warp_by_k"], key=lambda row: (row["experiment_name"], int_value(row["k_samples_used"]))):
        if source["experiment_name"] not in allowed:
            continue
        row = blank_row("ensemble_size.csv")
        row.update({
            "model_id": MODEL_HISTORICAL, "strategy": source["experiment_name"],
            "family": family_for_experiment(source["experiment_name"]),
            "n_samples": str(int_value(source["k_samples_used"])),
            "consensus_cer": fmt_float(float_value(source["weighted_CER"])),
            "consensus_field_accuracy": fmt_float(float_value(source["field_accuracy"])),
            "average_raw_confidence": fmt_float(float_value(source["avg_confidence"])),
            "total_evaluated_fields": str(int_value(source["total_consensus_records"])),
            "total_sample_records": str(int_value(source["total_samples"])),
            "denominator_status": "historical_warp_about_4920_noncanonical",
            "evidence_status": "reported_historical_aggregate",
            "source_artifact": paths["warp_by_k"][1], "source_sha256": source_by_key["warp_by_k"]["sha256"],
            "notes": "weighted_CER and field_accuracy copied from the aggregate by-k source; this is the legacy/public v7 denominator, not the paper-lineage 3684-row population.",
        })
        ensemble_rows.append(row)

    failure_row = blank_row("failure_examples.csv")
    failure_row.update({
        "example_id": "unavailable_releasable_examples", "model_id": MODEL_HISTORICAL,
        "release_status": "blocked_private_lineage_and_crop_authorization",
        "denominator_status": "not_applicable", "evidence_status": "blocked_unavailable",
        "notes": "No release-authorized crop references and stable redacted high-agreement-wrong example IDs were found. Raw private values are intentionally not copied.",
    })

    tables = {
        "strategy_summary.csv": strategy_rows,
        "error_correlation_summary.csv": correlation_rows,
        "precision_coverage.csv": precision_rows,
        "cost_by_run.csv": cost_rows,
        "review_frontier.csv": review_rows,
        "shift_agreement.csv": shift_rows,
        "cross_model_operating_points.csv": cross_rows,
        "augmentation_contribution.csv": contribution_rows,
        "ensemble_size.csv": ensemble_rows,
        "failure_examples.csv": [failure_row],
    }

    gt_warp = count_ground_truth(paths["warp_gt"][0])
    gt_shift = count_ground_truth(paths["shift_gt"][0])
    shift_counts = parse_shift_variant_counts(parsed["shift_settings"])
    metadata = {
        "active_warp_experiment_count": active_experiment_count(paths["warp_yaml"][0]),
        "ground_truth": {"warp_18_column": gt_warp, "shift_20_column": gt_shift},
        "shift_variant_counts": shift_counts,
        "canonical_denominator_target": PAPER_DENOMINATOR_TARGET,
        "canonical_denominator_status": "historical_filter_recovered_current_recompute_uses_legacy_v7_source",
        "source_paths": paths,
        "source_records_by_key": source_by_key,
    }
    return tables, sources, metadata


def yaml_quote(value: str) -> str:
    # YAML single-quoted scalars preserve Windows backslashes verbatim while
    # still escaping the only special character in this quoting mode.
    return "'" + value.replace("'", "''") + "'"


def write_local_manifest(path: Path, pa_root: Path, analysis_root: Path, sources: Sequence[Mapping[str, object]], metadata: Mapping[str, object]) -> None:
    by_logical = {str(source["logical_path"]): source for source in sources}
    warp_gt = by_logical["PA_DEATH/WARP/5164_gts.csv"]
    shift_gt = by_logical["PA_DEATH/SHIFT/5164_gts.csv"]
    warp_yaml = by_logical["PA_DEATH/WARP/PA_DEATH_WARP.yaml"]
    warp_rank = by_logical["PA_DEATH/WARP/metrics_no_punc/ensemble_selection_analysis.tsv"]
    shift_settings = by_logical["PA_DEATH/SHIFT/metrics_no_punc/run_settings.csv"]
    lines = [
        "schema_version: 1",
        "project: icdar_tta",
        "generated_by: scripts/recompute_historical.py",
        "sources:",
        "  pa_root:", f"    path: {yaml_quote(str(pa_root))}", "    mode: read_only",
        "  analysis_root:", f"    path: {yaml_quote(str(analysis_root))}", "    mode: read_only",
        "  ground_truth:",
        f"    paper_target_evaluation_rows: {PAPER_DENOMINATOR_TARGET}",
        "    raw_six_name_nonblank_fields: 3718", "    raw_to_paper_display_count_difference: 34",
        "    denominator_status: legacy_v7_source_not_paper_lineage",
        "    schema_groups:",
        "      group_18_column:", f"        path: {yaml_quote(str(pa_root / 'WARP/5164_gts.csv'))}",
        f"        rows: {metadata['ground_truth']['warp_18_column']['rows']}", "        columns: 18",
        f"        sha256: {warp_gt['sha256']}",
        "      group_20_column:", f"        path: {yaml_quote(str(pa_root / 'SHIFT/5164_gts.csv'))}",
        f"        rows: {metadata['ground_truth']['shift_20_column']['rows']}", "        columns: 20",
        f"        sha256: {shift_gt['sha256']}",
        "  historical_augmentations:", f"    config_path: {yaml_quote(str(pa_root / 'WARP/PA_DEATH_WARP.yaml'))}",
        f"    config_sha256: {warp_yaml['sha256']}", f"    active_experiment_count: {metadata['active_warp_experiment_count']}",
        f"    ranking_path: {yaml_quote(str(pa_root / 'WARP/metrics_no_punc/ensemble_selection_analysis.tsv'))}",
        f"    ranking_rows: {warp_rank['rows']}", f"    ranking_sha256: {warp_rank['sha256']}",
        "  shift_analysis:", f"    root: {yaml_quote(str(pa_root / 'CVPR_ANALYSIS'))}",
        f"    run_settings_path: {yaml_quote(str(pa_root / 'SHIFT/metrics_no_punc/run_settings.csv'))}",
        f"    run_settings_rows: {shift_settings['rows']}", f"    run_settings_sha256: {shift_settings['sha256']}",
        "    variant_counts:",
    ]
    for name, count in sorted(metadata["shift_variant_counts"].items()):
        lines.append(f"      {name}: {count}")
    lines.extend([
        "  source_images:", "    expected_count: 622", "    resolved_manifest: null",
        "    status: blocked_exact_622_source_image_hash_manifest_not_recovered",
        "  segmentation_masks:", "    configured_windows_root: null",
        "    resolved_wsl_root: null", "    status: blocked_mask_root_outside_authorized_roots_and_coverage_unverified",
        "  usage_logs:", "    path: null", "    status: blocked_not_located",
        "  modern_responses:", "    path: null", "    status: managed_by_separate_modern_screen_receipt",
        "  modern_models:",
        f"    gemini_flash: {MODERN_MODEL_IDS[0]}", f"    gemini_flash_lite: {MODERN_MODEL_IDS[1]}",
        f"    qwen_vision: {MODERN_MODEL_IDS[2]}", "    status: two_gemini_35_screens_complete_other_routes_blocked",
        "notes:", "  - No credentials or secrets are stored here.",
        "  - The current script intentionally recomputes legacy/public v7 tables from the WARP/SHIFT sources; it does not yet emit paper-lineage v9/v10 tables.",
        "  - See docs/GT_LINEAGE.md for the six fields, 24-record historical exclusion, 3684 row formula, and one blank-row caveat.",
        "  - This historical-only command does not call providers; the separate modern screen is documented in local_agent/MODERN_FULL_RECEIPT.md.",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Offline deterministic historical TTA table recomputation")
    parser.add_argument("--pa-root", required=True, type=Path, help="Explicit local PA_DEATH root")
    parser.add_argument("--analysis-root", required=True, type=Path, help="Explicit local pa_death_records622_official analysis root")
    parser.add_argument("--output-dir", required=True, type=Path, help="Directory receiving deterministic CSV outputs")
    parser.add_argument("--local-manifest", type=Path, default=None, help="Optional explicitly requested ignored local manifest path")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        tables, sources, metadata = derive_all(args.pa_root, args.analysis_root)
        if set(tables) != set(REQUIRED_OUTPUTS):
            raise DerivationError(f"internal required-output mismatch: {sorted(tables)}")
        for filename in REQUIRED_OUTPUTS:
            write_table(args.output_dir, filename, tables[filename])
        if args.local_manifest is not None:
            write_local_manifest(args.local_manifest, args.pa_root, args.analysis_root, sources, metadata)
        outputs = []
        for filename in REQUIRED_OUTPUTS:
            path = args.output_dir / filename
            outputs.append({
                "filename": filename,
                "rows": len(tables[filename]),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            })
        receipt = {
            "status": "ok",
            "sources": sorted(sources, key=lambda item: str(item["logical_path"])),
            "outputs": outputs,
            "metadata": {
                "active_warp_experiment_count": metadata["active_warp_experiment_count"],
                "ground_truth": metadata["ground_truth"],
                "shift_variant_counts": metadata["shift_variant_counts"],
                "canonical_denominator_target": metadata["canonical_denominator_target"],
                "canonical_denominator_status": metadata["canonical_denominator_status"],
            },
            "local_manifest_updated": args.local_manifest is not None,
        }
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 0
    except (DerivationError, OSError, csv.Error, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
