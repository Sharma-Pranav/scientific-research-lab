# Scientific research invariants

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
