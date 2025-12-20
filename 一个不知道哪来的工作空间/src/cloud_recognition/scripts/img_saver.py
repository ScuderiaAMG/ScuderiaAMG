#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
import cv2
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
import os
import time

# ==================== 配置参数 ====================
# ROS话题名称
TOPIC_NAME = "/point_projector/plane_2/projected_image"  # 修改为你的图像话题名称

# 保存图片的文件夹路径
SAVE_FOLDER = "../template"  # 修改为你想要保存的文件夹路径

# 保存间隔（秒），0表示保存每一帧
SAVE_INTERVAL = 0.1

# 图像格式 (png, jpg)
IMAGE_FORMAT = "png"

# 是否使用时间戳命名
USE_TIMESTAMP = True

# 最大保存图片数量 (0表示无限制)
MAX_IMAGES = 0

# 是否显示图像
SHOW_IMAGE = False
# =================================================

class ImageSaver:
    def __init__(self):
        self.bridge = CvBridge()
        self.last_save_time = 0
        self.image_count = 0
        
        # 创建保存文件夹
        if not os.path.exists(SAVE_FOLDER):
            os.makedirs(SAVE_FOLDER)
            print(f"创建文件夹: {SAVE_FOLDER}")
        
        # 订阅图像话题
        self.image_sub = rospy.Subscriber(TOPIC_NAME, Image, self.image_callback)
        print(f"开始订阅话题: {TOPIC_NAME}")
        print(f"保存路径: {SAVE_FOLDER}")
        print(f"保存间隔: {SAVE_INTERVAL}秒")
        
    def image_callback(self, msg):
        current_time = time.time()
        
        # 检查保存间隔
        if SAVE_INTERVAL > 0 and (current_time - self.last_save_time) < SAVE_INTERVAL:
            return
            
        try:
            # 将ROS图像消息转换为OpenCV图像
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            
            # 显示图像（可选）
            if SHOW_IMAGE:
                cv2.imshow("Image Viewer", cv_image)
                cv2.waitKey(1)
            
            # 生成文件名
            if USE_TIMESTAMP:
                timestamp = rospy.Time.now().to_sec()
                filename = f"image_{timestamp:.6f}.{IMAGE_FORMAT}"
            else:
                filename = f"image_{self.image_count:06d}.{IMAGE_FORMAT}"
            
            # 完整文件路径
            file_path = os.path.join(SAVE_FOLDER, filename)
            
            # 保存图像
            cv2.imwrite(file_path, cv_image)
            self.image_count += 1
            self.last_save_time = current_time
            
            print(f"保存图片: {file_path}")
            
            # 检查最大图片数量限制
            if MAX_IMAGES > 0 and self.image_count >= MAX_IMAGES:
                print(f"已保存 {MAX_IMAGES} 张图片，停止保存")
                rospy.signal_shutdown("达到最大图片数量")
                
        except Exception as e:
            print(f"处理图像时出错: {e}")

def main():
    # 初始化ROS节点
    rospy.init_node('image_saver', anonymous=True)
    
    # 创建图像保存器
    image_saver = ImageSaver()
    
    try:
        # 保持节点运行
        rospy.spin()
    except KeyboardInterrupt:
        print("程序被用户中断")
    finally:
        # 清理资源
        cv2.destroyAllWindows()
        print(f"总共保存了 {image_saver.image_count} 张图片")

if __name__ == '__main__':
    main()
