"""Consensus/alignment unit tests (docs/VALIDATION_TESTS.md section 3)."""

import unittest

from icdar_tta.alignment import GAP, needleman_wunsch
from icdar_tta.consensus import progressive_consensus


class TestNeedlemanWunsch(unittest.TestCase):
    def test_identical_strings_align_with_no_gaps(self):
        result = needleman_wunsch("mary", "mary")
        self.assertEqual(result.aligned_a, tuple("mary"))
        self.assertEqual(result.aligned_b, tuple("mary"))
        self.assertNotIn(GAP, result.aligned_a)
        self.assertNotIn(GAP, result.aligned_b)

    def test_single_substitution(self):
        result = needleman_wunsch("mary", "mray")
        # Hand-checkable: m-a-r-y vs m-r-a-y is two substitutions under a
        # simple linear-gap global alignment scoring scheme, or a single
        # insertion+deletion depending on tie-breaking; verify the
        # alignment reconstructs to the original strings when gaps removed.
        reconstructed_a = "".join(c for c in result.aligned_a if c is not None)
        reconstructed_b = "".join(c for c in result.aligned_b if c is not None)
        self.assertEqual(reconstructed_a, "mary")
        self.assertEqual(reconstructed_b, "mray")
        self.assertEqual(len(result.aligned_a), len(result.aligned_b))

    def test_insertion_produces_gap_in_shorter_string(self):
        result = needleman_wunsch("mary", "marry")
        self.assertEqual(len(result), len(result.aligned_b))
        self.assertIn(GAP, result.aligned_a)

    def test_empty_string_against_nonempty(self):
        result = needleman_wunsch("", "mary")
        self.assertEqual(result.aligned_a, (GAP, GAP, GAP, GAP))
        self.assertEqual(result.aligned_b, tuple("mary"))

    def test_deterministic_repeat_calls(self):
        r1 = needleman_wunsch("mary", "mray")
        r2 = needleman_wunsch("mary", "mray")
        self.assertEqual(r1.aligned_a, r2.aligned_a)
        self.assertEqual(r1.aligned_b, r2.aligned_b)
        self.assertEqual(r1.score, r2.score)


class TestProgressiveConsensus(unittest.TestCase):
    def test_single_sample_is_its_own_consensus(self):
        result = progressive_consensus(["Mary"])
        self.assertEqual(result.consensus_text, "Mary")
        self.assertEqual(result.n_valid_samples, 1)
        self.assertEqual(result.n_missing_samples, 0)

    def test_unanimous_samples_full_confidence(self):
        result = progressive_consensus(["Mary", "Mary", "Mary"])
        self.assertEqual(result.consensus_text, "Mary")
        self.assertEqual(result.field_confidence, 1.0)
        self.assertTrue(all(v == 1.0 for v in result.char_vote_fractions))

    def test_majority_wins_over_minority_typo(self):
        # Two agree on "Mary", one has a substitution typo "Mray".
        result = progressive_consensus(["Mary", "Mary", "Mray"])
        self.assertEqual(result.consensus_text, "Mary")

    def test_missing_samples_counted_and_excluded_from_voting(self):
        result = progressive_consensus(["Mary", None, "Mary", None])
        self.assertEqual(result.n_valid_samples, 2)
        self.assertEqual(result.n_missing_samples, 2)
        self.assertEqual(result.consensus_text, "Mary")

    def test_all_missing_returns_empty_consensus_explicitly(self):
        result = progressive_consensus([None, None])
        self.assertEqual(result.consensus_text, "")
        self.assertEqual(result.n_valid_samples, 0)
        self.assertEqual(result.n_missing_samples, 2)
        self.assertEqual(result.field_confidence, 0.0)

    def test_empty_sample_list(self):
        result = progressive_consensus([])
        self.assertEqual(result.consensus_text, "")
        self.assertEqual(result.n_valid_samples, 0)
        self.assertEqual(result.n_missing_samples, 0)

    def test_deterministic_across_repeated_runs(self):
        samples = ["Mary", "Mray", "Mary", "Marry", "Mary"]
        r1 = progressive_consensus(samples)
        r2 = progressive_consensus(samples)
        self.assertEqual(r1.consensus_text, r2.consensus_text)
        self.assertEqual(r1.char_vote_fractions, r2.char_vote_fractions)

    def test_order_sensitivity_is_not_assumed_invariant(self):
        # Per docs/VALIDATION_TESTS.md: do not assert order-invariance.
        # This test documents that different orders CAN legitimately
        # produce different consensus text; it does not assert equality.
        forward = progressive_consensus(["Mary", "Mray", "Marry"])
        reversed_order = progressive_consensus(["Marry", "Mray", "Mary"])
        # Both must still be valid, non-empty consensus outputs.
        self.assertTrue(len(forward.consensus_text) > 0)
        self.assertTrue(len(reversed_order.consensus_text) > 0)

    def test_char_vote_fractions_length_matches_consensus_length(self):
        result = progressive_consensus(["Mary", "Mray"])
        self.assertEqual(len(result.char_vote_fractions), len(result.consensus_text))


if __name__ == "__main__":
    unittest.main()
