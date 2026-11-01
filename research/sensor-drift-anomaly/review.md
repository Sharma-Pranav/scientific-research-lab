# Internal test assessment: synthetic sensor alarms

The source file is generated from a fixed seed, with labeled synthetic faults and a baseline level shift. Fixed and rolling detectors receive only observed readings. The runner records confusion matrices for stable and shifted periods.

**Limitations:** Deliberately chosen faults/drift, one realization, initial calibration already known clean, no actual hardware data, no false-alarm cost weights, no statistical uncertainty across multiple sources.

Scientific novelty **STOP**; this is an execution-harness generality test.
