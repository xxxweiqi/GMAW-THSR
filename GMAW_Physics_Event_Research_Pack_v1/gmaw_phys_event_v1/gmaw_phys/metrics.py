"""Common binary and spatial event evaluation for reference/external predictions.

This is an evaluator, not a reproduction of the published MBGN. Distances are
millimetres. Only labelled prediction cells contribute to evaluated coverage.
"""
from __future__ import annotations

from typing import Any
import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
from sklearn.metrics import average_precision_score, roc_auc_score

_EPS = 1e-8
_KEYS = ["seam_id", "segment_id"]


def _number(x: Any) -> float | None:
    if x is None or pd.isna(x):
        return None
    x = float(x)
    return x if np.isfinite(x) else None


def _ratio(a: float, b: float) -> float | None:
    return float(a / b) if b > 0 else None


def _union(intervals):
    result = []
    for a, b in sorted(intervals):
        if b <= a:
            continue
        if result and a <= result[-1][1] + _EPS:
            result[-1] = (result[-1][0], max(b, result[-1][1]))
        else:
            result.append((float(a), float(b)))
    return result


def _length(intervals):
    return float(sum(b - a for a, b in intervals))


def _intersect(intervals, start, end):
    return [(max(a, start), min(b, end)) for a, b in intervals
            if min(b, end) > max(a, start)]


def _boolean_series(series):
    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False).to_numpy(dtype=bool)
    return series.fillna(False).astype(str).str.lower().isin(
        ["true", "1", "1.0", "yes"]).to_numpy()


def _prepare_predictions(df):
    df = pd.DataFrame(df).copy().reset_index(drop=True)
    required = _KEYS + ["cell_start_mm", "cell_end_mm", "y_hard", "p_defect"]
    missing = [k for k in required if k not in df]
    if missing:
        raise ValueError("Prediction columns missing: " + ", ".join(missing))
    if df[_KEYS].isna().any().any():
        raise ValueError("seam_id and segment_id cannot be missing")
    for key in _KEYS:
        df[key] = df[key].astype(str)
    for key in ["cell_start_mm", "cell_end_mm", "p_defect"]:
        df[key] = pd.to_numeric(df[key], errors="raise")
        if not np.isfinite(df[key].to_numpy(dtype=float)).all():
            raise ValueError(f"{key} must be finite")
    if ((df.p_defect < 0) | (df.p_defect > 1)).any():
        raise ValueError("p_defect must be in [0, 1]")
    if (df.cell_end_mm <= df.cell_start_mm).any():
        raise ValueError("Every prediction cell must have positive length")
    df["y_hard"] = pd.to_numeric(df.y_hard, errors="raise")
    if not df.y_hard.isin([-1, 0, 1]).all():
        raise ValueError("y_hard must be -1 (unscored), 0, or 1")
    if "label_weight" not in df:
        df["label_weight"] = 1.0
    df["label_weight"] = pd.to_numeric(df.label_weight, errors="raise")
    if not np.isfinite(df.label_weight).all() or (df.label_weight < 0).any():
        raise ValueError("label_weight must be finite and nonnegative")
    if "sample_id" in df and df.duplicated(_KEYS + ["sample_id"]).any():
        raise ValueError("Duplicate sample_id within a seam/segment")
    df["_scored"] = df.y_hard.isin([0, 1]) & (df.label_weight > 0)
    df["_boundary"] = (_boolean_series(df.boundary_uncertain)
                       if "boundary_uncertain" in df else False)
    return df


def _prepare_events(df):
    df = pd.DataFrame(df).copy()
    if df.empty:
        return pd.DataFrame(columns=_KEYS + ["event_id", "start_mm", "end_mm",
                                             "reference_t_s"]), 0
    required = _KEYS + ["event_id", "start_mm", "end_mm"]
    missing = [k for k in required if k not in df]
    if missing:
        raise ValueError("Event columns missing: " + ", ".join(missing))
    excluded = 0
    if "class_name" in df:
        target = df.class_name.astype(str).str.lower().eq("undercut")
        excluded = int((~target).sum())
        df = df.loc[target].copy()
    for k in _KEYS + ["event_id"]:
        if df[k].isna().any():
            raise ValueError(f"{k} cannot be missing in events")
        df[k] = df[k].astype(str)
    for k in ["start_mm", "end_mm"]:
        df[k] = pd.to_numeric(df[k], errors="raise")
        if not np.isfinite(df[k]).all():
            raise ValueError(f"Event {k} must be finite")
    if (df.end_mm <= df.start_mm).any():
        raise ValueError("Every ground-truth event must have positive length")
    if df.duplicated(_KEYS + ["event_id"]).any():
        raise ValueError("Ground-truth event IDs must be unique within a segment")
    if "reference_t_s" not in df:
        df["reference_t_s"] = np.nan
    else:
        df["reference_t_s"] = pd.to_numeric(df.reference_t_s, errors="raise")
    return df.reset_index(drop=True), excluded


