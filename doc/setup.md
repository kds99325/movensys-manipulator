## 1a. Isaac ROS 4.1 Setup
please follow this isaac-ros setup first: https://nvidia-isaac-ros.github.io/v/release-4.1/getting_started/index.html





## 2a. Isaac-ROS 4.1 
### Isaac-ros: Docker [x86]
```
cd ${MOVENSYS_MANIPULATOR_PACKAGES}/doc                                                                              
docker compose --env-file .env -f isaac-ros/4.1/isaac-ros_4.1.yaml -f movensys_manipulator.x86.yaml down
docker compose --env-file .env -f isaac-ros/4.1/isaac-ros_4.1.yaml -f movensys_manipulator.x86.yaml build            
docker compose --env-file .env -f isaac-ros/4.1/isaac-ros_4.1.yaml -f movensys_manipulator.x86.yaml up -d 
```

### Isaac-ros: Docker [arm64]
```
cd ${MOVENSYS_MANIPULATOR_PACKAGES}/doc/isaac-ros/4.1
docker compose --env-file .env -f isaac-ros/4.1/isaac-ros_4.1.yaml -f ../movensys_manipulator.arm64.yaml down
docker compose --env-file .env -f isaac-ros/4.1/isaac-ros_4.1.yaml -f ../movensys_manipulator.arm64.yaml build
docker compose --env-file .env -f isaac-ros/4.1/isaac-ros_4.1.yaml -f ../movensys_manipulator.arm64.yaml up -d
```





## 2b. General : Docker [x86]
```
cd ${MOVENSYS_MANIPULATOR_PACKAGES}/doc                                                                              
docker compose --env-file .env -f general/general.yaml -f movensys_manipulator.x86.yaml down
docker compose --env-file .env -f general/general.yaml -f movensys_manipulator.x86.yaml build            
docker compose --env-file .env -f general/general.yaml -f movensys_manipulator.x86.yaml up -d 
```






### Checking the docker
```
docker exec -u admin -it movensys_manipulator_container bash -lc 'source /opt/ros/${ROS_DISTRO}$/setup.bash && source /home/admin/ws/install/setup.bash && exec bash -i'
```

