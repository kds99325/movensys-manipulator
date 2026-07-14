// Copyright 2026 Movensys Corporation.
// Licensed under the MIT License. See LICENSE.txt for details.

#include <atomic>
// std::chrono::nanoseconds
#include <chrono>
// for using std::bind
#include <functional>
#include <iomanip>
#include <memory>
// std::ostringstream
#include <sstream>
#include <string>
#include <thread>
#include <vector>
#include <algorithm>

// topic, service, action
#include "rclcpp/rclcpp.hpp"
// action server/client
#include "rclcpp_action/rclcpp_action.hpp"
// moveit2's joint trajectory
#include "control_msgs/action/follow_joint_trajectory.hpp"
#include "trajectory_msgs/msg/joint_trajectory.hpp"
#include "trajectory_msgs/msg/joint_trajectory_point.hpp"
// joint state for robot's status & command
#include "control_msgs/msg/joint_jog.hpp"
#include "sensor_msgs/msg/joint_state.hpp"
#include "std_msgs/msg/float64_multi_array.hpp"
#include "std_srvs/srv/set_bool.hpp"

// alias
using FollowJT = control_msgs::action::FollowJointTrajectory;
using GoalHandleFJT = rclcpp_action::ServerGoalHandle<FollowJT>;
using namespace std::chrono_literals;

// Get class from rclcpp::Node
class GazeboBridge : public rclcpp::Node {
public:
  std::vector<std::string> arm_joint_names_;
  std::vector<std::string> gripper_joint_names_;

  double gripper_state_ = 0.0;
  double gripper_open_  = 0.0;
  double gripper_close_ = 0.0;

  sensor_msgs::msg::JointState last_joint_state;

  rclcpp::Publisher<std_msgs::msg::Float64MultiArray>::SharedPtr pub_joint_command_;
  rclcpp::Subscription<sensor_msgs::msg::JointState>::SharedPtr sub_joint_state_;
  rclcpp::Service<std_srvs::srv::SetBool>::SharedPtr setGripperService_;
  rclcpp::Subscription<trajectory_msgs::msg::JointTrajectory>::SharedPtr sub_servo_;

  GazeboBridge() : Node("gazebo_bridge") {
    // Declare parameters
    this->declare_parameter("arm_joint_names",
        std::vector<std::string>{"j1", "j2", "j3", "j4", "j5", "j6"});
    this->declare_parameter("gripper_joint_names", std::vector<std::string>{});
    this->declare_parameter("gripper_open",  0.000);
    this->declare_parameter("gripper_close", 0.000);
    this->declare_parameter("joint_command_topic", "/joint_command_topic/no_topic");
    this->declare_parameter("joint_states_topic",  "/joint_states_topic/no_topic");
    this->declare_parameter("set_gripper_service", "/set_gripper_service/no_topic");
    this->declare_parameter("action_name", "/action_name/no_action");
    this->declare_parameter("servo_command_topic", "/servo_command_topic/no_topic");

    // Fetch parameters
    arm_joint_names_     = this->get_parameter("arm_joint_names").as_string_array();
    gripper_joint_names_ = this->get_parameter("gripper_joint_names").as_string_array();
    gripper_open_        = this->get_parameter("gripper_open").as_double();
    gripper_close_       = this->get_parameter("gripper_close").as_double();
    const auto joint_command_topic = this->get_parameter("joint_command_topic").as_string();
    const auto joint_states_topic  = this->get_parameter("joint_states_topic").as_string();
    const auto set_gripper_service = this->get_parameter("set_gripper_service").as_string();
    const auto action_name         = this->get_parameter("action_name").as_string();
    const auto servo_command_topic = this->get_parameter("servo_command_topic").as_string();

    // Create interfaces
    pub_joint_command_ = this->create_publisher<std_msgs::msg::Float64MultiArray>(
        joint_command_topic, 10);
    sub_joint_state_   = this->create_subscription<sensor_msgs::msg::JointState>(
        joint_states_topic,
        10, std::bind(&GazeboBridge::cb, this, std::placeholders::_1));

    setGripperService_ = this->create_service<std_srvs::srv::SetBool>(set_gripper_service,
                                std::bind(&GazeboBridge::setGripper, this,
                                std::placeholders::_1, std::placeholders::_2));

    action_server_ = rclcpp_action::create_server<FollowJT>(
        this,
        action_name,
        std::bind(&GazeboBridge::handle_goal,     this,
                  std::placeholders::_1, std::placeholders::_2),
        std::bind(&GazeboBridge::handle_cancel,   this, std::placeholders::_1),
        std::bind(&GazeboBridge::handle_accepted, this, std::placeholders::_1));

    sub_servo_ = this->create_subscription<trajectory_msgs::msg::JointTrajectory>(
        servo_command_topic, 10,
        std::bind(&GazeboBridge::cbServoCommand, this, std::placeholders::_1));

    pub_servo_reset_ = this->create_publisher<control_msgs::msg::JointJog>(
        "/servo_node/delta_joint_cmds", 10);

    RCLCPP_INFO(this->get_logger(), "gazebo_bridge is ready");
  }

private:
  rclcpp_action::Server<FollowJT>::SharedPtr action_server_;

