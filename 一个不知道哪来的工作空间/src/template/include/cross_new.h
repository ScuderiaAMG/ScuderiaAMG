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

// 类型枚举, 大概要把4, 5 给删掉
enum ObstacleType {
    OBSTACLE_RING_0 = 0,     // 圆环类型0（方框，用圆环方法穿越）
    OBSTACLE_RING_1 = 1,     // 圆环类型1（圆环，用圆环方法穿越）
    OBSTACLE_HORIZONTAL = 2, // 横框
    OBSTACLE_VERTICAL = 3,   // 竖框
    OBSTACLE_FLAG = 4,       // 刀旗
    OBSTACLE_FLAG_1 = 5,     // 另外一个方向的刀旗
    OBSTACLE_UNKNOWN = 99    // 未知类型
};

// 的信息
struct DetectedObstacle {
    geometry_msgs::Point position;
    int type;                        // 类型（0,1,2,3,4...）
    int id;                          // ID

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


DetectedObstacle cb_target;
DetectedObstacle current_target; // 当前目标
bool target_selected = false;  // 是否已选择目标
/************************************************************************
多检测回调函数：接收cloud_recognition的检测结果
*************************************************************************/
void obstacles_detection_cb(const cloud_recognition::Detection3DWithIDArray::ConstPtr& msg);
void obstacles_detection_cb(const cloud_recognition::Detection3DWithIDArray::ConstPtr& msg)
{
    target_selected = false;
    for (const auto& detection : msg->detections) {
        if (detection.id != OBSTACLE_RING_1) {
            ROS_INFO(" --- IGNORE --- 非圆环类型，ID=%d", detection.id);
            continue; // 只处理圆环类型
        }

        DetectedObstacle obstacle;
        obstacle.position.x = detection.point.x;
        obstacle.position.y = detection.point.y;
        obstacle.position.z = detection.point.z;
        obstacle.type = detection.id;  // 使用ID作为类型
        obstacle.id = detection.id;
        // new
        // 从plane_pose的四元数计算法向量
        if (detection.plane_pose.pose.orientation.x != 0.0 ||
            detection.plane_pose.pose.orientation.y != 0.0 ||
            detection.plane_pose.pose.orientation.z != 0.0 ||
            detection.plane_pose.pose.orientation.w != 0.0) {
            
            // 获取法向量
            tf2::Quaternion quat;
            tf2::fromMsg(detection.plane_pose.pose.orientation, quat);
            tf2::Matrix3x3 m(quat);
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

        cb_target = obstacle; // 默认选择第一个圆环为目标, 后续逻辑以后再加吧, 累了
        target_selected = true;
        // ROS_INFO("检测到圆环，ID=%d", obstacle.id);
        ROS_INFO_THROTTLE(5.0, "检测到圆环， ID=%d, 位置(%.2f, %.2f, %.2f), 法向量(%.2f, %.2f, %.2f)",
                          obstacle.id,
                          obstacle.position.x, obstacle.position.y, obstacle.position.z,
                          obstacle.normal.x, obstacle.normal.y, obstacle.normal.z);
        break; // 只选择第一个圆环
    }
}


/*****************************************************************
 * 统一穿越点生成函数：根据类型生成穿越点
*****************************************************************/
float ring_exit_distance = 0.50f; // 圆环/方框的接近和退出距离
float min_alignment_for_direct_cross = 0.95f; // 对齐度阈值
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

    if (distance > 0.05f) {
        // 检查穿越方向，确保法向量指向正确
        float dot_product = drone_to_obstacle_x * obstacle.normal.x + drone_to_obstacle_y * obstacle.normal.y;
        if (dot_product < 0) {
            // 反转法向量方向
            obstacle.normal.x = -obstacle.normal.x;
            obstacle.normal.y = -obstacle.normal.y;
        }
    }

    // 如果飞机和中心的连线, 和法向量几乎在一条线上的话, 可以直接做延长线穿一个点就可以了
    // 考虑三维空间的完整对齐度计算
    float drone_to_obstacle_z = obstacle.position.z - pz;
    float distance_3d = sqrt(drone_to_obstacle_x*drone_to_obstacle_x +
                            drone_to_obstacle_y*drone_to_obstacle_y +
                            drone_to_obstacle_z*drone_to_obstacle_z);

    // 三维点积计算对齐度
    float alignment_score = (obstacle.normal.x * drone_to_obstacle_x +
                            obstacle.normal.y * drone_to_obstacle_y +
                            obstacle.normal.z * drone_to_obstacle_z) / distance_3d;

    if (alignment_score > min_alignment_for_direct_cross) {  // 余弦值 > 0.95，约18度以内认为对齐
        geometry_msgs::Point exit_point;

        // 使用无人机到的三维方向作为穿越方向
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

    // 接近点：中心 - 法向量方向 × 接近距离
    geometry_msgs::Point approach_point;
    approach_point.x = obstacle.position.x - obstacle.normal.x * ring_exit_distance;  // 接近距离0.75米
    approach_point.y = obstacle.position.y - obstacle.normal.y * ring_exit_distance;
    approach_point.z = obstacle.position.z;

    // 退出点：中心 + 法向量方向 × 退出距离
    geometry_msgs::Point exit_point;
    exit_point.x = obstacle.position.x + obstacle.normal.x * ring_exit_distance;
    exit_point.y = obstacle.position.y + obstacle.normal.y * ring_exit_distance;
    exit_point.z = obstacle.position.z;

    obstacle.crossing_points.push_back(approach_point);
    obstacle.crossing_points.push_back(exit_point);

    ROS_INFO("生成圆环穿越点[类型%d]：接近点(%.2f,%.2f,%.2f) → 退出点(%.2f,%.2f,%.2f)",
                obstacle.type, approach_point.x, approach_point.y, approach_point.z,
                exit_point.x, exit_point.y, exit_point.z);
    
    obstacle.has_crossing_points = true;
    return true;

}

// 穿越函数
bool crossing_initialized = false;
float crossing_target_yaw = 0.0f;
int current_crossing_point_index = 0;

// 位置控制的统一穿越执行函数
bool execute_universal_crossing(float err_max);
bool execute_universal_crossing(float err_max) {

    float px = local_pos.pose.pose.position.x;
    float py = local_pos.pose.pose.position.y;
    float pz = local_pos.pose.pose.position.z;

    if (!crossing_initialized) {
        if (!target_selected) {
            ROS_WARN_THROTTLE(0.5, "未选择有效目标，无法执行穿越");
            return false;
        }
        current_target = cb_target;
        if (current_target.type != OBSTACLE_RING_1) {
            ROS_WARN("当前目标不是圆环类型，无法执行统一穿越");
            return false;
        }

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
        crossing_target_yaw = yaw;  // 默认保持当前朝向
        crossing_initialized = true;
    }

    // 获取当前穿越点
    if (current_crossing_point_index >= current_target.crossing_points.size()) {
        ROS_INFO("所有穿越点已完成");
        crossing_initialized = false; // 重置状态
        current_crossing_point_index = 0;
        return true; // 穿越完成
    }

    // 控制端
    // 获取当前目标点
    geometry_msgs::Point target_point = current_target.crossing_points[current_crossing_point_index];

    float dx = target_point.x - px;
    float dy = target_point.y - py;
    float dz = target_point.z - pz;
    float distance = sqrt(dx*dx + dy*dy + dz*dz);
    ROS_INFO("dx: %.2f, dy: %.2f, dz: %.2f", dx, dy, dz);
    if (fabs(dx) < err_max && fabs(dy) < err_max && fabs(dz) < err_max) {
        ROS_INFO("到达穿越点%d/%zu，前往下一点",
                 current_crossing_point_index + 1, current_target.crossing_points.size());
        current_crossing_point_index++;
        return false;  // 继续执行下一个点
    }
    ROS_INFO("使用位置控制前往穿越点%d/%zu，距离%.2f米",
             current_crossing_point_index + 1, current_target.crossing_points.size(), distance);
    setpoint_raw.type_mask = 8 + 16 + 32 + 64 + 128 + 256 + 512 + 2048; // 只控制位置和yaw
    setpoint_raw.coordinate_frame = 1; 
    setpoint_raw.position.x = target_point.x;
    setpoint_raw.position.y = target_point.y;
    setpoint_raw.position.z = target_point.z;
    setpoint_raw.yaw = crossing_target_yaw;
    // ROS_INFO_THROTTLE(0.1, "飞机当前的位置是(%.2f, %.2f, %.2f)，目标点是(%.2f, %.2f, %.2f)，距离%.2f米, err_max=%.2f",
    //                   px, py, pz,
    //                   target_point.x, target_point.y, target_point.z,
    //                   distance, err_max);
    ROS_INFO("飞机当前的位置是(%.2f, %.2f, %.2f)，目标点是(%.2f, %.2f, %.2f)，距离%.2f米, err_max=%.2f",
                    px, py, pz,
                    target_point.x, target_point.y, target_point.z,
                    distance, err_max);

    return false; // 继续执行当前点
}


#endif // RING_H
