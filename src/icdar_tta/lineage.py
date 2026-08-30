"""Lineage/provenance record helpers.

Implements the "Raw model-response provenance" contract in
``docs/DATA_CONTRACT.md``: every new response should carry provider,
exact model ID, timestamp, prompt/schema hash, source image hash,
transform ID, exposed generation parameters, raw response, parser
version, status/retry, usage, latency, and pricing snapshot when cost is
derived. This module validates that a provenance record is complete
enough to trust, without performing any network I/O itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


class LineageError(ValueError):
    pass


#: Required per docs/DATA_CONTRACT.md "Raw model-response provenance".
REQUIRED_LINEAGE_FIELDS = (
    "provider",
    "model_id",
    "request_timestamp_utc",
    "prompt_hash",
    "source_image_hash",
    "transform_id",
    "parser_version",
    "status",
)

#: Recorded "when available" / "when returned" per the same section;
#: absence is not an error but is reported by completeness checks.
RECOMMENDED_LINEAGE_FIELDS = (
    "generation_params",
    "response_text",
    "retry_count",
    "usage",
    "latency_seconds",
    "pricing_snapshot_id",
)


@dataclass(frozen=True)
class LineageRecord:
    provider: str
    model_id: str
    request_timestamp_utc: str
    prompt_hash: str
    source_image_hash: str
    transform_id: str
    parser_version: str
    status: str

    generation_params: Optional[dict] = None
    response_text: Optional[str] = None
    retry_count: Optional[int] = None
    usage: Optional[dict] = None
    latency_seconds: Optional[float] = None
    pricing_snapshot_id: Optional[str] = None

    def __post_init__(self) -> None:
        missing = [n for n in REQUIRED_LINEAGE_FIELDS if not getattr(self, n)]
        if missing:
            raise LineageError(f"LineageRecord missing required field(s): {missing}")

    def missing_recommended_fields(self) -> list:
        return [n for n in RECOMMENDED_LINEAGE_FIELDS if getattr(self, n) is None]

    def has_cost_provenance(self) -> bool:
        """True only if enough is present to derive a cost figure: usage
        counts plus a pricing snapshot identifier. Matches
        docs/DATA_CONTRACT.md's requirement that cost derivation record a
        "pricing snapshot ID or billing source".
        """
        return self.usage is not None and self.pricing_snapshot_id is not None


def validate_lineage_dict(data: dict) -> "LineageRecord":
    """Build and validate a LineageRecord from a plain dict (e.g. loaded
    from a committed JSON/YAML provenance file), raising LineageError
    with the exact missing field names on failure rather than a generic
    KeyError.
    """
    missing = [n for n in REQUIRED_LINEAGE_FIELDS if n not in data or not data[n]]
    if missing:
        raise LineageError(f"lineage record missing required field(s): {missing}")
    known = set(REQUIRED_LINEAGE_FIELDS) | set(RECOMMENDED_LINEAGE_FIELDS)
    kwargs = {k: v for k, v in data.items() if k in known}
    return LineageRecord(**kwargs)
