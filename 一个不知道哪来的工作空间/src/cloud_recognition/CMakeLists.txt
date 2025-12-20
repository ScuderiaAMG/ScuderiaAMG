cmake_minimum_required(VERSION 3.0.2)
project(cloud_recognition)

# 1. 查找依赖包
find_package(catkin REQUIRED COMPONENTS
  roscpp
  sensor_msgs
  pcl_ros
  pcl_conversions
  tf2
  tf2_ros
  tf2_sensor_msgs
  tf2_geometry_msgs
  cv_bridge
  image_transport
  vision_msgs
  std_msgs
  geometry_msgs
  message_generation
  # ✅ 添加 jsk_recognition_msgs
  jsk_recognition_msgs
  tf2_eigen
)

# 显式查找 PCL, OpenCV, yaml-cpp, Boost
find_package(PCL REQUIRED COMPONENTS common filters segmentation)
find_package(OpenCV REQUIRED)
find_package(yaml-cpp REQUIRED)
find_package(Boost REQUIRED)

# 2. 添加自定义消息文件（如果有的话）
add_message_files(
  FILES
  Detection3DWithID.msg
  Detection3DWithIDArray.msg
)

# 3. 生成消息
generate_messages(
  DEPENDENCIES
  std_msgs
  geometry_msgs
)

# 4. catkin_package：声明对外接口
catkin_package(
  INCLUDE_DIRS include
  CATKIN_DEPENDS 
    roscpp 
    sensor_msgs 
    pcl_ros 
    pcl_conversions
    cv_bridge
    tf2_ros
    tf2_sensor_msgs
    tf2_geometry_msgs
    image_transport
    vision_msgs
    std_msgs        
    geometry_msgs   
    message_runtime
    # ✅ 添加 jsk_recognition_msgs 到 CATKIN_DEPENDS
    jsk_recognition_msgs
    tf2_eigen
  DEPENDS 
    PCL
    YAML_CPP
    OpenCV
    Boost
)

# 5. 包含目录
include_directories(
  ${catkin_INCLUDE_DIRS}
  ${PCL_INCLUDE_DIRS}
  ${OpenCV_INCLUDE_DIRS}
  ${PROJECT_SOURCE_DIR}/include/cloud_recognition
)

# 链接库目录
link_directories(${PCL_LIBRARY_DIRS})
add_definitions(${PCL_DEFINITIONS})

# 6. 添加可执行文件
add_executable(plane_extractor src/plane_extractor.cpp)
add_executable(point_projector src/point_projector.cpp)
add_executable(template_match src/template_match.cpp)
add_executable(point_converter src/point_converter.cpp)
add_executable(goal_generater src/goal_generater.cpp)
add_executable(flag_recognition src/flag_recognition.cpp)


# 7. 链接库
target_link_libraries(plane_extractor 
  ${catkin_LIBRARIES} 
  ${PCL_LIBRARIES}
)

target_link_libraries(point_projector
  ${catkin_LIBRARIES}
  ${PCL_LIBRARIES}
  ${OpenCV_LIBRARIES}
  ${YAML_CPP_LIBRARIES}
  # ✅ 确保链接 jsk_recognition_msgs（通常包含在 ${catkin_LIBRARIES} 中，但显式列出更安全）
)

target_link_libraries(template_match
  ${catkin_LIBRARIES}
  ${OpenCV_LIBRARIES}
  ${Boost_LIBRARIES}
)

target_link_libraries(point_converter
  ${catkin_LIBRARIES}
)

target_link_libraries(goal_generater
  ${catkin_LIBRARIES}
)

target_link_libraries(flag_recognition
  ${catkin_LIBRARIES}
  ${PCL_LIBRARIES}
)



