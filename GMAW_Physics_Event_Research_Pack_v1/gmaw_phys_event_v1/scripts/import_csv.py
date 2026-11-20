"""Import an explicitly described, existing CSV dataset. Never invent labels.

Input manifest uses the standard schema, except signal_path names a native CSV
with t_s,current_a,voltage_v. All paths must be relative to --source. The importer
copies supplied images/metadata and converts only the signal storage to NPZ.
"""
import argparse
from pathlib import Path
import shutil
import sys
import json
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from gmaw_phys.data import _manifest, _read_segment, safe_path, validate_dataset


def import_csv_dataset(source, destination):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if destination == source or destination.is_relative_to(source):
        raise ValueError("Destination must be a separate directory outside the source")
    if destination.exists() and any(destination.iterdir()):
        raise FileExistsError("Destination is nonempty; source records will not be overwritten")
    manifest = _manifest(source)
    destination.mkdir(parents=True, exist_ok=True)
    converted = []
    for j, row in enumerate(manifest.to_dict("records")):
        frames, _, _ = _read_segment(source, row)
        signal_file = safe_path(source, row["signal_path"])
        native = pd.read_csv(signal_file)
        keys = ["t_s", "current_a", "voltage_v"]
        if not set(keys).issubset(native.columns):
            raise ValueError(f"{signal_file.name}: native CSV must contain {keys}; rename columns explicitly upstream")
        signals = {key: pd.to_numeric(native[key], errors="raise").to_numpy(float) for key in keys}
        if not all(np.isfinite(a).all() for a in signals.values()):
            raise ValueError("Nonfinite native CSV data")
        paths = [row[name] for name in ("frames_path", "trajectory_path", "events_path")] + list(frames.image_path)
        for rel in paths:
            path = safe_path(source, rel)
            target = destination / str(rel)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
        rel_signal = f"native_signals/segment_{j:05d}.npz"
        (destination / "native_signals").mkdir(exist_ok=True)
        np.savez_compressed(destination / rel_signal, **signals)
        converted.append(dict(row, signal_path=rel_signal))
    pd.DataFrame(converted, columns=manifest.columns).to_csv(destination / "manifest.csv", index=False)
    report = validate_dataset(destination)
    (destination / "import_validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    if not report["ok"]:
        raise ValueError("Imported data failed validation; inspect import_validation.json. No labels or metadata were inferred.")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", "--out", dest="output", required=True)
    args = parser.parse_args()
    print(json.dumps(import_csv_dataset(args.source, args.output), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
