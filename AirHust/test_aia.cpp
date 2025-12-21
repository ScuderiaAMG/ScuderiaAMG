//test.aia block XIV
//Saved by Escherichia on 11.24
//Edited by Escherichia on 11.25
//Edited by Escherichia on 11.26
//Edited by Escherichia on 11.26
//Edited by Escherichia on 11.26
//Edited by Escherichia on 11.26
//Edited by Escherichia on 11.27
//Edited by Escherichia on 11.27
//Edited by Escherichia on 11.27
//Edited by Escherichia on 11.28
//Edited by Escherichia on 11.28
//Edited by Pentsinh on 11.28
//Edited by LiuxinB on 11.29
//Edited by Escherichia on 11.29
//Edited by LiuxinB on 11.29
#include <ros/ros.h>
#include <vector>
#include <iostream>
#include <cmath>
#include <stdlib.h>
#include <px4_command/command.h>
#include <geometry_msgs/Pose.h>
#include <geometry_msgs/PoseStamped.h>
#include<std_msgs/Bool.h>
#include<math_utils.h>
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
px4_command::command Command_now;

geometry_msgs::PoseStamped pos_drone;
//---------------------------------------参数---------------------------------------------

double height; // 飞行高度
double sleep_time; // 每个点的停留时间
double radius; // 多边形的外接圆半径
double size; //边长?
double target_x;
double target_y;
double target_z;
Eigen::Quaterniond q_fcu;
Eigen::Vector3d Euler_fcu;
std::vector<float> calculateCirclePath(int points, float radius);
//-------------------------------计算圆形路径点的函数---------------------------------------
std::vector<float> calculateCirclePath(int points, float radius) {
    std::vector<float> circle;
    for (int i = 0; i < points; ++i) {
        float angle = 2 * M_PI * i / points;
        circle.push_back(radius * cos(angle));
        circle.push_back(radius * sin(angle));
    }
    return circle;
}

// 计算两个点之间的距离的函数
double calculateDistance(double current_x, double current_y, double current_z, double target_x, double target_y, double target_z)
{
    return sqrt((current_x - target_x) * (current_x - target_x) + (current_y - target_y) * (current_y - target_y)  );
}
//回调函数 
void pos_cb(const geometry_msgs::PoseStamped::ConstPtr &msg)
{
    pos_drone = *msg;
    // Read the Quaternion from the Mavros Package [Frame: ENU]
    Eigen::Quaterniond q_fcu_enu(msg->pose.orientation.w, msg->pose.orientation.x, msg->pose.orientation.y, msg->pose.orientation.z);
    q_fcu = q_fcu_enu;
    //Transform the Quaternion to Euler Angles
    Euler_fcu = quaternion_to_euler(q_fcu);
}

