#!/usr/bin/env python3

# SPDX-FileCopyrightText: NVIDIA CORPORATION & AFFILIATES
# Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

"""
Static Camera Info Publisher for Isaac Sim cameras.
Publishes camera_info topics when Isaac Sim doesn't provide them.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CameraInfo, Image
from std_msgs.msg import Header


class CameraInfoPublisher(Node):
    def __init__(self):
        super().__init__('camera_info_publisher')

        # Declare parameters
        self.declare_parameter('width', 1920)
        self.declare_parameter('height', 1200)
        self.declare_parameter('fx', 1200.0)  # Focal length x
        self.declare_parameter('fy', 1200.0)  # Focal length y
        self.declare_parameter('cx', 960.0)   # Principal point x (width/2)
        self.declare_parameter('cy', 600.0)   # Principal point y (height/2)
        self.declare_parameter('rgb_frame_id', 'front_stereo_camera_left')
        self.declare_parameter('depth_frame_id', 'front_stereo_camera_left')

        # Get parameters
        width = self.get_parameter('width').value
        height = self.get_parameter('height').value
        fx = self.get_parameter('fx').value
        fy = self.get_parameter('fy').value
        cx = self.get_parameter('cx').value
        cy = self.get_parameter('cy').value
        rgb_frame_id = self.get_parameter('rgb_frame_id').value
        depth_frame_id = self.get_parameter('depth_frame_id').value

        # Create publishers
        self.rgb_info_pub = self.create_publisher(
            CameraInfo,
            '/front_stereo_camera/left/camera_info',
            10
        )
        self.depth_info_pub = self.create_publisher(
            CameraInfo,
            '/front_stereo_camera/depth/camera_info',
            10
        )

        # Subscribe to image topics to sync camera_info with images
        self.rgb_sub = self.create_subscription(
            Image,
            '/front_stereo_camera/left/image_raw',
            self.rgb_image_callback,
            10
        )
        self.depth_sub = self.create_subscription(
            Image,
            '/front_stereo_camera/depth/ground_truth',
            self.depth_image_callback,
            10
        )

        # Create camera_info messages
        self.rgb_camera_info = self.create_camera_info(width, height, fx, fy, cx, cy, rgb_frame_id)
        self.depth_camera_info = self.create_camera_info(width, height, fx, fy, cx, cy, depth_frame_id)

        self.get_logger().info('Camera Info Publisher started')
        self.get_logger().info(f'Publishing camera_info for {width}x{height} cameras')
        self.get_logger().info(f'RGB frame_id: {rgb_frame_id}')
        self.get_logger().info(f'Depth frame_id: {depth_frame_id}')

    def create_camera_info(self, width, height, fx, fy, cx, cy, frame_id):
        """Create a CameraInfo message with the given parameters."""
        camera_info = CameraInfo()
        camera_info.width = width
        camera_info.height = height
        camera_info.distortion_model = 'plumb_bob'

        # Intrinsic camera matrix K
        # [fx  0 cx]
        # [ 0 fy cy]
        # [ 0  0  1]
        camera_info.k = [
            fx, 0.0, cx,
            0.0, fy, cy,
            0.0, 0.0, 1.0
        ]

        # Distortion parameters (assuming no distortion)
        camera_info.d = [0.0, 0.0, 0.0, 0.0, 0.0]

        # Rectification matrix (identity for unrectified images)
        camera_info.r = [
            1.0, 0.0, 0.0,
            0.0, 1.0, 0.0,
            0.0, 0.0, 1.0
        ]

        # Projection matrix P
        # [fx'  0  cx' Tx]
        # [ 0  fy' cy' Ty]
        # [ 0   0   1   0]
        camera_info.p = [
            fx, 0.0, cx, 0.0,
            0.0, fy, cy, 0.0,
            0.0, 0.0, 1.0, 0.0
        ]

        camera_info.header.frame_id = frame_id

        return camera_info

    def rgb_image_callback(self, msg):
        """Publish camera_info synchronized with RGB images."""
        self.rgb_camera_info.header.stamp = msg.header.stamp
        self.rgb_info_pub.publish(self.rgb_camera_info)

    def depth_image_callback(self, msg):
        """Publish camera_info synchronized with depth images."""
        self.depth_camera_info.header.stamp = msg.header.stamp
        self.depth_info_pub.publish(self.depth_camera_info)


def main(args=None):
    rclpy.init(args=args)
    node = CameraInfoPublisher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
