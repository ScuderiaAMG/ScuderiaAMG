//第一个版本：kimi 1.5
#include <ros/ros.h>
#include <sensor_msgs/LaserScan.h>
#include <geometry_msgs/Twist.h>
#include <nav_msgs/Odometry.h>
#include <slam_gmapping/slam_gmapping.h> // 假设使用gmapping进行SLAM

// 全局变量
ros::Publisher vel_pub;
geometry_msgs::Twist vel_cmd;

// SLAM相关变量
bool is_slam_initialized = false;
nav_msgs::Odometry odom_data;

// 激光雷达回调函数
void LidarCallback(const sensor_msgs::LaserScan::ConstPtr& msg) {
    static int nCount = 0;

    // 获取激光雷达中间点的距离
    int nMid = msg->ranges.size() / 2;
    float fMidDist = msg->ranges[nMid];
    ROS_INFO("前方测距 ranges[%d] = %f 米", nMid, fMidDist);

    // 避障逻辑
    if (fMidDist < 1.5f) { // 如果前方距离小于1.5米，执行避障
        vel_cmd.angular.z = 0.3; // 旋转避障
        nCount = 50; // 设置计数器，延时避障
    }
    else { // 否则正常前进
        vel_cmd.linear.x = 0.05; // 前进速度
    }

    // 发布速度指令
    if (nCount > 0) {
        nCount--;
    }
    else {
        vel_pub.publish(vel_cmd);
    }
}

// SLAM初始化函数
void initializeSLAM() {
    ros::NodeHandle nh;
    ros::Subscriber slam_sub = nh.subscribe("/scan", 10, LidarCallback);
    ros::Publisher map_pub = nh.advertise<nav_msgs::OccupancyGrid>("/map", 10);

    // 启动SLAM节点
    slam_gmapping::SlamGmapping slam;
    if (!slam.initialize()) {
        ROS_ERROR("SLAM initialization failed!");
        return;
    }

    is_slam_initialized = true;
    ROS_INFO("SLAM initialized successfully!");
}

// 主函数
int main(int argc, char** argv) {
    setlocale(LC_ALL, "");
    ros::init(argc, argv, "drone_navigation");

    ros::NodeHandle nh;
    vel_pub = nh.advertise<geometry_msgs::Twist>("/cmd_vel", 10);

    // 初始化SLAM
    initializeSLAM();

    // 订阅激光雷达数据
    ros::Subscriber lidar_sub = nh.subscribe("/scan", 10, LidarCallback);

    // 主循环
    ros::Rate loop_rate(10);
    while (ros::ok()) {
        // 发布速度指令
        vel_pub.publish(vel_cmd);

        // 处理ROS消息
        ros::spinOnce();

        // 控制循环频率
        loop_rate.sleep();
    }

    return 0;
}

/************************************************************************************************************************************************************************/
//第二个版本：deepseek R1

//需要使用：<depend>gmapping</depend>
//<depend>tf2_geometry_msgs< / depend>
//<depend>sensor_msgs< / depend>等ros包

#include <ros/ros.h>
#include <sensor_msgs/LaserScan.h>
#include <nav_msgs/OccupancyGrid.h>
#include <geometry_msgs/PoseStamped.h>
#include <tf2_ros/transform_listener.h>
#include <memory>

class SlamProcessor {
public:
    explicit SlamProcessor(ros::NodeHandle& nh)
        : tf_listener_(tf_buffer_)
    {
        // 参数初始化
        nh.param("laser_topic", laser_topic_, std::string("/scan"));
        nh.param("map_frame", map_frame_, std::string("map"));
        nh.param("odom_frame", odom_frame_, std::string("odom"));

        // 激光雷达数据订阅
        laser_sub_ = nh.subscribe(laser_topic_, 1, &SlamProcessor::laserCallback, this);

        // 地图数据发布
        map_pub_ = nh.advertise<nav_msgs::OccupancyGrid>("/slam_map", 1);

        // SLAM初始化逻辑
        initSlamSystem();
    }

    // 封装SLAM处理主循环
    void update() {
        if (!laser_data_ || !tfAvailable()) return;

        // 执行SLAM计算
        runSlamUpdate();

        // 发布最新地图
        publishMap();
    }

