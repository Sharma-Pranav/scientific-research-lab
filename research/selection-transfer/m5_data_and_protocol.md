# M5 real-data forecasting baseline: development protocol

**Status: EXPLORATORY. No new selector tested. Novelty/publication: STOP.**

## Data provenance and permission

The original M5 Accuracy data are subject to [Kaggle competition rules](https://www.kaggle.com/competitions/m5-forecasting-accuracy/data). Researchers should review the competition conditions before use. This script defaults to an independently hosted [Zenodo M5 mirror](https://zenodo.org/records/10203108) from the University of Nicosia, using a pinned MD5 of 26a366a25beb57b0a8f4c7b148758f94. No raw data are committed or uploaded to CI artifacts. SHA256 samples SKUs by ID before observing sales. The mirror is **not evidence of an unrestricted license**.

The 8 lowest SHA256 identifiers from each state/category stratum give 72 series. Only California and Texas (48 series) enter development. All Wisconsin series remain sealed. Historical observations from M5 days 1 through 1913 are ingested, but the final 112 days are not scored or used for selecting models.

Observed unit sales are not guaranteed to be uncensored customer demand. The calculation is a hypothetical inventory-loss proxy without holding, capacity, replenishment or stockout data.

## Time-dependent evaluation

The code uses eight 28-day, nonoverlapping development evaluation origins (zero-based); the latest evaluation label precedes the final 112-day holdout. For each evaluation origin, models train on data strictly before the origin. Each method is calibrated on the previous 12 disjoint historical windows. For past-window model selection, each historical window uses its own 12 strictly earlier windows for empirical residual quantile calibration. This nested chronology guards against future-label leakage; feature and real-world data-quality issues need separate audit.

## Four fixed baseline models

7-day seasonal naive, rolling mean28, rolling mean56, and Croston-SBA (smoothing=0.1). All are predetermined, without optimization against the evaluation labels. These are not modern strong benchmark models; later follow-up should include suitable high-performing forecasts and forecast congruence.

## Three selection baselines

(1) Past daily pinball score (1-day forecast target). (2) Past lead-time newsvendor cost using 3 windows. (3) Past lead-time newsvendor cost using 12 windows. Cost at lead times 7 and 14 is exactly pinball on the aggregated lead-time demand at the same alpha (0.5, 0.9). Do not claim an inconsistency of proper scores at matched horizons.

The future evaluation reports the regret of each selector compared with the best candidate model in hindsight in the same window. Hindsight selection is an evaluation yardstick only, not deployable. We report selector regret, zero-regret rates and approximate SKU-block confidence intervals; the latter do not capture correlated or hierarchical SKUs. Lookback counts are not matched computational budgets, merely a preliminary cost proxy.

## Explicit gates

Significance: provisional GO for retail model-selection relevance. Novelty: REVISE; no distinct result claimed. Feasibility: GO if hash-pinned raw data can be downloaded or user supplies authorized copy. Evidence: STOP until CI run artifacts are inspected. Publication: STOP. Wisconsin and final 112 days remain sealed through exploratory selection.

## Run

From the repository root after accepting applicable terms:

    python -m unittest discover -s tests -p 'test_m5_baselines.py' -v
    python -m research_lab.m5_baselines --config research/selection-transfer/m5_development.json --output research-output/m5-development --download

The GitHub Actions workflow runs independently and uploads only result, manifest and config files.
