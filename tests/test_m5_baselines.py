import csv
import tempfile
import unittest
from pathlib import Path
from research_lab.m5_baselines import (METHODS, quantile, errors, cost, forecast,
    verify_protocol, evaluate_origin, load_panel, summarize)
from research_lab.leadtime import newsvendor_cost

CFG={"phase":"exploratory","n_days":900,"per_stratum":1,
     "dev_states":["CA","TX"],"sealed_state":"WI","sealed_test_days":84,
     "min_history":90,"calibration_windows":8,"selection_windows":8,
     "partial_windows":2,"origins":[720,776],"methods":list(METHODS),
     "lead_times":[7,14],"alphas":[.5,.9]}

class M5BaselineTests(unittest.TestCase):
    def test_quantile_and_proper_cost_equivalence(self):
        self.assertEqual(quantile([-2,0,3,6],.5),0)
        self.assertEqual(quantile([-2,0,3,6],.9),6)
        item={"actual":[4.]*28,"pred":[3.]*28}
        self.assertEqual(cost(item,7,.9,0),newsvendor_cost(28,21,.9))
        self.assertEqual(errors(item,7),[7.]*4)

    def test_development_boundaries_and_group_seal(self):
        x=verify_protocol(CFG,900)
        self.assertLess(x["latest_dev_label_index"],x["sealed_start_index"])
        with self.assertRaisesRegex(ValueError,"Sealed"):
            verify_protocol({**CFG,"origins":[798]},900)
        with self.assertRaisesRegex(ValueError,"Overlapping"):
            verify_protocol({**CFG,"origins":[720,740]},900)
        with self.assertRaisesRegex(ValueError,"Group holdout"):
            verify_protocol({**CFG,"dev_states":["CA","TX","WI"]},900)

    def test_selection_does_not_see_current_or_future_labels(self):
        y=[float(3+4*(i%7==0)) for i in range(900)]
        a=evaluate_origin(y,720,CFG)
        b=evaluate_origin(y[:720]+[1000.]*180,720,CFG)
        for row_a,row_b in zip(a,b):
            self.assertEqual(row_a["selected"],row_b["selected"])
        self.assertNotEqual(a[0]["candidate_costs"],b[0]["candidate_costs"])

    def test_point_forecasts_are_past_only(self):
        y=[0,1,0,2,5,2,1]*20
        for method in METHODS:
            out=forecast(y,method)
            self.assertEqual(len(out),28)
            self.assertTrue(all(v>=0 for v in out))

    def test_identifier_sampling_does_not_use_sales(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"mini.csv"
            columns=["id","item_id","dept_id","cat_id","store_id","state_id"]+[f"d_{x}" for x in range(1,901)]
            with p.open("w",newline="") as f:
                writer=csv.writer(f);writer.writerow(columns)
                for s in ("CA","TX","WI"):
                    for c in ("FOODS","HOBBIES","HOUSEHOLD"):
                        for j in range(3):
                            writer.writerow([f"{s}_{c}_{j}","i","d",c,f"{s}_1",s]+[str(j)]*900)
            panel,meta=load_panel(p,n_days=900,n_each=1)
            self.assertEqual(len(panel),9)
            self.assertEqual(meta["source_rows"],27)
            again,_=load_panel(p,n_days=900,n_each=1)
            self.assertEqual([a["id"] for a in panel],[a["id"] for a in again])

    def test_regret_report(self):
        a={"lead_time":7,"alpha":.9,"series_id":"one",
           "regret":{"daily_pinball":1.,"partial_replay":0.,"full_replay":0.}}
        out=summarize([a,{**a,"series_id":"two"}])
        self.assertEqual(out[0]["methods"]["daily_pinball"]["mean_ex_post_regret"],1.)
        self.assertEqual(out[0]["daily_minus_full_regret"],1.)

if __name__=="__main__":unittest.main()
