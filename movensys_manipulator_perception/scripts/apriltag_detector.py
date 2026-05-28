#!/usr/bin/env python3
"""
ROS 2 AprilTag detection node (movensys_manipulator_perception).

Subscribes to camera image and camera_info topics, detects AprilTags,
and broadcasts TF transforms for each detected tag.

TF frames published (on /tf):
    <camera_frame> -> tag36h11:<tag_id>
"""

import cv2
from cv_bridge import CvBridge
from geometry_msgs.msg import TransformStamped
from pyapriltags import Detector
import rclpy
from rclpy.node import Node
from scipy.spatial.transform import Rotation
from sensor_msgs.msg import CameraInfo, Image
from tf2_ros import TransformBroadcaster


class AprilTagDetectorNode(Node):
    def __init__(self):
        super().__init__('apriltag_detector')

        self.declare_parameter('tag_family', 'tag36h11')
        self.declare_parameter('tag_size', 0.04)
        self.declare_parameter('image_topic', '/camera_hand/realsense2_camera/color/image_raw')
        self.declare_parameter(
            'camera_info_topic', '/camera_hand/realsense2_camera/color/camera_info')
        self.declare_parameter('camera_frame', 'camera_hand_color_optical_frame')
        self.declare_parameter('nthreads', 1)
        self.declare_parameter('quad_decimate', 2.0)
        self.declare_parameter('quad_sigma', 0.0)
        self.declare_parameter('refine_edges', 1)
        self.declare_parameter('decode_sharpening', 0.25)

        tag_family = self.get_parameter('tag_family').value
        self.tag_size = self.get_parameter('tag_size').value
        image_topic = self.get_parameter('image_topic').value
        camera_info_topic = self.get_parameter('camera_info_topic').value
        self.camera_frame = self.get_parameter('camera_frame').value

        self.detector = Detector(
            families=tag_family,
            nthreads=self.get_parameter('nthreads').value,
            quad_decimate=self.get_parameter('quad_decimate').value,
            quad_sigma=self.get_parameter('quad_sigma').value,
            refine_edges=self.get_parameter('refine_edges').value,
            decode_sharpening=self.get_parameter('decode_sharpening').value,
        )

        self.camera_params = None  # [fx, fy, cx, cy]
        self.bridge = CvBridge()
        self.tf_broadcaster = TransformBroadcaster(self)

        self.create_subscription(
            CameraInfo, camera_info_topic, self.camera_info_cb, 10
        )
        self.create_subscription(
            Image, image_topic, self.image_cb, 10
        )

        self.get_logger().info(
            f'AprilTag detector initialized: family={tag_family}, '
            f'tag_size={self.tag_size}m, camera_frame={self.camera_frame}'
        )

    def camera_info_cb(self, msg: CameraInfo):
        # K = [fx, 0, cx, 0, fy, cy, 0, 0, 1]
        self.camera_params = [msg.k[0], msg.k[4], msg.k[2], msg.k[5]]

    def image_cb(self, msg: Image):
        if self.camera_params is None:
            return

        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

        tags = self.detector.detect(
            gray,
            estimate_tag_pose=True,
            camera_params=self.camera_params,
            tag_size=self.tag_size,
        )

        for tag in tags:
            t = TransformStamped()
            t.header.stamp = msg.header.stamp
            t.header.frame_id = self.camera_frame
            t.child_frame_id = f'tag36h11:{tag.tag_id}'

            t.transform.translation.x = float(tag.pose_t[0][0])
            t.transform.translation.y = float(tag.pose_t[1][0])
            t.transform.translation.z = float(tag.pose_t[2][0])

            quat = Rotation.from_matrix(tag.pose_R).as_quat()
            t.transform.rotation.x = quat[0]
            t.transform.rotation.y = quat[1]
            t.transform.rotation.z = quat[2]
            t.transform.rotation.w = quat[3]

            self.tf_broadcaster.sendTransform(t)

            rpy = Rotation.from_matrix(tag.pose_R).as_euler('xyz', degrees=True)
            self.get_logger().info(
                f'Tag {tag.tag_id} | '
                f'xyz=({t.transform.translation.x:.4f}, '
                f'{t.transform.translation.y:.4f}, '
                f'{t.transform.translation.z:.4f}) m | '
                f'rpy=({rpy[0]:.2f}, {rpy[1]:.2f}, {rpy[2]:.2f}) deg'
            )


def main(args=None):
    rclpy.init(args=args)
    node = AprilTagDetectorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
