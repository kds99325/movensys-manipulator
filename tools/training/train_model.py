#!/usr/bin/env python3
"""
train_model.py
===============

Script for training a YOLO Oriented Bounding Box (OBB) model using the Ultralytics
YOLO framework, with optional export to OpenVINO format for optimized inference
on Intel hardware (CPU, GPU, NPU).

Directory Convention:
---------------------
All OBB assets are organized under `obb_assets/`:
    obb_assets/
        datasets/       <- Input datasets (from collect_dataset.py)
            cubes_obb/
                images/
                labels/
                classes.txt
        models/         <- Trained models output here
            cubes_obb/
                best.pt
                last.pt
                best_openvino_model/
                dataset/
                runs/

Ultralytics weights are stored separately (set via environment variable):
    export ULTRALYTICS_HOME=$HOME/ml_assets/weights

Features:
---------
1. Scans a dataset directory containing `images/` and `labels/` subfolders, and
   optionally a `classes.txt` or `dataset.yaml` for class names.
2. Automatically matches image-label pairs and warns about missing labels.
3. Splits the dataset into train, validation, and test sets with configurable
   ratios and random seed for reproducibility.
4. Creates a YOLO-compatible dataset structure, copying images and labels into
   the appropriate split folders, and generates a `dataset.yaml` file for training.
5. Reads class names from `classes.txt`, `dataset.yaml`, or uses default cube
   class names if none are found.
6. Trains a YOLO OBB model with customizable parameters (model, epochs, batch size,
   image size, device, etc.) and saves the best and last model weights.
7. Supports resuming training from a checkpoint and skipping the dataset split
   if already performed.
8. Optionally exports the trained model to OpenVINO IR format for deployment on
   Intel hardware with accelerated inference.

Usage:
------
    python3 train_model.py --dataset <dataset_dir> --output <output_dir> \
        [--epochs 100] [--model yolo26n-obb.pt] [--imgsz 640] [--batch 16] \
        [--device 0] [--export_openvino]

Examples:
---------
    # Train only (using obb_assets convention)
    python3 scripts/train_model.py \
        --dataset obb_assets/datasets/cubes_obb \
        --output obb_assets/models/cubes_obb

    # Train and export to OpenVINO
    python3 scripts/train_model.py \
        --dataset obb_assets/datasets/cubes_obb \
        --output obb_assets/models/cubes_obb \
        --epochs 20 --export_openvino

Expected Dataset Structure:
---------------------------
    dataset/
        images/
            000000.jpg
            000001.jpg
            ...
        labels/
            000000.txt
            000001.txt
            ...
        classes.txt (optional)

Arguments:
----------
--dataset         Path to the dataset directory containing images/ and labels/
--output          Output directory for the trained model and processed dataset
--model           Base YOLO OBB model to use (default: yolo26n-obb.pt)
--epochs          Number of training epochs (default: 100)
--imgsz           Image size for training (default: 640)
--batch           Batch size (default: 16)
--device          Device to use for training (e.g., '', '0', 'cpu')
--patience        Early stopping patience (default: 50)
--workers         Number of data loading workers (default: 8)
--train_ratio     Fraction of data for training (default: 0.7)
--val_ratio       Fraction of data for validation (default: 0.2)
--test_ratio      Fraction of data for testing (default: 0.1)
--seed            Random seed for reproducibility (default: 42)
--skip_split      Skip dataset splitting if already done
--resume          Resume training from a checkpoint
--export_openvino Export trained model to OpenVINO format after training

Outputs:
--------
- YOLO dataset structure in <output_dir>/dataset/
- dataset.yaml for YOLO training
- Trained model weights: best.pt, last.pt in <output_dir>
- OpenVINO model (if --export_openvino): <output_dir>/best_openvino_model/

OpenVINO Inference:
-------------------
After exporting, load and run inference with the OpenVINO model:

    from ultralytics import YOLO
    model = YOLO("<output_dir>/best_openvino_model/")
    results = model("image.jpg", device="intel:gpu")  # or intel:cpu, intel:npu

"""

import os
import sys
import argparse
import shutil
import random
from pathlib import Path
from typing import List, Tuple
import yaml

if 'ULTRALYTICS_HOME' not in os.environ:
    os.environ['ULTRALYTICS_HOME'] = str(Path.home() / 'ml_assets' / 'weights')
    Path(os.environ['ULTRALYTICS_HOME']).mkdir(parents=True, exist_ok=True)


