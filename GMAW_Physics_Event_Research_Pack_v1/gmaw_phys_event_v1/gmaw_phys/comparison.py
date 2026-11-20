"""Strict paired evaluation of two frozen runs on identical test observations."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .metrics import evaluate_predictions, _prepare_predictions, _prepare_events

_FRAME_KEYS = ["seam_id", "segment_id", "sample_id"]
_EVENT_KEYS = ["seam_id", "segment_id", "event_id"]
_METRICS = {
    "events.f1": "higher",
    "events.recall": "higher",
    "events.false_positive_events_per_evaluated_m": "lower",
    "frame.average_precision": "higher",
}


def _canonical_table(table, keys, name):
    table = pd.DataFrame(table).copy()
    missing = [key for key in keys if key not in table]
    if missing:
        raise ValueError(f"{name} missing identity columns: {missing}")
    for key in keys:
        if table[key].isna().any():
            raise ValueError(f"{name}: missing {key}")
        table[key] = table[key].astype(str)
    if table.duplicated(keys).any():
        raise ValueError(f"{name}: duplicate identity keys")
    return table.sort_values(keys).reset_index(drop=True)


def _is_prediction_column(name):
    return name == "p_defect" or (name.startswith("geom_") and name.endswith("_pred"))


def _assert_equal_columns(a, b, columns, kind):
    for key in columns:
        try:
            pd.testing.assert_series_equal(a[key], b[key], check_dtype=False,
                                           check_exact=True, check_names=False)
        except AssertionError as exc:
            raise ValueError(f"{kind} mismatch in {key}; paired comparison requires identical evaluation data") from exc


def validate_paired_inputs(pred_a, events_a, pred_b, events_b):
    """Reject unequal samples, metadata, labels or GT; never silently intersect.

    Row order and numeric dtype are immaterial. Values must match exactly;
    prediction probabilities and exported geometry predictions may differ.
    """
    a = _canonical_table(pred_a, _FRAME_KEYS, "Run A predictions")
    b = _canonical_table(pred_b, _FRAME_KEYS, "Run B predictions")
    a = _prepare_predictions(a)
    b = _prepare_predictions(b)
    if len(a) != len(b):
        raise ValueError("Sample identity mismatch: unequal prediction row counts")
    _assert_equal_columns(a, b, _FRAME_KEYS, "Sample identity")
    fixed_a = {key for key in a if not _is_prediction_column(key)}
    fixed_b = {key for key in b if not _is_prediction_column(key)}
    if fixed_a != fixed_b:
        raise ValueError(f"Prediction metadata schemas differ: {sorted(fixed_a ^ fixed_b)}")
    _assert_equal_columns(a, b, sorted(fixed_a), "Prediction metadata/coverage/labels")

    # Compare raw GT before target filtering, including non-target exclusions,
    # uncertainty, confidence and reference times when those columns are present.
    ga = _canonical_table(events_a, _EVENT_KEYS, "Run A events")
    gb = _canonical_table(events_b, _EVENT_KEYS, "Run B events")
    if set(ga) != set(gb) or len(ga) != len(gb):
        raise ValueError("Ground truth mismatch: unequal event schema or row count")
    _assert_equal_columns(ga, gb, sorted(ga.columns), "Ground truth")
    _prepare_events(ga)  # Validate finite intervals and unique IDs.
    _prepare_events(gb)
    return a, ga, b, gb


def _value(result, path):
    section, metric = path.split(".", 1)
    return result[section][metric]


def _synthetic_status(predictions):
    if "synthetic" not in predictions:
        return "SOURCE_STATUS_UNVERIFIED"
    flags = predictions.synthetic.fillna(False).astype(str).str.lower().isin(
        ["true", "1", "1.0", "yes"])
    if len(flags) and flags.all():
        return "SYNTHETIC_PIPELINE_ONLY"
    if flags.any():
        return "CONTAINS_SYNTHETIC_DATA"
    return "USER_DATA_REFERENCE_COMPARISON"


def compare_predictions(pred_a, events_a, pred_b, events_b, threshold_a,
                        threshold_b, iou_threshold=0.1, merge_gap_mm=0.0,
                        min_length_mm=0.0, n_bootstrap=1000,
                        confidence=0.95, seed=0, label_a="run_a",
                        label_b="run_b"):
    """Return B-A differences and paired seam-cluster percentile intervals.

    Thresholds must already be frozen on each run's own validation predictions.
    The function never calls threshold selection and never optimizes on test.
    The CLI verifies saved threshold provenance; direct callers own provenance.
    """
    if not isinstance(n_bootstrap, (int, np.integer)) or n_bootstrap < 0:
        raise ValueError("n_bootstrap must be a nonnegative integer")
    if not np.isfinite(confidence) or not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")
    a, ga, b, gb = validate_paired_inputs(pred_a, events_a, pred_b, events_b)
    opts = dict(iou_threshold=iou_threshold, merge_gap_mm=merge_gap_mm,
                min_length_mm=min_length_mm)
    result_a = evaluate_predictions(a, ga, threshold=threshold_a, **opts)
    result_b = evaluate_predictions(b, gb, threshold=threshold_b, **opts)
    seams = sorted(set(a.loc[a._scored, "seam_id"]))
    unevaluated = sorted((set(a.seam_id) | set(ga.seam_id)) - set(seams))
    samples = {key: [] for key in _METRICS}
    completed = int(n_bootstrap) if len(seams) >= 2 else 0
    if completed:
        rng = np.random.default_rng(seed)
        # Store cluster slices once; each repeated draw is still a distinct copy.
        clusters_a = {s: a.loc[a.seam_id == s] for s in seams}
        clusters_b = {s: b.loc[b.seam_id == s] for s in seams}
        clusters_gt = {s: ga.loc[ga.seam_id == s] for s in seams}
        for _ in range(completed):
            pa, pb, ge = [], [], []
            for copy_id, seam in enumerate(rng.choice(seams, len(seams), replace=True)):
                new_id = f"bootstrap_copy_{copy_id}"
                pa.append(clusters_a[seam].assign(seam_id=new_id))
                pb.append(clusters_b[seam].assign(seam_id=new_id))
                ge.append(clusters_gt[seam].assign(seam_id=new_id))
            sampled_gt = pd.concat(ge, ignore_index=True)
            ra = evaluate_predictions(pd.concat(pa, ignore_index=True), sampled_gt,
                                      threshold=threshold_a, **opts)
            rb = evaluate_predictions(pd.concat(pb, ignore_index=True), sampled_gt,
                                      threshold=threshold_b, **opts)
            for key in _METRICS:
                va, vb = _value(ra, key), _value(rb, key)
                if va is not None and vb is not None:
                    samples[key].append(float(vb - va))
    alpha = (1.0 - confidence) / 2.0
    comparisons = {}
    for key, favorable in _METRICS.items():
        va, vb = _value(result_a, key), _value(result_b, key)
        values = samples[key]
        bounds = np.quantile(values, [alpha, 1 - alpha]) if values else [None, None]
        comparisons[key] = dict(
            run_a=va, run_b=vb,
            difference_b_minus_a=float(vb - va) if va is not None and vb is not None else None,
            favorable_direction=favorable,
            paired_bootstrap_ci=dict(
                lower=float(bounds[0]) if bounds[0] is not None else None,
                upper=float(bounds[1]) if bounds[1] is not None else None,
                valid_replicates=len(values),
                undefined_replicates=completed - len(values)))
    reason = ("Fewer than two evaluable seams: no confidence interval."
              if len(seams) < 2 else
              "Bootstrap disabled; point estimates only." if n_bootstrap == 0 else
              "Few independent seams can give unstable intervals; many adjacent frames do not increase the cluster sample size.")
    return dict(
        label_a=str(label_a), label_b=str(label_b),
        threshold_a=float(threshold_a), threshold_b=float(threshold_b),
        evaluation_parameters=opts, paired_inputs_verified=True,
        identical_sample_count=len(a), n_evaluable_seams=len(seams),
        unevaluated_seams_excluded=unevaluated,
        total_evaluated_m=result_a["coverage"]["total_evaluated_m"],
        evidence_status=_synthetic_status(a),
        metric_comparisons=comparisons,
        run_a=dict(frame=result_a["frame"], clear_core=result_a["clear_core"],
                   events=result_a["events"], coverage=result_a["coverage"]),
        run_b=dict(frame=result_b["frame"], clear_core=result_b["clear_core"],
                   events=result_b["events"], coverage=result_b["coverage"]),
        bootstrap=dict(method="paired seam-cluster percentile differences (B minus A)",
                       confidence=float(confidence), seed=int(seed),
                       requested_replicates=int(n_bootstrap), completed_replicates=completed,
                       thresholds_refitted=False,
                       same_cluster_draws_for_both_runs=True, warning=reason),
        interpretation="Positive B-A favors B for F1/recall/AP; negative B-A favors B for FP per evaluated metre. Intervals describe test-seam sampling only, not training-seed variance, causal proof, or a welding experiment. No hypothesis-test p-value is claimed.")
