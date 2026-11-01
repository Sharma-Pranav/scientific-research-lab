import json
import tempfile
import unittest
from pathlib import Path
from research_lab.engine import audit, config_digest, run, validate_proposal

CONFIG = {
 "protocol_id": "test", "phase": "confirmatory", "question_id": "q", "dataset_version": "synthetic-gaussian-mixture-v1",
 "n": 10, "trials_per_seed": 8, "seeds": [1, 2], "contamination_rates": [0, 0.2], "contamination_sigma": 10,
 "target": "mean_absolute_estimation_error", "baselines": ["sample_mean", "sample_median"], "frozen": True
}

class HarnessTests(unittest.TestCase):
 def test_reproducible_results(self):
  from research_lab.engine import simulation
  self.assertEqual(simulation(CONFIG), simulation(CONFIG))
  self.assertEqual(config_digest(CONFIG), config_digest(dict(reversed(list(CONFIG.items())))))

 def test_append_audit_and_tamper_detection(self):
  with tempfile.TemporaryDirectory() as d:
   root = Path(d)
   path = root / 'protocol.json'
   path.write_text(json.dumps(CONFIG))
   m1, _ = run(root, path)
   m2, _ = run(root, path)
   self.assertNotEqual(m1['run_id'], m2['run_id'])
   self.assertEqual(audit(root), 2)
   result_file = root / 'runs' / m1['run_id'] / 'results.json'
   result_file.chmod(0o644) # simulate malicious editor despite write-once creation
   result_file.write_text('{}')
   with self.assertRaises(ValueError):
    audit(root)

 def test_confirmation_requires_frozen(self):
  with tempfile.TemporaryDirectory() as d:
   protocol = Path(d) / 'protocol.json'
   protocol.write_text(json.dumps({**CONFIG, 'frozen': False}))
   with self.assertRaises(ValueError):
    run(d, protocol)

 def test_novelty_stop_overrides_other_gates(self):
  proposal = json.loads((Path(__file__).resolve().parents[1] / 'research/robust-location/proposal.json').read_text())
  decisions, decision = validate_proposal(proposal)
  self.assertEqual(decisions['novelty_gate'], 'STOP')
  self.assertEqual(decision, 'STOP')
  with self.assertRaises(ValueError):
   validate_proposal({**proposal, 'publication_gate': 'GO'})

if __name__ == '__main__':
 unittest.main()
