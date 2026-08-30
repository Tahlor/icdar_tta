"""Agreement and pairwise error-correlation utilities.

Per the top-level ``README.md`` core claims: "Ensemble value depends on
both member accuracy and error correlation; ten copies of the same
mistake are effectively one opinion." This module computes the
error-correlation statistics needed to test that claim, matching the
paper-era reference values it must be checked against
(Grid-Warp 0.575, Resize 0.973) in ``docs/EXPERIMENT_PLAN.md``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Sequence


def pairwise_error_indicator_correlation(
    errors_a: Sequence[bool], errors_b: Sequence[bool]
) -> Optional[float]:
    """Pearson correlation between two aligned boolean error-indicator
    sequences (True = incorrect on that field/sample).

    Returns ``None`` when either sequence has zero variance (all-correct
    or all-incorrect), since correlation is undefined there rather than
    spuriously 0 or 1.
    """
    if len(errors_a) != len(errors_b):
        raise ValueError("errors_a and errors_b must be the same length (paired observations)")
    n = len(errors_a)
    if n == 0:
        return None

    xa = [1.0 if e else 0.0 for e in errors_a]
    xb = [1.0 if e else 0.0 for e in errors_b]
    mean_a = sum(xa) / n
    mean_b = sum(xb) / n

    var_a = sum((x - mean_a) ** 2 for x in xa)
    var_b = sum((x - mean_b) ** 2 for x in xb)
    if var_a == 0 or var_b == 0:
        return None

    cov = sum((a - mean_a) * (b - mean_b) for a, b in zip(xa, xb))
    return cov / math.sqrt(var_a * var_b)


def mean_pairwise_error_correlation(sample_error_matrix: Sequence[Sequence[bool]]) -> Optional[float]:
    """Mean of all pairwise correlations across samples.

    ``sample_error_matrix[k]`` is the error-indicator sequence (over
    fields/documents) for sample ``k``. Pairs with an undefined
    correlation (returned as ``None`` by
    :func:`pairwise_error_indicator_correlation`) are excluded from the
    mean rather than treated as zero, and the exclusion count is not
    silently hidden -- callers needing that count should call
    :func:`pairwise_error_correlation_summary` instead.
    """
    summary = pairwise_error_correlation_summary(sample_error_matrix)
    return summary.mean_correlation


@dataclass(frozen=True)
class PairwiseCorrelationSummary:
    mean_correlation: Optional[float]
    n_pairs_used: int
    n_pairs_undefined: int


def pairwise_error_correlation_summary(
    sample_error_matrix: Sequence[Sequence[bool]]
) -> PairwiseCorrelationSummary:
    k = len(sample_error_matrix)
    correlations = []
    undefined = 0
    for i in range(k):
        for j in range(i + 1, k):
            corr = pairwise_error_indicator_correlation(sample_error_matrix[i], sample_error_matrix[j])
            if corr is None:
                undefined += 1
            else:
                correlations.append(corr)
    mean_corr = (sum(correlations) / len(correlations)) if correlations else None
    return PairwiseCorrelationSummary(
        mean_correlation=mean_corr, n_pairs_used=len(correlations), n_pairs_undefined=undefined
    )


def agreement_fraction(values: Sequence[Optional[str]]) -> Optional[float]:
    """Fraction of non-missing values equal to the majority value.

    A simple, transparent raw-agreement score usable as an input to the
    precision/coverage sweep in :mod:`icdar_tta.metrics`. Per
    ``docs/EXPERIMENT_PLAN.md``, this is *raw agreement*, not a
    calibrated probability -- callers must not relabel this output as
    calibrated.
    """
    present = [v for v in values if v is not None]
    if not present:
        return None
    counts: dict = {}
    for v in present:
        counts[v] = counts.get(v, 0) + 1
    majority_count = max(counts.values())
    return majority_count / len(present)
