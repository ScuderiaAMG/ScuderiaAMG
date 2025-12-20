// detection_processor.h
#pragma once

#include <vector>
#include <tf2/LinearMath/Quaternion.h>
#include <tf2_geometry_msgs/tf2_geometry_msgs.h>
#include "cloud_recognition/Detection3DWithID.h"
#include "cloud_recognition/Detection3DWithIDArray.h"
#include <nav_msgs/Odometry.h>

// 距离参数（定义为 const，在头文件中是安全的）
const double OFFSET_DISTANCE = 0.6;  // 偏置距离
const double L_R_DISTANCE = 1.1 / 2; // 左右距离/2
const double T_B_DISTANCE = 1.2 / 2; // 上下距离/2
const double FLAG_OFFSET = 0.4; // 刀旗偏移距离

// 外部变量声明：由使用此头文件的 .cpp 文件定义
extern nav_msgs::Odometry local_pos;

namespace detection_processor
{

    /**
     * @brief 判断一个点相对于给定平面的有符号距离。
     *        >0: 与法向量同侧，<0: 异侧。
     *
     * @param point 要判断的点
     * @param plane_pose 定义平面的位姿
     * @return double 有符号距离
     */
    inline double signedDistanceToPlane(
        const geometry_msgs::Point &point,
        const geometry_msgs::Pose &plane_pose)
    {
        tf2::Quaternion q;
        tf2::fromMsg(plane_pose.orientation, q);
        tf2::Matrix3x3 m(q);
        tf2::Vector3 normal = m.getColumn(2); // Z轴是法向量
        normal.normalize();

        tf2::Vector3 plane_origin, point_vec;
        tf2::fromMsg(plane_pose.position, plane_origin);
        tf2::fromMsg(point, point_vec);

        tf2::Vector3 diff = point_vec - plane_origin;
        return diff.dot(normal);
    }

