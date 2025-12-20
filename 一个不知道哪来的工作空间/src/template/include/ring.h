#ifndef RING_H
#define RING_H

#include <ros/ros.h>
#include <vector>
#include <geometry_msgs/Point.h>
#include <geometry_msgs/PointStamped.h>
#include <nav_msgs/Odometry.h>
#include <mavros_msgs/PositionTarget.h>
#include <cloud_recognition/Detection3DWithIDArray.h>
#include <cloud_recognition/detection_processor.h> // new
#include <tf2/LinearMath/Quaternion.h>
#include <tf2_geometry_msgs/tf2_geometry_msgs.h>
#include <cmath>
#include <iostream>  // 为了使用 cout

// 刀旗
#include <geometry_msgs/PoseStamped.h>
#include <geometry_msgs/PolygonStamped.h>
#include <tf2_ros/transform_listener.h>
#include <Eigen/Geometry>


// 障碍物类型枚举, 大概要把4, 5 给删掉
enum ObstacleType {
    OBSTACLE_RING_0 = 0,     // 圆环类型0（方框，用圆环方法穿越）
    OBSTACLE_RING_1 = 1,     // 圆环类型1（圆环，用圆环方法穿越）
    OBSTACLE_HORIZONTAL = 2, // 横框
    OBSTACLE_VERTICAL = 3,   // 竖框
    OBSTACLE_FLAG = 4,       // 刀旗
    OBSTACLE_FLAG_1 = 5,     // 另外一个方向的刀旗
    OBSTACLE_UNKNOWN = 99    // 未知类型
};


struct DetectedObstacle {
    geometry_msgs::Point position;
    int type;                        // 障碍物类型（0,1,2,3,4...）
    int id;                          // 障碍物ID
    ros::Time detection_time;        // 检测时间                  // 是否有效

    // new
    geometry_msgs::Vector3 normal;   // 从plane_pose四元数计算的法向量
    // tf2::Vector3 normal;
    cloud_recognition::Detection3DWithID raw_detection; // 保存原始数据
    std::vector<geometry_msgs::Point> crossing_points; // 生成的穿越点
    bool has_crossing_points; // 是否有穿越点

    DetectedObstacle() : type(OBSTACLE_UNKNOWN), id(-1) {
        normal.x = 1.0; normal.y = 0.0; normal.z = 0.0; // 默认法向量
    }
};

// 全局变量
std::vector<DetectedObstacle> detected_obstacles;
DetectedObstacle current_target;
bool target_selected = false;

// 获取障碍物类型名称
const char* get_obstacle_type_name(int type)
{
    switch(type) {
        case OBSTACLE_RING_0: return "方框(圆环方法)";
        case OBSTACLE_RING_1: return "圆环";
        case OBSTACLE_HORIZONTAL: return "横框";
        case OBSTACLE_VERTICAL: return "竖框";
        case OBSTACLE_FLAG: return "刀旗";
        default: return "未知类型";
    }
}

/************************************************************************
角度normal化函数
*************************************************************************/
float normalize_angle(float angle) {
    while (angle > M_PI) angle -= 2*M_PI;
    while (angle < -M_PI) angle += 2*M_PI;
    return angle;
}

/************************************************************************
计算两个角的相对角度差
*************************************************************************/
float angle_difference(float target, float current) {
    float diff = target - current;
    return normalize_angle(diff);
}

/************************************************************************
偏向角计算函数: 保证飞机的姿态相对平滑
*************************************************************************/
// 平滑yaw控制变量
float target_yaw_for_smooth = 0.0;      // 目标yaw角度
float last_smooth_yaw = 0.0;            // 上次的平滑yaw
ros::Time last_yaw_update_time;         // 上次yaw更新时间
bool yaw_smooth_initialized = false;    // yaw平滑控制是否初始化
float max_yaw_rate = 2.8;               // 最大yaw角速度 (rad/s) = 160°/s - 积极但稳定
float smooth_yaw_control(float target_yaw, float current_yaw, float max_rate);
float smooth_yaw_control(float target_yaw, float current_yaw, float max_rate)
{
    ros::Time now = ros::Time::now();

    // 初始化
    if (!yaw_smooth_initialized) {
        last_smooth_yaw = current_yaw;
        last_yaw_update_time = now;
        yaw_smooth_initialized = true;
        return current_yaw;
    }

    // 计算时间差
    double dt = (now - last_yaw_update_time).toSec();
    if (dt <= 0 || dt > 0.5) {  // 防止时间异常
        last_yaw_update_time = now;
        return last_smooth_yaw;
    }

    // 计算角度差
    float angle_diff = angle_difference(target_yaw, last_smooth_yaw);

    // 限制角速度
    float max_change = max_rate * dt;
    if (fabs(angle_diff) > max_change) {
        angle_diff = (angle_diff > 0) ? max_change : -max_change;
    }

    // 更新角度
    last_smooth_yaw = normalize_angle(last_smooth_yaw + angle_diff);
    last_yaw_update_time = now;

    return last_smooth_yaw;
}

