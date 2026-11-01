# Wine Quality Red: curated real-data integration validation

**Study phase: EXPLORATORY. Scientific novelty: STOP.**

I am studying model evaluation across distinct real data types, because I want to find out whether the same generic research execution/audit harness handles curated datasets with different schemas, splitting rules and tasks, in order to help users trust the infrastructure rather than one hardcoded forecasting dataset.

## Primary question
Does a train-fitted alcohol-only linear model improve quality-score predictions over the training-mean baseline?

## Prediction and falsifier
Alcohol-only OLS reduces held-out MAE relative to train-only mean prediction.

**Falsifier:** Alcohol-only OLS has no smaller test MAE than the training-mean forecast.

## Scientific scope
The experiment intentionally uses very simple methods and a single evaluation split. The hypotheses are illustrative evaluation questions, not novel discoveries. The dataset is sourced from the official UCI Machine Learning Repository. Fit using training observations only; never choose a method after inspecting held-out outcomes. Record both positive and negative results. Dataset reuse is CC BY 4.0; provide proper creator attribution in the shared provenance documentation.

## Gate decision
Engineering validation pending. Novelty STOP; publication STOP.
