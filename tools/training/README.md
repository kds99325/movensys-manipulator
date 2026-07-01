# tools/training

Off-line, dev-time tooling for training the YOLO OBB models consumed by
`movensys_manipulator_perception` (cubes, dice, etc.). Nothing here is
built or installed by colcon — it is invoked by hand on a workstation
with a GPU.

The trained `best.pt` produced by this workflow is copied into
[`movensys_manipulator_perception/models/`](../../movensys_manipulator_perception/models/)
under the canonical name (`cubes_obb.pt`, `dice_obb.pt`, …) where the
runtime detector launchers pick it up.

## Layout convention

Datasets and training outputs live **outside the repo** so they are not
committed. The recommended on-disk layout is rooted at `$HOME/ml_assets`
(or any directory you point the script at via `--dataset` / `--output`):

```
$HOME/ml_assets/
  weights/                       # ULTRALYTICS_HOME — base weights cache
    yolo26n-obb.pt
    yolo26s-obb.pt
  datasets/
    cubes_obb/                   # raw labelled data (--dataset)
      images/   00001.jpg ...
      labels/   00001.txt ...    # YOLO OBB format
      classes.txt                # one class name per line, in id order
    dice_obb/
      images/  ...
      labels/  ...
      classes.txt
  obb_assets/models/             # training outputs (--output)
    cubes_obb/
      best.pt                    # ← copy this into the perception package
      last.pt
      dataset/                   # auto-generated train/val/test split
      runs/train/                # ultralytics run artifacts (curves, logs)
      best_openvino_model/       # only if --export_openvino
    dice_obb/
      ...
```

The repo's `.gitignore` already excludes `datasets/`, `obb_assets/`,
`runs/`, and stray `yolo*.pt` base weights, so accidental drops inside
this directory will not be committed.

## Install

```bash
python3 -m pip install -r requirements.txt
# torch + torchvision are pulled in transitively by ultralytics; install a
# CUDA-matched build separately if you need GPU training:
#   pip install --index-url https://download.pytorch.org/whl/cu124 torch torchvision
```

Set `ULTRALYTICS_HOME` so base weights are cached in a known location
(otherwise the script defaults it to `$HOME/ml_assets/weights`):

```bash
export ULTRALYTICS_HOME=$HOME/ml_assets/weights
```

## Bake the runtime border mask into the dataset (recommended)

Both runtime detectors paint a fixed border mask on every frame before
inference (`mask_*_fraction` / `mask_color` in their ROS YAML). For
training to match inference, run the same mask over the dataset before
training:

```bash
python3 apply_runtime_mask.py \
  --source $HOME/ml_assets/datasets/dice_funnel_v1 \
  --detector_config ../../movensys_manipulator_perception/config/dobot_cr3a/yolo_dice_detector.yaml \
  --dest   $HOME/ml_assets/datasets/dice_funnel_v1_masked
```

Then point `--dataset` below at the `_masked` dir. Boxes whose centroid
falls in the masked region are dropped; images with no surviving boxes
are skipped. `classes.txt` is copied through.

If you change the detector's mask values, re-run this step against the
same raw source — no recapture needed.

## Train

Cubes:

```bash
python3 train_model.py \
  --dataset $HOME/ml_assets/datasets/cubes_obb \
  --output  $HOME/ml_assets/obb_assets/models/cubes_obb \
  --model   yolo26s-obb.pt \
  --epochs  50 \
  --batch   16 \
  --device  0
```

Dice (same script, different dataset + output):

```bash
python3 train_model.py \
  --dataset $HOME/ml_assets/datasets/dice_obb \
  --output  $HOME/ml_assets/obb_assets/models/dice_obb \
  --model   yolo26s-obb.pt \
  --epochs  80 \
  --batch   16 \
  --device  0
```

The script splits the raw `images/`+`labels/` 70/20/10 with `--seed 42`,
writes a YOLO `dataset.yaml`, runs ultralytics training, and copies
`best.pt`/`last.pt` to `--output`. Pass `--skip_split` to reuse a split
already on disk, `--resume <ckpt.pt>` to continue training, and
`--export_openvino` to additionally export an OpenVINO IR for Intel
NPU/iGPU inference.

## Ship the trained model

Once you are happy with `best.pt`:

```bash
cp $HOME/ml_assets/obb_assets/models/cubes_obb/best.pt \
   ../../movensys_manipulator_perception/models/cubes_obb.pt
```

(Or `dice_obb.pt`.) That file is what `yolo_cube_detector.launch.py`
and `yolo_dice_detector.launch.py` resolve at runtime via
`get_package_share_directory('movensys_manipulator_perception') / 'models'`.

To ship the OpenVINO export instead, copy the whole `*_openvino_model/`
directory into `models/` and pass its path via the `model_path` launch
argument.
