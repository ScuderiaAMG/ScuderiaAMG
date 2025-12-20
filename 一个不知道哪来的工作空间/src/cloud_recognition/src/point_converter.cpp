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
#include <map>   // 用于存储多个平面的信息
#include <cmath> // for std::sqrt

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
    Eigen::Vector3d origin;    // Bottom-Left 点 (保留此定义)
    Eigen::Vector3d origin_tl; // 新增：Top-Left 点，作为新的转换起点
    Eigen::Vector3d u_axis;    // 从BL到BR (对应像素u/x)
    Eigen::Vector3d v_axis;    // 从BL到TL (对应像素v/y)
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

    // 新增：每个ID的最大点数限制
    std::map<int, int> max_points_per_id_;

    // 全局存储所有检测点，不再按平面区分
    std::vector<cloud_recognition::Detection3DWithID> global_detections_;

    // 新增：用于预筛选的缓冲区
    std::vector<cloud_recognition::Detection3DWithID> pre_filter_buffer_;

    // 存储更新半径参数
    double update_radius_;

    // 新增：预筛选参数
    int min_neighbors_for_initial_pass_;
    double neighbor_search_radius_;

    // 统一的发布者
    ros::Publisher detections3d_pub_; // 发布 Detection3DWithIDArray (聚合后的)
    ros::Publisher marker_pub_;       // 发布可视化标记
    ros::Publisher count_pub_;        // 发布总检测点数量 (可选)

    // 新增：刀旗点相关
    ros::Subscriber flag_sub_;
    std::string flag_topic_;
    double flag_default_z_; // 为刀旗点设置的默认Z坐标

    // 回调函数包装器
    void planeCallbackWrapper(const geometry_msgs::PolygonStamped::ConstPtr &msg, int plane_id);
    void poseCallbackWrapper(const geometry_msgs::PoseStamped::ConstPtr &msg, int plane_id);
    void imageCallbackWrapper(const sensor_msgs::ImageConstPtr &msg, int plane_id);
    void detectionsCallbackWrapper(const vision_msgs::Detection2DArray::ConstPtr &msg, int plane_id);

    // 新增：刀旗点回调
    void flagCallback(const geometry_msgs::Point::ConstPtr &msg);

    // 核心处理函数
    void processPlaneData(int plane_id);
    void computePlaneSizeAndResolution(int plane_id);
    Eigen::Vector3d convert2DTo3D(double u, double v, const PlaneData &plane_data);
    void visualizePoint(const Eigen::Vector3d &point, const std::string &frame_id, int plane_id, int detection_id, int class_id);
    void clearPreviousMarkers(const std::string &frame_id, int plane_id);

    // 修改：聚合并发布所有检测点
    void publishAggregatedDetections(const std_msgs::Header &header_for_pub); // 需要一个 header

    // 新增：辅助函数
    void enforceIdLimit(int class_id);
    void addFlagPoint(const geometry_msgs::Point &flag_point);

