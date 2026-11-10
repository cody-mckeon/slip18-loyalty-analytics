import json
import tempfile
import unittest
from pathlib import Path
from build_dashboard import ROOT, SOURCES, build

class DashboardTests(unittest.TestCase):
    def test_references_are_valid_and_business_effects_reconcile(self):
        e=json.loads(SOURCES['email'].read_text());p=json.loads(SOURCES['personalization'].read_text())
        self.assertAlmostEqual(e['groups']['1']['net_profit_per_customer']-e['groups']['0']['net_profit_per_customer'],e['effect'])
        self.assertAlmostEqual(p['groups']['personalized']['mean']-p['groups']['blanket_50']['mean'],p['personalized_vs_blanket50']['effect'])
        self.assertAlmostEqual(p['groups']['personalized']['mean']-p['groups']['no_offer']['mean'],p['personalized_vs_no_offer']['effect'])
        self.assertTrue(e['lower_95']>0)
        self.assertTrue(p['personalized_vs_no_offer']['lower_95']<0)
    def test_generated_html_is_self_contained_and_contains_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=build(Path(tmp)/'dashboard.html');text=path.read_text()
            self.assertIn('const DATA = ',text)
            self.assertNotIn('/*__EMBEDDED_DATA__*/',text)
            self.assertNotIn('<script src=',text)
            self.assertIn('No real Resorts World data',text)
            self.assertIn('100000',text)
            self.assertIn('personalized_vs_blanket50',text)

if __name__=='__main__':unittest.main()