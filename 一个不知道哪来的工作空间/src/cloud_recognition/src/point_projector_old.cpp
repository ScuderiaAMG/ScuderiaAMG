#include <ros/ros.h>
#include <sensor_msgs/PointCloud2.h>
#include <sensor_msgs/Image.h>
#include <sensor_msgs/image_encodings.h>
#include <geometry_msgs/PoseStamped.h>
#include <geometry_msgs/Point32.h>        // 用于表示点 (PolygonStamped 使用 Point32)
#include <geometry_msgs/PolygonStamped.h> // 用于发布多边形（四个顶点）
#include <pcl_conversions/pcl_conversions.h>
#include <pcl/point_cloud.h>
#include <pcl/point_types.h>
#include <yaml-cpp/yaml.h>
#include <cv_bridge/cv_bridge.h>
#include <opencv2/opencv.hpp>
#include <tf2_ros/transform_listener.h>
#include <tf2_geometry_msgs/tf2_geometry_msgs.h>
#include <tf2_sensor_msgs/tf2_sensor_msgs.h>
#include <tf2_eigen/tf2_eigen.h>
#include <Eigen/Dense>
#include <Eigen/Geometry>
#include <map>
#include <vector>
#include <string>
#include <limits>
#include <cmath>      // for M_PI, ceil
#include <functional> // for std::bind
#include <algorithm>  // for std::max, std::ceil

// --- PointCloudProjector 类定义 ---
class PointCloudProjector
{
private:
    ros::NodeHandle nh_;
    ros::NodeHandle nh_private_;
    ros::Publisher image_pub_;
    ros::Publisher plane_pose_pub_;
    ros::Publisher plane_corners_pub_; // 发布四个顶点
    double point_radius_;
    std::string target_frame_;
    Eigen::Vector3d plane_center_;
    Eigen::Vector3d x_axis_;
    Eigen::Vector3d y_axis_;
    Eigen::Vector3d z_axis_;

    // 原始配置参数（现在作为最小尺寸或备用）
    int config_image_width_;
    int config_image_height_;

    // --- 新增/修改的成员变量 ---
    double plane_width_;          // 动态计算的物理宽度
    double extrusion_length_;     // 动态计算的物理长度
    double resolution_x_;         // 固定或动态计算的 X 方向分辨率
    double resolution_y_;         // 固定或动态计算的 Y 方向分辨率
    int dynamic_image_width_px_;  // 动态计算的图像宽度（像素）
    int dynamic_image_height_px_; // 动态计算的图像高度（像素）

    // --- 固定分辨率相关参数 ---
    double fixed_resolution_m_per_px_; // 固定的物理分辨率 (m/px)
    bool use_fixed_resolution_;        // 是否使用固定分辨率

public:
    // --- 修改构造函数签名，添加新参数 ---
    PointCloudProjector(ros::NodeHandle &nh, ros::NodeHandle &nh_private,
                        const std::string &target_frame, double point_radius,
                        int image_width, int image_height,             // 保留原始配置参数
                        double fixed_res_m_per_px, bool use_fixed_res) // 新增参数
        : nh_(nh), nh_private_(nh_private), target_frame_(target_frame),
          point_radius_(point_radius),
          config_image_width_(image_width), config_image_height_(image_height), // 保存配置参数
          // --- 初始化新增成员变量 ---
          fixed_resolution_m_per_px_(fixed_res_m_per_px), use_fixed_resolution_(use_fixed_res),
          // 初始化动态尺寸为配置的最小值，以防万一
          dynamic_image_width_px_(image_width), dynamic_image_height_px_(image_height)
    {
        // 构造函数体可以保持为空或添加初始化逻辑
    }

    void initializePublishers(int plane_id)
    {
        std::string prefix = "/point_projector/plane_" + std::to_string(plane_id);
        image_pub_ = nh_.advertise<sensor_msgs::Image>(prefix + "/projected_image", 1);
        plane_pose_pub_ = nh_.advertise<geometry_msgs::PoseStamped>(prefix + "/projected_plane_pose", 1);
        plane_corners_pub_ = nh_.advertise<geometry_msgs::PolygonStamped>(prefix + "/plane_corners", 1);
        ROS_INFO("Initialized publishers for Plane ID: %d", plane_id);
    }

