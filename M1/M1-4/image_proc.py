#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""图像处理与控制节点 —— 终端2 运行

订阅:
    /camera/image_raw    640x480, 目标 30Hz（接受 bgr8 / mono8）
发布:
    /perception/result   640x480 mono8
    /control/cmd         Twist, 20Hz

运行:
    python3 image_proc.py

观测:
    ros2 topic hz    /perception/result
    ros2 topic hz    /control/cmd
    ros2 topic delay /perception/result
"""

import cv2
import numpy as np
import rclpy
from cv_bridge import CvBridge
from geometry_msgs.msg import Twist
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import Image
from rclpy.callback_groups import ReentrantCallbackGroup

IMAGE_IN = "/camera/image_raw"
IMAGE_OUT = "/perception/result"
CMD_OUT = "/control/cmd"

IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480
WORK_WIDTH = 1280
WORK_HEIGHT = 720
CONTROL_HZ = 20.0


def make_sub_qos():
    """图像链路的 QoS 配置。

    depth 表示"最多缓存多少条尚未处理的消息"。
    """
    return QoSProfile(
        depth=2,
        reliability=ReliabilityPolicy.RELIABLE,
        history=HistoryPolicy.KEEP_LAST,
    )


class ImageProc(Node):
    def __init__(self):
        super().__init__("image_proc")
        self.cb_group=ReentrantCallbackGroup()
        self.sub = self.create_subscription(
            Image, IMAGE_IN, self.on_image, make_sub_qos(), callback_group=self.cb_group
        )
        self.pub = self.create_publisher(Image, IMAGE_OUT, make_sub_qos())
        self.bridge = CvBridge()

    def on_image(self, msg):
        gray = self.bridge.imgmsg_to_cv2(msg, desired_encoding="mono8")

        brightened = np.clip(gray.astype(np.int16) + 20, 0, 255).astype(np.uint8)

        #对比度拉伸,使用NumPy向量化
        #等价于原代码的 (val - 128) * 1.5 + 128
        contrasted = np.clip((brightened.astype(np.float32) - 128) * 1.5 + 128, 0, 255).astype(np.uint8)

        #发布
        out = self.bridge.cv2_to_imgmsg(contrasted, encoding="mono8")
        out.header.stamp = msg.header.stamp  # 必须沿用输入时间戳
        out.header.frame_id = msg.header.frame_id
        self.pub.publish(out)


class ControlLoop(Node):
    def __init__(self):
        super().__init__("control_loop")
        self.cb_group = ReentrantCallbackGroup()
        self.pub = self.create_publisher(Twist, CMD_OUT, make_sub_qos())
        self.timer = self.create_timer(1.0 / CONTROL_HZ, self.on_timer, self.cb_group)

    def on_timer(self):
        cmd = Twist()
        cmd.linear.x = 0.10
        cmd.angular.z = 0.05
        self.pub.publish(cmd)


def main():
    rclpy.init()
    nodes = [ImageProc(), ControlLoop()]
    executor = MultiThreadedExecutor()
    for node in nodes:
        executor.add_node(node)
    try:
        executor.spin()
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        executor.shutdown()
        for node in nodes:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