    // 接口：获取当前地图
    nav_msgs::OccupancyGrid getMap() const {
        return current_map_;
    }

    // 接口：获取精确定位姿态
    bool getRobotPose(geometry_msgs::PoseStamped& pose) {
        return getFramePose(map_frame_, pose);
    }

private:
    void initSlamSystem() {
        // 初始化SLAM算法参数
        // 此处可集成Gmapping、Hector等SLAM实现
        ROS_INFO("Initializing SLAM system...");
        current_map_.header.frame_id = map_frame_;
        // 更多初始化代码...
    }

    void laserCallback(const sensor_msgs::LaserScan::ConstPtr& msg) {
        std::lock_guard<std::mutex> lock(data_mutex_);
        laser_data_ = msg;
    }

    bool tfAvailable() {
        return tf_buffer_.canTransform(map_frame_, odom_frame_, ros::Time(0));
    }

    bool getFramePose(const std::string& target_frame, geometry_msgs::PoseStamped& pose) {
        try {
            geometry_msgs::TransformStamped transform =
                tf_buffer_.lookupTransform(target_frame, "base_link", ros::Time(0));
            pose.header.stamp = ros::Time::now();
            pose.header.frame_id = target_frame;
            pose.pose.position.x = transform.transform.translation.x;
            pose.pose.position.y = transform.transform.translation.y;
            pose.pose.position.z = transform.transform.translation.z;
            pose.pose.orientation = transform.transform.rotation;
            return true;
        }
        catch (tf2::TransformException& ex) {
            ROS_WARN("TF lookup failure: %s", ex.what());
            return false;
        }
    }

    void runSlamUpdate() {
        // 此处实现具体的SLAM算法逻辑
        // 示例伪代码：
        // 1. 获取激光数据
        // 2. 获取里程计数据
        // 3. 执行扫描匹配
        // 4. 更新地图数据

        std::lock_guard<std::mutex> lock(data_mutex_);
        // 实际SLAM计算代码...

        // 示例：简单地图更新（实际应替换为SLAM算法）
        static int map_update_count = 0;
        current_map_.header.stamp = ros::Time::now();
        current_map_.info.resolution = 0.05;
        current_map_.info.width = 100;
        current_map_.info.height = 100;
        current_map_.data.resize(100 * 100, -1);
        map_update_count++;
    }

    void publishMap() {
        if (+()) return;
        map_pub_.publish(current_map_);
    }

    // SLAM相关数据
    ros::Subscriber laser_sub_;
    ros::Publisher map_pub_;
    tf2_ros::Buffer tf_buffer_;
    tf2_ros::TransformListener tf_listener_;

    // 线程安全数据访问
    std::mutex data_mutex_;
    sensor_msgs::LaserScan::ConstPtr laser_data_;
    nav_msgs::OccupancyGrid current_map_;

    // 配置参数
    std::string laser_topic_;
    std::string map_frame_;
    std::string odom_frame_;
};

// 飞行控制主类
class FlightController {
public:
    FlightController(ros::NodeHandle& nh)
        : slam_processor_(nh)
    {
        // 初始化其他飞行控制组件...
    }

    void mainLoop() {
        ros::Rate rate(10);
        while (ros::ok()) {
            // SLAM更新
            slam_processor_.update();

            // 获取定位信息
            geometry_msgs::PoseStamped current_pose;
            if (slam_processor_.getRobotPose(current_pose)) {
                // 路径规划与避障逻辑
                executeNavigation(current_pose);
            }

            rate.sleep();
        }
    }

private:
    void executeNavigation(const geometry_msgs::PoseStamped& pose) {
        // 实现导航避障逻辑
        // 1. 获取当前地图
        // 2. 路径规划
        // 3. 运动控制

        nav_msgs::OccupancyGrid current_map = slam_processor_.getMap();
        // 路径规划代码...
    }

    SlamProcessor slam_processor_;
    // 其他控制组件...
};

int main(int argc, char** argv) {
    ros::init(argc, argv, "drone_slam_controller");
    ros::NodeHandle nh("~");

    FlightController controller(nh);
    controller.mainLoop();

    return 0;
}



/***********************************************************************************************************************/
//第三个版本：deepseek-zju

//安装必要依赖sudo apt - get install ros - noetic - slam - gmapping

