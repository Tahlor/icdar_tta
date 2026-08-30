"""Metrics: precision/coverage/correlation/uncertainty unit tests
(docs/VALIDATION_TESTS.md sections 6 and agreement-correlation checks).
"""

import unittest

from icdar_tta.agreement import (
    agreement_fraction,
    mean_pairwise_error_correlation,
    pairwise_error_correlation_summary,
    pairwise_error_indicator_correlation,
)
from icdar_tta.metrics import (
    PrecisionCoverageError,
    exact_field_accuracy,
    mean_cer,
    precision_coverage_curve,
    wilson_interval,
)


class TestExactFieldAccuracy(unittest.TestCase):
    def test_all_correct(self):
        self.assertEqual(exact_field_accuracy([True, True, True]), 1.0)

    def test_mixed(self):
        self.assertAlmostEqual(exact_field_accuracy([True, False, True, False]), 0.5)

    def test_excludes_none(self):
        self.assertEqual(exact_field_accuracy([True, None, True, None]), 1.0)

    def test_all_none_returns_none(self):
        self.assertIsNone(exact_field_accuracy([None, None]))

    def test_empty_returns_none(self):
        self.assertIsNone(exact_field_accuracy([]))


class TestMeanCer(unittest.TestCase):
    def test_basic_mean(self):
        self.assertAlmostEqual(mean_cer([0.0, 0.5, 1.0]), 0.5)

    def test_excludes_none(self):
        self.assertAlmostEqual(mean_cer([0.0, None, 1.0]), 0.5)

    def test_all_none_returns_none(self):
        self.assertIsNone(mean_cer([None, None]))


class TestWilsonInterval(unittest.TestCase):
    def test_zero_total_returns_none_none(self):
        self.assertEqual(wilson_interval(0, 0), (None, None))

    def test_perfect_score_bounded_below_one(self):
        low, high = wilson_interval(10, 10)
        self.assertLess(high, 1.0 + 1e-9)
        self.assertGreater(low, 0.0)

    def test_interval_contains_point_estimate(self):
        low, high = wilson_interval(7, 10)
        self.assertLessEqual(low, 0.7)
        self.assertGreaterEqual(high, 0.7)

    def test_wider_interval_for_smaller_sample(self):
        low_small, high_small = wilson_interval(7, 10)
        low_large, high_large = wilson_interval(700, 1000)
        self.assertGreater(high_small - low_small, high_large - low_large)


