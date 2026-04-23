# YOLO Cube Detector Example

Run the YOLO OBB cube detector from `movensys_manipulator_perception`. The node subscribes to the hand RealSense camera, runs inference, and broadcasts a TF frame per detected cube (`yolo_cube_{green,yellow,blue,red}`) relative to `camera_hand_color_optical_frame`.

## 1. Build the package
```
mros colcon build --packages-select movensys_manipulator_perception --symlink-install
```

## 2. Launch the hand camera
```
mros ros2 launch movensys_manipulator_perception camera_hand.launch.py
```
Publishes `/camera_hand/realsense2_camera/color/image_raw` and `/camera_hand/realsense2_camera/color/camera_info`.

## 3. Launch the YOLO detector
In a second terminal:
```
mros ros2 launch movensys_manipulator_perception yolo_cube_detector.launch.py
```
Uses defaults from `config/yolo_cube_detector.yaml` and weights `models/cubes_obb.pt`.

### Override the model
```
mros ros2 launch movensys_manipulator_perception yolo_cube_detector.launch.py \
        model_path:=/path/to/cubes_obb_openvino_model
```

### Override the inference device
`device` is a node parameter (`cpu | cuda | AUTO | intel:cpu | intel:gpu | intel:npu`).
```
mros ros2 launch movensys_manipulator_perception yolo_cube_detector.launch.py \
        --ros-args -p device:=intel:gpu
```

## 4. Verify
### View published TF frames
```
mros ros2 run tf2_ros tf2_echo camera_hand_color_optical_frame yolo_cube_red
```

### View the debug image overlay
```
mros ros2 run rqt_image_view rqt_image_view /yolo_cube_detector/debug_image
```

### List detections via TF tree
```
mros ros2 run tf2_tools view_frames
```

## Tuning
Edit `config/yolo_cube_detector.yaml` (or override via `--ros-args -p <name>:=<value>`):

| Parameter | Meaning |
| --- | --- |
| `confidence_threshold` | Minimum detection confidence (0–1) |
| `cube_height` | Top-surface height of the cube in world frame (m) |
| `cam_z_world`, `cam_x_world`, `cam_y_world` | Camera position in world frame at the scan pose (m) |
| `cam_orientation` | Camera optical-frame orientation in world, `[x, y, z, w]` |
| `publish_debug_image` | Publish annotated overlay on `~/debug_image` |
| `image_topic`, `camera_info_topic`, `camera_frame` | Input topics and TF parent frame |

## Class mapping
`0: green_cube  1: yellow_cube  2: blue_cube  3: red_cube`
