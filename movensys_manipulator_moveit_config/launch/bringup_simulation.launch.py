from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    sim_arg = DeclareLaunchArgument(
        'simulator',
        default_value='gazebo',
        description='Simulation engine: [gazebo, isaacsim]'
    )
    planner_arg = DeclareLaunchArgument(
        'planner',
        default_value='moveit',
        description='Motion planner: [moveit, cumotion]'
    )

    def launch_setup(context, *args, **kwargs):
        sim = LaunchConfiguration('simulator').perform(context)
        planner = LaunchConfiguration('planner').perform(context)

        # Gazebo 사용 시 자동으로 rsp=false 처리
        use_rsp = 'false' if sim == 'gazebo' else 'true'

        actions = []

        # 1. Gazebo 실행 (simulator=gazebo일 때만 자동 포함)
        if sim == 'gazebo':
            gazebo_launch = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    FindPackageShare('movensys_manipulator_description'),
                    '/launch/gazebo_trajectory_simulation.launch.py'
                ])
            )
            actions.append(gazebo_launch)

        # 2. Simulator Bridge 실행
        sim_bridge_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                FindPackageShare('movensys_manipulator_moveit_config'),
                '/launch/sim_bridge.launch.py'
            ]),
            launch_arguments={'simulator': sim, 'use_sim_time': 'true'}.items()
        )
        actions.append(sim_bridge_launch)

        # 3. Motion Planner 실행 (MoveIt2 or cuMotion)
        if planner == 'moveit':
            planner_launch = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    FindPackageShare('movensys_manipulator_moveit_config'),
                    '/launch/moveit.launch.py'
                ]),
                launch_arguments={'use_sim_time': 'true', 'rsp': use_rsp}.items()
            )
        else:
            planner_launch = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    FindPackageShare('movensys_manipulator_isaac_ros_config'),
                    '/launch/isaac_cumotion.launch.py'
                ]),
                launch_arguments={'use_sim_time': 'true', 'rsp': use_rsp}.items()
            )
        actions.append(planner_launch)

        return actions

    return LaunchDescription([
        sim_arg,
        planner_arg,
        OpaqueFunction(function=launch_setup)
    ])