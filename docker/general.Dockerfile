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

    
    apt-get install -y \
      ros-${ROS_DISTRO}-joint-state-publisher \
      ros-${ROS_DISTRO}-joint-state-publisher-gui \
      ros-${ROS_DISTRO}-xacro \
      ros-${ROS_DISTRO}-rqt* \
      ros-${ROS_DISTRO}-ros2-control \
      ros-${ROS_DISTRO}-ros2-controllers \
      ros-${ROS_DISTRO}-controller-manager \
      ros-${ROS_DISTRO}-tf-transformations \
      ros-${ROS_DISTRO}-pal-statistics \
      ros-${ROS_DISTRO}-pal-statistics-msgs \
      ros-${ROS_DISTRO}-rmw-cyclonedds-cpp \
      ros-${ROS_DISTRO}-ros-testing \
      ros-${ROS_DISTRO}-moveit-ros \
      ros-${ROS_DISTRO}-moveit-planners \
      ros-${ROS_DISTRO}-moveit-plugins \
      ros-${ROS_DISTRO}-moveit-setup-assistant \
      ros-${ROS_DISTRO}-moveit-configs-utils \
      ros-${ROS_DISTRO}-moveit-task-constructor-core \
      ros-${ROS_DISTRO}-ament-package \
      ros-${ROS_DISTRO}-ament-index-cpp \
      ros-${ROS_DISTRO}-ament-cmake-core \
      ros-${ROS_DISTRO}-ament-index-python \
      ros-${ROS_DISTRO}-tf-transformations \
      ros-${ROS_DISTRO}-realsense2-camera \
      ros-${ROS_DISTRO}-rclcpp-action \
      python3-colcon-common-extensions \
      python3-setuptools \
    && rm -rf /var/lib/apt/lists/*