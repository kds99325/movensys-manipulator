# Trajectory Planning 
## Execution Procedure

### Step 1a: Open Isaac Sim
`~/workspaces/movensys-simulation/<MANIPULATOR_MODEL>/trajectory_simulation.usd`

### Step 1b: Open Gazebo
```
mros ros2 launch movensys_manipulator_description gazebo_trajectory_simulation.launch.py
```




### Step 2a: Run Isaacsim Bridge
```
mros ros2 launch movensys_manipulator_moveit_config isaacsim_bridge.launch.py use_sim_time:=true
```

### Step 2b: Run Gazebo Bridge
```
mros ros2 launch movensys_manipulator_moveit_config gazebo_bridge.launch.py use_sim_time:=true
```





### Step 3a: Launch MoveIt2's OMPL
```
mros ros2 launch movensys_manipulator_moveit_config moveit.launch.py use_sim_time:=true
```

### Step 3b: Launch cuMotion
```
mros ros2 launch movensys_manipulator_moveit_config cumotion.launch.py use_sim_time:=true
```






### Step 4: Launch API Node
```
mros ros2 launch movensys_manipulator_moveit_config movensys_manipulator_api.launch.py use_sim_time:=true
```

### Step 5 (optional): Execute Trajectory Test
```
mros ros2 launch movensys_manipulator_moveit_config movensys_manipulator_trajectory.launch.py use_sim_time:=true
```
