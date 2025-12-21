//edited by Escherichia on 12.4
//edited by Escherichia on 12.9
//edited by Pentsinh on 12.11 考虑到在第一段位移中障碍物的未知影响，这个版本第一段位移不包含避障功能
//edited by Pentsinh on 12.12 算法更改，圆锥避障法
//edited by Pentsinh on 12.13 算法优化，试图解决障碍物过近时避障失效的bug，添加了刹车操作

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
float x_1;
float y_1;
float x_2;
float y_2;
int range_min;                                                //激光雷达探测范围 最小角度
int range_max;                                                //激光雷达探测范围 最大角度
float last_time = 0;
float fly_height;
//--------------------------------------------算法相关--------------------------------------------------
float track_angle;
float avoid_angle;
float R_outside, R_inside;                                       //安全半径 [避障算法相关参数]
float distance_c, angle_c;                                       //最近障碍物距离 角度
float top_angle;                                                 //圆锥顶角的一半
float p_xy;                                                     //追踪部分位置环P
float vel_track;                                             //追踪部分速度
int flag_land;                                                  //降落标志位
//--------------------------------------------输出--------------------------------------------------
std_msgs::Bool flag_collision_avoidance;                       //是否进入避障模式标志位
float vel_sp_ENU[2];                                            //ENU下的总速度
float vel_sp_max;                                               //总速度限幅
px4_command::command Command_now;                               //发送给position_control.cpp的命令
//>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>声 明 函 数<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
void turn();
void cal_min_distance();
float satfunc(float data, float Max);
void printf();                                                                       //打印函数
void printf_param();                                                                 //打印各项参数以供检查
void collision_avoidance(float target_x, float target_y);
// 【坐标系旋转函数】- 机体系到enu系
// input是机体系,output是惯性系，yaw_angle是当前偏航角
void rotation_yaw(float yaw_angle, float input[2], float output[2])
{
    output[0] = input[0] * cos(yaw_angle) - input[1] * sin(yaw_angle);
    output[1] = input[0] * sin(yaw_angle) + input[1] * cos(yaw_angle);
}
//>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>回 调 函 数<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
//接收雷达的数据，并做相应处理,然后计算前后左右四向最小距离
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
    for (int i = 0; i < count; i++)
    {
        if (i + 180 > 359) Laser.ranges[i] = Laser_tmp.ranges[i - 180];
        else Laser.ranges[i] = Laser_tmp.ranges[i + 180];
        //cout<<"tmp: "<<i<<" l:"<<Laser_tmp.ranges[i]<<"|| Laser: "<<Laser.ranges[i]<<endl;
    }
    //cout<<"//////////////"<<endl;
    //计算前后左右四向最小距离
    cal_min_distance();

    cal_min_distance();
    cal_min_distance();
    cal_min_distance();
    cal_min_distance();
    cal_min_distance();
    cal_min_distance();
    cal_min_distance();

    cal_min_distance();

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
    ros::init(argc, argv, "collision_avoidance");
    ros::NodeHandle nh("~");
    // 频率 [20Hz]
    ros::Rate rate(20.0);
    //【订阅】Lidar数据
    //ros::Subscriber lidar_sub = nh.subscribe<sensor_msgs::LaserScan>("/scan", 1000, lidar_cb);
    ros::Subscriber lidar_sub = nh.subscribe<sensor_msgs::LaserScan>("/scan", 1000, lidar_cb);
    //【订阅】无人机当前位置 坐标系 NED系
    ros::Subscriber position_sub = nh.subscribe<geometry_msgs::PoseStamped>("/mavros/local_position/pose", 100, pos_cb);
    // 【发布】发送给position_control.cpp的命令
    ros::Publisher command_pub = nh.advertise<px4_command::command>("/px4/command", 10);

    //读取参数表中的参数
    nh.param<float>("x_1", x_1, 0.7); //dyx
    nh.param<float>("y_1", y_1, 0.0); //dyx

    nh.param<float>("x_2", x_2, 0.7);
    nh.param<float>("y_2", y_2, 3.0);

    nh.param<float>("R_outside", R_outside, 1.4);
    nh.param<float>("R_inside", R_inside, 0.42);

    nh.param<float>("p_xy", p_xy, 0.5);
    nh.param<float>("p_xy", p_xy, 0.5);

    nh.param<float>("vel_sp_max", vel_sp_max, 0.0);

    nh.param<int>("range_min", range_min, 0.0);
    nh.param<int>("range_max", range_max, 0.0);
