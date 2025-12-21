// collision_avoidance.cpp
// written by escherichia on 12.4

#include <ros/ros.h>

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
sensor_msgs::LaserScan Laser;                  // 激光雷达点云数据
geometry_msgs::PoseStamped pos_drone;          // 无人机当前位置
Eigen::Quaterniond q_fcu;
Eigen::Vector3d Euler_fcu;
float target_x;                                // 期望位置_x
float target_y;                                // 期望位置_y
int range_min;                                 // 激光雷达探测范围 最小角度
int range_max;                                 // 激光雷达探测范围 最大角度
float last_time = 0;
float fly_height;
//--------------------------------------------算法相关--------------------------------------------------

float R_outside,R_inside;                      // 安全半径 [避障算法相关参数]

float p_R;                                     // 大圈比例参数
float p_r;                                     // 小圈比例参数

float distance_c,angle_c;                      // 最近障碍物距离 角度
float distance_cx,distance_cy;                 // 最近障碍物距离XY

float vel_collision[2];                        // 躲避障碍部分速度
float vel_collision_max;                       // 躲避障碍部分速度限幅

float p_xy;                                    // 追踪部分位置环P
float vel_track[2];                            // 追踪部分速度
float vel_track_max;                           // 追踪部分速度限幅
int flag_land;                                 // 降落标志位
//--------------------------------------------输出--------------------------------------------------

std_msgs::Bool flag_collision_avoidance;       // 是否进入避障模式标志位
float vel_sp_body[2];                          // 总速度
float vel_sp_ENU[2];                           // ENU下的总速度
float vel_sp_max;                              // 总速度限幅
//>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>声 明 函 数<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

px4_command::command Command_now;              // 发送给position_control.cpp的命令

// 声明函数
void cal_min_distance();
float satfunc(float data, float Max);
void printf(); // 打印函数
void printf_param(); // 打印各项参数以供检查
void collision_avoidance(float target_x,float target_y);
// 【坐标系旋转函数】- 机体系到enu系
// input是机体系,output是惯性系，yaw_angle是当前偏航角
void rotation_yaw(float yaw_angle, float input[2], float output[2]);

//>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>回 调 函 数<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

// 接收雷达的数据，并做相应处理,然后计算前后左右四向最小距离
void lidar_cb(const sensor_msgs::LaserScan::ConstPtr& scan)
{
    sensor_msgs::LaserScan Laser_tmp = *scan;
    Laser = *scan;
    int count = Laser.ranges.size();

    // 剔除inf的情况
    for(int i = 0; i < count; i++)
    {
        if(isinf(Laser_tmp.ranges[i]))
        {
            if(i == 0)
            {
                Laser_tmp.ranges[i] = Laser_tmp.ranges[count-1];
            }
            else
            {
                Laser_tmp.ranges[i] = Laser_tmp.ranges[i-1];
            }
        }
    }

    for(int i = 0; i < count; i++)
    {
        if(i+180 > 359) Laser.ranges[i] = Laser_tmp.ranges[i-180];
        else Laser.ranges[i] = Laser_tmp.ranges[i+180];
        //cout<<"tmp: "<<i<<" l:"<<Laser_tmp.ranges[i]<<"|| Laser: "<<Laser.ranges[i]<<endl;

    }
    //cout<<"//////////////"<<endl;
   //计算前后左右四向最小距离
    cal_min_distance();
}

// 处理无人机当前位置的回调函数
void pos_cb(const geometry_msgs::PoseStamped::ConstPtr &msg)
{
    pos_drone = *msg;
    // Read the Quaternion from the Mavros Package [Frame: ENU]
    Eigen::Quaterniond q_fcu_enu(msg->pose.orientation.w, msg->pose.orientation.x, msg->pose.orientation.y, msg->pose.orientation.z);
    q_fcu = q_fcu_enu;
    //Transform the Quaternion to Euler Angles
    Euler_fcu = quaternion_to_euler(q_fcu);
}

// 计算前后左右四向最小距离
void cal_min_distance()
{
    distance_c = Laser.ranges[range_min];
    angle_c = range_min;
    for (int i = range_min; i <= range_max; i++)
    {
        if(Laser.ranges[i] < distance_c && Laser.ranges[i] != INFINITY)
        {
            distance_c = Laser.ranges[i];
            angle_c = i;
        }
    }
}

// 饱和函数
float satfunc(float data, float Max)
{
    if(abs(data)>Max)
    {
        return ( data > 0 ) ? Max : -Max;
    }
    else 
    {
        return data;
    }
}

