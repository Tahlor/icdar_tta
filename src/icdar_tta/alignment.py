"""Pairwise sequence alignment (Needleman-Wunsch) used by progressive consensus.

Per ``docs/VALIDATION_TESTS.md`` ("Consensus/alignment unit tests"), this
module must be independently verifiable against hand-checkable string
sets and must implement standard global-alignment scoring and gap
handling, character-level (not word-level), since name fields are short
strings where character-level voting is the meaningful unit.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

GAP = None  # sentinel representing an alignment gap


@dataclass(frozen=True)
class AlignmentResult:
    """Aligned character sequences, same length, gaps as ``None``."""

    aligned_a: tuple
    aligned_b: tuple
    score: int

    def __len__(self) -> int:
        return len(self.aligned_a)


def needleman_wunsch(
    a: str,
    b: str,
    *,
    match_score: int = 2,
    mismatch_score: int = -1,
    gap_penalty: int = -1,
) -> AlignmentResult:
    """Classic global alignment with linear gap penalty.

    Ties are broken deterministically in a fixed priority order
    (diagonal/match-or-mismatch, then up/gap-in-b, then left/gap-in-a) so
    that repeated calls on the same input always produce the same
    alignment, which downstream progressive consensus depends on for
    determinism.
    """
    n, m = len(a), len(b)
    score = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        score[i][0] = i * gap_penalty
    for j in range(1, m + 1):
        score[0][j] = j * gap_penalty

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            diag = score[i - 1][j - 1] + (match_score if a[i - 1] == b[j - 1] else mismatch_score)
            up = score[i - 1][j] + gap_penalty
            left = score[i][j - 1] + gap_penalty
            score[i][j] = max(diag, up, left)

    aligned_a: list = []
    aligned_b: list = []
    i, j = n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0:
            diag = score[i - 1][j - 1] + (match_score if a[i - 1] == b[j - 1] else mismatch_score)
        else:
            diag = None
        if diag is not None and score[i][j] == diag:
            aligned_a.append(a[i - 1])
            aligned_b.append(b[j - 1])
            i -= 1
            j -= 1
        elif i > 0 and score[i][j] == score[i - 1][j] + gap_penalty:
            aligned_a.append(a[i - 1])
            aligned_b.append(GAP)
            i -= 1
        else:
            aligned_a.append(GAP)
            aligned_b.append(b[j - 1])
            j -= 1

    aligned_a.reverse()
    aligned_b.reverse()
    return AlignmentResult(aligned_a=tuple(aligned_a), aligned_b=tuple(aligned_b), score=score[n][m])