def _frame_metrics(df, threshold, n_bins=10):
    n = len(df)
    empty = dict(n=0, positives=0, negatives=0, tp=0, fp=0, tn=0, fn=0,
                 accuracy=None, balanced_accuracy=None, macro_f1=None,
                 average_precision=None, auroc=None, brier=None, ece=None)
    if not n:
        return empty
    y = df.y_hard.to_numpy(dtype=int)
    p = df.p_defect.to_numpy(dtype=float)
    h = p >= threshold
    tp = int(np.sum(h & (y == 1)))
    fp = int(np.sum(h & (y == 0)))
    tn = int(np.sum(~h & (y == 0)))
    fn = int(np.sum(~h & (y == 1)))
    positives, negatives = int(y.sum()), int(n - y.sum())
    both = positives > 0 and negatives > 0
    # Absent-class macro metrics are deliberately undefined, not perfect scores.
    macro_f1 = (0.5 * (2 * tp / (2 * tp + fp + fn) +
                        2 * tn / (2 * tn + fp + fn))) if both else None
    ece = 0.0
    bins = np.minimum((p * n_bins).astype(int), n_bins - 1)
    for k in range(n_bins):
        ix = bins == k
        if ix.any():
            ece += float(ix.mean() * abs(p[ix].mean() - y[ix].mean()))
    return dict(n=n, positives=positives, negatives=negatives, tp=tp, fp=fp,
                tn=tn, fn=fn, accuracy=float((tp + tn) / n),
                balanced_accuracy=(0.5 * (tp / positives + tn / negatives)
                                   if both else None),
                macro_f1=_number(macro_f1),
                average_precision=(float(average_precision_score(y, p))
                                   if positives else None),
                auroc=(float(roc_auc_score(y, p)) if both else None),
                brier=float(np.mean((p - y) ** 2)), ece=float(ece))


def _predicted_intervals(group, support, threshold, merge_gap_mm, min_length_mm):
    positive = group.loc[group.p_defect >= threshold].sort_values(
        ["cell_start_mm", "cell_end_mm"])
    result = []
    for idx, row in positive.iterrows():
        a, b = float(row.cell_start_mm), float(row.cell_end_mm)
        can_merge = False
        if result and a <= result[-1]["end_mm"] + merge_gap_mm + _EPS:
            previous_end = result[-1]["end_mm"]
            gap = max(0.0, a - previous_end)
            covered_gap = _length(_intersect(support, previous_end, a))
            can_merge = covered_gap + _EPS >= gap
        if can_merge:
            result[-1]["end_mm"] = max(b, result[-1]["end_mm"])
            result[-1]["indices"].append(idx)
        else:
            result.append(dict(start_mm=a, end_mm=b, indices=[idx]))
    return [item for item in result
            if item["end_mm"] - item["start_mm"] + _EPS >= min_length_mm]


def _match_iou(iou, threshold):
    """Maximum eligible match cardinality, THEN maximum total IoU."""
    if not iou.size:
        return []
    eligible = (iou >= threshold) & (iou > 0)
    bonus = min(iou.shape) + 1.0
    score = np.where(eligible, bonus + iou, 0.0)
    rows, cols = linear_sum_assignment(-score)
    return [(int(r), int(c)) for r, c in zip(rows, cols) if eligible[r, c]]


