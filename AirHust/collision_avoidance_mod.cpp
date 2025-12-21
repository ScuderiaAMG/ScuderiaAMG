void collision_avoidance(float target_x, float target_y) {
    // ... 原有代码 ...

    if (flag_collision_avoidance.data == true) {
        // 计算障碍物相对于无人机的位置
        distance_cx = distance_c * cos(((angle_c) * 3.1415926) / 180);
        distance_cy = distance_c * sin(((angle_c) * 3.1415926) / 180);

        // 六边形避障策略：计算避障速度
        float hexagon_radius = R_outside + distance_c; // 六边形路径的半径
        vel_collision[0] = hexagon_radius * cos(((angle_c + 60) * 3.1415926) / 180); // 60度是六边形的一个内角
        vel_collision[1] = hexagon_radius * sin(((angle_c + 60) * 3.1415926) / 180);

        // 避障速度限幅
        for (int i = 0; i < 2; i++) {
            vel_collision[i] = satfunc(vel_collision[i], vel_collision_max);
        }
    }

    // ... 原有代码 ...
}


// 安全半径和避障参数
float R_outside; // 外部安全半径
float R_inside;  // 内部安全半径

// 正六边形避障参数
float hexagon_radius; // 正六边形路径半径
const float hexagon_angle_increment = 60.0; // 正六边形内角增量（度）






// 避障算法核心函数
void collision_avoidance(float target_x, float target_y) {
    // 根据最小距离判断是否启用避障策略
    if (distance_c >= R_outside) {
        flag_collision_avoidance.data = false;
    } else {
        flag_collision_avoidance.data = true;
    }

    // 计算追踪速度
    vel_track[0] = p_xy * (target_x - pos_drone.pose.position.x);
    vel_track[1] = p_xy * (target_y - pos_drone.pose.position.y);

    // 速度限幅
    for (int i = 0; i < 2; i++) {
        vel_track[i] = satfunc(vel_track[i], vel_track_max);
    }

    vel_collision[0] = 0;
    vel_collision[1] = 0;

    // 避障策略
    if (flag_collision_avoidance.data == true) {
        // 计算障碍物相对于无人机的位置
        distance_cx = distance_c * cos(((angle_c) * 3.1415926) / 180);
        distance_cy = distance_c * sin(((angle_c) * 3.1415926) / 180);

        // 正六边形避障策略：计算避障速度
        hexagon_radius = R_outside + distance_c; // 正六边形路径的半径
        float避障角度 = angle_c + 30.0; // 选择正六边形的一个内角（例如30度）

        // 计算避障速度，考虑正六边形路径
        vel_collision[0] = hexagon_radius * cos((避障角度 * 3.1415926) / 180);
        vel_collision[1] = hexagon_radius * sin((避障角度 * 3.1415926) / 180);

        // 避障速度限幅
        for (int i = 0; i < 2; i++) {
            vel_collision[i] = satfunc(vel_collision[i], vel_collision_max);
        }
    }

    // 计算总速度
    vel_sp_body[0] = vel_track[0] + vel_collision[0];
    vel_sp_body[1] = vel_track[1] + vel_collision[1];

    // 速度限幅
    for (int i = 0; i < 2; i++) {
        vel_sp_body[i] = satfunc(vel_sp_body[i], vel_sp_max);
    }

    // 坐标系旋转，将速度从机体坐标系转换到ENU坐标系
    rotation_yaw(Euler_fcu[2], vel_sp_body, vel_sp_ENU);
}


