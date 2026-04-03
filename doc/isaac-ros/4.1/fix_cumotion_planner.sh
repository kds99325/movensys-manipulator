#!/bin/bash
# Fix for isaac_ros_cumotion cumotion_planner.py
# Bug: goal_handle.succeed() was called without passing the result,
#      which sends an empty result immediately. The trajectory in the
#      return value was ignored.
# Fix: Pass the result to goal_handle.succeed(result)

CUMOTION_FILE="/opt/ros/jazzy/lib/python3.12/site-packages/isaac_ros_cumotion/cumotion_planner.py"

if [ ! -f "$CUMOTION_FILE" ]; then
    echo "Warning: cumotion_planner.py not found at $CUMOTION_FILE"
    exit 0
fi

echo "Applying cumotion_planner.py bug fix..."

# Create backup
cp "$CUMOTION_FILE" "${CUMOTION_FILE}.original"

# Use Python to apply the fix more reliably
python3 << 'PYTHON_SCRIPT'
import re

file_path = "/opt/ros/jazzy/lib/python3.12/site-packages/isaac_ros_cumotion/cumotion_planner.py"

with open(file_path, 'r') as f:
    content = f.read()

# Check if already patched
if "goal_handle.succeed(result)" in content:
    print("File already patched, skipping...")
    exit(0)

# Fix 1: Comment out the early goal_handle.succeed() call (around line 754)
# This is in execute_callback, right after setting plan_req
content = re.sub(
    r'(plan_req = goal_handle\.request\.request\n\n)(\s+)(goal_handle\.succeed\(\))',
    r'\1\2# \3  # REMOVED - Bug fix: must pass result to succeed()',
    content
)

# Fix 2: Add goal_handle.succeed(result) before each "return result" in execute_callback
# We need to be careful to only modify the execute_callback function

# Find the execute_callback function and modify return statements within it
def add_succeed_before_return(match):
    indent = match.group(1)
    return f'{indent}goal_handle.succeed(result)\n{indent}return result'

# Pattern to match "return result" with proper indentation (8+ spaces = inside execute_callback)
# We match return result that is indented with at least 8 spaces
content = re.sub(
    r'^(            )return result$',
    r'\1goal_handle.succeed(result)\n\1return result',
    content,
    flags=re.MULTILINE
)

# Also handle 12-space indentation (deeper in conditionals)
content = re.sub(
    r'^(                )return result$',
    r'\1goal_handle.succeed(result)\n\1return result',
    content,
    flags=re.MULTILINE
)

# Fix the final return at 8-space indentation (end of execute_callback)
content = re.sub(
    r'^(        )return result\n\n    def publish_voxels',
    r'\1goal_handle.succeed(result)  # Bug fix: pass result to succeed()\n\1return result\n\n    def publish_voxels',
    content,
    flags=re.MULTILINE
)

with open(file_path, 'w') as f:
    f.write(content)

print("Patch applied successfully!")
PYTHON_SCRIPT

echo "cumotion_planner.py fix applied."
