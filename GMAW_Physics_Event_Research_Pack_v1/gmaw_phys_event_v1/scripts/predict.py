#!/usr/bin/env python3
"""Export predictions from a saved reference checkpoint; does not retrain."""
from pathlib import Path
import argparse
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from gmaw_phys.train import predict_checkpoint


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data", required=True)
    p.add_argument("--checkpoint", required=True)
    p.add_argument("--split", default="test", choices=["train", "val", "test"])
    p.add_argument("--device", default="cpu")
    p.add_argument("--out", required=True)
    args = p.parse_args()
    df, ds = predict_checkpoint(args.data, args.checkpoint, args.split, args.device)
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    ds.events.to_csv(path.with_name(path.stem + "_events.csv"), index=False)
    print(path)


if __name__ == "__main__":
    main()
