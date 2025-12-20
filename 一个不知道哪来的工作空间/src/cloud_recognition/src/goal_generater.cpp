#include <ros/ros.h>
#include <tf2/LinearMath/Quaternion.h>
#include <tf2_geometry_msgs/tf2_geometry_msgs.h>
#include <vector>
#include <visualization_msgs/MarkerArray.h>
#include <nav_msgs/Odometry.h>

#include "cloud_recognition/Detection3DWithID.h"
#include "cloud_recognition/Detection3DWithIDArray.h"
#include "detection_processor.h" // 包含头文件

using namespace detection_processor;

// 全局变量：用于存储无人机位置和发布器
nav_msgs::Odometry local_pos;
ros::Publisher marker_pub;

// 回调函数：接收Odometry消息
void odomCallback(const nav_msgs::Odometry::ConstPtr &msg)
{
    local_pos = *msg;
}

int main(int argc, char **argv)
{
    ros::init(argc, argv, "detection_processor");
    ros::NodeHandle nh;
    ros::NodeHandle pnh("~");

    std::string input_topic = "all_plane_3d_detections";
    std::string output_topic = "output_detections";
    std::string marker_topic = "detection_markers";
    std::string odom_topic = "/Odomotry";
    int queue_size = 10;

    // pnh.getParam("input_topic", input_topic);
    // pnh.getParam("output_topic", output_topic);
    // pnh.getParam("queue_size", queue_size);
    // pnh.getParam("marker_topic", marker_topic);
    // pnh.getParam("odom_topic", odom_topic);

    ros::Publisher pub = nh.advertise<cloud_recognition::Detection3DWithIDArray>(output_topic, queue_size);
    marker_pub = nh.advertise<visualization_msgs::MarkerArray>(marker_topic, queue_size);

    // 订阅Odometry
    ros::Subscriber odom_sub = nh.subscribe<nav_msgs::Odometry>(odom_topic, 10, odomCallback);

    // 初始化无人机位置
    local_pos.pose.pose.position.x = local_pos.pose.pose.position.y = local_pos.pose.pose.position.z = 0.0;

    // 订阅检测消息
    ros::Subscriber sub = nh.subscribe<cloud_recognition::Detection3DWithIDArray>(
        input_topic, queue_size,
        [&pub](const cloud_recognition::Detection3DWithIDArray::ConstPtr &msg)
        {
            cloud_recognition::Detection3DWithIDArray output_msg;
            output_msg.header = msg->header;

            visualization_msgs::MarkerArray marker_array;
            int marker_id = 0;

            for (const auto &detection : msg->detections)
            {
                // 调用头文件中的处理函数生成点
                auto generated_detections = generatePointsFromDetection(detection);

                // 为生成的每个点根据顺序设置不同的颜色
                for (size_t i = 0; i < generated_detections.size(); i++)
                {
                    auto &new_det = generated_detections[i];
                    new_det.header = msg->header;
                    output_msg.detections.push_back(new_det);

                    // 创建可视化标记
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
                    // 根据顺序设置颜色
                    switch (i)
                    {
                    case 0: // 第一个点 - 红色
                        color.r = 1.0;
                        color.g = 0.0;
                        color.b = 0.0;
                        color.a = 1.0;
                        break;
                    case 1: // 第二个点 - 橙色
                        color.r = 1.0;
                        color.g = 0.5;
                        color.b = 0.0;
                        color.a = 1.0;
                        break;
                    case 2: // 第三个点 - 黄色
                        color.r = 1.0;
                        color.g = 1.0;
                        color.b = 0.0;
                        color.a = 1.0;
                        break;
                    case 3: // 第四个点 - 绿色
                        color.r = 0.0;
                        color.g = 1.0;
                        color.b = 0.0;
                        color.a = 1.0;
                        break;
                    case 4: // 第五个点 - 青色
                        color.r = 0.0;
                        color.g = 1.0;
                        color.b = 1.0;
                        color.a = 1.0;
                        break;
                    case 5: // 第六个点 - 蓝色
                        color.r = 0.0;
                        color.g = 0.0;
                        color.b = 1.0;
                        color.a = 1.0;
                        break;
                    case 6: // 第七个点 - 紫色
                        color.r = 1.0;
                        color.g = 0.0;
                        color.b = 1.0;
                        color.a = 1.0;
                        break;
                    default: // 其他点 - 白色
                        color.r = 1.0;
                        color.g = 1.0;
                        color.b = 1.0;
                        color.a = 1.0;
                        break;
                    }
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
    ROS_INFO("Subscribing to odometry: %s", odom_topic.c_str());

    ros::spin();
    return 0;
}