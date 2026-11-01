# Create and run a NEW research problem

## The architecture is intentionally domain-independent

The original M5 modules are **examples**, not the framework. A new question uses three independent layers:

1. **Scientific workflow:** framing, literature, competing hypotheses, falsifiers and independent review (AGENTS.md, .agents/skills/, templates/).
2. **Reusable execution harness:** project creation, protocol freezing, input SHA256 fingerprints, project-local registry, read-only run artifacts and deterministic audit/replay (research_lab/study.py).
3. **Your own domain adapter:** a Python experiment implementing run(protocol, inputs), with any dataset format or **no dataset**. The harness does not know whether you study forecasting, pricing, coding agents, reliability, simulation, human evaluation or scientific literature.

The framework cannot automatically invent a scientifically valid experiment for an arbitrary new domain. The researcher and Codex must still implement the measurements and establish that their design is meaningful.

## Dataset choice: curated by default, not mandatory

Before implementing a new empirical study, look first for **curated, maintained, documented datasets** relevant to the scientific question. Prefer direct official benchmark or institutionally hosted sources over opaque mirrors or ad hoc scraped collections where comparable quality is available.

A dataset qualifies as a credible research input only after checking: provenance and author/publisher; stable release/version; documentation/data dictionary; rights/license for use and redistribution; coverage and representativeness; label/measurement reliability; known missingness, bias and duplication; and split suitability (including time, group and leakage constraints). Store source links and fingerprint hashes in the protocol; keep raw third-party/private data out of Git unless the license explicitly allows distribution.

**Do not blindly favor popular benchmarks.** Curated-but-mismatched data may be worse than a well-designed alternative. Explain why the chosen data actually measure the proposed mechanism. Synthetic data are preferred for deterministic smoke tests or controlled demonstrations, and are legitimate for theoretical simulation, but cannot by themselves establish external real-world validity. Projects with no data (such as theoretical or synthetic experiments) remain supported.

## 1. First use: a new project, with no dataset

From the cloned repo root (Python 3.10+, Git):

~~~bash
python -m research_lab.study init sensor-reliability --title "Do sensor faults change anomaly-detection calibration?"
python -m research_lab.study run sensor-reliability
python -m research_lab.study audit sensor-reliability --replay
~~~

This first run deliberately executes a simple **toy coin simulation** that the scaffolder creates. It validates the execution system, **not your scientific hypothesis**. The generated files live in research/sensor-reliability/:

| File | Responsibility |
|---|---|
| proposal.md | Topic, question, reader-facing significance, competing hypotheses |
| evidence_matrix.csv | Primary sources, relevance, support and novelty audit |
| protocol.json | Research question, phase, hypothesis, falsifier, runner, seeds, settings and inputs |
| experiment.py | Domain-specific experiment code, exposing run(protocol, inputs) |
| review.md | Adversarial evidence review, limits and human decision |
| experiments.jsonl (after first run) | Project-local append-only run index; generated and ignored by Git |

Each execution creates runs/projects/sensor-reliability/<unique-id>/ with protocol.json, results.json and manifest.json. Generated run packages are ignored by Git, so for durable evidence upload the run directory to a controlled research-artifact store or CI artifact and commit a sourced summary with its hashes. Do not rely on your local filesystem as archival storage.

## 2. Replace the demonstration with your actual research

Open the generated proposal and protocol. Rewrite the question, significance, hypothesis, *falsifying outcome*, and settings. Then edit experiment.py:

~~~python
from pathlib import Path

def run(protocol: dict, inputs: dict[str, Path]) -> dict:
    # The experiment receives the complete declared protocol and SHA256-checked inputs.
    # This is your domain's implementation, not built into the research harness.
    seed_results = []
    for seed in protocol["seeds"]:
        # TODO: load data, build baselines, execute independent experiments
        # and record metric values plus uncertainty inputs
        seed_results.append({"seed": seed, "result": 0.0})
    return {"status": "illustrative_only_replace_before_claims",
            "by_seed": seed_results}
~~~

The code above is only a contract illustration. A serious study must return raw/per-unit metrics or references to preserved immutable artifacts, uncertainty, baseline comparisons and failed/negative results. Large model weights, sensitive data or proprietary datasets should remain outside Git; publish fingerprints and permitted derived evidence.

Ask Codex:

~~~text
Read AGENTS.md and docs/NEW_RESEARCH_PROJECT.md. Use the hypothesis-generation,
literature-verification and experiment-design skills to frame a new, falsifiable
research question. Replace the toy runner with a minimal working experiment for
that question, including strong baselines, seeds, method-level tests, and a
replay-auditable result. Do not touch other projects or any sealed holdout.
Do not claim novelty without primary-source verification and independent review.
~~~

## 3. New data sources: CSV, Parquet, images, API snapshots, model outputs, no data

There is **no dataset name hardcoded in the new execution harness**. Define input files in research/<slug>/protocol.json:

~~~json
{
  "inputs": [
    {
      "name": "readings",
      "path": "data/sensor_readings.csv",
      "sha256": null
    }
  ]
}
~~~

The rest of protocol.json must retain all original required fields. The input path is relative to repository root and cannot escape it. The runner receives inputs["readings"] as a pathlib.Path pointing to the actual file; it can load CSV, JSON, Parquet (with dependencies you install), images or arbitrary bytes.