/*
* 配套的.launch
<launch>
    <!-- 启动SLAM节点 -->
    <include file="$(find gmapping)/launch/slam_gmapping.launch"/>
    
    <!-- 启动导航节点 -->
    <node pkg="your_package" type="navigation_node" name="drone_navigation" output="screen">
        <param name="safe_distance" value="1.2"/>
        <param name="target_threshold" value="0.25"/>
    </node>
</launch> 
*/

#include <ros/ros.h>
#include <sensor_msgs/LaserScan.h>
#include <geometry_msgs/Twist.h>
#include <nav_msgs/Odometry.h>
#include <nav_msgs/GetMap.h>

class DroneNavigation {
public:
    DroneNavigation() : nh_("~") {
        // 参数初始化
        nh_.param("safe_distance", safe_distance_, 1.5f);
        nh_.param("target_threshold", target_threshold_, 0.3f);

        // 订阅者初始化
        laser_sub_ = nh_.subscribe("/scan", 1, &DroneNavigation::laserCallback, this);
        odom_sub_ = nh_.subscribe("/odom", 1, &DroneNavigation::odomCallback, this);

        // 发布者初始化
        cmd_pub_ = nh_.advertise<geometry_msgs::Twist>("/cmd_vel", 10);

        // SLAM服务初始化
        slam_client_ = nh_.serviceClient<nav_msgs::GetMap>("/dynamic_map");
    }

    void mainLoop() {
        ros::Rate rate(10);
        while (ros::ok()) {
            this->slamMapping();
            this->navigateThroughDoor();
            rate.sleep();
            ros::spinOnce();
        }
    }

private:
    // SLAM地图处理
    void slamMapping() {
        nav_msgs::GetMap srv;
        if (slam_client_.call(srv)) {
            current_map_ = srv.response.map;
            // 此处添加地图处理逻辑
        }
    }

    // 激光雷达回调
    void laserCallback(const sensor_msgs::LaserScan::ConstPtr& scan) {
        latest_scan_ = *scan;
        processObstacleData(scan);
    }

    // 里程计回调
    void odomCallback(const nav_msgs::Odometry::ConstPtr& odom) {
        current_pose_ = odom->pose.pose;
    }

    // 障碍物处理核心逻辑
    void processObstacleData(const sensor_msgs::LaserScan::ConstPtr& scan) {
        float min_distance = *std::min_element(scan->ranges.begin(), scan->ranges.end());

        if (min_distance < safe_distance_) {
            executeAvoidanceManeuver();
        }
        else {
            maintainCourse();
        }
    }

    // 穿门导航逻辑
    void navigateThroughDoor() {
        static bool door_detected = false;

        // 门框检测（示例逻辑）
        if (detectDoorFrame(latest_scan_)) {
            door_detected = true;
            adjustApproachAngle();
        }

        if (door_detected && checkClearance()) {
            executeDoorTraversal();
        }
    }

    // 避障机动
    void executeAvoidanceManeuver() {
        geometry_msgs::Twist cmd;
        cmd.angular.z = 0.5;  // 顺时针旋转
        cmd_pub_.publish(cmd);
    }

    // 保持航线
    void maintainCourse() {
        geometry_msgs::Twist cmd;
        cmd.linear.x = 0.5;   // 前进速度
        cmd_pub_.publish(cmd);
    }

    // 门框检测函数
    bool detectDoorFrame(const sensor_msgs::LaserScan& scan) {
        // 简化的门框检测逻辑
        const int mid_index = scan.ranges.size() / 2;
        return (scan.ranges[mid_index - 10] < 1.0 &&
            scan.ranges[mid_index + 10] < 1.0 &&
            scan.ranges[mid_index] > 2.0);
    }

    // 其他成员函数...

    // 成员变量
    ros::NodeHandle nh_;
    ros::Subscriber laser_sub_, odom_sub_;
    ros::Publisher cmd_pub_;
    ros::ServiceClient slam_client_;

    sensor_msgs::LaserScan latest_scan_;
    geometry_msgs::Pose current_pose_;
    nav_msgs::OccupancyGrid current_map_;

    float safe_distance_;
    float target_threshold_;
};

int main(int argc, char** argv) {
    ros::init(argc, argv, "drone_navigation_node");
    DroneNavigation drone;
    drone.mainLoop();
    return 0;
}

//