#include <ros/ros.h>
#include <sensor_msgs/PointCloud2.h>
#include <pcl_ros/point_cloud.h>
#include <pcl_ros/transforms.h>
#include <pcl/point_types.h>
#include <pcl/filters/voxel_grid.h>
#include <pcl/filters/passthrough.h>
#include <pcl_conversions/pcl_conversions.h>
#include <tf2_ros/transform_listener.h>
#include <tf2_sensor_msgs/tf2_sensor_msgs.h>
#include <visualization_msgs/Marker.h>
#include <visualization_msgs/MarkerArray.h>
#include <std_srvs/Empty.h>
#include <std_msgs/String.h>
#include <geometry_msgs/PoseStamped.h>
#include <iostream>
#include <sstream>
#include <mutex>
#include <thread>
#include <cmath>
#include <set>
#include <deque> // 新增
#include <iomanip> // For std::setprecision

// 地图ROI参数结构 (保留区域)
struct MapROIParams {
    double min_x, max_x;
    double min_y, max_y;
    double min_z, max_z;
    bool enable_roi_filter;
};

// DisROI参数结构 (移除区域)
struct DisROIParams {
    double min_x, max_x;
    double min_y, max_y;
    double min_z, max_z;
    bool enable_disroi_filter;
};

class MapAccumulatorOnlyPublish {
public:
    MapAccumulatorOnlyPublish(ros::NodeHandle& nh) 
        : nh_(nh), private_nh_("~"), tf_listener_(tf_buffer_), accumulated_cloud_(new pcl::PointCloud<pcl::PointXYZ>),
          downsampled_cloud_(new pcl::PointCloud<pcl::PointXYZ>), clear_requested_(false),
          current_z_(-1.0), start_accumulation_(false) {
        
        // --- 读取基础参数 ---
        private_nh_.param("input_topic", input_topic_, std::string("/cloud_registered"));
        private_nh_.param("map_frame", map_frame_, std::string("camera_init"));
        private_nh_.param("voxel_leaf_size", voxel_leaf_size_, 0.05);
        private_nh_.param("downsampled_voxel_leaf_size", downsampled_voxel_leaf_size_, 0.2);
        private_nh_.param("max_points", max_points_, 5000000);
        private_nh_.param("enable_realtime_preview", enable_realtime_preview_, true);
        private_nh_.param("preview_rate", preview_rate_, 20.0);
        
        // --- Map ROI过滤参数 ---
        private_nh_.param("enable_map_roi_filter", map_roi_params_.enable_roi_filter, false);
        private_nh_.param("map_roi_min_x", map_roi_params_.min_x, -50.0);
        private_nh_.param("map_roi_max_x", map_roi_params_.max_x, 50.0);
        private_nh_.param("map_roi_min_y", map_roi_params_.min_y, -50.0);
        private_nh_.param("map_roi_max_y", map_roi_params_.max_y, 50.0);
        private_nh_.param("map_roi_min_z", map_roi_params_.min_z, -10.0);
        private_nh_.param("map_roi_max_z", map_roi_params_.max_z, 1.5);

        // --- DisROI过滤参数 ---
        private_nh_.param("enable_disroi_filter", disroi_params_.enable_disroi_filter, false);
        private_nh_.param("disroi_min_x", disroi_params_.min_x, -2.0);
        private_nh_.param("disroi_max_x", disroi_params_.max_x, 2.0);
        private_nh_.param("disroi_min_y", disroi_params_.min_y, -2.0);
        private_nh_.param("disroi_max_y", disroi_params_.max_y, 2.0);
        private_nh_.param("disroi_min_z", disroi_params_.min_z, -1.0);
        private_nh_.param("disroi_max_z", disroi_params_.max_z, 3.0);

        // --- 高Z柱体清除参数 ---
        private_nh_.param("enable_initial_high_z_filter", enable_initial_high_z_filter_, true);
        private_nh_.param("grid_size", grid_size_, 0.03);
        private_nh_.param("custom_max_height", custom_max_height_, 5.0);
        private_nh_.param("high_z_filter_duration", high_z_filter_duration_, 30.0);

        // --- 新增：滑动窗口参数 ---
        private_nh_.param("sliding_window_duration", sliding_window_duration_, 10.0); // 秒
        private_nh_.param("start_height_threshold", start_height_threshold_, 0.2);

        // --- 订阅与发布 ---
        cloud_sub_ = nh_.subscribe(input_topic_, 10, &MapAccumulatorOnlyPublish::cloudCallback, this);
        pose_sub_ = nh_.subscribe("/mavros/local_position/pose", 10, &MapAccumulatorOnlyPublish::poseCallback, this);
        map_pub_ = nh_.advertise<sensor_msgs::PointCloud2>("/map_accumulator/accumulated_map", 1);
        downsampled_map_pub_ = nh_.advertise<sensor_msgs::PointCloud2>("/map_accumulator/downsampled_map", 1);
        marker_pub_ = nh_.advertise<visualization_msgs::Marker>("/map_accumulator/map_info", 1);
        roi_marker_pub_ = nh_.advertise<visualization_msgs::MarkerArray>("/map_accumulator/roi_markers", 1);
        info_pub_ = nh_.advertise<std_msgs::String>("/map_accumulator/info", 1);

        // --- 服务 ---
        clear_service_ = nh_.advertiseService("/map_accumulator/clear_map", &MapAccumulatorOnlyPublish::clearMapService, this);
        get_info_service_ = nh_.advertiseService("/map_accumulator/get_info", &MapAccumulatorOnlyPublish::getInfoService, this);

        // --- 初始化时间 ---
        last_preview_time_ = ros::Time::now();
        start_time_ = ros::Time::now();

        // --- 统计计数器 ---
        total_points_received_ = 0;
        disroi_filtered_points_ = 0;
        roi_filtered_points_ = 0;
        accumulated_points_ = 0;
        frame_count_ = 0;

        ROS_INFO("MapAccumulatorOnlyPublish initialized (High-Z Filter: %s, Sliding Window: %.1fs)", 
                 enable_initial_high_z_filter_ ? "Enabled" : "Disabled", sliding_window_duration_);
        ROS_INFO("Accumulation starts when z > %.2f", start_height_threshold_);
        
        // --- 启动后台线程 ---
        background_thread_ = std::thread(&MapAccumulatorOnlyPublish::backgroundThread, this);
    }

