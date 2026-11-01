"""Reader significance and reader-objection checks are structural, not scientific truth."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from research_lab.significance import assess, check_file, sections, template
from research_lab.study import init, run, audit


FRAME = {
    "Topic — I am studying": "how sensor drift changes anomaly alarm behavior in industrial telemetry",
    "Question — because I want to find out":
        "whether online recalibration reduces false alarms while preserving detection under distribution shift",
    "Reader significance — in order to help my reader understand":
        "when monitoring engineers can trust recalibrated alarms rather than accepting false alerts",
}
ARGUMENT = {
    "Claim": "In the stated synthetic test, a past-only rolling detector reduces false alarms relative to a fixed threshold.",
    "Reasons": "The rolling threshold adapts to a sustained baseline shift while still measuring extreme local residuals.",
    "Evidence":
        "The tested confusion matrices are archived at runs/projects/sensor-study/results.json and checked in the manifest.",
    "Acknowledgement & Response":
        "A skeptic could attribute the improvement to a deliberately favorable shift size; sensitivity across shifts is needed.",
    "Warrant":
        "Lower false-alarm counts at comparable detected-fault recall support the limited alarm-robustness claim only under those conditions.",
}


def document(fields):
    return "# Research significance\n\n" + "\n".join(
        f"## {heading}\n\n{text}\n" for heading, text in fields.items()
    )


class SignificanceTests(unittest.TestCase):
    def test_blank_template_must_fail_framing_and_argument_preflight(self):
        for stage in ("framing", "argument"):
            result = assess(template(), stage=stage)
            self.assertEqual(result["status"], "REVISE")
            self.assertIsNone(result["three_step_statement"])
            self.assertGreater(len(result["issues"]), 0)

    def test_three_step_framing_can_pass_without_pretending_final_evidence(self):
        state = assess(document(FRAME), stage="framing")
        self.assertEqual(state["status"], "READY_FOR_HUMAN_REVIEW")
        self.assertIn("because I want to find out", state["three_step_statement"])
        self.assertEqual(assess(document(FRAME), stage="argument")["status"], "REVISE")

    def test_five_part_argument_passes_structural_gate_only_with_locator(self):
        full = document({**FRAME, **ARGUMENT})
        state = assess(full, stage="argument")
        self.assertEqual(state["status"], "READY_FOR_HUMAN_REVIEW")
        self.assertIn("not automatically fact-checked", " ".join(state["limitations"]))
        altered = document({**FRAME, **ARGUMENT, "Evidence":
             "My intuition and a compelling explanation establish that the model must be correct."})
        result = assess(altered, stage="argument")
        self.assertEqual(result["status"], "REVISE")
        self.assertIn("no_traceable_locator", [item["issue"] for item in result["issues"]])

    def test_repeated_question_does_not_count_as_benefit(self):
        f = {**FRAME}
        f["Reader significance — in order to help my reader understand"] = f["Question — because I want to find out"]
        state = assess(document(f), stage="framing")
        self.assertEqual(state["status"], "REVISE")
        self.assertIn("repeats_question", [i["issue"] for i in state["issues"]])

    def test_duplicate_headings_cannot_override_source(self):
        with self.assertRaisesRegex(ValueError, "Repeated"):
            sections(document(FRAME) + "\n## Claim\n\nAnother claim.\n\n## Claim\n\nChanged again.\n")

    def test_missing_document_is_revise_not_publication_go(self):
        with tempfile.TemporaryDirectory() as dirname:
            report = check_file(Path(dirname) / "missing.md", stage="framing")
            self.assertEqual(report["status"], "REVISE")
            self.assertEqual(report["issues"][0]["issue"], "missing_file")

    def test_scaffolding_and_preflight_cli_do_not_block_exploratory_execution(self):
        with tempfile.TemporaryDirectory() as dirname:
            root = Path(dirname)
            project = init(root, "test-significance", "Can researchers write reader-significant questions?")
            self.assertTrue((project / "significance.md").is_file())
            run_record = run(root, "test-significance")
            manifest = json.loads((Path(run_record["directory"]) / "manifest.json").read_text())
            self.assertEqual(manifest["reader_significance_preflight"]["status"], "REVISE")
            frozen_sheet = Path(run_record["directory"]) / "significance.md"
            self.assertTrue(frozen_sheet.is_file())
            self.assertEqual(frozen_sheet.read_text(), (project / "significance.md").read_text())
            self.assertIn("significance.md", manifest["artifact_sha256"])
            self.assertEqual(audit(root, "test-significance", replay=True)["runs"], 1)
            cmd = [sys.executable, "-m", "research_lab.study", "--root",
                   str(root), "preflight", "test-significance"]
            failed = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(failed.returncode, 2)
            (project / "significance.md").write_text(document(FRAME), encoding="utf8")
            passed = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(passed.returncode, 0, passed.stderr)
            self.assertEqual(json.loads(passed.stdout)["status"], "READY_FOR_HUMAN_REVIEW")
            deep = subprocess.run(cmd + ["--stage", "argument"], capture_output=True, text=True)
            self.assertEqual(deep.returncode, 2)
            (project / "significance.md").write_text(document({**FRAME, **ARGUMENT}), encoding="utf8")
            # Later improvements may edit the live worksheet, never past evidence.
            self.assertEqual(audit(root, "test-significance", replay=True)["runs"], 1)
            self.assertNotEqual(frozen_sheet.read_text(), (project / "significance.md").read_text())
            final = subprocess.run(cmd + ["--stage", "argument"], capture_output=True, text=True)
            self.assertEqual(final.returncode, 0, final.stderr)
            # Even a coordinated change to one artifact is found by its run manifest.
            frozen_sheet.chmod(0o644)
            frozen_sheet.write_text("fabricated significance")
            with self.assertRaisesRegex(ValueError, "Saved artifact integrity failure"):
                audit(root, "test-significance")


if __name__ == "__main__":
    unittest.main()
