import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder


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

    moveit_config = (
        MoveItConfigsBuilder("movensys_manipulator")
        .robot_description_semantic(
            file_path=f"config/{manipulator_model}/movensys_manipulator.srdf")
        .robot_description(file_path=f"config/{manipulator_model}/movensys_manipulator.urdf.xacro")
        .robot_description_kinematics(file_path=f"config/{manipulator_model}/kinematics.yaml")
        .joint_limits(file_path=f"config/{manipulator_model}/joint_limits.yaml")
        .trajectory_execution(file_path=f"config/{manipulator_model}/moveit_controllers.yaml")
        .planning_scene_monitor(
            publish_robot_description=True, publish_robot_description_semantic=True
        )
        .pilz_cartesian_limits(file_path=f"config/{manipulator_model}/pilz_cartesian_limits.yaml")
        .planning_pipelines(
            pipelines=["ompl", "chomp", "pilz_industrial_motion_planner"]
        )
        .to_moveit_configs()
    )

    pkg_share = get_package_share_directory("movensys_manipulator_moveit_config")
    moveit2_client_config = os.path.join(
        pkg_share, "config", manipulator_model, "moveit2_client.yaml")
    coverage_pose_config = os.path.join(
        pkg_share, "config", manipulator_model, "coverage_pose.yaml")

    coverage_node = Node(
        package="movensys_manipulator_moveit_config",
        executable="coverage_pose",
        name="coverage_pose",
        output="screen",
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.joint_limits,
            moveit2_client_config,
            coverage_pose_config,
            {"use_sim_time": use_sim_time},
        ],
    )

    return LaunchDescription(declared_arguments + [coverage_node])