  // Servo is rejected while a move_group trajectory executes, accepted otherwise.
  std::atomic<bool> in_execution_{false};
  rclcpp::Publisher<control_msgs::msg::JointJog>::SharedPtr pub_servo_reset_;

  void resetServo() {
    control_msgs::msg::JointJog jog;
    jog.header.stamp = this->get_clock()->now();
    jog.joint_names = arm_joint_names_;
    jog.velocities.assign(arm_joint_names_.size(), 0.0);
    pub_servo_reset_->publish(jog);
  }

  // What is the purpose of this line?
  void cb(const sensor_msgs::msg::JointState::SharedPtr msg_in)
  {
    last_joint_state = *msg_in;
  }

  void cbServoCommand(const trajectory_msgs::msg::JointTrajectory::SharedPtr msg) {
    if (msg->points.empty() || in_execution_.load()) {
      return;  // reject servo while a move_group plan is executing
    }
    // Servo streams short trajectories; the last point is the freshest target.
    const auto& pt = msg->points.back();

    const size_t n_arm   = arm_joint_names_.size();
    const size_t n_total = n_arm + gripper_joint_names_.size();

    std_msgs::msg::Float64MultiArray joint_command;
    joint_command.data.resize(n_total);

    for (size_t j = 0; j < pt.positions.size() && j < n_arm; ++j) {
      joint_command.data[j] = pt.positions[j];
    }
    for (size_t j = 0; j < gripper_joint_names_.size(); ++j) {
      joint_command.data[n_arm + j] = gripper_state_;
    }

    pub_joint_command_->publish(joint_command);
  }

  // If we get a gripper-open request -> open gripper
  void setGripper(const std::shared_ptr<std_srvs::srv::SetBool::Request> request,
                          std::shared_ptr<std_srvs::srv::SetBool::Response> response) {
    gripper_state_    = request->data ? gripper_close_ : gripper_open_;
    response->success = true;

    const size_t n_arm   = arm_joint_names_.size();
    const size_t n_total = n_arm + gripper_joint_names_.size();

    std_msgs::msg::Float64MultiArray joint_command;
    joint_command.data.resize(n_total);

    // Copy current positions from last_joint_state by name to handle distro-specific joint order
    for (size_t i = 0; i < n_arm; ++i) {
      auto it = std::find(
          last_joint_state.name.begin(), last_joint_state.name.end(), arm_joint_names_[i]);
      if (it != last_joint_state.name.end()) {
        size_t idx = std::distance(last_joint_state.name.begin(), it);
        joint_command.data[i] = last_joint_state.position[idx];
      }
    }

    // Set gripper positions
    for (size_t i = 0; i < gripper_joint_names_.size(); ++i) {
      joint_command.data[n_arm + i] = gripper_state_;
    }

    pub_joint_command_->publish(joint_command);
    RCLCPP_INFO(this->get_logger(), "Gripper: %s", request->data ? "close" : "open");
  }

  rclcpp_action::GoalResponse handle_goal(
      const rclcpp_action::GoalUUID&,
      std::shared_ptr<const FollowJT::Goal> goal)
  {
    (void)goal;
    return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;
  }

