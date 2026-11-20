"""Generate reproducible SYNTHETIC software fixtures, not welding measurements."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image

from .data import MANIFEST_COLUMNS, FRAME_COLUMNS, EVENT_COLUMNS


def generate_demo(output_dir, seed=42):
    root = Path(output_dir).resolve()
    if root.exists() and any(root.iterdir()):
        raise FileExistsError(f"Refusing to overwrite nonempty fixture directory: {root}")
    root.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    rows = []
    for seam_index in range(9):
        seam = f"SYNTH_{seam_index + 1:02d}"
        folder = root / seam
        (folder / "images").mkdir(parents=True)
        duration = 16. + seam_index
        speed = 3.6 + .10 * seam_index
        thickness = [6., 8., 10.][seam_index % 3]
        split = "train" if seam_index < 5 else ("val" if seam_index < 7 else "test")
        # Explicitly 2 kHz: small synthetic data, never claimed to be real 100 kHz.
        fs = 2000.
        t = np.arange(int(duration * fs) + 1, dtype=float) / fs
        phase = rng.uniform(0, 2 * np.pi)
        event_times = [(5.4 + .09 * seam_index, 7.2 + .1 * seam_index),
                       (11.2 + .25 * seam_index, 13.0 + .25 * seam_index)]
        smooth_event = sum(.5 * (np.tanh((t - a) / .14) - np.tanh((t - b) / .14)) for a, b in event_times)
        base_current = 340. + 3.5 * seam_index
        current = (base_current + 8 * np.sin(2 * np.pi * 47 * t + phase)
                   + (1 + 5 * smooth_event) * rng.normal(0, 1, len(t)) + 16 * smooth_event)
        voltage = 31.5 + .4 * np.sin(2 * np.pi * 31 * t) + .5 * smooth_event + rng.normal(0, .1, len(t))
        np.savez_compressed(folder / "signals.npz", t_s=t, current_a=current, voltage_v=voltage)
        ft = np.arange(1, int(duration * 8) + 1, dtype=float) / 8
        # Dense trajectory independently records the common clock and position.
        trajectory_t = np.arange(int(duration * 100) + 1, dtype=float) / 100
        # Include frame anchors explicitly to avoid a synthetic sample-hold offset.
        trajectory_t = np.unique(np.r_[trajectory_t, ft])
        pd.DataFrame({"t_s": trajectory_t, "s_mm": trajectory_t * speed}).to_csv(folder / "trajectory.csv", index=False)
        frames = []
        yy, xx = np.mgrid[:64, :64]
        for k, anchor in enumerate(ft):
            event_strength = sum(.5 * (np.tanh((anchor - a) / .22) - np.tanh((anchor - b) / .22)) for a, b in event_times)
            width = .29 + .035 * np.sin(.8 * anchor + phase) + .065 * event_strength
            length = .48 + .03 * np.sin(.6 * anchor + phase) + .05 * event_strength
            cx = 32 + 1.4 * np.sin(.5 * anchor)
            cy = 32 + .5 * np.cos(.7 * anchor)
            field = np.exp(-((xx - cx) / (width * 32)) ** 2 - ((yy - cy) / (length * 32)) ** 2)
            noise = rng.normal(0, 2.2, (64, 64))
            base = np.clip(18 + 175 * field + noise, 0, 255)
            # Visual event cue is deliberately artificial and disclosed.
            if event_strength > .3:
                base[:, 42:44] *= 1 - .55 * event_strength
            rgb = np.stack([base, base * .82, base * .58], axis=-1).astype(np.uint8)
            rel = f"{seam}/images/{k:05d}.png"
            Image.fromarray(rgb).save(root / rel)
            frames.append(dict(sample_id=f"{seam}_{k:05d}", t_s=anchor,
                available_t_s=anchor + .012, image_path=rel, width_rel=width,
                length_rel=length, area_rel=np.pi / 4 * width * length, geom_valid=1))
        pd.DataFrame(frames, columns=FRAME_COLUMNS).to_csv(folder / "frames.csv", index=False)
        events = [dict(event_id=f"{seam}_E{j + 1}", start_mm=a * speed,
                       end_mm=b * speed, class_name="Undercut", confidence=.95,
                       boundary_sigma_mm=.18) for j, (a, b) in enumerate(event_times)]
        pd.DataFrame(events, columns=EVENT_COLUMNS).to_csv(folder / "events.csv", index=False)
        rows.append(dict(seam_id=seam, segment_id="run1", split=split,
            signal_path=f"{seam}/signals.npz", frames_path=f"{seam}/frames.csv",
            trajectory_path=f"{seam}/trajectory.csv", events_path=f"{seam}/events.csv",
            material="SYNTHETIC_NOT_A_MEASURED_MATERIAL", thickness_mm=thickness,
            view_offset_mm=-.65, position_sigma_mm=.15, inspection_start_mm=0.,
            inspection_end_mm=duration * speed, initial_power_w=base_current * 31.5, synthetic=True))
    pd.DataFrame(rows, columns=MANIFEST_COLUMNS).to_csv(root / "manifest.csv", index=False)
    notice = {
        "synthetic": True, "purpose": "software smoke tests only", "native_signal_hz": 2000,
        "image_hz": 8, "image_size_px": [64, 64], "seams": 9, "split_seams": [5, 2, 2],
        "duration_s": [16, 24], "target_events_per_seam": 2, "seed": seed,
        "warning": "Artificial correlations are built in. No real measurements, true defect mechanism, MBGN reproduction, or research performance claims."
    }
    (root / "SYNTHETIC_NOTICE.json").write_text(json.dumps(notice, ensure_ascii=False, indent=2), encoding="utf-8")
    return notice


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", "--out", dest="output", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    print(json.dumps(generate_demo(args.output, args.seed), indent=2))


if __name__ == "__main__":
    main()
