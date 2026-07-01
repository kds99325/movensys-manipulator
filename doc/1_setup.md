# Host Environment Setup

## 1. Bashrc Configuration
- Add the following environment variables to your `~/.bashrc`:
```
export ROS_DOMAIN_ID=73                         #use any number
export ROS_DISTRO=jazzy                         #support {jazzy, humble}
export MOVENSYS_ROS_VERSION=isaac-ros_4.1       #support {isaac-ros_4.1, isaac-ros_3.2, general} 
export CPU_ARCH=amd64                           #support {amd64, arm64}
export MANIPULATOR_MODEL=dobot_cr3a             #support {dobot_cr3a, dobot_cr5a}

export HOST_USER_UID=$(id -u)
export HOST_USER_GID=$(id -g)
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

export MOVENSYS_MANIPULATOR_PACKAGES=~/workspaces/movensys_ws/src/movensys-manipulator
export ISAAC_ROS_WS=~/workspaces/isaac_ros-dev

mros() {
  if [ $# -eq 0 ]; then
    docker exec -it -u admin movensys_manipulator_container \
      bash -lc 'source /opt/ros/${ROS_DISTRO}/setup.bash && source /home/admin/workspaces/movensys_ws/install/setup.bash && exec bash -i'
  else
    docker exec -it -u admin movensys_manipulator_container \
      bash -lc "source /opt/ros/\${ROS_DISTRO}/setup.bash && source /home/admin/workspaces/movensys_ws/install/setup.bash && $*"
  fi
}
```
```
xhost +local:docker
source ~/.bashrc
```

## 2. Set CycloneDDS buffer
```
sudo tee /etc/sysctl.d/99-network-buffers.conf << 'EOF'
net.core.rmem_max=67108864
net.core.rmem_default=67108864
net.core.wmem_max=67108864
net.core.wmem_default=67108864
EOF

sudo sysctl -p /etc/sysctl.d/99-network-buffers.conf
sysctl net.core.rmem_max net.core.rmem_default net.core.wmem_max net.core.wmem_default
```

## 4. Clone Repository
```
mkdir -p  ~/workspaces/movensys_ws/src
cd ~/workspaces/movensys_ws/src
git clone git@github.com:movensys/movensys-manipulator.git
```