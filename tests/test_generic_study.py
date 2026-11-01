import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from research_lab.study import audit, freeze, hash_file, init, load_protocol, run


class GenericResearchStudyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def make(self, slug="coin-demo"):
        return init(self.root, slug, "Does an estimator behave as predicted?")

    def update(self, folder, **changes):
        file = folder / "protocol.json"
        data = json.loads(file.read_text())
        data.update(changes)
        file.write_text(json.dumps(data))
        return data

    def test_new_project_runs_without_any_external_dataset(self):
        folder = self.make()
        self.assertTrue((folder / "proposal.md").exists())
        self.assertTrue((folder / "evidence_matrix.csv").exists())
        self.assertEqual(load_protocol(self.root, "coin-demo")[0]["phase"], "exploratory")
        first = run(self.root, "coin-demo")
        second = run(self.root, "coin-demo")
        self.assertNotEqual(first["run_id"], second["run_id"])
        self.assertEqual(first["result"], second["result"])
        self.assertEqual(audit(self.root, "coin-demo", replay=True)["runs"], 2)

    def test_csv_input_adapter_is_independent_of_M5(self):
        folder = self.make("sensor-sample")
        csv_path = self.root / "data" / "sensor.csv"
        csv_path.parent.mkdir()
        csv_path.write_text("value\n3\n4\n7\n")
        source = '''import csv
def run(protocol, inputs):
    with inputs["readings"].open(newline="") as source:
        rows = list(csv.DictReader(source))
    values = [float(row["value"]) for row in rows]
    return {"mean": sum(values)/len(values), "records": len(values),
            "domain": protocol["question"]}
'''
        (folder / "experiment.py").write_text(source)
        self.update(folder,
            inputs=[{"name":"readings", "path":"data/sensor.csv",
                     "sha256": hash_file(csv_path)}],
            settings={}, question="What is the sensor sample mean?")
        result = run(self.root, "sensor-sample")
        self.assertAlmostEqual(result["result"]["mean"], 14/3)
        self.assertEqual(audit(self.root, "sensor-sample", replay=True)["runs"], 1)
        csv_path.write_text("value\n3\n4\n700\n")
        with self.assertRaisesRegex(ValueError, "checksum mismatch"):
            audit(self.root, "sensor-sample", replay=True)

    def test_file_tampering_detected_even_with_same_registry(self):
        self.make()
        record = run(self.root, "coin-demo")
        path = Path(record["directory"]) / "results.json"
        path.chmod(0o644)
        path.write_text('{"mean_success_rate":999}')
        with self.assertRaisesRegex(ValueError, "Result tampered"):
            audit(self.root, "coin-demo")

    def test_new_protocol_and_runner_cannot_silently_rewrite_past(self):
        folder = self.make()
        run(self.root, "coin-demo")
        self.update(folder, hypothesis="Rewritten hypothesis")
        with self.assertRaisesRegex(ValueError, "drift"):
            audit(self.root, "coin-demo", replay=True)
        # Restore original to isolate runner mutation.
        self.update(folder, hypothesis="REPLACE with falsifiable hypothesis")
        (folder / "experiment.py").write_text((folder / "experiment.py").read_text()+"\n# changed\n")
        with self.assertRaisesRegex(ValueError, "drift"):
            audit(self.root, "coin-demo")

    def test_confirmation_needs_explicit_freeze_and_pinned_inputs(self):
        folder = self.make()
        self.update(folder, phase="confirmatory", frozen=True)
        with self.assertRaisesRegex(ValueError, "Missing freeze"):
            run(self.root, "coin-demo")
        proof = freeze(self.root, "coin-demo")
        self.assertEqual(len(proof["protocol_sha256"]), 64)
        result = run(self.root, "coin-demo")
        self.assertEqual(audit(self.root, "coin-demo", replay=True)["runs"], 1)
        self.assertEqual(result["result"]["kind"], "toy_coin_simulation_not_a_scientific_discovery")
        with self.assertRaises(FileExistsError):
            freeze(self.root, "coin-demo")
        self.update(folder, hypothesis="Changed after freeze")
        with self.assertRaisesRegex(ValueError, "Frozen"):
            run(self.root, "coin-demo")

    def test_confirmation_disallows_unpinned_input(self):
        folder = self.make()
        path = self.root / "data.csv"
        path.write_text("number\n1\n")
        self.update(folder, phase="confirmatory", frozen=True,
                    inputs=[{"name":"csv", "path":"data.csv", "sha256":None}])
        with self.assertRaisesRegex(ValueError, "Confirmatory inputs"):
            freeze(self.root, "coin-demo")

    def test_project_scoped_artifacts_are_independent(self):
        self.make("study-one")
        self.make("study-two")
        run(self.root, "study-one")
        run(self.root, "study-two")
        self.assertEqual(audit(self.root, "study-one", replay=True)["runs"],1)
        self.assertEqual(audit(self.root, "study-two", replay=True)["runs"],1)

    def test_reject_path_escape_and_invalid_slug(self):
        with self.assertRaisesRegex(ValueError, "slug"):
            init(self.root, "../escape", "X")
        folder = self.make()
        self.update(folder, runner="../../malicious.py")
        with self.assertRaisesRegex(ValueError, "escape"):
            load_protocol(self.root, "coin-demo")
        self.update(folder, runner="experiment.py",
                    inputs=[{"name":"data", "path":"../secret.csv", "sha256":None}])
        with self.assertRaisesRegex(ValueError, "escape"):
            load_protocol(self.root, "coin-demo")

    def test_replay_detects_forged_result_with_updated_hashes(self):
        folder = self.make()
        record = run(self.root, "coin-demo")
        output = Path(record["directory"])
        forged = {"kind":"toy_coin_simulation_not_a_scientific_discovery",
                  "mean_success_rate":0.99, "by_seed":[]}
        from research_lab.study import canonical, sha
        result_bytes = canonical(forged)
        (output / "results.json").chmod(0o644)
        (output / "results.json").write_bytes(result_bytes)
        man_file = output / "manifest.json"
        man = json.loads(man_file.read_text())
        man["artifact_sha256"]["results.json"] = sha(result_bytes)
        man_file.chmod(0o644)
        man_file.write_bytes(canonical(man))
        reg = folder / "experiments.jsonl"
        entry = json.loads(reg.read_text())
        entry["result_sha256"] = sha(result_bytes)
        entry["manifest_sha256"] = sha(canonical(man))
        reg.write_text(json.dumps(entry) + "\n")
        # Hash integrity alone is not a defense against coordinated changes.
        self.assertEqual(audit(self.root, "coin-demo", replay=False)["status"], "PASS")
        with self.assertRaisesRegex(ValueError, "Replay mismatch"):
            audit(self.root, "coin-demo", replay=True)


if __name__ == "__main__":
    unittest.main()
