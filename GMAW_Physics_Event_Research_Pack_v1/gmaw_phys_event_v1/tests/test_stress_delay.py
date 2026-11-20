import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from gmaw_phys.data import build_dataset
from gmaw_phys.demo import generate_demo
from gmaw_phys.physics import alignment_prior
from scripts.stress_causal_delay import (assert_causal_contract, normalize_delays,
    read_frozen_threshold, common_support, delay_plan, DelayedElectricalView)


class CausalDelayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name) / "fixture"
        generate_demo(cls.root, seed=31)
        cls.cfg = {"data": {"history_frames": 8, "signal_window_s": .1,
            "waveform_samples": 64, "image_size": 32, "thermal_taus_s": [.15, .75],
            "warmup_s": 3.75, "geometry_horizon_frames": 1,
            "alignment_pre_mm": 3., "alignment_post_mm": 1.5,
            "position_sigma_floor_mm": .5}}
        cls.dataset = build_dataset(cls.root, cls.cfg, "test")
        cls.common, cls.plans, cls.diagnostics = common_support(cls.dataset, [0, 1, 2, 4])

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_all_conditions_have_identical_ids_labels_and_coverage(self):
        self.assertEqual(len(self.common), len(self.dataset) - 8)  # 4 earlier frames per seam
        fields = ["sample_id", "seam_id", "segment_id", "s_mm", "cell_start_mm", "cell_end_mm", "y_hard", "y_soft"]
        views = [DelayedElectricalView(self.dataset, self.common, self.plans[d], d) for d in [0, 1, 2, 4]]
        for view in views:
            self.assertEqual([[r[k] for k in fields] for r in view.records],
                             [[r[k] for k in fields] for r in views[0].records])
        self.assertTrue(all(abs(r["electrical_age_s"] - .5) < 1e-12 for r in views[-1].records))

    def test_delay_zero_reproduces_original_inputs(self):
        view = DelayedElectricalView(self.dataset, self.common, self.plans[0], 0)
        original = self.dataset[self.common[0]]
        actual = view[0]
        for key in original:
            if key != "index":
                np.testing.assert_array_equal(original[key].numpy(), actual[key].numpy(), err_msg=key)

    def test_only_older_electrical_fields_change_and_prior_is_recomputed(self):
        original = self.dataset[self.common[0]]
        view = DelayedElectricalView(self.dataset, self.common, self.plans[4], 4)
        actual = view[0]
        for key in ["image", "condition", "target_position", "y_soft", "y_hard", "label_weight", "geom_target", "geom_mask"]:
            np.testing.assert_array_equal(original[key].numpy(), actual[key].numpy(), err_msg=key)
        plan = self.plans[4][self.common[0]]
        seg = self.dataset._segments[plan["segment_index"]]
        self.assertLess(plan["latest_signal_end_s"], view.records[0]["t_frame_s"])
        np.testing.assert_array_equal(actual["thermal"].numpy(), seg["thermal"][plan["first_frame"]:plan["source_frame"]+1])
        expected_prior, expected_mask = alignment_prior(
            seg["positions"][plan["first_frame"]:plan["source_frame"]+1],
            seg["target"][plan["current_frame"]], .5, 3., 1.5)
        np.testing.assert_array_equal(actual["alignment_prior"].numpy(), expected_prior)
        np.testing.assert_array_equal(actual["alignment_mask"].numpy(), expected_mask)
        self.assertFalse(np.array_equal(original["position"].numpy(), actual["position"].numpy()))

    def test_large_delay_cannot_expand_geometry_support(self):
        index = len(self.dataset) - 20
        plan, reason = delay_plan(self.dataset, index, 12)
        self.assertIsNone(plan)
        self.assertEqual(reason, "no_geometry_support_for_current_target")

    def test_negative_delays_and_centered_windows_are_rejected(self):
        with self.assertRaises(ValueError):
            normalize_delays([0, -1])
        with self.assertRaises(ValueError):
            normalize_delays([1, 2])
        with self.assertRaises(ValueError):
            assert_causal_contract({"data": {"signal_window_mode": "centered"}})
        with self.assertRaises(ValueError):
            assert_causal_contract({"data": {"signal_future_s": .05}})

    def test_test_selected_threshold_is_rejected(self):
        path = Path(self.temp.name) / "threshold.json"
        path.write_text(json.dumps({"threshold": .5, "selection_split": "test", "split_column_verified": True}))
        with self.assertRaises(ValueError):
            read_frozen_threshold(path)
        path.write_text(json.dumps({"threshold": .5, "selection_split": "validation", "split_column_verified": True}))
        self.assertEqual(read_frozen_threshold(path)[0], .5)


if __name__ == "__main__":
    unittest.main()
