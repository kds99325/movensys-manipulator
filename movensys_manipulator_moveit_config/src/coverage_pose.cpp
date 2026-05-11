#include <rclcpp/rclcpp.hpp>
#include <cmath>
#include <vector>
#include <map>
#include <string>
#include "moveit2_client.hpp"

bool runCoverage(const rclcpp::Node::SharedPtr& node, moveit2_client::MoveIt2Client& client);

int main(int argc, char* argv[]){
    rclcpp::init(argc, argv);

    auto node = std::make_shared<rclcpp::Node>("coverage_pose");

    rclcpp::executors::SingleThreadedExecutor executor;
    executor.add_node(node);
    std::thread spin_thread([&executor]() { executor.spin(); });

    // MoveIt client config
    node->declare_parameter("base_name",         "base");
    node->declare_parameter("eef_name",          "eef");
    node->declare_parameter("vel_scale",         0.0);
    node->declare_parameter("acc_scale",         0.0);
    node->declare_parameter("delay_exec",        0.0);
    node->declare_parameter("delay_gripper",     0.0);
    node->declare_parameter("max_step",          0.0);
    node->declare_parameter("planning_time",     0.0);
    node->declare_parameter("timeout",           0.0);
    node->declare_parameter("planning_attempts", 0);
    node->declare_parameter("replan",            true);
    node->declare_parameter("replan_attempts",   0);

    // Coverage waypoints
    node->declare_parameter("joint_names",      std::vector<std::string>{"j1","j2","j3","j4","j5","j6"});
    node->declare_parameter("joint_initial_0",  std::vector<double>(6, 0.0));

    node->declare_parameter("coverage_poses_0", std::vector<double>(6, 0.0));
    node->declare_parameter("coverage_poses_1", std::vector<double>(6, 0.0));
    node->declare_parameter("coverage_poses_2", std::vector<double>(6, 0.0));
    node->declare_parameter("coverage_poses_3", std::vector<double>(6, 0.0));
    node->declare_parameter("coverage_poses_4", std::vector<double>(6, 0.0));
    node->declare_parameter("coverage_poses_5", std::vector<double>(6, 0.0));

    moveit2_client::MoveIt2Client client(node, "movensys_manipulator_arm");

    client.base_name         = node->get_parameter("base_name").as_string();
    client.eef_name          = node->get_parameter("eef_name").as_string();
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

    runCoverage(node, client);

    executor.cancel();
    spin_thread.join();
    rclcpp::shutdown();
    return 0;
}

static moveit2_client::PoseTarget toPose(const std::vector<double>& v)
{
    return {{v[0], v[1], v[2]}, {v[3], v[4], v[5]}};
}

static std::map<std::string, double> toJointMap(
    const std::vector<double>& v, const std::vector<std::string>& names)
{
    std::map<std::string, double> m;
    for (size_t i = 0; i < names.size(); ++i) m[names[i]] = v[i];
    return m;
}

bool runCoverage(const rclcpp::Node::SharedPtr& node, moveit2_client::MoveIt2Client& client)
{
    const auto joint_names = node->get_parameter("joint_names").as_string_array();

    RCLCPP_INFO(node->get_logger(), "------- Initial Joint Movement -------");
    if (!client.jointMovement(toJointMap(node->get_parameter("joint_initial_0").as_double_array(), joint_names))) {
        RCLCPP_ERROR(node->get_logger(), "Initial Joint Movement failed"); return false; }

    const std::vector<std::string> pose_params = {
        "coverage_poses_0", "coverage_poses_1", "coverage_poses_2",
        "coverage_poses_3", "coverage_poses_4", "coverage_poses_5"
    };

    RCLCPP_INFO(node->get_logger(), "------- Coverage Cartesian Sweep -------");
    for (const auto& name : pose_params) {
        RCLCPP_INFO(node->get_logger(), "Moving to %s", name.c_str());
        if (!client.absoluteBaseEefCartesian(toPose(node->get_parameter(name).as_double_array()))) {
            RCLCPP_ERROR(node->get_logger(), "Coverage move to %s failed", name.c_str()); return false;
        }
    }

    RCLCPP_INFO(node->get_logger(), "Coverage sweep completed!");
    return true;
}
