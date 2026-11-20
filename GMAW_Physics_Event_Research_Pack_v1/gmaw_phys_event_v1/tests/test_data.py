import tempfile
import unittest
from pathlib import Path
import numpy as np
import pandas as pd

from gmaw_phys.data import (safe_path, native_power_integral, causal_resample,
                            soft_interval_label, validate_dataset, build_dataset)
from gmaw_phys.demo import generate_demo


class NativeSignalTests(unittest.TestCase):
    def test_native_mean_product_is_not_product_of_means(self):
        t = np.array([0., 1., 2., 3.])
        i = np.array([1., 3., 1., 3.])
        u = np.array([3., 1., 3., 1.])
        primitive = native_power_integral(t, i, u)
        self.assertAlmostEqual(float((primitive(2.) - primitive(0.)) / 2.), 3.)
        self.assertNotEqual(3., np.mean(i[:2]) * np.mean(u[:2]))

    def test_resampling_cannot_read_after_anchor(self):
        t = np.arange(0., .3, .0001)
        i, u = 350 + np.sin(2 * np.pi * 200 * t), np.full(len(t), 32.)
        before = causal_resample(t, i, u, .15, .1, 64)
        i[t > .15] = 100000.
        u[t > .15] = 100000.
        after = causal_resample(t, i, u, .15, .1, 64)
        np.testing.assert_array_equal(before, after)

    def test_antialias_filter_removes_high_frequency(self):
        t = np.arange(0., .3, .0001)
        i = 350 + 40 * np.sin(2 * np.pi * 3000 * t)
        u = np.full(len(t), 32.)
        output = causal_resample(t, i, u, .2, .1, 100)
        self.assertLess(float(np.std(output[0, 10:-10])), .01)

    def test_window_outside_support_rejected(self):
        t = np.arange(0., .3, .001)
        with self.assertRaises(ValueError):
            causal_resample(t, np.ones(len(t)), np.ones(len(t)), .05, .1, 100)

    def test_other_defect_is_not_normal(self):
        event = [{"start_mm": 5., "end_mm": 7., "class_name": "Hollow",
                  "confidence": 1., "boundary_sigma_mm": .3}]
        self.assertEqual(soft_interval_label(6., event, 0., 10.)[1], -1)
        self.assertEqual(soft_interval_label(7.4, event, 0., 10.)[1], -1)

    def test_unknown_inspection_and_confidence(self):
        event = [{"start_mm": 5., "end_mm": 7., "class_name": "Undercut",
                  "confidence": .2, "boundary_sigma_mm": .1}]
        self.assertEqual(soft_interval_label(11., event, 0., 10.)[1], -1)
        y, hard, weight, _ = soft_interval_label(6., event, 0., 10., .1)
        self.assertGreater(y, .99)
        self.assertEqual(hard, 1)
        self.assertEqual(weight, .2)

    def test_path_containment_including_symlink(self):
        with tempfile.TemporaryDirectory() as base:
            p = Path(base)
            root = p / "data"
            root.mkdir()
            (p / "secret").write_text("not a dataset")
            (root / "escape").symlink_to(p / "secret")
            for bad in ["../secret", str(p / "secret"), "escape"]:
                with self.assertRaises(ValueError):
                    safe_path(root, bad)


class FixtureContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name) / "fixture"
        generate_demo(cls.root, seed=7)
        cls.cfg = {"data": {"history_frames": 4, "signal_window_s": .1,
                    "waveform_samples": 64, "image_size": 32, "thermal_taus_s": [.15, .75],
                    "warmup_s": 3.75, "geometry_horizon_frames": 1}}

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_fixture_contract_and_coverage(self):
        report = validate_dataset(self.root)
        self.assertTrue(report["ok"], report["errors"])
        self.assertEqual(report["split_seams"], {"test": 2, "train": 5, "val": 2})
        self.assertTrue(report["synthetic"])
        d = build_dataset(self.root, self.cfg, "train")
        item = d[0]
        self.assertEqual(tuple(item["signal"].shape), (4, 2, 64))
        self.assertEqual(tuple(item["thermal"].shape), (4, 2))
        self.assertAlmostEqual(float(item["alignment_prior"].sum()), 1., places=6)
        self.assertTrue(all(r["cell_end_mm"] > r["cell_start_mm"] for r in d.records))
        self.assertTrue(all(r["t_decision_s"] >= r["t_frame_s"] for r in d.records))
        self.assertEqual(len(d.events), 10)

    def test_seam_split_leakage_is_rejected(self):
        path = self.root / "manifest.csv"
        original = path.read_bytes()
        try:
            table = pd.read_csv(path)
            extra = table.iloc[[0]].copy()
            extra["split"], extra["segment_id"] = "test", "another"
            pd.concat([table, extra], ignore_index=True).to_csv(path, index=False)
            report = validate_dataset(self.root)
            self.assertFalse(report["ok"])
            self.assertIn("multiple splits", " ".join(report["errors"]))
        finally:
            path.write_bytes(original)

    def test_rt_changes_do_not_change_alignment_or_inputs(self):
        a = build_dataset(self.root, self.cfg, "train")
        x = a[0]
        event_path = self.root / "SYNTH_01/events.csv"
        original = event_path.read_bytes()
        try:
            events = pd.read_csv(event_path)
            events.loc[:, "start_mm"] += 1.
            events.loc[:, "end_mm"] += 1.
            events.to_csv(event_path, index=False)
            b = build_dataset(self.root, self.cfg, "train")
            y = b[0]
            for key in ["signal", "image", "thermal", "power", "condition", "position",
                        "target_position", "alignment_prior", "alignment_mask"]:
                np.testing.assert_array_equal(x[key].numpy(), y[key].numpy(), err_msg=key)
        finally:
            event_path.write_bytes(original)

    def test_future_signal_and_geometry_do_not_change_inputs(self):
        a = build_dataset(self.root, self.cfg, "train")
        x = a[0]
        anchor = a.records[0]["t_frame_s"]
        signal_path = self.root / "SYNTH_01/signals.npz"
        frame_path = self.root / "SYNTH_01/frames.csv"
        raw_original, frame_original = signal_path.read_bytes(), frame_path.read_bytes()
        try:
            with np.load(signal_path, allow_pickle=False) as z:
                values = {key: z[key].copy() for key in z.files}
            values["current_a"][values["t_s"] > anchor] *= 2.
            np.savez_compressed(signal_path, **values)
            frames = pd.read_csv(frame_path)
            frames.loc[frames.t_s > anchor, ["width_rel", "length_rel", "area_rel"]] = .9
            frames.to_csv(frame_path, index=False)
            b = build_dataset(self.root, self.cfg, "train")
            y = b[0]
            for key in ["signal", "image", "thermal", "power", "alignment_prior"]:
                np.testing.assert_array_equal(x[key].numpy(), y[key].numpy(), err_msg=key)
            self.assertFalse(np.array_equal(x["geom_target"].numpy(), y["geom_target"].numpy()))
        finally:
            signal_path.write_bytes(raw_original)
            frame_path.write_bytes(frame_original)


if __name__ == "__main__":
    unittest.main()
