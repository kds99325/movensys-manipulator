# VLA Application
## Execution Procedure

### Step 1: Open Isaac Sim
`~/workspaces/movensys-simulation/<MANIPULATOR_MODEL>/3a_vla_simulation.usd`



### Step 2: Run simulator bridge
```
mros ros2 launch movensys_manipulator_moveit_config sim_bridge.launch.py simulator:=isaacsim use_sim_time:=true
```
`simulator:=gazebo` to use Gazebo.




### Step 3: Launch Servo
```
mros ros2 launch movensys_manipulator_moveit_config servo.launch.py use_sim_time:=true
```




### Step 4: Drive the end effector with the keyboard
```
mros ros2 run movensys_manipulator_moveit_config keyboard_teleop
```
Pick a mode first (`j` / `t` / `p`), then jog:

| Key            | Action                                                     |
|----------------|------------------------------------------------------------|
| `j`            | **JOINT** mode — keys `1`…`6` jog joint 1…6                 |
| `t`            | **TWIST** mode — Cartesian EEF jog                          |
| `p`            | **POSE** mode — nudge an absolute EEF target pose          |
| `↑` / `↓`      | X (+ / −)  — twist jog, or pose-target nudge                |
| `←` / `→`      | Y (− / +)  — twist jog, or pose-target nudge                |
| `.` / `;`      | Z (− / +)  — twist jog, or pose-target nudge                |
| `1` … `6`      | Joint jog for joint 1 … 6            (JOINT mode)           |
| `w` / `e`      | Twist frame = base (`world_manipulator`) / eef (`Link6`)   |
| `r`            | Reverse jog direction (twist / joint)                      |
| `q`            | Quit                                                       |

In **POSE** mode the target is seeded from the current EEF pose (via TF) and
streamed to Servo, which tracks it; the arrows/`.`/`;` move that target in the
base frame (orientation held from the seed).