    ~MapAccumulatorOnlyPublish() {
        if (background_thread_.joinable()) {
            background_thread_.join();
        }
        ROS_INFO("MapAccumulatorOnlyPublish shut down.");
    }

private:
    // ROS相关
    ros::NodeHandle nh_;
    ros::NodeHandle private_nh_;
    ros::Subscriber cloud_sub_;
    ros::Subscriber pose_sub_;
    ros::Publisher map_pub_;
    ros::Publisher downsampled_map_pub_;
    ros::Publisher marker_pub_;
    ros::Publisher roi_marker_pub_;
    ros::Publisher info_pub_;
    ros::ServiceServer clear_service_;
    ros::ServiceServer get_info_service_;

    // TF
    tf2_ros::Buffer tf_buffer_;
    tf2_ros::TransformListener tf_listener_;

    // 参数
    std::string input_topic_;
    std::string map_frame_;
    double voxel_leaf_size_;
    double downsampled_voxel_leaf_size_;
    int max_points_;
    bool enable_realtime_preview_;
    double preview_rate_;

    // ROI参数
    MapROIParams map_roi_params_;
    DisROIParams disroi_params_;

    // 高Z过滤参数
    bool enable_initial_high_z_filter_;
    double grid_size_;
    double custom_max_height_;
    double high_z_filter_duration_;
    ros::Time start_time_;