int main(int argc, char **argv) {
    // 初始化ROS节点
    ros::init(argc, argv, "collision_avoidance");
    ros::NodeHandle nh("~");
    ros::Rate rate(20.0);

    // 订阅和发布
    ros::Subscriber lidar_sub = nh.subscribe<sensor_msgs::LaserScan>("/scan", 1000, lidar_cb);
    ros::Subscriber position_sub = nh.subscribe<geometry_msgs::PoseStamped>("/mavros/local_position/pose", 100, pos_cb);
    ros::Publisher command_pub = nh.advertise<px4_command::command>("/px4/command", 10);

    // 读取参数
    nh.param<float>("target_x", target_x, 3.0);
    nh.param<float>("target_y", target_y, 3.0);
    nh.param<float>("R_outside", R_outside, 2.0);
    nh.param<float>("R_inside", R_inside, 1.0);
    nh.param<float>("p_xy", p_xy, 0.5);
    nh.param<float>("vel_track_max", vel_track_max, 0.5);
    nh.param<float>("vel_collision_max", vel_collision_max, 0.5);
    nh.param<float>("vel_sp_max", vel_sp_max, 1.0);
    nh.param<int>("range_min", range_min, 0);
    nh.param<int>("range_max", range_max, 359);
    nh.getParam("fly_height", fly_height);

    // 打印参数
    printf_param();

    // 检查参数
    int check_flag;
    cout << "Please check the parameter and setting, 1 for go on, else for quit: " << endl;
    cin >> check_flag;
    if (check_flag != 1) return -1;

    // 检查是否启动
    int start_flag;
    cout << "Whether choose to Start mission? 1 for start, 0 for quit" << endl;
    cin >> start_flag;
    if (start_flag != 1) return -1;

    // 初始化
    vel_track[0] = 0;
    vel_track[1] = 0;
    vel_collision[0] = 0;
    vel_collision[1] = 0;
    vel_sp_body[0] = 0;
    vel_sp_body[1] = 0;
    vel_sp_ENU[0] = 0;
    vel_sp_ENU[1] = 0;
    flag_land = 0;

    int comid = 1;
    while (ros::ok()) {
        ros::spinOnce();
        collision_avoidance(target_x, target_y);

        Command_now.command = Move_ENU;
        Command_now.comid = comid;
        comid++;
        Command_now.sub_mode = 2;
        Command_now.vel_sp[0] = vel_sp_ENU[0];
        Command_now.vel_sp[1] = vel_sp_ENU[1];
        Command_now.pos_sp[2] = fly_height;
        Command_now.yaw_sp = 0;

        float abs_distance = sqrt((pos_drone.pose.position.x - target_x) * (pos_drone.pose.position.x - target_x) + (pos_drone.pose.position.y - target_y) * (pos_drone.pose.position.y - target_y));
        if (abs_distance < 0.3 || flag_land == 1) {
            Command_now.command = Land;
            flag_land = 1;
        }
        if (flag_land == 1) Command_now.command = Land;
        command_pub.publish(Command_now);

        printf();
        rate.sleep();
    }
    return 0;
}















// 安全半径和避障参数
float R_outside; // 外部安全半径
float R_inside;  // 内部安全半径

// 正六边形避障参数
float hexagon_side_length; // 正六边形边长





