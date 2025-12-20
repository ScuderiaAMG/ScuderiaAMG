#include <ros/ros.h>
#include <sensor_msgs/PointCloud2.h>
#include <pcl_conversions/pcl_conversions.h>
#include <pcl/point_cloud.h>
#include <pcl/point_types.h>
#include <pcl/filters/voxel_grid.h>
#include <pcl/filters/passthrough.h>
#include <pcl/segmentation/extract_clusters.h>
#include <pcl/features/normal_3d.h>
#include <visualization_msgs/Marker.h>
#include <visualization_msgs/MarkerArray.h>
#include <geometry_msgs/Point.h>

#include <vector>
#include <cmath>
#include <algorithm>
#include <limits>

struct FlagObject
{
    double x, y;
    double min_z, max_z;
    double height; // 从Z=0到刀旗顶部的高度
    double width;
    // 移除points成员，避免内存分配器问题
};

class FlagDetector
{
private:
    ros::NodeHandle nh_;
    ros::NodeHandle private_nh_;
    ros::Subscriber cloud_sub_;
    ros::Publisher flag_pub_;
    ros::Publisher marker_pub_;
    ros::Publisher downsampled_cloud_pub_;
    ros::Publisher clustered_cloud_pub_;
    ros::Publisher roi_marker_pub_; // 新增：ROI可视化发布器
    ros::Timer roi_timer_;          // 新增：定期发布ROI边框

    // 参数
    double roi_min_x_, roi_max_x_;
    double roi_min_y_, roi_max_y_;
    double roi_min_z_, roi_max_z_;
    double voxel_leaf_size_;
    double cluster_tolerance_;
    int min_cluster_size_;
    int max_cluster_size_;
    double flag_width_min_;
    double flag_width_max_;
    double min_flag_height_;
    double max_flag_height_;
    double surrounding_radius_;
    int surrounding_threshold_;

    // 话题名称参数
    std::string input_topic_;
    std::string output_flag_topic_;
    std::string output_marker_topic_;
    std::string output_downsampled_topic_;
    std::string output_clustered_topic_;
    std::string output_roi_marker_topic_; // 新增：ROI标记话题
    std::string frame_id_;                // 新增：坐标系参数

public:
    FlagDetector() : nh_(), private_nh_("~")
    {
        // 使用私有节点句柄读取参数
        private_nh_.param<std::string>("input_topic", input_topic_, "/velodyne_points");
        private_nh_.param<std::string>("output_flag_topic", output_flag_topic_, "/flag_coordinates");
        private_nh_.param<std::string>("output_marker_topic", output_marker_topic_, "/flag_markers");
        private_nh_.param<std::string>("output_downsampled_topic", output_downsampled_topic_, "/downsampled_cloud");
        private_nh_.param<std::string>("output_clustered_topic", output_clustered_topic_, "/clustered_cloud");
        private_nh_.param<std::string>("output_roi_marker_topic", output_roi_marker_topic_, "/roi_boundary"); // 新增
        private_nh_.param<std::string>("frame_id", frame_id_, "world");                                    // 新增：坐标系参数

        // 订阅点云话题
        cloud_sub_ = nh_.subscribe(input_topic_, 1, &FlagDetector::cloudCallback, this);

        // 发布话题
        flag_pub_ = nh_.advertise<geometry_msgs::Point>(output_flag_topic_, 10);
        marker_pub_ = nh_.advertise<visualization_msgs::MarkerArray>(output_marker_topic_, 10);
        downsampled_cloud_pub_ = nh_.advertise<sensor_msgs::PointCloud2>(output_downsampled_topic_, 10);
        clustered_cloud_pub_ = nh_.advertise<sensor_msgs::PointCloud2>(output_clustered_topic_, 10);
        roi_marker_pub_ = nh_.advertise<visualization_msgs::Marker>(output_roi_marker_topic_, 10); // 新增

        // 使用私有节点句柄读取参数
        private_nh_.param("roi_min_x", roi_min_x_, 0.0);
        private_nh_.param("roi_max_x", roi_max_x_, 8.0);
        private_nh_.param("roi_min_y", roi_min_y_, -8.0);
        private_nh_.param("roi_max_y", roi_max_y_, 0.0);
        private_nh_.param("roi_min_z", roi_min_z_, 0.2);
        private_nh_.param("roi_max_z", roi_max_z_, 3.5);
        private_nh_.param("voxel_leaf_size", voxel_leaf_size_, 0.05);
        private_nh_.param("cluster_tolerance", cluster_tolerance_, 0.1);
        private_nh_.param("min_cluster_size", min_cluster_size_, 10);
        private_nh_.param("max_cluster_size", max_cluster_size_, 500);
        private_nh_.param("flag_width_min", flag_width_min_, 0.02);
        private_nh_.param("flag_width_max", flag_width_max_, 0.5);
        private_nh_.param("min_flag_height", min_flag_height_, 0.3);
        private_nh_.param("max_flag_height", max_flag_height_, 2.0);
        private_nh_.param("surrounding_radius", surrounding_radius_, 0.5);
        private_nh_.param("surrounding_threshold", surrounding_threshold_, 5);

        ROS_INFO("Flag Detector initialized with ROI: [%.2f, %.2f] x [%.2f, %.2f] x [%.2f, %.2f]",
                 roi_min_x_, roi_max_x_, roi_min_y_, roi_max_y_, roi_min_z_, roi_max_z_);
        ROS_INFO("Input topic: %s", input_topic_.c_str());
        ROS_INFO("Frame ID: %s", frame_id_.c_str());
        ROS_INFO("Subscribed to topic: %s", input_topic_.c_str());

        // 定期发布ROI边界框
        roi_timer_ = nh_.createTimer(ros::Duration(1.0), &FlagDetector::publishROIBoundaryTimer, this);
    }

