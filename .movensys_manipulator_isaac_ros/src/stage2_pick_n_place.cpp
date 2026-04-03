#include <rclcpp/rclcpp.hpp>
#include <cmath>
#include <vector>
#include <string>
#include <thread>
#include <chrono>
#include <cstdlib>
#include "moveit2_client.hpp"

struct BoxPose {
    moveit2_client::PoseTarget up;
    moveit2_client::PoseTarget down;
};

bool runAprilTagPickPlace(const rclcpp::Node::SharedPtr& node, moveit2_client::MoveIt2Client& client, 
                          bool target_spawn);

int main(int argc, char* argv[]) {
    rclcpp::init(argc, argv);

    auto node = std::make_shared<rclcpp::Node>("stage3_apriltag_cpp");

    rclcpp::executors::SingleThreadedExecutor executor;
    executor.add_node(node);
    std::thread spin_thread([&executor]() { executor.spin(); });

    node->declare_parameter<bool>("target_spawn", true);
    bool target_spawn = node->get_parameter("target_spawn").as_bool();
    RCLCPP_INFO(node->get_logger(), "target_spawn: %s", target_spawn ? "true" : "false");

    moveit2_client::MoveIt2Client client(node, "movensys_manipulator_arm");

    client.base_name = "world_manipulator";
    client.link_name = "Link6";

    client.vel_scale = 1.0;
    client.acc_scale = 1.0;
    client.delay_exec = 0.4;
    
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

    runAprilTagPickPlace(node, client, target_spawn);

    executor.cancel();
    spin_thread.join();
    rclcpp::shutdown();
    return 0;
}

