"""
yolo_cube_detector.launch.py
============================
Launcher for the YOLO OBB cube detector node.

Loads defaults from config/yolo_cube_detector.yaml. The `model_path`
argument is required — typically resolved to a file installed by the
sibling `movensys_perception_models` package.

Example:
    ros2 launch movensys_perception yolo_cube_detector.launch.py \\
        model_path:=$(ros2 pkg prefix movensys_perception_models)\\
/share/movensys_perception_models/models/cubes_obb.pt
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('movensys_perception')
    default_params = os.path.join(pkg_share, 'config', 'yolo_cube_detector.yaml')

    declared_arguments = [
        DeclareLaunchArgument(
            'params_file', default_value=default_params,
            description='YAML parameter file for the YOLO cube detector',
        ),
        DeclareLaunchArgument(
            'model_path', default_value='',
            description='Path to OpenVINO model dir or .pt weights file (REQUIRED)',
        ),
        DeclareLaunchArgument(
            'use_sim_time', default_value='false',
            description='Use simulation time',
        ),
    ]

    detector_node = Node(
        package='movensys_perception',
        executable='yolo_cube_detector.py',
        name='yolo_cube_detector',
        output='screen',
        parameters=[
            LaunchConfiguration('params_file'),
            {
                'model_path': LaunchConfiguration('model_path'),
                'use_sim_time': LaunchConfiguration('use_sim_time'),
            },
        ],
    )

    return LaunchDescription(declared_arguments + [detector_node])