public:
    MultiPlanePointConverter() : nh_private_("~")
    {
        nh_private_.param("num_planes", num_planes_, 1);         // 默认订阅1个平面
        nh_private_.param("update_radius", update_radius_, 0.1); // 默认值 0.1 米
        // 新增：读取预筛选参数
        nh_private_.param("min_neighbors_for_initial_pass", min_neighbors_for_initial_pass_, 3); // 默认至少3个邻居
        nh_private_.param("neighbor_search_radius", neighbor_search_radius_, 0.05);              // 默认搜索半径 5cm
        // 新增：读取刀旗点话题参数
        nh_private_.param<std::string>("flag_topic", flag_topic_, "/flag_coordinates");
        // 新增：读取刀旗点默认Z坐标参数
        nh_private_.param("flag_default_z", flag_default_z_, 0.0); // 默认Z=0.0

        // 新增：读取每个ID的最大点数限制
        XmlRpc::XmlRpcValue id_limits;
        if (nh_private_.getParam("max_points_per_id", id_limits) && id_limits.getType() == XmlRpc::XmlRpcValue::TypeStruct)
        {
            for (XmlRpc::XmlRpcValue::iterator it = id_limits.begin(); it != id_limits.end(); ++it)
            {
                int id = std::stoi(it->first);
                int limit = static_cast<int>(it->second);
                max_points_per_id_[id] = limit;
                ROS_INFO("ID %d max points limit: %d", id, limit);
            }
        }
        else
        {
            ROS_WARN("No max_points_per_id parameter found or invalid format, using default limits");
            // 设置默认限制 - 现在包含ID=4（刀旗）
            max_points_per_id_[0] = 1;
            max_points_per_id_[1] = 2;
            max_points_per_id_[2] = 3;
            max_points_per_id_[3] = 4;
            max_points_per_id_[4] = 10; // 刀旗ID=4，最多10个
            max_points_per_id_[5] = 6;
        }

        ROS_INFO("Using neighbor search radius: %.3f meters", neighbor_search_radius_);
        ROS_INFO("Using minimum neighbors for initial pass: %d", min_neighbors_for_initial_pass_);
        ROS_INFO("Using update radius: %.3f meters", update_radius_);
        ROS_INFO("Using flag topic: %s", flag_topic_.c_str());
        ROS_INFO("Using flag default Z: %.3f meters", flag_default_z_);

        // 初始化发布者
        detections3d_pub_ = nh_.advertise<cloud_recognition::Detection3DWithIDArray>("all_plane_3d_detections", 10); // 使用数组消息
        marker_pub_ = nh_.advertise<visualization_msgs::Marker>("visualization_marker", 100);
        count_pub_ = nh_.advertise<std_msgs::Int32>("total_detection_count", 10);

        // 新增：订阅刀旗点话题
        flag_sub_ = nh_.subscribe<geometry_msgs::Point>(flag_topic_, 10, &MultiPlanePointConverter::flagCallback, this);
        ROS_INFO("Subscribed to flag topic: %s", flag_topic_.c_str());

        // 为每个平面初始化订阅者
        for (int i = 1; i <= num_planes_; ++i)
        {
            PlaneData &plane_data = planes_data_[i];          // 如果不存在会自动创建
            plane_data.marker_namespace += std::to_string(i); // 设置命名空间
            std::string plane_topic = "/point_projector/plane_" + std::to_string(i) + "/plane_corners";
            std::string pose_topic = "/point_projector/plane_" + std::to_string(i) + "/projected_plane_pose";
            std::string image_topic = "/point_projector/plane_" + std::to_string(i) + "/projected_image";
            std::string detections_topic = "/template_centers/plane_" + std::to_string(i);

            // 使用 lambda 捕获 plane_id
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
                detections_topic, 10, // 队列大小可以调整
                [this, i](const vision_msgs::Detection2DArray::ConstPtr &msg)
                { this->detectionsCallbackWrapper(msg, i); });
            ROS_INFO("Subscribed to topics for plane %d", i);
        }
        ROS_INFO("MultiPlanePointConverter node initialized with %d planes", num_planes_);
        ROS_INFO("Using update radius: %.3f meters", update_radius_);
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
    bool points_updated_or_added = false; // 标记是否有任何更新或添加到 global_detections_
    ROS_INFO("Plane %d: Processing %lu detections", plane_id, msg->detections.size());
    for (size_t i = 0; i < msg->detections.size(); i++)
    {
        const auto &detection = msg->detections[i];
        double u_actual = detection.bbox.center.x * plane_data.resolution_x;
        double v_actual = detection.bbox.center.y * plane_data.resolution_y;
        Eigen::Vector3d point3d = convert2DTo3D(u_actual, v_actual, plane_data);
        // 填充 Detection3DWithID 消息 (用于预筛选缓冲区和聚合)
        cloud_recognition::Detection3DWithID detection_3d_msg;
        detection_3d_msg.header = msg->header; // 使用原始检测的 header
        detection_3d_msg.point.x = point3d.x();
        detection_3d_msg.point.y = point3d.y();
        detection_3d_msg.point.z = point3d.z();
        detection_3d_msg.id = 0; // 默认 ID
        if (!detection.results.empty())
        {
            detection_3d_msg.id = detection.results[0].id; // 获取检测类型 ID
            // 新增：设置 match_value
            detection_3d_msg.match_value = detection.results[0].score; // 使用模板匹配的置信度
        }
        else
        {
            detection_3d_msg.match_value = 0.0; // 默认值
        }
        detection_3d_msg.plane_pose = plane_data.plane_pose; // 直接赋值平面的位姿

        // 1. 将新点加入预筛选缓冲区
        pre_filter_buffer_.push_back(detection_3d_msg);

        // 2. 计算该点周围的邻居数量 (包括它自己)
        int neighbor_count = 0;
        for (const auto &existing_point : pre_filter_buffer_)
        { // 在预筛选缓冲区中查找
            // 确保在相同坐标系下比较
            if (existing_point.header.frame_id == detection_3d_msg.header.frame_id)
            {
                double dx = detection_3d_msg.point.x - existing_point.point.x;
                double dy = detection_3d_msg.point.y - existing_point.point.y;
                // double dz = detection_3d_msg.point.z - existing_point.point.z; // 如果考虑 Z 轴
                double dz = 0.0; // 假设主要在平面内比较，或者投影平面上比较
                double distance = std::sqrt(dx * dx + dy * dy + dz * dz);
                if (distance < neighbor_search_radius_)
                {
                    neighbor_count++;
                }
            }
        }

        // 3. 判断是否满足进入下一步的条件
        bool passes_pre_filter = (neighbor_count >= min_neighbors_for_initial_pass_);

        if (!passes_pre_filter)
        {
            // 不满足条件，仅记录日志，不执行后续更新/添加 global_detections_ 的逻辑
            ROS_DEBUG("Point from plane %d at (%.3f, %.3f, %.3f) did not pass pre-filter (neighbors: %d < %d within %.3fm)",
                      plane_id, detection_3d_msg.point.x, detection_3d_msg.point.y, detection_3d_msg.point.z,
                      neighbor_count, min_neighbors_for_initial_pass_, neighbor_search_radius_);
            continue; // 跳过这个点的后续处理
        }

        bool found_close_point = false;
        auto it_existing = global_detections_.begin();
        for (; it_existing != global_detections_.end(); ++it_existing) // 使用显式迭代器，方便删除
        {
            auto &existing_detection = *it_existing;
            // 计算两点间距离 (假设在同一坐标系下)
            // 确保帧 ID 一致再比较
            if (existing_detection.header.frame_id == detection_3d_msg.header.frame_id)
            {
                double dx = detection_3d_msg.point.x - existing_detection.point.x;
                double dy = detection_3d_msg.point.y - existing_detection.point.y;
                // double dz = detection_3d_msg.point.z - existing_detection.point.z;
                double dz = 0.0; // 投影到平面上
                double distance = std::sqrt(dx * dx + dy * dy + dz * dz);
                double dynamic_radius = update_radius_; // 默认半径
                if (detection_3d_msg.id == 2 || detection_3d_msg.id == 3)
                {
                    dynamic_radius = update_radius_ * 1.5; // -----------为 ID 2/3 的点增大半径------------------
                }
                // --- 修改点：使用动态半径进行比较 ---
                if (distance < dynamic_radius)
                {
                    // 找到邻近点，根据优先级规则决定操作
                    bool existing_is_low_priority = (existing_detection.id == 0 || existing_detection.id == 1);
                    bool new_is_high_priority = (detection_3d_msg.id == 2 || detection_3d_msg.id == 3);

                    if (existing_is_low_priority && new_is_high_priority)
                    {
                        // --- 新增规则：高优先级点踢掉低优先级点 ---
                        // 1. 删除旧的低优先级点
                        int global_index = std::distance(global_detections_.begin(), it_existing);
                        // 可视化删除旧点（可选，但推荐）
                        visualization_msgs::Marker delete_marker;
                        delete_marker.header.frame_id = existing_detection.header.frame_id;
                        delete_marker.header.stamp = ros::Time::now();
                        delete_marker.ns = "global_converted_detections";
                        delete_marker.id = global_index; // 使用旧点的索引
                        delete_marker.action = visualization_msgs::Marker::DELETE;
                        marker_pub_.publish(delete_marker);

                        it_existing = global_detections_.erase(it_existing); // 删除旧点，更新迭代器
                        ROS_INFO("Removed low-priority point (ID: %d) at (%.3f, %.3f, %.3f) due to high-priority point (ID: %d) from plane %d",
                                 existing_detection.id, existing_detection.point.x, existing_detection.point.y, existing_detection.point.z,
                                 detection_3d_msg.id, plane_id);

                        // 2. 将新点作为新点添加 (跳出循环，执行添加逻辑)
                        found_close_point = false; // 确保走添加分支
                        break;                     // 跳出循环
                    }
                    else
                    {
                        // --- 原有逻辑或默认逻辑：更新旧点 ---
                        // 包括：优先级相同、旧点优先级更高、或不满足踢出条件的情况
                        existing_detection = detection_3d_msg; // 用新消息完全替换旧的
                        found_close_point = true;
                        points_updated_or_added = true; // 标记有更新
                        ROS_DEBUG("Updated existing point (ID: %d) at (%.3f, %.3f, %.3f) with new point (ID: %d) from plane %d (distance: %.4f)",
                                  existing_detection.id, existing_detection.point.x, existing_detection.point.y, existing_detection.point.z,
                                  detection_3d_msg.id, plane_id, distance);
                        // 可视化更新后的点
                        int global_index = std::distance(global_detections_.begin(), it_existing); // 重新计算索引
                        visualizePoint(Eigen::Vector3d(existing_detection.point.x, existing_detection.point.y, existing_detection.point.z),
                                       existing_detection.header.frame_id,
                                       -1, // 或者用其他方式标识这是更新点
                                       global_index,
                                       existing_detection.id);

                        // 🔧 新增：检查并强制执行ID限制（更新后可能需要删除低置信度点）
                        enforceIdLimit(existing_detection.id);
                        break; // 找到并处理后跳出循环
                    }
                }
            }
        }
        if (!found_close_point)
        {
            // 没有找到邻近点，或者因为优先级规则需要添加新点
            global_detections_.push_back(detection_3d_msg);
            points_updated_or_added = true; // 标记有添加
            ROS_DEBUG("Added new point (ID: %d) at (%.3f, %.3f, %.3f) from plane %d",
                      detection_3d_msg.id, detection_3d_msg.point.x, detection_3d_msg.point.y, detection_3d_msg.point.z, plane_id);
            // 可视化新添加的点
            visualizePoint(Eigen::Vector3d(detection_3d_msg.point.x, detection_3d_msg.point.y, detection_3d_msg.point.z),
                           detection_3d_msg.header.frame_id,
                           plane_id,
                           global_detections_.size() - 1,
                           detection_3d_msg.id);

            // 🔧 新增：检查并强制执行ID限制
            enforceIdLimit(detection_3d_msg.id);
        }

        ROS_INFO("Plane %d: Converted detection %lu: pixel(%.0f,%.0f) -> 3D(%.3f,%.3f,%.3f) ID:%d (Neighbors: %d)",
                 plane_id, i, detection.bbox.center.x, detection.bbox.center.y,
                 point3d.x(), point3d.y(), point3d.z(), detection_3d_msg.id, neighbor_count);
    }
    // 如果有点被更新或添加到 global_detections_，则发布全局列表
    if (points_updated_or_added)
    {
        // 使用当前处理的消息 header 作为聚合消息的基础 header
        std_msgs::Header header_for_aggregated_msg = msg->header;
        header_for_aggregated_msg.stamp = ros::Time::now();     // 更新时间戳为当前时间
        publishAggregatedDetections(header_for_aggregated_msg); // 发布更新后的全局列表
    }
}

