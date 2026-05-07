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

    camera_hand_node = Node(
        package='realsense2_camera',
        executable='realsense2_camera_node',
        name='realsense2_camera',
        namespace='camera_hand',
        parameters=[realsense_config],
        output='screen',
        remappings=[
            ('realsense2_camera/color/image_raw', '/image_hand/rgb'),
            ('realsense2_camera/color/camera_info', '/image_hand/camera_info')
        ]
    )

    return LaunchDescription([
        camera_hand_node
    ])
