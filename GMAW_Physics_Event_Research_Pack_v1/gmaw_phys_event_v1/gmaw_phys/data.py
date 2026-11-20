"""Causal, seam-exclusive input contract for the GMAW reference experiment.

Native U*I is integrated before any waveform resampling. The power integration
uses a documented left sample hold and never reads a future native power value.
The normalized thermal state is a proxy, not temperature or measured heat input.
"""
from __future__ import annotations

from collections import OrderedDict, Counter
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image
from scipy.signal import resample_poly
from scipy.special import ndtr
import torch
from torch.utils.data import Dataset
import yaml

MANIFEST_COLUMNS = ["seam_id", "segment_id", "split", "signal_path", "frames_path",
                    "trajectory_path", "events_path", "material", "thickness_mm",
                    "view_offset_mm", "position_sigma_mm", "inspection_start_mm",
                    "inspection_end_mm", "initial_power_w", "synthetic"]
FRAME_COLUMNS = ["sample_id", "t_s", "available_t_s", "image_path", "width_rel",
                 "length_rel", "area_rel", "geom_valid"]
EVENT_COLUMNS = ["event_id", "start_mm", "end_mm", "class_name", "confidence",
                 "boundary_sigma_mm"]
GEOMETRY_COLUMNS = ["width_rel", "length_rel", "area_rel"]


def load_config(path):
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def safe_path(root, relative):
    root = Path(root).resolve()
    rel = Path(str(relative))
    if rel.is_absolute() or not str(relative).strip() or "\\" in str(relative):
        raise ValueError(f"Expected portable relative path: {relative!r}")
    path = (root / rel).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Path escapes dataset root: {relative}")
    if not path.is_file():
        raise ValueError(f"Missing file: {relative}")
    return path


def _bool(value):
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if str(value).strip().lower() in {"1", "true"}:
        return True
    if str(value).strip().lower() in {"0", "false"}:
        return False
    raise ValueError(f"Expected true/false or 0/1, got {value!r}")


def _csv(path, columns):
    frame = pd.read_csv(path, keep_default_na=False)
    missing = set(columns) - set(frame.columns)
    if missing:
        raise ValueError(f"{path.name}: missing columns {sorted(missing)}")
    return frame


def _numbers(frame, columns):
    for name in columns:
        frame[name] = pd.to_numeric(frame[name], errors="raise")
        if not np.isfinite(frame[name].to_numpy(float)).all():
            raise ValueError(f"Nonfinite values in {name}")


def _strict_time(t, name):
    if len(t) < 2 or not np.isfinite(t).all() or np.any(np.diff(t) <= 0):
        raise ValueError(f"{name} needs >=2 finite strictly increasing samples")


def _load_signal(path):
    with np.load(path, allow_pickle=False) as obj:
        required = {"t_s", "current_a", "voltage_v"}
        if not required.issubset(obj.files):
            raise ValueError(f"{path.name}: NPZ requires {sorted(required)}")
        arrays = [np.asarray(obj[key], dtype=np.float64)
                  for key in ("t_s", "current_a", "voltage_v")]
    if any(a.ndim != 1 for a in arrays) or len({len(a) for a in arrays}) != 1:
        raise ValueError("Signal arrays must be equal-length 1D numeric arrays")
    if not all(np.isfinite(a).all() for a in arrays):
        raise ValueError("Nonfinite native signal values")
    _strict_time(arrays[0], "Native signal timestamps")
    if np.any(arrays[1] * arrays[2] < 0):
        raise ValueError("Negative native U*I: correct/record sensor polarity upstream; no silent clipping")
    return tuple(arrays)


