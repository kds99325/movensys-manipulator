import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('movensys_manipulator_perception')
    manipulator_model = os.environ.get('MANIPULATOR_MODEL', 'dobot_cr3a')
    default_params = os.path.join(pkg_share, 'config', manipulator_model, 'apriltag_detector.yaml')

    use_sim_time = LaunchConfiguration('use_sim_time')

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

    moveit_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('movensys_manipulator_moveit_config'),
                'launch', 'moveit.launch.py',
            )
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items(),
    )

    apriltag_node = Node(
        package='movensys_manipulator_perception',
        executable='apriltag_detector.py',
        name='apriltag_detector',
        output='screen',
        parameters=[
            LaunchConfiguration('params_file'),
            {'use_sim_time': use_sim_time},
        ],
    )

    return LaunchDescription(declared_arguments + [moveit_launch, apriltag_node])
