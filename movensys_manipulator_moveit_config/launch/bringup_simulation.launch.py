from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    EnvironmentVariable,
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.substitutions import FindPackageShare


VALID_SIMULATORS = {"gazebo", "isaacsim"}
VALID_PLANNERS = {"moveit", "cumotion"}
VALID_MODELS = {"dobot_cr3a", "dobot_cr5a"}


def include_launch(package, filename, arguments):
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare(package),
                "launch",
                filename,
            ])
        ),
        launch_arguments=arguments.items(),
    )


def launch_setup(context):
    simulator = LaunchConfiguration("simulator").perform(context)
    planner = LaunchConfiguration("planner").perform(context)
    model = LaunchConfiguration("model").perform(context)

    if simulator not in VALID_SIMULATORS:
        raise RuntimeError(
            f"Invalid simulator '{simulator}'; "
            f"expected one of {sorted(VALID_SIMULATORS)}"
        )

    if planner not in VALID_PLANNERS:
        raise RuntimeError(
            f"Invalid planner '{planner}'; "
            f"expected one of {sorted(VALID_PLANNERS)}"
        )

    if model not in VALID_MODELS:
        raise RuntimeError(
            f"Invalid model '{model}'; "
            f"expected one of {sorted(VALID_MODELS)}"
        )

    common_arguments = {
        "model": model,
        "use_sim_time": "true",
    }

    actions = []

    if simulator == "gazebo":
        actions.append(
            include_launch(
                "movensys_manipulator_description",
                "gazebo_trajectory_simulation.launch.py",
                common_arguments,
            )
        )

    actions.append(
        include_launch(
            "movensys_manipulator_moveit_config",
            "sim_bridge.launch.py",
            {
                **common_arguments,
                "simulator": simulator,
            },
        )
    )

    planner_package = (
        "movensys_manipulator_moveit_config"
        if planner == "moveit"
        else "movensys_manipulator_isaac_ros_config"
    )
    planner_file = (
        "moveit.launch.py"
        if planner == "moveit"
        else "isaac_cumotion.launch.py"
    )

    actions.append(
        include_launch(
            planner_package,
            planner_file,
            {
                **common_arguments,
                "rsp": "false" if simulator == "gazebo" else "true",
            },
        )
    )

    return actions


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            "simulator",
            default_value="gazebo",
            description="gazebo or isaacsim",
        ),
        DeclareLaunchArgument(
            "planner",
            default_value="moveit",
            description="moveit or cumotion",
        ),
        DeclareLaunchArgument(
            "model",
            default_value=EnvironmentVariable(
                "MANIPULATOR_MODEL",
                default_value="dobot_cr3a",
            ),
            description="dobot_cr3a or dobot_cr5a",
        ),
        OpaqueFunction(function=launch_setup),
    ])