def _read_segment(root, row):
    frames = _csv(safe_path(root, row["frames_path"]), FRAME_COLUMNS)
    trajectory = _csv(safe_path(root, row["trajectory_path"]), ["t_s", "s_mm"])
    events = _csv(safe_path(root, row["events_path"]), EVENT_COLUMNS)
    _numbers(frames, ["t_s", "available_t_s"])
    _numbers(trajectory, ["t_s", "s_mm"])
    _numbers(events, ["start_mm", "end_mm", "confidence", "boundary_sigma_mm"])
    _strict_time(frames.t_s.to_numpy(float), "Frame timestamps")
    _strict_time(trajectory.t_s.to_numpy(float), "Trajectory timestamps")
    if np.any(np.diff(trajectory.s_mm.to_numpy(float)) <= 0):
        raise ValueError("Segment trajectory must progress strictly forward; split stops/reversals upstream")
    if np.any(frames.available_t_s < frames.t_s):
        raise ValueError("An image cannot be available before its frame timestamp")
    if frames.sample_id.astype(str).duplicated().any():
        raise ValueError("Duplicate sample_id in segment")
    if events.event_id.astype(str).duplicated().any():
        raise ValueError("Duplicate event_id in segment")
    frames["geom_valid"] = frames.geom_valid.map(_bool)
    for col in GEOMETRY_COLUMNS:
        # Missing geometry is allowed only when geom_valid is false.
        values = pd.to_numeric(frames[col], errors="coerce")
        good = frames.geom_valid.to_numpy(bool)
        if not np.isfinite(values[good]).all() or np.any((values[good] < 0) | (values[good] > 1)):
            raise ValueError(f"{col}: valid geometry must be finite fractions in [0,1]")
        frames[col] = values.fillna(0.)
    if len(events):
        if np.any(events.end_mm <= events.start_mm):
            raise ValueError("Event end_mm must exceed start_mm")
        if np.any((events.confidence < 0) | (events.confidence > 1)) or np.any(events.boundary_sigma_mm < 0):
            raise ValueError("Event confidence must be [0,1] and sigma nonnegative")
        if any(str(x).strip().lower() in {"", "normal"} for x in events.class_name):
            raise ValueError("Events require defect or Unknown names; Normal is the inspected background")
    for image_path in frames.image_path:
        safe_path(root, image_path)
    return frames, trajectory, events


def _manifest(root):
    manifest = _csv(safe_path(root, "manifest.csv"), MANIFEST_COLUMNS)
    if not len(manifest):
        raise ValueError("Manifest is empty")
    for name in ("seam_id", "segment_id", "split"):
        manifest[name] = manifest[name].astype(str)
        if (manifest[name].str.len() == 0).any():
            raise ValueError(f"Empty {name}")
    if not set(manifest.split).issubset({"train", "val", "test"}):
        raise ValueError("Split must be train/val/test")
    if manifest.duplicated(["seam_id", "segment_id"]).any():
        raise ValueError("Duplicate seam_id/segment_id")
    if (manifest.groupby("seam_id").split.nunique() != 1).any():
        raise ValueError("A seam appears in multiple splits; whole-seam exclusivity is required")
    numeric = ["thickness_mm", "view_offset_mm", "position_sigma_mm", "inspection_start_mm",
               "inspection_end_mm", "initial_power_w"]
    _numbers(manifest, numeric)
    if np.any(manifest.thickness_mm <= 0) or np.any(manifest.position_sigma_mm < 0) or np.any(manifest.initial_power_w < 0):
        raise ValueError("Invalid thickness, position sigma, or initial power")
    if np.any(manifest.inspection_end_mm <= manifest.inspection_start_mm):
        raise ValueError("Inspection coverage must have positive length")
    manifest["synthetic"] = manifest.synthetic.map(_bool)
    return manifest


