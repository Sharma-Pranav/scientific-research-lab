# Sensor alarm robustness under synthetic baseline drift

I am studying anomaly alarm calibration in drifting industrial telemetry, because I want to find out whether rolling, past-only robust normalization can avoid false alarms after a baseline shift while still detecting injected spikes, in order to help monitoring engineers choose safer alerting defaults.

**H0:** False-positive rates and injected-fault recall do not improve compared with a fixed 3-sigma threshold.
**H1:** Rolling median/MAD has lower false-positive rate after a synthetic level shift and similar recall.
**Alternative:** The improvement is an artifact of the deliberately chosen drift magnitude, defect amplitude, window, and threshold.

Input is **synthetic labeled data**, generated deterministically; never generalize to real sensors. The runner does not access labels for anomaly scores; labels are only used for evaluation. Baseline calibration uses the first 32 observations without synthetic faults or shift; rolling windows use only past readings. The reported experiment is an engineering test, not a novel anomaly method or external validation.

Publication gate: **STOP**. Literature novelty and external validity unverified.
