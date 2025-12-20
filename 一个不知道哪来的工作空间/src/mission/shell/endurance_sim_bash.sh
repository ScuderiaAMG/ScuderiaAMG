#!/bin/bash

# 创建会话和第一个窗口
tmux new-session -d -s ros_session -n main_nodes

# Pane 0: roscore
tmux send-keys -t ros_session:0 'roscore' C-m

# Pane 1: location.launch
tmux split-window -h -t ros_session:0
tmux send-keys -t ros_session:0.1 'sleep 3; roslaunch tutorial_gazebo sim.launch' C-m

# Pane 2: simple_camera_driver.launch
tmux split-window -v -t ros_session:0.1
tmux send-keys -t ros_session:0.2 'sleep 4; source ~/endurance_ws/devel/setup.bash; roslaunch usb_cam simple_camera_driver.launch' C-m

# Pane 3: ros_predict.launch
tmux split-window -v -t ros_session:0.2
tmux send-keys -t ros_session:0.3 'sleep 5; source ~/endurance_ws/devel/setup.bash; roslaunch yolov8_ros ros_predict_endurance.launch' C-m

# Pane 3: ros_predict.launch
tmux split-window -v -t ros_session:0.3
tmux send-keys -t ros_session:0.4 'sleep 5; source ~/endurance_ws/devel/setup.bash; roslaunch template gazebo_sim.launch' C-m

# 整理第一个窗口布局
tmux select-layout -t ros_session:0 tiled
# --------------------
# 第二窗口（相机和检测）
# --------------------
tmux new-window -t ros_session:1 -n camera_detection

# Pane 0: web_viewer
tmux send-keys -t ros_session:1 'sleep 5; rosrun web_video_server web_video_server' C-m

tmux split-window -h -t ros_session:1
tmux send-keys -t ros_session:1.1 'sleep 5; source ~/endurance_ws/devel/setup.bash; roslaunch cloud_recognition all_noflag.launch' C-m

tmux split-window -h -t ros_session:1.1
tmux send-keys -t ros_session:1.2 'sleep 5; source ~/endurance_ws/devel/setup.bash; roslaunch mission trajectory.launch' C-m

# 整理第二个窗口布局
tmux select-layout -t ros_session:1 tiled

# --------------------
# 第三窗口（监控和任务）
# --------------------
tmux new-window -t ros_session:2 -n monitors_mission

# Pane 0: /mavros/local_position/pose
tmux send-keys -t ros_session:2 'sleep 6; rostopic echo /mavros/local_position/pose' C-m

# Pane 1: /object_position
tmux split-window -h -t ros_session:2
tmux send-keys -t ros_session:2.1 'sleep 6; source ~/endurance_ws/devel/setup.bash; rostopic echo /object_position' C-m

# Pane 3: complete_mission.launch
tmux split-window -v -t ros_session:2.1
tmux send-keys -t ros_session:2.2 'sleep 7; source ~/endurance_ws/devel/setup.bash; roslaunch mission endurance.launch' C-m

# 整理第三个窗口布局
tmux select-layout -t ros_session:2 tiled

# 附加到会话并显示第一个窗口
tmux select-window -t ros_session:0
tmux attach-session -t ros_session:2