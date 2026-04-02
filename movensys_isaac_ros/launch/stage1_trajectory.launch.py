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

    # Build MoveIt config with joint_limits
    moveit_config = (
        MoveItConfigsBuilder("movensys_manipulator", package_name="movensys_moveit_config")
        .robot_description_semantic(file_path="config/movensys_manipulator.srdf")
        .robot_description(file_path="config/movensys_manipulator.urdf.xacro")
        .joint_limits(file_path="config/joint_limits.yaml")
        .robot_description_kinematics(file_path="config/kinematics.yaml")
        .to_moveit_configs()
    )

    # Stage1 trajectory node with MoveIt parameters
    stage1_trajectory_node = Node(
        package="movensys_isaac_ros",
        executable="stage1_trajectory_cpp",
        name="stage1_trajectory_cpp",
        output="screen",
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.joint_limits,
            {"use_sim_time": use_sim_time},
        ],
    )

    return LaunchDescription(declared_arguments + [stage1_trajectory_node])
