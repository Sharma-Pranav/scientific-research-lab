# Scientific Research Lab — operator guide

**Audience:** researchers and AI engineers using Python, Git and Codex.  
**Verified repository status:** research harness and two M5 development experiments are on the default branch. The latest history-length study completed with 32 passing repository tests and a successful data/evidence workflow as of 2026-11-01.  
**Scientific status:** exploratory research only. No original, externally validated, publication-ready contribution has been established.

This repository is a **research execution and verification harness**, not a push-button autonomous scientist. Python executes experiments; Git records protocols; Codex helps develop questions, methods, implementations and critical reviews. The human research director must approve the question, source interpretation, experiments and claims.

## 1. What it does — and what it does not

Capabilities already implemented:

- Repository-wide scientific rules (AGENTS.md), five optional Codex skills, research templates and project-specific protocols.
- A self-contained synthetic robust-estimation pilot, with append-only JSONL registry and artifact hashes.
- A separate AR(1) lead-time policy simulation, with analytic benchmark and deterministic replay verification.
- Real M5 retail-series development experiments with historical forecast selection, quantitative loss evaluation, stored derived case-level outputs and automated audits.
- An exploratory study changing historical validation length (1, 3, 6, 12 windows) with daily and policy-oriented control comparisons.
- Automated methodology tests and GitHub Actions jobs that create auditable evidence without uploading raw M5 records.
- Recorded negative findings, limits and an internal adversarial review.

Not implemented:

- Fully autonomous literature search with trustworthy fact checking or automatic originality assessment.
- A generic experiment executor for arbitrary datasets or model libraries; each new study needs its own runner and validation.
- A secure external preregistration service, tamper-proof evidence store, or blinded independent peer review.
- A model with a verified novel contribution; a manuscript accepted for publication.
- Proper cost-matched inventory simulation with real replenishment/stockout economics. Matching a number of scored losses is **not** matching CPU time or information.

**Terminology:** A passing CI check means the code, selected mathematical consistency checks and specified provenance rules passed. It does **not** mean a research hypothesis is true or novel.

## 2. Getting started (Windows, macOS, Linux)

Prerequisites: Git, Python 3.10 or newer, and optional Codex access through the Codex extension or CLI. The provided runtime and tests require no pip-installed third-party packages. You do not need to set up a cloud account to run the synthetic examples. The M5 examples require a third-party source file and network access unless you provide it locally.

Clone and enter the repository:

~~~bash
git clone https://github.com/Sharma-Pranav/scientific-research-lab.git
cd scientific-research-lab
git switch main
git pull --ff-only
python --version
python -m unittest discover -s tests -v
~~~

On Windows, use PowerShell or the VS Code terminal. If Python is installed as py rather than python, replace python with py -3.11 in examples. Prefer the same supported Python version as CI for reproducibility (currently 3.11).

Expected behavior for the verified main commit: all 32 tests pass. A later commit may change the count. If tests fail, **record the failure** and fix it before beginning a new study; do not infer that prior CI success proves your local environment.

Next check the shipped synthetic evidence and its gates:

~~~bash
python -m research_lab.cli gate research/robust-location/proposal.json
python -m research_lab.cli audit
python -m research_lab.evidence research/robust-location/evidence_matrix.csv research/leadtime-dependence/evidence_matrix.csv research/selection-transfer/evidence_matrix.csv
~~~

The gate must report STOP for publication on the legacy pilot. The registry audit is for the historical robust-location runs; it is distinct from the separate real-data M5 audit commands. Evidence matrix validation only checks **form** and URLs, not the truth of papers or novelty.

## 3. Open and operate with Codex

Open this repository's root directory in VS Code and use Codex in that workspace, or launch Codex CLI from the repository root if you have it configured. Codex can read AGENTS.md, and the project includes five repo-local skills in .agents/skills. See the official Codex documentation for current installation and product availability: https://developers.openai.com/codex/

The division of responsibility is deliberate:

| Human / researcher | Codex | Deterministic scripts and CI |
|---|---|---|
| Select decision-relevant scientific question and whether it is worth pursuing | Draft questions, find comparable mechanisms, challenge hypotheses | Validate files, schema, tests and published execution outputs |
| Confirm citation meaning and novelty after reading primary sources | Collect candidate literature and overlap matrix | Check evidence-matrix structure, not truth |
| Approve splits, frozen protocols, costs, budgets and baselines | Propose/test code on an isolated branch | Execute runs, check invariants, hash outputs, recalculate case-level regret |
| Decide when to abandon an idea or make public claims | Produce a skeptical review with explicit counterexamples | Report reproducibility and CI results, never automatically grant publication GO |

