# Nvblox Obstacle Avoidance
## Execution Procedure

### Step 1: Open Isaac Sim
`~/workspaces/movensys-simulation/<MANIPULATOR_MODEL>/nvblox_simulation.usd`






### Step 2: Run simulator bridge
```
mros ros2 launch movensys_manipulator_moveit_config sim_bridge.launch.py simulator:=isaacsim use_sim_time:=true 
```






### Step 3: Launch cuMotion + NvBlox
```
mros ros2 launch movensys_manipulator_isaac_config cumotion_nvblox.launch.py use_sim_time:=true
```







### Step 4: AprilTag Pick and Place
```
mros ros2 launch movensys_manipulator_isaac_config obstacle_avoidance.launch.py use_sim_time:=true
```
