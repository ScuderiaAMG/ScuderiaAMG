cmake_minimum_required(VERSION 3.0.2)
project(drone_manager)

find_package(catkin REQUIRED COMPONENTS
  roscpp
  fly_ctl
  geometry_msgs
  std_msgs
  nav_msgs
  mavros_msgs
)

catkin_package()

include_directories(
  ${catkin_INCLUDE_DIRS}
)

add_executable(cruise_node src/drone_main_node.cpp)

target_link_libraries(cruise_node
  ${catkin_LIBRARIES}
)

add_dependencies(cruise_node
  ${${PROJECT_NAME}_EXPORTED_TARGETS}
  ${catkin_EXPORTED_TARGETS}
)
