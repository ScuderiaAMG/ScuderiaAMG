#include <ros/ros.h>
#include <tf2/LinearMath/Quaternion.h>
#include <tf2_geometry_msgs/tf2_geometry_msgs.h>
#include <vector>
#include <visualization_msgs/MarkerArray.h>

#include "cloud_recognition/Detection3DWithID.h"
#include "cloud_recognition/Detection3DWithIDArray.h"

using cloud_recognition::Detection3DWithID;
using cloud_recognition::Detection3DWithIDArray;

// 距离参数
const double OFFSET_DISTANCE = 0.33;
const double L_R_DISTANCE = 0.55;
const double T_B_DISTANCE = 0.2;

std::vector<Detection3DWithID> processDetection(const Detection3DWithID &detection);

ros::Publisher marker_pub; // 可视化发布器

int main(int argc, char **argv)
{
    ros::init(argc, argv, "goal_generater");
    ros::NodeHandle nh;
    ros::NodeHandle pnh("~");

    std::string input_topic = "/all_plane_3d_detections";
    std::string output_topic = "output_detections";
    std::string marker_topic = "detection_markers";
    int queue_size = 10;

    pnh.getParam("input_topic", input_topic);
    pnh.getParam("output_topic", output_topic);
    pnh.getParam("queue_size", queue_size);
    pnh.getParam("marker_topic", marker_topic);

    ros::Publisher pub = nh.advertise<Detection3DWithIDArray>(output_topic, queue_size);
    marker_pub = nh.advertise<visualization_msgs::MarkerArray>(marker_topic, queue_size);

    ros::Subscriber sub = nh.subscribe<Detection3DWithIDArray>(
        input_topic, queue_size,
        [&pub](const Detection3DWithIDArray::ConstPtr &msg)
        {
            Detection3DWithIDArray output_msg;
            output_msg.header = msg->header;

            visualization_msgs::MarkerArray marker_array;
            int marker_id = 0;

            for (const auto &detection : msg->detections)
            {
                auto generated_detections = processDetection(detection);
                for (auto &new_det : generated_detections)
                {
                    new_det.header = msg->header;
                    output_msg.detections.push_back(new_det);

                    visualization_msgs::Marker marker;
                    marker.header = msg->header;
                    marker.ns = "detection_points";
                    marker.id = marker_id++;
                    marker.type = visualization_msgs::Marker::SPHERE;
                    marker.action = visualization_msgs::Marker::ADD;
                    marker.pose.position = new_det.point;
                    marker.pose.orientation.w = 1.0;
                    marker.scale.x = marker.scale.y = marker.scale.z = 0.04;

                    std_msgs::ColorRGBA color;
                    int id = new_det.id;
                    switch (id)
                    {
                    case 0:
                    case 1:
                        color.r = 0.0;
                        color.g = 0.0;
                        color.b = 1.0;
                        break; // blue
                    case 2:
                        color.r = 0.0;
                        color.g = 1.0;
                        color.b = 0.0;
                        break; // green
                    case 3:
                        color.r = 1.0;
                        color.g = 1.0;
                        color.b = 0.0;
                        break; // yellow
                    default:
                        color.r = 1.0;
                        color.g = 0.0;
                        color.b = 0.0;
                        break; // red
                    }
                    color.a = 1.0;
                    marker.color = color;

                    marker_array.markers.push_back(marker);
                }
            }

            pub.publish(output_msg);
            marker_pub.publish(marker_array);

            ROS_INFO("Generated %zu detections from %zu inputs.",
                     output_msg.detections.size(), msg->detections.size());
        });

    ROS_INFO("Detection processor node started.");
    ROS_INFO("Subscribing to: %s, Publishing to: %s", input_topic.c_str(), output_topic.c_str());
    ROS_INFO("Publishing markers to: %s", marker_topic.c_str());

    ros::spin();
    return 0;
}

