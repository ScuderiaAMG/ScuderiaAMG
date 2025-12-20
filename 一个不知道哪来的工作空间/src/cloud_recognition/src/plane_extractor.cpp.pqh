#include <ros/ros.h>
#include <sensor_msgs/PointCloud2.h>
#include <pcl_conversions/pcl_conversions.h>
#include <pcl/point_cloud.h>
#include <pcl/point_types.h>
#include <pcl/filters/extract_indices.h>
#include <pcl/segmentation/sac_segmentation.h>
#include <pcl/filters/voxel_grid.h>
#include <pcl/filters/passthrough.h>
#include <pcl/segmentation/extract_clusters.h>
#include <pcl/common/centroid.h>
#include <pcl/common/eigen.h>
#include <cmath>
#include <vector>
#include <Eigen/Dense>

class PlaneExtractor
{
public:
    PlaneExtractor()
    {
        loadParameters();

        sub_ = nh_.subscribe(input_topic_, 1, &PlaneExtractor::cloudCallback, this);

        // 动态创建发布者：支持最多 total_max_fragments_ 个平面片段（主平面 + 分裂后的子簇）
        for (int i = 0; i < total_max_fragments_; ++i)
        {
            std::string topic_name = "/plane_extractor/plane_clouds_" + std::to_string(i + 1);
            pub_planes_.push_back(nh_.advertise<sensor_msgs::PointCloud2>(topic_name, 1));
        }

        // 发布有效聚类的可视化点云
        pub_valid_clusters_ = nh_.advertise<sensor_msgs::PointCloud2>("/plane_extractor/valid_clusters_colored", 1);

        ROS_INFO_STREAM("PlaneExtractor node started.");
        ROS_INFO_STREAM("Input topic: " << input_topic_);
        ROS_INFO_STREAM("Max main planes to extract: " << max_planes_);
        ROS_INFO_STREAM("Max total plane fragments (topics): " << total_max_fragments_);
        ROS_INFO_STREAM("Vertical tolerance (rad): " << vertical_tolerance_);
        ROS_INFO_STREAM("ROI: x[" << roi_x_min_ << ", " << roi_x_max_ << "] "
                                  << "y[" << roi_y_min_ << ", " << roi_y_max_ << "] "
                                  << "z[" << roi_z_min_ << ", " << roi_z_max_ << "]");
        ROS_INFO_STREAM("Clustering tolerance: " << cluster_tolerance_ << " m");
        ROS_INFO_STREAM("Min cluster size: " << min_cluster_size_);
        ROS_INFO_STREAM("Max cluster size: " << max_cluster_size_);
        ROS_INFO_STREAM("Merge distance threshold: " << merge_distance_threshold_ << " m");
        ROS_INFO_STREAM("Merge angle threshold: " << merge_angle_threshold_ << " rad");
        ROS_INFO_STREAM("Max height threshold: " << max_height_threshold_ << " m");
        ROS_INFO_STREAM("Enable cluster coloring: " << enable_cluster_coloring_);
    }

private:
    void loadParameters()
    {
        nh_.param<double>("roi/x_min", roi_x_min_, 0.5);
        nh_.param<double>("roi/x_max", roi_x_max_, 2.0);
        nh_.param<double>("roi/y_min", roi_y_min_, -1.0);
        nh_.param<double>("roi/y_max", roi_y_max_, 1.0);
        nh_.param<double>("roi/z_min", roi_z_min_, 0.0);
        nh_.param<double>("roi/z_max", roi_z_max_, 1.5);

        nh_.param<int>("segmentation/max_iterations", max_iterations_, 200);
        nh_.param<double>("segmentation/distance_threshold", distance_threshold_, 0.02);
        nh_.param<bool>("segmentation/optimize_coefficients", optimize_coefficients_, true);

        nh_.param<double>("preprocessing/voxel_leaf_size", voxel_leaf_size_, 0.01);
        nh_.param<std::string>("preprocessing/input_topic", input_topic_, "/cloud_registered");

        nh_.param<int>("plane_extraction/max_planes", max_planes_, 4);                      // 增加默认值
        nh_.param<double>("plane_extraction/vertical_tolerance", vertical_tolerance_, 0.1); // 弧度
        nh_.param<int>("plane_extraction/total_max_fragments", total_max_fragments_, 20);   // 最大片段数（用于话题编号）

        // 聚类参数
        nh_.param<double>("clustering/tolerance", cluster_tolerance_, 0.05);
        nh_.param<int>("clustering/min_cluster_size", min_cluster_size_, 50);
        nh_.param<int>("clustering/max_cluster_size", max_cluster_size_, 99999999);

        // 合并参数
        nh_.param<double>("merge/distance_threshold", merge_distance_threshold_, 0.1); // 质心距离阈值
        nh_.param<double>("merge/angle_threshold", merge_angle_threshold_, 0.1);       // 平面角度阈值（弧度）

        // 高度限制参数
        nh_.param<double>("height_filter/max_height", max_height_threshold_, 1.5); // 最大高度阈值
        nh_.param<bool>("height_filter/enable", enable_height_filter_, true);      // 是否启用高度过滤

        // 聚类可视化参数
        nh_.param<bool>("visualization/enable_cluster_coloring", enable_cluster_coloring_, true);
    }

