# Trajectory Planning 
## Execution Procedure

### Step 1a: Open Isaac Sim
`~/robotics_isaac_sim/movensys_manipulator/trajectory_simulation.usd`

### Step 1b: Open Gazebo Harmonic
```
docker exec -it movensys_manipulator_container \
bash -lc 'source /opt/ros/${ROS_DISTRO}/setup.bash && \
        source /home/admin/ws/install/setup.bash && \
        ros2 launch movensys_gazebo trajectory_simulation.launch.py'
```



### Step 2a: Run Isaacsim Bridge
```
docker exec -it movensys_manipulator_container \
bash -lc 'source /opt/ros/${ROS_DISTRO}/setup.bash && \
        source /home/admin/ws/install/setup.bash && \
        ros2 run movensys_manipulator_moveit_config isaacsim_bridge --ros-args -p use_sim_time:=true'
```

### Step 2b: Run Gazebo Bridge
```
docker exec -it movensys_manipulator_container \
bash -lc 'source /opt/ros/${ROS_DISTRO}/setup.bash && \
        source /home/admin/ws/install/setup.bash && \
        ros2 run movensys_manipulator_moveit_config gazebo_bridge --ros-args -p use_sim_time:=true'
```





### Step 3a: Launch Trajectory Planning based on MoveIt2's OMPL
```
docker exec -it movensys_manipulator_container \
bash -lc 'source /opt/ros/${ROS_DISTRO}/setup.bash && \
        source /home/admin/ws/install/setup.bash && \
        ros2 launch movensys_manipulator_moveit_config movensys_manipulator_moveit.launch.py use_sim_time:=true'
```

### Step 3b: Launch cuMotion
```
docker exec -it movensys_manipulator_container \
bash -lc 'source /opt/ros/${ROS_DISTRO}/setup.bash && \
        source /home/admin/ws/install/setup.bash && \
        ros2 launch movensys_manipulator_isaac_ros isaac_cumotion.launch.py use_sim_time:=true'
```





### Step 4: Launch API Node
```
docker exec -it movensys_manipulator_container \
bash -lc 'source /opt/ros/${ROS_DISTRO}/setup.bash && \
        source /home/admin/ws/install/setup.bash && \
        ros2 launch movensys_manipulator_moveit_config movensys_manipulator_api.launch.py use_sim_time:=true'
```

