ARG ROS_DISTRO
FROM ros:${ROS_DISTRO}-ros-base
ARG ROS_DISTRO
USER root
WORKDIR /workspaces

RUN rm -f /etc/apt/sources.list.d/yarn.list || true

RUN if [ "${ROS_DISTRO}" = "jazzy" ]; then \
      sed -i -E 's|http://(archive\|security)\.ubuntu\.com/ubuntu/|https://\1.ubuntu.com/ubuntu/|g' \
        /etc/apt/sources.list.d/ubuntu.sources; \
    elif [ "${ROS_DISTRO}" = "humble" ]; then \
      sed -i -E 's|http://(archive\|security)\.ubuntu\.com/ubuntu/|https://\1.ubuntu.com/ubuntu/|g' \
        /etc/apt/sources.list; \
    fi

RUN apt-get update && \
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
      ros-${ROS_DISTRO}-moveit-servo \
      ros-${ROS_DISTRO}-moveit-planners \
      ros-${ROS_DISTRO}-moveit-plugins \
      ros-${ROS_DISTRO}-moveit-setup-assistant \
      ros-${ROS_DISTRO}-moveit-configs-utils \
      ros-${ROS_DISTRO}-moveit-task-constructor-core \
      ros-${ROS_DISTRO}-ament-package \
      ros-${ROS_DISTRO}-ament-index-cpp \
      ros-${ROS_DISTRO}-ament-cmake-core \
      ros-${ROS_DISTRO}-ament-index-python \
      ros-${ROS_DISTRO}-realsense2-camera \
      ros-${ROS_DISTRO}-rclcpp-action \
      python3-colcon-common-extensions \
      python3-setuptools \
    && rm -rf /var/lib/apt/lists/*

ARG HOST_USER_UID=1000
ARG HOST_USER_GID=1000
RUN existing_user=$(getent passwd ${HOST_USER_UID} | cut -d: -f1); \
    existing_group=$(getent group ${HOST_USER_GID} | cut -d: -f1); \
    if [ -n "$existing_group" ] && [ "$existing_group" != "admin" ]; then \
      groupmod -n admin "$existing_group"; \
    elif [ -z "$existing_group" ]; then \
      groupadd -g ${HOST_USER_GID} admin; \
    fi; \
    if [ -n "$existing_user" ] && [ "$existing_user" != "admin" ]; then \
      usermod -l admin -d /home/admin -m "$existing_user"; \
    elif [ -z "$existing_user" ]; then \
      useradd -m -u ${HOST_USER_UID} -g ${HOST_USER_GID} -s /bin/bash admin; \
    fi && \
    echo "admin ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

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

RUN apt-get update && \
    apt-get install -y python3-pip && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /usr/lib/python3/dist-packages/transforms3d \
           /usr/lib/python3/dist-packages/transforms3d-*.egg-info \
           /usr/lib/python3/dist-packages/sympy \
           /usr/lib/python3/dist-packages/sympy-*.egg-info \
           /usr/lib/python3/dist-packages/filelock \
           /usr/lib/python3/dist-packages/filelock-*.egg-info \
           /usr/lib/python3/dist-packages/filelock-*.dist-info && \
    if [ "$ROS_DISTRO" = "humble" ]; then PIP_FLAGS=""; else PIP_FLAGS="--break-system-packages"; fi && \
    python3 -m pip install --no-cache-dir $PIP_FLAGS \
        --extra-index-url https://pytorch-extension.intel.com/release-whl/stable/xpu/us/ \
        torch==2.5.1+cxx11.abi \
        torchvision==0.20.1+cxx11.abi \
        intel-extension-for-pytorch==2.5.10+xpu \
        oneccl_bind_pt==2.5.0+xpu && \
    python3 -m pip install --no-cache-dir $PIP_FLAGS \
        "numpy<2" \
        opencv-python \
        "transforms3d>=0.4.1" \
        pyyaml \
        ultralytics \
        openvino \
        pyapriltags
