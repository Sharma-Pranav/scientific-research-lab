# Reader significance and scientific argument — sequential testing under the null

This worksheet interprets a **previously executed illustrative Monte Carlo experiment**. The statistical mechanism is known; no new theory or empirical generalization is claimed.

## Topic — I am studying

the probability of reporting a false discovery when randomized A/B experiments are tested for statistical significance multiple times before their scheduled final analysis

## Question — because I want to find out

how examining five interim p-values without a correction changes the chance of rejecting a true null hypothesis relative to a final-only test and a Bonferroni-adjusted monitoring rule

## Reader significance — in order to help my reader understand

why experiment owners and product decision-makers can mistakenly interpret routine interim significance checks as strong evidence of a treatment effect, and when multiplicity control becomes necessary

## Claim

In 7,500 simulated null experiments with five cumulative looks, rejecting on any unadjusted 5-percent p-value produced a larger empirical false-positive rate than testing only at the final look, while the adjusted monitoring rule reduced this rate.

## Reasons

Each experiment generated independent normal observations with zero true treatment effect, and all three testing policies were evaluated using the same cumulative sampled data so that their observed false-rejection frequencies are directly comparable within this simulation design.

## Evidence

The fixed-final policy rejected 5.12 percent, unadjusted repeated inspection rejected 14.39 percent, and Bonferroni-adjusted inspection rejected 3.15 percent of the 7,500 trials. Results and run fingerprints are documented in https://github.com/Sharma-Pranav/scientific-research-lab/blob/main/docs/TWO_PROBLEM_RESULTS.md and the verified GitHub Actions run https://github.com/Sharma-Pranav/scientific-research-lab/actions/runs/41315737232.

## Acknowledgement & Response

The result depends on a specified five-look schedule, known Gaussian variance, null effect and repeated z-tests. More efficient valid sequential inference procedures also exist, so this experiment cannot establish that Bonferroni is optimal or that the simulated rates represent a particular commercial A/B platform.

## Warrant

Because treatment effects are exactly zero by construction and every rejection is therefore a false positive, the observed rejection frequencies directly measure false-positive behavior for these three rules under the stated null simulation, but say nothing about power, practical treatment effects or real-world experiment conduct.

**Scientific novelty: STOP. Publication gate: STOP. Human review remains necessary.**
