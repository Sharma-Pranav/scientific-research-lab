# M5 development history-length falsification — results (2026-11-01)

**Status:** Successfully executed *exploratory* benchmark; **scientific novelty REVISE; publication STOP**. This is not a causal or confirmatory result.

## Question and prediction

Is a longer historical lookback (12 vs 3 validation windows) more reliable for forecast selection on future 7-/14-day newsvendor-style cost? Does a past-only demand-instability proxy help explain when stale history hurts?

See [the pre-run protocol](history_length_protocol.md), [JSON specification](history_length_exploratory.json), and CI [run 41312151051](https://github.com/Sharma-Pranav/scientific-research-lab/actions/runs/41312151051).

### Evidence provenance

- Commit at execution: ba16196e5501c4b3ff8c5bf8277f0c3fbc9dd5df.
- Dataset: 30,490 M5 series from checksum-pinned Zenodo mirror; MD5 26a366a25beb57b0a8f4c7b148758f94.
- Panel: 72 identifier-selected series; 48 CA/TX development series. **WI and last 112 days excluded from scoring.** Eight development origins × two lead times × two cost fractiles = **1,536 cases**.
- Protocol SHA256: 96f0f8b92e0c5bd4ec45277b4882e1c5c785c2f57ba2c64ec132e0cedcc88798.
- Base development protocol SHA256: 7a38c2b91880e130e1e19b4edcc6e1eabd6161d4e267a459deb5402ac3750b0a.
- Results SHA256: 02dce14786fd72b360c2a2851567e46194a58e33e101304fcaf4bfb9c5db97b1.
- GitHub Actions artifact: ID 13085965988, ZIP SHA256 e2d0f07bee306f01548796d11121b63d7e9e62ba117adb0381cf8f7555911606.
- [Independent workflow evidence](https://github.com/Sharma-Pranav/scientific-research-lab/actions/runs/41312151051): 6 dedicated tests passed, data acquired, all regrets/summaries audited, derived artifacts uploaded. [Overall test workflow](https://github.com/Sharma-Pranav/scientific-research-lab/actions/runs/41312151069): 32 tests passed.
- Cross-check against earlier [M5 baseline evidence](m5_development_results.md): **exact agreement for all 1,536 common cases** in candidate realized costs and selected methods/regrets of policy_3 vs partial replay, policy_12 vs full replay, daily_full_12 vs daily pinball.

## Mean ex-post decision regret: policy validation lookback length

Lower is better; *evaluation oracle is the best of four forecast methods in hindsight*, not an attainable future decision rule.

| Lead time | Fractile alpha | Policy 1 | Policy 3 | Policy 6 | Policy 12 |
|---|---:|---:|---:|---:|---:|
| 7 | 0.50 | 0.6269 | **0.4756** | 0.5265 | 0.5779 |
| 7 | 0.90 | 0.3230 | 0.3290 | 0.3060 | **0.3049** |
| 14 | 0.50 | 1.4447 | **1.1629** | 1.1711 | 1.2578 |
| 14 | 0.90 | **0.8500** | 0.8768 | 0.8510 | 0.9524 |

**Observation:** there is no monotonic history-length improvement, and no universally optimal k in these four development scenarios. At alpha=0.50, 3 windows outperform 12 windows on average, but at alpha=0.90 the comparison is mixed.

The primary contrast is regret(policy_12) minus regret(policy_3); positive means longer validation performed worse.

| Lead time | Alpha | Equal-store weighted mean difference | Approx. descriptive 95% store-block interval |
|---|---:|---:|---|
| 7 | 0.50 | +0.1076 | [-0.0946, +0.3097] |
| 7 | 0.90 | -0.0268 | [-0.0766, +0.0229] |
| 14 | 0.50 | +0.0900 | [-0.2083, +0.3884] |
| 14 | 0.90 | +0.0566 | [-0.1020, +0.2152] |

All four intervals include zero. The seven stores are not an independent random sample, so intervals are descriptive and do **not** validate inference or equivalence.

## Matched-count daily control

A daily policy using positions 0, L, 2L... of each 28-day window uses the **same number of scored losses** as the lead-time selector. This comparison does **not** match CPU time, amount of demand data or decision horizon, and therefore cannot establish compute efficiency. The prespecified policy_3 minus daily_matched_3 mean-difference descriptive intervals, for L=7/.5, L=7/.9, L=14/.5 and L=14/.9, are:

- -0.1439 [-0.3077, +0.0199]
- -0.0062 [-0.0621, +0.0497]
- -0.1227 [-0.4011, +0.1557]
- -0.0081 [-0.1953, +0.1792]

None excludes zero. The controls do not establish a policy-selector advantage in this sample.

## Adversarial check: does past demand instability explain longer-history failure?

Instability was defined from the **last 28 vs previous 56 days, before the evaluation origin**, with >0.5 as high instability.

Only **14 of 384 unique SKU-origin cases (3.6%)** entered the high-instability group. Seven of those 14 are from the single TX_2 store. The policy_12 minus policy_3 regret difference at alpha=0.50 was larger within this small high-instability subgroup:

| Lead time | High instability (n=14) | Low instability (n=370) |
|---|---:|---:|
| 7 | +2.4109 | +0.0150 |
| 14 | +3.0804 | -0.0181 |

But this was not consistent at alpha=0.90 (L=7: -0.1578 vs -0.0190; L=14: +0.0584 vs +0.0763). The subgroup is tiny and strongly store-confounded. Removing TX_2 nearly eliminates or reverses the overall mean penalty for policy_12 at alpha=0.50:

| Lead time | All development SKUs | Excluding TX_2 |
|---|---:|---:|
| 7 | +0.102 | +0.018 |
| 14 | +0.095 | -0.007 |

This is **strong counterevidence** against treating the observed pattern as a broad causal law of temporal drift.

## Claim / reasons / evidence / counterargument / warrant

**Permissible narrow claim:** In this particular M5 development panel, changing the historical validation length from 1 to 12 windows yielded inconsistent model-selection regret; 12 windows did not uniformly improve regret.

**Potential reason (not established):** Historical validation can trade variance against stale evidence. Differences in demand regime may change the value of older validation windows.

**Evidence:** 1,536 case-level results, source-verified provenance, three comparison families, deterministic re-check of every case's chosen-method regret and summary, and cross-implementation comparison to the earlier baseline.

**Counterarguments:** Apparent 50%-fractile advantage for shorter history is concentrated in one store; only four weak forecasting baselines; correlated SKU/stores and sales-as-demand proxy; different calibration data and horizon aggregation; multiple exploratory comparisons; no independent confirmatory sample or cost-matched validation.

**Warrant:** The data support only descriptive variation within the prespecified development sample. They do not establish mechanism, statistical significance, novelty or deployable economic savings.

## Gate decision

- Engineering execution: **GO** (CI, provenance, all 32 tests, separate saved-artifact audit).
- Scientific significance: **provisional GO** for the model-selection question, not its answer.
- Novelty: **REVISE** (closely related prior selection and inventory literature; no unique finding).
- Evidential strength: **REVISE** (observational and confounded).
- Publication: **STOP**.

## Next research decision

Do **not** build a novel drift detector from this thin evidence yet. Stronger asymmetric action: implement at least one competitive probabilistic forecasting baseline and a **genuinely compute-matched** replay comparator; audit rolling-origin quantile calibration and report per-store stability. Keep WI and the 112-day temporal holdout untouched. If the signal survives, register an explicit diagnostic before confirmatory testing; otherwise stop the idea.
