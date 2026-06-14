# DPCR-AGB Training & Evaluation Workflow

Full recipe: train → evaluate → get predictions → plots.

---

## 0. Setup (run once per terminal session)

```bash
cd /home/nibio/DPCR-AGB/torch-points3d
export PATH=/usr/local/cuda-11.8/bin:/home/nibio/anaconda3/bin:$PATH
export WANDB_MODE=offline
PYTHON=/home/nibio/.local/share/mamba/envs/pts/bin/python
```

---

## 1. Train the model

### MinkowskiNet (SENet50) — recommended

```bash
$PYTHON -u train.py \
  task=instance models=instance/minkowski_baseline model_name=SENet50 \
  data=instance/CAN/reg data.transform_type=sparse_xy \
  training=nfi/minkowski lr_scheduler=cosineawr \
  update_lr_scheduler_on=on_num_batch \
  training.epochs=100 training.batch_size=16 \
  training.wandb.log=False
```

### KPConv — alternative method

```bash
$PYTHON -u train.py \
  task=instance models=instance/kpconv model_name=KPConv \
  data=instance/CAN/reg data.transform_type=fixed_xy \
  training=nfi/kpconv lr_scheduler=cosineawr \
  update_lr_scheduler_on=on_num_batch \
  training.epochs=100 training.batch_size=16 \
  training.wandb.log=False
```

### Norwegian dataset — replace `CAN` with `NOR`

```bash
$PYTHON -u train.py \
  task=instance models=instance/minkowski_baseline model_name=SENet50 \
  data=instance/NOR/reg data.transform_type=sparse_xy \
  training=nfi/minkowski lr_scheduler=cosineawr \
  update_lr_scheduler_on=on_num_batch \
  training.epochs=100 training.batch_size=16 \
  training.wandb.log=False
```

**Training output** is saved to: `outputs/YYYY-MM-DD/HH-MM-SS/SENet50.pt`

Find the latest run:
```bash
ls -t outputs/$(date +%Y-%m-%d)/
```

---

## 2. Plot loss curves

```bash
CKPT=outputs/YYYY-MM-DD/HH-MM-SS   # <-- set this!

$PYTHON plot_training.py --log $CKPT/train.log
# → saves: $CKPT/loss_curves.png
```

---

## 3. Evaluate on test set (get predictions CSV)

### MinkowskiNet / CAN dataset

```bash
CKPT=outputs/YYYY-MM-DD/HH-MM-SS   # <-- set this!

$PYTHON eval.py \
  model_name=SENet50 \
  checkpoint_dir=$(pwd)/$CKPT \
  weight_name="latest" \
  batch_size=16 num_workers=4 \
  eval_stages='["test"]' \
  data=instance/CAN/reg \
  data.transform_type=sparse_xy_eval \
  task=instance \
  visualization.activate=True \
  "visualization.format=[csv]"
```

### KPConv / CAN dataset

```bash
$PYTHON eval.py \
  model_name=KPConv \
  checkpoint_dir=$(pwd)/$CKPT \
  weight_name="latest" \
  batch_size=16 num_workers=4 \
  eval_stages='["test"]' \
  data=instance/CAN/reg \
  data.transform_type=fixed_xy_eval \
  task=instance \
  visualization.activate=True \
  "visualization.format=[csv]"
```

### Norwegian dataset — change `CAN` → `NOR`, `sparse_xy_eval` stays the same

```bash
$PYTHON eval.py \
  model_name=SENet50 \
  checkpoint_dir=$(pwd)/$CKPT \
  weight_name="latest" \
  batch_size=16 num_workers=4 \
  eval_stages='["test"]' \
  data=instance/NOR/reg \
  data.transform_type=sparse_xy_eval \
  task=instance \
  visualization.activate=True \
  "visualization.format=[csv]"
```

**Predictions CSV** is saved to: `$CKPT/eval/<timestamp>/CAN_test_preds.csv`

---

## 4. Plot predicted vs observed

```bash
# Find the predictions CSV
PRED=$(find $CKPT/eval -name "*_test_preds.csv" | tail -1)

# CAN dataset
$PYTHON plot_predictions.py \
  --pred $PRED \
  --labels /home/nibio/SR16_DL/NO_prep_forCanada/NFI_data_withsplit_forCanada.csv \
  --target VOLMB

# NOR dataset
$PYTHON plot_predictions.py \
  --pred $PRED \
  --labels /home/nibio/SR16_DL/NO_test/shifted_laz/../SR16_ref_2024_forDLtrain_all_setasidesamp_nodupl_realcoord_2025Febr_shift_final.gpkg \
  --target VOLMB
# → saves: pred_obs_VOLMB.png  and  pred_obs_VOLMB.csv  next to the predictions CSV
```

---

## 5. Full one-liner workflow (after training)

```bash
CKPT=outputs/YYYY-MM-DD/HH-MM-SS   # <-- set this!

# Loss curves
$PYTHON plot_training.py --log $CKPT/train.log

# Eval
$PYTHON eval.py model_name=SENet50 checkpoint_dir=$(pwd)/$CKPT weight_name="latest" \
  batch_size=16 num_workers=4 eval_stages='["test"]' \
  data=instance/CAN/reg data.transform_type=sparse_xy_eval task=instance \
  visualization.activate=True "visualization.format=[csv]"

# Pred vs observed plot
PRED=$(find $CKPT/eval -name "*.csv" | tail -1)
$PYTHON plot_predictions.py --pred $PRED \
  --labels /home/nibio/SR16_DL/NO_prep_forCanada/NFI_data_withsplit_forCanada.csv \
  --target VOLMB
```

---

## Summary of outputs

| File | Description |
|------|-------------|
| `$CKPT/train.log` | Full training log with per-epoch losses |
| `$CKPT/SENet50.pt` | Saved model checkpoint |
| `$CKPT/loss_curves.png` | Val/test loss across epochs |
| `$CKPT/eval/.../CAN_test_preds.csv` | Raw predictions (label_idx, VOLMB_pred) |
| `$CKPT/eval/.../pred_obs_VOLMB.png` | Predicted vs observed scatter plot |
| `$CKPT/eval/.../pred_obs_VOLMB.csv` | Observed + predicted table ready for further analysis |

---

## Dataset configs available

| Dataset | `data=` | Labels file |
|---------|---------|-------------|
| Canada/Norway-prep | `instance/CAN/reg` | `NFI_data_withsplit_forCanada.csv` |
| Norwegian NFI | `instance/NOR/reg` | `SR16_ref_...gpkg` |
| Danish NFI | `instance/NFI/reg` | `nfi_preprocessed_data.zip` |
