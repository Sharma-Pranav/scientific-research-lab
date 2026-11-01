# Two research questions: significance and argument validation

**Scope:** This checks the newly integrated three-step significance formula and five-part reader argument on two already executed scientific questions, not only on made-up form entries.

## Question 1 — curated real data, urban mobility forecasting

**Topic:** one-step daily rental forecasting for urban bike-sharing systems.
**Question:** do naive weekly seasonality and recent averages reduce error versus the last observed day on the reserved 120-day interval?
**Reader significance:** help mobility planning analysts understand why intuitive seasonality assumptions require evaluation on future periods.
**Result/claim:** on this test, last-day naive MAE was **918.84**, recent 28-day mean **1,046.57**, and weekly seasonal naive **1,342.27**. The expected improvement from weekly seasonality was **not observed**.
**Warrant boundary:** this warrants a ranking only of the tested rules, data window and online one-step forecast setting. It is not a causal result or general refutation of seasonal demand.
**Source:** [UCI curated-dataset results](THREE_CURATED_DATASETS_RESULTS.md); official Bike Sharing DOI 10.24432/C5W894.

## Question 2 — dataset-free statistical simulation, A/B experiments

**Topic:** multiple interim significance checks in randomized product experiments.
**Question:** under a true null, how much does uncorrected significance monitoring change the probability of a false rejection?
**Reader significance:** help experiment owners and product decision-makers understand when unadjusted interim tests misstate evidence strength.
**Result/claim:** among 7,500 simulated zero-effect experiments, false rejection was **5.12%** final-only, **14.39%** unadjusted any-look and **3.15%** with Bonferroni adjustment.
**Warrant boundary:** exact null, known Gaussian variance and five prespecified looks. No claim about production experimentation platforms, statistical power or novelty.
**Source:** [two-project simulation results](TWO_PROBLEM_RESULTS.md).

## What is tested

Both projects include substantive significance.md worksheets with the three-part reader framing and all five argument sections. The dedicated GitHub Actions workflow:

1. Runs repository tests; validates both framing stages.
2. Retrieves the official Bike Sharing file and checks its pinned SHA256.
3. Runs the curated bike experiment and no-data statistical simulation using their original project protocols.
4. Replay-audits each run and checks that the exact significance worksheet was captured and hashed with each result.
5. Validates both argument stages and independently recomputes decisive numerical comparisons against the saved results.
6. Verifies that circular reader significance, missing responses, and untraceable evidence are **REVISE** outcomes.
7. Explicitly proves a **limitation:** structurally convincing content with an arbitrary, potentially fabricated URL may pass. Source truth, novelty, and scientific inference need human review.

These are retrospective interpretations of earlier exploratory experiments, **not prospectively preregistered new claims**.

## Running from a fresh clone

~~~bash
python -m unittest discover -s tests -v
python -m research_lab.study preflight uci-bike-forecasting --stage framing
python -m research_lab.study preflight sequential-testing-risk --stage framing
python research/curated-three-datasets/acquire.py --root . --expected-hashes research/curated-three-datasets/pinned_sha256.json
python -m research_lab.study run uci-bike-forecasting
python -m research_lab.study audit uci-bike-forecasting --replay
python -m research_lab.study run sequential-testing-risk
python -m research_lab.study audit sequential-testing-risk --replay
python -m research_lab.study preflight uci-bike-forecasting --stage argument
python -m research_lab.study preflight sequential-testing-risk --stage argument
~~~

**Scientific novelty: STOP. Publication: STOP.**