Ask Codex to use the relevant skill explicitly by name when appropriate (for example, $literature-verification). If your Codex interface does not expose skill invocation, ask it to read the specific SKILL.md path and follow its instructions. Skills are *procedural prompts*, not callable Python functions and not independent autonomous agents.

**Five skills and when to use them:**

| Skill | File | Deliverable |
|---|---|---|
| literature-verification | .agents/skills/literature-verification/SKILL.md | Evidence matrix with primary locators, support status and overlaps |
| hypothesis-generation | .agents/skills/hypothesis-generation/SKILL.md | H0, alternative mechanisms, refutable predictions and discriminating tests |
| experiment-design | .agents/skills/experiment-design/SKILL.md | Concrete protocol, splits, metrics, seeds, matched baselines and negative controls |
| falsification | .agents/skills/falsification/SKILL.md | Fragility, leakage, competing explanations and counterexamples |
| independent-review | .agents/skills/independent-review/SKILL.md | Skeptical claim/evidence/warrant review and GO/REVISE/STOP recommendation |

Starter Codex task to **understand the repository**, without changing it:

~~~text
Inspect AGENTS.md, docs/USER_GUIDE.md, the research/selection-transfer protocols,
research_lab/m5_baselines.py, research_lab/m5_history.py and the relevant tests.
Explain the research workflow as it actually exists. Distinguish code that has
executed successfully, scientific assumptions, and missing capabilities.
Do not edit files or claim a study is publishable.
~~~

## 4. Fastest first exercise: inspect an existing negative result

Read in this order:

1. research/selection-transfer/m5_data_and_protocol.md — problem, source and temporal holdouts.
2. research/selection-transfer/m5_development_results.md — first real-data benchmark, with performance that did not favor longer replay.
3. research/selection-transfer/history_length_protocol.md — what was specified before the second run.
4. research/selection-transfer/history_length_results.md — 1/3/6/12-window comparison and counterexamples.
5. reviews/m5-history-falsification-review.md — why those results do not establish the proposed causal explanation.
6. GitHub Actions: successful history-length run https://github.com/Sharma-Pranav/scientific-research-lab/actions/runs/41312725714 and harness test run https://github.com/Sharma-Pranav/scientific-research-lab/actions/runs/41312725717.

**What the study found:** the best lookback length changed with decision horizon and critical fractile. In particular, a shorter-history advantage at the 0.50 fractile was sensitive to one store, TX_2; approximate store-cluster intervals crossed zero. The appropriate conclusion is inconclusive and heterogeneous, **not** that long history is inherently harmful.

Ask Codex:

~~~text
Use $independent-review. Read the history_length_protocol.md,
history_length_results.md and reviews/m5-history-falsification-review.md.
Extract each permitted result, its exact evidence source, the strongest
counterargument and a potential falsification. Do not assert a causal drift
mechanism or statistical significance. Recommend the smallest next test
that could overturn our interpretation.
~~~

## 5. Run the synthetic exercises locally

### 5A. Robust-estimation pilot

The project already contains two committed robust-location runs. You can audit them without creating new files:

~~~bash
python -m research_lab.cli audit
~~~

To create another **exploratory** robust-estimation run:

~~~bash
python -m research_lab.cli pilot --phase exploratory
python -m research_lab.cli audit
git status --short
~~~

The runner creates a new subfolder in runs/ and appends to registry/experiments.jsonl. **Do not casually commit your local trial to the shared historical registry.** Run experiments on a separate branch or throwaway clone, inspect the artifacts, and review what should be retained.

The pilot can run confirmatory mode using the frozen example, but this is an educational synthetic experiment. A frozen flag does not equal independent or prospective preregistration.

### 5B. Synthetic AR(1) lead-time experiment

Use an unused output path. Output creation intentionally fails when the directory already exists:

~~~bash
python -m research_lab.leadtime --config research/leadtime-dependence/exploratory.json --output research-output/ar1-my-exploration
python -m research_lab.leadtime --verify --config research/leadtime-dependence/exploratory.json --output research-output/ar1-my-exploration
~~~

The program writes config.json, results.json and manifest.json. The verifier checks hashes, protocol and implementation identity, and deterministically replays the simulation in the current environment. For the predefined confirmatory configuration, use:

