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
    // 模板图像
    std::vector<cv::Mat> templates_; // 原始模板图像
    std::vector<std::string> template_names_;
    // 模板匹配参数
    double threshold_;                        // 全局默认阈值
    std::vector<double> template_thresholds_; // 每个模板的阈值
    int match_method_;
    // 新增：缩放参数 (x和y方向)
    double scale_x_min_;
    double scale_x_max_;
    double scale_x_step_;
    double scale_y_min_;
    double scale_y_max_;
    double scale_y_step_;
    // 模板文件路径
    std::vector<std::string> template_paths_;
    // 平面数量
    int num_planes_;

public:
    TemplateMatchingNode() : nh_(), private_nh_("~"), it_(nh_)
    {
        // 从参数服务器获取配置
        getParameters();
        // 加载模板图像
        loadTemplates();
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
        // 读取模板路径列表
        private_nh_.param<std::vector<std::string>>(
            "template_paths",
            template_paths_,
            {"/home/pentsinh/vision_ws/src/cloud_recognition/template/obs1.png"});
        // 读取模板名称列表
        private_nh_.param<std::vector<std::string>>(
            "template_names",
            template_names_,
            {"Object_0"});
        // 确保名称和路径数量一致
        if (template_names_.size() != template_paths_.size())
        {
            ROS_WARN("template_names size (%zu) != template_paths size (%zu), using default names",
                     template_names_.size(), template_paths_.size());
            template_names_.clear();
            for (size_t i = 0; i < template_paths_.size(); ++i)
            {
                template_names_.push_back("Object_" + std::to_string(i));
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

        // --- 新增代码：读取每个模板的阈值 ---
        // 尝试读取每个模板的特定阈值列表
        std::vector<double> tmp_thresholds;
        private_nh_.param<std::vector<double>>("template_thresholds", tmp_thresholds, std::vector<double>());

        // 确保 template_thresholds_ 数量与模板数量一致
        template_thresholds_.clear();
        if (tmp_thresholds.size() == template_paths_.size())
        {
            template_thresholds_ = tmp_thresholds;
            ROS_INFO("Loaded per-template thresholds.");
        }
        else
        {
            if (!tmp_thresholds.empty())
            {
                ROS_WARN("template_thresholds size (%zu) != template_paths/ names size (%zu), using default threshold %.2f for all.",
                         tmp_thresholds.size(), template_paths_.size(), threshold_);
            }
            // 如果没有提供或数量不匹配，则为所有模板使用默认阈值
            template_thresholds_.resize(template_paths_.size(), threshold_);
        }
        // --- 新增代码结束 ---

        // 打印参数
        ROS_INFO("Loaded %zu templates:", template_paths_.size());
        for (size_t i = 0; i < template_paths_.size(); ++i)
        {
            ROS_INFO("  - %s (Name: %s, Threshold: %.2f)", template_paths_[i].c_str(), template_names_[i].c_str(), template_thresholds_[i]);
        }
        ROS_INFO("Default Matching threshold: %.2f", threshold_);
        ROS_INFO("Match method: %d", match_method_);
        // 打印新的缩放参数
        ROS_INFO("Scale X range: %.2f - %.2f (step: %.2f)", scale_x_min_, scale_x_max_, scale_x_step_);
        ROS_INFO("Scale Y range: %.2f - %.2f (step: %.2f)", scale_y_min_, scale_y_max_, scale_y_step_);
        ROS_INFO("Number of planes: %d", num_planes_);
    }
    void loadTemplates()
    {
        templates_.clear();
        for (const auto &path : template_paths_)
        {
            cv::Mat template_img = cv::imread(path, cv::IMREAD_COLOR);
            if (template_img.empty())
            {
                ROS_WARN("Failed to load template: %s", path.c_str());
                continue;
            }
            cv::Mat template_gray;
            cv::cvtColor(template_img, template_gray, cv::COLOR_BGR2GRAY);
            templates_.push_back(template_gray); // 存储原始尺寸的灰度图
            ROS_INFO("Loaded template: %s, size: %dx%d",
                     path.c_str(), template_img.cols, template_img.rows);
        }
        if (templates_.empty())
        {
            ROS_ERROR("No valid templates loaded!");
            ros::shutdown();
        }
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
    // 修改后的模板匹配函数，支持 x 和 y 方向独立缩放
    std::vector<std::tuple<cv::Point, cv::Point, double, double>> findTemplateMatches(
        const cv::Mat &image_gray, const cv::Mat &templ, double current_threshold) // 新增参数
    {
        std::vector<std::tuple<cv::Point, cv::Point, double, double>> matches; // (pt1, pt2, scale_x, scale_y)
        if (image_gray.empty() || templ.empty())
            return matches;
        // 遍历 x 和 y 方向的缩放比例
        for (double scale_x = scale_x_min_; scale_x <= scale_x_max_; scale_x += scale_x_step_)
        {
            for (double scale_y = scale_y_min_; scale_y <= scale_y_max_; scale_y += scale_y_step_)
            {
                // 调整模板大小
                cv::Mat resized_template;
                // 使用 INTER_AREA 进行缩小，LINEAR 用于放大，通常 INTER_LINEAR 是一个好选择
                cv::resize(templ, resized_template, cv::Size(), scale_x, scale_y, cv::INTER_LINEAR);
                // 检查调整后模板是否仍然适合图像
                if (resized_template.cols > image_gray.cols || resized_template.rows > image_gray.rows)
                {
                    continue; // 模板太大，跳过
                }
                int result_cols = image_gray.cols - resized_template.cols + 1;
                int result_rows = image_gray.rows - resized_template.rows + 1;
                if (result_cols <= 0 || result_rows <= 0)
                    continue;
                cv::Mat result(result_rows, result_cols, CV_32FC1);
                cv::matchTemplate(image_gray, resized_template, result, match_method_);
                bool is_inverse_method = (match_method_ == cv::TM_SQDIFF ||
                                          match_method_ == cv::TM_SQDIFF_NORMED);
                // 遍历匹配结果矩阵，查找所有满足阈值的点
                for (int y = 0; y < result.rows; ++y)
                {
                    for (int x = 0; x < result.cols; ++x)
                    {
                        double value = static_cast<double>(result.at<float>(y, x));
                        // 使用传入的 current_threshold
                        if ((is_inverse_method && value <= (1.0 - current_threshold)) ||
                            (!is_inverse_method && value >= current_threshold))
                        {
                            cv::Point pt1(x, y);
                            cv::Point pt2(x + resized_template.cols, y + resized_template.rows);
                            matches.push_back(std::make_tuple(pt1, pt2, scale_x, scale_y)); // 记录匹配框和对应的缩放比例
                        }
                    }
                }
            } // end for scale_y
        } // end for scale_x
        // 去重 - 使用修改后的 NMS
        return nonMaxSuppression(matches);
    }
    // 修改后的非极大值抑制，处理不同大小的匹配框 (基于 IoU)
    std::vector<std::tuple<cv::Point, cv::Point, double, double>> nonMaxSuppression(
        const std::vector<std::tuple<cv::Point, cv::Point, double, double>> &matches)
    {
        if (matches.empty())
            return matches;
        std::vector<bool> suppressed(matches.size(), false);
        std::vector<std::tuple<cv::Point, cv::Point, double, double>> filtered_matches;
        // 可以根据需要调整 IoU 阈值
        const double iou_threshold = 0.3;
        for (size_t i = 0; i < matches.size(); ++i)
        {
            if (suppressed[i])
                continue;
            cv::Point pt1_i = std::get<0>(matches[i]);
            cv::Point pt2_i = std::get<1>(matches[i]);
            // cv::Point center_i = (pt1_i + pt2_i) / 2; // 如果需要中心点
            int width_i = pt2_i.x - pt1_i.x;
            int height_i = pt2_i.y - pt1_i.y;
            double area_i = static_cast<double>(width_i) * height_i;
            filtered_matches.push_back(matches[i]); // 假设当前匹配是有效的
            for (size_t j = i + 1; j < matches.size(); ++j)
            {
                if (suppressed[j])
                    continue;
                cv::Point pt1_j = std::get<0>(matches[j]);
                cv::Point pt2_j = std::get<1>(matches[j]);
                // cv::Point center_j = (pt1_j + pt2_j) / 2; // 如果需要中心点
                int width_j = pt2_j.x - pt1_j.x;
                int height_j = pt2_j.y - pt1_j.y;
                double area_j = static_cast<double>(width_j) * height_j;
                // 计算两个矩形的交集区域
                int inter_x1 = std::max(pt1_i.x, pt1_j.x);
                int inter_y1 = std::max(pt1_i.y, pt1_j.y);
                int inter_x2 = std::min(pt2_i.x, pt2_j.x);
                int inter_y2 = std::min(pt2_i.y, pt2_j.y);
                int inter_width = std::max(0, inter_x2 - inter_x1);
                int inter_height = std::max(0, inter_y2 - inter_y1);
                double inter_area = static_cast<double>(inter_width) * inter_height;
                // 计算并集区域
                double union_area = area_i + area_j - inter_area;
                // 计算 IoU
                double iou = (union_area > 0) ? (inter_area / union_area) : 0;
                // 如果 IoU 超过阈值，则抑制其中一个 (保留第一个)
                if (iou > iou_threshold)
                {
                    suppressed[j] = true; // 抑制重叠的
                }
            }
        }
        return filtered_matches;
    }
    // 统一的图像回调函数，接收 plane_index 作为参数
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
            // 从高优先级模板开始匹配
            for (int i = static_cast<int>(templates_.size()) - 1; i >= 0; --i)
            {
                const cv::Mat &templ = templates_[i];
                // --- 修改：获取当前模板的阈值 ---
                double current_template_threshold = template_thresholds_[i];
                // --- 修改结束 ---

                bool template_found = false; // 标志位：此模板是否已找到，找到则跳出缩放循环
                // 遍历 x 和 y 方向的缩放比例
                for (double scale_x = scale_x_min_; scale_x <= scale_x_max_ && !template_found; scale_x += scale_x_step_)
                {
                    for (double scale_y = scale_y_min_; scale_y <= scale_y_max_ && !template_found; scale_y += scale_y_step_)
                    {
                        // 1. 调整模板大小
                        cv::Mat resized_template;
                        cv::resize(templ, resized_template, cv::Size(), scale_x, scale_y, cv::INTER_LINEAR);
                        // 2. 检查调整后模板是否仍然适合图像
                        if (resized_template.cols > binary_image.cols || resized_template.rows > binary_image.rows)
                        {
                            continue; // 模板太大，跳过
                        }
                        // 3. 应用掩码，创建当前搜索区域的副本
                        cv::Mat masked_image;
                        binary_image.copyTo(masked_image, mask);
                        // 4. 执行单次模板匹配
                        int result_cols = masked_image.cols - resized_template.cols + 1;
                        int result_rows = masked_image.rows - resized_template.rows + 1;
                        if (result_cols <= 0 || result_rows <= 0)
                            continue;
                        cv::Mat result(result_rows, result_cols, CV_32FC1);
                        cv::matchTemplate(masked_image, resized_template, result, match_method_);
                        bool is_inverse_method = (match_method_ == cv::TM_SQDIFF ||
                                                  match_method_ == cv::TM_SQDIFF_NORMED);
                        // 5. 查找匹配位置 (只找第一个满足阈值的点)
                        cv::Point match_loc;
                        double min_val, max_val;
                        cv::Point min_loc, max_loc;
                        cv::minMaxLoc(result, &min_val, &max_val, &min_loc, &max_loc);
                        cv::Point pt1 = is_inverse_method ? min_loc : max_loc;
                        double match_val = is_inverse_method ? min_val : max_val;
                        // --- 修改：使用当前模板的阈值进行判断 ---
                        if ((is_inverse_method && match_val <= (1.0 - current_template_threshold)) ||
                            (!is_inverse_method && match_val >= current_template_threshold))
                        {
                            // --- 修改结束 ---
                            // 6. 计算匹配框和中心点
                            cv::Point pt2(pt1.x + resized_template.cols, pt1.y + resized_template.rows);
                            cv::Point center = (pt1 + pt2) / 2;
                            // 7. 绘制矩形和标签 (可选：显示缩放信息)
                            cv::rectangle(result_image, pt1, pt2, cv::Scalar(0, 255, 0), 2);
                            std::string label = template_names_[i] +
                                                " (Sx:" + std::to_string(static_cast<int>(scale_x * 100)) + "%" +
                                                ", Sy:" + std::to_string(static_cast<int>(scale_y * 100)) + "%)";
                            cv::putText(result_image, label,
                                        cv::Point(pt1.x, pt1.y - 10),
                                        cv::FONT_HERSHEY_SIMPLEX, 0.5,
                                        cv::Scalar(0, 255, 0), 1);
                            // 8. **关键：更新掩码**
                            // 将此匹配区域“涂黑”，防止后续任何尺度或模板在此区域再次匹配
                            cv::rectangle(mask, pt1, pt2, cv::Scalar(0), -1);
                            // 9. 构造 Detection2D 并发布
                            vision_msgs::Detection2D det;
                            det.header = msg->header;
                            det.bbox.center.x = center.x;
                            det.bbox.center.y = center.y;
                            det.bbox.size_x = pt2.x - pt1.x;
                            det.bbox.size_y = pt2.y - pt1.y;
                            vision_msgs::ObjectHypothesisWithPose hypothesis;
                            hypothesis.id = i;            // 模板索引
                            hypothesis.score = match_val; // 使用匹配值作为置信度
                            // hypothesis.pose.pose.position.x = center.x; // 如果需要，可以填充pose
                            // hypothesis.pose.pose.position.y = center.y;
                            det.results.push_back(hypothesis);
                            detections_msg.detections.push_back(det);
                            // 10. 标记已找到，并跳出内层循环
                            template_found = true;
                            ROS_INFO("Plane %d: Matched '%s' at (%d, %d), scale: (%.2f, %.2f)",
                                     plane_index + 1, template_names_[i].c_str(), center.x, center.y, scale_x, scale_y);
                        }
                    } // end for scale_y
                } // end for scale_x
            } // end for template i
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