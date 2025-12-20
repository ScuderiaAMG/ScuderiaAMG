#include <ros/ros.h>
#include <image_transport/image_transport.h>
#include <cv_bridge/cv_bridge.h>
#include <sensor_msgs/image_encodings.h>
#include <opencv2/opencv.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/highgui.hpp>
#include <vector>
#include <string>
#include <boost/bind/bind.hpp>
#include <vision_msgs/Detection2DArray.h>
#include <vision_msgs/Detection2D.h>
#include <vision_msgs/ObjectHypothesisWithPose.h>
#include <XmlRpcValue.h>

struct TemplateVariant
{
    cv::Mat image;    // 模板图像
    double threshold; // 该变体的阈值
    std::string name; // 变体名称（可选，用于调试）
};

struct TemplateGroup
{
    std::string class_name;                // 类别名称（所有变体共用）
    int class_id;                          // 类别ID
    std::vector<TemplateVariant> variants; // 该类别的多个模板变体
};

class TemplateMatchingNode
{
private:
    ros::NodeHandle nh_;
    ros::NodeHandle private_nh_; // 私有命名空间NodeHandle
    image_transport::ImageTransport it_;
    // 多个订阅者和发布者
    std::vector<image_transport::Subscriber> image_subs_;
    std::vector<image_transport::Publisher> image_pubs_;
    // 多个平面的结果发布者（每个 plane 一个）
    std::vector<ros::Publisher> centers_pubs_; // 发布 Detection2DArray

    // 全局模板组（所有plane共享）
    std::vector<TemplateGroup> template_groups_; // [group_index]

    // 模板匹配参数
    double threshold_; // 全局默认阈值
    int match_method_;
    // 新增：缩放参数 (x和y方向)
    double scale_x_min_;
    double scale_x_max_;
    double scale_x_step_;
    double scale_y_min_;
    double scale_y_max_;
    double scale_y_step_;
    // 平面数量
    int num_planes_;

public:
    TemplateMatchingNode() : nh_(), private_nh_("~"), it_(nh_)
    {
        // 从参数服务器获取配置
        getParameters();
        // 初始化多个订阅者和发布者
        setupSubscribersAndPublishers();
        ROS_INFO("Template Matching Node initialized with %d planes", num_planes_);
    }

private:
    void getParameters()
    {
        // 读取平面数量
        private_nh_.param<int>("num_planes", num_planes_, 2); // 默认2个平面
        if (num_planes_ <= 0)
        {
            ROS_FATAL("Invalid num_planes: %d, must be > 0", num_planes_);
            ros::shutdown();
            return;
        }

        // 读取全局模板组配置
        XmlRpc::XmlRpcValue template_groups_param;
        if (private_nh_.getParam("template_groups", template_groups_param))
        {
            ROS_ASSERT(template_groups_param.getType() == XmlRpc::XmlRpcValue::TypeArray);

            for (int j = 0; j < template_groups_param.size(); ++j)
            {
                TemplateGroup group;
                XmlRpc::XmlRpcValue &group_param = template_groups_param[j];

                group.class_name = static_cast<std::string>(group_param["class_name"]);
                group.class_id = static_cast<int>(group_param["class_id"]);

                XmlRpc::XmlRpcValue &variants_param = group_param["variants"];
                ROS_ASSERT(variants_param.getType() == XmlRpc::XmlRpcValue::TypeArray);

                for (int k = 0; k < variants_param.size(); ++k)
                {
                    TemplateVariant variant;
                    XmlRpc::XmlRpcValue &variant_param = variants_param[k];

                    std::string path = static_cast<std::string>(variant_param["path"]);
                    variant.threshold = static_cast<double>(variant_param["threshold"]);
                    variant.name = variant_param.hasMember("name") ? static_cast<std::string>(variant_param["name"]) : "variant_" + std::to_string(k);

                    // 加载模板图像
                    cv::Mat img = cv::imread(path, cv::IMREAD_COLOR);
                    if (!img.empty())
                    {
                        cv::cvtColor(img, img, cv::COLOR_BGR2GRAY);
                        variant.image = img;
                        group.variants.push_back(variant);
                        ROS_INFO("Loaded variant '%s' for class '%s'",
                                 variant.name.c_str(), group.class_name.c_str());
                    }
                    else
                    {
                        ROS_WARN("Failed to load template: %s", path.c_str());
                    }
                }

                template_groups_.push_back(group);
            }
        }

        // 匹配参数
        private_nh_.param<double>("matching_threshold", threshold_, 0.8);
        private_nh_.param<int>("match_method", match_method_, cv::TM_CCOEFF_NORMED);
        // 新增：读取 x 和 y 方向的缩放参数
        private_nh_.param<double>("scale_x_min", scale_x_min_, 0.8);
        private_nh_.param<double>("scale_x_max", scale_x_max_, 1.2);
        private_nh_.param<double>("scale_x_step", scale_x_step_, 0.05);
        private_nh_.param<double>("scale_y_min", scale_y_min_, 0.8);
        private_nh_.param<double>("scale_y_max", scale_y_max_, 1.2);
        private_nh_.param<double>("scale_y_step", scale_y_step_, 0.05);

        // 打印参数
        ROS_INFO("Loaded %zu template groups:", template_groups_.size());
        for (const auto &group : template_groups_)
        {
            ROS_INFO("  - Class: %s (ID: %d) with %zu variants",
                     group.class_name.c_str(), group.class_id, group.variants.size());
            for (const auto &variant : group.variants)
            {
                ROS_INFO("    * Variant: %s, threshold: %.2f",
                         variant.name.c_str(), variant.threshold);
            }
        }
        ROS_INFO("Default Matching threshold: %.2f", threshold_);
        ROS_INFO("Match method: %d", match_method_);
        // 打印新的缩放参数
        ROS_INFO("Scale X range: %.2f - %.2f (step: %.2f)", scale_x_min_, scale_x_max_, scale_x_step_);
        ROS_INFO("Scale Y range: %.2f - %.2f (step: %.2f)", scale_y_min_, scale_y_max_, scale_y_step_);
        ROS_INFO("Number of planes: %d", num_planes_);
    }

