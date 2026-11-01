# Candidate research program: Can decision-risk screening outperform accuracy-only selection?

**Status: NOVELTY REVISE / EVIDENCE STOP / NOT YET A PUBLICATION CLAIM.**

## Topic / question / significance

I am studying operationally robust selection of demand-forecasting models.

Because I want to find out whether a **cheap pre-deployment warning rule** based on out-of-sample forecast errors and temporal dependence can identify when an accuracy-based winner is likely to be inferior across plausible future lead times and cost ratios—*without* running expensive full-scale inventory simulations for every candidate.

In order to help readers understand when to trust a forecasting leaderboard, when to abstain from declaring a winner, and when full operational validation is worth its computation and engineering cost.

## Competing hypotheses

- H0: Cheap risk diagnostics do not improve regret or evaluation cost relative to existing selection methods.
- H1: A pre-specified diagnostic based on horizon alignment, residual covariance, and cost-range uncertainty detects rank instability out of sample with lower evaluation cost than direct full-policy replay, at matched false-safe rates.
- H2: An even simpler dependence heuristic performs as well, so a new combined diagnostic is unnecessary.
- H3: Any apparent gain comes from selection leakage or unrealistic simulated operating-cost assumptions, and vanishes on held-out products, stores and time windows.

**Falsifying evidence:** In blinded holdout regimes, proposed screening fails to improve the regret-vs-compute Pareto frontier over a covariance threshold and a reduced-budget full replay, or fails false-safe/coverage targets.

## Contribution candidate (not a claim)

A reproducible, validity-calibrated *select / review / abstain* contract for forecasting model deployment under unknown future lead times and economic penalties. Report a curve of decision regret and the cost of obtaining evidence, not only accuracy or a cherry-picked rate of correct warnings.

## Required strong baselines

1. Best standard forecast metric matching the target horizon.
2. Single-cost-ratio direct newsvendor validation on historical holdout.
3. Full grid of policy simulations at a matching computational budget.
4. Dependence-only / covariance threshold classifier.
5. Forecast congruence baseline (Pritularga & Kourentzes, working paper), if computable from released forecast-origin panels.
6. Randomized and always-abstain controls with matched review load.

## Scope and experimental design

- Stage 0: novelty audit against Prak 2017, Babai 2022, Theodorou 2025, Pritularga/Kourentzes 2024, 2026 published model-selection robustness and forecast selection papers. **No novel contribution yet verified.**
- Stage 1: obtain official M5 bottom-level daily demand and build rolling-origin forecast bundles without training/test contamination. Keep item and calendar identifiers; document legitimate zero-demand days and promotions.
- Stage 2: devise synthetic shift generator (autocorrelation / intermittent occurrence / seasonality / cost ratio / lead-time range) to discover falsifiers, not to select the final headline result.
- Stage 3: preregister holdout stores, product groups, fixed cost/lead-time grids, alpha, uncertainty and false-safe-rate constraint before testing the proposed warning rule.
- Stage 4: evaluate at least three non-overlapping temporal test periods; out-of-sample item groups, simple and strong forecasting methods; report CIs clustered by product group / regime and computational work.
- Stage 5: independent reviewer checks evidence matrix, all failed experiments, alternatives, held-out targets and publication novelty.

## Measurement contract

- Primary: cost-normalized decision regret versus validation computation/time, conditional on maximum permitted false-safe probability.
- Secondary: risk-warning precision/recall at a fixed abstention budget; coverage of truly safe selections; service-level calibration; robustness to cost weights and lead-time shifts.
- Guardrails: decision-policy match, proper forecast horizon, no post-hoc policy tuning, report skipped/failed methods, equal forecast training resources.
- No arbitrary 95% significance threshold as a proxy for practical relevance. Use effect sizes with uncertainty and external scope.

## Explicit reasons this may fail

- Full policy replay is cheap enough, making the warning rule operationally redundant.
- Regret uncertainty cannot be calibrated with limited SKU histories.
- Existing model confidence set / congruence / robust selection methods already subsume the idea.
- Synthetic shift regimes fail to represent operational inventory dynamics.
- M5 retail inventory policies are not interchangeable with industrial spare-parts planning.

## GO gates

**Significance: provisional GO.** Selecting forecasts safely under uncertain decisions is consequential.

**Novelty: REVISE.** Strong overlapping research exists and must be read, not merely searched by title.

**Feasibility: REVISE.** Need sourced public data and historical forecast bundles, access and compute budget.

**Evidence: STOP.** No empirical results on this candidate question.

**Publication: STOP.** No manuscript claims until genuine novelty and external verification.
