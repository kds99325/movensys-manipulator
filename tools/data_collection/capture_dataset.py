#!/usr/bin/env python3
"""
capture_dataset.py — periodic image grabber for OBB dataset capture.

Subscribes to a ROS 2 image topic, saves one frame every --interval
seconds as a 5-digit-padded JPEG, and exits after --count saves.

Resumes numbering: scans the output directory for existing
``NNNNN.jpg`` files and starts at ``max+1``. Gaps are not filled.

Run inside the container (or on a host with ROS jazzy + cv_bridge),
after the camera is publishing — typically:

    ros2 launch movensys_manipulator_perception camera_hand.launch.py

…then, in another shell:

    python3 capture_dataset.py --name dice_funnel_v1
"""

import argparse
import re
import sys
from pathlib import Path

import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image


FILENAME_RE = re.compile(r'^(\d{5})\.jpg$')


def next_index(output_dir: Path) -> int:
    if not output_dir.exists():
        return 1
    nums = []
    for entry in output_dir.iterdir():
        m = FILENAME_RE.match(entry.name)
        if m:
            nums.append(int(m.group(1)))
    return (max(nums) + 1) if nums else 1


class DatasetCapture(Node):

    def __init__(self, output_dir: Path, topic: str, interval: float,
                 count: int, quality: int):
        super().__init__('dataset_capture')

        self.output_dir = output_dir
        self.target = count
        self.quality = quality
        self.saved = 0
        self.next_n = next_index(output_dir)
        self.first_n = self.next_n
        self.bridge = CvBridge()
        self.latest: Image | None = None

        if self.next_n > 99999:
            self.get_logger().error(
                f'Output already contains 99999.jpg — 5-digit numbering '
                f'space is exhausted at {output_dir}')
            sys.exit(1)

        self.create_subscription(Image, topic, self._on_image,
                                 qos_profile_sensor_data)
        self.create_timer(interval, self._on_tick)

        self.get_logger().info(
            f'Capturing to {output_dir}\n'
            f'  topic     : {topic}\n'
            f'  interval  : {interval} s\n'
            f'  count     : {count}\n'
            f'  starting  : {self.next_n:05d}.jpg\n'
            f'  quality   : {quality}')

    def _on_image(self, msg: Image) -> None:
        self.latest = msg

    def _on_tick(self) -> None:
        if self.latest is None:
            self.get_logger().warn(
                'No frame received yet — skipping this tick.')
            return

        try:
            cv_img = self.bridge.imgmsg_to_cv2(self.latest, 'bgr8')
        except Exception as exc:
            self.get_logger().error(f'cv_bridge conversion failed: {exc}')
            return

        path = self.output_dir / f'{self.next_n:05d}.jpg'
        ok = cv2.imwrite(str(path), cv_img,
                         [cv2.IMWRITE_JPEG_QUALITY, self.quality])
        if not ok:
            self.get_logger().error(f'cv2.imwrite failed for {path}')
            return

        self.saved += 1
        self.get_logger().info(
            f'[{self.saved}/{self.target}] saved {path.name}')
        self.next_n += 1

        if self.saved >= self.target:
            self.get_logger().info(
                f'Done — saved {self.saved} frames '
                f'({self.first_n:05d}.jpg … {self.next_n - 1:05d}.jpg) '
                f'to {self.output_dir}')
            rclpy.shutdown()


def resolve_output(output: str | None, name: str | None) -> Path:
    if output:
        return Path(output).expanduser().resolve()
    if not name:
        print('error: pass either --output <dir> or --name <dataset_name>',
              file=sys.stderr)
        sys.exit(2)
    base = Path(__file__).resolve().parent / 'output'
    return (base / name / 'images').resolve()


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Periodic ROS image capture for OBB dataset building.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--output', type=str, default=None,
                        help='Output directory. If omitted, derived from --name '
                             'as tools/data_collection/output/<name>/images.')
    parser.add_argument('--name', type=str, default=None,
                        help='Dataset name (used to build default --output).')
    parser.add_argument('--topic', type=str, default='/image_hand/rgb',
                        help='sensor_msgs/Image topic to capture from.')
    parser.add_argument('--interval', type=float, default=10.0,
                        help='Seconds between saves.')
    parser.add_argument('--count', type=int, default=50,
                        help='Number of frames to save before exiting.')
    parser.add_argument('--quality', type=int, default=95,
                        help='JPEG quality, 0-100.')
    args = parser.parse_args(argv)

    if args.count <= 0:
        parser.error('--count must be > 0')
    if args.interval <= 0:
        parser.error('--interval must be > 0')
    if not 0 <= args.quality <= 100:
        parser.error('--quality must be in [0, 100]')

    output_dir = resolve_output(args.output, args.name)
    output_dir.mkdir(parents=True, exist_ok=True)

    rclpy.init()
    node = DatasetCapture(output_dir, args.topic, args.interval,
                          args.count, args.quality)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info(
            f'Interrupted — saved {node.saved}/{node.target} frames.')
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
