#!/usr/bin/env python3
"""
yolo_dice_detector.py  —  YOLO OBB dice detection node (movensys_manipulator_perception)
=========================================================================================

Subscribes to the hand camera, runs YOLO OBB inference, and for every
detected dice face class broadcasts a TF frame relative to the camera
optical frame — same convention used by apriltag_detector.py and
yolo_cube_detector.py so downstream MoveIt2 clients can reuse a single
TF-based tracking loop.

3-D position (camera frame)
----------------------------
The camera is at a fixed height and orientation (scan pose). The
cam_z_world and R_cam values are derived from hardcoded parameters
and computed once at startup — no TF lookup is needed at runtime.

For a camera pointing roughly downward, the die centroid pixel is
unprojected to a 3-D ray, which is intersected with the horizontal
plane  z_world = dice_height  (top surface of a 5 cm die lying on the
floor: dice_height = 0.05 m).  The resulting world point is then
expressed back in the camera optical frame as a simple scalar multiple
of the normalised ray direction:

    x_norm = (px - cx) / fx
    y_norm = (py - cy) / fy
    d_world = R_cam_to_world @ [x_norm, y_norm, 1.0]
    t       = (dice_height - cam_z_world) / d_world[2]
    p_cam   = t * [x_norm, y_norm, 1.0]          # in optical frame

TF frames published (on /tf):
    <camera_frame>  ->  yolo_dice_one
    <camera_frame>  ->  yolo_dice_two
    <camera_frame>  ->  yolo_dice_three
    <camera_frame>  ->  yolo_dice_four
    <camera_frame>  ->  yolo_dice_five
    <camera_frame>  ->  yolo_dice_six

Model class mapping (matches dataset.yaml):
    0: Five  1: Four  2: One  3: Six  4: Three  5: Two
"""

import math

import cv2
import numpy as np
import rclpy
from cv_bridge import CvBridge
from geometry_msgs.msg import TransformStamped
from rclpy.node import Node
from scipy.spatial.transform import Rotation
from sensor_msgs.msg import CameraInfo, Image
from tf2_ros import TransformBroadcaster


CLASS_NAMES = ['Five', 'Four', 'One', 'Six', 'Three', 'Two']
CLASS_SHORT = ['five',  'four',  'one', 'six', 'three', 'two']
CLASS_COLORS = {
    'Five':  (0,   0,   255),
    'Four':  (0,   165, 255),
    'One':   (0,   255, 255),
    'Six':   (0,   255, 0),
    'Three': (255, 128, 0),
    'Two':   (255, 0,   255),
}