//  nh.getParam("fly_height", fly_height);
    nh.param<int>("fly_height", fly_height, 0.5);


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
    cout << "Whether choose to Start mission_1? 1 for start, 0 for quit" << endl;
    cin >> start_flag;
    if (start_flag != 1) return -1;

    //初值
    track_angle = 0;

    vel_track = 0;



    vel_sp_ENU[0] = 0;
    vel_sp_ENU[1] = 0;

    flag_land = 0;

    target_x = x_1;
    target_y = y_1;

    //检查激光雷达
    //ros::spinOnce();
    //if (Laser.ranges.size() == 0)
    //    return -1;

    int comid = 1;
    //>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Main Loop<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    while (ros::ok() && track_angle < 90)
    {
        //回调一次 更新传感器状态
        //1. 更新雷达点云数据，存储在Laser中,并计算四向最小距离
        ros::spinOnce();

        

        Command_now.command = Move_ENU;     //机体系下移动

        Command_now.sub_mode = 0;//第一段采用距离控制
        Command_now.pos_sp[0] = target_x;
        Command_now.pos_sp[1] = target_y;
        Command_now.pos_sp[2] = fly_height;
        Command_now.yaw_sp = track_angle;
        Command_now.comid = comid;
        comid++;

        float abs_distance;
        abs_distance = sqrt((pos_drone.pose.position.x - target_x) * (pos_drone.pose.position.x - target_x) + (pos_drone.pose.position.y - target_y) * (pos_drone.pose.position.y - target_y));
        if (abs_distance < 0.3)
        {
            turn();
        }
        /*if (abs_distance < 0.3 && track_angle == 90)
        {
            break;
        }*/
        if (flag_land == 1) Command_now.command = Land;
        command_pub.publish(Command_now);
        //打印
        printf();
        rate.sleep();
    }
    //int i = 0;
    //while (ros::ok()&&i<=60)
    //{
    //    ros::spinOnce();
    //    Command_now.command = Move_ENU;     //机体系下移动
    //    Command_now.sub_mode = 0;
    //    Command_now.pos_sp[0] = target_x;
    //    Command_now.pos_sp[1] = target_y;
    //    Command_now.pos_sp[2] = fly_height;
    //    Command_now.yaw_sp = track_angle;//这里track_angle不再变化
    //    Command_now.comid = comid;
    //    comid++;
    //    cout << "wait " << i << "/ 60" << endl;
    //    i++;
    //}


    target_x = x_2;
    target_y = y_2;

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


void turn()
{
    track_angle = track_angle + 1;
}

//计算前后左右四向最小距离
void cal_min_distance()
{
    distance_c = Laser.ranges[range_min];
    angle_c = 0;
    for (int i = range_min; i <= range_max; i++)
    {
        if (Laser.ranges[i] < distance_c)
        {
            distance_c = Laser.ranges[i];
            angle_c = i;
        }
    }
}

//饱和函数
float satfunc(float data, float Max)
{
    if (abs(data) > Max) return (data > 0) ? Max : -Max;
    else return data;
}

