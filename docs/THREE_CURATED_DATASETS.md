# Three curated UCI datasets — real-world portability validation

**Purpose:** Re-check the dataset-independent research framework on three *real curated sources* in different scientific domains. These are engineering reproducibility demonstrations, not publication candidates.

| Source | Domain and task | UCI record | Dataset and expected size | License |
|---|---|---|---|---|
| Iris (Fisher, 1936) | Biology / multiclass classification | [UCI 53](https://archive.ics.uci.edu/dataset/53/iris) | iris.data, 150 rows | CC BY 4.0 |
| Wine Quality (Cortez et al., 2009) | Chemistry / score regression | [UCI 186](https://archive.ics.uci.edu/dataset/186/wine+quality) | winequality-red.csv, 1599 rows | CC BY 4.0 |
| Bike Sharing (Fanaee-T, 2013) | Mobility / chronological demand forecasting | [UCI 275](https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset) | day.csv, 731 rows | CC BY 4.0 |

The official UCI static release ZIP is retrieved for each dataset. Dataset file SHA256, archive SHA256, origin URL, record ID and expected source shape are captured by the acquisition tool. Final protocols must record **pinned source SHA256 values** from an actual successful source run. No raw UCI dataset is committed to Git or uploaded to an artifact.

## How the three evaluation methods are different

- **Iris:** randomly shaped but deterministic SHA256 **row-index split** into training and held-out rows, train-only majority baseline and nearest-class-centroid classifier. Metrics: accuracy and macro F1.
- **Red Wine Quality:** SHA256 row-index holdout, train-only mean quality prediction versus train-fitted alcohol-only ordinary least squares. Metrics: MAE and RMSE. The sensory target is ordinal; continuous interpretation is illustrative.
- **Daily Bike Sharing:** final 120 chronologically later days held out, three rolling, causal one-day-ahead forecasting rules (lag 1, lag 7, trailing mean 28). Forecasts can use previously realized test-day outcomes, never future ones. Metrics: MAE and WAPE. Excludes contemporaneous weather or decomposed count columns to prevent leakage.

All three use **the same** generic \`python -m research_lab.study run <slug>\` and \`audit <slug> --replay\` pipeline. Each retains its own question, protocol, input checksum, runner hash and project-local registry.

## Reproduce in a local clone

~~~bash
python -m unittest discover -s tests -v
python research/curated-three-datasets/acquire.py --root .
python -m research_lab.study run uci-iris-classification
python -m research_lab.study audit uci-iris-classification --replay
python -m research_lab.study run uci-wine-regression
python -m research_lab.study audit uci-wine-regression --replay
python -m research_lab.study run uci-bike-forecasting
python -m research_lab.study audit uci-bike-forecasting --replay
~~~

Data downloads require network access and the UCI source to remain available. If the source changes or a pinned hash mismatches, **STOP** and investigate. Do not change the expected fingerprint merely to get a test green.

## Strict scientific limits

Three curated *real* datasets establish a stronger demonstration of technical portability than synthetic tests, but not scientific novelty, superiority of the simplistic models, independent reviewer validation, or a guarantee that the research platform can autonomously design credible scientific studies in arbitrary domains. Iris is particularly small, Wine Quality is a quality-score proxy, and bike sharing one-step retrospective evaluation is not a deployment.

**Scientific novelty: STOP. Publication: STOP.**
