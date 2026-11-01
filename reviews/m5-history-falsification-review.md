# Independent-style adversarial review: history-length experiment

**Nature of review:** methodological cross-check conducted on saved evidence and stored predictions, not a blinded human peer review.

**Review decision: REVISE. Publication: STOP.**

## Tests actually passed
- Methodology tests and no-future-label tests passed on GitHub Actions.
- Dataset checksum and frozen base protocol fingerprint matched earlier M5 benchmark.
- New artifact auditor rechecked every saved method regret, sample constraints and all aggregate summaries.
- Exact replay of 1,536 original baseline comparisons for common selectors (policy 3/12, daily 12) was confirmed against the older evidence archive.

## Disconfirming observations
1. At alpha 0.90, longer history improves average 7-day cost relative to three windows, contradicting a universal stale-history prediction.
2. All store-cluster descriptive intervals for policy 12 minus policy 3 cross zero.
3. High-instability group comprises only 14 of 384 unique origin-series cases; seven belong to TX_2. The high-instability effect is not stable across alphas.
4. Leave-TX_2-out sensitivity reduces the 7-day, alpha=0.5 difference to 0.018 and reverses the 14-day, alpha=0.5 difference to -0.007.
5. Matching the count of scored losses is *not* matching compute, history information, uncertainty or operational target.

## Evidence validity
The stored regret comparison is correct for these four simple forecasters and these M5 windows. It is not robust evidence that temporal drift causally makes longer history harmful. The evaluation oracle is retrospective; sales may reflect stockouts; the small correlated store sample and model set limit generalization. Stop accidental multiple-testing narratives.

## Actionable next gate
Before a candidate screening method is proposed, compare with stronger forecasting baselines, use a matched-CPU or matched-budget experimental design, and perform a formal source-level novelty review. Preserve original sealed holdouts; no manuscript yet.