def _sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_dataset(root):
    """Return diagnostics; never change data or infer missing metadata."""
    result = {"ok": False, "errors": [], "warnings": [], "segments": 0, "seams": 0,
              "synthetic": None, "diagnostics": [], "fingerprint_scope":
              "SHA256 of manifest/CSV/native-signal bytes; image paths+sizes, not image bytes"}
    root = Path(root).resolve()
    try:
        manifest = _manifest(root)
    except Exception as exc:
        result["errors"].append(str(exc))
        return result
    result.update(segments=int(len(manifest)), seams=int(manifest.seam_id.nunique()),
                  synthetic=bool(manifest.synthetic.all()),
                  split_seams={k: int(v) for k, v in manifest.groupby("split").seam_id.nunique().items()})
    seen_samples, seen_paths = set(), {}
    fingerprint = hashlib.sha256()
    fingerprint.update(_sha256(root / "manifest.csv").encode())
    for row in manifest.to_dict("records"):
        key = f"{row['seam_id']}/{row['segment_id']}"
        try:
            frames, trajectory, events = _read_segment(root, row)
            t, current, voltage = _load_signal(safe_path(root, row["signal_path"]))
            dt = float(np.median(np.diff(t)))
            gap_ratio = float(np.max(np.diff(t)) / dt)
            if gap_ratio > 2.1 + 1e-7:
                raise ValueError(f"Native stream contains gaps (max/median dt={gap_ratio:.3g}); split genuine acquisition gaps upstream")
            if frames.t_s.min() < t[0] or frames.t_s.max() > t[-1] + dt * 1e-3:
                raise ValueError("Frames extend outside observed native signal support")
            if frames.t_s.min() < trajectory.t_s.min() or frames.t_s.max() > trajectory.t_s.max():
                raise ValueError("Trajectory does not cover all frame anchors")
            ids = set(frames.sample_id.astype(str))
            if ids & seen_samples:
                raise ValueError("sample_id must be globally unique")
            seen_samples.update(ids)
            for name in ("signal_path", "frames_path", "trajectory_path", "events_path"):
                path = safe_path(root, row[name])
                if path in seen_paths and seen_paths[path] != row["split"]:
                    raise ValueError(f"Underlying {name} is reused across splits")
                seen_paths[path] = row["split"]
                fingerprint.update((str(row[name]) + _sha256(path)).encode())
            for rel in frames.image_path:
                path = safe_path(root, rel)
                if path in seen_paths and seen_paths[path] != row["split"]:
                    raise ValueError("An image file is reused across splits")
                seen_paths[path] = row["split"]
                fingerprint.update(f"{rel}:{path.stat().st_size}".encode())
            result["diagnostics"].append({"seam_id": row["seam_id"], "segment_id": row["segment_id"],
                "split": row["split"], "native_samples": len(t), "native_hz_median": 1. / dt,
                "native_max_gap_s": float(np.max(np.diff(t))), "frames": len(frames),
                "image_hz_median": 1. / float(np.median(np.diff(frames.t_s))),
                "target_events": int((events.class_name == "Undercut").sum()),
                "other_events": int((events.class_name != "Undercut").sum()),
                "mean_native_ui_w": float(np.mean(current * voltage)), "synthetic": row["synthetic"]})
            if not row["synthetic"] and 1. / dt < 90000:
                result["warnings"].append(f"{key}: native sampling is below 100kHz; no upsampling can restore missing information")
            if np.max(np.diff(frames.t_s)) > .20:
                result["warnings"].append(f"{key}: frame gaps present; windows crossing gaps will be omitted")
        except Exception as exc:
            result["errors"].append(f"{key}: {exc}")
    result["data_fingerprint_sha256"] = fingerprint.hexdigest()
    result["ok"] = not result["errors"]
    if result["synthetic"]:
        result["warnings"].append("All data are synthetic software fixtures; metrics are not evidence of welding performance")
    return result


def native_power_integral(t, current, voltage):
    """Return causal primitive F(q) of native U*I with left sample hold."""
    power = current * voltage
    cumulative = np.r_[0., np.cumsum(power[:-1] * np.diff(t))]
    def primitive(query):
        query = np.asarray(query, dtype=float)
        if np.any(query < t[0] - 1e-10) or np.any(query > t[-1] + 1e-10):
            raise ValueError("Requested power integral outside observed native support")
        idx = np.clip(np.searchsorted(t, query, side="right") - 1, 0, len(t) - 1)
        return cumulative[idx] + power[idx] * (query - t[idx])
    return primitive


def causal_resample(t, current, voltage, anchor, window_s, output_samples, native_dt=None):
    """Polyphase antialiased waveform resampling of an entirely past window."""
    left = anchor - window_s
    if left < t[0] - 1e-10 or anchor > t[-1] + 1e-10:
        raise ValueError("Causal waveform window lacks native support")
    stop = int(np.searchsorted(t, anchor, side="right"))
    start = max(0, int(np.searchsorted(t, left, side="right")) - 1)
    if stop - start < 2:
        raise ValueError("Insufficient samples for causal waveform")
    observed_t = t[start:stop]
    # Infer cadence from this observed past window, not future timestamps.
    dt = float(native_dt if native_dt is not None else np.median(np.diff(observed_t)))
    count = max(2, int(round(window_s / dt)))
    grid = left + np.arange(count, dtype=float) * window_s / count
    source = np.stack([np.interp(grid, observed_t, current[start:stop]),
                       np.interp(grid, observed_t, voltage[start:stop])], axis=0)
    divisor = math.gcd(count, int(output_samples))
    wave = resample_poly(source, int(output_samples) // divisor, count // divisor,
                         axis=-1, padtype="line")
    if wave.shape[-1] != output_samples:
        raise RuntimeError("Unexpected polyphase output size")
    # Fixed physical scales, not fitted on train or test values.
    return (wave / np.array([[400.], [40.]])).astype(np.float32)


