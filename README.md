# Scientific Research Lab

## Start here — research on any problem

This is a **dataset-independent research workspace**, not an M5-only forecasting project. Use Codex to help design and challenge a study; use the Python harness to execute and audit it. **Start with a falsifiable question, not with a model or a preferred conclusion.**

1. **Frame the question.** State why it matters, what outcome would falsify the hypothesis, and the strongest competing explanation.
2. **Check existing research.** Use the five Codex research skills to verify primary literature, novelty, methods, baselines, and counterarguments before implementing a solution.
3. **Choose data deliberately.** **Prefer curated, well-documented research datasets** from trusted sources (for example, official benchmark maintainers, institutional repositories, and dataset archives). Check provenance, version, license/reuse permissions, data dictionary, target labels, quality, and predefined splits. Prefer realistic datasets over convenient but weak ones. Use synthetic data for unit tests and controlled mechanisms, **not** as a substitute for real-world validation. If no credible curated dataset fits, document the trade-off and use a justified alternative; some simulation/theoretical studies need no dataset.
4. **Scaffold and implement.** Create a project, replace the generated **toy** experiment with domain-specific logic and strong baselines, then freeze a confirmatory protocol only after exploratory decisions are complete.
5. **Run, verify, challenge.** Execute the study, replay-audit artifacts, investigate failures and negative outcomes, and require an independent scientific review before any publication claim.

```bash
git clone https://github.com/Sharma-Pranav/scientific-research-lab.git
cd scientific-research-lab
python -m unittest discover -s tests -v
python -m research_lab.study init my-question --title "A falsifiable research question"
# Edit research/my-question/{proposal.md,protocol.json,experiment.py,evidence_matrix.csv}
# Replace the scaffolded toy runner before interpreting scientific results.
python -m research_lab.study run my-question
python -m research_lab.study audit my-question --replay
```

**Codex starter prompt:**

> Read `AGENTS.md` and `docs/NEW_RESEARCH_PROJECT.md`. Help investigate **[my research question]** using the five research skills. Check closest prior work and scientific novelty; prefer credible curated datasets with clear provenance, valid reuse rights and appropriate splits; formulate competing falsifiable hypotheses; define strong baselines, uncertainty, and leakage controls; implement a trusted project-specific runner; execute and replay-audit results; conduct an adversarial review. Keep exploratory and confirmatory evidence separate. Report actual tests, sources, limitations, and GO / REVISE / STOP gates. Do not claim novelty or publication readiness without evidence.

**Guides:** [New project tutorial](docs/NEW_RESEARCH_PROJECT.md) · [Full operator guide](docs/USER_GUIDE.md) · [Two-problem cross-domain validation](docs/TWO_PROBLEM_RESULTS.md).

A deliberately small Codex research harness: evidence-gated scientific workflow, isolated Git worktrees, append-only experiment registry, artifact audit and reproducible simulation pilot. **It does not autonomously establish scientific novelty or publication readiness.**

**Start here:** [Detailed operator guide](docs/USER_GUIDE.md) — installation, Codex skills, exact commands, GitHub Actions, interpreting evidence, new research workflows, and troubleshooting.

**Status:** the repository supports repeatable research engineering and real-data exploratory experiments. The M5 studies were executed and verified in GitHub Actions. Scientific novelty and a publication-ready result remain **unproven**.

## Quick start

Requires Python >=3.10; the core and tests have no third-party runtime dependencies. From repository root:

```bash
python -m unittest discover -s tests -v
python -m research_lab.cli audit
python -m research_lab.cli gate research/robust-location/proposal.json

# Independent new research project; no M5 file needed
python -m research_lab.study init demonstration-question --title "Can this test be reproduced?"
python -m research_lab.study run demonstration-question
python -m research_lab.study audit demonstration-question --replay
```

The new project begins with a reproducible **toy experiment**; replace it before making scientific claims. For the older robust-estimation pilot, `python -m research_lab.cli pilot --phase exploratory` appends new records to a shared legacy experiment registry; use a separate worktree/clone and review before committing anything.

`pilot` writes immutable `runs/<run-id>/{config.json,results.json,manifest.json}` artifacts and appends a record to `registry/experiments.jsonl`. `audit` recomputes content hashes and verifies registry consistency; it does not prove that an experiment is scientifically valid. Each pilot experiment is independent, and a confirmation protocol must have been frozen before execution. **Do not edit an existing confirmatory protocol after inspecting its data**; amend under a new protocol ID. For demonstrations, sample sizes are intentionally small.

## Scientific phases

1. Specify topic, question, reader-facing significance, falsifying outcome and baseline.
2. Record verified primary-source citations and closest prior art in `evidence_matrix.csv`. Treat unverified novelty as **STOP**.
3. Generate H0/H1/H2 and freeze a discriminating experimental protocol.
4. Run exploration with full logging. Freeze confirmation before inspecting its results.
5. Execute confirmation, calculate uncertainty, inspect sensitivity and ablations where appropriate, and retain failures.
6. Ask an independent reviewer in a fresh Codex thread/worktree to audit artifacts and update a review template.
7. Decide GO/REVISE/STOP using gates. The supplied pilot must return **STOP** for publication novelty.