class TestPrecisionCoverageCurve(unittest.TestCase):
    def _fixture(self):
        # 10 fields; score correlates with correctness so stricter
        # thresholds should raise precision and lower coverage.
        scores = [0.9, 0.9, 0.8, 0.8, 0.6, 0.6, 0.4, 0.4, 0.2, 0.2]
        correct = [True, True, True, False, True, False, False, False, False, False]
        return scores, correct

    def test_accepted_plus_review_equals_total(self):
        scores, correct = self._fixture()
        points = precision_coverage_curve(scores, correct, thresholds=[0.9, 0.6, 0.2])
        for p in points:
            self.assertEqual(p.accepted_fields + p.review_fields, p.total_evaluated_fields)

    def test_coverage_formula(self):
        scores, correct = self._fixture()
        points = precision_coverage_curve(scores, correct, thresholds=[0.6])
        p = points[0]
        self.assertAlmostEqual(p.coverage, p.accepted_fields / p.total_evaluated_fields)

    def test_precision_formula(self):
        scores, correct = self._fixture()
        points = precision_coverage_curve(scores, correct, thresholds=[0.9])
        p = points[0]
        self.assertAlmostEqual(p.precision, p.accepted_correct / p.accepted_fields)

    def test_coverage_non_increasing_with_stricter_threshold(self):
        scores, correct = self._fixture()
        # Deliberately unordered input to prove the check is threshold-order independent.
        points = precision_coverage_curve(scores, correct, thresholds=[0.2, 0.9, 0.6, 0.4])
        by_threshold = sorted(points, key=lambda p: p.threshold)
        coverages = [p.coverage for p in by_threshold]
        self.assertEqual(coverages, sorted(coverages, reverse=True))

    def test_accepted_sets_nested_by_count(self):
        scores, correct = self._fixture()
        points = precision_coverage_curve(scores, correct, thresholds=[0.2, 0.4, 0.6, 0.8, 0.9])
        by_threshold = sorted(points, key=lambda p: p.threshold)
        counts = [p.accepted_fields for p in by_threshold]
        for prev, cur in zip(counts, counts[1:]):
            self.assertLessEqual(cur, prev)

    def test_excludes_out_of_scope_none_fields(self):
        scores = [0.9, 0.9, 0.5]
        correct = [True, True, None]  # third field has blank ground truth
        points = precision_coverage_curve(scores, correct, thresholds=[0.5])
        self.assertEqual(points[0].total_evaluated_fields, 2)

    def test_precision_none_when_nothing_accepted(self):
        scores = [0.1, 0.1]
        correct = [True, False]
        points = precision_coverage_curve(scores, correct, thresholds=[0.99])
        self.assertIsNone(points[0].precision)
        self.assertEqual(points[0].accepted_fields, 0)

    def test_mismatched_lengths_raises(self):
        with self.assertRaises(PrecisionCoverageError):
            precision_coverage_curve([0.5, 0.6], [True], thresholds=[0.5])

    def test_confidence_interval_present_when_accepted(self):
        scores, correct = self._fixture()
        points = precision_coverage_curve(scores, correct, thresholds=[0.6])
        p = points[0]
        self.assertIsNotNone(p.precision_ci_low)
        self.assertIsNotNone(p.precision_ci_high)
        self.assertLessEqual(p.precision_ci_low, p.precision)
        self.assertGreaterEqual(p.precision_ci_high, p.precision)


class TestPairwiseErrorCorrelation(unittest.TestCase):
    def test_perfectly_correlated_errors(self):
        errors_a = [True, False, True, False]
        errors_b = [True, False, True, False]
        self.assertAlmostEqual(pairwise_error_indicator_correlation(errors_a, errors_b), 1.0)

    def test_perfectly_anticorrelated_errors(self):
        errors_a = [True, False, True, False]
        errors_b = [False, True, False, True]
        self.assertAlmostEqual(pairwise_error_indicator_correlation(errors_a, errors_b), -1.0)

    def test_zero_variance_returns_none(self):
        errors_a = [True, True, True]
        errors_b = [True, False, True]
        self.assertIsNone(pairwise_error_indicator_correlation(errors_a, errors_b))

    def test_mismatched_length_raises(self):
        with self.assertRaises(ValueError):
            pairwise_error_indicator_correlation([True], [True, False])

    def test_mean_pairwise_correlation_across_samples(self):
        matrix = [
            [True, False, True, False],
            [True, False, True, False],
            [False, True, False, True],
        ]
        mean_corr = mean_pairwise_error_correlation(matrix)
        self.assertIsNotNone(mean_corr)

    def test_summary_reports_undefined_pair_counts(self):
        matrix = [
            [True, True, True],  # zero variance
            [True, False, True],
            [False, True, False],
        ]
        summary = pairwise_error_correlation_summary(matrix)
        self.assertGreaterEqual(summary.n_pairs_undefined, 1)
        self.assertEqual(summary.n_pairs_used + summary.n_pairs_undefined, 3)  # 3 choose 2


class TestAgreementFraction(unittest.TestCase):
    def test_unanimous(self):
        self.assertEqual(agreement_fraction(["Mary", "Mary", "Mary"]), 1.0)

    def test_majority(self):
        self.assertAlmostEqual(agreement_fraction(["Mary", "Mary", "Mray"]), 2 / 3)

    def test_excludes_none(self):
        self.assertEqual(agreement_fraction(["Mary", None, "Mary"]), 1.0)

    def test_all_none_returns_none(self):
        self.assertIsNone(agreement_fraction([None, None]))


if __name__ == "__main__":
    unittest.main()