    /**
     * @brief 核心函数：根据输入的 Detection3DWithID，根据其 ID 生成一系列新的 3D 点。
     *        生成逻辑依赖于 plane_pose 和外部变量 local_pos。
     *
     * @param detection 输入的检测信息
     * @return std::vector<Detection3DWithID> 生成的新检测点数组
     */
    inline std::vector<cloud_recognition::Detection3DWithID> generatePointsFromDetection(
        const cloud_recognition::Detection3DWithID &detection)
    {
        std::vector<cloud_recognition::Detection3DWithID> result;
        int id = detection.id;
        const geometry_msgs::Point &p = detection.point;
        const geometry_msgs::Pose &plane_pose = detection.plane_pose.pose;

        switch (id)
        {
        // --- id 0 & 1: 沿法向量生成前后点 ---
        case 0:
        case 1:
        {
            tf2::Quaternion q;
            tf2::fromMsg(plane_pose.orientation, q);
            tf2::Matrix3x3 m(q);
            tf2::Vector3 normal = m.getColumn(2);
            normal.normalize();

            // 生成两个候选点
            cloud_recognition::Detection3DWithID det_neg = detection;
            det_neg.point.x = p.x - OFFSET_DISTANCE * normal.x();
            det_neg.point.y = p.y - OFFSET_DISTANCE * normal.y();
            det_neg.point.z = p.z - OFFSET_DISTANCE * normal.z();

            cloud_recognition::Detection3DWithID det_pos = detection;
            det_pos.point.x = p.x + OFFSET_DISTANCE * normal.x();
            det_pos.point.y = p.y + OFFSET_DISTANCE * normal.y();
            det_pos.point.z = p.z + OFFSET_DISTANCE * normal.z();

            // 判断哪个点在法向量同侧
            double dist_neg = signedDistanceToPlane(det_neg.point, plane_pose);
            double dist_pos = signedDistanceToPlane(det_pos.point, plane_pose);

            bool neg_same_side = (dist_neg > 0);
            bool pos_same_side = (dist_pos > 0);

            // 确保“同侧优先”
            if (neg_same_side && !pos_same_side)
            {
                result.push_back(det_neg); // 同侧
                result.push_back(det_pos); // 异侧
            }
            else if (pos_same_side && !neg_same_side)
            {
                result.push_back(det_pos); // 同侧
                result.push_back(det_neg); // 异侧
            }
            else
            {
                // 同在一侧或都在异侧（理论上不会发生，除非平面与点重合）
                // 可以按默认顺序 push，或者报错
                result.push_back(det_neg);
                result.push_back(det_pos);
            }

            break;
        }

        // --- id 2: 左右框 + 法向偏移，排序后输出 ---
        case 2:
        {
            tf2::Quaternion q;
            tf2::fromMsg(plane_pose.orientation, q);
            tf2::Matrix3x3 m(q);
            tf2::Vector3 normal = m.getColumn(2);
            normal.normalize();

            double nx = normal.x(), ny = normal.y();
            tf2::Vector3 dir_horizontal(-ny, nx, 0.0);
            double length = dir_horizontal.length();
            if (length > 1e-6)
                dir_horizontal /= length;
            else
                dir_horizontal.setValue(1.0, 0.0, 0.0);
;
            // 生成左右基础点
            geometry_msgs::Point left_pt, right_pt;
            left_pt.x = p.x - L_R_DISTANCE * dir_horizontal.x();
            left_pt.y = p.y - L_R_DISTANCE * dir_horizontal.y();
            left_pt.z = p.z;
            right_pt.x = p.x + L_R_DISTANCE * dir_horizontal.x();
            right_pt.y = p.y + L_R_DISTANCE * dir_horizontal.y();
            right_pt.z = p.z;

            // 为每个基础点生成法向偏移点
            std::vector<cloud_recognition::Detection3DWithID> left_group, right_group;
            for (double sign : {-1.0, 1.0})
            {
                cloud_recognition::Detection3DWithID det_left = detection;
                det_left.point.x = left_pt.x + sign * OFFSET_DISTANCE * normal.x();
                det_left.point.y = left_pt.y + sign * OFFSET_DISTANCE * normal.y();
                det_left.point.z = left_pt.z + sign * OFFSET_DISTANCE * normal.z();
                left_group.push_back(det_left);

                cloud_recognition::Detection3DWithID det_right = detection;
                det_right.point.x = right_pt.x + sign * OFFSET_DISTANCE * normal.x();
                det_right.point.y = right_pt.y + sign * OFFSET_DISTANCE * normal.y();
                det_right.point.z = right_pt.z + sign * OFFSET_DISTANCE * normal.z();
                right_group.push_back(det_right);
            }

            // // 所有点一起排序：按到飞机的距离排序
            // std::vector<cloud_recognition::Detection3DWithID> left_points, right_points;
            // left_points.push_back(left_group[0]);  // 左侧近
            // left_points.push_back(left_group[1]);  // 左侧远
            // right_points.push_back(right_group[0]); // 右侧近
            // right_points.push_back(right_group[1]); // 右侧远
            // // 添加所有4个点...
            
            // 按距离排序左侧两个点
            std::sort(left_group.begin(), left_group.end(),
                      [&](const cloud_recognition::Detection3DWithID &a, const cloud_recognition::Detection3DWithID &b)
                      {
                          // 计算距离
                          double da = sqrt(pow(a.point.x - local_pos.pose.pose.position.x, 2) +
                                           pow(a.point.y - local_pos.pose.pose.position.y, 2) +
                                           pow(a.point.z - local_pos.pose.pose.position.z, 2));
                          double db = sqrt(pow(b.point.x - local_pos.pose.pose.position.x, 2) +
                                           pow(b.point.y - local_pos.pose.pose.position.y, 2) +
                                           pow(b.point.z - local_pos.pose.pose.position.z, 2));
                          return da < db;
                      });
            // 按距离排序右侧两个点
            std::sort(right_group.begin(), right_group.end(),
                      [&](const cloud_recognition::Detection3DWithID &a, const cloud_recognition::Detection3DWithID &b)
                      {
                          // 计算距离
                          double da = sqrt(pow(a.point.x - local_pos.pose.pose.position.x, 2) +
                                           pow(a.point.y - local_pos.pose.pose.position.y, 2) +
                                           pow(a.point.z - local_pos.pose.pose.position.z, 2));
                          double db = sqrt(pow(b.point.x - local_pos.pose.pose.position.x, 2) +
                                           pow(b.point.y - local_pos.pose.pose.position.y, 2) +
                                           pow(b.point.z - local_pos.pose.pose.position.z, 2));
                          return da < db;
                      });


            float dis2left = sqrt(pow(left_group[0].point.x - local_pos.pose.pose.position.x, 2) +
                                   pow(left_group[0].point.y - local_pos.pose.pose.position.y, 2) +
                                   pow(left_group[0].point.z - local_pos.pose.pose.position.z, 2));
            float dis2right = sqrt(pow(right_group[0].point.x - local_pos.pose.pose.position.x, 2) +
                                    pow(right_group[0].point.y - local_pos.pose.pose.position.y, 2) +
                                    pow(right_group[0].point.z - local_pos.pose.pose.position.z, 2));

            if(dis2left < dis2right) {
                result.push_back(left_group[0]);  // 左侧近
                result.push_back(left_group[1]);  // 左侧远
                result.push_back(right_group[1]); // 右侧远
                result.push_back(right_group[0]); // 右侧近
            }
            else{
                result.push_back(right_group[0]); // 右侧近
                result.push_back(right_group[1]); // 右侧远
                result.push_back(left_group[1]);  // 左侧远
                result.push_back(left_group[0]);  // 左侧近
            }
            break;
        }

        // --- id 3: 上下框 + 法向偏移，严格排序 ---
        case 3:
        {
            tf2::Quaternion q;
            tf2::fromMsg(plane_pose.orientation, q);
            tf2::Matrix3x3 m(q);
            tf2::Vector3 normal = m.getColumn(2);
            normal.normalize();

            // 1. 生成上、下基础点
            geometry_msgs::Point point_down, point_up;
            point_down.x = point_up.x = p.x;
            point_down.y = point_up.y = p.y;
            point_down.z = p.z - T_B_DISTANCE; // 下
            point_up.z = p.z + T_B_DISTANCE;   // 上

            // 2. 为每个基础点生成法向偏移点
            std::vector<cloud_recognition::Detection3DWithID> upper_group, lower_group;
            for (double sign : {-1.0, 1.0})
            {
                cloud_recognition::Detection3DWithID det_down = detection;
                det_down.point.x = point_down.x + sign * OFFSET_DISTANCE * normal.x();
                det_down.point.y = point_down.y + sign * OFFSET_DISTANCE * normal.y();
                det_down.point.z = point_down.z + sign * OFFSET_DISTANCE * normal.z();
                lower_group.push_back(det_down);

                cloud_recognition::Detection3DWithID det_up = detection;
                det_up.point.x = point_up.x + sign * OFFSET_DISTANCE * normal.x();
                det_up.point.y = point_up.y + sign * OFFSET_DISTANCE * normal.y();
                det_up.point.z = point_up.z + sign * OFFSET_DISTANCE * normal.z();
                upper_group.push_back(det_up);
            }

            // 按距离排序下方两个点
            std::sort(lower_group.begin(), lower_group.end(),
                      [&](const cloud_recognition::Detection3DWithID &a, const cloud_recognition::Detection3DWithID &b)
                      {
                          // 计算距离
                          double da = sqrt(pow(a.point.x - local_pos.pose.pose.position.x, 2) +
                                           pow(a.point.y - local_pos.pose.pose.position.y, 2) +
                                           pow(a.point.z - local_pos.pose.pose.position.z, 2));
                          double db = sqrt(pow(b.point.x - local_pos.pose.pose.position.x, 2) +
                                           pow(b.point.y - local_pos.pose.pose.position.y, 2) +
                                           pow(b.point.z - local_pos.pose.pose.position.z, 2));
                          return da < db;
                      });
            // 按距离排序上方两个点
            std::sort(upper_group.begin(), upper_group.end(),
                      [&](const cloud_recognition::Detection3DWithID &a, const cloud_recognition::Detection3DWithID &b)
                      {
                          // 计算距离
                          double da = sqrt(pow(a.point.x - local_pos.pose.pose.position.x, 2) +
                                           pow(a.point.y - local_pos.pose.pose.position.y, 2) +
                                           pow(a.point.z - local_pos.pose.pose.position.z, 2));
                          double db = sqrt(pow(b.point.x - local_pos.pose.pose.position.x, 2) +
                                           pow(b.point.y - local_pos.pose.pose.position.y, 2) +
                                           pow(b.point.z - local_pos.pose.pose.position.z, 2));
                          return da < db;
                      });

            result.push_back(lower_group[0]); // 下侧近
            result.push_back(lower_group[1]); // 下侧远
            result.push_back(upper_group[1]);  // 上侧远
            result.push_back(upper_group[0]);  // 上侧近
            break;
        }

      
        case 4: // 正刀旗
        
        {
            tf2::Quaternion q;
            tf2::fromMsg(plane_pose.orientation, q);
            tf2::Matrix3x3 m(q);
            tf2::Vector3 normal = m.getColumn(2); // Z轴是法向量
            normal.normalize();

            // 定义竖直方向（世界坐标系的Z轴）
            tf2::Vector3 up_vector(0, 0, 1);

            // 将法向量投影到水平面上
            tf2::Vector3 normal_horizontal = normal - normal.dot(up_vector) * up_vector;
            double horizontal_length = normal_horizontal.length();

            if (horizontal_length > 1e-6)
            {
                normal_horizontal.normalize();

                // 绕竖直轴顺时针旋转90度（从上方看）
                // 逆时针90度：(x,y) -> (-y,x)
                tf2::Vector3 rotated_direction(-normal_horizontal.y(), normal_horizontal.x(), 0);

                // 生成偏移点
                cloud_recognition::Detection3DWithID new_det = detection;
                new_det.point.x = p.x + FLAG_OFFSET * rotated_direction.x();
                new_det.point.y = p.y + FLAG_OFFSET * rotated_direction.y();
                new_det.point.z = p.z + FLAG_OFFSET * rotated_direction.z();

                result.push_back(new_det);
            }
            else
            {
                // 如果法向量几乎竖直，使用默认的X轴方向
                cloud_recognition::Detection3DWithID new_det = detection;
                new_det.point.x = p.x + FLAG_OFFSET;
                new_det.point.y = p.y;
                new_det.point.z = p.z;
                result.push_back(new_det);
            }

            break;
        }
        case 5: // 反刀旗
        {
            tf2::Quaternion q;
            tf2::fromMsg(plane_pose.orientation, q);
            tf2::Matrix3x3 m(q);
            tf2::Vector3 normal = m.getColumn(2); // Z轴是法向量
            normal.normalize();

            // 定义竖直方向（世界坐标系的Z轴）
            tf2::Vector3 up_vector(0, 0, 1);

            // 将法向量投影到水平面上
            tf2::Vector3 normal_horizontal = normal - normal.dot(up_vector) * up_vector;
            double horizontal_length = normal_horizontal.length();

            if (horizontal_length > 1e-6)
            {
                normal_horizontal.normalize();

                // 绕竖直轴顺时针旋转90度（从上方看）
                // 顺时针90度：(x,y) -> (y,-x)
                tf2::Vector3 rotated_direction(normal_horizontal.y(), -normal_horizontal.x(), 0);

                // 生成偏移点
                cloud_recognition::Detection3DWithID new_det = detection;
                new_det.point.x = p.x + FLAG_OFFSET * rotated_direction.x();
                new_det.point.y = p.y + FLAG_OFFSET * rotated_direction.y();
                new_det.point.z = p.z + FLAG_OFFSET * rotated_direction.z();

                result.push_back(new_det);
            }
            else
            {
                // 如果法向量几乎竖直，使用默认的X轴方向
                cloud_recognition::Detection3DWithID new_det = detection;
                new_det.point.x = p.x + FLAG_OFFSET;
                new_det.point.y = p.y;
                new_det.point.z = p.z;
                result.push_back(new_det);
            }

            break;
        }
        default:
            break;
        }

        return result;
    }

} // namespace detection_processor
