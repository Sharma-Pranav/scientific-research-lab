"""Small, dependency-free simulation engine and tamper-evident run registry."""
from __future__ import annotations
import hashlib
import json
import math
import os
import platform
import random
import statistics
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path


def canonical_bytes(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def config_digest(config):
    return digest(canonical_bytes(config))


def git_commit(root):
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, stderr=subprocess.DEVNULL, timeout=3).decode().strip()
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None


def simulation(config):
    assert config["dataset_version"] == "synthetic-gaussian-mixture-v1", "Unknown data generator"
    assert config["target"] == "mean_absolute_estimation_error"
    assert sorted(config["baselines"]) == ["sample_mean", "sample_median"]
    n = int(config["n"])
    trials = int(config["trials_per_seed"])
    assert n >= 2 and trials >= 1
    out = []
    for rate in config["contamination_rates"]:
        assert 0 <= rate <= 1
        rows = []
        for seed in config["seeds"]:
            # Per-cell seed eliminates cross-condition RNG dependence while preserving reproducibility.
            rng = random.Random(f"{config['dataset_version']}:{seed}:{rate}")
            mean_errors, median_errors = [], []
            for _ in range(trials):
                xs = [rng.gauss(0, float(config["contamination_sigma"]) if rng.random() < rate else 1.0) for _ in range(n)]
                mean_errors.append(abs(statistics.fmean(xs)))
                median_errors.append(abs(statistics.median(xs)))
            rows.append({"seed": seed, "mean_mae": statistics.fmean(mean_errors), "median_mae": statistics.fmean(median_errors),
                         "delta_median_minus_mean": statistics.fmean(median_errors) - statistics.fmean(mean_errors)})
        deltas = [r["delta_median_minus_mean"] for r in rows]
        avg = statistics.fmean(deltas)
        # Descriptive t approximation, assumes independent seed-block estimates (not raw trials).
        std_err = statistics.stdev(deltas) / math.sqrt(len(deltas)) if len(deltas) >= 2 else None
        out.append({"rate": rate, "by_seed": rows, "delta_mean": avg, "approx_95ci":
                    [avg - 1.96 * std_err, avg + 1.96 * std_err] if std_err is not None else None})
    return {"metric": "MAE of location estimate relative to zero", "negative_delta_favors": "sample_median",
            "uncertainty_note": "Illustrative normal-approximation interval across independent seed-block estimates; not formal coverage validation",
            "conditions": out}


def write_new(path, content):
    # O_EXCL prevents accidental overwrite and prevents replacing completed artifacts through this interface.
    fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
    with os.fdopen(fd, "wb") as out:
        out.write(content)
        out.flush()
        os.fsync(out.fileno())


def run(root, config_file):
    root = Path(root)
    config = json.loads(Path(config_file).read_text(encoding="utf-8"))
    assert config["phase"] in {"exploratory", "confirmatory"}
    if config["phase"] == "confirmatory" and config.get("frozen") is not True:
        raise ValueError("Confirmatory protocol must be explicitly frozen before execution")
    cfg_hash = config_digest(config)
    started = time.perf_counter()
    result = simulation(config)
    elapsed = time.perf_counter() - started
    rid = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "-" + uuid.uuid4().hex[:8]
    run_dir = root / "runs" / rid
    run_dir.mkdir(parents=True, exist_ok=False)
    payloads = {"config.json": canonical_bytes(config), "results.json": canonical_bytes(result)}
    manifest = {"run_id": rid, "status": "completed", "phase": config["phase"], "protocol_id": config["protocol_id"],
                "question_id": config["question_id"], "config_hash": cfg_hash,
                "dataset_fingerprint": digest(config["dataset_version"].encode()),
                "seeds": config["seeds"], "baselines": config["baselines"],
                "metric": config["target"], "elapsed_seconds": elapsed,
                "software": {"python": sys.version.split()[0], "platform": platform.platform()},
                "hardware": platform.machine(), "git_commit": git_commit(root),
                "artifact_sha256": {name: digest(data) for name, data in payloads.items()},
                "created_utc": datetime.now(timezone.utc).isoformat(),
                "uncertainty": result["uncertainty_note"]}
    for name, data in payloads.items():
        write_new(run_dir / name, data)
    write_new(run_dir / "manifest.json", canonical_bytes(manifest))
    registry = root / "registry" / "experiments.jsonl"
    registry.parent.mkdir(parents=True, exist_ok=True)
    # Append-only; single writer only (not a concurrent transactional database).
    with open(registry, "a", encoding="utf-8") as out:
        out.write(json.dumps({"run_id": rid, "manifest_sha256": digest(canonical_bytes(manifest)),
                              "path": f"runs/{rid}", "status": "completed", "config_hash": cfg_hash}, sort_keys=True) + "\n")
        out.flush()
        os.fsync(out.fileno())
    return manifest, result


def audit(root):
    root = Path(root)
    registry = root / "registry" / "experiments.jsonl"
    if not registry.exists():
        raise ValueError("Registry is missing")
    lines = [x for x in registry.read_text(encoding="utf-8").splitlines() if x.strip()]
    if not lines:
        raise ValueError("Registry is empty")
    seen = set()
    for line in lines:
        item = json.loads(line)
        rid = item["run_id"]
        if rid in seen or item["path"] != f"runs/{rid}":
            raise ValueError(f"Invalid or duplicate registry entry: {rid}")
        seen.add(rid)
        d = root / "runs" / rid
        manifest_raw = (d / "manifest.json").read_bytes()
        manifest = json.loads(manifest_raw)
        if digest(manifest_raw) != item["manifest_sha256"] or manifest["run_id"] != rid:
            raise ValueError(f"Manifest integrity failure: {rid}")
        for name, hash_ in manifest["artifact_sha256"].items():
            if digest((d / name).read_bytes()) != hash_:
                raise ValueError(f"Artifact integrity failure: {rid}/{name}")
        config = json.loads((d / "config.json").read_text(encoding="utf-8"))
        if config_digest(config) != manifest["config_hash"] or item["config_hash"] != manifest["config_hash"]:
            raise ValueError(f"Config mismatch: {rid}")
        if digest(config["dataset_version"].encode()) != manifest["dataset_fingerprint"]:
            raise ValueError(f"Dataset fingerprint mismatch: {rid}")
        if manifest["phase"] == "confirmatory" and not config.get("frozen"):
            raise ValueError(f"Unfrozen confirmation: {rid}")
    orphaned = [d.name for d in (root / "runs").iterdir() if d.is_dir() and d.name not in seen]
    if orphaned:
        raise ValueError(f"Orphan run directories: {orphaned}")
    return len(seen)


def validate_proposal(proposal):
    for key in ("topic", "question", "significance", "claim", "reasons", "falsifier", "baselines"):
        if not proposal.get(key):
            raise ValueError(f"Missing research requirement: {key}")
    decisions = {k: proposal.get(k) for k in ("significance_gate", "novelty_gate", "feasibility_gate", "evidence_gate")}
    if any(v not in {"GO", "REVISE", "STOP"} for v in decisions.values()):
        raise ValueError("All four gate decisions must be explicit")
    # Automated gates can only request independent review, never approve publication.
    publication = "HUMAN_REVIEW_REQUIRED" if set(decisions.values()) == {"GO"} else "STOP"
    if proposal.get("publication_gate") == "GO":
        raise ValueError("Automated gates cannot authorize publication GO")
    return decisions, publication