    void cloudCallback(const sensor_msgs::PointCloud2ConstPtr &msg)
    {
        ROS_INFO_THROTTLE(1.0, "Received point cloud with %u points", msg->width * msg->height);

        // 转换ROS点云到PCL
        pcl::PointCloud<pcl::PointXYZ>::Ptr cloud(new pcl::PointCloud<pcl::PointXYZ>);
        pcl::fromROSMsg(*msg, *cloud);

        // ROI过滤
        pcl::PointCloud<pcl::PointXYZ>::Ptr roi_cloud(new pcl::PointCloud<pcl::PointXYZ>);
        roi_filter(cloud, roi_cloud);

        if (roi_cloud->empty())
        {
            ROS_WARN_THROTTLE(1.0, "ROI filtered cloud is empty");
            return;
        }

        // 降采样
        pcl::PointCloud<pcl::PointXYZ>::Ptr downsampled_cloud(new pcl::PointCloud<pcl::PointXYZ>);
        voxel_grid_filter(roi_cloud, downsampled_cloud);

        // 发布降采样后的点云
        publishDownsampledCloud(downsampled_cloud, msg->header);

        // 聚类
        std::vector<pcl::PointCloud<pcl::PointXYZ>::Ptr> clusters = clusterPointCloud(downsampled_cloud);

        // 发布聚类后的点云（用于调试）
        publishClusteredCloud(clusters, msg->header);

        // 检测刀旗
        std::vector<FlagObject> flags = detectFlags(clusters);

        // 发布检测结果
        publishResults(flags, msg->header);
    }

private:
    void roi_filter(const pcl::PointCloud<pcl::PointXYZ>::Ptr &input,
                    pcl::PointCloud<pcl::PointXYZ>::Ptr &output)
    {
        output->clear();
        for (const auto &point : input->points)
        {
            if (point.x >= roi_min_x_ && point.x <= roi_max_x_ &&
                point.y >= roi_min_y_ && point.y <= roi_max_y_ &&
                point.z >= roi_min_z_ && point.z <= roi_max_z_)
            {
                output->points.push_back(point);
            }
        }
        output->width = output->points.size();
        output->height = 1;
    }

    void voxel_grid_filter(const pcl::PointCloud<pcl::PointXYZ>::Ptr &input,
                           pcl::PointCloud<pcl::PointXYZ>::Ptr &output)
    {
        pcl::VoxelGrid<pcl::PointXYZ> voxel_filter;
        voxel_filter.setInputCloud(input);
        voxel_filter.setLeafSize(voxel_leaf_size_, voxel_leaf_size_, voxel_leaf_size_);
        voxel_filter.filter(*output);
    }

