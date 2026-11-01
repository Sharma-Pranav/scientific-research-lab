# M5 development baseline — observed results (2026-11-01)

**Evidence:** [GitHub Actions run 41306676485](https://github.com/Sharma-Pranav/scientific-research-lab/actions/runs/41306676485), source commit f16b5b0e28b2b4595f1388a6334b962dda0d869e. All six M5 methodology tests passed; the source acquisition, benchmark run, holdout guards, and evidence-artifact upload completed successfully.

**Source provenance:** 30,490 M5 series in SHA-checked source file; published M5 Zenodo MD5 26a366a25beb57b0a8f4c7b148758f94. Sampled 72 identifier-selected series across nine state/category groups; CA/TX development only (48 series). Wisconsin and the last 112 days were not used for experimental scoring.

**Reproduction map:** Protocol SHA256 7a38c2b91880e130e1e19b4edcc6e1eabd6161d4e267a459deb5402ac3750b0a; sample-identifiers SHA256 1642798440f6027a6d51ba106de49997df852553326e52dbac2248aa491b8924; derived results SHA256 0aff75506d3e0b319cdd9b99444bef3b7be05abfc524a011ce3178bf497b4c16. CI artifact ID 13083800949, artifact ZIP digest sha256:df1cec67d063dd67fa08295c629e36017fc473c0b323d46a3eb167c292031c6f. Raw data are not in artifacts. Results/manifest/config are in the GitHub Actions artifact.

## Descriptive outcomes

Each lead-time and critical-fractile setting contains 384 series-origin observations (48 SKU-store series × 8 origins). Lower **mean ex-post regret** is better. Regret is against the best of four candidate models *in hindsight*, not against a deployable oracle.

| Lead time | Critical fractile | Daily pinball | 3-window lead-time replay | 12-window lead-time replay | Daily minus full (approx 95% SKU-block CI) |
|---|---:|---:|---:|---:|---|
| 7 | 0.50 | 0.4993 | **0.4756** | 0.5779 | -0.0786 [-0.2423, +0.0851] |
| 7 | 0.90 | **0.3048** | 0.3290 | 0.3049 | -0.0001 [-0.0378, +0.0376] |
| 14 | 0.50 | **1.0947** | 1.1629 | 1.2578 | -0.1631 [-0.4972, +0.1709] |
| 14 | 0.90 | **0.8506** | 0.8768 | 0.9524 | -0.1019 [-0.2127, +0.0089] |

**Observed negative result:** Longer-horizon direct cost validation using all 12 windows did **not** produce lower *average* regret than daily pinball selection in this development sample at any tested horizon/fractile. In the 7-day, 50% setting, the 3-window cost validation had the lowest average regret. None of the illustrative paired intervals excludes zero. These were pre-listed comparison choices but the result interpretation remains **exploratory**, not confirmatory.

Across all 1,536 cases, daily and full replay selected the **same** model 50.7% of the time. In about 21.0% of cases daily had strictly lower regret; full replay had strictly lower regret in about 20.7%. Roughly 9.3% of cases had effectively tied costs among all four candidates.

## Post-hoc heterogeneity diagnostics (not preregistered claims)

Mean regret pooled across all four scenarios and eight origins:

| Segment | Daily | Partial replay | Full replay |
|---|---:|---:|---:|
| FOODS | 0.9918 | 1.0677 | 1.2102 |
| HOBBIES | 0.7228 | 0.6924 | 0.7257 |
| HOUSEHOLD | 0.3475 | 0.3731 | 0.3838 |
| CA | 0.4056 | 0.4870 | 0.4131 |
| TX | 0.9691 | 0.9352 | 1.1335 |

These patterns are not independent tests, and differences could arise from SKU selection, missing features, nonstationarity, quantile calibration, imperfect cost proxy or chance. They motivate falsification, **not** mechanistic conclusions.

## Independent-style methodological challenge

- The full lead-time policy validation is based on historical forecast recalibration and only two/four aggregated cost observations per 28-day window; a longer lookback need not mean more representative data.
- Daily and lead-time validation workloads differ substantially; **no equal-compute comparison** was implemented.
- The methods are intentionally simple. No strong gradient boosting, probabilistic foundation model, or congruence baseline was evaluated. Therefore this is **not** a performance claim about state-of-the-art forecasting.
- Hindsight regret is defined relative to the selected candidate set and uses future labels only for evaluation. It is not a real economic cost measured from observed stock decisions.
- M5 observed sales may be censored and may not reflect true demand; lead-time inventory assumption omits capacity, order quantity, stockouts, prices and replenishment structure.
- The 48 SKU-store series are not statistically independent, so the block intervals are descriptive, not confirmatory evidence of absence of effect.
- Only CA/TX and nonfinal temporal folds were analyzed. WI and last 112 days **remain sealed**.
- The research team has not verified novelty of a proposed screening diagnostic, performed independent reviewer replication, or validated legal reuse terms beyond the public dataset page.

## Gates

Significance: provisional GO. Feasibility: GO for this baseline. Evidence: GO for **execution and provenance of exploratory baseline only**. Scientific novelty: REVISE. Publication: STOP.

## Smallest falsification sequence

1. Test whether longer replay history is harmed by temporal shifts: hold forecast models and origins fixed; vary historical cost-scoring window count (1, 3, 6, 12), with no peeking at sealed data. Correct multiple comparisons and label this exploration.
2. Introduce a properly matched-computation cost-replay baseline, and report both compute time and loss-evaluation counts.
3. Reproduce a verified forecast-congruence or modern probabilistic forecasting baseline. Re-check full-text novelty against published selection methods.
4. Only if an effect survives: preregister a novel screening diagnostic and reserve WI / final temporal observations for the confirmatory test.
