# Sequential significance peeking under the null

I am studying experiment monitoring practices, because I want to find out how repeated unadjusted significance testing changes false-positive frequency even under no treatment effect, in order to help teams avoid false findings.

**H0:** Repeated unadjusted tests do not inflate false-positive frequency beyond a final-only test.
**H1:** Across five data-dependent opportunities to stop, the probability of any uncorrected p<0.05 is greater than for a fixed final test; Bonferroni controls FWER.

Fixed design: 5 interim looks, 20 fresh independent standard-normal observations per arm per look, 3 Monte Carlo seeds × 2500 replications. Known unit variance, two-sided z-tests. Same simulated samples are used for all three policies. This is a known multiple-testing result, **not novel**, and illustrates generic dataset-free runs rather than novel empirical research.

Publication gate: **STOP**. No novelty or study on actual A/B test logs.