    std::vector<pcl::PointCloud<pcl::PointXYZ>::Ptr> clusterPointCloud(const pcl::PointCloud<pcl::PointXYZ>::Ptr &cloud)
    {
        // 使用Euclidean聚类
        pcl::search::KdTree<pcl::PointXYZ>::Ptr tree(new pcl::search::KdTree<pcl::PointXYZ>);
        tree->setInputCloud(cloud);

        std::vector<pcl::PointIndices> cluster_indices;
        pcl::EuclideanClusterExtraction<pcl::PointXYZ> ec;
        ec.setClusterTolerance(cluster_tolerance_);
        ec.setMinClusterSize(min_cluster_size_);
        ec.setMaxClusterSize(max_cluster_size_);
        ec.setSearchMethod(tree);
        ec.setInputCloud(cloud);
        ec.extract(cluster_indices);

        std::vector<pcl::PointCloud<pcl::PointXYZ>::Ptr> clusters;
        for (const auto &indices : cluster_indices)
        {
            pcl::PointCloud<pcl::PointXYZ>::Ptr cluster(new pcl::PointCloud<pcl::PointXYZ>);
            for (const auto &idx : indices.indices)
            {
                cluster->points.push_back(cloud->points[idx]);
            }
            cluster->width = cluster->points.size();
            cluster->height = 1;
            clusters.push_back(cluster);
        }

        ROS_INFO_THROTTLE(1.0, "Found %zu clusters", clusters.size());
        return clusters;
    }

    std::vector<FlagObject> detectFlags(const std::vector<pcl::PointCloud<pcl::PointXYZ>::Ptr> &clusters)
    {
        std::vector<FlagObject> potential_flags;

        // 首先筛选可能的刀旗候选
        for (const auto &cluster : clusters)
        {
            FlagObject flag = extractFlagFromCluster(cluster);

            // 检查宽度和高度是否符合刀旗特征（高度现在是从Z=0到顶部）
            if (flag.width >= flag_width_min_ && flag.width <= flag_width_max_ &&
                flag.height >= min_flag_height_ && flag.height <= max_flag_height_)
            {
                potential_flags.push_back(flag);
            }
        }

        // 检查每个候选周围是否有其他聚类
        std::vector<FlagObject> flags;
        for (const auto &candidate : potential_flags)
        {
            if (isIsolated(candidate, potential_flags))
            {
                flags.push_back(candidate);
            }
        }

        ROS_INFO_THROTTLE(1.0, "Detected %zu flags", flags.size());
        return flags;
    }

    FlagObject extractFlagFromCluster(const pcl::PointCloud<pcl::PointXYZ>::Ptr &cluster)
    {
        FlagObject flag;

        if (cluster->points.empty())
        {
            flag.x = 0;
            flag.y = 0;
            flag.min_z = 0;
            flag.max_z = 0;
            flag.height = 0; // 从Z=0到顶部的高度
            flag.width = 0;
            return flag;
        }

        // 计算包围盒
        double min_x = std::numeric_limits<double>::max();
        double max_x = std::numeric_limits<double>::lowest();
        double min_y = std::numeric_limits<double>::max();
        double max_y = std::numeric_limits<double>::lowest();
        double min_z = std::numeric_limits<double>::max();
        double max_z = std::numeric_limits<double>::lowest();

        for (const auto &point : cluster->points)
        {
            double px = static_cast<double>(point.x);
            double py = static_cast<double>(point.y);
            double pz = static_cast<double>(point.z);

            if (px < min_x)
                min_x = px;
            if (px > max_x)
                max_x = px;
            if (py < min_y)
                min_y = py;
            if (py > max_y)
                max_y = py;
            if (pz < min_z)
                min_z = pz;
            if (pz > max_z)
                max_z = pz;
        }

        flag.x = (min_x + max_x) / 2.0;
        flag.y = (min_y + max_y) / 2.0;
        flag.min_z = min_z;
        flag.max_z = max_z;
        flag.height = max_z;                                 // 修改：从Z=0到刀旗顶部的高度
        flag.width = std::max(max_x - min_x, max_y - min_y); // 取X和Y方向的最大值作为宽度

        return flag;
    }

    bool isIsolated(const FlagObject &flag, const std::vector<FlagObject> &all_flags)
    {
        int surrounding_count = 0;

        for (const auto &other_flag : all_flags)
        {
            if (&flag == &other_flag)
                continue; // 跳过自己

            double dist = sqrt(pow(flag.x - other_flag.x, 2) + pow(flag.y - other_flag.y, 2));
            if (dist <= surrounding_radius_)
            {
                surrounding_count++;
                if (surrounding_count > surrounding_threshold_)
                {
                    return false; // 周围聚类过多，不是独立的刀旗
                }
            }
        }

        return true; // 周围聚类数量在阈值内，是独立的刀旗
    }