// 新增：刀旗点回调函数
void MultiPlanePointConverter::flagCallback(const geometry_msgs::Point::ConstPtr &msg)
{
    ROS_INFO_THROTTLE(1.0, "Received flag point: (%.3f, %.3f, %.3f)", msg->x, msg->y, msg->z);
    // 创建一个 geometry_msgs::Point，使用消息的 x, y 和默认的 z
    geometry_msgs::Point flag_point;
    flag_point.x = msg->x;
    flag_point.y = msg->y;
    flag_point.z = flag_default_z_; // 使用参数设置的默认Z值
    addFlagPoint(flag_point);
}

// 新增：添加刀旗点到全局列表的函数
void MultiPlanePointConverter::addFlagPoint(const geometry_msgs::Point &flag_point)
{
    // 创建 Detection3DWithID 消息
    cloud_recognition::Detection3DWithID detection_3d_msg;
    detection_3d_msg.header.stamp = ros::Time::now();
    detection_3d_msg.header.frame_id = "world"; // 或者根据实际情况设置帧ID
    detection_3d_msg.point = flag_point;
    detection_3d_msg.id = 4;                                    // 刀旗的ID为4
    detection_3d_msg.match_value = 1.0;                         // 刀旗点的置信度设为1.0
    detection_3d_msg.plane_pose = geometry_msgs::PoseStamped(); // 刀旗点没有平面位姿，设为空

    // 添加到全局检测列表
    global_detections_.push_back(detection_3d_msg);

    // 可视化新添加的刀旗点
    visualizePoint(Eigen::Vector3d(detection_3d_msg.point.x, detection_3d_msg.point.y, detection_3d_msg.point.z),
                   detection_3d_msg.header.frame_id,
                   -2, // 表示是刀旗点
                   global_detections_.size() - 1,
                   detection_3d_msg.id);

    // 检查并强制执行ID限制（ID=4）
    enforceIdLimit(detection_3d_msg.id);

    ROS_INFO("Added flag point (ID: %d) at (%.3f, %.3f, %.3f)",
             detection_3d_msg.id, detection_3d_msg.point.x, detection_3d_msg.point.y, detection_3d_msg.point.z);

    // 发布更新后的全局列表
    std_msgs::Header header_for_aggregated_msg;
    header_for_aggregated_msg.stamp = ros::Time::now();
    header_for_aggregated_msg.frame_id = detection_3d_msg.header.frame_id;
    publishAggregatedDetections(header_for_aggregated_msg);
}

