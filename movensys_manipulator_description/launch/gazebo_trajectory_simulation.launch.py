import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess, DeclareLaunchArgument, RegisterEventHandler, TimerAction
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import Command, PathJoinSubstitution, LaunchConfiguration
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    ros_distro = os.environ.get('ROS_DISTRO')

    gz_sim_pkg =    {'humble': 'ros_ign_gazebo',       'jazzy': 'ros_gz_sim'}[ros_distro]
    gz_bridge_pkg = {'humble': 'ros_ign_bridge',       'jazzy': 'ros_gz_bridge'}[ros_distro]
    gz_sim_launch = {'humble': 'ign_gazebo.launch.py', 'jazzy': 'gz_sim.launch.py'}[ros_distro]
    clock_msg =     {'humble': 'ignition.msgs.Clock',  'jazzy': 'gz.msgs.Clock'}[ros_distro]

    pkg_share = get_package_share_directory('movensys_manipulator_description')
    xacro_file = os.path.join(pkg_share, 'urdf', os.environ.get('MANIPULATOR_MODEL', 'dobot_cr3a'), 'movensys_manipulator.gazebo.xacro')

    # Get robot description
    robot_description_content = Command(['xacro ', xacro_file])

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='both',
        parameters=[{
            'use_sim_time': True,
            'robot_description': robot_description_content,
            'publish_frequency': 100.0
        }]
    )

    # Include Gazebo sim launch file with physics optimization
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            get_package_share_directory(gz_sim_pkg),
            f'/launch/{gz_sim_launch}'
        ]),
        launch_arguments={
            'gz_args': '-r -v 1 empty.sdf'
        }.items()
    )

    # Spawn robot from URDF topic
    spawn_entity_robot = Node(
        package=gz_sim_pkg,
        executable='create',
        output='screen',
        arguments=[
            '-name', 'movensys_manipulator',
            '-topic', 'robot_description',
            '-z', '0.1'
        ]
    )

    # Bridge for clock
    gz_ros_bridge = Node(
        package=gz_bridge_pkg,
        executable='parameter_bridge',
        arguments=[f'/clock@rosgraph_msgs/msg/Clock[{clock_msg}'],
        output='screen'
    )

    # Load controllers
    load_joint_state_broadcaster = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active', 'joint_state_broadcaster'],
        output='screen'
    )

    load_joint_position_controller = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active', 'gazebo_position_controller'],
        output='screen'
    )

    return LaunchDescription([
        gz_sim,
        robot_state_publisher,
        spawn_entity_robot,
        gz_ros_bridge,
        load_joint_state_broadcaster,
        load_joint_position_controller
    ])