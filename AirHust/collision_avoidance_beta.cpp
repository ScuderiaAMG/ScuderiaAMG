//思路：
//	****基于平面扫描的laser*****以下考虑均在body系下*******只能对前面的障碍物生效******
//	当障碍物进入飞机的安全半径时，记录处于安全半径内x>0的雷达点云，这些雷达点云的角度为death_angle
//	由于飞机自身有宽度size--->>death_angle要加上修正角度---->>360个角度除去他们得到life_angle
//	距离0/360最近的life_angle为最佳角度avoid_angle（机体系的x轴指向目标点）
//	
//Edited by Pentsinh on 12.01
#include <ros/ros.h>

//topic 头文件
#include <iostream>
#include <px4_command/command.h>
#include <std_msgs/Bool.h>
#include <geometry_msgs/Pose.h>
#include <geometry_msgs/PoseStamped.h>
#include <sensor_msgs/LaserScan.h>
#include <cmath>
#include <stdlib.h>
#include <math_utils.h>

using namespace std;
//>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>全 局 变 量<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
enum Command
{
    Move_ENU,
    Move_Body,
    Hold,
    Takeoff,
    Land,
    Arm,
    Disarm,
    Failsafe_land,
    Idle
};
//--------------------------------------------输入--------------------------------------------------
sensor_msgs::LaserScan Laser;                                   //激光雷达点云数据
geometry_msgs::PoseStamped pos_drone;                                  //无人机当前位置
Eigen::Quaterniond q_fcu;
Eigen::Vector3d Euler_fcu;
float target_x;                                                 //期望位置_x
float target_y;                                                 //期望位置_y
int range_min;                                                //激光雷达探测范围 最小角度
int range_max;                                                //激光雷达探测范围 最大角度
float last_time = 0;
float fly_height;
//--------------------------------------------算法相关--------------------------------------------------
float R_recognize;                          //飞机的避障算法生效的识别半径
float R_safe;                                      //飞机安全半径 [避障算法相关参数]
float track_angle;                              //追踪角度**********************************
vector<int> death_angle;                        // 记录处于安全半径内的雷达点云角度
int avoid_angle = 0;                      // 最佳角度avoid_angle（机体系的x轴指向目标点）
vector<int> life_angle;
float p_xy;                                                     //追踪部分位置环P*******************应该是速度系数吧
float vel_track;                                             //追踪速度*******************这里不做限幅，最后做总限幅
int flag_land;                                                  //降落标志位
//--------------------------------------------输出--------------------------------------------------
std_msgs::Bool flag_collision_avoidance;                       //是否进入避障模式标志位
float vel_sp_ENU[2];                                            //ENU下的总速度
float vel_sp_max;                                               //总速度限幅
px4_command::command Command_now;                               //发送给position_control.cpp的命令
//>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>声 明 函 数<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

void printf();                                                                       //打印函数
void printf_param();                                                                 //打印各项参数以供检查
void collision_avoidance(float target_x, float target_y);
void calculate_avoid_angle();                                               //计算death_angle，并找出life_angle和avoid_angle
// 【坐标系旋转函数】- 机体系到enu系
// input是机体系,output是惯性系，yaw_angle是当前偏航角
void rotation_yaw(float yaw_angle, float input[2], float output[2])
{
    output[0] = input[0] * cos(yaw_angle) - input[1] * sin(yaw_angle);
    output[1] = input[0] * sin(yaw_angle) + input[1] * cos(yaw_angle);
}
//>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>回 调 函 数<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
//接收雷达的数据，并做相应处理
void lidar_cb(const sensor_msgs::LaserScan::ConstPtr& scan)
{
    sensor_msgs::LaserScan Laser_tmp;
    Laser_tmp = *scan;
    Laser = *scan;
    int count;    //count = 359
    count = Laser.ranges.size();

    //剔除inf的情况
    for (int i = 0; i < count; i++)
    {
        //判断是否为inf
        int a = isinf(Laser_tmp.ranges[i]);
        //如果为inf，则赋值上一角度的值
        if (a == 1)
        {
            if (i == 0)
            {
                Laser_tmp.ranges[i] = Laser_tmp.ranges[count - 1];
            }
            else
            {
                Laser_tmp.ranges[i] = Laser_tmp.ranges[i - 1];
            }
        }

    }






}