    void setupSubscribersAndPublishers()
    {
        image_subs_.resize(num_planes_);
        image_pubs_.resize(num_planes_);
        centers_pubs_.resize(num_planes_);
        for (int i = 0; i < num_planes_; ++i)
        {
            std::string input_topic = "/point_projector/plane_" + std::to_string(i + 1) + "/projected_image";
            std::string output_topic = "template_matching_result/plane_" + std::to_string(i + 1);
            std::string centers_topic = "template_centers/plane_" + std::to_string(i + 1);
            image_subs_[i] = it_.subscribe(
                input_topic, 1,
                boost::bind(&TemplateMatchingNode::imageCallback, this, boost::placeholders::_1, i),
                ros::VoidPtr(),
                image_transport::TransportHints());
            image_pubs_[i] = it_.advertise(output_topic, 1);
            centers_pubs_[i] = nh_.advertise<vision_msgs::Detection2DArray>(centers_topic, 1);
            ROS_INFO("Subscribed to: %s", input_topic.c_str());
            ROS_INFO("Publishing image result to: %s", output_topic.c_str());
            ROS_INFO("Publishing centers to: %s", centers_topic.c_str());
        }
    }

    // 统一的图像回调函数，接收 plane_index 作为参数
    void imageCallback(const sensor_msgs::ImageConstPtr &msg, int plane_index)
    {
        try
        {
            // 转换为单通道二值图
            cv_bridge::CvImagePtr cv_ptr = cv_bridge::toCvCopy(msg, sensor_msgs::image_encodings::MONO8);
            cv::Mat binary_image = cv_ptr->image;
            // 结果图像（BGR 用于可视化）
            cv::Mat result_image;
            cv::cvtColor(binary_image, result_image, cv::COLOR_GRAY2BGR);
            // 掩码：防止重复匹配 (关键：在所有尺度和模板间共享)
            cv::Mat mask = cv::Mat::ones(binary_image.size(), CV_8UC1) * 255;
            // 存储所有检测结果（用于发布）
            vision_msgs::Detection2DArray detections_msg;
            detections_msg.header = msg->header;

            // 从高优先级模板组开始匹配（逆序遍历，索引大的优先级高）
            for (int group_idx = static_cast<int>(template_groups_.size()) - 1; group_idx >= 0; --group_idx)
            {
                const auto &group = template_groups_[group_idx];
                bool group_found = false;

                // 遍历该组的所有变体
                for (size_t variant_idx = 0; variant_idx < group.variants.size() && !group_found; ++variant_idx)
                {
                    const auto &variant = group.variants[variant_idx];

                    // 对每个变体进行多尺度匹配
                    for (double scale_x = scale_x_min_; scale_x <= scale_x_max_ && !group_found; scale_x += scale_x_step_)
                    {
                        for (double scale_y = scale_y_min_; scale_y <= scale_y_max_ && !group_found; scale_y += scale_y_step_)
                        {
                            // 调整模板大小
                            cv::Mat resized_template;
                            cv::resize(variant.image, resized_template, cv::Size(), scale_x, scale_y, cv::INTER_LINEAR);

                            // 检查模板大小
                            if (resized_template.cols > binary_image.cols || resized_template.rows > binary_image.rows)
                                continue;

                            // 应用掩码（如果需要）
                            cv::Mat masked_image = binary_image.clone();
                            masked_image.setTo(cv::Scalar(0), ~mask);

                            // 执行模板匹配
                            int result_cols = masked_image.cols - resized_template.cols + 1;
                            int result_rows = masked_image.rows - resized_template.rows + 1;
                            if (result_cols <= 0 || result_rows <= 0)
                                continue;

                            cv::Mat result(result_rows, result_cols, CV_32FC1);
                            cv::matchTemplate(masked_image, resized_template, result, match_method_);

                            bool is_inverse_method = (match_method_ == cv::TM_SQDIFF || match_method_ == cv::TM_SQDIFF_NORMED);

                            // 查找最佳匹配
                            double min_val, max_val;
                            cv::Point min_loc, max_loc;
                            cv::minMaxLoc(result, &min_val, &max_val, &min_loc, &max_loc);

                            double match_val = is_inverse_method ? min_val : max_val;
                            cv::Point match_loc = is_inverse_method ? min_loc : max_loc;

                            // 使用该变体的阈值进行判断
                            if ((is_inverse_method && match_val <= (1.0 - variant.threshold)) ||
                                (!is_inverse_method && match_val >= variant.threshold))
                            {
                                // 计算匹配框
                                cv::Point pt1 = match_loc;
                                cv::Point pt2(pt1.x + resized_template.cols, pt1.y + resized_template.rows);
                                cv::Point center = (pt1 + pt2) / 2;

                                // 绘制结果（使用组的类别名）
                                cv::rectangle(result_image, pt1, pt2, cv::Scalar(0, 255, 0), 2);
                                std::string label = group.class_name +
                                                    " (Sx:" + std::to_string(static_cast<int>(scale_x * 100)) + "%" +
                                                    ", Sy:" + std::to_string(static_cast<int>(scale_y * 100)) + "%)";
                                cv::putText(result_image, label, cv::Point(pt1.x, pt1.y - 10),
                                            cv::FONT_HERSHEY_SIMPLEX, 0.5, cv::Scalar(0, 255, 0), 1);

                                // 更新掩码
                                cv::rectangle(mask, pt1, pt2, cv::Scalar(0), -1);

                                // 发布检测结果（使用组的类别信息）
                                vision_msgs::Detection2D det;
                                det.header = msg->header;
                                det.bbox.center.x = center.x;
                                det.bbox.center.y = center.y;
                                det.bbox.size_x = pt2.x - pt1.x;
                                det.bbox.size_y = pt2.y - pt1.y;

                                vision_msgs::ObjectHypothesisWithPose hypothesis;
                                hypothesis.id = group.class_id; // 使用组ID
                                hypothesis.score = match_val;

                                det.results.push_back(hypothesis);
                                detections_msg.detections.push_back(det);

                                // 标记该组已找到，跳出变体循环和缩放循环
                                group_found = true;

                                ROS_INFO("Plane %d: Matched '%s' (variant: %s) at (%d, %d), scale: (%.2f, %.2f)",
                                         plane_index + 1, group.class_name.c_str(), variant.name.c_str(),
                                         center.x, center.y, scale_x, scale_y);
                            }
                        }
                    }
                }
            }

            // 发布可视化图像
            cv_bridge::CvImage out_img;
            out_img.header = msg->header;
            out_img.encoding = sensor_msgs::image_encodings::BGR8;
            out_img.image = result_image;
            image_pubs_[plane_index].publish(out_img.toImageMsg());
            // 发布检测结果（中心坐标等）
            centers_pubs_[plane_index].publish(detections_msg); // 即使为空也发布
        }
        catch (cv_bridge::Exception &e)
        {
            ROS_ERROR("Plane %d: cv_bridge exception: %s", plane_index + 1, e.what());
        }
        catch (const std::exception &e)
        {
            ROS_ERROR("Plane %d: Standard exception: %s", plane_index + 1, e.what());
        }
    }
};

int main(int argc, char **argv)
{
    ros::init(argc, argv, "template_match");
    TemplateMatchingNode node;
    ros::spin();
    return 0;
}