# Bike Sharing Daily: curated real-data integration validation

**Study phase: EXPLORATORY. Scientific novelty: STOP.**

I am studying model evaluation across distinct real data types, because I want to find out whether the same generic research execution/audit harness handles curated datasets with different schemas, splitting rules and tasks, in order to help users trust the infrastructure rather than one hardcoded forecasting dataset.

## Primary question
Do weekly seasonality and recent averages improve next-day bike rental forecasts relative to a last-day naive forecast?

## Prediction and falsifier
At least one seasonal or moving-average baseline improves last-day MAE on the chronological final period.

**Falsifier:** Neither lag-7 nor moving-average forecasts beat lag-1 on held-out MAE.

## Scientific scope
The experiment intentionally uses very simple methods and a single evaluation split. The hypotheses are illustrative evaluation questions, not novel discoveries. The dataset is sourced from the official UCI Machine Learning Repository. Fit using training observations only; never choose a method after inspecting held-out outcomes. Record both positive and negative results. Dataset reuse is CC BY 4.0; provide proper creator attribution in the shared provenance documentation.

## Gate decision
Engineering validation pending. Novelty STOP; publication STOP.
