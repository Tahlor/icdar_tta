"""Normalization/CER unit tests (docs/VALIDATION_TESTS.md section 2)."""

import unittest

from icdar_tta.normalize import (
    character_error_rate,
    is_blank,
    is_exact_match,
    levenshtein_distance,
    normalize_field,
)


class TestBlankHandling(unittest.TestCase):
    def test_none_is_blank(self):
        self.assertTrue(is_blank(None))

    def test_empty_string_is_blank(self):
        self.assertTrue(is_blank(""))

    def test_whitespace_only_is_blank(self):
        self.assertTrue(is_blank("   \t  "))

    def test_nonblank_value(self):
        self.assertFalse(is_blank("Mary"))

    def test_normalize_field_blank_returns_none(self):
        self.assertIsNone(normalize_field(None))
        self.assertIsNone(normalize_field(""))
        self.assertIsNone(normalize_field("   "))


class TestCaseInsensitivity(unittest.TestCase):
    def test_case_insensitive_match(self):
        self.assertEqual(normalize_field("MARY"), normalize_field("mary"))
        self.assertTrue(is_exact_match("MARY", "mary"))

    def test_mixed_case_surname(self):
        self.assertEqual(normalize_field("McDonald"), normalize_field("MCDONALD"))


class TestPunctuationAndSpacing(unittest.TestCase):
    def test_strips_documented_punctuation(self):
        self.assertEqual(normalize_field("Mary."), "mary")
        self.assertEqual(normalize_field("Smith, Jr."), "smith jr")

    def test_preserves_hyphen_and_apostrophe(self):
        # Documented default: hyphens/apostrophes are meaningful in PA
        # surnames and are not stripped.
        self.assertEqual(normalize_field("O'Brien"), "o'brien")
        self.assertEqual(normalize_field("Smith-Jones"), "smith-jones")

    def test_collapses_internal_whitespace(self):
        self.assertEqual(normalize_field("Mary   Ann"), "mary ann")

    def test_strips_leading_trailing_whitespace(self):
        self.assertEqual(normalize_field("  Mary  "), "mary")


class TestUnicodeNormalization(unittest.TestCase):
    def test_nfkc_equivalent_forms_match(self):
        # "e" + combining acute accent vs precomposed "é"
        combining = "Rene\u0301"
        precomposed = "René"
        self.assertEqual(normalize_field(combining), normalize_field(precomposed))


class TestExactMatch(unittest.TestCase):
    def test_blank_ground_truth_returns_none_not_false(self):
        self.assertIsNone(is_exact_match("Mary", None))
        self.assertIsNone(is_exact_match("Mary", ""))

    def test_blank_prediction_nonblank_gt_is_false(self):
        self.assertFalse(is_exact_match(None, "Mary"))

    def test_exact_mismatch(self):
        self.assertFalse(is_exact_match("Mray", "Mary"))


class TestLevenshteinDistance(unittest.TestCase):
    def test_identical_strings(self):
        self.assertEqual(levenshtein_distance("mary", "mary"), 0)

    def test_empty_vs_nonempty(self):
        self.assertEqual(levenshtein_distance("", "mary"), 4)
        self.assertEqual(levenshtein_distance("mary", ""), 4)

    def test_single_substitution(self):
        self.assertEqual(levenshtein_distance("mary", "mray"), 2)

    def test_single_insertion(self):
        self.assertEqual(levenshtein_distance("mary", "marry"), 1)

    def test_single_deletion(self):
        self.assertEqual(levenshtein_distance("marry", "mary"), 1)

    def test_classic_kitten_sitting(self):
        self.assertEqual(levenshtein_distance("kitten", "sitting"), 3)


class TestCharacterErrorRate(unittest.TestCase):
    def test_perfect_match_is_zero(self):
        self.assertEqual(character_error_rate("Mary", "Mary"), 0.0)

    def test_blank_ground_truth_is_none(self):
        self.assertIsNone(character_error_rate("Mary", None))
        self.assertIsNone(character_error_rate("Mary", ""))

    def test_blank_prediction_nonblank_gt(self):
        # Fully missing prediction against a 4-char ground truth: CER 1.0
        self.assertEqual(character_error_rate(None, "Mary"), 1.0)

    def test_one_substitution_over_four_chars(self):
        self.assertAlmostEqual(character_error_rate("Mray", "Mary"), 2 / 4)

    def test_case_insensitive_by_default(self):
        self.assertEqual(character_error_rate("MARY", "mary"), 0.0)

    def test_unnormalized_mode_is_case_sensitive(self):
        cer = character_error_rate("MARY", "mary", normalized=False)
        self.assertGreater(cer, 0.0)


if __name__ == "__main__":
    unittest.main()