// 避障算法核心函数
void collision_avoidance(float target_x,float target_y)
{
    // 根据最小距离判断是否启用避障策略
    if (distance_c >= R_outside)
    {
        flag_collision_avoidance.data = false;
    }
    else
    {
        flag_collision_avoidance.data = true;
    }

    // 计算追踪速度
    vel_track[0] = p_xy * (target_x - pos_drone.pose.position.x);
    vel_track[1] = p_xy * (target_y - pos_drone.pose.position.y);

    // 速度限幅
    for (int i = 0; i < 2; i++)
    {
        vel_track[i] = satfunc(vel_track[i], vel_track_max);
    }

    vel_collision[0] = 0;
    vel_collision[1] = 0;

    // 避障策略
    if(flag_collision_avoidance.data == true)
    {
        // 计算障碍物相对于无人机的位置
        distance_cx = distance_c * cos(((angle_c)*3.1415926)/180);
        distance_cy = distance_c * sin(((angle_c)*3.1415926)/180);

        // 使用人工势场法计算避障速度，添加虚拟势场以避免陷入局部最小值
        float virtual_repulsive_force = 0.5; // 虚拟排斥力，需要根据实际情况调整
        if(distance_c < R_inside) // 当障碍物过近时，增加虚拟排斥力
        {
            virtual_repulsive_force = 2.0;
        }

        // 计算避障速度，考虑虚拟势场
        vel_collision[0] = virtual_repulsive_force * distance_cx / distance_c;
        vel_collision[1] = virtual_repulsive_force * distance_cy / distance_c;

        // 避障速度限幅
        for (int i = 0; i < 2; i++)
        {
            vel_collision[i] = satfunc(vel_collision[i], vel_collision_max);
        }
    }

    // 计算总速度
    vel_sp_body[0] = vel_track[0] + vel_collision[0];
    vel_sp_body[1] = vel_track[1] + vel_collision[1];

    // 速度限幅
    for (int i = 0; i < 2; i++)
    {
        vel_sp_body[i] = satfunc(vel_sp_body[i], vel_sp_max);
    }

    // 坐标系旋转，将速度从机体坐标系转换到ENU坐标系
    rotation_yaw(Euler_fcu[2], vel_sp_body, vel_sp_ENU);
}

// 坐标系旋转函数 - 机体系到enu系
void rotation_yaw(float yaw_angle, float input[2], float output[2])
{
    output[0] = input[0] * cos(yaw_angle) + input[1] * sin(yaw_angle);
    output[1] = -input[0] * sin(yaw_angle) + input[1] * cos(yaw_angle);
}

// 打印函数，输出无人机当前信息
void printf()
{
    cout <<">>>>>>>>>>>>>>>>>>>>>>>>>>>>>collision_avoidance<<<<<<<<<<<<<<<<<<<<<<<<<<<<<" <<endl;
    cout << "Minimun_distance : "<<endl;
    cout << "Distance : " << distance_c << " [m] "<<endl;
    cout << "Angle :    " << angle_c    << " [du] "<<endl;
    cout << "distance_cx :    " << distance_cx    << " [m] "<<endl;
    cout << "distance_cy :    " << distance_cy    << " [m] "<<endl;
    if(flag_collision_avoidance.data == true)
    {
        cout << "Collision avoidance Enabled "<<endl;
    }
    else
    {
        cout << "Collision avoidance Disabled "<<endl;
    }
    cout << "vel_track_x : " << vel_track[0] << " [m/s] "<<endl;
    cout << "vel_track_y : " << vel_track[1] << " [m/s] "<<endl;

    cout << "vel_collision_x : " << vel_collision[0] << " [m/s] "<<endl;
    cout << "vel_collision_y : " << vel_collision[1] << " [m/s] " << endl;

    cout << "vel_sp_x : " << vel_sp_ENU[0] << " [m/s] " << endl;
    cout << "vel_sp_y : " << vel_sp_ENU[1] << " [m/s] " << endl;
    cout << "Position x : " << pos_drone.pose.position.x << " [m] " << endl;
    cout << "Position y : " << pos_drone.pose.position.y << " [m] " << endl;
    cout << "Position z : " << pos_drone.pose.position.z << " [m] " << endl;
}

// 打印参数函数，输出参数以供检查
void printf_param()
{
    cout <<">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Parameter <<<<<<<<<<<<<<<<<<<<<<<<<<<" << endl;
    cout << "target_x : " << target_x << endl;
    cout << "target_y : " << target_y << endl;

    cout << "R_outside : " << R_outside << endl;
    cout << "R_inside : " << R_inside << endl;

    cout << "p_xy : " << p_xy << endl;
    cout << "vel_track_max : " << vel_track_max << endl;

    cout << "p_R : " << p_R << endl;
    cout << "p_r : " << p_r << endl;

    cout << "vel_collision_max : " << vel_collision_max << endl;

    cout << "vel_sp_max : " << vel_sp_max << endl;
    cout << "range_min : " << range_min << endl;
    cout << "range_max : " << range_max << endl;
    cout << "fly height: " << fly_height << endl;
}

