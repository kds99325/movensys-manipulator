# Model Variants

YOLO OBB weights. `cubes_obb.pt` / `dice_obb.pt` are the active files;
others are rollback backups. Override via the `model_path` launch arg.

## Cubes — 4 classes: green, yellow, blue, red

| File | Status | Background | MD5 |
|---|---|---|---|
| `cubes_obb.pt` | **Active** | Monoplyboard | `a468496e…` |
| `cubes_obb.pt.monoplyboard_background` | Backup | Monoplyboard | `a468496e…` (≡ active) |
| `cubes_obb.pt.silver_background` | Backup | Silver | `815f057f…` |

## Dice — 6 classes: One–Six

| File | Status | Scene | MD5 |
|---|---|---|---|
| `dice_obb.pt` | **Active** | With 3D tray | `2315e8e1…` |
| `dice_obb.pt_with_3D_Tray` | Backup | With 3D tray | `2315e8e1…` (≡ active) |
| `dice_obb.pt.without_3D_Tray` | Backup | No tray | `456e3e4f…` |

OpenVINO exports (`*_openvino_model/`) are not checked in; produce via
`tools/training/` and select with `device: intel:npu|intel:gpu`.
