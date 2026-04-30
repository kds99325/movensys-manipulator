# YOLO OBB Detectors — Run Guide

Two ROS 2 nodes in this directory perform YOLO oriented-bounding-box (OBB)
detection from the hand camera and broadcast a TF frame per detected class:

- [yolo_cube_detector.py](yolo_cube_detector.py) — colored cubes
  (`green`, `yellow`, `blue`, `red`)
- [yolo_dice_detector.py](yolo_dice_detector.py) — dice faces
  (`one` … `six`)

Both share the same architecture: subscribe to a RealSense color image +
`CameraInfo`, run inference with `ultralytics`, project the OBB centroid
onto a horizontal plane at the object's known top-surface height, and
publish `<camera_frame> -> yolo_<cube|dice>_<class>` on `/tf`.

---

## 1. Prerequisites

### Python dependencies

Install once into the Python environment used by ROS 2:

```bash
pip install -r ../launch/requirements.txt
```

Key packages: `ultralytics`, `opencv-python`, `numpy<2`, `openvino`
(see [launch/requirements.txt](../launch/requirements.txt)).

### ROS 2 dependencies

Resolved via `package.xml`:

```bash
cd ~/movensys_ws
rosdep install --from-paths src --ignore-src -r -y
```

### Build the package

```bash
cd ~/movensys_ws
colcon build --packages-select movensys_manipulator_perception --symlink-install
source install/setup.bash
```

### Camera stream

The detectors subscribe to the hand camera by default. Bring it up first:

```bash
ros2 launch movensys_manipulator_perception camera_hand.launch.py
```

This publishes `/image_hand/rgb`, `/image_hand/depth`, and
`/image_hand/camera_info`. The detectors only consume `rgb` and
`camera_info`; depth is unused. The detector will log
`Image received but camera_info not yet received — skipping` until
both topics are alive.

### Model weights

Default weights are shipped in the package's `share/models/` directory:

- `cubes_obb.pt`
- `dice_obb.pt`

The launch files resolve them automatically. Override with the
`model_path` launch arg (a `.pt` file or an OpenVINO export directory).

---

## 2. Run via launch files (recommended)

```bash
ros2 launch movensys_manipulator_perception yolo_cube_detector.launch.py
ros2 launch movensys_manipulator_perception yolo_dice_detector.launch.py
```

This loads defaults from
[config/yolo_cube_detector.yaml](../config/yolo_cube_detector.yaml) /
[config/yolo_dice_detector.yaml](../config/yolo_dice_detector.yaml).

### Common overrides

```bash
# Use a custom checkpoint
ros2 launch movensys_manipulator_perception yolo_cube_detector.launch.py \
    model_path:=/abs/path/to/my_cubes.pt

# Use simulation time (e.g. when replaying a bag with --clock)
ros2 launch movensys_manipulator_perception yolo_dice_detector.launch.py \
    use_sim_time:=true

# Custom params file
ros2 launch movensys_manipulator_perception yolo_cube_detector.launch.py \
    params_file:=/abs/path/to/cube_params.yaml
```

---

## 3. Run the script directly

Useful when iterating on a single param without editing the YAML:

```bash
ros2 run movensys_manipulator_perception yolo_cube_detector.py \
    --ros-args \
    -p model_path:=/abs/path/to/cubes_obb.pt \
    -p confidence_threshold:=0.4 \
    -p device:=cuda \
    -p publish_debug_image:=true
```

```bash
ros2 run movensys_manipulator_perception yolo_dice_detector.py \
    --ros-args \
    -p model_path:=/abs/path/to/dice_obb.pt \
    -p dice_height:=0.05
```

Equivalent invocation pattern with a YAML file:

```bash
ros2 run movensys_manipulator_perception yolo_cube_detector.py \
    --ros-args --params-file install/movensys_manipulator_perception/share/movensys_manipulator_perception/config/yolo_cube_detector.yaml \
    -p model_path:=install/movensys_manipulator_perception/share/movensys_manipulator_perception/models/cubes_obb.pt
```

---

## 4. Parameters

| Parameter | Default | Notes |
|---|---|---|
| `model_path` | (set by launch) | `.pt` file or OpenVINO export dir |
| `confidence_threshold` | `0.5` | Per-detection conf cutoff |
| `cube_height` / `dice_height` | `0.05` | Top-surface height in world Z (m) |
| `cam_z_world` | `0.45` | Camera height above floor at scan pose (m) |
| `cam_x_world`, `cam_y_world` | `0.0` | Camera XY in world at scan pose (m) |
| `cam_orientation` | `[0, 1, 0, 0]` | Optical frame quat in world (xyzw); default = scan RPY (π, 0, π) |
| `publish_debug_image` | `true` | Enable `~/debug_image` annotated stream |
| `device` | `"cpu"` | `cpu` \| `cuda` \| `AUTO` \| `intel:cpu` \| `intel:gpu` \| `intel:npu` |
| `image_topic` | `/image_hand/rgb` | Input color image |
| `camera_info_topic` | `/image_hand/camera_info` | Intrinsics |
| `camera_frame` | `camera_hand_color_optical_frame` | Parent frame for published TFs |

---

## 5. Topics & TF

**Subscribed**

- `image_topic` (`sensor_msgs/Image`, `bgr8`)
- `camera_info_topic` (`sensor_msgs/CameraInfo`)

**Published**

- `/tf` (`tf2_msgs/TFMessage`) — one transform per detected class:
  - cube: `yolo_cube_green`, `yolo_cube_yellow`, `yolo_cube_blue`, `yolo_cube_red`
  - dice: `yolo_dice_one` … `yolo_dice_six`
- `~/debug_image` (`sensor_msgs/Image`) when `publish_debug_image=true`

Only the highest-confidence detection per class is broadcast each frame.

---

## 6. Quick verification

After launching, in separate terminals:

```bash
# Confirm TFs are flowing
ros2 run tf2_ros tf2_echo camera_hand_color_optical_frame yolo_cube_red

# View the annotated debug image
ros2 run rqt_image_view rqt_image_view /yolo_cube_detector/debug_image
ros2 run rqt_image_view rqt_image_view /yolo_dice_detector/debug_image
```

Console logs show pixel centroid, confidence, yaw, and the resolved
camera/world coordinates for every accepted detection.

---

## 7. Troubleshooting

| Symptom | Likely cause |
|---|---|
| `model_path parameter is empty` | Launch arg not set and YAML doesn't define it — pass `model_path:=...` |
| `Model path does not exist` | The path resolves outside the install share — use an absolute path |
| `ultralytics is not installed` | Run `pip install -r ../launch/requirements.txt` |
| `Image received but camera_info not yet received` | Camera driver not running, or QoS mismatch — verify with `ros2 topic hz <camera_info_topic>` |
| `Intersection behind camera` / `Ray parallel to floor plane` | Camera pose params (`cam_z_world`, `cam_orientation`) don't match the actual scan pose |
| All TFs land at wrong XY | Wrong `cam_orientation` quat — must be the optical frame's pose **in world** at the scan pose |
