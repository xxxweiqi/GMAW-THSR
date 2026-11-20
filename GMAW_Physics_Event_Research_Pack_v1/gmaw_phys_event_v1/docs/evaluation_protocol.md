# Unified evaluation protocol

This module evaluates the package reference models and externally supplied
predictions from an original MBGN implementation. It does **not** implement,
retrain or claim to reproduce the published MBGN. Keep the original architecture,
input timing (including any future samples), training split and weights in the
external run's provenance record. A causal reference baseline must not be called
an original-MBGN reproduction.

## Input and coverage

Prediction CSVs contain the exported dataset records and `p_defect` in [0,1].
The mandatory evaluator fields are `seam_id,segment_id,cell_start_mm,cell_end_mm,
y_hard,p_defect`. `label_weight` defaults to 1 when absent. Use the data builder's
cells; do not fabricate large cells spanning absent frames, uninspected spans or
other-defect exclusion regions. Only `y_hard` 0/1 with positive `label_weight`
contributes to frame scores or evaluated spatial support. Hard-label metrics are
unweighted. `boundary_uncertain` selects the separate clear-core analysis.

GT CSV fields are `seam_id,segment_id,event_id,start_mm,end_mm`; include
`reference_t_s` for delay analysis. `class_name`, when supplied, must be Undercut
for target events. Other class names are excluded and counted. The reference data
builder excludes other-defect cells upstream; the evaluator cannot infer missing
exclusion coordinates from frame labels alone.

Coverage is the **union of evaluated cell intervals per segment**, summed across
segments, in metres. It is not nominal weld length, distance from first to last
sample, or a sum of overlapping cell lengths. Thus FP per evaluated metre cannot
be improved by adding unseen weld length to the denominator. Report this length
alongside all event scores and report the builder's inspected-but-unavailable
coverage separately. The evaluator knows only the supplied cells and event table.

## Frame analysis

Report accuracy, balanced accuracy, macro-F1, AP, AUROC, Brier score and ECE.
ECE uses 10 fixed equal-width bins and compares mean positive-class probability
with positive-class frequency. AP requires at least one positive. AUROC, balanced
accuracy and macro-F1 require both classes. Undefined values become JSON `null`,
never NaN or a fabricated perfect score. Also report the same metrics after
excluding uncertain boundary cells. This clear-core subset must not replace the
full scoring subset without showing both sample counts.

## Event conversion and matching

1. Threshold `p_defect >= threshold` on scored cells only.
2. Union contiguous/overlapping positive cells inside each seam and segment.
3. Optionally join positive intervals separated by at most `merge_gap_mm`, but
   only if the **entire gap has evaluated coverage**. Segments and coverage holes
   are never bridged, even with a large merge-gap setting.
4. Apply `min_length_mm` to the resulting intervals.
5. Intersect each GT event with evaluated support. A completely unseen GT event
   is listed as unobserved and is not a false negative. Partially covered events
   retain their identity, coverage fraction and possibly disjoint visible pieces.
6. Compute IoU against the **union of each GT's visible pieces**. Match predicted
   events to GT one-to-one, maximizing the count of pairs with positive overlap
   and IoU at least `iou_threshold`, then maximizing total IoU. Greedy matching
   does not satisfy this rule.

Primary event precision/recall/F1 concerns **observed events**. Always report
fully covered, partially covered and unobserved counts. Partial-event recall is
not full-event recall. Also report recall restricted to fully covered GT. A
partially observed GT spanning a coverage hole remains one lesion: separate
predicted intervals cannot both count as independent true positives for it.
The detailed event tables expose any resulting extra detections.

Boundary MAE uses matched **fully covered** GT only. It averages absolute start
and end error. Artificial boundaries created by coverage clipping are not treated
as true defect boundaries. Event F1 is undefined if neither observed GT nor
predicted events exist. If GT exists but no prediction, recall and F1 are zero;
precision remains undefined. The corresponding denominators are always exported.

## Threshold and postprocessing selection

Select threshold, IoU criterion, gap and minimum-length policy using training/
validation decisions, then freeze them before the final test. Do not tune on test
RT coordinates or test predictions. `select_threshold(val_predictions, events,
threshold_candidates=None, iou_threshold=0.1, merge_gap_mm=0., min_length_mm=0.)`
returns a dict with `threshold`, objective and selection reason. If `split` is
present it must be validation-only. Without it, the caller must verify provenance.
Default candidates are fixed quantiles of validation scores plus 0, .5 and 1.
Ties prefer the value nearest .5, then the larger value. The objective is observed
event F1. Without observed validation GT it falls back to validation macro-F1,
and if that is undefined it fixes .5 with a recorded reason. No test fallback exists.

Example using a threshold selected on separate validation seams:

```bash
python scripts/evaluate_predictions.py \
  --predictions external/test_predictions.csv \
  --events external/test_events.csv \
  --validation-predictions external/val_predictions.csv \
  --validation-events external/val_events.csv \
  --save-threshold-json runs/external_threshold.json \
  --method-name original_MBGN_external \
  --output runs/external_test_metrics.json --bootstrap 1000
```

The CLI rejects overlapping validation/scored seam IDs. Reuse the saved threshold
via `--threshold-json` for an already frozen evaluation, or specify a precommitted
`--threshold`. The script cannot verify an external training log, input timing,
or upstream separation of test seams; document those in the experiment record.

## Cluster uncertainty and timing

Optional bootstrap resamples whole seam clusters with replacement, retaining all
segments, cells and GT for each draw. Duplicate draws get unique cluster IDs so
their intervals are not collapsed. The threshold stays fixed. This estimates
between-seam test-sampling variability, not training-seed uncertainty. Report
number of seams, valid/undefined replicate counts and the percentile method.
Seams with no scored cells are listed separately and cannot inflate the number
of independent evaluable clusters.
With fewer than two seams no interval is reported. With a small seam count,
intervals can still be unstable; many adjacent frames do not cure that limitation.

`first_threshold_hit_delay_s` is the earliest decision timestamp of a positive
cell in a matched predicted interval minus the time the arc passes the GT event
start. Supplied geometry offsets and sensor availability affect that comparison.
Runtime, hysteresis, actuator response and a deployed streaming alarm are not
measured. Negative values are possible and are not clipped. This is a first-hit
timing statistic, **not full online system latency**. Missing reference/decision
timestamps yield null timing values and an explicit valid-event count.