  rclcpp_action::CancelResponse handle_cancel(const std::shared_ptr<GoalHandleFJT>) {
    return rclcpp_action::CancelResponse::ACCEPT;
  }

  // If we get a goal -> then execute()
  void handle_accepted(const std::shared_ptr<GoalHandleFJT> goal_handle) {
    std::thread(&GazeboBridge::execute, this, goal_handle).detach();
  }

  void execute(const std::shared_ptr<GoalHandleFJT> goal_handle){
    in_execution_ = true;   // reject servo while this plan executes
    // which repo have information about moveit2's trajectory?
    RCLCPP_INFO(this->get_logger(), "Received a new trajectory goal!");
    const auto goal = goal_handle->get_goal();
    const auto& traj = goal->trajectory;

    // Log joint names
    std::ostringstream jn;
    for (size_t i = 0; i < traj.joint_names.size(); ++i) {
      if (i) {
        jn << ", ";
      }
      jn << traj.joint_names[i];
    }
    RCLCPP_INFO(this->get_logger(), "Joint Names: [%s]", jn.str().c_str());

    // Log points
    for (size_t i = 0; i < traj.points.size(); ++i) {
      const auto &pt = traj.points[i];
      std::ostringstream pos, vel, acc;
      for (size_t k = 0; k < pt.positions.size(); ++k) {
        if (k) { pos << ", "; }
        pos << pt.positions[k];
      }
      for (size_t k = 0; k < pt.velocities.size(); ++k) {
        if (k) { vel << ", "; }
        vel << pt.velocities[k];
      }
      for (size_t k = 0; k < pt.accelerations.size(); ++k) {
        if (k) { acc << ", "; }
        acc << pt.accelerations[k];
      }
      RCLCPP_INFO(
        this->get_logger(),
        "Point %zu: Positions: [%s], Velocities: [%s], Accelerations: [%s], "
        "TimeFromStart: %d s %u ns",
        i, pos.str().c_str(), vel.str().c_str(), acc.str().c_str(),
        pt.time_from_start.sec, pt.time_from_start.nanosec);
      if (i != 0) {
        rclcpp::Duration duration_cur(traj.points[i].time_from_start);
        rclcpp::Duration duration_pre(traj.points[i-1].time_from_start);
        // we can get moving time (current - previous joint)
        RCLCPP_INFO(
          this->get_logger(),
          "Time interval: %f",
          (duration_cur-duration_pre).seconds());
      }
    }

    const size_t n_arm   = arm_joint_names_.size();
    const size_t n_total = n_arm + gripper_joint_names_.size();

    for (size_t i = 0; i < traj.points.size(); ++i) {
      const auto& pt = traj.points[i];

      // publish command
      std_msgs::msg::Float64MultiArray joint_command;
      joint_command.data.resize(n_total);

      // Copy positions from trajectory point
      for (size_t j = 0; j < pt.positions.size() && j < n_arm; ++j) {
        joint_command.data[j] = pt.positions[j];
      }

      // Set gripper positions
      for (size_t j = 0; j < gripper_joint_names_.size(); ++j) {
        joint_command.data[n_arm + j] = gripper_state_;
      }

      pub_joint_command_->publish(joint_command);

      if (i + 1 < traj.points.size()) {
        // time bottlenect is from moveit2.
        // Can we set a start time? -> but seems dangerous if we set traj-time to certain value.
        rclcpp::Duration t1(traj.points[i].time_from_start);
        rclcpp::Duration t2(traj.points[i+1].time_from_start);

        rclcpp::Duration dt = t2 - t1;

        std::this_thread::sleep_for(std::chrono::nanoseconds(dt.nanoseconds()));
      }
    }

    auto result = std::make_shared<FollowJT::Result>();
    result->error_code = 0;
    goal_handle->succeed(result);
    in_execution_ = false;  // done -> servo accepted again
    resetServo();           // re-anchor servo to the current pose (no snap-back)
  }
};

int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<GazeboBridge>());
  rclcpp::shutdown();
  return 0;
}
