cmake_minimum_required(VERSION 3.8)
project(movensys_manipulator_moveit_config)

if(NOT CMAKE_C_STANDARD)
  set(CMAKE_C_STANDARD 99)
endif()

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclpy REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(control_msgs REQUIRED)
find_package(trajectory_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_srvs REQUIRED)
find_package(moveit_ros_planning_interface REQUIRED)
find_package(moveit_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_msgs REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
find_package(Eigen3 REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

# MoveIt2 Client Library
add_library(moveit2_client_lib SHARED
  src/moveit2_client.cpp
)
ament_target_dependencies(moveit2_client_lib
  rclcpp
  std_srvs
  moveit_ros_planning_interface
  moveit_msgs
  geometry_msgs
  tf2_ros
  tf2_msgs
  tf2_geometry_msgs
)
target_include_directories(moveit2_client_lib PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
  ${EIGEN3_INCLUDE_DIRS}
)

install(DIRECTORY
  launch
  rviz
  config
  DESTINATION share/${PROJECT_NAME}/
)

install(DIRECTORY include/
  DESTINATION include
)

add_executable(isaacsim_bridge src/isaacsim_bridge.cpp)
ament_target_dependencies(isaacsim_bridge rclcpp rclcpp_action control_msgs trajectory_msgs sensor_msgs std_srvs)

add_executable(gazebo_bridge src/gazebo_bridge.cpp)
ament_target_dependencies(gazebo_bridge rclcpp rclcpp_action control_msgs trajectory_msgs sensor_msgs std_srvs)

add_executable(moveit2_trajectory_cpp src/moveit2_trajectory.cpp)
target_link_libraries(moveit2_trajectory_cpp moveit2_client_lib)
ament_target_dependencies(moveit2_trajectory_cpp
  rclcpp
  moveit_ros_planning_interface
  moveit_msgs
  geometry_msgs
  std_srvs
)

install(TARGETS moveit2_trajectory_cpp
  DESTINATION lib/${PROJECT_NAME}
)

install(TARGETS moveit2_client_lib isaacsim_bridge gazebo_bridge
  EXPORT export_moveit2_client_lib
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION lib/${PROJECT_NAME}
)

ament_export_targets(export_moveit2_client_lib HAS_LIBRARY_TARGET)
ament_export_dependencies(
  rclcpp
  std_srvs
  moveit_ros_planning_interface
  moveit_msgs
  geometry_msgs
  tf2_ros
  tf2_msgs
  tf2_geometry_msgs
  Eigen3
)

ament_python_install_package(movensys_manipulator_moveit_config)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
