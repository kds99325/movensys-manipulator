# AprilTag Pick and Place
## Execution Procedure

### Step 1: Open Isaac Sim
`~/workspaces/movensys-simulation/<MANIPULATOR_MODEL>/apriltag_pick_and_place_hil.usd`






### Step 2: Run wmx-ros2 for manipulator
check `~/workspaces/movensys_ws/src/wmx-ros2/doc/launch_<MANIPULATOR_MODEL>_manipulator.md` 





### Step 3a: Launch MoveIt2's OMPL + OpenCV Apriltag
```
mros ros2 launch movensys_manipulator_perception apriltag_detector.launch.py
```

### Step 3b: Launch cuMotion + Isaac Apriltag
```
mros ros2 launch movensys_manipulator_isaac_ros_config isaac_cumotion_apriltag.launch.py
```







### Step 4: AprilTag Pick and Place
```
mros ros2 launch movensys_manipulator_moveit_config apriltag_pick_and_place.launch.py use_sim_time:=false target_spawn:=false
```
