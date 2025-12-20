#include <ros/ros.h>
#include <geometry_msgs/PointStamped.h>
#include <geometry_msgs/PolygonStamped.h>
#include <geometry_msgs/PoseStamped.h>
#include <geometry_msgs/Point.h> // 显式包含 Point
#include <visualization_msgs/Marker.h>
#include <vision_msgs/Detection2DArray.h>
#include <std_msgs/Int32.h>
#include <sensor_msgs/Image.h>
// 包含新的消息类型
#include "cloud_recognition/Detection3DWithID.h"
#include "cloud_recognition/Detection3DWithIDArray.h"
#include <vector>
#include <Eigen/Dense>
#include <map> // 用于存储多个平面的信息

// 为每个平面定义一个结构体来存储其状态和参数
struct PlaneData
{
    // 存储平面的四个顶点
    std::vector<geometry_msgs::Point> plane_vertices;
    bool plane_received = false;
    // 存储平面的位姿信息
    geometry_msgs::PoseStamped plane_pose;
    bool pose_received = false;
    // 存储图像尺寸
    int image_width = 640;  // 默认值
    int image_height = 480; // 默认值
    bool image_info_received = false;
    // 平面参数
    Eigen::Vector3d origin;
    Eigen::Vector3d u_axis; // 从BL到BR (对应像素u/x)
    Eigen::Vector3d v_axis; // 从BL到TL (对应像素v/y)
    Eigen::Vector3d normal;
    double plane_width = 0.0;         // 物理平面宽度
    double plane_height = 0.0;        // 物理平面高度
    double resolution_x = 0.0;        // 每像素代表的物理距离 (x方向)
    double resolution_y = 0.0;        // 每像素代表的物理距离 (y方向)
    bool plane_size_computed = false; // 是否已计算尺寸和分辨率

    // 为每个平面创建独立的订阅者
    ros::Subscriber plane_sub;
    ros::Subscriber pose_sub;
    ros::Subscriber image_sub;
    ros::Subscriber detections_sub; // 这个可以共用一个回调，但需要知道 plane_id

    // 可视化标记的命名空间（可选，用于区分不同平面的可视化）
    std::string marker_namespace = "converted_detections_plane_";
};

class MultiPlanePointConverter
{
private:
    ros::NodeHandle nh_;
    ros::NodeHandle nh_private_;
    int num_planes_; // 从 launch 文件读取

    // 存储所有平面的数据
    std::map<int, PlaneData> planes_data_;

    // 统一的发布者
    ros::Publisher detections3d_pub_; // 发布 Detection3DWithIDArray
    ros::Publisher marker_pub_;       // 发布可视化标记
    ros::Publisher count_pub_;        // 发布总检测点数量 (可选)

    // 回调函数需要知道是哪个平面的，所以需要一个包装器或捕获 plane_id
    void planeCallbackWrapper(const geometry_msgs::PolygonStamped::ConstPtr &msg, int plane_id);
    void poseCallbackWrapper(const geometry_msgs::PoseStamped::ConstPtr &msg, int plane_id);
    void imageCallbackWrapper(const sensor_msgs::ImageConstPtr &msg, int plane_id);
    void detectionsCallbackWrapper(const vision_msgs::Detection2DArray::ConstPtr &msg, int plane_id);

