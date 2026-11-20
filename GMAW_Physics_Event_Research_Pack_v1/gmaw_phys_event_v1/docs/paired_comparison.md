# Paired comparison of frozen runs

`scripts/compare_runs.py` compares two existing test-prediction exports. It does
not train, tune, search thresholds or reproduce original MBGN. Each run must
contain `predictions_test.csv`, `events_test.csv`, `threshold_selection.json`
and `resolved_config.yaml`. The saved threshold must record
`selection_split: validation`; the two runs may have different frozen thresholds.
Event IoU and interval postprocessing must be identical.

```bash
python scripts/compare_runs.py \
  --run-a runs/snapshot_fusion_seed7 \
  --run-b runs/phys_align_seed7 \
  --label-a snapshot_reference --label-b physical_alignment_reference \
  --bootstrap 1000 --seed 42 \
  --output runs/paired_snapshot_vs_physical.json
```

## Strict pairing

The default is refusal when observations differ. Identity is the tuple
`(seam_id, segment_id, sample_id)`. Both runs must have exactly the same identities,
cell boundaries, hard/soft labels, label weights, boundary-uncertainty flags,
timestamps and other exported observation metadata. Row order may differ and
numeric dtypes may differ; actual values must be equal. Only `p_defect` and
`geom_*_pred` are allowed to differ. The complete ground-truth tables must agree,
including non-target exclusions, confidence and boundary metadata when present.

The script never silently intersects sample lists or matches only the overlapping
coverage. A shorter-history model may have more eligible early frames than a
longer-history model; construct a common evaluation cohort upstream using a
predeclared, label-independent eligibility rule and export both runs on that
cohort. Do not silently discard difficult samples after seeing performance.

When an exported validation CSV is available, validation/test seam overlap is
rejected. File SHA-256 hashes and each threshold selection record are saved in the
comparison. This verifies the recorded inputs, not the entire external training
history. The direct Python API accepts frozen numeric thresholds and requires the
caller to verify their validation provenance.

## Difference estimates

Results report **B minus A** for event F1, event recall, false-positive events per
evaluated metre, and frame average precision. Positive differences favor B for
F1/recall/AP; negative differences favor B for FP/metre. The full run summaries
retain coverage and partially/unobserved-event counts. Event recall concerns
observed GT; see `evaluation_protocol.md` for the partial-coverage rules.

Bootstrap resamples complete evaluable seams, using the same ordered draw for
both runs. Each repeated occurrence receives the same new identity in A, B and
GT, so a repeated seam neither disappears through interval union nor pairs with
a different seam. Thresholds and postprocessing remain fixed for every draw.
Only seams with at least one scored cell count as independent clusters; GT-only
unobserved seams remain listed but cannot increase the sample size.

With at least two evaluable seams, the script computes percentile intervals of
the **paired metric differences**, not a difference of separately calculated CI
endpoints. Each metric records valid and undefined replicate counts. If either
run's metric is undefined, that replicate is excluded for that difference and
counted explicitly. Fewer than two seams yields null interval bounds. Set
`--bootstrap 0` for point estimates only. All undefined values are strict JSON
`null`, not NaN.

Two or a few seams do not establish population-level reliability: their bootstrap
intervals can be unstable or degenerate. Adjacent frame counts do not replace
independent seam repetitions. This interval captures held-out seam-sampling
variation conditional on the fitted runs; it does not quantify training-seed
variation, establish causality, or serve as a hypothesis test. For the synthetic
demo, `SYNTHETIC_PIPELINE_ONLY` means only that the paired evaluation pipeline
runs. The resulting difference is not evidence of welding performance.
