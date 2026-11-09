import tempfile
import unittest
from pathlib import Path
from offer_optimization import (SEGMENTS, OFFERS, make_training, learn_policy, evaluate, summarize, run, compare)

class OfferTests(unittest.TestCase):
    def test_reproducibility_and_balanced_training(self):
        rows=make_training(seed=99,n=1200)
        self.assertEqual(rows,make_training(seed=99,n=1200))
        self.assertEqual({o:sum(r['offer']==o for r in rows) for o in OFFERS},{o:300 for o in OFFERS})
    def test_no_offer_has_no_redemption_or_contact_charge(self):
        rows=make_training(seed=3,n=1200)
        for r in rows:
            if r['offer']==0:
                self.assertEqual(r['redeemed'],0)
                if r['visits']==0:self.assertEqual(r['net_profit'],0)
    def test_policy_is_pre_treatment_and_from_training(self):
        train=make_training(seed=4,n=4800)
        policy,_=learn_policy(train)
        self.assertEqual(set(policy),set(SEGMENTS))
        self.assertTrue(set(policy.values()).issubset(OFFERS))
    def test_eval_random_group_counts_and_fixed_baselines(self):
        policy={s:25 for s in SEGMENTS}
        rows=evaluate(10,900,policy)
        self.assertEqual({g:sum(r['assignment']==g for r in rows) for g in ('personalized','blanket_50','no_offer')}, {'personalized':300,'blanket_50':300,'no_offer':300})
        for r in rows:
            if r['assignment']=='no_offer':self.assertEqual(r['offer'],0)
            if r['assignment']=='blanket_50':self.assertEqual(r['offer'],50)
            if r['assignment']=='personalized':self.assertEqual(r['offer'],25)
        result=summarize(rows)
        self.assertEqual(result['groups']['personalized']['n'],300)
    def test_known_comparison(self):
        x=compare([10,20,30],[1,2,3])
        self.assertAlmostEqual(x['effect'],18)
        self.assertLess(x['lower_95'],x['effect'])
        self.assertGreater(x['upper_95'],x['effect'])
    def test_end_to_end_small(self):
        with tempfile.TemporaryDirectory() as temp:
            summary=run(temp,train_n=1200,eval_n=900)
            self.assertTrue((Path(temp)/'frozen_policy.json').exists())
            self.assertIn('personalized_vs_blanket50',summary)
    def test_invalid_counts(self):
        with self.assertRaises(ValueError):make_training(n=10)
        with self.assertRaises(ValueError):evaluate(1,10,{s:0 for s in SEGMENTS})

if __name__=='__main__':unittest.main()