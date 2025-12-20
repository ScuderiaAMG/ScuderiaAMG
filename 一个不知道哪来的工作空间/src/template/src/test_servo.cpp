#include "template.h"
#include "servo.h"
int main(int argc, char **argv)
{
  // 防止中文输出乱码
  setlocale(LC_ALL, "");

  // 初始化ROS节点
  ros::init(argc, argv, "test_servo");
  ros::NodeHandle nh;

  // 订阅mavros相关话题
  ros::Subscriber state_sub = nh.subscribe<mavros_msgs::State>("mavros/state", 10, state_cb);
  ros::Subscriber local_pos_sub = nh.subscribe<nav_msgs::Odometry>("/mavros/local_position/odom", 10, local_pos_cb);

  // 发布无人机多维控制话题
  ros::Publisher mavros_setpoint_pos_pub = nh.advertise<mavros_msgs::PositionTarget>("/mavros/setpoint_raw/local", 100);

  // 创建服务客户端
  ros::ServiceClient arming_client = nh.serviceClient<mavros_msgs::CommandBool>("mavros/cmd/arming");
  ros::ServiceClient set_mode_client = nh.serviceClient<mavros_msgs::SetMode>("mavros/set_mode");
  ros::ServiceClient ctrl_pwm_client = nh.serviceClient<mavros_msgs::CommandLong>("mavros/cmd/command");

  // 舵机相关初始化
  Servo servo_controller;
  servo_controller.servo_init(nh);

  // 设置话题发布频率，需要大于2Hz，飞控连接有500ms的心跳包
  ros::Rate rate(20);
  ros::Time start_time = ros::Time::now();
  ros::spinOnce();

  bool step1 = false, step2 = false, step3 = false, step4 = false, step5 = false;

  while (ros::ok())
  {
      double elapsed = (ros::Time::now() - start_time).toSec();

      if (!step1 && elapsed > 1.0) {
          ROS_WARN("Triggering servo 1...");
          servo_controller.servo_control_num_better(1);
          step1 = true;
      }
      if (!step2 && elapsed > 3.0) {
          ROS_WARN("Triggering servo 2...");
          servo_controller.servo_control_num_better(2);
          step2 = true;
      }
      if (!step3 && elapsed > 5.0) {
          ROS_WARN("Triggering servo 3...");
          servo_controller.servo_control_num_better(3);
          step3 = true;
      }
      if (!step4 && elapsed > 7.0) {
          ROS_WARN("Triggering servo 4...");
          servo_controller.servo_control_num_better(4);
          step4 = true;
      }
      if (!step5 && elapsed > 10.0) {
          ROS_WARN("Triggering all servos...");
          servo_controller.servo_control_num(0,"close");
          step5 = true;
          break; // 执行完退出
      }

    ros::spinOnce();
    rate.sleep();
  }
}