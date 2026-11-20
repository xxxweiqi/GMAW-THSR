"""Frozen-checkpoint stress test with genuinely older electrical observations.

This is a stale-electrical-sensor availability experiment, NOT clock calibration
or an estimator of physical formation delay. Current images, targets, process
conditions and RT labels remain fixed. Every condition shares exactly the same
eligible sample IDs and evaluated spatial cells. No retraining/threshold tuning.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from gmaw_phys.data import build_dataset, validate_dataset
from gmaw_phys.models import build_model
from gmaw_phys.physics import alignment_prior
from gmaw_phys.metrics import evaluate_predictions
from gmaw_phys.train import set_seed, choose_device, predict_loader, write_json


def _hash_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def assert_causal_contract(cfg):
    data = cfg.get("data", {})
    if float(data.get("signal_window_s", .1)) <= 0:
        raise ValueError("The causal past waveform window must be positive")
    for key in ("signal_window_mode", "signal_window_alignment", "window_alignment"):
        if key in data and str(data[key]).lower() not in {"causal", "past", "past_only", "trailing"}:
            raise ValueError(f"{key} is not a causal past-only window; centered/future windows are rejected")
    for key in ("centered_window", "signal_centered"):
        if key in data and str(data[key]).lower() not in {"false", "0", "none"}:
            raise ValueError("Centered/future waveform windows are not supported")
    for key in ("signal_future_s", "future_window_s", "signal_lookahead_s", "future_context_s"):
        if float(data.get(key, 0.)) > 0:
            raise ValueError("Future electrical context is prohibited")


def normalize_delays(delays):
    values = [int(x) for x in delays]
    if any(v < 0 or v != float(x) for v, x in zip(values, delays)):
        raise ValueError("Delays must be nonnegative integer numbers of original frames")
    values = sorted(set(values))
    if not values or values[0] != 0:
        raise ValueError("Include delay 0 as the same-coverage baseline")
    return values


def read_frozen_threshold(path):
    info = json.loads(Path(path).read_text(encoding="utf-8"))
    if str(info.get("selection_split", "")).lower() not in {"val", "validation"}:
        raise ValueError("Threshold file must explicitly identify selection_split=validation")
    if not info.get("split_column_verified", False):
        raise ValueError("Threshold provenance must confirm the validation split column was checked")
    threshold = float(info["threshold"])
    if not np.isfinite(threshold) or not 0 <= threshold <= 1:
        raise ValueError("Invalid frozen probability threshold")
    return threshold, info


def delay_plan(dataset, current_index, delay):
    """Return geometry-only plan or a reason; never inspect labels/events.

    This adapter deliberately uses the reference loader's frame-level caches,
    rather than moving back d *eligible records*. The latter would silently
    change the delay when other-defect/unknown rows have been excluded.
    """
    if int(delay) != delay or delay < 0:
        raise ValueError("Only integer nonnegative delays are causal")
    si, k, _, _ = dataset._indices[current_index]
    seg = dataset._segments[si]
    source = k - int(delay)
    first = source - dataset.history + 1
    if first < 0:
        return None, "insufficient_original_frame_history"
    times = seg["frame_t"]
    if source >= len(times) or times[source] > times[k] or (delay > 0 and times[source] >= times[k]):
        return None, "not_strictly_earlier_electrical_anchor"
    if times[source] - seg["signal_start"] < float(dataset.dc.get("warmup_s", 0.)) - 1e-10:
        return None, "delayed_anchor_before_thermal_warmup"
    earliest_native = times[first] - max(.125, dataset.window)
    if earliest_native < seg["signal_start"] - 1e-10 or times[source] > seg["signal_end"] + 1e-10:
        return None, "missing_observed_native_support"
    # This also checks the time between stale and current anchors. A missing
    # camera frame must not silently turn 4 frames into an arbitrary time gap.
    if np.any(np.diff(times[first:k + 1]) > float(dataset.dc.get("max_image_gap_s", .20))):
        return None, "original_frame_gap_in_shifted_interval"
    positions = seg["positions"][first:source + 1]
    target = float(seg["target"][k])
    sigma = max(float(seg["row"]["position_sigma_mm"]),
                float(dataset.dc.get("position_sigma_floor_mm", .5)))
    prior, mask = alignment_prior(positions, target, sigma,
        float(dataset.dc.get("alignment_pre_mm", 3.)),
        float(dataset.dc.get("alignment_post_mm", 1.5)))
    if not np.any(mask):
        return None, "no_geometry_support_for_current_target"
    return dict(segment_index=si, current_frame=k, source_frame=source,
                first_frame=first, prior=prior, mask=mask,
                age_s=float(times[k] - times[source]),
                oldest_signal_start_s=float(times[first] - dataset.window),
                latest_signal_end_s=float(times[source])), None


def common_support(dataset, delays):
    delays = normalize_delays(delays)
    per_delay, diagnostics = {}, {}
    for delay in delays:
        plans, rejected = {}, Counter()
        for index in range(len(dataset)):
            plan, reason = delay_plan(dataset, index, delay)
            if plan is None:
                rejected[reason] += 1
            else:
                plans[index] = plan
        per_delay[delay] = plans
        diagnostics[str(delay)] = {"eligible_before_intersection": len(plans),
                                   "rejected_by_reason": dict(rejected)}
    common = sorted(set.intersection(*(set(plans) for plans in per_delay.values())))
    return common, per_delay, diagnostics


class DelayedElectricalView(Dataset):
    """Keep current observation/label fields, replace only electrical history."""
    def __init__(self, base, common_indices, plans, delay):
        self.base, self.common_indices, self.plans, self.delay = base, list(common_indices), plans, int(delay)
        self.events = base.events
        self.records = []
        for original in self.common_indices:
            plan = plans[original]
            seg = base._segments[plan["segment_index"]]
            record = dict(base.records[original])
            record.update(delay_frames=int(delay), electrical_age_s=plan["age_s"],
                electrical_source_sample_id=str(seg["frames"].iloc[plan["source_frame"]].sample_id),
                electrical_oldest_window_start_s=plan["oldest_signal_start_s"],
                electrical_latest_window_end_s=plan["latest_signal_end_s"],
                physical_support_tokens=int(np.count_nonzero(plan["mask"])))
            self.records.append(record)

    def __len__(self):
        return len(self.common_indices)

    def __getitem__(self, index):
        original = self.common_indices[index]
        result = {key: value.clone() for key, value in self.base[original].items()}
        plan = self.plans[original]
        si, first, end = plan["segment_index"], plan["first_frame"], plan["source_frame"]
        seg = self.base._segments[si]
        result["signal"] = torch.as_tensor(np.stack([self.base._wave(si, j) for j in range(first, end + 1)]))
        result["power"] = torch.as_tensor(seg["power"][first:end + 1, None].copy(), dtype=torch.float32)
        result["thermal"] = torch.as_tensor(seg["thermal"][first:end + 1].copy(), dtype=torch.float32)
        result["position"] = torch.as_tensor(seg["positions"][first:end + 1].copy(), dtype=torch.float32)
        result["alignment_prior"] = torch.as_tensor(plan["prior"].copy(), dtype=torch.float32)
        result["alignment_mask"] = torch.as_tensor(plan["mask"].copy(), dtype=torch.bool)
        result["index"] = torch.tensor(index, dtype=torch.int64)
        # image (including current image), condition, target_position, labels and
        # future geometry targets are deliberately inherited without changes.
        return result


def run_stress(data_root, checkpoint_path, output_dir, delays=(0, 1, 2, 4),
               threshold_path=None, split="test", device="cpu", batch_size=None):
    if split not in {"val", "test"}:
        raise ValueError("Stress evaluation accepts val/test; it never trains")
    checkpoint_path, output_dir = Path(checkpoint_path).resolve(), Path(output_dir).resolve()
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError("Output directory must be empty; no existing experiment is overwritten")
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    if checkpoint.get("reference_not_original_mbgn") is not True:
        raise ValueError("Only this reference pipeline's causal raw-input checkpoints are accepted")
    cfg = checkpoint["config"]
    assert_causal_contract(cfg)
    delays = normalize_delays(delays)
    threshold_path = Path(threshold_path or checkpoint_path.parent / "threshold_selection.json").resolve()
    threshold, threshold_info = read_frozen_threshold(threshold_path)
    validation = validate_dataset(data_root)
    if not validation["ok"]:
        raise ValueError("Dataset validation failed: " + "; ".join(validation["errors"]))
    prior_qc = checkpoint_path.parent / "data_validation.json"
    if prior_qc.exists():
        original_fingerprint = json.loads(prior_qc.read_text(encoding="utf-8")).get("data_fingerprint_sha256")
        if original_fingerprint and original_fingerprint != validation["data_fingerprint_sha256"]:
            raise ValueError("Dataset fingerprint differs from the checkpoint run; restore the recorded dataset")
    set_seed(int(cfg.get("seed", 42)), int(cfg.get("train", {}).get("torch_threads", 2)))
    device = choose_device(device)
    base = build_dataset(data_root, cfg, split)
    common, per_delay, diagnostics = common_support(base, delays)
    output_dir.mkdir(parents=True, exist_ok=True)
    coverage = {"original_eligible_samples": len(base), "common_samples": len(common),
        "removed_from_common_support": len(base) - len(common), "delays_frames": delays,
        "per_delay_eligibility": diagnostics,
        "sample_intersection_rule": "all requested delays pass causal raw support, warmup, no gaps and geometry support; no label/probability criterion",
        "identical_spatial_cells": True, "threshold_retuned": False,
        "physical_support_expanded": False,
        "warning": "Delay 0 is rescored on the common intersection; compare against that baseline, not the original full test score."}
    write_json(output_dir / "common_coverage.json", coverage)
    if not common:
        raise ValueError("No common legal support. Inspect common_coverage.json and explicitly choose smaller --delays; support widths were not changed.")
    base_records = pd.DataFrame([base.records[i] for i in common])
    base_records.to_csv(output_dir / "common_records.csv", index=False)
    base.events.to_csv(output_dir / "reference_events.csv", index=False)
    coverage["common_sample_ids_sha256"] = hashlib.sha256("\n".join(base_records.sample_id.astype(str)).encode()).hexdigest()
    model = build_model(cfg).to(device)
    model.load_state_dict(checkpoint["state_dict"], strict=True)
    model.eval()
    eval_options = {key: cfg.get("evaluation", {}).get(key, default) for key, default in
                    (("iou_threshold", .1), ("merge_gap_mm", 0.), ("min_length_mm", 0.))}
    summaries, metrics_by_delay = [], {}
    for delay in delays:
        view = DelayedElectricalView(base, common, per_delay[delay], delay)
        loader = DataLoader(view, batch_size=int(batch_size or cfg.get("train", {}).get("batch_size", 32)),
                            shuffle=False, num_workers=0)
        predictions = predict_loader(model, loader, view, device)
        predictions["split"] = split
        # IDs, labels and coverage cells must agree exactly across conditions.
        for key in ("sample_id", "seam_id", "segment_id", "s_mm", "cell_start_mm", "cell_end_mm", "y_hard", "y_soft", "label_weight"):
            if not np.array_equal(predictions[key].to_numpy(), base_records[key].to_numpy()):
                raise AssertionError(f"Stress intervention changed current {key}")
        predictions.to_csv(output_dir / f"predictions_delay_{delay:02d}.csv", index=False)
        metrics = evaluate_predictions(predictions, base.events, threshold=threshold, **eval_options)
        metrics["evidence_status"] = "SYNTHETIC_PIPELINE_ONLY" if validation.get("synthetic") else "USER_DATA_STALE_SENSOR_STRESS"
        metrics["stress_delay_frames"] = delay
        metrics["threshold_source"] = str(threshold_path)
        metrics["threshold_retuned"] = False
        age = predictions.electrical_age_s.to_numpy(float)
        metrics["electrical_age_s"] = {"min": float(age.min()), "median": float(np.median(age)), "max": float(age.max())}
        metrics["timing_note"] = "Current decision time retained; electrical history is intentionally stale. This is not measured clock error or a calibrated formation lag. Runtime and actuator delay are excluded."
        write_json(output_dir / f"metrics_delay_{delay:02d}.json", metrics)
        metrics_by_delay[delay] = metrics
        event = metrics["events"]
        summaries.append(dict(delay_frames=delay, electrical_age_ms_median=float(np.median(age) * 1000),
            samples=len(predictions), threshold=threshold,
            evaluated_m=metrics["coverage"]["total_evaluated_m"],
            frame_macro_f1=metrics["frame"]["macro_f1"], frame_average_precision=metrics["frame"]["average_precision"],
            event_f1=event["f1"], event_recall=event["recall"],
            false_positive_events_per_evaluated_m=event["false_positive_events_per_evaluated_m"],
            matched_boundary_mae_mm=event["matched_boundary_mae_mm"],
            first_hit_delay_s=event["first_threshold_hit_delay_s_mean"]))
    # Physical coverage must be exactly the same in every condition, not just n.
    baseline_coverage = metrics_by_delay[0]["coverage"]
    if any(m["coverage"] != baseline_coverage for m in metrics_by_delay.values()):
        raise AssertionError("Evaluated spatial coverage changed across delay conditions")
    coverage["evaluation_coverage"] = baseline_coverage
    coverage["observed_event_count"] = metrics_by_delay[0]["events"]["observed_gt_events"]
    write_json(output_dir / "common_coverage.json", coverage)
    pd.DataFrame(summaries).to_csv(output_dir / "stress_summary.csv", index=False)
    write_json(output_dir / "stress_run_info.json", dict(
        checkpoint=str(checkpoint_path), checkpoint_sha256=_hash_file(checkpoint_path),
        threshold_file=str(threshold_path), threshold_file_sha256=_hash_file(threshold_path),
        threshold_selection=threshold_info, data_fingerprint_sha256=validation["data_fingerprint_sha256"],
        split=split, delays_frames=delays, device=str(device), model=cfg["model"],
        common_sample_ids_sha256=coverage["common_sample_ids_sha256"],
        intervention="strictly older electrical/power/thermal/position history, unchanged current image/condition/target/labels",
        labels_used_to_choose_delay_or_support=False, original_physics_support_unchanged=True,
        evidence_status=metrics_by_delay[0]["evidence_status"]))
    return dict(output_dir=str(output_dir), coverage=coverage, summary=summaries)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--output", "--out", dest="output", required=True)
    parser.add_argument("--threshold-file")
    parser.add_argument("--delays", default="0,1,2,4", help="Nonnegative original-frame shifts; include 0")
    parser.add_argument("--split", choices=["val", "test"], default="test")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--batch-size", type=int)
    args = parser.parse_args()
    result = run_stress(args.data, args.checkpoint, args.output,
        delays=[int(x.strip()) for x in args.delays.split(",")], threshold_path=args.threshold_file,
        split=args.split, device=args.device, batch_size=args.batch_size)
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
