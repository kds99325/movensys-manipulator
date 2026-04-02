#!/bin/bash
# Fix for isaac_ros_cumotion robot_segmenter.py
# Bug: enable_ros_publish is hardcoded as False in both PyNitrosImageBuilder.build()
#      calls inside publish_images(). This causes world_depth_ros and robot_mask_ros
#      to never publish any data, even though the topics are created and the GPU
#      segmentation runs correctly.
# Fix: Set enable_ros_publish=True so the _ros topics carry actual image data.

SEGMENTER_FILE="/opt/ros/jazzy/lib/python3.12/site-packages/isaac_ros_cumotion/robot_segmenter.py"

if [ ! -f "$SEGMENTER_FILE" ]; then
    echo "Warning: robot_segmenter.py not found at $SEGMENTER_FILE"
    exit 0
fi

echo "Applying robot_segmenter.py bug fix..."

cp "$SEGMENTER_FILE" "${SEGMENTER_FILE}.original"

python3 - "$SEGMENTER_FILE" << 'PYTHON_SCRIPT'
import sys

file_path = sys.argv[1]

with open(file_path, 'r') as f:
    content = f.read()

# Check if already patched
if "                                            False)" not in content:
    print("File already patched, skipping...")
    sys.exit(0)

# Fix mask_builder.build() call - unique context: 'mono8' is only in this call
content = content.replace(
    "                                            'mono8',\n"
    "                                            camera_header[idx],\n"
    "                                            0,\n"
    "                                            False)",
    "                                            'mono8',\n"
    "                                            camera_header[idx],\n"
    "                                            0,\n"
    "                                            True)"
)

# Fix world_depth_builder.build() call - unique context: depth_encoding[idx] is only in this call
content = content.replace(
    "                                            depth_encoding[idx],\n"
    "                                            camera_header[idx],\n"
    "                                            0,\n"
    "                                            False)",
    "                                            depth_encoding[idx],\n"
    "                                            camera_header[idx],\n"
    "                                            0,\n"
    "                                            True)"
)

if "                                            False)" in content:
    print("ERROR: One or both replacements did not apply.")
    sys.exit(1)

with open(file_path, 'w') as f:
    f.write(content)

print("Patch applied successfully!")
PYTHON_SCRIPT

echo "robot_segmenter.py fix applied."
