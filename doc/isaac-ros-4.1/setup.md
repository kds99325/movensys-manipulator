## 1. Nvidia Setup
please follow this isaac-ros setup first: https://nvidia-isaac-ros.github.io/v/release-4.1/getting_started/index.html

## 2. Dependencies
```
sudo apt-get update -y && \
sudo apt-get install -y ros-jazzy-joint-state-publisher \
                        ros-jazzy-joint-state-publisher-gui \
                        ros-jazzy-xacro \
                        ros-jazzy-rqt* \
                        ros-jazzy-ros2-control \
                        ros-jazzy-ros2-controllers \
                        ros-jazzy-controller-manager \
                        ros-jazzy-tf-transformations \
                        ros-jazzy-pal-statistics \
                        ros-jazzy-pal-statistics-msgs \
                        ros-jazzy-rmw-cyclonedds-cpp \
                        ros-jazzy-moveit-ros \
                        ros-jazzy-moveit-planners \
                        ros-jazzy-moveit-plugins \
                        ros-jazzy-moveit-setup-assistant \
                        ros-jazzy-moveit-configs-utils \
                        curl jq tar
```

## 3. Docker 
### Case A: Docker [x86]
```
cd ${MANIPULATOR_ROS_WS}/src/movensys-manipulator/doc/isaac-ros-4.1/docker
docker compose -f isaac-ros-4.1.yaml -f compose.x86.yaml down
docker compose -f isaac-ros-4.1.yaml -f compose.x86.yaml build
docker compose -f isaac-ros-4.1.yaml -f compose.x86.yaml up -d
```

### Case B: Docker [arm64]
```
cd ${MANIPULATOR_ROS_WS}/src/movensys-manipulator/doc/isaac-ros-4.1/docker
docker compose -f isaac-ros-4.1.yaml -f compose.arm64.yaml down
docker compose -f isaac-ros-4.1.yaml -f compose.arm64.yaml build
docker compose -f isaac-ros-4.1.yaml -f compose.arm64.yaml up -d
```