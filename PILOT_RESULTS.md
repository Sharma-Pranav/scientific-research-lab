# Pilot execution results (local, 2026-11-01)

Commands executed in the local directory:

```bash
python -m unittest discover -s tests -v
python -m research_lab.cli gate research/robust-location/proposal.json
python -m research_lab.cli pilot --phase exploratory
python -m research_lab.cli pilot --phase confirmatory
python -m research_lab.cli audit
```

Results: **4/4 tests passed**, gate result **publication STOP**, registry audit **PASS (2 runs)**.

| Phase | contamination | median MAE minus mean MAE | approximate 95% CI across seed blocks |
|---|---:|---:|---|
| exploratory | 0.00 | +0.028151 | [0.020429, 0.035873] |
| exploratory | 0.05 | -0.291938 | [-0.316973, -0.266904] |
| exploratory | 0.10 | -0.448282 | [-0.462444, -0.434120] |
| exploratory | 0.20 | -0.712039 | [-0.780090, -0.643988] |
| confirmatory | 0.00 | +0.032560 | [0.027115, 0.038005] |
| confirmatory | 0.05 | -0.271356 | [-0.285185, -0.257528] |
| confirmatory | 0.10 | -0.441418 | [-0.457321, -0.425514] |
| confirmatory | 0.20 | -0.673841 | [-0.690273, -0.657410] |

Negative differences favor the sample median. See immutable-by-interface raw artifacts under `runs/` for exact precision and hashes. These confidence intervals are illustrative normal-approximation intervals across seed blocks, not formal robust coverage guarantees.

Confirmation protocol SHA256 (canonical JSON): `06cc6d17bc0ead2a55c886cf3538318c0a7d947cfb9ef2d5c1d607de74b5cbbe`.

No novelty claim, source verification, human external review, independent implementation replication, or publication readiness established.
