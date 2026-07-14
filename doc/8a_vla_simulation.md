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




### Step 4: Enable moveit2 servo
```
mros ros2 service call /servo_node/start_servo std_srvs/srv/Trigger
```




### Step 5: Drive the end effector with the keyboard
```
mros ros2 run moveit_servo servo_keyboard_input
```
Keep this terminal focused — it reads keys directly. It prints its own key map on
start-up; the defaults are:

| Key            | Action                                             |
|----------------|----------------------------------------------------|
| `↑` / `↓`      | Cartesian jog along **x** (+ / −)                  |
| `←` / `→`      | Cartesian jog along **y** (− / +)                  |
| `.` / `;`      | Cartesian jog along **z** (− / +)                  |
| `1` … `6`      | Joint jog for joint 1 … 6                          |
| `r`            | Reverse the current jog direction                  |
| `w`            | Command in the **world/base** frame (`world_manipulator`) |
| `e`            | Command in the **end-effector** frame (`Link6`)    |
| `q`            | Quit                                               |
