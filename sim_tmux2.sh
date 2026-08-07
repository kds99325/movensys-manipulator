#!/bin/bash

# 1. 세션 이름 설정
SESSION="movensys_sim"

# 2. 이미 실행 중인 동일 세션이 있다면 종료 (초기화)
tmux kill-session -t $SESSION 2>/dev/null

echo "Starting Movensys Simulation Session with Active State Polling..."

# 3. 새 세션 생성 [Pane 0.0: 좌상단]
#    Step 1b. Gazebo 시뮬레이터 실행
tmux new-session -d -s $SESSION -n "trajectory_test"
tmux send-keys -t $SESSION:0.0 "mros ros2 launch movensys_manipulator_description gazebo_trajectory_simulation.launch.py" C-m

# 4. 화면을 먼저 위/아래(-v)로 2등분 (위: 0.0 / 아래: 0.1 생성)
tmux split-window -v -t $SESSION:0.0

# 5. 위쪽 창(0.0)을 좌/우(-h)로 분할 -> [Pane 0.1: 우상단 생성] (아래쪽 창은 0.2로 번호 밀림)
#    Step 2a. 우상단(0.1)에서 ROS 2 내부 /clock 토픽 감지 즉시 Sim Bridge 실행
tmux split-window -h -t $SESSION:0.0
tmux send-keys -t $SESSION:0.1 "mros bash -c 'echo \"[Waiting for Gazebo /clock...]\"; until ros2 topic list 2>/dev/null | grep -q \"/clock\"; do sleep 1; done; echo \"[Connected! Launching Sim Bridge...]\"; ros2 launch movensys_manipulator_moveit_config sim_bridge.launch.py simulator:=gazebo use_sim_time:=true'" C-m

# 6. 아래쪽 창(0.2)을 좌/우(-h)로 분할 -> [Pane 0.2: 좌하단 / Pane 0.3: 우하단 생성]
#    Step 3a. 좌하단(0.2)에서 /joint_states 토픽 감지 즉시 MoveIt2 실행
tmux split-window -h -t $SESSION:0.2
tmux send-keys -t $SESSION:0.2 "mros bash -c 'echo \"[Waiting for Sim Bridge /joint_states...]\"; until ros2 topic list 2>/dev/null | grep -q \"/joint_states\"; do sleep 1; done; echo \"[Connected! Launching MoveIt2...]\"; ros2 launch movensys_manipulator_moveit_config moveit.launch.py use_sim_time:=true rsp:=false'" C-m

# 7. Step 4. 우하단(0.3)에서 MoveIt Servo 서비스 감지 즉시 Keyboard Teleop 실행
#    (시간 동기화 오류 예방을 위해 --ros-args -p use_sim_time:=true 옵션 포함)
tmux send-keys -t $SESSION:0.3 "mros bash -c 'echo \"[Waiting for MoveIt Servo service...]\"; until ros2 service list 2>/dev/null | grep -q \"/servo_node/switch_command_type\"; do sleep 1; done; echo \"[Ready! Starting Keyboard Teleop...]\"; ros2 run movensys_manipulator_moveit_config keyboard_teleop --ros-args -p use_sim_time:=true'" C-m

# 8. 사용자가 즉시 키보드 입력을 할 수 있도록 포커스를 우하단 창(Pane 0.3)으로 이동
tmux select-pane -t $SESSION:0.3

# 9. 백그라운드 세션을 현재 터미널에 띄우기
tmux attach-session -t $SESSION