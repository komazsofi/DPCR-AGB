#!/usr/bin/env python3
"""
Parse DPCR-AGB train.log and plot loss curves across epochs.

Usage:
    python plot_training.py --log outputs/2026-06-12/18-09-22-844903/train.log
    python plot_training.py --log outputs/2026-06-12/18-09-22-844903/train.log --out loss_curves.png
"""
import re
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def parse_log(log_path):
    epoch_pattern    = re.compile(r"EPOCH (\d+) / \d+")
    train_pattern    = re.compile(r"train_loss_reg=([0-9.]+)")
    val_pattern      = re.compile(r"val_loss_reg = ([0-9.eE+\-]+)")
    test_pattern     = re.compile(r"test_loss_reg = ([0-9.eE+\-]+)")

    records = []
    current_epoch = None
    train_losses  = []

    with open(log_path) as f:
        for line in f:
            em = epoch_pattern.search(line)
            if em:
                current_epoch = int(em.group(1))
                train_losses  = []

            # batch-level train loss (take last value per epoch)
            tm = train_pattern.search(line)
            if tm and current_epoch is not None:
                train_losses.append(float(tm.group(1)))

            vm = val_pattern.search(line)
            if vm and current_epoch is not None:
                train_mean = sum(train_losses) / len(train_losses) if train_losses else float("nan")
                records.append({
                    "epoch": current_epoch,
                    "train_loss": train_mean,
                    "val_loss": float(vm.group(1)),
                    "test_loss": float("nan"),
                })

            ttm = test_pattern.search(line)
            if ttm and records and records[-1]["epoch"] == current_epoch:
                records[-1]["test_loss"] = float(ttm.group(1))

    return pd.DataFrame(records)


def plot(df, out_path):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["epoch"], df["train_loss"], label="Train loss", marker="o", markersize=3)
    ax.plot(df["epoch"], df["val_loss"],   label="Val loss",   marker="s", markersize=3)
    if not df["test_loss"].isna().all():
        ax.plot(df["epoch"], df["test_loss"], label="Test loss", marker="^", markersize=3, linestyle="--")

    # mark best val epoch
    best_epoch = df.loc[df["val_loss"].idxmin(), "epoch"]
    best_val   = df["val_loss"].min()
    ax.axvline(best_epoch, color="gray", linestyle=":", alpha=0.7)
    ax.annotate(f"Best val\nEpoch {best_epoch}\n{best_val:.4f}",
                xy=(best_epoch, best_val), xytext=(best_epoch + 1, best_val * 1.3),
                fontsize=8, arrowprops=dict(arrowstyle="->", color="gray"))

    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss (normalized)")
    ax.set_title("Training loss curves")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    print(f"Saved plot to: {out_path}")

    # print summary table
    print("\nEpoch summary:")
    print(df.to_string(index=False, float_format="{:.4f}".format))
    print(f"\nBest val loss: {best_val:.4f} at epoch {best_epoch}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", required=True, help="Path to train.log")
    parser.add_argument("--out", default=None, help="Output PNG path (default: next to log)")
    args = parser.parse_args()

    log_path = Path(args.log)
    out_path = Path(args.out) if args.out else log_path.parent / "loss_curves.png"

    df = parse_log(log_path)
    plot(df, out_path)
