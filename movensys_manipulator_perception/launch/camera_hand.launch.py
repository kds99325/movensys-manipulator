import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('movensys_manipulator_perception')
    manipulator_model = os.environ.get('MANIPULATOR_MODEL', 'dobot_cr3a')
    realsense_config = os.path.join(pkg_share, 'config', manipulator_model, 'realsense_hand.yaml')

    declared_arguments = [
        DeclareLaunchArgument(
            'camera_tf_x', default_value='0.0',
            description='Camera mount offset X from Link6 (meters)',
        ),
        DeclareLaunchArgument(
            'camera_tf_y', default_value='0.0',
            description='Camera mount offset Y from Link6 (meters)',
        ),
        DeclareLaunchArgument(
            'camera_tf_z', default_value='0.05',
            description='Camera mount offset Z from Link6 (meters)',
        ),
        DeclareLaunchArgument(
            'camera_tf_roll', default_value='0.0',
            description='Camera mount roll from Link6 (radians)',
        ),
        DeclareLaunchArgument(
            'camera_tf_pitch', default_value='0.0',
            description='Camera mount pitch from Link6 (radians)',
        ),
        DeclareLaunchArgument(
            'camera_tf_yaw', default_value='0.0',
            description='Camera mount yaw from Link6 (radians)',
        ),
    ]

    camera_node = Node(
        package='realsense2_camera',
        executable='realsense2_camera_node',
        name='realsense2_camera',
        namespace='camera_hand',
        parameters=[realsense_config],
        output='screen',
    )

    static_tf_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='link6_to_camera_tf',
        arguments=[
            '--x', LaunchConfiguration('camera_tf_x'),
            '--y', LaunchConfiguration('camera_tf_y'),
            '--z', LaunchConfiguration('camera_tf_z'),
            '--roll', LaunchConfiguration('camera_tf_roll'),
            '--pitch', LaunchConfiguration('camera_tf_pitch'),
            '--yaw', LaunchConfiguration('camera_tf_yaw'),
            '--frame-id', 'Link6',
            '--child-frame-id', 'camera_hand_link_link',
        ],
    )

    return LaunchDescription(declared_arguments + [camera_node, static_tf_node])
