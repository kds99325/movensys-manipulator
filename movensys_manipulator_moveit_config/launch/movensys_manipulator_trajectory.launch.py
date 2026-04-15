from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    declared_arguments = []

    declared_arguments.append(
        DeclareLaunchArgument(
            "use_sim_time",
            default_value="false",
            description="Use simulation time",
        )
    )

    use_sim_time = LaunchConfiguration("use_sim_time")

    manipulator_model = os.environ.get("MANIPULATOR_MODEL", "dobot_cr3a")

    # Build MoveIt config with joint_limits
    moveit_config = (
        MoveItConfigsBuilder("movensys_manipulator", package_name="movensys_manipulator_moveit_config")
        .robot_description_semantic(file_path=f"config/{manipulator_model}/movensys_manipulator.srdf")
        .robot_description(file_path=f"config/{manipulator_model}/movensys_manipulator.urdf.xacro")
        .joint_limits(file_path=f"config/{manipulator_model}/joint_limits.yaml")
        .robot_description_kinematics(file_path=f"config/{manipulator_model}/kinematics.yaml")
        .to_moveit_configs()
    )

    pkg_share = get_package_share_directory("movensys_manipulator_moveit_config")
    moveit2_client_config = os.path.join(pkg_share, "config", manipulator_model, "moveit2_client.yaml")
    trajectory_config     = os.path.join(pkg_share, "config", manipulator_model, "trajectory.yaml")

    trajectory_node = Node(
        package="movensys_manipulator_moveit_config",
        executable="moveit2_trajectory_cpp",
        name="moveit2_trajectory_cpp",
        output="screen",
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.joint_limits,
            moveit2_client_config,
            trajectory_config,
            {"use_sim_time": use_sim_time},
        ],
    )

    return LaunchDescription(declared_arguments + [trajectory_node])