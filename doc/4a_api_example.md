# API Node Examples

## Subscribe EEF pose (base frame)
```
ros2 topic echo /wmx/moveit2/eef_pose
```

## Subscribe EEF orientation as roll/pitch/yaw (rad)
```
ros2 topic echo /wmx/moveit2/eef_rpy
```

## Get EEF pose (service)
```
docker exec -it movensys_manipulator_container \
bash -lc 'source /opt/ros/${ROS_DISTRO}/setup.bash && source /home/admin/ws/install/setup.bash && \
        ros2 service call /wmx/moveit2/get_eef_pose movensys_manipulator_moveit_config/srv/GetEefPose "{}"'
```

## Subscribe joint states
```
ros2 topic echo /joint_states
```

## Gripper service
```
ros2 service call /wmx/set_gripper std_srvs/srv/SetBool "{data: true}"
```

## Get tf for specific transform
```
ros2 run tf2_ros tf2_echo world_manipulator Link6
```

---

## Service calls

#### Absolute cartesian move (base frame)
```
docker exec -it movensys_manipulator_container \
bash -lc 'source /opt/ros/${ROS_DISTRO}/setup.bash && source /home/admin/ws/install/setup.bash && \
        ros2 service call /wmx/moveit2/absolute_base_eef_cartesian \
        movensys_manipulator_moveit_config/srv/MovePose \
        "{pos: [0.098, -0.071, 0.45], ori: [3.14, 0.0, 3.14]}"'
```

#### Relative cartesian move (base frame)
```
docker exec -it movensys_manipulator_container \
bash -lc 'source /opt/ros/${ROS_DISTRO}/setup.bash && source /home/admin/ws/install/setup.bash && \
        ros2 service call /wmx/moveit2/relative_base_eef_cartesian \
        movensys_manipulator_moveit_config/srv/MovePose \
        "{pos: [0.05, 0.0, 0.0], ori: [0.0, 0.0, 0.0]}"'
```

#### Relative cartesian move (tool frame)
```
docker exec -it movensys_manipulator_container \
bash -lc 'source /opt/ros/${ROS_DISTRO}/setup.bash && source /home/admin/ws/install/setup.bash && \
        ros2 service call /wmx/moveit2/relative_tool_eef_cartesian \
        movensys_manipulator_moveit_config/srv/MovePose \
        "{pos: [0.05, 0.0, 0.0], ori: [0.0, 0.0, 0.0]}"'
```

#### Absolute joint-space move (pose target, base frame)
```
docker exec -it movensys_manipulator_container \
bash -lc 'source /opt/ros/${ROS_DISTRO}/setup.bash && source /home/admin/ws/install/setup.bash && \
        ros2 service call /wmx/moveit2/absolute_base_eef_joint_movement \
        movensys_manipulator_moveit_config/srv/MovePose \
        "{pos: [-0.2, -0.071, 0.45], ori: [3.14, 0.0, 3.14]}"'
```

#### Joint movement (absolute)
```
docker exec -it movensys_manipulator_container \
bash -lc 'source /opt/ros/${ROS_DISTRO}/setup.bash && source /home/admin/ws/install/setup.bash && \
        ros2 service call /wmx/moveit2/joint_movement \
        movensys_manipulator_moveit_config/srv/MoveJoints \
        "{joint_names: [joint1, joint2, joint3, joint4, joint5, joint6], \
          joint_values: [1.982, 0.1325, 0.9693, 0.474, -1.5697, 0.4105]}"'
```

#### Joint movement (relative / increment)
```
docker exec -it movensys_manipulator_container \
bash -lc 'source /opt/ros/${ROS_DISTRO}/setup.bash && source /home/admin/ws/install/setup.bash && \
        ros2 service call /wmx/moveit2/relative_joint_movement \
        movensys_manipulator_moveit_config/srv/MoveJoints \
        "{joint_names: [joint1, joint2], joint_values: [0.2, -0.2]}"'
```