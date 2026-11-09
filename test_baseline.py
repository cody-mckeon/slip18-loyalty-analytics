import sqlite3
import unittest
from collections import Counter

from baseline import estimate, generate, score


class BaselineTests(unittest.TestCase):
    def test_generator_is_reproducible_and_balanced(self):
        rows = list(generate(seed=42, size=1000))
        self.assertEqual(rows, list(generate(seed=42, size=1000)))
        self.assertEqual(Counter(row[2] for row in rows), {0: 500, 1: 500})
        self.assertEqual(len(score(rows)), len(rows))

    def test_sql_costs_and_all_assigned_denominator(self):
        rows = score([
            (1, "regular", 0, 1, 8000, 3000, 0),
            (2, "regular", 0, 0, 0, 0, 0),
            (3, "regular", 1, 1, 12000, 3000, 1),
            (4, "regular", 1, 0, 0, 0, 0),
        ])
        self.assertEqual([row["net_cents"] for row in rows], [5000, 0, 3975, -25])
        self.assertAlmostEqual(estimate(rows)[0], -5.25)
        self.assertAlmostEqual(estimate(rows, redemption_cost=35)[0], 2.25)

    def test_reject_invalid_records(self):
        invalid = [
            [(1, "regular", 0, 1, 8000, 3000, 1)],
            [(1, "regular", 1, 0, 8000, 3000, 0)],
            [(1, "regular", 0, 0, 0, 0, 0)] * 2,
        ]
        for rows in invalid:
            with self.subTest(rows=rows), self.assertRaises(sqlite3.IntegrityError):
                score(rows)

    def test_inference_matches_hand_calculation(self):
        rows = [
            dict(treatment=arm, net_cents=cents, redeemed=0)
            for arm, cents in [(0, 0), (0, 200), (1, 200), (1, 400)]
        ]
        effect, low, high, p_value = estimate(rows)
        self.assertEqual(effect, 2)
        self.assertAlmostEqual(high - effect, 2.77180765)
        self.assertAlmostEqual(effect - low, 2.77180765)
        self.assertAlmostEqual(p_value, 0.15729921)
        adjusted = estimate(rows, alpha=0.05 / 3)
        self.assertGreater(adjusted[2], high)

    def test_reject_missing_arm(self):
        with self.assertRaises(ValueError):
            estimate(score([(1, "regular", 0, 0, 0, 0, 0)]))


if __name__ == "__main__":
    unittest.main()