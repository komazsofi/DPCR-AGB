# DPCR-AGB Installation Recipe

Tested on: Ubuntu 20.04, NVIDIA GPU, CUDA 11.8, Python 3.8

---

## Prerequisites

```bash
# Check CUDA is available
ls /usr/local/cuda*          # should find cuda-11.x
nvidia-smi                   # should show GPU

# Install system dependencies
sudo apt update
sudo apt install -y gcc-8 g++-8 libopenblas-dev git curl
```

---

## 1. Install micromamba

```bash
curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xvj bin/micromamba
sudo mv bin/micromamba /usr/local/bin/micromamba
micromamba --version
```

---

## 2. Clone the repo

```bash
git clone https://github.com/komazsofi/DPCR-AGB.git
cd DPCR-AGB
```

---

## 3. Create the conda environment

```bash
cd torch-points3d
micromamba env create -f env.yml
# This installs Python 3.8, PyTorch 2.0.1+CUDA, and most dependencies.
# Note: lazrs will fail during pip install — that is expected and OK.
```

Activate the environment (use this prefix for all commands below):

```bash
export PATH=/usr/local/cuda-11.8/bin:/home/$USER/anaconda3/bin:$PATH
export WANDB_MODE=offline
PYTHON=/home/$USER/.local/share/mamba/envs/pts/bin/python
```

---

## 4. Install additional pip packages

```bash
$PYTHON -m pip install laszip pyproj==3.3.1
```

---

## 5. Install MinkowskiEngine

```bash
# Clone the compatible fork
git clone https://github.com/StefOe/MinkowskiEngine /tmp/MinkowskiEngine
cd /tmp/MinkowskiEngine

# Build (uses openblas from the conda env)
MAX_JOBS=4 $PYTHON setup.py install --blas=openblas --force_cuda --verbose
cd -
```

This takes ~10–20 minutes. Verify with:

```bash
$PYTHON -c "import MinkowskiEngine; print(MinkowskiEngine.__version__)"
# Expected: 0.5.4
```

---

## 6. Compile KPConv wrappers

```bash
cd /home/$USER/DPCR-AGB/torch-points3d
$PYTHON torch_points3d/modules/KPConv/cpp_wrappers/cpp_subsampling/setup.py build_ext --inplace
$PYTHON torch_points3d/modules/KPConv/cpp_wrappers/cpp_neighbors/setup.py build_ext --inplace
```

---

## 7. Verify training works (Danish NFI test data)

Download the sample dataset from the release and place it under `data/`:

```bash
cd /home/$USER/DPCR-AGB/torch-points3d
# Download nfi_preprocessed_data.zip (499 MB) and unzip to data/
# Then run a quick 2-epoch test:
$PYTHON -u train.py \
  task=instance models=instance/minkowski_baseline model_name=SENet50 \
  data=instance/NFI/reg data.transform_type=sparse_xy \
  training=nfi/minkowski lr_scheduler=cosineawr \
  update_lr_scheduler_on=on_num_batch \
  training.epochs=2 training.batch_size=4 \
  training.wandb.log=False
```

---

## 8. Run on Norwegian NFI data

### Prepare data

```bash
mkdir -p /home/$USER/DPCR-AGB/torch-points3d/data/norway/raw
ln -s /path/to/your/shifted_laz /home/$USER/DPCR-AGB/torch-points3d/data/norway/raw/shifted_laz
ln -s /path/to/your/nfi.gpkg     /home/$USER/DPCR-AGB/torch-points3d/data/norway/raw/norway_nfi.gpkg
```

The GPKG must have columns: `FLATEID` (plot ID matching LAZ filenames), `VOLMB`, `split` (train/val/test), `geometry` (EPSG:25833).

### Train

```bash
cd /home/$USER/DPCR-AGB/torch-points3d
$PYTHON -u train.py \
  task=instance models=instance/minkowski_baseline model_name=SENet50 \
  data=instance/NOR/reg data.transform_type=sparse_xy \
  training=nfi/minkowski lr_scheduler=cosineawr \
  update_lr_scheduler_on=on_num_batch \
  training.epochs=50 training.batch_size=4 \
  training.wandb.log=False
# Checkpoint saved to: outputs/YYYY-MM-DD/HH-MM-SS/SENet50.pt
```

### Evaluate and get predictions CSV

```bash
CKPT=/home/$USER/DPCR-AGB/torch-points3d/outputs/YYYY-MM-DD/HH-MM-SS

$PYTHON eval.py \
  model_name=SENet50 \
  checkpoint_dir=$CKPT \
  weight_name="latest" \
  batch_size=16 num_workers=4 \
  eval_stages='["test"]' \
  data=instance/NOR/reg \
  data.transform_type=sparse_xy_eval \
  task=instance \
  visualization.activate=True \
  "visualization.format=[csv]"
# Output: $CKPT/eval/<timestamp>/NOR_test_preds.csv
# Columns: label_idx, VOLMB (predicted)
```

---

## Known fixes applied in this fork

| File | Fix |
|------|-----|
| `torch_points3d/datasets/instance/las_dataset.py` | Use try/except for LAZ backend selection (laspy 2.x changed API) |
| `torch_points3d/models/instance/kpconv.py` | Added `has_mol_targets` and `has_cls_targets` attributes |
| `torch_points3d/modules/KPConv/cpp_wrappers/*/setup.py` | Replaced deprecated `numpy.distutils` with `numpy.get_include()` |
| `conf/data/instance/NFI/reg.yaml` | Added `total_BMag_ha` second target |
| `conf/data/instance/NOR/` | New Norwegian dataset config files |