//  Core Processing Functions (Adapted from original)
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
        plane_data.origin = Eigen::Vector3d(plane_data.plane_vertices[0].x, plane_data.plane_vertices[0].y, plane_data.plane_vertices[0].z);    // BL
        plane_data.origin_tl = Eigen::Vector3d(plane_data.plane_vertices[1].x, plane_data.plane_vertices[1].y, plane_data.plane_vertices[1].z); // TL
        Eigen::Vector3d p_br(plane_data.plane_vertices[3].x, plane_data.plane_vertices[3].y, plane_data.plane_vertices[3].z);
        Eigen::Vector3d p_tl(plane_data.plane_vertices[1].x, plane_data.plane_vertices[1].y, plane_data.plane_vertices[1].z); // TL
        plane_data.u_axis = p_br - plane_data.origin;                                                                         // BR - BL
        plane_data.v_axis = p_tl - plane_data.origin;                                                                         // TL - BL
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
    // 确保必要的顶点信息可用
    if (plane_data.plane_vertices.size() < 4)
    {
        ROS_ERROR("convert2DTo3D: Not enough plane vertices available.");
        return Eigen::Vector3d::Zero(); // 或者返回一个错误标志
    }

    // 1. 获取 BL, BR 和 TL 点的世界坐标
    // 根据 point_projector 的 publishPlaneCorners 和 MultiPlanePointConverter 的约定：
    // plane_vertices[0] = BL, plane_vertices[1] = TL, plane_vertices[2] = TR, plane_vertices[3] = BR
    Eigen::Vector3d p_bl(plane_data.plane_vertices[0].x, plane_data.plane_vertices[0].y, plane_data.plane_vertices[0].z); // BL
    Eigen::Vector3d p_br(plane_data.plane_vertices[3].x, plane_data.plane_vertices[3].y, plane_data.plane_vertices[3].z); // BR
    Eigen::Vector3d p_tl(plane_data.plane_vertices[1].x, plane_data.plane_vertices[1].y, plane_data.plane_vertices[1].z); // TL

    // 2. 计算 u_axis 和 v_axis 向量 (与之前计算一致)
    Eigen::Vector3d u_axis = p_br - p_bl; // 从 BL 到 BR
    Eigen::Vector3d v_axis = p_tl - p_bl; // 从 BL 到 TL

    // 3. 计算 u 和 v 方向的单位向量
    Eigen::Vector3d u_unit = u_axis.normalized();
    Eigen::Vector3d v_unit = v_axis.normalized();

    // 4. 核心修正：处理坐标系方向不匹配
    //    图像 Y 坐标增大 (向下) 对应 世界 Z 坐标减少 (或沿 v_axis 方向向 BL 移动)
    //    因此，我们从 TL 点开始，并沿 -v_unit 方向移动 v 距离
    //    这可以理解为：从 TL 点出发，u * u_unit 控制左右移动，
    //                 -v * v_unit 控制上下移动 (v 增大时，向 BL 方向移动，即 Z 减小)

    // 使用 TL 点作为起点，u 分量正常，v 分量取负
    Eigen::Vector3d point3d = p_tl + u * u_unit - v * v_unit;

    return point3d;
}

