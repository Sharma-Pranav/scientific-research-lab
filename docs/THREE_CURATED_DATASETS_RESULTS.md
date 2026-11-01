# Three curated UCI real-data studies — results, November 1, 2026

**Purpose:** Test general-purpose research execution on three genuine, independently curated datasets with distinct questions, source formats, split strategies, methods, and metrics. Scientific novelty STOP. Publication STOP.

## Source and execution evidence

The [first successful GitHub Actions execution](https://github.com/Sharma-Pranav/scientific-research-lab/actions/runs/41317604944), on commit 40ea333, checked out the real repository with GitHub Actions, downloaded three official UCI archives, ran **47 tests**, executed all three projects, successfully replay-audited their saved outputs, and uploaded only derived evidence (artifact [13088241113](https://github.com/Sharma-Pranav/scientific-research-lab/actions/runs/41317604944/artifacts/13088241113)). Subsequent runs pin all file fingerprints in research/curated-three-datasets/pinned_sha256.json.

All sources are credited to the UCI Machine Learning Repository and licensed CC BY 4.0. For reuse, preserve source author and DOI attribution.

## A. UCI Iris — classification

Source: R. A. Fisher (1936), Iris, [DOI 10.24432/C56C76](https://doi.org/10.24432/C56C76).

- 150 real plant observations, 4 morphology predictors and 3 species; row-index SHA256 holdout **111 training / 39 test**.
- Baselines trained only on training rows: majority species and nearest feature centroid.

| Method | Accuracy | Macro F1 |
|---|---:|---:|
| Training majority | 30.77% | 0.1569 |
| Nearest centroid | **92.31%** | **0.9259** |

Interpretation: a known simple classifier works well on a small/easy dataset; not a novel scientific finding.

## B. Red Wine Quality — regression

Source: Cortez et al. (2009), Wine Quality, [DOI 10.24432/C56S3T](https://doi.org/10.24432/C56S3T).

- 1,599 real red-wine records; SHA256 holdout **1,289 train / 310 test**.
- Baselines: training-mean sensory quality; univariate training-fitted ordinary least squares using only alcohol.
- Sensory quality is ordinal; using a continuous-error model is only an illustration.

| Method | MAE | RMSE |
|---|---:|---:|
| Training mean | 0.6855 | 0.8302 |
| Alcohol-only OLS | **0.5618** | **0.7459** |

Interpretation: this one-feature predictor improves on a weak baseline, without establishing causality or state-of-the-art quality prediction.

## C. Bike Sharing — daily forecasting

Source: Fanaee-T (2013), Bike Sharing, [DOI 10.24432/C5W894](https://doi.org/10.24432/C5W894).

- 731 real daily rental records; chronological split **611 history / final 120 test days**, 2012-09-03 through 2012-12-31.
- One-step online prediction: previously observed days, including earlier days of the evaluation period, are available; no future weather or target-component data.
- Baselines: last observed day, same weekday last week, recent 28-day mean.

| Method | MAE (daily rentals) | WAPE |
|---|---:|---:|
| Last day | **918.84** | **16.17%** |
| Trailing 28-day mean | 1,046.57 | 18.42% |
| Same weekday last week | 1,342.27 | 23.62% |

Disconfirming observation: simple weekly seasonal naive performs worse than last-day naive in this particular holdout. This does not show that weekly seasonal structure has no predictive value elsewhere.

## Engineering checks and limitations

- Three independent real curated UCI datasets, three domain runners, three source schemas, and multiple split/evaluation strategies: **PASS**.
- Generic study CLI, exact protocol/runner/input fingerprinting, project-isolated registries, saved evidence, deterministic full audit replay: **PASS**.
- Source file SHA256 checks: **PASS** after pinning and re-execution (see the latest GitHub Actions run).
- 47 repository tests passed on initial source execution.
- No dataset source files committed and no raw data uploaded in workflow artifacts.
- **Not established:** automatic scientific method design, novelty, multi-dataset evidence synthesis, causal explanation, competitive modern models, or external deployment reliability.

The test demonstrates software portability, not a universal autonomous scientist.

## Reproduce from a fresh clone

~~~bash
python -m unittest discover -s tests -v
python research/curated-three-datasets/acquire.py --root . --expected-hashes research/curated-three-datasets/pinned_sha256.json
python -m research_lab.study run uci-iris-classification
python -m research_lab.study audit uci-iris-classification --replay
python -m research_lab.study run uci-wine-regression
python -m research_lab.study audit uci-wine-regression --replay
python -m research_lab.study run uci-bike-forecasting
python -m research_lab.study audit uci-bike-forecasting --replay
~~~

Run in a fresh clone/worktree for clean project registries. The source download requires access to official UCI releases; source changes must stop execution until investigated, not silently change pinned hashes.
