#include <ros/ros.h>
#include <sensor_msgs/PointCloud2.h>
#include <sensor_msgs/Image.h>
#include <sensor_msgs/image_encodings.h>
#include <geometry_msgs/PoseStamped.h>
#include <geometry_msgs/Point32.h>
#include <geometry_msgs/PolygonStamped.h>
#include <pcl_conversions/pcl_conversions.h>
#include <pcl/point_cloud.h>
#include <pcl/point_types.h>
#include <yaml-cpp/yaml.h>
#include <cv_bridge/cv_bridge.h>
#include <opencv2/opencv.hpp>
#include <tf2_ros/transform_listener.h>
#include <tf2_geometry_msgs/tf2_geometry_msgs.h>
#include <tf2_sensor_msgs/tf2_sensor_msgs.h>
#include <Eigen/Dense>
#include <Eigen/Geometry>
#include <map>
#include <vector>
#include <string>
#include <limits>
#include <cmath>
#include <functional>
#include <algorithm>

// 新增：用于发布带孔多边形
#include <jsk_recognition_msgs/PolygonArray.h>

// --- PointCloudProjector 类定义 ---
class PointCloudProjector
{
private:
    ros::NodeHandle nh_;
    ros::NodeHandle nh_private_;
    ros::Publisher image_pub_;
    ros::Publisher plane_pose_pub_;
    ros::Publisher plane_corners_pub_;
    ros::Publisher polygon_array_pub_;

    std::string target_frame_;
    Eigen::Vector3d plane_center_;
    Eigen::Vector3d x_axis_;
    Eigen::Vector3d y_axis_;
    Eigen::Vector3d z_axis_;

    // 原始配置参数
    int config_image_width_;
    int config_image_height_;

    // 动态尺寸
    double plane_width_;
    double extrusion_length_;
    double resolution_x_;
    double resolution_y_;
    int dynamic_image_width_px_;
    int dynamic_image_height_px_;

    // 固定分辨率相关
    double fixed_resolution_m_per_px_;
    bool use_fixed_resolution_;

    // 形态学参数
    int morphology_kernel_size_;

    // 微孔面积阈值（单位为像素）
    int min_hole_area_px_;

public:
    PointCloudProjector(ros::NodeHandle &nh, ros::NodeHandle &nh_private,
                        const std::string &target_frame,
                        int image_width, int image_height,
                        double fixed_res_m_per_px, bool use_fixed_res,
                        int kernel_size,
                        int min_hole_area_px = 50) // 👈 新增参数
        : nh_(nh), nh_private_(nh_private), target_frame_(target_frame),
          config_image_width_(image_width), config_image_height_(image_height),
          fixed_resolution_m_per_px_(fixed_res_m_per_px),
          use_fixed_resolution_(use_fixed_res),
          dynamic_image_width_px_(image_width), dynamic_image_height_px_(image_height),
          morphology_kernel_size_(kernel_size),
          min_hole_area_px_(min_hole_area_px) // 初始化
    {
    }

    void initializePublishers(int plane_id)
    {
        std::string prefix = "/point_projector/plane_" + std::to_string(plane_id);
        image_pub_ = nh_.advertise<sensor_msgs::Image>(prefix + "/projected_image", 1);
        plane_pose_pub_ = nh_.advertise<geometry_msgs::PoseStamped>(prefix + "/projected_plane_pose", 1);
        plane_corners_pub_ = nh_.advertise<geometry_msgs::PolygonStamped>(prefix + "/plane_corners", 1);
        polygon_array_pub_ = nh_.advertise<jsk_recognition_msgs::PolygonArray>(prefix + "/polygons", 1);

        ROS_INFO("Initialized publishers for Plane ID: %d", plane_id);
    }

