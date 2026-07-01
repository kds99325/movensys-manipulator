# models

Trained model assets used by the YOLO detectors in this package.

## Contents

- `cubes_obb.pt` — Ultralytics YOLO OBB weights (4-class cubes: green, yellow, blue, red).
- `cubes_obb_openvino_model/` — (optional) OpenVINO export of the cube model for Intel NPU/GPU inference.
- `dice_obb.pt` — Ultralytics YOLO OBB weights (6-class dice faces: One, Two, Three, Four, Five, Six).
- `dice_obb_openvino_model/` — (optional) OpenVINO export of the dice model for Intel NPU/GPU inference.

Files are installed to `share/movensys_manipulator_perception/models/`. The
`yolo_cube_detector.launch.py` and `yolo_dice_detector.launch.py` launchers
resolve `cubes_obb.pt` / `dice_obb.pt` from that path by default; override
with the `model_path` launch argument to point at an OpenVINO export or a
different `.pt` file.

Training scripts live at [`tools/training/`](../../../tools/training/)
at the repo root. See that directory's `README.md` for dataset layout,
how to run `train_model.py`, and how to drop the resulting `best.pt`
back into this folder.
