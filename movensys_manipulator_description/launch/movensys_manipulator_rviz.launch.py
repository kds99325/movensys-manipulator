import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command
import launch_ros.actions
from launch_ros.actions import Node


xacro_file = os.path.join(
    get_package_share_directory('movensys_manipulator_description'),
    'urdf',
    os.environ.get('MANIPULATOR_MODEL', 'dobot_cr3a'),
    'movensys_manipulator.xacro',
)
rviz_config_path = os.path.join(
    get_package_share_directory('movensys_manipulator_description'),
    'rviz',
    'movensys_manipulator.rviz',
)

rviz_node = launch_ros.actions.Node(
    package='rviz2',
    executable='rviz2',
    name='rviz2',
    output='screen',
    arguments=['-d', rviz_config_path],
)

robot_state_publisher = launch_ros.actions.Node(
    package='robot_state_publisher',
    executable='robot_state_publisher',
    parameters=[{'robot_description': Command(['xacro ', xacro_file])}],
)

start_joint_gui = Node(
    package='joint_state_publisher_gui',
    executable='joint_state_publisher_gui',
    name='joint_state_publisher_gui',
    output='screen',
    parameters=[{'use_gui': True}],
)


def generate_launch_description():
    return LaunchDescription([
        rviz_node,
        robot_state_publisher,
        start_joint_gui,
    ])
