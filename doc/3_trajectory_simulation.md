# Trajectory Planning 
## Execution Procedure

### Step 1a: Open Isaac Sim
`~/robotics_isaac_sim/movensys_manipulator/trajectory_simulation.usd`

### Step 1b: Open Gazebo Harmonic [Docker]
```
ros2 launch movensys_gazebo trajectory_simulation.launch.py
```




### Step 2a: Run Isaacsim Bridge [Docker]
```
ros2 run movensys_manipulator_moveit_config isaacsim_bridge --ros-args -p use_sim_time:=true
```

### Step 2b: Run Gazebo Bridge [Docker]
```
ros2 run movensys_manipulator_moveit_config gazebo_bridge --ros-args -p use_sim_time:=true
```




### Step 3a: Launch Trajectory Planning based on MoveIt2's OMPL [Docker]
```
ros2 launch movensys_manipulator_moveit_config movensys_manipulator_moveit.launch.py use_sim_time:=true
```

### Step 3b: Launch cuMotion [Docker]
```
ros2 launch movensys_manipulator_isaac_ros isaac_cumotion.launch.py use_sim_time:=true
```




### Step 4: Execute Trajectory Test [Docker]
```
ros2 launch movensys_manipulator_moveit_config movensys_manipulator_trajectory.launch.py use_sim_time:=true
```


#### Get EEF pose [Docker]
```
ros2 run tf2_ros tf2_echo world_manipulator Link6
```