    void processPlaneCloud(const pcl::PointCloud<pcl::PointXYZ>::Ptr &cloud, const std_msgs::Header &header)
    {
        if (cloud->empty())
        {
            ROS_WARN("Received empty plane cloud");
            return;
        }
        if (!createProjectionPlane(cloud))
        {
            ROS_WARN("Failed to create projection plane for cloud");
            return;
        }

        // --- 核心修改：根据动态计算的尺寸创建图像 ---
        cv::Mat projected_image = cv::Mat::zeros(dynamic_image_height_px_, dynamic_image_width_px_, CV_8UC1);

        for (const auto &point : cloud->points)
        {
            Eigen::Vector3d point_3d(point.x, point.y, point.z);
            Eigen::Vector3d projected_point = projectPointToPlane(point_3d);
            int pixel_x, pixel_y;
            if (worldToPixel(projected_point, pixel_x, pixel_y))
            {
                drawPointOnImage(projected_image, pixel_x, pixel_y);
            }
        }

        sensor_msgs::ImagePtr image_msg = cv_bridge::CvImage(
                                              header,
                                              sensor_msgs::image_encodings::MONO8,
                                              projected_image)
                                              .toImageMsg();
        image_pub_.publish(image_msg);
        publishPlaneInfo(header); // 会同时发布姿态和顶点
    }

private:
    bool createProjectionPlane(const pcl::PointCloud<pcl::PointXYZ>::Ptr &cloud)
    {
        std::vector<Eigen::Vector2d> xy_points;
        for (const auto &point : cloud->points)
        {
            xy_points.emplace_back(point.x, point.y);
        }
        if (xy_points.size() < 2)
        {
            ROS_WARN("Not enough points for line fitting");
            return false;
        }
        Eigen::Vector2d line_direction;
        Eigen::Vector2d line_center;
        if (!fitLinePCA(xy_points, line_direction, line_center))
        {
            ROS_WARN("Failed to fit line to projected points");
            return false;
        }
        Eigen::Vector3d line_dir_3d(line_direction(0), line_direction(1), 0.0);
        line_dir_3d.normalize();
        z_axis_ = line_dir_3d.cross(Eigen::Vector3d(0, 0, 1)).normalized();
        x_axis_ = line_dir_3d;
        y_axis_ << 0, 0, 1;
        calculatePlaneSizeAndCenter(cloud, line_center);
        ROS_DEBUG("Created projection plane:");
        ROS_DEBUG("  Plane center: (%.3f, %.3f, %.3f)",
                  plane_center_(0), plane_center_(1), plane_center_(2));
        ROS_DEBUG("  Plane size (phys): %.2f x %.2f m", plane_width_, extrusion_length_);
        ROS_DEBUG("  Image size (px): %d x %d", dynamic_image_width_px_, dynamic_image_height_px_);
        ROS_DEBUG("  Resolution: %.6f m/px", resolution_x_); // x_ 和 y_ 应该相同
        return true;
    }

    bool fitLinePCA(const std::vector<Eigen::Vector2d> &points,
                    Eigen::Vector2d &direction, Eigen::Vector2d &center)
    {
        if (points.empty())
            return false;
        Eigen::Vector2d sum = Eigen::Vector2d::Zero();
        for (const auto &point : points)
        {
            sum += point;
        }
        center = sum / points.size();
        Eigen::Matrix2d covariance = Eigen::Matrix2d::Zero();
        for (const auto &point : points)
        {
            Eigen::Vector2d rel_vec = point - center;
            covariance += rel_vec * rel_vec.transpose();
        }
        covariance /= points.size();
        Eigen::SelfAdjointEigenSolver<Eigen::Matrix2d> eigen_solver(covariance);
        if (eigen_solver.info() != Eigen::Success)
        {
            return false;
        }
        direction = eigen_solver.eigenvectors().col(1);
        direction.normalize();
        return true;
    }

