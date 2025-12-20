#include <ros/ros.h>
#include <sensor_msgs/PointCloud2.h>
#include <pcl_conversions/pcl_conversions.h>
#include <pcl/point_cloud.h>
#include <pcl/point_types.h>
#include <pcl/filters/extract_indices.h>
#include <pcl/segmentation/sac_segmentation.h>
#include <pcl/filters/voxel_grid.h>
#include <pcl/filters/passthrough.h>
#include <cmath>

class PlaneExtractor
{
public:
    PlaneExtractor()
    {
        loadParameters();

        sub_ = nh_.subscribe(input_topic_, 1, &PlaneExtractor::cloudCallback, this);

        // 动态创建发布者
        for (int i = 0; i < max_planes_; ++i)
        {
            std::string topic_name = "/plane_extractor/plane_clouds_" + std::to_string(i + 1);
            pub_planes_.push_back(nh_.advertise<sensor_msgs::PointCloud2>(topic_name, 1));
        }

        ROS_INFO_STREAM("PlaneExtractor node started.");
        ROS_INFO_STREAM("Input topic: " << input_topic_);
        ROS_INFO_STREAM("Max planes: " << max_planes_);
        ROS_INFO_STREAM("Vertical tolerance (rad): " << vertical_tolerance_);
        ROS_INFO_STREAM("ROI: x[" << roi_x_min_ << ", " << roi_x_max_ << "] "
                                  << "y[" << roi_y_min_ << ", " << roi_y_max_ << "] "
                                  << "z[" << roi_z_min_ << ", " << roi_z_max_ << "]");
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

        nh_.param<int>("plane_extraction/max_planes", max_planes_, 2);
        nh_.param<double>("plane_extraction/vertical_tolerance", vertical_tolerance_, 0.1); // 弧度
    }

    bool isVerticalPlane(const pcl::ModelCoefficients::Ptr coeffs, double tolerance)
    {
        // 法向量 (a, b, c)
        double a = coeffs->values[0];
        double b = coeffs->values[1];
        double c = coeffs->values[2];

        // 与 Z 轴夹角：cosθ = |c| / sqrt(a² + b² + c²)
        double norm = std::sqrt(a * a + b * b + c * c);
        if (norm < 1e-6)
            return false;
        double cos_theta = std::abs(c) / norm;
        double angle = std::acos(cos_theta);

        // 检查角度是否接近90度（π/2）
        double target_angle = M_PI / 2.0;
        return std::abs(angle - target_angle) <= tolerance;
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

        pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_remaining(new pcl::PointCloud<pcl::PointXYZ>);
        *cloud_remaining = *region_cloud;

        int plane_count = 0;

        while (plane_count < max_planes_)
        {
            pcl::ModelCoefficients::Ptr coefficients(new pcl::ModelCoefficients);
            pcl::PointIndices::Ptr inliers(new pcl::PointIndices);

            pcl::SACSegmentation<pcl::PointXYZ> seg;
            seg.setOptimizeCoefficients(optimize_coefficients_);
            seg.setModelType(pcl::SACMODEL_PLANE);
            seg.setMethodType(pcl::SAC_RANSAC);
            seg.setMaxIterations(max_iterations_);
            seg.setDistanceThreshold(distance_threshold_);
            seg.setInputCloud(cloud_remaining);
            seg.segment(*inliers, *coefficients);

            if (inliers->indices.empty())
                break;

            // 判断是否垂直于地面
            if (!isVerticalPlane(coefficients, vertical_tolerance_))
            {
                ROS_DEBUG("Plane is not vertical, skipping.");
                // 从剩余点中移除该平面点
                pcl::ExtractIndices<pcl::PointXYZ> extract;
                extract.setInputCloud(cloud_remaining);
                extract.setIndices(inliers);
                extract.setNegative(true);
                pcl::PointCloud<pcl::PointXYZ>::Ptr temp(new pcl::PointCloud<pcl::PointXYZ>);
                extract.filter(*temp);
                *cloud_remaining = *temp;
                continue;
            }

            // 提取平面点
            pcl::ExtractIndices<pcl::PointXYZ> extract;
            extract.setInputCloud(cloud_remaining);
            extract.setIndices(inliers);
            pcl::PointCloud<pcl::PointXYZ>::Ptr plane_cloud(new pcl::PointCloud<pcl::PointXYZ>);
            extract.filter(*plane_cloud);

            // 发布平面
            sensor_msgs::PointCloud2 output_msg;
            pcl::toROSMsg(*plane_cloud, output_msg);
            output_msg.header = input_msg->header;
            pub_planes_[plane_count].publish(output_msg);

            ROS_INFO_STREAM("Published " << plane_cloud->points.size() << " points on vertical plane " << (plane_count + 1) << ".");

            // 移除已提取的点
            extract.setNegative(true);
            pcl::PointCloud<pcl::PointXYZ>::Ptr temp(new pcl::PointCloud<pcl::PointXYZ>);
            extract.filter(*temp);
            *cloud_remaining = *temp;

            plane_count++;
        }

        if (plane_count == 0)
        {
            ROS_WARN("No vertical planes found in the specified region.");
        }
    }

    ros::NodeHandle nh_;
    ros::Subscriber sub_;
    std::vector<ros::Publisher> pub_planes_;

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
    double vertical_tolerance_; // 弧度
};

int main(int argc, char **argv)
{
    ros::init(argc, argv, "plane_extractor");
    PlaneExtractor pe;
    ros::spin();
    return 0;
}