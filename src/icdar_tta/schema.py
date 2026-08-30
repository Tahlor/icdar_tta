"""Field-level record schema shared by every derived table in this package.

The canonical field-level prediction table is defined in
``docs/EXPERIMENT_PLAN.md`` (Phase 1) and the observation-identity rule is
defined in ``docs/DATA_CONTRACT.md`` ("Fields"):

    A field observation is uniquely addressable by at least
    (doc_id, field_name, model_id, run_id, strategy, transform_id, sample_index)

This module intentionally does not hardcode any paper-era reference
constant as ground truth. Reference counts (622 documents, 3,684 paper-era
evaluation rows; the paper describes them as nonblank) are exposed as
*documented defaults* that callers may override once local inventory is
connected, per
``docs/VALIDATION_TESTS.md`` ("Reference counts should be configurable
if the inventory proves the paper-era artifact differs").
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Any, Optional

# Paper-era reference counts. These are regression targets to verify
# against recomputed evidence, not assumed ground truth (AGENTS.md,
# "Source-of-truth priority").
PAPER_REFERENCE_DOCUMENT_COUNT = 622
PAPER_REFERENCE_EVALUATION_ROW_COUNT = 3684
# Backward-compatible name for callers that imported the original constant.
# Its historical name reflects the paper's wording, not a strict blankness
# assertion; the v9/v10 artifact has one retained blank row. See
# docs/GT_LINEAGE.md.
PAPER_REFERENCE_NONBLANK_FIELD_COUNT = PAPER_REFERENCE_EVALUATION_ROW_COUNT

#: Minimum required columns for the normalized field-level prediction
#: table, per docs/EXPERIMENT_PLAN.md Phase 1.
REQUIRED_FIELD_COLUMNS = (
    "doc_id",
    "field_name",
    "ground_truth",
    "model_id",
    "run_id",
    "strategy",
    "transform_id",
    "sample_index",
    "prediction",
    "normalized_prediction",
    "is_exact_correct",
    "cer",
    "response_path_or_id",
    "fold",
)

#: Optional columns recommended "where available" by the same section.
OPTIONAL_FIELD_COLUMNS = (
    "usage_tokens_prompt",
    "usage_tokens_completion",
    "latency_seconds",
    "api_status",
    "retry_count",
    "prompt_hash",
    "transform_params",
    "image_hash",
)


class SchemaError(ValueError):
    """Raised when a field-level record violates the schema contract."""


@dataclass(frozen=True)
class FieldRecord:
    """One row of the normalized field-level prediction table.

    Instances are immutable so that a table (a sequence of
    ``FieldRecord``) can be treated as a stable, hashable unit of
    evidence once constructed.
    """

    doc_id: str
    field_name: str
    ground_truth: Optional[str]
    model_id: str
    run_id: str
    strategy: str
    transform_id: str
    sample_index: int
    prediction: Optional[str]
    normalized_prediction: Optional[str]
    is_exact_correct: Optional[bool]
    cer: Optional[float]
    response_path_or_id: str
    fold: Optional[str] = None

    # Optional provenance columns (docs/DATA_CONTRACT.md "Raw model-response
    # provenance"). Kept optional so unit tests / partial evidence do not
    # need to fabricate values.
    usage_tokens_prompt: Optional[int] = None
    usage_tokens_completion: Optional[int] = None
    latency_seconds: Optional[float] = None
    api_status: Optional[str] = None
    retry_count: Optional[int] = None
    prompt_hash: Optional[str] = None
    transform_params: Optional[dict] = None
    image_hash: Optional[str] = None

    def __post_init__(self) -> None:
        missing = [
            name
            for name in ("doc_id", "field_name", "model_id", "run_id", "strategy", "transform_id", "response_path_or_id")
            if not getattr(self, name)
        ]
        if missing:
            raise SchemaError(f"FieldRecord missing required identity field(s): {missing}")
        if self.sample_index < 0:
            raise SchemaError(f"sample_index must be >= 0, got {self.sample_index}")

    @property
    def observation_key(self) -> tuple:
        """The unique-observation key from docs/DATA_CONTRACT.md."""
        return (
            self.doc_id,
            self.field_name,
            self.model_id,
            self.run_id,
            self.strategy,
            self.transform_id,
            self.sample_index,
        )

    def to_dict(self) -> dict:
        return {f.name: getattr(self, f.name) for f in fields(self)}


def validate_table_schema(rows: list) -> None:
    """Validate a list of dict-like or FieldRecord rows against the schema.

    Raises SchemaError on the first violation found. Checks performed:

    - every required column is present on every row;
    - observation keys are unique across the table (docs/DATA_CONTRACT.md);
    - ``doc_id`` values are unique per (doc_id, field_name) *only* combined
      with ground_truth consistency (a given (doc_id, field_name) must not
      have two different non-null ground_truth values, which would indicate
      a labeling/merge bug per docs/VALIDATION_TESTS.md
      "no duplicate (doc_id, field_name) ground-truth keys").
    """
    seen_obs_keys: set = set()
    gt_by_field: dict = {}

    for i, row in enumerate(rows):
        data = row.to_dict() if isinstance(row, FieldRecord) else dict(row)
        missing = [c for c in REQUIRED_FIELD_COLUMNS if c not in data]
        if missing:
            raise SchemaError(f"row {i} missing required column(s): {missing}")

        obs_key = (
            data["doc_id"],
            data["field_name"],
            data["model_id"],
            data["run_id"],
            data["strategy"],
            data["transform_id"],
            data["sample_index"],
        )
        if obs_key in seen_obs_keys:
            raise SchemaError(f"row {i} duplicates observation key {obs_key}")
        seen_obs_keys.add(obs_key)

        gt_key = (data["doc_id"], data["field_name"])
        gt_value = data.get("ground_truth")
        if gt_value is not None:
            prior = gt_by_field.get(gt_key)
            if prior is not None and prior != gt_value:
                raise SchemaError(
                    f"row {i} ground_truth conflict for {gt_key}: {prior!r} vs {gt_value!r}"
                )
            gt_by_field[gt_key] = gt_value


def count_distinct_documents(rows: list) -> int:
    docs = set()
    for row in rows:
        data = row.to_dict() if isinstance(row, FieldRecord) else dict(row)
        docs.add(data["doc_id"])
    return len(docs)


def count_nonblank_ground_truth_fields(rows: list) -> int:
    """Count distinct (doc_id, field_name) pairs with a nonblank ground truth.

    Counts the strict nonblank keys present in the supplied rows. Callers must
    apply the intended six-field/filter contract before using this count. The
    paper-era 3,684-row artifact target and its one retained blank row are
    documented separately in ``docs/GT_LINEAGE.md``.
    """
    keys = set()
    for row in rows:
        data = row.to_dict() if isinstance(row, FieldRecord) else dict(row)
        gt = data.get("ground_truth")
        if gt is not None and str(gt).strip() != "":
            keys.add((data["doc_id"], data["field_name"]))
    return len(keys)
