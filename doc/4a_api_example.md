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
ros2 service call /wmx/moveit2/get_eef_pose movensys_manipulator_moveit_config/srv/GetEefPose "{}"
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
ros2 run tf2_ros tf2_echo world_manipulator Link6 --timeout 1
```

---

## Service calls

#### Absolute cartesian move (base frame)
```
ros2 service call /wmx/moveit2/absolute_base_eef_cartesian \
  movensys_manipulator_moveit_config/srv/MovePose \
  "{pos: [0.3, 0.0, 0.4], ori: [0.0, 1.5708, 0.0]}"
```

#### Relative cartesian move (base frame)
```
ros2 service call /wmx/moveit2/relative_base_eef_cartesian \
  movensys_manipulator_moveit_config/srv/MovePose \
  "{pos: [0.05, 0.0, 0.0], ori: [0.0, 0.0, 0.0]}"
```

#### Relative cartesian move (tool frame)
```
ros2 service call /wmx/moveit2/relative_tool_eef_cartesian \
  movensys_manipulator_moveit_config/srv/MovePose \
  "{pos: [0.05, 0.0, 0.0], ori: [0.0, 0.0, 0.0]}"
```

#### Absolute joint-space move (pose target, base frame)
```
ros2 service call /wmx/moveit2/absolute_base_eef_joint_movement \
  movensys_manipulator_moveit_config/srv/MovePose \
  "{pos: [0.3, 0.0, 0.4], ori: [0.0, 1.5708, 0.0]}"
```

#### Joint movement
```
ros2 service call /wmx/moveit2/joint_movement \
  movensys_manipulator_moveit_config/srv/MoveJoints \
  "{joint_names: ['Joint1', 'Joint2', 'Joint3', 'Joint4', 'Joint5', 'Joint6'], \
    joint_values: [0.0, -0.5, 1.0, 0.0, 0.5, 0.0]}"
```
