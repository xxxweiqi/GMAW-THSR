"""Validate a dataset and save a machine-readable report without mutation."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from gmaw_phys.data import validate_dataset


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", "--dataset", dest="data", required=True)
    parser.add_argument("--output", "--out", dest="output")
    args = parser.parse_args()
    report = validate_dataset(args.data)
    rendered = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(rendered, encoding="utf-8")
    print(rendered)
    raise SystemExit(0 if report["ok"] else 2)


if __name__ == "__main__":
    main()
