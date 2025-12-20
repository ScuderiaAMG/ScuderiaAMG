#include <template.h>
#include <yolo.h>
#include "cross_new.h"
using namespace std;

// 全局变量定义
int mission_num = 0;
float if_debug = 0;
float err_max = 0.2;
int after_catapult_mission_num = 0; //投货后继续的任务编号
typedef struct CheckPoint
{
    geometry_msgs::Point position;
} CheckPoint;
int num_checkpoints = 0; //巡航点数量
int checkPoint_index = 0; 
vector<CheckPoint> checkPoints; //巡航点数组
int circle_times = 0; //巡航圈数计数器
int circle_times_max = 1; //最大巡航圈数
bool if_catapult = false; //是否投货标志

void print_param()
{
  cout << "=== 控制参数 ===" << endl;
  cout << "err_max: " << err_max << endl;
  cout << "ALTITUDE: " << ALTITUDE << endl;
  cout << "if_debug: " << if_debug << endl;
  if(if_debug == 1) cout << "自动offboard" << endl;
  else cout << "遥控器offboard" << endl;
  cout << "===摄像头相关===" << endl;
  cout << "fx: " << fx << ", fy: " << fy << ", cx: " << cx << ", cy: " << cy << endl;
  cout << "camera_height: " << camera_height << endl;
  cout << "camera_offset_body_x: " << camera_offset_body_x << endl;
  cout << "camera_offset_body_y: " << camera_offset_body_y << endl;
  cout << "=== 巡航点信息 ===" << endl;
  cout << "num_checkpoints: " << num_checkpoints << endl;
  cout << "circle_times_max: " << circle_times_max << endl;
  for(int i = 0; i < num_checkpoints; i++)
  {
      cout << "CheckPoint " << i << ": (" << checkPoints[i].position.x << ", " << checkPoints[i].position.y << ")" << endl;
  }
}


int main(int argc, char **argv)
{
  // 防止中文输出乱码
  setlocale(LC_ALL, "");

  // 初始化ROS节点
  ros::init(argc, argv, "cross");
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

  // 新的多障碍物检测回调注册
  ros::Subscriber obstacles_detection_sub = nh.subscribe<cloud_recognition::Detection3DWithIDArray>("all_plane_3d_detections", 10, obstacles_detection_cb);

  // 设置话题发布频率，需要大于2Hz，飞控连接有500ms的心跳包
  ros::Rate rate(20);

  // 参数读取

  nh.param<float>("err_max", err_max, 0.15);
  nh.param<float>("if_debug", if_debug, 0);
  nh.param<float>("camera_height", camera_height, 0);
  nh.param<float>("camera_offset_body_x", camera_offset_body_x, 0);
  nh.param<float>("camera_offset_body_y", camera_offset_body_y, 0);
  nh.param<int>("circle_times_max", circle_times_max, 1);
  nh.param("num_checkpoints", num_checkpoints, 0);
  for(int i = 0; i < num_checkpoints; i++)
  {
      CheckPoint cp;
      nh.param("checkpoints/" + std::to_string(i) + "/x", cp.position.x, 0.0);
      nh.param("checkpoints/" + std::to_string(i) + "/y", cp.position.y, 0.0);
      checkPoints.push_back(cp);
  }
  print_param();

  
  int choice = 0;
  cout << "1 to go on , else to quit" << endl;
  cin >> choice;
  if (choice != 1) return 0;
  ros::spinOnce();
  rate.sleep();
  
  // 等待连接到飞控
  while (ros::ok() && !current_state.connected)
  {
    ros::spinOnce();
    rate.sleep();
  }
  //设置无人机的期望位置


  // 定义客户端变量，设置为offboard模式
  mavros_msgs::SetMode offb_set_mode;
  offb_set_mode.request.custom_mode = "OFFBOARD";

  // 定义客户端变量，请求无人机解锁
  mavros_msgs::CommandBool arm_cmd;
  arm_cmd.request.value = true;

  // 记录当前时间，并赋值给变量last_request
  ros::Time last_request = ros::Time::now();

  while (ros::ok())
  {
    if (current_state.mode != "OFFBOARD" && (ros::Time::now() - last_request > ros::Duration(3.0)))
    {
      if(if_debug == 1)
      {
        if (set_mode_client.call(offb_set_mode) && offb_set_mode.response.mode_sent)
        {
          ROS_INFO("Offboard enabled");
        }
      }
      else
      {
        ROS_INFO("Waiting for OFFBOARD mode");
      }
      last_request = ros::Time::now();
    }
    else
    {
      if (!current_state.armed && (ros::Time::now() - last_request > ros::Duration(3.0)))
      {
        if (arming_client.call(arm_cmd) && arm_cmd.response.success)
        {
          ROS_INFO("Vehicle armed");
        }
        last_request = ros::Time::now();
      }
    }
    // 当无人机到达起飞点高度后，悬停3秒后进入任务模式，提高视觉效果
    if (fabs(local_pos.pose.pose.position.z - ALTITUDE) < 0.2)
    {
      if (ros::Time::now() - last_request > ros::Duration(1.0))
      {
        mission_num = 10;
 	      last_request = ros::Time::now();
        break;
      }
    }

    mission_pos_cruise(0, 0, ALTITUDE, 0, err_max); 
    mavros_setpoint_pos_pub.publish(setpoint_raw);
    ros::spinOnce();
    rate.sleep();
  }
  

  while (ros::ok())
  {
    ROS_WARN("mission_num = %d", mission_num);
    
    switch (mission_num)
    {
      // mission1: 起飞
      case 10:
        if (mission_pos_cruise(0, 0, ALTITUDE, 0, err_max))
        {
          if(lib_time_record_func(1.0, ros::Time::now()))
          {
            mission_num = 75;
            last_request = ros::Time::now();
          } 
        }
	    else if(ros::Time::now() - last_request >= ros::Duration(10.0))
        {
          mission_num = 75;
          last_request = ros::Time::now();
          lib_time_init_flag = true;
        }
        break;

      case 75: //穿环
        if(execute_universal_crossing(err_max))
        {
          ROS_INFO("穿环任务完成，继续后续任务");
          mission_num = 171;
          last_request = ros::Time::now();
        }
        break;

      case 171: //降落
        if(precision_land())
        {
          mission_num = -1; //任务结束
        }
        break;

    }
    mavros_setpoint_pos_pub.publish(setpoint_raw);
    ros::spinOnce();
    rate.sleep();
    
    if(mission_num == -1) 
    {
      exit(0);
    }
  }
  return 0;
}


