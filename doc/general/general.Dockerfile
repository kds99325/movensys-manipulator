ARG ROS_DISTRO
FROM osrf/ros:${ROS_DISTRO}-desktop
ARG ROS_DISTRO
USER root
WORKDIR /workspaces

RUN sed -i 's|http://security.ubuntu.com/ubuntu|http://archive.ubuntu.com/ubuntu|g' /etc/apt/sources.list && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean && \
    apt-get update

RUN apt-get update && \
    apt-get install -y \
      ros-${ROS_DISTRO}-ament-package \
      ros-${ROS_DISTRO}-ament-index-cpp \
      ros-${ROS_DISTRO}-ament-cmake-core \
      ros-${ROS_DISTRO}-ament-index-python \
      ros-${ROS_DISTRO}-pal-statistics \
      ros-${ROS_DISTRO}-pal-statistics-msgs \
      ros-${ROS_DISTRO}-rmw-cyclonedds-cpp \
      ros-${ROS_DISTRO}-tf-transformations \
      ros-${ROS_DISTRO}-realsense2-camera \
      python3-colcon-common-extensions \
      python3-setuptools \
      ros-${ROS_DISTRO}-rclcpp-action \
      ros-${ROS_DISTRO}-moveit-ros \
      ros-${ROS_DISTRO}-moveit-planners \
      ros-${ROS_DISTRO}-moveit-plugins \
      ros-${ROS_DISTRO}-moveit-setup-assistant \
      ros-${ROS_DISTRO}-moveit-configs-utils \
    && rm -rf /var/lib/apt/lists/*