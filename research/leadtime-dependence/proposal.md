# Lead-time dependence and quantile model selection — version-pinned CI pilot (not external preregistration)

## Scientific framing

I am studying **the transfer of one-period quantile model rankings to multi-period stocking decisions**,

because I want to find out **when temporal autocorrelation reverses the operational ranking of two models even when one dominates one-period pinball loss**,

in order to help readers understand **which forecasting evaluation choices can and cannot justify an inventory stocking decision**.

## Claim and alternatives

- H0: One-period pinball ranking carries through to multi-period cost, for the predefined models and data generator.
- H1: With positive autocorrelation and lead times >1, the inflated-safety-stock model B can beat independence-based model A on multi-period normalized newsvendor cost even though A is optimal for the marginal one-period pinball loss.
- H2: The reversal can be fully explained by covariance neglected in the aggregate demand variance. Under the exact AR(1) lead-time quantile oracle, both A and B should be worse in expectation.
- H3: The apparent advantage is a simulation artifact; the independently derived Gaussian expected cost does not agree with Monte Carlo estimates.

Primary comparison is **B minus A** in normalized newsvendor cost, at rho=0.6, lead time 7, alpha=0.9, padding=0.45. Negative favors B. Negative controls are rho=0 and lead time 1. Sensitivity grid varies rho, lead time, critical fractile, and padding. All configurations, metrics and seeds are defined in the committed JSON files before CI execution.

## Model and warrant

D_t = 100 + 10 Z_t where stationary Z_t = rho Z_(t-1) + sqrt(1-rho²)epsilon_t, with independent standard-normal epsilon.

Lead-time demand S_L = sum_{t=1}^L D_t, with variance 100 [L + 2 sum_{k=1}^{L-1}(L-k)rho^k]. Daily marginal distributions are fixed across rho.

A uses iid aggregation: Q_A(L)=100L+10 z_alpha sqrt(L). B uses a fixed padding on that safety term: Q_B(L)=100L+10 z_alpha sqrt(L)(1+padding). Oracle uses exact AR(1) aggregate variance.

Daily pinball score is computed on the first daily observation. Normalized stocking cost is (1-alpha)(q-y)+ + alpha(y-q)+. For the **same target horizon**, this is exactly the pinball loss, so it cannot reverse rankings at equal alpha. The mismatch in target aggregation is essential; any manuscript must acknowledge it, not claim a failure of proper scoring rules.

Independent Monte Carlo blocks produce differences and approximate Student-t intervals across blocks. A closed-form Gaussian expected-cost calculation independently checks Monte Carlo. This is a pedagogical stationary Gaussian simulation, not an industrial intermittent-demand study.

## Limits and novelty gate

**Novelty: STOP for this experiment.** Prior work already analyzes demand autocorrelation, lead-time variance and safety stock implications (2017 and 2022 EJOR papers in the matrix). This is an infrastructure validation and a necessary negative control, not a publishable contribution.

Potential subsequent direction (not yet a claim): a budget-matched, out-of-domain diagnostic for predicting model-selection failure when demand dependence and operational costs shift; requires a separate novelty audit against the lead-time and forecast-congruence literature, real datasets, and pre-registered splits.