bool runAprilTagPickPlace(const rclcpp::Node::SharedPtr& node, moveit2_client::MoveIt2Client& client,
                          bool target_spawn) {
    const std::string camera_hand_link = "camera_hand_color_optical_frame";
    const std::vector<std::string> tag_ids = {
                                                "tag36h11:5",   // green
                                                "tag36h11:9",   // blue
                                                "tag36h11:7",   // grey
                                                "tag36h11:11",  // red
    };

    const std::vector<std::string> target_topic_name = {
                                                "/target1_sub",   // green
                                                "/target2_sub",   // blue
                                                "/target3_sub",   // grey
                                                "/target4_sub",  // red
    };

    const double z_target_pose = 0.07;

    const double tag_down_z = 0.21;
    const double tag_tol_pose = 0.03;
    const double tag_tol_orientation = 0.05;

    const double tag_to_target_x = 0.01;
    const double tag_to_target_y = -0.065;
    const double tag_to_target_yaw = 0.0;

    const moveit2_client::PoseTarget initial_pose = {{0.098, -0.071, 0.561}, {M_PI, 0.0, M_PI}};
    const moveit2_client::PoseTarget scan_pose = {{-0.23, -0.07, 0.5}, {M_PI, 0.0, M_PI}};

    const std::vector<BoxPose> box_poses = {
        // green
        {{{0.191, -0.1945, 0.50}, {3.141, 0.0, 3.108}},
         {{0.191, -0.1945, 0.295}, {3.141, 0.0, 3.108}}},
        
        // blue
        {{{0.299, -0.199, 0.50}, {3.141, 0.0, 3.108}},
         {{0.299, -0.199, 0.295}, {3.141, 0.0, 3.108}}},
        
        // yellow
        {{{0.1955, -0.039, 0.50}, {3.142, 0.0, 3.101}},
         {{0.1955, -0.039, 0.295}, {3.142, 0.0, 3.101}}},
        
        // red
        {{{0.303, -0.042, 0.50}, {3.142, 0.0, 3.104}},
         {{0.303, -0.042, 0.295}, {3.142, 0.0, 3.104}}},
    };

    RCLCPP_INFO(node->get_logger(), "------- START CYCLE -------");

    // Initial pose
    if (!client.absoluteBaseEefCartesian(initial_pose)) {
        RCLCPP_ERROR(node->get_logger(), "Move to initial pose failed");
        return false;
    }

    // Gripper open
    if (!client.setGripper(false)) {
        RCLCPP_ERROR(node->get_logger(), "Failed to open gripper");
        return false;
    }

    for (size_t i = 0; i < tag_ids.size(); ++i) {
        RCLCPP_INFO(node->get_logger(), "[%zu/%zu] Running target id = %s", i + 1, tag_ids.size(), tag_ids[i].c_str());

        // Scan pose
        if (!client.absoluteBaseEefCartesian(scan_pose)) {
            RCLCPP_ERROR(node->get_logger(), "Move to scan pose failed");
            return false;
        }

        double x_tag = 0.0, y_tag = 0.0, yaw_tag = 0.0;

        // Tag tracking loop
        while (rclcpp::ok()) {
            auto tf_result = client.lookupTF(camera_hand_link, tag_ids[i]);

            if (!tf_result.has_value()) {
                RCLCPP_WARN(node->get_logger(), "No TF for tag, retrying...");
                std::this_thread::sleep_for(std::chrono::milliseconds(100));
                continue;
            }

            x_tag = tf_result->x;
            y_tag = tf_result->y;
            yaw_tag = tf_result->yaw;

            // Stop if close enough
            if (std::abs(x_tag) < tag_tol_pose && std::abs(y_tag) < tag_tol_pose && std::abs(yaw_tag) < tag_tol_orientation) {
                RCLCPP_INFO(node->get_logger(), "##### Converged to tag. #####");
                break;
            }

            // Tracking movement tool to center tag
            moveit2_client::PoseTarget delta_pose = {{x_tag, y_tag, 0.0}, {0.0, 0.0, yaw_tag}};
            if (!client.relativeToolEefCartesian(delta_pose)) {
                RCLCPP_ERROR(node->get_logger(), "Tracking movement failed");
                return false;
            }
        }

        if (!rclcpp::ok()) {
            RCLCPP_WARN(node->get_logger(), "Shutdown requested, aborting.");
            return false;
        }

        // Move tool to center target (with offset from tag center)
        moveit2_client::PoseTarget target_offset = {
            {tag_to_target_x + x_tag, tag_to_target_y + y_tag, 0.0},
            {0.0, 0.0, tag_to_target_yaw + yaw_tag}
        };
        if (!client.relativeToolEefCartesian(target_offset)) {
            RCLCPP_ERROR(node->get_logger(), "Move to target center failed");
            return false;
        }










        // Teleport target in Isaac Sim (only if target_spawn is enabled)
        if (target_spawn) {
            // Get current EEF pose using MoveIt getCurrentState
            auto eef_tf = client.getCurrentEefPose();
            if (!eef_tf.has_value()) {
                RCLCPP_ERROR(node->get_logger(), "Failed to get current EEF pose");
                return false;
            }

            // Apply +90 deg Z rotation (EEF frame to target frame)
            // Position: x_target = -y_eef, y_target = x_eef
            double x_eef = -eef_tf->y;
            double y_eef = eef_tf->x;

            // Format pose string for Isaac Sim teleport
            std::string pose_str = "{position: {x: " + std::to_string(x_eef) +
                                   ", y: " + std::to_string(y_eef) +
                                   ", z: " + std::to_string(z_target_pose) + "}" +
                                   ", orientation: {x: " + std::to_string(eef_tf->qx) +
                                   ", y: " + std::to_string(eef_tf->qy) +
                                   ", z: " + std::to_string(eef_tf->qz) +
                                   ", w: " + std::to_string(eef_tf->qw) + "}}";

            RCLCPP_INFO(node->get_logger(), "Teleport target pose in Isaac Sim: %s", pose_str.c_str());

            // Publish pose to target topic
            std::string cmd = "ros2 topic pub -1 " + target_topic_name[i] +
                              " geometry_msgs/msg/Pose \"" + pose_str + "\"";
            int result = std::system(cmd.c_str());
            RCLCPP_INFO(node->get_logger(), "ros2 topic pub result: %d", result);
        }










        // Target down pose
        moveit2_client::PoseTarget down_delta = {{0.0, 0.0, -tag_down_z}, {0.0, 0.0, 0.0}};
        if (!client.relativeBaseEefCartesian(down_delta)) {
            RCLCPP_ERROR(node->get_logger(), "Move down failed");
            return false;
        }

        // Gripper close
        if (!client.setGripper(true)) {
            RCLCPP_ERROR(node->get_logger(), "Failed to close gripper");
            return false;
        }

        // Target up pose
        moveit2_client::PoseTarget up_delta = {{0.0, 0.0, tag_down_z}, {0.0, 0.0, 0.0}};
        if (!client.relativeBaseEefCartesian(up_delta)) {
            RCLCPP_ERROR(node->get_logger(), "Move up failed");
            return false;
        }

        // Box up pose
        if (!client.absoluteBaseEefCartesian(box_poses[i].up)) {
            RCLCPP_ERROR(node->get_logger(), "Move to box up pose failed");
            return false;
        }

        // Box down pose
        if (!client.absoluteBaseEefCartesian(box_poses[i].down)) {
            RCLCPP_ERROR(node->get_logger(), "Move to box down pose failed");
            return false;
        }

        // Gripper open
        if (!client.setGripper(false)) {
            RCLCPP_ERROR(node->get_logger(), "Failed to open gripper");
            return false;
        }

        // Box up pose (return)
        if (!client.absoluteBaseEefCartesian(box_poses[i].up)) {
            RCLCPP_ERROR(node->get_logger(), "Move to box up pose (return) failed");
            return false;
        }
    }

    RCLCPP_INFO(node->get_logger(), "------- STOP CYCLE -------");
    return true;
}