void MultiPlanePointConverter::visualizePoint(const Eigen::Vector3d &point, const std::string &frame_id, int plane_id, int detection_id, int class_id)
{
    visualization_msgs::Marker point_marker;
    point_marker.header.frame_id = frame_id;
    point_marker.header.stamp = ros::Time::now();
    point_marker.ns = "global_converted_detections"; // 使用统一的命名空间
    point_marker.id = detection_id;                  // 在同一平面内使用检测ID
    point_marker.type = visualization_msgs::Marker::SPHERE;
    point_marker.action = visualization_msgs::Marker::ADD;
    point_marker.pose.position.x = point.x();
    point_marker.pose.position.y = point.y();
    point_marker.pose.position.z = point.z();
    point_marker.pose.orientation.w = 1.0;
    point_marker.scale.x = 0.1;
    point_marker.scale.y = 0.1;
    point_marker.scale.z = 0.1;
    // 可以根据 class_id 设置不同颜色
    // ID=4 (刀旗) 使用橙色
    if (class_id == 4)
    {
        point_marker.color.r = 1.0f;  // Red
        point_marker.color.g = 0.65f; // Orange
        point_marker.color.b = 0.0f;  // Blue
    }
    else
    {
        point_marker.color.r = (class_id == 1) ? 1.0f : 0.0f;
        point_marker.color.g = (class_id == 2) ? 1.0f : 0.0f;
        point_marker.color.b = (class_id == 3) ? 1.0f : 1.0f; // 默认蓝色
    }
    point_marker.color.a = 1.0f;
    marker_pub_.publish(point_marker);
}

