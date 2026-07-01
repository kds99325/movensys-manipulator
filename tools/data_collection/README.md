# tools/data_collection

Dev-time helper for collecting raw images for OBB datasets (cubes, dice,
funnel scenes, …). Not built or installed by colcon — invoked by hand.

## What `capture_dataset.py` does

- Subscribes to a ROS 2 image topic.
- Saves one frame every `--interval` seconds as `NNNNN.jpg` (zero-padded
  to 5 digits, JPEG).
- Resumes numbering: scans the output directory for existing
  `NNNNN.jpg` files and starts at `max + 1`. Gaps are not filled.
- Exits after `--count` saves.

If no frame has arrived since startup (camera not publishing yet), the
script logs a warning and skips the tick **without** consuming the
slot — the next tick tries again.

## Prerequisites

Run inside the docker container, or on a host with ROS 2 Jazzy +
`cv_bridge` + `python3-opencv` installed.

The camera must be publishing on `--topic` (default `/image_hand/rgb`).
Start it via:

```bash
ros2 launch movensys_manipulator_perception camera_hand.launch.py
```

## Usage

Default: 50 frames at 10 s spacing into
`tools/data_collection/output/<name>/images/`:

```bash
python3 capture_dataset.py --name dice_funnel_v1
```

Custom interval / count / topic:

```bash
python3 capture_dataset.py \
  --name     dice_funnel_v1 \
  --topic    /image_hand/rgb \
  --interval 5 \
  --count    100
```

Explicit output path (overrides `--name`):

```bash
python3 capture_dataset.py \
  --output $HOME/ml_assets/datasets/dice_obb/images \
  --count  50
```

Stop early with Ctrl-C — already-written files are kept and the next
run resumes after the highest existing number.

## Where the output lives

The default `tools/data_collection/output/` directory is gitignored.
Move (or symlink) the dataset into the layout expected by
[`tools/training/`](../training/README.md) when you're ready to train:

```bash
mkdir -p $HOME/ml_assets/datasets/dice_funnel_v1
mv tools/data_collection/output/dice_funnel_v1/images \
   $HOME/ml_assets/datasets/dice_funnel_v1/
# then label them, drop classes.txt, and run train_model.py
```