    // --- 修改后的 calculatePlaneSizeAndCenter 函数 ---
    void calculatePlaneSizeAndCenter(const pcl::PointCloud<pcl::PointXYZ>::Ptr &cloud,
                                     const Eigen::Vector2d &line_center_2d)
    {
        double min_x = std::numeric_limits<double>::max();
        double max_x = std::numeric_limits<double>::lowest();
        double min_z = std::numeric_limits<double>::max();
        double max_z = std::numeric_limits<double>::lowest();
        for (const auto &point : cloud->points)
        {
            Eigen::Vector3d point_vec(point.x, point.y, point.z);
            Eigen::Vector3d rel_vec = point_vec - Eigen::Vector3d(line_center_2d(0), line_center_2d(1), 0.0);
            double proj_x = rel_vec.dot(x_axis_);
            double proj_z = point.z;
            min_x = std::min(min_x, proj_x);
            max_x = std::max(max_x, proj_x);
            min_z = std::min(min_z, proj_z);
            max_z = std::max(max_z, proj_z);
        }

        // 1. 计算原始尺寸（加了边界）
        double original_plane_width = (max_x - min_x) + 2 * 0.3;
        double original_extrusion_length = (max_z - min_z) + 2 * 0.2;

        // 2. 计算原始中心点（在世界坐标系中）
        double center_x_proj_original = (max_x + min_x) / 2.0;
        double center_z_original = (max_z + min_z) / 2.0;
        Eigen::Vector3d center_offset_original = center_x_proj_original * x_axis_ + center_z_original * y_axis_; // y_axis_ is (0,0,1)
        Eigen::Vector3d original_plane_center_world = Eigen::Vector3d(line_center_2d(0), line_center_2d(1), 0.0) + center_offset_original;

        double final_resolution_x, final_resolution_y;
        double final_plane_width, final_extrusion_length;
        int final_image_width_px, final_image_height_px;

        if (use_fixed_resolution_ && fixed_resolution_m_per_px_ > 0)
        {
            // --- 使用固定分辨率 ---
            final_resolution_x = fixed_resolution_m_per_px_;
            final_resolution_y = fixed_resolution_m_per_px_;

            // 根据固定分辨率和原始物理尺寸计算所需的像素数
            // ceil 确保像素数足够容纳物理尺寸
            final_image_width_px = std::ceil(original_plane_width / final_resolution_x);
            final_image_height_px = std::ceil(original_extrusion_length / final_resolution_y);

            // 为了保证严格的固定分辨率，物理尺寸应为整数像素数 * 分辨率
            // 或者，我们保持物理尺寸为原始尺寸，但图像尺寸是能容纳它的最小整数像素尺寸
            // 这里采用后者，物理尺寸是精确的原始尺寸，图像像素是向上取整的
            // 但为了使分辨率严格等于 fixed_resolution_m_per_px_，我们应使用：
            // final_plane_width = final_image_width_px * final_resolution_x;
            // final_extrusion_length = final_image_height_px * final_resolution_y;
            // 这样做物理尺寸会略微增大以适应整数像素，这是更严格的固定分辨率实现。
            // 采用更严格的实现：
            final_plane_width = final_image_width_px * final_resolution_x;
            final_extrusion_length = final_image_height_px * final_resolution_y;

            // 平面中心仍然使用原始ROI的中心
            plane_center_ = original_plane_center_world;
        }
        else
        {
            // --- 使用原始的动态分辨率逻辑 ---
            // 为了兼容性，仍然使用 config_image_width_ 和 config_image_height_
            double resolution_x_needed = original_plane_width / config_image_width_;
            double resolution_y_needed = original_extrusion_length / config_image_height_;
            double resolution = std::max(resolution_x_needed, resolution_y_needed);

            final_resolution_x = resolution;
            final_resolution_y = resolution;
            final_image_width_px = config_image_width_;
            final_image_height_px = config_image_height_;
            final_plane_width = resolution * config_image_width_;
            final_extrusion_length = resolution * config_image_height_;
            plane_center_ = original_plane_center_world; // 保持原始中心
        }

        // 5. 更新成员变量
        plane_width_ = final_plane_width;
        extrusion_length_ = final_extrusion_length;
        resolution_x_ = final_resolution_x;
        resolution_y_ = final_resolution_y;
        dynamic_image_width_px_ = final_image_width_px;
        dynamic_image_height_px_ = final_image_height_px;

        ROS_DEBUG("Plane sizing - Original: %.2fx%.2f m, Final: %.2fx%.2f m (%dx%d px), Resolution: %.6f m/px",
                  original_plane_width, original_extrusion_length,
                  plane_width_, extrusion_length_,
                  dynamic_image_width_px_, dynamic_image_height_px_,
                  resolution_x_);
    }

