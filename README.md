# Scientific Research Lab — v0.1

A deliberately small Codex research harness: evidence-gated scientific workflow, isolated Git worktrees, append-only experiment registry, artifact audit and reproducible simulation pilot. **It does not autonomously establish scientific novelty or publication readiness.**

## Quick start

Requires Python >=3.10; runtime has no third-party dependencies. From repository root:

```bash
python -m research_lab.cli gate research/robust-location/proposal.json
python -m research_lab.cli pilot --phase exploratory
python -m research_lab.cli pilot --phase confirmatory
python -m research_lab.cli audit
python -m unittest discover -s tests -v
```

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

The robust-location pilot tests engineering reproducibility, *not a novel statistical result*. This project contains no literature verification or real-world dataset validation. A valid audit is not a guarantee of non-tampering by someone able to rewrite the entire repository. Use signed commits / write-once external storage for stronger provenance.
