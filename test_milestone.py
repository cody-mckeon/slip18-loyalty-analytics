import math
import unittest
from baseline import generate
from experiment_validation import validate
from power_analysis import plan

class PowerTests(unittest.TestCase):
    def test_reference_normal_approximation(self):
        # Formula independent check: sd=100, MDE=10, alpha=.05, power=.80;
        # 2*(1.95996+.84162)^2 * 100^2/10^2 ~= 1569.78 / arm
        x=plan(10,100)
        self.assertEqual(x['control'],1570)
        self.assertEqual(x['treatment'],1570)
        self.assertEqual(x['total'],3140)
    def test_monotonicity(self):
        self.assertGreater(plan(5,100)['total'],plan(10,100)['total'])
        self.assertGreater(plan(10,200)['total'],plan(10,100)['total'])
        self.assertGreater(plan(10,100,power=.9)['total'],plan(10,100,power=.8)['total'])
        self.assertGreater(plan(10,100,alpha=.01)['total'],plan(10,100,alpha=.05)['total'])
    def test_validation_of_arguments(self):
        for args in [dict(mde=0,sd=100),dict(mde=10,sd=0),dict(mde=10,sd=100,power=1),dict(mde=10,sd=100,alpha=0),dict(mde=10,sd=100,treatment_to_control=-2),dict(mde=float('nan'),sd=100)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                plan(**args)
    def test_unequal_allocation(self):
        r=plan(10,100,treatment_to_control=2)
        self.assertEqual(r['treatment'],r['control']*2)

class ExperimentIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.rows=list(generate(seed=42,size=1000))
    def test_generated_cohort_passes(self):
        x=validate(self.rows,expected_count=1000)
        self.assertTrue(x['passed'],x)
        self.assertEqual((x['treatment'],x['control']),(500,500))
    def test_unsorted_input_passes(self):
        x=validate(list(reversed(self.rows)),expected_count=1000)
        self.assertTrue(x['passed'],x)
    def test_duplicate_and_missing_row(self):
        modified=self.rows[:-1]+[self.rows[0]]
        x=validate(modified,expected_count=1000)
        self.assertFalse(x['passed'])
        self.assertTrue(any('duplicate' in error for error in x['errors']))
    def test_invalid_redemption(self):
        rows=[(1,'regular',0,1,10000,1000,1),(2,'regular',1,0,0,0,0)]
        self.assertFalse(validate(rows)['passed'])
    def test_bad_no_visit_outcome(self):
        rows=[(1,'regular',0,0,500,0,0),(2,'regular',1,0,0,0,0)]
        self.assertFalse(validate(rows)['passed'])
    def test_sample_ratio_mismatch_warning(self):
        rows=[(i,'regular',1 if i<=90 else 0,0,0,0,0) for i in range(1,101)]
        x=validate(rows,expected_count=100)
        self.assertTrue(x['passed'])
        self.assertTrue(any('ratio' in w for w in x['warnings']))
    def test_missing_count(self):
        x=validate(self.rows,expected_count=1001)
        self.assertFalse(x['passed'])

if __name__=='__main__':
    unittest.main()