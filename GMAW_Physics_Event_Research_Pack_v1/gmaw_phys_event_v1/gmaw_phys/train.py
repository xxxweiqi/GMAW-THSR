"""Training and validation-only model/threshold selection.

This module intentionally never selects a checkpoint, threshold, geometry offset,
or hyperparameter using test labels. The reference CNN is not original MBGN.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.metadata
import json
import platform
import random
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
import yaml
from torch.utils.data import DataLoader


def read_config(path):
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def json_safe(value):
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, np.ndarray):
        return json_safe(value.tolist())
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (float, np.floating)):
        return float(value) if np.isfinite(value) else None
    if isinstance(value, Path):
        return str(value)
    return value


def write_json(path, value):
    Path(path).write_text(json.dumps(json_safe(value), indent=2, ensure_ascii=False,
                                    allow_nan=False), encoding="utf-8")


def set_seed(seed, threads=2):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.set_num_threads(max(1, int(threads)))
    torch.use_deterministic_algorithms(True, warn_only=True)
    torch.backends.cudnn.benchmark = False


def choose_device(requested):
    if requested == "auto":
        requested = "cuda" if torch.cuda.is_available() else "cpu"
    if str(requested).startswith("cuda") and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable; use train.device: cpu or auto.")
    return torch.device(requested)


def _to_device(batch, device):
    return {k: v.to(device) if isinstance(v, torch.Tensor) else v
            for k, v in batch.items()}


def _make_dataset(root, cfg, split):
    from . import data
    if hasattr(data, "build_dataset"):
        return data.build_dataset(root, cfg, split)
    return data.WeldDataset(root, cfg, split)


def _bce(logits, batch, pos_weight):
    weight = batch["label_weight"].float()
    loss = F.binary_cross_entropy_with_logits(
        logits.reshape(-1), batch["y_soft"].float().reshape(-1),
        pos_weight=pos_weight, reduction="none")
    return (loss * weight).sum() / weight.sum().clamp_min(1.0)


def _aux_loss(output, batch):
    mask = batch["geom_mask"].float()
    target = torch.nan_to_num(batch["geom_target"].float(), nan=0.0)
    err = F.smooth_l1_loss(output["geom_pred"], target, reduction="none")
    return (err * mask).sum() / mask.sum().clamp_min(1.0)


@torch.no_grad()
def predict_loader(model, loader, dataset, device):
    model.eval()
    rows = []
    for raw_batch in loader:
        batch = _to_device(raw_batch, device)
        output = model(batch)
        probability = torch.sigmoid(output["logits"].reshape(-1)).cpu().numpy()
        index = raw_batch["index"].cpu().numpy().reshape(-1)
        geom = output["geom_pred"].cpu().numpy()
        gt = raw_batch["geom_target"].cpu().numpy()
        mask = raw_batch["geom_mask"].cpu().numpy()
        for j, original_index in enumerate(index):
            row = dict(dataset.records[int(original_index)])
            row["p_defect"] = float(probability[j])
            for q, name in enumerate(("width", "length", "area")):
                row[f"geom_{name}_pred"] = float(geom[j, q])
                row[f"geom_{name}_target"] = float(gt[j, q]) if mask[j, q] else np.nan
            rows.append(row)
    return pd.DataFrame(rows)


@torch.no_grad()
def validation_loss(model, loader, device, pos_weight):
    # Select checkpoints by classification loss only, identical across ablations.
    model.eval()
    numerator, denominator = 0.0, 0.0
    for raw_batch in loader:
        batch = _to_device(raw_batch, device)
        output = model(batch)
        loss = F.binary_cross_entropy_with_logits(
            output["logits"].reshape(-1), batch["y_soft"].float().reshape(-1),
            pos_weight=pos_weight, reduction="none")
        weight = batch["label_weight"].float()
        numerator += float((loss * weight).sum().cpu())
        denominator += float(weight.sum().cpu())
    if denominator == 0:
        raise ValueError("Validation has no labeled support. Resolve coverage/labels first.")
    return numerator / denominator


def _fingerprints(dataset_root):
    root = Path(dataset_root)
    records = []
    # Metadata checksum plus file size; large native signals are not redundantly rehashed.
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        row = {"path": str(path.relative_to(root)), "bytes": path.stat().st_size}
        if path.suffix.lower() in {".csv", ".yaml", ".json"}:
            row["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        records.append(row)
    return records


def _versions():
    result = {"python": platform.python_version(), "platform": platform.platform()}
    for name in ("torch", "numpy", "pandas", "scipy", "scikit-learn", "Pillow", "PyYAML"):
        try:
            result[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            result[name] = "unavailable"
    return result


def run_training(dataset_root, config, output_dir):
    from .data import validate_dataset
    from .models import build_model
    from .metrics import evaluate_predictions, select_threshold

    cfg = copy.deepcopy(config)
    out = Path(output_dir)
    if out.exists() and any(out.iterdir()):
        raise FileExistsError(f"Output directory is not empty: {out}. Use a new run name.")
    out.mkdir(parents=True, exist_ok=True)
    start_time = time.perf_counter()
    qc = validate_dataset(dataset_root)
    write_json(out / "data_validation.json", qc)
    if not qc.get("ok", False):
        raise ValueError("Dataset validation failed; see data_validation.json.")
    set_seed(cfg["seed"], cfg["train"].get("torch_threads", 2))
    device = choose_device(cfg["train"].get("device", "auto"))
    (out / "resolved_config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False,
                                                             allow_unicode=True), encoding="utf-8")
    datasets = {s: _make_dataset(dataset_root, cfg, s) for s in ("train", "val", "test")}
    for split, ds in datasets.items():
        if len(ds) == 0:
            raise ValueError(f"No eligible {split} samples after causal history/coverage checks.")
        write_json(out / f"{split}_data_summary.json", ds.summary)
    train_labels = np.array([r["y_hard"] for r in datasets["train"].records])
    train_weights = np.array([r["label_weight"] for r in datasets["train"].records])
    eligible = train_weights > 0
    negative = int(np.sum((train_labels == 0) & eligible))
    positive = int(np.sum((train_labels == 1) & eligible))
    if min(negative, positive) == 0:
        raise ValueError("Training requires both Normal and Undercut on independent eligible data.")
    pos_weight_value = min(10.0, max(0.1, negative / positive))
    pos_weight = torch.tensor(pos_weight_value, dtype=torch.float32, device=device)
    generator = torch.Generator().manual_seed(int(cfg["seed"]))
    loaders = {s: DataLoader(ds, batch_size=int(cfg["train"]["batch_size"]),
                            shuffle=s == "train", num_workers=int(cfg["train"].get("num_workers", 0)),
                            generator=generator if s == "train" else None, drop_last=False)
               for s, ds in datasets.items()}
    model = build_model(cfg).to(device)
    optimizer = torch.optim.AdamW(model.parameters(),
                                 lr=float(cfg["train"]["learning_rate"]),
                                 weight_decay=float(cfg["train"].get("weight_decay", 0.0)))
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    best_loss, best_epoch, bad_epochs = float("inf"), -1, 0
    history = []
    aux_weight = float(cfg["train"].get("aux_weight", 0.2)) if cfg["model"].get("use_aux", False) else 0.0
    for epoch in range(int(cfg["train"]["epochs"])):
        model.train()
        losses = []
        for raw_batch in loaders["train"]:
            batch = _to_device(raw_batch, device)
            optimizer.zero_grad(set_to_none=True)
            output = model(batch)
            classification = _bce(output["logits"], batch, pos_weight)
            geometry = _aux_loss(output, batch)
            loss = classification + aux_weight * geometry
            if not torch.isfinite(loss):
                raise FloatingPointError("Non-finite training loss; no model reported as successful.")
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
            optimizer.step()
            losses.append((float(classification.detach().cpu()), float(geometry.detach().cpu())))
        val_loss = validation_loss(model, loaders["val"], device, pos_weight)
        history.append({"epoch": epoch + 1, "classification_loss": np.mean([x[0] for x in losses]),
                        "geometry_loss": np.mean([x[1] for x in losses]), "val_classification_loss": val_loss})
        print(f"epoch={epoch+1} train_bce={history[-1]['classification_loss']:.5f} val_bce={val_loss:.5f}", flush=True)
        if val_loss < best_loss - 1e-7:
            best_loss, best_epoch, bad_epochs = val_loss, epoch + 1, 0
            torch.save({"state_dict": model.state_dict(), "config": cfg,
                        "best_epoch": best_epoch, "reference_not_original_mbgn": True}, out / "model.pt")
        else:
            bad_epochs += 1
        if bad_epochs >= int(cfg["train"].get("patience", 15)):
            break
    pd.DataFrame(history).to_csv(out / "training_history.csv", index=False)
    checkpoint = torch.load(out / "model.pt", map_location=device, weights_only=True)
    model.load_state_dict(checkpoint["state_dict"])
    val_predictions = predict_loader(model, loaders["val"], datasets["val"], device)
    val_predictions["split"] = "val"
    eval_options = {k: cfg["evaluation"][k] for k in
                    ("iou_threshold", "merge_gap_mm", "min_length_mm")}
    selected = select_threshold(val_predictions, datasets["val"].events, **eval_options)
    selected["evaluation_parameters"] = dict(eval_options)
    write_json(out / "threshold_selection.json", selected)
    threshold = float(selected["threshold"])
    val_predictions.to_csv(out / "predictions_val.csv", index=False)
    datasets["val"].events.to_csv(out / "events_val.csv", index=False)
    # Test is accessed for scoring only after checkpoint and threshold are frozen.
    test_predictions = predict_loader(model, loaders["test"], datasets["test"], device)
    test_predictions["split"] = "test"
    test_predictions.to_csv(out / "predictions_test.csv", index=False)
    datasets["test"].events.to_csv(out / "events_test.csv", index=False)
    metrics = evaluate_predictions(test_predictions, datasets["test"].events,
                                   threshold=threshold, **eval_options)
    geometry_mae = {}
    for name in ("width", "length", "area"):
        true = test_predictions[f"geom_{name}_target"]
        pred = test_predictions[f"geom_{name}_pred"]
        geometry_mae[name] = float((true - pred).abs().mean()) if true.notna().any() else None
    metrics["geometry_mae_roi_fraction"] = geometry_mae if aux_weight else None
    metrics["evidence_status"] = "SYNTHETIC_PIPELINE_ONLY" if bool(qc.get("synthetic", False)) else "USER_DATA_REFERENCE_RUN"
    metrics["reference_not_original_mbgn"] = True
    metrics["timing_note"] = "Event delays exclude preprocessing, model runtime and robot actuation."
    write_json(out / "metrics_test.json", metrics)
    run_info = {"created_utc": datetime.now(timezone.utc).isoformat(), "seed": cfg["seed"],
                "model": cfg["model"], "device": str(device), "trainable_parameters": trainable,
                "best_epoch": best_epoch, "best_val_classification_loss": best_loss,
                "training_pos_weight": pos_weight_value, "selected_threshold": threshold,
                "samples": {s: len(ds) for s, ds in datasets.items()},
                "elapsed_s": time.perf_counter() - start_time, "versions": _versions(),
                "data_root": str(Path(dataset_root).resolve()),
                "dataset_fingerprint": _fingerprints(dataset_root),
                "evidence_status": metrics["evidence_status"],
                "scope": "Trainable reference implementation; not an original MBGN reproduction."}
    write_json(out / "run_info.json", run_info)
    print(f"Finished: {out}; status={metrics['evidence_status']}", flush=True)
    return {"output_dir": str(out), "metrics": metrics, "run_info": run_info}


def predict_checkpoint(dataset_root, checkpoint_path, split="test", device="cpu"):
    from .models import build_model
    ckpt = torch.load(checkpoint_path, map_location=device, weights_only=True)
    cfg = ckpt["config"]
    set_seed(cfg["seed"], cfg["train"].get("torch_threads", 2))
    ds = _make_dataset(dataset_root, cfg, split)
    model = build_model(cfg).to(device)
    model.load_state_dict(ckpt["state_dict"])
    loader = DataLoader(ds, batch_size=cfg["train"]["batch_size"], shuffle=False)
    return predict_loader(model, loader, ds, torch.device(device)), ds
