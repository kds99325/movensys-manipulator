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

    declare_rsp = DeclareLaunchArgument(
        "rsp",
        default_value="true",
        description="Publish /robot_description via isaac_cumotion.launch.py. Set false "
                    "when a backend launch (Gazebo sim or wmx_r2_control) already publishes it."
    )

    pkg = get_package_share_directory('movensys_manipulator_isaac_ros_config')

    apriltag_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg, 'launch', 'isaac_apriltag.launch.py')
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    cumotion_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg, 'launch', 'isaac_cumotion.launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'rsp': LaunchConfiguration('rsp'),
        }.items()
    )

    return LaunchDescription([
        declare_use_sim_time,
        declare_rsp,
        apriltag_launch,
        cumotion_launch,
    ])