~~~bash
python -m research_lab.leadtime --config research/leadtime-dependence/confirmatory.json --output research-output/ar1-my-confirmation
python -m research_lab.leadtime --verify --config research/leadtime-dependence/confirmatory.json --output research-output/ar1-my-confirmation
~~~

**Interpretation:** the ranking reversal is a known result in inventory and correlated demand research. This pilot validates engineering mechanics, not a new statistical theorem or novel scientific contribution.

## 6. Run the M5 real-data benchmark

### 6A. Data rights and source requirements

The original M5 competition data are associated with Kaggle competition rules:
https://www.kaggle.com/competitions/m5-forecasting-accuracy/data

The existing scripts use this M5 Zenodo mirror:
https://zenodo.org/records/10203108

Before downloading or publishing derived materials, review applicable competition terms and dataset license/reuse conditions. A publicly accessible mirror is **not** automatically an unrestricted research license. The code checks the published MD5 26a366a25beb57b0a8f4c7b148758f94. MD5 is a legacy provenance check, not proof against deliberate malicious substitution; the scientific protocol identifies the source.

The code reads the M5 file into memory, including the Wisconsin series and final 112 days, while sampling. Their **evaluation and model-selection outcomes are excluded** by the existing guardrails. This is a *procedural* sealed holdout, not inaccessible encrypted storage; do not inspect those labels, and use physically separated holdouts for stronger future confirmation.

Raw downloaded data live under data/raw/ and are Git-ignored. Never put the source file in a PR, chat transcript, workflow artifact or committed result package.

### 6B. First baseline: 48-series development evaluation

If an authorized CSV already exists at the default path, omit --download. Otherwise, and only if permitted to use the mirror:

~~~bash
python -m research_lab.m5_baselines --config research/selection-transfer/m5_development.json --output research-output/m5-my-baseline --download
python -m research_lab.m5_baselines --config research/selection-transfer/m5_development.json --output research-output/m5-my-baseline --verify
~~~

This performs eight rolling origins for 48 CA/TX development SKU-store series, two lead times and two cost ratios: **1,536 series-origin-decision cases**. Four fixed forecasting methods are ranked by (a) previous one-day pinball loss, (b) three-window policy-loss replay, and (c) twelve-window policy-loss replay. It computes hindsight regret relative to the best available candidate on each evaluation window.

What to inspect after it finishes:

- research-output/m5-my-baseline/config.json — exact input protocol.
- research-output/m5-my-baseline/results.json — dataset fingerprint, 1,536 case records and four summary settings.
- research-output/m5-my-baseline/manifest.json — hashes to check the saved evidence.
- research/selection-transfer/m5_development_results.md — known executed reference results.

An unchanged deterministic run should reproduce the reference results in a compatible Python environment. If it does not, compare configuration, source checksum and code commit before attributing a discrepancy to science.

### 6C. History-length falsification study

Uses the same source and development panel, but tests 1, 3, 6 and 12 historical windows and three selection families:

~~~bash
python -m research_lab.m5_history --config research/selection-transfer/history_length_exploratory.json --base-config research/selection-transfer/m5_development.json --output research-output/m5-my-history --download
python -m research_lab.m5_history --config research/selection-transfer/history_length_exploratory.json --base-config research/selection-transfer/m5_development.json --output research-output/m5-my-history --verify
~~~

The program examines the same 48 CA/TX series and 1,536 scenarios, producing 12 selection choices per case (4 history lengths × 3 evaluation families). The procedure includes a past-only mean-shift proxy for demand instability.

Important: the matched-daily comparator uses the same *count* of loss evaluations as the aggregated policy comparator, but does **not** equalize CPU time, total information or the statistical target. Do not describe it as compute-matched.

### 6D. Use GitHub Actions instead of downloading M5 locally

At the repository on GitHub, select **Actions** and the workflow:

- **M5 real-data development baselines**; or
- **M5 history-length falsification (exploratory)**.

Choose **Run workflow**, select the intended reviewed branch (prefer main), and start it. The workflow downloads the pinned data, performs tests and the scientific protocol, audits outputs, and uploads **derived evidence only**. In the completed workflow run, open **Artifacts** and download the named evidence ZIP. It contains config.json, results.json and manifest.json.

Artifacts may expire under GitHub retention policy; commit a concise signed/hashed results report and review, not the third-party raw data. A workflow run alone does not establish independent replication or publication readiness.

## 7. How to read the outputs

