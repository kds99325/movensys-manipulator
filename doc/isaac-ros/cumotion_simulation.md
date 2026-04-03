# cuMotion 
## Execution Procedure

### Step 1: Open Isaac Sim
`~/robotics_isaac_sim/movensys_manipulator/trajectory_simulation.usd`

### Step 2: Run Isaacsim Bridge
```
docker exec -it movensys_manipulator_container \
bash -lc 'source /opt/ros/${ROS_DISTRO}/setup.bash && \
        source /home/admin/ws/install/setup.bash && \
        ros2 run movensys_manipulator_moveit_config isaacsim_bridge --ros-args -p use_sim_time:=true'
```

### Step 3: Launch cuMotion
```
docker exec -it movensys_manipulator_container \
bash -lc 'source /opt/ros/${ROS_DISTRO}/setup.bash && \
        source /home/admin/ws/install/setup.bash && \
        ros2 launch movensys_manipulator_isaac_ros isaac_cumotion.launch.py use_sim_time:=true'
```

### Step 4: Execute Trajectory Test
```
docker exec -it movensys_manipulator_container \
bash -lc 'source /opt/ros/${ROS_DISTRO}/setup.bash && \
        source /home/admin/ws/install/setup.bash && \
        ros2 launch movensys_manipulator_moveit_config movensys_manipulator_trajectory.launch.py use_sim_time:=true'
```