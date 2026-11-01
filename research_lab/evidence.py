"""Structural literature-evidence checks; not a factual source-verification service."""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
from urllib.parse import urlsplit

STATES = {"VERIFIED", "UNVERIFIED", "CONTRADICTED", "OPEN"}
FIELDS = ("claim", "source_url", "exact_evidence", "status", "relationship_to_project")


def validate_matrix(path: str | Path) -> dict:
    with Path(path).open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or not set(FIELDS).issubset(reader.fieldnames):
            raise ValueError(f"{path}: expected columns {FIELDS}")
        rows = list(reader)
    if not rows:
        raise ValueError(f"{path}: empty matrix")
    counts = {state: 0 for state in sorted(STATES)}
    for number, row in enumerate(rows, 2):
        if None in row:
            raise ValueError(f"{path}:{number}: surplus CSV columns")
        status = (row["status"] or "").strip()
        if status not in STATES:
            raise ValueError(f"{path}:{number}: unsupported evidence state {status!r}")
        counts[status] += 1
        if not (row["claim"] or "").strip() or not (row["relationship_to_project"] or "").strip():
            raise ValueError(f"{path}:{number}: missing claim or overlap analysis")
        url = (row["source_url"] or "").strip()
        support = (row["exact_evidence"] or "").strip()
        if status in {"VERIFIED", "CONTRADICTED"} and (not url or not support):
            raise ValueError(f"{path}:{number}: evidence and source URL required for {status}")
        if url:
            parts = urlsplit(url)
            if parts.scheme != "https" or not parts.netloc:
                raise ValueError(f"{path}:{number}: expected HTTPS primary-source URL")
        if status == "OPEN" and not url and support:
            raise ValueError(f"{path}:{number}: unsupported OPEN claim must not present source evidence")
    return {
        "matrix": str(path), "rows": len(rows), "states": counts,
        "novelty_automatically_verified": False,
        "meaning": "Schema validation only; verify sources by reading them."
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("matrices", nargs="+")
    args = p.parse_args()
    print(json.dumps([validate_matrix(path) for path in args.matrices], indent=2))


if __name__ == "__main__":
    main()
