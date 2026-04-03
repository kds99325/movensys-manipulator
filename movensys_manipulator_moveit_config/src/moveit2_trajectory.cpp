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

    moveit2_client::MoveIt2Client client(node, "movensys_manipulator_arm");

    client.base_name = "world_manipulator";
    client.link_name = "Link6";

    client.vel_scale = 0.3;
    client.acc_scale = 0.3;
    client.delay_exec = 0.1;
    
    client.delay_gripper = 1.0;
    client.max_step = 0.1;
    client.planning_time = 1.0;
    client.timeout = 1.0;
    client.planning_attempts = 5;
    client.replan = true;
    client.replan_attempts = 5;

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
                                                                {{0.098, -0.071, 0.561}, {M_PI, 0.0, M_PI}},
                                                                {{-0.23, -0.07, 0.5}, {M_PI, 0.0, M_PI}},
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
                                                                {{"joint1", 1.915}, {"joint2", 0.2696}, {"joint3", 1.5353},
                                                                {"joint4", -0.2303}, {"joint5", -1.5708}, {"joint6", 0.3443}},
                                                                
                                                                {{"joint1", 0.7178}, {"joint2", 0.1456}, {"joint3", 1.6902},
                                                                {"joint4", -0.2614}, {"joint5", -1.5708}, {"joint6", -0.8529}},
    };
    for (const auto& joints : joint_poses) {
        if (!client.jointMovement(joints)) {
            RCLCPP_ERROR(node->get_logger(), "Joint Movement move failed");
            return false;
        }
    }

    RCLCPP_INFO(node->get_logger(), "------- Absolute Base EEF Joint Movement -------");
    std::vector<moveit2_client::PoseTarget> joint_movement_poses = {
                                                                    {{0.23, -0.07, 0.5}, {M_PI, 0.0, M_PI}},
                                                                    {{-0.23, -0.07, 0.5}, {M_PI, 0.0, M_PI}},
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