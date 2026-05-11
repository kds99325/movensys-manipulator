#!/usr/bin/env python3
"""
apply_runtime_mask.py — bake the detector's runtime border mask into a
training dataset.

The runtime detectors (`yolo_dice_detector.py`, `yolo_cube_detector.py`)
apply a fixed border mask to every incoming frame before YOLO inference,
configured via ``mask_*_fraction`` / ``mask_color`` in their ROS YAML.
For supervised learning to be valid, the training set must match that
distribution. This script:

1. Loads the four mask fractions and the fill color from a detector YAML.
2. For each image in ``--source/images/``, paints the four borders with
   ``mask_color`` and writes the result to ``--dest/images/``.
3. For each YOLO OBB label in ``--source/labels/``, drops boxes whose
   centroid falls inside the masked region; writes the survivors to
   ``--dest/labels/``. Images with no surviving boxes are skipped entirely.
4. Copies ``classes.txt`` if present.

Usage:
    python3 apply_runtime_mask.py \\
        --source $HOME/ml_assets/datasets/dice_funnel_v1 \\
        --detector_config ../../movensys_manipulator_perception/config/dobot_cr3a/yolo_dice_detector.yaml \\
        --dest   $HOME/ml_assets/datasets/dice_funnel_v1_masked
"""

import argparse
import shutil
import sys
from pathlib import Path

import cv2
import numpy as np
import yaml


IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}


def load_mask_params(config_path: Path) -> dict:
    """Pull mask_*_fraction and mask_color out of a detector ROS YAML."""
    with open(config_path) as f:
        data = yaml.safe_load(f) or {}

    # Expected: { <node_name>: { ros__parameters: { mask_*: ..., ... } } }
    params = {}
    for node_value in data.values():
        if isinstance(node_value, dict) and 'ros__parameters' in node_value:
            params = node_value['ros__parameters']
            break

    out = {
        'left':   float(params.get('mask_left_fraction', 0.0)),
        'right':  float(params.get('mask_right_fraction', 0.0)),
        'top':    float(params.get('mask_top_fraction', 0.0)),
        'bottom': float(params.get('mask_bottom_fraction', 0.0)),
        'color':  tuple(int(c) for c in params.get('mask_color', [0, 0, 0])),
    }
    if any(not 0.0 <= out[k] < 1.0 for k in ('left', 'right', 'top', 'bottom')):
        sys.exit(f'mask fractions in {config_path} out of range [0,1)')
    if out['left'] + out['right'] >= 1.0 or out['top'] + out['bottom'] >= 1.0:
        sys.exit(f'mask fractions in {config_path} cover the entire image')
    if len(out['color']) != 3:
        sys.exit(f'mask_color in {config_path} must be a 3-element BGR list')
    return out


def apply_mask(image: np.ndarray, mask: dict) -> None:
    """Same border paint as the runtime detector. In-place."""
    h, w = image.shape[:2]
    nl = int(round(w * mask['left']))
    nr = int(round(w * mask['right']))
    nt = int(round(h * mask['top']))
    nb = int(round(h * mask['bottom']))
    color = mask['color']
    if nl: image[:, :nl]     = color
    if nr: image[:, w - nr:] = color
    if nt: image[:nt, :]     = color
    if nb: image[h - nb:, :] = color


def filter_obb_labels(label_path: Path, mask: dict) -> list[str]:
    """
    Keep only OBB rows whose centroid is outside the masked border.

    YOLO OBB format: ``cls x1 y1 x2 y2 x3 y3 x4 y4`` with all coords
    normalized to [0, 1]. The kept region is the inner rectangle:
        [mask.left, 1 - mask.right] × [mask.top, 1 - mask.bottom]
    """
    if not label_path.exists():
        return []

    keep = []
    x_lo, x_hi = mask['left'], 1.0 - mask['right']
    y_lo, y_hi = mask['top'],  1.0 - mask['bottom']

    for line in label_path.read_text().splitlines():
        parts = line.split()
        if len(parts) < 9:
            continue
        xs = [float(parts[i]) for i in (1, 3, 5, 7)]
        ys = [float(parts[i]) for i in (2, 4, 6, 8)]
        cx = sum(xs) / 4.0
        cy = sum(ys) / 4.0
        if x_lo <= cx <= x_hi and y_lo <= cy <= y_hi:
            keep.append(line)
    return keep


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Bake the runtime border mask into a YOLO OBB dataset.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--source', type=str, required=True,
                        help='Source dataset dir with images/ and labels/.')
    parser.add_argument('--detector_config', type=str, required=True,
                        help='Detector ROS YAML to read mask_*_fraction from.')
    parser.add_argument('--dest', type=str, required=True,
                        help='Output dataset dir (images/ and labels/ created).')
    args = parser.parse_args(argv)

    source = Path(args.source).expanduser().resolve()
    dest = Path(args.dest).expanduser().resolve()
    cfg = Path(args.detector_config).expanduser().resolve()

    src_images = source / 'images'
    src_labels = source / 'labels'
    if not src_images.is_dir() or not src_labels.is_dir():
        sys.exit(f'Source must contain images/ and labels/: {source}')
    if not cfg.is_file():
        sys.exit(f'Detector config not found: {cfg}')

    mask = load_mask_params(cfg)
    print(f'Mask: L={mask["left"]:.2f} R={mask["right"]:.2f} '
          f'T={mask["top"]:.2f} B={mask["bottom"]:.2f}  color={mask["color"]}')

    dst_images = dest / 'images'
    dst_labels = dest / 'labels'
    dst_images.mkdir(parents=True, exist_ok=True)
    dst_labels.mkdir(parents=True, exist_ok=True)

    n_total = n_kept = n_skipped_no_labels = n_dropped_boxes = 0

    for img_path in sorted(src_images.iterdir()):
        if img_path.suffix.lower() not in IMAGE_EXTS:
            continue
        n_total += 1

        label_path = src_labels / f'{img_path.stem}.txt'
        original_count = sum(1 for line in label_path.read_text().splitlines()
                             if line.strip()) if label_path.exists() else 0
        kept = filter_obb_labels(label_path, mask)
        n_dropped_boxes += original_count - len(kept)

        if not kept:
            n_skipped_no_labels += 1
            continue

        image = cv2.imread(str(img_path), cv2.IMREAD_COLOR)
        if image is None:
            print(f'WARN: could not read {img_path} — skipping')
            continue
        apply_mask(image, mask)

        out_img = dst_images / img_path.name
        if not cv2.imwrite(str(out_img), image):
            print(f'WARN: failed to write {out_img}')
            continue

        (dst_labels / f'{img_path.stem}.txt').write_text('\n'.join(kept) + '\n')
        n_kept += 1

    classes_src = source / 'classes.txt'
    if classes_src.is_file():
        shutil.copy2(classes_src, dest / 'classes.txt')
        print(f'Copied {classes_src.name} → {dest / "classes.txt"}')

    print(f'\nProcessed {n_total} images')
    print(f'  kept            : {n_kept}')
    print(f'  skipped (no labels survived mask): {n_skipped_no_labels}')
    print(f'  boxes dropped   : {n_dropped_boxes}')
    print(f'\nMasked dataset written to {dest}')


if __name__ == '__main__':
    main()
