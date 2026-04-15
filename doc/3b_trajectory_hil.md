# Trajectory Planning 
## Execution Procedure

### Step 1a: Open Isaac Sim
`~/workspaces/robotics_isaac_sim/<MANIPULATOR_MODEL>/trajectory_hil.usd`

### Step 1b: Open Gazebo [Docker]
```
ros2 launch movensys_manipulator_description gazebo_trajectory_simulation.launch.py
```




### Step 2: Run wmx-ros2 for manipulator
https://github.com/movensys/wmx-ros2/blob/main/doc/launch_<MANIPULATOR_MODEL>_manipulator.md






### Step 3a: Launch MoveIt2's OMPL [Docker]
```
ros2 launch movensys_manipulator_moveit_config moveit.launch.py
```

### Step 3b: Launch cuMotion [Docker]
```
ros2 launch movensys_manipulator_moveit_config cumotion.launch.py
```





### Step 4: Launch API Node [Docker]
```
ros2 launch movensys_manipulator_moveit_config movensys_manipulator_api.launch.py
```

### Step 5 (optional): Execute Trajectory Test [Docker]
```
ros2 launch movensys_manipulator_moveit_config movensys_manipulator_trajectory.launch.py
```