    // 生成随机颜色
    uint32_t getColor(int index)
    {
        // 使用预定义的颜色方案，避免过于相似的颜色
        std::vector<std::vector<uint8_t>> colors = {
            {255, 0, 0},     // Red
            {0, 255, 0},     // Green
            {0, 0, 255},     // Blue
            {255, 255, 0},   // Yellow
            {255, 0, 255},   // Magenta
            {0, 255, 255},   // Cyan
            {255, 165, 0},   // Orange
            {128, 0, 128},   // Purple
            {255, 192, 203}, // Pink
            {165, 42, 42},   // Brown
            {128, 128, 0},   // Olive
            {0, 128, 128},   // Teal
            {128, 0, 0},     // Maroon
            {0, 128, 0},     // Dark Green
            {0, 0, 128},     // Navy
            {255, 215, 0},   // Gold
            {75, 0, 130},    // Indigo
            {240, 230, 140}, // Khaki
            {255, 69, 0},    // Red-Orange
            {50, 205, 50}    // Lime Green
        };

        if (index < colors.size())
        {
            uint8_t r = colors[index][0];
            uint8_t g = colors[index][1];
            uint8_t b = colors[index][2];
            return (static_cast<uint32_t>(r) << 16) | (static_cast<uint32_t>(g) << 8) | static_cast<uint32_t>(b);
        }
        else
        {
            // 如果索引超出预定义颜色数量，生成随机颜色
            srand(index);
            uint8_t r = rand() % 256;
            uint8_t g = rand() % 256;
            uint8_t b = rand() % 256;
            return (static_cast<uint32_t>(r) << 16) | (static_cast<uint32_t>(g) << 8) | static_cast<uint32_t>(b);
        }
    }

    bool isVerticalPlane(const pcl::ModelCoefficients::Ptr coeffs, double tolerance)
    {
        double a = coeffs->values[0];
        double b = coeffs->values[1];
        double c = coeffs->values[2];

        double norm = std::sqrt(a * a + b * b + c * c);
        if (norm < 1e-6)
            return false;
        double cos_theta = std::abs(c) / norm;
        double angle = std::acos(cos_theta);

        double target_angle = M_PI / 2.0;
        return std::abs(angle - target_angle) <= tolerance;
    }

    // 检查聚类是否包含超过最大高度的点
    bool hasPointsAboveThreshold(const pcl::PointCloud<pcl::PointXYZ>::Ptr &cluster_cloud, double max_height)
    {
        for (const auto &point : cluster_cloud->points)
        {
            if (point.z > max_height)
            {
                return true;
            }
        }
        return false;
    }

    // 计算两个平面法向量之间的角度
    double calculatePlaneAngle(const pcl::ModelCoefficients::Ptr &coeffs1,
                               const pcl::ModelCoefficients::Ptr &coeffs2)
    {
        Eigen::Vector3f normal1(coeffs1->values[0], coeffs1->values[1], coeffs1->values[2]);
        Eigen::Vector3f normal2(coeffs2->values[0], coeffs2->values[1], coeffs2->values[2]);

        normal1.normalize();
        normal2.normalize();

        double dot_product = normal1.dot(normal2);
        // 确保dot_product在[-1, 1]范围内以避免数值误差
        dot_product = std::max(-1.0, std::min(1.0, dot_product));

        return std::acos(std::abs(dot_product)); // 使用绝对值，考虑平行平面
    }

