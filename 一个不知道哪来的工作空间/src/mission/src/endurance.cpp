#include <template.h>
#include <yolo.h>
#include "cross_new.h"
#include "servo.h"
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
int box_num = 1; //投货编号

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
  cout << "===舵机偏移===" << endl;
  for(auto &it: servo_offset){
    cout << it.first << ' ' << it.second << endl;
  }
}


int main(int argc, char **argv)
{
  // 防止中文输出乱码
  setlocale(LC_ALL, "");

  // 初始化ROS节点
  ros::init(argc, argv, "template");
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

  // 新的圆环检测回调注册
  ros::Subscriber obstacles_detection_sub = nh.subscribe<cloud_recognition::Detection3DWithIDArray>("all_plane_3d_detections", 10, obstacles_detection_cb);

  //yolo相关回调
  ros::Subscriber yolo_ros_box_sub = nh.subscribe<yolov8_ros_msgs::BoundingBoxes>("/object_position", 1, yolo_ros_cb);

  //舵机相关初始化
  Servo servo_controller;
  servo_controller.servo_init(nh);

  // 设置话题发布频率，需要大于2Hz，飞控连接有500ms的心跳包
  ros::Rate rate(20);

  // 参数读取

  nh.param<float>("err_max", err_max, 0);
  nh.param<float>("if_debug", if_debug, 0);
  nh.param<float>("camera_height", camera_height, 0);
  nh.param<float>("camera_offset_body_x", camera_offset_body_x, 0);
  nh.param<float>("camera_offset_body_y", camera_offset_body_y, 0);
  nh.param<int>("circle_times_max", circle_times_max, 1);
  nh.param("num_checkpoints", num_checkpoints, 0);
  nh.param<float>("ring_exit_distance", ring_exit_distance, 0.50f);
  nh.param<float>("min_alignment_for_direct_cross", min_alignment_for_direct_cross, 0.95f);
  for(int i = 0; i < num_checkpoints; i++)
  {
      CheckPoint cp;
      nh.param("checkpoints/" + std::to_string(i) + "/x", cp.position.x, 0.0);
      nh.param("checkpoints/" + std::to_string(i) + "/y", cp.position.y, 0.0);
      checkPoints.push_back(cp);
  }
  servo_offset = {
      {0.0f, 0.0f}, // 占位
      {0.0f, 0.0f}, // front_left
      {0.0f, 0.0f}, // front_right
      {0.0f, 0.0f}, // back_left
      {0.0f, 0.0f}  // back_right
  };
  for (int i = 1; i <= 4; ++i) {
      std::string prefix = "servo_offset_" + std::to_string(i);
      nh.param<float>(prefix + "_x", servo_offset[i].first,  0.0f);
      nh.param<float>(prefix + "_y", servo_offset[i].second, 0.0f);
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
 
  setpoint_raw.type_mask = /*1 + 2 + 4 + 8 + 16 + 32*/ +64 + 128 + 256 + 512 /*+ 1024 + 2048*/;
  setpoint_raw.coordinate_frame = 1;
  setpoint_raw.position.x = 0;
  setpoint_raw.position.y = 0;
  setpoint_raw.position.z = ALTITUDE;
  setpoint_raw.yaw = 0;

  // send a few setpoints before starting
  for (int i = 100; ros::ok() && i > 0; --i)
  {
    mavros_setpoint_pos_pub.publish(setpoint_raw);
    ros::spinOnce();
    rate.sleep();
  }
  std::cout<<"ok"<<std::endl;

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
            mission_num = 20;
            last_request = ros::Time::now();
          } 
        }
	    else if(ros::Time::now() - last_request >= ros::Duration(3.0))
        {
          mission_num = 20;
          last_request = ros::Time::now();
          lib_time_init_flag = true;
        }
        break;

      //飞到投货点1
      case 20:
        if(mission_pos_cruise(checkPoints[0].position.x, checkPoints[0].position.y, ALTITUDE, 0, err_max))
        {
          mission_num = 30;
        }
        break;

      //中枢位，决定是否投货
      case 30:
        if(circle_times == circle_times_max - 1)
        {
          if_catapult = true;//最后一圈投货
          ROS_WARN("准备投货");
          circle_times++;
          mission_num = 180; //去投货
          last_request = ros::Time::now();
          after_catapult_mission_num = 191; //投货后飞向checkpoint1继续巡航
        }
        else
        {
          circle_times++;
          ROS_WARN("继续巡航，第 %d 圈", circle_times);
          mission_num = 40;
        }
        break;

      //飞向checkpoint1（角点）3.5 2.2
      case 40:
        if(mission_pos_cruise(checkPoints[1].position.x, checkPoints[1].position.y, ALTITUDE, 0, err_max))
        {
          mission_num = 41;
        }
        break;

      // 绕圈
      case 41:
        if(circle_advanced(2.5, 1.3, M_PI/50))
        {
          mission_num = 42;
        }
        break;

      case 42:
        if(mission_pos_cruise(checkPoints[1].position.x, checkPoints[1].position.y, ALTITUDE, 0, err_max))
        {
          mission_num = 50;
        }
        break;

      //飞向checkpoint2（投货点2）
      case 50:
        if(mission_pos_cruise(checkPoints[2].position.x, checkPoints[2].position.y, ALTITUDE, 0, err_max))
        {
          if(!if_catapult)
          {
            mission_num = 60; //继续巡航
          }
          else
          {
            mission_num = 180; //投货
            last_request = ros::Time::now();
            after_catapult_mission_num = 192; //投货后飞向checkpoint3继续巡航
          }
        }
        break;

      //飞向checkpoint3（角点）
      case 60:
        if(mission_pos_cruise(checkPoints[3].position.x, checkPoints[3].position.y, ALTITUDE, 0, err_max))
        {
          mission_num = 70;
        }
        break;

      //飞向checkpoint4（穿环前投货点3）
      case 70:
        if(mission_pos_cruise(checkPoints[4].position.x, checkPoints[4].position.y, ALTITUDE, 0, err_max))
        {
          if(!if_catapult)
          {
            mission_num = 75; //继续巡航
          }
          else
          {
            mission_num = 180; //投货
            last_request = ros::Time::now();
            after_catapult_mission_num = 193; //投货后飞向checkpoint5继续巡航
          }
        }
        break;
      
      case 75: //穿环
        if(execute_universal_crossing(err_max))
        {
          ROS_INFO("穿环任务完成，继续后续任务");
          mission_num = 90;
          last_request = ros::Time::now();
        }
        break;

      //飞向checkpoint5（穿环后角点）
      case 80:
        if(mission_pos_cruise(checkPoints[5].position.x, checkPoints[5].position.y, ALTITUDE, 0, err_max))
        {
          mission_num = 90;
        }
        break;

      //飞向checkpoint6（投货点4）
      case 90:
        if(mission_pos_cruise(checkPoints[6].position.x, checkPoints[6].position.y, ALTITUDE, 0, err_max))
        {
          if(!if_catapult)
          {
            mission_num = 100; //返回中枢位，继续下一圈巡航
          }
          else
          {
            mission_num = 180; //投货
            last_request = ros::Time::now();
            after_catapult_mission_num = 170; //回家
          }
        }
        break;

      case 170: //飞回起飞点
        if(mission_pos_cruise(0, 0, ALTITUDE, 0, err_max))
        {
          mission_num = 171;
        }
        break;
      
      case 171: //降落
        if(precision_land())
        {
          mission_num = -1; //任务结束
        }
        break;

      //飞向checkpoint7（角点）
      case 100:
        if(mission_pos_cruise(checkPoints[7].position.x, checkPoints[7].position.y, ALTITUDE, 0, err_max))
        {
          mission_num = 20;
        }
        break;

      case 180: //投货
        // if(current_position_cruise(0,0,ALTITUDE,0,err_max))
        if(hover(2.0))
        {
          mission_num = 181;
          yolo_start_checking = true;
          last_request = ros::Time::now();
        }
        break;
      
      case 181: //悬停
        if(yolo_found)
        {
          mission_num = 182;
          last_request = ros::Time::now();
        }
        else if(ros::Time::now() - last_request > ros::Duration(5.0)) //5秒未找到目标
        {
          ROS_WARN("未找到投货目标");
          put_target_x = checkPoints[2*(box_num-1)].position.x - servo_offset[box_num].first;
          put_target_y = checkPoints[2*(box_num-1)].position.y - servo_offset[box_num].second;
          mission_num = 182;
          last_request = ros::Time::now();
        }
        break;

      case 182:
        if(yolo_found){
          put_target_x = yolo_target_x - servo_offset[box_num].first;
          put_target_y = yolo_target_y - servo_offset[box_num].second;
        }
        mission_pos_cruise(put_target_x,put_target_y,ALTITUDE,0,err_max); //对准
        if(ros::Time::now() - last_request > ros::Duration(4.0))
        {
          mission_num = 183;
        }
        break;

      case 183:
        if(mission_pos_cruise(put_target_x,put_target_y,PUT_ALTITUDE,0,err_max)) //对准
        {
          if(lib_time_record_func(1.0, ros::Time::now()))
          mission_num = 184;
          last_request = ros::Time::now();
        }
        break;

      case 184:
        servo_controller.servo_control_num_better(box_num); //投货
        if(ros::Time::now() - last_request > ros::Duration(2.0))
        {
          yolo_start_checking = false;
          yolo_found = false;
          mission_num = 185;
          box_num ++;
          if(box_num > 4) box_num = 4; //最多4个投货点
        }
        break;

      case 185: //复位高度
        if(current_position_cruise(0,0,ALTITUDE,0,err_max))
        {
          mission_num = after_catapult_mission_num;
        }
        break;

      case 191: //第一次投货回中
        if(mission_pos_cruise(0, 0, ALTITUDE, 0, err_max))
        {
          mission_num = 50;
        }
        break;
              
      case 192: //第二次投货回中
        if(mission_pos_cruise(0, 0, ALTITUDE, 0, err_max))
        {
          mission_num = 70;
        }
        break;
              
      case 193: //第三次投货回中
        if(mission_pos_cruise(0, 0, ALTITUDE, 0, err_max))
        {
          mission_num = 90;
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


