#include "fly_ctl/motion_control.h"
#include <ros/ros.h>
#include <tf/transform_datatypes.h>

namespace fly_ctl {

MotionController::MotionController(ros::NodeHandle& nh) : nh_(nh), 
    has_odom_(false), 
    has_init_position_(false) 
{
    // ------------ 读取参数 ------------ //

    // 这几个可以不写在yaml里, 直接使用默认值:
    nh_.param("state_topic", state_topic_, std::string("/mavros/state"));
    nh_.param("odom_topic", odom_topic_, std::string("/mavros/local_position/odom"));

    // 这两个建议写在yaml里, 方便调整:
    nh_.param("position_tolerance", position_tolerance_, 0.2);
    // nh_.param("err_max", position_tolerance_, 0.2); --- IGNORE ---
    nh_.param("max_yaw_rate", max_yaw_rate_, 1.5); 
    nh_.param("auto_offboard", auto_offboard_, false);

    nh_.param("arming_client_topic", arming_client_topic_, std::string("/mavros/cmd/arming"));
    nh_.param("set_mode_client_topic", set_mode_client_topic_, std::string("/mavros/set_mode"));

    // 初始化发布器和订阅器
    arming_client_ = nh_.serviceClient<mavros_msgs::CommandBool>(arming_client_topic_);
    set_mode_client_ = nh_.serviceClient<mavros_msgs::SetMode>(set_mode_client_topic_);

    setpoint_raw_pub_ = nh_.advertise<mavros_msgs::PositionTarget>("/mavros/setpoint_raw/local", 10);
    state_sub_ = nh_.subscribe(state_topic_, 10, &MotionController::stateCallback, this);
    odom_sub_ = nh_.subscribe(odom_topic_, 10, &MotionController::odomCallback, this);

    // 初始化setpoint_raw_
    setpoint_raw_.coordinate_frame = mavros_msgs::PositionTarget::FRAME_LOCAL_NED;
    setpoint_raw_.type_mask = 1 + 2 + 4 + /*8 + 16 + 32*/ + 64 + 128 + 256 + 512 /*+ 1024 */ + 2048; // 只控制位置和偏航角
    setpoint_raw_.yaw = 0.0;
    setpoint_raw_.yaw_rate = 0.0;

    current_roll_ = current_pitch_ = current_yaw_ = 0.0;
    last_ctl_time_ = ros::Time::now();
}

// 理论上你有回调函数用了的话就不需要跑这个函数了
bool MotionController::initialize() {
    ros::Rate rate(20.0); // 20 Hz
    ROS_INFO("Waiting for FCU connection...");
    while (ros::ok() && (!has_odom_ || !current_state_.connected)) {
        ros::spinOnce();
        rate.sleep();
    }
    
    // 初始化起飞位置, 如果还没有初始化, 保险起见
    if (!has_init_position_ && current_odom_.pose.pose.position.z != 0) {
        init_x_ = current_odom_.pose.pose.position.x;
        init_y_ = current_odom_.pose.pose.position.y;
        init_z_ = current_odom_.pose.pose.position.z;
        init_yaw_ = current_yaw_;
        has_init_position_ = true;
        ROS_INFO("Initialized takeoff position: (%.2f, %.2f, %.2f), yaw: %.2f", 
                 init_x_, init_y_, init_z_, init_yaw_);
                 return true;
    }
    else if (has_init_position_) {
        return true;
    }
    else {
        ROS_ERROR("Failed to initialize: no valid odometry data");
        return false;
    }
}

// 回调函数接收无人机的状态信息
void MotionController::stateCallback(const mavros_msgs::State::ConstPtr& msg) {
    current_state_ = *msg;
}

// 回调函数接收无人机的里程计信息
void MotionController::odomCallback(const nav_msgs::Odometry::ConstPtr& msg) {
    current_odom_ = *msg;
    has_odom_ = true;
    
    // 提取当前姿态
    extractRPY(current_odom_.pose.pose.orientation, current_roll_, current_pitch_, current_yaw_);
    if (current_odom_.pose.pose.position.z == 0 || current_odom_.pose.pose.position.x == 0 || current_odom_.pose.pose.position.y == 0) {
        has_odom_ = false; // 如果高度为0, 认为没有有效里程计
        return;
    }

    // 自动初始化起飞位置（如果还没初始化）
    if (!has_init_position_ && current_odom_.pose.pose.position.z != 0) {
        init_x_ = current_odom_.pose.pose.position.x;
        init_y_ = current_odom_.pose.pose.position.y;
        init_z_ = current_odom_.pose.pose.position.z;
        init_yaw_ = current_yaw_;
        has_init_position_ = true;
        ROS_INFO("Auto-initialized takeoff position: (%.2f, %.2f, %.2f), yaw: %.2f", 
                 init_x_, init_y_, init_z_, init_yaw_);
    }
}

// 提取欧拉角
void MotionController::extractRPY(const geometry_msgs::Quaternion& quat, 
                                  double& roll, double& pitch, double& yaw) {
    tf::Quaternion tf_quat;
    tf::quaternionMsgToTF(quat, tf_quat);
    tf::Matrix3x3(tf_quat).getRPY(roll, pitch, yaw);
}

// 不需要
bool MotionController::takeoff(double height, double timeout) {
    if (!has_init_position_) {
        ROS_ERROR("Cannot takeoff: no initial position available");
        return false;
    }
    
    dronePose target_pose(init_x_, init_y_, init_z_ + height, init_yaw_);
    return moveToPosition(target_pose);
}

// bool MotionController::land(double timeout) {
//     if (!has_init_position_) {
//         ROS_ERROR("Cannot land: no initial position available");
//         return false;
//     }
    
//     // 降落到起飞点高度
//     dronePose land_pose(init_x_, init_y_, init_z_, current_yaw_);
//     return moveToPosition(land_pose);
// }


bool MotionController::setOffboardMode(float takeoff_height) {
    ros::Rate rate(20.0); // 20 Hz
    mavros_msgs::SetMode offb_set_mode;
    offb_set_mode.request.custom_mode = "OFFBOARD";
    mavros_msgs::CommandBool arm_cmd;
    arm_cmd.request.value = true;
    
    // 先设置初始 setpoint（起飞位置）
    if (!has_init_position_) {
        ROS_ERROR("Cannot takeoff: no initial position available");
        return false;
    }
    
    setpoint_raw_.header.stamp = ros::Time::now();
    setpoint_raw_.coordinate_frame = mavros_msgs::PositionTarget::FRAME_LOCAL_NED;
    setpoint_raw_.type_mask = 8 + 16 + 32 + 64 + 128 + 256 + 512 + 2048; // 只控制位置
    setpoint_raw_.position.x = init_x_;
    setpoint_raw_.position.y = init_y_;
    setpoint_raw_.position.z = init_z_ + takeoff_height;
    setpoint_raw_.yaw = init_yaw_;
    
    // 先发送 setpoint 2 秒（重要！）
    ROS_INFO("Publishing setpoints before switching to OFFBOARD...");
    for(int i = 0; i < 40; ++i) { // 2 秒
        publishSetpoint();
        ros::spinOnce();
        rate.sleep();
    }
    
    last_ctl_time_ = ros::Time::now();
    
    while (ros::ok())
    {
        // 先尝试切换到 OFFBOARD 模式
        if (current_state_.mode != "OFFBOARD")
        {
            if (ros::Time::now() - last_ctl_time_ > ros::Duration(3.0))
            {
                if(auto_offboard_)
                {
                    if (set_mode_client_.call(offb_set_mode) && offb_set_mode.response.mode_sent)
                    {
                        ROS_INFO("Offboard mode request sent");
                    }
                    else
                    {
                        ROS_WARN("Failed to set OFFBOARD mode");
                    }
                } 
                else 
                {
                    ROS_INFO("Waiting for manual OFFBOARD mode switch (set auto_offboard:=true to auto switch)");
                }
                last_ctl_time_ = ros::Time::now();
            }
        }
        else // 已经在 OFFBOARD 模式
        {
            // 尝试解锁
            if (!current_state_.armed)
            {
                if (ros::Time::now() - last_ctl_time_ > ros::Duration(3.0))
                {
                    if (arming_client_.call(arm_cmd) && arm_cmd.response.success)
                    {
                        ROS_INFO("Vehicle armed successfully");
                    }
                    else
                    {
                        ROS_WARN("Failed to arm vehicle");
                    }
                    last_ctl_time_ = ros::Time::now();
                }
            }
            else // 已解锁，开始起飞
            {
                ROS_INFO("Taking off to %.2f meters...", takeoff_height);
                if (moveRelativeXYZ(0, 0, takeoff_height))
                {
                    ROS_INFO("Takeoff to %.2f meters successful.", takeoff_height);
                    return true;
                }
            }
        }
        
        // 持续发布 setpoint（非常重要！）
        publishSetpoint();
        ros::spinOnce();
        rate.sleep();
    }
    return false;   
}

bool MotionController::hover(double timeout, double z, double yaw) {
    if (!has_odom_) {
        ROS_ERROR("Cannot hover: no odometry data available");
        return false;
    }
    if (hover_flag_ == false) {
        hover_flag_ = true;
        hover_start_time_ = ros::Time::now();
        hover_target_ = getCurrentPosition();
    }
    hover_target_.z = z;
    hover_target_.yaw = yaw;
    // 角度归一化到 [-π, π]
    normalizeAngle(hover_target_.yaw);
    if ((ros::Time::now() - hover_start_time_).toSec() >= timeout) {
        hover_flag_ = false;
        ROS_INFO("Hover time completed");
        return true;
    }
    moveToPosition(hover_target_);
    return false;
}

bool MotionController::moveToPosition(const dronePose& target) {
    if (!has_odom_) {
        ROS_ERROR("Cannot move to position: no odometry data available");
        return false;
    }
        // 检查是否到达目标
        double dx = current_odom_.pose.pose.position.x - target.x;
        double dy = current_odom_.pose.pose.position.y - target.y;
        double dz = current_odom_.pose.pose.position.z - target.z;
        double dyaw = current_yaw_ - target.yaw;

        ROS_INFO("Moving to target: (%.2f, %.2f, %.2f), current: (%.2f, %.2f, %.2f), diff: (%.2f, %.2f, %.2f)", 
                 target.x, target.y, target.z,
                 current_odom_.pose.pose.position.x,
                 current_odom_.pose.pose.position.y,
                 current_odom_.pose.pose.position.z,
                 dx, dy, dz);

        // 角度归一化到 [-π, π]
        normalizeAngle(dyaw);

        if (fabs(dx) < position_tolerance_ && fabs(dy) < position_tolerance_ && fabs(dz) < position_tolerance_ && fabs(dyaw) < 0.1) {
            ROS_INFO("Reached target position");
            move_to_position_flag_ = false;
            return true;
        }
        if (move_to_position_flag_ == false) {
            move_to_position_flag_ = true;
            last_ctl_time_ = ros::Time::now();
        }

        ros::Time current_time = ros::Time::now();
        double dt = (current_time - last_ctl_time_).toSec();
        double  new_yaw = current_yaw_;
        if (dt > 0.01) { // 避免除零
            new_yaw = updateYawWithRateLimit(target.yaw, dt);
            last_ctl_time_ = current_time;
        } else {
            dt = 0.05; // 假设一个小的dt
            new_yaw = updateYawWithRateLimit(target.yaw, dt);
            last_ctl_time_ = current_time;
        }
        // publishSetpoint(setpoint); 只在最后while后发布
        mavros_msgs::PositionTarget setpoint;
        setpoint.header.stamp = ros::Time::now();
        setpoint.coordinate_frame = mavros_msgs::PositionTarget::FRAME_LOCAL_NED;
        setpoint.type_mask = /*1 + 2 + 4 */ +8 + 16 + 32 + 64 + 128 + 256 + 512 /*+ 1024 */ + 2048;
        
        setpoint.position.x = target.x;
        setpoint.position.y = target.y;
        setpoint.position.z = target.z;
        setpoint.yaw = target.yaw;
        setpoint_raw_ = setpoint;
    return false;
}

// 封装了一下, 一坨
bool MotionController::moveToXYZ(double x, double y, double z, double yaw) {
    dronePose target(x, y, z, yaw);
    return moveToPosition(target);
}

bool MotionController::moveRelativeXYZ(double dx, double dy, double dz) {
    if (!moveRelative_flag_) {
        moveRelative_flag_ = true;
        setRelativeTarget(dx, dy, dz);
        ROS_INFO("Set relative target to (%.2f, %.2f, %.2f)", dx, dy, dz);
    }
    bool has_reached = moveToPosition(relative_target_);
    if (has_reached) {
        moveRelative_flag_ = false;
    }
    return has_reached;
    // return moveToPosition(relative_target_);
}

void MotionController::setRelativeTarget(double &dx, double &dy, double &dz) {
    double target_x = current_odom_.pose.pose.position.x + dx * cos(current_yaw_) - dy * sin(current_yaw_);
    double target_y = current_odom_.pose.pose.position.y + dx * sin(current_yaw_) + dy * cos(current_yaw_);
    double target_z = current_odom_.pose.pose.position.z + dz;
    double target_yaw = current_yaw_;
    // 角度归一化到 [-π, π]
    normalizeAngle(target_yaw);
    relative_target_ = dronePose(target_x, target_y, target_z, target_yaw);
    ROS_INFO("Computed relative target: (%.2f, %.2f, %.2f), yaw: %.2f", 
             target_x, target_y, target_z, target_yaw);
}

void MotionController::setRelativeStart(bool flag) {
    moveRelative_flag_ = flag;
}


// 角度直接用位置控制
bool MotionController::moveWithVelocity(const Velocity& vel, double target_yaw) {
    if (!vel_ctl_flag_) {
        vel_ctl_flag_ = true;
    }
     // 计算时间差
    ros::Time current_time = ros::Time::now();
    double dt = (current_time - last_ctl_time_).toSec();
    if (dt < 0.01) dt = 0.05; //
    last_ctl_time_ = current_time;
    double new_yaw = updateYawWithRateLimit(target_yaw, dt);

    mavros_msgs::PositionTarget setpoint;
    setpoint.header.stamp = ros::Time::now();
    setpoint.coordinate_frame = mavros_msgs::PositionTarget::FRAME_LOCAL_NED;
    setpoint.type_mask = 1 + 2 + 4 + /*8 + 16 + 32*/ + 64 + 128 + 256 + 512 /*+ 1024 */ + 2048; // 只控制速度和偏航角
    setpoint.velocity.x = vel.vx;
    setpoint.velocity.y = vel.vy;
    setpoint.velocity.z = vel.vz;
    setpoint.yaw = new_yaw;
    setpoint_raw_ = setpoint;
    return true;
}

bool MotionController::moveWithVelocity(double vx, double vy, double vz, double yaw_rate, double target_yaw) {
    Velocity vel(vx, vy, vz);
    return moveWithVelocity(vel, target_yaw);
}

bool MotionController::isArmed() const {
    return current_state_.armed;
}

// ?
bool MotionController::isInAir() const {
    return has_odom_ && current_odom_.pose.pose.position.z > (init_z_ + 0.1);
}

dronePose MotionController::getCurrentPosition() const {
    return dronePose(current_odom_.pose.pose.position.x,
                     current_odom_.pose.pose.position.y,
                     current_odom_.pose.pose.position.z,
                     current_yaw_);
}

dronePose MotionController::getInitPosition() const {
    return dronePose(init_x_, init_y_, init_z_, init_yaw_);
}

double MotionController::getCurrentYaw() const {
    return current_yaw_;
}

void MotionController::publishSetpoint() {
    setpoint_raw_pub_.publish(setpoint_raw_);
}

double MotionController::updateYawWithRateLimit(double target_yaw, double dt) {
    double yaw_diff = target_yaw - current_yaw_;
    // 角度归一化到 [-π, π]
    normalizeAngle(yaw_diff);
    
    double max_yaw_change = max_yaw_rate_ * dt;
    if (fabs(yaw_diff) > max_yaw_change) {
        yaw_diff = (yaw_diff > 0) ? max_yaw_change : -max_yaw_change;
    }
    return current_yaw_ + yaw_diff;
    // current_yaw_ += yaw_diff;
} // namespace fly_ctl

void MotionController::normalizeAngle(double& angle) {
    while (angle > M_PI) angle -= 2 * M_PI;
    while (angle < -M_PI) angle += 2 * M_PI;
}

}
