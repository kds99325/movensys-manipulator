import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")

    declare_use_sim_time = DeclareLaunchArgument(
        "use_sim_time",
        default_value="false",
        description="Use simulation clock (/clock)"
    )

    pkg_movensys_isaac_ros_config = get_package_share_directory(
        'movensys_manipulator_isaac_ros_config')
    pkg_movensys_manipulator_perception = get_package_share_directory(
        'movensys_manipulator_perception')

    nvblox_rviz = os.path.join(pkg_movensys_isaac_ros_config, 'rviz', 'nvblox.rviz')

    camera_nvblox = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_movensys_manipulator_perception, 'launch', 'camera_nvblox.launch.py')
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items(),
    )

    cumotion_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_movensys_isaac_ros_config, 'launch', 'isaac_cumotion.launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'read_esdf_world': 'true',
            'rviz_config': nvblox_rviz,
        }.items()
    )

    nvblox_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_movensys_isaac_ros_config, 'launch', 'isaac_nvblox.launch.py')
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    return LaunchDescription([
        declare_use_sim_time,
        camera_nvblox,
        cumotion_launch,
        nvblox_launch,
    ])