For exploratory runs, a missing expected sha256 is allowed; the system still hashes the bytes and records the observed SHA256 and file length in the manifest. For confirmation, an explicit SHA256 is **mandatory**. Get SHA256 by Python:

~~~bash
python -c "import hashlib,pathlib; p=pathlib.Path('data/sensor_readings.csv'); print(hashlib.sha256(p.read_bytes()).hexdigest())"
~~~

Use the printed digest in protocol.json. For a large file, calculate the hash in chunks to avoid loading it all into memory. You may store dataset snapshots outside the repository, but the current harness accepts only files **within repository root**: place files in the ignored data/ directory, or implement a trusted adapter to materialize external content first.

This handles arbitrary formats **through your runner code**; it does not include built-in Parquet parsing, statistical tests, cloud connectors or automatic validity checking.

## 4. Protocol phases

**Exploratory** (default): phase exploratory, frozen false. You may change the research question and create a new run, but if an earlier run was recorded, the default auditor flags protocol and runner drift. Preserve prior runs and start a new protocol/project version rather than rewriting history if you need both audits to pass.

**Confirmatory**: first complete the exploratory analysis and specify a *new protocol* before seeing held-out labels. Set phase confirmatory and frozen true. Hash all inputs, freeze the protocol, then run:

~~~bash
python -m research_lab.study freeze sensor-reliability
python -m research_lab.study run sensor-reliability
python -m research_lab.study audit sensor-reliability --replay
~~~

The freeze command creates freeze.json, recording the exact protocol, runner and input fingerprints. It cannot overwrite an existing freeze file. A confirmation run refuses mismatched data, protocol or code.

**Critical limitation:** A Git-tracked freeze file is version evidence, not independent preregistration. For publishable science, archive the freeze and protocol timestamp in a trusted external service before opening the held-out target data. Also reserve independent reviewers, correct statistical methods and a valid uncertainty design.

Never repurpose an existing exploratory project into confirmation if you need to preserve its older registry; create a new project ID such as sensor-reliability-confirm-v1.

## 5. What verification means

~~~bash
python -m research_lab.study audit sensor-reliability
python -m research_lab.study audit sensor-reliability --replay
~~~

Basic audit checks the project registry, recorded artifacts, code hash, protocol hash and each available input fingerprint. Replay audit re-executes experiment.py and compares the serialized result **byte-for-byte**. For stochastic experiments, use only protocol-declared random seeds and deterministic operations where possible; if the scientific method is fundamentally nondeterministic, document a scientifically justified reproducibility tolerance in a new reviewed adapter rather than weakening the strict generic checker.

The harness runs experiment.py as trusted local Python code. It is **not a security sandbox**. Review scripts before executing, especially if they came from the internet or an agent.

A passed replay test does not mean the statistics are appropriate, the experiment's assumptions hold, the datasets are legally reusable, the literature is correct, or the findings are novel. Those are separate human scientific gates.

## 6. Run tests, CI, and track experiments

Check environment and tests:

~~~bash
python -m unittest discover -s tests -v
python -m research_lab.cli audit
~~~

The GitHub repository workflow also tests the generic no-data project and its replay. When a new study needs a large dataset, implement a project-specific CI job that downloads a pinned source, executes run, audits outputs and retains permitted derived evidence as a workflow artifact. Never upload raw private datasets or credentials.

Working on parallel hypotheses? Use different git worktrees and *different project slugs*. The project registry is append-only but **single-writer**; it is not safe to have concurrent writes to one project registry without a transactional backend or lock.

## 7. Examples of problems supported by the new architecture

| Domain | Data adapter (your runner) | Testable research question |
|---|---|---|
| Forecasting / pricing | Historical transactions, time series and cost parameters | When does cost-aware model selection outperform horizon-matched accuracy selection? |
| Agentic coding | Commit states, verified test outcomes, token and walltime logs | Under fixed budget, does a coding-agent reviewer catch defects beyond automated tests? |
| Industrial anomaly detection | Vibration/telemetry with labeled faults and deployment metadata | Under which shifts do calibrated anomaly alarms degrade? |
| AI operations | Model event logs, monitoring traces and incidents | Can a change-detection rule improve detection delay at a fixed false-alarm budget? |
| Scientific methodology | Experiment results, paper metadata and protocol records | Does independent adversarial review change unsupported-claim rate? |
| Synthetic theory research | **No dataset**; deterministic simulator and seeds | Does an estimator satisfy predicted error bounds under specified assumptions? |

**No new data adapter, credible scientific baseline, or novel claim is automatically supplied for these domains.** The platform reduces repeated infrastructure work; the domain-specific science remains real work.

## 8. Exit gates for a serious new study

1. A scientific question and meaningful reader decision.
2. Evidence matrix verified against primary literature, with unresolved novelty explicitly marked.
3. Falsifiable primary hypothesis, H0 and alternatives.
4. Pinned data and split specification; genuinely sealed test cases.
5. Baseline, metric, uncertainty, compute budget and negative controls.
6. Passing unit tests, complete case-level evidence and replay where feasible.
7. Independent critical review, sensitivity analysis and explicit GO/REVISE/STOP.
8. Publication requires additional original, externally credible evidence. The harness never authorizes it automatically.

**Use it as a research operating system, not an algorithm that automatically discovers publishable results.**
