import copy
import unittest

import numpy as np
import torch

from gmaw_phys.physics import alignment_prior, thermal_filter_bank
from gmaw_phys.models import MODEL_NAMES, build_model


class PhysicsTests(unittest.TestCase):
    def test_constant_input_exact_response_and_decay(self):
        times = np.arange(0.0, 6.0, 0.125)
        taus = np.array([0.15, 0.75, 1.5])
        result = thermal_filter_bank(times, np.full(len(times), 12000.0), taus, 12000.0)
        expected = 1.0 - np.exp(-times[:, None] / taus)
        np.testing.assert_allclose(result, expected, atol=1e-7, rtol=1e-6)
        self.assertTrue(np.all(result >= 0))
        self.assertTrue(np.all(result <= 1))
        self.assertTrue(np.all(np.diff(result, axis=0) >= 0))
        decay = thermal_filter_bank(times, np.zeros(len(times)), taus, 12000.0, 12000.0)
        np.testing.assert_allclose(decay, np.exp(-times[:, None] / taus), atol=1e-7)

    def test_causal_prefix_and_full_segment_memory(self):
        times = np.arange(50) * 0.125
        power = np.linspace(8000, 14000, 50)
        full = thermal_filter_bank(times, power, [0.15, 0.75], 12000, 5000)
        prefix = thermal_filter_bank(times[:21], power[:21], [0.15, 0.75], 12000, 5000)
        np.testing.assert_array_equal(prefix, full[:21])
        changed = power.copy()
        changed[21:] *= 10
        np.testing.assert_array_equal(full[:21], thermal_filter_bank(times, changed, [0.15, 0.75], 12000, 5000)[:21])
        incorrectly_reset = thermal_filter_bank(times[10:21], power[10:21], [0.15, 0.75], 12000, 5000)
        self.assertGreater(float(np.abs(incorrectly_reset - full[10:21]).max()), 0.1)

    def test_irregular_bins_and_initial_value(self):
        out = thermal_filter_bank([0.2, 0.3, 0.8], [9999, 0, 12000], [0.5], 12000, 6000)
        expected1 = 0.5 * np.exp(-0.1 / 0.5)
        expected2 = np.exp(-0.5 / 0.5) * expected1 + (1 - np.exp(-1))
        np.testing.assert_allclose(out[:, 0], [0.5, expected1, expected2], atol=1e-7)

    def test_validation(self):
        for times, power, taus, pref in [([0, 0], [1, 1], [1], 1), ([0], [-1], [1], 1), ([0], [1], [0], 1), ([0], [1], [1], 0)]:
            with self.assertRaises(ValueError):
                thermal_filter_bank(times, power, taus, pref)

    def test_alignment_geometry_and_empty_support(self):
        prior, mask = alignment_prior([0, 1, 2, 3, 4], 2, 0.5, 1, 1)
        np.testing.assert_array_equal(mask, [False, True, True, True, False])
        self.assertEqual(float(prior[0]), 0.0)
        self.assertEqual(float(prior[4]), 0.0)
        self.assertAlmostEqual(float(prior.sum()), 1.0, places=6)
        self.assertEqual(float(prior[1]), float(prior[3]))
        self.assertGreater(float(prior[2]), float(prior[1]))
        empty, no_support = alignment_prior([0, 1], 99, 0.5, 1, 1)
        self.assertFalse(no_support.any())
        self.assertEqual(float(empty.sum()), 0.0)


class ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        torch.set_num_threads(1)

    def batch(self):
        torch.manual_seed(7)
        b, length, k = 3, 8, 3
        return {
            "signal": torch.rand(b, length, 2, 128),
            "image": torch.rand(b, length, 3, 32, 32),
            "condition": torch.rand(b, 2),
            "power": torch.rand(b, length, 1),
            "thermal": torch.rand(b, length, k),
            "alignment_mask": torch.tensor([[False, False, True, True, True, True, False, False]]).expand(b, -1).clone(),
            "alignment_prior": torch.tensor([[0, 0, 0.1, 0.4, 0.4, 0.1, 0, 0.0]]).expand(b, -1).clone(),
            "geom_target": torch.rand(b, 3), "geom_mask": torch.ones(b, 3),
            "y_hard": torch.tensor([0, 1, 1]), "y_soft": torch.rand(b),
        }

    def config(self, name="phys_align", **flags):
        model = {"name": name, "hidden_dim": 24, "dropout": 0.0, "use_aux": True,
                 "use_heat": name in ("thermal_filter", "phys_align"), "use_alignment": name == "phys_align"}
        model.update(flags)
        return {"data": {"thermal_taus_s": [0.15, 0.35, 0.75]}, "model": model}

    def test_variants_shapes_and_backward(self):
        for name in MODEL_NAMES:
            with self.subTest(name=name):
                model = build_model(self.config(name))
                output = model(self.batch())
                self.assertEqual(tuple(output["logits"].shape), (3,))
                self.assertEqual(tuple(output["geom_pred"].shape), (3, 3))
                self.assertTrue(torch.isfinite(output["logits"]).all())
                loss = output["logits"].square().mean() + output["geom_pred"].square().mean()
                loss.backward()
                for module in (model.electrical_encoder, model.image_encoder, model.classifier, model.geometry_head):
                    self.assertTrue(any(p.grad is not None and p.grad.abs().sum() > 0 for p in module.parameters()))
                if model.use_heat:
                    self.assertEqual(tuple(output["thermal_mix"].shape), (3, 8, 1))
                    self.assertIsNotNone(model.thermal_logits.grad)
                    self.assertGreater(float(model.thermal_logits.grad.abs().sum()), 0)
                    weights = model.thermal_weights()
                    self.assertTrue((weights >= 0).all())
                    self.assertAlmostEqual(float(weights.sum()), 1.0, places=6)

    def test_hard_mask_and_no_electrical_cross_token_leak(self):
        model = build_model(self.config()).eval()
        batch = self.batch()
        output = model(batch)
        self.assertTrue(torch.equal(output["attention"][~batch["alignment_mask"]], torch.zeros_like(output["attention"][~batch["alignment_mask"]])))
        torch.testing.assert_close(output["attention"].sum(1), torch.ones(3))
        modified = {key: value.clone() for key, value in batch.items()}
        modified["signal"][~batch["alignment_mask"]] = 1000
        modified["power"][~batch["alignment_mask"]] = 1000
        modified["thermal"][~batch["alignment_mask"]] = 1000
        changed = model(modified)
        torch.testing.assert_close(output["logits"], changed["logits"], atol=1e-7, rtol=1e-6)
        torch.testing.assert_close(output["attention"], changed["attention"], atol=1e-7, rtol=1e-6)

    def test_future_targets_and_labels_are_not_inputs(self):
        model = build_model(self.config()).eval()
        batch = self.batch()
        expected = model(batch)
        for key in ["geom_target", "geom_mask", "y_hard", "y_soft"]:
            batch[key] = torch.full_like(batch[key], 999)
        actual = model(batch)
        torch.testing.assert_close(expected["logits"], actual["logits"], atol=0, rtol=0)
        torch.testing.assert_close(expected["geom_pred"], actual["geom_pred"], atol=0, rtol=0)
        for key in ["geom_target", "geom_mask", "y_hard", "y_soft"]:
            del batch[key]
        torch.testing.assert_close(actual["logits"], model(batch)["logits"], atol=0, rtol=0)

    def test_flags_and_missing_aux_observation(self):
        batch = self.batch()
        for key in ["geom_target", "geom_mask", "y_hard", "y_soft", "thermal", "alignment_prior", "alignment_mask"]:
            del batch[key]
        model = build_model(self.config(use_heat=False, use_alignment=False, use_aux=False))
        out = model(batch)
        self.assertNotIn("thermal_mix", out)
        self.assertTrue(torch.equal(out["geom_pred"], torch.zeros(3, 3)))
        self.assertTrue((out["attention"] > 0).all())
        self.assertIsNone(model.geometry_head)

    def test_no_support_rejected(self):
        batch = self.batch()
        batch["alignment_mask"][0] = False
        with self.assertRaisesRegex(ValueError, "physical support"):
            build_model(self.config())(batch)


if __name__ == "__main__":
    unittest.main()
