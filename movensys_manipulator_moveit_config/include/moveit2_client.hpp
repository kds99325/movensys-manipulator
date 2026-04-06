#ifndef MOVEIT2_CLIENT_HPP
#define MOVEIT2_CLIENT_HPP

#include <rclcpp/rclcpp.hpp>
#include <moveit/move_group_interface/move_group_interface.hpp>
#include <geometry_msgs/msg/pose.hpp>
#include <std_srvs/srv/set_bool.hpp>
#include <tf2/LinearMath/Quaternion.h>
#include <tf2/LinearMath/Matrix3x3.h>
#include <tf2_msgs/msg/tf_message.hpp>
#include <geometry_msgs/msg/transform_stamped.hpp>

#include <string>
#include <vector>
#include <map>
#include <memory>
#include <array>
#include <optional>
#include <mutex>

namespace moveit2_client{
    struct PoseTarget {
        std::array<double, 3> pos;
        std::array<double, 3> ori;
    };

    struct TFResult {
        double x, y, z;
        double roll, pitch, yaw;
        double qx, qy, qz, qw;
    };

    class MoveIt2Client{
        public:
            explicit MoveIt2Client(const rclcpp::Node::SharedPtr& node, const std::string& group_name);

            std::string base_name;
            std::string link_name;
            double vel_scale;
            double acc_scale;
            double max_step;
            double planning_time;
            double delay_exec;
            double delay_gripper;
            double timeout;
            int planning_attempts;
            bool replan;
            int replan_attempts;

            bool jointMovement(const std::map<std::string, double>& joint_targets);
            bool relativeJointMovement(const std::map<std::string, double>& joint_deltas);
            bool absoluteBaseEefJointMovement(const PoseTarget& target);
            
            bool absoluteBaseEefCartesian(const PoseTarget& target);
            bool relativeBaseEefCartesian(const PoseTarget& delta);
            bool relativeToolEefCartesian(const PoseTarget& delta);

            bool setGripper(bool open_gripper);

            std::optional<TFResult> lookupTF(const std::string& parent_frame,
                                              const std::string& child_frame);

            std::optional<TFResult> getCurrentEefPose();

            static geometry_msgs::msg::Pose createPose(const PoseTarget& target);
            void logCurrentState();

        private:
            rclcpp::Node::SharedPtr node_;
            std::shared_ptr<moveit::planning_interface::MoveGroupInterface> move_group_;
            rclcpp::Client<std_srvs::srv::SetBool>::SharedPtr gripper_client_;
            rclcpp::Subscription<tf2_msgs::msg::TFMessage>::SharedPtr tf_sub_;
            std::map<std::string, geometry_msgs::msg::TransformStamped> tf_cache_;
            std::mutex tf_mutex_;

            void tfCallback(const tf2_msgs::msg::TFMessage::SharedPtr msg);
    };

}  // namespace moveit2_client

#endif  // MOVEIT2_CLIENT_HPP