def evaluate_predictions(predictions_df, events_df, threshold=0.5,
                         iou_threshold=0.1, merge_gap_mm=0.0,
                         min_length_mm=0.0):
    """Evaluate fixed-threshold predictions on actual labelled cell coverage.

    Events with partial coverage are clipped and explicitly marked; recall is
    for *observed events*, not all inspected events. Unobserved GT is reported
    separately and never counted as FN. Predicted intervals never cross gaps in
    evaluated coverage, nor seam or segment boundaries.
    """
    if not np.isfinite(threshold) or not 0 <= threshold <= 1:
        raise ValueError("threshold must be in [0, 1]")
    if not np.isfinite(iou_threshold) or not 0 <= iou_threshold <= 1:
        raise ValueError("iou_threshold must be in [0, 1]")
    if (not np.isfinite(merge_gap_mm) or not np.isfinite(min_length_mm)
            or merge_gap_mm < 0 or min_length_mm < 0):
        raise ValueError("Interval gap/length must be finite and nonnegative")
    df = _prepare_predictions(predictions_df)
    gt, excluded_events = _prepare_events(events_df)
    scored = df.loc[df._scored]
    groups = {key: grp for key, grp in scored.groupby(_KEYS, sort=True)}
    supports = {key: _union(zip(grp.cell_start_mm, grp.cell_end_mm))
                for key, grp in groups.items()}
    group_keys = sorted(set(groups) | set(map(tuple, gt[_KEYS].to_numpy())))
    matches, gt_details, pred_details, coverage_rows = [], [], [], []
    total_mm = 0.0
    full_count = partial_count = unobserved_count = matched_full = 0
    boundary_errors, delays = [], []
    for key in group_keys:
        support = supports.get(key, [])
        support_mm = _length(support)
        total_mm += support_mm
        coverage_rows.append(dict(seam_id=key[0], segment_id=key[1],
                                  evaluated_mm=support_mm,
                                  intervals_mm=[list(v) for v in support]))
        pred = (_predicted_intervals(groups[key], support, threshold,
                                    merge_gap_mm, min_length_mm)
                if key in groups else [])
        local_gt = gt.loc[(gt.seam_id == key[0]) & (gt.segment_id == key[1])]
        observed = []
        for _, event in local_gt.iterrows():
            start, end = float(event.start_mm), float(event.end_mm)
            visible = _intersect(support, start, end)
            visible_mm = _length(visible)
            fraction = min(1.0, visible_mm / (end - start))
            if visible_mm <= _EPS:
                status = "unobserved"
                unobserved_count += 1
            elif fraction >= 1.0 - _EPS:
                status = "fully_covered"
                full_count += 1
            else:
                status = "partially_covered"
                partial_count += 1
            detail = dict(seam_id=key[0], segment_id=key[1],
                          event_id=event.event_id, start_mm=start, end_mm=end,
                          coverage_status=status, coverage_fraction=fraction,
                          visible_intervals_mm=[list(v) for v in visible],
                          matched=False, prediction_id=None,
                          reference_t_s=_number(event.reference_t_s))
            gt_details.append(detail)
            if status != "unobserved":
                observed.append((event, visible, detail))
        iou = np.zeros((len(pred), len(observed)), dtype=float)
        for i, item in enumerate(pred):
            plen = item["end_mm"] - item["start_mm"]
            for j, (_, visible, _) in enumerate(observed):
                intersection = _length(_intersect(visible, item["start_mm"],
                                                  item["end_mm"]))
                union = plen + _length(visible) - intersection
                iou[i, j] = intersection / union if union > 0 else 0.0
        pairs = _match_iou(iou, iou_threshold)
        paired = {i: j for i, j in pairs}
        for i, item in enumerate(pred):
            prediction_id = f"{key[0]}/{key[1]}/pred_{i:05d}"
            first_hit = None
            if "t_decision_s" in df:
                times = pd.to_numeric(df.loc[item["indices"], "t_decision_s"],
                                      errors="coerce").to_numpy(dtype=float)
                times = times[np.isfinite(times)]
                if len(times):
                    first_hit = float(times.min())
            detail = dict(seam_id=key[0], segment_id=key[1],
                          prediction_id=prediction_id,
                          start_mm=item["start_mm"], end_mm=item["end_mm"],
                          first_threshold_hit_t_s=first_hit,
                          matched=i in paired, event_id=None)
            pred_details.append(detail)
            if i not in paired:
                continue
            j = paired[i]
            event, _, event_detail = observed[j]
            event_detail["matched"] = True
            event_detail["prediction_id"] = prediction_id
            detail["event_id"] = event.event_id
            reference = _number(event.reference_t_s)
            delay = first_hit - reference if first_hit is not None and reference is not None else None
            boundary_mae = None
            if event_detail["coverage_status"] == "fully_covered":
                matched_full += 1
                boundary_mae = 0.5 * (abs(item["start_mm"] - event.start_mm) +
                                      abs(item["end_mm"] - event.end_mm))
                boundary_errors.append(float(boundary_mae))
            if delay is not None:
                delays.append(delay)
            matches.append(dict(seam_id=key[0], segment_id=key[1],
                                prediction_id=prediction_id, event_id=event.event_id,
                                iou=float(iou[i, j]),
                                coverage_status=event_detail["coverage_status"],
                                boundary_mae_mm=_number(boundary_mae),
                                first_threshold_hit_delay_s=_number(delay)))
    tp = len(matches)
    n_pred = len(pred_details)
    n_gt = full_count + partial_count
    fp, fn = n_pred - tp, n_gt - tp
    precision, recall = _ratio(tp, n_pred), _ratio(tp, n_gt)
    f1 = _ratio(2 * tp, 2 * tp + fp + fn)
    event_metrics = dict(
        tp=tp, fp=fp, fn=fn, predicted_events=n_pred, observed_gt_events=n_gt,
        fully_covered_gt_events=full_count, partially_covered_gt_events=partial_count,
        unobserved_gt_events=unobserved_count, precision=precision, recall=recall,
        f1=f1, false_positive_events_per_evaluated_m=_ratio(fp, total_mm / 1000.0),
        full_coverage_recall=_ratio(matched_full, full_count),
        matched_full_coverage_events=matched_full,
        matched_boundary_mae_mm=_number(np.mean(boundary_errors)) if boundary_errors else None,
        boundary_metric_n=len(boundary_errors),
        first_threshold_hit_delay_s_mean=_number(np.mean(delays)) if delays else None,
        first_threshold_hit_delay_s_median=_number(np.median(delays)) if delays else None,
        delay_metric_n=len(delays))
    return dict(
        threshold=float(threshold), iou_threshold=float(iou_threshold),
        merge_gap_mm=float(merge_gap_mm), min_length_mm=float(min_length_mm),
        frame=_frame_metrics(scored, threshold),
        clear_core=_frame_metrics(scored.loc[~scored._boundary], threshold),
        events=event_metrics,
        coverage=dict(total_evaluated_m=total_mm / 1000.0,
                      input_frames=len(df), scored_frames=len(scored),
                      excluded_frames=len(df) - len(scored),
                      boundary_uncertain_scored_frames=int(scored._boundary.sum()),
                      excluded_non_target_gt_events=excluded_events,
                      segments=coverage_rows),
        event_details=dict(ground_truth=gt_details, predictions=pred_details, matches=matches),
        definitions=dict(
            event_recall="Observed GT events only; partial GT clipped to evaluated support; unobserved GT excluded and listed.",
            event_matching="One-to-one matching maximizes count of IoU-eligible pairs, then total IoU.",
            coverage="Union of scored cells (y_hard in {0,1}, label_weight>0), never nominal seam length.",
            frame_weighting="Unweighted hard-label frame metrics; label_weight controls inclusion only.",
            boundary_mae="Matched fully covered GT only; mean absolute start/end error.",
            ece="10 fixed equal-width probability bins; absolute mean probability minus positive frequency.",
            delay="First threshold-positive observation in a matched predicted interval minus arc-pass GT-start reference time. Geometry offset and sensor availability are reflected in supplied positions/t_decision_s; runtime, hysteresis and actuator delay are not measured. This is not full online latency.",
            undefined="Undefined metrics are JSON null, including absent-class AUROC/balanced accuracy/macro-F1."))