## Codex usage

Open the repository as Codex workspace. Codex reads `AGENTS.md`; reusable skills live under `.agents/skills/<name>/SKILL.md`. To explore competing hypotheses in parallel without interference:

```bash
git worktree add ../lab-h1 -b research/h1
git worktree add ../lab-h2 -b research/h2
# Run distinct Codex tasks in these directories. Merge only after independent review.
```

Avoid parallel writes to the same `registry/` or `runs/` folder; import completed run packages through reviewed commits. The reviewer should start in a separate worktree without the researcher's conversational context.

## Limits

The robust-location pilot tests engineering reproducibility, *not a novel statistical result*. Literature claims are represented in matrices and require manual verification; subsequent M5 real-data research studies were executed but do not establish novel scientific claims. A valid audit is not a guarantee of non-tampering by someone able to rewrite the entire repository. Use signed commits / write-once external storage for stronger provenance.

## Research-integrity V0.2

The selection-transfer project remains a **research candidate**. Two real-data M5 development studies have been executed and documented; no scientific novelty has been established. Begin with the [operator guide](docs/USER_GUIDE.md), the M5 results and the adversarial reviews, not manuscript drafting.

Mechanical controls:

```bash
python -m unittest discover -s tests -v
python -m research_lab.evidence research/robust-location/evidence_matrix.csv research/leadtime-dependence/evidence_matrix.csv research/selection-transfer/evidence_matrix.csv
python -m research_lab.leadtime --config research/leadtime-dependence/exploratory.json --output research-output/exploratory
python -m research_lab.leadtime --verify --config research/leadtime-dependence/exploratory.json --output research-output/exploratory
python -m research_lab.leadtime --config research/leadtime-dependence/confirmatory.json --output research-output/confirmatory
python -m research_lab.leadtime --verify --config research/leadtime-dependence/confirmatory.json --output research-output/confirmatory
```

Output directories must not already exist. The verifier checks exact protocol and implementation fingerprints, result hashes, and deterministic replay *in the same environment*. It cannot establish scientific validity, secure preregistration or historical novelty.

Evidence CSV schema is `claim,source_url,exact_evidence,status,relationship_to_project`. The structural checker does not visit URLs or verify substantive source assertions. All-GO gate states return `HUMAN_REVIEW_REQUIRED`, never automatic publication approval.

`research_lab.splits.rolling_origin` creates time-ordered fold boundaries with an optional embargo and sealed final holdout; `stable_group_partition` holds out complete groups. These utilities cannot by themselves prevent target or feature leakage.

## M5 real-data development benchmark (2026-11-01)

The first real-data experiment is implemented in `research_lab/m5_baselines.py`. It uses an MD5-pinned M5 source file and fixed identifier-only SKU selection, protects the last 112 days and Wisconsin holdout, and compares historical daily pinball model selection with partial and full lead-time cost validation. It does **not** test a proposed new screening method or support a publication claim.

- Protocol and data permissions: [research/selection-transfer/m5_data_and_protocol.md](research/selection-transfer/m5_data_and_protocol.md)
- Executed results and SHA256 provenance: [research/selection-transfer/m5_development_results.md](research/selection-transfer/m5_development_results.md)
- Independent-style critique: [reviews/m5-development-internal-review.md](reviews/m5-development-internal-review.md)
- Reproducible workflow: [.github/workflows/m5-development.yml](.github/workflows/m5-development.yml)

A zero-dependency local run requires an authorized M5 CSV and can download the public Zenodo mirror when permitted. The GitHub workflow does not upload raw data; only derived research artifacts.

## Exploratory M5 history-length falsification (2026-11-01)

The research lab now has a separately audited extension measuring whether historical policy-validation lookback length (1/3/6/12 windows) improves out-of-window forecast selection. Three selection families are evaluated: policy loss, full daily pinball and daily pinball matched by loss-count (not CPU). The study uses the same CA/TX development panel; Wisconsin and the final 112 days remain unused for scoring.

- [Predetermined exploratory protocol](research/selection-transfer/history_length_protocol.md)
- [Actual results, provenance, and disconfirming sensitivity](research/selection-transfer/history_length_results.md)
- [Adversarial methodological review](reviews/m5-history-falsification-review.md)
- [Research execution workflow](.github/workflows/m5-history.yml)

The observed history-length effect is inconsistent and heavily influenced by particular stores. No novelty, causal mechanism, or publication claim is established. **Publication gate: STOP.**

## Tested against two unrelated research problems

A new integration suite uses the same generic research runner for **checksum-pinned synthetic industrial sensor CSV data** and a **dataset-free randomized A/B significance simulation**. Both executed on GitHub Actions, passed deterministic replay audits and preserved separate projects. This confirms execution-layer portability, not scientific novelty or validity on real industrial datasets.

- [Full cross-domain execution report](docs/TWO_PROBLEM_RESULTS.md)
- [Exact experiment protocols and limitations](docs/TWO_PROBLEM_VALIDATION.md)
- [GitHub Actions two-problem workflow](.github/workflows/two-research-problems.yml)