    Eigen::Vector3d projectPointToPlane(const Eigen::Vector3d &point)
    {
        Eigen::Vector3d rel_vec = point - plane_center_;
        double distance = rel_vec.dot(z_axis_);
        return point - distance * z_axis_;
    }

    // --- 修改：使用动态图像尺寸进行检查 ---
    bool worldToPixel(const Eigen::Vector3d &world_point, int &pixel_x, int &pixel_y)
    {
        Eigen::Vector3d rel_vec = world_point - plane_center_;
        double proj_x = rel_vec.dot(x_axis_);
        double proj_y = rel_vec.dot(y_axis_);

        // 使用动态计算的物理尺寸进行边界检查
        if (std::abs(proj_x) > plane_width_ / 2.0 || std::abs(proj_y) > extrusion_length_ / 2.0)
        {
            return false;
        }

        pixel_x = static_cast<int>((proj_x + plane_width_ / 2.0) / resolution_x_);
        pixel_y = static_cast<int>((extrusion_length_ / 2.0 - proj_y) / resolution_y_);

        // 使用动态计算的像素尺寸进行边界检查
        if (pixel_x >= 0 && pixel_x < dynamic_image_width_px_ &&
            pixel_y >= 0 && pixel_y < dynamic_image_height_px_)
        {
            return true;
        }
        return false;
    }

    // --- 修改：使用动态分辨率和图像尺寸 ---
    void drawPointOnImage(cv::Mat &image, int center_x, int center_y)
    {
        // 分辨率现在是固定的或动态计算的统一值
        int radius_pixels_x = static_cast<int>(std::ceil(point_radius_ / resolution_x_));
        int radius_pixels_y = static_cast<int>(std::ceil(point_radius_ / resolution_y_));
        radius_pixels_x = std::max(1, radius_pixels_x);
        radius_pixels_y = std::max(1, radius_pixels_y);
        cv::ellipse(image,
                    cv::Point(center_x, center_y),
                    cv::Size(radius_pixels_x, radius_pixels_y),
                    0, 0, 360,
                    cv::Scalar(255), -1);
    }

    // 修改：将发布姿态和顶点的逻辑合并
    void publishPlaneInfo(const std_msgs::Header &header)
    {
        // 发布平面姿态
        geometry_msgs::PoseStamped plane_pose;
        plane_pose.header = header;
        plane_pose.pose.position.x = plane_center_(0);
        plane_pose.pose.position.y = plane_center_(1);
        plane_pose.pose.position.z = plane_center_(2);
        Eigen::Matrix3d rotation_matrix;
        rotation_matrix.col(0) = x_axis_;
        rotation_matrix.col(1) = y_axis_;
        rotation_matrix.col(2) = z_axis_;
        Eigen::Quaterniond quaternion(rotation_matrix);
        quaternion.normalize();
        plane_pose.pose.orientation.x = quaternion.x();
        plane_pose.pose.orientation.y = quaternion.y();
        plane_pose.pose.orientation.z = quaternion.z();
        plane_pose.pose.orientation.w = quaternion.w();
        plane_pose_pub_.publish(plane_pose);

        // 发布四个顶点
        publishPlaneCorners(header);
    }

