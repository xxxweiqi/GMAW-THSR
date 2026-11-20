#!/usr/bin/env python3
"""Run prespecified baseline/ablation matrix without test-based model selection."""
from pathlib import Path
import argparse
import copy
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from gmaw_phys.train import read_config, run_training, write_json


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data", required=True)
    p.add_argument("--config", default="configs/research.yaml")
    p.add_argument("--matrix", default="configs/experiments.yaml")
    p.add_argument("--out", required=True)
    p.add_argument("--seeds", default="17,42,73")
    p.add_argument("--only", default="", help="Comma separated experiment IDs; empty means all")
    p.add_argument("--epochs", type=int)
    args = p.parse_args()
    base = read_config(args.config)
    matrix = read_config(args.matrix)["experiments"]
    selected = set(filter(None, args.only.split(",")))
    records = []
    for row in matrix:
        if selected and row["id"] not in selected:
            continue
        for seed in map(int, args.seeds.split(",")):
            cfg = copy.deepcopy(base)
            cfg["seed"] = seed
            cfg["model"].update({"name": row["model"], **{k: row[k] for k in
                                 ("use_heat", "use_alignment", "use_aux")}})
            if args.epochs is not None:
                cfg["train"]["epochs"] = args.epochs
            result = run_training(args.data, cfg, Path(args.out) / row["id"] / f"seed_{seed}")
            records.append({"id": row["id"], "seed": seed, **result})
            write_json(Path(args.out) / "suite_results.json", records)
    if not records:
        raise ValueError("No experiments selected.")


if __name__ == "__main__":
    main()
