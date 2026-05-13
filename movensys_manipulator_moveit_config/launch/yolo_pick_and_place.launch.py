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

    moveit_config = (
        MoveItConfigsBuilder("movensys_manipulator")
        .robot_description_semantic(file_path=f"config/{manipulator_model}/movensys_manipulator.srdf")
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
    moveit2_client_config  = os.path.join(pkg_share, "config", manipulator_model, "moveit2_client.yaml")
    yolo_trajectory_config = os.path.join(pkg_share, "config", manipulator_model, "yolo_trajectory.yaml")

    if not os.path.isfile(yolo_trajectory_config):
        raise FileNotFoundError(
            f"yolo_trajectory.yaml not found for manipulator model '{manipulator_model}'. "
            f"Expected: {yolo_trajectory_config}. "
            f"Set MANIPULATOR_MODEL to a model that has YOLO configuration (e.g. dobot_cr5a)."
        )

    yolo_pick_and_place_node = Node(
        package="movensys_manipulator_moveit_config",
        executable="yolo_pick_and_place_cpp",
        name="yolo_pick_and_place_cpp",
        output="screen",
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.joint_limits,
            moveit2_client_config,
            yolo_trajectory_config,
            {"use_sim_time": use_sim_time},
        ],
    )

    return LaunchDescription(declared_arguments + [yolo_pick_and_place_node])