void MultiPlanePointConverter::clearPreviousMarkers(const std::string &frame_id, int plane_id)
{
    visualization_msgs::Marker delete_marker;
    delete_marker.header.frame_id = frame_id;
    delete_marker.header.stamp = ros::Time::now();
    delete_marker.ns = "global_converted_detections"; // 使用统一的命名空间
    delete_marker.id = 0;
    delete_marker.action = visualization_msgs::Marker::DELETEALL;
    marker_pub_.publish(delete_marker);
}

void MultiPlanePointConverter::publishAggregatedDetections(const std_msgs::Header &header_for_pub)
{
    // 准备发布消息
    cloud_recognition::Detection3DWithIDArray aggregated_detections_msg;
    aggregated_detections_msg.header = header_for_pub; // 使用传入的 header

    // 遍历全局检测点列表
    for (const auto &detection : global_detections_) // 直接遍历全局列表
    {
        // 将检测点添加到最终的发布消息中
        aggregated_detections_msg.detections.push_back(detection);
        // total_count++; // 可以保留或直接用 global_detections_.size()
    }
    // 发布聚合后的消息
    if (!aggregated_detections_msg.detections.empty())
    {
        detections3d_pub_.publish(aggregated_detections_msg);
        ROS_INFO("Published aggregated detections: %lu points (global list size: %lu)",
                 aggregated_detections_msg.detections.size(), global_detections_.size());
    }
    else
    {
        ROS_DEBUG("No detections to publish in aggregated message.");
    }
    //  可选：发布总数量
    std_msgs::Int32 count_msg;
    count_msg.data = global_detections_.size(); // 使用全局列表大小
    count_pub_.publish(count_msg);
}

