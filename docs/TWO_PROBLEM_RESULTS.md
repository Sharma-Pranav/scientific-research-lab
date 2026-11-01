# Cross-domain generality test — executed 2026-11-01

**Scientific novelty: STOP; research infrastructure: GO for two kinds of controlled examples.** Two unrelated research projects were run and independently replay-audited using the reusable `research_lab.study` framework.

## Execution and trust boundary

A direct `git clone` from the assistant's isolated container was attempted but **failed because github.com DNS is inaccessible**. Instead, [GitHub Actions run 41315737232](https://github.com/Sharma-Pranav/scientific-research-lab/actions/runs/41315737232) used `actions/checkout@v4` to clone the **actual committed GitHub repository**. The runner executed the existing 41 tests, generated one synthetic data file, ran both project scripts, replay-audited both outputs, checked the asserted scientific-control directions, and uploaded the derived artifacts.

Source commit: `30696a1e02ddf6d89dc2a966d402e35810bb17a1`. Artifact: [ID 13087336003](https://github.com/Sharma-Pranav/scientific-research-lab/actions/runs/41315737232/artifacts/13087336003), archive SHA256 `25df0fdf20ac108de8405f50c4f31dd78c0729e7be9e2ccf527276c50e47f1d1`. No raw CSV was uploaded.

## Study A: sensor baseline shift and anomaly detection

This is a **CSV-backed synthetic** industrial-sensor example with a deterministic, SHA256-pinned source file: `74910aa0dc2bcdf60531f5f04ae5de903eb3ebae4a0358931757ff2b60eaa0e3`.

- 240 readings, initial 32 baseline calibration readings, eight labeled injected faults; level shift starts at t=120.
- Compared fixed initial 3-sigma detection with a rolling median and MAD threshold computed from strictly past readings.
- Shifted-segment false positives: **104/115** (90.43%) fixed baseline versus **3/115** (2.61%) rolling method.
- Both identified all five injected faults in the shifted segment. Entire post-calibration experiment: 8/8 faults detected by both.
- The rolling method has substantially higher synthetic precision because it does not mistake the entire shifted baseline for faults.

**Validity challenge:** the fixture is intentionally constructed to favor adaptation; the shift, fault amplitudes, window length and thresholds are not benchmarked on real industrial telemetry. This does not prove industrial operating value, robust uncertainty coverage, or novelty.

## Study B: repeated significance checking under the null

This is a **dataset-free Monte Carlo** study, using 3 predetermined independent seeds and 2,500 simulated experiments per seed (7,500 total). Each experiment draws independent standard-normal samples with equal true means and known unit variance. Every simulated trial has five cumulative statistical looks, with 20 new observations per treatment arm per look.

| Null hypothesis testing policy | Empirical probability of at least one false rejection |
|---|---:|
| One final unadjusted test (look 5 only) | **5.12%** |
| Any of five unadjusted tests (each alpha 0.05) | **14.39%** |
| Any of five Bonferroni-adjusted tests (alpha 0.01 each) | **3.15%** |

**Validity challenge:** a five-look schedule under a known Gaussian null only illustrates the known multiple-testing problem; it does not quantify effect sizes, false-discovery rates in real experiments, or novel sequential inference.

## Engineering gates

| Gate | Result |
|---|---|
| Check out the real GitHub source tree | PASS via actions/checkout |
| Existing repository tests | PASS, 41 tests |
| Study A with file input and expected SHA256 | PASS |
| Study B without any file input | PASS |
| Project-local run registry and manifest integrity | PASS |
| Bitwise deterministic replay of both projects | PASS |
| Independent directionality assertions and negative controls | PASS |
| Derived artifact upload | PASS |
| Demonstrated scientific novelty | **STOP** |
| Demonstrated research utility on unrelated real-world datasets | **NOT TESTED** |

## What this proves — and what it does not

These two deliberately simple experiments prove that **the research execution harness is not hardcoded to the M5 forecasting data format or domain** and can execute independent project runners both with and without input files.

They do not establish that Codex can autonomously design valid research methods, that the scientific skills are independently fact-checked, or that the framework works for arbitrary complex science with no additional domain code. Larger research needs dataset adapters, strong baselines, appropriate uncertainty, controlled permissions, and scientific peer review.

The next *strong* proof of generality should replicate a result using a third-party data source in a non-forecasting area and a second, independently written adapter, rather than accumulating more toy simulations.
