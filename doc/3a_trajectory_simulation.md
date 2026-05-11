# Trajectory Planning 
## Execution Procedure

### Step 1a: Open Isaac Sim
`~/workspaces/movensys-simulation/<MANIPULATOR_MODEL>/3a_trajectory_simulation.usd`

### Step 1b: Open Gazebo
```
mros ros2 launch movensys_manipulator_description gazebo_trajectory_simulation.launch.py
```




### Step 2a: Run simulator bridge
```
mros ros2 launch movensys_manipulator_moveit_config sim_bridge.launch.py simulator:=isaacsim use_sim_time:=true 
```
`simulator:=gazebo` for use gazebo





### Step 3a: Launch MoveIt2's OMPL + API
```
mros ros2 launch movensys_manipulator_moveit_config moveit.launch.py use_sim_time:=true
```

### Step 3b: Launch cuMotion + API
```
mros ros2 launch movensys_manipulator_isaac_ros_config isaac_cumotion.launch.py use_sim_time:=true
```







### Step 5 (optional): Execute Trajectory Test
```
mros ros2 launch movensys_manipulator_moveit_config trajectory_test.launch.py use_sim_time:=true
```

### Step 5 (optional): Execute Coverage Test
```
mros ros2 launch movensys_manipulator_moveit_config coverage_pose.launch.py use_sim_time:=true
```