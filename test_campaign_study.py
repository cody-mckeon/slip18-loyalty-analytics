import math
import unittest
from campaign_study import (historical_customers, create_plan, conduct, HISTORICAL_N,
                            MDE, ELIGIBLE_POPULATION)

class CampaignStudyTests(unittest.TestCase):
    def test_historical_reproducible_and_no_offer(self):
        a=list(historical_customers(seed=7,count=100))
        self.assertEqual(a, list(historical_customers(seed=7,count=100)))
        self.assertEqual(len(a),100)
        self.assertTrue(all(r[2]>=0 and math.isfinite(r[3]) for r in a))
    def test_planning_independent_and_economically_defined(self):
        history=list(historical_customers(seed=22,count=2000))
        p=create_plan(history)
        self.assertEqual(p['preperiod_n'],2000)
        self.assertGreater(p['preperiod_sd'],0)
        self.assertEqual(MDE,10)
        self.assertEqual(p['plan']['total'],p['plan']['control']+p['plan']['treatment'])
    def test_rollout_cannot_exceed_eligibility(self):
        p=create_plan([(i,'regular',1,(10000 if i%2 else 0)) for i in range(100)])
        self.assertFalse(p['feasible'])
        self.assertGreater(p['plan']['total'],ELIGIBLE_POPULATION)
    def test_prospective_has_both_arms_and_results(self):
        p=create_plan(list(historical_customers(seed=3,count=2000)))
        if p['feasible']:
            r=conduct(p)
            self.assertTrue(r['checks']['passed'])
            self.assertEqual(r['groups']['0']['assigned'],r['groups']['1']['assigned'])
            self.assertAlmostEqual(r['groups']['1']['net_profit_per_customer']-r['groups']['0']['net_profit_per_customer'],r['effect'])
            self.assertLess(r['lower_95'],r['upper_95'])

if __name__=='__main__': unittest.main()