    // 核心处理函数 (从原 PlanePointConverter 移植)
    void processPlaneData(int plane_id);
    void computePlaneSizeAndResolution(int plane_id);
    Eigen::Vector3d convert2DTo3D(double u, double v, const PlaneData &plane_data);
    void visualizePoint(const Eigen::Vector3d &point, const std::string &frame_id, int plane_id, int detection_id, int class_id);
    void clearPreviousMarkers(const std::string &frame_id, int plane_id);

public:
    MultiPlanePointConverter() : nh_private_("~")
    {
        nh_private_.param("num_planes", num_planes_, 1); // 默认订阅1个平面

        // 初始化发布者
        detections3d_pub_ = nh_.advertise<cloud_recognition::Detection3DWithIDArray>("all_plane_3d_detections", 10); // 使用数组消息
        marker_pub_ = nh_.advertise<visualization_msgs::Marker>("visualization_marker", 100);
        count_pub_ = nh_.advertise<std_msgs::Int32>("total_detection_count", 10);

        // 为每个平面初始化订阅者
        for (int i = 1; i <= num_planes_; ++i)
        {
            PlaneData &plane_data = planes_data_[i];          // 如果不存在会自动创建
            plane_data.marker_namespace += std::to_string(i); // 设置命名空间

            std::string plane_topic = "/point_projector/plane_" + std::to_string(i) + "/plane_corners";
            std::string pose_topic = "/point_projector/plane_" + std::to_string(i) + "/projected_plane_pose";
            std::string image_topic = "/point_projector/plane_" + std::to_string(i) + "/projected_image";
            std::string detections_topic = "/template_centers/plane_" + std::to_string(i);

            // 使用 lambda 或 boost::bind 捕获 plane_id
            plane_data.plane_sub = nh_.subscribe<geometry_msgs::PolygonStamped>(
                plane_topic, 1,
                [this, i](const geometry_msgs::PolygonStamped::ConstPtr &msg)
                { this->planeCallbackWrapper(msg, i); });

            plane_data.pose_sub = nh_.subscribe<geometry_msgs::PoseStamped>(
                pose_topic, 1,
                [this, i](const geometry_msgs::PoseStamped::ConstPtr &msg)
                { this->poseCallbackWrapper(msg, i); });

            plane_data.image_sub = nh_.subscribe<sensor_msgs::Image>(
                image_topic, 1,
                [this, i](const sensor_msgs::ImageConstPtr &msg)
                { this->imageCallbackWrapper(msg, i); });

            plane_data.detections_sub = nh_.subscribe<vision_msgs::Detection2DArray>(
                detections_topic, 10,
                [this, i](const vision_msgs::Detection2DArray::ConstPtr &msg)
                { this->detectionsCallbackWrapper(msg, i); });

            ROS_INFO("Subscribed to topics for plane %d", i);
        }

        ROS_INFO("MultiPlanePointConverter node initialized with %d planes", num_planes_);
    }
};

// --- Callback Wrappers ---
void MultiPlanePointConverter::planeCallbackWrapper(const geometry_msgs::PolygonStamped::ConstPtr &msg, int plane_id)
{
    auto it = planes_data_.find(plane_id);
    if (it == planes_data_.end())
        return; // 安全检查
    PlaneData &plane_data = it->second;

    if (msg->polygon.points.size() != 4)
    {
        ROS_WARN("Plane %d: Expected 4 vertices, got %lu", plane_id, msg->polygon.points.size());
        return;
    }
    plane_data.plane_vertices.clear();
    for (const auto &point : msg->polygon.points)
    {
        geometry_msgs::Point p;
        p.x = point.x;
        p.y = point.y;
        p.z = point.z;
        plane_data.plane_vertices.push_back(p);
    }
    plane_data.plane_received = true;
    plane_data.plane_size_computed = false;
    ROS_INFO("Plane %d: Received plane vertices", plane_id);
    processPlaneData(plane_id);
}

void MultiPlanePointConverter::poseCallbackWrapper(const geometry_msgs::PoseStamped::ConstPtr &msg, int plane_id)
{
    auto it = planes_data_.find(plane_id);
    if (it == planes_data_.end())
        return;
    PlaneData &plane_data = it->second;

    double norm = sqrt(msg->pose.orientation.x * msg->pose.orientation.x +
                       msg->pose.orientation.y * msg->pose.orientation.y +
                       msg->pose.orientation.z * msg->pose.orientation.z +
                       msg->pose.orientation.w * msg->pose.orientation.w);
    if (norm < 1e-6)
    {
        ROS_WARN("Plane %d: Invalid quaternion, norm: %f", plane_id, norm);
        return;
    }
    plane_data.plane_pose = *msg;
    plane_data.pose_received = true;
    ROS_INFO("Plane %d: Received plane pose", plane_id);
    processPlaneData(plane_id);
}

void MultiPlanePointConverter::imageCallbackWrapper(const sensor_msgs::ImageConstPtr &msg, int plane_id)
{
    auto it = planes_data_.find(plane_id);
    if (it == planes_data_.end())
        return;
    PlaneData &plane_data = it->second;

    plane_data.image_width = msg->width;
    plane_data.image_height = msg->height;
    plane_data.image_info_received = true;
    ROS_INFO_ONCE("Plane %d: Received image info: %dx%d", plane_id, plane_data.image_width, plane_data.image_height);
    processPlaneData(plane_id); // 尝试计算尺寸
}

