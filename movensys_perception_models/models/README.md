# movensys_perception_models

Holds trained model assets consumed by `movensys_perception`.

## Expected contents

- `cubes_obb.pt` — Ultralytics YOLO OBB weights (4-class cubes: green, yellow, blue, red).
- `cubes_obb_openvino_model/` — (optional) OpenVINO export of the same model for Intel NPU/GPU inference.

Drop the trained weights directly into this folder before building. They are
installed to `share/movensys_perception_models/models/` and can be resolved at
launch time via:

```bash
ros2 launch movensys_perception yolo_cube_detector.launch.py \
    model_path:=$(ros2 pkg prefix movensys_perception_models)/share/movensys_perception_models/models/cubes_obb.pt
```

Training scripts live in the reference program at
`reference_program/movensys_intel_manipulator/sample_yolo_programe/scripts/train_model.py`.