| Field | Meaning | Frequent mistake |
|---|---|---|
| protocol_sha256 / config_hash | Hash of exact configured parameters | Treating a hash as a scientific preregistration |
| dataset md5 / sample_id_sha256 | File and identifier-sampling provenance | Assuming MD5 proves legality or all data semantics |
| candidate_costs | Hypothetical inventory-style loss for each fixed forecasting method | Treating loss as observed monetary savings |
| ex_post_best / ex_post_oracle_cost | Minimum cost among tested methods **after** seeing evaluation data | Treating hindsight as deployable model selection |
| regret | Cost of selected method minus hindsight best in that case | Claiming regret is causal or globally optimal |
| daily_full_k | Choose by k past full daily windows | Comparing its evaluation count directly with lead-time loss |
| daily_matched_k | Choose by k past daily windows, but score 28/L fixed positions | Calling equal loss counts equal computational effort |
| policy_k | Choose by k past lead-time aggregated policy windows | Claiming more windows necessarily means more robust evidence |
| approx_*95ci | Descriptive interval using small dependent SKU/store blocks | Claiming statistical significance or coverage guarantees |

Lower regret is desirable within the *specific* metric and candidate set. Uncertainty, units, lead time, cost assumptions, and sample dependence always matter.

## 8. How to begin a NEW research question

This is the core way to compound your work: reuse the rules and methods, but create a new **question-specific** experiment. The repository does not automatically generate a working new runner.

### Step 1 — Set up isolated work

~~~bash
git switch main
git pull --ff-only
git switch -c research/your-question-slug
~~~

Create research/your-question-slug/ and copy templates/research_proposal.md. Do not edit another study's frozen protocol just to obtain a better result.

Ask Codex:

~~~text
Use $hypothesis-generation. Create research/your-question-slug/proposal.md
from templates/research_proposal.md.
Topic: [what is studied].
Question: [exact unknown relationship].
Significance: [which reader/decision becomes better informed].
Give H0, H1 and at least two credible alternatives; for each, specify a
result that would falsify it, a strong baseline, expected cost and a cheap
pilot. Do not write code yet and do not claim scientific novelty.
~~~

### Step 2 — Audit relevant prior literature

Create evidence_matrix.csv using columns:

~~~text
claim,source_url,exact_evidence,status,relationship_to_project
~~~

Ask Codex to use $literature-verification to find the *closest equivalent* research, not just superficially similar paper titles. A source is VERIFIED only after the author or a trusted reviewer has checked the actual primary paper and precise claim. Reading metadata or seeing an abstract is not enough for detailed mechanism claims.

Validate form only:

~~~bash
python -m research_lab.evidence research/your-question-slug/evidence_matrix.csv
~~~

Even a PASS here does not say references were checked or that the paper is novel.

### Step 3 — Design a falsification-oriented protocol

Use templates/experiment_protocol.md. Specify before execution:

- Population, dataset provenance, unit of analysis, train/validation/holdout boundaries, and who may see test labels.
- Target horizon, costs, evaluation metric, baseline models and matched resource budget.
- Separately registered exploratory versus confirmatory comparisons, negative controls, ablations and sensitivity checks.
- Seed and randomness policy, effect-size threshold, uncertainty method, multiple comparison treatment and stopping rules.
- The exact outcome that would make you **reject** the idea.

Prompt:

~~~text
Use $experiment-design. Read the verified evidence matrix and proposed
hypotheses. Propose the smallest reproducible experiment on development
data only. Specify data availability, timestamp leakage risks,
baseline fairness, metrics, uncertainty, budgets and falsifiers.
First create a protocol and test plan; leave all sealed holdouts untouched.
Implement only after the protocol is reviewed.
~~~

### Step 4 — Implement small, test thoroughly

Write a self-contained module in research_lab/, unit tests in tests/, and (when needed) a GitHub Actions workflow under .github/workflows/. Before asking for results, demand that the implementation:

- Fails if the protocol is malformed, hashes differ or the holdout gets used.
- Produces case-level evidence and an auditable summary, not only a formatted table.
- Has negative controls and a known analytical/simple benchmark where possible.
- Supports re-running on an empty output directory; preserves earlier results.
- Keeps raw third-party or private datasets out of the repository and workflow artifacts.

### Step 5 — Execute on development data, challenge the finding

Run tests, execution and artifact audit. Compare empirical results against at least one independent calculation. Explicitly list failed runs and sensitivity or counterexamples; never delete negative findings.

Prompt:

