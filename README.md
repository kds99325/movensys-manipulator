# Host Environment Setup

## 1. Bashrc Configuration
- Add the following environment variables to your `~/.bashrc`:
```
export ROS_DOMAIN_ID=73
export HOST_USER_UID=1000        # replace with: id -u
export HOST_USER_GID=1000        # replace with: id -g
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
source /opt/ros/jazzy/setup.bash
```
```
source ~/.bashrc
```

## 2. Clone Repository
```
git clone https://github.com/movensys/movensys-manipulator.git
```

## 3. How to run
Please check the `doc/` folder to know how to run it.