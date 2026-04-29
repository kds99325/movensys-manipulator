# Nvblox Obstacle Avoidance
## Execution Procedure

### Step 1: Open Isaac Sim
`~/workspaces/movensys-simulation/<MANIPULATOR_MODEL>/obstacle_avoidance_simulation.usd`






### Step 2: Run simulator bridge
```
mros ros2 launch movensys_manipulator_moveit_config sim_bridge.launch.py simulator:=isaacsim use_sim_time:=true 
```






### Step 3: Launch cuMotion + NvBlox
```
mros ros2 launch movensys_manipulator_isaac_ros_config isaac_cumotion_nvblox.launch.py use_sim_time:=true
```







### Step 4: Obstacle Avoidance
```
mros ros2 launch movensys_manipulator_moveit_config obstacle_avoidance.launch.py use_sim_time:=true
```