    // 滑动窗口参数
    double sliding_window_duration_;
    double start_height_threshold_;
    double current_z_;
    bool start_accumulation_; // 新增：是否已满足高度条件开始积累

    // 数据
    pcl::PointCloud<pcl::PointXYZ>::Ptr accumulated_cloud_;
    pcl::PointCloud<pcl::PointXYZ>::Ptr downsampled_cloud_;
    std::mutex cloud_mutex_;
    ros::Time last_preview_time_;
    int frame_count_;

    // 滑动窗口缓冲区
    struct CloudStamped {
        pcl::PointCloud<pcl::PointXYZ>::Ptr cloud;
        ros::Time stamp;
    };
    std::deque<CloudStamped> cloud_buffer_;

    // 高Z网格标记集
    std::set<std::pair<int, int>> filtered_xy_grids_; 

    // 统计计数器
    size_t total_points_received_;
    size_t disroi_filtered_points_;
    size_t roi_filtered_points_;
    size_t accumulated_points_;
    
    // 控制标志
    bool clear_requested_;
    std::mutex control_mutex_;

    // 线程
    std::thread background_thread_;

    // 回调函数
    void cloudCallback(const sensor_msgs::PointCloud2ConstPtr& cloud_msg);
    void poseCallback(const geometry_msgs::PoseStampedConstPtr& msg);

    // 点云处理
    pcl::PointCloud<pcl::PointXYZ>::Ptr transformCloud(const sensor_msgs::PointCloud2ConstPtr& cloud_msg);
    void downsampleCloud(pcl::PointCloud<pcl::PointXYZ>::Ptr& cloud);
    pcl::PointCloud<pcl::PointXYZ>::Ptr downsampleCloudNew(const pcl::PointCloud<pcl::PointXYZ>::Ptr& cloud, double leaf_size);
    pcl::PointCloud<pcl::PointXYZ>::Ptr filterMapROI(const pcl::PointCloud<pcl::PointXYZ>::Ptr& cloud);
    pcl::PointCloud<pcl::PointXYZ>::Ptr filterDisROI(const pcl::PointCloud<pcl::PointXYZ>::Ptr& cloud);

    // 高Z柱体清除逻辑
    void highZFilterAndMark(const pcl::PointCloud<pcl::PointXYZ>::Ptr& incoming_cloud);
    void applyHighZFilterToMap(); 

    // 地图管理（滑动窗口）
    void rebuildMapFromBuffer(); // 替代 addCloudToMap

    // 地图发布
    void publishMap();
    void publishDownsampledMap();
    void publishMapInfo();
    void publishROIMarkers();

    // 服务回调
    bool clearMapService(std_srvs::Empty::Request& req, std_srvs::Empty::Response& res);
    bool getInfoService(std_srvs::Empty::Request& req, std_srvs::Empty::Response& res);

    // 后台线程
    void backgroundThread();

    // 实时预览
    void realtimePreview();
};

// ==================== Callbacks ====================

void MapAccumulatorOnlyPublish::poseCallback(const geometry_msgs::PoseStampedConstPtr& msg) {
    current_z_ = msg->pose.position.z;
}

void MapAccumulatorOnlyPublish::cloudCallback(const sensor_msgs::PointCloud2ConstPtr& cloud_msg) {
    // 只要高度超过阈值，就开始积累， 后续不再检查高度
    if (current_z_ <= start_height_threshold_ && !start_accumulation_) {
        return;
    }
    if (!start_accumulation_) {
        start_accumulation_ = true;
        ROS_INFO("Height %.3f > %.3f: Starting point cloud accumulation.", current_z_, start_height_threshold_);
    }

    // 正常处理点云
    pcl::PointCloud<pcl::PointXYZ>::Ptr transformed_cloud = transformCloud(cloud_msg);
    if (!transformed_cloud || transformed_cloud->empty()) {
        return;
    }

    total_points_received_ += transformed_cloud->size();
    frame_count_++;
    
    if (enable_initial_high_z_filter_) {
        highZFilterAndMark(transformed_cloud); 
    }

    // 添加带时间戳的点云到缓冲区
    {
        std::lock_guard<std::mutex> lock(cloud_mutex_);
        cloud_buffer_.push_back({transformed_cloud, cloud_msg->header.stamp});
    }

    if (enable_realtime_preview_ && 
        (ros::Time::now() - last_preview_time_).toSec() > 1.0 / preview_rate_) {
        realtimePreview();
        last_preview_time_ = ros::Time::now();
    }
}

