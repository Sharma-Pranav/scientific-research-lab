"""Cross-domain tests of reader significance and five-part argument validation."""
import unittest
from pathlib import Path

from research_lab.significance import assess, check_file, sections

ROOT = Path(__file__).resolve().parents[1]
QUESTIONS = ("uci-bike-forecasting", "sequential-testing-risk")


class TwoRealResearchQuestionsTests(unittest.TestCase):
    def test_two_different_real_project_arguments_pass_structural_review(self):
        statements = set()
        for slug in QUESTIONS:
            file = ROOT / "research" / slug / "significance.md"
            framing = check_file(file, stage="framing")
            argument = check_file(file, stage="argument")
            self.assertEqual(framing["status"], "READY_FOR_HUMAN_REVIEW", (slug, framing["issues"]))
            self.assertEqual(argument["status"], "READY_FOR_HUMAN_REVIEW", (slug, argument["issues"]))
            self.assertEqual(len(argument["complete_sections"]), 8)
            statements.add(argument["three_step_statement"])
            self.assertTrue(sections(file.read_text())["evidence"])
        self.assertEqual(len(statements), 2)

    def test_two_reader_benefits_and_grounded_outcomes(self):
        bike = (ROOT / "research/uci-bike-forecasting/significance.md").read_text()
        ab = (ROOT / "research/sequential-testing-risk/significance.md").read_text()
        x, y = sections(bike), sections(ab)
        self.assertIn("mobility planning analysts", x["significance"])
        self.assertIn("experiment owners and product decision-makers", y["significance"])
        self.assertIn("918.84", x["evidence"])
        self.assertIn("1,342.27", x["evidence"])
        for amount in ("14.39", "5.12", "3.15"):
            self.assertIn(amount, y["evidence"])
        self.assertIn("not", x["response"].lower())
        self.assertIn("not", y["warrant"].lower())
        self.assertIn("Publication gate: STOP", ab)

    def test_missing_reader_consequence_is_rejected(self):
        for slug in QUESTIONS:
            src = (ROOT / "research" / slug / "significance.md").read_text()
            part = sections(src)
            broken = src.replace(part["significance"], part["question"], 1)
            result = assess(broken, stage="framing")
            self.assertEqual(result["status"], "REVISE", (slug, result))
            self.assertIn("repeats_question", [i["issue"] for i in result["issues"]])

    def test_missing_rebuttal_and_untraceable_evidence_are_rejected(self):
        for slug in QUESTIONS:
            src = (ROOT / "research" / slug / "significance.md").read_text()
            part = sections(src)
            no_response = src.replace(part["response"], "[Write the strongest alternative]")
            result = assess(no_response, stage="argument")
            self.assertEqual(result["status"], "REVISE")
            self.assertIn("response", [i["section"] for i in result["issues"]])
            no_locator = src.replace(
                part["evidence"],
                "A reviewer inspected figures privately and thought they demonstrated this outcome.")
            result = assess(no_locator, stage="argument")
            self.assertEqual(result["status"], "REVISE")
            self.assertIn("no_traceable_locator", [i["issue"] for i in result["issues"]])

    def test_known_limitation_arbitrary_url_is_not_fact_checked(self):
        file = ROOT / "research/sequential-testing-risk/significance.md"
        src = file.read_text()
        fictitious = src.replace(
            sections(src)["evidence"],
            "An unrelated claim purports to be proven: https://example.org/fake-proof")
        self.assertEqual(assess(fictitious, stage="argument")["status"], "READY_FOR_HUMAN_REVIEW")


if __name__ == "__main__":
    unittest.main()
