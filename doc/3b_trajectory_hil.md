# Trajectory Planning 
## Execution Procedure

### Step 1a: Open Isaac Sim
`~/workspaces/movensys-simulation/<MANIPULATOR_MODEL>/trajectory_hil.usd`

### Step 1b: Open Gazebo
```
```




### Step 2: Run wmx-ros2 for manipulator
check `~/workspaces/movensys_ws/src/wmx-ros2/doc/launch_<MANIPULATOR_MODEL>_manipulator.md` 






### Step 3a: Launch MoveIt2's OMPL + API
```
mros ros2 launch movensys_manipulator_moveit_config moveit.launch.py
```

### Step 3b: Launch cuMotion + API
```
mros ros2 launch movensys_manipulator_isaac_ros_config isaac_cumotion.launch.py
```






### Step 4 (optional): Execute Trajectory Test
```
mros ros2 launch movensys_manipulator_moveit_config trajectory_test.launch.py
```