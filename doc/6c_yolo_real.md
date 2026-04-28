# YOLO Pick-and-Place (Real Hardware)
## Execution Procedure

### Step 1a: Open Isaac Sim
`~/workspaces/movensys-simulation/<MANIPULATOR_MODEL>/trajectory_real.usd`

### Step 1b: Open Gazebo
```
mros ros2 launch movensys_manipulator_description gazebo_trajectory_real.launch.py
```




### Step 2: Run wmx-ros2 for manipulator
check `~/workspaces/movensys_ws/src/wmx-ros2/doc/launch_<MANIPULATOR_MODEL>_manipulator.md`




### Step 3a: Launch MoveIt2's OMPL + API
```
mros ros2 launch movensys_manipulator_moveit_config moveit.launch.py
```

### Step 3b: Launch cuMotion + API
```
mros ros2 launch movensys_manipulator_moveit_config cumotion.launch.py
```




### Step 4: Launch the hand camera
```
mros ros2 launch movensys_manipulator_perception camera_hand.launch.py
```




### Step 5: Launch the YOLO cube detector
```
mros ros2 launch movensys_manipulator_perception yolo_cube_detector.launch.py
```
Broadcasts TF frames `yolo_cube_{green,blue,yellow,red}` relative to
`camera_hand_link_color_optical_frame`. See `6d_yolo_example.md` for
model/device overrides and verification commands.




### Step 6: Execute YOLO pick-and-place
```
mros ros2 launch movensys_manipulator_moveit_config movensys_manipulator_yolo_trajectory.launch.py
```
Loads pick/drop poses from `config/<MANIPULATOR_MODEL>/yolo_trajectory.yaml`.
The node moves to the scan pose, visually servos over each cube in
`cube_classes` order, picks it up, and places it in the per-class drop box.
