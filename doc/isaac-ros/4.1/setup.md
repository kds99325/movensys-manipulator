## 1. Nvidia Setup
please follow this isaac-ros setup first: https://nvidia-isaac-ros.github.io/v/release-4.1/getting_started/index.html

## 2. Docker 
### Case A: Docker [x86]
```
cd ${MOVENSYS_MANIPULATOR_PACKAGES}/doc/isaac-ros/4.1
docker compose --env-file ../../.env -f isaac-ros_4.1.yaml -f ../isaac-ros.x86.yaml down
docker compose --env-file ../../.env -f isaac-ros_4.1.yaml -f ../isaac-ros.x86.yaml build
docker compose --env-file ../../.env -f isaac-ros_4.1.yaml -f ../isaac-ros.x86.yaml up -d
```

### Case B: Docker [arm64]
```
cd ${MOVENSYS_MANIPULATOR_PACKAGES}/doc/isaac-ros/4.1
docker compose --env-file ../../.env -f isaac-ros_4.1.yaml -f ../isaac-ros.arm64.yaml down
docker compose --env-file ../../.env -f isaac-ros_4.1.yaml -f ../isaac-ros.arm64.yaml build
docker compose --env-file ../../.env -f isaac-ros_4.1.yaml -f ../isaac-ros.arm64.yaml up -d
```

### Checking the docker
```
docker exec -u admin -it movensys_manipulator_container bash -lc 'source /opt/ros/jazzy/setup.bash && source /home/admin/ws/install/setup.bash && exec bash -i'
```

