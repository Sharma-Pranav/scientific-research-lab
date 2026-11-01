# M5 validation-history falsification study

**Registered before the development-run results below are inspected. EXPLORATORY ONLY. No sealed Wisconsin or final-112-day validation.**

## Topic, question, significance

I am studying historical model-selection evidence for retail forecasting.
Because I want to find out whether longer operational-validation lookbacks improve forecasting model selection, and whether their failure is associated with *past-only* demand-regime instability.
In order to help practitioners understand whether paying for additional operational evaluation improves decisions or simply accumulates stale evidence.

## Claims and falsifiers

- H0: Neither increasing the number of validation windows nor a past-data instability proxy systematically alters future decision regret in development.
- H1: A 12-window policy selector has **higher** regret than a 3-window selector when a demand-regime change is present, suggesting stale validation evidence can hurt.
- H2: Lower variance of 12-window evaluation offsets drift so 12-window performs better in stable regimes.
- H3: The effect comes from unequal score sample counts, quantile calibration or forecast baseline weaknesses; a daily comparator matched on the number of scored terms eliminates the apparent differences.

Primary signed comparison: mean regret(policy_12) minus mean regret(policy_3), at each of four prespecified 7/14-day and 0.5/0.9 alpha settings. Positive implies more history harms the selection. Full 1/3/6/12 sensitivity grid is exploratory, not hypothesis-confirming. All outcomes must be reported.

## Experimental controls

Same M5 source, identifier-selected SKU panel (48 CA/TX series), rolling origins, forecasting methods, actual-demand proxy, cost definition and holdout borders as the previously executed development baseline.

Candidate forecasting methods: seasonal naive, mean28, mean56, fixed-alpha Croston SBA. No method training or selection on current/future labels. Nested calibration uses only 12 strictly earlier historical forecast windows for *each* historical selection window.

For each lookback length k = 1,3,6,12:
- policy_k: lead-time pinball on k historical 28-day windows (28/L scored losses per window);
- daily_full_k: daily pinball on k historical 28-day windows (28 scored losses per window);
- daily_matched_k: pinball only at fixed positions 0,L,2L,... within each historical window (28/L scores per window), and calibrates the daily residual quantile on those positions. This matches the **number of scored loss terms** and calibration terms, not actual CPU compute, information content, target variance or horizon. It is not a proper compute-matched experiment.

All selectors rank candidate methods on historical scores, then future regret is computed against the *best of the four candidates in hindsight*. The hindsight oracle is used only for scoring, not for selection.

The prespecified past-only demand-instability proxy is abs(mean(last 28 days) - mean(prior 56 days))/(1 + mean(prior 56 days)). Threshold >0.5 denotes high instability. The value is calculated from historical observations prior to evaluation origin. **It is an observational correlate, not a proven change-point test or mechanism.**

## Uncertainty, multiple comparisons, limits

Report all four primary scenario comparisons and all k/family combinations. Report store-cluster paired differences and approximate intervals, explicitly **descriptive** due to within-state correlation, few stores, multiple comparisons and nonrandom sample selection. We do not treat an interval crossing zero as evidence of equivalence or no effect.

External validity limitations: four weak forecast models; 48 products; correlated SKU-store data; actual sales can be censored demand; ex-post loss not realized supply-chain economics; fixed lead times, cost ratios and calibration windows; retrospective only, no test-domain shift.

## Stop/go

Significance: provisional GO. Feasibility: GO if M5 verified. Novelty: REVISE. Evidence: STOP until CI run is verified. Publication: STOP.

If full policy replay outperforms shorter replay consistently, reject the stale-history mechanism. If effects vary by scenario or regime, report instability and reject universal claims. Next stage may include stronger forecasting baselines and matched computation, **without unsealing** reserved holdouts.