    // --- 修改：确保顶点坐标与动态计算的平面尺寸一致 ---
    void publishPlaneCorners(const std_msgs::Header &header)
    {
        // 使用动态计算的 plane_width_ 和 extrusion_length_
        double half_width = plane_width_ / 2.0;
        double half_height = extrusion_length_ / 2.0;

        // 局部坐标 (以 plane_center_ 为原点)
        Eigen::Vector3d corner_local_bl(-half_width, -half_height, 0); // Bottom-Left
        Eigen::Vector3d corner_local_tl(-half_width, half_height, 0);  // Top-Left
        Eigen::Vector3d corner_local_tr(half_width, half_height, 0);   // Top-Right
        Eigen::Vector3d corner_local_br(half_width, -half_height, 0);  // Bottom-Right

        // 转换到世界坐标
        Eigen::Vector3d corner_world_bl = plane_center_ +
                                          corner_local_bl(0) * x_axis_ + corner_local_bl(1) * y_axis_ + corner_local_bl(2) * z_axis_;
        Eigen::Vector3d corner_world_tl = plane_center_ +
                                          corner_local_tl(0) * x_axis_ + corner_local_tl(1) * y_axis_ + corner_local_tl(2) * z_axis_;
        Eigen::Vector3d corner_world_tr = plane_center_ +
                                          corner_local_tr(0) * x_axis_ + corner_local_tr(1) * y_axis_ + corner_local_tr(2) * z_axis_;
        Eigen::Vector3d corner_world_br = plane_center_ +
                                          corner_local_br(0) * x_axis_ + corner_local_br(1) * y_axis_ + corner_local_br(2) * z_axis_;

        // 创建并填充 PolygonStamped 消息
        geometry_msgs::PolygonStamped corners_msg;
        corners_msg.header = header;
        corners_msg.polygon.points.resize(4);

        corners_msg.polygon.points[0].x = corner_world_bl(0);
        corners_msg.polygon.points[0].y = corner_world_bl(1);
        corners_msg.polygon.points[0].z = corner_world_bl(2);
        corners_msg.polygon.points[1].x = corner_world_tl(0);
        corners_msg.polygon.points[1].y = corner_world_tl(1);
        corners_msg.polygon.points[1].z = corner_world_tl(2);
        corners_msg.polygon.points[2].x = corner_world_tr(0);
        corners_msg.polygon.points[2].y = corner_world_tr(1);
        corners_msg.polygon.points[2].z = corner_world_tr(2);
        corners_msg.polygon.points[3].x = corner_world_br(0);
        corners_msg.polygon.points[3].y = corner_world_br(1);
        corners_msg.polygon.points[3].z = corner_world_br(2);

        // 发布消息
        plane_corners_pub_.publish(corners_msg);

        // 可选：打印日志
        ROS_DEBUG("Published plane corners for frame %s (size: %.2fx%.2fm):", header.frame_id.c_str(), plane_width_, extrusion_length_);
        ROS_DEBUG("  BL: (%.3f, %.3f, %.3f)", corner_world_bl(0), corner_world_bl(1), corner_world_bl(2));
        ROS_DEBUG("  TL: (%.3f, %.3f, %.3f)", corner_world_tl(0), corner_world_tl(1), corner_world_tl(2));
        ROS_DEBUG("  TR: (%.3f, %.3f, %.3f)", corner_world_tr(0), corner_world_tr(1), corner_world_tr(2));
        ROS_DEBUG("  BR: (%.3f, %.3f, %.3f)", corner_world_br(0), corner_world_br(1), corner_world_br(2));
    }
};

// --- 修改后的主类 ---
class MultiTopicPlaneProjector
{
private:
    ros::NodeHandle nh_;
    ros::NodeHandle nh_private_;
    std::vector<ros::Subscriber> input_subs_;
    std::string config_file_;
    std::string target_frame_;
    double point_radius_;
    int image_width_;  // 保留原始配置参数
    int image_height_; // 保留原始配置参数
    std::vector<std::string> input_topics_;
    std::vector<PointCloudProjector> projectors_;
    tf2_ros::Buffer tf_buffer_;
    tf2_ros::TransformListener tf_listener_;

