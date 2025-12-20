#!/usr/bin/env python3

import rospy
from gazebo_msgs.msg import ModelStates
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist, Vector3
import tf

class GazeboOdomPublisher:
    def __init__(self):
        # 从参数服务器获取模型名称，默认为 "iris"
        self.model_name = rospy.get_param("~model_name", "iris")
        self.odom_frame = rospy.get_param("~odom_frame", "world")
        self.base_link_frame = rospy.get_param("~base_link_frame", self.model_name + "/base_link")

        self.pub = rospy.Publisher("/gazebo/real/odom", Odometry, queue_size=10)
        self.sub = rospy.Subscriber("/gazebo/model_states", ModelStates, self.model_states_callback)

        rospy.loginfo(f"Gazebo Odom Publisher: publishing /gazebo/real/odom for model '{self.model_name}'")

    def model_states_callback(self, msg):
        try:
            # 查找模型索引
            idx = msg.name.index(self.model_name)
        except ValueError:
            # 模型尚未出现
            return

        # 构造 Odometry 消息
        odom = Odometry()
        odom.header.stamp = rospy.Time.now()
        odom.header.frame_id = self.odom_frame
        odom.child_frame_id = self.base_link_frame

        # 位姿
        odom.pose.pose.position = msg.pose[idx].position
        odom.pose.pose.orientation = msg.pose[idx].orientation

        # 速度（线速度 + 角速度）
        odom.twist.twist.linear = msg.twist[idx].linear
        odom.twist.twist.angular = msg.twist[idx].angular

        # 协方差暂时设为0（Gazebo 是真值，无噪声）
        odom.pose.covariance = [0.0] * 36
        odom.twist.covariance = [0.0] * 36

        self.pub.publish(odom)

if __name__ == '__main__':
    rospy.init_node('gazebo_odom_publisher', anonymous=True)
    node = GazeboOdomPublisher()
    rospy.spin()