    void processPlaneCloud(const pcl::PointCloud<pcl::PointXYZ>::Ptr &cloud, const std_msgs::Header &header)
    {
        if (cloud->empty())
        {
            ROS_WARN("Received empty point cloud, skipping projection");
            return;
        }

        if (!createProjectionPlane(cloud))
        {
            ROS_WARN("Failed to create projection plane, skipping");
            return;
        }

        // --- 1. 创建二值图像（仅投影点）---
        cv::Mat binary_image = cv::Mat::zeros(dynamic_image_height_px_, dynamic_image_width_px_, CV_8UC1);
        for (const auto &point : cloud->points)
        {
            Eigen::Vector3d world_point(point.x, point.y, point.z);
            Eigen::Vector3d proj_point = projectPointToPlane(world_point);
            int pixel_x, pixel_y;
            if (worldToPixel(proj_point, pixel_x, pixel_y))
            {
                binary_image.at<uchar>(pixel_y, pixel_x) = 255;
            }
        }

        // --- 2. 形态学闭合（修复断裂）---
        cv::Mat closed_image;
        int k = std::max(1, morphology_kernel_size_);
        k = (k % 2 == 1) ? k : k + 1; // 必须为奇数
        cv::Mat kernel = cv::getStructuringElement(cv::MORPH_ELLIPSE, cv::Size(k, k));
        cv::morphologyEx(binary_image, closed_image, cv::MORPH_CLOSE, kernel);

        // --- 3. 提取轮廓（含层级）---
        std::vector<std::vector<cv::Point>> contours;
        std::vector<cv::Vec4i> hierarchy;
        cv::findContours(closed_image, contours, hierarchy, cv::RETR_CCOMP, cv::CHAIN_APPROX_SIMPLE);

        // --- 4. 定义微孔面积阈值（单位为像素）---
        int min_hole_area_px = 50; // 👈 可配置参数

        // --- 5. 创建最终带孔多边形图像（mask）---
        cv::Mat polygon_mask = cv::Mat::zeros(dynamic_image_height_px_, dynamic_image_width_px_, CV_8UC1);

        for (size_t i = 0; i < contours.size(); ++i)
        {
            bool is_outer = (hierarchy[i][3] == -1); // 父节点为 -1 表示外轮廓
            double area = cv::contourArea(contours[i]);

            if (is_outer)
            {
                // 填充外部轮廓
                cv::fillPoly(polygon_mask, std::vector<std::vector<cv::Point>>{contours[i]}, cv::Scalar(255));
            }
            else
            {
                // 内部孔洞
                if (area <= min_hole_area_px)
                {
                    // 如果是小孔，则填充为白色（即填补）
                    cv::fillPoly(polygon_mask, std::vector<std::vector<cv::Point>>{contours[i]}, cv::Scalar(255));
                }
                else
                {
                    // 否则保留为黑色（保持孔洞）
                    cv::fillPoly(polygon_mask, std::vector<std::vector<cv::Point>>{contours[i]}, cv::Scalar(0));
                }
            }
        }

        // --- 6. 发布最终带孔多边形图像 ---
        sensor_msgs::ImagePtr image_msg = cv_bridge::CvImage(
                                              header,
                                              sensor_msgs::image_encodings::MONO8,
                                              polygon_mask)
                                              .toImageMsg();
        image_pub_.publish(image_msg);

        // --- 7. 发布带孔多边形 ---
        // publishPolygonArray(header, contours, hierarchy);

        // --- 8. 发布平面姿态和边界框 ---
        publishPlaneInfo(header);
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
            ROS_WARN("Insufficient points for line fitting");
            return false;
        }

        Eigen::Vector2d line_direction;
        Eigen::Vector2d line_center;
        if (!fitLinePCA(xy_points, line_direction, line_center))
        {
            ROS_WARN("Failed to fit line using PCA");
            return false;
        }

        Eigen::Vector3d line_dir_3d(line_direction(0), line_direction(1), 0.0);
        line_dir_3d.normalize();

        z_axis_ = line_dir_3d.cross(Eigen::Vector3d(0, 0, 1)).normalized();
        x_axis_ = line_dir_3d;
        y_axis_ << 0, 0, 1;