    // --- 新增成员变量：用于固定分辨率 ---
    double fixed_resolution_m_per_px_; // 固定的物理分辨率 (m/px)
    bool use_fixed_resolution_;        // 是否使用固定分辨率

public:
    MultiTopicPlaneProjector()
        : nh_private_("~"),
          tf_buffer_(),
          tf_listener_(tf_buffer_),
          // --- 初始化新增成员变量 ---
          fixed_resolution_m_per_px_(0.01), // 默认值，例如 1cm/像素
          use_fixed_resolution_(false)      // 默认关闭，使用动态分辨率
    {
        // 1. 首先加载 config_file 路径
        nh_private_.param<std::string>("config_file", config_file_, "projector_config.yaml");
        // 2. 加载 YAML 配置文件
        loadConfig();

        // 3. 处理参数默认值 (ROS 参数服务器 -> YAML 配置 -> 硬编码默认值)
        nh_private_.param<std::string>("target_frame", target_frame_, target_frame_);
        if (target_frame_.empty())
            target_frame_ = "world";

        nh_private_.param<double>("point_radius", point_radius_, point_radius_);
        if (point_radius_ <= 0)
            point_radius_ = 0.05;

        nh_private_.param<int>("image_width", image_width_, image_width_);
        if (image_width_ <= 0)
            image_width_ = 800;

        nh_private_.param<int>("image_height", image_height_, image_height_);
        if (image_height_ <= 0)
            image_height_ = 600;

        // --- 加载固定分辨率参数 ---
        nh_private_.param<double>("fixed_resolution_m_per_px", fixed_resolution_m_per_px_, fixed_resolution_m_per_px_);
        nh_private_.param<bool>("use_fixed_resolution", use_fixed_resolution_, use_fixed_resolution_);
        // YAML 配置已通过 loadConfig 加载，具有最高优先级

        if (input_topics_.empty())
        {
            ROS_ERROR("No input topics configured. Exiting.");
            return;
        }

        int num_topics = input_topics_.size();
        projectors_.reserve(num_topics);
        input_subs_.reserve(num_topics);

        for (int i = 0; i < num_topics; ++i)
        {
            // --- 修改 emplace_back 调用，传递新增的参数 ---
            projectors_.emplace_back(nh_, nh_private_, target_frame_, point_radius_,
                                     image_width_, image_height_,                        // 传递原始配置参数
                                     fixed_resolution_m_per_px_, use_fixed_resolution_); // 传递新参数
            projectors_[i].initializePublishers(i + 1);
            ROS_INFO("Initialized projector ID: %d for topic: %s", i + 1, input_topics_[i].c_str());
        }

        for (int i = 0; i < num_topics; ++i)
        {
            ros::Subscriber sub = nh_.subscribe<sensor_msgs::PointCloud2>(
                input_topics_[i], 1,
                [this, i](const sensor_msgs::PointCloud2ConstPtr &msg)
                {
                    this->planeCloudCallback(msg, i);
                });
            input_subs_.push_back(sub);
            ROS_INFO("Subscribed to input topic: %s", input_topics_[i].c_str());
        }

        ROS_INFO("MultiTopicPlaneProjector initialized.");
        ROS_INFO("Target frame: %s", target_frame_.c_str());
        ROS_INFO("Point radius: %.3f m", point_radius_);
        // --- 打印分辨率配置 ---
        if (use_fixed_resolution_)
        {
            ROS_INFO("Using FIXED resolution: %.6f m/px", fixed_resolution_m_per_px_);
            ROS_INFO("Image size will be DYNAMIC based on point cloud bounds.");
        }
        else
        {
            ROS_INFO("Using DYNAMIC resolution (based on point cloud bounds and config image size %dx%d).", image_width_, image_height_);
        }
        ROS_INFO("Number of input topics: %zu", input_topics_.size());
    }

private:
    void loadConfig()
    {
        try
        {
            YAML::Node config = YAML::LoadFile(config_file_);
            ROS_INFO_STREAM("Loading configuration from: " << config_file_);

            if (config["input_topics"])
            {
                YAML::Node topics_node = config["input_topics"];
                if (topics_node.IsSequence())
                {
                    input_topics_.clear();
                    for (const auto &topic_node : topics_node)
                    {
                        std::string topic = topic_node.as<std::string>();
                        if (!topic.empty())
                            input_topics_.push_back(topic);
                        else
                            ROS_WARN("Empty topic name found in config, ignoring.");
                    }
                    if (input_topics_.empty())
                        ROS_WARN("input_topics list is empty in config file %s.", config_file_.c_str());
                    else
                        ROS_INFO("Loaded %zu input topics from config.", input_topics_.size());
                }
                else
                    ROS_ERROR("input_topics in config file %s is not a sequence.", config_file_.c_str());
            }
            else
                ROS_ERROR("Required configuration 'input_topics' not found in %s.", config_file_.c_str());

            // 加载其他 YAML 配置项
            if (config["target_frame"])
            {
                target_frame_ = config["target_frame"].as<std::string>();
                ROS_INFO_STREAM("Loaded target_frame from YAML: " << target_frame_);
            }
            if (config["point_radius"])
            {
                point_radius_ = config["point_radius"].as<double>();
                ROS_INFO_STREAM("Loaded point_radius from YAML: " << point_radius_);
            }
            if (config["image_width"])
            {
                image_width_ = config["image_width"].as<int>();
                ROS_INFO_STREAM("Loaded image_width from YAML: " << image_width_);
            }
            if (config["image_height"])
            {
                image_height_ = config["image_height"].as<int>();
                ROS_INFO_STREAM("Loaded image_height from YAML: " << image_height_);
            }

            // --- 加载固定分辨率的 YAML 配置 ---
            if (config["fixed_resolution_m_per_px"])
            {
                fixed_resolution_m_per_px_ = config["fixed_resolution_m_per_px"].as<double>();
                ROS_INFO_STREAM("Loaded fixed_resolution_m_per_px from YAML: " << fixed_resolution_m_per_px_);
            }
            if (config["use_fixed_resolution"])
            {
                use_fixed_resolution_ = config["use_fixed_resolution"].as<bool>();
                ROS_INFO_STREAM("Loaded use_fixed_resolution from YAML: " << std::boolalpha << use_fixed_resolution_);
            }
        }
        catch (const YAML::Exception &e)
        {
            ROS_ERROR("YAML Exception: Failed to load config file '%s': %s", config_file_.c_str(), e.what());
        }
        catch (const std::exception &e)
        {
            ROS_ERROR("Standard Exception: Failed to load config file '%s': %s", config_file_.c_str(), e.what());
        }
        catch (...)
        {
            ROS_ERROR("Unknown error occurred while loading config file '%s'", config_file_.c_str());
        }
    }

