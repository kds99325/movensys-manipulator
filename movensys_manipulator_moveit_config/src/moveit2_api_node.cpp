#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <thread>
#include <map>
#include "moveit2_client.hpp"
#include <movensys_manipulator_moveit_config/srv/move_pose.hpp>
#include <movensys_manipulator_moveit_config/srv/move_joints.hpp>

using MovePose   = movensys_manipulator_moveit_config::srv::MovePose;
using MoveJoints = movensys_manipulator_moveit_config::srv::MoveJoints;

class MoveIt2ApiNode
{
public:
    MoveIt2ApiNode()
    {
        node_ = std::make_shared<rclcpp::Node>("moveit2_api_node");

        client_ = std::make_shared<moveit2_client::MoveIt2Client>(
            node_, "movensys_manipulator_arm");

        client_->base_name       = "world_manipulator";
        client_->link_name       = "Link6";
        client_->vel_scale       = 0.3;
        client_->acc_scale       = 0.3;
        client_->delay_exec      = 0.1;
        client_->delay_gripper   = 1.0;
        client_->max_step        = 0.1;
        client_->planning_time   = 1.0;
        client_->timeout         = 1.0;
        client_->planning_attempts = 5;
        client_->replan          = true;
        client_->replan_attempts = 5;

        // Serialize movement commands so they don't interleave
        cb_group_ = node_->create_callback_group(
            rclcpp::CallbackGroupType::MutuallyExclusive);

        abs_base_cart_srv_ = node_->create_service<MovePose>(
            "/wmx/moveit2/absolute_base_eef_cartesian",
            std::bind(&MoveIt2ApiNode::onAbsoluteBaseEefCartesian, this,
                      std::placeholders::_1, std::placeholders::_2),
            rmw_qos_profile_services_default, cb_group_);

        rel_base_cart_srv_ = node_->create_service<MovePose>(
            "/wmx/moveit2/relative_base_eef_cartesian",
            std::bind(&MoveIt2ApiNode::onRelativeBaseEefCartesian, this,
                      std::placeholders::_1, std::placeholders::_2),
            rmw_qos_profile_services_default, cb_group_);

        rel_tool_cart_srv_ = node_->create_service<MovePose>(
            "/wmx/moveit2/relative_tool_eef_cartesian",
            std::bind(&MoveIt2ApiNode::onRelativeToolEefCartesian, this,
                      std::placeholders::_1, std::placeholders::_2),
            rmw_qos_profile_services_default, cb_group_);

        abs_base_joint_srv_ = node_->create_service<MovePose>(
            "/wmx/moveit2/absolute_base_eef_joint_movement",
            std::bind(&MoveIt2ApiNode::onAbsoluteBaseEefJointMovement, this,
                      std::placeholders::_1, std::placeholders::_2),
            rmw_qos_profile_services_default, cb_group_);

        joint_mov_srv_ = node_->create_service<MoveJoints>(
            "/wmx/moveit2/joint_movement",
            std::bind(&MoveIt2ApiNode::onJointMovement, this,
                      std::placeholders::_1, std::placeholders::_2),
            rmw_qos_profile_services_default, cb_group_);

        // EEF pose publisher — separate callback group so it doesn't block movements
        pub_cb_group_ = node_->create_callback_group(
            rclcpp::CallbackGroupType::MutuallyExclusive);

        eef_pose_pub_ = node_->create_publisher<geometry_msgs::msg::PoseStamped>(
            "/wmx/moveit2/eef_pose", 10);

        eef_pose_timer_ = node_->create_wall_timer(
            std::chrono::milliseconds(100),  // 10 Hz
            std::bind(&MoveIt2ApiNode::publishEefPose, this),
            pub_cb_group_);

        RCLCPP_INFO(node_->get_logger(), "MoveIt2 API node ready. Services:");
        RCLCPP_INFO(node_->get_logger(), "  /wmx/moveit2/absolute_base_eef_cartesian      [MovePose]");
        RCLCPP_INFO(node_->get_logger(), "  /wmx/moveit2/relative_base_eef_cartesian      [MovePose]");
        RCLCPP_INFO(node_->get_logger(), "  /wmx/moveit2/relative_tool_eef_cartesian      [MovePose]");
        RCLCPP_INFO(node_->get_logger(), "  /wmx/moveit2/absolute_base_eef_joint_movement [MovePose]");
        RCLCPP_INFO(node_->get_logger(), "  /wmx/moveit2/joint_movement                   [MoveJoints]");
        RCLCPP_INFO(node_->get_logger(), "  (gripper: call /wmx/set_gripper directly       [SetBool])");
        RCLCPP_INFO(node_->get_logger(), "Publisher:");
        RCLCPP_INFO(node_->get_logger(), "  /wmx/moveit2/eef_pose [PoseStamped] @ 10 Hz");
    }

    rclcpp::Node::SharedPtr get_node() { return node_; }

private:
    static moveit2_client::PoseTarget toPoseTarget(const MovePose::Request::SharedPtr& req)
    {
        moveit2_client::PoseTarget t;
        t.pos = {req->pos[0], req->pos[1], req->pos[2]};
        t.ori = {req->ori[0], req->ori[1], req->ori[2]};
        return t;
    }

