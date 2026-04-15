import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    declared_arguments = [
        DeclareLaunchArgument("use_sim_time", default_value="true",
                              description="Use simulation time"),
    ]

    use_sim_time = LaunchConfiguration("use_sim_time")

    manipulator_model = os.environ.get("MANIPULATOR_MODEL", "dobot_cr3a")

    pkg_share = get_package_share_directory("movensys_manipulator_moveit_config")
    bridge_params = os.path.join(pkg_share, "config", manipulator_model, "isaacsim_bridge.yaml")

    isaacsim_bridge_node = Node(
        package="movensys_manipulator_moveit_config",
        executable="isaacsim_bridge",
        name="isaacsim_bridge",
        output="screen",
        parameters=[
            bridge_params,
            {"use_sim_time": use_sim_time},
        ],
    )

    return LaunchDescription(declared_arguments + [isaacsim_bridge_node])