    // 合并平面点云
    std::vector<pcl::PointCloud<pcl::PointXYZ>::Ptr> mergePlanes(
        const std::vector<pcl::PointCloud<pcl::PointXYZ>::Ptr> &plane_clouds,
        const std::vector<pcl::ModelCoefficients::Ptr> &plane_coeffs)
    {
        std::vector<bool> processed(plane_clouds.size(), false);
        std::vector<pcl::PointCloud<pcl::PointXYZ>::Ptr> merged_planes;

        for (size_t i = 0; i < plane_clouds.size(); ++i)
        {
            if (processed[i])
                continue;

            pcl::PointCloud<pcl::PointXYZ>::Ptr merged_cloud(new pcl::PointCloud<pcl::PointXYZ>);
            *merged_cloud = *plane_clouds[i];

            // 计算当前平面的质心
            Eigen::Vector4f centroid1;
            pcl::compute3DCentroid(*plane_clouds[i], centroid1);

            std::vector<int> to_merge;
            to_merge.push_back(i);

            // 寻找可以合并的其他平面
            for (size_t j = i + 1; j < plane_clouds.size(); ++j)
            {
                if (processed[j])
                    continue;

                // 计算质心距离
                Eigen::Vector4f centroid2;
                pcl::compute3DCentroid(*plane_clouds[j], centroid2);

                double distance = std::sqrt(
                    std::pow(centroid1[0] - centroid2[0], 2) +
                    std::pow(centroid1[1] - centroid2[1], 2) +
                    std::pow(centroid1[2] - centroid2[2], 2));

                // 计算平面角度
                double angle = calculatePlaneAngle(plane_coeffs[i], plane_coeffs[j]);

                // 检查是否满足合并条件
                if (distance <= merge_distance_threshold_ && angle <= merge_angle_threshold_)
                {
                    to_merge.push_back(j);
                }
            }

            // 合并找到的平面
            for (size_t k = 1; k < to_merge.size(); ++k)
            {
                size_t idx = to_merge[k];
                *merged_cloud += *plane_clouds[idx];
                processed[idx] = true;
            }

            processed[i] = true;
            merged_planes.push_back(merged_cloud);
        }

        return merged_planes;
    }

