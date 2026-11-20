#!/usr/bin/env python3
"""Create standalone diagnostic figures from a completed reference run."""
from pathlib import Path
import argparse
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", required=True)
    args = p.parse_args()
    root = Path(args.run)
    df = pd.read_csv(root / "predictions_test.csv")
    events = pd.read_csv(root / "events_test.csv")
    metrics = json.loads((root / "metrics_test.json").read_text(encoding="utf-8"))
    choice = json.loads((root / "threshold_selection.json").read_text(encoding="utf-8"))
    seam = df.seam_id.iloc[0]
    part = df[df.seam_id == seam].sort_values("s_mm")
    synthetic = metrics.get("evidence_status") == "SYNTHETIC_PIPELINE_ONLY"
    title = "SYNTHETIC PIPELINE TEST - NOT WELDING EXPERIMENTAL EVIDENCE" if synthetic else "Held-out reference-model predictions"
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True, layout="constrained")
    axes[0].plot(part.s_mm, part.p_defect, color="#176B87", label="Predicted defect probability")
    axes[0].axhline(choice["threshold"], color="#BD582C", ls="--", label="Threshold fixed on validation")
    for j, e in enumerate(events[events.seam_id == seam].itertuples()):
        for ax in axes:
            ax.axvspan(e.start_mm, e.end_mm, color="#DFA949", alpha=.22,
                       label="Ground-truth interval" if j == 0 and ax is axes[0] else None)
    axes[0].set(ylabel="Probability", ylim=(-.03, 1.03), title=f"Seam {seam}")
    axes[0].legend(loc="upper right", fontsize=8)
    axes[1].step(part.s_mm, part.y_soft, where="mid", color="#63836D", label="Soft training target")
    axes[1].scatter(part.s_mm, part.y_hard, s=5, color="#434D57", label="Hard spatial label")
    axes[1].set(xlabel="Weld coordinate (mm)", ylabel="Spatial label", ylim=(-.05, 1.05))
    axes[1].legend(loc="upper right", fontsize=8)
    fig.suptitle(title, fontsize=11, fontweight="bold")
    fig.savefig(root / "prediction_diagnostic.png", dpi=180)
    fig.savefig(root / "prediction_diagnostic.pdf")
    plt.close(fig)
    history_path = root / "training_history.csv"
    if history_path.exists():
        hist = pd.read_csv(history_path)
        fig, ax = plt.subplots(figsize=(7, 4), layout="constrained")
        ax.plot(hist.epoch, hist.classification_loss, marker="o", label="Training BCE")
        ax.plot(hist.epoch, hist.val_classification_loss, marker="o", label="Validation BCE")
        ax.set(xlabel="Epoch", ylabel="Loss", title=title)
        ax.legend()
        fig.savefig(root / "training_diagnostic.png", dpi=180)
        plt.close(fig)
    print(root / "prediction_diagnostic.png")


if __name__ == "__main__":
    main()