    void onAbsoluteBaseEefCartesian(
        const MovePose::Request::SharedPtr req,
        MovePose::Response::SharedPtr res)
    {
        RCLCPP_INFO(node_->get_logger(),
            "[svc] absolute_base_eef_cartesian pos=[%.3f,%.3f,%.3f] ori=[%.3f,%.3f,%.3f]",
            req->pos[0], req->pos[1], req->pos[2],
            req->ori[0], req->ori[1], req->ori[2]);
        res->success = client_->absoluteBaseEefCartesian(toPoseTarget(req));
        res->message = res->success ? "success" : "failed";
    }

    void onRelativeBaseEefCartesian(
        const MovePose::Request::SharedPtr req,
        MovePose::Response::SharedPtr res)
    {
        RCLCPP_INFO(node_->get_logger(),
            "[svc] relative_base_eef_cartesian delta pos=[%.3f,%.3f,%.3f] ori=[%.3f,%.3f,%.3f]",
            req->pos[0], req->pos[1], req->pos[2],
            req->ori[0], req->ori[1], req->ori[2]);
        res->success = client_->relativeBaseEefCartesian(toPoseTarget(req));
        res->message = res->success ? "success" : "failed";
    }

    void onRelativeToolEefCartesian(
        const MovePose::Request::SharedPtr req,
        MovePose::Response::SharedPtr res)
    {
        RCLCPP_INFO(node_->get_logger(),
            "[svc] relative_tool_eef_cartesian delta pos=[%.3f,%.3f,%.3f] ori=[%.3f,%.3f,%.3f]",
            req->pos[0], req->pos[1], req->pos[2],
            req->ori[0], req->ori[1], req->ori[2]);
        res->success = client_->relativeToolEefCartesian(toPoseTarget(req));
        res->message = res->success ? "success" : "failed";
    }

    void onAbsoluteBaseEefJointMovement(
        const MovePose::Request::SharedPtr req,
        MovePose::Response::SharedPtr res)
    {
        RCLCPP_INFO(node_->get_logger(),
            "[svc] absolute_base_eef_joint_movement pos=[%.3f,%.3f,%.3f] ori=[%.3f,%.3f,%.3f]",
            req->pos[0], req->pos[1], req->pos[2],
            req->ori[0], req->ori[1], req->ori[2]);
        res->success = client_->absoluteBaseEefJointMovement(toPoseTarget(req));
        res->message = res->success ? "success" : "failed";
    }

    void onJointMovement(
        const MoveJoints::Request::SharedPtr req,
        MoveJoints::Response::SharedPtr res)
    {
        if (req->joint_names.size() != req->joint_values.size()) {
            res->success = false;
            res->message = "joint_names and joint_values size mismatch";
            RCLCPP_ERROR(node_->get_logger(), "[svc] joint_movement: %s", res->message.c_str());
            return;
        }

        std::map<std::string, double> joints;
        for (size_t i = 0; i < req->joint_names.size(); ++i) {
            joints[req->joint_names[i]] = req->joint_values[i];
        }

        RCLCPP_INFO(node_->get_logger(), "[svc] joint_movement: %zu joints", joints.size());
        res->success = client_->jointMovement(joints);
        res->message = res->success ? "success" : "failed";
    }

    void publishEefPose()
    {
        auto result = client_->getCurrentEefPose();
        if (!result) {
            return;
        }

        geometry_msgs::msg::PoseStamped msg;
        msg.header.stamp    = node_->now();
        msg.header.frame_id = client_->base_name;
        msg.pose.position.x = result->x;
        msg.pose.position.y = result->y;
        msg.pose.position.z = result->z;
        msg.pose.orientation.x = result->qx;
        msg.pose.orientation.y = result->qy;
        msg.pose.orientation.z = result->qz;
        msg.pose.orientation.w = result->qw;

        eef_pose_pub_->publish(msg);
    }

    rclcpp::Node::SharedPtr node_;
    std::shared_ptr<moveit2_client::MoveIt2Client> client_;
    rclcpp::CallbackGroup::SharedPtr cb_group_;
    rclcpp::CallbackGroup::SharedPtr pub_cb_group_;

    rclcpp::Service<MovePose>::SharedPtr             abs_base_cart_srv_;
    rclcpp::Service<MovePose>::SharedPtr             rel_base_cart_srv_;
    rclcpp::Service<MovePose>::SharedPtr             rel_tool_cart_srv_;
    rclcpp::Service<MovePose>::SharedPtr             abs_base_joint_srv_;
    rclcpp::Service<MoveJoints>::SharedPtr                          joint_mov_srv_;
    rclcpp::Publisher<geometry_msgs::msg::PoseStamped>::SharedPtr   eef_pose_pub_;
    rclcpp::TimerBase::SharedPtr                                    eef_pose_timer_;
};

int main(int argc, char* argv[])
{
    rclcpp::init(argc, argv);

    MoveIt2ApiNode api_node;

    rclcpp::executors::MultiThreadedExecutor executor;
    executor.add_node(api_node.get_node());

    executor.spin();

    rclcpp::shutdown();
    return 0;
}
