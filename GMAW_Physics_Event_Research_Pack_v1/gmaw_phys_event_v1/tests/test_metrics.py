"""Tests target scientific evaluation failure modes, not model architecture."""
import json
import unittest

import numpy as np
import pandas as pd

from gmaw_phys.metrics import (evaluate_predictions, select_threshold,
                               cluster_bootstrap, _match_iou)


def predictions(cells, probs, labels=None, seam="A", segment="one", **extra):
    n = len(cells)
    d = dict(sample_id=[f"f{k}" for k in range(n)], seam_id=[seam] * n,
             segment_id=[segment] * n, cell_start_mm=[v[0] for v in cells],
             cell_end_mm=[v[1] for v in cells],
             p_defect=probs, y_hard=labels if labels is not None else [1] * n,
             label_weight=[1.0] * n, boundary_uncertain=[False] * n,
             t_decision_s=np.arange(n, dtype=float))
    d.update(extra)
    return pd.DataFrame(d)


def events(intervals, seam="A", segment="one"):
    return pd.DataFrame([dict(seam_id=seam, segment_id=segment, event_id=f"e{i}",
                              start_mm=a, end_mm=b, reference_t_s=0.0,
                              class_name="Undercut", confidence=1.0)
                         for i, (a, b) in enumerate(intervals)],
                        columns=["seam_id", "segment_id", "event_id", "start_mm",
                                 "end_mm", "reference_t_s", "class_name", "confidence"])


class FrameMetricsTests(unittest.TestCase):
    def test_frame_metrics_and_clear_core(self):
        p = predictions([(0, 1), (1, 2), (2, 3), (3, 4)],
                        [.1, .9, .8, .2], [0, 1, 0, 1],
                        boundary_uncertain=[False, False, True, True])
        r = evaluate_predictions(p, events([(1, 2), (3, 4)]))
        self.assertAlmostEqual(r["frame"]["macro_f1"], .5)
        self.assertAlmostEqual(r["frame"]["auroc"], .75)
        self.assertAlmostEqual(r["frame"]["brier"], .325)
        self.assertEqual(r["clear_core"]["n"], 2)
        self.assertEqual(r["clear_core"]["macro_f1"], 1.0)
        self.assertAlmostEqual(r["frame"]["average_precision"], 5 / 6)

    def test_undefined_metrics_are_json_null(self):
        p = predictions([(0, 1)], [.1], [0])
        r = evaluate_predictions(p, events([]))
        self.assertIsNone(r["frame"]["auroc"])
        self.assertIsNone(r["frame"]["average_precision"])
        self.assertIsNone(r["frame"]["macro_f1"])
        self.assertIsNone(r["events"]["f1"])
        serialized = json.dumps(r, allow_nan=False)
        self.assertIn("null", serialized)

    def test_invalid_probability_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_predictions(predictions([(0, 1)], [1.1]), events([]))

    def test_unknown_and_zero_weight_excluded_from_coverage(self):
        p = predictions([(0, 10), (10, 20), (20, 30)], [.9, .9, .9],
                        [1, -1, 1], label_weight=[1., 1., 0.])
        r = evaluate_predictions(p, events([(0, 30)]))
        self.assertEqual(r["frame"]["n"], 1)
        self.assertAlmostEqual(r["coverage"]["total_evaluated_m"], .01)
        self.assertEqual(r["coverage"]["excluded_frames"], 2)