        calculatePlaneSizeAndCenter(cloud, line_center);
        return true;
    }

    bool fitLinePCA(const std::vector<Eigen::Vector2d> &points,
                    Eigen::Vector2d &direction, Eigen::Vector2d &center)
    {
        if (points.empty())
            return false;

        Eigen::Vector2d sum = Eigen::Vector2d::Zero();
        for (const auto &point : points)
            sum += point;

        center = sum / points.size();

        Eigen::Matrix2d covariance = Eigen::Matrix2d::Zero();
        for (const auto &point : points)
        {
            Eigen::Vector2d diff = point - center;
            covariance += diff * diff.transpose();
        }
        covariance /= points.size();

        Eigen::SelfAdjointEigenSolver<Eigen::Matrix2d> eigen_solver(covariance);
        if (eigen_solver.info() != Eigen::Success)
            return false;

        direction = eigen_solver.eigenvectors().col(1);
        direction.normalize();
        return true;
    }

    void calculatePlaneSizeAndCenter(const pcl::PointCloud<pcl::PointXYZ>::Ptr &cloud,
                                     const Eigen::Vector2d &line_center_2d)
    {
        double min_x = std::numeric_limits<double>::max();
        double max_x = std::numeric_limits<double>::lowest();
        double min_z = std::numeric_limits<double>::max();
        double max_z = std::numeric_limits<double>::lowest();

        for (const auto &point : cloud->points)
        {
            Eigen::Vector3d world_point(point.x, point.y, point.z);
            Eigen::Vector3d rel_vec = world_point - Eigen::Vector3d(line_center_2d(0), line_center_2d(1), 0.0);

            double proj_x = rel_vec.dot(x_axis_);
            double proj_z = world_point.z();

            min_x = std::min(min_x, proj_x);
            max_x = std::max(max_x, proj_x);
            min_z = std::min(min_z, proj_z);
            max_z = std::max(max_z, proj_z);
        }

        double original_plane_width = (max_x - min_x) + 2 * 0.3;
        double original_extrusion_length = (max_z - min_z) + 2 * 0.2;

        double center_x_proj_original = (max_x + min_x) / 2.0;
        double center_z_original = (max_z + min_z) / 2.0;
        Eigen::Vector3d center_offset_original = center_x_proj_original * x_axis_ + center_z_original * y_axis_;
        Eigen::Vector3d original_plane_center_world = Eigen::Vector3d(line_center_2d(0), line_center_2d(1), 0.0) + center_offset_original;

        double final_resolution_x, final_resolution_y;
        double final_plane_width, final_extrusion_length;
        int final_image_width_px, final_image_height_px;

        if (use_fixed_resolution_ && fixed_resolution_m_per_px_ > 0)
        {
            final_resolution_x = final_resolution_y = fixed_resolution_m_per_px_;
            final_plane_width = original_plane_width;
            final_extrusion_length = original_extrusion_length;
            final_image_width_px = static_cast<int>(std::ceil(final_plane_width / final_resolution_x));
            final_image_height_px = static_cast<int>(std::ceil(final_extrusion_length / final_resolution_y));
        }
        else
        {
            final_plane_width = original_plane_width;
            final_extrusion_length = original_extrusion_length;
            final_resolution_x = final_plane_width / config_image_width_;
            final_resolution_y = final_extrusion_length / config_image_height_;
            final_image_width_px = config_image_width_;
            final_image_height_px = config_image_height_;
        }

        plane_center_ = original_plane_center_world;
        plane_width_ = final_plane_width;
        extrusion_length_ = final_extrusion_length;
        resolution_x_ = final_resolution_x;
        resolution_y_ = final_resolution_y;
        dynamic_image_width_px_ = final_image_width_px;
        dynamic_image_height_px_ = final_image_height_px;
    }

    Eigen::Vector3d projectPointToPlane(const Eigen::Vector3d &point)
    {
        Eigen::Vector3d rel_vec = point - plane_center_;
        double distance = rel_vec.dot(z_axis_);
        return point - distance * z_axis_;
    }

    bool worldToPixel(const Eigen::Vector3d &world_point, int &pixel_x, int &pixel_y)
    {
        Eigen::Vector3d rel_vec = world_point - plane_center_;
        double proj_x = rel_vec.dot(x_axis_);
        double proj_y = rel_vec.dot(y_axis_);

        if (std::abs(proj_x) > plane_width_ / 2.0 || std::abs(proj_y) > extrusion_length_ / 2.0)
        {
            return false;
        }

        pixel_x = static_cast<int>((proj_x + plane_width_ / 2.0) / resolution_x_);
        pixel_y = static_cast<int>((extrusion_length_ / 2.0 - proj_y) / resolution_y_);

        if (pixel_x >= 0 && pixel_x < dynamic_image_width_px_ &&
            pixel_y >= 0 && pixel_y < dynamic_image_height_px_)
        {
            return true;
        }
        return false;
    }

    void publishPlaneInfo(const std_msgs::Header &header)
    {
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

        // ✅ 手动赋值（避免 tf2::toMsg 问题）
        plane_pose.pose.orientation.x = quaternion.x();
        plane_pose.pose.orientation.y = quaternion.y();
        plane_pose.pose.orientation.z = quaternion.z();
        plane_pose.pose.orientation.w = quaternion.w();

        plane_pose_pub_.publish(plane_pose);
        publishPlaneCorners(header);
    }

    void publishPlaneCorners(const std_msgs::Header &header)
    {
        double half_width = plane_width_ / 2.0;
        double half_height = extrusion_length_ / 2.0;

        Eigen::Vector3d corner_local_bl(-half_width, -half_height, 0);
        Eigen::Vector3d corner_local_tl(-half_width, half_height, 0);
        Eigen::Vector3d corner_local_tr(half_width, half_height, 0);
        Eigen::Vector3d corner_local_br(half_width, -half_height, 0);

        auto to_point = [](const Eigen::Vector3d &v)
        {
            geometry_msgs::Point32 pt;
            pt.x = v(0);
            pt.y = v(1);
            pt.z = v(2);
            return pt;
        };

        geometry_msgs::PolygonStamped corners_msg;
        corners_msg.header = header;
        corners_msg.polygon.points.resize(4);
        corners_msg.polygon.points[0] = to_point(plane_center_ + corner_local_bl(0) * x_axis_ + corner_local_bl(1) * y_axis_);
        corners_msg.polygon.points[1] = to_point(plane_center_ + corner_local_tl(0) * x_axis_ + corner_local_tl(1) * y_axis_);
        corners_msg.polygon.points[2] = to_point(plane_center_ + corner_local_tr(0) * x_axis_ + corner_local_tr(1) * y_axis_);
        corners_msg.polygon.points[3] = to_point(plane_center_ + corner_local_br(0) * x_axis_ + corner_local_br(1) * y_axis_);

        plane_corners_pub_.publish(corners_msg);
    }

    std::vector<geometry_msgs::Point32> pixelContourToWorld(const std::vector<cv::Point> &contour, bool is_outer)
    {
        std::vector<geometry_msgs::Point32> points;
        for (const auto &pt : contour)
        {
            double world_x = (pt.x * resolution_x_ - plane_width_ / 2.0);
            double world_y = (extrusion_length_ / 2.0 - pt.y * resolution_y_);
            Eigen::Vector3d world_point = plane_center_ + world_x * x_axis_ + world_y * y_axis_;

            geometry_msgs::Point32 point;
            point.x = world_point(0);
            point.y = world_point(1);
            point.z = world_point(2);
            points.push_back(point);
        }

        if (!is_outer && !points.empty())
            std::reverse(points.begin(), points.end());

        return points;
    }

    // void publishPolygonArray(const std_msgs::Header &header,
    //                          const std::vector<std::vector<cv::Point>> &contours,
    //                          const std::vector<cv::Vec4i> &hierarchy)
    // {
    //     jsk_recognition_msgs::PolygonArray array_msg;
    //     array_msg.header = header;

    //     for (size_t i = 0; i < contours.size(); ++i)
    //     {
    //         if (hierarchy[i][3] != -1)
    //             continue; // 只处理外轮廓

    //         // ✅ 使用 PolygonWithHolesStamped
    //         jsk_recognition_msgs::PolygonWithHolesStamped poly_stamped;
    //         poly_stamped.header = header;

    //         // 外轮廓
    //         poly_stamped.polygon.polygon.points = pixelContourToWorld(contours[i], true);

    //         // 添加 holes
    //         for (size_t j = 0; j < contours.size(); ++j)
    //         {
    //             if (static_cast<int>(i) == hierarchy[j][3])
    //             {
    //                 geometry_msgs::Polygon hole;
    //                 hole.points = pixelContourToWorld(contours[j], false);
    //                 poly_stamped.holes.push_back(hole);
    //             }
    //         }

    //         // ✅ 添加到数组
    //         array_msg.polygons.push_back(poly_stamped);
    //         array_msg.labels.push_back(0);
    //         array_msg.likelihood.push_back(1.0);
    //     }

    //     polygon_array_pub_.publish(array_msg);
    // }
};