// ==================== Point Cloud Processing ====================

pcl::PointCloud<pcl::PointXYZ>::Ptr MapAccumulatorOnlyPublish::transformCloud(
    const sensor_msgs::PointCloud2ConstPtr& cloud_msg) {
    try {
        geometry_msgs::TransformStamped transform = tf_buffer_.lookupTransform(
            map_frame_, cloud_msg->header.frame_id, cloud_msg->header.stamp, ros::Duration(0.1));
        sensor_msgs::PointCloud2 transformed_msg;
        tf2::doTransform(*cloud_msg, transformed_msg, transform);
        pcl::PointCloud<pcl::PointXYZ>::Ptr cloud(new pcl::PointCloud<pcl::PointXYZ>);
        pcl::fromROSMsg(transformed_msg, *cloud);
        return cloud;
    } catch (tf2::TransformException& ex) {
        ROS_WARN("Transform failed: %s", ex.what());
        return nullptr;
    }
}

void MapAccumulatorOnlyPublish::downsampleCloud(pcl::PointCloud<pcl::PointXYZ>::Ptr& cloud) {
    if (cloud->empty() || voxel_leaf_size_ <= 0) {
        return;
    }
    pcl::VoxelGrid<pcl::PointXYZ> voxel_grid;
    voxel_grid.setInputCloud(cloud);
    voxel_grid.setLeafSize(voxel_leaf_size_, voxel_leaf_size_, voxel_leaf_size_);
    voxel_grid.filter(*cloud);
}

pcl::PointCloud<pcl::PointXYZ>::Ptr MapAccumulatorOnlyPublish::downsampleCloudNew(
    const pcl::PointCloud<pcl::PointXYZ>::Ptr& cloud, double leaf_size) {
    if (cloud->empty() || leaf_size <= 0) {
        return cloud;
    }
    pcl::PointCloud<pcl::PointXYZ>::Ptr downsampled_cloud(new pcl::PointCloud<pcl::PointXYZ>);
    pcl::VoxelGrid<pcl::PointXYZ> voxel_grid;
    voxel_grid.setInputCloud(cloud);
    voxel_grid.setLeafSize(leaf_size, leaf_size, leaf_size);
    voxel_grid.filter(*downsampled_cloud);
    return downsampled_cloud;
}

pcl::PointCloud<pcl::PointXYZ>::Ptr MapAccumulatorOnlyPublish::filterMapROI(
    const pcl::PointCloud<pcl::PointXYZ>::Ptr& cloud) {
    if (cloud->empty() || !map_roi_params_.enable_roi_filter) {
        return cloud;
    }

    pcl::PointCloud<pcl::PointXYZ>::Ptr region_cloud(new pcl::PointCloud<pcl::PointXYZ>);
    pcl::PointCloud<pcl::PointXYZ>::Ptr temp_cloud(new pcl::PointCloud<pcl::PointXYZ>);
    pcl::PassThrough<pcl::PointXYZ> pass;

    pass.setInputCloud(cloud);
    pass.setFilterFieldName("x");
    pass.setFilterLimits(map_roi_params_.min_x, map_roi_params_.max_x);
    pass.filter(*temp_cloud);

    if (temp_cloud->empty()) { roi_filtered_points_ += cloud->size(); return temp_cloud; }

    pass.setInputCloud(temp_cloud);
    pass.setFilterFieldName("y");
    pass.setFilterLimits(map_roi_params_.min_y, map_roi_params_.max_y);
    pass.filter(*region_cloud);

    if (region_cloud->empty()) { roi_filtered_points_ += temp_cloud->size(); return region_cloud; }

    pass.setInputCloud(region_cloud);
    pass.setFilterFieldName("z");
    pass.setFilterLimits(map_roi_params_.min_z, map_roi_params_.max_z);
    pass.filter(*region_cloud);

    size_t filtered_count = cloud->size() - region_cloud->size();
    roi_filtered_points_ += filtered_count;
    return region_cloud;
}