class EventMetricsTests(unittest.TestCase):
    def test_matching_maximizes_cardinality_before_iou(self):
        # Greedy maximum IoU gets one match; correct assignment gets two.
        m = np.array([[.9, .2], [.3, 0.]])
        self.assertEqual(set(_match_iou(m, .1)), {(0, 1), (1, 0)})

    def test_one_prediction_cannot_match_two_events(self):
        p = predictions([(0, 10)], [.9])
        r = evaluate_predictions(p, events([(0, 4), (6, 10)]), iou_threshold=.1)
        self.assertEqual(r["events"]["tp"], 1)
        self.assertEqual(r["events"]["fn"], 1)
        self.assertEqual(r["events"]["recall"], .5)

    def test_never_merge_across_coverage_gap(self):
        p = predictions([(0, 1), (3, 4)], [.9, .9])
        r = evaluate_predictions(p, events([]), merge_gap_mm=20)
        self.assertEqual(r["events"]["predicted_events"], 2)
        self.assertAlmostEqual(r["coverage"]["total_evaluated_m"], .002)
        self.assertAlmostEqual(r["events"]["false_positive_events_per_evaluated_m"], 1000)

    def test_merge_short_negative_gap_only_inside_support(self):
        p = predictions([(0, 1), (1, 2), (2, 3)], [.9, .1, .9], [1, 0, 1])
        r = evaluate_predictions(p, events([(0, 3)]), merge_gap_mm=1.)
        self.assertEqual(r["events"]["predicted_events"], 1)
        self.assertEqual(r["events"]["tp"], 1)

    def test_no_merge_across_segment_or_seam(self):
        p = pd.concat([predictions([(0, 1)], [.9]),
                       predictions([(1, 2)], [.9], segment="two"),
                       predictions([(1, 2)], [.9], seam="B")], ignore_index=True)
        r = evaluate_predictions(p, events([]), merge_gap_mm=100.)
        self.assertEqual(r["events"]["predicted_events"], 3)
        self.assertAlmostEqual(r["coverage"]["total_evaluated_m"], .003)

    def test_partial_and_unobserved_events_are_explicit(self):
        p = predictions([(0, 2)], [.9])
        g = events([(0, 4), (10, 11)])
        r = evaluate_predictions(p, g)
        self.assertEqual(r["events"]["partially_covered_gt_events"], 1)
        self.assertEqual(r["events"]["unobserved_gt_events"], 1)
        self.assertEqual(r["events"]["fn"], 0)
        self.assertEqual(r["events"]["recall"], 1.)
        self.assertIsNone(r["events"]["full_coverage_recall"])
        self.assertEqual(r["event_details"]["ground_truth"][0]["coverage_fraction"], .5)
        self.assertIsNone(r["events"]["matched_boundary_mae_mm"])

    def test_iou_uses_union_of_visible_fragments(self):
        p = predictions([(0, 1), (2, 3)], [.9, .9])
        r = evaluate_predictions(p, events([(0, 3)]), iou_threshold=.4)
        self.assertEqual(r["events"]["tp"], 1)
        self.assertEqual(r["events"]["fp"], 1)
        self.assertEqual(r["event_details"]["matches"][0]["iou"], .5)
        self.assertEqual(r["event_details"]["ground_truth"][0]["visible_intervals_mm"],
                         [[0., 1.], [2., 3.]])

    def test_denominator_uses_interval_union_not_sum_or_nominal_length(self):
        p = predictions([(0, 2), (1, 3)], [.9, .9], [0, 0])
        r = evaluate_predictions(p, events([]))
        self.assertAlmostEqual(r["coverage"]["total_evaluated_m"], .003)
        self.assertAlmostEqual(r["events"]["false_positive_events_per_evaluated_m"], 1000 / 3)

    def test_minimum_length_is_applied_after_merge(self):
        p = predictions([(0, .5), (.5, 1)], [.9, .9])
        r = evaluate_predictions(p, events([(0, 1)]), min_length_mm=.75)
        self.assertEqual(r["events"]["tp"], 1)

    def test_delay_is_first_threshold_hit_minus_reference(self):
        p = predictions([(0, 1), (1, 2)], [.9, .9], t_decision_s=[5., 6.])
        g = events([(0, 2)])
        g["reference_t_s"] = 4.7
        r = evaluate_predictions(p, g)
        self.assertAlmostEqual(r["events"]["first_threshold_hit_delay_s_mean"], .3)
        self.assertIn("not full online latency", r["definitions"]["delay"])
        self.assertEqual(r["events"]["matched_boundary_mae_mm"], 0.)


class SelectionAndBootstrapTests(unittest.TestCase):
    def test_selection_rejects_test_split(self):
        p = predictions([(0, 1), (1, 2)], [.1, .9], [0, 1], split=["test", "test"])
        with self.assertRaises(ValueError):
            select_threshold(p, events([(1, 2)]))

    def test_selection_returns_fixed_threshold_without_test_fallback(self):
        p = predictions([(0, 1)], [.2], [0])
        r = select_threshold(p, events([]))
        self.assertEqual(r["threshold"], .5)
        self.assertIn("no test fallback", r["reason"])
        self.assertFalse(r["split_column_verified"])
        verified = select_threshold(p.assign(split="val"), events([]))
        self.assertTrue(verified["split_column_verified"])

    def test_selection_prefers_validation_event_f1(self):
        p = predictions([(0, 1), (1, 2)], [.4, .8], [0, 1], split=["val", "val"])
        r = select_threshold(p, events([(1, 2)]), threshold_candidates=[.3, .5, .9],
                             iou_threshold=.6)
        self.assertEqual(r["threshold"], .5)
        self.assertEqual(r["objective"], "events.f1")

    def test_bootstrap_is_reproducible_and_preserves_duplicate_seam_draws(self):
        a = predictions([(0, 1), (1, 2)], [.1, .9], [0, 1])
        b = predictions([(0, 1), (1, 2)], [.1, .2], [0, 1], seam="B")
        p = pd.concat([a, b], ignore_index=True)
        g = pd.concat([events([(1, 2)]), events([(1, 2)], seam="B")], ignore_index=True)
        r = cluster_bootstrap(p, g, n_bootstrap=30, seed=11)
        r2 = cluster_bootstrap(p, g, n_bootstrap=30, seed=11)
        self.assertEqual(r, r2)
        self.assertEqual(r["completed_replicates"], 30)
        self.assertEqual(r["intervals"]["events.f1"]["valid_replicates"], 30)
        self.assertEqual(r["intervals"]["events.f1"]["lower"], 0.)
        self.assertEqual(r["intervals"]["events.f1"]["upper"], 1.)
        self.assertFalse(r["threshold_refitted"])
        json.dumps(r, allow_nan=False)

    def test_single_seam_bootstrap_does_not_fake_interval(self):
        r = cluster_bootstrap(predictions([(0, 1)], [.9]), events([(0, 1)]),
                              n_bootstrap=10)
        self.assertEqual(r["completed_replicates"], 0)
        self.assertIsNone(r["intervals"]["events.f1"]["lower"])

    def test_unobserved_gt_seam_cannot_inflate_bootstrap_sample_size(self):
        g = pd.concat([events([(0, 1)]), events([(0, 1)], seam="unobserved")],
                      ignore_index=True)
        r = cluster_bootstrap(predictions([(0, 1)], [.9]), g, n_bootstrap=10)
        self.assertEqual(r["n_seams"], 1)
        self.assertEqual(r["completed_replicates"], 0)
        self.assertEqual(r["unevaluated_seams_excluded"], ["unobserved"])


if __name__ == "__main__":
    unittest.main()