def soft_interval_label(s_mm, events, inspection_start_mm, inspection_end_mm,
                        position_sigma_mm=0.):
    """Spatial Gaussian label uncertainty. Confidence changes weight, not class."""
    if not inspection_start_mm <= s_mm <= inspection_end_mm:
        return 0., -1, 0., False
    rows = events.to_dict("records") if isinstance(events, pd.DataFrame) else events
    probability, hard, weight, uncertain = 0., 0, 1., False
    for event in rows:
        a, b = float(event["start_mm"]), float(event["end_mm"])
        sigma = math.hypot(float(event.get("boundary_sigma_mm", 0.)), position_sigma_mm)
        near = a - 2 * sigma <= s_mm <= b + 2 * sigma
        if event["class_name"] != "Undercut":
            if near:
                return 0., -1, 0., True
            continue
        if sigma > 0:
            q = float(ndtr((s_mm - a) / sigma) - ndtr((s_mm - b) / sigma))
            edge = min(abs(s_mm - a), abs(s_mm - b)) <= 2 * sigma
        else:
            q, edge = float(a <= s_mm <= b), False
        if q > probability:
            probability = q
        if a <= s_mm <= b:
            hard = 1
        if near:
            weight = min(weight, float(event.get("confidence", 1.)))
        uncertain = uncertain or edge
    return float(np.clip(probability, 0., 1.)), hard, weight, uncertain


def _causal_positions(frame_t, trajectory):
    t, s = trajectory.t_s.to_numpy(float), trajectory.s_mm.to_numpy(float)
    idx = np.searchsorted(t, frame_t, side="right") - 1
    if np.any(idx < 0):
        raise ValueError("No past trajectory sample for frame")
    previous = np.maximum(idx - 1, 0)
    denom = t[idx] - t[previous]
    speed = np.divide(s[idx] - s[previous], denom, out=np.zeros(len(idx)), where=denom > 0)
    # No interpolation with future robot pose: most recent observed position.
    return s[idx], speed


