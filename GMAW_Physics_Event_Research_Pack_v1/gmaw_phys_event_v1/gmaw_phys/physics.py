"""Causal, low-dimensional physical proxies used by the reference models.

These filters are dimensionless dissipative states, not measured temperatures,
enthalpies, or a calibrated reconstruction of a three-dimensional weld pool.
The time constants are fixed model assumptions selected on training/validation
data.  They must not be interpreted as identified material properties.
"""

from __future__ import annotations

import numpy as np


def thermal_filter_bank(t_s, power_w, taus_s, p_ref_w, initial_power_w=0.0):
    """Integrate a normalized bank over one complete continuous segment.

    ``t_s[k]`` is the right end of a power bin. ``power_w[k]`` is the
    mean native-sample U*I over (t_s[k-1], t_s[k]], not a product of
    separately averaged current and voltage. At k=0 the interval is zero,
    and the state is exactly ``initial_power_w / p_ref_w``.

    For each fixed tau, dz/dt = (P/P_ref - z)/tau. The piecewise-constant
    input has the exact exponential update. Compute this function ONCE on
    the full segment, then slice histories; resetting per training window
    would erase thermal history and is not supported by the data pipeline.
    """
    t = np.asarray(t_s, dtype=np.float64)
    power = np.asarray(power_w, dtype=np.float64)
    taus = np.asarray(taus_s, dtype=np.float64)
    if t.ndim != 1 or power.ndim != 1 or t.shape != power.shape:
        raise ValueError("t_s and power_w must be one-dimensional arrays of equal length")
    if taus.ndim != 1 or taus.size == 0:
        raise ValueError("taus_s must be a non-empty one-dimensional array")
    if not np.all(np.isfinite(t)) or not np.all(np.isfinite(power)):
        raise ValueError("timestamps and power must be finite")
    if not np.all(np.isfinite(taus)) or np.any(taus <= 0):
        raise ValueError("all fixed time constants must be finite and positive")
    if t.size > 1 and np.any(np.diff(t) <= 0):
        raise ValueError("timestamps must be strictly increasing")
    p_ref = float(p_ref_w)
    initial = float(initial_power_w)
    if not np.isfinite(p_ref) or p_ref <= 0:
        raise ValueError("p_ref_w must be finite and positive")
    if not np.isfinite(initial) or initial < 0 or np.any(power < 0):
        raise ValueError("power and initial_power_w must be nonnegative; check sensor polarity")
    result = np.empty((t.size, taus.size), dtype=np.float64)
    state = np.full(taus.shape, initial / p_ref, dtype=np.float64)
    for k in range(t.size):
        dt = 0.0 if k == 0 else t[k] - t[k - 1]
        # -expm1 remains accurate for small dt/tau.
        gain = -np.expm1(-dt / taus)
        state = (1.0 - gain) * state + gain * (power[k] / p_ref)
        result[k] = state
    if not np.all(np.isfinite(result)):
        raise ValueError("normalized filter state is non-finite")
    return result.astype(np.float32)


def alignment_prior(positions_mm, target_mm, sigma_mm, pre_mm, post_mm):
    """Geometry-only Gaussian prior and finite spatial support.

    Positions belong to already acquired causal electrical history. The data
    loader is responsible for that time ordering; this function has no labels
    or inspection-event inputs. No-support returns zeros so the caller can
    skip the sample instead of inventing an alignment.
    """
    positions = np.asarray(positions_mm, dtype=np.float64)
    if positions.ndim != 1 or not np.all(np.isfinite(positions)):
        raise ValueError("positions_mm must be a finite one-dimensional array")
    target, sigma, pre, post = map(float, (target_mm, sigma_mm, pre_mm, post_mm))
    if not np.all(np.isfinite([target, sigma, pre, post])):
        raise ValueError("alignment parameters must be finite")
    if sigma <= 0 or pre < 0 or post < 0:
        raise ValueError("sigma must be positive and support widths nonnegative")
    mask = (positions >= target - pre) & (positions <= target + post)
    prior = np.zeros(positions.shape, dtype=np.float64)
    if mask.any():
        with np.errstate(over="ignore", invalid="ignore"):
            distances = np.clip((positions[mask] - target) / sigma, -1e150, 1e150)
            log_weights = -0.5 * distances**2
        log_weights -= np.max(log_weights)
        weights = np.exp(log_weights)
        prior[mask] = weights / weights.sum()
    return prior.astype(np.float32), mask
