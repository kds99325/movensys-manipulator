# models

Trained model assets used by the YOLO cube detector in this package.

## Contents

- `cubes_obb.pt` — Ultralytics YOLO OBB weights (4-class cubes: green, yellow, blue, red).
- `cubes_obb_openvino_model/` — (optional) OpenVINO export of the same model for Intel NPU/GPU inference.

Files are installed to `share/movensys_manipulator_perception/models/`. The
`yolo_cube_detector.launch.py` launcher resolves `cubes_obb.pt` from that path
by default; override with the `model_path` launch argument to point at an
OpenVINO export or a different `.pt` file.

Training scripts live in the reference program at
`reference_program/movensys_intel_manipulator/sample_yolo_programe/scripts/train_model.py`.
