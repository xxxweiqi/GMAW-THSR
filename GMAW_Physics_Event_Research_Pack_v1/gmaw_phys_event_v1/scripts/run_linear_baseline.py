#!/usr/bin/env python3
"""Fixed causal heat filters + logistic classifier, a simple physical baseline.

No CNN, no trainable thermal dynamics, no original MBGN reproduction.
The scaler and classifier fit training seams only. Probabilities are evaluated
at a validation-selected threshold. Soft targets use weighted duplicate rows.
"""
from pathlib import Path
import argparse
import sys
import time
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
import yaml
from scipy.special import expit
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from gmaw_phys.data import validate_dataset
from gmaw_phys.train import read_config, _make_dataset, write_json, _versions
from gmaw_phys.metrics import evaluate_predictions, select_threshold


def features(ds):
    x, soft, weight, geometry_targets = [], [], [], []
    for i in range(len(ds)):
        item = ds[i]
        image = item["image"][-1].numpy()
        # Current optical summary, not future geometry labels.
        rgb_mean = image.mean(axis=(1, 2))
        rgb_std = image.std(axis=(1, 2))
        signal = item["signal"][-1].numpy()
        row = np.r_[item["thermal"][-1].numpy(), item["power"][-1].numpy(),
                    item["condition"].numpy(), signal.mean(axis=1), signal.std(axis=1),
                    rgb_mean, rgb_std]
        x.append(row)
        soft.append(float(item["y_soft"]))
        weight.append(float(item["label_weight"]))
        # Kept in a separate return value for matching offline evaluation schemas.
        # These future targets are NEVER appended to row/x or passed to fit/predict.
        geometry = item["geom_target"].numpy()
        mask = item["geom_mask"].numpy()
        geometry_targets.append([float(geometry[j]) if mask[j] else np.nan
                                 for j in range(3)])
    return (np.asarray(x), np.asarray(soft), np.asarray(weight),
            np.asarray(geometry_targets, dtype=float))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data", required=True)
    p.add_argument("--config", default="configs/research.yaml")
    p.add_argument("--out", required=True)
    args = p.parse_args()
    cfg = read_config(args.config)
    out = Path(args.out)
    if out.exists() and any(out.iterdir()):
        raise FileExistsError("Choose a new, empty output directory.")
    out.mkdir(parents=True, exist_ok=True)
    qc = validate_dataset(args.data)
    write_json(out / "data_validation.json", qc)
    if not qc["ok"]:
        raise ValueError("Dataset validation failed")
    (out / "resolved_config.yaml").write_text(
        yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True), encoding="utf-8")
    start = time.perf_counter()
    sets = {s: _make_dataset(args.data, cfg, s) for s in ("train", "val", "test")}
    for split, ds in sets.items():
        write_json(out / f"{split}_data_summary.json", ds.summary)
    matrices = {s: features(ds) for s, ds in sets.items()}
    x, q, weight, _offline_geometry = matrices["train"]
    good = weight > 0
    if not good.any() or not np.any(q[good] > .5) or not np.any(q[good] < .5):
        raise ValueError("Training requires both classes.")
    scaler = StandardScaler().fit(x[good])
    scaled = scaler.transform(x[good])
    x_aug = np.concatenate((scaled, scaled))
    y_aug = np.r_[np.zeros(good.sum(), dtype=int), np.ones(good.sum(), dtype=int)]
    w_aug = np.r_[weight[good] * (1 - q[good]), weight[good] * q[good]]
    model = LogisticRegression(C=1.0, max_iter=500, random_state=cfg["seed"])
    model.fit(x_aug, y_aug, sample_weight=w_aug)
    preds = {}
    for split in ("val", "test"):
        ds = sets[split]
        df = pd.DataFrame(ds.records)
        df["p_defect"] = model.predict_proba(scaler.transform(matrices[split][0]))[:, 1]
        for j, name in enumerate(("width", "length", "area")):
            df[f"geom_{name}_target"] = matrices[split][3][:, j]
        df["split"] = split
        preds[split] = df
    options = {k: cfg["evaluation"][k] for k in ("iou_threshold", "merge_gap_mm", "min_length_mm")}
    choice = select_threshold(preds["val"], sets["val"].events, **options)
    choice["evaluation_parameters"] = dict(options)
    write_json(out / "threshold_selection.json", choice)
    for split in ("val", "test"):
        preds[split].to_csv(out / f"predictions_{split}.csv", index=False)
        sets[split].events.to_csv(out / f"events_{split}.csv", index=False)
    metrics = evaluate_predictions(preds["test"], sets["test"].events,
                                   threshold=choice["threshold"], **options)
    metrics["evidence_status"] = "SYNTHETIC_PIPELINE_ONLY" if qc.get("synthetic") else "USER_DATA_REFERENCE_RUN"
    write_json(out / "metrics_test.json", metrics)
    # JSON coefficients avoid shipping an executable pickle model.
    coeffs = {"mean": scaler.mean_, "scale": scaler.scale_, "coefficient": model.coef_[0],
              "intercept": model.intercept_[0], "formula": "sigmoid(((x-mean)/scale) @ coefficient + intercept)"}
    write_json(out / "linear_model.json", coeffs)
    recovered = expit(scaler.transform(matrices["test"][0]) @ model.coef_[0] + model.intercept_[0])
    assert np.allclose(recovered, preds["test"].p_defect, atol=1e-10)
    write_json(out / "run_info.json", {"model": "fixed_thermal_logistic", "config": cfg,
               "versions": _versions(), "samples": {s: len(ds) for s, ds in sets.items()},
               "elapsed_s": time.perf_counter()-start, "evidence_status": metrics["evidence_status"],
               "scope": "Simple causal thermal baseline, not ARX and not original MBGN"})
    print(out)


if __name__ == "__main__":
    main()
