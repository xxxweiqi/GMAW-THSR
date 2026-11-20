#!/usr/bin/env python3
"""Train one reference model and evaluate once with validation-frozen threshold."""
from pathlib import Path
import argparse
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from gmaw_phys.train import read_config, run_training


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data", required=True)
    p.add_argument("--config", default="configs/research.yaml")
    p.add_argument("--out", required=True)
    p.add_argument("--model", choices=["snapshot_fusion", "history_gru", "power_features", "thermal_filter", "phys_align"])
    p.add_argument("--epochs", type=int)
    p.add_argument("--seed", type=int)
    args = p.parse_args()
    cfg = read_config(args.config)
    if args.model:
        cfg["model"]["name"] = args.model
        if args.model != "phys_align":
            cfg["model"].update(use_heat=args.model == "thermal_filter", use_alignment=False, use_aux=False)
    if args.epochs is not None:
        cfg["train"]["epochs"] = args.epochs
    if args.seed is not None:
        cfg["seed"] = args.seed
    run_training(args.data, cfg, args.out)


if __name__ == "__main__":
    main()
