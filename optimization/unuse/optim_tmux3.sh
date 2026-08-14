#!/bin/bash

# 1. 세션 이름 설정
SESSION="movensys_sim"

# 2. 이미 실행 중인 동일 세션이 있다면 종료
tmux kill-session -t $SESSION 2>/dev/null

echo "Starting Movensys Simulation Session with Active State Polling..."

# ==========================================
# 실행할 '순수' ROS 명령어들 정리 (mros 제외)
# ==========================================

# Pane 0.0: Gazebo 실행
CMD_GAZEBO="ros2 launch movensys_manipulator_description gazebo_trajectory_simulation.launch.py"

# Pane 0.1: Sim Bridge 실행
CMD_BRIDGE="echo '[Waiting for Gazebo /clock...]'; \
until ros2 topic list 2>/dev/null | grep -q '/clock'; do sleep 1; done; \
echo '[Connected! Launching Sim Bridge...]'; \
ros2 launch movensys_manipulator_moveit_config sim_bridge.launch.py simulator:=gazebo use_sim_time:=true"

# Pane 0.2: MoveIt2 실행
CMD_MOVEIT="echo '[Waiting for Sim Bridge /joint_states...]'; \
until ros2 topic list 2>/dev/null | grep -q '/joint_states'; do sleep 1; done; \
echo '[Connected! Launching MoveIt2...]'; \
ros2 launch movensys_manipulator_moveit_config moveit.launch.py use_sim_time:=true rsp:=false"

# Pane 0.3: Keyboard Teleop 실행
CMD_TELEOP="echo '[Waiting for MoveIt Servo service...]'; \
until ros2 service list 2>/dev/null | grep -q '/servo_node/switch_command_type'; do sleep 1; done; \
echo '[Ready! Starting Keyboard Teleop...]'; \
ros2 run movensys_manipulator_moveit_config keyboard_teleop --ros-args -p use_sim_time:=true"


# ==========================================
# Tmux 레이아웃 구성 및 명령어 전송
# ==========================================

# 1. 창 생성 및 분할
tmux new-session -d -s $SESSION -n "trajectory_test"
tmux split-window -v -t $SESSION:0.0
tmux split-window -h -t $SESSION:0.0
tmux split-window -h -t $SESSION:0.2

# 2. 4개의 Pane 모두 mros 컨테이너로 먼저 진입시킴
tmux send-keys -t $SESSION:0.0 "mros" C-m
tmux send-keys -t $SESSION:0.1 "mros" C-m
tmux send-keys -t $SESSION:0.2 "mros" C-m
tmux send-keys -t $SESSION:0.3 "mros" C-m

# 컨테이너 쉘(bash)이 완전히 켜질 때까지 안전하게 1초 대기
sleep 1

# 3. 도커 내부 쉘에 실제 ROS 명령어 전송
tmux send-keys -t $SESSION:0.0 "$CMD_GAZEBO" C-m
tmux send-keys -t $SESSION:0.1 "$CMD_BRIDGE" C-m
tmux send-keys -t $SESSION:0.2 "$CMD_MOVEIT" C-m
tmux send-keys -t $SESSION:0.3 "$CMD_TELEOP" C-m

# 4. 사용자 입력 창으로 포커스 이동 및 세션 띄우기
tmux select-pane -t $SESSION:0.3
tmux attach-session -t $SESSION