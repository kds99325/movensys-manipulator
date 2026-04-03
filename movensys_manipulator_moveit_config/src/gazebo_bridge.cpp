// std::chrono::nanoseconds
#include <chrono>
#include <thread>
#include <vector>
#include <string>
// for using std::bind
#include <functional>
// std::ostringstream
#include <sstream>
#include <iomanip>

// topic, service, action
#include "rclcpp/rclcpp.hpp"
// action server/client
#include "rclcpp_action/rclcpp_action.hpp"
// moveit2's joint trajectory
#include "control_msgs/action/follow_joint_trajectory.hpp"
#include "trajectory_msgs/msg/joint_trajectory.hpp"
#include "trajectory_msgs/msg/joint_trajectory_point.hpp"
// joint state for robot's status & command
#include "sensor_msgs/msg/joint_state.hpp"
#include "std_msgs/msg/float64_multi_array.hpp"
#include "std_srvs/srv/set_bool.hpp"

// alias
using FollowJT = control_msgs::action::FollowJointTrajectory;
using GoalHandleFJT = rclcpp_action::ServerGoalHandle<FollowJT>;
using namespace std::chrono_literals;

// Get class from rclcpp::Node
class SimulationAction : public rclcpp::Node {
public:
  double gripper_state_ = 0.000;

  sensor_msgs::msg::JointState last_joint_state;

  std::vector<std::string> joint_names_{"joint1","joint2","joint3","joint4","joint5","joint6","picker_1_joint","picker_2_joint"};

  rclcpp::Publisher<std_msgs::msg::Float64MultiArray>::SharedPtr pub_joint_command_;
  rclcpp::Subscription<sensor_msgs::msg::JointState>::SharedPtr sub_joint_state_;
  rclcpp::Service<std_srvs::srv::SetBool>::SharedPtr setGripperService_;

  SimulationAction() : Node("gazebo_bridge") {
    // Publisher for gazebo_position_controller commands (Float64MultiArray)
    pub_joint_command_ = this->create_publisher<std_msgs::msg::Float64MultiArray>("/gazebo_position_controller/commands", 10);
    sub_joint_state_ = this->create_subscription<sensor_msgs::msg::JointState>("/joint_states",
                        10, std::bind(&SimulationAction::cb, this, std::placeholders::_1));

    setGripperService_ = this->create_service<std_srvs::srv::SetBool>("/wmx/set_gripper",
                                std::bind(&SimulationAction::setGripper, this,
                                std::placeholders::_1, std::placeholders::_2));

    action_server_ = rclcpp_action::create_server<FollowJT>(
        this,
        "/movensys_manipulator_arm_controller/follow_joint_trajectory",
        std::bind(&SimulationAction::handle_goal, this, std::placeholders::_1, std::placeholders::_2),
        std::bind(&SimulationAction::handle_cancel, this, std::placeholders::_1),
        std::bind(&SimulationAction::handle_accepted, this, std::placeholders::_1));

    RCLCPP_INFO(this->get_logger(), "gazebo_bridge is ready");
  }

private:
  rclcpp_action::Server<FollowJT>::SharedPtr action_server_;

  // What is the purpose of this line?
  void cb(const sensor_msgs::msg::JointState::SharedPtr msg_in)
  {
    last_joint_state = *msg_in;
  }

  // If we get a gripper-open request -> open gripper
  void setGripper(const std::shared_ptr<std_srvs::srv::SetBool::Request> request,
                          std::shared_ptr<std_srvs::srv::SetBool::Response> response) {
    if (request->data){
      gripper_state_ = 0.045;
      response->success = true;
    }
    else{
      gripper_state_ = 0.000;
      response->success = true;
    }

    std_msgs::msg::Float64MultiArray joint_command;
    joint_command.data.resize(8);

    // Copy current positions from last_joint_state
    for (size_t i = 0; i < 6 && i < last_joint_state.position.size(); ++i) {
      joint_command.data[i] = last_joint_state.position[i];
    }

    // Set gripper positions
    joint_command.data[6] = gripper_state_;
    joint_command.data[7] = gripper_state_;

    pub_joint_command_->publish(joint_command);
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
    std::thread(&SimulationAction::execute, this, goal_handle).detach();
  }

  void execute(const std::shared_ptr<GoalHandleFJT> goal_handle){
    // which repo have information about moveit2's trajectory?
    RCLCPP_INFO(this->get_logger(), "Received a new trajectory goal!");
    const auto goal = goal_handle->get_goal();
    const auto& traj = goal->trajectory;

    // Log joint names
    std::ostringstream jn;
    for (size_t i = 0; i < traj.joint_names.size(); ++i) {
      if (i) jn << ", ";
      jn << traj.joint_names[i];
    }
    RCLCPP_INFO(this->get_logger(), "Joint Names: [%s]", jn.str().c_str());

    // Log points
    for (size_t i = 0; i < traj.points.size(); ++i) {
      const auto &pt = traj.points[i];
      std::ostringstream pos, vel, acc;
      for (size_t k = 0; k < pt.positions.size(); ++k) { if (k) pos << ", "; pos << pt.positions[k]; }
      for (size_t k = 0; k < pt.velocities.size(); ++k) { if (k) vel << ", "; vel << pt.velocities[k]; }
      for (size_t k = 0; k < pt.accelerations.size(); ++k) { if (k) acc << ", "; acc << pt.accelerations[k]; }
      RCLCPP_INFO(
        this->get_logger(),
        "Point %zu: Positions: [%s], Velocities: [%s], Accelerations: [%s], TimeFromStart: %d s %u ns",
        i, pos.str().c_str(), vel.str().c_str(), acc.str().c_str(),
        pt.time_from_start.sec, pt.time_from_start.nanosec);
      if(i!=0) {
        rclcpp::Duration duration_cur(traj.points[i].time_from_start);
        rclcpp::Duration duration_pre(traj.points[i-1].time_from_start);
        // we can get moving time (current - previous joint)
        RCLCPP_INFO(
          this->get_logger(),
          "Time interval: %f",
          (duration_cur-duration_pre).seconds());        
      }
    }
    
    for (size_t i = 0; i < traj.points.size(); ++i) {
      const auto& pt = traj.points[i];

      // publish command
      std_msgs::msg::Float64MultiArray joint_command;
      joint_command.data.resize(8);

      // Copy positions from trajectory point
      for (size_t j = 0; j < pt.positions.size() && j < 6; ++j) {
        joint_command.data[j] = pt.positions[j];
      }

      // Set gripper positions
      joint_command.data[6] = gripper_state_;
      joint_command.data[7] = gripper_state_;

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
  }
};

int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<SimulationAction>());
  rclcpp::shutdown();
  return 0;
}