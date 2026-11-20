#!/usr/bin/env python3
"""Check template schemas only; empty templates are not a valid real dataset."""
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import yaml
from gmaw_phys.data import MANIFEST_COLUMNS, FRAME_COLUMNS, EVENT_COLUMNS


def main():
    base = ROOT / "templates"
    expected = {
        "data/manifest.csv": MANIFEST_COLUMNS,
        "data/frames.csv": FRAME_COLUMNS,
        "data/events.csv": EVENT_COLUMNS,
        "data/signals_native.csv": ["t_s", "current_a", "voltage_v"],
        "data/trajectory.csv": ["t_s", "s_mm"],
        "data/predictions.csv": ["sample_id", "seam_id", "segment_id", "s_mm", "cell_start_mm", "cell_end_mm", "t_frame_s", "t_decision_s", "y_hard", "y_soft", "label_weight", "boundary_uncertain", "synthetic", "split", "p_defect"],
        "data/evaluation_events.csv": ["seam_id", "segment_id", *EVENT_COLUMNS, "reference_t_s"],
    }
    checked = []
    for name, columns in expected.items():
        with (base / name).open(encoding="utf-8", newline="") as handle:
            rows = list(csv.reader(handle))
        if rows != [columns]:
            raise ValueError(f"Template must contain exactly the current header, no fabricated data: {name}")
        checked.append(name)
    annotation = base / "annotation_review.csv"
    with annotation.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    if len(rows) != 1 or not {"event_id", "reviewer_a", "reviewer_b", "final_class", "boundary_sigma_mm"}.issubset(rows[0]):
        raise ValueError("Annotation review template is malformed")
    checked.append(annotation.name)
    for name in ["metadata_record.yaml", "calibration_record.yaml", "experiment_log.yaml"]:
        obj = yaml.safe_load((base / name).read_text(encoding="utf-8"))
        if not isinstance(obj, dict) or obj.get("template_version") != 1 or obj.get("record_status") != "unfilled_template":
            raise ValueError(f"Unfilled record template marker missing: {name}")
        checked.append(name)
    print(json.dumps({"ok": True, "checked_files": checked, "scope": "schema_only_not_real_data_validation"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
