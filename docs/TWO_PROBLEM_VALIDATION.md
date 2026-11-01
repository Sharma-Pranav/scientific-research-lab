# Cross-domain integration test: two unrelated scientific questions

This is a **generalization test for the research execution harness**, not a contribution to anomaly detection or multiple-testing theory.

## Test A: Industrial-style temperature sensor anomaly alarms

- Problem: Can a past-only rolling median/MAD detector maintain alarm precision after a synthetic sensor baseline shift?
- Data: deterministic, synthetic labeled CSV created from `research/sensor-drift-anomaly/generate_fixture.py`.
- Source SHA256 pinned in `research/sensor-drift-anomaly/protocol.json`.
- Evaluation: detector confusion matrices by pre-shift and shifted periods.
- Guardrail: training calibration contains no synthetic shift or injected faults; detection uses earlier measurements only. No external sensors, hardware or industrial fleet validated.

## Test B: Statistical A/B experiments with repeated interim peeking

- Problem: Under the exact null, how does repeated unadjusted interim significance testing change the chance of at least one false rejection?
- Data: **none** — simulation uses the protocol's seeds and algorithm.
- Controls: final-only unadjusted z-test and Bonferroni-corrected anytime rejection on the same simulated experiments.
- Evaluation: empirical Type I error over 7,500 independent repetitions, grouped by seed.
- Guardrail: known unit variance, independent Gaussian samples, fixed number of looks. This illustrates a known statistical mechanism.

## Running locally

From a real clone with Python 3.10+:

```bash
python research/sensor-drift-anomaly/generate_fixture.py
python -m research_lab.study run sensor-drift-anomaly
python -m research_lab.study audit sensor-drift-anomaly --replay
python -m research_lab.study run sequential-testing-risk
python -m research_lab.study audit sequential-testing-risk --replay
```

Every run writes its own unique output under `runs/projects/<slug>/<run-id>/` and its own `research/<slug>/experiments.jsonl`. Generated CSV is under ignored `data/`. Input fingerprints and full deterministic replay are checked by the reusable code in `research_lab/study.py`.

The [GitHub Actions integration workflow](../../.github/workflows/two-research-problems.yml) checks out the actual Git commit, runs the repository test suite, executes both studies, audits both, checks scientifically meaningful directionality controls, and uploads only derived results/manifests. This is important because the assistant's separate local container cannot resolve `github.com`, so a direct local `git clone` is unavailable; Actions checkout is the authoritative verification of the actual repository.

## Interpret with the correct limits

- Both experiments are **toy synthetic studies**; neither establishes novelty, field utility, independent scientific review, or publication readiness.
- They genuinely exercise two distinct formats: a checksum-verified data file and a dataset-free simulation.
- Cross-domain execution proves the infrastructure is not coupled to M5. It does **not** establish that the harness automatically designs valid experiments across arbitrary research fields.
- All scientific novelty and publication gates: **STOP**.
