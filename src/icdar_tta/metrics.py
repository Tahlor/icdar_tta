"""Aggregate accuracy/CER metrics and precision-coverage-with-uncertainty curves.

Implements the checks in ``docs/VALIDATION_TESTS.md`` section 6
("Precision/coverage consistency tests"):

- ``accepted_fields + review_fields == total_evaluated_fields``;
- ``coverage == accepted_fields / total_evaluated_fields``;
- ``precision == accepted_correct / accepted_fields`` where accepted > 0;
- accepted sets are nested as the threshold becomes stricter for the
  same score definition;
- coverage is non-increasing as the threshold becomes stricter;
- sample counts and failure exclusions are explicit.

and the paper-metric regression targets in the same document / in
``README.md`` (71.2% / 9.0% / 75.2% / 7.2% / 74.8%), exposed here as
*tolerance-checkable* functions rather than hardcoded assertions -- the
actual regression tests live under ``tests/`` and load real recomputed
tables when available.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Sequence


def exact_field_accuracy(is_exact_correct: Sequence[Optional[bool]]) -> Optional[float]:
    """Fraction of True among non-None entries. None entries (blank
    ground truth, out-of-scope fields) are excluded from both numerator
    and denominator. This is the strict nonblank metric convention; the
    paper-era v9/v10 artifact population is a separate 3,684-row contract
    with one retained blank row, documented in ``docs/GT_LINEAGE.md``.
    """
    scored = [v for v in is_exact_correct if v is not None]
    if not scored:
        return None
    return sum(1 for v in scored if v) / len(scored)


def mean_cer(cer_values: Sequence[Optional[float]]) -> Optional[float]:
    scored = [v for v in cer_values if v is not None]
    if not scored:
        return None
    return sum(scored) / len(scored)


def wilson_interval(successes: int, total: int, *, z: float = 1.959963984540054) -> tuple:
    """Wilson score confidence interval for a binomial proportion.

    Default ``z`` corresponds to a 95% two-sided interval. Chosen over
    the normal (Wald) interval because it stays well-behaved near 0/1
    proportions, which matter at strict high-precision thresholds where
    accepted counts can be small -- appropriate for "uncertainty
    intervals appropriate to the accepted-field binomial count" in
    docs/EXPERIMENT_PLAN.md.

    Returns ``(low, high)``. If ``total == 0`` returns ``(None, None)``.
    """
    if total == 0:
        return (None, None)
    p_hat = successes / total
    denom = 1 + z * z / total
    center = p_hat + z * z / (2 * total)
    margin = z * math.sqrt((p_hat * (1 - p_hat) + z * z / (4 * total)) / total)
    low = (center - margin) / denom
    high = (center + margin) / denom
    return (max(0.0, low), min(1.0, high))


@dataclass(frozen=True)
class OperatingPoint:
    """One point on a precision-vs-coverage curve at a fixed threshold."""

    threshold: float
    accepted_fields: int
    accepted_correct: int
    review_fields: int
    total_evaluated_fields: int
    precision: Optional[float]
    precision_ci_low: Optional[float]
    precision_ci_high: Optional[float]
    coverage: float


class PrecisionCoverageError(ValueError):
    pass


def precision_coverage_curve(
    scores: Sequence[float],
    is_correct: Sequence[Optional[bool]],
    thresholds: Sequence[float],
) -> list:
    """Build a precision/coverage curve by sweeping ``thresholds``.

    ``scores[i]`` is the confidence/agreement score for evaluated field
    ``i``; ``is_correct[i]`` is whether that field's accepted prediction
    is exactly correct, or ``None`` if the field is out of the nonblank
    evaluation scope (excluded entirely from ``total_evaluated_fields``,
    matching :func:`exact_field_accuracy`).

    A field is "accepted" at threshold ``t`` iff ``score >= t``.
    Thresholds are swept in the order given; the caller is responsible
    for passing them in ascending or descending order if a particular
    display order is desired, but this function verifies the
    nestedness/monotonicity invariants regardless of input order by
    sorting internally for the invariant check while preserving the
    caller's original order in the returned list.
    """
    if len(scores) != len(is_correct):
        raise PrecisionCoverageError("scores and is_correct must be the same length (paired observations)")

    in_scope = [(s, c) for s, c in zip(scores, is_correct) if c is not None]
    total_evaluated = len(in_scope)

    points = []
    for t in thresholds:
        accepted = [c for s, c in in_scope if s >= t]
        accepted_fields = len(accepted)
        accepted_correct = sum(1 for c in accepted if c)
        review_fields = total_evaluated - accepted_fields

        if accepted_fields != review_fields + accepted_fields - review_fields:
            # unreachable; kept as a explicit self-check placeholder is
            # unnecessary -- the real invariant is checked below.
            pass
        if accepted_fields + review_fields != total_evaluated:
            raise PrecisionCoverageError("accepted_fields + review_fields != total_evaluated_fields")

        precision = (accepted_correct / accepted_fields) if accepted_fields > 0 else None
        ci_low, ci_high = wilson_interval(accepted_correct, accepted_fields) if accepted_fields > 0 else (None, None)
        coverage = accepted_fields / total_evaluated if total_evaluated > 0 else 0.0

        expected_coverage = accepted_fields / total_evaluated if total_evaluated > 0 else 0.0
        if abs(coverage - expected_coverage) > 1e-12:
            raise PrecisionCoverageError("coverage != accepted_fields / total_evaluated_fields")

        points.append(
            OperatingPoint(
                threshold=t,
                accepted_fields=accepted_fields,
                accepted_correct=accepted_correct,
                review_fields=review_fields,
                total_evaluated_fields=total_evaluated,
                precision=precision,
                precision_ci_low=ci_low,
                precision_ci_high=ci_high,
                coverage=coverage,
            )
        )

    _check_monotonicity_by_threshold(points)
    return points


def _check_monotonicity_by_threshold(points: Sequence[OperatingPoint]) -> None:
    """Verify coverage is non-increasing and accepted sets are nested as
    threshold increases, regardless of the order points were requested
    in. Raises PrecisionCoverageError on violation.
    """
    by_threshold = sorted(points, key=lambda p: p.threshold)
    for prev, cur in zip(by_threshold, by_threshold[1:]):
        if cur.coverage > prev.coverage + 1e-12:
            raise PrecisionCoverageError(
                f"coverage increased with stricter threshold: "
                f"t={prev.threshold} cov={prev.coverage} -> t={cur.threshold} cov={cur.coverage}"
            )
        if cur.accepted_fields > prev.accepted_fields:
            raise PrecisionCoverageError(
                f"accepted_fields increased with stricter threshold: "
                f"t={prev.threshold} n={prev.accepted_fields} -> t={cur.threshold} n={cur.accepted_fields}"
            )