    void planeCloudCallback(const sensor_msgs::PointCloud2ConstPtr &cloud_msg, int projector_index)
    {
        if (projector_index < 0 || projector_index >= static_cast<int>(projectors_.size()))
        {
            ROS_ERROR("Invalid projector index %d received in callback.", projector_index);
            return;
        }

        sensor_msgs::PointCloud2 transformed_cloud;
        if (target_frame_ != cloud_msg->header.frame_id)
        {
            try
            {
                geometry_msgs::TransformStamped transform = tf_buffer_.lookupTransform(
                    target_frame_, cloud_msg->header.frame_id, cloud_msg->header.stamp);
                tf2::doTransform(*cloud_msg, transformed_cloud, transform);
            }
            catch (tf2::TransformException &ex)
            {
                ROS_WARN("TF Transform failed: %s", ex.what());
                return;
            }
        }
        else
        {
            transformed_cloud = *cloud_msg;
        }

        pcl::PointCloud<pcl::PointXYZ>::Ptr input_cloud(new pcl::PointCloud<pcl::PointXYZ>);
        pcl::fromROSMsg(transformed_cloud, *input_cloud);

        if (input_cloud->empty())
        {
            ROS_WARN("Received empty point cloud on topic index %d", projector_index);
            return;
        }

        ROS_DEBUG("Processing cloud from topic index %d with projector ID: %d", projector_index, projector_index + 1);
        projectors_[projector_index].processPlaneCloud(input_cloud, cloud_msg->header);
    }
};

// --- 主函数 ---
int main(int argc, char **argv)
{
    ros::init(argc, argv, "point_projector");
    MultiTopicPlaneProjector projector;
    ros::spin();
    return 0;
}