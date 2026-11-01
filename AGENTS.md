# Scientific research invariants

## Reader significance and argument: two separate quality gates

**Start with the reader's "So what?" before committing to a large experiment.** Write:

1. **I am studying** — the concrete topic or phenomenon.
2. **because I want to find out** — the specific unknown question or mechanism.
3. **in order to help my reader understand** — the wider understanding or consequential decision for someone else.

After obtaining evidence, stress-test the argument against the reader's five objections:
**Claim** (what is the point?), **Reasons** (why believe it?),
**Evidence** (how do you know?), **Acknowledgement & Response**
(what about the strongest competing explanation?), and **Warrant**
(why do the reasons/evidence support that specific point?).

New projects have research/<slug>/significance.md. Check framing before costly scientific work
with \`python -m research_lab.study preflight <slug> --stage framing\`;
after results, check all five argument elements with \`--stage argument\`.
A READY_FOR_HUMAN_REVIEW check means only that the worksheet is structurally complete.
It does **not** verify scientific significance, evidence correctness, novelty, or publication readiness.
A toy experiment may still run with REVISE status so users can test infrastructure; never treat
a completed run as a passed reader-significance gate.

## Data selection: default to curated evidence

- **Prefer curated datasets** directly maintained by research institutions, benchmark maintainers, official public agencies, peer-reviewed supplementary archives, or established repositories, when suitable for the actual question. Curated does **not** automatically mean bias-free or suitable for a particular inference.
- Verify official source and version, documentation/data card, provenance, data dictionary and measurement process, license/reuse rights, known data quality, target construction, label uncertainty, dataset shift, and representative coverage. Check for duplicates, missingness, selection bias and leakage.
- Preserve source URI, retrieval date, dataset/version ID, file checksum, permissible transformations and split specification in the project protocol/evidence. Prefer predefined benchmark splits when scientifically appropriate, and explicitly reserve held-out data. Never redistribute raw datasets without permission.
- Prefer credible real-world evidence for externally valid empirical claims. Use synthetic data when the question is theoretical, for controlled falsification, or for test fixtures; clearly identify it as synthetic and do not use it alone to claim field effectiveness.
- If a curated dataset does not suit the scientific question, do not force it: justify the alternative collection or simulation and document how the limitations affect interpretation. Some research requires no dataset.

- Start every project with **I am studying ... / because I want to find out ... / in order to help readers understand ...**
- State a falsifiable claim, mechanism, H0, at least one competing explanation, and a meaningful baseline.
- Separate exploration from confirmation. Freeze protocols before confirmatory data inspection; never rewrite earlier protocols to fit outcomes.
- Do not invent sources, citations, experimental runs, statistics, or novelty claims. Verified sources require an inspectable primary link and specific supported finding.
- Report failed and negative runs; never cherry-pick. Preserve exact config, seed, dataset fingerprint, compute and code version for each reported result.
- Never present estimates without uncertainty, validity limitations and scope conditions appropriate to the question.
- Experimental code changes require tests and an auditable run. Never claim tests passed without actually executing them.
- Treat scientific novelty and publication readiness as human-reviewed gates independent of metric improvement.
- Keep research protocols in `research/`, mechanics in `research_lab/`, audit in `tests/`, and run evidence in `runs/`.
- Never edit completed run directories or registry entries. Amend by adding new runs and documented corrections.
- Independent review must be done from evidence, without inheriting the desired narrative or granting the researcher final authority.

## Verification commands and review boundary

- Run `python -m unittest discover -s tests -v` and `python -m research_lab.evidence research/*/evidence_matrix.csv` before claiming engineering readiness. Matrix validation is **not** literature fact-checking.
- Lead-time results need `python -m research_lab.leadtime --verify --config <protocol> --output <run-dir>` plus intact saved artifacts. A frozen field is not external preregistration.
- For real time-series data, seal the final test period, use horizon-aligned rolling splits with an embargo as necessary, and keep group holdouts separate. Audit feature availability, labels, transforms and model-selection leakage.
- All internal gates marked GO permit only independent human review, not automatic publication approval.

## Domain-independent research projects

- For new questions, use \`python -m research_lab.study init <slug> --title "..."\` and follow \`docs/NEW_RESEARCH_PROJECT.md\`. Do not copy M5-specific evaluators into unrelated studies.
- New experiments expose \`run(protocol, inputs)\` in their project-local trusted runner; reusable code must not assume a dataset name, file type, forecasting metric, or domain.
- Distinguish project scaffolding and infrastructure verification from scientifically valid methods and publication readiness.
- For confirmation, pin all inputs, freeze exact protocol and runner code, and use a separately protected test set and independent review. A local freeze file is not external preregistration.
- Never run unreviewed experiment plugins: loading project experiment.py executes arbitrary local Python.