    void cloudCallback(const sensor_msgs::PointCloud2ConstPtr &input_msg)
    {
        pcl::PointCloud<pcl::PointXYZ>::Ptr cloud(new pcl::PointCloud<pcl::PointXYZ>);
        pcl::fromROSMsg(*input_msg, *cloud);

        pcl::PointCloud<pcl::PointXYZ>::Ptr filtered_cloud(new pcl::PointCloud<pcl::PointXYZ>);
        pcl::PointCloud<pcl::PointXYZ>::Ptr region_cloud(new pcl::PointCloud<pcl::PointXYZ>);

        // 降采样
        pcl::VoxelGrid<pcl::PointXYZ> voxel;
        voxel.setInputCloud(cloud);
        voxel.setLeafSize(voxel_leaf_size_, voxel_leaf_size_, voxel_leaf_size_);
        voxel.filter(*filtered_cloud);

        // ROI 过滤
        pcl::PassThrough<pcl::PointXYZ> pass;
        pass.setInputCloud(filtered_cloud);
        pass.setFilterFieldName("x");
        pass.setFilterLimits(roi_x_min_, roi_x_max_);
        pass.filter(*region_cloud);

        pass.setInputCloud(region_cloud);
        pass.setFilterFieldName("y");
        pass.setFilterLimits(roi_y_min_, roi_y_max_);
        pass.filter(*region_cloud);

        pass.setInputCloud(region_cloud);
        pass.setFilterFieldName("z");
        pass.setFilterLimits(roi_z_min_, roi_z_max_);
        pass.filter(*region_cloud);

        if (region_cloud->points.size() < 100)
        {
            ROS_WARN("Not enough points in ROI for plane segmentation.");
            return;
        }

        // === 第一步：对整个点云进行聚类 ===
        std::vector<pcl::PointIndices> cluster_indices;
        pcl::search::KdTree<pcl::PointXYZ>::Ptr tree(new pcl::search::KdTree<pcl::PointXYZ>);
        tree->setInputCloud(region_cloud);

        pcl::EuclideanClusterExtraction<pcl::PointXYZ> ec;
        ec.setClusterTolerance(cluster_tolerance_);
        ec.setMinClusterSize(min_cluster_size_);
        ec.setMaxClusterSize(max_cluster_size_);
        ec.setSearchMethod(tree);
        ec.setInputCloud(region_cloud);
        ec.extract(cluster_indices);

        ROS_INFO_STREAM("Detected " << cluster_indices.size() << " clusters before height filtering.");

        // === 第二步：高度过滤聚类 ===
        std::vector<pcl::PointIndices> filtered_cluster_indices;

        if (enable_height_filter_)
        {
            for (const auto &cluster : cluster_indices)
            {
                // 创建当前聚类的点云
                pcl::PointCloud<pcl::PointXYZ>::Ptr cluster_cloud(new pcl::PointCloud<pcl::PointXYZ>);
                for (int idx : cluster.indices)
                {
                    cluster_cloud->points.push_back(region_cloud->points[idx]);
                }
                cluster_cloud->width = cluster_cloud->points.size();
                cluster_cloud->height = 1;
                cluster_cloud->is_dense = false;

                // 检查聚类中是否有超过最大高度的点
                if (!hasPointsAboveThreshold(cluster_cloud, max_height_threshold_))
                {
                    filtered_cluster_indices.push_back(cluster);
                }
                else
                {
                    ROS_DEBUG("Filtered out cluster with points above height threshold (%.2f m)", max_height_threshold_);
                }
            }

            ROS_INFO_STREAM("After height filtering: " << filtered_cluster_indices.size() << " clusters remaining.");
        }
        else
        {
            filtered_cluster_indices = cluster_indices;
            ROS_INFO_STREAM("Height filtering disabled, using all " << filtered_cluster_indices.size() << " clusters.");
        }

        // === 第三步：发布有效的聚类（彩色可视化） ===
        if (enable_cluster_coloring_)
        {
            pcl::PointCloud<pcl::PointXYZRGB>::Ptr colored_cloud(new pcl::PointCloud<pcl::PointXYZRGB>);

            for (size_t i = 0; i < filtered_cluster_indices.size(); ++i)
            {
                uint32_t color = getColor(i);

                for (int idx : filtered_cluster_indices[i].indices)
                {
                    pcl::PointXYZRGB colored_point;
                    pcl::PointXYZ original_point = region_cloud->points[idx];

                    colored_point.x = original_point.x;
                    colored_point.y = original_point.y;
                    colored_point.z = original_point.z;

                    // 设置RGB值
                    uint8_t r = (color >> 16) & 0xFF;
                    uint8_t g = (color >> 8) & 0xFF;
                    uint8_t b = color & 0xFF;

                    colored_point.r = r;
                    colored_point.g = g;
                    colored_point.b = b;

                    colored_cloud->points.push_back(colored_point);
                }
            }

            colored_cloud->width = colored_cloud->points.size();
            colored_cloud->height = 1;
            colored_cloud->is_dense = false;

            // 发布彩色点云
            sensor_msgs::PointCloud2 colored_msg;
            pcl::toROSMsg(*colored_cloud, colored_msg);
            colored_msg.header = input_msg->header;
            pub_valid_clusters_.publish(colored_msg);

            ROS_INFO_STREAM("Published colored visualization of " << filtered_cluster_indices.size() << " valid clusters.");
        }

        // 存储提取的平面点云和对应的系数
        std::vector<pcl::PointCloud<pcl::PointXYZ>::Ptr> extracted_planes;
        std::vector<pcl::ModelCoefficients::Ptr> plane_coefficients;

        // === 第四步：对每个聚类分别进行平面提取 ===
        for (const auto &cluster : filtered_cluster_indices)
        {
            pcl::PointCloud<pcl::PointXYZ>::Ptr cluster_cloud(new pcl::PointCloud<pcl::PointXYZ>);
            for (int idx : cluster.indices)
            {
                cluster_cloud->points.push_back(region_cloud->points[idx]);
            }
            cluster_cloud->width = cluster_cloud->points.size();
            cluster_cloud->height = 1;
            cluster_cloud->is_dense = false;

            // 平面拟合
            pcl::ModelCoefficients::Ptr coefficients(new pcl::ModelCoefficients);
            pcl::PointIndices::Ptr inliers(new pcl::PointIndices);

            pcl::SACSegmentation<pcl::PointXYZ> seg;
            seg.setOptimizeCoefficients(optimize_coefficients_);
            seg.setModelType(pcl::SACMODEL_PLANE);
            seg.setMethodType(pcl::SAC_RANSAC);
            seg.setMaxIterations(max_iterations_);
            seg.setDistanceThreshold(distance_threshold_);
            seg.setInputCloud(cluster_cloud);
            seg.segment(*inliers, *coefficients);

            if (inliers->indices.empty())
            {
                ROS_DEBUG("RANSAC failed to find a plane in cluster.");
                continue;
            }

            // 判断是否为垂直平面
            if (!isVerticalPlane(coefficients, vertical_tolerance_))
            {
                ROS_DEBUG("Plane in cluster is not vertical.");
                continue;
            }

            // 提取平面点
            pcl::PointCloud<pcl::PointXYZ>::Ptr plane_cloud(new pcl::PointCloud<pcl::PointXYZ>);
            pcl::ExtractIndices<pcl::PointXYZ> extract;
            extract.setInputCloud(cluster_cloud);
            extract.setIndices(inliers);
            extract.filter(*plane_cloud);

            if (plane_cloud->points.size() >= min_cluster_size_) // 确保平面点云大小合理
            {
                extracted_planes.push_back(plane_cloud);
                plane_coefficients.push_back(coefficients);
            }
        }

        ROS_INFO_STREAM("Extracted " << extracted_planes.size() << " vertical planes before merging.");

        // === 第五步：合并相似的平面 ===
        std::vector<pcl::PointCloud<pcl::PointXYZ>::Ptr> final_planes;
        if (!extracted_planes.empty())
        {
            final_planes = mergePlanes(extracted_planes, plane_coefficients);
            ROS_INFO_STREAM("Merged planes to " << final_planes.size() << " final planes.");
        }

        // === 第六步：发布合并后的平面 ===
        next_pub_index_ = 0;
        for (size_t i = 0; i < final_planes.size(); ++i)
        {
            if (next_pub_index_ >= total_max_fragments_)
            {
                ROS_WARN("Maximum fragment count reached.");
                break;
            }

            // 发布
            sensor_msgs::PointCloud2 output_msg;
            pcl::toROSMsg(*final_planes[i], output_msg);
            output_msg.header = input_msg->header;
            pub_planes_[next_pub_index_].publish(output_msg);

            ROS_INFO_STREAM("Published merged vertical plane with " << final_planes[i]->points.size()
                                                                    << " points to /plane_extractor/plane_clouds_"
                                                                    << (next_pub_index_ + 1));

            next_pub_index_++;
        }

        ROS_INFO_STREAM("Total vertical planes published after merging: " << next_pub_index_);
    }

    ros::NodeHandle nh_;
    ros::Subscriber sub_;
    std::vector<ros::Publisher> pub_planes_;
    ros::Publisher pub_valid_clusters_; // 新增：发布彩色聚类点云

    // 参数变量
    double roi_x_min_, roi_x_max_;
    double roi_y_min_, roi_y_max_;
    double roi_z_min_, roi_z_max_;

    int max_iterations_;
    double distance_threshold_;
    bool optimize_coefficients_;

    double voxel_leaf_size_;
    std::string input_topic_;

    int max_planes_;
    double vertical_tolerance_;
    int total_max_fragments_; // 最大支持的平面片段数（用于话题编号）

    // 聚类参数
    double cluster_tolerance_;
    int min_cluster_size_;
    int max_cluster_size_;

    // 合并参数
    double merge_distance_threshold_;
    double merge_angle_threshold_;

    // 高度限制参数
    double max_height_threshold_;
    bool enable_height_filter_;

    // 聚类可视化参数
    bool enable_cluster_coloring_;

    // 全局发布索引
    int next_pub_index_;
};

int main(int argc, char **argv)
{
    ros::init(argc, argv, "plane_extractor");
    PlaneExtractor pe;
    ros::spin();
    return 0;
}