// --- MultiTopicPlaneProjector ---
class MultiTopicPlaneProjector
{
private:
    ros::NodeHandle nh_;
    ros::NodeHandle nh_private_;
    std::vector<ros::Subscriber> input_subs_;
    std::string config_file_;
    std::string target_frame_;
    int image_width_, image_height_;
    double fixed_resolution_m_per_px_;
    bool use_fixed_resolution_;
    int morphology_kernel_size_;
    int min_hole_area_px_;

    // *** 新增：仿照spatial的自动话题生成方式 ***
    std::string input_topic_base_;
    int max_input_topics_;

    std::vector<PointCloudProjector> projectors_;
    tf2_ros::Buffer tf_buffer_;
    tf2_ros::TransformListener tf_listener_;

public:
    MultiTopicPlaneProjector()
        : nh_private_("~"), tf_buffer_(), tf_listener_(tf_buffer_)
    {
        nh_private_.param<std::string>("config_file", config_file_, "projector_config.yaml");
        loadConfig();

        nh_private_.param<std::string>("target_frame", target_frame_, target_frame_);
        if (target_frame_.empty())
        {
            ROS_ERROR("target_frame is empty! Please check your config file or parameters.");
            ros::shutdown();
            return;
        }

        nh_private_.param<int>("image_width", image_width_, image_width_);
        nh_private_.param<int>("image_height", image_height_, image_height_);
        nh_private_.param<double>("fixed_resolution_m_per_px", fixed_resolution_m_per_px_, 0.01);
        nh_private_.param<bool>("use_fixed_resolution", use_fixed_resolution_, false);
        nh_private_.param<int>("morphology_kernel_size", morphology_kernel_size_, 5);
        nh_private_.param<int>("min_hole_area_px", min_hole_area_px_, 30);

        // *** 新增：读取自动话题生成参数 ***
        nh_private_.param<std::string>("input_topic_base", input_topic_base_, "/fast_detector/refined_plane_");
        nh_private_.param<int>("max_input_topics", max_input_topics_, 4);

        ROS_INFO("Point Projector initialized with:");
        ROS_INFO("  - Target frame: %s", target_frame_.c_str());
        ROS_INFO("  - Input topic base: %s", input_topic_base_.c_str());
        ROS_INFO("  - Max input topics: %d", max_input_topics_);
        ROS_INFO("  - Image size: %dx%d", image_width_, image_height_);
        ROS_INFO("  - Fixed resolution: %s (%.3f m/px)",
                 use_fixed_resolution_ ? "Yes" : "No", fixed_resolution_m_per_px_);

        setupSubscribers();
    }

private:
    void loadConfig()
    {
        try
        {
            YAML::Node config = YAML::LoadFile(config_file_);

            // 读取基本参数（保持原有逻辑）
            if (config["target_frame"])
                target_frame_ = config["target_frame"].as<std::string>();
            else
                target_frame_ = "camera_init";

            if (config["image_width"])
                image_width_ = config["image_width"].as<int>();
            else
                image_width_ = 800;

            if (config["image_height"])
                image_height_ = config["image_height"].as<int>();
            else
                image_height_ = 600;

            if (config["fixed_resolution_m_per_px"])
                fixed_resolution_m_per_px_ = config["fixed_resolution_m_per_px"].as<double>();
            else
                fixed_resolution_m_per_px_ = 0.01;

            if (config["use_fixed_resolution"])
                use_fixed_resolution_ = config["use_fixed_resolution"].as<bool>();
            else
                use_fixed_resolution_ = false;

            if (config["morphology_kernel_size"])
                morphology_kernel_size_ = config["morphology_kernel_size"].as<int>();
            else
                morphology_kernel_size_ = 5;

            if (config["min_hole_area_px"])
                min_hole_area_px_ = config["min_hole_area_px"].as<int>();
            else
                min_hole_area_px_ = 50;

            // *** 新增：读取自动话题生成参数 ***
            if (config["input_topic_base"])
                input_topic_base_ = config["input_topic_base"].as<std::string>();
            else
                input_topic_base_ = "/fast_detector/refined_plane_";

            if (config["max_input_topics"])
                max_input_topics_ = config["max_input_topics"].as<int>();
            else
                max_input_topics_ = 4;

            ROS_INFO("Config loaded successfully from: %s", config_file_.c_str());
        }
        catch (const YAML::Exception &e)
        {
            ROS_WARN("Failed to load config file %s: %s. Using default parameters.",
                     config_file_.c_str(), e.what());

            // 设置默认值
            target_frame_ = "camera_init";
            image_width_ = 800;
            image_height_ = 600;
            fixed_resolution_m_per_px_ = 0.01;
            use_fixed_resolution_ = false;
            morphology_kernel_size_ = 5;
            input_topic_base_ = "/fast_detector/refined_plane_";
            max_input_topics_ = 4;
        }
    }

