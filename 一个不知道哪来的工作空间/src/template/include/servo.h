#include <ros/ros.h>
#include <std_msgs/Empty.h>
#include <std_msgs/Int32.h>

#define PUT_ALTITUDE 0.1f

//舵机偏移参数
vector<pair<float,float>> servo_offset = {
    {0.0, 0.0}, // 占位
    {0.0, 0.0}, // front_left
    {0.0, 0.0}, // front_right
    {0.0, 0.0}, // back_left
    {0.0, 0.0}  // back_right
};

class Servo{

private:
    //舵机相关订阅
    ros::Publisher servo_pub_all_open;
    ros::Publisher servo_pub_all_close;
    ros::Publisher servo_pub_front_left;
    ros::Publisher servo_pub_front_right;
    ros::Publisher servo_pub_back_left;
    ros::Publisher servo_pub_back_right;

    ros::Publisher servo_pub_front_left_open;
    ros::Publisher servo_pub_front_right_open;
    ros::Publisher servo_pub_back_left_open;
    ros::Publisher servo_pub_back_right_open;

    ros::Publisher servo_pub_front_left_close;
    ros::Publisher servo_pub_front_right_close;
    ros::Publisher servo_pub_back_left_close;
    ros::Publisher servo_pub_back_right_close;

public:

    void servo_init(ros::NodeHandle& nh)
    {
        servo_pub_all_open = nh.advertise<std_msgs::Empty>("/servo/all/open", 10);
        servo_pub_all_close = nh.advertise<std_msgs::Empty>("/servo/all/close", 10);
        servo_pub_front_left = nh.advertise<std_msgs::Int32>("/servo/front_left", 10);
        servo_pub_front_right = nh.advertise<std_msgs::Int32>("/servo/front_right", 10);
        servo_pub_back_left = nh.advertise<std_msgs::Int32>("/servo/back_left", 10);
        servo_pub_back_right = nh.advertise<std_msgs::Int32>("/servo/back_right", 10);

        servo_pub_front_left_open = nh.advertise<std_msgs::Empty>("/servo/front_left/open", 10);
        servo_pub_front_left_close = nh.advertise<std_msgs::Empty>("/servo/front_left/close", 10);
        servo_pub_front_right_open = nh.advertise<std_msgs::Empty>("/servo/front_right/open", 10);
        servo_pub_front_right_close = nh.advertise<std_msgs::Empty>("/servo/front_right/close", 10);
        
        servo_pub_back_left_open = nh.advertise<std_msgs::Empty>("/servo/back_left/open", 10);
        servo_pub_back_left_close = nh.advertise<std_msgs::Empty>("/servo/back_left/close", 10);
        servo_pub_back_right_open = nh.advertise<std_msgs::Empty>("/servo/back_right/open", 10);
        servo_pub_back_right_close = nh.advertise<std_msgs::Empty>("/servo/back_right/close", 10);
    }

    void servo_all_control(string mode="open")
    {
        std_msgs::Empty msg;
        ros::Publisher pub;
        if(mode=="open") {ROS_WARN("舵机全部打开！");pub = servo_pub_all_open;}
        else {ROS_WARN("舵机全部关闭！");pub = servo_pub_all_close;}
        pub.publish(msg);
    }

    void servo_control_better(string pos,string mode="open")
    {
        ros::Publisher pub;
        std_msgs::Empty msg;
        if(pos=="front_left"){
            if(mode=="open"){
                pub = servo_pub_front_left_open;
                ROS_WARN("左前舵机打开！");
            }
            else{
                pub = servo_pub_front_left_close;
                ROS_WARN("左前舵机关闭！");
            }
        }
        else if(pos=="front_right"){
        if(mode=="open"){
                pub = servo_pub_front_right_open;
                ROS_WARN("右前舵机打开！");
            }
            else{
                pub = servo_pub_front_right_close;
                ROS_WARN("右前舵机关闭！");
            }
        }
        else if(pos=="back_left"){
        if(mode=="open"){
                pub = servo_pub_back_left_open;
                ROS_WARN("左后舵机打开！");
            }
            else{
                pub = servo_pub_back_left_close;
                ROS_WARN("左后舵机关闭！");
            }
        }
        else if(pos=="back_right"){
            if(mode=="open"){
                pub = servo_pub_back_right_open;
                ROS_WARN("右后舵机打开！");
            }
            else{
                pub = servo_pub_back_right_close;
                ROS_WARN("右后舵机关闭！");
            }
        }
        pub.publish(msg);
    }

    void servo_control_num_better(int num,string mode="open")
    {
        switch(num)
        {
            case 0:
                servo_all_control(mode);
                break;
            case 1:
                servo_control_better("front_left",mode);
                break;
            case 2:
                servo_control_better("front_right",mode);
                break;
            case 3:
                servo_control_better("back_left",mode);
                break;
            case 4:
                servo_control_better("back_right",mode);
                break;
            default:
                ROS_ERROR("Wrong servo_control num!\n");
        }
    }

    void servo_control(ros::Publisher& pub,string pos,string mode="open")
    {
        std_msgs::Int32 msg;
        if(pos=="front_left"){
            if(mode=="open"){
                msg.data = 180;
                ROS_WARN("左前舵机打开！");
            }
            else{
                msg.data = 30;
                ROS_WARN("左前舵机关闭！");
            }
        }
        else if(pos=="front_right"){
        if(mode=="open"){
                msg.data = 180;
                ROS_WARN("右前舵机打开！");
            }
            else{
                msg.data = 0;
                ROS_WARN("右前舵机关闭！");
            }
        }
        else if(pos=="back_left"){
        if(mode=="open"){
                msg.data = 180;
                ROS_WARN("左后舵机打开！");
            }
            else{
                msg.data = 0;
                ROS_WARN("左后舵机关闭！");
            }
        }
        else if(pos=="back_right"){
            if(mode=="open"){
                msg.data = 180;
                ROS_WARN("右后舵机打开！");
            }
            else{
                msg.data = 30;
                ROS_WARN("右后舵机关闭！");
            }
        }
        pub.publish(msg);
    }

    void servo_control_num(int num,string mode="open")
    {
        switch(num)
        {
            case 0:
                servo_all_control(mode);
                break;
            case 1:
                servo_control(servo_pub_front_left,"front_left",mode);
                break;
            case 2:
                servo_control(servo_pub_front_right,"front_right",mode);
                break;
            case 3:
                servo_control(servo_pub_back_left,"back_left",mode);
                break;
            case 4:
                servo_control(servo_pub_back_right,"back_right",mode);
                break;
            default:
                ROS_ERROR("Wrong servo_control num!\n");
        }
    }

};