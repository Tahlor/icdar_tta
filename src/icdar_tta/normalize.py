"""PA death-record name-field normalization and character error rate (CER).

Per ``docs/DATA_CONTRACT.md`` ("Fields"), the paper evaluation focused on
nonblank given-name/surname fields for the decedent, mother, and father.
Per ``docs/VALIDATION_TESTS.md`` ("Normalization/CER unit tests"), the
normalization policy must be:

- case-insensitive comparison;
- punctuation/space handling consistent with the paper evaluation;
- explicit empty/nonblank field handling;
- a standard edit-distance CER (insertion/deletion/substitution);
- Unicode-normalized if the source labels require it.

The exact historical normalization script has not yet been located in
this offline pass (see local_agent/HISTORICAL_INVENTORY.md /
GOALS_AUDIT.md). This module implements a documented, conservative
default policy and exposes every normalization decision as a separate,
overridable function so a recovered historical script can replace any
one step without forcing a rewrite of CER/consensus code that depends
on it.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Optional

#: Punctuation stripped during normalization. Hyphens and apostrophes are
#: deliberately *not* stripped by default because PA surnames commonly use
#: them meaningfully (e.g. "O'Brien", "Smith-Jones"); this is a documented
#: default, not a recovered historical constant.
_STRIP_PUNCTUATION_RE = re.compile(r"[.,;:!?\"\u201c\u201d]")
_WHITESPACE_RE = re.compile(r"\s+")


def is_blank(value: Optional[str]) -> bool:
    """Return True if a raw or normalized field value counts as blank."""
    return value is None or str(value).strip() == ""


def normalize_field(value: Optional[str]) -> Optional[str]:
    """Normalize one name-field value for comparison.

    Returns ``None`` for blank input so blank-handling stays explicit
    throughout the pipeline (never silently coerced to an empty string
    that would compare equal to itself elsewhere).

    Steps (documented default policy):
    1. Unicode NFKC normalization.
    2. Strip a fixed, documented punctuation set.
    3. Collapse internal whitespace runs to a single space.
    4. Strip leading/trailing whitespace.
    5. Casefold (case-insensitive comparison).
    """
    if is_blank(value):
        return None
    text = unicodedata.normalize("NFKC", str(value))
    text = _STRIP_PUNCTUATION_RE.sub("", text)
    text = _WHITESPACE_RE.sub(" ", text).strip()
    text = text.casefold()
    return text if text != "" else None


def is_exact_match(prediction: Optional[str], ground_truth: Optional[str]) -> Optional[bool]:
    """Exact-match comparison after normalization.

    Returns ``None`` (not False) when the ground truth is blank, since
    "nonblank evaluated fields" are the denominator per
    docs/EXPERIMENT_PLAN.md; blank ground-truth fields are out of scope
    for accuracy rather than automatic mismatches.
    """
    norm_gt = normalize_field(ground_truth)
    if norm_gt is None:
        return None
    norm_pred = normalize_field(prediction)
    return norm_pred == norm_gt


def levenshtein_distance(a: str, b: str) -> int:
    """Standard edit distance (insertion/deletion/substitution, unit cost)."""
    if a == b:
        return 0
    if len(a) == 0:
        return len(b)
    if len(b) == 0:
        return len(a)

    prev_row = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        cur_row = [i] + [0] * len(b)
        for j, cb in enumerate(b, start=1):
            cost_sub = prev_row[j - 1] + (0 if ca == cb else 1)
            cost_del = prev_row[j] + 1
            cost_ins = cur_row[j - 1] + 1
            cur_row[j] = min(cost_sub, cost_del, cost_ins)
        prev_row = cur_row
    return prev_row[-1]


def character_error_rate(
    prediction: Optional[str],
    ground_truth: Optional[str],
    *,
    normalized: bool = True,
) -> Optional[float]:
    """Character error rate = edit_distance(pred, gt) / len(gt).

    Returns ``None`` when ground truth is blank (undefined CER, not 0 or
    1) so blank-handling is explicit per docs/VALIDATION_TESTS.md.

    If ``normalized`` is True (default), both strings are passed through
    :func:`normalize_field` before distance computation, matching the
    comparison policy used for exact-match accuracy. Set to False to
    compute CER on raw strings.
    """
    if normalized:
        gt = normalize_field(ground_truth)
        pred = normalize_field(prediction) or ""
    else:
        if is_blank(ground_truth):
            gt = None
        else:
            gt = str(ground_truth)
        pred = "" if is_blank(prediction) else str(prediction)

    if gt is None:
        return None
    distance = levenshtein_distance(pred, gt)
    return distance / len(gt)
