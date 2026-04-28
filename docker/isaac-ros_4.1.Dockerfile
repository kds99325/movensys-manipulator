ARG ARCH=amd64
FROM nvcr.io/nvidia/isaac/ros:isaac_ros_6a0af6f39da3232fdca6b60f4b174e8a-${ARCH}

USER root
WORKDIR /workspaces

RUN rm -f /etc/apt/sources.list.d/yarn.list || true

RUN sed -i -E 's|http://(archive\|security)\.ubuntu\.com/ubuntu/|https://\1.ubuntu.com/ubuntu/|g' \
      /etc/apt/sources.list.d/ubuntu.sources

RUN apt-get update && \
    apt-get install -y \
      ros-jazzy-ament-package \
      ros-jazzy-ament-index-cpp \
      ros-jazzy-ament-cmake-core \
      ros-jazzy-ament-index-python \
      ros-jazzy-pal-statistics \
      ros-jazzy-pal-statistics-msgs \
      ros-jazzy-rmw-cyclonedds-cpp \
      ros-jazzy-tf-transformations \
      ros-jazzy-realsense2-camera \
      ros-jazzy-isaac-ros-apriltag \
      ros-jazzy-isaac-ros-realsense \
      ros-jazzy-isaac-ros-depth-image-proc \
      ros-jazzy-isaac-ros-image-proc \
      python3-colcon-common-extensions \
      python3-setuptools \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install -y \
      ros-jazzy-isaac-ros-cumotion-examples \
      ros-jazzy-isaac-manipulator-ros-python-utils \
      ros-jazzy-isaac-ros-nvblox \
    && rm -rf /var/lib/apt/lists/*

COPY fix_cumotion_planner.sh /tmp/fix_cumotion_planner.sh
RUN chmod +x /tmp/fix_cumotion_planner.sh && /tmp/fix_cumotion_planner.sh && rm /tmp/fix_cumotion_planner.sh

COPY fix_robot_segmenter.sh /tmp/fix_robot_segmenter.sh
RUN chmod +x /tmp/fix_robot_segmenter.sh && /tmp/fix_robot_segmenter.sh && rm /tmp/fix_robot_segmenter.sh

RUN apt-get update && apt-get install -y \
        ros-jazzy-rclcpp-action \
        ros-jazzy-moveit-ros \
        ros-jazzy-moveit-planners \
        ros-jazzy-moveit-plugins \
        ros-jazzy-moveit-setup-assistant \
        ros-jazzy-moveit-configs-utils \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    if [ "$ROS_DISTRO" = "jazzy" ]; then \
      apt-get install -y \
        ros-${ROS_DISTRO}-ros-gz-sim \
        ros-${ROS_DISTRO}-gz-ros2-control \
        ros-${ROS_DISTRO}-ros-gz-bridge \
        ros-${ROS_DISTRO}-gz-sim-vendor \
        ros-${ROS_DISTRO}-gz-transport-vendor; \
    elif [ "$ROS_DISTRO" = "humble" ]; then \
      apt-get install -y \
        ros-${ROS_DISTRO}-ros-ign-gazebo \
        ros-${ROS_DISTRO}-ign-ros2-control \
        ros-${ROS_DISTRO}-ros-ign-bridge; \
    fi && \
    rm -rf /var/lib/apt/lists/*