def select_threshold(val_predictions, events, threshold_candidates=None,
                     iou_threshold=0.1, merge_gap_mm=0.0, min_length_mm=0.0):
    """Select on validation only; return threshold and auditable objective.

    If a split column is present it must contain only 'val'/'validation'. Without
    that column the caller is responsible for supplying only validation seams.
    No observed GT: use validation macro-F1; undefined fallback: fixed 0.5.
    """
    df = pd.DataFrame(val_predictions)
    if "split" in df and not df["split"].astype(str).isin(["val", "validation"]).all():
        raise ValueError("Threshold selection requires validation-only predictions")
    opts = dict(iou_threshold=iou_threshold, merge_gap_mm=merge_gap_mm,
                min_length_mm=min_length_mm)
    initial = evaluate_predictions(df, events, threshold=0.5, **opts)
    if initial["events"]["observed_gt_events"] > 0:
        section, field, reason = "events", "f1", "Validation observed-event F1"
    elif initial["frame"]["macro_f1"] is not None:
        section, field, reason = "frame", "macro_f1", "No observed validation GT events; validation frame macro-F1 fallback"
    else:
        return dict(threshold=0.5, objective=None, objective_value=None,
                    reason="No usable validation event objective or two-class frame objective; fixed 0.5 (no test fallback)",
                    selection_split="validation", candidates_evaluated=0,
                    split_column_verified="split" in df)
    if threshold_candidates is None:
        scored_p = df.loc[df.y_hard.isin([0, 1]), "p_defect"].to_numpy(dtype=float)
        candidates = np.unique(np.r_[0.0, 0.5, 1.0,
                                     np.quantile(scored_p, np.linspace(0, 1, 99))])
    else:
        candidates = np.unique(np.asarray(threshold_candidates, dtype=float))
        if not len(candidates):
            raise ValueError("threshold_candidates cannot be empty")
    best = None
    for threshold in candidates:
        value = evaluate_predictions(df, events, threshold=float(threshold), **opts)[section][field]
        if value is None:
            continue
        # Conservative deterministic tie-break: nearest .5, then larger threshold.
        key = (value, -abs(float(threshold) - 0.5), float(threshold))
        if best is None or key > best[0]:
            best = (key, float(threshold), float(value))
    return dict(threshold=best[1] if best else 0.5,
                objective=f"{section}.{field}",
                objective_value=best[2] if best else None, reason=reason,
                selection_split="validation", candidates_evaluated=len(candidates),
                split_column_verified="split" in df)


