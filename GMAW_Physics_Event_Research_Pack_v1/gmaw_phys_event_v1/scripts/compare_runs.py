#!/usr/bin/env python3
"""Compare frozen reference runs with a strict paired seam bootstrap."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
import yaml
from gmaw_phys.comparison import compare_predictions


def load_run(path):
    path = Path(path)
    prediction_file = path / "predictions_test.csv"
    events_file = path / "events_test.csv"
    selection_file = path / "threshold_selection.json"
    config_file = path / "resolved_config.yaml"
    required = [prediction_file, events_file, selection_file, config_file]
    for file in required:
        if not file.is_file():
            raise ValueError(f"Run file missing: {file}")
    selection = json.loads(selection_file.read_text(encoding="utf-8"))
    if selection.get("selection_split") != "validation":
        raise ValueError(f"{selection_file}: validation-only threshold provenance required")
    if "threshold" not in selection:
        raise ValueError(f"{selection_file}: missing frozen threshold")
    config = yaml.safe_load(config_file.read_text(encoding="utf-8"))
    opts = {key: config["evaluation"][key] for key in
            ("iou_threshold", "merge_gap_mm", "min_length_mm")}
    saved_opts = selection.get("evaluation_parameters", {})
    for key, value in opts.items():
        if key in saved_opts and saved_opts[key] != value:
            raise ValueError(f"{path}: saved threshold evaluation parameter {key} disagrees with config")
    predictions = pd.read_csv(prediction_file)
    if "split" in predictions and not predictions["split"].astype(str).eq("test").all():
        raise ValueError(f"{prediction_file}: contains non-test predictions")
    # This audits existing exported split identities; it does not rerun validation.
    val_file = path / "predictions_val.csv"
    if val_file.is_file():
        val = pd.read_csv(val_file, usecols=["seam_id"])
        if set(val.seam_id.astype(str)) & set(predictions.seam_id.astype(str)):
            raise ValueError(f"{path}: validation/test seam overlap")
    provenance = dict(run_dir=str(path), threshold_selection=selection,
                      file_sha256={file.name: hashlib.sha256(file.read_bytes()).hexdigest()
                                   for file in required})
    return predictions, pd.read_csv(events_file), float(selection["threshold"]), opts, provenance


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-a", required=True, type=Path)
    parser.add_argument("--run-b", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--label-a")
    parser.add_argument("--label-b")
    parser.add_argument("--bootstrap", type=int, default=1000)
    parser.add_argument("--confidence", type=float, default=.95)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    try:
        a, ga, ta, opts_a, provenance_a = load_run(args.run_a)
        b, gb, tb, opts_b, provenance_b = load_run(args.run_b)
        if opts_a != opts_b:
            raise ValueError("Runs use different event evaluation parameters; paired comparison refused")
        result = compare_predictions(a, ga, b, gb, ta, tb, **opts_a,
                                     n_bootstrap=args.bootstrap,
                                     confidence=args.confidence, seed=args.seed,
                                     label_a=args.label_a or args.run_a.name,
                                     label_b=args.label_b or args.run_b.name)
    except (ValueError, KeyError) as exc:
        parser.error(str(exc))
    result["provenance"] = dict(run_a=provenance_a, run_b=provenance_b,
                                validation_threshold_provenance_verified=True,
                                original_mbgn_reproduced=False)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2,
                                      allow_nan=False), encoding="utf-8")
    print(json.dumps(dict(output=str(args.output), evidence_status=result["evidence_status"],
                          n_evaluable_seams=result["n_evaluable_seams"],
                          metric_comparisons=result["metric_comparisons"]),
                     ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