class YoloDiceDetector(Node):
    """
    ROS 2 node: YOLO OBB dice detection with camera-frame TF broadcast.
    """

    def __init__(self):
        super().__init__('yolo_dice_detector')

        self.declare_parameter('model_path', '')
        self.declare_parameter('confidence_threshold', 0.5)
        self.declare_parameter('dice_height', 0.05)
        self.declare_parameter('cam_z_world', 0.45)
        self.declare_parameter('cam_x_world', 0.0)
        self.declare_parameter('cam_y_world', 0.0)
        self.declare_parameter('cam_orientation', [0.0, 1.0, 0.0, 0.0])
        self.declare_parameter('publish_debug_image', True)
        self.declare_parameter('device', 'cpu')
        self.declare_parameter('image_topic',
                               '/camera_hand/realsense2_camera/color/image_raw')
        self.declare_parameter('camera_info_topic',
                               '/camera_hand/realsense2_camera/color/camera_info')
        self.declare_parameter('camera_frame',
                               'camera_hand_color_optical_frame')

        model_path            = self.get_parameter('model_path').value
        self.conf_threshold   = self.get_parameter('confidence_threshold').value
        self.dice_height      = self.get_parameter('dice_height').value
        self.cam_z_world      = self.get_parameter('cam_z_world').value
        self.cam_x_world      = self.get_parameter('cam_x_world').value
        self.cam_y_world      = self.get_parameter('cam_y_world').value
        cam_quat              = self.get_parameter('cam_orientation').value
        self.publish_debug    = self.get_parameter('publish_debug_image').value
        self.device           = self.get_parameter('device').value
        image_topic           = self.get_parameter('image_topic').value
        camera_info_topic     = self.get_parameter('camera_info_topic').value
        self.camera_frame     = self.get_parameter('camera_frame').value

        self.R_cam = self._quat_to_rot(cam_quat)

        self.bridge = CvBridge()
        self.model  = None
        self.fx = self.fy = self.cx = self.cy = None

        self.tf_broadcaster = TransformBroadcaster(self)

        if not model_path:
            self.get_logger().error(
                'model_path parameter is empty — pass it via launch argument.')
        else:
            self._load_model(model_path)

        self.create_subscription(CameraInfo, camera_info_topic,
                                 self._camera_info_cb, 10)
        self.create_subscription(Image, image_topic,
                                 self._image_cb, 10)

        if self.publish_debug:
            self.debug_pub = self.create_publisher(Image, '~/debug_image', 10)

        self.get_logger().info(
            f'YoloDiceDetector ready\n'
            f'  model       : {model_path}\n'
            f'  device      : {self.device}\n'
            f'  dice_height : {self.dice_height} m\n'
            f'  cam_z_world : {self.cam_z_world} m\n'
            f'  cam_quat    : {cam_quat}\n'
            f'  conf        : {self.conf_threshold}\n'
            f'  camera      : {self.camera_frame}')

    def _load_model(self, model_path: str):
        try:
            from pathlib import Path
            from ultralytics import YOLO

            path = Path(model_path).expanduser().resolve()
            if not path.exists():
                self.get_logger().error(f'Model path does not exist: {path}')
                return

            self.get_logger().info(f'Loading YOLO model from {path} …')
            self.model = YOLO(str(path), task='obb')
            self.get_logger().info('Model loaded.')
        except ImportError:
            self.get_logger().error('ultralytics is not installed.')
        except Exception as exc:
            self.get_logger().error(f'Model load failed: {exc}')

    def _camera_info_cb(self, msg: CameraInfo):
        if self.fx is None:
            self.get_logger().info(
                f'Camera intrinsics received: fx={msg.k[0]:.1f} fy={msg.k[4]:.1f} '
                f'cx={msg.k[2]:.1f} cy={msg.k[5]:.1f}')
        # K = [fx, 0, cx,  0, fy, cy,  0, 0, 1]
        self.fx = msg.k[0]
        self.fy = msg.k[4]
        self.cx = msg.k[2]
        self.cy = msg.k[5]

    def _image_cb(self, msg: Image):
        if self.model is None:
            self.get_logger().warn('Image received but model not loaded — skipping.',
                                   throttle_duration_sec=5.0)
            return
        if self.fx is None:
            self.get_logger().warn('Image received but camera_info not yet received — skipping.',
                                   throttle_duration_sec=5.0)
            return

        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception as exc:
            self.get_logger().error(f'cv_bridge failed: {exc}')
            return
        self.get_logger().info('Image received, running inference...',
                               throttle_duration_sec=5.0)

        try:
            results = self.model(cv_image,
                                 conf=self.conf_threshold,
                                 device=self.device,
                                 verbose=False)
        except Exception as exc:
            self.get_logger().error(f'Inference failed: {exc}')
            return

        best: dict[int, tuple] = {}
        for result in results:
            if result.obb is None:
                continue
            for i in range(len(result.obb)):
                cls_id = int(result.obb.cls[i].item())
                conf   = float(result.obb.conf[i].item())
                if cls_id >= len(CLASS_NAMES):
                    continue
                if cls_id not in best or conf > best[cls_id][0]:
                    corners = result.obb.xyxyxyxy[i].cpu().numpy().reshape(4, 2)
                    best[cls_id] = (conf, corners)

        self.get_logger().info(
            f'Detections: {len(best)} class(es) — '
            f'{", ".join(CLASS_NAMES[c] for c in best)}' if best else 'Detections: none')

        tf_msgs = []
        annotations = []

        for cls_id, (conf, corners) in best.items():
            cx_px = float(np.mean(corners[:, 0]))
            cy_px = float(np.mean(corners[:, 1]))
            image_yaw = self._smart_yaw(corners)

            self.get_logger().info(
                f'{CLASS_NAMES[cls_id]}: pixel=({cx_px:.0f},{cy_px:.0f})  '
                f'conf={conf:.2f}  yaw={math.degrees(image_yaw):.1f}°')

            p_cam = self._project_to_camera_frame(cx_px, cy_px)

            if p_cam is None:
                self.get_logger().info(
                    f'{CLASS_NAMES[cls_id]}: projection failed — skipping')
                continue

            p_world = self._cam_to_world(p_cam)
            self.get_logger().info(
                f'{CLASS_NAMES[cls_id]}: '
                f'cam=({p_cam[0]:.3f},{p_cam[1]:.3f},{p_cam[2]:.3f})  '
                f'world=({p_world[0]:.3f},{p_world[1]:.3f},{p_world[2]:.3f})')

            quat = Rotation.from_euler('z', image_yaw).as_quat()

            t = TransformStamped()
            t.header.stamp    = msg.header.stamp
            t.header.frame_id = self.camera_frame
            t.child_frame_id  = f'yolo_dice_{CLASS_SHORT[cls_id]}'
            t.transform.translation.x = float(p_cam[0])
            t.transform.translation.y = float(p_cam[1])
            t.transform.translation.z = float(p_cam[2])
            t.transform.rotation.x    = float(quat[0])
            t.transform.rotation.y    = float(quat[1])
            t.transform.rotation.z    = float(quat[2])
            t.transform.rotation.w    = float(quat[3])
            tf_msgs.append(t)

            annotations.append({
                'corners':    corners,
                'centroid':   (int(cx_px), int(cy_px)),
                'cls_name':   CLASS_NAMES[cls_id],
                'conf':       conf,
                'image_yaw':  image_yaw,
                'p_cam':      p_cam,
            })

        for tf_msg in tf_msgs:
            self.tf_broadcaster.sendTransform(tf_msg)
        self.get_logger().info(f'Broadcast {len(tf_msgs)} TF frame(s)')

        if self.publish_debug:
            debug = self._draw(cv_image, annotations)
            out_msg = self.bridge.cv2_to_imgmsg(debug, 'bgr8')
            out_msg.header = msg.header
            self.debug_pub.publish(out_msg)

    def _project_to_camera_frame(
            self, px: float, py: float) -> np.ndarray | None:
        x_norm = (px - self.cx) / self.fx
        y_norm = (py - self.cy) / self.fy
        d_opt  = np.array([x_norm, y_norm, 1.0])

        d_world = self.R_cam @ d_opt

        if abs(d_world[2]) < 1e-6:
            self.get_logger().warn('Ray parallel to floor plane, skipping.')
            return None

        t = (self.dice_height - self.cam_z_world) / d_world[2]

        if t < 0.0:
            self.get_logger().warn('Intersection behind camera, skipping.')
            return None

        return t * d_opt

    def _cam_to_world(self, p_cam: np.ndarray) -> np.ndarray:
        t_cam = np.array([self.cam_x_world, self.cam_y_world, self.cam_z_world])
        return self.R_cam @ p_cam + t_cam

    def _smart_yaw(self, corners: np.ndarray) -> float:
        """
        OBB yaw relative to the vertical image axis. For a die's square
        footprint (4-fold / 90° symmetry), every edge is equivalent —
        fold each edge angle into [-π/4, π/4] and pick the one closest
        to vertical.
        """
        folded = []
        for i in range(4):
            p1 = corners[i]
            p2 = corners[(i + 1) % 4]
            dx = float(p2[0] - p1[0])
            dy = float(p2[1] - p1[1])
            angle = math.atan2(dx, -dy)
            while angle >  math.pi / 4:
                angle -= math.pi / 2
            while angle < -math.pi / 4:
                angle += math.pi / 2
            folded.append(angle)

        return min(folded, key=abs)

    @staticmethod
    def _quat_to_rot(quat: list) -> np.ndarray:
        x, y, z, w = quat
        n = math.sqrt(x*x + y*y + z*z + w*w)
        x, y, z, w = x/n, y/n, z/n, w/n
        return np.array([
            [1 - 2*(y*y + z*z),  2*(x*y - z*w),  2*(x*z + y*w)],
            [2*(x*y + z*w),  1 - 2*(x*x + z*z),  2*(y*z - x*w)],
            [2*(x*z - y*w),  2*(y*z + x*w),  1 - 2*(x*x + y*y)],
        ])

    def _draw(self, image: np.ndarray, annotations: list) -> np.ndarray:
        vis = image.copy()
        for ann in annotations:
            color    = CLASS_COLORS.get(ann['cls_name'], (255, 255, 255))
            corners  = ann['corners'].astype(np.int32)
            centroid = ann['centroid']
            yaw      = ann['image_yaw']
            p_cam    = ann['p_cam']

            cv2.polylines(vis, [corners], True, color, 2)
            cv2.circle(vis, centroid, 5, color, -1)

            length = 35
            ex = int(centroid[0] + length * math.sin(yaw))
            ey = int(centroid[1] - length * math.cos(yaw))
            cv2.arrowedLine(vis, centroid, (ex, ey), color, 2)

            cx0, cy0 = centroid
            for idx, (cx, cy) in enumerate(corners):
                corner_label = f"C{idx}({cx},{cy})"
                dx = int(cx) - cx0
                dy = int(cy) - cy0
                norm = math.hypot(dx, dy) or 1.0
                pad = 18
                tx = int(cx) + int(dx / norm * pad)
                ty = int(cy) + int(dy / norm * pad)
                if dx >= 0:
                    tx -= 70
                cv2.circle(vis, (int(cx), int(cy)), 3, color, -1)
                cv2.putText(vis, corner_label, (tx, ty),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1)

            label = f"{ann['cls_name']}  {ann['conf']:.2f}"
            pos3d = f"cam({p_cam[0]:.2f},{p_cam[1]:.2f},{p_cam[2]:.2f})"
            lx = centroid[0] - 50
            ly = centroid[1] - 28
            cv2.putText(vis, label, (lx, ly),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
            cv2.putText(vis, pos3d, (lx, ly + 16),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, color, 1)

        return vis


def main(args=None):
    rclpy.init(args=args)
    node = YoloDiceDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
