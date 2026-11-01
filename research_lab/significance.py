"""Structural 'So what?' and five-part scientific argument preflight.

A READY_FOR_HUMAN_REVIEW result asserts only that fields are non-placeholder
and sources are traceable; it does NOT validate relevance, truth, inference
or publication readiness. No external libraries or specific science domain.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HEADINGS = {
    "topic": "Topic — I am studying",
    "question": "Question — because I want to find out",
    "significance": "Reader significance — in order to help my reader understand",
    "claim": "Claim",
    "reasons": "Reasons",
    "evidence": "Evidence",
    "response": "Acknowledgement & Response",
    "warrant": "Warrant",
}
FRAMING = ("topic", "question", "significance")
ARGUMENT = FRAMING + ("claim", "reasons", "evidence", "response", "warrant")

PROMPTS = {
    "topic": "Specify the concrete topic or phenomenon studied.",
    "question": "State what you want to find out, not just the broad topic.",
    "significance": "Identify what a reader or decision-maker will better understand, beyond your project.",
    "claim": "What is your point? Name a testable, scoped conclusion rather than a wish.",
    "reasons": "Why should the reader believe the claim? Give the logical supporting reasons.",
    "evidence": "How do you know? Cite an inspectable result, proof, artifact, or primary source.",
    "response": "What about the strongest counterargument or alternative? State and answer it fairly.",
    "warrant": "Explain precisely why the reasons and evidence support this claim.",
}
_PLACEHOLDERS = re.compile(
    r"\b(todo|tbd|replace|placeholder|insert|fill me|not yet|pending evidence)\b"
    r"|\[[^\]]*(?:write|insert|topic|question|evidence|reader|claim)[^\]]*\]",
    flags=re.IGNORECASE,
)
# A stable pointer, not proof of factual correctness or legitimate licensing.
_LOCATOR = re.compile(
    r"https?://|doi:|doi\.org/|\bruns/|\bartifacts/|"
    r"\bsha256:|\bproof:|\blemma:|\btheorem:|"
    r"\b(?:[\w/-]+/)?(?:results|manifest|evidence)[\w.-]*\.(?:json|csv|md|pdf)\b",
    flags=re.IGNORECASE,
)
_SECTION = re.compile(r"^##\s+(.+?)\s*$")


def template() -> str:
    return """# Significance and scientific argument worksheet

Write this as a reader-facing contribution, not as a promise of novelty.
For the initial framing preflight, complete the first three sections.
After collecting evidence, complete all eight sections for argument review.

## Topic — I am studying

[Write the concrete topic or phenomenon]

## Question — because I want to find out

[Write the precise unknown relationship or mechanism]

## Reader significance — in order to help my reader understand

[Write who benefits and what broader understanding or decision improves]

## Claim

[Write the strongest scoped, evidence-supported claim; revise after experiment]

## Reasons

[Write the logical reasons supporting the claim]

## Evidence

[Write an inspectable results.json path, primary source URL, DOI, or proof locator]

## Acknowledgement & Response

[Write the strongest plausible alternative and how the evidence addresses it]

## Warrant

[Write why these specific reasons and evidence justify the scoped claim]

**Caution:** The worksheet is a structural writing aid. Passing its check
does not verify citations, significance, statistical validity, or novelty.
"""


def sections(source: str) -> dict[str, str]:
    """Parse exact Markdown headings; reject duplicates instead of silently replacing."""
    by_name = {label.casefold(): key for key, label in HEADINGS.items()}
    found: dict[str, list[str]] = {}
    current = None
    for line in source.splitlines():
        match = _SECTION.match(line)
        if match:
            key = by_name.get(match.group(1).strip().casefold())
            if key:
                if key in found:
                    raise ValueError(f"Repeated significance section: {HEADINGS[key]}")
                found[key] = []
            current = key
        elif current is not None:
            found[current].append(line)
    return {key: "\n".join(lines).strip() for key, lines in found.items()}


def meaningful(value: str) -> bool:
    normalized = re.sub(r"\s+", " ", value.strip())
    if len(normalized) < 25 or not re.search(r"[A-Za-z]", normalized):
        return False
    if normalized.strip(" -—:.[]_") == "":
        return False
    return not bool(_PLACEHOLDERS.search(normalized))


def assess(source: str, stage="framing") -> dict:
    """Return actionable structural feedback, without a machine significance verdict."""
    if stage not in {"framing", "argument"}:
        raise ValueError("Stage must be framing or argument")
    parsed = sections(source)
    targets = FRAMING if stage == "framing" else ARGUMENT
    issues = []
    for key in targets:
        if not meaningful(parsed.get(key, "")):
            issues.append({"section": key, "issue": "missing_or_placeholder", "action": PROMPTS[key]})
    if not any(i["section"] == "significance" for i in issues) and not any(
        i["section"] == "question" for i in issues
    ):
        question = parsed["question"].lower().strip(" .")
        significance = parsed["significance"].lower().strip(" .")
        if question == significance:
            issues.append({"section": "significance", "issue": "repeats_question",
                           "action": "Explain the reader's broader understanding, not the research question again."})
    if stage == "argument" and meaningful(parsed.get("evidence", "")):
        if not _LOCATOR.search(parsed["evidence"]):
            issues.append({"section": "evidence", "issue": "no_traceable_locator",
                           "action": "Include a result artifact path, source URL, DOI, or explicit proof locator."})
    frame = {}
    if all(meaningful(parsed.get(k, "")) for k in FRAMING):
        frame = {k: re.sub(r"\s+", " ", parsed[k]).rstrip(".") for k in FRAMING}
    statement = (
        f"I am studying {frame['topic']} because I want to find out {frame['question']} "
        f"in order to help my reader understand {frame['significance']}."
        if frame else None
    )
    return {
        "stage": stage, "status": "READY_FOR_HUMAN_REVIEW" if not issues else "REVISE",
        "complete_sections": [k for k in targets if meaningful(parsed.get(k, ""))],
        "issues": issues, "three_step_statement": statement,
        "limitations": [
            "Structural completeness does not establish reader relevance, original contribution or validity.",
            "Evidence locators and statements are not automatically fact-checked.",
            "Independent human review is required; this checker never issues publication GO.",
        ],
    }


def check_file(path: str | Path, stage="framing") -> dict:
    p = Path(path)
    if not p.is_file():
        return {
            "stage": stage, "status": "REVISE", "complete_sections": [],
            "issues": [{"section": "worksheet", "issue": "missing_file",
                        "action": f"Create the significance worksheet: {p}"}],
            "three_step_statement": None,
            "limitations": ["Worksheet is absent; no significance claim has been reviewed."],
        }
    return assess(p.read_text(encoding="utf-8"), stage=stage)


def main():
    parser = argparse.ArgumentParser(description="Reader-significance and claim-quality preflight")
    parser.add_argument("worksheet")
    parser.add_argument("--stage", choices=("framing", "argument"), default="framing")
    args = parser.parse_args()
    result = check_file(args.worksheet, stage=args.stage)
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] != "READY_FOR_HUMAN_REVIEW":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
