#!/bin/bash

# ============ 脚本说明 ============
# 功能：在大终端中启动 7 个 roslaunch（7 pane 分屏）
# 依赖：确保终端足够大（建议 ≥ 45 行）
# 用法：chmod +x start_7.sh && ./start_7.sh

# ============ 清理旧会话 ============
tmux kill-session -t start 2>/dev/null || true

# ============ 创建后台会话（不自动退出） ============
tmux new-session -d -s start -n "launches" "exec bash"

# ============ 分割出 7 个 pane（策略：先水平分上下，再垂直细分） ============


tmux split-window -h -t start -p 66 #1
tmux split-window -h -t start -p 50 #2

tmux split-window -v -t start.0  #3
tmux split-window -v -t start.2  #4
tmux split-window -v -t start.4  #5 
tmux split-window -v -t start.0  #6

tmux send -t start.0 "roslaunch ring_detector roi_mapping.launch" 
tmux send -t start.1 "roslaunch cloud_recognition plane_extractor.launch" 
tmux send -t start.2 "roslaunch fast_detector spatial_cluster_refiner.launch" 
tmux send -t start.3 "roslaunch cloud_recognition point_projector.launch"
tmux send -t start.4 "roslaunch cloud_recognition template_match.launch"
tmux send -t start.5 "roslaunch cloud_recognition point_converter.launch"
tmux send -t start.6 "roslaunch cloud_recognition rviz.launch"
## 显示刚刚创建的会话
tmux a -t start