//>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>主 函 数<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
int main(int argc, char **argv) 
{
    ros::init(argc, argv, "polygon_and_circle");
    ros::NodeHandle nh("~");
    //订阅 
    ros::Subscriber position_sub = nh.subscribe<geometry_msgs::PoseStamped>("/mavros/local_position/pose", 100, pos_cb);
    ros::Rate rate(20.0);
    ros::Publisher move_pub = nh.advertise<px4_command::command>("/px4/command", 10);

//>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>参数读取<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    nh.param("height", height, 0.5);
    nh.param("size", size, 1.0);
    nh.param("sleep_time", sleep_time, 10.0);
    nh.param("radius", radius, 1.0);

    // 检查参数
    int check_flag;
    cout << "Parameters:" << endl;
    cout << "size: "<<size<<"[m]"<<endl;
    cout << "Height: " << height << " m" << endl;
    cout << "Sleep Time: " << sleep_time << " s" << endl;
    cout << "Radius: " << radius << " m" << endl;
    cout << "Please check the parameter and setting, 1 for go on, else for quit: " << endl;
    cin >> check_flag;
    if (check_flag != 1) {
        return -1;
    }

    //check arm
    int Arm_flag;
    cout<<"Whether choose to Arm? 1 for Arm, 0 for quit"<<endl;
    cin >> Arm_flag;
    if(Arm_flag == 1)
    {
        Command_now.command = Arm;
        move_pub.publish(Command_now);
    }
    else return -1;

    int takeoff_flag;
    cout << "Whether choose to Takeoff? 1 for Takeoff, 0 for quit "<<endl;
    cin >> takeoff_flag;
    if(takeoff_flag != 1)
    {
        return -1;
    }
    int i=0;
    int comid = 0;
     
     //>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>主程序<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    
//check takeoff
   /* int Take_off_flag;
    cout<<"Whether choose to Takeoff? 1 for Takeoff, 0 for quit"<<endl;
    cin >> Take_off_flag;
    if(Take_off_flag == 1)
    {
        Command_now.command = Takeoff;
        move_pub.publish(Command_now);
    }
    else return -1;*/

//takeoff
 i = 0;
    while (i < sleep_time*20)
    {
        Command_now.command = Move_ENU;
        Command_now.sub_mode = 0;
        Command_now.pos_sp[0] = 0;
        Command_now.pos_sp[1] = 0;
        Command_now.pos_sp[2] = height;
        Command_now.yaw_sp = 0;
        Command_now.comid = comid;
        comid++;
        move_pub.publish(Command_now);
        rate.sleep();
        cout << "Point 0----->takeoff"<<endl;
        i++;
    }







 /*   
    target_x = 0;
    target_y = 0;
    target_z = height;
    while (calculateDistance(pos_drone.pose.position.x, pos_drone.pose.position.y, pos_drone.pose.position.z, target_x, target_y, target_z) > 0.05)
    {	ros::spinOnce();
        Command_now.command = Move_ENU; 
        Command_now.sub_mode = 0;
        Command_now.pos_sp[0] = 0;
        Command_now.pos_sp[1] = 0;
        Command_now.pos_sp[2] = height;
        Command_now.yaw_sp = 0;
        Command_now.comid = comid;
        comid++;
        move_pub.publish(Command_now);
        rate.sleep();
        cout << "Point 0----->takeoff"<<endl;
    }
*/
   
    for (i = 0; i<=5; i++)
    {
	ros::spinOnce();
        target_x = size * cos(2 * M_PI * i / 5);
        target_y = size * sin(2 * M_PI * i / 5);
        target_z = height;
        while (calculateDistance(pos_drone.pose.position.x, pos_drone.pose.position.y, pos_drone.pose.position.z, target_x, target_y, target_z) > 0.1)
        {
            Command_now.command = Move_ENU;
            Command_now.sub_mode = 0;
            Command_now.pos_sp[0] = target_x;
            Command_now.pos_sp[1] = target_y;
            Command_now.pos_sp[2] = height;
            Command_now.yaw_sp = 0;
            Command_now.comid = comid;
            comid++;
            move_pub.publish(Command_now);
            rate.sleep();
            cout  <<"Point "<<i+1<<"----" << endl;
ros::spinOnce();
	    cout << "target_X: " << target_x << " target_y: " << target_y << endl;
	    cout << calculateDistance(pos_drone.pose.position.x, pos_drone.pose.position.y, pos_drone.pose.position.z, target_x, target_y, target_z) << endl;
        }

    }
    
 ros::spinOnce();   
    target_x = size*cos(0);
    target_y = size*sin(0);
    target_z = height;
    while(calculateDistance(pos_drone.pose.position.x, pos_drone.pose.position.y, pos_drone.pose.position.z, target_x, target_y, target_z) > 0.2)
    {
        Command_now.command = Move_ENU;
        Command_now.sub_mode = 0;
        Command_now.pos_sp[0] = size*cos(0);
        Command_now.pos_sp[1] = size*sin(0);
        Command_now.pos_sp[2] = height;
        Command_now.yaw_sp = 0;
        Command_now.comid = comid;
        comid++;
        move_pub.publish(Command_now);
        rate.sleep();
	    cout << "Back to Point 1-----"<<endl;        
    }
    
    
    // Fly a circle
 //   vector<float> circle = calculateCirclePath(150, radius);
 //   i=0;
 //   for(i=0;i<300;i+=2)
 //   {
 //       target_x = circle[i];
 //       target_y = circle[i + 1];
 //   	while(pos_drone.pose.position.x, pos_drone.pose.position.y, pos_drone.pose.position.z, target_x, target_y, target_z) >0.02)
 //   	{
 //      	 Command_now.command = Move_ENU;
 //      	 Command_now.sub_mode = 0;
 //        Command_now.pos_sp[0] = target_x;
 //        Command_now.pos_sp[1] = target_y;
 //      	 Command_now.pos_sp[2] = height;
 //      	 Command_now.yaw_sp = 0;
 //      	 Command_now.comid = comid;
 //      	 comid++;
 //        move_pub.publish(Command_now);
 //        rate.sleep();

 //   	}
 //   }
    
    //point return
    ros::spinOnce();
    target_x = 0;
    target_y = 0;
    target_z = height;
    while (calculateDistance(pos_drone.pose.position.x, pos_drone.pose.position.y, pos_drone.pose.position.z, target_x, target_y, target_z) > 0.2)
    {
        Command_now.command = Move_ENU;
        Command_now.sub_mode = 0;
        Command_now.pos_sp[0] = 0;
        Command_now.pos_sp[1] = 0;
        Command_now.pos_sp[2] = height;
        Command_now.yaw_sp = 0;
        Command_now.comid = comid;
        comid++;
        move_pub.publish(Command_now);
        rate.sleep();
	cout << "Back to Point 0----->to land"<<endl; 
    }

    //降落
    Command_now.command = Land;
    while (ros::ok())
    {
      move_pub.publish(Command_now);
      rate.sleep();
      cout << "Land"<<endl;
    }
    rate.sleep();
    cout << "Mission complete,existing...."<<endl;
    return 0;
    }