void MultiPlanePointConverter::detectionsCallbackWrapper(const vision_msgs::Detection2DArray::ConstPtr &msg, int plane_id)
{
    auto it = planes_data_.find(plane_id);
    if (it == planes_data_.end())
        return;
    PlaneData &plane_data = it->second;

    // 检查必要数据是否就绪
    if (!plane_data.plane_received || plane_data.plane_vertices.size() != 4)
    {
        ROS_WARN_THROTTLE(5.0, "Plane %d: Plane vertices not valid, cannot convert detections", plane_id);
        return;
    }
    if (!plane_data.plane_size_computed)
    {
        if (plane_data.image_info_received)
        {
            computePlaneSizeAndResolution(plane_id);
        }
        else
        {
            ROS_WARN_THROTTLE(5.0, "Plane %d: Plane size/resolution not computed and image info missing", plane_id);
            return;
        }
        if (!plane_data.plane_size_computed)
        {
            ROS_WARN_THROTTLE(5.0, "Plane %d: Failed to compute plane size/resolution", plane_id);
            return;
        }
    }

    // 准备发布消息
    cloud_recognition::Detection3DWithIDArray detections_3d_array_msg;
    detections_3d_array_msg.header = msg->header;            // 使用检测消息的 header
    detections_3d_array_msg.header.stamp = ros::Time::now(); // 更新时间戳

    clearPreviousMarkers(msg->header.frame_id, plane_id); // 清除该平面的旧标记

    ROS_INFO("Plane %d: Processing %lu detections", plane_id, msg->detections.size());

    for (size_t i = 0; i < msg->detections.size(); i++)
    {
        const auto &detection = msg->detections[i];
        double u_actual = detection.bbox.center.x * plane_data.resolution_x;
        double v_actual = detection.bbox.center.y * plane_data.resolution_y;

        Eigen::Vector3d point3d = convert2DTo3D(u_actual, v_actual, plane_data);

        // 填充并发布 Detection3DWithID 消息
        cloud_recognition::Detection3DWithID detection_3d_msg;
        detection_3d_msg.header = msg->header;
        detection_3d_msg.header.stamp = ros::Time::now();
        // --- 修正：显式赋值 Eigen::Vector3d 到 geometry_msgs::Point ---
        detection_3d_msg.point.x = point3d.x();
        detection_3d_msg.point.y = point3d.y();
        detection_3d_msg.point.z = point3d.z();
        // ---
        detection_3d_msg.id = 0; // 默认 ID
        if (!detection.results.empty())
        {
            detection_3d_msg.id = detection.results[0].id; // 获取检测类型 ID
        }
        detections_3d_array_msg.detections.push_back(detection_3d_msg); // 添加到数组

        // 可视化 (可选，但需要区分平面)
        visualizePoint(point3d, msg->header.frame_id, plane_id, i, detection_3d_msg.id);

        ROS_INFO("Plane %d: Converted detection %lu: pixel(%.0f,%.0f) -> 3D(%.3f,%.3f,%.3f) ID:%d",
                 plane_id, i, detection.bbox.center.x, detection.bbox.center.y,
                 point3d.x(), point3d.y(), point3d.z(), detection_3d_msg.id);
    }

    // 发布包含所有检测的数组消息
    if (!detections_3d_array_msg.detections.empty())
    {
        detections3d_pub_.publish(detections_3d_array_msg);
        // 可选：发布总数量
        std_msgs::Int32 count_msg;
        count_msg.data = detections_3d_array_msg.detections.size();
        count_pub_.publish(count_msg);
    }
}

// --- Core Processing Functions (Adapted from original) ---

void MultiPlanePointConverter::processPlaneData(int plane_id)
{
    auto it = planes_data_.find(plane_id);
    if (it == planes_data_.end())
        return;
    PlaneData &plane_data = it->second;

    if (plane_data.plane_vertices.size() == 4 && plane_data.pose_received)
    {
        // 计算坐标系 (简化版，假设顶点已经包含了位姿信息，或者顶点是世界坐标)
        // 如果顶点是相对于平面坐标系的，还需要结合 plane_pose_ 进行变换
        // 这里假设顶点已经是世界坐标
        plane_data.origin = Eigen::Vector3d(plane_data.plane_vertices[0].x, plane_data.plane_vertices[0].y, plane_data.plane_vertices[0].z);
        Eigen::Vector3d p_br(plane_data.plane_vertices[3].x, plane_data.plane_vertices[3].y, plane_data.plane_vertices[3].z);
        Eigen::Vector3d p_tl(plane_data.plane_vertices[1].x, plane_data.plane_vertices[1].y, plane_data.plane_vertices[1].z);
        plane_data.u_axis = p_br - plane_data.origin;
        plane_data.v_axis = p_tl - plane_data.origin;
        Eigen::Vector3d vertex_normal = plane_data.u_axis.cross(plane_data.v_axis);
        vertex_normal.normalize();
        plane_data.normal = vertex_normal;
        ROS_DEBUG("Plane %d: Coordinate system calculated", plane_id);
    }

    if (plane_data.plane_vertices.size() == 4 && plane_data.image_info_received)
    {
        computePlaneSizeAndResolution(plane_id);
    }
}

