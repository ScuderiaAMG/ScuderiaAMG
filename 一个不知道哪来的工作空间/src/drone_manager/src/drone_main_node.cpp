#include "fly_ctl/motion_control.h"

// --- IGNORE --- //
using namespace std;
using namespace fly_ctl;

class DroneManager {
    public:
        // 定义状态机状态
        enum State {
            INIT,
            TAKEOFF,
            CRUISE,
            LAND,
            FINISH
        };

        struct CheckPoint{
            geometry_msgs::Point position;
            float yaw;
        };

        DroneManager(ros::NodeHandle& nh) 
            : motion_controller_(nh) 
        {
            ROS_INFO("Initializing DroneManager...");
            nh.param("control_rate", control_rate_, 20.0); // 从参数服务器读取
            nh.param("err_max", err_max_, 0.2f); // 从参数服务器读取
            nh.param("num_checkpoints", num_checkpoints_, 0); // 从参数服务器读取
            // 读取检查点
            for (int i = 0; i < num_checkpoints_; ++i) {
                CheckPoint cp;
                nh.getParam("checkpoints/" + to_string(i) + "/x", cp.position.x);
                nh.getParam("checkpoints/" + to_string(i) + "/y", cp.position.y);
                nh.getParam("checkpoints/" + to_string(i) + "/z", cp.position.z);
                nh.getParam("checkpoints/" + to_string(i) + "/yaw", cp.yaw);
                checkpoints_.push_back(cp);
            }
            // 打印参数:
            ROS_INFO("Control Rate: %.2f Hz", control_rate_);
            ROS_INFO("Error Max: %.2f m", err_max_);
            ROS_INFO("Number of Checkpoints: %d", num_checkpoints_);
            for (const auto& cp : checkpoints_) {
                ROS_INFO("Checkpoint - Position: (%.2f, %.2f, %.2f), Yaw: %.2f",
                         cp.position.x, cp.position.y, cp.position.z, cp.yaw);
            }

            motion_controller_.initialize();
        }

        void run() {
            ROS_INFO("Starting Drone Manager Node...");
            ros::Rate rate(control_rate_); // 控制循环频率
            while (ros::ok()) {
                if (tmp_mission_state_ != mission_state_) {
                    tmp_mission_state_ = mission_state_;
                    ROS_INFO("Mission state changed to: %d", mission_state_);
                }

                // ROS_INFO只能打印char*类型的字符串, 所以需要转换
                ROS_INFO("Current Mission State: %s", stateToString(mission_state_).c_str());
                switch (mission_state_) {
                    case INIT: {
                        if (motion_controller_.initialize()) {
                            ROS_INFO("MotionController initialized successfully.");
                            changeCurrentState(DroneManager::INIT);
                        } else {
                            ROS_ERROR("MotionController failed to initialize.");
                            changeCurrentState(DroneManager::FINISH);
                            exit(0);
                        }
                        
                        int choice;
                        cout << "Start Drone Manager Node or Let off fireworks (1 or 0 ?)" << endl;
                        cin >> choice;
                        if (choice != 1) {
                            cout << "Exiting Drone Manager Node." << endl;
                            exit (0);
                        } else {
                            cout << "Starting Drone Manager Node." << endl;
                        }

                        if (motion_controller_.setOffboardMode(fly_height_)) {
                            ROS_INFO("Offboard mode set and takeoff initiated.");
                            changeCurrentState(TAKEOFF);
                        }
                        ROS_INFO("Haha, reached the end of INIT state.");
                        break;
                    }
                    
                    // 带悬停的起飞
                    case TAKEOFF:
                        // 前面的起飞逻辑已经放在setOffboardMode里了
                        if (motion_controller_.hover(fly_height_, motion_controller_.getCurrentYaw(), 3.0)) {
                            ROS_INFO("Takeoff and hover successful.");
                            changeCurrentState(CRUISE);
                        }
                        break;

                    case CRUISE:
                        if (motion_controller_.moveToXYZ(
                                checkpoints_[current_checkpoint_index_].position.x,
                                checkpoints_[current_checkpoint_index_].position.y,
                                fly_height_,
                                checkpoints_[current_checkpoint_index_].yaw)) {
                            ROS_INFO("Reached checkpoint %d.", current_checkpoint_index_);
                            current_checkpoint_index_++;
                        }
                        if (current_checkpoint_index_ >= checkpoints_.size()) {
                            ROS_INFO("All checkpoints reached. Transitioning to LAND state.");
                            changeCurrentState(LAND);
                        }
                        break;

                    case LAND:
                        // 降落状态, 在当前位置降落
                        if (motion_controller_.hover(5.0, 0.10, 3.0)) {
                            ROS_INFO("Landing successful.");
                            changeCurrentState(FINISH);
                        }
                        break;
                    case FINISH:
                        // 结束状态, 可以添加结束逻辑
                        ROS_INFO("Mission finished.");
                        exit(0);
                        return;
                    default:
                        ROS_WARN("Unknown mission state! exiting!");
                        exit(0);
                        break;
                }


                // 状态机最后发布setpoint指令:
                ros::spinOnce();
                motion_controller_.publishSetpoint(); // 发布当前的setpoint
                rate.sleep();
            }
        }

    private:
        MotionController motion_controller_; // 这里声明我的成员变量
        double control_rate_ = 20.0; // 默认值
        float err_max_ = 0.2; // 最大误差阈值
        int num_checkpoints_ = 0; // 检查点数量
        float fly_height_ = 1.2; // 飞行高度
        State tmp_mission_state_ = INIT; // 临时任务状态
        State mission_state_ = INIT; // 任务状态
        std::vector<CheckPoint> checkpoints_; // 检查点列表
        int current_checkpoint_index_ = 0;
        void changeCurrentState(State new_state) {
            mission_state_ = new_state;
        }

        string stateToString(State state) {
            switch (state) {
                case INIT: return "INIT";
                case TAKEOFF: return "TAKEOFF";
                case CRUISE: return "CRUISE";
                case LAND: return "LAND";
                case FINISH: return "FINISH";
                default: return "UNKNOWN";
            }
        }
};

int main(int argc, char** argv) {
    ros::init(argc, argv, "drone_main_node");
    ros::NodeHandle nh("~");
    DroneManager manager(nh);
    manager.run();
    exit(0);
    return 0;
}