~~~text
Use $falsification. Challenge the new experiment without trying to
make the paper look better. Check leakage, weak baselines, statistical
unit, uncertainty, multiple comparisons, cost mismatch, data regime,
selection bias, and whether one group drives the apparent effect.
Create a critical review with tests that could reverse the conclusion.
Preserve unsuccessful results and do not unseal final test data.
~~~

### Step 6 — Independent review and GO/REVISE/STOP

Start an isolated Codex thread or Git worktree with a reviewer who sees the protocol, evidence matrix and artifacts, not the researcher's desired explanation:

~~~text
Use $independent-review. Using only the protocol, verified evidence
matrix, case-level results, manifests and tests, independently assess:
claim, reasons, observed evidence, acknowledgement of alternatives,
warrant, uncertainty, novelty overlap, and false-positive risks.
Give separate significance, novelty, feasibility and evidence gates.
Recommend GO/REVISE/STOP. Do not authorize publication.
~~~

The human researcher makes the final decision. A promising exploratory result is not permission to inspect reserved test data repeatedly. For actual confirmatory work, precommit a frozen protocol in a location and process independent of the final-test evaluation; test once or use a planned sequential design.

### Step 7 — Publish only evidence-supported work

Before drafting a manuscript: check primary-source novelty, independent replication or analytic cross-check, robust baselines, uncertainty and sensitivity, and the validity of using the data. Then use templates/manuscript_outline.md. Write only what the artifacts support, including limitations and negative results. A public technical report or reproducible benchmark can be a useful asset even if novelty is insufficient for peer-reviewed publication; label it accurately.

## 9. Git worktrees and parallel hypotheses

You do not need autonomous multi-agent orchestration. Independent Git worktrees provide useful isolation and can be reviewed/merged one at a time:

~~~bash
git worktree add ../research-h1 -b research/hypothesis-h1
git worktree add ../research-h2 -b research/hypothesis-h2
~~~

Open each worktree as a separate Codex workspace/thread. Do not let two concurrent processes append to the same registry/experiments.jsonl or write the same runs/ directory. Worktrees share Git object storage but have separate working directories. Use unique protocol IDs and output paths. Commit protocols, code and reviews with clear provenance; merge only after the corresponding CI and independent-style review pass.

## 10. Troubleshooting

| Symptom | Likely cause | Corrective action |
|---|---|---|
| Python cannot import research_lab | Command run outside repository root | Change directory to the cloned repository |
| An output directory already exists | Deliberate write-once artifact creation | Use a new name; do not overwrite recorded research |
| M5 download fails | Network restrictions, source outage or permission | Supply a legitimately obtained file via --data; never bypass the source checksum silently |
| M5 checksum mismatch | Wrong version or incomplete/corrupted file | Compare source manifest and expected version; stop rather than change checksum to fit |
| Protocol hash mismatch | JSON values, formatting canonicalization or parameters changed | Restore the exact frozen protocol; create a new protocol ID for real revisions |
| A GitHub workflow passes, but the result differs locally | Python/software, code revision, source file or floating-point environment differs | Record environment, Git commit, protocol and result hashes and investigate |
| Evidence-matrix validation passes | Only schema/source fields were checked | Manually read and cross-check substantive claims before marking VERIFIED |
| Novelty remains STOP | Existing literature overlaps or no distinct evidence | Improve the question, test a new mechanism, or publish an accurately labeled replication |
| Apparent strong result disappears in one store or time slice | Confounding or selection instability | Keep negative result and run stronger, separately specified validation; do not cherry-pick |
| No paper produced | The repo is a research tool, not a paper generator | Establish new contribution, independent validation, and publication readiness separately |

## 11. What should happen next for this particular research program

Do not invest in a drift-warning model on the current negative study. Highest-leverage next experiments, in order:

1. Add competitive probabilistic forecast baselines on the same development-only M5 boundaries and reproduce the existing simpler methods exactly.
2. Measure **actual CPU/runtime and inference/training cost**, not merely scored loss counts, for partial/full policy replay; match budgets between selection strategies.
3. Implement at least one independently verified related-work method (forecast congruence / robust model selection) and audit exact conceptual overlap.
4. Only after those survive falsification, preregister a candidate selection-risk diagnostic, keep Wisconsin and the final 112 days sealed, and plan an appropriate confirmatory evaluation.

A manuscript is a downstream deliverable, not a success criterion for the next coding iteration. Good scientific evidence may justify a STOP. That is a successful use of this system.
