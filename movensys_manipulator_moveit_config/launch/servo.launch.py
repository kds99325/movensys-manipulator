import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import ComposableNodeContainer, Node
from launch_ros.descriptions import ComposableNode
from launch_ros.substitutions import FindPackageShare
from moveit_configs_utils import MoveItConfigsBuilder
import yaml

def load_yaml(package_name, file_path):
    absolute_file_path = os.path.join(get_package_share_directory(package_name), file_path)
    with open(absolute_file_path, "r") as f:
        return yaml.safe_load(f)


def generate_launch_description():
    declared_arguments = [
        DeclareLaunchArgument(
            "use_sim_time",
            default_value="true",
            description="Use simulation time",
        ),
        DeclareLaunchArgument(
            "rsp",
            default_value="true",
            description="Start robot_state_publisher here (set false to defer to a "
                        "backend launch that publishes /robot_description)",
        ),
        DeclareLaunchArgument(
            "rviz_config",
            default_value="movensys_manipulator_moveit.rviz",
            description="RViz configuration file",
        ),
    ]
    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])


def launch_setup(context, *args, **kwargs):
    use_sim_time = LaunchConfiguration("use_sim_time")
    manipulator_model = os.environ.get("MANIPULATOR_MODEL", "dobot_cr3a")

    moveit_config = (
        MoveItConfigsBuilder("movensys_manipulator")
        .robot_description_semantic(
            file_path=f"config/{manipulator_model}/movensys_manipulator.srdf")
        .robot_description(
            file_path=f"config/{manipulator_model}/movensys_manipulator.urdf.xacro")
        .robot_description_kinematics(
            file_path=f"config/{manipulator_model}/kinematics.yaml")
        .joint_limits(file_path=f"config/{manipulator_model}/joint_limits.yaml")
        .trajectory_execution(
            file_path=f"config/{manipulator_model}/moveit_controllers.yaml")
        .pilz_cartesian_limits(
            file_path=f"config/{manipulator_model}/pilz_cartesian_limits.yaml")
        .planning_pipelines(
            pipelines=["ompl", "chomp", "pilz_industrial_motion_planner"])
        .to_moveit_configs()
    )

    servo_yaml = load_yaml(
        "movensys_manipulator_moveit_config",
        f"config/{manipulator_model}/servo.yaml",
    )
    servo_params = {"moveit_servo": servo_yaml}

    servo_container = ComposableNodeContainer(
        name="servo_container",
        namespace="",
        package="rclcpp_components",
        executable="component_container_mt",
        output="screen",
        composable_node_descriptions=[
            ComposableNode(
                package="moveit_servo",
                plugin="moveit_servo::ServoNode",
                name="servo_node",
                parameters=[
                    servo_params,
                    moveit_config.robot_description,
                    moveit_config.robot_description_semantic,
                    moveit_config.robot_description_kinematics,
                    moveit_config.joint_limits,
                    {"use_sim_time": use_sim_time},
                ],
            ),
        ],
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="both",
        condition=IfCondition(LaunchConfiguration("rsp")),
        parameters=[moveit_config.robot_description, {"use_sim_time": use_sim_time}],
    )

    rviz_config = PathJoinSubstitution(
        [FindPackageShare("movensys_manipulator_moveit_config"),
         "rviz", LaunchConfiguration("rviz_config")]
    )
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", rviz_config],
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            {"use_sim_time": use_sim_time},
        ],
    )

    return [
        robot_state_publisher,
        servo_container,
        rviz_node,
    ]