/************************************************************************
多障碍物检测回调函数：接收cloud_recognition的检测结果
*************************************************************************/
void obstacles_detection_cb(const cloud_recognition::Detection3DWithIDArray::ConstPtr& msg);
void obstacles_detection_cb(const cloud_recognition::Detection3DWithIDArray::ConstPtr& msg)
{
    detected_obstacles.clear();
    target_selected = false;

    for (const auto& detection : msg->detections) {
        // 把刀旗给删掉:
        if (detection.id == OBSTACLE_FLAG || detection.id == OBSTACLE_FLAG_1) {
            ROS_ERROR("莫名其妙出现的刀旗类型障碍物，跳过");
            continue; // 跳过刀旗类型
        } else {
            // 归一化为圆环类型:
            // detection.id = OBSTACLE_RING_1;
        }

        DetectedObstacle obstacle;
        obstacle.position.x = detection.point.x;
        obstacle.position.y = detection.point.y;
        obstacle.position.z = detection.point.z;
        obstacle.type = detection.id;  // 使用ID作为类型
        obstacle.id = detection.id;
        obstacle.detection_time = ros::Time::now();
        // new
        // 从plane_pose的四元数计算法向量
        if (detection.plane_pose.pose.orientation.x != 0.0 ||
            detection.plane_pose.pose.orientation.y != 0.0 ||
            detection.plane_pose.pose.orientation.z != 0.0 ||
            detection.plane_pose.pose.orientation.w != 0.0) {
            tf2::Quaternion quat;
            tf2::fromMsg(detection.plane_pose.pose.orientation, quat);
            tf2::Matrix3x3 m(quat);
            // obstacle.normal = m.getColumn(2); // 获取法向量
            // obstacle.normal.z = 0;
            // obstacle.normal.normalize(); // 确保法向量是单位向量
            tf2::Vector3 tmp_normal = m.getColumn(2);
            tmp_normal.setZ(0.0); // 确保垂直立环
            tmp_normal.normalize();
            obstacle.normal.x = tmp_normal.x();
            obstacle.normal.y = tmp_normal.y();
            obstacle.normal.z = tmp_normal.z();

        } else {
            // 如果没有有效的四元数，使用默认法向量
            obstacle.normal.x = 1.0;
            obstacle.normal.y = 0.0;
            obstacle.normal.z = 0.0;
        }

        obstacle.raw_detection = detection; // 后续生成穿越点时使用
        obstacle.has_crossing_points = false; // 初始没有穿越点

        detected_obstacles.push_back(obstacle);
        if (obstacle.type == OBSTACLE_RING_0) {
            ROS_INFO_THROTTLE(0.1, "检测到方框障碍物，ID=%d", obstacle.id);
        } else if (obstacle.type == OBSTACLE_RING_1) {
            ROS_INFO_THROTTLE(0.1, "检测到圆环障碍物，ID=%d", obstacle.id);
            // current_target = obstacle; // 默认选择第一个圆环为目标, 目前只考虑圆环
            // target_selected = true;
            // break; // 只选择第一个圆环
        } else {
            ROS_INFO_THROTTLE(0.1, "检测到未知类型障碍物，类型=%d, ID=%d", obstacle.type, obstacle.id);
        }
    }
    if (!target_selected) {
        ROS_WARN_THROTTLE(1.0, "没有检测到圆环类型障碍物作为目标");
    } else {
        ROS_INFO_THROTTLE(1.0, "已选择障碍物ID=%d作为当前目标", current_target.id);
    }
    ROS_INFO_THROTTLE(1.0, "检测到 %zu 个障碍物", detected_obstacles.size());
}