def cluster_bootstrap(pred_df, events_df, threshold=0.5, iou_threshold=0.1,
                      merge_gap_mm=0.0, min_length_mm=0.0, n_bootstrap=1000,
                      confidence=0.95, seed=0):
    """Fixed-threshold seam-cluster percentile bootstrap; no frame resampling.

    GT-only seams remain in the main evaluation coverage report, but cannot
    enlarge the number of evaluable bootstrap clusters. Resampled copies receive
    distinct IDs, so duplicate draws cannot collapse spatial intervals/events.
    Undefined replicates are counted explicitly, never converted to zero.
    """
    if n_bootstrap < 1 or not isinstance(n_bootstrap, (int, np.integer)):
        raise ValueError("n_bootstrap must be a positive integer")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")
    pred = _prepare_predictions(pred_df)
    gt, _ = _prepare_events(events_df)
    seams = sorted(set(pred.loc[pred._scored, "seam_id"]))
    unevaluated_seams = sorted((set(pred.seam_id) | set(gt.seam_id)) - set(seams))
    paths = [("frame", "macro_f1"), ("frame", "average_precision"),
             ("frame", "auroc"), ("frame", "brier"), ("events", "f1"),
             ("events", "recall"), ("events", "false_positive_events_per_evaluated_m")]
    values = {".".join(path): [] for path in paths}
    if len(seams) >= 2:
        rng = np.random.default_rng(seed)
        for _ in range(n_bootstrap):
            ps, gs = [], []
            for k, seam in enumerate(rng.choice(seams, size=len(seams), replace=True)):
                p = pred.loc[pred.seam_id == seam].copy()
                g = gt.loc[gt.seam_id == seam].copy()
                p["seam_id"] = f"draw_{k}"
                g["seam_id"] = f"draw_{k}"
                ps.append(p)
                gs.append(g)
            result = evaluate_predictions(pd.concat(ps, ignore_index=True),
                                          pd.concat(gs, ignore_index=True),
                                          threshold, iou_threshold, merge_gap_mm,
                                          min_length_mm)
            for section, field in paths:
                value = result[section][field]
                if value is not None:
                    values[f"{section}.{field}"].append(value)
    alpha = (1 - confidence) / 2
    intervals = {}
    for key, vals in values.items():
        lo, hi = (np.quantile(vals, [alpha, 1 - alpha]) if vals else [None, None])
        intervals[key] = dict(lower=_number(lo), upper=_number(hi),
                              valid_replicates=len(vals),
                              undefined_replicates=(n_bootstrap - len(vals)
                                                    if len(seams) >= 2 else 0))
    return dict(method="seam-cluster percentile bootstrap", confidence=float(confidence),
                seed=int(seed), n_seams=len(seams),
                unevaluated_seams_excluded=unevaluated_seams,
                requested_replicates=int(n_bootstrap),
                completed_replicates=int(n_bootstrap) if len(seams) >= 2 else 0,
                threshold_refitted=False, intervals=intervals,
                warning=("Fewer than two independent seams: interval not estimable."
                         if len(seams) < 2 else
                         "Few seams can produce unstable intervals; frame count is not the independent sample size."))
