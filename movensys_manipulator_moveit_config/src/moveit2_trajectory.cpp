#include <rclcpp/rclcpp.hpp>
#include <cmath>
#include <vector>
#include <map>
#include "moveit2_client.hpp"

bool runTrajectory(const rclcpp::Node::SharedPtr& node, moveit2_client::MoveIt2Client& client);

int main(int argc, char* argv[]){
    rclcpp::init(argc, argv);

    auto node = std::make_shared<rclcpp::Node>("moveit2_trajectory_cpp");

    rclcpp::executors::SingleThreadedExecutor executor;
    executor.add_node(node);
    std::thread spin_thread([&executor]() { executor.spin(); });

    node->declare_parameter("base_name",         "world_manipulator");
    node->declare_parameter("link_name",         "Link6");
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

    moveit2_client::MoveIt2Client client(node, "movensys_manipulator_arm");

    client.base_name         = node->get_parameter("base_name").as_string();
    client.link_name         = node->get_parameter("link_name").as_string();
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
        "Config: base_name=%s, link_name=%s, vel_scale=%.2f, acc_scale=%.2f, "
        "max_step=%.2f, planning_time=%.2f, delay_exec=%.2f, delay_gripper=%.2f, timeout=%.2f",
        client.base_name.c_str(), client.link_name.c_str(),
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
    RCLCPP_INFO(node->get_logger(), "------- Absolute Base EEF Cartesian -------");
    std::vector<moveit2_client::PoseTarget> cartesian_poses = {
                                                                {{0.098, -0.071, 0.45}, {M_PI, 0.0, M_PI}},
                                                                {{0.098, 0.130, 0.45}, {M_PI, 0.0, M_PI}},
                                                                {{-0.23, 0.0, 0.450}, {M_PI, 0.0, M_PI}},
    };
    for (const auto& target : cartesian_poses) {
        if (!client.absoluteBaseEefCartesian(target)) {
            RCLCPP_ERROR(node->get_logger(), "Absolute Base EEF Cartesian move failed");
            return false;
        }
    }

    RCLCPP_INFO(node->get_logger(), "------- Relative Base EEF Cartesian -------");
    std::vector<moveit2_client::PoseTarget> relative_base_deltas = {
                                                                    {{-0.1, 0.0, 0.0}, {0.0, 0.0, M_PI/8}},
                                                                    {{0.1, 0.0, 0.0}, {0.0, 0.0, -M_PI/8}},
    };
    for (const auto& delta : relative_base_deltas) {
        if (!client.relativeBaseEefCartesian(delta)) {
            RCLCPP_ERROR(node->get_logger(), "Relative Base EEF Cartesian move failed");
            return false;
        }
    }

    RCLCPP_INFO(node->get_logger(), "------- Relative Tool EEF Cartesian -------");
    std::vector<moveit2_client::PoseTarget> relative_tool_deltas = {
                                                                    {{-0.1, 0.0, 0.0}, {0.0, 0.0, M_PI/8}},
                                                                    {{0.1, 0.0, 0.0}, {0.0, 0.0, -M_PI/8}},
    };
    for (const auto& delta : relative_tool_deltas) {
        if (!client.relativeToolEefCartesian(delta)) {
            RCLCPP_ERROR(node->get_logger(), "Relative Tool EEF Cartesian move failed");
            return false;
        }
    }

    RCLCPP_INFO(node->get_logger(), "------- Joint Movement -------");
    std::vector<std::map<std::string, double>> joint_poses = {
                                                                {{"joint1", 1.982}, {"joint2", 0.1325}, {"joint3", 0.9693},
                                                                {"joint4", 0.474}, {"joint5", -1.5697}, {"joint6", 0.4105}},
                                                                
                                                                {{"joint1", 0.5551}, {"joint2", -0.0225}, {"joint3", 1.135},
                                                                {"joint4", 0.4638}, {"joint5", -1.5708}, {"joint6", -1.0157}},
    };
    for (const auto& joints : joint_poses) {
        if (!client.jointMovement(joints)) {
            RCLCPP_ERROR(node->get_logger(), "Joint Movement move failed");
            return false;
        }
    }

    RCLCPP_INFO(node->get_logger(), "------- Absolute Base EEF Joint Movement -------");
    std::vector<moveit2_client::PoseTarget> joint_movement_poses = {
                                                                    {{0.23, 0.0, 0.450}, {M_PI, 0.0, M_PI}},
                                                                    {{-0.23, 0.0, 0.450}, {M_PI, 0.0, M_PI}},
    };
    for (const auto& target : joint_movement_poses) {
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