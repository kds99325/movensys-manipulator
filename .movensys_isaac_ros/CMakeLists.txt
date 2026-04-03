cmake_minimum_required(VERSION 3.8)
project(movensys_isaac_ros)

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
find_package(movensys_moveit_config REQUIRED)
include_directories(${movensys_moveit_config_DIR}/../../../include)
link_directories(${movensys_moveit_config_DIR}/../../../lib)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

install(DIRECTORY
  launch
  src
  scripts
  config
  rviz
  DESTINATION share/${PROJECT_NAME}/
)

add_executable(stage1_cumotion_cpp src/stage1_cumotion.cpp)
ament_target_dependencies(stage1_cumotion_cpp rclcpp movensys_moveit_config)
target_link_libraries(stage1_cumotion_cpp moveit2_client_lib)

add_executable(stage2_pick_n_place_cpp src/stage2_pick_n_place.cpp)
ament_target_dependencies(stage2_pick_n_place_cpp rclcpp movensys_moveit_config)
target_link_libraries(stage2_pick_n_place_cpp moveit2_client_lib)

add_executable(stage3_pose_to_pose_cpp src/stage3_pose_to_pose.cpp)
ament_target_dependencies(stage3_pose_to_pose_cpp rclcpp movensys_moveit_config)
target_link_libraries(stage3_pose_to_pose_cpp moveit2_client_lib)

install(TARGETS
  stage1_cumotion_cpp
  stage2_pick_n_place_cpp
  stage3_pose_to_pose_cpp
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION lib/${PROJECT_NAME}
)

install(PROGRAMS
    scripts/camera_transform_tuning.py
    DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()