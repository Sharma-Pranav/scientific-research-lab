# Real-data baseline package: required before proposing a new model

**Status: PENDING. No public dataset, forecast bundles, real-data simulations or novelty evidence has been produced.**

## Research objective
Can a low-cost warning identify when an accuracy-led forecasting model selection will be unreliable under shifts in replenishment lead time and the cost ratio? Compare regret against evaluation time; do not write a paper before a new effect survives falsification.

## Data and leakage
1. Obtain the official M5 competition sales, prices, and calendar data. Save source location, release/license, SHA256, download date, schema and observation count. No redistribution until license checked.
2. Define the unit of demand, decision horizon, unknown lead times and cost-ratio set. Sales do not reveal stockout-adjusted demand.
3. Version the training period, rolling-origin development folds, and sealed final temporal holdout before tuning. Prevent leakage through feature availability, post-origin aggregation, normalization, imputation and training of global models.
4. Hold out entire stores or product families as an out-of-group validation. Report sample count and target shift. Record computational budget.

## Minimum strong baselines
- Horizon-matched pinball/WQL forecast ranking on identical origins.
- Full policy replay over a preregistered lead-time and cost-ratio grid.
- Residual covariance/dependence threshold without a learned classifier.
- Partial policy replay matched for evaluation cost.
- Always-review and randomized-review controls at the same abstention budget.
- Literature-grounded forecast congruence where definition and data permit.

## Experimental objective and stop conditions
Primary criterion: decision regret versus evaluation cost at a fixed maximum false-safe rate on sealed out-of-time and out-of-group observations.

Secondary: abstention/coverage, calibration, service level, robustness to cost and lead time, evaluation cost and errors across all items. Report confidence intervals clustered by independent SKU group or regime; include negative outcomes and model-tuning budget.

Reject a novel diagnostic if matched-cost partial replay or covariance-only screening performs equally well. Reject a paper claim if source-verification or independent validity review fails, even if experiments improve metrics.

**Gates: significance provisional GO; novelty REVISE; feasibility REVISE; evidence STOP; publication STOP.**