def get_image_label_pairs(dataset_dir: Path) -> List[Tuple[Path, Path]]:
    """
    Get matched pairs of images and labels from dataset directory.
    
    Returns list of (image_path, label_path) tuples.
    """
    images_dir = dataset_dir / 'images'
    labels_dir = dataset_dir / 'labels'
    
    if not images_dir.exists():
        raise FileNotFoundError(f'Images directory not found: {images_dir}')
    if not labels_dir.exists():
        raise FileNotFoundError(f'Labels directory not found: {labels_dir}')
    
    # Find all images
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    images = [f for f in images_dir.iterdir() if f.suffix.lower() in image_extensions]
    
    pairs = []
    for img_path in images:
        # Look for corresponding label file
        label_path = labels_dir / f'{img_path.stem}.txt'
        if label_path.exists():
            pairs.append((img_path, label_path))
        else:
            print(f'Warning: No label found for {img_path.name}, skipping')
    
    return pairs


def split_dataset(
    pairs: List[Tuple[Path, Path]], 
    train_ratio: float = 0.7,
    val_ratio: float = 0.2,
    test_ratio: float = 0.1,
    seed: int = 42
) -> Tuple[List, List, List]:
    """
    Split dataset into train/val/test sets.
    
    Args:
        pairs: List of (image_path, label_path) tuples
        train_ratio: Fraction for training (default 0.7)
        val_ratio: Fraction for validation (default 0.2) 
        test_ratio: Fraction for testing (default 0.1)
        seed: Random seed for reproducibility
        
    Returns:
        Tuple of (train_pairs, val_pairs, test_pairs)
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 0.001, \
        f'Ratios must sum to 1.0, got {train_ratio + val_ratio + test_ratio}'
    
    random.seed(seed)
    shuffled = pairs.copy()
    random.shuffle(shuffled)
    
    n = len(shuffled)
    train_end = int(n * train_ratio)
    val_end = train_end + int(n * val_ratio)
    
    train_pairs = shuffled[:train_end]
    val_pairs = shuffled[train_end:val_end]
    test_pairs = shuffled[val_end:]
    
    return train_pairs, val_pairs, test_pairs


def create_yolo_dataset_structure(
    output_dir: Path,
    train_pairs: List[Tuple[Path, Path]],
    val_pairs: List[Tuple[Path, Path]],
    test_pairs: List[Tuple[Path, Path]],
    class_names: List[str]
) -> Path:
    """
    Create YOLO dataset directory structure and copy files.
    
    Structure:
        output_dir/
            dataset/
                train/
                    images/
                    labels/
                val/
                    images/
                    labels/
                test/
                    images/
                    labels/
                dataset.yaml
    
    Returns path to dataset.yaml
    """
    dataset_dir = output_dir / 'dataset'
    
    # Create directory structure
    for split in ['train', 'val', 'test']:
        (dataset_dir / split / 'images').mkdir(parents=True, exist_ok=True)
        (dataset_dir / split / 'labels').mkdir(parents=True, exist_ok=True)
    
    # Copy files
    split_data = [
        ('train', train_pairs),
        ('val', val_pairs),
        ('test', test_pairs)
    ]
    
    for split_name, pairs in split_data:
        print(f'Copying {len(pairs)} samples to {split_name}...')
        for img_path, label_path in pairs:
            shutil.copy2(img_path, dataset_dir / split_name / 'images' / img_path.name)
            shutil.copy2(label_path, dataset_dir / split_name / 'labels' / label_path.name)
    
    # Create dataset.yaml
    yaml_content = {
        'path': str(dataset_dir.absolute()),
        'train': 'train/images',
        'val': 'val/images',
        'test': 'test/images',
        'names': {i: name for i, name in enumerate(class_names)}
    }
    
    yaml_path = dataset_dir / 'dataset.yaml'
    with open(yaml_path, 'w') as f:
        yaml.dump(yaml_content, f, default_flow_style=False, sort_keys=False)
    
    print(f'Created dataset.yaml at {yaml_path}')
    return yaml_path


def read_class_names(dataset_dir: Path) -> List[str]:
    """
    Read class names from classes.txt or dataset.yaml in the source dataset.
    """
    # Try classes.txt first
    classes_file = dataset_dir / 'classes.txt'
    if classes_file.exists():
        with open(classes_file, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    
    # Try dataset.yaml
    yaml_file = dataset_dir / 'dataset.yaml'
    if yaml_file.exists():
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
            if 'names' in data:
                names = data['names']
                if isinstance(names, dict):
                    return [names[i] for i in sorted(names.keys())]
                elif isinstance(names, list):
                    return names
    
    # Default class names
    print('Warning: No class names found, using default cube names')
    return ['red_cube', 'green_cube', 'blue_cube', 'yellow_cube']


def train_yolo_obb(
    yaml_path: Path,
    output_dir: Path,
    model_name: str = 'yolo26n-obb.pt',
    epochs: int = 100,
    imgsz: int = 640,
    batch: int = 16,
    device: str = '',
    patience: int = 50,
    workers: int = 8,
    project: str = None,
    name: str = 'train'
) -> Path:
    """
    Train YOLO OBB model.
    
    Args:
        yaml_path: Path to dataset.yaml
        output_dir: Output directory for trained model
        model_name: Base model to use (default: yolo26n-obb.pt)
        epochs: Number of training epochs
        imgsz: Image size for training
        batch: Batch size
        device: Device to use ('' for auto, '0' for GPU 0, 'cpu' for CPU)
        patience: Early stopping patience
        workers: Number of data loading workers
        project: Project name for runs
        name: Run name
        
    Returns:
        Path to best trained model weights
    """
    try:
        from ultralytics import YOLO
    except ImportError:
        print('Error: ultralytics package not installed.')
        print('Install with: pip install ultralytics')
        sys.exit(1)
    
    # Load base model
    print(f'\nLoading base model: {model_name}')
    model = YOLO(model_name)
    
    # Set up training arguments
    train_args = {
        'data': str(yaml_path),
        'epochs': epochs,
        'imgsz': imgsz,
        'batch': batch,
        'patience': patience,
        'workers': workers,
        'project': str(output_dir / 'runs') if project is None else project,
        'name': name,
        'exist_ok': True,
        'pretrained': True,
        'optimizer': 'auto',
        'verbose': True,
        'seed': 42,
        'close_mosaic': 10,  # Disable mosaic augmentation in last 10 epochs
        'amp': True,  # Automatic mixed precision
    }
    
    if device:
        train_args['device'] = device
    
    print(f'\nStarting training with:')
    print(f'  Dataset: {yaml_path}')
    print(f'  Epochs: {epochs}')
    print(f'  Image size: {imgsz}')
    print(f'  Batch size: {batch}')
    print(f'  Output: {output_dir}')
    
    # Train
    results = model.train(**train_args)
    
    # Copy best weights to output directory
    best_weights = Path(results.save_dir) / 'weights' / 'best.pt'
    output_weights = output_dir / 'best.pt'
    
    if best_weights.exists():
        shutil.copy2(best_weights, output_weights)
        print(f'\nBest model saved to: {output_weights}')
    
    # Also copy last weights
    last_weights = Path(results.save_dir) / 'weights' / 'last.pt'
    if last_weights.exists():
        shutil.copy2(last_weights, output_dir / 'last.pt')
    
    return output_weights


def export_to_openvino(model_path: Path, output_dir: Path) -> Path:
    """
    Export a trained YOLO model to OpenVINO IR format.
    
    The exported model can be used for optimized inference on Intel hardware
    including CPU, integrated/discrete GPU, and NPU accelerators.
    
    Args:
        model_path: Path to the trained PyTorch model (.pt file)
        output_dir: Directory to save the exported OpenVINO model
        
    Returns:
        Path to the exported OpenVINO model directory
        
    Example:
        After export, load and run inference:
            model = YOLO("best_openvino_model/")
            results = model("image.jpg", device="intel:gpu")
    """
    try:
        from ultralytics import YOLO
    except ImportError:
        print('Error: ultralytics package not installed.')
        print('Install with: pip install ultralytics')
        sys.exit(1)
    
    if not model_path.exists():
        print(f'Error: Model file not found: {model_path}')
        return None
    
    print(f'\nLoading model for export: {model_path}')
    model = YOLO(str(model_path))
    
    print('Exporting to OpenVINO format...')
    export_path = model.export(format='openvino')
    
    # Move exported model to output directory
    exported_dir = Path(export_path)
    target_dir = output_dir / f'{model_path.stem}_openvino_model'
    
    if exported_dir.exists() and exported_dir != target_dir:
        if target_dir.exists():
            shutil.rmtree(target_dir)
        shutil.move(str(exported_dir), str(target_dir))
        print(f'OpenVINO model saved to: {target_dir}')
    else:
        target_dir = exported_dir
        print(f'OpenVINO model exported to: {target_dir}')
    
    return target_dir


def main():
    parser = argparse.ArgumentParser(
        description='Train YOLO OBB model on custom dataset',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Required arguments
    parser.add_argument('--dataset', type=str, required=True,
                        help='Path to dataset directory with images/ and labels/')
    parser.add_argument('--output', type=str, required=True,
                        help='Output directory for trained model')
    
    # Training parameters
    parser.add_argument('--model', type=str, default='yolo26s-obb.pt',
                        help='Base model to use (e.g., yolo26n-obb.pt, yolo26s-obb.pt)')
    parser.add_argument('--epochs', type=int, default=100,
                        help='Number of training epochs')
    parser.add_argument('--imgsz', type=int, default=640,
                        help='Image size for training')
    parser.add_argument('--batch', type=int, default=16,
                        help='Batch size (-1 for auto)')
    parser.add_argument('--device', type=str, default='',
                        help='Device to use (empty for auto, 0 for GPU 0, cpu for CPU)')
    parser.add_argument('--patience', type=int, default=50,
                        help='Early stopping patience (epochs without improvement)')
    parser.add_argument('--workers', type=int, default=8,
                        help='Number of data loading workers')
    
    # Dataset split ratios
    parser.add_argument('--train_ratio', type=float, default=0.7,
                        help='Fraction of data for training')
    parser.add_argument('--val_ratio', type=float, default=0.2,
                        help='Fraction of data for validation')
    parser.add_argument('--test_ratio', type=float, default=0.1,
                        help='Fraction of data for testing')
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed for reproducibility')
    
    # Optional
    parser.add_argument('--skip_split', action='store_true',
                        help='Skip splitting if dataset is already split')
    parser.add_argument('--resume', type=str, default=None,
                        help='Resume training from checkpoint')
    parser.add_argument('--export_openvino', action='store_true',
                        help='Export trained model to OpenVINO format for Intel hardware inference')
    
    args = parser.parse_args()
    
    # Expand paths
    dataset_dir = Path(args.dataset).expanduser().resolve()
    output_dir = Path(args.output).expanduser().resolve()
    
    # Validate dataset directory
    if not dataset_dir.exists():
        print(f'Error: Dataset directory not found: {dataset_dir}')
        sys.exit(1)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f'Dataset: {dataset_dir}')
    print(f'Output: {output_dir}')
    print(f'Weights: {os.environ["ULTRALYTICS_HOME"]}')
    
    # Check if we need to split dataset
    yaml_path = output_dir / 'dataset' / 'dataset.yaml'
    
    if args.skip_split and yaml_path.exists():
        print(f'\nUsing existing dataset split: {yaml_path}')
    else:
        # Get image-label pairs
        print('\nScanning dataset...')
        pairs = get_image_label_pairs(dataset_dir)
        print(f'Found {len(pairs)} image-label pairs')
        
        if len(pairs) == 0:
            print('Error: No valid image-label pairs found')
            sys.exit(1)
        
        # Split dataset
        print(f'\nSplitting dataset ({args.train_ratio:.0%} train, {args.val_ratio:.0%} val, {args.test_ratio:.0%} test)...')
        train_pairs, val_pairs, test_pairs = split_dataset(
            pairs,
            train_ratio=args.train_ratio,
            val_ratio=args.val_ratio,
            test_ratio=args.test_ratio,
            seed=args.seed
        )
        
        print(f'  Train: {len(train_pairs)} samples')
        print(f'  Val: {len(val_pairs)} samples')
        print(f'  Test: {len(test_pairs)} samples')
        
        # Read class names
        class_names = read_class_names(dataset_dir)
        print(f'\nClasses: {class_names}')
        
        # Create YOLO dataset structure
        print('\nCreating YOLO dataset structure...')
        yaml_path = create_yolo_dataset_structure(
            output_dir,
            train_pairs,
            val_pairs,
            test_pairs,
            class_names
        )
    
    # Resume from checkpoint if specified
    if args.resume:
        print(f'\nResuming from checkpoint: {args.resume}')
        args.model = args.resume
    
    # Train model
    print('\n' + '='*60)
    print('TRAINING')
    print('='*60)
    
    best_model = train_yolo_obb(
        yaml_path=yaml_path,
        output_dir=output_dir,
        model_name=args.model,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        patience=args.patience,
        workers=args.workers
    )
    
    print('\n' + '='*60)
    print('TRAINING COMPLETE')
    print('='*60)
    print(f'Best model: {best_model}')
    print(f'Output directory: {output_dir}')
    
    # Export to OpenVINO if requested
    if args.export_openvino:
        print('\n' + '='*60)
        print('OPENVINO EXPORT')
        print('='*60)
        
        openvino_model = export_to_openvino(best_model, output_dir)
        
        if openvino_model:
            print('\n' + '='*60)
            print('EXPORT COMPLETE')
            print('='*60)
            print(f'OpenVINO model: {openvino_model}')
            print('\nTo run inference with OpenVINO:')
            print(f'  from ultralytics import YOLO')
            print(f'  model = YOLO("{openvino_model}")')
            print(f'  results = model("image.jpg", device="intel:gpu")  # or intel:cpu, intel:npu')


if __name__ == '__main__':
    main()