void pos_cb(const geometry_msgs::PoseStamped::ConstPtr& msg)
{
    pos_drone = *msg;
    // Read the Quaternion from the Mavros Package [Frame: ENU]
    Eigen::Quaterniond q_fcu_enu(msg->pose.orientation.w, msg->pose.orientation.x, msg->pose.orientation.y, msg->pose.orientation.z);
    q_fcu = q_fcu_enu;
    //Transform the Quaternion to Euler Angles
    Euler_fcu = quaternion_to_euler(q_fcu);
}
//>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>主 函 数<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
int main(int argc, char** argv)
{
    ros::init(argc, argv, "collision_avoidance_beta");
    ros::NodeHandle nh("~");
    // 频率 [20Hz]
    ros::Rate rate(20.0);
    //【订阅】Lidar数据
    ros::Subscriber lidar_sub = nh.subscribe<sensor_msgs::LaserScan>("/laser/scan", 1000, lidar_cb);
    //【订阅】无人机当前位置 坐标系 NED系
    ros::Subscriber position_sub = nh.subscribe<geometry_msgs::PoseStamped>("/mavros/local_position/pose", 100, pos_cb);
    // 【发布】发送给position_control.cpp的命令
    ros::Publisher command_pub = nh.advertise<px4_command::command>("/px4/command", 10);

    //读取参数表中的参数
    nh.param<float>("target_x", target_x, 1.0); //dyx
    nh.param<float>("target_y", target_y, 0.0); //dyx
    nh.param<float>("R_recognize", R_recognize, 2);
    nh.param<float>("R_safe", R_safe, 1);
    nh.param<float>("p_xy", p_xy, 0.5);
    nh.param<float>("vel_sp_max", vel_sp_max, 0.0);
    nh.param<int>("range_min", range_min, 0.0);
    nh.param<int>("range_max", range_max, 0.0);
    nh.getParam("/px4_pos_controller/Takeoff_height", fly_height);
    //打印现实检查参数
    printf_param();

    //check paramater
    int check_flag;
    //输入1,继续，其他，退出程序
    cout << "Please check the parameter and setting，1 for go on， else for quit: " << endl;
    cin >> check_flag;
    if (check_flag != 1) return -1;

    //check arm
    int Arm_flag;
    cout << "Whether choose to Arm? 1 for Arm, 0 for quit" << endl;
    cin >> Arm_flag;
    if (Arm_flag == 1)
    {
        Command_now.command = Arm;
        command_pub.publish(Command_now);
    }
    else return -1;

    //check takeoff
    int Take_off_flag;
    cout << "Whether choose to Takeoff? 1 for Takeoff, 0 for quit" << endl;
    cin >> Take_off_flag;
    if (Take_off_flag == 1)
    {
        Command_now.command = Takeoff;
        command_pub.publish(Command_now);
    }
    else return -1;

    //check start collision_avoid
    int start_flag;
    cout << "Whether choose to Start mission? 1 for start, 0 for quit" << endl;
    cin >> start_flag;
    if (start_flag != 1) return -1;

    //初值
    vel_track = 0;



    vel_sp_ENU[0] = 0;
    vel_sp_ENU[1] = 0;

    flag_land = 0;

    int comid = 1;
    //>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Main Loop<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    while (ros::ok())
    {
        //回调一次 更新传感器状态
        //1. 更新雷达点云数据，存储在Laser中,并计算四向最小距离
        ros::spinOnce();
        collision_avoidance(target_x, target_y);

        Command_now.command = Move_ENU;     //机体系下移动
        Command_now.comid = comid;
        comid++;
        Command_now.sub_mode = 2; // xy 速度控制模式 z 位置控制模式
        Command_now.vel_sp[0] = vel_sp_ENU[0];
        Command_now.vel_sp[1] = vel_sp_ENU[1];  //ENU frame
        Command_now.pos_sp[2] = fly_height;
        Command_now.yaw_sp = track_angle;

        float abs_distance;
        abs_distance = sqrt((pos_drone.pose.position.x - target_x) * (pos_drone.pose.position.x - target_x) + (pos_drone.pose.position.y - target_y) * (pos_drone.pose.position.y - target_y));
        if (abs_distance < 0.3 || flag_land == 1)
        {
            Command_now.command = 3;     //Land
            flag_land = 1;
        }
        if (flag_land == 1) Command_now.command = Land;
        command_pub.publish(Command_now);
        //打印
        printf();
        rate.sleep();
    }
    return 0;
}