pcl::PointCloud<pcl::PointXYZ>::Ptr MapAccumulatorOnlyPublish::filterDisROI(
    const pcl::PointCloud<pcl::PointXYZ>::Ptr& cloud) {
    if (cloud->empty() || !disroi_params_.enable_disroi_filter) {
        return cloud; 
    }

    pcl::PointCloud<pcl::PointXYZ>::Ptr filtered_cloud(new pcl::PointCloud<pcl::PointXYZ>);
    size_t discard_count = 0;

    for (const auto& point : cloud->points) {
        bool inside_disroi = (point.x >= disroi_params_.min_x && point.x <= disroi_params_.max_x) &&
                             (point.y >= disroi_params_.min_y && point.y <= disroi_params_.max_y) &&
                             (point.z >= disroi_params_.min_z && point.z <= disroi_params_.max_z);
        
        if (!inside_disroi) {
            filtered_cloud->points.push_back(point);
        } else {
            discard_count++;
        }
    }

    filtered_cloud->width = filtered_cloud->points.size();
    filtered_cloud->height = 1;
    filtered_cloud->is_dense = cloud->is_dense;
    filtered_cloud->header = cloud->header;

    disroi_filtered_points_ += discard_count;
    return filtered_cloud;
}

// ==================== High-Z Filtering ====================

void MapAccumulatorOnlyPublish::highZFilterAndMark(const pcl::PointCloud<pcl::PointXYZ>::Ptr& incoming_cloud) {
    ros::Duration elapsed = ros::Time::now() - start_time_;
    if (elapsed.toSec() > high_z_filter_duration_) {
        ROS_INFO_ONCE("Initial high-Z filtering duration reached (%.1fs). Disabling further grid marking.", high_z_filter_duration_);
        return; 
    }

    std::lock_guard<std::mutex> lock(cloud_mutex_);
    for (const auto& point : incoming_cloud->points) {
        if (point.z > map_roi_params_.max_z && point.z <= custom_max_height_) {
            int grid_x = static_cast<int>(std::floor(point.x / grid_size_));
            int grid_y = static_cast<int>(std::floor(point.y / grid_size_));
            filtered_xy_grids_.insert({grid_x, grid_y});
        }
    }
}

void MapAccumulatorOnlyPublish::applyHighZFilterToMap() {
    if (filtered_xy_grids_.empty() || accumulated_cloud_->empty()) {
        return;
    }

    std::lock_guard<std::mutex> lock(cloud_mutex_);
    pcl::PointCloud<pcl::PointXYZ>::Ptr filtered_cloud(new pcl::PointCloud<pcl::PointXYZ>);
    filtered_cloud->reserve(accumulated_cloud_->size());
    size_t removed_count = 0;

    for (const auto& point : accumulated_cloud_->points) {
        int grid_x = static_cast<int>(std::floor(point.x / grid_size_));
        int grid_y = static_cast<int>(std::floor(point.y / grid_size_));
        if (filtered_xy_grids_.count({grid_x, grid_y})) {
            removed_count++;
        } else {
            filtered_cloud->points.push_back(point);
        }
    }

    accumulated_cloud_.swap(filtered_cloud);
    accumulated_cloud_->width = accumulated_cloud_->points.size();
    accumulated_cloud_->height = 1;
    accumulated_points_ = accumulated_cloud_->size();
    downsampled_cloud_ = downsampleCloudNew(accumulated_cloud_, downsampled_voxel_leaf_size_);
}

