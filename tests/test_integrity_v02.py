import json
import tempfile
import unittest
from pathlib import Path

from research_lab.engine import validate_proposal
from research_lab.evidence import validate_matrix
from research_lab.leadtime import write_artifacts, verify_artifacts, canonical
from research_lab.splits import rolling_origin, stable_group_partition

BASE=Path(__file__).resolve().parents[1]
CONFIG=BASE/'research/leadtime-dependence/confirmatory.json'


class EvidenceTests(unittest.TestCase):
    def test_existing_research_evidence_matrices(self):
        for name in ('robust-location','leadtime-dependence','selection-transfer'):
            r=validate_matrix(BASE/'research'/name/'evidence_matrix.csv')
            self.assertGreater(r['rows'],0)
            self.assertFalse(r['novelty_automatically_verified'])

    def test_unsubstantiated_verified_claim_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'matrix.csv'
            f.write_text('claim,source_url,exact_evidence,status,relationship_to_project\n'
                         'New method works,,,VERIFIED,Overlaps with X\n')
            with self.assertRaisesRegex(ValueError,'required'):
                validate_matrix(f)

    def test_no_machine_granted_publication_go(self):
        p=json.loads((BASE/'research/robust-location/proposal.json').read_text())
        for key in ('significance_gate','novelty_gate','feasibility_gate','evidence_gate'):
            p[key]='GO'
        p['publication_gate']='HUMAN_REVIEW_REQUIRED'
        self.assertEqual(validate_proposal(p)[1],'HUMAN_REVIEW_REQUIRED')
        p['publication_gate']='GO'
        with self.assertRaisesRegex(ValueError,'cannot authorize publication'):
            validate_proposal(p)


class ProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        original=json.loads(CONFIG.read_text())
        cls.tiny={**original,'trials_per_seed':3,'seeds':[2,3,5]}

    def make_run(self,root):
        f=root/'frozen.json'
        f.write_text(json.dumps(self.tiny))
        output=root/'run'
        write_artifacts(f,output)
        return f,output

    def test_replay_and_checksum(self):
        with tempfile.TemporaryDirectory() as d:
            cfg,out=self.make_run(Path(d))
            report=verify_artifacts(out,config_path=cfg,replay=True)
            self.assertEqual(report['status'],'PASS')
            self.assertTrue(report['replay_performed'])

    def test_tampered_result_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            cfg,out=self.make_run(Path(d))
            results=out/'results.json'
            results.chmod(0o644)
            results.write_text('{"fake":1}')
            with self.assertRaisesRegex(ValueError,'hash mismatch'):
                verify_artifacts(out,config_path=cfg)

    def test_changed_protocol_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            cfg,out=self.make_run(Path(d))
            cfg.write_text(json.dumps({**self.tiny,'trials_per_seed':4}))
            with self.assertRaisesRegex(ValueError,'differs'):
                verify_artifacts(out,config_path=cfg)

    def test_replay_detects_forged_result_with_updated_hash(self):
        import hashlib
        with tempfile.TemporaryDirectory() as d:
            cfg,out=self.make_run(Path(d))
            results=out/'results.json'
            manifest=out/'manifest.json'
            forged=json.loads(results.read_text())
            forged['cells'][0]['difference_B_minus_A']=42.0
            results.chmod(0o644)
            results.write_bytes(canonical(forged))
            meta=json.loads(manifest.read_text())
            meta['result_sha256']=hashlib.sha256(results.read_bytes()).hexdigest()
            manifest.chmod(0o644)
            manifest.write_bytes(canonical(meta))
            with self.assertRaisesRegex(ValueError,'Replay'):
                verify_artifacts(out,config_path=cfg,replay=True)


class SplitTests(unittest.TestCase):
    def test_temporal_boundaries_and_sealed_final_holdout(self):
        folds=rolling_origin(140,min_train=60,horizon=14,step=7,embargo=3,sealed_test=28)
        self.assertTrue(folds)
        self.assertEqual(folds[0],(0,60,63,77))
        for start,end,eval_start,eval_end in folds:
            self.assertEqual(start,0)
            self.assertEqual(eval_start-end,3)
            self.assertLessEqual(eval_end,112)
            self.assertLess(end,eval_start)

    def test_short_series_fails_closed(self):
        with self.assertRaises(ValueError):
            rolling_origin(40,min_train=30,horizon=10,embargo=2,sealed_test=5)

    def test_group_splits_are_deterministic_disjoint(self):
        train,hold=stable_group_partition(['a','b','c','d','a'],holdout_fraction=.5,salt='protocol-1')
        t2,h2=stable_group_partition(['d','c','b','a'],holdout_fraction=.5,salt='protocol-1')
        self.assertEqual((train,hold),(t2,h2))
        self.assertFalse(set(train)&set(hold))
        self.assertEqual(set(train)|set(hold),{'a','b','c','d'})


if __name__=='__main__':
    unittest.main()
