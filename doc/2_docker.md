# 1. Note For Isaac-ROS only
please follow this isaac-ros setup first: https://nvidia-isaac-ros.github.io/v/release-4.1/getting_started/index.html
 
# 2. Docker setup
```
cd ${MOVENSYS_MANIPULATOR_PACKAGES}/docker                                                                              
docker compose -f ${MOVENSYS_ROS_VERSION}.yaml -f movensys_manipulator.${CPU_ARCH}.yaml down
docker compose -f ${MOVENSYS_ROS_VERSION}.yaml -f movensys_manipulator.${CPU_ARCH}.yaml build            
docker compose -f ${MOVENSYS_ROS_VERSION}.yaml -f movensys_manipulator.${CPU_ARCH}.yaml up -d 
```

### Checking the docker
```
docker exec -it movensys_manipulator_container bash -lc 'source /opt/ros/${ROS_DISTRO}/setup.bash && source /home/admin/ws/install/setup.bash && exec bash -i'
```

# 3. Checking URDF
```
docker exec -it movensys_manipulator_container \
bash -lc 'source /opt/ros/${ROS_DISTRO}/setup.bash && \
        source /home/admin/ws/install/setup.bash && \
        ros2 launch movensys_manipulator_description movensys_manipulator_rviz.launch.py'
```