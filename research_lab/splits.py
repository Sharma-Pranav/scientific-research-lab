"""Ordered forecasting split boundaries, including embargo and sealed final holdout.

Feature availability, fitting transforms, and label availability still require review.
"""
from __future__ import annotations
import hashlib


def rolling_origin(n: int, min_train: int, horizon: int, *, step: int | None = None,
                   embargo: int = 0, sealed_test: int = 0):
    """Return (train_start, train_end, eval_start, eval_end) with exclusive ends."""
    if any(type(x) is not int for x in (n, min_train, horizon, embargo, sealed_test)):
        raise TypeError("all parameters must be integral")
    if n <= 0 or min_train <= 0 or horizon <= 0 or embargo < 0 or sealed_test < 0:
        raise ValueError("invalid split sizes")
    if step is None:
        step = horizon
    if type(step) is not int or step <= 0:
        raise ValueError("step must be positive integer")
    development_end = n - sealed_test
    if development_end < min_train + embargo + horizon:
        raise ValueError("not enough development data for a complete fold")
    folds = []
    for train_end in range(min_train, development_end - embargo - horizon + 1, step):
        eval_start = train_end + embargo
        folds.append((0, train_end, eval_start, eval_start + horizon))
    return folds


def stable_group_partition(groups, *, holdout_fraction: float, salt: str):
    """Partition by group, never individual rows; hashed groups need not split evenly."""
    if not 0 < holdout_fraction < 1 or not salt:
        raise ValueError("invalid fraction or missing partition salt")
    train, holdout = [], []
    for group in sorted(set(str(g) for g in groups)):
        h = hashlib.sha256((salt + ":" + group).encode()).digest()
        x = int.from_bytes(h, "big") / (1 << 256)
        (holdout if x < holdout_fraction else train).append(group)
    return train, holdout