//>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>主 函 数<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
int main(int argc, char **argv)
{
    // 初始化ROS节点，节点名为"collision_avoidance"
    ros::init(argc, argv, "collision_avoidance");
    ros::NodeHandle nh("~");
    // 频率 [20Hz]
    ros::Rate rate(20.0);
    //【订阅】Lidar数据
    ros::Subscriber lidar_sub = nh.subscribe<sensor_msgs::LaserScan>("/laser/scan", 1000, lidar_cb);
    //【订阅】无人机当前位置 坐标系 NED系
    ros::Subscriber position_sub = nh.subscribe<geometry_msgs::PoseStamped>("/mavros/local_position/pose", 100, pos_cb);
    // 【发布】发送给position_control.cpp的命令
    ros::Publisher command_pub = nh.advertise<px4_command::command>("/px4/command", 10);

    // 从参数服务器读取参数
    nh.param<float>("target_x", target_x, 3.0);                      // 读取目标位置x，默认值为1.0
    nh.param<float>("target_y", target_y, 3.0);                      // 读取目标位置y，默认值为0.0
    nh.param<float>("R_outside", R_outside, 2);                      // 读取安全半径R_outside，默认值为2
    nh.param<float>("R_inside", R_inside, 1);                        // 读取安全半径R_inside，默认值为1
    nh.param<float>("p_xy", p_xy, 0.5);                              // 读取位置环比例参数p_xy，默认值为0.5
    nh.param<float>("vel_track_max", vel_track_max, 0.5);            // 读取追踪速度最大值，默认值为0.5
    nh.param<float>("p_R", p_R, 0.0);                                // 读取大圈比例参数p_R，默认值为0
    nh.param<float>("p_r", p_r, 0.0);                                // 读取小圈比例参数p_r，默认值为0
    nh.param<float>("vel_collision_max", vel_collision_max, 0.0);    // 读取避障速度最大值，默认值为0
    nh.param<float>("vel_sp_max", vel_sp_max, 0.0);                  // 读取总速度最大值，默认值为0
    nh.param<int>("range_min", range_min, 0);                        // 读取激光雷达最小角度，默认值为0
    nh.param<int>("range_max", range_max, 359);                      // 读取激光雷达最大角度，默认值为359
    nh.getParam("fly_height", fly_height);   // 读取起飞高度

    // 打印参数以供检查
    printf_param();

    //check paramater
    int check_flag;
    //输入1,继续，其他，退出程序
    cout << "Please check the parameter and setting,1 for go on, else for quit: " << endl;
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
    if (Take_off_flag != 1) return -1;

    // 初始化
    vel_track[0] = 0;
    vel_track[1] = 0;
    vel_collision[0] = 0;
    vel_collision[1] = 0;
    vel_sp_body[0] = 0;
    vel_sp_body[1] = 0;
    vel_sp_ENU[0] = 0;
    vel_sp_ENU[1] = 0;
    flag_land = 0;

    int comid = 1;
    //>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Main Loop<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    while (ros::ok())
    {
        // 回调一次更新传感器状态
        ros::spinOnce();
        collision_avoidance(target_x,target_y);

        // 设置命令并发布
        Command_now.command = Move_ENU; // 设置命令为Move_ENU
        Command_now.comid = comid; // 设置命令ID
        comid++;
        Command_now.sub_mode = 2; // 设置控制模式为xy速度控制，z位置控制
        Command_now.vel_sp[0] = vel_sp_ENU[0]; // 设置x方向速度
        Command_now.vel_sp[1] = vel_sp_ENU[1]; // 设置y方向速度
        Command_now.pos_sp[2] = fly_height; // 设置z方向位置（飞行高度）
        Command_now.yaw_sp = 0 ; // 设置偏航角为0

        // 计算当前位置到目标点的距离，如果距离小于0.3米或者标志位为降落，则设置命令为降落
        float abs_distance = sqrt((pos_drone.pose.position.x - target_x) * (pos_drone.pose.position.x - target_x) + (pos_drone.pose.position.y - target_y) * (pos_drone.pose.position.y - target_y));
        if(abs_distance < 0.3 || flag_land == 1)
        {
            Command_now.command = Land; // 设置命令为Land
            flag_land = 1;
        }
        if(flag_land == 1) Command_now.command = Land; // 如果标志位为降落，则设置命令为降落
        command_pub.publish(Command_now); // 发布命令

        // 打印无人机当前信息
        printf();
        rate.sleep(); // 按照20Hz的频率休眠
    }
    return 0;
}