    void publishROIBoundaryTimer(const ros::TimerEvent &)
    {
        publishROIBoundary();
    }

    void publishROIBoundary()
    {
        visualization_msgs::Marker roi_marker;
        roi_marker.header.frame_id = frame_id_; // 使用参数指定的坐标系
        roi_marker.header.stamp = ros::Time::now();
        roi_marker.ns = "roi_boundary";
        roi_marker.id = 0;
        roi_marker.type = visualization_msgs::Marker::LINE_LIST;
        roi_marker.action = visualization_msgs::Marker::ADD;

        // 设置ROI边界框的线宽
        roi_marker.scale.x = 0.02; // 增加线宽

        // 设置颜色（绿色，增加透明度以避免遮挡）
        roi_marker.color.r = 0.0;
        roi_marker.color.g = 1.0;
        roi_marker.color.b = 0.0;
        roi_marker.color.a = 0.5; // 降低透明度

        // 检查ROI参数是否有效
        if (roi_max_x_ <= roi_min_x_ || roi_max_y_ <= roi_min_y_ || roi_max_z_ <= roi_min_z_)
        {
            ROS_WARN("Invalid ROI parameters, cannot create boundary box");
            return;
        }

        // 定义ROI边界框的8个顶点
        geometry_msgs::Point p[8];

        // 底面4个顶点 (Z = roi_min_z_)
        p[0].x = roi_min_x_;
        p[0].y = roi_min_y_;
        p[0].z = roi_min_z_; // 左前下
        p[1].x = roi_max_x_;
        p[1].y = roi_min_y_;
        p[1].z = roi_min_z_; // 右前下
        p[2].x = roi_max_x_;
        p[2].y = roi_max_y_;
        p[2].z = roi_min_z_; // 右后下
        p[3].x = roi_min_x_;
        p[3].y = roi_max_y_;
        p[3].z = roi_min_z_; // 左后下

        // 顶面4个顶点 (Z = roi_max_z_)
        p[4].x = roi_min_x_;
        p[4].y = roi_min_y_;
        p[4].z = roi_max_z_; // 左前上
        p[5].x = roi_max_x_;
        p[5].y = roi_min_y_;
        p[5].z = roi_max_z_; // 右前上
        p[6].x = roi_max_x_;
        p[6].y = roi_max_y_;
        p[6].z = roi_max_z_; // 右后上
        p[7].x = roi_min_x_;
        p[7].y = roi_max_y_;
        p[7].z = roi_max_z_; // 左后上

        // 底面边线
        roi_marker.points.push_back(p[0]);
        roi_marker.points.push_back(p[1]); // 前边
        roi_marker.points.push_back(p[1]);
        roi_marker.points.push_back(p[2]); // 右边
        roi_marker.points.push_back(p[2]);
        roi_marker.points.push_back(p[3]); // 后边
        roi_marker.points.push_back(p[3]);
        roi_marker.points.push_back(p[0]); // 左边

        // 顶面边线
        roi_marker.points.push_back(p[4]);
        roi_marker.points.push_back(p[5]); // 前边
        roi_marker.points.push_back(p[5]);
        roi_marker.points.push_back(p[6]); // 右边
        roi_marker.points.push_back(p[6]);
        roi_marker.points.push_back(p[7]); // 后边
        roi_marker.points.push_back(p[7]);
        roi_marker.points.push_back(p[4]); // 左边

        // 垂直边线
        roi_marker.points.push_back(p[0]);
        roi_marker.points.push_back(p[4]); // 左前垂直
        roi_marker.points.push_back(p[1]);
        roi_marker.points.push_back(p[5]); // 右前垂直
        roi_marker.points.push_back(p[2]);
        roi_marker.points.push_back(p[6]); // 右后垂直
        roi_marker.points.push_back(p[3]);
        roi_marker.points.push_back(p[7]); // 左后垂直

        roi_marker_pub_.publish(roi_marker);

        ROS_INFO_ONCE("Published ROI boundary marker with %zu points", roi_marker.points.size());
    }

    void publishDownsampledCloud(const pcl::PointCloud<pcl::PointXYZ>::Ptr &cloud,
                                 const std_msgs::Header &header)
    {
        if (cloud->empty())
        {
            ROS_WARN_THROTTLE(1.0, "Downsampled cloud is empty, not publishing");
            return;
        }

        sensor_msgs::PointCloud2 output_msg;
        pcl::toROSMsg(*cloud, output_msg);
        output_msg.header = header;
        downsampled_cloud_pub_.publish(output_msg);
    }

