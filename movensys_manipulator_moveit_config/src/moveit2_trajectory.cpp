#include <rclcpp/rclcpp.hpp>
#include <cmath>
#include <vector>
#include <map>
#include "moveit2_client.hpp"

bool runTrajectory(const rclcpp::Node::SharedPtr& node, moveit2_client::MoveIt2Client& client);

// Parse a flat [x,y,z,rx,ry,rz, ...] vector into PoseTarget list
static std::vector<moveit2_client::PoseTarget> parsePoses(const std::vector<double>& flat)
{
    std::vector<moveit2_client::PoseTarget> poses;
    for (size_t i = 0; i + 5 < flat.size(); i += 6)
        poses.push_back({{flat[i], flat[i+1], flat[i+2]}, {flat[i+3], flat[i+4], flat[i+5]}});
    return poses;
}

// Parse a flat [j1,j2,...,jN, j1,j2,...,jN, ...] vector into joint map list
static std::vector<std::map<std::string, double>> parseJointPoses(
    const std::vector<double>& flat, const std::vector<std::string>& names)
{
    std::vector<std::map<std::string, double>> result;
    const size_t n = names.size();
    for (size_t i = 0; i + n <= flat.size(); i += n) {
        std::map<std::string, double> m;
        for (size_t j = 0; j < n; ++j) m[names[j]] = flat[i + j];
        result.push_back(m);
    }
    return result;
}

int main(int argc, char* argv[]){
    rclcpp::init(argc, argv);

    auto node = std::make_shared<rclcpp::Node>("moveit2_trajectory_cpp");

    rclcpp::executors::SingleThreadedExecutor executor;
    executor.add_node(node);
    std::thread spin_thread([&executor]() { executor.spin(); });

    // MoveIt client config
    node->declare_parameter("base_name",         "world_manipulator");
    node->declare_parameter("eef_name",          "Link6");
    node->declare_parameter("vel_scale",         0.3);
    node->declare_parameter("acc_scale",         0.3);
    node->declare_parameter("delay_exec",        0.1);
    node->declare_parameter("delay_gripper",     1.0);
    node->declare_parameter("max_step",          0.1);
    node->declare_parameter("planning_time",     1.0);
    node->declare_parameter("timeout",           1.0);
    node->declare_parameter("planning_attempts", 5);
    node->declare_parameter("replan",            true);
    node->declare_parameter("replan_attempts",   5);

    // Trajectory waypoints — each pose: [x, y, z, roll, pitch, yaw]
    node->declare_parameter("pose_initial",
        std::vector<double>{0.098, -0.071, 0.45, M_PI, 0.0, M_PI});

    node->declare_parameter("cartesian_poses",
        std::vector<double>{ 0.098,  0.130, 0.450, M_PI, 0.0, M_PI,
                            -0.230,  0.000, 0.450, M_PI, 0.0, M_PI});

    node->declare_parameter("relative_base_deltas",
        std::vector<double>{-0.1, 0.0, 0.0, 0.0, 0.0,  M_PI/8,
                             0.1, 0.0, 0.0, 0.0, 0.0, -M_PI/8});

    node->declare_parameter("relative_tool_deltas",
        std::vector<double>{-0.1, 0.0, 0.0, 0.0, 0.0,  M_PI/8,
                             0.1, 0.0, 0.0, 0.0, 0.0, -M_PI/8});

    // Joint waypoints — flat list: [j1,j2,j3,j4,j5,j6, j1,j2,j3,j4,j5,j6, ...]
    node->declare_parameter("joint_names",
        std::vector<std::string>{"joint1","joint2","joint3","joint4","joint5","joint6"});

    node->declare_parameter("joint_poses",
        std::vector<double>{ 3.5519,  0.1319, 0.9702,  0.4732, -1.5703,  0.4102,
                             2.1251, -0.0225, 1.1350,  0.4638, -1.5708, -1.0157});

    node->declare_parameter("joint_movement_poses",
        std::vector<double>{ 0.230, 0.0, 0.450, M_PI, 0.0, M_PI,
                            -0.230, 0.0, 0.450, M_PI, 0.0, M_PI});

    moveit2_client::MoveIt2Client client(node, "movensys_manipulator_arm");

    client.base_name         = node->get_parameter("base_name").as_string();
    client.eef_name         = node->get_parameter("eef_name").as_string();
    client.vel_scale         = node->get_parameter("vel_scale").as_double();
    client.acc_scale         = node->get_parameter("acc_scale").as_double();
    client.delay_exec        = node->get_parameter("delay_exec").as_double();
    client.delay_gripper     = node->get_parameter("delay_gripper").as_double();
    client.max_step          = node->get_parameter("max_step").as_double();
    client.planning_time     = node->get_parameter("planning_time").as_double();
    client.timeout           = node->get_parameter("timeout").as_double();
    client.planning_attempts = node->get_parameter("planning_attempts").as_int();
    client.replan            = node->get_parameter("replan").as_bool();
    client.replan_attempts   = node->get_parameter("replan_attempts").as_int();

    RCLCPP_INFO(node->get_logger(),
        "Config: base_name=%s, eef_name=%s, vel_scale=%.2f, acc_scale=%.2f, "
        "max_step=%.2f, planning_time=%.2f, delay_exec=%.2f, delay_gripper=%.2f, timeout=%.2f",
        client.base_name.c_str(), client.eef_name.c_str(),
        client.vel_scale, client.acc_scale, client.max_step,
        client.planning_time, client.delay_exec, client.delay_gripper, client.timeout);

    runTrajectory(node, client);

    executor.cancel();
    spin_thread.join();
    rclcpp::shutdown();
    return 0;
}