class WeldDataset(Dataset):
    """Metadata stays resident; raw signals use a one-segment LRU.

    Images/waveforms are lazily cached once per frame (never L copies). NPZ is
    not memory mapped: very long runs must be exported at manageable lengths.
    """
    def __init__(self, root, cfg, split):
        from .physics import thermal_filter_bank, alignment_prior
        self.root, self.cfg, self.split = Path(root).resolve(), cfg, split
        self.dc = cfg.get("data", {})
        self.history = int(self.dc.get("history_frames", 8))
        self.window = float(self.dc.get("signal_window_s", .1))
        self.samples = int(self.dc.get("waveform_samples", 128))
        self.size = int(self.dc.get("image_size", 48))
        if self.history < 1 or self.window <= 0 or self.samples < 2 or self.size < 8:
            raise ValueError("Invalid data window/history/resolution configuration")
        self.records, self._indices, self._segments = [], [], []
        self._raw_cache, self._wave_cache, self._image_cache = OrderedDict(), OrderedDict(), OrderedDict()
        counts, event_rows = Counter(), []
        manifest = _manifest(self.root)
        for row in manifest[manifest.split == split].to_dict("records"):
            frames, traj, events = _read_segment(self.root, row)
            t, current, voltage = _load_signal(safe_path(self.root, row["signal_path"]))
            native_dt = float(np.median(np.diff(t)))
            if np.max(np.diff(t)) > self.dc.get("max_signal_gap_factor", 2.1) * native_dt + 1e-10:
                raise ValueError("Native gaps would invalidate causal thermal history; segment explicitly upstream")
            ft = frames.t_s.to_numpy(float)
            if ft.min() < t[0] or ft.max() > t[-1] + 1e-9:
                raise ValueError("Frames outside native signal support")
            pos, speed = _causal_positions(ft, traj)
            if np.any(np.diff(pos) <= 0):
                raise ValueError("Trajectory updates too sparse for unique forward frame positions")
            target = pos + float(row["view_offset_mm"])
            primitive = native_power_integral(t, current, voltage)
            grid = np.unique(np.r_[t[0], np.arange(t[0], ft[-1], .125), ft])
            dt_grid = np.diff(grid)
            powers = np.r_[row["initial_power_w"], np.diff(primitive(grid)) / dt_grid]
            p_ref = float(self.dc.get("power_reference_w", 12000.))
            states = thermal_filter_bank(grid, powers,
                self.dc.get("thermal_taus_s", [.15, .35, .75]), p_ref,
                initial_power_w=float(row["initial_power_w"]))
            thermal = states[np.searchsorted(grid, ft)]
            mean_power = np.zeros(len(ft), dtype=np.float32)
            valid_power = ft - .125 >= t[0] - 1e-10
            mean_power[valid_power] = ((primitive(ft[valid_power]) -
                primitive(ft[valid_power] - .125)) / .125 / p_ref).astype(np.float32)
            segment = dict(row=row, frames=frames, frame_t=ft, positions=pos, target=target,
                           speed=speed, thermal=thermal, power=mean_power,
                           signal_start=float(t[0]), signal_end=float(t[-1]), native_dt=native_dt)
            si = len(self._segments)
            self._segments.append(segment)
            for event in events[events.class_name == "Undercut"].to_dict("records"):
                start = float(event["start_mm"])
                ref = float(np.interp(start, traj.s_mm, traj.t_s)) if traj.s_mm.min() <= start <= traj.s_mm.max() else None
                event_rows.append(dict(event, seam_id=row["seam_id"], segment_id=row["segment_id"],
                                       reference_t_s=ref))
            max_gap = float(self.dc.get("max_image_gap_s", .20))
            sigma = max(float(row["position_sigma_mm"]), float(self.dc.get("position_sigma_floor_mm", .5)))
            warmup = float(self.dc.get("warmup_s", 0.))
            for k in range(len(ft)):
                counts["frames_total"] += 1
                first = k - self.history + 1
                if first < 0 or ft[k] - t[0] < warmup or ft[first] - max(.125, self.window) < t[0] - 1e-10:
                    counts["insufficient_history_or_warmup"] += 1
                    continue
                if np.any(np.diff(ft[first:k + 1]) > max_gap):
                    counts["history_crosses_image_gap"] += 1
                    continue
                prior, mask = alignment_prior(pos[first:k + 1], target[k], sigma,
                    float(self.dc.get("alignment_pre_mm", 3.)), float(self.dc.get("alignment_post_mm", 1.5)))
                if not np.any(mask):
                    counts["no_physical_alignment_support"] += 1
                    continue
                y_soft, y_hard, weight, uncertain = soft_interval_label(target[k], events,
                    float(row["inspection_start_mm"]), float(row["inspection_end_mm"]),
                    float(row["position_sigma_mm"]))
                if y_hard < 0 or weight <= 0:
                    counts["unknown_other_or_zero_confidence"] += 1
                    continue
                # Coverage cells never bridge dropped frames/gaps. Cell neighbours
                # are original anchors; these are evaluation metadata, not inputs.
                nominal = max(native_dt, float(np.median(np.diff(ft))))
                half_left = min((target[k] - target[k - 1]) / 2, speed[k] * nominal / 2)
                half_right = min((target[k + 1] - target[k]) / 2, speed[k] * nominal / 2) if k + 1 < len(ft) else speed[k] * nominal / 2
                left = max(target[k] - half_left, float(row["inspection_start_mm"]), float(target[0]))
                right = min(target[k] + half_right, float(row["inspection_end_mm"]), float(target[-1]))
                # Exclusion regions must also carve evaluation cells, not only centres.
                for event in events[events.class_name != "Undercut"].to_dict("records"):
                    es = math.hypot(float(event["boundary_sigma_mm"]), float(row["position_sigma_mm"]))
                    a, b = event["start_mm"] - 2 * es, event["end_mm"] + 2 * es
                    if target[k] < a:
                        right = min(right, a)
                    elif target[k] > b:
                        left = max(left, b)
                if right <= left:
                    counts["zero_coverage_cell"] += 1
                    continue
                record = dict(sample_id=str(frames.iloc[k].sample_id), seam_id=row["seam_id"],
                    segment_id=row["segment_id"], s_mm=float(target[k]), cell_start_mm=float(left),
                    cell_end_mm=float(right), t_frame_s=float(ft[k]),
                    t_decision_s=float(max(ft[k], frames.iloc[first:k + 1].available_t_s.max())),
                    y_hard=int(y_hard), y_soft=float(y_soft), label_weight=float(weight),
                    boundary_uncertain=bool(uncertain), synthetic=bool(row["synthetic"]))
                self.records.append(record)
                self._indices.append((si, k, prior, mask))
            del t, current, voltage, primitive
        self.events = pd.DataFrame(event_rows, columns=EVENT_COLUMNS + ["seam_id", "segment_id", "reference_t_s"])
        self.summary = dict(split=split, samples=len(self.records), seams=int(manifest[manifest.split == split].seam_id.nunique()),
            target_events=len(self.events), counts=dict(counts), synthetic=bool(manifest[manifest.split == split].synthetic.all()),
            input_normalization={"current_a": 400., "voltage_v": 40., "power_w": self.dc.get("power_reference_w", 12000.)},
            native_power_integration="left sample hold of native U*I before resampling",
            power_window_s=.125, resampling="scipy.signal.resample_poly, line padding; whole input window is causal")

    def __len__(self):
        return len(self.records)

    @staticmethod
    def _cache(cache, key, loader, limit):
        if key not in cache:
            cache[key] = loader()
            while len(cache) > limit:
                cache.popitem(last=False)
        cache.move_to_end(key)
        return cache[key]

    def _raw(self, si):
        path = safe_path(self.root, self._segments[si]["row"]["signal_path"])
        return self._cache(self._raw_cache, si, lambda: _load_signal(path), 1)

    def _wave(self, si, k):
        def get():
            t, current, voltage = self._raw(si)
            return causal_resample(t, current, voltage, self._segments[si]["frame_t"][k],
                                   self.window, self.samples)
        return self._cache(self._wave_cache, (si, k), get, 256)

    def _image(self, si, k):
        def get():
            path = safe_path(self.root, self._segments[si]["frames"].iloc[k].image_path)
            with Image.open(path) as image:
                array = np.asarray(image.convert("RGB").resize((self.size, self.size), Image.Resampling.BILINEAR), dtype=np.float32) / 255.
            return array.transpose(2, 0, 1).copy()
        return self._cache(self._image_cache, (si, k), get, 256)

    def __getitem__(self, index):
        si, k, prior, mask = self._indices[index]
        seg, record = self._segments[si], self.records[index]
        first = k - self.history + 1
        history = range(first, k + 1)
        geom, geom_mask = np.zeros(3, np.float32), np.zeros(3, np.float32)
        horizon = int(self.dc.get("geometry_horizon_frames", 1))
        future = k + horizon
        # These values are labels only. Validation/test expose them solely for
        # held-out geometry MAE; the model forward never receives them as input.
        if horizon > 0 and future < len(seg["frames"]):
            row = seg["frames"].iloc[future]
            if row.geom_valid and np.all(np.diff(seg["frame_t"][k:future + 1]) <= self.dc.get("max_image_gap_s", .20)):
                geom = row[GEOMETRY_COLUMNS].to_numpy(dtype=np.float32)
                geom_mask[:] = 1.
        values = {
            "signal": np.stack([self._wave(si, j) for j in history]),
            "image": np.stack([self._image(si, j) for j in history]),
            "thermal": seg["thermal"][first:k + 1].astype(np.float32),
            "power": seg["power"][first:k + 1, None].astype(np.float32),
            "condition": np.array([seg["row"]["thickness_mm"] / 10., seg["speed"][k] / 5.], np.float32),
            "position": seg["positions"][first:k + 1].astype(np.float32),
            "target_position": np.float32(seg["target"][k]),
            "alignment_prior": np.asarray(prior, dtype=np.float32),
            "alignment_mask": np.asarray(mask, dtype=bool),
            "y_soft": np.float32(record["y_soft"]), "y_hard": np.int64(record["y_hard"]),
            "label_weight": np.float32(record["label_weight"]),
            "geom_target": geom, "geom_mask": geom_mask, "index": np.int64(index)}
        return {key: torch.as_tensor(value) for key, value in values.items()}

    def export_metadata(self, output_dir):
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(self.records).to_csv(output / f"{self.split}_records.csv", index=False)
        self.events.to_csv(output / f"{self.split}_events.csv", index=False)
        (output / f"{self.split}_summary.json").write_text(json.dumps(self.summary, ensure_ascii=False, indent=2), encoding="utf-8")


def build_dataset(root, cfg, split):
    return WeldDataset(root, cfg, split)
