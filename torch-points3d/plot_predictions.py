#!/usr/bin/env python3
"""
Plot predicted vs observed from a DPCR-AGB predictions CSV.

Usage:
    python plot_predictions.py --pred outputs/.../eval/.../CAN_test_preds.csv \
                               --labels /path/to/NFI_data.csv \
                               --target VOLMB
    python plot_predictions.py --pred CAN_test_preds.csv --labels labels.csv --target VOLMB --out pred_obs.png
"""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error


def load_data(pred_csv, labels_csv_or_gpkg, target):
    pred_df = pd.read_csv(pred_csv, index_col="label_idx")

    # Load ground truth — support CSV or GPKG
    p = Path(labels_csv_or_gpkg)
    if p.suffix in [".gpkg", ".geojson", ".shp"]:
        import geopandas as gpd
        label_df = gpd.read_file(labels_csv_or_gpkg)
    else:
        label_df = pd.read_csv(labels_csv_or_gpkg)

    label_df.index = label_df.index  # keep original integer index

    # Join on index (label_idx in pred maps to row index in label file)
    merged = pred_df.join(label_df[[target]].rename(columns={target: f"{target}_obs"}), how="inner")
    merged = merged.dropna(subset=[target, f"{target}_obs"])
    return merged


def compute_metrics(obs, pred):
    r2   = r2_score(obs, pred)
    mae  = mean_absolute_error(obs, pred)
    rmse = np.sqrt(mean_squared_error(obs, pred))
    bias = np.mean(pred - obs)
    return r2, mae, rmse, bias


def plot(merged, target, out_path):
    obs  = merged[f"{target}_obs"].values
    pred = merged[target].values

    r2, mae, rmse, bias = compute_metrics(obs, pred)

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.scatter(obs, pred, alpha=0.3, s=10, color="steelblue", label=f"n={len(obs)}")

    # 1:1 line
    lim = [min(obs.min(), pred.min()) * 0.95, max(obs.max(), pred.max()) * 1.05]
    ax.plot(lim, lim, "k--", linewidth=1, label="1:1 line")

    # regression line
    m, b = np.polyfit(obs, pred, 1)
    x_fit = np.array(lim)
    ax.plot(x_fit, m * x_fit + b, "r-", linewidth=1.5, label=f"Fit (slope={m:.2f})")

    stats_txt = f"R²={r2:.3f}  RMSE={rmse:.1f}  MAE={mae:.1f}  Bias={bias:.1f}"
    ax.set_title(f"Predicted vs Observed — {target}\n{stats_txt}", fontsize=11)
    ax.set_xlabel(f"Observed {target}")
    ax.set_ylabel(f"Predicted {target}")
    ax.set_xlim(lim); ax.set_ylim(lim)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    print(f"Saved plot to: {out_path}")
    print(f"\nMetrics for {target}:")
    print(f"  R²   = {r2:.4f}")
    print(f"  RMSE = {rmse:.2f}")
    print(f"  MAE  = {mae:.2f}")
    print(f"  Bias = {bias:.2f}")
    print(f"  n    = {len(obs)}")

    # Save merged table too
    table_path = out_path.with_suffix(".csv")
    merged[[f"{target}_obs", target]].rename(columns={target: f"{target}_pred"}).to_csv(table_path)
    print(f"Saved obs/pred table to: {table_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pred",   required=True, help="Path to *_test_preds.csv from eval.py")
    parser.add_argument("--labels", required=True, help="Original label CSV or GPKG file")
    parser.add_argument("--target", default="VOLMB", help="Target variable name (default: VOLMB)")
    parser.add_argument("--out",    default=None,   help="Output PNG path")
    args = parser.parse_args()

    pred_path = Path(args.pred)
    out_path  = Path(args.out) if args.out else pred_path.parent / f"pred_obs_{args.target}.png"

    merged = load_data(args.pred, args.labels, args.target)
    plot(merged, args.target, out_path)