bool runTrajectory(const rclcpp::Node::SharedPtr& node, moveit2_client::MoveIt2Client& client)
{
    const auto joint_names         = node->get_parameter("joint_names").as_string_array();
    const auto pose_initial_flat   = node->get_parameter("pose_initial").as_double_array();
    const auto cartesian_flat      = node->get_parameter("cartesian_poses").as_double_array();
    const auto rel_base_flat       = node->get_parameter("relative_base_deltas").as_double_array();
    const auto rel_tool_flat       = node->get_parameter("relative_tool_deltas").as_double_array();
    const auto joint_poses_flat    = node->get_parameter("joint_poses").as_double_array();
    const auto joint_mov_flat      = node->get_parameter("joint_movement_poses").as_double_array();

    RCLCPP_INFO(node->get_logger(), "------- Absolute Base EEF Joint Movement -------");
    for (const auto& target : parsePoses(pose_initial_flat)) {
        if (!client.absoluteBaseEefJointMovement(target)) {
            RCLCPP_ERROR(node->get_logger(), "Absolute Base EEF Joint Movement failed");
            return false;
        }
    }

    RCLCPP_INFO(node->get_logger(), "------- Absolute Base EEF Cartesian -------");
    for (const auto& target : parsePoses(cartesian_flat)) {
        if (!client.absoluteBaseEefCartesian(target)) {
            RCLCPP_ERROR(node->get_logger(), "Absolute Base EEF Cartesian move failed");
            return false;
        }
    }

    RCLCPP_INFO(node->get_logger(), "------- Relative Base EEF Cartesian -------");
    for (const auto& delta : parsePoses(rel_base_flat)) {
        if (!client.relativeBaseEefCartesian(delta)) {
            RCLCPP_ERROR(node->get_logger(), "Relative Base EEF Cartesian move failed");
            return false;
        }
    }

    RCLCPP_INFO(node->get_logger(), "------- Relative Tool EEF Cartesian -------");
    for (const auto& delta : parsePoses(rel_tool_flat)) {
        if (!client.relativeToolEefCartesian(delta)) {
            RCLCPP_ERROR(node->get_logger(), "Relative Tool EEF Cartesian move failed");
            return false;
        }
    }

    RCLCPP_INFO(node->get_logger(), "------- Joint Movement -------");
    for (const auto& joints : parseJointPoses(joint_poses_flat, joint_names)) {
        if (!client.jointMovement(joints)) {
            RCLCPP_ERROR(node->get_logger(), "Joint Movement move failed");
            return false;
        }
    }

    RCLCPP_INFO(node->get_logger(), "------- Absolute Base EEF Joint Movement -------");
    for (const auto& target : parsePoses(joint_mov_flat)) {
        if (!client.absoluteBaseEefJointMovement(target)) {
            RCLCPP_ERROR(node->get_logger(), "Absolute Base EEF Joint Movement failed");
            return false;
        }
    }

    RCLCPP_INFO(node->get_logger(), "------- Gripper Service -------");
    client.setGripper(true);
    client.setGripper(false);

    RCLCPP_INFO(node->get_logger(), "All movements completed!");
    return true;
}