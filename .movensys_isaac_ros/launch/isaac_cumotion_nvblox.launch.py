from os import path
import os
import yaml

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, ComposableNodeContainer, LoadComposableNodes
from launch_ros.descriptions import ComposableNode
from ament_index_python.packages import get_package_share_directory


def augment_moveit_config(moveit_config):
    config_file_path = path.join(
        get_package_share_directory('isaac_ros_cumotion_moveit'),
        'config',
        'isaac_ros_cumotion_planning.yaml'
    )

    with open(config_file_path) as config_file:
        config = yaml.safe_load(config_file)

    moveit_config.planning_pipelines['planning_pipelines'].append('isaac_ros_cumotion')
    moveit_config.planning_pipelines['isaac_ros_cumotion'] = config
    moveit_config.planning_pipelines['default_planning_pipeline'] = 'isaac_ros_cumotion'


def generate_launch_description():

    use_sim_time = LaunchConfiguration("use_sim_time")

    declare_use_sim_time = DeclareLaunchArgument(
        "use_sim_time",
        default_value="false",
        description="Use simulation clock (/clock)"
    )

    pkg_movensys_isaac_config = get_package_share_directory('movensys_isaac_ros')
    pkg_movensys_description = get_package_share_directory('movensys_manipulator_description')

    robot_xrdf = os.path.join(pkg_movensys_description, 'urdf', 'movensys_manipulator.xrdf')
    urdf_path = os.path.join(pkg_movensys_description, 'urdf', 'movensys_manipulator.urdf')

    nvblox_base_config = os.path.join(pkg_movensys_isaac_config, 'config', 'nvblox_movensys_base.yaml')
    workspace_config = os.path.join(pkg_movensys_isaac_config, 'config', 'movensys_sim.yaml')

    rviz_config_path = os.path.join(pkg_movensys_isaac_config, 'rviz', 'stage3.rviz')

    moveit_launch_path = path.join(
        get_package_share_directory('movensys_moveit_config'),
        'launch',
        'movensys_manipulator_moveit.launch.py'
    )

    lf = open(moveit_launch_path).read()

    lf = lf.replace('generate_launch_description', 'generate_base_launch_description')

    lf = lf.replace(
        'run_move_group_node =',
        'augment_moveit_config(moveit_config)\n    run_move_group_node ='
    )

    lf = lf.replace(
        "parameters=[moveit_config.robot_description]",
        "parameters=[moveit_config.robot_description, {'use_sim_time': use_sim_time}]"
    )
    
    lf = lf.replace(
        'arguments=["-d", rviz_config]',
        f'arguments=["-d", "{rviz_config_path}"]'
    )

    exec(lf, globals())

    manipulation_container = ComposableNodeContainer(
        name='manipulation_container',
        namespace='',
        package='rclcpp_components',
        executable='component_container_mt',
        composable_node_descriptions=[],
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
    )

    nvblox_remappings = [
        # Color camera
        ('/camera_0/color/image', '/image_nvblox/rgb'),
        ('/camera_0/color/camera_info', '/image_nvblox/camera_info'),
        # Depth camera - using robot-filtered depth from robot_segmenter
        # Isaac ROS 4.1 ignores world_depth_publish_topics yaml param, hardcodes _ros/_bridge suffixes
        ('/camera_0/depth/image', '/robot_segmenter/world_depth_ros'),
        ('/camera_0/depth/camera_info', '/image_nvblox/camera_info'),
    ]

    # You can set more camera in here.
    nvblox_node = ComposableNode(
        name='nvblox_node',
        package='nvblox_ros',
        plugin='nvblox::NvbloxNode',
        remappings=nvblox_remappings,
        parameters=[
            nvblox_base_config,
            workspace_config,
            {'num_cameras': 1},
            {'use_sim_time': use_sim_time},
        ]
    )

    # Load nvblox as composable node into the manipulation container
    # This matches the working isaac_manipulator approach
    load_nvblox = LoadComposableNodes(
        target_container='manipulation_container',
        composable_node_descriptions=[nvblox_node],
    )

    robot_segmenter_config = os.path.join(
        pkg_movensys_isaac_config, 'config', 'robot_segmenter_movensys.yaml'
    )
    robot_segmenter = Node(
        package='isaac_ros_cumotion',
        executable='robot_segmenter_node',
        name='robot_segmenter_node',
        output='screen',
        parameters=[
            robot_segmenter_config,
            {
                # Override robot files from launch
                'robot': robot_xrdf,
                'urdf_path': urdf_path,
                'use_sim_time': use_sim_time,
            }
        ]
    )

    # Required by cumotion_planner_node in Isaac ROS 4.1 before it can proceed
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

    # cuMotion Planner Node (GPU motion planning with ESDF)
    # https://nvidia-isaac-ros.github.io/v/release-4.1/repositories_and_packages/isaac_ros_cumotion/isaac_ros_cumotion/index.html#cumotionactionserver
    cumotion_planner = Node(
        package='isaac_ros_cumotion',
        executable='cumotion_planner_node',
        name='cumotion_planner_node',
        output='screen',
        parameters=[
            {
                'robot': robot_xrdf,
                'urdf_path': urdf_path,
                'use_sim_time': use_sim_time,
                'read_esdf_world': True, # ESDF integration - THIS IS KEY for obstacle avoidance
                'esdf_service_name': '/nvblox_node/get_esdf_and_gradient',
                'workspace_file_path': workspace_config, # grid_center_m/grid_size_m are derived from this
                'voxel_size': 0.01,
                'time_dilation_factor': 1.0, # 0.5 = 50% speed (safer), 1.0 = full speed
                'override_moveit_scaling_factors': False,
                'max_attempts': 10, # Increase planning attempts for complex obstacle scenarios
                'num_graph_seeds': 10,
                'num_trajopt_seeds': 10,
                'num_trajopt_time_steps': 50,
                'collision_cache_cuboid': 30,
                'collision_cache_mesh': 30,
                'joint_states_topic': '/joint_states',
                'add_ground_plane': True,
                'publish_curobo_world_as_voxels': False,
                'publish_voxel_size': 0.02,  # Larger voxel size for visualization
                'max_publish_voxels': 50000,  # Reduced for better performance
            }
        ]
    )

    return LaunchDescription([
        declare_use_sim_time,
        generate_base_launch_description(),
        manipulation_container,
        robot_segmenter,
        load_nvblox,
        static_planning_scene,
        cumotion_planner,
    ])
