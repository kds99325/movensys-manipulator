import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('movensys_manipulator_perception')
    default_params = os.path.join(pkg_share, 'config', 'apriltag_detector.yaml')

    declared_arguments = [
        DeclareLaunchArgument(
            'params_file', default_value=default_params,
            description='YAML parameter file for the AprilTag detector',
        ),
        DeclareLaunchArgument(
            'use_sim_time', default_value='false',
            description='Use simulation clock (/clock)',
        ),
    ]

    apriltag_node = Node(
        package='movensys_manipulator_perception',
        executable='apriltag_detector.py',
        name='apriltag_detector',
        output='screen',
        parameters=[
            LaunchConfiguration('params_file'),
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
        ],
    )

    return LaunchDescription(declared_arguments + [apriltag_node])