    void setupSubscribers()
    {
        // *** 新增：自动生成话题订阅（仿照spatial方式）***
        for (int i = 1; i <= max_input_topics_; ++i)
        {
            std::string topic_name = input_topic_base_ + std::to_string(i);

            // 创建对应的投影器
            projectors_.emplace_back(nh_, nh_private_, target_frame_,
                                     image_width_, image_height_,
                                     fixed_resolution_m_per_px_, use_fixed_resolution_,
                                     morphology_kernel_size_,
                                     min_hole_area_px_);
            projectors_.back().initializePublishers(i);

            // 创建订阅器
            ros::Subscriber sub = nh_.subscribe<sensor_msgs::PointCloud2>(
                topic_name, 1,
                boost::bind(&MultiTopicPlaneProjector::planeCloudCallback, this, _1, i - 1));
            input_subs_.push_back(sub);

            ROS_INFO("Subscribed to: %s -> projector %d", topic_name.c_str(), i);
        }

        ROS_INFO("Total %d projectors initialized and subscribed", max_input_topics_);
    }

    void planeCloudCallback(const sensor_msgs::PointCloud2ConstPtr &msg, int idx)
    {
        if (idx >= static_cast<int>(projectors_.size()))
        {
            ROS_ERROR("Invalid projector index: %d (max: %zu)", idx, projectors_.size());
            return;
        }

        try
        {
            sensor_msgs::PointCloud2 transformed_cloud;
            if (msg->header.frame_id != target_frame_)
            {
                geometry_msgs::TransformStamped transform_stamped = tf_buffer_.lookupTransform(
                    target_frame_, msg->header.frame_id, msg->header.stamp, ros::Duration(0.1));
                tf2::doTransform(*msg, transformed_cloud, transform_stamped);
            }
            else
            {
                transformed_cloud = *msg;
            }

            pcl::PointCloud<pcl::PointXYZ>::Ptr pcl_cloud(new pcl::PointCloud<pcl::PointXYZ>);
            pcl::fromROSMsg(transformed_cloud, *pcl_cloud);

            if (!pcl_cloud->empty())
            {
                projectors_[idx].processPlaneCloud(pcl_cloud, transformed_cloud.header);
            }
        }
        catch (const tf2::TransformException &ex)
        {
            ROS_WARN_THROTTLE(1.0, "Transform lookup failed for projector %d: %s", idx + 1, ex.what());
        }
        catch (const std::exception &e)
        {
            ROS_ERROR("Error processing cloud for projector %d: %s", idx + 1, e.what());
        }
    }
};

int main(int argc, char **argv)
{
    ros::init(argc, argv, "point_projector");
    MultiTopicPlaneProjector node;
    ros::spin();
    return 0;
}