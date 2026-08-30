"""Deterministic progressive consensus over repeated/augmented samples.

Per ``docs/VALIDATION_TESTS.md``:

- "progressive consensus output under the canonical deterministic sample
  order" — this module builds consensus by folding samples in a caller-
  supplied, fixed order (typically ``sample_index`` ascending); it never
  reorders samples internally.
- "per-character vote fractions" and "word/field confidence aggregation"
  are exposed as explicit outputs, not derived ad hoc downstream.
- "deterministic behavior across repeated runs" — no randomness is used
  anywhere in this module.
- "missing/failed sample behavior is explicit rather than silently
  treated as agreement" — ``None``/failed samples are excluded from
  voting and counted separately, never coerced to an empty-string vote
  that would spuriously agree with other empty predictions.
- "Do not assert order-invariance unless the actual consensus algorithm
  is proven order-invariant; progressive consensus can be order-
  sensitive." This implementation is explicitly order-sensitive (each
  new sample is aligned against the *current* consensus string, not
  against all prior samples jointly), and is documented as such rather
  than asserted invariant.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Optional, Sequence

from icdar_tta.alignment import GAP, needleman_wunsch


@dataclass(frozen=True)
class ConsensusResult:
    """Result of progressive consensus over one field's sample sequence.

    Attributes:
        consensus_text: The majority-vote consensus string.
        n_valid_samples: Count of non-``None`` samples that contributed.
        n_missing_samples: Count of ``None``/excluded samples.
        char_vote_fractions: Per consensus-character vote fraction, i.e.
            the fraction of contributing samples whose aligned character
            at that position matched the consensus character. Length
            equals ``len(consensus_text)``.
        field_confidence: Mean of ``char_vote_fractions`` (0.0 if the
            consensus string is empty), a simple field-level aggregate.
    """

    consensus_text: str
    n_valid_samples: int
    n_missing_samples: int
    char_vote_fractions: tuple
    field_confidence: float


def _votes_at_position(aligned_consensus: Sequence, aligned_sample: Sequence) -> list:
    """Character-level votes: 1.0 if the aligned sample char matches the
    aligned consensus char at that position, else 0.0. A gap in the
    sample (missing character) counts as a non-match, not an omission,
    since progressive consensus must resolve one fixed-length output
    string.
    """
    votes = []
    for c_char, s_char in zip(aligned_consensus, aligned_sample):
        votes.append(1.0 if (c_char is not None and c_char == s_char) else 0.0)
    return votes


def _mode(tokens: Sequence[Optional[str]], previous: Optional[str]) -> Optional[str]:
    """Return a deterministic mode, retaining ``previous`` on a tie."""
    counts = Counter(tokens)
    if not counts:
        return previous
    maximum = max(counts.values())
    candidates = [token for token, count in counts.items() if count == maximum]
    if previous in candidates:
        return previous
    return sorted(candidates, key=lambda token: (token is not None, token or ""))[0]


def _representative(tokens: Sequence[Optional[str]], previous: Optional[str]) -> Optional[str]:
    """Choose a character for aligning a later sample to this column.

    A column whose gap is currently the mode still needs a representative
    character so later samples can revisit the same insertion/deletion
    position and potentially reverse that decision.
    """
    characters = [token for token in tokens if token is not None]
    if not characters:
        return None
    return _mode(characters, previous if previous is not None else characters[0])


def _legacy_progressive_consensus(
    samples: Sequence[Optional[str]],
    *,
    match_score: int = 2,
    mismatch_score: int = -1,
    gap_penalty: int = -1,
) -> ConsensusResult:
    """Fold ``samples`` in the given order into one consensus string.

    ``samples`` should already be in the canonical deterministic order
    (e.g. ascending ``sample_index``); this function does not sort or
    shuffle its input.

    Algorithm: start from the first valid sample as the initial
    consensus. For each subsequent valid sample, align it against the
    *current* consensus string with Needleman-Wunsch, then at each
    aligned position pick the majority character seen so far
    (consensus wins ties, preserving the existing consensus over a
    single dissenting new sample) to form the next consensus string.
    Per-position vote tallies are carried forward so
    ``char_vote_fractions`` reflects the full accumulated history, not
    just the last comparison.
    """
    valid = [s for s in samples if s is not None]
    n_missing = len(samples) - len(valid)

    if not valid:
        return ConsensusResult(
            consensus_text="",
            n_valid_samples=0,
            n_missing_samples=n_missing,
            char_vote_fractions=tuple(),
            field_confidence=0.0,
        )

    consensus = list(valid[0])
    # match_votes[i] = number of contributing samples whose aligned char
    # at consensus position i matched the consensus char at that time.
    match_votes = [1] * len(consensus)
    total_votes = [1] * len(consensus)
    # samples_processed tracks how many valid samples have had a chance
    # to vote so far (including the seed sample). A brand-new inserted
    # character has only been "seen" by one sample; it must not be
    # promoted into the permanent consensus unless it goes on to win
    # majority support among the samples that have since had a chance to
    # agree/disagree with it, otherwise a single dissenting sample could
    # inject an insertion that silently outvotes the true majority
    # (see tests/test_consensus_alignment.py::test_majority_wins_over_minority_typo).
    samples_processed = 1

    for sample in valid[1:]:
        aligned = needleman_wunsch(
            "".join(consensus),
            sample,
            match_score=match_score,
            mismatch_score=mismatch_score,
            gap_penalty=gap_penalty,
        )
        new_consensus: list = []
        new_match_votes: list = []
        new_total_votes: list = []

        # Walk the alignment, carrying forward per-old-position vote
        # counts and provisionally admitting new positions for
        # sample-only gaps (insertions), which are only kept if they end
        # up with majority support among samples that had a chance to
        # vote on them.
        old_pos = 0
        for c_char, s_char in zip(aligned.aligned_a, aligned.aligned_b):
            if c_char is not None:
                # Existing consensus position (possibly with a gap in sample).
                votes_here = match_votes[old_pos]
                total_here = total_votes[old_pos]
                if s_char is not None:
                    total_here += 1
                    if s_char == c_char:
                        votes_here += 1
                new_consensus.append(c_char)
                new_match_votes.append(votes_here)
                new_total_votes.append(total_here)
                old_pos += 1
            else:
                # Sample introduced a character with no consensus
                # counterpart (insertion candidate). It has been seen by
                # exactly 1 of `samples_processed + 1` samples so far
                # (this sample is the first to propose it). Reject it
                # unless a strict majority of samples-that-could-have-
                # voted support it; a single proposal among >= 2 total
                # samples is a minority and must not silently become
                # consensus.
                total_here = samples_processed + 1
                votes_here = 1
                if votes_here * 2 > total_here:
                    new_consensus.append(s_char)
                    new_match_votes.append(votes_here)
                    new_total_votes.append(total_here)
                # else: drop the minority-supported insertion entirely.

        consensus = new_consensus
        match_votes = new_match_votes
        total_votes = new_total_votes
        samples_processed += 1

    char_vote_fractions = tuple(
        (mv / tv if tv > 0 else 0.0) for mv, tv in zip(match_votes, total_votes)
    )
    field_confidence = (sum(char_vote_fractions) / len(char_vote_fractions)) if char_vote_fractions else 0.0

    return ConsensusResult(
        consensus_text="".join(consensus),
        n_valid_samples=len(valid),
        n_missing_samples=n_missing,
        char_vote_fractions=char_vote_fractions,
        field_confidence=field_confidence,
    )


def progressive_consensus(
    samples: Sequence[Optional[str]],
    *,
    match_score: int = 2,
    mismatch_score: int = -1,
    gap_penalty: int = -1,
) -> ConsensusResult:
    """Fold samples in the supplied order into a profile consensus.

    ``None`` samples are unavailable observations and are excluded from the
    alignment profile, but are counted in ``n_missing_samples``. Every valid
    sample contributes a token (including alignment gaps) to each profile
    column. The column mode is the consensus, so substitutions, insertions,
    and deletions can all be resolved by later majority votes.
    """
    valid = [sample for sample in samples if sample is not None]
    n_missing = len(samples) - len(valid)
    if not valid:
        return ConsensusResult("", 0, n_missing, tuple(), 0.0)

    # Each column stores one token per valid sample. None is an alignment gap
    # here; unavailable samples were removed above.
    columns: list[list[Optional[str]]] = [[character] for character in valid[0]]
    consensus_tokens: list[Optional[str]] = list(valid[0])
    processed = 1

    for sample in valid[1:]:
        # Keep a representative character even when a gap is currently the
        # column mode. This preserves insertion/deletion positions for later
        # samples that may reverse the majority.
        representatives = [
            _representative(column, consensus_tokens[index])
            for index, column in enumerate(columns)
        ]
        active = [
            (index, character)
            for index, character in enumerate(representatives)
            if character is not None
        ]
        aligned = needleman_wunsch(
            "".join(character for _, character in active),
            sample,
            match_score=match_score,
            mismatch_score=mismatch_score,
            gap_penalty=gap_penalty,
        )

        active_position = 0
        new_columns: list[list[Optional[str]]] = []
        new_tokens: list[Optional[str]] = []
        for old_character, sample_character in zip(aligned.aligned_a, aligned.aligned_b):
            if old_character is GAP:
                # A sample-only insertion: prior samples vote for a gap.
                new_columns.append([None] * processed + [sample_character])
                new_tokens.append(None)
                continue

            old_index = active[active_position][0]
            active_position += 1
            column = list(columns[old_index])
            column.append(sample_character)
            new_columns.append(column)
            new_tokens.append(_mode(column, consensus_tokens[old_index]))

        if active_position != len(active):
            raise AssertionError("alignment did not consume every profile column")
        columns = new_columns
        consensus_tokens = new_tokens
        processed += 1

    final_tokens: list[Optional[str]] = []
    char_vote_fractions: list[float] = []
    for column, previous in zip(columns, consensus_tokens):
        winner = _mode(column, previous)
        final_tokens.append(winner)
        if winner is not None:
            # Alignment gaps in a valid sample are disagreement with a
            # character winner. Whole-sample availability is handled by the
            # caller using n_valid_samples/n_missing_samples.
            char_vote_fractions.append(sum(token == winner for token in column) / len(valid))

    consensus_text = "".join(token for token in final_tokens if token is not None)
    field_confidence = sum(char_vote_fractions) / len(char_vote_fractions) if char_vote_fractions else 0.0
    return ConsensusResult(
        consensus_text=consensus_text,
        n_valid_samples=len(valid),
        n_missing_samples=n_missing,
        char_vote_fractions=tuple(char_vote_fractions),
        field_confidence=field_confidence,
    )