// ==================== Sliding Window Map Management ====================

void MapAccumulatorOnlyPublish::rebuildMapFromBuffer() {
    std::lock_guard<std::mutex> lock(cloud_mutex_);

    // 清空当前累积地图
    accumulated_cloud_->clear();
    accumulated_points_ = 0;

    if (cloud_buffer_.empty()) {
        downsampled_cloud_->clear();
        return;
    }

    ros::Time now = ros::Time::now();
    ros::Duration window(sliding_window_duration_);

    // 从队列前端移除过期的帧
    while (!cloud_buffer_.empty()) {
        ros::Duration age = now - cloud_buffer_.front().stamp;
        if (age > window) {
            cloud_buffer_.pop_front(); // 移除过期帧
        } else {
            break;
        }
    }

    // 合并所有未过期的帧到地图
    for (const auto& stamped_cloud : cloud_buffer_) {
        pcl::PointCloud<pcl::PointXYZ>::Ptr cloud = stamped_cloud.cloud;

        // 应用 DisROI 和 Map ROI 过滤
        pcl::PointCloud<pcl::PointXYZ>::Ptr disroi_filtered = filterDisROI(cloud);
        if (disroi_filtered->empty()) continue;

        pcl::PointCloud<pcl::PointXYZ>::Ptr roi_filtered = filterMapROI(disroi_filtered);
        if (roi_filtered->empty()) continue;

        pcl::PointCloud<pcl::PointXYZ>::Ptr downsampled(new pcl::PointCloud<pcl::PointXYZ>(*roi_filtered));
        downsampleCloud(downsampled);

        *accumulated_cloud_ += *downsampled;
        accumulated_points_ += downsampled->size();
    }

    // 全局降采样（如果超限）
    if (accumulated_cloud_->size() > static_cast<size_t>(max_points_)) {
        ROS_WARN_ONCE("Map size exceeds limit, downsampling entire map.");
        downsampleCloud(accumulated_cloud_);
        accumulated_points_ = accumulated_cloud_->size();
    }

    // 更新发布用的降采样地图
    downsampled_cloud_ = downsampleCloudNew(accumulated_cloud_, downsampled_voxel_leaf_size_);
}

// ==================== Services & Background ====================

bool MapAccumulatorOnlyPublish::clearMapService(std_srvs::Empty::Request& req, std_srvs::Empty::Response& res) {
    std::lock_guard<std::mutex> lock(control_mutex_);
    clear_requested_ = true;
    ROS_INFO("Clear map service requested");
    return true;
}

void MapAccumulatorOnlyPublish::backgroundThread() {
    ros::Rate rate(2); // 降低频率，因为 rebuildMapFromBuffer 可能较耗时
    while (ros::ok()) {
        {
            std::lock_guard<std::mutex> lock(control_mutex_);
            if (clear_requested_) {
                std::lock_guard<std::mutex> cloud_lock(cloud_mutex_);
                accumulated_cloud_->clear();
                downsampled_cloud_->clear();
                cloud_buffer_.clear(); // 清空缓冲区
                filtered_xy_grids_.clear(); 
                start_time_ = ros::Time::now();
                start_accumulation_ = false; // 重置积累状态
                frame_count_ = 0;
                total_points_received_ = 0;
                disroi_filtered_points_ = 0;
                roi_filtered_points_ = 0;
                accumulated_points_ = 0;
                clear_requested_ = false;
                ROS_INFO("Map cleared (sliding window reset)");
            }
        }
        
        // 定期重建地图（确保旧点被清除）
        rebuildMapFromBuffer();

        if (enable_initial_high_z_filter_ && !filtered_xy_grids_.empty()) {
            applyHighZFilterToMap();
        }

        static int counter = 0;
        if (++counter % 10 == 0) { // 每5秒
            publishMapInfo();
            publishROIMarkers(); 
        }
        rate.sleep();
    }
}