void MultiPlanePointConverter::enforceIdLimit(int class_id)
{
    // 检查是否设置了该ID的限制
    auto limit_it = max_points_per_id_.find(class_id);
    if (limit_it == max_points_per_id_.end())
    {
        return; // 没有设置限制，不处理
    }

    int max_limit = limit_it->second;

    // 统计当前该ID的点数
    std::vector<std::pair<double, int>> points_with_scores; // {score, index}
    std::vector<int> indices_to_remove;                     // 记录需要删除的索引

    for (size_t i = 0; i < global_detections_.size(); ++i)
    {
        if (global_detections_[i].id == class_id)
        {
            points_with_scores.push_back({global_detections_[i].match_value, i});
        }
    }

    // 如果点数超过限制
    if (static_cast<int>(points_with_scores.size()) > max_limit)
    {
        // 按置信度排序（从低到高）
        std::sort(points_with_scores.begin(), points_with_scores.end());

        // 计算需要删除的点数
        int points_to_remove = points_with_scores.size() - max_limit;

        // 从置信度最低的开始删除
        for (int i = 0; i < points_to_remove; ++i)
        {
            int index_to_remove = points_with_scores[i].second;
            indices_to_remove.push_back(index_to_remove);

            // 发布删除标记
            visualization_msgs::Marker delete_marker;
            delete_marker.header.frame_id = global_detections_[index_to_remove].header.frame_id;
            delete_marker.header.stamp = ros::Time::now();
            delete_marker.ns = "global_converted_detections";
            delete_marker.id = index_to_remove;
            delete_marker.action = visualization_msgs::Marker::DELETE;
            marker_pub_.publish(delete_marker);

            ROS_INFO("Removed low-confidence point (ID: %d, Score: %.3f) due to ID limit",
                     class_id, points_with_scores[i].first);
        }

        // 按索引从大到小排序，避免删除时索引偏移
        std::sort(indices_to_remove.rbegin(), indices_to_remove.rend());

        // 从全局列表中删除
        for (int index_to_remove : indices_to_remove)
        {
            global_detections_.erase(global_detections_.begin() + index_to_remove);
        }
    }
}

int main(int argc, char **argv)
{
    ros::init(argc, argv, "plane_converter");
    MultiPlanePointConverter converter;
    ros::spin();
    return 0;
}