std::vector<Detection3DWithID> processDetection(const Detection3DWithID &detection)
{
    std::vector<Detection3DWithID> result;
    int id = detection.id;
    const geometry_msgs::Point &p = detection.point;

    switch (id)
    {
    case 0: // obs1: 方框
    case 1: // obs2: 圆环
    {
        const geometry_msgs::Pose &pose = detection.plane_pose.pose;
        tf2::Quaternion q;
        tf2::fromMsg(pose.orientation, q);
        tf2::Matrix3x3 m(q);

        tf2::Vector3 normal = m.getColumn(2); // ✅ 获取 Z 轴（法向量）
        normal.normalize();

        double d = OFFSET_DISTANCE;
        for (double sign : {-1.0, 1.0})
        {
            Detection3DWithID new_det = detection;
            new_det.point.x = p.x + sign * d * normal.x();
            new_det.point.y = p.y + sign * d * normal.y();
            new_det.point.z = p.z + sign * d * normal.z();
            result.push_back(new_det);
        }
        break;
    }

    case 2: // obs3: 左右框
    {
        const geometry_msgs::Pose &pose = detection.plane_pose.pose;
        tf2::Quaternion q;
        tf2::fromMsg(pose.orientation, q);
        tf2::Matrix3x3 m(q);

        tf2::Vector3 normal = m.getColumn(2);
        normal.normalize();

        double nx = normal.x();
        double ny = normal.y();
        tf2::Vector3 dir_horizontal(-ny, nx, 0.0);
        double length = dir_horizontal.length();

        if (length < 1e-6)
        {
            ROS_WARN("Normal is nearly vertical; using X-axis as default horizontal direction.");
            dir_horizontal.setValue(1.0, 0.0, 0.0);
        }
        else
        {
            dir_horizontal /= length;
        }

        double d_lr = L_R_DISTANCE;
        double d_offset = OFFSET_DISTANCE;

        geometry_msgs::Point left_right_points[2];
        for (int i = 0; i < 2; ++i)
        {
            double sign_lr = (i == 0) ? -1.0 : 1.0;
            left_right_points[i].x = p.x + sign_lr * d_lr * dir_horizontal.x();
            left_right_points[i].y = p.y + sign_lr * d_lr * dir_horizontal.y();
            left_right_points[i].z = p.z;
        }

        for (int i = 0; i < 2; ++i)
        {
            const geometry_msgs::Point &base_pt = left_right_points[i];
            for (double sign_n : {-1.0, 1.0})
            {
                Detection3DWithID new_det = detection;
                new_det.point.x = base_pt.x + sign_n * d_offset * normal.x();
                new_det.point.y = base_pt.y + sign_n * d_offset * normal.y();
                new_det.point.z = base_pt.z + sign_n * d_offset * normal.z();
                result.push_back(new_det);
            }
        }
        break;
    }

    case 3: // obs4: 上下框
    {
        const geometry_msgs::Pose &pose = detection.plane_pose.pose;
        tf2::Quaternion q;
        tf2::fromMsg(pose.orientation, q);
        tf2::Matrix3x3 m(q);

        tf2::Vector3 normal = m.getColumn(2);
        normal.normalize();

        double d_tb = T_B_DISTANCE;
        double d_offset = OFFSET_DISTANCE;

        geometry_msgs::Point top_bottom_points[2];
        top_bottom_points[0].x = p.x;
        top_bottom_points[0].y = p.y;
        top_bottom_points[0].z = p.z - d_tb; // 下

        top_bottom_points[1].x = p.x;
        top_bottom_points[1].y = p.y;
        top_bottom_points[1].z = p.z + d_tb; // 上

        for (int i = 0; i < 2; ++i)
        {
            const geometry_msgs::Point &base_pt = top_bottom_points[i];
            for (double sign : {-1.0, 1.0})
            {
                Detection3DWithID new_det = detection;
                new_det.point.x = base_pt.x + sign * d_offset * normal.x();
                new_det.point.y = base_pt.y + sign * d_offset * normal.y();
                new_det.point.z = base_pt.z + sign * d_offset * normal.z();
                result.push_back(new_det);
            }
        }
        break;
    }

    default:
        break;
    }

    return result;
}