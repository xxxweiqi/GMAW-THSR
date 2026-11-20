import json
import unittest
import pandas as pd

from gmaw_phys.comparison import compare_predictions, validate_paired_inputs


def make_case():
    records = []
    events = []
    for seam in ["S1", "S2"]:
        for i, label in enumerate([0, 1]):
            records.append(dict(seam_id=seam, segment_id="one", sample_id=f"f{i}",
                                cell_start_mm=float(i), cell_end_mm=float(i + 1),
                                y_hard=label, label_weight=1., p_defect=.1 if i == 0 else .9,
                                boundary_uncertain=False, synthetic=True))
        events.append(dict(seam_id=seam, segment_id="one", event_id="e1",
                           start_mm=1., end_mm=2., reference_t_s=1.,
                           class_name="Undercut", confidence=1.))
    return pd.DataFrame(records), pd.DataFrame(events)


class PairedComparisonTests(unittest.TestCase):
    def test_identical_runs_have_zero_paired_ci(self):
        p, g = make_case()
        r = compare_predictions(p, g, p, g, .5, .5, n_bootstrap=20, seed=9)
        for metric in r["metric_comparisons"].values():
            self.assertEqual(metric["difference_b_minus_a"], 0.)
            self.assertEqual(metric["paired_bootstrap_ci"]["lower"], 0.)
            self.assertEqual(metric["paired_bootstrap_ci"]["upper"], 0.)
        self.assertEqual(r["evidence_status"], "SYNTHETIC_PIPELINE_ONLY")
        self.assertFalse(r["bootstrap"]["thresholds_refitted"])
        json.dumps(r, allow_nan=False)

    def test_order_does_not_change_pairing(self):
        p, g = make_case()
        r = compare_predictions(p, g, p.iloc[::-1], g.iloc[::-1], .5, .5, n_bootstrap=0)
        self.assertTrue(r["paired_inputs_verified"])
        self.assertEqual(r["identical_sample_count"], 4)

    def test_unequal_samples_rejected_no_intersection(self):
        p, g = make_case()
        with self.assertRaisesRegex(ValueError, "Sample identity mismatch"):
            compare_predictions(p, g, p.iloc[:-1], g, .5, .5, n_bootstrap=0)

    def test_changed_sample_id_rejected(self):
        p, g = make_case()
        b = p.copy()
        b.loc[0, "sample_id"] = "other"
        with self.assertRaisesRegex(ValueError, "Sample identity"):
            validate_paired_inputs(p, g, b, g)

    def test_equal_total_coverage_but_different_cells_rejected(self):
        p, g = make_case()
        b = p.copy()
        b.loc[0, "cell_end_mm"] = .9
        b.loc[1, "cell_start_mm"] = .9
        with self.assertRaisesRegex(ValueError, "coverage/labels"):
            validate_paired_inputs(p, g, b, g)

    def test_ground_truth_boundary_or_confidence_change_rejected(self):
        p, g = make_case()
        for field in ["end_mm", "confidence"]:
            other = g.copy()
            other.loc[0, field] += .1
            with self.assertRaisesRegex(ValueError, "Ground truth"):
                validate_paired_inputs(p, g, p, other)

    def test_label_and_boundary_uncertainty_change_rejected(self):
        p, g = make_case()
        for field, value in [("y_hard", 1), ("boundary_uncertain", True),
                             ("label_weight", .5)]:
            other = p.copy()
            other.loc[0, field] = value
            with self.assertRaisesRegex(ValueError, "coverage/labels"):
                validate_paired_inputs(p, g, other, g)

    def test_each_run_uses_own_fixed_threshold(self):
        p, g = make_case()
        b = p.copy()
        b["p_defect"] = [.05, .2, .05, .2]
        r = compare_predictions(p, g, b, g, .5, .15, n_bootstrap=0)
        self.assertEqual(r["metric_comparisons"]["events.f1"]["difference_b_minus_a"], 0.)
        self.assertEqual(r["threshold_b"], .15)

    def test_direction_and_paired_cluster_replicates(self):
        good, g = make_case()
        bad = good.copy()
        bad["p_defect"] = [.8, .1, .8, .1]
        r = compare_predictions(bad, g, good, g, .5, .5, n_bootstrap=15, seed=3)
        f = r["metric_comparisons"]["events.f1"]
        fp = r["metric_comparisons"]["events.false_positive_events_per_evaluated_m"]
        self.assertEqual(f["difference_b_minus_a"], 1.)
        self.assertEqual(f["paired_bootstrap_ci"]["lower"], 1.)
        self.assertEqual(f["paired_bootstrap_ci"]["upper"], 1.)
        self.assertEqual(f["paired_bootstrap_ci"]["valid_replicates"], 15)
        self.assertEqual(fp["difference_b_minus_a"], -500.)
        self.assertEqual(fp["favorable_direction"], "lower")
        self.assertEqual(r["total_evaluated_m"], .004)

    def test_seed_reproducibility_and_nonzero_cluster_variation(self):
        good, g = make_case()
        bad = good.copy()
        bad.loc[bad.seam_id == "S1", "p_defect"] = [.8, .1]
        kwargs = dict(n_bootstrap=25, seed=4)
        r1 = compare_predictions(bad, g, good, g, .5, .5, **kwargs)
        r2 = compare_predictions(bad, g, good, g, .5, .5, **kwargs)
        self.assertEqual(r1, r2)
        interval = r1["metric_comparisons"]["events.f1"]["paired_bootstrap_ci"]
        self.assertEqual(interval["lower"], 0.)
        self.assertEqual(interval["upper"], 1.)

    def test_gt_only_seam_cannot_create_second_cluster(self):
        p, g = make_case()
        p = p[p.seam_id == "S1"]
        r = compare_predictions(p, g, p, g, .5, .5, n_bootstrap=20)
        self.assertEqual(r["n_evaluable_seams"], 1)
        self.assertEqual(r["unevaluated_seams_excluded"], ["S2"])
        self.assertEqual(r["bootstrap"]["completed_replicates"], 0)
        self.assertIsNone(r["metric_comparisons"]["events.f1"]["paired_bootstrap_ci"]["lower"])

    def test_no_positive_events_yields_null_not_nan_difference(self):
        p, g = make_case()
        p["p_defect"] = .1
        p["y_hard"] = 0
        g = g.iloc[:0]
        r = compare_predictions(p, g, p, g, .5, .5, n_bootstrap=5)
        m = r["metric_comparisons"]["events.f1"]
        self.assertIsNone(m["difference_b_minus_a"])
        self.assertEqual(m["paired_bootstrap_ci"]["undefined_replicates"], 5)
        json.dumps(r, allow_nan=False)


if __name__ == "__main__":
    unittest.main()
