# CMakeLists.txt
cmake_minimum_required(VERSION 3.0.2)
project(ring_detector)

# 设置C++标准
add_compile_options(-std=c++14)

# 查找所需的catkin包
find_package(catkin REQUIRED COMPONENTS
  roscpp
  sensor_msgs
  pcl_ros
  pcl_conversions
  geometry_msgs
  visualization_msgs
  tf2_ros
  tf2_geometry_msgs
  tf2_sensor_msgs
  nav_msgs
  std_srvs
  std_msgs
)

# 查找PCL
find_package(PCL REQUIRED)

# 查找Eigen3
find_package(Eigen3 REQUIRED)

# 查找Boost（用于文件系统操作）
find_package(Boost REQUIRED COMPONENTS filesystem)

# 声明catkin包
catkin_package(
  INCLUDE_DIRS include
  CATKIN_DEPENDS
    roscpp
    sensor_msgs
    pcl_ros
    pcl_conversions
    geometry_msgs
    visualization_msgs
    tf2_ros
    tf2_geometry_msgs
    tf2_sensor_msgs
    nav_msgs
    std_srvs
    std_msgs
)

# 包含目录
include_directories(
  include
  ${catkin_INCLUDE_DIRS}
  ${PCL_INCLUDE_DIRS}
  ${EIGEN3_INCLUDE_DIRS}
)

# 链接目录
link_directories(${PCL_LIBRARY_DIRS})

# 定义编译选项
add_definitions(${PCL_DEFINITIONS})

# 地图累积器节点
add_executable(map_accumulator_node
  src/map_accumulator_node.cpp
)

target_link_libraries(map_accumulator_node
  ${catkin_LIBRARIES}
  ${PCL_LIBRARIES}
  ${Boost_LIBRARIES}
)

add_dependencies(map_accumulator_node ${${PROJECT_NAME}_EXPORTED_TARGETS} ${catkin_EXPORTED_TARGETS})
