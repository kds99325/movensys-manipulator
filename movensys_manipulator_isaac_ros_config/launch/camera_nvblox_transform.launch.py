""" Static transform publisher acquired via MoveIt 2 hand-eye calibration """
""" EYE-TO-HAND: world -> camera """
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description() -> LaunchDescription:
    use_sim_time_arg = DeclareLaunchArgument(
        "use_sim_time", default_value="false",
        description="Use simulation clock (/clock)"
    )

    start_camera_nvblox_transform_simulation = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        output="log",
        condition=IfCondition(LaunchConfiguration("use_sim_time")),
        parameters=[{"use_sim_time": True}],
        arguments=[
            "--frame-id", "world_manipulator",
            "--child-frame-id", "camera_nvblox_color_optical_frame",
            "--x", "-0.7",
            "--y", "-0.7",
            "--z", "0.8318",
            "--roll", "-2.078",
            "--pitch", "-0.0121",
            "--yaw", "-0.7338",
        ],
    )

    start_camera_nvblox_transform_real = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        output="log",
        condition=UnlessCondition(LaunchConfiguration("use_sim_time")),
        parameters=[{"use_sim_time": False}],
        arguments=[
            "--frame-id", "world_manipulator",
            "--child-frame-id", "camera_nvblox_link",
            "--x", "-0.5765517241379307",
            "--y", "-0.4955172413793103",
            "--z", "0.8635632183908046",
            "--roll", "-0.056385804597701185",
            "--pitch", "0.5833227586206899",
            "--yaw", "0.7622045977011492",
        ],
    )

    return LaunchDescription([
        use_sim_time_arg,
        start_camera_nvblox_transform_simulation,
        start_camera_nvblox_transform_real,
    ])