/*****************************************************************
 * 统一穿越点生成函数：根据障碍物类型生成穿越点
*****************************************************************/
float ring_exit_distance = 0.50f; // 圆环/方框的接近和退出距离
bool generate_universal_crossing_points(DetectedObstacle& obstacle);
bool generate_universal_crossing_points(DetectedObstacle& obstacle)
{
    obstacle.crossing_points.clear();
    
    float px = local_pos.pose.pose.position.x;
    float py = local_pos.pose.pose.position.y;
    float pz = local_pos.pose.pose.position.z;

    float drone_to_obstacle_x = obstacle.position.x - px;
    float drone_to_obstacle_y = obstacle.position.y - py;
    float distance = sqrt(drone_to_obstacle_x*drone_to_obstacle_x + drone_to_obstacle_y*drone_to_obstacle_y);

    if (distance > 0.2) {
        // 检查穿越方向，确保法向量指向正确
        float dot_product = drone_to_obstacle_x * obstacle.normal.x + drone_to_obstacle_y * obstacle.normal.y;
        if (dot_product < 0) {
            // 反转法向量方向
            obstacle.normal.x = -obstacle.normal.x;
            obstacle.normal.y = -obstacle.normal.y;
        }
    }

    // 如果飞机和障碍物中心的连线, 和障碍物法向量几乎在一条线上的话, 可以直接做延长线穿一个点就可以了
    // 考虑三维空间的完整对齐度计算
    float drone_to_obstacle_z = obstacle.position.z - pz;
    float distance_3d = sqrt(drone_to_obstacle_x*drone_to_obstacle_x +
                            drone_to_obstacle_y*drone_to_obstacle_y +
                            drone_to_obstacle_z*drone_to_obstacle_z);

    // 三维点积计算对齐度
    float alignment_score = (obstacle.normal.x * drone_to_obstacle_x +
                            obstacle.normal.y * drone_to_obstacle_y +
                            obstacle.normal.z * drone_to_obstacle_z) / distance_3d;

    if (alignment_score > 0.95) {  // 余弦值 > 0.95，约18度以内认为对齐
        geometry_msgs::Point exit_point;

        // 使用无人机到障碍物的三维方向作为穿越方向
        float normalized_dx = drone_to_obstacle_x / distance_3d;
        float normalized_dy = drone_to_obstacle_y / distance_3d;
        float normalized_dz = drone_to_obstacle_z / distance_3d;

        exit_point.x = obstacle.position.x + normalized_dx * ring_exit_distance;
        exit_point.y = obstacle.position.y + normalized_dy * ring_exit_distance;
        exit_point.z = obstacle.position.z + normalized_dz * ring_exit_distance;

        obstacle.crossing_points.push_back(exit_point);

        ROS_INFO("圆环或方框[%d]几乎正对飞行方向(3D对齐度%.2f), 采用直接穿越策略: (%.2f, %.2f, %.2f)",
                    obstacle.type, alignment_score, exit_point.x, exit_point.y, exit_point.z);
        
        obstacle.has_crossing_points = true;
        return true;
    }

    // 接近点：障碍物中心 - 法向量方向 × 接近距离
    geometry_msgs::Point approach_point;
    approach_point.x = obstacle.position.x - obstacle.normal.x * ring_exit_distance;  // 接近距离0.75米
    approach_point.y = obstacle.position.y - obstacle.normal.y * ring_exit_distance;
    approach_point.z = obstacle.position.z;

    // 退出点：障碍物中心 + 法向量方向 × 退出距离
    geometry_msgs::Point exit_point;
    exit_point.x = obstacle.position.x + obstacle.normal.x * ring_exit_distance;
    exit_point.y = obstacle.position.y + obstacle.normal.y * ring_exit_distance;
    exit_point.z = obstacle.position.z;

    obstacle.crossing_points.push_back(approach_point);
    obstacle.crossing_points.push_back(exit_point);

    ROS_INFO("生成圆环/方框穿越点[类型%d]：接近点(%.2f,%.2f,%.2f) → 退出点(%.2f,%.2f,%.2f)",
                obstacle.type, approach_point.x, approach_point.y, approach_point.z,
                exit_point.x, exit_point.y, exit_point.z);
    
    obstacle.has_crossing_points = true;
    return true;

}

/************************************************************************
统一穿越执行函数：按顺序飞向所有穿越点
*************************************************************************/
bool speed_mode = false; // 全局速度模式标志(在yaml中读取为false, 则全程位置控制 )
int current_crossing_point_index = 0;
bool crossing_initialized = false;
float crossing_target_yaw = 0.0; // 初始化的时候赋值
float max_cross_vel = 2.2f; // 最大穿越速度 (m/s)

