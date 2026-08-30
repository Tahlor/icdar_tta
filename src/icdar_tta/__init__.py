"""icdar_tta: dependency-light offline analysis core.

This package implements the reproducible, no-network parts of the
icdar_tta workspace described in the repository root ``README.md`` and
``AGENTS.md``: field-record schema, PA name-field normalization/CER,
model-response parsing with explicit repair/failure handling,
deterministic progressive consensus/alignment/agreement, precision-
coverage/correlation/uncertainty metrics, lineage/provenance helpers,
and a validation CLI.

Nothing in this package performs network I/O, calls a model provider,
or requires credentials. See ``docs/DATA_CONTRACT.md`` and
``docs/VALIDATION_TESTS.md`` for the contracts this package implements.
"""

from icdar_tta import (
    agreement,
    alignment,
    consensus,
    lineage,
    manifest,
    metrics,
    normalize,
    parser,
    schema,
)

__all__ = [
    "agreement",
    "alignment",
    "consensus",
    "lineage",
    "manifest",
    "metrics",
    "normalize",
    "parser",
    "schema",
]

__version__ = "0.1.0"
