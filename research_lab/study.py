"""Dataset-agnostic research projects: scaffold, run, freeze, audit.

A study owns its methods in research/<slug>/experiment.py. The harness owns
protocol validation, input fingerprints, execution records and replay audits.
Import and execute only code you trust: this is NOT a sandbox.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import os
import platform
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from research_lab.engine import canonical_bytes, git_commit, write_new

SLUG = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
NAME = re.compile(r"^[a-z][a-z0-9_]*$")
STATUSES = {"exploratory", "confirmatory"}


def canonical(obj):
    return canonical_bytes(obj)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def hash_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for part in iter(lambda: f.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def project_dir(root, slug):
    if not SLUG.fullmatch(slug):
        raise ValueError("Project slug must contain only lowercase letters, numbers and hyphens")
    return Path(root) / "research" / slug


def _inside(base, relative):
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError("Expected nonempty relative path")
    base = Path(base).resolve()
    target = (base / relative).resolve()
    if not target.is_relative_to(base):
        raise ValueError("Paths may not escape their designated directory")
    return target


def load_protocol(root, slug):
    path = project_dir(root, slug) / "protocol.json"
    p = json.loads(path.read_text(encoding="utf8"))
    required = ("schema_version", "project", "phase", "question", "significance",
                "hypothesis", "falsifier", "runner", "inputs", "settings", "seeds", "frozen")
    for key in required:
        if key not in p:
            raise ValueError(f"Protocol missing {key}")
    if p["schema_version"] != 1 or p["project"] != slug:
        raise ValueError("Schema or project ID mismatch")
    if p["phase"] not in STATUSES or not isinstance(p["frozen"], bool):
        raise ValueError("Invalid phase or frozen indicator")
    if p["phase"] == "exploratory" and p["frozen"]:
        raise ValueError("Exploration must not pose as a frozen confirmatory protocol")
    if any(not isinstance(p[k], str) or not p[k].strip()
           for k in ("question", "significance", "hypothesis", "falsifier")):
        raise ValueError("Question, significance, hypothesis and falsifier required")
    if not isinstance(p["settings"], dict) or not isinstance(p["inputs"], list):
        raise ValueError("Settings must be object and inputs must be array")
    if not isinstance(p["seeds"], list) or not p["seeds"] or len(set(map(str, p["seeds"]))) != len(p["seeds"]):
        raise ValueError("Record a nonempty list of distinct seeds")
    if not all(type(s) is int for s in p["seeds"]):
        raise ValueError("Seeds must be integers")
    if not isinstance(p["runner"], str) or not p["runner"].endswith(".py"):
        raise ValueError("Runner must be a relative .py file")
    runner = _inside(project_dir(root, slug), p["runner"])
    if not runner.is_file():
        raise ValueError("Runner source is missing")
    names = set()
    for entry in p["inputs"]:
        if not isinstance(entry, dict) or set(entry) != {"name", "path", "sha256"}:
            raise ValueError("Inputs require name, path, sha256")
        if not isinstance(entry["name"], str) or not NAME.fullmatch(entry["name"]):
            raise ValueError("Invalid input name")
        if entry["name"] in names:
            raise ValueError("Duplicate input name")
        names.add(entry["name"])
        if not isinstance(entry["path"], str) or not entry["path"]:
            raise ValueError("Input path is missing")
        _inside(root, entry["path"])
        if entry["sha256"] is not None and (not isinstance(entry["sha256"], str)
                                            or not re.fullmatch(r"[a-f0-9]{64}", entry["sha256"])):
            raise ValueError("Invalid expected input SHA256")
        if p["phase"] == "confirmatory" and not entry["sha256"]:
            raise ValueError("Confirmatory inputs must have expected SHA256")
    # Confirmatory protocol must have an explicitly frozen, independently stored fingerprint.
    if p["phase"] == "confirmatory" and not p["frozen"]:
        raise ValueError("Confirmation must be frozen")
    canonical(p)  # Reject nonfinite numbers and non-JSON values.
    return p, runner


def input_manifest(root, protocol):
    paths, records = {}, {}
    for entry in protocol["inputs"]:
        resolved = _inside(root, entry["path"])
        if not resolved.is_file():
            raise FileNotFoundError(f"Declared input absent: {entry['name']}")
        actual = hash_file(resolved)
        if entry["sha256"] is not None and actual != entry["sha256"]:
            raise ValueError(f"Input checksum mismatch: {entry['name']}")
        paths[entry["name"]] = resolved
        records[entry["name"]] = {"path": entry["path"], "sha256": actual,
                                  "bytes": resolved.stat().st_size}
    return paths, records


def fingerprints(protocol, runner, records):
    return {"protocol_sha256": sha(canonical(protocol)),
            "runner_sha256": hash_file(runner),
            "inputs": records}


def _freeze_path(root, slug):
    return project_dir(root, slug) / "freeze.json"


def check_freeze(root, slug, protocol, fp):
    if protocol["phase"] != "confirmatory":
        return
    f = _freeze_path(root, slug)
    if not f.exists():
        raise ValueError("Missing freeze.json for confirmatory experiment")
    proof = json.loads(f.read_text(encoding="utf8"))
    for k in ("protocol_sha256", "runner_sha256", "inputs"):
        if proof.get(k) != fp[k]:
            raise ValueError(f"Frozen protocol/source mismatch: {k}")


def freeze(root, slug):
    protocol, runner = load_protocol(root, slug)
    if protocol["phase"] != "confirmatory":
        raise ValueError("Only confirmatory protocols can be frozen")
    _, records = input_manifest(root, protocol)
    fingerprints_ = fingerprints(protocol, runner, records)
    proof = {**fingerprints_, "created_utc": datetime.now(timezone.utc).isoformat(),
             "warning": "Local freeze is versioned evidence, not independent preregistration"}
    write_new(_freeze_path(root, slug), canonical(proof))
    return proof


def execute(runner, protocol, inputs):
    spec = importlib.util.spec_from_file_location("research_experiment_" + uuid.uuid4().hex, runner)
    if spec is None or spec.loader is None:
        raise ValueError("Cannot load experiment runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    fn = getattr(module, "run", None)
    if not callable(fn):
        raise ValueError("Runner must expose run(protocol, inputs)")
    outcome = fn(protocol, inputs)
    if not isinstance(outcome, dict):
        raise ValueError("Experiment must return a JSON object")
    return json.loads(canonical(outcome))


def run(root, slug):
    root = Path(root)
    protocol, runner = load_protocol(root, slug)
    inputs, records = input_manifest(root, protocol)
    fp = fingerprints(protocol, runner, records)
    check_freeze(root, slug, protocol, fp)
    result = execute(runner, protocol, inputs)
    # Report framing quality as a distinct, nonblocking human-review status.
    from research_lab.significance import check_file
    significance_preflight = check_file(project_dir(root, slug) / "significance.md", stage="framing")
    rid = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "-" + uuid.uuid4().hex[:8]
    output = root / "runs" / "projects" / slug / rid
    output.mkdir(parents=True, exist_ok=False)
    payloads = {"protocol.json": canonical(protocol), "results.json": canonical(result)}
    manifest = {"schema_version": 1, "run_id": rid, "project": slug,
                "phase": protocol["phase"], "status": "completed",
                **fp, "artifact_sha256": {k: sha(v) for k, v in payloads.items()},
                "python": sys.version.split()[0], "platform": platform.platform(),
                "git_commit": git_commit(root),
                "created_utc": datetime.now(timezone.utc).isoformat(),
                "publication_status": "NOT_AUTOMATICALLY_APPROVED",
                "reader_significance_preflight": significance_preflight}
    for name, payload in payloads.items():
        write_new(output / name, payload)
    man_bytes = canonical(manifest)
    write_new(output / "manifest.json", man_bytes)
    registry = project_dir(root, slug) / "experiments.jsonl"
    registry.parent.mkdir(parents=True, exist_ok=True)
    with registry.open("a", encoding="utf8") as f:
        f.write(json.dumps({"run_id": rid, "manifest_sha256": sha(man_bytes),
                            "result_sha256": sha(payloads["results.json"])},
                           sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())
    return {"run_id": rid, "directory": str(output),
            "protocol_sha256": fp["protocol_sha256"], "result": result}


def audit(root, slug, replay=False):
    root = Path(root)
    protocol, runner = load_protocol(root, slug)
    paths, records = input_manifest(root, protocol)
    fp = fingerprints(protocol, runner, records)
    check_freeze(root, slug, protocol, fp)
    registry = project_dir(root, slug) / "experiments.jsonl"
    if not registry.is_file():
        raise ValueError("Project registry missing; no recorded experiments")
    entries = [json.loads(line) for line in registry.read_text(encoding="utf8").splitlines() if line.strip()]
    if not entries:
        raise ValueError("Project registry is empty")
    seen = set()
    saved_ids = set()
    base = root / "runs" / "projects" / slug
    for entry in entries:
        rid = entry["run_id"]
        if rid in seen or not re.fullmatch(r"[0-9]{8}T[0-9]{12}Z-[0-9a-f]{8}", rid):
            raise ValueError("Invalid or duplicate run ID")
        seen.add(rid)
        folder = base / rid
        man_bytes = (folder / "manifest.json").read_bytes()
        res_bytes = (folder / "results.json").read_bytes()
        proto_bytes = (folder / "protocol.json").read_bytes()
        man = json.loads(man_bytes)
        if sha(man_bytes) != entry["manifest_sha256"]:
            raise ValueError("Manifest tampered")
        if sha(res_bytes) != entry["result_sha256"]:
            raise ValueError("Result tampered")
        if man["project"] != slug or man["run_id"] != rid or man["status"] != "completed":
            raise ValueError("Run manifest mismatch")
        for k in ("protocol_sha256", "runner_sha256", "inputs"):
            if man[k] != fp[k]:
                raise ValueError(f"Code, protocol or input drift: {k}")
        if sha(proto_bytes) != man["artifact_sha256"]["protocol.json"] or proto_bytes != canonical(protocol):
            raise ValueError("Saved protocol altered")
        if sha(res_bytes) != man["artifact_sha256"]["results.json"]:
            raise ValueError("Saved result altered")
        if replay:
            regenerated = canonical(execute(runner, protocol, paths))
            if regenerated != res_bytes:
                raise ValueError("Replay mismatch: cannot reproduce saved result")
    if base.exists():
        saved_ids = {p.name for p in base.iterdir() if p.is_dir()}
    if saved_ids != seen:
        raise ValueError("Registry contains missing or unregistered run directories")
    return {"status": "PASS", "project": slug, "runs": len(entries),
            "replay": bool(replay), "protocol_sha256": fp["protocol_sha256"]}


EXAMPLE = '''"""Replace this demonstration with your own domain-specific method."""
import random
import statistics


def run(protocol, inputs):
    # No dataset needed for this example. Access CSV or other files through inputs.
    n = int(protocol["settings"]["trials_per_seed"])
    p = float(protocol["settings"]["simulated_success_probability"])
    if n <= 0 or not 0 <= p <= 1:
        raise ValueError("Invalid simulation settings")
    by_seed = []
    for seed in protocol["seeds"]:
        rng = random.Random(seed)
        successes = sum(rng.random() < p for _ in range(n))
        by_seed.append({"seed": seed, "success_rate": successes / n})
    return {"kind": "toy_coin_simulation_not_a_scientific_discovery",
            "mean_success_rate": statistics.fmean(x["success_rate"] for x in by_seed),
            "by_seed": by_seed}
'''


def init(root, slug, title):
    folder = project_dir(root, slug)
    if folder.exists():
        raise FileExistsError("Research project already exists")
    folder.mkdir(parents=True, exist_ok=False)
    if not title.strip():
        raise ValueError("Research title cannot be blank")
    protocol = {
        "schema_version": 1, "project": slug, "phase": "exploratory", "frozen": False,
        "question": title, "significance": "REPLACE with why this question matters",
        "hypothesis": "REPLACE with falsifiable hypothesis",
        "falsifier": "REPLACE with observation rejecting this hypothesis",
        "runner": "experiment.py", "inputs": [],
        "settings": {"trials_per_seed": 100, "simulated_success_probability": 0.5},
        "seeds": [11, 19, 23],
    }
    (folder / "protocol.json").write_bytes(canonical(protocol))
    (folder / "experiment.py").write_text(EXAMPLE, encoding="utf8")
    from research_lab.significance import template as significance_template
    (folder / "significance.md").write_text(significance_template(), encoding="utf8")
    (folder / "proposal.md").write_text(
        f"# {title}\n\n"
        "Complete the three-step reader-significance statement in significance.md "
        "before treating this as a scientifically framed question. "
        "After obtaining results, complete the five-part argument there.\n\n"
        "## H0, H1 and alternatives\n\n## Strong baselines / falsifiers\n\n"
        "## Significance and novelty review\n\n**Novelty: OPEN; publication: STOP.**\n",
        encoding="utf8")
    with (folder / "evidence_matrix.csv").open("w", encoding="utf8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(("claim", "source_url", "exact_evidence", "status", "relationship_to_project"))
        writer.writerow(("Novelty of the proposed method", "", "", "OPEN", "Requires primary-source audit"))
    (folder / "review.md").write_text(
        "# Independent-style review\n\n"
        "Claim / reasons / evidence / acknowledgement & response / warrant:\n\n"
        "See significance.md; independent review must answer all five reader questions.\n\n"
        "**Scientific novelty: OPEN. Publication: STOP.**\n", encoding="utf8")
    return folder


def main():
    p = argparse.ArgumentParser(description="Dataset-agnostic scientific research project harness")
    p.add_argument("--root", default=".")
    sub = p.add_subparsers(dest="command", required=True)
    i = sub.add_parser("init")
    i.add_argument("slug")
    i.add_argument("--title", required=True)
    for cmd in ("run", "freeze", "audit", "preflight"):
        q = sub.add_parser(cmd)
        q.add_argument("slug")
        if cmd == "audit":
            q.add_argument("--replay", action="store_true")
        if cmd == "preflight":
            q.add_argument("--stage", choices=("framing", "argument"), default="framing")
    args = p.parse_args()
    if args.command == "init":
        print(json.dumps({"project_dir": str(init(args.root, args.slug, args.title))}))
    elif args.command == "run":
        print(json.dumps(run(args.root, args.slug), indent=2))
    elif args.command == "freeze":
        print(json.dumps(freeze(args.root, args.slug), indent=2))
    elif args.command == "preflight":
        from research_lab.significance import check_file
        report = check_file(project_dir(args.root, args.slug) / "significance.md", stage=args.stage)
        print(json.dumps(report, indent=2))
        if report["status"] != "READY_FOR_HUMAN_REVIEW":
            raise SystemExit(2)
    else:
        print(json.dumps(audit(args.root, args.slug, args.replay), indent=2))


if __name__ == "__main__":
    main()