void MultiPlanePointConverter::computePlaneSizeAndResolution(int plane_id)
{
    auto it = planes_data_.find(plane_id);
    if (it == planes_data_.end())
        return;
    PlaneData &plane_data = it->second;

    if (plane_data.plane_vertices.size() != 4 || !plane_data.image_info_received)
    {
        return;
    }

    Eigen::Vector3d p_bl(plane_data.plane_vertices[0].x, plane_data.plane_vertices[0].y, plane_data.plane_vertices[0].z);
    Eigen::Vector3d p_br(plane_data.plane_vertices[3].x, plane_data.plane_vertices[3].y, plane_data.plane_vertices[3].z);
    Eigen::Vector3d p_tl(plane_data.plane_vertices[1].x, plane_data.plane_vertices[1].y, plane_data.plane_vertices[1].z);

    plane_data.u_axis = p_br - p_bl;
    plane_data.v_axis = p_tl - p_bl;
    plane_data.plane_width = plane_data.u_axis.norm();
    plane_data.plane_height = plane_data.v_axis.norm();

    if (plane_data.image_width > 0 && plane_data.image_height > 0)
    { // 避免除零
        plane_data.resolution_x = plane_data.plane_width / static_cast<double>(plane_data.image_width);
        plane_data.resolution_y = plane_data.plane_height / static_cast<double>(plane_data.image_height);
        plane_data.plane_size_computed = true;
        ROS_INFO("Plane %d: Computed size/resolution - Image: %dx%d, Physical: %.3fx%.3fm, Res: %.6f, %.6f m/px",
                 plane_id, plane_data.image_width, plane_data.image_height,
                 plane_data.plane_width, plane_data.plane_height,
                 plane_data.resolution_x, plane_data.resolution_y);
    }
    else
    {
        ROS_WARN("Plane %d: Invalid image dimensions for resolution calculation (%dx%d)",
                 plane_id, plane_data.image_width, plane_data.image_height);
    }
}

Eigen::Vector3d MultiPlanePointConverter::convert2DTo3D(double u, double v, const PlaneData &plane_data)
{
    Eigen::Vector3d u_unit = plane_data.u_axis.normalized();
    Eigen::Vector3d v_unit = plane_data.v_axis.normalized();
    Eigen::Vector3d point3d = plane_data.origin + u * u_unit + v * v_unit;
    return point3d;
}

void MultiPlanePointConverter::visualizePoint(const Eigen::Vector3d &point, const std::string &frame_id, int plane_id, int detection_id, int class_id)
{
    visualization_msgs::Marker point_marker;
    point_marker.header.frame_id = frame_id;
    point_marker.header.stamp = ros::Time::now();
    point_marker.ns = "converted_detections_plane_" + std::to_string(plane_id); // 区分平面
    point_marker.id = detection_id;                                             // 在同一平面内使用检测ID
    point_marker.type = visualization_msgs::Marker::SPHERE;
    point_marker.action = visualization_msgs::Marker::ADD;
    point_marker.pose.position.x = point.x();
    point_marker.pose.position.y = point.y();
    point_marker.pose.position.z = point.z();
    point_marker.pose.orientation.w = 1.0;
    point_marker.scale.x = 0.1;
    point_marker.scale.y = 0.1;
    point_marker.scale.z = 0.1;
    // 可以根据 class_id 或 plane_id 设置不同颜色
    point_marker.color.r = (class_id == 1) ? 1.0f : 0.0f;
    point_marker.color.g = (class_id == 2) ? 1.0f : 0.0f;
    point_marker.color.b = (class_id == 3) ? 1.0f : 1.0f; // 默认蓝色
    point_marker.color.a = 1.0f;
    marker_pub_.publish(point_marker);
}

void MultiPlanePointConverter::clearPreviousMarkers(const std::string &frame_id, int plane_id)
{
    // 删除特定平面的所有标记
    visualization_msgs::Marker delete_marker;
    delete_marker.header.frame_id = frame_id;
    delete_marker.header.stamp = ros::Time::now();
    delete_marker.ns = "converted_detections_plane_" + std::to_string(plane_id);
    delete_marker.id = 0;
    delete_marker.action = visualization_msgs::Marker::DELETEALL;
    marker_pub_.publish(delete_marker);
}

int main(int argc, char **argv)
{
    ros::init(argc, argv, "multi_plane_detection_converter");
    MultiPlanePointConverter converter;
    ros::spin();
    return 0;
}