    void publishClusteredCloud(const std::vector<pcl::PointCloud<pcl::PointXYZ>::Ptr> &clusters,
                               const std_msgs::Header &header)
    {
        pcl::PointCloud<pcl::PointXYZRGB> colored_cloud;

        // 为每个聚类分配不同颜色
        std::vector<uint8_t> colors[] = {
            {255, 0, 0},   // 红色
            {0, 255, 0},   // 绿色
            {0, 0, 255},   // 蓝色
            {255, 255, 0}, // 黄色
            {255, 0, 255}, // 紫色
            {0, 255, 255}, // 青色
        };

        for (size_t i = 0; i < clusters.size(); ++i)
        {
            auto color = colors[i % (sizeof(colors) / sizeof(colors[0]))];
            for (const auto &point : clusters[i]->points)
            {
                pcl::PointXYZRGB colored_point;
                colored_point.x = point.x;
                colored_point.y = point.y;
                colored_point.z = point.z;
                colored_point.r = color[0];
                colored_point.g = color[1];
                colored_point.b = color[2];
                colored_cloud.push_back(colored_point);
            }
        }

        if (!colored_cloud.empty())
        {
            sensor_msgs::PointCloud2 output_msg;
            pcl::toROSMsg(colored_cloud, output_msg);
            output_msg.header = header;
            clustered_cloud_pub_.publish(output_msg);
        }
    }

    void publishResults(const std::vector<FlagObject> &flags,
                        const std_msgs::Header &header)
    {
        // 发布刀旗坐标
        for (const auto &flag : flags)
        {
            geometry_msgs::Point point_msg;
            point_msg.x = flag.x;
            point_msg.y = flag.y;
            point_msg.z = flag.height / 2.0; // Z坐标为高度的一半（中心高度）
            flag_pub_.publish(point_msg);
        }

        // 发布可视化标记
        visualization_msgs::MarkerArray marker_array;

        for (size_t i = 0; i < flags.size(); ++i)
        {
            const auto &flag = flags[i];

            // 创建圆柱体标记（表示刀旗杆）
            visualization_msgs::Marker flag_marker;
            flag_marker.header = header;
            flag_marker.ns = "flags";
            flag_marker.id = i;
            flag_marker.type = visualization_msgs::Marker::CYLINDER;
            flag_marker.action = visualization_msgs::Marker::ADD;

            flag_marker.pose.position.x = flag.x;
            flag_marker.pose.position.y = flag.y;
            flag_marker.pose.position.z = flag.height / 2.0; // Z坐标为高度的一半
            flag_marker.pose.orientation.w = 1.0;

            flag_marker.scale.x = flag.width;  // 直径
            flag_marker.scale.y = flag.width;  // 直径
            flag_marker.scale.z = flag.height; // 圆柱体高度为从Z=0到顶部的高度

            flag_marker.color.r = 1.0;
            flag_marker.color.g = 0.0;
            flag_marker.color.b = 0.0;
            flag_marker.color.a = 0.7;

            marker_array.markers.push_back(flag_marker);

            // 创建坐标文本标记
            visualization_msgs::Marker text_marker;
            text_marker.header = header;
            text_marker.ns = "flag_text";
            text_marker.id = i + flags.size();
            text_marker.type = visualization_msgs::Marker::TEXT_VIEW_FACING;
            text_marker.action = visualization_msgs::Marker::ADD;

            text_marker.pose.position.x = flag.x;
            text_marker.pose.position.y = flag.y;
            text_marker.pose.position.z = flag.height + 0.3; // Z坐标为顶部高度+偏移
            text_marker.pose.orientation.w = 1.0;

            text_marker.scale.z = 0.25;

            text_marker.color.r = 1.0;
            text_marker.color.g = 1.0;
            text_marker.color.b = 1.0;
            text_marker.color.a = 1.0;

            char text[100];
            snprintf(text, sizeof(text), "Flag(%.2f, %.2f)", flag.x, flag.y);
            text_marker.text = std::string(text);

            marker_array.markers.push_back(text_marker);
        }

        marker_pub_.publish(marker_array);
    }
};

int main(int argc, char **argv)
{
    ros::init(argc, argv, "flag_recognition");
    FlagDetector detector;
    ros::spin();
    return 0;
}