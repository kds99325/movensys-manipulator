import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, ComposableNodeContainer, LoadComposableNodes
from launch_ros.descriptions import ComposableNode
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")

    declare_use_sim_time = DeclareLaunchArgument(
        "use_sim_time",
        default_value="false",
        description="Use simulation clock (/clock)"
    )

    pkg_movensys_isaac_ros_config = get_package_share_directory('movensys_manipulator_isaac_ros_config')
    pkg_movensys_description = get_package_share_directory('movensys_manipulator_description')

    manipulator_model = os.environ.get('MANIPULATOR_MODEL', 'dobot_cr3a')

    robot_xrdf = os.path.join(pkg_movensys_description, 'urdf', manipulator_model, 'movensys_manipulator.xrdf')
    urdf_path = os.path.join(pkg_movensys_description, 'urdf', manipulator_model, 'movensys_manipulator.urdf')

    nvblox_base_config = os.path.join(pkg_movensys_isaac_ros_config, 'config', manipulator_model, 'nvblox_movensys_base.yaml')
    workspace_config = os.path.join(pkg_movensys_isaac_ros_config, 'config', manipulator_model, 'movensys_sim.yaml')

    manipulation_container = ComposableNodeContainer(
        name='manipulation_container',
        namespace='',
        package='rclcpp_components',
        executable='component_container_mt',
        composable_node_descriptions=[],
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
    )

    nvblox_node = ComposableNode(
        name='nvblox_node',
        package='nvblox_ros',
        plugin='nvblox::NvbloxNode',
        remappings=[
            ('/camera_0/color/image', '/image_nvblox/rgb'),
            ('/camera_0/color/camera_info', '/image_nvblox/camera_info'),
            ('/camera_0/depth/image', '/robot_segmenter/world_depth_ros'),
            ('/camera_0/depth/camera_info', '/image_nvblox/camera_info'),
        ],
        parameters=[
            nvblox_base_config,
            workspace_config,
            {'num_cameras': 1},
            {'use_sim_time': use_sim_time},
        ]
    )

    load_nvblox = LoadComposableNodes(
        target_container='manipulation_container',
        composable_node_descriptions=[nvblox_node],
    )

    robot_segmenter_config = os.path.join(
        pkg_movensys_isaac_ros_config, 'config', manipulator_model, 'robot_segmenter_movensys.yaml'
    )
    robot_segmenter = Node(
        package='isaac_ros_cumotion',
        executable='robot_segmenter_node',
        name='robot_segmenter_node',
        output='screen',
        parameters=[
            robot_segmenter_config,
            {
                'robot': robot_xrdf,
                'urdf_path': urdf_path,
                'use_sim_time': use_sim_time,
            }
        ]
    )

    ros_distro = os.environ.get('ROS_DISTRO', 'humble')

    nodes = [
        declare_use_sim_time,
        manipulation_container,
        robot_segmenter,
        load_nvblox,
    ]

    if ros_distro == 'jazzy':
        static_planning_scene = Node(
            package='isaac_ros_cumotion',
            executable='static_planning_scene',
            name='static_planning_scene',
            output='screen',
            parameters=[
                {
                    'robot': robot_xrdf,
                    'urdf_path': urdf_path,
                    'use_sim_time': use_sim_time,
                }
            ]
        )
        nodes.append(static_planning_scene)

    return LaunchDescription(nodes)
