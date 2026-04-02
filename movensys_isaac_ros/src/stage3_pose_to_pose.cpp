#include <rclcpp/rclcpp.hpp>
#include <cmath>
#include <vector>
#include <string>
#include <thread>
#include <chrono>
#include "moveit2_client.hpp"

bool runNvbloxDemo(const rclcpp::Node::SharedPtr& node, moveit2_client::MoveIt2Client& client, int delay_nvblox);

int main(int argc, char* argv[]) {
    rclcpp::init(argc, argv);

    auto node = std::make_shared<rclcpp::Node>("stage2_nvblox_cpp");

    rclcpp::executors::SingleThreadedExecutor executor;
    executor.add_node(node);
    std::thread spin_thread([&executor]() { executor.spin(); });

    moveit2_client::MoveIt2Client client(node, "movensys_manipulator_arm");

    client.base_name = "world_manipulator";
    client.link_name = "Link6";

    client.vel_scale = 1.0;
    client.acc_scale = 1.0;
    client.delay_exec = 0.3;
    
    client.delay_gripper = 1.0;
    client.max_step = 0.1;
    client.planning_time = 1.0;
    client.timeout = 1.0;
    client.planning_attempts = 5;
    client.replan = true;
    client.replan_attempts = 5;

    int delay_nvblox = 0.0;

    RCLCPP_INFO(node->get_logger(),
        "Config: base_name=%s, link_name=%s, vel_scale=%.2f, acc_scale=%.2f, "
        "max_step=%.2f, planning_time=%.2f, delay_exec=%.2f, delay_gripper=%.2f, timeout=%.2f, "
        "planning_attempts=%d, replan=%s, replan_attempts=%d",
        client.base_name.c_str(), client.link_name.c_str(),
        client.vel_scale, client.acc_scale, client.max_step,
        client.planning_time, client.delay_exec, client.delay_gripper, client.timeout,
        client.planning_attempts, client.replan ? "true" : "false", client.replan_attempts);

    runNvbloxDemo(node, client, delay_nvblox);

    executor.cancel();
    spin_thread.join();
    rclcpp::shutdown();
    return 0;
}

bool runNvbloxDemo(const rclcpp::Node::SharedPtr& node, moveit2_client::MoveIt2Client& client, int delay_nvblox) {
    RCLCPP_INFO(node->get_logger(), "------- Absolute Base EEF Cartesian -------");
    std::vector<moveit2_client::PoseTarget> cartesian_poses = {
                                                                {{-0.35, -0.1, 0.5}, {M_PI, 0.0, M_PI}}
    };
    for (const auto& target : cartesian_poses) {
        if (!client.absoluteBaseEefCartesian(target)) {
            RCLCPP_ERROR(node->get_logger(), "Absolute Base EEF Cartesian move failed");
            return false;
        }
    }

    std::this_thread::sleep_for(std::chrono::milliseconds(static_cast<int>(delay_nvblox * 1000)));

    RCLCPP_INFO(node->get_logger(), "------- Absolute Base EEF Joint Movement -------");
    const std::vector<moveit2_client::PoseTarget> absolute_base_eef_joint_movement_poses = {
        {{0.35, -0.1, 0.4}, {M_PI, 0.0, M_PI}},
        {{-0.35, -0.1, 0.4}, {M_PI, 0.0, M_PI}}
    };

    for(int i=0; i<2; i++){
        for (const auto& target : absolute_base_eef_joint_movement_poses) {
            if (!client.absoluteBaseEefJointMovement(target)) {
                RCLCPP_ERROR(node->get_logger(), "Move A failed");
                return false;
            }
        }   
    }

    RCLCPP_INFO(node->get_logger(), "------- NVBLOX DEMO COMPLETE -------");
    return true;
}
