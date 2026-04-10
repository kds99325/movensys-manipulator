# Trajectory Planning 
## Execution Procedure

### Step 1a: Open Isaac Sim
`~/workspaces/robotics_isaac_sim/movensys_manipulator/trajectory_real.usd`

### Step 1b: Open Gazebo [Docker]
```
ros2 launch movensys_gazebo trajectory_real.launch.py
```




### Step 2: Run CR3A wmx-ros2
https://github.com/movensys/wmx-ros2/blob/main/doc/3_launch_cr3a_manipulator.md





### Step 3a: Launch Trajectory Planning based on MoveIt2's OMPL [Docker]
```
ros2 launch movensys_manipulator_moveit_config movensys_manipulator_moveit.launch.py
```

### Step 3b: Launch cuMotion [Docker]
```
ros2 launch movensys_manipulator_isaac_ros isaac_cumotion.launch.py
```




### Step 4: Execute Trajectory Test [Docker]
```
ros2 launch movensys_manipulator_moveit_config movensys_manipulator_trajectory.launch.py
```


#### Get EEF pose [Docker]
```
ros2 run tf2_ros tf2_echo world_manipulator Link6
```