//主函数
int main(int argc, char **argv) {
    // 初始化ROS节点
    ros::init(argc, argv, "collision_avoidance");
    ros::NodeHandle nh("~");
    ros::Rate rate(20.0);

    // 订阅和发布
    ros::Subscriber lidar_sub = nh.subscribe<sensor_msgs::LaserScan>("/scan", 1000, lidar_cb);
    ros::Subscriber position_sub = nh.subscribe<geometry_msgs::PoseStamped>("/mavros/local_position/pose", 100, pos_cb);
    ros::Publisher command_pub = nh.advertise<px4_command::command>("/px4/command", 10);

    // 读取参数
    nh.param<float>("target_x", target_x, 3.0);
    nh.param<float>("target_y", target_y, 3.0);
    nh.param<float>("R_outside", R_outside, 2.0);
    nh.param<float>("R_inside", R_inside, 1.0);
    nh.param<float>("p_xy", p_xy, 0.5);
    nh.param<float>("vel_track_max", vel_track_max, 0.5);
    nh.param<float>("hexagon_side_length", hexagon_side_length, 2.0); // 读取正六边形边长参数
    nh.param<float>("vel_collision_max", vel_collision_max, 0.5);
    nh.param<float>("vel_sp_max", vel_sp_max, 1.0);
    nh.param<int>("range_min", range_min, 0);
    nh.param<int>("range_max", range_max, 359);
    nh.getParam("fly_height", fly_height);

    // 打印参数
    printf_param();

    // 检查参数
    int check_flag;
    cout << "Please check the parameter and setting, 1 for go on, else for quit: " << endl;
    cin >> check_flag;
    if (check_flag != 1) return -1;

    // 检查是否启动
    int start_flag;
    cout << "Whether choose to Start mission? 1 for start, 0 for quit" << endl;
    cin >> start_flag;
    if (start_flag != 1) return -1;

    // 初始化
    vel_track[0] = 0;
    vel_track[1] = 0;
    vel_collision[0] = 0;
    vel_collision[1] = 0;
    vel_sp_body[0] = 0;
    vel_sp_body[1] = 0;
    vel_sp_ENU[0] = 0;
    vel_sp_ENU[1] = 0;
    flag_land = 0;

    int comid = 1;
    while (ros::ok()) {
        ros::spinOnce();
        collision_avoidance(target_x, target_y);

        Command_now.command = Move_ENU;
        Command_now.comid = comid;
        comid++;
        Command_now.sub_mode = 2;
        Command_now.vel_sp[0] = vel_sp_ENU[0];
        Command_now.vel_sp[1] = vel_sp_ENU[1];
        Command_now.pos_sp[2] = fly_height;
        Command_now.yaw_sp = 0;

        float abs_distance = sqrt((pos_drone.pose.position.x - target_x) * (pos_drone.pose.position.x - target_x) + (pos_drone.pose.position.y - target_y) * (pos_drone.pose.position.y - target_y));
        if (abs_distance < 0.3 || flag_land == 1) {
            Command_now.command = Land;
            flag_land = 1;
        }
        if (flag_land == 1) Command_now.command = Land;
        command_pub.publish(Command_now);

        printf();
        rate.sleep();
    }
    return 0;
}










// 避障算法核心函数
void collision_avoidance(float target_x, float target_y) {
    // 根据最小距离判断是否启用避障策略
    if (distance_c >= R_outside) {
        flag_collision_avoidance.data = false;
    } else {
        flag_collision_avoidance.data = true;
    }

    // 计算追踪速度
    vel_track[0] = p_xy * (target_x - pos_drone.pose.position.x);
    vel_track[1] = p_xy * (target_y - pos_drone.pose.position.y);

    // 速度限幅
    for (int i = 0; i < 2; i++) {
        vel_track[i] = satfunc(vel_track[i], vel_track_max);
    }

    vel_collision[0] = 0;
    vel_collision[1] = 0;

    // 避障策略
    if (flag_collision_avoidance.data == true) {
        // 计算障碍物相对于无人机的位置
        distance_cx = distance_c * cos(((angle_c) * 3.1415926) / 180);
        distance_cy = distance_c * sin(((angle_c) * 3.1415926) / 180);

        // 正六边形避障策略：计算避障速度
        float angle_increment = 60.0 * 3.1415926 / 180.0; // 将角度转换为弧度
        float avoidance_angle = angle_c * 3.1415926 / 180.0 + angle_increment; // 计算避障角度

        // 计算避障速度，考虑正六边形路径
        vel_collision[0] = hexagon_side_length * cos(avoidance_angle);
        vel_collision[1] = hexagon_side_length * sin(avoidance_angle);

        // 避障速度限幅
        for (int i = 0; i < 2; i++) {
            vel_collision[i] = satfunc(vel_collision[i], vel_collision_max);
        }
    }

    // 计算总速度
    vel_sp_body[0] = vel_track[0] + vel_collision[0];
    vel_sp_body[1] = vel_track[1] + vel_collision[1];

    // 速度限幅
    for (int i = 0; i < 2; i++) {
        vel_sp_body[i] = satfunc(vel_sp_body[i], vel_sp_max);
    }

    // 坐标系旋转，将速度从机体坐标系转换到ENU坐标系
    rotation_yaw(Euler_fcu[2], vel_sp_body, vel_sp_ENU);
}