#include "template.h"

int main(int argc, char **argv) {
    // 初始化ROS节点
    ros::init(argc, argv, "trajectory_visualizer");
    ros::NodeHandle nh;
    
    // 初始化发布器
    marker_pub = nh.advertise<visualization_msgs::Marker>("drone_trajectory", 10);
    
    // 订阅无人机位置
    ros::Subscriber pose_sub = nh.subscribe(
        "/mavros/local_position/pose", 
        10, 
        pose_callback
    );
    
    ROS_INFO("Trajectory Visualizer started. Waiting for position data...");
    
    // 设置循环频率
    ros::Rate rate(30);  // 30Hz
    
    while (ros::ok()) {
        ros::spinOnce();
        rate.sleep();
    }
    
    return 0;
}