//计算death_angle，并找出life_angle，从而得到避障角avoid_angle
void calculate_avoid_angle()
{
    float correct_angle;                           //对于边缘角度的修正角
    death_angle.clear(); // 清空death_angle
    for (int i = range_min; i <= range_max; i++) {
        if (Laser.ranges[i] < R_recognize) 
        { // 如果雷达点云在安全半径内
            death_angle.push_back(i); // 记录该角度
            //以上没有考虑飞机的实际宽度
            //还需要寻找边缘角度，增加安全避障半径
           correct_angle = 0;
            correct_angle = Laser.ranges[i]/R_safe/M_PI*180;//
           for (int j = 1; j <= correct_angle; j++) {
                int adj_angle_plus = (i + j) % 360;
                int adj_angle_minus = (i - j + 360) % 360;

                // 确保调整后的角度在范围内
                if (adj_angle_plus >= range_min && adj_angle_plus <= range_max && find(death_angle.begin(), death_angle.end(), adj_angle_plus) == death_angle.end()) 
                    death_angle.push_back(adj_angle_plus);
                
                if (adj_angle_minus >= range_min && adj_angle_minus <= range_max && find(death_angle.begin(), death_angle.end(), adj_angle_minus) == death_angle.end()) 
                    death_angle.push_back(adj_angle_minus);
                
            }
        }
    }

    // 从360个角度中除去death_angle，得到life_angle
    life_angle.clear();
    for (int i = range_min; i <= range_max; i++) {
        bool is_death = false;
        for (auto death : death_angle) {
            if (i == death) {
                is_death = true;
                break;
            }
        }
        if (!is_death) life_angle.push_back(i);
    }
    
    
     ROS_INFO("Death angles:");
    for (int angle : death_angle) {
        ROS_INFO("%d ", angle);
    }
    ROS_INFO("Life angles:");
    for (int angle : life_angle) {
        ROS_INFO("%d ", angle);
    }
    

    // 找出距离0/360最近的life_angle作为avoid_angle
    avoid_angle = 0;
    int min_diff = 359;
    for (int i = 0; i < life_angle.size(); i++) 
    {
    	
         int diff_to_0 = abs(life_angle[i] - 0);
  	int diff_to_360 = abs(life_angle[i] - 360);
  	int current_diff = min(diff_to_0, diff_to_360);
  	if (current_diff < min_diff)
  	{
      	   min_diff = current_diff;
      	   avoid_angle = life_angle[i];
      	   
  	}
    }
    if (life_angle.size() == 0)//如果飞机被障碍物包围，直接降落
        flag_land = 1;
}

void collision_avoidance(float target_x, float target_y)//*******************************************************************************算法在这里
{
    
    

    // 计算追踪角度
    track_angle = atan((target_y - pos_drone.pose.position.y) / (target_x - pos_drone.pose.position.x));
    
    //计算追踪速度
    vel_track = p_xy * sqrt((target_x - pos_drone.pose.position.x) * (target_x - pos_drone.pose.position.x) + (target_y - pos_drone.pose.position.y) * (target_y - pos_drone.pose.position.y));
    if (vel_track > vel_sp_max)
        vel_track = vel_sp_max;
    //计算避障角
    calculate_avoid_angle();
    //计算世界系下的速度
    vel_sp_ENU[0] = vel_track * cos(track_angle - (float)avoid_angle * M_PI / 180);
    vel_sp_ENU[1] = vel_track * sin(track_angle - (float)avoid_angle * M_PI / 180);


}

void printf()
{
    cout << ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>collision_avoidance<<<<<<<<<<<<<<<<<<<<<<<<<<<<<" << endl;
    cout << "vel_track : " << vel_track << " [m/s] " << endl;
    cout << "vel_sp_x : " << vel_sp_ENU[0] << " [m/s] " << endl;
    cout << "vel_sp_y : " << vel_sp_ENU[1] << " [m/s] " << endl;
    cout<<"Current Position: "<<endl;
    cout<< "X: " << pos_drone.pose.position.x <<endl;
    cout<< "Y: " << pos_drone.pose.position.y <<endl;
    cout<< "Z: " << pos_drone.pose.position.z<<endl;
        cout << "target_x : " << target_x << endl;
    cout << "target_y : " << target_y << endl;
    cout<<"death_angle.size():"<<death_angle.size()<<endl;
    cout<<"life_angle.size():"<<life_angle.size()<<endl;
    if (death_angle.size() > 0)
    {
        cout << "*****************collision_avoidance working****************8" << endl;
        cout << "track_angle:" << track_angle << endl;
        cout << "avoid_angle:" << avoid_angle << endl;
        cout << "advance angle:" << track_angle - avoid_angle << endl;
    }
}

void printf_param()
{
    cout << ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Parameter <<<<<<<<<<<<<<<<<<<<<<<<<<<" << endl;
    cout << "target_x : " << target_x << endl;
    cout << "target_y : " << target_y << endl;

    cout << "R_recognize : " << R_recognize << endl;
    cout << "R_safe : " << R_safe << endl;

    cout << "p_xy : " << p_xy << endl;

    cout << "vel_sp_max : " << vel_sp_max << endl;
    cout << "range_min : " << range_min << endl;
    cout << "range_max : " << range_max << endl;
    cout << "fly heigh: " << fly_height << endl;
}