bool execute_universal_crossing(float cross_speed, float err_max);
bool execute_universal_crossing(float cross_speed, float err_max)
{
    float px = local_pos.pose.pose.position.x;
    float py = local_pos.pose.pose.position.y;
    float pz = local_pos.pose.pose.position.z;

    // 初始化穿越（只执行一次）
    if (!crossing_initialized) {
        current_target = detected_obstacles[0]; // 默认选择第一个圆环为目标
        target_selected = true;
        // 检查是否距离过近，直接当作穿过
        float dx = current_target.position.x - px;
        float dy = current_target.position.y - py;
        float distance = sqrt(dx*dx + dy*dy);

        // 生成穿越点
        if (!current_target.has_crossing_points) {
            if (!generate_universal_crossing_points(current_target)) {
                ROS_ERROR("生成穿越点失败，无法执行穿越");
                return false;
            }
        }

        if (current_target.crossing_points.empty()) {
            ROS_ERROR("穿越点为空，无法执行穿越");
            return false;
        }

        if (current_target.crossing_points.size() >= 2) {
            geometry_msgs::Point second_last = current_target.crossing_points[current_target.crossing_points.size()-2];
            geometry_msgs::Point first_last = current_target.crossing_points[current_target.crossing_points.size()-1];
            float forward_dx = first_last.x - second_last.x;
            float forward_dy = first_last.y - second_last.y;
            if (sqrt(forward_dx*forward_dx + forward_dy*forward_dy) > 0.3) {
                crossing_target_yaw = atan2(forward_dy, forward_dx);  // 朝向穿越前进方向
            }
        }
        else if (current_target.crossing_points.size() == 1) {
            // 如果只有一个点，直接朝向该点
            crossing_target_yaw = atan2(current_target.crossing_points[0].y - py,
                                        current_target.crossing_points[0].x - px);
        } else {
            crossing_target_yaw = yaw;  // 默认保持当前朝向
        }   // 默认情况是什么不好说

        crossing_initialized = true;
        current_crossing_point_index = 0;

        ROS_INFO("开始统一穿越[类型%d]：%s，共%zu个穿越点",
                 current_target.type, get_obstacle_type_name(current_target.type),
                 current_target.crossing_points.size());
    }

    // 检查是否完成所有穿越点
    if (current_crossing_point_index >= current_target.crossing_points.size()) {
        ROS_INFO("统一穿越完成[类型%d]！", current_target.type);
        // 重置状态
        crossing_initialized = false;
        current_crossing_point_index = 0;
        // 悬停在最后一个点，朝向前方
        geometry_msgs::Point last_point = current_target.crossing_points.back();
        setpoint_raw.type_mask = 8 + 16 + 32 + 64 + 128 + 256 + 512 + 2048;
        setpoint_raw.coordinate_frame = 1;
        setpoint_raw.position.x = last_point.x;
        setpoint_raw.position.y = last_point.y;
        setpoint_raw.position.z = last_point.z;

        // 计算穿越完成后的前进方向（基于最后两个穿越点）
        float completion_yaw = yaw;  // 默认保持当前朝向
        if (current_target.crossing_points.size() >= 2) {
            completion_yaw = crossing_target_yaw;
        }

        // 平滑转向前方 - 完成后较快转向前方
        float smooth_completion_yaw = smooth_yaw_control(completion_yaw, yaw, max_yaw_rate * 0.9f);  // 2.5 rad/s = 143°/s
        setpoint_raw.yaw = smooth_completion_yaw;
        target_selected = false;
        ROS_INFO("统一穿越完成后悬停在最后点(%.2f, %.2f, %.2f)，朝向%.2f°",
                 last_point.x, last_point.y, last_point.z, smooth_completion_yaw * 180.0 / M_PI);
        return true;
    }


    // 控制端
    // 获取当前目标点
    geometry_msgs::Point target_point = current_target.crossing_points[current_crossing_point_index];

    // 计算到目标点的距离
    float dx = target_point.x - px;
    float dy = target_point.y - py;
    float dz = target_point.z - pz;
    float distance = sqrt(dx*dx + dy*dy + dz*dz);

    // 检查是否到达当前穿越点
    if (distance < err_max) {
        ROS_INFO("到达穿越点%d/%zu，前往下一点",
                 current_crossing_point_index + 1, current_target.crossing_points.size());
        current_crossing_point_index++;
        return false;  // 继续执行下一个点
    }

    if (!speed_mode || ((current_target.type == OBSTACLE_FLAG  || current_target.type == OBSTACLE_FLAG_1))) {
        if (current_target.type == OBSTACLE_FLAG || current_target.type == OBSTACLE_FLAG_1) {
            ROS_INFO_THROTTLE(0.1, "刀旗穿越使用位置控制"); // 这里应该不会出现刀旗
        }
        setpoint_raw.type_mask = 8 + 16 + 32 + 64 + 128 + 256 + 512 + 2048; // 只控制位置和yaw
        setpoint_raw.position.x = target_point.x;
        setpoint_raw.position.y = target_point.y;
        setpoint_raw.position.z = target_point.z;
        ROS_INFO_THROTTLE(0.02, "飞机当前的位置是(%.2f, %.2f, %.2f)", px, py, pz);
        ROS_INFO_THROTTLE(0.02, "现在是位置控制");
    } else {
            // 使用速度控制飞向目标
        float dynamic_factor = 0.8f;
        if (distance > 0.6f) {
            dynamic_factor = 0.8f;      // 远距离全速
        } 
        else if (distance > 0.4f && distance < 0.6f) {
            dynamic_factor = 0.48f;      // 中距离半速
        }
        else if (distance < 0.4f) {
            dynamic_factor = 0.15f;      // 近距离减速
        }

        // 使用速度控制飞向目标点
        setpoint_raw.type_mask = 0b101111000111;  // 速度控制模式
        setpoint_raw.coordinate_frame = 1;
        setpoint_raw.velocity.x = (dx) * cross_speed * dynamic_factor;
        setpoint_raw.velocity.y = (dy) * cross_speed * dynamic_factor;
        setpoint_raw.velocity.z = (dz) * cross_speed * dynamic_factor;

        // 对速度做一个限制
        float total_velocity = sqrt(pow(setpoint_raw.velocity.x, 2) + pow(setpoint_raw.velocity.y, 2) + pow(setpoint_raw.velocity.z, 2));
        if (total_velocity > max_cross_vel)
        {
            setpoint_raw.velocity.x *= max_cross_vel / total_velocity;
            setpoint_raw.velocity.y *= max_cross_vel / total_velocity;
            setpoint_raw.velocity.z *= max_cross_vel / total_velocity;
        }

        // 如果速度过小, 用位置控制(横框时候的修改):
        if (total_velocity < 0.5f) {
            setpoint_raw.type_mask = 8 + 16 + 32 + 64 + 128 + 256 + 512 + 2048; // 只控制位置和yaw
            setpoint_raw.position.x = target_point.x;
            setpoint_raw.position.y = target_point.y;
            setpoint_raw.position.z = target_point.z;
            ROS_INFO_THROTTLE(0.02, "飞机当前的位置是(%.2f, %.2f, %.2f)", px, py, pz);
            ROS_INFO_THROTTLE(0.02, "现在是位置控制");
        }
    }

    // 最新修改, 飞机始终不转头:
    // 智能yaw控制：平滑转向，避免急转头
    // 根据距离调整yaw控制策略 - 积极但稳定的动态调节
    float yaw_rate = max_yaw_rate;
    if (distance < 0.5f) {
        yaw_rate = max_yaw_rate * 0.6f;  // 接近目标时适度降低转向速度 (1.7 rad/s = 97°/s)
    } else if (distance > 1.0f) {
        yaw_rate = max_yaw_rate * 1.2f;  // 远离目标时允许更快转向 (3.4 rad/s = 195°/s)
    }

    float smooth_yaw = smooth_yaw_control(crossing_target_yaw, yaw, yaw_rate);
    setpoint_raw.yaw = smooth_yaw;

    ROS_INFO_THROTTLE(0.02, "统一穿越中[类型%d]: 第%d/%zu个点(%.2f,%.2f,%.2f) 距离%.2fm 速度(%.2f,%.2f,%.2f) yaw角速度%.1f°/s",
                     current_target.type, current_crossing_point_index + 1, current_target.crossing_points.size(),
                     target_point.x, target_point.y, target_point.z, distance,
                     setpoint_raw.velocity.x, setpoint_raw.velocity.y, setpoint_raw.velocity.z,
                     yaw_rate * 180.0 / M_PI);

    return false;
}

#endif // RING_H