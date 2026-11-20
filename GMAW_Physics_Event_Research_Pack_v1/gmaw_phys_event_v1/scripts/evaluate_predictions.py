#!/usr/bin/env python3
"""Evaluate reference or external original-MBGN predictions with one protocol."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
from gmaw_phys.metrics import evaluate_predictions, select_threshold, cluster_bootstrap


def read_events(path):
    if path is None:
        raise ValueError("Provide an events CSV, including headers for a genuinely empty table")
    return pd.read_csv(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", type=Path, required=True,
                        help="Scored split prediction CSV with manifest record fields and p_defect")
    parser.add_argument("--events", type=Path, required=True,
                        help="GT event CSV including seam_id/segment_id; header-only is allowed")
    parser.add_argument("--output", type=Path, required=True)
    choice = parser.add_mutually_exclusive_group()
    choice.add_argument("--threshold", type=float,
                        help="Previously fixed threshold; default is 0.5, never fit to scored split")
    choice.add_argument("--threshold-json", type=Path,
                        help="JSON from an earlier validation selection; must contain threshold")
    choice.add_argument("--validation-predictions", type=Path,
                        help="Separate validation CSV for threshold selection")
    parser.add_argument("--validation-events", type=Path)
    parser.add_argument("--save-threshold-json", type=Path)
    parser.add_argument("--iou-threshold", type=float, default=0.1)
    parser.add_argument("--merge-gap-mm", type=float, default=0.0)
    parser.add_argument("--min-length-mm", type=float, default=0.0)
    parser.add_argument("--bootstrap", type=int, default=0,
                        help="Optional number of fixed-threshold seam bootstrap replicates")
    parser.add_argument("--bootstrap-seed", type=int, default=0)
    parser.add_argument("--method-name", default="external_predictions",
                        help="For example original_MBGN_external; this does not assert a reproduction")
    args = parser.parse_args()
    pred = pd.read_csv(args.predictions)
    events = read_events(args.events)
    opts = dict(iou_threshold=args.iou_threshold, merge_gap_mm=args.merge_gap_mm,
                min_length_mm=args.min_length_mm)
    if args.validation_predictions:
        if args.validation_events is None:
            parser.error("--validation-events is required with --validation-predictions")
        if args.validation_predictions.resolve() == args.predictions.resolve():
            parser.error("Threshold selection file must be separate from scored prediction file")
        val = pd.read_csv(args.validation_predictions)
        val_events = read_events(args.validation_events)
        if set(val.seam_id.astype(str)) & set(pred.seam_id.astype(str)):
            parser.error("Validation and scored predictions must have disjoint seam_id values")
        if "split" not in val:
            # The separate command-line role is the provenance assertion.
            val = val.assign(split="val")
        selection = select_threshold(val, val_events, **opts)
    elif args.threshold_json:
        selection = json.loads(args.threshold_json.read_text(encoding="utf-8"))
        if "threshold" not in selection:
            parser.error("Threshold JSON must contain a threshold field")
        # Prevent quietly changing event postprocessing after threshold selection.
        prior = selection.get("evaluation_parameters", {})
        for key, value in opts.items():
            if key in prior and prior[key] != value:
                parser.error(f"{key} differs from saved validation threshold parameters")
    else:
        selection = dict(threshold=0.5 if args.threshold is None else args.threshold,
                         objective=None, reason="Fixed supplied/default threshold; no fit to scored data")
    selection["evaluation_parameters"] = opts
    if args.save_threshold_json:
        args.save_threshold_json.parent.mkdir(parents=True, exist_ok=True)
        args.save_threshold_json.write_text(json.dumps(selection, ensure_ascii=False,
                                                        indent=2, allow_nan=False), encoding="utf-8")
    result = evaluate_predictions(pred, events, threshold=selection["threshold"], **opts)
    result["threshold_selection"] = selection
    result["provenance"] = dict(method_name=args.method_name,
                                 predictions_file=str(args.predictions),
                                 events_file=str(args.events),
                                 original_mbgn_reproduced=False,
                                 note="Unified evaluation of supplied prediction files; no training or original MBGN reproduction is performed.")
    if args.bootstrap > 0:
        result["bootstrap"] = cluster_bootstrap(
            pred, events, threshold=selection["threshold"],
            n_bootstrap=args.bootstrap, seed=args.bootstrap_seed, **opts)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2,
                                      allow_nan=False), encoding="utf-8")
    print(json.dumps(dict(output=str(args.output), threshold=selection["threshold"],
                          frame=result["frame"], events=result["events"],
                          total_evaluated_m=result["coverage"]["total_evaluated_m"]),
                     ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
