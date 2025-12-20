#include <yolov8_ros_msgs/BoundingBoxes.h>
using namespace std;

//相机参数相关变量
float fx = 435.4970;
float fy = 435.6341;
float cx = 331.7275;
float cy = 232.0249;
float camera_height = 0.0; //相机相对于无人机机体的高度差，单位米
float camera_offset_body_x = 0.0; //相机相对于无人机机体前后方向的偏移，单位米
float camera_offset_body_y = 0.0; //相机相对于无人机机体左右方向的偏移，单位米


bool yolo_start_checking = false;
bool yolo_found = false;
float yolo_target_x = 0.0;
float yolo_target_y = 0.0;
float put_target_x,put_target_y;
yolov8_ros_msgs::BoundingBox cb;
void yolo_ros_cb(const yolov8_ros_msgs::BoundingBoxes::ConstPtr &msg){    
    if(!yolo_start_checking) {
		yolo_found = false; //不需要再置false了
		return;
	}
    for(yolov8_ros_msgs::BoundingBox bounding_box:msg->bounding_boxes)
    {        
		if(bounding_box.probability < 0.7) continue; //保险误发送，重新检验置信度
    	std::cout<<"CLASS: "<<bounding_box.Class<<std::endl;
		cb.Class = bounding_box.Class;
		std::cout<<"probability: "<<bounding_box.probability<<std::endl;
		cb.probability = bounding_box.probability;
		if(bounding_box.Class.empty()) continue; // 如果类别为空，跳过该框
		yolo_found = true;

		// 计算目标位置（考虑飞机yaw角度）
		float center_x = bounding_box.xmin;
		float center_y = bounding_box.ymin;
		
		// 相机坐标系下的偏移量（相对于相机光心）
		float camera_offset_x = (cy - center_y) * (local_pos.pose.pose.position.z + camera_height - init_position_z_take_off ) / fy + camera_offset_body_x;
		float camera_offset_y = (cx - center_x) * (local_pos.pose.pose.position.z + camera_height - init_position_z_take_off ) / fx;
		
		// 考虑飞机yaw角度，将相机坐标系转换到世界坐标系
		float cos_yaw = cos(yaw);
		float sin_yaw = sin(yaw);
		
		// 世界坐标系下的目标位置
		yolo_target_x = local_pos.pose.pose.position.x + camera_offset_x * cos_yaw - camera_offset_y * sin_yaw;
		yolo_target_y = local_pos.pose.pose.position.y + camera_offset_x * sin_yaw + camera_offset_y * cos_yaw;
		std::cout << "center_x = " << center_x << ", center_y = " << center_y << std::endl;
		std::cout << "calculate_box_target_x = " << yolo_target_x << ", calculate_box_target_y = " << yolo_target_y << std::endl;

    }
}