void collision_avoidance(float target_x, float target_y)
{
    //计算追踪角度
    track_angle = atan2((target_y - pos_drone.pose.position.y), (target_x - pos_drone.pose.position.x));
    if (track_angle < 0)
        track_angle = track_angle + 2 * M_PI;
    track_angle = track_angle / M_PI * 180;//弧度转角度0-359.99

    //avoid_angle初始化
    avoid_angle = track_angle;

    
    if (fabs(R_inside) <= fabs(distance_c))//如果障碍物未进入R_inside
    {
        //计算圆锥顶角的一半
        top_angle = asin(R_inside / distance_c) / M_PI * 180;

        //判断障碍物是否当道
        bool Is_in = false;
        if (fabs(angle_c - 360) < top_angle || angle_c < top_angle)
            Is_in = true;


        //根据最小距离和是否当道判断：是否启用避障策略
        if (distance_c >= R_outside || !Is_in)
        {
            flag_collision_avoidance.data = false;
        }
        else
        {
            flag_collision_avoidance.data = true;
        }



        // 避障策略
        if (flag_collision_avoidance.data == true)
        {
            if (angle_c < 180)
                avoid_angle = (int)(avoid_angle + (int)(angle_c - top_angle + 360) % 360) % 360;
            else
                avoid_angle = (int)(avoid_angle + (int)(angle_c + top_angle - 360) % 360) % 360;
        }

    }
    else//如果飞机已经进入R_inside，设法退出R_inside，采用给一个向后的速度达到刹车的效果，具体刹车效果受多方因素影响：周围障碍物的密集程度、飞机的速度、飞机的性能。。。
        avoid_angle = ((int)avoid_angle + ((int)angle_c + 180) % 360) % 360;
        
    //上面三处长计算式首先计算了机体系的避障角，然后转到世界，多次取余目的是确保角度在0-359.99
  


    //计算追踪速度
    vel_track = p_xy * sqrt((target_x - pos_drone.pose.position.x) * (target_x - pos_drone.pose.position.x) + (target_y - pos_drone.pose.position.y) * (target_y - pos_drone.pose.position.y));
   
    //速度限幅
    vel_track = satfunc(vel_track, vel_sp_max);
    
  

    //根据追踪速度的避障角计算世界系下的速度
    vel_sp_ENU[0] = vel_track * cos(avoid_angle / 180 * M_PI);
    vel_sp_ENU[1] = vel_track * sin(avoid_angle / 180 * M_PI);

}

void printf()
{
    cout << ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>collision_avoidance<<<<<<<<<<<<<<<<<<<<<<<<<<<<<" << endl;
    cout << "Minimun_distance : " << endl;
    cout << "Distance : " << distance_c << " [m] " << endl;
    cout << "Angle :    " << angle_c << " [du] " << endl;
    if (flag_collision_avoidance.data == true)
    {
        cout << "Collision avoidance Enabled " << endl;
    }
    else
    {
        cout << "Collision avoidance Disabled " << endl;
    }
    cout << "vel_track : " << vel_track << " [m/s] " << endl;
    cout << "X:" << pos_drone.pose.position.x << endl;
    cout << "Y:" << pos_drone.pose.position.y << endl;
    cout << "top_angle :" << top_angle << "[deg]" << endl;
    cout << "track_angle :" << track_angle << "[deg]" << endl;
    cout << "avoid_angle :" << avoid_angle << "[deg]" << endl;

    cout << "vel_sp_x : " << vel_sp_ENU[0] << " [m/s] " << endl;
    cout << "vel_sp_y : " << vel_sp_ENU[1] << " [m/s] " << endl;
}

void printf_param()
{
    cout << ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Parameter <<<<<<<<<<<<<<<<<<<<<<<<<<<" << endl;
    cout << "x_1 : " << x_1 << endl;
    cout << "y_1 : " << y_1 << endl;

    cout << "x_2 : " << x_2 << endl;
    cout << "y_2 : " << y_2 << endl;

    cout << "R_outside : " << R_outside << endl;
    cout << "R_inside : " << R_inside << endl;

    cout << "p_xy : " << p_xy << endl;

    cout << "vel_sp_max : " << vel_sp_max << endl;
    cout << "range_min : " << range_min << endl;
    cout << "range_max : " << range_max << endl;
    cout << "fly heigh: " << fly_height << endl;
}







