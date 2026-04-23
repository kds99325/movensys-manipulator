# Terminal 1 — MoveIt + controllers (existing bring-up)

# Terminal 2 — perception
ros2 launch movensys_manipulator_perception yolo_cube_detector.launch.py
# Terminal 3 — YOLO pick-and-place
ros2 launch movensys_manipulator_moveit_config movensys_manipulator_yolo_trajectory.launch.py