"""Scientific-methodology tests, including real negative controls and forged evidence."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from research_lab.leadtime import canonical
from research_lab.m5_baselines import METHODS
from research_lab.m5_history import (
    audit, digest, evaluate_origin, matched_daily_cost, matched_daily_errors,
    past_mean_shift, run, summarize, validate
)

BASE={
    "phase":"exploratory","n_days":1100,"per_stratum":1,
    "dev_states":["CA","TX"],"sealed_state":"WI","sealed_test_days":84,
    "min_history":90,"calibration_windows":12,"selection_windows":12,
    "partial_windows":3,"origins":[800,856],"methods":list(METHODS),
    "lead_times":[7,14],"alphas":[.5,.9]
}
CFG={
    "phase":"exploratory","publication_gate":"STOP",
    "base_protocol_sha256":digest(BASE),
    "n_days":1100,"per_stratum":1,
    "dev_states":["CA","TX"],"sealed_state":"WI","sealed_test_days":84,
    "origins":[800,856],"methods":list(METHODS),
    "calibration_windows":12,"selection_windows":12,
    "lead_times":[7,14],"alphas":[.5,.9],
    "history_lengths":[1,3,6,12],
    "regime_threshold":0.5
}

def fake_panel():
    panel=[]
    for state in ("CA","TX","WI"):
        for cat in ("FOODS","HOBBIES","HOUSEHOLD"):
            series=[float((t%7==0)*4+(t%13==0)*2+(t//28)%3) for t in range(1100)]
            panel.append({"id":state+"-"+cat,"store":state+"_1","state":state,
                          "category":cat,"y":series})
    return panel

class M5HistoryTests(unittest.TestCase):
    def test_registration_and_holdout_cannot_change(self):
        self.assertLess(validate(CFG,BASE)["latest_dev_label_index"],1016)
        with self.assertRaisesRegex(ValueError,"Changed"):
            validate({**CFG,"dev_states":["CA","TX","WI"]},BASE)
        with self.assertRaisesRegex(ValueError,"Changed"):
            validate({**CFG,"origins":[800,900]},BASE)
        with self.assertRaisesRegex(ValueError,"history lengths"):
            validate({**CFG,"history_lengths":[1,3,6]},BASE)
        with self.assertRaisesRegex(ValueError,"publication"):
            validate({**CFG,"publication_gate":"GO"},BASE)

    def test_past_instability_never_reads_future(self):
        y=[3.]*1100
        y[772:800]=[12.]*28
        score=past_mean_shift(y,800)
        self.assertGreater(score,.5)
        self.assertEqual(score,past_mean_shift(y[:800]+[500.]*300,800))

    def test_matched_loss_count_and_nonleaking_selection(self):
        sample=fake_panel()[0]["y"]
        rows_a=evaluate_origin(sample,800,CFG)
        rows_b=evaluate_origin(sample[:800]+[999.]*300,800,CFG)
        self.assertEqual(len(rows_a),4)
        for a,b in zip(rows_a,rows_b):
            self.assertEqual(a["past_instability"],b["past_instability"])
            self.assertEqual({k:v["winner"] for k,v in a["selections"].items()},
                             {k:v["winner"] for k,v in b["selections"].items()})
            L=a["lead_time"]
            for k in (1,3,6,12):
                self.assertEqual(a["selections"][f"policy_{k}"]["loss_terms_per_model"],
                                 a["selections"][f"daily_matched_{k}"]["loss_terms_per_model"])
                self.assertEqual(a["selections"][f"daily_full_{k}"]["loss_terms_per_model"],28*k)

    def test_daily_counterfactual_uses_fixed_positions(self):
        window={"actual":[1.]*28,"pred":[0.]*28}
        self.assertEqual(matched_daily_errors(window,7),[1.]*4)
        self.assertAlmostEqual(matched_daily_cost(window,7,.9,0),.9)

    def test_report_covers_all_histories_and_scenarios(self):
        panel=fake_panel()
        meta={"n_days":1100,"md5":"fixture","sample_id_sha256":"fixture"}
        result=run(CFG,BASE,panel,meta)
        self.assertEqual(result["n_skus"],6)
        self.assertEqual(result["n_cases"],6*2*2*2)
        self.assertEqual(len(result["summaries"]),4)
        self.assertEqual({r["state"] for r in result["rows"]},{"CA","TX"})
        for s in result["summaries"]:
            self.assertEqual(len(s["methods"]),12)

    def test_forged_regret_and_recomputed_checksum_are_detected(self):
        meta={"n_days":1100,"md5":"fixture","sample_id_sha256":"fixture"}
        result=run(CFG,BASE,fake_panel(),meta)
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            p=root/"proposal.json";p.write_bytes(canonical(CFG))
            b=root/"base.json";b.write_bytes(canonical(BASE))
            (root/"config.json").write_bytes(canonical(CFG))
            (root/"results.json").write_bytes(canonical(result))
            manifest={"protocol_sha256":digest(CFG),"base_protocol_sha256":digest(BASE),
                      "results_sha256":hashlib.sha256(canonical(result)).hexdigest()}
            (root/"manifest.json").write_bytes(canonical(manifest))
            self.assertEqual(audit(root,p,b)["status"],"PASS")
            result["rows"][0]["selections"]["policy_3"]["regret"]+=42
            (root/"results.json").write_bytes(canonical(result))
            manifest["results_sha256"]=hashlib.sha256(canonical(result)).hexdigest()
            (root/"manifest.json").write_bytes(canonical(manifest))
            with self.assertRaisesRegex(ValueError,"Stored regret mismatch"):
                audit(root,p,b)

if __name__=="__main__":
    unittest.main()
