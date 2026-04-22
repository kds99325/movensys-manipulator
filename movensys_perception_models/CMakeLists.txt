cmake_minimum_required(VERSION 3.8)
project(movensys_perception_models)

find_package(ament_cmake REQUIRED)

install(DIRECTORY
  models
  DESTINATION share/${PROJECT_NAME}/
)

ament_package()
