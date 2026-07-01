"""Launcher for the YOLO OBB dice detector node.

Loads defaults from config/$MANIPULATOR_MODEL/yolo_dice_detector.yaml. The `model_path`
argument defaults to the dice_obb.pt weights shipped inside this
package's models/ directory; override to point at a different .pt
file or an OpenVINO export.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('movensys_manipulator_perception')
    manipulator_model = os.environ.get('MANIPULATOR_MODEL', 'dobot_cr3a')
    default_params = os.path.join(pkg_share, 'config', manipulator_model, 'yolo_dice_detector.yaml')
    default_model = os.path.join(pkg_share, 'models', 'dice_obb-with_3D_Tray.pt')

    declared_arguments = [
        DeclareLaunchArgument(
            'params_file', default_value=default_params,
            description='YAML parameter file for the YOLO dice detector',
        ),
        DeclareLaunchArgument(
            'model_path', default_value=default_model,
            description='Path to OpenVINO model dir or .pt weights file',
        ),
        DeclareLaunchArgument(
            'use_sim_time', default_value='false',
            description='Use simulation time',
        ),
    ]

    detector_node = Node(
        package='movensys_manipulator_perception',
        executable='yolo_dice_detector.py',
        name='yolo_dice_detector',
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
