import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def launch_setup(context, *args, **kwargs):
    use_sim_time = LaunchConfiguration("use_sim_time")
    simulator = context.perform_substitution(LaunchConfiguration("simulator"))

    manipulator_model = os.environ.get("MANIPULATOR_MODEL", "dobot_cr3a")
    pkg_share = get_package_share_directory("movensys_manipulator_moveit_config")

    if simulator == "isaacsim":
        bridge_params = os.path.join(pkg_share, "config", manipulator_model, "isaacsim_bridge.yaml")
        bridge_node = Node(
            package="movensys_manipulator_moveit_config",
            executable="isaacsim_bridge",
            name="isaacsim_bridge",
            output="screen",
            parameters=[bridge_params, {"use_sim_time": use_sim_time}],
        )
    elif simulator == "gazebo":
        bridge_params = os.path.join(pkg_share, "config", manipulator_model, "gazebo_bridge.yaml")
        bridge_node = Node(
            package="movensys_manipulator_moveit_config",
            executable="gazebo_bridge",
            name="gazebo_bridge",
            output="screen",
            parameters=[bridge_params, {"use_sim_time": use_sim_time}],
        )
    else:
        raise RuntimeError(f"Unknown simulator '{simulator}'. Valid options: 'isaacsim', 'gazebo'")

    return [bridge_node]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            "simulator",
            default_value="isaacsim",
            description="Simulator to bridge: 'isaacsim' or 'gazebo'",
        ),
        DeclareLaunchArgument(
            "use_sim_time",
            default_value="true",
            description="Use simulation time",
        ),
        OpaqueFunction(function=launch_setup),
    ])
