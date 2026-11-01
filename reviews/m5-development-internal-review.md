# Internal adversarial review — M5 development benchmark

**Role:** independent-style methodological critique of saved evidence; NOT a blinded external peer review.

## Claim and evidence

**Permitted claim:** In one CI-executed, checksum-verified M5 development sample with 48 CA/TX series, 8 origins, four simple forecasting methods and four cost settings, longer 12-window policy-replay selection did not improve average observed hindsight regret over daily pinball selection. Source: [run 41306676485](https://github.com/Sharma-Pranav/scientific-research-lab/actions/runs/41306676485), manifest SHA references in the result report.

**Not permitted:** Policy replay is inherently inferior, daily pinball transfers reliably to industrial decisions, a negative difference proves statistical equivalence, the result is novel, or the dataset proves real inventory savings.

## Strongest objections

1. Baselines are too simple for a general paper. Full replay uses only 2-4 holdout targets per 28-day window; daily pinball uses 28. Variance of policy estimation is a confound.
2. Comparison is not computation-matched or information-matched.
3. Normalized inventory loss uses actual sales instead of true demand; possible censoring and store-specific costs ignored.
4. 48 identifiers selected without outcomes avoids selection-on-outcome bias, but a small SKU panel and item-family correlation limit external validity.
5. No independent implementation or replay from a second source has been attempted.
6. Novelty unresolved: closely related forecast-selection and inventory research exists.
7. Analysis of category/state differences and explanation by drift is exploratory and post hoc.

## Verification

Passed GitHub Actions: dataset checksum, development boundaries, 6 methodology tests and full pipeline execution. Derived artifact contains source manifest, protocol, 1,536 case records and summary. Run artifact SHA is recorded in the linked result report. No raw data committed.

## Decision

**GO** for second-stage *exploratory falsification* of history-length and horizon-matched selection. **STOP** for confirmatory claims, novelty assertions, or manuscript drafting. Preserve the two sealed holdouts.
