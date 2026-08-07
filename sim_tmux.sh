#!/bin/bash

# 1. 세션 이름 설정
SESSION="movensys_sim"

# 2. 이미 실행 중인 동일 세션이 있다면 종료 (초기화)
tmux kill-session -t $SESSION 2>/dev/null

# 3. 새 세션 생성 [Pane 0.0: 좌상단]
#    Step 1b. Gazebo 시뮬레이터 실행
tmux new-session -d -s $SESSION -n "trajectory_test"
tmux send-keys -t $SESSION:0.0 "mros ros2 launch movensys_manipulator_description gazebo_trajectory_simulation.launch.py" C-m

# 4. 화면을 먼저 위/아래(-v)로 2등분 (위: 0.0 / 아래: 0.1 생성)
tmux split-window -v -t $SESSION:0.0

# 5. 위쪽 창(0.0)을 좌/우(-h)로 분할 -> [Pane 0.1: 우상단 생성] (아래쪽 창은 0.2로 번호가 밀림)
#    Step 2a. 우상단(0.1)에 Sim Bridge 실행 (Gazebo 로딩 대기 5초)
tmux split-window -h -t $SESSION:0.0
tmux send-keys -t $SESSION:0.1 "sleep 5 && mros ros2 launch movensys_manipulator_moveit_config sim_bridge.launch.py simulator:=gazebo use_sim_time:=true" C-m

# 6. 아래쪽 창(0.2)을 좌/우(-h)로 분할 -> [Pane 0.2: 좌하단 / Pane 0.3: 우하단 생성]
#    Step 3a. 좌하단(0.2)에 MoveIt2 실행 (Bridge 연결 대기 8초)
tmux split-window -h -t $SESSION:0.2
tmux send-keys -t $SESSION:0.2 "sleep 8 && mros ros2 launch movensys_manipulator_moveit_config moveit.launch.py use_sim_time:=true rsp:=false" C-m

# 7. Step 4. 우하단(0.3)에 Keyboard Teleop 실행 (MoveIt 준비 대기 12초)
tmux send-keys -t $SESSION:0.3 "sleep 12 && mros ros2 run movensys_manipulator_moveit_config keyboard_teleop" C-m

# 8. 사용자가 즉시 키보드 입력을 할 수 있도록 포커스를 우하단 창(Pane 3)으로 이동
tmux select-pane -t $SESSION:0.3

# 9. 백그라운드 세션을 현재 터미널에 띄우기
tmux attach-session -t $SESSION