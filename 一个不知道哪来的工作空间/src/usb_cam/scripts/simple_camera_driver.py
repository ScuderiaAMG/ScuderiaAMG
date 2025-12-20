#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import rospy
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError


def find_video_devices():
    """查找所有 /dev/video* 设备"""
    devices = []
    try:
        for f in os.listdir('/dev'):
            if f.startswith('video') and f[5:].isdigit():
                devices.append(int(f[5:]))
        devices.sort()
        return [f'/dev/video{d}' for d in devices]
    except Exception as e:
        rospy.logerr(f"查找设备时出错: {e}")
        return []

def test_camera_device(device_path):
    """测试摄像头设备是否可以打开"""
    rospy.loginfo(f"测试设备: {device_path}")
    
    # 检查设备文件是否存在
    if not os.path.exists(device_path):
        rospy.logwarn(f"设备文件不存在: {device_path}")
        return False
    
    # 检查权限
    if not os.access(device_path, os.R_OK):
        rospy.logwarn(f"没有读取权限: {device_path}")
        return False
    
    # 尝试打开
    cap = cv2.VideoCapture(device_path)
    if not cap.isOpened():
        rospy.logwarn(f"OpenCV 无法打开设备: {device_path}")
        cap.release()
        return False
    
    # 尝试读取一帧
    ret, frame = cap.read()
    if not ret:
        rospy.logwarn(f"无法从设备读取帧: {device_path}")
        cap.release()
        return False
    
    rospy.loginfo(f"设备测试成功: {device_path}, 分辨率: {frame.shape}")
    cap.release()
    return True

def main(argv):
    rospy.init_node("simple_camera_driver", argv=argv)

    # 获取参数：优先使用指定设备路径，否则使用 camera_id 数字
    device_path = rospy.get_param("~device_path", "")
    camera_id = rospy.get_param("~camera_id", 0)
    frame_id = rospy.get_param("~frame_id", "mono_camera")
    rate_duration = rospy.get_param("~rate", 10)

    image_pub = rospy.Publisher("camera/image_raw", Image, queue_size=1)

    capture = None

    if device_path:
        if test_camera_device(device_path):
            capture = cv2.VideoCapture(device_path)
        else:
            rospy.logerr(f"指定设备无法使用: {device_path}")
            return
    else:
        # 自动查找并测试设备
        video_devices = find_video_devices()
        rospy.loginfo(f"找到的视频设备: {video_devices}")

        for dev in video_devices:
            if test_camera_device(dev):
                capture = cv2.VideoCapture(dev)
                if capture.isOpened():
                    rospy.loginfo(f"成功打开设备: {dev}")
                    break
        else:
            rospy.logerr("没有找到任何可用的摄像头设备")
            return

    # 设置分辨率
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    width = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
    rospy.loginfo(f"摄像头分辨率设置为: {int(width)}x{int(height)}")

    bridge = CvBridge()
    rate = rospy.Rate(rate_duration)

    while not rospy.is_shutdown():
        ret, frame = capture.read()
        if ret:
            try:
                image_msg = bridge.cv2_to_imgmsg(frame, "bgr8")
                image_msg.header.stamp = rospy.Time.now()
                image_msg.header.frame_id = frame_id
                image_pub.publish(image_msg)
            except CvBridgeError as e:
                rospy.logerr(e)
        rate.sleep()

    capture.release()


if __name__ == '__main__':
    main(sys.argv)