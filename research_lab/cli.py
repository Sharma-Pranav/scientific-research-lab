"""Entry points: python -m research_lab.cli {pilot,audit,gate}."""
import argparse
import json
from pathlib import Path
from research_lab.engine import audit, run, validate_proposal


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["pilot", "audit", "gate"])
    parser.add_argument("proposal", nargs="?")
    parser.add_argument("--phase", choices=["exploratory", "confirmatory"], default="exploratory")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root)
    if args.command == "pilot":
        config = root / "research" / "robust-location" / (args.phase + ".json")
        manifest, result = run(root, config)
        print(f"run: {manifest['run_id']} | phase: {args.phase} | config_sha256: {manifest['config_hash']}")
        for item in result["conditions"]:
            print(f"rate={item['rate']}: median_minus_mean={item['delta_mean']:.6f}, approx_95ci={item['approx_95ci']}")
    elif args.command == "audit":
        print(f"registry audit: PASS ({audit(root)} runs)")
    else:
        if not args.proposal:
            parser.error("gate requires path to proposal.json")
        decisions, publication = validate_proposal(json.loads(Path(args.proposal).read_text(encoding="utf8")))
        print(json.dumps({"gates": decisions, "publication_decision": publication}, indent=2))

if __name__ == "__main__":
    main()