// ==================== Publishing ====================

void MapAccumulatorOnlyPublish::publishMapInfo() {
    std::lock_guard<std::mutex> lock(cloud_mutex_);
    std_msgs::String info_msg;
    std::stringstream ss;
    ss << std::fixed << std::setprecision(1);

    ss << "Map Info:\n";
    ss << "Points: " << accumulated_cloud_->size() << "\n";
    ss << "Downsampled Points: " << downsampled_cloud_->size() << "\n";
    ss << "Frames: " << frame_count_ << "\n";
    ss << "Buffered Frames: " << cloud_buffer_.size() << "\n"; // 新增
    ss << "Sliding Window: " << sliding_window_duration_ << "s\n"; // 新增
    ss << "HighZ Grids Marked: " << filtered_xy_grids_.size() << "\n";
    ss << "Accumulating: " << (start_accumulation_ ? "Yes" : "No") << "\n";

    if (total_points_received_ > 0) {
        ss << "=== Filtering Statistics ===\n";
        ss << "Total received: " << total_points_received_ << "\n";
        ss << "DisROI filtered: " << disroi_filtered_points_ << " (" << 100.0 * disroi_filtered_points_ / total_points_received_ << "%)\n";
        ss << "ROI filtered: " << roi_filtered_points_ << " (" << 100.0 * roi_filtered_points_ / total_points_received_ << "%)\n";
        ss << "Accumulated: " << accumulated_points_ << " (" << 100.0 * accumulated_points_ / total_points_received_ << "%)\n";
    }
    
    info_msg.data = ss.str();
    info_pub_.publish(info_msg);

    if (!accumulated_cloud_->empty()) {
        visualization_msgs::Marker marker;
        marker.header.stamp = ros::Time::now();
        marker.header.frame_id = map_frame_;
        marker.ns = "map_info";
        marker.id = 0;
        marker.type = visualization_msgs::Marker::TEXT_VIEW_FACING;
        marker.action = visualization_msgs::Marker::ADD;
        marker.pose.position.x = 0;
        marker.pose.position.y = 0;
        marker.pose.position.z = 5; 
        marker.pose.orientation.w = 1.0;
        marker.scale.z = 1.0;
        marker.color.r = 1.0;
        marker.color.g = 1.0;
        marker.color.b = 1.0;
        marker.color.a = 1.0;
        
        std::stringstream text_ss;
        text_ss << std::fixed << std::setprecision(0);
        text_ss << "Points: " << accumulated_cloud_->size() 
                << "\nDownsampled: " << downsampled_cloud_->size()
                << "\nFrames: " << frame_count_
                << "\nBuffer: " << cloud_buffer_.size()
                << "\nHigh-Z Grids: " << filtered_xy_grids_.size();
                
        marker.text = text_ss.str();
        marker_pub_.publish(marker);
    }
}

void MapAccumulatorOnlyPublish::realtimePreview() {
    rebuildMapFromBuffer(); // 重建最新窗口内的地图
    publishMap();
    publishDownsampledMap(); 
}

void MapAccumulatorOnlyPublish::publishMap() {
    std::lock_guard<std::mutex> lock(cloud_mutex_);
    if (accumulated_cloud_->empty()) return;
    sensor_msgs::PointCloud2 map_msg;
    pcl::toROSMsg(*accumulated_cloud_, map_msg);
    map_msg.header.stamp = ros::Time::now();
    map_msg.header.frame_id = map_frame_;
    map_pub_.publish(map_msg);
}

