// Copyright 2026 Movensys Corporation.
// Licensed under the MIT License. See LICENSE.txt for details.

#include <gtest/gtest.h>

#include <string>

#include "movensys_manipulator_moveit_config/srv/get_eef_pose.hpp"
#include "movensys_manipulator_moveit_config/srv/move_joints.hpp"
#include "movensys_manipulator_moveit_config/srv/move_pose.hpp"

TEST(MovePose, request_pos_and_ori) {
  movensys_manipulator_moveit_config::srv::MovePose::Request req;
  req.pos = {0.3, 0.0, 0.4};
  req.ori = {0.0, 0.0, 1.5707963};
  EXPECT_DOUBLE_EQ(req.pos[0], 0.3);
  EXPECT_DOUBLE_EQ(req.ori[2], 1.5707963);
}

TEST(MovePose, response_default_and_set) {
  movensys_manipulator_moveit_config::srv::MovePose::Response res;
  EXPECT_FALSE(res.success);
  res.success = true;
  res.message = "ok";
  EXPECT_TRUE(res.success);
  EXPECT_EQ(res.message, "ok");
}

TEST(MoveJoints, request_arrays_match) {
  movensys_manipulator_moveit_config::srv::MoveJoints::Request req;
  req.joint_names = {"joint_1", "joint_2", "joint_3"};
  req.joint_values = {0.0, 1.57, -0.5};
  ASSERT_EQ(req.joint_names.size(), req.joint_values.size());
  EXPECT_EQ(req.joint_names[1], "joint_2");
  EXPECT_DOUBLE_EQ(req.joint_values[1], 1.57);
}

TEST(MoveJoints, response_default_and_set) {
  movensys_manipulator_moveit_config::srv::MoveJoints::Response res;
  EXPECT_FALSE(res.success);
  res.message = "planning failed";
  EXPECT_EQ(res.message, "planning failed");
}

TEST(GetEefPose, response_pose_fields) {
  movensys_manipulator_moveit_config::srv::GetEefPose::Response res;
  res.pos = {0.2, -0.1, 0.5};
  res.rpy = {0.0, 1.5707963, 0.0};
  res.success = true;
  res.message = "ok";
  EXPECT_DOUBLE_EQ(res.pos[1], -0.1);
  EXPECT_DOUBLE_EQ(res.rpy[1], 1.5707963);
  EXPECT_TRUE(res.success);
}

int main(int argc, char ** argv)
{
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
