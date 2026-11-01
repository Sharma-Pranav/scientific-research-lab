# Reader significance and scientific argument — UCI Bike Sharing

This worksheet describes an **already completed exploratory demonstration**. It is not a preregistration, causal conclusion, novelty assessment, or operational recommendation.

## Topic — I am studying

the evaluation of simple daily bike-rental forecasting rules on a chronologically later period of a curated urban mobility dataset

## Question — because I want to find out

whether weekly seasonal repetition or a recent four-week average produces lower one-step-ahead rental error than a last-day forecast on the selected 2012 test period

## Reader significance — in order to help my reader understand

why mobility planning analysts should check seemingly intuitive seasonal forecasting assumptions against a temporally appropriate baseline before relying on them in operational planning

## Claim

In the 120-day chronological UCI Bike Sharing test interval, the lag-one forecast had lower mean absolute error than both the lag-seven seasonal naive rule and a trailing 28-day average.

## Reasons

Each benchmark forecast was computed using only demand observed before its prediction time, and all three methods were scored on the same 120 daily outcomes with the same absolute-error measure.

## Evidence

The replayed baseline results show mean absolute errors of 918.84 rentals for lag one, 1,046.57 for the trailing 28-day mean, and 1,342.27 for lag seven. Read the archived results in https://github.com/Sharma-Pranav/scientific-research-lab/blob/main/docs/THREE_CURATED_DATASETS_RESULTS.md and the checked GitHub workflow https://github.com/Sharma-Pranav/scientific-research-lab/actions/runs/41317865983. The source is the UCI Bike Sharing dataset, DOI https://doi.org/10.24432/C5W894.

## Acknowledgement & Response

The final 120 days include seasonality changes, trends and weather variation; this single slice may favor the last-day rule. The comparison excludes richer seasonal methods and known-at-prediction-time covariates. Consequently it challenges an untested simple weekly-naive assumption for this interval, not the usefulness of seasonality in general.

## Warrant

Because the holdout timestamps are later than the initial history and all tested methods use the same target and loss, their observed test errors justify only the narrow ranking of these three rules on this one-step online evaluation interval, not a general claim about better deployment forecasts.

**Scientific novelty: STOP. Publication gate: STOP. Human review remains necessary.**