void MapAccumulatorOnlyPublish::publishDownsampledMap() {
    std::lock_guard<std::mutex> lock(cloud_mutex_);
    if (downsampled_cloud_->empty()) return;
    sensor_msgs::PointCloud2 downsampled_msg;
    pcl::toROSMsg(*downsampled_cloud_, downsampled_msg);
    downsampled_msg.header.stamp = ros::Time::now();
    downsampled_msg.header.frame_id = map_frame_;
    downsampled_map_pub_.publish(downsampled_msg);
}

void MapAccumulatorOnlyPublish::publishROIMarkers() {
    visualization_msgs::MarkerArray marker_array;
    
    if (map_roi_params_.enable_roi_filter) {
        visualization_msgs::Marker map_roi_marker;
        map_roi_marker.header.stamp = ros::Time::now();
        map_roi_marker.header.frame_id = map_frame_;
        map_roi_marker.ns = "map_roi";
        map_roi_marker.id = 0;
        map_roi_marker.type = visualization_msgs::Marker::CUBE;
        map_roi_marker.action = visualization_msgs::Marker::ADD;
        map_roi_marker.pose.position.x = (map_roi_params_.min_x + map_roi_params_.max_x) / 2.0;
        map_roi_marker.pose.position.y = (map_roi_params_.min_y + map_roi_params_.max_y) / 2.0;
        map_roi_marker.pose.position.z = (map_roi_params_.min_z + map_roi_params_.max_z) / 2.0;
        map_roi_marker.pose.orientation.w = 1.0;
        map_roi_marker.scale.x = map_roi_params_.max_x - map_roi_params_.min_x;
        map_roi_marker.scale.y = map_roi_params_.max_y - map_roi_params_.min_y;
        map_roi_marker.scale.z = map_roi_params_.max_z - map_roi_params_.min_z;
        map_roi_marker.color.r = 0.0;
        map_roi_marker.color.g = 1.0;
        map_roi_marker.color.b = 0.0;
        map_roi_marker.color.a = 0.2;
        marker_array.markers.push_back(map_roi_marker);
    }
    
    if (disroi_params_.enable_disroi_filter) {
        visualization_msgs::Marker disroi_marker;
        disroi_marker.header.stamp = ros::Time::now();
        disroi_marker.header.frame_id = map_frame_;
        disroi_marker.ns = "disroi";
        disroi_marker.id = 1;
        disroi_marker.type = visualization_msgs::Marker::CUBE;
        disroi_marker.action = visualization_msgs::Marker::ADD;
        disroi_marker.pose.position.x = (disroi_params_.min_x + disroi_params_.max_x) / 2.0;
        disroi_marker.pose.position.y = (disroi_params_.min_y + disroi_params_.max_y) / 2.0;
        disroi_marker.pose.position.z = (disroi_params_.min_z + disroi_params_.max_z) / 2.0;
        disroi_marker.pose.orientation.w = 1.0;
        disroi_marker.scale.x = disroi_params_.max_x - disroi_params_.min_x;
        disroi_marker.scale.y = disroi_params_.max_y - disroi_params_.min_y;
        disroi_marker.scale.z = disroi_params_.max_z - disroi_params_.min_z;
        disroi_marker.color.r = 1.0;
        disroi_marker.color.g = 0.0;
        disroi_marker.color.b = 0.0;
        disroi_marker.color.a = 0.3;
        marker_array.markers.push_back(disroi_marker);
    }
    
    if (!marker_array.markers.empty()) {
        roi_marker_pub_.publish(marker_array);
    }
}

bool MapAccumulatorOnlyPublish::getInfoService(std_srvs::Empty::Request& req, std_srvs::Empty::Response& res) {
    publishMapInfo();
    return true;
}

// ==================== Main ====================

int main(int argc, char** argv) {
    ros::init(argc, argv, "map_accumulator_only_node");
    ros::NodeHandle nh;
    MapAccumulatorOnlyPublish accumulator(nh);
    ros::spin();
    return 0;
}